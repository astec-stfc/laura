"""Tests for the PALS importer (``PalsLatticeImporter``).

PALS is parsed by the external ``palsparserpy`` package, which LAURA does not
depend on, so every test here is skipped where it is not installed.

Two fixtures back these tests: ``pals_test_lattice.pals.yaml``, one element of
each supported kind with values chosen so the conversions are checkable by
hand, and ``pals_test_branches.pals.yaml``, which carries the lattice-level
constructs -- a periodic branch, a repeated sub-line and a fork.
"""

import os

import pytest
from scipy.constants import speed_of_light

from laura.translator.converters.codes.pals import PalsLatticeImporter
from laura.translator.utils.pals import parser_available

_DATA = os.path.join(os.path.dirname(__file__), "data")
_LATTICE = os.path.join(_DATA, "pals_test_lattice.pals.yaml")
_BRANCHES = os.path.join(_DATA, "pals_test_branches.pals.yaml")
_TRAVELLING_WAVE = os.path.join(_DATA, "pals_test_travelling_wave.pals.yaml")

pytestmark = pytest.mark.skipif(
    not parser_available(), reason="palsparserpy is not installed"
)


@pytest.fixture
def elements():
    importer = PalsLatticeImporter(source_file=_LATTICE)
    with pytest.warns(UserWarning):
        return importer.create_laura_element_dictionary()


@pytest.fixture
def branches():
    return PalsLatticeImporter(source_file=_BRANCHES)


@pytest.fixture
def travelling_wave():
    importer = PalsLatticeImporter(source_file=_TRAVELLING_WAVE)
    return importer.create_laura_element_dictionary()


class TestPalsElements:
    def test_drifts_are_not_imported(self, elements):
        # LAURA regenerates drifts from the gaps between elements.
        assert "d1" not in elements
        assert "d2" not in elements

    def test_quadrupole_normalised_strength_is_integrated(self, elements):
        q1 = elements["q1"]
        assert q1.hardware_type == "Quadrupole"
        assert q1.magnetic.KnL(1) == pytest.approx(0.4)

    def test_unnormalised_field_uses_the_branch_reference(self, elements):
        # Bn1 = 1.2 T/m over 0.5 m, normalised as K = (q/P0) B with the momentum
        # the parser propagated from the beginning element's 1 GeV. The sign
        # follows the charge, as PALS defines the normalisation.
        momentum = (1.0e9**2 - 510998.95**2) ** 0.5
        assert elements["q2"].magnetic.KnL(1) == pytest.approx(
            -1.2 * 0.5 * speed_of_light / momentum, rel=1e-6
        )

    def test_sextupole_and_octupole(self, elements):
        assert elements["s1"].magnetic.KnL(2) == pytest.approx(1.5)
        octupole = elements["o1"].magnetic
        assert octupole.KnL(3) == pytest.approx(3.0)
        assert octupole.multipoles.K3L.skew == pytest.approx(0.5)

    def test_bend(self, elements):
        b1 = elements["b1"]
        assert b1.hardware_type == "Dipole"
        assert b1.magnetic.KnL(0) == pytest.approx(0.15)
        assert b1.magnetic.rho == pytest.approx(1.5 / 0.15)
        assert b1.magnetic.entrance_edge_angle == pytest.approx(0.05)
        assert b1.magnetic.exit_edge_angle == pytest.approx(0.03)
        assert b1.magnetic.tilt == pytest.approx(0.1)
        # PALS states the fint*hgap product; LAURA holds the two separately, so
        # the gap is pinned and the product kept as the integral.
        assert b1.magnetic.edge_field_integral == pytest.approx(0.02)
        assert b1.magnetic.exit_edge_field_integral == pytest.approx(0.04)
        assert b1.magnetic.gap == pytest.approx(2.0)

    def test_solenoid_strength_is_normalised_and_integrated(self, elements):
        sol = elements["sol1"]
        assert sol.hardware_type == "Solenoid"
        assert sol.magnetic.fields.S0L == pytest.approx(0.6 * 0.4)

    def test_cavity(self, elements):
        cav = elements["cav1"]
        assert cav.hardware_type == "RFCavity"
        assert cav.cavity.frequency == pytest.approx(1.3e9)
        assert cav.cavity.n_cells == 9
        # A standing-wave cavity is taken to run in pi mode, so one cell is
        # half a wavelength.
        assert cav.cavity.cell_length == pytest.approx(speed_of_light / (2 * 1.3e9))
        # PALS measures the phase in turns from the accelerating crest; LAURA
        # measures it in degrees from the zero crossing.
        assert cav.cavity.phase == pytest.approx(-90.0)
        assert cav.simulation.field_amplitude == pytest.approx(2.0e7)

    def test_travelling_wave_cell_length_uses_the_two_thirds_pi_mode(
        self, travelling_wave
    ):
        cav = travelling_wave["cav_tw"]
        assert cav.cavity.structure_type == "TravellingWave"
        assert cav.cavity.cell_length == pytest.approx(speed_of_light / (3 * 2998.5e6))

    def test_travelling_wave_amplitude_is_the_gradient_not_the_voltage(
        self, travelling_wave
    ):
        assert travelling_wave["cav_tw"].simulation.field_amplitude == pytest.approx(
            1.0e7
        )

    def test_correctors_take_the_plane_from_the_bmad_key(self, elements):
        kick1 = elements["kick1"]
        assert kick1.hardware_type == "Horizontal_Corrector"
        assert kick1.magnetic.horizontal_kick == pytest.approx(-0.001)

        kick2 = elements["kick2"]
        assert kick2.hardware_type == "Vertical_Corrector"
        assert kick2.magnetic.vertical_kick == pytest.approx(0.002)

    def test_unlabelled_kicker_keeps_both_planes(self, elements):
        kick3 = elements["kick3"]
        assert kick3.hardware_type == "Combined_Corrector"
        assert kick3.magnetic.horizontal_kick == pytest.approx(-0.003)
        assert kick3.magnetic.vertical_kick == pytest.approx(0.004)

    def test_instruments_are_disambiguated_by_the_bmad_key(self, elements):
        assert elements["mon1"].hardware_type == "Beam_Position_Monitor"
        assert elements["inst1"].hardware_type == "Diagnostic"

    def test_mask_becomes_a_sized_collimator(self, elements):
        col = elements["col1"]
        assert col.hardware_type == "Collimator"
        assert col.aperture.horizontal_size == pytest.approx(0.02)
        assert col.aperture.vertical_size == pytest.approx(0.04)
        assert col.aperture.shape == "rectangular"

    def test_body_shift_becomes_a_position_and_rotation_error(self, elements):
        off1 = elements["off1"]
        assert off1.physical.error.position.x == pytest.approx(0.001)
        # y_rot turns the opposite way from LAURA's theta.
        assert off1.physical.error.rotation.theta == pytest.approx(-0.002)
        assert off1.physical.error.rotation.psi == pytest.approx(0.003)

    def test_positions_are_the_exit_face(self, elements):
        assert elements["q1"].physical.s_point == "end"
        assert elements["q1"].physical.s == pytest.approx(1.5)
        assert elements["mark1"].physical.s == pytest.approx(6.85)

    def test_section_resolves_positions(self, elements):
        importer = PalsLatticeImporter(source_file=_LATTICE)
        with pytest.warns(UserWarning):
            section = importer.create_section()
        lattice = section["main_line"]
        assert lattice.elements.elements["q1"].physical.middle.z == pytest.approx(1.25)


