#!/usr/bin/env python3
"""
Rename module *files* and rewrite every import that refers to them.

Separate from pep8_rename.py, which renames identifiers. This one moves files,
resolves relative imports to absolute so it can match them precisely, rewrites
``from``/``import`` statements, leaves a deprecating shim at each old path, and
updates the Sphinx autodoc stubs.

Case-only renames are deliberately avoided
------------------------------------------
``CATAP.py`` -> ``catap.py`` differs only in case, so on macOS and Windows the
old and new files cannot coexist -- which makes a compat shim impossible and
confuses git. Those modules get a distinct name instead (``catap_exporter.py``),
so the shim can sit alongside.

    python tools/rename_modules.py --check
    python tools/rename_modules.py --apply
"""

from __future__ import annotations

import argparse
import ast
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

#: old dotted module path -> new dotted module path
MODULE_RENAMES: dict[str, str] = {
    # laura/Exporters -- all case-only against their lowercase form, so each
    # takes a distinct name to leave room for the shim.
    "laura.Exporters.CATAP": "laura.Exporters.catap_exporter",
    "laura.Exporters.RDF": "laura.Exporters.rdf_exporter",
    "laura.Exporters.SQL": "laura.Exporters.sql_exporter",
    "laura.Exporters.YAML": "laura.Exporters.yaml_exporter",
    "laura.Exporters.Export_CATAP_YAML": "laura.Exporters.export_catap_yaml",
    # laura/Importers
    "laura.Importers.CATAP_Loader": "laura.Importers.catap_loader",
    "laura.Importers.Magnet_Table": "laura.Importers.magnet_table",
    "laura.Importers.MySafeConstructor": "laura.Importers.my_safe_constructor",
    "laura.Importers.MySafeLoader": "laura.Importers.my_safe_loader",
    "laura.Importers.SimFrame_Loader": "laura.Importers.simframe_loader",
    "laura.Importers.YAML_Loader": "laura.Importers.yaml_loader",
    # laura/models -- RF.py is case-only against rf.py, hence rf_elements.
    "laura.models.RF": "laura.models.rf_elements",
    "laura.models.baseModels": "laura.models.base_models",
    "laura.models.elementList": "laura.models.element_list",
    # laura/translator
    "laura.translator.utils.SDDSFile": "laura.translator.utils.sdds_file",
    "laura.translator.utils.elegant.SDDSFile": "laura.translator.utils.elegant.sdds_file",
    "laura.translator.utils.elegant.sdds_classes_APS":
        "laura.translator.utils.elegant.sdds_classes_aps",
    "laura.translator.utils.fields.FieldParameter":
        "laura.translator.utils.fields.field_parameter",
}

#: Pre-existing breakage in modules this rename touches: these three use
#: `from Importers.X import Y`, missing the `laura.` prefix, so they raise
#: ModuleNotFoundError on import today. Fixed here because their import lines
#: are being rewritten anyway.
BROKEN_ABSOLUTE_IMPORTS = {
    "from Importers.CATAP_Loader": "from laura.Importers.CATAP_Loader",
    "from Importers.MySafeConstructor": "from laura.Importers.MySafeConstructor",
    "from Importers.MySafeLoader": "from laura.Importers.MySafeLoader",
}

SHIM = '''"""
Deprecated module path.

``{old}`` was renamed to ``{new}`` for PEP 8 compliance (module names are
lower_snake_case). This shim keeps the old import path working; it will be
removed in a future release.

Attribute access is delegated to the new module, so any deprecated *names* it
serves through its own ``__getattr__`` keep working through here too.
"""

import warnings

from {new_pkg} import {new_mod} as _target

warnings.warn(
    "{old} was renamed to {new}. The old path still works but will be "
    "removed in a future release; import from {new} instead.",
    DeprecationWarning,
    stacklevel=2,
)


def __getattr__(name):
    return getattr(_target, name)


def __dir__():
    return dir(_target)
'''


def module_path(dotted: str) -> Path:
    return ROOT / (dotted.replace(".", "/") + ".py")


def package_of(path: Path) -> str:
    """Dotted package containing *path* (``laura/models/element.py`` -> laura.models)."""
    rel = path.relative_to(ROOT).with_suffix("")
    parts = list(rel.parts)
    if parts[-1] == "__init__":
        parts.pop()
    else:
        parts.pop()
    return ".".join(parts)


def resolve(module: str | None, level: int, pkg: str) -> str:
    """Resolve a possibly-relative ImportFrom target to an absolute dotted path."""
    if level == 0:
        return module or ""
    parts = pkg.split(".")
    if level > 1:
        parts = parts[: len(parts) - (level - 1)]
    return ".".join(parts + ([module] if module else []))


