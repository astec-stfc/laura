"""Tests for the MAD-X (cpymad) translator.

Build small element/lattice fixtures, translate them and feed the generated
MAD-X input into ``cpymad`` for verification.
"""

import pytest

pytest.importorskip("easygdf")
pytest.importorskip("h5py")

from laura.models.baseModels import (  # noqa: E402
    set_functional_definitions,
    set_resolve_functional,
)
from laura.models.element import (  # noqa: E402
    Combined_Corrector,
    Dipole,
    Horizontal_Corrector,
    Quadrupole,
    RFCavity,
    Vertical_Corrector,
)
from laura.models.elementList import SectionLattice  # noqa: E402
from laura.models.physical import PhysicalElement, Position  # noqa: E402
from laura.translator.converters.cavity import RFCavityTranslator  # noqa: E402
from laura.translator.converters.magnet import (  # noqa: E402
    CorrectorTranslator,
    DipoleTranslator,
    MagnetTranslator,
)
from laura.translator.converters.section import SectionLatticeTranslator  # noqa: E402


@pytest.fixture(autouse=True)
def _reset_defs():
    set_functional_definitions({}, merge=False)
    set_resolve_functional(False)
    yield
    set_functional_definitions({}, merge=False)
    set_resolve_functional(False)


def _quad(k1l):
    q = Quadrupole(
        name="q1",
        machine_area="S02",
        magnetic={"magnetic_length": 0.1, "k1l": k1l},
    )
    return MagnetTranslator.model_validate(q.model_dump())


def _dipole(**magnetic):
    base = {"magnetic_length": 0.5}
    base.update(magnetic)
    d = Dipole(name="D1", machine_area="ARC", magnetic=base)
    return DipoleTranslator.model_validate(d.model_dump())


def _cavity(field_amplitude, phase=0.0, structure="StandingWave"):
    cavity = {"phase": phase, "structure_Type": structure}
    if structure.lower() == "travellingwave":
        cavity |= {"mode_numerator": 2, "mode_denominator": 3}
    cav = RFCavity(
        name="C1",
        machine_area="L02",
        cavity=cavity,
        simulation={"field_amplitude": field_amplitude},
    )
    return RFCavityTranslator.model_validate(cav.model_dump())


class TestMadxElements:
    def test_quad_numeric(self):
        out = _quad(-2.0).to_madx()
        # k1 is the normalized strength KnL/length = -2.0 / 0.1
        assert "q1: quadrupole" in out
        assert "k1 = -20.0" in out
        assert ":=" not in out

    def test_quad_symbolic_is_deferred(self):
        set_functional_definitions({"quad1_k1l": -2.0})
        out = _quad("quad1_k1l").to_madx()
        assert "k1 := quad1_k1l / 0.1" in out

    def test_quad_resolved_mode_bakes_numbers(self):
        set_functional_definitions({"quad1_k1l": -2.0})
        set_resolve_functional(True)
        out = _quad("quad1_k1l").to_madx()
        assert "k1 = -20.0" in out
        assert "quad1_k1l" not in out

    def test_dipole_angle_and_edges(self):
        dt = _dipole(k0l=0.2, entrance_edge_angle=0.05, exit_edge_angle=0.05)
        out = dt.to_madx()
        assert "d1: sbend" in out.lower() or "D1: sbend" in out
        assert "angle = 0.2" in out
        assert "e1 = 0.05" in out
        assert "e2 = 0.05" in out

    def test_dipole_symbolic_angle_is_deferred(self):
        set_functional_definitions({"bend1": 0.1})
        dt = _dipole(k0l="bend1")
        assert "angle := bend1" in dt.to_madx()

    def test_drift_element_is_written(self):
        # MAD-X lattices are conventionally built with explicit drift elements
        # rather than relying on implicit gap-filling between placed elements.
        from laura.models.element import Drift
        from laura.translator.converters.drift import DriftTranslator

        drift = Drift(
            name="dr1",
            machine_area="S",
            hardware_class="Drift",
            physical={"length": 1.0},
        )
        dt = DriftTranslator.model_validate(drift.model_dump())
        assert dt.to_madx() == "dr1: drift, l = 1.0;\n"

    def test_marker_has_no_attributes(self):
        from laura.models.element import Marker
        from laura.translator.converters.diagnostic import DiagnosticTranslator

        marker = Marker(name="m1", machine_area="S")
        mt = DiagnosticTranslator.model_validate(marker.model_dump())
        assert mt.to_madx() == "m1: marker;\n"


