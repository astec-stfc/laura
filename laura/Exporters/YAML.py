import logging
import os
import shutil
import yaml
from warnings import warn
from typing import Union, Literal, Optional
from ..models.elementList import MachineModel
from ..models.element import PhysicalElement
from ..models.magnetic import MagneticElement
from ..Importers.YAML_Loader import (
    COMBINED_SCHEMAS_KEY,
    collapse_controls_schema,
    get_controls_schema_variables,
    resolve_controls_schema_path,
)

_log = logging.getLogger("laura.exporter.yaml")

PositionMode = Literal["global", "s", "reference"]


def _schema_base_dirs(schema_root: Union[str, None], ele: PhysicalElement):
    """Try flat schema roots before the legacy per-element directory layout."""
    if schema_root is None:
        return (None,)
    return (schema_root, os.path.join(schema_root, ele.subdirectory))


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


def _collapse_dump_controls(
    dump: dict, ele: PhysicalElement, schema_root: Union[str, None]
) -> None:
    """
    If ``dump['controls']`` names a ``schema`` and that schema can be found,
    replace its fully-expanded ``variables`` with the minimal override form
    (see :func:`laura.Importers.YAML_Loader.collapse_controls_schema`),
    mutating ``dump`` in place. If the schema can't be located, the `variables`
    dump is already fully expanded (nothing to collapse), so the dangling
    `schema`/`identifier_pattern` reference is dropped instead of left in
    place -- otherwise reloading the export would try (and fail) to resolve
    it again despite `variables` already being complete.
    """
    controls = dump.get("controls")
    if not isinstance(controls, dict) or not controls.get("schema"):
        return
    error = None
    for base_dir in _schema_base_dirs(schema_root, ele):
        try:
            schema_variables = get_controls_schema_variables(controls["schema"], base_dir)
            break
        except FileNotFoundError as exc:
            error = exc
    else:
        warn(f"Cannot collapse controls schema for {ele.name}: {error}")
        dump["controls"] = {
            k: v for k, v in controls.items() if k not in ("schema", "identifier_pattern")
        }
        return
    live_variables = ele.controls.variables if ele.controls is not None else None
    dump["controls"] = collapse_controls_schema(
        controls, ele.name, schema_variables, live_variables=live_variables
    )


def _copy_controls_schema(
    ele: PhysicalElement, schema_root: Union[str, None], destination_dir: str, copied: set
) -> None:
    """Copy the schema file `ele.controls` references into `destination_dir`
    (once per destination path), so an exported tree using `collapse_schema`
    is loadable on its own without depending on the original lattice's schema
    files still being where they were."""
    controls = getattr(ele, "controls", None)
    schema_ref = getattr(controls, "schema_", None) if controls is not None else None
    if not schema_ref:
        return
    dest_path = os.path.join(destination_dir, schema_ref)
    if dest_path in copied:
        return
    copied.add(dest_path)
    error = None
    for base_dir in _schema_base_dirs(schema_root, ele):
        try:
            src_path = resolve_controls_schema_path(schema_ref, base_dir)
            break
        except FileNotFoundError as exc:
            error = exc
    else:
        warn(f"Cannot copy controls schema for {ele.name}: {error}")
        return
    if os.path.abspath(src_path) == os.path.abspath(dest_path):
        return
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    shutil.copyfile(src_path, dest_path)


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
    collapse_schema: bool = False,
    schema_root: Union[str, None] = None,
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
    collapse_schema:
        If True and `ele.controls` names a schema (see
        `laura.models.control.ControlsInformation.schema_`), write
        `controls` back out as `{schema, identifier_pattern, variables}`
        with only the per-element overrides -- the same compact form the
        lattice may have been loaded from -- instead of the fully
        expanded `variables` dict. Disabled by default; falls back to the
        full expansion (with a warning) if the schema can't be found.
    schema_root:
        The YAML root the schema path in `controls.schema` is
        relative to (typically the directory the lattice was loaded
        from); required for `collapse_schema` to find anything to diff
        against.
    """
    try:
        dump = ele.base_model_dump(exclude_defaults=True)
    except Exception:
        dump = ele.base_model_dump()
    dump.pop("CASCADING_RULES", None)
    dump = _clean_export_data(dump, ele)
    dump = _apply_position_mode(dump, ele, position_mode, prev_name, prev_ele)
    if collapse_schema:
        _collapse_dump_controls(dump, ele, schema_root)
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
    collapse_schema: bool = False,
    schema_root: Union[str, None] = None,
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
    collapse_schema:
        If True, elements referencing a controls schema are
        written in collapsed form (see `export_as_yaml`), and the schemas
        they use are embedded in the combined file itself under the
        reserved `laura.Importers.YAML_Loader.COMBINED_SCHEMAS_KEY` key,
        so the file is self-contained -- loadable via
        `read_YAML_Combined_File` with no companion `_schema.yaml` files
        needed. Falls back to full expansion (with a warning) for any
        element whose schema can't be found.
    schema_root:
        As `export_as_yaml`; defaults to `machine.element_list`
        when that is a directory path.
    """
    filename = os.path.join(path, "summary.yaml")
    os.makedirs(path, exist_ok=True)
    if collapse_schema and schema_root is None and isinstance(
        getattr(machine, "element_list", None), str
    ):
        schema_root = machine.element_list

    embedded_schemas = {}
    combined_yaml = {}
    for name, elem, prev_name, prev_elem in _iter_section_order(machine):
        combined_yaml[name] = export_as_yaml(
            None, elem, position_mode, prev_name=prev_name, prev_ele=prev_elem
        )
    for name, elem in machine.elements.items():
        if elem is None:
            continue
        dump = export_as_yaml(None, elem)
        if collapse_schema:
            controls = dump.get("controls")
            if isinstance(controls, dict) and controls.get("schema"):
                schema_ref = controls["schema"]
                combined_key = os.path.join(elem.subdirectory, schema_ref)
                if combined_key not in embedded_schemas:
                    error = None
                    for base_dir in _schema_base_dirs(schema_root, elem):
                        try:
                            embedded_schemas[combined_key] = get_controls_schema_variables(
                                schema_ref, base_dir
                            )
                            break
                        except FileNotFoundError as exc:
                            error = exc
                    else:
                        warn(f"Cannot embed controls schema for {elem.name}: {error}")
                        embedded_schemas[combined_key] = None
                if embedded_schemas.get(combined_key) is not None:
                    live_variables = elem.controls.variables if elem.controls is not None else None
                    dump["controls"] = collapse_controls_schema(
                        {**controls, "schema": combined_key},
                        elem.name,
                        embedded_schemas[combined_key],
                        live_variables=live_variables,
                    )
                else:
                    dump["controls"] = {
                        k: v for k, v in controls.items()
                        if k not in ("schema", "identifier_pattern")
                    }
        combined_yaml[name] = dump

    embedded_schemas = {k: v for k, v in embedded_schemas.items() if v is not None}
    if embedded_schemas:
        combined_yaml[COMBINED_SCHEMAS_KEY] = embedded_schemas

    with open(filename, "w") as yaml_file:
        yaml.default_flow_style = True
        yaml.dump(combined_yaml, yaml_file)


