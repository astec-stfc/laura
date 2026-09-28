"""Tidying for the YAML exporter: what makes an imported machine readable on disk.

An importer hands over exactly what the source code computed.
Each helper here makes the importer more sensible; `export_machine` switches them on
with ``round_floats``, ``field_directory`` and ``auto_templates``.
"""

import collections
import hashlib
import math
import os
from typing import Dict, Iterable, Optional, Tuple

import numpy as np
from scipy.constants import speed_of_light

from ..importers.yaml_loader import NON_INHERITED_FIELDS
from ..translator.utils.fields import FieldMap
from ..translator.utils.fields.field_parameter import FieldParameter

POSITION_DECIMALS = 10
"""Decimal places (metres) kept on positions, ``s`` and lengths: 0.1 nm."""

SIGNIFICANT_FIGURES = 12
"""Significant figures kept on every other float."""

NEGLIGIBLE = 1e-12
"""Anything smaller in magnitude is written as zero."""


def _round(value: float, decimals: Optional[int]) -> float:
    if not math.isfinite(value):
        return value
    if decimals is None:
        value = float(f"{value:.{SIGNIFICANT_FIGURES}g}")
    else:
        value = round(value, decimals)
    return 0.0 if abs(value) < NEGLIGIBLE else value


def _round_in_place(obj, decimals: Optional[int] = None):
    from pydantic import BaseModel

    from ..models.physical import PhysicalElement, Position

    if isinstance(obj, bool) or obj is None:
        return obj
    if isinstance(obj, (float, np.floating)):
        return _round(float(obj), decimals)
    if isinstance(obj, np.ndarray) and obj.dtype.kind == "f":
        return np.vectorize(lambda v: _round(float(v), decimals), otypes=[float])(obj)
    if isinstance(obj, list):
        obj[:] = [_round_in_place(v, decimals) for v in obj]
    elif isinstance(obj, dict):
        for key, value in obj.items():
            obj[key] = _round_in_place(value, decimals)
    elif isinstance(obj, BaseModel) and not isinstance(obj, FieldMap):
        for field in type(obj).model_fields:
            value = getattr(obj, field, None)
            places = decimals
            if isinstance(obj, Position) or (
                isinstance(obj, PhysicalElement) and field in ("s", "length")
            ):
                places = POSITION_DECIMALS
            cleaned = _round_in_place(value, places)
            if cleaned is not value and not np.array_equal(cleaned, value):
                object.__setattr__(obj, field, cleaned)
    return obj


def rounded(element):
    """A copy of element with the floating-point noise taken out."""
    copy = _round_in_place(element.model_copy(deep=True))
    cavity = getattr(element, "cavity", None)
    physical = getattr(element, "physical", None)
    frequency = getattr(cavity, "frequency", None)
    n_cells = getattr(cavity, "n_cells", None)
    if frequency and n_cells and physical is not None and physical.length:
        cells = n_cells * speed_of_light / (2 * frequency)
        if copy.physical.length < cells <= physical.length * (1 + 1e-12):
            object.__setattr__(copy.physical, "length", physical.length)
    return copy


_FIELD_SUFFIXES = {"field_definition": "field", "wakefield_definition": "wake"}


def _field_key(field: FieldMap) -> str:
    """A digest of everything the HDF5 field file keeps."""
    digest = hashlib.sha1()
    for name in FieldMap.model_fields:
        value = getattr(field, name, None)
        if name in ("filename", "read") or value is None:
            continue
        samples = value.value if isinstance(value, FieldParameter) else value
        if isinstance(samples, (np.ndarray, list, tuple)):
            digest.update(name.encode() + np.asarray(samples, dtype=float).tobytes())
        else:
            digest.update(f"{name}={samples!r}".encode())
    return digest.hexdigest()


