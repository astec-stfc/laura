"""Tests for the newly-added element types (ElectrostaticSeparator, AC dipoles,
Wire, BeamBeam, RFMultipole) and the fixes made to the already-existing
MatrixTransform/CrabCavity wiring, plus the MAD-X twcavity/ecollimator
sub-type selection.
"""

import pytest

pytest.importorskip("easygdf")
pytest.importorskip("h5py")

from laura.models.element import (  # noqa: E402
    ElectrostaticSeparator,
    Horizontal_AC_Dipole,
    Vertical_AC_Dipole,
    Wire,
    BeamBeam,
    RFMultipole,
    MatrixTransform,
    CrabCavity,
    RFDeflectingCavity,
    RFCavity,
    Aperture,
    Collimator,
    Marker,
)
from laura.models.elementList import SectionLattice, MachineModel  # noqa: E402
from laura.translator.converters.converter import translate_elements  # noqa: E402
from laura.translator.converters.section import SectionLatticeTranslator  # noqa: E402
from laura.translator.converters.model import MachineModelTranslator  # noqa: E402


class TestElectrostaticSeparator:
    def test_madx(self):
        es = ElectrostaticSeparator(
            name="es1", machine_area="S",
            simulation={"horizontal_field": 2e6, "vertical_field": 1e6},
            physical={"length": 2.0},
        )
        out = translate_elements([es])["es1"].to_madx()
        assert "es1: elseparator" in out
        assert "ex = 2.0" in out
        assert "ey = 1.0" in out

    def test_madx_parses(self):
        pytest.importorskip("cpymad")
        from cpymad.madx import Madx
        es = ElectrostaticSeparator(
            name="es1", machine_area="S", simulation={"horizontal_field": 2e6},
        )
        madx = Madx(stdout=False)
        madx.input(translate_elements([es])["es1"].to_madx())
        assert madx.elements["es1"].ex == pytest.approx(2.0)


class TestACDipole:
    def test_madx_horizontal_and_vertical(self):
        hac = Horizontal_AC_Dipole(
            name="hac1", machine_area="S",
            simulation={"field_amplitude": 1e6, "frequency": 1e5, "phase": 0.0, "ramp": [1, 2, 3, 4]},
        )
        vac = Vertical_AC_Dipole(
            name="vac1", machine_area="S", simulation={"field_amplitude": 2e6, "frequency": 2e5},
        )
        d = translate_elements([hac, vac])
        h_out = d["hac1"].to_madx()
        v_out = d["vac1"].to_madx()
        assert "hac1: hacdipole" in h_out
        assert "volt = 1.0" in h_out
        assert "freq = 0.1" in h_out
        assert "ramp1 = 1" in h_out and "ramp4 = 4" in h_out
        assert "vac1: vacdipole" in v_out

    def test_madx_parses(self):
        pytest.importorskip("cpymad")
        from cpymad.madx import Madx
        hac = Horizontal_AC_Dipole(
            name="hac1", machine_area="S", simulation={"field_amplitude": 1e6, "frequency": 1e5},
        )
        madx = Madx(stdout=False)
        madx.input(translate_elements([hac])["hac1"].to_madx())
        assert madx.elements["hac1"].volt == pytest.approx(1.0)

    def test_xsuite(self):
        pytest.importorskip("xtrack")
        hac = Horizontal_AC_Dipole(
            name="hac1", machine_area="S", simulation={"field_amplitude": 1e3, "frequency": 1e5},
        )
        vac = Vertical_AC_Dipole(
            name="vac1", machine_area="S", simulation={"field_amplitude": 1e3, "frequency": 1e5},
        )
        d = translate_elements([hac, vac])
        _, cls, props = d["hac1"].to_xsuite(beam_length=1)
        assert props["plane"] == "h"
        _, cls, props = d["vac1"].to_xsuite(beam_length=1)
        assert props["plane"] == "v"
        obj = cls(**props)
        assert obj is not None

    def test_xsuite_revolution_frequency_conversion(self):
        pytest.importorskip("xtrack")
        hac = Horizontal_AC_Dipole(
            name="hac1", machine_area="S", simulation={"field_amplitude": 1e3, "frequency": 1e5},
        )
        translator = translate_elements([hac])["hac1"]
        # default: raw Hz value passed through unconverted
        _, _, props = translator.to_xsuite(beam_length=1)
        assert props["freq"] == pytest.approx(1e5)
        # explicit revolution frequency: converted to Xsuite's per-turn convention
        _, _, props = translator.to_xsuite(beam_length=1, revolution_frequency=1e6)
        assert props["freq"] == pytest.approx(0.1)


