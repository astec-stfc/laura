from pydantic import (
    AliasChoices,
    Field,
    field_validator,
)
from typing import List, Type, Union
from .base_models import IgnoreExtra, T, DeviceList
from ._generated import (
    _DiagnosticElementBase,
    _BPMDiagnosticElementBase,
    _BAMDiagnosticElementBase,
    _BLMDiagnosticElementBase,
    _ScreenDiagnosticElementBase,
    _ChargeDiagnosticElementBase,
    _CameraDiagnosticElementBase,
    _CameraPixelResultsIndicesBase,
    _CameraPixelResultsNamesBase,
    _CameraMaskBase,
    _CameraSensorBase,
)


class DiagnosticElement(_DiagnosticElementBase):
    """
    Base class for diagnostic elements.
    """

    pass


class BeamPositionMonitorDiagnostic(_BPMDiagnosticElementBase):
    """
    BPM Diagnostic model.
    """

    pass


class BeamArrivalMonitorDiagnostic(_BAMDiagnosticElementBase):
    """
    BAM Diagnostic model.
    """

    pass


class BunchLengthMonitorDiagnostic(_BLMDiagnosticElementBase):
    """
    BLM Diagnostic model.
    """

    pass


class PhotonIntensityMonitorDiagnostic(DiagnosticElement):
    """
    Photon Intensity Monitor Diagnostic model.
    """

    type: str = Field(
        default="I0",
        validation_alias=AliasChoices("type", "intensity_monitor_type"),
    )
    """Photon Intensity Monitor type"""

    intensity: float = 0.0


class CameraPixelResultsIndices(_CameraPixelResultsIndicesBase):
    """
    Class defining the names of analysis results for the camera pixel data
    """

    pass


class CameraPixelResultsNames(_CameraPixelResultsNamesBase):
    """
    Class defining the names of the analysis results for the camera data in SI units (or mm)
    """

    pass


class CameraMask(_CameraMaskBase, IgnoreExtra):
    """
    Class defining the camera analysis mask parameters.
    """

    middle: List[Union[float, int]] = [1280, 1080]  # X_MASK_DEF, Y_MASK_DEF
    """Center of the mask in pixels."""

    radius: List[Union[float, int]] = [1240, 1040]  # X_MASK_RAD_DEF, Y_MASK_RAD_DEF
    """Mask radius in pixels."""

    maximum: List[Union[float, int]] = [300, 300]  # X_MASK_RAD_MAX, Y_MASK_RAD_MAX
    """Maximum mask radius in pixels."""


class CameraSensor(_CameraSensorBase, IgnoreExtra):
    """
    Camera Sensor model. Contains information about the number of pixels, scale factors, bit depth, etc.
    """

    middle: List[Union[float, int]] = [0, 0]  # X_CENTER_DEF, Y_CENTER_DEF
    """Center definitions for the camera."""

    minimum: List[Union[float, int]] = [150, 150]  # MIN_X_PIXEL_POS, MIN_Y_PIXEL_POS
    """Minimum pixel positions in x and y directions."""

    maximum: List[Union[float, int]] = [2400, 2000]  # MAX_X_PIXEL_POS, MAX_Y_PIXEL_POS
    """Maximum pixel positions in x and y directions."""

    operating_middle: List[Union[float, int]] = [
        1000,
        1000,
    ]  # OPERATING_CENTER_X, OPERATING_CENTER_Y
    """Operating center positions in x and y"""

    mechanical_middle: List[Union[float, int]] = [
        1000,
        1000,
    ]  # MECHANICAL_CENTER_X, MECHANICAL_CENTER_Y
    """Mechanical center of the camera in x and y"""


def _build_camera_sensor(**kwargs) -> CameraSensor:
    return CameraSensor(**kwargs)


