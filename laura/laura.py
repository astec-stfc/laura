"""
LAURA Main Module

The main class for handling a full particle accelerator lattice.
"""

import glob
import logging
import os
import types
from itertools import chain
from typing import Any, Dict, List

from pydantic import PrivateAttr, field_validator, model_validator
from yaml.constructor import Constructor

_log = logging.getLogger("laura.machine")


import numpy as np

from .importers.yaml_loader import (
    ElementLoadError,
    LazyElementDict,
    RawFileNamespace,
    collect_template_filenames,
    collect_unique_by_name,
    collect_unique_filenames,
    read_yaml_combined_file,
    read_yaml_element_file,
)
from ._compat import DeprecatedMethodAliases
from .models.element import BaseElement
from .models.element_list import MachineModel, insert_drifts


NON_ELEMENT_FILENAMES = {"summary.yaml", "summary.yml"}
"""Files to ignore when scanning an ``element_list`` directory. ``summary.yaml`` is an
aggregate of every element in the machine, not a single-element file, so treating it as
one invents a bogus element -- and it cannot be recognised by content, because
:func:`~laura.importers.yaml_loader.fast_get_element_metadata` reads only the first 2000
characters and most real element files declare ``name:`` after that (falling back to the
filename), so a summary would simply be named after its file."""



def flatten(xss):
    """Flatten a list of lists."""
    return list(chain.from_iterable(xss))


_CORRECTOR_TYPES = ["combined_corrector", "horizontal_corrector", "vertical_corrector"]


def _getter(
    what: str,
    element_class: str | None = None,
    element_type: str | list | None = None,
    then=None,
    returns: str | None = None,
):
    """
    Build a ``get_<family>(end, start, path)`` method, listing the names of the
    elements of ``element_class``/``element_type`` along a path, optionally
    post-processed by ``then(machine, names)``.
    """

    def get(self, end: str = None, start: str = None, path: str = None) -> list[str]:
        names = self.elements_between(
            start=start,
            end=end,
            element_class=element_class,
            element_type=element_type,
            path=path,
        )
        return then(self, names) if then else names

    get.__doc__ = f"""
        Get all {what} between start and end

        :param end: Name of the last element in the sequence
        :param start: Name of the first element in the sequence
        :param path: Name of the lattice path to use
        :return: {returns or f"List of the names of the {what}"}
        """
    return get


def _union(machine, getter) -> set:
    """The union of ``getter`` over every lattice path of ``machine``."""
    return set(chain.from_iterable(getter(machine, path=path) for path in machine.lattices))


def _all_paths(getter, what: str) -> property:
    """Build an ``all_<family>`` property: ``getter`` over the whole machine."""
    return property(
        lambda self: _union(self, getter),
        doc=f"""
        Get all {what} in the machine
        :return: Set of the names of all {what}
        """,
    )


def _split_correctors(machine, names: list[str]) -> list[str]:
    """``names``, with each combined corrector split into its sub-correctors."""
    return flatten(machine._sub_correctors(name) for name in names)


def _sub_corrector(attr: str):
    """Replace each combined corrector by its ``attr`` sub-corrector, if any."""

    def pick(machine, names: list[str]) -> list[str]:
        subs = (getattr(machine[name], attr, None) for name in names)
        return [name if sub is None else sub for name, sub in zip(names, subs)]

    return pick


def add_bool(self, node):
    return self.construct_scalar(node)


def _lattice_root(lattice: Any) -> str | None:
    """
    Return the top-level directory of a machine lattice package.

    Looks for ``master_lattice``; if this is not set, look for absolute file paths.
    """
    root = getattr(lattice, "master_lattice", None)
    if root is None:
        filename = getattr(lattice, "__file__", None)
        if filename:
            root = os.path.dirname(os.path.abspath(filename))
    if root is None:
        data_files = getattr(lattice, "data_files", None)
        if data_files:
            root = os.path.dirname(os.path.abspath(data_files))
    return root


Constructor.add_constructor("tag:yaml.org,2002:bool", add_bool)