def export_machine(
    path: str,
    machine: MachineModel,
    overwrite: bool = False,
    verbose: bool = False,
    position_mode: PositionMode = "global",
    collapse_schema: bool = False,
    schema_root: Union[str, None] = None,
    copy_schemas: bool = True,
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
    collapse_schema:
        As `export_as_yaml`.
    schema_root:
        As `export_as_yaml`; defaults to `machine.element_list`
        when that is a directory path.
    copy_schemas:
        When `collapse_schema` is set, also copy each schema
        file referenced into the corresponding destination subdirectory
        (once each), so the exported tree is loadable on its own.
    """
    os.makedirs(path, exist_ok=True)
    if collapse_schema and schema_root is None and isinstance(
        getattr(machine, "element_list", None), str
    ):
        schema_root = machine.element_list
    copied_schemas = set()
    for name, elem, prev_name, prev_elem in _iter_section_order(machine):
        directory = os.path.join(path, elem.subdirectory)
        os.makedirs(directory, exist_ok=True)
        filename = os.path.join(directory, elem.name + ".yaml")
        if overwrite or not os.path.isfile(filename):
            if verbose:
                _log.debug("Exporting element '%s' to file '%s'", name, filename)
            export_as_yaml(
                filename,
                elem,
                position_mode,
                prev_name=prev_name,
                prev_ele=prev_elem,
                collapse_schema=collapse_schema,
                schema_root=schema_root,
            )
            if collapse_schema and copy_schemas:
                _copy_controls_schema(elem, schema_root, directory, copied_schemas)


def export_elements(
    path: str,
    elements: list,
    position_mode: PositionMode = "global",
    collapse_schema: bool = False,
    schema_root: Union[str, None] = None,
    copy_schemas: bool = True,
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
    collapse_schema:
        As `export_as_yaml`.
    schema_root:
        As `export_as_yaml`.
    copy_schemas:
        As `export_machine`.
    """
    copied_schemas = set()
    prev_name: Optional[str] = None
    prev_elem = None
    for elem in elements:
        if elem is None:
            continue
        directory = os.path.join(path, elem.subdirectory)
        os.makedirs(directory, exist_ok=True)
        filename = os.path.join(directory, elem.name + ".yaml")
        export_as_yaml(
            filename,
            elem,
            position_mode,
            prev_name=prev_name,
            prev_ele=prev_elem,
            collapse_schema=collapse_schema,
            schema_root=schema_root,
        )
        if collapse_schema and copy_schemas:
            _copy_controls_schema(elem, schema_root, directory, copied_schemas)
        prev_name = elem.name
        prev_elem = elem
