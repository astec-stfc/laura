"""Exports of the less common element types."""

import pytest

pytest.importorskip("easygdf")
pytest.importorskip("h5py")

from laura.models.element import (  # noqa: E402
    ElectrostaticSeparator,
    HorizontalACDipole,
    VerticalACDipole,
    Wire,
    WireScanner,
    BeamBeam,
    RFMultipole,
    MatrixTransform,
    TwissMatch,
    CrabCavity,
    RFCavity,
    Aperture,
    Collimator,
    Marker,
)
from laura.models.element_list import SectionLattice, MachineModel  # noqa: E402
from laura.translator.converters.converter import translate_elements  # noqa: E402
from laura.translator.converters.section import SectionLatticeTranslator  # noqa: E402
from laura.translator.converters.model import MachineModelTranslator  # noqa: E402


def _madx_element(element):
    madx = pytest.importorskip("cpymad.madx").Madx(stdout=False)
    madx.input(translate_elements([element])[element.name].to_madx())
    return madx.elements[element.name]


def _crab():
    return CrabCavity(
        name="cc1", machine_area="S",
        cavity={"phase": 0.0, "structure_type": "StandingWave"},
        simulation={"field_amplitude": 5e6}, physical={"length": 1.0},
    )


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
        es = ElectrostaticSeparator(
            name="es1", machine_area="S", simulation={"horizontal_field": 2e6},
        )
        assert _madx_element(es).ex == pytest.approx(2.0)


