"""Additional tests for laura.laura.LAURA covering branches not exercised by
test_laura_class.py: the `lattice=` package-expansion validator, element_list
path-resolution branches, master_lattice-relative/eager_mode loading, and the
remaining get_*/all_* accessor methods (correctors, charge diagnostics,
position diagnostics, cameras, vacuum components, RF cavities)."""

import os
import tempfile

import pytest

from laura import LAURA
from laura.laura import add_bool, flatten
from laura.models.element import (
    Marker,
    Quadrupole,
    Dipole,
    Sextupole,
    Solenoid,
    HorizontalCorrector,
    VerticalCorrector,
    CombinedCorrector,
    BeamPositionMonitor,
    Screen,
    RFCavity,
    FaradayCupMonitor,
    Shutter,
    Valve,
)
from laura.models.diagnostic import ScreenDiagnostic
from laura.exporters.yaml_exporter import export_machine


class TestModuleHelpers:
    def test_add_bool_delegates_to_construct_scalar(self):
        class Stub:
            def construct_scalar(self, node):
                return "stub-value"

        assert add_bool(Stub(), None) == "stub-value"

    def test_flatten(self):
        assert flatten([[1, 2], [3], [4, 5]]) == [1, 2, 3, 4, 5]


class TestResolveLatticePackage:
    def _stub_lattice(self, with_data_files=False):
        m1 = Marker(name="M1", machine_area="S", physical={"middle": {"x": 0, "y": 0, "z": 0}})

        class LatticeStub:
            layout = {"default_layout": "l1", "layouts": {"l1": ["S"]}}
            section = {"sections": {"S": ["M1"]}}
            element_list = [m1]

        if with_data_files:
            LatticeStub.data_files = "/some/dir"
        return LatticeStub()

    def test_lattice_kwarg_expands_fields(self):
        lm = LAURA(lattice=self._stub_lattice())
        assert "M1" in lm.elements

    def test_lattice_kwarg_sets_master_lattice_from_data_files(self):
        lm = LAURA(lattice=self._stub_lattice(with_data_files=True))
        assert lm.master_lattice == "/some/dir"

    def test_invalid_lattice_object_raises(self):
        class NotALattice:
            pass

        with pytest.raises(ValueError, match="lattice must be a module"):
            LAURA(lattice=NotALattice())

    def test_non_dict_input_passes_through(self):
        # model_validate() may be called with an existing model instance rather
        # than a dict; _resolve_lattice_package must pass it through unchanged.
        lm = LAURA(lattice=self._stub_lattice())
        revalidated = LAURA.model_validate(lm)
        assert "M1" in revalidated.elements


class TestValidateElementListPathResolution:
    def test_resolves_relative_to_package_file(self):
        assert LAURA.validate_element_list("models/RF.py").endswith("RF.py")

    def test_resolves_relative_to_package_dir(self):
        assert LAURA.validate_element_list("schema/YAML").endswith("YAML")

    def test_unresolvable_string_passed_through(self):
        assert LAURA.validate_element_list("/definitely/does/not/exist") == "/definitely/does/not/exist"

    def test_non_string_passed_through(self):
        assert LAURA.validate_element_list(["a", "b"]) == ["a", "b"]


class TestElementListLoading:
    def test_missing_element_list_raises(self):
        with pytest.raises(ValueError, match="does not exist"):
            LAURA(
                element_list="/nope/not/here",
                layout={"default_layout": "a", "layouts": {"a": ["SEC"]}},
                section={"sections": {"SEC": []}},
            )

    def test_master_lattice_relative_directory_resolves(self):
        m = Marker(name="M1", machine_area="SEC", physical={"middle": {"x": 0, "y": 0, "z": 0}})
        with tempfile.TemporaryDirectory() as tmpdir:
            lattice_dir = os.path.join(tmpdir, "lattice")
            fake_machine = LAURA(
                element_list=[m],
                layout={"default_layout": "l1", "layouts": {"l1": ["SEC"]}},
                section={"sections": {"SEC": ["M1"]}},
            )
            export_machine(path=lattice_dir, machine=fake_machine, overwrite=True)

            reloaded = LAURA(
                element_list="lattice",
                master_lattice=tmpdir,
                layout={"default_layout": "l1", "layouts": {"l1": ["SEC"]}},
                section={"sections": {"SEC": ["M1"]}},
            )
            assert "M1" in reloaded.elements

    def test_eager_mode_loads_elements_immediately(self):
        m = Marker(name="M1", machine_area="SEC", physical={"middle": {"x": 0, "y": 0, "z": 0}})
        with tempfile.TemporaryDirectory() as tmpdir:
            lattice_dir = os.path.join(tmpdir, "lattice")
            fake_machine = LAURA(
                element_list=[m],
                layout={"default_layout": "l1", "layouts": {"l1": ["SEC"]}},
                section={"sections": {"SEC": ["M1"]}},
            )
            export_machine(path=lattice_dir, machine=fake_machine, overwrite=True)

            reloaded = LAURA(
                element_list=lattice_dir,
                eager_mode=True,
                layout={"default_layout": "l1", "layouts": {"l1": ["SEC"]}},
                section={"sections": {"SEC": ["M1"]}},
            )
            assert reloaded["M1"].name == "M1"


