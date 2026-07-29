"""Tests for functional-parameter handling in the translators.

By default every code resolves a functional parameter to its number. Codes that
natively support symbolic parameters keep the name: ELEGANT declares them with a
``% <value> sto <name>`` header and references them as quoted rpn variables.

The translator import chain pulls in optional field-IO dependencies, so the whole
module is skipped when they are unavailable.
"""

import pytest

pytest.importorskip("easygdf")
pytest.importorskip("h5py")

from laura.models.baseModels import (  # noqa: E402
    set_functional_definitions,
    set_resolve_functional,
)
from laura.models.element import Quadrupole, RFCavity, NonLinearLens  # noqa: E402
from laura.translator.converters.magnet import (  # noqa: E402
    MagnetTranslator,
    NonLinearLensTranslator,
)
from laura.translator.converters.cavity import RFCavityTranslator  # noqa: E402
from laura.translator.utils.functions import (  # noqa: E402
    elegant_functional_definitions,
)


@pytest.fixture(autouse=True)
def _reset_defs():
    set_functional_definitions({}, merge=False)
    set_resolve_functional(False)
    yield
    set_functional_definitions({}, merge=False)
    set_resolve_functional(False)


def _quad(k1l):
    q = Quadrupole(
        name="q1", machine_area="S02",
        magnetic={"magnetic_length": 0.1, "k1l": k1l},
    )
    return MagnetTranslator.model_validate(q.model_dump())


def _cavity(field_amplitude, phase=0.0, structure="StandingWave"):
    cav = RFCavity(
        name="C1", machine_area="L02",
        cavity={"phase": phase, "structure_Type": structure},
        simulation={"field_amplitude": field_amplitude},
    )
    return RFCavityTranslator.model_validate(cav.model_dump())


class TestFullDumpResolution:
    def test_resolve_true_by_default(self):
        set_functional_definitions({"quad1_k1l": -2.0})
        qt = _quad("quad1_k1l")
        assert qt.full_dump()["magnetic_multipoles_K1L_normal"] == -2.0

    def test_resolve_false_keeps_symbolic(self):
        set_functional_definitions({"quad1_k1l": -2.0})
        qt = _quad("quad1_k1l")
        assert qt.full_dump(resolve=False)["magnetic_multipoles_K1L_normal"] == "quad1_k1l"

    def test_numeric_unaffected(self):
        qt = _quad(-2.0)
        assert qt.full_dump()["magnetic_multipoles_K1L_normal"] == -2.0


class TestElegantSymbolic:
    def test_quad_k1_passthrough(self):
        set_functional_definitions({"quad1_k1l": -2.0})
        out = _quad("quad1_k1l").to_elegant()
        # k1 is the normalized strength KnL/length, so the symbolic kl is
        # carried through divided by the (0.1 m) magnetic length.
        assert 'k1 = "quad1_k1l 0.1 /"' in out

    def test_quad_zero_length_k1_passthrough(self):
        set_functional_definitions({"quad1_k1l": -2.0})
        q = Quadrupole(
            name="q1", machine_area="S02",
            magnetic={"magnetic_length": 0.0, "k1l": "quad1_k1l"},
        )
        out = MagnetTranslator.model_validate(q.model_dump()).to_elegant()
        # zero-length: normalized strength equals the integrated value
        assert 'k1 = "quad1_k1l"' in out

    def test_quad_k1_numeric_unchanged(self):
        out = _quad(-2.0).to_elegant()
        # -2.0 / 0.1 m
        assert "k1 = -20.0" in out
        assert '"' not in out.split("k1 = ")[1].split(",")[0]

    def test_cavity_volt_passthrough(self):
        set_functional_definitions({"V_L02.01": 55e6})
        out = _cavity("V_L02.01").to_elegant()
        assert 'volt = "V_L02.01"' in out

    def test_cavity_phase_rpn(self):
        # ELEGANT phase convention is 90 - phase; symbolic -> rpn expression
        set_functional_definitions({"cav1_phase": 30.0})
        out = _cavity(1e6, phase="cav1_phase").to_elegant()
        assert 'phase = "90 cav1_phase -"' in out

    def test_header_lists_all_definitions(self):
        set_functional_definitions({"a": 1, "b": 2.5})
        header = elegant_functional_definitions()
        assert "% 1 sto a" in header
        assert "% 2.5 sto b" in header

    def test_header_empty_when_no_definitions(self):
        assert elegant_functional_definitions() == ""

    def test_resolution_mode_bakes_in_numbers(self):
        # With resolution mode on, ELEGANT gets resolved numbers and no rpn store
        set_functional_definitions({"quad1_k1l": -2.0})
        set_resolve_functional(True)
        out = _quad("quad1_k1l").to_elegant()
        assert "k1 = -20.0" in out  # -2.0 / 0.1 m, baked in
        assert '"quad1_k1l"' not in out
        assert "sto" not in out  # no % ... sto header


