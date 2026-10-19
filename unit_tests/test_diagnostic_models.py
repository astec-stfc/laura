"""Tests for laura.models.diagnostic camera-sensor factories, Camera_Diagnostic_Type
dispatch, and Screen_Diagnostic device-list coercion."""

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
    def test_pco_dispatch(self):
        cam = camera_diagnostic_type(type="PCO")
        assert cam.sensor.x_pixels == 2560

    def test_manta_dispatch(self):
        cam = camera_diagnostic_type(type="Manta")
        assert cam.sensor.x_pixels == 1936

    def test_unknown_type_falls_back_to_manta(self):
        cam = camera_diagnostic_type(type="Unknown")
        assert cam.sensor.x_pixels == 1936

    def test_pco_camera_diagnostic_helper(self):
        cam = pco_camera_diagnostic()
        assert isinstance(cam, CameraDiagnostic)
        assert cam.sensor.x_pixels == 2560

    def test_manta_camera_diagnostic_helper(self):
        cam = manta_camera_diagnostic()
        assert isinstance(cam, CameraDiagnostic)
        assert cam.sensor.x_pixels == 1936


class TestScreenDiagnosticDeviceCoercion:
    def test_devices_from_csv_string(self):
        s = ScreenDiagnostic(devices="A, B, C")
        assert s.devices == ["A", "B", "C"]

    def test_devices_from_list(self):
        s = ScreenDiagnostic(devices=["A", "B"])
        assert s.devices == ["A", "B"]

    def test_devices_from_dict(self):
        s = ScreenDiagnostic(devices={"devices": ["A"]})
        assert s.devices == ["A"]

    def test_devices_from_devicelist_instance(self):
        dl = DeviceList(devices=["X"])
        s = ScreenDiagnostic(devices=dl)
        assert s.devices == ["X"]

    def test_devices_invalid_type_raises(self):
        with pytest.raises(ValueError):
            ScreenDiagnostic(devices=5)
