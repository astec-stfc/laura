#!/usr/bin/env python3
"""Generate laura/models/_generated.py from laura/schema/laura_schema.yaml.

Class names are given a ``_`` prefix and ``Base`` suffix
(e.g., ``Quadrupole`` → ``_QuadrupoleBase``) to avoid conflicts
with the hand-written wrapper classes in ``laura/models/``.

Enum classes keep their original names so they remain importable
from the generated module.

Usage (from repo root)::

    python laura/schema/generate_pydantic.py

Or via the generate.ps1 / generate.sh scripts::

    .\\laura\\schema\\generate.ps1
"""

import ast
import re
import subprocess
import sys
from pathlib import Path

import yaml

# ── Non-schema class names defined inside the generated file ─────────────────
# These are infrastructure types produced by gen-pydantic itself, not schema
# classes, so they must NOT be renamed.
_KEEP_AS_IS: frozenset[str] = frozenset(
    {
        "ConfiguredBaseModel",
        "LinkMLMeta",
    }
)

# ── Header prepended to the output file ──────────────────────────────────────
_HEADER = """\
# This file is auto-generated from laura/schema/laura_schema.yaml.
# DO NOT EDIT MANUALLY – regenerate with:
#   python laura/schema/generate_pydantic.py
# or:
#   .\\laura\\schema\\generate.ps1
#
# Class naming convention
# -----------------------
# * Enum classes keep their original names (HardwareClassEnum, etc.) so they
#   can be imported directly from this module.
# * All other schema-defined classes are renamed with a leading underscore and
#   a ``Base`` suffix (e.g., Quadrupole → _QuadrupoleBase) to avoid name
#   conflicts with the hand-written wrapper classes in laura/models/*.
#
# Migration guide
# ---------------
# To make a hand-written model use the generated base, import with an alias::
#
#     from laura.models._generated import ManufacturerElement as _ManufacturerElementBase
#
#     class ManufacturerElement(_ManufacturerElementBase):
#         # Override fields that differ from the generated defaults
#         manufacturer: str = ""
#         serial_number: str = ""
#         # Keep custom validators ...
#
# See laura/models/reference.py and laura/models/manufacturer.py for examples.

"""


# ── Step 1: run gen-pydantic ──────────────────────────────────────────────────

def _run_gen_pydantic(schema_path: str) -> str:
    """Invoke gen-pydantic and return its stdout as a string."""
    # Locate gen-pydantic next to the active Python interpreter.
    # On Windows/conda, scripts live in a Scripts/ subdirectory.
    python_dir = Path(sys.executable).parent
    candidates = [
        python_dir / "gen-pydantic",
        python_dir / "gen-pydantic.exe",
        python_dir / "Scripts" / "gen-pydantic",
        python_dir / "Scripts" / "gen-pydantic.exe",
    ]
    gen_pydantic = next((p for p in candidates if p.exists()), "gen-pydantic")

    result = subprocess.run(
        [str(gen_pydantic), schema_path, "--extra-fields", "ignore"],
        capture_output=True,
        text=True,
        # Without this, `text=True` decodes with the locale encoding, which on
        # Windows is cp1252 -- and every non-ASCII character in a schema
        # description (en dashes, Greek letters, the ohm sign) comes back as
        # mojibake and is written into _generated.py that way.
        encoding="utf-8",
    )
    if result.returncode != 0:
        sys.stderr.write(result.stderr)
        raise RuntimeError(
            f"gen-pydantic failed with exit code {result.returncode}"
        )
    return result.stdout


# ── Step 2: collect schema-defined class names ────────────────────────────────

def _collect_schema_classes(
    content: str,
) -> tuple[set[str], set[str]]:
    """
    Parse *content* (raw gen-pydantic output) and return:

    * ``enum_names``  – classes that inherit from ``(str, Enum)``.
                        These are kept with their original names.
    * ``model_names`` – all other schema-defined model classes.
                        These will be renamed to ``_XxxBase``.
    """
    enum_names: set[str] = set()
    model_names: set[str] = set()

    for m in re.finditer(r"^class (\w+)\(([^)]+)\):", content, re.MULTILINE):
        name = m.group(1)
        if name in _KEEP_AS_IS:
            continue
        bases_str = m.group(2)
        if "Enum" in bases_str:
            enum_names.add(name)
        else:
            model_names.add(name)

    return enum_names, model_names


