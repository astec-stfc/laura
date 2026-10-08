"""Tests for the LAURA main class."""

import numpy as np
import pytest

from laura import LAURA
from laura.exporters.yaml_exporter import export_machine, export_as_yaml
from laura.laura import add_bool, flatten
from laura.models.diagnostic import ScreenDiagnostic
from laura.models.element import (
    BeamPositionMonitor,
    CombinedCorrector,
    Dipole,
    FaradayCupMonitor,
    HorizontalCorrector,
    Marker,
    Quadrupole,
    RFCavity,
    Screen,
    Sextupole,
    Shutter,
    Solenoid,
    Valve,
    VerticalCorrector,
)


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
    sections = {"sections": {"FODO": ["M1", "QF", "QD", "M2"]}}
    layouts = {"default_layout": "line1", "layouts": {"line1": ["FODO"]}}
    return LAURA(
        element_list=fodo_elements,
        layout=layouts,
        section=sections,
    )


@pytest.fixture
def full_machine():
    """Magnets, correctors (incl. split combined ones), diagnostics, RF, vacuum."""
    elems = [
        Marker(
            name="START",
            machine_area="S1",
            physical={"middle": {"x": 0, "y": 0, "z": 0}},
        ),
        Quadrupole(
            name="Q1",
            machine_area="S1",
            magnetic={"length": 0.3, "k1l": -1.0},
            physical={"length": 0.3, "middle": {"x": 0, "y": 0, "z": 0.5}},
        ),
        Dipole(
            name="D1",
            machine_area="S1",
            magnetic={"length": 0.5, "angle": 0.0},
            physical={"length": 0.5, "middle": {"x": 0, "y": 0, "z": 1.0}},
        ),
        Sextupole(
            name="SX1",
            machine_area="S1",
            magnetic={"length": 0.1, "k2l": 5.0},
            physical={"length": 0.1, "middle": {"x": 0, "y": 0, "z": 1.5}},
        ),
        Solenoid(
            name="SOL1",
            machine_area="S1",
            magnetic={"length": 0.2},
            physical={"length": 0.2, "middle": {"x": 0, "y": 0, "z": 2.0}},
        ),
        HorizontalCorrector(
            name="HC1",
            machine_area="S1",
            physical={"middle": {"x": 0, "y": 0, "z": 2.5}},
        ),
        VerticalCorrector(
            name="VC1",
            machine_area="S1",
            physical={"middle": {"x": 0, "y": 0, "z": 3.0}},
        ),
        CombinedCorrector(
            name="CC1",
            machine_area="S1",
            physical={"middle": {"x": 0, "y": 0, "z": 3.5}},
        ),
        BeamPositionMonitor(
            name="BPM1",
            machine_area="S1",
            physical={"middle": {"x": 0, "y": 0, "z": 4.0}},
        ),
        Screen(
            name="SCR1",
            machine_area="S1",
            physical={"middle": {"x": 0, "y": 0, "z": 4.5}},
            diagnostic=ScreenDiagnostic(camera_name="CAM1"),
        ),
        RFCavity(
            name="RFC1",
            machine_area="S1",
            physical={"middle": {"x": 0, "y": 0, "z": 5.0}},
        ),
        FaradayCupMonitor(
            name="FCM1",
            machine_area="S1",
            physical={"middle": {"x": 0, "y": 0, "z": 5.5}},
        ),
        Shutter(
            name="SH1",
            machine_area="S1",
            physical={"middle": {"x": 0, "y": 0, "z": 6.0}},
        ),
        Valve(
            name="VA1",
            machine_area="S1",
            physical={"middle": {"x": 0, "y": 0, "z": 6.5}},
        ),
        CombinedCorrector(
            name="CC2",
            machine_area="S1",
            physical={"middle": {"x": 0, "y": 0, "z": 6.8}},
            Horizontal_Corrector="CC2_H",
            Vertical_Corrector="CC2_V",
        ),
        CombinedCorrector(
            name="CC3",
            machine_area="S1",
            physical={"middle": {"x": 0, "y": 0, "z": 6.9}},
            Horizontal_Corrector="CC3_H",
        ),
        CombinedCorrector(
            name="CC4",
            machine_area="S1",
            physical={"middle": {"x": 0, "y": 0, "z": 6.95}},
            Vertical_Corrector="CC4_V",
        ),
        Marker(
            name="END",
            machine_area="S1",
            physical={"middle": {"x": 0, "y": 0, "z": 7.0}},
        ),
    ]
    sections = {"sections": {"S1": [e.name for e in elems]}}
    layouts = {"default_layout": "beam1", "layouts": {"beam1": ["S1"]}}
    return LAURA(element_list=elems, layout=layouts, section=sections)


