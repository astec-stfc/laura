"""
LAURA Main Module

The main class for handling a full particle accelerator lattice.
"""

import logging
import os
import glob
import types
from math import copysign
from itertools import chain
from typing import List, Dict, Any
from pydantic import field_validator, model_validator
from yaml.constructor import Constructor

_log = logging.getLogger("laura.machine")

from .models.physical import PhysicalElement, Position
from .models.elementList import MachineModel, baseElement, dot, chunks
from .models.element import Drift
from .Importers.YAML_Loader import (
    read_YAML_Combined_File,
    read_YAML_Element_File,
    LazyElementDict,
    fast_get_element_metadata,
)
import numpy as np
import time


def flatten(xss):
    """Flatten a list of lists."""
    return list(chain.from_iterable(xss))


def add_bool(self, node):
    return self.construct_scalar(node)


Constructor.add_constructor("tag:yaml.org,2002:bool", add_bool)


class LAURA(MachineModel):
    """
    LAURA Main Class

    The main class for handling a full particle accelerator lattice.
    """

    element_list: str | List[baseElement]
    """List containing all elements in the machine model, either as a path to a YAML file/directory 
    or as a list of element objects."""

    exclude_keys: List[str] | None = None
    """List of top-level keys to exclude when reading YAML files"""

    eager_mode: bool = False
    """Whether to load all elements into memory immediately (True) or use lazy loading (False, default)"""

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
            if hasattr(lattice, "data_files") and "master_lattice" not in data:
                data["master_lattice"] = lattice.data_files
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
                elems = read_YAML_Combined_File(el_list)
                values = {y.name: y for y in elems if hasattr(y, "name")}
                self.elements.update(values)
            elif os.path.isdir(el_list):
                files = glob.glob(
                    os.path.abspath(el_list + "/**/*.yaml"), recursive=True
                )
                filenames = {}
                for fn in files:
                    meta = fast_get_element_metadata(fn)
                    filenames[meta["name"]] = fn
                # Create lazy dict instead of loading all!
                if not self.eager_mode:
                    self.elements = LazyElementDict(
                        filenames, exclude_keys=self.exclude_keys
                    )
                else:
                    elems = [
                        read_YAML_Element_File(fn, exclude_keys=self.exclude_keys)
                        for fn in files
                    ]
                    self.elements.update(
                        {y.name: y for y in elems if isinstance(y, baseElement)}
                    )
        elif el_list:
            values = {y.name: y for y in el_list if hasattr(y, "name")}
            self.elements.update(values)

        # Call super after populating elements so _build_layouts can work
        super().model_post_init(__context)

    def createDrifts(
        self, end: str = None, start: str = None, path: str = None
    ) -> Dict:
        """
        Insert drifts into a sequence of 'elements'

        :param end: Name of the last element in the sequence
        :param start: Name of the first element in the sequence
        :param path: Name of the lattice path to use
        :return: Dictionary of elements with drifts inserted
        """
        positions = []
        originalelements = dict()
        elementno = 0
        newelements = dict()

        elements = self.elements_between(
            start=start, end=end, element_class=None, path=path
        )

        for name in elements:
            elem = self.elements[name]
            if elem.is_subelement():
                continue
            originalelements[name] = elem
            pos = elem.physical.start.array
            positions.append(pos)
            positions.append(elem.physical.end.array)
        positions = positions[1:]
        positions.append(positions[-1])
        driftdata = list(
            zip(iter(list(originalelements.items())), list(chunks(positions, 2)))
        )

        for e, d in driftdata:
            newelements[e[0]] = e[1]
            if len(d) > 1:
                x1, y1, z1 = d[0]
                x2, y2, z2 = d[1]
                try:
                    length = np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2 + (z2 - z1) ** 2)
                    vector = dot((d[1] - d[0]), [0, 0, 1])
                except Exception as exc:
                    _log.error("Drift calculation error near element '%s': %s", e[0], exc)
                    _log.debug("Position data: %s", d)
                    raise exc
                if round(length, 6) > 0:
                    elementno += 1
                    name = "drift" + str(elementno)
                    x, y, z = [(a + b) / 2.0 for a, b in zip(d[0], d[1])]
                    newdrift = Drift(
                        name=name,
                        machine_area=newelements[e[0]].machine_area,
                        hardware_class="Drift",
                        physical=PhysicalElement(
                            length=abs(round(copysign(length, vector), 6)),
                            middle=Position(x=x, y=y, z=z),
                            datum=Position(x=x, y=y, z=z),
                        ),
                    )
                    newelements[name] = newdrift
        return newelements

    def get_elements(
        self, end: str = None, start: str = None, path: str = None
    ) -> list[str]:
        """
        Get all elements between start and end

        :param end: Name of the last element in the sequence
        :param start: Name of the first element in the sequence
        :param path: Name of the lattice path to use
        :return: List of element names
        """
        return self.elements_between(
            start=start, end=end, element_class=None, path=path
        )

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
        elements = self.createDrifts(start=start, end=end, path=path)
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
                # A combined corrector is placed as a single physical element,
                # but get_horizontal_correctors()/get_vertical_correctors()
                # hand back the names of its individual H/V sub-elements
                # (separate control PVs at the same location) instead of the
                # combined corrector's own name. Those sub-names never appear
                # in the path's element list, so give them the parent's
                # s-position too.
                original = self.elements.get(elem)
                for sub_attr in ("Horizontal_Corrector", "Vertical_Corrector"):
                    sub_name = getattr(original, sub_attr, None)
                    if sub_name:
                        elem_s[sub_name] = elem_s[elem]
        return elem_s

    def get_rf_cavities(
        self, end: str = None, start: str = None, path: str = None
    ) -> list[str]:
        """
        Get all RF cavities between start and end

        :param end: Name of the last element in the sequence
        :param start: Name of the first element in the sequence
        :param path: Name of the lattice path to use
        :return: List of RF cavity names
        """
        return self.elements_between(
            start=start, end=end, element_class="rf", path=path
        )

    def get_diagnostics(
        self, end: str = None, start: str = None, path: str = None
    ) -> list[str]:
        """
        Get all diagnostic devices between start and end

        :param end: Name of the last element in the sequence
        :param start: Name of the first element in the sequence
        :param path: Name of the lattice path to use
        :return: List of diagnostic devices names
        """
        return self.elements_between(
            start=start, end=end, element_class="diagnostic", path=path
        )

    def get_charge_diagnostics(
        self, end: str = None, start: str = None, path: str = None
    ) -> list[str]:
        """
        Get all charge diagnostic devices between start and end

        :param end: Name of the last element in the sequence
        :param start: Name of the first element in the sequence
        :param path: Name of the lattice path to use
        :return: List of charge diagnostic devices names
        """
        return self.elements_between(
            start=start,
            end=end,
            element_class="diagnostic",
            element_type=["FCM", "WCM", "ICT"],
            path=path,
        )

    def get_beam_position_monitors(
        self, end: str = None, start: str = None, path: str = None
    ) -> list[str]:
        """
        Get all BPM devices between start and end

        :param end: Name of the last element in the sequence
        :param start: Name of the first element in the sequence
        :param path: Name of the lattice path to use
        :return: List of BPM devices names
        """
        return self.elements_between(
            start=start,
            end=end,
            element_class="diagnostic",
            element_type="BPM",
            path=path,
        )

    def get_position_diagnostics(
        self, end: str = None, start: str = None, path: str = None
    ) -> list[str]:
        """
        Get all position diagnostic devices between start and end

        :param end: Name of the last element in the sequence
        :param start: Name of the first element in the sequence
        :param path: Name of the lattice path to use
        :return: List of position diagnostic devices names
        """
        return self.elements_between(
            start=start,
            end=end,
            element_class="diagnostic",
            element_type=["Screen", "BPM"],
            path=path,
        )

    def get_cameras(
        self, end: str = None, start: str = None, path: str = None
    ) -> list[str]:
        """
        Get all camera devices between start and end

        :param end: Name of the last element in the sequence
        :param start: Name of the first element in the sequence
        :param path: Name of the lattice path to use
        :return: List of camera devices names
        """
        return [
            self[scr].diagnostic.camera_name
            for scr in self.elements_between(
                start=start,
                end=end,
                element_class="diagnostic",
                element_type="Screen",
                path=path,
            )
        ]

    def get_screens_and_cameras(
        self, end: str = None, start: str = None, path: str = None
    ) -> Dict[str, str]:
        """
        Get all screen devices with their associated cameras between start and end

        :param end: Name of the last element in the sequence
        :param start: Name of the first element in the sequence
        :param path: Name of the lattice path to use
        :return: Dict of screens with camera names
        """
        return {
            scr: self[scr].diagnostic
            for scr in self.elements_between(
                start=start,
                end=end,
                element_class="diagnostic",
                element_type="Screen",
                path=path,
            )
        }

    def get_magnets(
        self, end: str = None, start: str = None, path: str = None
    ) -> list[str]:
        """
        Get all magnets between start and end

        :param end: Name of the last element in the sequence
        :param start: Name of the first element in the sequence
        :param path: Name of the lattice path to use
        :return: List of magnet names
        """
        return self.elements_between(
            start=start, end=end, element_class="magnet", path=path
        )

    def get_separate_magnets(
        self, end: str = None, start: str = None, path: str = None
    ) -> list[str]:
        """
        Get all magnet between start and end and separate combined correctors into their sub-correctors

        :param end: Name of the last element in the sequence
        :param start: Name of the first element in the sequence
        :param path: Name of the lattice path to use
        :return: List of magnet names
        """
        magnets = self.get_magnets(end=end, start=start, path=path)
        return list(
            flatten(
                [(self.__get_combined_corrector_sub_correctors(c)) for c in magnets]
            )
        )

    def get_quadrupoles(
        self, end: str = None, start: str = None, path: str = None
    ) -> list[str]:
        """
        Get all quadrupole magnets between start and end

        :param end: Name of the last element in the sequence
        :param start: Name of the first element in the sequence
        :param path: Name of the lattice path to use
        :return: List of quadrupole magnet names
        """
        return self.elements_between(
            start=start,
            end=end,
            element_class="magnet",
            element_type="quadrupole",
            path=path,
        )

    def get_dipoles(
        self, end: str = None, start: str = None, path: str = None
    ) -> list[str]:
        """
        Get all dipole magnets between start and end

        :param end: Name of the last element in the sequence
        :param start: Name of the first element in the sequence
        :param path: Name of the lattice path to use
        :return: List of dipole magnet names
        """
        return self.elements_between(
            start=start,
            end=end,
            element_class="magnet",
            element_type="dipole",
            path=path,
        )

    def __get_combined_corrector_sub_correctors(self, elem: str) -> list[str]:
        """
        Split a Combined_Corrector into its sub-correctors

        :param elem: Name of the combined corrector element
        :return: Names of sub-corrector elements (if they exist) or the original element name
        """
        if (
            hasattr(self[elem], "Horizontal_Corrector")
            and self[elem].Horizontal_Corrector is not None
        ):
            if (
                hasattr(self[elem], "Vertical_Corrector")
                and self[elem].Vertical_Corrector is not None
            ):
                return [self[elem].Horizontal_Corrector, self[elem].Vertical_Corrector]
            else:
                return [self[elem].Horizontal_Corrector]
        elif (
            hasattr(self[elem], "Vertical_Corrector")
            and self[elem].Vertical_Corrector is not None
        ):
            return [self[elem].Vertical_Corrector]
        else:
            return [elem]

    def get_correctors(
        self, end: str = None, start: str = None, path: str = None
    ) -> list[str]:
        """
        Get all corrector magnets between start and end

        :param end: Name of the last element in the sequence
        :param start: Name of the first element in the sequence
        :param path: Name of the lattice path to use
        :return: List of corrector magnet names
        """
        correctors = self.elements_between(
            start=start,
            end=end,
            element_class="magnet",
            element_type=[
                "combined_corrector",
                "horizontal_corrector",
                "vertical_corrector",
            ],
            path=path,
        )
        return list(
            flatten(
                [(self.__get_combined_corrector_sub_correctors(c)) for c in correctors]
            )
        )

    def get_horizontal_correctors(
        self, end: str = None, start: str = None, path: str = None
    ) -> list[str]:
        """
        Get all horizontal corrector magnets between start and end

        :param end: Name of the last element in the sequence
        :param start: Name of the first element in the sequence
        :param path: Name of the lattice path to use
        :return: List of horizontal corrector magnet names
        """
        horizontal_correctors = self.elements_between(
            start=start,
            end=end,
            element_class="magnet",
            element_type=["combined_corrector", "horizontal_corrector"],
            path=path,
        )
        return [
            (
                self[c].Horizontal_Corrector
                if hasattr(self[c], "Horizontal_Corrector")
                and self[c].Horizontal_Corrector is not None
                else c
            )
            for c in horizontal_correctors
        ]

    def get_vertical_correctors(
        self, end: str = None, start: str = None, path: str = None
    ) -> list[str]:
        """
        Get all vertical corrector magnets between start and end

        :param end: Name of the last element in the sequence
        :param start: Name of the first element in the sequence
        :param path: Name of the lattice path to use
        :return: List of vertical corrector magnet names
        """
        vertical_correctors = self.elements_between(
            start=start,
            end=end,
            element_class="magnet",
            element_type=["combined_corrector", "Vertical_Corrector"],
            path=path,
        )
        return [
            (
                self[c].Vertical_Corrector
                if hasattr(self[c], "Vertical_Corrector")
                and self[c].Vertical_Corrector is not None
                else c
            )
            for c in vertical_correctors
        ]

    def get_lattice_correctors(
        self, end: str = None, start: str = None, path: str = None
    ) -> list[str]:
        """
        Get all corrector magnets between start and end

        :param end: Name of the last element in the sequence
        :param start: Name of the first element in the sequence
        :param path: Name of the lattice path to use
        :return: List of corrector magnet names
        """
        return self.elements_between(
            start=start,
            end=end,
            element_class="magnet",
            element_type=[
                "combined_corrector",
                "horizontal_corrector",
                "vertical_corrector",
            ],
            path=path,
        )

    def get_combined_correctors(
        self, end: str = None, start: str = None, path: str = None
    ) -> list[str]:
        """
        Get all combined corrector magnets between start and end

        :param end: Name of the last element in the sequence
        :param start: Name of the first element in the sequence
        :param path: Name of the lattice path to use
        :return: List of combined corrector magnet names
        """
        return self.elements_between(
            start=start,
            end=end,
            element_class="magnet",
            element_type=["combined_corrector"],
            path=path,
        )

    def get_sextupoles(
        self, end: str = None, start: str = None, path: str = None
    ) -> list[str]:
        """
        Get all sectupole magnets between start and end

        :param end: Name of the last element in the sequence
        :param start: Name of the first element in the sequence
        :param path: Name of the lattice path to use
        :return: List of sectupole magnet names
        """
        return self.elements_between(
            start=start,
            end=end,
            element_class="magnet",
            element_type="sextupole",
            path=path,
        )

    def get_solenoids(
        self, end: str = None, start: str = None, path: str = None
    ) -> list[str]:
        """
        Get all solenoid magnets between start and end

        :param end: Name of the last element in the sequence
        :param start: Name of the first element in the sequence
        :param path: Name of the lattice path to use
        :return: List of solenoid magnet names
        """
        return self.elements_between(
            start=start,
            end=end,
            element_class="magnet",
            element_type="solenoid",
            path=path,
        )

    def get_vacuum_components(
        self, end: str = None, start: str = None, path: str = None
    ) -> list[str]:
        """
        Get all vacuum components between start and end

        :param end: Name of the last element in the sequence
        :param start: Name of the first element in the sequence
        :param path: Name of the lattice path to use
        :return: List of vacuum component names
        """
        return self.elements_between(
            start=start, end=end, element_class="vacuum", path=path
        )

    def get_shutters(
        self, end: str = None, start: str = None, path: str = None
    ) -> list[str]:
        """
        Get all shutter devices between start and end

        :param end: Name of the last element in the sequence
        :param start: Name of the first element in the sequence
        :param path: Name of the lattice path to use
        :return: List of shutter devices names
        """
        return self.elements_between(
            start=start,
            end=end,
            element_class="vacuum",
            element_type="shutter",
            path=path,
        )

    def __all_elements(
        self,
        element_class: str | list | None = None,
        element_type: str | list | None = None,
    ) -> set:
        """
        Get a set of all elements of a given class and/or type

        :param element_class: Class of the element (e.g., 'magnet', 'rf', 'diagnostic')
        :param element_type: Type of the element (e.g., 'quadrupole', 'dipole', 'BPM')
        :return: Set of element names
        """
        return set(
            [
                elem
                for pathelems in [
                    self.elements_between(
                        start=None,
                        end=None,
                        element_class=element_class,
                        element_type=element_type,
                        path=path,
                    )
                    for path in self.lattices.keys()
                ]
                for elem in pathelems
            ]
        )

    @property
    def all_elements(self) -> set:
        """
        Get all elements in the machine
        :return: Set of all element names
        """
        return self.__all_elements()

    @property
    def all_rf_cavities(self) -> set:
        """
        Get all rf cavities in the machine
        :return: Set of all cavity names
        """
        return self.__all_elements(element_class="rf")

    @property
    def all_diagnostics(self) -> set:
        """
        Get all diagnostic devices in the machine
        :return: Set of all diagnostic device names
        """
        return self.__all_elements(element_class="diagnostic")

    @property
    def all_charge_diagnostics(self) -> set:
        """
        Get all charge diagnostics in the machine
        :return: Set of all charge diagnostic names
        """
        return self.__all_elements(
            element_class="diagnostic",
            element_type=["FCM", "WCM", "ICT"],
        )

    @property
    def all_beam_position_monitors(self) -> set:
        """
        Get all BPM devices in the machine
        :return: Set of all BPM names
        """
        return self.__all_elements(
            element_class="diagnostic",
            element_type="BPM",
        )

    @property
    def all_position_diagnostics(self) -> set:
        """
        Get all position diagnostic devices in the machine
        :return: Set of all position diagnostic device names
        """
        return self.__all_elements(
            element_class="diagnostic",
            element_type=["Screen", "BPM"],
        )

    @property
    def all_cameras(self) -> list:
        """
        Get all camera devices in the machine
        :return: List of all camera device names
        """
        return [
            self[scr].diagnostic.camera_name
            for scr in self.__all_elements(
                element_class="diagnostic",
                element_type="Screen",
            )
        ]

    @property
    def all_screens_and_cameras(self) -> Dict:
        """
        Get all screens with their associated cameras in the machine
        :return: Dict of all screens with camera names
        """
        return {
            scr: self[scr].diagnostic.camera_name
            for scr in self.__all_elements(
                element_class="diagnostic",
                element_type="Screen",
            )
        }

    @property
    def all_magnets(self) -> set:
        """
        Get all magnets in the machine
        :return: Set of all magnet names
        """
        return self.__all_elements(element_class="magnet")

    @property
    def all_quadrupoles(self) -> set:
        """
        Get all quadrupole magnets in the machine
        :return: Set of all quadrupole magnet names
        """
        return self.__all_elements(
            element_class="magnet",
            element_type="quadrupole",
        )

    @property
    def all_dipoles(self) -> set:
        """
        Get all dipole magnets in the machine
        :return: Set of all dipole magnet names
        """
        return self.__all_elements(
            element_class="magnet",
            element_type="dipole",
        )

    @property
    def all_combined_correctors(self) -> set:
        """
        Get all combined corrector magnets in the machine
        :return: Set of all combined corrector magnet names
        """
        return self.__all_elements(
            element_class="magnet",
            element_type="combined_corrector",
        )

    @property
    def all_separate_magnets(self) -> set:
        """
        Get all separate magnets in the machine
        :return: Set of all separate magnet names
        """
        return set(
            [
                elem
                for pathelems in [
                    self.get_separate_magnets(start=None, end=None, path=path)
                    for path in self.lattices.keys()
                ]
                for elem in pathelems
            ]
        )

    @property
    def all_correctors(self) -> set:
        """
        Get all corrector magnets in the machine
        :return: Set of all corrector magnet names
        """
        return set(
            [
                elem
                for pathelems in [
                    self.get_correctors(
                        start=None,
                        end=None,
                        path=path,
                    )
                    for path in self.lattices.keys()
                ]
                for elem in pathelems
            ]
        )

    @property
    def all_horizontal_correctors(self) -> set:
        """
        Get all horizontal corrector magnets in the machine
        :return: Set of all horizontal corrector magnet names
        """
        return set(
            [
                elem
                for pathelems in [
                    self.get_horizontal_correctors(
                        start=None,
                        end=None,
                        path=path,
                    )
                    for path in self.lattices.keys()
                ]
                for elem in pathelems
            ]
        )

    @property
    def all_vertical_correctors(self) -> set:
        """
        Get all vertical corrector magnets in the machine
        :return: Set of all vertical corrector magnet names
        """
        return set(
            [
                elem
                for pathelems in [
                    self.get_vertical_correctors(
                        start=None,
                        end=None,
                        path=path,
                    )
                    for path in self.lattices.keys()
                ]
                for elem in pathelems
            ]
        )

    @property
    def all_sextupoles(self) -> set:
        """
        Get all sextupole magnets in the machine
        :return: Set of all sextupole magnet names
        """
        return self.__all_elements(
            element_class="magnet",
            element_type="sextupole",
        )

    @property
    def all_solenoids(self) -> set:
        """
        Get all solenoid magnets in the machine
        :return: Set of all solenoid magnet names
        """
        return self.__all_elements(
            element_class="magnet",
            element_type="solenoid",
        )

    @property
    def all_vacuum_components(self) -> set:
        """
        Get all vacuum components in the machine
        :return: Set of all vacuum component names
        """
        return self.__all_elements(element_class="vacuum")

    @property
    def all_shutters(self) -> set:
        """
        Get all shutter elements in the machine
        :return: Set of all shutter element names
        """
        return self.__all_elements(
            element_class="vacuum",
            element_type="shutter",
        )
