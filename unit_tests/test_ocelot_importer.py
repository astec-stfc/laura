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


def test_monitor_and_rbend_and_bend_are_imported():
    """Regression test: robustness check against real EuXFEL lattices found
    that Ocelot's `Monitor` (mapped by `_switch_dict` to a LAURA hardware
    type named "Monitor", which does not exist -- every BPM was silently
    dropped) and `RBend`/`Bend` (missing from `_switch_dict` entirely) were
    all dropped on import, never raising or warning about anything but
    "not recognized"."""
    from ocelot.cpbd.elements import Monitor, RBend, Bend
    from ocelot.cpbd.magnetic_lattice import MagneticLattice

    bpm = Monitor(eid="BPM1")
    rb = RBend(l=0.5, angle=0.01, eid="RB1")
    b = Bend(l=0.5, angle=0.02, eid="B1")
    importer = OcelotLatticeImporter(
        magnetic_lattice=MagneticLattice([bpm, rb, b]), name="test"
    )
    elements = importer.create_laura_element_dictionary()

    assert set(elements) == {"BPM1", "RB1", "B1"}
    assert elements["BPM1"].hardware_type == "Diagnostic"
    assert elements["RB1"].hardware_type == "Dipole"
    assert elements["RB1"].magnetic.KnL(0) == pytest.approx(0.01)
    assert elements["B1"].hardware_type == "Dipole"
    assert elements["B1"].magnetic.KnL(0) == pytest.approx(0.02)


def test_combined_function_magnet_keeps_every_multipole_order():
    """Regression test: the per-attribute loop used to compute every
    multipole strength at the single order implied by the element's own
    hardware_type (`magnetic_orders[hardware_type]`), so a combined-function
    SBend (nonzero `angle` *and* `k1`, e.g. EuXFEL's QF.1967.TL) kept its
    K0L but silently dropped its entire K1L quadrupole component -- and the
    same shape of bug meant a Quadrupole's own `k2` (an embedded sextupole
    correction) was dropped too."""
    from ocelot.cpbd.elements import SBend, Quadrupole
    from ocelot.cpbd.magnetic_lattice import MagneticLattice

    bend = SBend(l=0.5, angle=0.01, k1=0.3, eid="COMBINED")
    quad = Quadrupole(l=0.2, k1=0.5, k2=1.5, eid="Q1")
    importer = OcelotLatticeImporter(
        magnetic_lattice=MagneticLattice([bend, quad]), name="test"
    )
    elements = importer.create_laura_element_dictionary()

    assert elements["COMBINED"].magnetic.KnL(0) == pytest.approx(0.01)
    assert elements["COMBINED"].magnetic.KnL(1) == pytest.approx(0.3 * 0.5)
    assert elements["Q1"].magnetic.KnL(1) == pytest.approx(0.5 * 0.2)
    assert elements["Q1"].magnetic.KnL(2) == pytest.approx(1.5 * 0.2)


def test_corrector_kick_angle_is_imported():
    """Regression test: keyword_conversion_rules_ocelot.yaml maps a
    corrector's kick to `hangle`/`vangle`, which are export-only
    @computed_field aliases on the Translator class (converters/magnet.py),
    not real fields on the base model -- the generic keyword dispatch can
    never match them, so every corrector's kick angle silently imported as
    0.0 regardless of its native `angle` value."""
    from ocelot.cpbd.elements import Hcor, Vcor
    from ocelot.cpbd.magnetic_lattice import MagneticLattice

    h = Hcor(l=0.3, angle=0.001, eid="CH1")
    v = Vcor(l=0.3, angle=-0.002, eid="CV1")
    importer = OcelotLatticeImporter(
        magnetic_lattice=MagneticLattice([h, v]), name="test"
    )
    elements = importer.create_laura_element_dictionary()

    assert elements["CH1"].magnetic.horizontal_kick == pytest.approx(0.001)
    assert elements["CV1"].magnetic.vertical_kick == pytest.approx(-0.002)


def test_initial_twiss_is_imported_as_twiss_match():
    """Robustness check against real EuXFEL lattices found that files like
    l2_special_optics.py build an initial `Twiss` object (conventionally
    `tws0`) and hand it to a separate tracking/matching call -- it isn't
    part of `MagneticLattice.sequence` at all, so it was never imported even
    though LAURA has a `TwissMatch` element built for exactly this ("a
    zero-length marker that defines the desired optical functions at a
    location", schema/YAML/elements.yaml). Passed in explicitly via
    `initial_twiss` since there's nothing on `MagneticLattice` to find it by."""
    from ocelot import Twiss
    from ocelot.cpbd.elements import Quadrupole
    from ocelot.cpbd.magnetic_lattice import MagneticLattice

    twiss = Twiss()
    twiss.beta_x, twiss.beta_y = 9.42, 22.19
    twiss.alpha_x, twiss.alpha_y = -0.66, 1.51
    twiss.Dx, twiss.Dy = 0.1, 0.2
    twiss.Dxp, twiss.Dyp = 0.01, 0.02
    twiss.s = 2956  # a position in the larger machine this section came from

    q = Quadrupole(l=0.5, k1=0.1, eid="Q1")
    importer = OcelotLatticeImporter(
        magnetic_lattice=MagneticLattice([q]), initial_twiss=twiss, name="test"
    )
    elements = importer.create_laura_element_dictionary()

    assert list(elements)[0] == "initial_twiss"
    marker = elements["initial_twiss"]
    assert marker.hardware_type == "TwissMatch"
    assert marker.physical.s == 0.0  # local position, not twiss.s
    assert marker.physical.length == 0.0
    assert marker.simulation.beta_x == pytest.approx(9.42)
    assert marker.simulation.beta_y == pytest.approx(22.19)
    assert marker.simulation.alpha_x == pytest.approx(-0.66)
    assert marker.simulation.alpha_y == pytest.approx(1.51)
    assert marker.simulation.eta_x == pytest.approx(0.1)
    assert marker.simulation.eta_y == pytest.approx(0.2)
    assert marker.simulation.eta_xp == pytest.approx(0.01)
    assert marker.simulation.eta_yp == pytest.approx(0.02)
    assert marker.simulation.from_beam is False
    assert list(elements)[1] == "Q1"
