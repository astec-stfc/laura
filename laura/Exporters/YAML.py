import glob
import logging
import os
import shutil
from typing import Literal, Optional, Union
from warnings import warn

import yaml

from ..Importers.YAML_Loader import (
    COMBINED_SCHEMAS_KEY,
    COMBINED_TEMPLATES_KEY,
    INHERIT_KEYS,
    NON_INHERITED_FIELDS,
    RawFileNamespace,
    collapse_controls_schema,
    collect_template_filenames,
    get_controls_schema_variables,
    resolve_controls_schema_path,
    resolve_inheritance,
)
from ..models.element import PhysicalElement
from ..models.elementList import MachineModel
from ..models.magnetic import MagneticElement

_log = logging.getLogger("laura.exporter.yaml")

PositionMode = Literal["global", "s", "reference", "sequential"]

_ABUT_TOLERANCE = 1e-9


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
        if (
            "s" in phys_dict
            and "middle" not in phys_dict
            and ele.physical.middle is not None
        ):
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


def _is_empty(value) -> bool:
    """True for a value that says nothing: ``None`` or an empty container.

    ``0``, ``0.0``, ``False`` and ``""`` are values someone may have written and
    are never empty by this test.
    """
    if value is None:
        return True
    return isinstance(value, (dict, list, tuple, set)) and not value


_MEANINGFUL_WHEN_EMPTY = frozenset(
    {
        "physical.middle",
        "physical.position",
        "physical.centre",
        "physical.datum",
        "physical.reference_placement",
    }
)

_MULTIPOLE_SLOTS = "magnetic.multipoles"


def _prune_empty(data: dict, path: str = "") -> dict:
    """Drop the keys that carry nothing, depth-first.

    ``exclude_defaults=True`` drops a field equal to its default, but a
    sub-model whose own fields are all defaults is not equal to anything and
    dumps as ``{}``. These are removed, except if they are in
    `_MEANINGFUL_WHEN_EMPTY`.

    List *entries* are recursed into but never removed -- position matters in a
    list, and an empty entry is a hole, not an absence.
    """
    pruned = {}
    for key, value in data.items():
        here = f"{path}.{key}" if path else key
        if isinstance(value, dict):
            value = _prune_empty(value, here)
        elif isinstance(value, (list, tuple)):
            value = [
                _prune_empty(item, here) if isinstance(item, dict) else item
                for item in value
            ]
        if (
            path == _MULTIPOLE_SLOTS
            and isinstance(value, dict)
            and set(value) == {"order"}
        ):
            continue
        if _is_empty(value) and here not in _MEANINGFUL_WHEN_EMPTY:
            continue
        pruned[key] = value
    return pruned


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
            schema_variables = get_controls_schema_variables(
                controls["schema"], base_dir
            )
            break
        except FileNotFoundError as exc:
            error = exc
    else:
        warn(f"Cannot collapse controls schema for {ele.name}: {error}")
        dump["controls"] = {
            k: v
            for k, v in controls.items()
            if k not in ("schema", "identifier_pattern")
        }
        return
    live_variables = ele.controls.variables if ele.controls is not None else None
    dump["controls"] = collapse_controls_schema(
        controls, ele.name, schema_variables, live_variables=live_variables
    )


def _template_namespace(template_root: Union[str, None]):
    """``name -> raw element dict`` for whatever an ``inherits_from`` may name.

    Mirrors what the loader builds during import: the ``_templates`` block plus
    the ordinary elements of a combined file, or every named element file in a
    directory.
    """
    if not template_root or not os.path.exists(template_root):
        return None
    if os.path.isfile(template_root):
        try:
            with open(template_root, "r") as stream:
                raw = yaml.safe_load(stream) or {}
        except Exception as error:
            _log.debug("Cannot read templates from %s: %s", template_root, error)
            return None
        if not isinstance(raw, dict):
            return None
        namespace = {
            name: value
            for name, value in raw.items()
            if isinstance(value, dict) and not name.startswith("_")
        }
        namespace.update(raw.get(COMBINED_TEMPLATES_KEY) or {})
        return namespace
    files = sorted(
        glob.glob(
            os.path.join(os.path.abspath(template_root), "**", "*.yaml"), recursive=True
        )
        + glob.glob(
            os.path.join(os.path.abspath(template_root), "**", "*.yml"), recursive=True
        )
    )
    return RawFileNamespace(collect_template_filenames(files))