# ── Step 3: apply renaming ────────────────────────────────────────────────────

def _rename_classes(content: str, model_names: set[str]) -> str:
    """
    Rename every schema model class (those in *model_names*) to ``_XxxBase``
    throughout *content*.

    Enum names are intentionally absent from *model_names* so they are left
    unchanged.  String literals inside ``json_schema_extra`` dict values are
    also left unchanged because they appear as quoted strings, not bare
    identifiers, and the targeted patterns below do not match quoted strings.
    """

    def new_name(n: str) -> str:
        return f"_{n}Base" if n in model_names else n

    # ── Pattern 1: class definition header ───────────────────────────────────
    # ``class Xxx(Parent1, Parent2):``
    def _replace_class_def(m: re.Match) -> str:
        cls_name = new_name(m.group(1))
        # Rename each base class identifier
        new_bases = re.sub(
            r"\b(\w+)\b", lambda bm: new_name(bm.group(1)), m.group(2)
        )
        return f"class {cls_name}({new_bases}):"

    content = re.sub(
        r"^class (\w+)\(([^)]+)\):",
        _replace_class_def,
        content,
        flags=re.MULTILINE,
    )

    # ── Pattern 2: Optional[list[Xxx]] ───────────────────────────────────────
    # Must be handled before Optional[Xxx] to avoid partial match.
    content = re.sub(
        r"Optional\[list\[(\w+)\]\]",
        lambda m: f"Optional[list[{new_name(m.group(1))}]]",
        content,
    )

    # ── Pattern 3: Optional[Xxx] ─────────────────────────────────────────────
    content = re.sub(
        r"Optional\[(\w+)\]",
        lambda m: f"Optional[{new_name(m.group(1))}]",
        content,
    )

    # ── Pattern 4: list[Xxx] (bare, not wrapped in Optional) ─────────────────
    content = re.sub(
        r"(?<!Optional\[)list\[(\w+)\]",
        lambda m: f"list[{new_name(m.group(1))}]",
        content,
    )

    # ── Pattern 5: model_rebuild() calls at module level ─────────────────────
    # ``Xxx.model_rebuild()``
    content = re.sub(
        r"^(\w+)\.model_rebuild\(\)",
        lambda m: f"{new_name(m.group(1))}.model_rebuild()",
        content,
        flags=re.MULTILINE,
    )

    return content


# ── Public API ────────────────────────────────────────────────────────────────


# ── Step 4: apply ifabsent defaults, fix multivalued, inject AliasChoices ────

def _parse_ifabsent(value: str) -> str | None:
    """Convert a LinkML ifabsent directive to a Python literal string.

    Returns a Python literal string, e.g. ``'0.0'``, ``'""'``, ``'"Generic"'``,
    or *None* if the value cannot be parsed.
    """
    if value.startswith("float(") and value.endswith(")"):
        inner = value[6:-1].strip()
        try:
            return repr(float(inner))
        except ValueError:
            return None
    if value.startswith("string(") and value.endswith(")"):
        inner = value[7:-1]
        return repr(inner)
    if value.startswith("int(") and value.endswith(")"):
        inner = value[4:-1].strip()
        try:
            return repr(int(inner))
        except ValueError:
            return None
    return None


