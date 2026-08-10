#!/usr/bin/env python3
"""Normalise ``gen-doc`` output so Sphinx can render it.

``gen-doc`` targets MkDocs and prefixes every page with a MkDocs-only front
matter block::

    ---
    search:
      boost: 1.0
    ---# Type: Boolean

On the built-in type pages the closing fence is emitted glued to the title, as
above.  MyST cannot read that as front matter, so the leading ``---`` becomes a
transition ("Document or section may not begin with a transition"), the page
loses its H1, and every following ``##`` warns "Document headings start at H2".
A page with no H1 also has no title to show in a toctree.

The block means nothing to Sphinx either way, so it is stripped from every page.

Usage (from repo root)::

    python laura/schema/postprocess_docs.py [docs/source/schema]

Called automatically by ``generate.ps1`` / ``generate.sh`` after ``gen-doc``.
"""

import re
import sys
from pathlib import Path

DEFAULT_DIR = Path("docs/source/schema")

#: The MkDocs front matter block, tolerating a closing fence with the page
#: title glued to it (which is why this cannot simply be left in place).
_FRONT_MATTER = re.compile(r"\A---\s*\r?\nsearch:\s*\r?\n\s+boost:[^\r\n]*\r?\n---")


def strip_front_matter(directory: Path) -> int:
    """Strip the MkDocs front matter from every ``*.md`` in *directory*.

    Returns the number of files changed.
    """
    changed = 0
    for path in sorted(directory.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        stripped = _FRONT_MATTER.sub("", text, count=1).lstrip()
        if stripped != text:
            path.write_text(stripped, encoding="utf-8")
            changed += 1
    return changed


if __name__ == "__main__":
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_DIR
    if not target.is_dir():
        sys.exit(f"No such directory: {target}")
    print(f"Normalised {strip_front_matter(target)} page(s) in {target}", file=sys.stderr)
