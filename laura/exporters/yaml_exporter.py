import logging
import os
import yaml
from typing import Union, Literal, Optional
from ..models.element_list import MachineModel
from ..models.element import PhysicalElement
from ..models.magnetic import MagneticElement

_log = logging.getLogger("laura.exporter.yaml")

PositionMode = Literal["global", "s", "reference"]


def represent_tuple(dumper, data):
    return dumper.represent_sequence("tag:yaml.org,2002:seq", data)


yaml.add_representer(tuple, represent_tuple)


def _clean_export_data(data: dict, ele: PhysicalElement) -> dict:
    """Remove computed / internal fields and restore essential identification fields
    that may have been stripped by exclude_defaults."""
    # --- Essential identification fields (have subclass-level defaults) ---
    data["hardware_type"] = ele.hardware_type
    data["hardware_class"] = ele.hardware_class

    # --- Computed fields on PhysicalElement ---
    if "physical" in data and isinstance(data["physical"], dict):
        data["physical"].pop("_physical_angle", None)
        # exclude_defaults=True can silently drop 'middle' when it equals the
        # all-zero Position() default (e.g. an element sitting at the global
        # origin). If 's' is present, 'middle' must be too — otherwise this
        # element alone round-trips as s-only and conflicts with sibling
        # elements that do have 'middle', tripping the mixed-coordinate-
        # system check on reload.
        phys_dict = data["physical"]
        if "s" in phys_dict and "middle" not in phys_dict and ele.physical.middle is not None:
            phys_dict["middle"] = ele.physical.middle.model_dump(exclude_defaults=True)

    # --- Computed fields on MagneticElement / Dipole_Magnet ---
    if "magnetic" in data and isinstance(data["magnetic"], dict):
        data["magnetic"].pop("half_gap", None)
        data["magnetic"].pop("rho", None)
        # Restore order (subclass default matches actual value, but useful in YAML)
        if hasattr(ele, "magnetic") and isinstance(ele.magnetic, MagneticElement):
            data["magnetic"]["order"] = ele.magnetic.order

    # --- Empty alias (Aliases([]) serialises as {} or []) ---
    alias = data.get("alias")
    if isinstance(alias, (dict, list)) and not alias:
        data.pop("alias", None)

    return data


def _apply_position_mode(
    dump: dict,
    ele,
    mode: PositionMode,
    prev_name: Optional[str] = None,
    prev_ele=None,
) -> dict:
    """Replace the physical positioning data in-place using the requested mode.

    ``"global"`` (default) — keep existing ``middle`` / Cartesian output.
    ``"s"``      — replace ``middle`` with arc-length ``s`` value.
    ``"reference"`` — replace ``middle`` with a ``reference_placement``
                      using ``s_offset`` relative to *prev_ele* (arc-length
                      from prev element's exit to this element's middle).
                      Falls back to ``"s"`` when no previous element is
                      available (i.e. the first element in a section).
    """
    if mode == "global":
        return dump

    phys = getattr(ele, "physical", None)
    if phys is None or "physical" not in dump:
        return dump

    phys_dict = dump["physical"]

    if mode == "s":
        if phys.s is not None:
            phys_dict.pop("middle", None)
            phys_dict["s"] = round(phys.s, 6)
            if phys.s_point != "middle":
                phys_dict["s_point"] = phys.s_point

    elif mode == "reference":
        prev_phys = getattr(prev_ele, "physical", None) if prev_ele is not None else None
        if (
            prev_name is not None
            and prev_phys is not None
            and phys.s is not None
            and prev_phys.s is not None
        ):
            # Arc-length from prev element's exit (s_mid + L/2) to this element's middle.
            # ReferencePlacement.point defaults to "end", so LAURA resolves from prev.end.
            s_offset = round(phys.s - (prev_phys.s + prev_phys.length / 2.0), 6)
            phys_dict.pop("middle", None)
            phys_dict["reference_placement"] = {
                "element": prev_name,
                "s_offset": s_offset,
            }
        elif phys.s is not None:
            # First element in its section — no predecessor, fall back to s-coordinate.
            phys_dict.pop("middle", None)
            phys_dict["s"] = round(phys.s, 6)
            if phys.s_point != "middle":
                phys_dict["s_point"] = phys.s_point

    return dump


def _iter_section_order(machine: MachineModel):
    """Yield ``(name, elem, prev_name, prev_elem)`` in section order.

    Each element appears at most once (first section occurrence wins).
    Elements not referenced by any section are yielded last without a
    predecessor.
    """
    seen: set = set()
    for section in machine.sections.values():
        prev_name: Optional[str] = None
        prev_elem = None
        for name in section.order:
            if name in seen:
                continue
            elem = machine.elements.get(name)
            if elem is None:
                continue
            seen.add(name)
            yield name, elem, prev_name, prev_elem
            prev_name = name
            prev_elem = elem
    for name, elem in machine.elements.items():
        if name not in seen and elem is not None:
            yield name, elem, None, None