def _parse_schema_info(
    schema_path: str,
) -> tuple[dict[str, str], set[str], set[str], dict[str, list[str]], dict[str, dict[str, list[str]]]]:
    """Read the schema YAML and extract field-level metadata.

    Returns a five-tuple:

    * ``defaults``       – ``{field_name: python_literal_str}`` for slots with
                            ``ifabsent``.  First definition wins (class order in
                            YAML).
    * ``multivalued``    – set of field names marked ``multivalued: true``.
    * ``dict_valued``    – set of field names marked ``multivalued: true``,
                            ``inlined: true``, and ``inlined_as_list: false``.
                            These are emitted as ``dict[str, T]`` rather than
                            ``list[T]``.
    * ``global_aliases`` – ``{field_name: [alias1, …]}`` for slots with
                            ``aliases:``, using *first-wins* semantics.  Used as
                            a fallback when the class-specific mapping has no
                            entry.
    * ``class_aliases``  – ``{class_name: {slot_name: [alias1, …]}}`` per-class
                            alias map.  Use this in preference to
                            ``global_aliases`` so that the same slot name defined
                            in several classes (e.g. ``type`` in every diagnostic
                            sub-class) gets the correct alias for each class.
    """
    defaults: dict[str, str] = {}
    multivalued: set[str] = set()
    dict_valued: set[str] = set()
    global_aliases: dict[str, list[str]] = {}
    class_aliases: dict[str, dict[str, list[str]]] = {}

    seen_paths: set[Path] = set()

    def _resolve_import_path(base_path: Path, import_name: str) -> Path | None:
        if ":" in import_name and not import_name.lower().endswith(".yaml"):
            return None
        candidate = Path(import_name)
        if not candidate.is_absolute():
            candidate = (base_path.parent / candidate).resolve()
        if candidate.exists():
            return candidate
        if candidate.suffix.lower() != ".yaml":
            yaml_candidate = candidate.with_suffix(".yaml")
            if yaml_candidate.exists():
                return yaml_candidate
        return None

    def _visit(path: Path) -> None:
        path = path.resolve()
        if path in seen_paths:
            return
        seen_paths.add(path)

        with open(path, encoding="utf-8") as fh:
            schema = yaml.safe_load(fh) or {}

        for class_name, class_def in (schema.get("classes") or {}).items():
            for slot_name, slot_def in (class_def.get("attributes") or {}).items():
                if not slot_def:
                    continue
                ifabsent = slot_def.get("ifabsent")
                if ifabsent:
                    parsed = _parse_ifabsent(str(ifabsent))
                    if parsed is not None and slot_name not in defaults:
                        defaults[slot_name] = parsed
                if slot_def.get("multivalued"):
                    multivalued.add(slot_name)
                    if slot_def.get("inlined") and slot_def.get("inlined_as_list") is False:
                        dict_valued.add(slot_name)
                slot_aliases = slot_def.get("aliases")
                if slot_aliases:
                    aliases_list = list(slot_aliases)
                    class_aliases.setdefault(class_name, {})[slot_name] = aliases_list
                    if slot_name not in global_aliases:
                        global_aliases[slot_name] = aliases_list

        for import_name in schema.get("imports") or []:
            if not isinstance(import_name, str):
                continue
            import_path = _resolve_import_path(path, import_name)
            if import_path is not None:
                _visit(import_path)

    _visit(Path(schema_path))

    return defaults, multivalued, dict_valued, global_aliases, class_aliases