class TestRevolutionFrequencyCascade:
    """`revolution_frequency` is an optional attribute on SectionLattice,
    MachineLayout, and MachineModel; SectionLatticeTranslator.to_xsuite feeds
    its own value through to any ACDipoleTranslator elements it translates,
    and MachineLayoutTranslator/MachineModelTranslator cascade their own value
    down to child sections/layouts that don't define their own."""

    def _lattice(self, revolution_frequency=None):
        hac = Horizontal_AC_Dipole(
            name="hac1", machine_area="S1", simulation={"field_amplitude": 1e3, "frequency": 1e5},
        )
        m = Marker(name="m1", machine_area="S1", hardware_class="Marker")
        return hac, m, revolution_frequency

    def test_section_level(self):
        pytest.importorskip("xtrack")
        hac, m, _ = self._lattice()
        section = SectionLattice(name="S1", order=["m1", "hac1"], elements=[m, hac], revolution_frequency=2e6)
        line = SectionLatticeTranslator.from_section(section).to_xsuite(beam_length=1, save=False)
        assert line["hac1"].freq == pytest.approx(1e5 / 2e6)

    def test_section_without_its_own_frequency_stays_unconverted(self):
        pytest.importorskip("xtrack")
        hac, m, _ = self._lattice()
        section = SectionLattice(name="S1", order=["m1", "hac1"], elements=[m, hac])
        line = SectionLatticeTranslator.from_section(section).to_xsuite(beam_length=1, save=False)
        assert line["hac1"].freq == pytest.approx(1e5)

    def test_cascades_from_machine_model_to_section(self):
        pytest.importorskip("xtrack")
        hac, m, _ = self._lattice()
        mm = MachineModel(
            layout={"default_layout": "beam1", "layouts": {"beam1": ["S1"]}},
            section={"sections": {"S1": ["m1", "hac1"]}},
            elements={e.name: e for e in [m, hac]},
            revolution_frequency=4e6,
        )
        result = MachineModelTranslator.from_machine(mm).to_xsuite(beam_length=1, save=False)
        line = result["beam1"]["S1"]
        assert line["hac1"].freq == pytest.approx(1e5 / 4e6)

    def test_categorical_string_parameters_do_not_trigger_deferred_expression_path(self):
        # ACDipole's `plane` ("h"/"v") is a plain categorical string, not a
        # functional-definition reference, so it must not be mistaken for a
        # symbolic value (which would route construction through env.new(),
        # and ACDipole is not in xtrack's env.new() allow-list).
        pytest.importorskip("xtrack")
        hac, m, _ = self._lattice()
        section = SectionLattice(name="S1", order=["m1", "hac1"], elements=[m, hac])
        # Should not raise.
        line = SectionLatticeTranslator.from_section(section).to_xsuite(beam_length=1, save=False)
        assert line["hac1"].plane == "h"


class TestWire:
    def test_madx(self):
        w = Wire(
            name="w1", machine_area="S",
            simulation={"current": 100, "horizontal_offset": 0.01, "interaction_length": 0.02},
            physical={"length": 0.03},
        )
        out = translate_elements([w])["w1"].to_madx()
        assert "w1: wire" in out
        assert "current = {100.0}" in out
        assert "xma = {0.01}" in out

    def test_madx_parses(self):
        pytest.importorskip("cpymad")
        from cpymad.madx import Madx
        w = Wire(name="w1", machine_area="S", simulation={"current": 100, "horizontal_offset": 0.01})
        madx = Madx(stdout=False)
        madx.input(translate_elements([w])["w1"].to_madx())
        assert list(madx.elements["w1"].current) == pytest.approx([100.0])

    def test_xsuite(self):
        pytest.importorskip("xtrack")
        w = Wire(
            name="w1", machine_area="S",
            simulation={"current": 100, "horizontal_offset": 0.01}, physical={"length": 0.03},
        )
        _, cls, props = translate_elements([w])["w1"].to_xsuite(beam_length=1)
        assert props["L_phy"] == pytest.approx(0.03)
        assert cls(**props) is not None


