#!/usr/bin/env python3
"""Generate laura/schema/generated/laura_orm.py from laura/schema/YAML/laura_schema.yaml.

Runs gen-sqla then post-processes to fix self-referential many-to-many
relationships.  SQLAlchemy 2.0 raises AmbiguousForeignKeysError when a
secondary junction table has two FK columns that both reference the same
parent table (which is exactly what happens for self-referential M2M like
AcceleratorElement.upstream/downstream).  gen-sqla does not emit the
required primaryjoin/secondaryjoin, so we add them here.

Usage (from repo root)::

    python laura/schema/generate_orm.py

Or via the generate.ps1 / generate.sh scripts.
"""

import re
import subprocess
import sys
from pathlib import Path


# ---------------------------------------------------------------------------
# Step 1: run gen-sqla
# ---------------------------------------------------------------------------


def _run_gen_sqla(schema_path: str) -> str:
    """Invoke gen-sqla and return its stdout as a string."""
    python_dir = Path(sys.executable).parent
    gen_sqla = python_dir / "gen-sqla"
    if not gen_sqla.exists():
        gen_sqla = python_dir / "gen-sqla.exe"
    if not gen_sqla.exists():
        gen_sqla = "gen-sqla"

    result = subprocess.run(
        [str(gen_sqla), schema_path],
        capture_output=True,
        text=True,
        # `text=True` alone decodes with the locale encoding (cp1252 on Windows),
        # turning every non-ASCII character in a schema description into mojibake.
        encoding="utf-8",
    )
    if result.returncode != 0:
        sys.stderr.write(result.stderr)
        raise RuntimeError(f"gen-sqla failed with exit code {result.returncode}")
    return result.stdout


# ---------------------------------------------------------------------------
# Step 2: parse class metadata from the generated source
# ---------------------------------------------------------------------------


def _class_blocks(content: str) -> list[tuple[int, int, str]]:
    """Return [(start, end, class_name), ...] for every ``class X(Base):`` block."""
    positions = [
        (m.start(), m.group(1))
        for m in re.finditer(r"^class (\w+)\(Base\):", content, re.MULTILINE)
    ]
    blocks = []
    for i, (start, name) in enumerate(positions):
        end = positions[i + 1][0] if i + 1 < len(positions) else len(content)
        blocks.append((start, end, name))
    return blocks


def _parse_pk_columns(content: str) -> dict[str, str]:
    """Return ``{ClassName: pk_column_name}`` for all ``Base`` subclasses."""
    pk_cols: dict[str, str] = {}
    for start, end, cls_name in _class_blocks(content):
        block = content[start:end]
        for line in block.splitlines():
            m = re.match(r"^\s+(\w+)\s*=\s*Column\(.*primary_key\s*=\s*True", line)
            if m:
                pk_cols[cls_name] = m.group(1)
                break
    return pk_cols


def _parse_junction_fk_columns(content: str) -> dict[str, list[str]]:
    """Return ``{ClassName: [col1, col2]}`` for junction table classes.

    Only captures Column-mapped attributes (skips ``id``).  Junction tables
    have exactly two such columns: the source FK and the target FK.
    """
    junction_cols: dict[str, list[str]] = {}
    for start, end, cls_name in _class_blocks(content):
        block = content[start:end]
        cols = [
            m.group(1)
            for line in block.splitlines()
            for m in [re.match(r"^\s+(\w+)\s*=\s*Column\(", line)]
            if m and m.group(1) != "id"
        ]
        if cols:
            junction_cols[cls_name] = cols
    return junction_cols


# ---------------------------------------------------------------------------
# Step 3: rewrite self-referential M2M relationships
# ---------------------------------------------------------------------------


def _fix_self_referential_m2m(content: str) -> str:
    """Add explicit primaryjoin/secondaryjoin to self-referential M2M relationships.

    gen-sqla emits (inside ``class Foo(Base):``):

        # ManyToMany
        slot = relationship( "Foo", secondary="Foo_slot")

    SQLAlchemy 2.0 cannot determine which of the two FK columns in the
    junction table is the "source" and which is the "target" when both
    reference the same table.  The fix adds:

        primaryjoin="Foo.pk == FooSlot.Foo_pk"
        secondaryjoin="Foo.pk == FooSlot.slot_pk"

    using string expressions that SQLAlchemy resolves lazily against the
    mapper class registry (so forward references to later-defined junction
    classes work correctly).
    """
    pk_cols = _parse_pk_columns(content)
    junction_fk_cols = _parse_junction_fk_columns(content)

    lines = content.split("\n")
    result: list[str] = []
    current_class: str | None = None

    class_re = re.compile(r"^class (\w+)\(Base\):")
    rel_re = re.compile(
        r'^(\s+)(\w+)\s*=\s*relationship\(\s*"(\w+)",\s*secondary="(\w+)"\s*\)'
    )

    i = 0
    while i < len(lines):
        line = lines[i]

        m = class_re.match(line)
        if m:
            current_class = m.group(1)

        # Look for the two-line pattern:  # ManyToMany\n  slot = relationship(...)
        if (
            current_class is not None
            and line.strip() == "# ManyToMany"
            and i + 1 < len(lines)
        ):
            next_line = lines[i + 1]
            rel_m = rel_re.match(next_line)
            if rel_m:
                indent = rel_m.group(1)
                slot = rel_m.group(2)
                target = rel_m.group(3)
                secondary = rel_m.group(4)

                if target == current_class:
                    # Junction class name follows CamelCase convention:
                    # ClassName + each word of slot capitalised (no underscores).
                    junction_cls = current_class + "".join(
                        w.capitalize() for w in slot.split("_")
                    )
                    pk = pk_cols.get(current_class, "id")
                    cols = junction_fk_cols.get(junction_cls, [])

                    if len(cols) >= 2:
                        # Source column starts with "<ClassName>_"; target does not.
                        src_col = next(
                            (c for c in cols if c.startswith(current_class + "_")),
                            cols[0],
                        )
                        tgt_col = next(
                            (c for c in cols if not c.startswith(current_class + "_")),
                            cols[1],
                        )

                        result.append(line)  # # ManyToMany
                        result.append(f"{indent}{slot} = relationship(")
                        result.append(f'{indent}    "{target}",')
                        result.append(f'{indent}    secondary="{secondary}",')
                        result.append(
                            f'{indent}    primaryjoin="'
                            f'{current_class}.{pk} == {junction_cls}.{src_col}",'
                        )
                        result.append(
                            f'{indent}    secondaryjoin="'
                            f'{current_class}.{pk} == {junction_cls}.{tgt_col}",'
                        )
                        result.append(f"{indent})")
                        i += 2
                        continue

        result.append(line)
        i += 1

    return "\n".join(result)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def generate(schema_path: str = "laura/schema/YAML/laura_schema.yaml") -> str:
    """Generate and return the full content of the SQLAlchemy ORM module."""
    raw = _run_gen_sqla(schema_path)
    return _fix_self_referential_m2m(raw)


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    out_path = Path("laura/schema/generated/laura_orm.py")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    content = generate()
    out_path.write_text(content, encoding="utf-8")
    print(f"Written {len(content):,} chars to {out_path}", file=sys.stderr)