def rewrite_imports(src: str, path: Path) -> tuple[str, int]:
    """
    Rewrite import statements referring to renamed modules.

    Done with a line-oriented regex over statements identified by AST, rather
    than a full CST pass: import statements are simple enough that this is
    reliable, and it preserves formatting exactly.
    """
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return src, 0

    pkg = package_of(path)
    # (lineno, kind, old_text, new_text); kind distinguishes the module part of
    # a `from ... import` -- which may sit behind leading dots -- from an
    # imported name, so the two are matched with different anchors.
    edits: list[tuple[int, str, str, str]] = []

    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            absolute = resolve(node.module, node.level, pkg)
            new = MODULE_RENAMES.get(absolute)
            if new is not None and node.module:
                # only the final component of the module path changes
                head, _, _ = node.module.rpartition(".")
                new_module = f"{head}.{new.rsplit('.', 1)[1]}" if head else new.rsplit(".", 1)[1]
                edits.append((node.lineno, "module", node.module, new_module))
                continue
            # `from <pkg> import <module>` -- the module is an imported *name*
            for alias in node.names:
                target = f"{absolute}.{alias.name}" if absolute else alias.name
                new_t = MODULE_RENAMES.get(target)
                if new_t is not None:
                    edits.append((node.lineno, "name", alias.name, new_t.rsplit(".", 1)[1]))
        elif isinstance(node, ast.Import):
            for alias in node.names:
                new_t = MODULE_RENAMES.get(alias.name)
                if new_t is not None:
                    edits.append((node.lineno, "module", alias.name, new_t))

    if not edits:
        return src, 0

    lines = src.splitlines(keepends=True)
    count = 0
    for lineno, kind, old, new in edits:
        i = lineno - 1
        if i >= len(lines) or old not in lines[i]:
            continue
        if kind == "module":
            # anchor on `from`/`import` plus any leading dots, so a relative
            # `from .FieldParameter import FieldParameter` rewrites the module
            # and not the identically-named class after `import`.
            pat = rf"((?:from|import)\s+\.*){re.escape(old)}(?![\w])"
            new_line, n = re.subn(pat, lambda m: m.group(1) + new, lines[i], count=1)
        else:
            # an imported name: anchor after `import` or a comma
            pat = rf"((?:import|,)\s+){re.escape(old)}(?![\w])"
            new_line, n = re.subn(pat, lambda m: m.group(1) + new, lines[i], count=1)
        if n:
            lines[i] = new_line
            count += 1
    return "".join(lines), count


def iter_sources() -> list[Path]:
    out = []
    for base in ("laura", "unit_tests", "Testing", "examples"):
        d = ROOT / base
        if not d.is_dir():
            continue
        out += [p for p in sorted(d.rglob("*.py")) if "__pycache__" not in p.parts]
    return out


def update_docs(apply: bool) -> int:
    """Rewrite module paths in the Sphinx autodoc stubs."""
    changed = 0
    for rst in sorted((ROOT / "docs/source").rglob("*.rst")):
        text = original = rst.read_text()
        for old, new in MODULE_RENAMES.items():
            if old not in text:
                continue
            text = re.sub(rf"(?<![\w.]){re.escape(old)}(?![\w])", new, text)
            # section headings escape underscores: ``laura.models.baseModels module``
            esc_old, esc_new = old.replace("_", r"\_"), new.replace("_", r"\_")
            text = text.replace(esc_old, esc_new)
        if text != original:
            changed += 1
            print(f"  docs: {rst.relative_to(ROOT)}")
            if apply:
                rst.write_text(text)
    return changed


def fix_heading_underlines(path: Path) -> None:
    """Re-pad rst heading underlines whose title changed length."""
    lines = path.read_text().splitlines(keepends=True)
    for i in range(len(lines) - 1):
        underline = lines[i + 1].rstrip("\n")
        if underline and set(underline) <= set("=-~^\"'#*+") and len(set(underline)) == 1:
            title = lines[i].rstrip("\n")
            if title and len(underline) != len(title):
                lines[i + 1] = underline[0] * len(title) + "\n"
    path.write_text("".join(lines))


def main() -> int:
    ap = argparse.ArgumentParser()
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    apply = args.apply

    print("== moving module files ==")
    moved = 0
    for old, new in MODULE_RENAMES.items():
        src, dst = module_path(old), module_path(new)
        if dst.exists():
            continue
        if not src.exists():
            print(f"  !! missing: {src.relative_to(ROOT)}")
            continue
        print(f"  {src.relative_to(ROOT)} -> {dst.relative_to(ROOT)}")
        moved += 1
        if apply:
            shutil.move(str(src), str(dst))

    print("\n== fixing pre-existing broken absolute imports ==")
    for dotted in ("laura.Importers.catap_loader", "laura.Importers.my_safe_loader",
                   "laura.Exporters.export_catap_yaml"):
        p = module_path(dotted)
        if not p.exists():
            continue
        s = p.read_text()
        for bad, good in BROKEN_ABSOLUTE_IMPORTS.items():
            if bad in s:
                print(f"  {p.relative_to(ROOT)}: {bad!r} -> {good!r}")
                if apply:
                    s = s.replace(bad, good)
        if apply:
            p.write_text(s)

    print("\n== rewriting imports ==")
    total = 0
    for p in iter_sources():
        s = p.read_text()
        new_s, n = rewrite_imports(s, p)
        if n:
            total += n
            print(f"  {p.relative_to(ROOT)}: {n}")
            if apply:
                p.write_text(new_s)

    print("\n== writing compat shims ==")
    for old, new in MODULE_RENAMES.items():
        shim_path = module_path(old)
        if shim_path.exists():
            continue
        new_pkg, new_mod = new.rsplit(".", 1)
        print(f"  shim: {shim_path.relative_to(ROOT)} -> {new}")
        if apply:
            shim_path.write_text(
                SHIM.format(old=old, new=new, new_pkg=new_pkg, new_mod=new_mod)
            )

    print("\n== docs ==")
    update_docs(apply)
    if apply:
        for rst in sorted((ROOT / "docs/source").rglob("*.rst")):
            fix_heading_underlines(rst)

    print(f"\n{'applied' if apply else 'would apply'}: {moved} moves, {total} import edits")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