class TestLAURAConstruction:
    def test_from_element_list(self, fodo_machine):
        for name in ["M1", "QF", "QD", "M2"]:
            assert name in fodo_machine.elements
            assert name in fodo_machine.get_elements()
        assert "FODO" in fodo_machine.sections
        assert "line1" in fodo_machine.lattices
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


class TestLAURAGetters:
    def test_get_elements_between(self, fodo_machine):
        elems = fodo_machine.get_elements(start="QF", end="QD")
        assert elems == ["QF", "QD"]

    def test_get_magnets(self, full_machine):
        mags = full_machine.get_magnets()
        assert "Q1" in mags
        assert "D1" in mags
        assert "SX1" in mags

    def test_get_quadrupoles(self, full_machine):
        quads = full_machine.get_quadrupoles()
        assert "Q1" in quads
        assert "D1" not in quads

    def test_get_dipoles(self, full_machine):
        dips = full_machine.get_dipoles()
        assert "D1" in dips
        assert "Q1" not in dips


class TestLAURAAllProperties:
    """``get_X()`` walks the layouts, ``all_X`` the element list; checked together."""

    @pytest.mark.parametrize(
        "category, member",
        [
            ("quadrupoles", "Q1"),
            ("dipoles", "D1"),
            ("sextupoles", "SX1"),
            ("solenoids", "SOL1"),
            ("diagnostics", "BPM1"),
            ("beam_position_monitors", "BPM1"),
        ],
    )
    def test_get_and_all_find_the_same_elements(self, full_machine, category, member):
        got = getattr(full_machine, f"get_{category}")()
        every = getattr(full_machine, f"all_{category}")
        assert member in got
        assert set(got) == set(every)

    def test_all_elements(self, full_machine):
        all_elems = full_machine.all_elements
        assert isinstance(all_elems, set)
        assert "Q1" in all_elems
        assert "D1" in all_elems
        assert "START" in all_elems

    def test_all_magnets(self, full_machine):
        all_mags = full_machine.all_magnets
        assert "Q1" in all_mags
        assert "D1" in all_mags
        assert "BPM1" not in all_mags


class TestDriftsAndSPos:
    def test_create_drifts(self, fodo_machine):
        drifts = fodo_machine.create_drifts()
        assert isinstance(drifts, dict)
        assert len(drifts) >= 4
        assert "M1" in drifts
        assert "QF" in drifts

    def test_s_pos(self, fodo_machine):
        spos = fodo_machine.get_elements_s_pos()
        assert isinstance(spos, dict)
        for name in ["M1", "QF", "QD", "M2"]:
            assert name in spos
        values = list(spos.values())
        for i in range(1, len(values)):
            assert values[i] >= values[i - 1]


class TestYAMLRoundTrip:
    def test_export_and_reload(self, fodo_machine, tmp_path):
        lattice_path = str(tmp_path / "lattice")
        export_machine(path=lattice_path, machine=fodo_machine, overwrite=True)

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
            name="M1", machine_area="SEC", hardware_class="Marker",
            physical={"middle": {"x": 0.0, "y": 0.0, "z": 0.0}},
        )
        result = export_as_yaml(None, m)
        assert isinstance(result, dict)
        assert result["name"] == "M1"


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


class TestModuleHelpers:
    def test_add_bool_delegates_to_construct_scalar(self):
        class Stub:
            def construct_scalar(self, node):
                return "stub-value"

        assert add_bool(Stub(), None) == "stub-value"

    def test_flatten(self):
        assert flatten([[1, 2], [3], [4, 5]]) == [1, 2, 3, 4, 5]


class TestResolveLatticePackage:
    def _stub_lattice(self, data_files=None):
        m1 = Marker(
            name="M1", machine_area="S", physical={"middle": {"x": 0, "y": 0, "z": 0}}
        )

        class LatticeStub:
            layout = {"default_layout": "l1", "layouts": {"l1": ["S"]}}
            section = {"sections": {"S": ["M1"]}}
            element_list = [m1]

        if data_files is not None:
            LatticeStub.data_files = data_files
        return LatticeStub()

    def test_lattice_kwarg_expands_fields(self):
        lm = LAURA(lattice=self._stub_lattice())
        assert "M1" in lm.elements

    def test_lattice_kwarg_sets_master_lattice_from_data_files(self, tmp_path):
        pkg = tmp_path / "pkg"
        lm = LAURA(lattice=self._stub_lattice(data_files=str(pkg / "lattice.yaml")))
        assert lm.master_lattice == str(pkg)

    def test_invalid_lattice_object_raises(self):
        class NotALattice:
            pass

        with pytest.raises(ValueError, match="lattice must be a module"):
            LAURA(lattice=NotALattice())

    def test_non_dict_input_passes_through(self):
        lm = LAURA(lattice=self._stub_lattice())
        revalidated = LAURA.model_validate(lm)
        assert "M1" in revalidated.elements