def _apply_schema_fixes(content: str, schema_path: str) -> str:
    """Post-process the renamed generated code.

    Three transformations are applied, line by line:

    1. **ifabsent defaults** – ``Optional[T] = Field(default=None, …)``
       becomes ``T = Field(default=<value>, …)`` for fields listed in the
       schema with ``ifabsent:``.

    2. **multivalued lists** – ``Optional[list[T]] = Field(default=None, …)``
       becomes ``list[T] = Field(default_factory=list, …)`` for all
       ``multivalued: true`` fields.

    3. **AliasChoices** – for fields with LinkML ``aliases:``, a
       ``validation_alias=AliasChoices(field_name, *aliases)`` keyword
       argument is injected into the ``Field(…)`` call immediately before
       the ``json_schema_extra`` argument.  The alias map is resolved
       *per-class* so that slots with the same name in different schema
       classes (e.g. ``type`` in every diagnostic sub-class) each get
       their own correct alias rather than the first-class alias.

    An ``AliasChoices`` import is spliced into the pydantic import block if
    any field requires it.
    """
    defaults, multivalued, dict_valued, global_aliases, class_aliases = _parse_schema_info(schema_path)

    needs_alias_choices = False

    # Track the current schema class being processed so we can look up
    # per-class aliases (e.g. for the ``type`` slot that appears in every
    # diagnostic sub-class with a different alias).
    # The class headers produced by _rename_classes look like:
    #   class _BPMDiagnosticElementBase(_DiagnosticElementBase):
    # We strip the leading ``_`` and trailing ``Base`` to recover the
    # original schema class name used as a key in class_aliases.
    _class_header_re = re.compile(r"^class _?(\w+?)(?:Base)?\(")
    current_class_orig: str | None = None

    lines = content.split("\n")
    result: list[str] = []

    for line in lines:
        # Update current class context
        hdr = _class_header_re.match(line)
        if hdr:
            current_class_orig = hdr.group(1)

        # Choose the most specific alias map available for this class
        per_class = class_aliases.get(current_class_orig, {}) if current_class_orig else {}
        merged_aliases = {**global_aliases, **per_class}

        line = _fix_field_line(line, defaults, multivalued, dict_valued, merged_aliases)
        if "AliasChoices(" in line:
            needs_alias_choices = True
        result.append(line)

    fixed = "\n".join(result)

    if needs_alias_choices:
        fixed = _inject_alias_choices_import(fixed)

    return fixed


# Python primitive type names for which Optional-stripping is safe.
# Complex generated-class types (e.g. ``_PositionBase``) are intentionally
# excluded to avoid applying ifabsent defaults from an identically-named
# slot in a different schema class.
_PRIMITIVE_TYPES: frozenset[str] = frozenset({"float", "str", "int", "bool"})


def _fix_field_line(
    line: str,
    defaults: dict[str, str],
    multivalued: set[str],
    dict_valued: set[str],
    aliases: dict[str, list[str]],
) -> str:
    """Apply schema-driven fixes to a single field-declaration line."""

    # ── Optional[T] = Field(…) ───────────────────────────────────────────────
    # gen-pydantic already substitutes the concrete default from ``ifabsent``
    # (so ``default=None`` → ``default=0``) but keeps ``Optional[T]``.
    # We strip ``Optional`` only for primitive Python types to avoid
    # misapplying defaults when the same slot name appears in two schema
    # classes with different ranges (e.g. ManufacturerElement.manufacturer:str
    # vs StandardElement.manufacturer:ManufacturerElement).
    # ── Optional[list[T]] = Field(default=None, …) — multivalued that
    # gen-pydantic did NOT automatically convert ─────────────────────────────
    optlist_m = re.match(
        r"^( {4})(\w+): Optional\[list\[(\w+)\]\] = Field\(default=None, ",
        line,
    )
    if optlist_m:
        field_name = optlist_m.group(2)
        if field_name in dict_valued:
            inner = optlist_m.group(3)
            line = re.sub(r"Optional\[list\[(\w+)\]\]", f"dict[str, {inner}]", line, count=1)
            line = line.replace("default=None,", "default_factory=dict,", 1)
        elif field_name in multivalued:
            line = re.sub(r"Optional\[list\[(\w+)\]\]", r"list[\1]", line, count=1)
            line = line.replace("default=None,", "default_factory=list,", 1)
        line = _inject_alias_choices(line, field_name, aliases)
        return line

    # ── Optional[T] = Field(…) ───────────────────────────────────────────────
    opt_m = re.match(
        r"^( {4})(\w+): Optional\[(\w+)\] = Field\(",
        line,
    )
    if opt_m:
        field_name = opt_m.group(2)
        field_type = opt_m.group(3)

        if field_name in defaults and field_type in _PRIMITIVE_TYPES and "default=None" not in line:
            line = re.sub(r"Optional\[(\w+)\]", r"\1", line, count=1)

        line = _inject_alias_choices(line, field_name, aliases)
        return line

    # ── list[T] = Field(…) — multivalued (gen-pydantic already converted) ────
    list_m = re.match(
        r"^( {4})(\w+): list\[(\w+)\] = Field\(",
        line,
    )
    if list_m:
        field_name = list_m.group(2)
        if field_name in dict_valued:
            inner = list_m.group(3)
            line = re.sub(r"list\[(\w+)\]", f"dict[str, {inner}]", line, count=1)
            line = line.replace("default_factory=list,", "default_factory=dict,", 1)
        line = _inject_alias_choices(line, field_name, aliases)
        return line

    return line


