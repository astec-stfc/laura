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