def _strip_inherited(dump: dict, parent: dict, excluded) -> None:
    """Remove from *dump* every key the parent already supplies identically.

    Anything in *excluded* is left alone however well it matches:
    those keys are never inherited, so dropping one would lose it outright
    rather than shorten it.
    """
    for key, parent_value in parent.items():
        if key not in dump or key in INHERIT_KEYS:
            continue
        rule = excluded.get(key, _INHERITABLE)
        if rule is None:  # the whole key is never inherited
            continue
        child_value = dump[key]
        if isinstance(child_value, dict) and isinstance(parent_value, dict):
            nested = {} if rule is _INHERITABLE else {name: None for name in rule}
            _strip_inherited(child_value, parent_value, nested)
            if not child_value:
                dump.pop(key)
        elif child_value == parent_value:
            dump.pop(key)


def _collapse_dump_inheritance(dump: dict, ele, namespace) -> Optional[str]:
    """Write the element as ``inherits_from`` plus only what differs.

    The inverse of :func:`~laura.Importers.YAML_Loader.resolve_inheritance`.

    Returns the name of the parent it collapsed against, so a caller writing a
    self-contained file knows which definitions it has to carry with it, or
    ``None`` when the dump was left expanded.
    """
    parent_name = next(
        (dump[key] for key in INHERIT_KEYS if dump.get(key) is not None), None
    )
    if parent_name is None:
        return None
    for key in INHERIT_KEYS:
        dump.pop(key, None)

    parent_raw = namespace.get(parent_name) if namespace is not None else None
    if not isinstance(parent_raw, dict):
        warn(
            f"Cannot collapse inheritance for {ele.name}: no definition of "
            f"'{parent_name}' was found, so it is written out in full."
        )
        return None

    try:
        parent = resolve_inheritance(dict(parent_raw), namespace)
    except Exception as error:  # a parent whose own chain is broken
        warn(f"Cannot collapse inheritance for {ele.name}: {error}")
        return None

    _strip_inherited(dump, parent, NON_INHERITED_FIELDS)
    dump["inherits_from"] = parent_name
    return parent_name


def _gather_template_chain(name: Optional[str], namespace, collected: dict) -> None:
    """Add *name* and everything it in turn inherits from to *collected*.

    A collapsed element is only loadable where its parent is, and a parent may
    itself be a child. Walking the chain is what makes an export carrying its
    templates self-contained rather than self-contained one level deep.
    """
    while name is not None and name not in collected:
        raw = namespace.get(name) if namespace is not None else None
        if not isinstance(raw, dict):
            return
        collected[name] = raw
        name = next(
            (raw[key] for key in INHERIT_KEYS if raw.get(key) is not None), None
        )


