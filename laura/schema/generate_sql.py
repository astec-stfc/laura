"""Generate laura/schema/generated/laura_schema.sql from laura/schema/YAML/laura_schema.yaml.

Runs gen-sqltables then narrows over-wide primary keys, the same correction
:mod:`generate_orm` makes to the SQLAlchemy ORM.  Where a class has a ``key:
true`` slot but no ``identifier``, gen-sqltables drops the surrogate ``id`` and
puts *every* column in the primary key -- seventeen of them on ControlVariable.
A primary-key column may not be NULL, and most of a ControlVariable's columns
are optional, so that table could never be written to.  The generator already
knows the real key and emits it as a ``UNIQUE`` constraint alongside, so that is
what the primary key becomes.

Keeping this in a module rather than inline in generate.sh / generate.ps1 means
the two scripts cannot drift, which is how the ORM's self-referential-join fix
was silently lost once before.

Usage (from repo root)::

    python laura/schema/generate_sql.py

Or via the generate.ps1 / generate.sh scripts.
"""

import re
import subprocess
import sys
from pathlib import Path


def _run_gen_sqltables(schema_path: str) -> str:
    """Invoke gen-sqltables and return its stdout as a string."""
    python_dir = Path(sys.executable).parent
    gen = python_dir / "gen-sqltables"
    if not gen.exists():
        gen = python_dir / "gen-sqltables.exe"
    if not gen.exists():
        gen = "gen-sqltables"

    result = subprocess.run(
        [str(gen), schema_path],
        capture_output=True,
        text=True,
        # `text=True` alone decodes with the locale encoding (cp1252 on Windows),
        # turning every non-ASCII character in a schema description into mojibake.
        encoding="utf-8",
    )
    if result.returncode != 0:
        sys.stderr.write(result.stderr)
        raise RuntimeError(f"gen-sqltables failed with exit code {result.returncode}")
    return result.stdout


_TABLE_RE = re.compile(r'CREATE TABLE "?\w+"?\s*\(.*?\n\);', re.S)
_PK_RE = re.compile(r"^\tPRIMARY KEY \((.*)\)", re.M)
_UNIQUE_RE = re.compile(r"^\tUNIQUE \((.*)\)", re.M)


def _fix_key_slot_pk(content: str) -> str:
    """Replace an all-columns primary key with the table's UNIQUE constraint.

    Junction tables legitimately have a two-column composite key and are left
    alone.
    """

    def _fix_table(m: re.Match) -> str:
        table = m.group(0)
        pk = _PK_RE.search(table)
        if pk is None or len(pk.group(1).split(",")) <= 2:
            return table
        unique = _UNIQUE_RE.search(table)
        if unique is None:
            return table
        return table.replace(pk.group(0), f"\tPRIMARY KEY ({unique.group(1)})", 1)

    return _TABLE_RE.sub(_fix_table, content)


def generate(schema_path: str = "laura/schema/YAML/laura_schema.yaml") -> str:
    """Generate and return the full content of the SQL DDL."""
    return _fix_key_slot_pk(_run_gen_sqltables(schema_path))


if __name__ == "__main__":
    out_path = Path("laura/schema/generated/laura_schema.sql")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    content = generate()
    out_path.write_text(content, encoding="utf-8")
    print(f"Written {len(content):,} chars to {out_path}", file=sys.stderr)
