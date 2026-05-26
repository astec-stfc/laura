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

import re
import subprocess
import sys
from pathlib import Path

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
    python_dir = Path(sys.executable).parent
    gen_pydantic = python_dir / "gen-pydantic"
    if not gen_pydantic.exists():
        gen_pydantic = python_dir / "gen-pydantic.exe"
    if not gen_pydantic.exists():
        # Fallback: rely on PATH
        gen_pydantic = "gen-pydantic"

    result = subprocess.run(
        [str(gen_pydantic), schema_path, "--extra-fields", "ignore"],
        capture_output=True,
        text=True,
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

def generate(
    schema_path: str = "laura/schema/laura_schema.yaml",
) -> str:
    """Generate and return the full content of ``_generated.py``."""
    raw = _run_gen_pydantic(schema_path)
    _enum_names, model_names = _collect_schema_classes(raw)
    renamed = _rename_classes(raw, model_names)
    return _HEADER + renamed


# ── CLI entry point ───────────────────────────────────────────────────────────

if __name__ == "__main__":
    out_path = Path("laura/models/_generated.py")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    content = generate()
    out_path.write_text(content, encoding="utf-8")
    print(f"Written {len(content):,} chars to {out_path}", file=sys.stderr)