def _copy_controls_schema(
    ele: PhysicalElement,
    schema_root: Union[str, None],
    destination_dir: str,
    copied: set,
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


def _copy_templates(
    dump: dict, namespace, destination_root: str, namespace_copy: dict
) -> None:
    """Write the definitions ``dump`` now inherits from into the exported tree.

    Written to the export root as
    ``_<name>.yaml``, which is what makes the loader treat it as a definition
    to inherit from rather than as a machine element.
    """
    parent_name = next(
        (dump[key] for key in INHERIT_KEYS if dump.get(key) is not None), None
    )
    collected: dict = {}
    _gather_template_chain(parent_name, namespace, collected)
    for name, raw in collected.items():
        if name in namespace_copy:
            continue
        namespace_copy[name] = raw
        with open(os.path.join(destination_root, f"_{name}.yaml"), "w") as handle:
            yaml.dump(raw, handle)


_POSITION_KEYS = ("middle", "s", "s_point", "reference_placement")

_INHERITABLE = object()


def _sequential_position(dump: dict, phys_dict: dict, ele, prev_ele, name: str) -> dict:
    """Drop the position entirely, leaving order and length to carry it.

    The inverse of sequential (drift-based) placement: an element that abuts
    its predecessor needs no position written at all.
    Only correct where the elements really do abut — a gap with no ``Drift``
    element in it is spacing that exists nowhere else in the file, so an element
    that does not abut keeps an explicit ``s`` and anchors the rest of the line
    from there.
    """
    phys = ele.physical
    if phys.s is None:
        return dump

    s_start = phys.s - phys.length / 2.0
    if prev_ele is None:
        abuts = abs(s_start) <= _ABUT_TOLERANCE
    else:
        prev_phys = getattr(prev_ele, "physical", None)
        if prev_phys is None or prev_phys.s is None:
            return dump
        abuts = abs(s_start - (prev_phys.s + prev_phys.length / 2.0)) <= _ABUT_TOLERANCE

    if abuts:
        for key in _POSITION_KEYS:
            phys_dict.pop(key, None)
    else:
        phys_dict.pop("middle", None)
        phys_dict.pop("reference_placement", None)
        phys_dict["s"] = round(s_start, 6)
        phys_dict["s_point"] = "start"
        warn(
            f"Element '{name}' does not abut its predecessor, so sequential "
            "export cannot drop its position: it is written with an explicit "
            "s instead. Add a Drift element to carry the gap if you want the "
            "fully sequential form."
        )
    return dump


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
    ``"sequential"`` — write no position at all, leaving the section order and
                      the element lengths to fix it on reload. Requires the
                      elements to abut; see :func:`_sequential_position`.
    """
    if mode == "global":
        return dump

    phys = getattr(ele, "physical", None)
    if phys is None or "physical" not in dump:
        return dump

    phys_dict = dump["physical"]

    if mode == "sequential":
        return _sequential_position(dump, phys_dict, ele, prev_ele, ele.name)

    if mode == "s":
        if phys.s is not None:
            phys_dict.pop("middle", None)
            phys_dict["s"] = round(phys.s, 6)
            if phys.s_point != "middle":
                phys_dict["s_point"] = phys.s_point

    elif mode == "reference":
        prev_phys = (
            getattr(prev_ele, "physical", None) if prev_ele is not None else None
        )
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


def export_machine_sections(
    path: str, machine: MachineModel, filename: str = "_sections.yaml"
) -> None:
    """Write the section orders out beside the exported elements.

    Sequential placement keeps the geometry in the section order rather than on
    the elements, so an export in ``"sequential"`` mode is only reloadable
    alongside the orders that produced it -- including the numbering a repeated
    element was split into. The other position modes write the
    geometry onto the elements themselves and do not depend on this.

    The ``_`` prefix keep the file out of the element list when the
    export directory is loaded back.
    """
    os.makedirs(path, exist_ok=True)
    sections = {
        name: {"elements": list(section.order), "type": section.section_type}
        for name, section in machine.sections.items()
    }
    with open(os.path.join(path, filename), "w") as handle:
        yaml.dump({"sections": sections}, handle, sort_keys=False)


def export_as_yaml(
    filename: Union[str, None],
    ele,
    position_mode: PositionMode = "global",
    *,
    prev_name: Optional[str] = None,
    prev_ele=None,
    collapse_schema: bool = False,
    schema_root: Union[str, None] = None,
    collapse_inheritance: bool = False,
    template_root: Union[str, None] = None,
    namespace=None,
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
        ``"sequential"``
            No position at all: the section order and the element lengths
            carry it. Only elements that abut their predecessor can drop their position;
            one that does not is written with an explicit ``s`` anchoring
            what follows it, and warns.
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
    collapse_inheritance:
        If True and the element declares `inherits_from`, write it back out
        as that declaration plus only the keys that differ from the
        resolved parent instead of the fully expanded element.
        Disabled by default; falls back to the full expansion
        if the parent cannot be found.
    template_root:
        The combined file or element directory the parent named by
        `inherits_from` is defined in (typically the lattice the element was
        loaded from); required for `collapse_inheritance` to have anything
        to diff against.
    namespace:
        An already-built ``name -> raw element dict`` namespace to use in
        place of reading `template_root`.
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
    if collapse_inheritance:
        if namespace is None:
            namespace = _template_namespace(template_root)
        _collapse_dump_inheritance(dump, ele, namespace)
    dump = _prune_empty(dump)
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
    collapse_inheritance: bool = False,
    template_root: Union[str, None] = None,
    write_sections: bool = True,
) -> None:
    """Export all elements to a single combined ``summary.yaml``.

    Parameters
    ----------
    path:
        Directory in which to write ``summary.yaml``.
    machine:
        Machine model to export.
    position_mode:
        Position representation — ``"global"`` (default), ``"s"``,
        ``"reference"`` (each element relative to its section predecessor),
        or ``"sequential"`` (no position at all, carried by the section
        order and the lengths). See `export_as_yaml`.
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
    collapse_inheritance:
        If True, elements declaring `inherits_from` are written in collapsed
        form (see `export_as_yaml`). Parents that are themselves
        exported elements are left where they are rather than duplicated.
    template_root:
        As `export_as_yaml`; defaults to `machine.element_list`.
    write_sections:
        In `"sequential"` position mode, also write the section orders to
        `_sections.yaml` (see `export_machine_sections`), without which the
        export carries no positions at all. Ignored in the other modes.
    """
    filename = os.path.join(path, "summary.yaml")
    os.makedirs(path, exist_ok=True)
    if (
        collapse_schema
        and schema_root is None
        and isinstance(getattr(machine, "element_list", None), str)
    ):
        schema_root = machine.element_list
    if (
        collapse_inheritance
        and template_root is None
        and isinstance(getattr(machine, "element_list", None), str)
    ):
        template_root = machine.element_list
    namespace = _template_namespace(template_root) if collapse_inheritance else None

    embedded_schemas = {}
    embedded_templates: dict = {}
    combined_yaml = {}
    for name, elem, prev_name, prev_elem in _iter_section_order(machine):
        dump = export_as_yaml(
            None, elem, position_mode, prev_name=prev_name, prev_ele=prev_elem
        )
        if collapse_schema:
            controls = dump.get("controls")
            if isinstance(controls, dict) and controls.get("schema"):
                schema_ref = controls["schema"]
                combined_key = os.path.join(elem.subdirectory, schema_ref)
                if combined_key not in embedded_schemas:
                    error = None
                    for base_dir in _schema_base_dirs(schema_root, elem):
                        try:
                            embedded_schemas[combined_key] = (
                                get_controls_schema_variables(schema_ref, base_dir)
                            )
                            break
                        except FileNotFoundError as exc:
                            error = exc
                    else:
                        warn(f"Cannot embed controls schema for {elem.name}: {error}")
                        embedded_schemas[combined_key] = None
                if embedded_schemas.get(combined_key) is not None:
                    live_variables = (
                        elem.controls.variables if elem.controls is not None else None
                    )
                    dump["controls"] = collapse_controls_schema(
                        {**controls, "schema": combined_key},
                        elem.name,
                        embedded_schemas[combined_key],
                        live_variables=live_variables,
                    )
                else:
                    dump["controls"] = {
                        k: v
                        for k, v in controls.items()
                        if k not in ("schema", "identifier_pattern")
                    }
        if collapse_inheritance:
            _gather_template_chain(
                _collapse_dump_inheritance(dump, elem, namespace),
                namespace,
                embedded_templates,
            )
        combined_yaml[name] = _prune_empty(dump)

    embedded_schemas = {k: v for k, v in embedded_schemas.items() if v is not None}
    if embedded_schemas:
        combined_yaml[COMBINED_SCHEMAS_KEY] = embedded_schemas
    embedded_templates = {
        k: v for k, v in embedded_templates.items() if k not in combined_yaml
    }
    if embedded_templates:
        combined_yaml[COMBINED_TEMPLATES_KEY] = embedded_templates

    with open(filename, "w") as yaml_file:
        yaml.default_flow_style = True
        yaml.dump(combined_yaml, yaml_file)

    if position_mode == "sequential" and write_sections:
        export_machine_sections(path, machine)


def export_machine(
    path: str,
    machine: MachineModel,
    overwrite: bool = False,
    verbose: bool = False,
    position_mode: PositionMode = "global",
    collapse_schema: bool = False,
    schema_root: Union[str, None] = None,
    copy_schemas: bool = True,
    collapse_inheritance: bool = False,
    template_root: Union[str, None] = None,
    copy_templates: bool = True,
    write_sections: bool = True,
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
        Position representation — ``"global"`` (default), ``"s"``,
        ``"reference"`` (each element relative to its section predecessor),
        or ``"sequential"`` (no position at all). See `export_as_yaml`.
    collapse_schema:
        As `export_as_yaml`.
    schema_root:
        As `export_as_yaml`; defaults to `machine.element_list`
        when that is a directory path.
    copy_schemas:
        When `collapse_schema` is set, also copy each schema
        file referenced into the corresponding destination subdirectory
        (once each), so the exported tree is loadable on its own.
    collapse_inheritance:
        As `export_as_yaml`.
    template_root:
        As `export_as_yaml`; defaults to `machine.element_list`.
    copy_templates:
        When `collapse_inheritance` is set, also write each definition
        inherited from (and its own chain of parents) into the export root
        as `_<name>.yaml`.
    write_sections:
        In `"sequential"` position mode, also write the section orders to
        `_sections.yaml` (see `export_machine_sections`), without which the
        export carries no positions at all. Ignored in the other modes.
    """
    os.makedirs(path, exist_ok=True)
    if (
        collapse_schema
        and schema_root is None
        and isinstance(getattr(machine, "element_list", None), str)
    ):
        schema_root = machine.element_list
    if (
        collapse_inheritance
        and template_root is None
        and isinstance(getattr(machine, "element_list", None), str)
    ):
        template_root = machine.element_list
    namespace = _template_namespace(template_root) if collapse_inheritance else None
    copied_schemas = set()
    copied_templates = {name: None for name in machine.elements}
    for name, elem, prev_name, prev_elem in _iter_section_order(machine):
        directory = os.path.join(path, elem.subdirectory)
        os.makedirs(directory, exist_ok=True)
        filename = os.path.join(directory, elem.name + ".yaml")
        if overwrite or not os.path.isfile(filename):
            if verbose:
                _log.debug("Exporting element '%s' to file '%s'", name, filename)
            dump = export_as_yaml(
                None,
                elem,
                position_mode,
                prev_name=prev_name,
                prev_ele=prev_elem,
                collapse_schema=collapse_schema,
                schema_root=schema_root,
                collapse_inheritance=collapse_inheritance,
                template_root=template_root,
                namespace=namespace,
            )
            with open(filename, "w") as yaml_file:
                yaml.dump(dump, yaml_file)
            if collapse_schema and copy_schemas:
                _copy_controls_schema(elem, schema_root, directory, copied_schemas)
            if collapse_inheritance and copy_templates:
                _copy_templates(dump, namespace, path, copied_templates)
    if position_mode == "sequential" and write_sections:
        export_machine_sections(path, machine)


def export_elements(
    path: str,
    elements: list,
    position_mode: PositionMode = "global",
    collapse_schema: bool = False,
    schema_root: Union[str, None] = None,
    copy_schemas: bool = True,
    collapse_inheritance: bool = False,
    template_root: Union[str, None] = None,
    copy_templates: bool = True,
) -> None:
    """Export a list of elements to individual YAML files.

    Parameters
    ----------
    path:
        Root output directory.
    elements:
        Ordered list of elements to export.
    position_mode:
        Position representation — ``"global"`` (default), ``"s"``,
        ``"reference"`` (each element relative to its predecessor in the
        list), or ``"sequential"`` (no position at all).
    collapse_schema:
        As `export_as_yaml`.
    schema_root:
        As `export_as_yaml`.
    copy_schemas:
        As `export_machine`.
    collapse_inheritance:
        As `export_as_yaml`.
    template_root:
        As `export_as_yaml`.
    copy_templates:
        As `export_machine`.
    """
    namespace = _template_namespace(template_root) if collapse_inheritance else None
    copied_schemas = set()
    copied_templates = {elem.name: None for elem in elements if elem is not None}
    prev_name: Optional[str] = None
    prev_elem = None
    for elem in elements:
        if elem is None:
            continue
        directory = os.path.join(path, elem.subdirectory)
        os.makedirs(directory, exist_ok=True)
        filename = os.path.join(directory, elem.name + ".yaml")
        dump = export_as_yaml(
            None,
            elem,
            position_mode,
            prev_name=prev_name,
            prev_ele=prev_elem,
            collapse_schema=collapse_schema,
            schema_root=schema_root,
            collapse_inheritance=collapse_inheritance,
            template_root=template_root,
            namespace=namespace,
        )
        with open(filename, "w") as yaml_file:
            yaml.dump(dump, yaml_file)
        if collapse_schema and copy_schemas:
            _copy_controls_schema(elem, schema_root, directory, copied_schemas)
        if collapse_inheritance and copy_templates:
            _copy_templates(dump, namespace, path, copied_templates)
        prev_name = elem.name
        prev_elem = elem
