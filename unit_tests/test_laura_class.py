"""Tests for the LAURA main class — constructor, getters, all_* properties."""

import pytest
import os
import tempfile
import shutil

from laura import LAURA
from laura.models.element import (
    Quadrupole,
    Dipole,
    Sextupole,
    Marker,
    Drift,
    RFCavity,
    Beam_Position_Monitor,
    Screen,
    Solenoid,
    PhysicalBaseElement,
    Horizontal_Corrector,
    Vertical_Corrector,
    Shutter,
    Aperture,
)
from laura.models.physical import Position
from laura.models.elementList import MachineModel
from laura.Exporters.YAML import export_machine, export_as_yaml

# ---------------------------------------------------------------------------
# Fixtures: small FODO-like machine
# ---------------------------------------------------------------------------


@pytest.fixture
def fodo_elements():
    """Create a FODO lattice of Marker, Quad, Quad, Marker."""
    m1 = Marker(
        name="M1",
        machine_area="FODO",
        hardware_class="Marker",
        physical={"middle": {"x": 0.0, "y": 0.0, "z": 0.0}},
    )
    q1f = Quadrupole(
        name="QF",
        machine_area="FODO",
        magnetic={"length": 0.3, "k1l": -1.0},
        physical={"length": 0.3, "middle": {"x": 0.0, "y": 0.0, "z": 0.75}},
    )
    q1d = Quadrupole(
        name="QD",
        machine_area="FODO",
        magnetic={"length": 0.3, "k1l": 1.0},
        physical={"length": 0.3, "middle": {"x": 0.0, "y": 0.0, "z": 2.25}},
    )
    m2 = Marker(
        name="M2",
        machine_area="FODO",
        hardware_class="Marker",
        physical={"middle": {"x": 0.0, "y": 0.0, "z": 3.0}},
    )
    return [m1, q1f, q1d, m2]


@pytest.fixture
def fodo_machine(fodo_elements):
    """LAURA machine built from element list."""
    sections = {"sections": {"FODO": ["M1", "QF", "QD", "M2"]}}
    layouts = {"default_layout": "line1", "layouts": {"line1": ["FODO"]}}
    return LAURA(
        element_list=fodo_elements,
        layout=layouts,
        section=sections,
    )


@pytest.fixture
def rich_machine():
    """A richer machine with magnets, diagnostics, RF, aperture, etc."""
    elems = [
        Marker(
            name="START",
            machine_area="S1",
            hardware_class="Marker",
            physical={"middle": {"x": 0.0, "y": 0.0, "z": 0.0}},
        ),
        Quadrupole(
            name="Q1",
            machine_area="S1",
            magnetic={"length": 0.3, "k1l": -1.0},
            physical={"length": 0.3, "middle": {"x": 0.0, "y": 0.0, "z": 0.5}},
        ),
        Beam_Position_Monitor(
            name="BPM1",
            machine_area="S1",
            hardware_class="Diagnostic",
            physical={"middle": {"x": 0.0, "y": 0.0, "z": 1.2}},
        ),
        Dipole(
            name="D1",
            machine_area="S1",
            magnetic={"length": 0.5, "angle": 0.0},
            physical={"length": 0.5, "middle": {"x": 0.0, "y": 0.0, "z": 2.0}},
        ),
        Sextupole(
            name="SX1",
            machine_area="S1",
            magnetic={"length": 0.1, "k2l": 5.0},
            physical={"length": 0.1, "middle": {"x": 0.0, "y": 0.0, "z": 2.6}},
        ),
        Solenoid(
            name="SOL1",
            machine_area="S1",
            magnetic={"length": 0.2},
            physical={"length": 0.2, "middle": {"x": 0.0, "y": 0.0, "z": 3.0}},
        ),
        Marker(
            name="END",
            machine_area="S1",
            hardware_class="Marker",
            physical={"middle": {"x": 0.0, "y": 0.0, "z": 4.0}},
        ),
    ]
    sections = {"sections": {"S1": [e.name for e in elems]}}
    layouts = {"default_layout": "beam1", "layouts": {"beam1": ["S1"]}}
    return LAURA(element_list=elems, layout=layouts, section=sections)


# ---------------------------------------------------------------------------
# Construction
# ---------------------------------------------------------------------------


class TestLAURAConstruction:
    def test_from_element_list(self, fodo_machine):
        assert "M1" in fodo_machine.elements
        assert "QF" in fodo_machine.elements
        assert "QD" in fodo_machine.elements
        assert "M2" in fodo_machine.elements

    def test_sections_built(self, fodo_machine):
        assert "FODO" in fodo_machine.sections

    def test_lattices_built(self, fodo_machine):
        assert "line1" in fodo_machine.lattices

    def test_default_path(self, fodo_machine):
        assert fodo_machine.default_path == "line1"

    def test_element_access_by_name(self, fodo_machine):
        qf = fodo_machine["QF"]
        assert qf.name == "QF"
        assert qf.hardware_type == "Quadrupole"

    def test_element_access_multiple(self, fodo_machine):
        elems = fodo_machine[["M1", "M2"]]
        assert len(elems) == 2
        assert elems[0].name == "M1"

    def test_iter(self, fodo_machine):
        names = list(fodo_machine)
        assert "QF" in names

    def test_invalid_element_list_raises(self):
        with pytest.raises(ValueError):
            LAURA(
                element_list="/nonexistent/path",
                layout={"default_layout": "a", "layouts": {"a": ["SEC"]}},
                section={"sections": {"SEC": []}},
            )


# ---------------------------------------------------------------------------
# get_* methods
# ---------------------------------------------------------------------------