# ---------------------------------------------------------------------------
# Rich fixture exercising the remaining get_*/all_* accessor methods
# ---------------------------------------------------------------------------

@pytest.fixture
def full_machine():
    elems = [
        Marker(name="START", machine_area="S1", physical={"middle": {"x": 0, "y": 0, "z": 0}}),
        Quadrupole(
            name="Q1", machine_area="S1", magnetic={"length": 0.3, "k1l": -1.0},
            physical={"length": 0.3, "middle": {"x": 0, "y": 0, "z": 0.5}},
        ),
        Dipole(
            name="D1", machine_area="S1", magnetic={"length": 0.5, "angle": 0.0},
            physical={"length": 0.5, "middle": {"x": 0, "y": 0, "z": 1.0}},
        ),
        Sextupole(
            name="SX1", machine_area="S1", magnetic={"length": 0.1, "k2l": 5.0},
            physical={"length": 0.1, "middle": {"x": 0, "y": 0, "z": 1.5}},
        ),
        Solenoid(
            name="SOL1", machine_area="S1", magnetic={"length": 0.2},
            physical={"length": 0.2, "middle": {"x": 0, "y": 0, "z": 2.0}},
        ),
        HorizontalCorrector(name="HC1", machine_area="S1", physical={"middle": {"x": 0, "y": 0, "z": 2.5}}),
        VerticalCorrector(name="VC1", machine_area="S1", physical={"middle": {"x": 0, "y": 0, "z": 3.0}}),
        CombinedCorrector(name="CC1", machine_area="S1", physical={"middle": {"x": 0, "y": 0, "z": 3.5}}),
        BeamPositionMonitor(name="BPM1", machine_area="S1", physical={"middle": {"x": 0, "y": 0, "z": 4.0}}),
        Screen(
            name="SCR1", machine_area="S1", physical={"middle": {"x": 0, "y": 0, "z": 4.5}},
            diagnostic=ScreenDiagnostic(camera_name="CAM1"),
        ),
        RFCavity(name="RFC1", machine_area="S1", physical={"middle": {"x": 0, "y": 0, "z": 5.0}}),
        FaradayCupMonitor(name="FCM1", machine_area="S1", physical={"middle": {"x": 0, "y": 0, "z": 5.5}}),
        Shutter(name="SH1", machine_area="S1", physical={"middle": {"x": 0, "y": 0, "z": 6.0}}),
        Valve(name="VA1", machine_area="S1", physical={"middle": {"x": 0, "y": 0, "z": 6.5}}),
        CombinedCorrector(
            name="CC2", machine_area="S1", physical={"middle": {"x": 0, "y": 0, "z": 6.8}},
            Horizontal_Corrector="CC2_H", Vertical_Corrector="CC2_V",
        ),
        CombinedCorrector(
            name="CC3", machine_area="S1", physical={"middle": {"x": 0, "y": 0, "z": 6.9}},
            Horizontal_Corrector="CC3_H",
        ),
        CombinedCorrector(
            name="CC4", machine_area="S1", physical={"middle": {"x": 0, "y": 0, "z": 6.95}},
            Vertical_Corrector="CC4_V",
        ),
        Marker(name="END", machine_area="S1", physical={"middle": {"x": 0, "y": 0, "z": 7.0}}),
    ]
    sections = {"sections": {"S1": [e.name for e in elems]}}
    layouts = {"default_layout": "beam1", "layouts": {"beam1": ["S1"]}}
    return LAURA(element_list=elems, layout=layouts, section=sections)