def _inject_alias_choices(
    line: str, field_name: str, aliases: dict[str, list[str]]
) -> str:
    """Add ``validation_alias=AliasChoices(…)`` to the Field call on *line*."""
    if field_name not in aliases:
        return line
    slot_aliases = aliases[field_name]
    # Build AliasChoices args: field name first, then schema aliases
    args = ", ".join(repr(a) for a in [field_name] + slot_aliases)
    alias_kwarg = f"validation_alias=AliasChoices({args}), "
    # Inject just before json_schema_extra (or before closing paren if absent)
    if ", json_schema_extra" in line:
        line = line.replace(", json_schema_extra", f", {alias_kwarg}json_schema_extra", 1)
    elif line.rstrip().endswith(")"):
        line = line.rstrip()[:-1] + f", {alias_kwarg})"
    return line


def _inject_alias_choices_import(content: str) -> str:
    """Ensure ``AliasChoices`` is imported from pydantic in *content*."""
    # Already imported?
    if "AliasChoices" in content.split("class ConfiguredBaseModel")[0]:
        return content
    # Splice into the existing pydantic import block
    content = content.replace(
        "from pydantic import (\n    BaseModel,",
        "from pydantic import (\n    AliasChoices,\n    BaseModel,",
        1,
    )
    return content


def _serialize_by_field_name(content: str) -> str:
    """Make ``ConfiguredBaseModel`` dump field names rather than aliases. """
    return content.replace(
        "        serialize_by_alias = True,", "        serialize_by_alias = False,", 1
    )


# ── Step 5: mirror field descriptions as attribute docstrings ────────────────

def _add_attribute_docstrings(content: str) -> str:
    """Repeat each field's ``description`` as a PEP 224 attribute docstring.

    LinkML ``description:`` already reaches the generated code in two places:
    class descriptions become class docstrings, and slot descriptions become
    ``Field(description=...)``.  Plain ``sphinx.ext.autodoc`` does not render
    the latter, but it does pick up a string literal placed directly after an
    annotated assignment — so we emit one.

    The module is parsed with ``ast`` rather than matched line-by-line because
    the ``Field(...)`` calls span many lines and contain nested parentheses.
    """
    lines = content.split("\n")
    # 1-based line number to insert after → docstring line
    inserts: dict[int, str] = {}

    for cls in ast.parse(content).body:
        if not isinstance(cls, ast.ClassDef):
            continue
        for node in cls.body:
            if not isinstance(node, ast.AnnAssign) or not isinstance(node.value, ast.Call):
                continue
            desc = next(
                (
                    kw.value.value
                    for kw in node.value.keywords
                    if kw.arg == "description" and isinstance(kw.value, ast.Constant)
                ),
                None,
            )
            if isinstance(desc, str) and desc.strip():
                body = "\n    ".join(desc.strip().split("\n"))
                inserts[node.end_lineno] = f'    """{body}"""'

    for lineno in sorted(inserts, reverse=True):
        lines.insert(lineno, inserts[lineno])

    return "\n".join(lines)


# ── Public API ────────────────────────────────────────────────────────────────

# ── Step 6: drop slots the hand-written wrappers implement as properties ─────