def pco_camera_sensor():
    """
    A specific instantiation of `~laura.models.diagnostic.Camera_Sensor` for PCO cameras.
    """

    return _build_camera_sensor(
        x_pixels=2560,
        y_pixels=2160,
        x_scale_factor=2,
        y_scale_factor=2,
        beam_pixel_average=97.2,
        x_pixels_to_mm=0.013,
        y_pixels_to_mm=0.013,
        minimum=[150, 150],
        maximum=[2400, 2000],
        bit_depth=12,
        operating_middle=[1000, 1000],
        mechanical_middle=[1000, 1000],
    )


def manta_camera_sensor():
    """
    A specific instantiation of `~laura.models.diagnostic.Camera_Sensor` for Manta cameras.
    """

    return _build_camera_sensor(
        x_pixels=1936,
        y_pixels=1216,
        x_scale_factor=2,
        y_scale_factor=2,
        beam_pixel_average=97.2,
        x_pixels_to_mm=0.0233,
        y_pixels_to_mm=0.0177,
        minimum=[136, 116],
        maximum=[1800, 1100],
        bit_depth=12,
        operating_middle=[900, 550],
        mechanical_middle=[900, 550],
    )


class CameraDiagnostic(_CameraDiagnosticElementBase):
    """
    Camera Diagnostic model.
    """

    pass


def camera_diagnostic_type(type: str = "PCO", **kwargs) -> CameraDiagnostic:
    if type.lower() == "pco":
        return pco_camera_diagnostic(type=type, **kwargs)
    if type.lower() == "manta":
        return manta_camera_diagnostic(type=type, **kwargs)
    return manta_camera_diagnostic(type=type, **kwargs)


def pco_camera_diagnostic(**kwargs):
    return CameraDiagnostic(sensor=pco_camera_sensor(), **kwargs)


def manta_camera_diagnostic(**kwargs):
    return CameraDiagnostic(sensor=manta_camera_sensor(), **kwargs)


def _coerce_device_list(v: Union[str, List, dict, DeviceList]) -> DeviceList:
    if isinstance(v, str):
        return DeviceList(devices=list(map(str.strip, v.split(","))))
    if isinstance(v, (list, tuple)):
        return DeviceList(devices=list(v))
    if isinstance(v, dict):
        return DeviceList(**v)
    if isinstance(v, DeviceList):
        return v
    raise ValueError("devices should be a string or a list of strings")


class ScreenDiagnostic(_ScreenDiagnosticElementBase):
    """
    Screen Diagnostic model.
    """

    @field_validator("devices", mode="before")
    @classmethod
    def validate_devices(cls, v: Union[str, List]) -> DeviceList:
        return _coerce_device_list(v)


class ChargeDiagnosticElement(_ChargeDiagnosticElementBase):
    """
    Charge Diagnostic model.
    """


from laura._compat import deprecated_aliases  # noqa: E402

__getattr__ = deprecated_aliases(
    __name__,
    globals(),
    {
        "Beam_Arrival_Monitor_Diagnostic": "BeamArrivalMonitorDiagnostic",
        "Beam_Position_Monitor_Diagnostic": "BeamPositionMonitorDiagnostic",
        "Bunch_Length_Monitor_Diagnostic": "BunchLengthMonitorDiagnostic",
        "Camera_Diagnostic": "CameraDiagnostic",
        "Camera_Diagnostic_Type": "camera_diagnostic_type",
        "Camera_Mask": "CameraMask",
        "Camera_Pixel_Results_Indices": "CameraPixelResultsIndices",
        "Camera_Pixel_Results_Names": "CameraPixelResultsNames",
        "Camera_Sensor": "CameraSensor",
        "Charge_Diagnostic": "ChargeDiagnosticElement",
        "Manta_Camera_Diagnostic": "manta_camera_diagnostic",
        "Manta_Camera_Sensor": "manta_camera_sensor",
        "PCO_Camera_Diagnostic": "pco_camera_diagnostic",
        "PCO_Camera_Sensor": "pco_camera_sensor",
        "Photon_Intensity_Monitor_Diagnostic": "PhotonIntensityMonitorDiagnostic",
        "Screen_Diagnostic": "ScreenDiagnostic",
    },
)