class TestACDipole:
    def test_madx_horizontal_and_vertical(self):
        hac = HorizontalACDipole(
            name="hac1", machine_area="S",
            simulation={"field_amplitude": 1e6, "frequency": 1e5, "phase": 0.0, "ramp": [1, 2, 3, 4]},
        )
        vac = VerticalACDipole(
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
        hac = HorizontalACDipole(
            name="hac1", machine_area="S", simulation={"field_amplitude": 1e6, "frequency": 1e5},
        )
        assert _madx_element(hac).volt == pytest.approx(1.0)

    def test_xsuite(self):
        pytest.importorskip("xtrack")
        hac = HorizontalACDipole(
            name="hac1", machine_area="S", simulation={"field_amplitude": 1e3, "frequency": 1e5},
        )
        vac = VerticalACDipole(
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
        hac = HorizontalACDipole(
            name="hac1", machine_area="S", simulation={"field_amplitude": 1e3, "frequency": 1e5},
        )
        translator = translate_elements([hac])["hac1"]
        # default: raw Hz passed through
        _, _, props = translator.to_xsuite(beam_length=1)
        assert props["freq"] == pytest.approx(1e5)
        # with a revolution frequency: Xsuite's per-turn convention
        _, _, props = translator.to_xsuite(beam_length=1, revolution_frequency=1e6)
        assert props["freq"] == pytest.approx(0.1)


class TestRevolutionFrequencyCascade:
    """Layouts and models cascade `revolution_frequency` to sections without their own."""

    @pytest.fixture(autouse=True)
    def _xtrack(self):
        pytest.importorskip("xtrack")

    def _lattice(self):
        hac = HorizontalACDipole(
            name="hac1", machine_area="S1", simulation={"field_amplitude": 1e3, "frequency": 1e5},
        )
        m = Marker(name="m1", machine_area="S1", hardware_class="Marker")
        return hac, m

    def test_section_level(self):
        hac, m = self._lattice()
        section = SectionLattice(name="S1", order=["m1", "hac1"], elements=[m, hac], revolution_frequency=2e6)
        line = SectionLatticeTranslator.from_section(section).to_xsuite(beam_length=1, save=False)
        assert line["hac1"].freq == pytest.approx(1e5 / 2e6)

    def test_section_without_its_own_frequency_stays_unconverted(self):
        hac, m = self._lattice()
        section = SectionLattice(name="S1", order=["m1", "hac1"], elements=[m, hac])
        line = SectionLatticeTranslator.from_section(section).to_xsuite(beam_length=1, save=False)
        assert line["hac1"].freq == pytest.approx(1e5)

    def test_cascades_from_machine_model_to_section(self):
        hac, m = self._lattice()
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
        # A symbolic-looking `plane` would route through env.new(), whose allow-list lacks ACDipole.
        hac, m = self._lattice()
        section = SectionLattice(name="S1", order=["m1", "hac1"], elements=[m, hac])
        line = SectionLatticeTranslator.from_section(section).to_xsuite(beam_length=1, save=False)
        assert line["hac1"].plane == "h"


class TestWireScanner:
    """``WireScanner`` is a profile diagnostic, unrelated to the beam-beam ``Wire``."""

    def test_is_a_diagnostic_and_registered(self):
        from laura.models.element import Diagnostic, ELEMENT_REGISTRY

        ws = WireScanner(name="ws1", machine_area="S")
        assert isinstance(ws, Diagnostic)
        assert not isinstance(ws, Wire)
        assert ws.hardware_type == "WireScanner"
        assert ELEMENT_REGISTRY["WireScanner"] is WireScanner

    @pytest.mark.parametrize(
        "method, expected",
        [
            ("to_elegant", "ws1: watch"),
            ("to_bmad", "ws1: instrument"),
            ("to_madx", "ws1: instrument"),
        ],
    )
    def test_exports_as_a_passive_diagnostic(self, method, expected):
        ws = WireScanner(name="ws1", machine_area="S")
        assert getattr(translate_elements([ws])["ws1"], method)().startswith(expected)


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
        w = Wire(name="w1", machine_area="S", simulation={"current": 100, "horizontal_offset": 0.01})
        assert list(_madx_element(w).current) == pytest.approx([100.0])

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
        bb = _madx_element(BeamBeam(name="bb1", machine_area="S", simulation={"charge": -1.0, "n_particles": 1e11}))
        assert bb.npart == pytest.approx(1e11)
        assert bb.charge == pytest.approx(-1.0)

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
        rfm = RFMultipole(
            name="rfm1", machine_area="S",
            simulation={"frequency": 4e8, "field_amplitude": 1e6, "knl": [0, 0.1, 0, 0, 0]},
        )
        assert list(_madx_element(rfm).knl)[1] == pytest.approx(0.1)

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
    def test_matrix_transform_dispatches_to_dedicated_translator(self):
        from laura.translator.converters.matrix import MatrixTransformTranslator
        mt = MatrixTransform(name="mt1", machine_area="S", simulation={"r_matrix": {"r21": 0.5}})
        assert isinstance(translate_elements([mt])["mt1"], MatrixTransformTranslator)

    def test_twiss_match_madx_is_zero_length_marker(self):
        twiss = TwissMatch(name="match1", machine_area="S")

        assert translate_elements([twiss])["match1"].to_madx() == "match1: marker;\n"

    def test_crab_cavity_dispatches_to_rfcavity_translator(self):
        from laura.translator.converters.cavity import RFCavityTranslator
        assert isinstance(translate_elements([_crab()])["cc1"], RFCavityTranslator)

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
        assert out.startswith("mt1: ematrix")
        assert out.strip().endswith(";")
        assert "L = 0.5" in out
        assert "R21 = 0.5" in out

    def test_matrix_transform_elegant_writes_the_diagonal_out(self):
        """elegant's EMATRIX starts from the zero matrix; MAD-X's `matrix` from the identity."""
        mt = MatrixTransform(
            name="mt1", machine_area="S",
            simulation={"r_matrix": {"r12": 1.677, "r34": 1.677}},
            physical={"length": 1.677},
        )
        out = translate_elements([mt])["mt1"].to_elegant()
        for i in range(1, 7):
            assert f"R{i}{i} = 1.0" in out
        assert "R12 = 1.677" in out
        assert "R34 = 1.677" in out
        # zeros are still omitted
        assert out.count("R") == 8

    def test_matrix_transform_elegant_writes_an_identity_matrix(self):
        """With only a length, elegant would build the zero matrix."""
        mt = MatrixTransform(name="mt1", machine_area="S", physical={"length": 0.5})
        out = translate_elements([mt])["mt1"].to_elegant()
        for i in range(1, 7):
            assert f"R{i}{i} = 1.0" in out

    def test_crab_cavity_elegant_uses_rfdf_not_rfca(self):
        out = translate_elements([_crab()])["cc1"].to_elegant()
        assert "cc1: rfdf" in out
        assert "voltage = 5000000.0" in out
        # +90 degree ELEGANT phase convention applied
        assert "phase = 90.0" in out
        assert out.count("n_kicks") == 1

    def test_crab_cavity_madx(self):
        out = translate_elements([_crab()])["cc1"].to_madx()
        assert "cc1: crabcavity" in out
        assert "volt = 5.0" in out

    def test_crab_cavity_xsuite_ocelot_cheetah_do_not_crash(self):
        pytest.importorskip("xtrack")
        pytest.importorskip("ocelot")
        pytest.importorskip("cheetah")
        translator = translate_elements([_crab()])["cc1"]
        assert translator.to_xsuite(beam_length=1)[1].__name__ == "CrabCavity"
        assert translator.to_ocelot() is not None
        assert translator.to_cheetah() is not None

    def test_thin_cavity_survives_ocelot(self):
        """Ocelot divides by a cavity's length; CLIC DR's RF is thin."""
        oc = pytest.importorskip("ocelot")
        cav = RFCavity(
            name="rf", machine_area="S", physical={"length": 0.0},
            cavity={"phase": 0.0, "frequency": 3e9, "structure_type": "StandingWave"},
            simulation={"field_amplitude": 4.5e6},
        )
        element = translate_elements([cav])["rf"].to_ocelot()
        assert 0 < element.l < 1e-8
        twiss = oc.Twiss()
        twiss.E, twiss.beta_x, twiss.beta_y = 2.86, 1.0, 1.0
        oc.twiss(oc.MagneticLattice([oc.Drift(l=1.0), element]), twiss)


class TestMadxCavityAndAperture:
    # MAD-X's twcavity does not accelerate, so TW cavities are rfcavity too (focusing via a MATRIX).
    # ELEGANT defaults to SRS (standing wave); TW cavities request TW1 to match MAD-X/Ocelot focusing.
    @pytest.mark.parametrize(
        "cavity, method, expected",
        [
            ({"structure_type": "TravellingWave", "mode_numerator": 2, "mode_denominator": 3},
             "to_madx", "c1: rfcavity"),
            ({"structure_type": "StandingWave"}, "to_madx", "c1: rfcavity"),
            ({"structure_type": "TravellingWave", "mode_numerator": 2, "mode_denominator": 3},
             "to_elegant", "body_focus_model = TW1"),
            ({"structure_type": "StandingWave"}, "to_elegant", "body_focus_model = SRS"),
        ],
        ids=["tw-madx", "sw-madx", "tw-elegant", "sw-elegant"],
    )
    def test_cavity_export(self, cavity, method, expected):
        cav = RFCavity(
            name="c1", machine_area="S",
            cavity={"phase": 0.0, **cavity},
            simulation={"field_amplitude": 20e6}, physical={"length": 1.0},
        )
        assert expected in getattr(translate_elements([cav])["c1"], method)()

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


@pytest.mark.parametrize("geometry, change_p0", [("closed", 0), ("open", 1), (None, 1)])
def test_ring_cavity_leaves_the_reference_momentum_alone(geometry, change_p0):
    """A ring's reference is its design momentum; ELEGANT refuses closed optics otherwise."""
    cavity = RFCavity(
        name="rf", machine_area="S", physical={"length": 0.0},
        cavity={"phase": 0.0, "frequency": 3e9, "structure_type": "StandingWave"},
        simulation={"field_amplitude": 4.5e6},
    )
    section = SectionLattice(name="S", order=["rf"], elements=[cavity], geometry=geometry)
    written = SectionLatticeTranslator.from_section(section).to_elegant()
    assert f"change_p0 = {change_p0}" in written
    assert cavity.simulation.change_p0 == 1  # the lattice keeps its own


@pytest.mark.parametrize("length, written", [(0.0, False), (1.0, True)])
def test_thin_cavity_has_no_body_focusing(length, written):
    """ELEGANT's body focusing scales as 1/L."""
    cavity = RFCavity(
        name="rf", machine_area="S", physical={"length": length},
        cavity={"phase": 0.0, "frequency": 2e9, "structure_type": "StandingWave"},
        simulation={"field_amplitude": 4.5e6},
    )
    assert ("body_focus_model" in translate_elements([cavity])["rf"].to_elegant()) is written