class TestValidateElementListPathResolution:
    def test_resolves_relative_to_package_file(self):
        assert LAURA.validate_element_list("models/RF.py").endswith("RF.py")

    def test_resolves_relative_to_package_dir(self):
        assert LAURA.validate_element_list("schema/YAML").endswith("YAML")

    def test_unresolvable_string_passed_through(self):
        assert (
            LAURA.validate_element_list("/definitely/does/not/exist")
            == "/definitely/does/not/exist"
        )

    def test_non_string_passed_through(self):
        assert LAURA.validate_element_list(["a", "b"]) == ["a", "b"]


_ONE_MARKER_LINE = {
    "layout": {"default_layout": "l1", "layouts": {"l1": ["SEC"]}},
    "section": {"sections": {"SEC": ["M1"]}},
}


def _export_one_marker(path):
    m = Marker(
        name="M1", machine_area="SEC", physical={"middle": {"x": 0, "y": 0, "z": 0}}
    )
    export_machine(path=str(path), machine=LAURA(element_list=[m], **_ONE_MARKER_LINE), overwrite=True)


class TestElementListLoading:
    def test_missing_element_list_raises(self):
        with pytest.raises(ValueError, match="does not exist"):
            LAURA(
                element_list="/nope/not/here",
                layout={"default_layout": "a", "layouts": {"a": ["SEC"]}},
                section={"sections": {"SEC": []}},
            )

    def test_master_lattice_relative_directory_resolves(self, tmp_path):
        _export_one_marker(tmp_path / "lattice")
        reloaded = LAURA(element_list="lattice", master_lattice=str(tmp_path), **_ONE_MARKER_LINE)
        assert "M1" in reloaded.elements

    def test_eager_mode_loads_elements_immediately(self, tmp_path):
        lattice_dir = str(tmp_path / "lattice")
        _export_one_marker(lattice_dir)
        reloaded = LAURA(element_list=lattice_dir, eager_mode=True, **_ONE_MARKER_LINE)
        assert reloaded["M1"].name == "M1"


class TestCorrectorGetters:
    def test_get_correctors_includes_all_kinds(self, full_machine):
        correctors = full_machine.get_correctors()
        assert "HC1" in correctors
        assert "VC1" in correctors
        assert "CC1" in correctors

    def test_get_lattice_correctors(self, full_machine):
        lattice_correctors = full_machine.get_lattice_correctors()
        assert "CC1" in lattice_correctors

    def test_combined_corrector_splits_into_sub_correctors(self, full_machine):
        correctors = full_machine.get_correctors()
        assert "CC2_H" in correctors
        assert "CC2_V" in correctors
        assert "CC2" not in correctors
        # only horizontal / only vertical
        assert "CC3_H" in correctors
        assert "CC4_V" in correctors

    def test_get_elements_s_pos_propagates_to_corrector_subnames(self, full_machine):
        s_pos = full_machine.get_elements_s_pos()
        assert "CC2_H" in s_pos
        assert "CC2_V" in s_pos
        assert s_pos["CC2_H"] == s_pos["CC2"]


class TestDriftLength:
    def test_drift_length_euclidean_norm(self, full_machine):
        start = np.array([0.0, 0.0, 0.0])
        end = np.array([3.0, 4.0, 0.0])
        assert full_machine._drift_length(start, end) == pytest.approx(5.0)


class TestDiagnosticAndCameraGetters:
    def test_get_position_diagnostics(self, full_machine):
        pos_diag = full_machine.get_position_diagnostics()
        assert "BPM1" in pos_diag
        assert "SCR1" in pos_diag

    def test_get_cameras(self, full_machine):
        assert full_machine.get_cameras() == ["CAM1"]

    def test_get_screens_and_cameras(self, full_machine):
        result = full_machine.get_screens_and_cameras()
        assert result["SCR1"].camera_name == "CAM1"

    def test_all_screens_and_cameras(self, full_machine):
        result = full_machine.all_screens_and_cameras
        assert result["SCR1"] == "CAM1"


@pytest.mark.parametrize(
    "category, member",
    [
        ("correctors", "HC1"),
        ("horizontal_correctors", "HC1"),
        ("vertical_correctors", "VC1"),
        ("combined_correctors", "CC1"),
        ("separate_magnets", "Q1"),
        ("charge_diagnostics", "FCM1"),
        ("position_diagnostics", "BPM1"),
        ("cameras", "CAM1"),
        ("rf_cavities", "RFC1"),
        ("vacuum_components", "VA1"),
    ],
)
def test_get_and_all_agree_on_membership(full_machine, category, member):
    """Only ``get_correctors`` splits combined correctors into ``_H``/``_V``."""
    got = getattr(full_machine, f"get_{category}")()
    assert member in got
    assert member in getattr(full_machine, f"all_{category}")


def test_shutter_getters_return_list_and_set(full_machine):
    assert isinstance(full_machine.get_shutters(), list)
    assert isinstance(full_machine.all_shutters, set)