class TestMadxCorrector:
    def test_horizontal_and_vertical_correctors(self):
        hc = Horizontal_Corrector(
            name="hc1",
            machine_area="S",
            magnetic={"magnetic_length": 0.1, "horizontal_kick": 0.02},
        )
        vc = Vertical_Corrector(
            name="vc1",
            machine_area="S",
            magnetic={"magnetic_length": 0.1, "vertical_kick": 0.03},
        )
        ht = CorrectorTranslator.model_validate(hc.model_dump())
        vt = CorrectorTranslator.model_validate(vc.model_dump())
        assert ht.to_madx() == "hc1: hkicker, l = 0.1, kick = 0.02;\n"
        assert vt.to_madx() == "vc1: vkicker, l = 0.1, kick = 0.03;\n"

    def test_combined_corrector_carries_both_planes(self):
        cc = Combined_Corrector(
            name="cc1",
            machine_area="S",
            magnetic={
                "magnetic_length": 0.1,
                "horizontal_kick": 0.04,
                "vertical_kick": 0.05,
            },
        )
        ct = CorrectorTranslator.model_validate(cc.model_dump())
        out = ct.to_madx()
        assert "cc1: kicker" in out
        assert "hkick = 0.04" in out
        assert "vkick = 0.05" in out

    def test_symbolic_kick_is_deferred(self):
        set_functional_definitions({"hc_kick": 0.02})
        hc = Horizontal_Corrector(
            name="hc1",
            machine_area="S",
            magnetic={"magnetic_length": 0.1, "horizontal_kick": "hc_kick"},
        )
        ht = CorrectorTranslator.model_validate(hc.model_dump())
        assert "kick := hc_kick" in ht.to_madx()

    def test_cpymad_tracks_correct_plane(self):
        pytest.importorskip("cpymad")
        from cpymad.madx import Madx

        hc = Horizontal_Corrector(
            name="HC1",
            machine_area="S",
            magnetic={"magnetic_length": 0.1, "horizontal_kick": 0.05},
            physical=PhysicalElement(length=0.1, middle=Position(x=0, y=0, z=1.0)),
        )
        vc = Vertical_Corrector(
            name="VC1",
            machine_area="S",
            magnetic={"magnetic_length": 0.1, "vertical_kick": 0.07},
            physical=PhysicalElement(length=0.1, middle=Position(x=0, y=0, z=2.0)),
        )
        section = SectionLattice(name="S1", order=["HC1", "VC1"], elements=[hc, vc])
        out = SectionLatticeTranslator.from_section(section).to_madx()

        madx = Madx(stdout=False)
        madx.input(out)
        madx.beam(particle="electron", energy=1.0)
        madx.use(sequence="S1")
        tw = madx.twiss(betx=1, bety=1, x=0, y=0, px=0, py=0)
        assert tw["px"][-1] == pytest.approx(0.05)
        assert tw["py"][-1] == pytest.approx(0.07)


class TestMadxCavity:
    def test_cavity_units_and_lag_convention(self):
        out = _cavity(20e6, phase=0.0).to_madx()
        assert "volt = 20.0" in out
        assert "lag = 0.25" in out
        assert "freq = 2998.5" in out

    def test_cavity_symbolic_volt_and_phase(self):
        set_functional_definitions({"V_L02.01": 55e6, "cav1_phase": 30.0})
        out = _cavity("V_L02.01", phase="cav1_phase").to_madx()
        assert "volt := (V_L02.01) * 1e-06" in out
        assert "lag := (90 - (cav1_phase)) / 360" in out

    def test_travelling_wave_voltage_scaling(self):
        import numpy as np

        ct = _cavity(20e6, structure="TravellingWave")
        out = ct.to_madx()
        factor = abs((ct.get_cells() + 3.8) * ct.cavity.cell_length * (1 / np.sqrt(2)))
        expected_mv = factor * 20e6 / 1e6
        assert f"volt = {expected_mv}" in out