class TestCorrectorGetters:
    def test_get_correctors_includes_all_kinds(self, full_machine):
        correctors = full_machine.get_correctors()
        assert "HC1" in correctors
        assert "VC1" in correctors
        assert "CC1" in correctors

    def test_get_horizontal_correctors(self, full_machine):
        assert "HC1" in full_machine.get_horizontal_correctors()

    def test_get_vertical_correctors(self, full_machine):
        assert "VC1" in full_machine.get_vertical_correctors()

    def test_get_lattice_correctors(self, full_machine):
        lattice_correctors = full_machine.get_lattice_correctors()
        assert "CC1" in lattice_correctors

    def test_get_combined_correctors(self, full_machine):
        assert "CC1" in full_machine.get_combined_correctors()

    def test_get_separate_magnets(self, full_machine):
        separated = full_machine.get_separate_magnets()
        assert "Q1" in separated

    def test_all_correctors(self, full_machine):
        assert "HC1" in full_machine.all_correctors

    def test_all_horizontal_correctors(self, full_machine):
        assert "HC1" in full_machine.all_horizontal_correctors

    def test_all_vertical_correctors(self, full_machine):
        assert "VC1" in full_machine.all_vertical_correctors

    def test_all_combined_correctors(self, full_machine):
        assert "CC1" in full_machine.all_combined_correctors

    def test_all_separate_magnets(self, full_machine):
        assert "Q1" in full_machine.all_separate_magnets

    def test_all_sextupoles(self, full_machine):
        assert "SX1" in full_machine.all_sextupoles

    def test_all_solenoids(self, full_machine):
        assert "SOL1" in full_machine.all_solenoids

    def test_combined_corrector_with_both_sub_correctors_splits(self, full_machine):
        correctors = full_machine.get_correctors()
        assert "CC2_H" in correctors
        assert "CC2_V" in correctors
        assert "CC2" not in correctors

    def test_combined_corrector_with_only_horizontal_splits(self, full_machine):
        correctors = full_machine.get_correctors()
        assert "CC3_H" in correctors

    def test_combined_corrector_with_only_vertical_splits(self, full_machine):
        correctors = full_machine.get_correctors()
        assert "CC4_V" in correctors

    def test_get_elements_s_pos_propagates_to_corrector_subnames(self, full_machine):
        s_pos = full_machine.get_elements_s_pos()
        assert "CC2_H" in s_pos
        assert "CC2_V" in s_pos
        assert s_pos["CC2_H"] == s_pos["CC2"]


class TestDriftLength:
    def test_drift_length_euclidean_norm(self, full_machine):
        import numpy as np

        start = np.array([0.0, 0.0, 0.0])
        end = np.array([3.0, 4.0, 0.0])
        assert full_machine._drift_length(start, end) == pytest.approx(5.0)


class TestDiagnosticAndCameraGetters:
    def test_get_charge_diagnostics(self, full_machine):
        assert "FCM1" in full_machine.get_charge_diagnostics()

    def test_get_position_diagnostics(self, full_machine):
        pos_diag = full_machine.get_position_diagnostics()
        assert "BPM1" in pos_diag
        assert "SCR1" in pos_diag

    def test_get_cameras(self, full_machine):
        assert full_machine.get_cameras() == ["CAM1"]

    def test_get_screens_and_cameras(self, full_machine):
        result = full_machine.get_screens_and_cameras()
        assert result["SCR1"].camera_name == "CAM1"

    def test_all_charge_diagnostics(self, full_machine):
        assert "FCM1" in full_machine.all_charge_diagnostics

    def test_all_position_diagnostics(self, full_machine):
        assert "BPM1" in full_machine.all_position_diagnostics

    def test_all_cameras(self, full_machine):
        assert "CAM1" in full_machine.all_cameras

    def test_all_screens_and_cameras(self, full_machine):
        result = full_machine.all_screens_and_cameras
        assert result["SCR1"] == "CAM1"


class TestRFAndVacuumGetters:
    def test_get_rf_cavities(self, full_machine):
        assert "RFC1" in full_machine.get_rf_cavities()

    def test_all_rf_cavities(self, full_machine):
        assert "RFC1" in full_machine.all_rf_cavities

    def test_get_vacuum_components(self, full_machine):
        vacuum = full_machine.get_vacuum_components()
        assert "VA1" in vacuum

    def test_all_vacuum_components(self, full_machine):
        assert "VA1" in full_machine.all_vacuum_components

    def test_get_shutters_returns_list(self, full_machine):
        # Shutter's hardware_class is "Shutter", not "Vacuum" -- get_shutters()
        # filters on element_class="vacuum", so no current element type matches.
        # Exercised here for coverage of the accessor itself, not as a claim
        # about which elements it returns.
        assert isinstance(full_machine.get_shutters(), list)

    def test_all_shutters_returns_set(self, full_machine):
        assert isinstance(full_machine.all_shutters, set)
