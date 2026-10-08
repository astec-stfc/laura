"""OcelotLatticeImporter run against a real ocelot MagneticLattice."""

import subprocess
import sys

import pytest

pytest.importorskip("ocelot")

from ocelot.cpbd.magnetic_lattice import MagneticLattice

from laura.translator.converters.codes.ocelot import OcelotLatticeImporter


def _periodic_lattice():
    """A cell repeated with `* N`, reusing the same element objects."""
    from ocelot.cpbd.elements import Drift, Quadrupole

    d1 = Drift(l=0.5, eid="D1")
    q1 = Quadrupole(l=0.2, k1=0.3, eid="Q1")
    q2 = Quadrupole(l=0.2, k1=-0.3, eid="Q2")
    cell = (d1, q1, d1, q2) * 3
    return MagneticLattice(cell)


def _elements(*sequence, **kwargs):
    return OcelotLatticeImporter(
        magnetic_lattice=MagneticLattice(list(sequence)), name="test", **kwargs
    ).create_laura_element_dictionary()


def test_importing_codes_does_not_load_ocelot():
    """ocelot-desy is optional and ocelot_conversion raises ImportError without it. A
    fresh subprocess, so an already-imported `ocelot` cannot mask the check.
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
    """Simulates ocelot's absence with a blocked import."""
    result = subprocess.run(
        [sys.executable, "-c", _BLOCK_OCELOT_AND_IMPORT_CODES],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr


def test_repeated_elements_across_periods_are_not_collapsed():
    importer = OcelotLatticeImporter(magnetic_lattice=_periodic_lattice(), name="test")
    elements = importer.create_laura_element_dictionary()

    assert list(elements) == [
        "D1.1", "Q1.1", "D1.2", "Q2.1",
        "D1.3", "Q1.2", "D1.4", "Q2.2",
        "D1.5", "Q1.3", "D1.6", "Q2.3",
    ]
    s_positions = [elements[name].physical.s for name in elements]
    assert s_positions == sorted(s_positions)
    assert len(set(s_positions)) == 12


def test_monitor_and_rbend_and_bend_are_imported():
    """Ocelot's `Monitor` holds `x`/`y`/`x_ref`/`y_ref`, so only a
    `Beam_Position_Monitor` exports to it; other monitors export as `Marker`.
    """
    from ocelot.cpbd.elements import Monitor, RBend, Bend

    bpm = Monitor(eid="BPM1")
    rb = RBend(l=0.5, angle=0.01, eid="RB1")
    b = Bend(l=0.5, angle=0.02, eid="B1")
    elements = _elements(bpm, rb, b)

    assert set(elements) == {"BPM1", "RB1", "B1"}
    assert elements["BPM1"].hardware_type == "Beam_Position_Monitor"
    assert elements["RB1"].hardware_type == "Dipole"
    assert elements["RB1"].magnetic.KnL(0) == pytest.approx(0.01)
    assert elements["B1"].hardware_type == "Dipole"
    assert elements["B1"].magnetic.KnL(0) == pytest.approx(0.02)


def test_combined_function_magnet_keeps_every_multipole_order():
    from ocelot.cpbd.elements import SBend, Quadrupole

    bend = SBend(l=0.5, angle=0.01, k1=0.3, eid="COMBINED")
    quad = Quadrupole(l=0.2, k1=0.5, k2=1.5, eid="Q1")
    elements = _elements(bend, quad)

    assert elements["COMBINED"].magnetic.KnL(0) == pytest.approx(0.01)
    assert elements["COMBINED"].magnetic.KnL(1) == pytest.approx(0.3 * 0.5)
    assert elements["Q1"].magnetic.KnL(1) == pytest.approx(0.5 * 0.2)
    assert elements["Q1"].magnetic.KnL(2) == pytest.approx(1.5 * 0.2)


def test_corrector_kick_angle_is_imported():
    """`hangle`/`vangle` are export-only computed aliases, which the generic keyword
    dispatch can never match.
    """
    from ocelot.cpbd.elements import Hcor, Vcor

    h = Hcor(l=0.3, angle=0.001, eid="CH1")
    v = Vcor(l=0.3, angle=-0.002, eid="CV1")
    elements = _elements(h, v)

    assert elements["CH1"].magnetic.horizontal_kick == pytest.approx(0.001)
    assert elements["CV1"].magnetic.vertical_kick == pytest.approx(-0.002)


def test_initial_twiss_is_imported_as_twiss_match():
    """Ocelot's initial `Twiss` (`tws0`) is not in `MagneticLattice.sequence`, so it is
    passed in via `initial_twiss`.
    """
    from ocelot import Twiss
    from ocelot.cpbd.elements import Quadrupole

    twiss = Twiss()
    twiss.beta_x, twiss.beta_y = 9.42, 22.19
    twiss.alpha_x, twiss.alpha_y = -0.66, 1.51
    twiss.Dx, twiss.Dy = 0.1, 0.2
    twiss.Dxp, twiss.Dyp = 0.01, 0.02
    twiss.s = 2956  # a position in the larger machine this section came from

    q = Quadrupole(l=0.5, k1=0.1, eid="Q1")
    elements = _elements(q, initial_twiss=twiss)

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


def test_functional_parameters_survive_a_laura_ocelot_round_trip(tmp_path):
    """Ocelot has no expressions; LAURA's own export carries the symbols."""
    pytest.importorskip("cpymad")
    from laura.translator.converters.codes.madx import MadxLatticeImporter
    from laura.translator.converters.layout import MachineLayoutTranslator

    source = tmp_path / "line.madx"
    source.write_text(
        "beam, particle=electron, energy=1;\n"
        "quad_k1 = 0.4;\n"
        "q: quadrupole, l=0.5, k1 := quad_k1;\n"
        "line: sequence, l=1; q, at=0.5; endsequence;\n"
    )
    layout = MadxLatticeImporter(source_file=str(source)).create_layout()
    maglat = next(
        iter(MachineLayoutTranslator.from_layout(layout).to_ocelot(save=False).values())
    )
    importer = OcelotLatticeImporter(magnetic_lattice=maglat, name="line")
    elements = importer.create_laura_element_dictionary()

    assert elements["q"].magnetic.multipoles.K1L.normal == "quad_k1"
    assert importer.functional_definitions["quad_k1"] == pytest.approx(0.2)