class TestBeamBeam:
    def test_madx(self):
        bb = BeamBeam(
            name="bb1", machine_area="S",
            simulation={"n_particles": 1e11, "horizontal_sigma": 1e-5, "vertical_sigma": 2e-5},
        )
        out = translate_elements([bb])["bb1"].to_madx()
        assert "bb1: beambeam" in out
        assert "npart = 100000000000.0" in out
        assert "sigx = 1e-05" in out

    def test_madx_parses(self):
        pytest.importorskip("cpymad")
        from cpymad.madx import Madx
        bb = BeamBeam(name="bb1", machine_area="S", simulation={"charge": -1.0, "n_particles": 1e11})
        madx = Madx(stdout=False)
        madx.input(translate_elements([bb])["bb1"].to_madx())
        assert madx.elements["bb1"].npart == pytest.approx(1e11)
        assert madx.elements["bb1"].charge == pytest.approx(-1.0)

    def test_elegant_charge_is_total_coulombs(self):
        from laura.models.constants import elementary_charge
        bb = BeamBeam(
            name="bb1", machine_area="S",
            simulation={"charge": -1.0, "n_particles": 1e11, "horizontal_offset": 0.001},
        )
        out = translate_elements([bb])["bb1"].to_elegant()
        assert "bb1: beambeam" in out
        assert f"charge = {-1e11 * elementary_charge}" in out
        assert "xcenter = 0.001" in out

    def test_xsuite(self):
        pytest.importorskip("xfields")
        bb = BeamBeam(
            name="bb1", machine_area="S",
            simulation={
                "charge": -1.0, "n_particles": 1e11,
                "horizontal_sigma": 1e-5, "vertical_sigma": 2e-5,
                "horizontal_offset": 0.001,
            },
        )
        name, cls, props = translate_elements([bb])["bb1"].to_xsuite(beam_length=1)
        assert cls.__name__ == "BeamBeamBiGaussian2D"
        assert props["other_beam_q0"] == pytest.approx(-1.0)
        assert props["other_beam_num_particles"] == pytest.approx(1e11)
        assert props["other_beam_Sigma_11"] == pytest.approx((1e-5) ** 2)
        assert props["other_beam_Sigma_33"] == pytest.approx((2e-5) ** 2)
        assert cls(**props) is not None


class TestRFMultipole:
    def test_madx(self):
        rfm = RFMultipole(
            name="rfm1", machine_area="S",
            simulation={"frequency": 4e8, "field_amplitude": 1e6, "phase": 0.0, "knl": [0, 0.1, 0, 0, 0]},
            physical={"length": 0.1},
        )
        out = translate_elements([rfm])["rfm1"].to_madx()
        assert "rfm1: rfmultipole" in out
        assert "volt = 1.0" in out
        assert "freq = 400.0" in out
        assert "lag = 0.25" in out
        assert "knl = {0.0, 0.1, 0.0, 0.0, 0.0}" in out

    def test_madx_parses(self):
        pytest.importorskip("cpymad")
        from cpymad.madx import Madx
        rfm = RFMultipole(
            name="rfm1", machine_area="S",
            simulation={"frequency": 4e8, "field_amplitude": 1e6, "knl": [0, 0.1, 0, 0, 0]},
        )
        madx = Madx(stdout=False)
        madx.input(translate_elements([rfm])["rfm1"].to_madx())
        assert list(madx.elements["rfm1"].knl)[1] == pytest.approx(0.1)

    def test_xsuite(self):
        pytest.importorskip("xtrack")
        rfm = RFMultipole(
            name="rfm1", machine_area="S",
            simulation={"frequency": 4e8, "field_amplitude": 1e6, "knl": [0, 0.1, 0, 0, 0]},
        )
        _, cls, props = translate_elements([rfm])["rfm1"].to_xsuite(beam_length=1)
        assert props["knl"] == [0.0, 0.1, 0.0, 0.0, 0.0]
        assert cls(**props) is not None