def externalise_shared_fields(
    elements: Iterable, directory: str, reference: Optional[str] = None
) -> Dict[str, Dict[str, str]]:
    """
    Write every field held as samples to *directory*, once per distinct field.

    Parameters
    ----------
    elements:
        The elements to look through.
    directory:
        Where the files go.
    reference:
        What the elements call *directory*, e.g. ``"$master_lattice$Data_Files/"``.
        Defaults to its absolute path.

    Returns
    -------
    dict
        ``element name -> {slot: file name}``, for the caller to put in place of
        the samples.
    """
    groups: Dict[Tuple[str, str], list] = collections.defaultdict(list)
    for elem in elements:
        simulation = getattr(elem, "simulation", None)
        for slot in _FIELD_SUFFIXES:
            field = getattr(simulation, slot, None)
            if isinstance(field, FieldMap) and field.read:
                groups[(slot, _field_key(field))].append(elem)
    if not groups:
        return {}

    os.makedirs(directory, exist_ok=True)
    if reference is None:
        reference = os.path.abspath(directory) + os.sep
    used: set = set()
    names: Dict[str, Dict[str, str]] = collections.defaultdict(dict)
    for (slot, _), members in groups.items():
        first = members[0]
        if len(members) == 1:
            stem = f"{first.name}_{_FIELD_SUFFIXES[slot]}"
        else:
            family = first.hardware_model or first.hardware_type
            length = getattr(getattr(first, "physical", None), "length", None) or 0.0
            stem = f"{family}_{length:g}m_{_FIELD_SUFFIXES[slot]}"
        unique, number = stem, 1
        while unique in used:
            number += 1
            unique = f"{stem}_{number}"
        used.add(unique)
        field = getattr(first.simulation, slot).model_copy(deep=True)
        field.filename = os.path.join(os.path.abspath(directory), unique + ".hdf5")
        written = field.write_field_file("hdf5") or field.filename
        for elem in members:
            names[elem.name][slot] = reference + os.path.basename(written)
    return dict(names)


TEMPLATE_MIN_MEMBERS = 4
"""Families smaller than this get no template."""

TEMPLATE_MIN_SAVING = 6
"""Nor do families whose template would save fewer keys than this per member."""

_IDENTITY_KEYS = ("controls", "hardware_class", "hardware_type", "hardware_model")


def _plain(value):
    if hasattr(value, "tolist"):
        return value.tolist()
    if isinstance(value, (list, tuple)):
        return [_plain(v) for v in value]
    return value


def _leaves(tree: dict, path: tuple = ()):
    """``(path, value)`` for every non-empty leaf an element could inherit."""
    for key, value in tree.items():
        if not path and (key in NON_INHERITED_FIELDS or key in _IDENTITY_KEYS):
            continue
        rule = NON_INHERITED_FIELDS.get(path[0]) if path else None
        if len(path) == 1 and rule and key in rule:
            continue
        if isinstance(value, dict):
            if value:
                yield from _leaves(value, path + (key,))
        else:
            yield path + (key,), _plain(value)


def family_templates(dumps: Dict[str, Tuple[object, dict]]):
    """Templates for the families of identical devices among *dumps*.
    A family is every element sharing a type, model and length.

    Parameters
    ----------
    dumps:
        ``name -> (element, its YAML dump)``, in section order.

    Returns
    -------
    ``(templates, members)``: ``template name -> raw definition``, and
    ``element name -> template name``.
    """
    families = collections.defaultdict(list)
    for name, (elem, dump) in dumps.items():
        if elem.hardware_type == "Drift" or dump.get("inherits_from"):
            continue
        length = getattr(getattr(elem, "physical", None), "length", None) or 0.0
        families[(elem.hardware_type, elem.hardware_model, round(length, 6))].append(
            (name, elem, dump)
        )

    templates: dict = {}
    members: Dict[str, str] = {}
    for (hardware_type, hardware_model, length), family in families.items():
        if len(family) < TEMPLATE_MIN_MEMBERS:
            continue
        leaves = [dict(_leaves(dump)) for _, _, dump in family]
        shared = {}
        for path in set(leaves[0]).intersection(*leaves[1:]):
            counts = collections.Counter(repr(leaf[path]) for leaf in leaves)
            text, count = counts.most_common(1)[0]
            if count * 2 >= len(family):
                shared[path] = next(
                    leaf[path] for leaf in leaves if repr(leaf[path]) == text
                )
        saving = sum(
            leaf[path] == value for leaf in leaves for path, value in shared.items()
        ) / len(family)
        if saving < TEMPLATE_MIN_SAVING:
            continue
        model_part = (
            f"_{hardware_model}"
            if hardware_model and hardware_model != "Generic"
            else ""
        )
        template_name = f"{hardware_type}{model_part}_L{length:g}".replace(".", "p")
        first = family[0][1]
        template = {
            "name": template_name,
            "hardware_class": first.hardware_class,
            "hardware_type": hardware_type,
        }
        if hardware_model:
            template["hardware_model"] = hardware_model
        for path, value in sorted(shared.items()):
            node = template
            for key in path[:-1]:
                node = node.setdefault(key, {})
            node[path[-1]] = value
        templates[template_name] = template
        for name, _, _ in family:
            members[name] = template_name
    return templates, members
