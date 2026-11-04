#!/usr/bin/env python3
"""Generate the schema reference pages with ``gen-doc``, normalised so Sphinx
can render them.

``gen-doc`` targets MkDocs and prefixes every page with a MkDocs-only front
matter block::

    ---
    search:
      boost: 1.0
    ---# Type: Boolean

On the built-in type pages the closing fence is glued to the title, as above,
so MyST reads the ``---`` as a transition and the page loses its H1. The block
means nothing to Sphinx, so it is stripped from every page.

The pages are not committed: ``docs/source/conf.py`` calls :func:`generate`
on every Sphinx build. To preview them without building (from repo root)::

    python laura/schema/postprocess_docs.py [docs/source/schema]
"""

import re
import subprocess
import sys
from pathlib import Path

DEFAULT_DIR = Path("docs/source/schema")
SCHEMA = Path(__file__).parent / "YAML" / "laura_schema.yaml"

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


def generate(directory: Path = DEFAULT_DIR) -> int:
    """Write the reference pages for :data:`SCHEMA` into *directory*.

    The directory is cleared first: ``gen-doc`` writes but never prunes, so a
    renamed class or slot would leave its old page behind. Returns the number
    of pages normalised.
    """
    directory.mkdir(parents=True, exist_ok=True)
    for page in directory.glob("*.md"):
        page.unlink()
    # gen-doc itself, whose defaults differ from DocGenerator's; it prints a stray "None"
    subprocess.run(
        [sys.executable, "-m", "linkml.generators.docgen", "-d", str(directory), str(SCHEMA)],
        check=True,
        stdout=subprocess.DEVNULL,
    )
    return strip_front_matter(directory)


if __name__ == "__main__":
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_DIR
    print(f"Generated {generate(target)} page(s) in {target}", file=sys.stderr)
