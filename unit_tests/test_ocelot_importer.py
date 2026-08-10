"""Behavioral tests for OcelotLatticeImporter (laura/translator/converters/codes/ocelot.py).

Unlike test_code_importer_consistency.py (AST-level static checks only),
these construct a real ocelot.cpbd.magnetic_lattice.MagneticLattice and run
the importer against it.
"""

import subprocess
import sys

import pytest

pytest.importorskip("ocelot")

from laura.translator.converters.codes.ocelot import OcelotLatticeImporter


def _periodic_lattice():
    """A standard Ocelot idiom: build a cell once, repeat it with `* N`,
    reusing the same element objects across periods."""
    from ocelot.cpbd.elements import Drift, Quadrupole
    from ocelot.cpbd.magnetic_lattice import MagneticLattice

    d1 = Drift(l=0.5, eid="D1")
    q1 = Quadrupole(l=0.2, k1=0.3, eid="Q1")
    q2 = Quadrupole(l=0.2, k1=-0.3, eid="Q2")
    cell = (d1, q1, d1, q2) * 3
    return MagneticLattice(cell)


def test_importing_codes_does_not_load_ocelot():
    """codes/ocelot.py must not import the real `ocelot` package at module
    level -- laura.translator.converters.codes (via `from .ocelot import
    ocelot_unsupported`) is on the path every translator user hits, and
    ocelot-desy is an optional extra (see context/decisions.md). Regression
    test: previously `from ...conversion_rules.codes import
    ocelot_conversion` at module top level in codes/ocelot.py pulled in the
    real package -- and ocelot_conversion.py itself *raises* ImportError if
    ocelot-desy isn't installed, so this used to break every translator
    import, not just Ocelot's. Run in a fresh subprocess so this session's
    already-imported `ocelot` (from other tests) can't mask the check.
    """
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            "import sys; "
            "from laura.translator.converters.codes import elegant_unsupported; "
            "sys.exit(1 if 'ocelot' in sys.modules else 0)",
        ],
    )
    assert result.returncode == 0


_BLOCK_OCELOT_AND_IMPORT_CODES = """
import builtins, sys
real_import = builtins.__import__
def blocking_import(name, globals=None, locals=None, fromlist=(), level=0):
    if level == 0 and (name == "ocelot" or name.startswith("ocelot.")):
        raise ImportError(f"simulated: {name} not installed")
    return real_import(name, globals, locals, fromlist, level)
builtins.__import__ = blocking_import
from laura.translator.converters.codes import elegant_unsupported, ocelot_unsupported
sys.exit(0)
"""


def test_translator_imports_work_without_ocelot_installed():
    """Regression test for the crash this session found and fixed:
    ocelot_conversion.py raises ImportError (not a graceful fallback) if
    ocelot-desy is missing, and codes/ocelot.py used to import it at module
    top level -- so merely importing laura.translator.converters.codes (the
    entry point for every translator/importer, not just Ocelot's) crashed
    outright for anyone without the optional ocelot-desy extra installed.
    Simulates ocelot's absence via a blocked absolute import rather than
    actually uninstalling it.
    """
    result = subprocess.run(
        [sys.executable, "-c", _BLOCK_OCELOT_AND_IMPORT_CODES],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr


def test_repeated_elements_across_periods_are_not_collapsed():
    """A standard `cell * N` lattice must import every occurrence of a
    repeated element, not just the last one. Regression test: previously
    keyed self.laura_elements by the raw (non-unique) elem.id."""
    importer = OcelotLatticeImporter(magnetic_lattice=_periodic_lattice(), name="test")
    elements = importer.create_laura_element_dictionary()

    assert list(elements) == ["Q1.1", "Q2.1", "Q1.2", "Q2.2", "Q1.3", "Q2.3"]
    s_positions = [elements[name].physical.s for name in elements]
    assert s_positions == sorted(s_positions)
    assert len(set(s_positions)) == 6
