"""laura.models.diagnostic camera and screen models."""

import pytest

from laura.models.diagnostic import (
    pco_camera_sensor,
    manta_camera_sensor,
    CameraDiagnostic,
    camera_diagnostic_type,
    pco_camera_diagnostic,
    manta_camera_diagnostic,
    ScreenDiagnostic,
)
from laura.models.base_models import DeviceList


class TestCameraSensorFactories:
    def test_pco_camera_sensor(self):
        sensor = pco_camera_sensor()
        assert sensor.x_pixels == 2560
        assert sensor.bit_depth == 12

    def test_manta_camera_sensor(self):
        sensor = manta_camera_sensor()
        assert sensor.x_pixels == 1936
        assert sensor.minimum == [136, 116]


class TestCameraDiagnosticType:
    @pytest.mark.parametrize(
        "camera_type, x_pixels",
        [("PCO", 2560), ("Manta", 1936), ("Unknown", 1936)],
        ids=["pco", "manta", "unknown_falls_back_to_manta"],
    )
    def test_dispatch(self, camera_type, x_pixels):
        assert camera_diagnostic_type(type=camera_type).sensor.x_pixels == x_pixels

    @pytest.mark.parametrize(
        "helper, x_pixels", [(pco_camera_diagnostic, 2560), (manta_camera_diagnostic, 1936)]
    )
    def test_camera_diagnostic_helper(self, helper, x_pixels):
        cam = helper()
        assert isinstance(cam, CameraDiagnostic)
        assert cam.sensor.x_pixels == x_pixels


class TestScreenDiagnosticDeviceCoercion:
    @pytest.mark.parametrize(
        "devices, expected",
        [
            ("A, B, C", ["A", "B", "C"]),
            (["A", "B"], ["A", "B"]),
            ({"devices": ["A"]}, ["A"]),
            (DeviceList(devices=["X"]), ["X"]),
        ],
        ids=["csv_string", "list", "dict", "devicelist_instance"],
    )
    def test_devices_coerced(self, devices, expected):
        assert ScreenDiagnostic(devices=devices).devices == expected

    def test_devices_invalid_type_raises(self):
        with pytest.raises(ValueError):
            ScreenDiagnostic(devices=5)


class TestDatumFromStart:
    """``diagnostic.datum_from_start``: where the instrument measures, from the upstream face."""

    @staticmethod
    def bpm(**diagnostic):
        from laura.models.element import BeamPositionMonitor

        return BeamPositionMonitor(
            name="BPM",
            machine_area="S",
            physical={"length": 0.21, "middle": {"z": 3.0}, "datum": {"z": 3.105}},
            diagnostic=diagnostic,
        )

    def test_absent_by_default(self):
        assert self.bpm().diagnostic.datum_from_start is None

    def test_it_is_stored_and_leaves_the_mechanical_datum_alone(self):
        bpm = self.bpm(datum_from_start=0.0353)
        assert bpm.diagnostic.datum_from_start == pytest.approx(0.0353)
        assert bpm.physical.datum.z == pytest.approx(3.105)

    def test_it_cannot_be_negative(self):
        with pytest.raises(ValueError):
            self.bpm(datum_from_start=-0.01)

    def test_every_diagnostic_inherits_it(self):
        assert ScreenDiagnostic(datum_from_start=0.1).datum_from_start == 0.1

    YAML = {
        "name": "BPM",
        "hardware_class": "Diagnostic",
        "hardware_type": "Beam_Position_Monitor",
        "machine_area": "S",
        "physical": {"length": 0.21},
        "diagnostic": {"type": "Stripline", "datum_from_start": 0.0353},
    }

    def test_it_loads_from_yaml(self):
        from laura.importers.yaml_loader import interpret_yaml_element

        element = interpret_yaml_element(self.YAML, strict=True)
        assert element.diagnostic.datum_from_start == pytest.approx(0.0353)