class TestPalsLattice:
    def test_fork_makes_a_second_branch(self, branches):
        assert branches.branch_names() == ["ring", "dump"]

    def test_repeated_sublines_are_numbered_apart(self, branches):
        with pytest.warns(UserWarning, match="Fork"):
            layout = branches.create_layout()
        assert layout.sections["ring"].order == [
            "qf.1",
            "qd.1",
            "b.1",
            "qf.2",
            "qd.2",
            "b.2",
            "to_dump",
        ]

    def test_layout_carries_the_branch_reference(self, branches):
        with pytest.warns(UserWarning, match="Fork"):
            layout = branches.create_layout()
        assert layout.name == "lat1"
        assert layout.particle == "proton"
        ring = layout.sections["ring"]
        assert ring.geometry == "closed"
        assert ring.reference_energy == pytest.approx(2.0e9)
        dump = layout.sections["dump"]
        assert dump.geometry == "open"
        assert dump.reference_energy == pytest.approx(2.0e9)

    def test_forked_branch_keeps_its_own_elements(self, branches):
        with pytest.warns(UserWarning, match="Fork"):
            layout = branches.create_layout()
        dump = layout.sections["dump"]
        assert dump.order == ["dump_begin", "dump_quad", "dump_screen"]
        assert dump.elements.elements["dump_screen"].hardware_type == (
            "Beam_Position_Monitor"
        )

    def test_machine_model_merges_the_branches(self, branches):
        with pytest.warns(UserWarning):
            model = branches.create_machine_model(min_section_length=3)
        assert list(model.lattices) == ["lat1"]
        assert set(model.sections) == {"ring", "dump"}
        assert model.particle == "proton"
        assert model.elements["qf.1"].magnetic.KnL(1) == pytest.approx(0.6)

    def test_export_yaml_writes_a_summary(self, branches, tmp_path):
        with pytest.warns(UserWarning):
            model = branches.create_machine_model(min_section_length=3)
        branches.export_yaml(str(tmp_path), model)
        assert (tmp_path / "summary.yaml").exists()
