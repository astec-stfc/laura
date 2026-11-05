import os
import sys
from pathlib import Path

import pytest

# In a conda env, test against its own libtao, not a ~/Documents/bmad-ecosystem build.
if (Path(sys.prefix) / "lib" / "libtao.so").exists():
    os.environ.setdefault("LAURA_LIBTAO", str(Path(sys.prefix) / "lib" / "libtao.so"))

try:
    # RF-Track's import-time update check segfaults in its bundled libssl once
    # pybdsim's libraries are loaded, so it must be imported first.
    import RF_Track  # noqa: F401
except ImportError:
    pass

from laura.models.base_models import set_functional_definitions, set_resolve_functional


@pytest.fixture(autouse=True)
def _reset_functionals():
    """Functional definitions and the resolve flag are module globals; start and end every test clean."""
    set_functional_definitions({}, merge=False)
    set_resolve_functional(False)
    yield
    set_functional_definitions({}, merge=False)
    set_resolve_functional(False)