class LAURA(DeprecatedMethodAliases, MachineModel):
    """
    LAURA Main Class

    The main class for handling a full particle accelerator lattice.
    """

    _DEPRECATED_METHOD_ALIASES = {
        "createDrifts": "create_drifts",
    }
    """Legacy names which are served by a ``FutureWarning``"""

    element_list: str | List[BaseElement]
    """List containing all elements in the machine model, either as a path to a YAML file/directory 
    or as a list of element objects."""

    exclude_keys: List[str] | None = None
    """List of top-level keys to exclude when reading YAML files"""

    eager_mode: bool = False
    """Whether to load all elements into memory immediately (True) or use lazy loading (False, default)"""

    strict: bool = False
    """Whether an element that fails to load raises
    :class:`~laura.Importers.YAML_Loader.ElementLoadError` (True) or is skipped
    (False, default). Errors can be inspected via :attr:`load_errors`."""

    _load_errors: List[ElementLoadError] = PrivateAttr(default_factory=list)

    @property
    def load_errors(self) -> List[ElementLoadError]:
        """
        Elements the files describe that are not in this machine, as
        :class:`~laura.Importers.YAML_Loader.ElementLoadError` records.
        """
        return self._load_errors

    @model_validator(mode="before")
    @classmethod
    def _resolve_lattice_package(cls, data: Any) -> Any:
        """Accept a ``lattice`` keyword that is a laura_lattices machine module
        (or any object with ``layout``, ``section`` and ``element_list``
        attributes) and expand it into the individual fields."""
        if not isinstance(data, dict):
            return data
        lattice = data.pop("lattice", None)
        if lattice is None:
            return data
        if isinstance(lattice, types.ModuleType) or (
            hasattr(lattice, "layout")
            and hasattr(lattice, "section")
            and hasattr(lattice, "element_list")
        ):
            data.setdefault("layout", lattice.layout)
            data.setdefault("section", lattice.section)
            data.setdefault("element_list", lattice.element_list)
            if "master_lattice" not in data:
                root = _lattice_root(lattice)
                if root is not None:
                    data["master_lattice"] = root
        else:
            raise ValueError(
                "lattice must be a module (e.g. laura_lattices.CLARA) or an object "
                "with 'layout', 'section', and 'element_list' attributes"
            )
        return data

    """List of top-level keys to exclude when reading YAML files"""

    @field_validator("element_list", mode="before")
    @classmethod
    def validate_element_list(cls, v: str | list) -> str | list:
        if isinstance(v, str):
            if os.path.isfile(v):
                return v
            elif os.path.isfile(os.path.abspath(os.path.dirname(__file__) + "/" + v)):
                return os.path.abspath(os.path.dirname(__file__) + "/" + v)
            elif os.path.isdir(v):
                return v
            elif os.path.isdir(os.path.abspath(os.path.dirname(__file__) + "/" + v)):
                return os.path.abspath(os.path.dirname(__file__) + "/" + v)
            else:
                return v
        else:
            return v

    def model_post_init(self, __context):
        el_list = self.element_list
        if (
            isinstance(el_list, str)
            and not os.path.exists(el_list)
            and self.master_lattice
        ):
            candidate = os.path.join(self.master_lattice, el_list)
            if os.path.exists(candidate):
                el_list = candidate

        if isinstance(el_list, str) and el_list and not os.path.exists(el_list):
            raise ValueError(
                f"element_list '{self.element_list}' does not exist"
                + (
                    f" (also tried relative to master_lattice '{self.master_lattice}')"
                    if self.master_lattice
                    else ""
                )
            )

        if isinstance(el_list, str):
            if os.path.isfile(el_list):
                elems = read_yaml_combined_file(
                    el_list, strict=self.strict, errors=self._load_errors
                )
                values = collect_unique_by_name(
                    ((y.name, el_list, y) for y in elems if hasattr(y, "name")),
                    errors=self._load_errors,
                    strict=self.strict,
                )
                self.elements.update(values)
            elif os.path.isdir(el_list):
                files = glob.glob(
                    os.path.abspath(el_list + "/**/*.yaml"), recursive=True
                )
                auxiliary = [f for f in files if os.path.basename(f).startswith("_")]
                files = [f for f in files if not os.path.basename(f).startswith("_") and os.path.basename(f).lower() not in NON_ELEMENT_FILENAMES]
                filenames = collect_unique_filenames(
                    files, errors=self._load_errors, strict=self.strict
                )
                templates = collect_template_filenames(auxiliary)
                # Create lazy dict instead of loading all!
                if not self.eager_mode:
                    self.elements = LazyElementDict(
                        filenames,
                        exclude_keys=self.exclude_keys,
                        strict=self.strict,
                        errors=self._load_errors,
                        templates=templates,
                    )
                else:
                    namespace = RawFileNamespace({**templates, **filenames})
                    memo: Dict = {}
                    elems = [
                        read_yaml_element_file(
                            fn,
                            exclude_keys=self.exclude_keys,
                            strict=self.strict,
                            errors=self._load_errors,
                            namespace=namespace,
                            memo=memo,
                        )
                        for fn in files
                    ]
                    self.elements.update(
                        {y.name: y for y in elems if isinstance(y, BaseElement)}
                    )
        elif el_list:
            values = collect_unique_by_name(
                ((y.name, None, y) for y in el_list if hasattr(y, "name")),
                errors=self._load_errors,
                strict=self.strict,
            )
            self.elements.update(values)

        super().model_post_init(__context)

    def create_drifts(
        self, end: str = None, start: str = None, path: str = None
    ) -> Dict:
        """
        Insert drifts into a sequence of 'elements'

        :param end: Name of the last element in the sequence
        :param start: Name of the first element in the sequence
        :param path: Name of the lattice path to use
        :return: Dictionary of elements with drifts inserted
        """
        elements = {}
        for name in self.elements_between(
            start=start, end=end, element_class=None, path=path
        ):
            if not self.elements[name].is_subelement():
                elements[name] = self.elements[name]
        return insert_drifts(elements, "drift", min_length=1e-12)

    def _drift_length(self, start: list[float], end: list[float]):
        return np.linalg.norm(end - start)

    def get_elements_s_pos(
        self, end: str = None, start: str = None, path: str = None
    ) -> Dict[str, float]:
        """
        Get s positions of all elements between start and end

        :param end: Name of the last element in the sequence
        :param start: Name of the first element in the sequence
        :param path: Name of the lattice path to use
        :return: Dictionary of element names and their s positions
        """
        elements = self.create_drifts(start=start, end=end, path=path)
        start_and_end = [
            [name, elem.physical.length, elem.hardware_type == "Drift"]
            for name, elem in elements.items()
        ]
        elem_s = {}
        s_pos = 0
        for elem, l, drift in start_and_end:
            s_pos += l
            if not drift:
                elem_s[elem] = round(s_pos, 6)
                original = self.elements.get(elem)
                for sub_attr in ("Horizontal_Corrector", "Vertical_Corrector"):
                    sub_name = getattr(original, sub_attr, None)
                    if sub_name:
                        elem_s[sub_name] = elem_s[elem]
        return elem_s

    def _sub_correctors(self, elem: str) -> list[str]:
        """
        Split a Combined_Corrector into its sub-correctors

        :param elem: Name of the combined corrector element
        :return: Names of sub-corrector elements (if they exist) or the original element name
        """
        subs = [
            getattr(self[elem], attr, None)
            for attr in ("Horizontal_Corrector", "Vertical_Corrector")
        ]
        return [sub for sub in subs if sub is not None] or [elem]

    get_elements = _getter("elements")
    get_rf_cavities = _getter("RF cavities", "rf")
    get_diagnostics = _getter("diagnostic devices", "diagnostic")
    get_charge_diagnostics = _getter(
        "charge diagnostic devices", "diagnostic", ["FCM", "WCM", "ICT"]
    )
    get_beam_position_monitors = _getter("BPM devices", "diagnostic", "BPM")
    get_position_diagnostics = _getter(
        "position diagnostic devices", "diagnostic", ["Screen", "BPM"]
    )
    get_cameras = _getter(
        "camera devices",
        "diagnostic",
        "Screen",
        then=lambda self, screens: [self[s].diagnostic.camera_name for s in screens],
    )
    get_screens_and_cameras = _getter(
        "screen devices with their associated cameras",
        "diagnostic",
        "Screen",
        then=lambda self, screens: {s: self[s].diagnostic for s in screens},
        returns="Dict of screens with camera names",
    )
    get_magnets = _getter("magnets", "magnet")
    get_separate_magnets = _getter(
        "magnets, with combined correctors separated into their sub-correctors,",
        "magnet",
        then=_split_correctors,
        returns="List of magnet names",
    )
    get_quadrupoles = _getter("quadrupole magnets", "magnet", "quadrupole")
    get_dipoles = _getter("dipole magnets", "magnet", "dipole")
    get_correctors = _getter(
        "corrector magnets", "magnet", _CORRECTOR_TYPES, then=_split_correctors
    )
    get_horizontal_correctors = _getter(
        "horizontal corrector magnets",
        "magnet",
        ["combined_corrector", "horizontal_corrector"],
        then=_sub_corrector("Horizontal_Corrector"),
    )
    get_vertical_correctors = _getter(
        "vertical corrector magnets",
        "magnet",
        ["combined_corrector", "Vertical_Corrector"],
        then=_sub_corrector("Vertical_Corrector"),
    )
    get_lattice_correctors = _getter("corrector magnets", "magnet", _CORRECTOR_TYPES)
    get_combined_correctors = _getter(
        "combined corrector magnets", "magnet", ["combined_corrector"]
    )
    get_sextupoles = _getter("sextupole magnets", "magnet", "sextupole")
    get_solenoids = _getter("solenoid magnets", "magnet", "solenoid")
    get_vacuum_components = _getter("vacuum components", "vacuum")
    get_shutters = _getter("shutter devices", "vacuum", "shutter")

    all_elements = _all_paths(get_elements, "elements")
    all_rf_cavities = _all_paths(get_rf_cavities, "RF cavities")
    all_diagnostics = _all_paths(get_diagnostics, "diagnostic devices")
    all_charge_diagnostics = _all_paths(get_charge_diagnostics, "charge diagnostics")
    all_beam_position_monitors = _all_paths(get_beam_position_monitors, "BPM devices")
    all_position_diagnostics = _all_paths(
        get_position_diagnostics, "position diagnostic devices"
    )
    all_magnets = _all_paths(get_magnets, "magnets")
    all_quadrupoles = _all_paths(get_quadrupoles, "quadrupole magnets")
    all_dipoles = _all_paths(get_dipoles, "dipole magnets")
    all_combined_correctors = _all_paths(
        get_combined_correctors, "combined corrector magnets"
    )
    all_separate_magnets = _all_paths(get_separate_magnets, "separate magnets")
    all_correctors = _all_paths(get_correctors, "corrector magnets")
    all_horizontal_correctors = _all_paths(
        get_horizontal_correctors, "horizontal corrector magnets"
    )
    all_vertical_correctors = _all_paths(
        get_vertical_correctors, "vertical corrector magnets"
    )
    all_sextupoles = _all_paths(get_sextupoles, "sextupole magnets")
    all_solenoids = _all_paths(get_solenoids, "solenoid magnets")
    all_vacuum_components = _all_paths(get_vacuum_components, "vacuum components")
    all_shutters = _all_paths(get_shutters, "shutter elements")

    @property
    def all_cameras(self) -> list:
        """
        Get all camera devices in the machine
        :return: List of all camera device names
        """
        return [
            self[scr].diagnostic.camera_name
            for scr in _union(self, _getter("screens", "diagnostic", "Screen"))
        ]

    @property
    def all_screens_and_cameras(self) -> Dict:
        """
        Get all screens with their associated cameras in the machine
        :return: Dict of all screens with camera names
        """
        return {
            scr: self[scr].diagnostic.camera_name
            for scr in _union(self, _getter("screens", "diagnostic", "Screen"))
        }


for _name, _attr in vars(LAURA).items():
    if _name.startswith("get_") and getattr(_attr, "__name__", None) == "get":
        _attr.__name__, _attr.__qualname__ = _name, f"LAURA.{_name}"
del _name, _attr