class TestDirectReadResolution:
    def test_cavity_phase_field_amplitude_resolve(self):
        set_functional_definitions({"V_L02.01": 55e6, "cav1_phase": 30.0})
        ct = _cavity("V_L02.01", phase="cav1_phase")
        assert ct.field_amplitude == 55e6
        assert ct.phase == 30.0


class TestCascadeToTranslators:
    def test_section_translator_carries_definitions(self, tmp_path):
        from laura.models.element import Quadrupole, Marker
        from laura.models.elementList import MachineModel
        from laura.translator.converters.section import SectionLatticeTranslator

        f = tmp_path / "defs.yaml"
        f.write_text("quad1_k1l: -2.0\n")
        q = Quadrupole(
            name="Q1", machine_area="S1",
            magnetic={"length": 0.1, "k1l": "quad1_k1l"},
            physical={"length": 0.1, "middle": {"x": 0, "y": 0, "z": 1.0}},
        )
        m = Marker(
            name="M1", machine_area="S1", hardware_class="Marker",
            physical={"middle": {"x": 0, "y": 0, "z": 0.0}},
        )
        mm = MachineModel(
            layout={"default_layout": "beam1", "layouts": {"beam1": ["S1"]}},
            section={"sections": {"S1": ["M1", "Q1"]}},
            elements={e.name: e for e in [m, q]},
            functional_definitions=str(f),
        )
        st = SectionLatticeTranslator.from_section(mm.sections["S1"])
        # the definitions are carried onto the translator (not just global state)
        assert st.functional_definitions == {"quad1_k1l": -2.0}
        out = st.to_elegant()
        assert "% -2.0 sto quad1_k1l" in out
        assert 'k1 = "quad1_k1l 0.1 /"' in out


class TestDipole:
    def _dipole(self, **magnetic):
        from laura.models.element import Dipole
        from laura.translator.converters.magnet import DipoleTranslator
        base = {"magnetic_length": 0.5}
        base.update(magnetic)
        d = Dipole(name="D1", machine_area="ARC", magnetic=base)
        return DipoleTranslator.model_validate(d.model_dump())

    def test_bend_angle_symbolic_and_resolved(self):
        set_functional_definitions({"bend1": 0.1})
        dt = self._dipole(k0l="bend1")
        assert 'angle = "bend1"' in dt.to_elegant()
        set_resolve_functional(True)
        assert "angle = 0.1" in dt.to_elegant()

    def test_functional_edge_angle_symbolic(self):
        set_functional_definitions({"bend1": 0.1, "e1v": 0.05})
        dt = self._dipole(k0l="bend1", entrance_edge_angle="e1v")
        assert 'e1 = "e1v"' in dt.to_elegant()

    def test_reserved_angle_edge_resolves(self):
        # "angle/2" references the bend angle and always resolves numerically
        set_functional_definitions({"bend1": 0.1})
        dt = self._dipole(k0l="bend1", exit_edge_angle="angle/2")
        assert "e2 = 0.05" in dt.to_elegant()