def export_as_yaml(
    filename: Union[str, None],
    ele,
    position_mode: PositionMode = "global",
    *,
    prev_name: Optional[str] = None,
    prev_ele=None,
) -> Union[dict, None]:
    """Export a single element as YAML.

    Parameters
    ----------
    filename:
        Output path, or ``None`` to return the dict instead of writing.
    ele:
        Element to export.
    position_mode:
        How to represent the physical position:

        ``"global"`` (default)
            Cartesian ``middle: {x, y, z}`` coordinates.
        ``"s"``
            Arc-length ``s: <float>`` value (requires a resolved trajectory).
        ``"reference"``
            ``reference_placement`` with ``s_offset`` relative to *prev_ele*.
            The first element of a section (no predecessor) falls back to
            ``"s"`` mode.
    prev_name:
        Name of the preceding element in section order (used by
        ``"reference"`` mode).
    prev_ele:
        Preceding element object (used by ``"reference"`` mode).
    """
    try:
        dump = ele.base_model_dump(exclude_defaults=True)
    except Exception:
        dump = ele.base_model_dump()
    dump.pop("CASCADING_RULES", None)
    dump = _clean_export_data(dump, ele)
    dump = _apply_position_mode(dump, ele, position_mode, prev_name, prev_ele)
    if filename is not None:
        with open(filename, "w") as yaml_file:
            yaml.default_flow_style = False
            yaml.dump(dump, yaml_file)
    else:
        return dump


def export_machine_combined_file(
    path: str,
    machine: MachineModel,
    position_mode: PositionMode = "global",
) -> None:
    """Export all elements to a single combined ``summary.yaml``.

    Parameters
    ----------
    path:
        Directory in which to write ``summary.yaml``.
    machine:
        Machine model to export.
    position_mode:
        Position representation — ``"global"`` (default), ``"s"``, or
        ``"reference"`` (each element relative to its section predecessor).
    """
    filename = os.path.join(path, "summary.yaml")
    os.makedirs(path, exist_ok=True)
    combined_yaml = {}
    for name, elem, prev_name, prev_elem in _iter_section_order(machine):
        combined_yaml[name] = export_as_yaml(
            None, elem, position_mode, prev_name=prev_name, prev_ele=prev_elem
        )
    with open(filename, "w") as yaml_file:
        yaml.default_flow_style = True
        yaml.dump(combined_yaml, yaml_file)


def export_machine(
    path: str,
    machine: MachineModel,
    overwrite: bool = False,
    verbose: bool = False,
    position_mode: PositionMode = "global",
) -> None:
    """Export each element to its own YAML file.

    Parameters
    ----------
    path:
        Root output directory.  Sub-directories mirror ``elem.subdirectory``.
    machine:
        Machine model to export.
    overwrite:
        Overwrite existing files when ``True`` (default ``False``).
    verbose:
        Log each file path at DEBUG level.
    position_mode:
        Position representation — ``"global"`` (default), ``"s"``, or
        ``"reference"`` (each element relative to its section predecessor).
    """
    os.makedirs(path, exist_ok=True)
    for name, elem, prev_name, prev_elem in _iter_section_order(machine):
        directory = os.path.join(path, elem.subdirectory)
        os.makedirs(directory, exist_ok=True)
        filename = os.path.join(directory, elem.name + ".yaml")
        if overwrite or not os.path.isfile(filename):
            if verbose:
                _log.debug("Exporting element '%s' to file '%s'", name, filename)
            export_as_yaml(
                filename, elem, position_mode, prev_name=prev_name, prev_ele=prev_elem
            )


def export_elements(
    path: str,
    elements: list,
    position_mode: PositionMode = "global",
) -> None:
    """Export a list of elements to individual YAML files.

    Parameters
    ----------
    path:
        Root output directory.
    elements:
        Ordered list of elements to export.
    position_mode:
        Position representation — ``"global"`` (default), ``"s"``, or
        ``"reference"`` (each element relative to its predecessor in the list).
    """
    prev_name: Optional[str] = None
    prev_elem = None
    for elem in elements:
        if elem is None:
            continue
        directory = os.path.join(path, elem.subdirectory)
        os.makedirs(directory, exist_ok=True)
        filename = os.path.join(directory, elem.name + ".yaml")
        export_as_yaml(
            filename, elem, position_mode, prev_name=prev_name, prev_ele=prev_elem
        )
        prev_name = elem.name
        prev_elem = elem