class TestLAURAGetters:
    def test_get_elements_returns_all(self, fodo_machine):
        elems = fodo_machine.get_elements()
        assert "M1" in elems
        assert "QF" in elems
        assert "QD" in elems
        assert "M2" in elems

    def test_get_elements_between(self, fodo_machine):
        elems = fodo_machine.get_elements(start="QF", end="QD")
        assert elems == ["QF", "QD"]

    def test_get_magnets(self, rich_machine):
        mags = rich_machine.get_magnets()
        assert "Q1" in mags
        assert "D1" in mags
        assert "SX1" in mags

    def test_get_quadrupoles(self, rich_machine):
        quads = rich_machine.get_quadrupoles()
        assert "Q1" in quads
        assert "D1" not in quads

    def test_get_dipoles(self, rich_machine):
        dips = rich_machine.get_dipoles()
        assert "D1" in dips
        assert "Q1" not in dips

    def test_get_sextupoles(self, rich_machine):
        sexts = rich_machine.get_sextupoles()
        assert "SX1" in sexts

    def test_get_solenoids(self, rich_machine):
        sols = rich_machine.get_solenoids()
        assert "SOL1" in sols

    def test_get_diagnostics(self, rich_machine):
        diag = rich_machine.get_diagnostics()
        assert "BPM1" in diag

    def test_get_beam_position_monitors(self, rich_machine):
        bpms = rich_machine.get_beam_position_monitors()
        assert "BPM1" in bpms


# ---------------------------------------------------------------------------
# all_* properties
# ---------------------------------------------------------------------------


class TestLAURAAllProperties:
    def test_all_elements(self, rich_machine):
        all_elems = rich_machine.all_elements
        assert isinstance(all_elems, set)
        assert "Q1" in all_elems
        assert "D1" in all_elems
        assert "START" in all_elems

    def test_all_magnets(self, rich_machine):
        all_mags = rich_machine.all_magnets
        assert "Q1" in all_mags
        assert "D1" in all_mags
        assert "BPM1" not in all_mags

    def test_all_quadrupoles(self, rich_machine):
        assert "Q1" in rich_machine.all_quadrupoles

    def test_all_dipoles(self, rich_machine):
        assert "D1" in rich_machine.all_dipoles

    def test_all_sextupoles(self, rich_machine):
        assert "SX1" in rich_machine.all_sextupoles

    def test_all_solenoids(self, rich_machine):
        assert "SOL1" in rich_machine.all_solenoids

    def test_all_diagnostics(self, rich_machine):
        assert "BPM1" in rich_machine.all_diagnostics

    def test_all_beam_position_monitors(self, rich_machine):
        assert "BPM1" in rich_machine.all_beam_position_monitors


# ---------------------------------------------------------------------------
# createDrifts / get_elements_s_pos
# ---------------------------------------------------------------------------


class TestDriftsAndSPos:
    def test_create_drifts_returns_dict(self, fodo_machine):
        drifts = fodo_machine.createDrifts()
        assert isinstance(drifts, dict)
        # Should contain original elements + inserted drifts
        assert len(drifts) >= 4

    def test_create_drifts_includes_originals(self, fodo_machine):
        drifts = fodo_machine.createDrifts()
        assert "M1" in drifts
        assert "QF" in drifts

    def test_s_pos_returns_dict(self, fodo_machine):
        spos = fodo_machine.get_elements_s_pos()
        assert isinstance(spos, dict)
        # Markers and quads should have s positions
        for name in ["M1", "QF", "QD", "M2"]:
            assert name in spos

    def test_s_pos_monotonically_increasing(self, fodo_machine):
        spos = fodo_machine.get_elements_s_pos()
        values = list(spos.values())
        for i in range(1, len(values)):
            assert values[i] >= values[i - 1]


# ---------------------------------------------------------------------------
# Export round-trip with YAML
# ---------------------------------------------------------------------------


class TestYAMLRoundTrip:
    def test_export_and_reload(self, fodo_machine):
        with tempfile.TemporaryDirectory() as tmpdir:
            lattice_path = os.path.join(tmpdir, "lattice")
            export_machine(path=lattice_path, machine=fodo_machine, overwrite=True)

            # Reload
            sections = {"sections": {"FODO": ["M1", "QF", "QD", "M2"]}}
            layouts = {"default_layout": "line1", "layouts": {"line1": ["FODO"]}}
            reloaded = LAURA(
                element_list=lattice_path,
                layout=layouts,
                section=sections,
            )
            assert "QF" in reloaded.elements
            assert "QD" in reloaded.elements
            assert reloaded["QF"].hardware_type == "Quadrupole"

    def test_export_as_yaml_returns_dict(self):
        m = Marker(
            name="M1",
            machine_area="SEC",
            hardware_class="Marker",
            physical={"middle": {"x": 0.0, "y": 0.0, "z": 0.0}},
        )
        result = export_as_yaml(None, m)
        assert isinstance(result, dict)
        assert result["name"] == "M1"


# ---------------------------------------------------------------------------
# MachineModel get_element / LatticeError
# ---------------------------------------------------------------------------


class TestMachineModelAccess:
    def test_get_element_exists(self, fodo_machine):
        elem = fodo_machine.get_element("QF")
        assert elem.name == "QF"

    def test_get_element_not_found(self, fodo_machine):
        from laura.models.exceptions import LatticeError

        with pytest.raises(LatticeError):
            fodo_machine.get_element("NONEXISTENT")

    def test_str_repr(self, fodo_machine):
        s = str(fodo_machine)
        assert "QF" in s or "M1" in s
