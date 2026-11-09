#!/usr/bin/env python3
"""Drop the redundant sibling ``type`` that ``gen-json-schema`` emits beside ``anyOf``.

For a slot declared with ``any_of``, ``gen-json-schema`` writes both the union
*and* the slot's own ``range`` as a sibling keyword::

    "entrance_edge_angle": {
      "anyOf": [{"type": "number"}, {"type": "string"}, {"type": "null"}],
      "type": "string"
    }

JSON Schema conjoins sibling keywords, so this validates as
``anyOf(...) AND type`` -- i.e. only the branch matching ``type`` is actually
accepted and every other branch is dead. That inverts the intent of ``any_of``:
a numeric ``entrance_edge_angle`` was rejected because the slot has no explicit
``range:`` and so inherited ``default_range: string``, and a symbolic
``phase``/``field_amplitude`` was rejected because those slots do declare
``range: float``. Either way ``validate=True`` rejected values the Python model
accepts.

The sibling is pure redundancy -- ``gen-json-schema`` always emits the primary
range as one of the ``anyOf`` branches too -- so it is dropped wherever the
union already covers it. A sibling ``type`` *not* present in the union is left
alone and reported, since that would be a real narrowing rather than a repeat.

Usage (from repo root)::

    python laura/schema/postprocess_json_schema.py [laura/schema/generated/laura_element.schema.json]

Called automatically by ``generate.ps1`` / ``generate.sh`` after
``gen-json-schema``.
"""

import json
import sys
from pathlib import Path
from typing import Any

DEFAULT_PATH = Path("laura/schema/generated/laura_element.schema.json")


def _branch_types(any_of: list[Any]) -> set[str]:
    """Collect the ``type`` values named by the branches of an ``anyOf``."""
    types: set[str] = set()
    for branch in any_of:
        if not isinstance(branch, dict):
            continue
        branch_type = branch.get("type")
        if isinstance(branch_type, str):
            types.add(branch_type)
        elif isinstance(branch_type, list):
            types.update(t for t in branch_type if isinstance(t, str))
    return types


def strip_redundant_types(node: Any, path: str = "", kept: list[str] | None = None) -> int:
    """Recursively drop ``type`` siblings of ``anyOf``. Returns the number dropped."""
    if kept is None:
        kept = []
    dropped = 0
    if isinstance(node, dict):
        any_of = node.get("anyOf")
        sibling = node.get("type")
        if isinstance(any_of, list) and sibling is not None:
            wanted = {sibling} if isinstance(sibling, str) else set(sibling)
            if wanted <= _branch_types(any_of):
                del node["type"]
                dropped += 1
            else:
                kept.append(f"{path or '<root>'} (type={sibling!r} not among anyOf branches)")
        for key, value in node.items():
            dropped += strip_redundant_types(value, f"{path}.{key}" if path else key, kept)
    elif isinstance(node, list):
        for i, item in enumerate(node):
            dropped += strip_redundant_types(item, f"{path}[{i}]", kept)
    return dropped


if __name__ == "__main__":
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_PATH
    if not target.is_file():
        sys.exit(f"No such file: {target}")
    schema = json.loads(target.read_text(encoding="utf-8"))
    kept: list[str] = []
    dropped = strip_redundant_types(schema, kept=kept)
    if dropped:
        target.write_text(json.dumps(schema, indent=2) + "\n", encoding="utf-8")
    print(f"  Dropped {dropped} redundant type sibling(s) of anyOf", file=sys.stderr)
    for entry in kept:
        print(f"  WARNING: kept narrowing type at {entry}", file=sys.stderr)