class TestMadxSection:
    def _line(self, elements, defs=None, resolve=False):
        section = SectionLattice(
            name="S1",
            order=[e.name for e in elements],
            elements=elements,
            functional_definitions=defs or {},
            resolve_functional=resolve,
        )
        return SectionLatticeTranslator.from_section(section).to_madx()

    def _magnets(self, k1l=0.3, k0l=0.1, volt=5e6):
        q = Quadrupole(
            name="Q1",
            machine_area="S",
            magnetic={"magnetic_length": 0.5, "k1l": k1l},
            physical=PhysicalElement(length=0.5, middle=Position(x=0, y=0, z=1.0)),
        )
        d = Dipole(
            name="D1",
            machine_area="S",
            magnetic={"magnetic_length": 0.5, "k0l": k0l},
            physical=PhysicalElement(length=0.5, middle=Position(x=0, y=0, z=2.0)),
        )
        c = RFCavity(
            name="C1",
            machine_area="S",
            cavity={"phase": 0.0, "structure_Type": "StandingWave"},
            simulation={"field_amplitude": volt},
            physical=PhysicalElement(length=1.0, middle=Position(x=0, y=0, z=3.0)),
        )
        return [q, d, c]

    def test_sequence_structure(self):
        out = self._line(self._magnets())
        assert "S1: SEQUENCE, refer=entry" in out
        assert out.strip().endswith("ENDSEQUENCE;")
        assert "Q1: quadrupole" in out
        assert "D1: sbend" in out
        assert "C1: rfcavity" in out
        assert "S1_drift_1: drift" in out
        assert "S1_drift_2: drift" in out

    def test_symbolic_header_and_cpymad_parses(self):
        pytest.importorskip("cpymad")
        from cpymad.madx import Madx

        defs = {"kq": 0.3, "bend1": 0.1, "Vcav": 5e6}
        out = self._line(self._magnets(k1l="kq", k0l="bend1", volt="Vcav"), defs=defs)
        assert "kq = 0.3;" in out
        assert "bend1 = 0.1;" in out

        madx = Madx(stdout=False)
        madx.input(out)
        # k1 = kq / length = 0.3 / 0.5
        assert madx.elements["Q1"].k1 == pytest.approx(0.6)
        # deferred expression stays live
        madx.globals["kq"] = 0.9
        assert madx.elements["Q1"].k1 == pytest.approx(1.8)

    def test_cpymad_twiss_runs(self):
        pytest.importorskip("cpymad")
        from cpymad.madx import Madx

        out = self._line(self._magnets())
        madx = Madx(stdout=False)
        madx.input(out)
        madx.beam(particle="electron", energy=1.0)
        madx.use(sequence="S1")
        tw = madx.twiss(betx=1, bety=1)
        assert tw["s"][-1] == pytest.approx(2.751570601951526)

    def test_resolved_mode_bakes_numbers_no_header(self):
        pytest.importorskip("cpymad")
        defs = {"kq": 0.3, "bend1": 0.1, "Vcav": 5e6}
        out = self._line(
            self._magnets(k1l="kq", k0l="bend1", volt="Vcav"), defs=defs, resolve=True
        )
        assert "kq = 0.3;" not in out
        assert ":=" not in out
        assert "k1 = 0.6" in out


class TestDipoleFringeFields:
    """MAD-X's fringe attributes, and the two ways they used to go wrong."""

    def test_fint_comes_from_the_magnet_not_the_simulation_default(self):
        """`MagnetSimulationElement.edge_field_integral` used to default to 0.5
        and shadow the magnet's own value.

        The slot now defaults to `None`, so it is skipped unless something set
        it deliberately, and it keeps working as an override when it did.
        """
        dt = _dipole(k0l=0.2, gap=0.04, edge_field_integral=0.3)
        assert "fint = 0.3" in dt.to_madx()

        d = Dipole(
            name="D1",
            machine_area="ARC",
            magnetic={
                "magnetic_length": 0.5,
                "k0l": 0.2,
                "gap": 0.04,
                "edge_field_integral": 0.3,
            },
            simulation={"edge_field_integral": 0.77},
        )
        override = DipoleTranslator.model_validate(d.model_dump())
        assert "fint = 0.77" in override.to_madx()

    def test_asymmetric_faces_are_folded_onto_the_single_hgap(self):
        """MAD-X carries `fint` and `fintx` but only one `hgap`, where Bmad has
        `hgap` and `hgapx`.

        The gap to keep is the first non-zero one. A bend split by superposition
        has a zero gap *and* a zero integral on its interior face, so keeping
        that one would zero the real fringe at the other end.
        """
        symmetric = _dipole(k0l=0.2, gap=0.04, edge_field_integral=0.3).to_madx()
        assert "fint = 0.3" in symmetric
        assert "hgap = 0.02" in symmetric
        assert "fintx" not in symmetric

        entrance_half = _dipole(
            k0l=0.2,
            gap=0.03,
            edge_field_integral=0.45,
            exit_gap=0.0,
            exit_edge_field_integral=0.0,
        ).to_madx()
        assert "fint = 0.45" in entrance_half
        assert "hgap = 0.015" in entrance_half
        assert "fintx = 0.0" in entrance_half

        exit_half = _dipole(
            k0l=0.2,
            gap=0.0,
            edge_field_integral=0.0,
            exit_gap=0.03,
            exit_edge_field_integral=0.45,
        ).to_madx()
        assert "fint = 0.0" in exit_half
        assert "hgap = 0.015" in exit_half, "the exit gap must survive a zero entrance"
        assert "fintx = 0.45" in exit_half

        # Both faces real but with different gaps: the product is what matters,
        # so the exit integral absorbs the ratio.
        both = _dipole(
            k0l=0.2,
            gap=0.04,
            edge_field_integral=0.3,
            exit_gap=0.02,
            exit_edge_field_integral=0.3,
        ).to_madx()
        assert "hgap = 0.02" in both
        assert "fint = 0.3" in both
        assert "fintx = 0.15" in both
