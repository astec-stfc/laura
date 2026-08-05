"""Tests for laura.models.diagnostic camera-sensor factories, Camera_Diagnostic_Type
dispatch, and Screen_Diagnostic device-list coercion."""

import pytest

from laura.models.diagnostic import (
    PCO_Camera_Sensor,
    Manta_Camera_Sensor,
    Camera_Diagnostic,
    Camera_Diagnostic_Type,
    PCO_Camera_Diagnostic,
    Manta_Camera_Diagnostic,
    Screen_Diagnostic,
)
from laura.models.baseModels import DeviceList


class TestCameraSensorFactories:
    def test_pco_camera_sensor(self):
        sensor = PCO_Camera_Sensor()
        assert sensor.x_pixels == 2560
        assert sensor.bit_depth == 12

    def test_manta_camera_sensor(self):
        sensor = Manta_Camera_Sensor()
        assert sensor.x_pixels == 1936
        assert sensor.minimum == [136, 116]


class TestCameraDiagnosticType:
    def test_pco_dispatch(self):
        cam = Camera_Diagnostic_Type(type="PCO")
        assert cam.sensor.x_pixels == 2560

    def test_manta_dispatch(self):
        cam = Camera_Diagnostic_Type(type="Manta")
        assert cam.sensor.x_pixels == 1936

    def test_unknown_type_falls_back_to_manta(self):
        cam = Camera_Diagnostic_Type(type="Unknown")
        assert cam.sensor.x_pixels == 1936

    def test_pco_camera_diagnostic_helper(self):
        cam = PCO_Camera_Diagnostic()
        assert isinstance(cam, Camera_Diagnostic)
        assert cam.sensor.x_pixels == 2560

    def test_manta_camera_diagnostic_helper(self):
        cam = Manta_Camera_Diagnostic()
        assert isinstance(cam, Camera_Diagnostic)
        assert cam.sensor.x_pixels == 1936


class TestScreenDiagnosticDeviceCoercion:
    def test_devices_from_csv_string(self):
        s = Screen_Diagnostic(devices="A, B, C")
        assert s.devices == ["A", "B", "C"]

    def test_devices_from_list(self):
        s = Screen_Diagnostic(devices=["A", "B"])
        assert s.devices == ["A", "B"]

    def test_devices_from_dict(self):
        s = Screen_Diagnostic(devices={"devices": ["A"]})
        assert s.devices == ["A"]

    def test_devices_from_devicelist_instance(self):
        dl = DeviceList(devices=["X"])
        s = Screen_Diagnostic(devices=dl)
        assert s.devices == ["X"]

    def test_devices_invalid_type_raises(self):
        with pytest.raises(ValueError):
            Screen_Diagnostic(devices=5)