class TestXsuite:
    """Xsuite natively supports symbolic parameters via Environment variables, so
    functional values are passed through as deferred expressions."""

    def _line(self, elements, defs, beam_length=1, resolve=False):
        pytest.importorskip("xtrack")
        from laura.models.elementList import SectionLattice
        from laura.translator.converters.section import SectionLatticeTranslator

        section = SectionLattice(
            name="S", order=[e.name for e in elements], elements=elements,
            functional_definitions=defs, resolve_functional=resolve,
        )
        return SectionLatticeTranslator.from_section(section).to_xsuite(
            beam_length=beam_length, save=False
        )

    def _magnets(self):
        from laura.models.element import Quadrupole, Dipole, RFCavity
        from laura.models.physical import PhysicalElement, Position
        q = Quadrupole(
            name="Q1", machine_area="S",
            magnetic={"magnetic_length": 0.5, "k1l": "kq"},
            physical=PhysicalElement(length=0.5, middle=Position(x=0, y=0, z=1.0)),
        )
        d = Dipole(
            name="D1", machine_area="S",
            magnetic={"magnetic_length": 0.5, "k0l": "bend1"},
            physical=PhysicalElement(length=0.5, middle=Position(x=0, y=0, z=2.0)),
        )
        c = RFCavity(
            name="C1", machine_area="S",
            cavity={"phase": 0.0, "structure_Type": "StandingWave"},
            simulation={"field_amplitude": "Vcav"},
            physical=PhysicalElement(length=1.0, middle=Position(x=0, y=0, z=3.0)),
        )
        return [q, d, c]

    def test_symbolic_expressions_are_deferred(self):
        line = self._line(self._magnets(), {"kq": 0.3, "bend1": 0.1, "Vcav": 5e6})
        assert line["Q1"].k1 == pytest.approx(0.3 / 0.5)  # kq / length
        assert line["D1"].k0 == pytest.approx(0.1 / 0.5)  # bend1 / length
        assert line["C1"].voltage == pytest.approx(5e6)
        # the reference is a live deferred expression
        line.vars["kq"] = 0.9
        assert line["Q1"].k1 == pytest.approx(0.9 / 0.5)

    def test_resolved_mode_bakes_numbers(self):
        # resolve_functional set via the lattice (which cascades it globally)
        line = self._line(
            self._magnets(), {"kq": 0.3, "bend1": 0.1, "Vcav": 5e6}, resolve=True
        )
        assert line["Q1"].k1 == pytest.approx(0.3 / 0.5)
        # not a live reference: changing the (unused) var leaves k1 unchanged
        line.vars["kq"] = 0.9
        assert line["Q1"].k1 == pytest.approx(0.3 / 0.5)


class TestSolenoid:
    def test_solenoid_ks_symbolic_and_resolved(self, recwarn):
        from laura.models.element import Solenoid
        from laura.translator.converters.magnet import SolenoidTranslator

        set_functional_definitions({"sol_ks": 1.5})
        sol = Solenoid(
            name="SOL1", machine_area="INJ",
            magnetic={"magnetic_length": 0.2, "ks": "sol_ks"},
        )
        st = SolenoidTranslator.model_validate(sol.model_dump())
        # symbolic (default): ks passes through as the functional name
        assert 'ks = "sol_ks"' in st.to_elegant()
        # no pydantic "expected float, got str" serialization warning
        assert not any("serialized value" in str(w.message) for w in recwarn.list)
        # resolved mode bakes the number in
        set_resolve_functional(True)
        assert "ks = 1.5" in st.to_elegant()


class TestNonLinearLens:
    def test_resolve_and_symbolic(self):
        set_functional_definitions({"nll_k": 0.4})
        nll = NonLinearLens(
            name="nll1", machine_area="S02",
            magnetic={"knll": "nll_k", "cnll": 0.01, "magnetic_length": 0.1},
        )
        nt = NonLinearLensTranslator.model_validate(nll.model_dump())
        assert nt.full_dump()["magnetic_integrated_strength"] == 0.4
        assert nt.full_dump(resolve=False)["magnetic_integrated_strength"] == "nll_k"