class TestMatrixTransformAndCrabCavityDispatch:
    """Both were added to the model but not fully wired into translate_elements()."""

    def test_matrix_transform_dispatches_to_dedicated_translator(self):
        from laura.translator.converters.matrix import MatrixTransformTranslator
        mt = MatrixTransform(name="mt1", machine_area="S", simulation={"r_matrix": {"r21": 0.5}})
        assert isinstance(translate_elements([mt])["mt1"], MatrixTransformTranslator)

    def test_crab_cavity_dispatches_to_rfcavity_translator(self):
        from laura.translator.converters.cavity import RFCavityTranslator
        cc = CrabCavity(
            name="cc1", machine_area="S",
            cavity={"phase": 0.0, "structure_Type": "StandingWave"},
            simulation={"field_amplitude": 5e6}, physical={"length": 1.0},
        )
        assert isinstance(translate_elements([cc])["cc1"], RFCavityTranslator)

    def test_matrix_transform_madx(self):
        mt = MatrixTransform(
            name="mt1", machine_area="S", simulation={"r_matrix": {"r21": 0.5}}, physical={"length": 0.5},
        )
        out = translate_elements([mt])["mt1"].to_madx()
        assert "mt1: matrix" in out
        assert "rm21 = 0.5" in out

    def test_matrix_transform_elegant_is_well_formed(self):
        mt = MatrixTransform(
            name="mt1", machine_area="S", simulation={"r_matrix": {"r21": 0.5}}, physical={"length": 0.5},
        )
        out = translate_elements([mt])["mt1"].to_elegant()
        # element name/type must be the string's own prefix, not appended after
        # the parameters (this was the pre-existing bug).
        assert out.startswith("mt1: ematrix")
        assert out.strip().endswith(";")
        assert "R21 = 0.5" in out

    def test_crab_cavity_elegant_uses_rfdf_not_rfca(self):
        cc = CrabCavity(
            name="cc1", machine_area="S",
            cavity={"phase": 0.0, "structure_Type": "StandingWave"},
            simulation={"field_amplitude": 5e6}, physical={"length": 1.0},
        )
        out = translate_elements([cc])["cc1"].to_elegant()
        assert "cc1: rfdf" in out
        assert "voltage = 5000000.0" in out
        # +90 degree ELEGANT phase convention applied
        assert "phase = 90.0" in out
        # no duplicate n_kicks entries (pre-existing bug)
        assert out.count("n_kicks") == 1

    def test_rf_deflecting_cavity_elegant_uses_rfdf_not_rfca(self):
        # Regression check: this was broken the same way before CrabCavity
        # existed -- RFDeflectingCavity always fell back to plain RFCA
        # whenever no wakefield was defined (the common case).
        rdc = RFDeflectingCavity(
            name="rdc1", machine_area="S",
            cavity={"phase": 0.0, "structure_Type": "StandingWave"},
            simulation={"field_amplitude": 5e6}, physical={"length": 1.0},
        )
        out = translate_elements([rdc])["rdc1"].to_elegant()
        assert "rdc1: rfdf" in out

    def test_crab_cavity_madx(self):
        cc = CrabCavity(
            name="cc1", machine_area="S",
            cavity={"phase": 0.0, "structure_Type": "StandingWave"},
            simulation={"field_amplitude": 5e6}, physical={"length": 1.0},
        )
        out = translate_elements([cc])["cc1"].to_madx()
        assert "cc1: crabcavity" in out
        assert "volt = 5.0" in out

    def test_crab_cavity_xsuite_ocelot_cheetah_do_not_crash(self):
        pytest.importorskip("xtrack")
        pytest.importorskip("ocelot")
        pytest.importorskip("cheetah")
        cc = CrabCavity(
            name="cc1", machine_area="S",
            cavity={"phase": 0.0, "structure_Type": "StandingWave"},
            simulation={"field_amplitude": 5e6}, physical={"length": 1.0},
        )
        translator = translate_elements([cc])["cc1"]
        assert translator.to_xsuite(beam_length=1)[1].__name__ == "CrabCavity"
        assert translator.to_ocelot() is not None
        assert translator.to_cheetah() is not None


class TestMadxCavityAndAperture:
    def test_travelling_wave_cavity_uses_twcavity(self):
        cav = RFCavity(
            name="c1", machine_area="S",
            cavity={"structure_Type": "TravellingWave", "phase": 0.0},
            simulation={"field_amplitude": 20e6}, physical={"length": 1.0},
        )
        out = translate_elements([cav])["c1"].to_madx()
        assert "c1: twcavity" in out

    def test_standing_wave_cavity_uses_rfcavity(self):
        cav = RFCavity(
            name="c1", machine_area="S",
            cavity={"structure_Type": "StandingWave", "phase": 0.0},
            simulation={"field_amplitude": 20e6}, physical={"length": 1.0},
        )
        out = translate_elements([cav])["c1"].to_madx()
        assert "c1: rfcavity" in out

    def test_elliptical_aperture_uses_ecollimator(self):
        ap = Aperture(
            name="ap1", machine_area="S",
            aperture={"horizontal_size": 0.01, "vertical_size": 0.02, "shape": "elliptical"},
        )
        out = translate_elements([ap])["ap1"].to_madx()
        assert "ap1: ecollimator" in out

    def test_rectangular_collimator_uses_rcollimator(self):
        col = Collimator(
            name="col1", machine_area="S",
            aperture={"horizontal_size": 0.03, "vertical_size": 0.04, "shape": "rectangular"},
            physical={"length": 0.1},
        )
        out = translate_elements([col])["col1"].to_madx()
        assert "col1: rcollimator" in out
