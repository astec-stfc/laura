"""Tests for the MAD-X TWISS TFS importer (``MadxLatticeImporter``).

Mirrors the ELEGANT importer's own design: a single file (here, a MAD-X
TWISS TFS table) supplies both element parameters and, via its own ``S``
column (MAD-X's cumulative arc-length at the exit of each element),
``position_mode="s"`` positioning. Since no MAD-X binary/cpymad is available
in this environment, the fixture is a hand-written TFS table exercising one
element of each type/collision this importer handles specially.
"""

import os
import math
import pytest

from laura.translator.converters.codes.madx import MadxLatticeImporter

_TWISS = os.path.join(os.path.dirname(__file__), "data", "madx_test_twiss.tfs")


@pytest.fixture
def importer():
    imp = MadxLatticeImporter(twiss_file=_TWISS)
    imp.create_laura_element_dictionary()
    return imp


class TestMadxImporter:
    def test_drift_not_imported(self, importer):
        assert "DR1" not in importer.elements

    def test_lattice_name_from_sequence_header(self, importer):
        assert importer.lattice_name == "TESTLINE"

    def test_marker(self, importer):
        assert importer.elements["BEG"].hardware_type == "Marker"

    def test_quadrupole_integrated_strength(self, importer):
        q = importer.elements["Q1"]
        assert q.hardware_type == "Quadrupole"
        # K1=0.4, L=0.5 -> K1L = 0.2
        assert q.magnetic.KnL(1) == pytest.approx(0.2)

    def test_dipole_angle_and_edges(self, importer):
        b = importer.elements["B1"]
        assert b.hardware_type == "Dipole"
        assert b.magnetic.KnL(0) == pytest.approx(0.1)
        assert b.magnetic.entrance_edge_angle == pytest.approx(0.05)
        assert b.magnetic.exit_edge_angle == pytest.approx(0.05)

    def test_sextupole_integrated_strength(self, importer):
        s = importer.elements["S1"]
        # K2=0.6, L=0.3 -> K2L = 0.18
        assert s.magnetic.KnL(2) == pytest.approx(0.18)

    def test_correctors_pick_up_plane_specific_kick(self, importer):
        hk = importer.elements["HK1"]
        vk = importer.elements["VK1"]
        cc = importer.elements["CC1"]
        assert hk.hardware_type == "Horizontal_Corrector"
        assert hk.magnetic.horizontal_kick == pytest.approx(0.03)
        assert vk.hardware_type == "Vertical_Corrector"
        assert vk.magnetic.vertical_kick == pytest.approx(0.04)
        assert cc.hardware_type == "Combined_Corrector"
        assert cc.magnetic.horizontal_kick == pytest.approx(0.02)
        assert cc.magnetic.vertical_kick == pytest.approx(0.03)

    def test_cavity_units_and_phase_convention(self, importer):
        c = importer.elements["C1"]
        assert c.hardware_type == "RFCavity"
        # VOLT is MV -> field_amplitude in V
        assert c.simulation.field_amplitude == pytest.approx(20.0e6)
        # FREQ is MHz -> frequency in Hz
        assert c.cavity.frequency == pytest.approx(2998.5e6)
        # lag=0.25 (crest) -> phase = 90 - 360*0.25 = 0
        assert c.cavity.phase == pytest.approx(0.0)

    def test_solenoid_field(self, importer):
        sol = importer.elements["SOL1"]
        assert sol.hardware_type == "Solenoid"
        # KS=0.4, L=0.5 -> integrated S0L = 0.2
        assert sol.magnetic.fields.S0L == pytest.approx(0.2)

    def test_rcollimator_disambiguated_and_sized(self, importer):
        col = importer.elements["COL1"]
        assert col.hardware_type == "Collimator"
        assert col.aperture.horizontal_size == pytest.approx(0.01)
        assert col.aperture.vertical_size == pytest.approx(0.02)

    def test_s_position_mode(self, importer):
        # position_mode="s" (default): physical.s comes straight from MAD-X's
        # own cumulative S column.
        assert importer.elements["Q1"].physical.s == pytest.approx(1.5)
        assert importer.elements["Q1"].physical.s_point == "end"

    def test_create_section_resolves_positions(self, importer):
        section = importer.create_section()
        seclat = list(section.values())[0]
        assert seclat.elements.elements["Q1"].physical.middle is not None

    def test_create_layout(self, importer):
        layout = importer.create_layout()
        assert layout.name == "TESTLINE"
        assert len(layout.sections) == 1