#: ``{generated class name: {slot, ...}}`` to omit from the generated bases.
#:
#: These slots stay in the schema — they are part of the data model and lattice
#: YAML may set them — but a wrapper in ``laura/models/`` implements them as a
#: Python property instead of storing them. Pydantic cannot have both: a
#: subclass property shadowing an inherited field makes the property object
#: itself the field default, which then fails validation.
_PYDANTIC_EXCLUDED_SLOTS: dict[str, frozenset[str]] = {
    # MagneticElement.angle is derived from multipoles.K0L so that a symbolic
    # (functional) bend angle survives round-tripping and reads follow the
    # global resolution mode.
    #
    # Entries are inherited: gen-pydantic re-declares every inherited slot in
    # each subclass, so excluding a slot here also excludes it from every
    # generated base descending from this one.
    "_MagneticElementBase": frozenset({"angle"}),
}


def _excluded_slots_by_class(tree: ast.Module) -> dict[str, frozenset[str]]:
    """Resolve ``_PYDANTIC_EXCLUDED_SLOTS`` through the generated class tree.

    A class inherits the exclusions of every ancestor it is generated from, so
    a slot listed once on a root base is dropped from all of its descendants.
    """
    parents: dict[str, list[str]] = {
        node.name: [b.id for b in node.bases if isinstance(b, ast.Name)]
        for node in tree.body
        if isinstance(node, ast.ClassDef)
    }
    resolved: dict[str, frozenset[str]] = {}

    def excluded_for(name: str, seen: frozenset[str] = frozenset()) -> frozenset[str]:
        if name in resolved:
            return resolved[name]
        if name in seen:  # defensive: generated output should never cycle
            return frozenset()
        slots = _PYDANTIC_EXCLUDED_SLOTS.get(name, frozenset())
        for base in parents.get(name, []):
            slots |= excluded_for(base, seen | {name})
        resolved[name] = slots
        return slots

    return {name: excluded_for(name) for name in parents}


def _drop_excluded_slots(content: str) -> str:
    """Remove ``_PYDANTIC_EXCLUDED_SLOTS`` field definitions from *content*.

    Fields are matched with ``ast`` rather than by line, because ``Field(...)``
    calls span multiple lines; the trailing attribute docstring, if any, goes
    with them.
    """
    tree = ast.parse(content)
    by_class = _excluded_slots_by_class(tree)
    lines = content.split("\n")
    drop: set[int] = set()  # 0-based line indices
    for node in tree.body:
        if not isinstance(node, ast.ClassDef):
            continue
        excluded = by_class.get(node.name)
        if not excluded:
            continue
        body = node.body
        for i, stmt in enumerate(body):
            if not (
                isinstance(stmt, ast.AnnAssign)
                and isinstance(stmt.target, ast.Name)
                and stmt.target.id in excluded
            ):
                continue
            end = stmt.end_lineno
            # Swallow the PEP 224 attribute docstring that follows, if present.
            nxt = body[i + 1] if i + 1 < len(body) else None
            if (
                isinstance(nxt, ast.Expr)
                and isinstance(nxt.value, ast.Constant)
                and isinstance(nxt.value.value, str)
            ):
                end = nxt.end_lineno
            drop.update(range(stmt.lineno - 1, end))
    if not drop:
        return content
    return "\n".join(line for i, line in enumerate(lines) if i not in drop)


def generate(
    schema_path: str = "laura/schema/YAML/laura_schema.yaml",
) -> str:
    """Generate and return the full content of ``_generated.py``."""
    raw = _run_gen_pydantic(schema_path)
    _enum_names, model_names = _collect_schema_classes(raw)
    renamed = _rename_classes(raw, model_names)
    fixed = _apply_schema_fixes(renamed, schema_path)
    configured = _serialize_by_field_name(fixed)
    documented = _add_attribute_docstrings(configured)
    trimmed = _drop_excluded_slots(documented)
    return _HEADER + trimmed


# ── CLI entry point ───────────────────────────────────────────────────────────

if __name__ == "__main__":
    out_path = Path("laura/models/_generated.py")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    content = generate()
    out_path.write_text(content, encoding="utf-8")
    print(f"Written {len(content):,} chars to {out_path}", file=sys.stderr)
