"""
LAURA Element Module

The main class for representing accelerator elements in LAURA.
"""

from typing import Optional, Type, List, Union, Dict, Any
import os
from pydantic import field_validator, Field
from .control import (
    ControlsInformation,
    ScreenControlsInformation,
    MirrorControlsInformation,
    ShutterControlsInformation,
)
from .baseModels import T, Aliases, IgnoreExtra
from ._generated import (
    _AcceleratorElementBase,
    _ElementBase,
    _PhysicalAcceleratorElementBase,
    _MagnetBase,
    _TwissMatchBase,
    _DiagnosticBase,
    _BeamPositionMonitorBase,
    _BeamArrivalMonitorBase,
    _BunchLengthMonitorBase,
    _CameraBase,
    _ScreenBase,
    _ChargeDiagnosticBase,
    _WallCurrentMonitorBase,
    _FaradayCupMonitorBase,
    _IntegratedCurrentTransformerBase,
    _StageBase,
    _VacuumGaugeBase,
    _LaserBase,
    _LaserEnergyMeterBase,
    _LaserHalfWavePlateBase,
    _LaserMirrorBase,
    _LaserAttenuatorBase,
    _PlasmaBase,
    _LightingBase,
    _PIDBase,
    _LowLevelRFBase,
    _RFCavityBase,
    _CrabCavityBase,
    _WakefieldBase,
    _RFDeflectingCavityBase,
    _RFModulatorBase,
    _RFProtectionBase,
    _RFHeartbeatBase,
    _ShutterBase,
    _ValveBase,
    _MarkerBase,
    _ApertureBase,
    _CollimatorBase,
    _DriftBase,
    _MatrixTransformBase,
    _ElectrostaticSeparatorBase,
    _ACDipoleBase,
    _HorizontalACDipoleBase,
    _VerticalACDipoleBase,
    _WireBase,
    _BeamBeamBase,
    _RFMultipoleBase,
    _DipoleBase,
    _QuadrupoleBase,
    _SextupoleBase,
    _OctupoleBase,
    _SolenoidBase,
    _NonLinearLensBase,
    _WigglerBase,
    _HorizontalCorrectorBase,
    _VerticalCorrectorBase,
    _CombinedCorrectorBase,
)
from ..utils import CascadingAccessMixin, flatten_dict, StringWithQuotes, FlowList
from .manufacturer import ManufacturerElement
from .electrical import ElectricalElement
from .degauss import DegaussableElement
from .physical import PhysicalElement, Rotation
from .reference import ReferenceElement
from .magnetic import (
    MagneticElement,
    Dipole_Magnet,
    Quadrupole_Magnet,
    Sextupole_Magnet,
    Octupole_Magnet,
    Solenoid_Magnet,
    NonLinearLens_Magnet,
    Wiggler_Magnet,
    Corrector_Magnet,
)
from .plasma import PlasmaElement
from .diagnostic import (
    Beam_Position_Monitor_Diagnostic,
    Beam_Arrival_Monitor_Diagnostic,
    Bunch_Length_Monitor_Diagnostic,
    Camera_Diagnostic,
    Screen_Diagnostic,
    Charge_Diagnostic,
    Photon_Intensity_Monitor_Diagnostic,
)
from .laser import (
    LaserElement,
    LaserEnergyMeterElement,
    LaserMirrorElement,
    LaserHalfWavePlateElement,
)
from .lighting import LightingElement
from .RF import (
    PIDElement,
    Low_Level_RF_Element,
    RFModulatorElement,
    RFProtectionElement,
    RFHeartbeatElement,
    RFCavityElement,
    RFDeflectingCavityElement,
    WakefieldElement,
)
from .shutter import ShutterElement, ValveElement
from .simulation import (
    ApertureElement,
    RFCavitySimulationElement,
    WakefieldSimulationElement,
    MagnetSimulationElement,
    DriftSimulationElement,
    DiagnosticSimulationElement,
    MatrixTransformSimulationElement,
    PlasmaSimulationElement,
    SimulationElement,
    TwissMatchSimulationElement,
    ElectrostaticSeparatorSimulationElement,
    ACDipoleSimulationElement,
    WireSimulationElement,
    BeamBeamSimulationElement,
    RFMultipoleSimulationElement,
)
# Re-export from utils for backwards compatibility
flatten = flatten_dict
string_with_quotes = StringWithQuotes
flow_list = FlowList


def _ensure_nested_default(instance: Any, attribute_name: str, factory) -> None:
    if getattr(instance, attribute_name) is None:
        setattr(instance, attribute_name, factory())


def _coerce_nested_model(value: Any, model_cls):
    if value is None or isinstance(value, model_cls):
        return value if value is not None else model_cls()
    if hasattr(value, "model_dump"):
        return model_cls(**value.model_dump())
    if isinstance(value, dict):
        return model_cls(**value)
    return value


class baseElement(CascadingAccessMixin, _AcceleratorElementBase, IgnoreExtra):
    """
    Base-level element class. All LAURA elements derive from this.

    Combines schema base (_AcceleratorElementBase) with utility mixins:
    - IgnoreExtra: Ignores unknown fields (extra="ignore")
    - CascadingAccessMixin: Enables nested attribute access (e.g., quad.k1l)

    """

    @classmethod
    def linkml_class_name(cls) -> str:
        """Name of the LinkML class this element is an instance of.

        Exporters that mint schema URIs must go through this rather than
        ``hardware_type``.  ``hardware_type`` is a dispatch label
        (``Horizontal_Corrector``); the schema class is ``HorizontalCorrector``,
        and the two agree only by coincidence.  Building URIs from the label
        left 184 of CLARA's 438 elements typed as something the ontology does
        not declare, and two of those names -- ``laura:Horizontal_Corrector``,
        ``laura:Vertical_Corrector`` -- are real terms of the wrong kind
        (``owl:DatatypeProperty`` slots of ``CombinedCorrector``).

        The schema stays the single source of truth: gen-pydantic carries each
        class's ``class_uri`` onto the generated base, and where the schema
        declares none the base's own name is the class name.
        """

        own_base = f"_{cls.__name__.replace('_', '')}Base"
        candidates = [k for k in cls.__mro__ if k.__name__ == own_base]
        candidates += [k for k in cls.__mro__ if k.__name__ != own_base]

        for klass in candidates:
            meta = klass.__dict__.get("linkml_meta")
            if meta is not None and "class_uri" in meta:
                # Accepts both the CURIE the schema uses and a full IRI.
                return str(meta["class_uri"]).rsplit("/", 1)[-1].split(":")[-1]
            if klass.__name__.startswith("_") and klass.__name__.endswith("Base"):
                return klass.__name__[1:-4]
        return cls.__name__

    @field_validator("name", mode="before")
    @classmethod
    def validate_name(cls, v: str) -> str:
        assert isinstance(v, str)
        return v

    @field_validator("alias", mode="before")
    @classmethod
    def validate_alias(cls, v: Union[str, List, None]) -> list:
        if isinstance(v, str):
            return list(map(str.strip, v.split(",")))
        elif isinstance(v, (list, tuple)):
            return list(v)
        elif isinstance(v, dict):
            return v.get("aliases", [])
        elif v is None:
            return []
        else:
            raise ValueError("alias should be a string or a list of strings")

    @field_validator("subelement", mode="before")
    @classmethod
    def validate_subelement(cls, v) -> str | None:
        if v is True:
            return ""
        if v is False or v is None:
            return None
        return str(v)

    def escape_string_list(self, escapes) -> str:
        if len(list(escapes)) > 0:
            return string_with_quotes(",".join(map(str, list(escapes))))
        return string_with_quotes("")

    @property
    def subdirectory(self) -> str:
        if self.__class__.__name__ == self.hardware_type:
            return os.path.join(self.hardware_class, self.hardware_type)
        return os.path.join(
            self.hardware_class, self.__class__.__name__, self.hardware_type
        )

    @property
    def YAML_filename(self) -> str:
        return os.path.join(self.subdirectory, self.name + ".yaml")

    @property
    def hardware_info(self) -> Dict[str, str]:
        """
        Retrieve the `hardware_class` and `hardware_type` of the object as a dict

        Returns
        -------
            Dict[str, str]: {"class": `hardware_class`, "type": `hardware_type`}
        """
        return {"class": self.hardware_class, "type": self.hardware_type}

    def flat(self) -> Dict[str, Any]:
        """
        Dump the entire element model as a flat dictionary, with sub-models separated by "_".

        For example, if an element has `element.electrical.maxI` this will be keyed in the dictionary as
        `eletrical_maxI: value`

        Returns
        -------
            Dict[str, Any]: Flattened dictionary representing the element.
        """
        return flatten(self.model_dump(), parent_key="", separator="_")

    def is_subelement(self) -> bool:
        """
        Flag to indicate whether the element is a subelement of another, such as a solenoid surrounding
        an RF cavity or a BPM embedded inside a magnet. This precludes it from being included when calculating
        the full length of a beamline.

        Returns
        -------
            bool: True if the element is a subelement.
        """
        return self.subelement is not None


class Element(baseElement, _ElementBase):
    """
    Standard class for representing elements.
    Inherits from `baseElement` which wraps schema base `_AcceleratorElementBase`.
    Adds StandardElement fields: simulation, electrical, manufacturer, controls, reference.

    Attributes:
        simulation: :class:`~laura.models.simulation.SimulationElement`: The simulation attributes of the element.
        electrical: :class:`~laura.models.electrical.ElectricalElement`: The electrical attributes of the element.
        manufacturer: :class:`~laura.models.manufacturer.Manufacturer`: The manufacturer attributes of the element.
        controls: :class:`~laura.models.control.ControlsInformation` | None: The control system attributes of the element.
        reference: :class:`~laura.models.reference.ReferenceElement` | None: Reference information for the element.
    """

    # Override the generated base-class type so that dicts are validated as
    # ManufacturerElement (which coerces int serial_number → str) rather than the
    # bare _ManufacturerElementBase which only accepts strings.
    manufacturer: Optional[ManufacturerElement] = Field(default=None)

    controls: ControlsInformation | None = None
    """Control-system process-variable definitions."""

    def model_post_init(self, __context: Any) -> None:
        # Preserve prior convenience behavior while keeping declarations schema-first.
        super().model_post_init(__context)
        try:
            _ensure_nested_default(self, "simulation", SimulationElement)
        except Exception:
            # Subclass has a more specific simulation type; let it handle initialisation.
            pass
        _ensure_nested_default(self, "electrical", ElectricalElement)
        _ensure_nested_default(self, "manufacturer", ManufacturerElement)


class PhysicalBaseElement(Element, _PhysicalAcceleratorElementBase):
    """
    Element with a physical attribute; see :class:`~laura.models.physical.PhysicalElement`.

    Attributes:
        physical: PhysicalElement: The physical attributes of the element.
    """

    # Override the generated base-class type so that dicts are validated directly
    # as PhysicalElement (which knows about reference_placement) rather than the
    # base _PhysicalElementBase which would silently drop unknown fields.
    physical: Optional[PhysicalElement] = Field(default=None)

    def model_post_init(self, __context: Any) -> None:
        super().model_post_init(__context)
        self.physical = _coerce_nested_model(self.physical, PhysicalElement)
        # Wire parent reference so _physical_angle can read the bend angle
        if self.physical is not None:
            self.physical._parent = self

    @property
    def bend_angle(self) -> Rotation:
        """
        Bending angle of the element.
        #TODO this probably doesn't do what it should.

        Returns
        -------
            :class:`~laura.models.physical.Rotation`: The rotation attribute of the element.
        """
        return Rotation.from_list([0, 0, 0])

    @property
    def start_angle(self) -> Rotation:
        """
        Initial global rotation angle of the element.
        #TODO this probably doesn't do what it should.
        """
        return self.physical.rotation + self.physical.global_rotation

    @property
    def end_angle(self) -> Rotation:
        """
        Final global rotation angle of the element
        #TODO this probably doesn't do what it should.
        """
        return self.start_angle


class Magnet(PhysicalBaseElement, _MagnetBase):
    """
    Base class for representing magnets.
    Inherits from PhysicalBaseElement, which provides proper attribute cascading
    through __getattr__/__setattr__ and the IgnoreExtra mechanism.

    Attributes:
        hardware_class: Magnet (frozen, overrides schema)
        degauss: :class:`~laura.models.degauss.DegaussableElement`: The degaussing attributes of the magnet.
        simulation: :class:`~laura.models.simulation.MagnetSimulationElement`: The simulation attributes of the magnet.
        magnetic: :class:`~laura.models.magnetic.MagneticElement` | None: The magnetic attributes of the magnet.
        physical: :class:`~laura.models.physical.PhysicalElement` | None: Physical attributes of the magnet.
    """

    hardware_class: str = Field(default="Magnet", frozen=True)
    """Magnet hardware class."""

    simulation: Optional[MagnetSimulationElement] = None
    """Magnet simulation attributes."""

    def model_post_init(self, __context: Any) -> None:
        super().model_post_init(__context)
        _ensure_nested_default(self, "simulation", MagnetSimulationElement)

    @property
    def bend_angle(self) -> Rotation:
        """
        Rotation of the magnet based on its bending angle.
        """
        if self.magnetic is not None and getattr(self.magnetic, 'angle', None) is not None:
            # angle may be stored symbolically as a functional-definition name;
            # geometry needs a number, and KnL() always resolves.
            return Rotation.from_list([0, 0, self.magnetic.KnL(0)])
        return Rotation.from_list([0, 0, 0])

    @property
    def end_angle(self) -> float:
        """End angle of the magnet"""
        return self.start_angle.theta + self.bend_angle.theta


class Dipole(Magnet, _DipoleBase):
    """
    Dipole element.

    Attributes:
        hardware_type (str): The hardware type of the dipole.
        magnetic (:class:`~laura.models.magnetic.Dipole_Magnet`): The magnetic attributes of the dipole.
    """

    hardware_type: str = Field(default="Dipole", frozen=True)
    """Dipole hardware type."""

    magnetic: Dipole_Magnet = Field(default_factory=Dipole_Magnet)


class Quadrupole(Magnet, _QuadrupoleBase):
    """
    Quadrupole element.

    Attributes:
        hardware_type (str): The hardware type of the quadrupole.
        magnetic (:class:`~laura.models.magnetic.Quadrupole_Magnet`): The magnetic attributes of the quadrupole.
    """

    hardware_type: str = Field(default="Quadrupole", frozen=True)
    """Quadrupole hardware type."""

    magnetic: Quadrupole_Magnet = Field(default_factory=Quadrupole_Magnet)
    """Magnetic attributes of the quadrupole."""


class Sextupole(Magnet, _SextupoleBase):
    """
    Sextupole element.

    Attributes:
        hardware_type (str): The hardware type of the sextupole.
        magnetic (:class:`~laura.models.magnetic.Sextupole_Magnet`): The magnetic attributes of the sextupole.
    """

    hardware_type: str = Field(default="Sextupole", frozen=True)
    """Sextupole hardware type."""

    magnetic: Sextupole_Magnet = Field(default_factory=Sextupole_Magnet)
    """Magnetic attributes of the sextupole."""


class Octupole(Magnet, _OctupoleBase):
    """
    Octupole element.

    Attributes:
        hardware_type (str): The hardware type of the octupole.
        magnetic (:class:`~laura.models.magnetic.Octupole_Magnet`): The magnetic attributes of the octupole.
    """

    hardware_type: str = Field(default="Octupole", frozen=True)
    """Octupole hardware type."""

    magnetic: Octupole_Magnet = Field(default_factory=Octupole_Magnet)
    """Magnetic attributes of the octupole."""


class Horizontal_Corrector(Dipole, _HorizontalCorrectorBase):
    """
    Horizontal corrector element.

    Attributes:
        hardware_type (str): The hardware type of the corrector.
        magnetic (:class:`~laura.models.magnetic.Corrector_Magnet`): The magnetic
        attributes of the corrector -- only ``horizontal_kick`` is expected to be
        set.
    """

    hardware_type: str = Field(default="Horizontal_Corrector", frozen=True)
    """Horizontal corrector hardware type."""

    magnetic: Corrector_Magnet = Field(default_factory=Corrector_Magnet)
    """Corrector magnetic attributes."""


class Vertical_Corrector(Dipole, _VerticalCorrectorBase):
    """
    Vertical corrector element.

    Attributes:
        hardware_type (str): The hardware type of the corrector.
        magnetic (:class:`~laura.models.magnetic.Corrector_Magnet`): The magnetic
        attributes of the corrector -- only ``vertical_kick`` is expected to be
        set.
    """

    hardware_type: str = Field(default="Vertical_Corrector", frozen=True)
    """Vertical corrector hardware type."""

    magnetic: Corrector_Magnet = Field(default_factory=Corrector_Magnet)
    """Corrector magnetic attributes."""


class Combined_Corrector(Dipole, _CombinedCorrectorBase):
    """
    Combined (horizontal + vertical) corrector element.

    Attributes:
        hardware_type (str): The hardware type of the corrector.
        magnetic (:class:`~laura.models.magnetic.Corrector_Magnet`): The magnetic
        attributes of the corrector; both ``horizontal_kick`` and ``vertical_kick``
        may be set independently.
        Horizontal_Corrector (str): Name of a separately-defined
        :class:`Horizontal_Corrector` element this combined corrector is paired
        with, for hardware/PS bookkeeping (see e.g. ``LAURA.get_correctors``) --
        this is a cross-reference, not where the horizontal kick strength lives.
        Vertical_Corrector (str): As ``Horizontal_Corrector``, for the paired
        :class:`Vertical_Corrector` element.
    """

    hardware_type: str = Field(default="Combined_Corrector", frozen=True)
    """Combined corrector hardware type."""

    magnetic: Corrector_Magnet = Field(default_factory=Corrector_Magnet)
    """Corrector magnetic attributes."""

    Horizontal_Corrector: str | None = Field(default=None, frozen=True)
    """Name of horizontal corrector."""

    Vertical_Corrector: str | None = Field(default=None, frozen=True)
    """Name of vertical corrector."""


class Solenoid(Magnet, _SolenoidBase):
    """
    Solenoid element.

    Attributes:
        hardware_type (str): The hardware type of the solenoid.
        magnetic (:class:`~laura.models.magnetic.Solenoid_Magnet`): The magnetic attributes of the solenoid.
    """

    hardware_type: str = Field(default="Solenoid", frozen=True)
    """Solenoid hardware type."""

    magnetic: Solenoid_Magnet = Field(default_factory=Solenoid_Magnet)
    """Magnetic attributes of the solenoid."""


class NonLinearLens(Magnet, _NonLinearLensBase):
    """
    Non-linear lens element.

    Attributes:
        hardware_type (str): The hardware type of the NLL.
        magnetic (:class:`~laura.models.magnetic.NonLinearLens_Magnet`): The magnetic attributes of the NLL.
    """

    hardware_type: str = Field(default="NonLinearLens", frozen=True)
    """Non-linear lens hardware type."""

    magnetic: NonLinearLens_Magnet = Field(default_factory=NonLinearLens_Magnet)
    """Magnetic attributes of the non-linear-lens."""


class Wiggler(Magnet, _WigglerBase):
    """
    Wiggler element.

    Attributes:
        hardware_type (str): The hardware type of the wiggler.
        magnetic (:class:`~laura.models.magnetic.Wiggler_Magnet`): The magnetic attributes of the wiggler.
        laser (:class:`~laura.models.laser.Laser_Magnet` or None): The laser associated with the wiggler.
    """

    hardware_type: str = Field(default="Wiggler", frozen=True)
    """Wiggler hardware type."""

    magnetic: Wiggler_Magnet = Field(default_factory=Wiggler_Magnet)
    """Magnetic attributes of the wiggler."""

    laser: LaserElement | None = None
    """Laser attached to the wiggler."""


class TwissMatch(PhysicalBaseElement, _TwissMatchBase):
    """
    Twiss matching element. Used for changing the Twiss parameters of the beam.

    Attributes:
        hardware_type (str): The hardware type of the element.
        hardware_class (str): The hardware class of the element.
        simulation (:class:`~laura.models.simulation.TwissMatchSimulationElement`): The simulation attributes of the matching element.
    """

    hardware_type: str = Field(default="TwissMatch", frozen=True)
    """Twiss match hardware type."""

    hardware_class: str = Field(default="TwissMatch", frozen=True)
    """Twiss match hardware class."""

    simulation: Optional[TwissMatchSimulationElement] = None
    """TwissMatch simulation attributes."""

    def model_post_init(self, __context: Any) -> None:
        super().model_post_init(__context)
        _ensure_nested_default(self, "simulation", TwissMatchSimulationElement)

class MatrixTransform(PhysicalBaseElement):
    """
    Matrix transform element. Applies an instantaneous matrix kick to the beam, up to 2nd order.

    Attributes:
        hardware_type (str): The hardware type of the element.
        hardware_class (str): The hardware class of the element.
        simulation (:class:`~laura.models.simulation.MatrixSimulationElement`): The simulation attributes of the matrix element.
    """

    hardware_type: str = Field(default="MatrixTransform", frozen=True)
    """Twiss match hardware type."""

    hardware_class: str = Field(default="Simulation", frozen=True)
    """Twiss match hardware class."""

    simulation: MatrixTransformSimulationElement = Field(
        default_factory=MatrixTransformSimulationElement
    )
    """Simulation attributes of the matrix element."""

    def model_post_init(self, __context: Any) -> None:
        super().model_post_init(__context)
        _ensure_nested_default(self, "simulation", MatrixTransformSimulationElement)


class Diagnostic(PhysicalBaseElement, _DiagnosticBase):
    """
    Base class for representing diagnostics.

    Attributes:
        hardware_type (str): The hardware type of the diagnostic.
        hardware_class (str): The hardware class of the diagnostic.
        simulation: (:class:`~laura.models.simulation.DiagnosticSimulationElement`): The simulation
        attributes of the diagnostic (including its `output_filename`).
    """

    hardware_type: str = Field(default="Diagnostic", frozen=True)
    """Diagnostic hardware type."""

    hardware_class: str = Field(default="Diagnostic", frozen=True)
    """Diagnostic hardware class."""

    simulation: Optional[DiagnosticSimulationElement] = None
    """Diagnostic simulation attributes."""

    def model_post_init(self, __context: Any) -> None:
        super().model_post_init(__context)
        _ensure_nested_default(self, "simulation", DiagnosticSimulationElement)


class Beam_Position_Monitor(Diagnostic, _BeamPositionMonitorBase):
    """
    BPM element.

    Attributes:
        hardware_type (str): The hardware type of the diagnostic.
        hardware_model (str): The specific hardware model of the diagnostic (i.e. Stripline, Cavity).
        diagnostic: (:class:`~laura.models.diagnostic.Beam_Position_Monitor_Diagnostic`): The diagnostic
        attributes of the BPM.
    """

    hardware_type: str = Field(
        default="Beam_Position_Monitor", frozen=True, alias="BPM"
    )
    """BPM hardware type."""

    hardware_model: str = Field(default="Stripline", frozen=True)
    """BPM hardware model."""

    def model_post_init(self, __context: Any) -> None:
        super().model_post_init(__context)
        _ensure_nested_default(self, "diagnostic", Beam_Position_Monitor_Diagnostic)


class Beam_Arrival_Monitor(Diagnostic, _BeamArrivalMonitorBase):
    """
    BAM element.

    Attributes:
        hardware_type (str): The hardware type of the diagnostic.
        hardware_model (str): The specific hardware model of the diagnostic.
        diagnostic: (:class:`~laura.models.diagnostic.Beam_Arrival_Monitor_Diagnostic`): The diagnostic
        attributes of the BAM.
    """

    hardware_type: str = Field(default="Beam_Arrival_Monitor", frozen=True, alias="BAM")
    """BAM hardware type."""

    hardware_model: str = Field(default="DESY", frozen=True)
    """BAM hardware model."""

    def model_post_init(self, __context: Any) -> None:
        super().model_post_init(__context)
        _ensure_nested_default(self, "diagnostic", Beam_Arrival_Monitor_Diagnostic)


class Bunch_Length_Monitor(Diagnostic, _BunchLengthMonitorBase):
    """
    BLM element.

    Attributes:
        hardware_type (str): The hardware type of the diagnostic.
        hardware_model (str): The specific hardware model of the diagnostic.
        diagnostic: (:class:`~laura.models.diagnostic.Bunch_Length_Monitor_Diagnostic`): The diagnostic
        attributes of the BLM.
    """

    hardware_type: str = Field(default="Bunch_Length_Monitor", frozen=True, alias="BLM")
    """BLM hardware type."""

    hardware_model: str = Field(default="CDR", frozen=True)
    """BLM hardware model."""

    def model_post_init(self, __context: Any) -> None:
        super().model_post_init(__context)
        _ensure_nested_default(self, "diagnostic", Bunch_Length_Monitor_Diagnostic)


class Photon_Monitor(Diagnostic):
    """
    Photon monitor element.

    Attributes:
        hardware_type (str): The hardware type of the diagnostic.
        hardware_model (str): The specific hardware model of the diagnostic.
        intensity: (:class:`~laura.models.diagnostic.Photon_Intensity_Monitor_Diagnostic`): The diagnostic
        attributes of the intensity monitor.
    """

    hardware_type: str = Field(
        default="Photon_Monitor", frozen=True,
    )
    """Photon monitor hardware type."""

    hardware_model: str = Field(default="Photon_Monitor", frozen=True)
    """Photon monitor hardware model."""

    intensity: Photon_Intensity_Monitor_Diagnostic = Field(
        default_factory=Photon_Intensity_Monitor_Diagnostic
    )
    """Diagnostic attributes of the intensity monitor."""


class Camera(Diagnostic, _CameraBase):
    """
    Camera element.

    Attributes:
        hardware_type (str): The hardware type of the diagnostic.
        hardware_model (str): The specific hardware model of the diagnostic.
        diagnostic: (:class:`~laura.models.diagnostic.Camera_Diagnostic`): The diagnostic
        attributes of the Camera.
    """

    hardware_type: str = Field(default="Camera", frozen=True)
    """Camera hardware type."""

    hardware_model: str = Field(default="PCO", frozen=True)
    """Camera hardware model."""

    def model_post_init(self, __context: Any) -> None:
        super().model_post_init(__context)
        _ensure_nested_default(self, "diagnostic", Camera_Diagnostic)


class Screen(Diagnostic, _ScreenBase):
    """
    Screen element.

    Attributes:
        hardware_type (str): The hardware type of the diagnostic.
        hardware_model (str): The specific hardware model of the diagnostic.
        diagnostic: (:class:`~laura.models.diagnostic.Screen_Diagnostic`): The diagnostic
        attributes of the Screen.
    """

    hardware_type: str = Field(default="Screen", frozen=True)
    """Screen hardware type."""

    hardware_model: str = Field(default="YAG", frozen=True)
    """Screen hardware model."""

    controls: ScreenControlsInformation | None = None

    def model_post_init(self, __context: Any) -> None:
        super().model_post_init(__context)
        _ensure_nested_default(self, "diagnostic", Screen_Diagnostic)


class ChargeDiagnostic(Diagnostic, _ChargeDiagnosticBase):
    """
    Generic charge diagnostic element.

    Attributes:
        hardware_type (str): The hardware type of the diagnostic.
        diagnostic: (:class:`~laura.models.diagnostic.Charge_Diagnostic`): The diagnostic
        attributes of the diagnostic.
    """

    hardware_type: str = Field(default="ChargeDiagnostic", frozen=True)
    """Charge diagnostic hardware type."""

    def model_post_init(self, __context: Any) -> None:
        super().model_post_init(__context)
        _ensure_nested_default(self, "diagnostic", Charge_Diagnostic)


class Wall_Current_Monitor(ChargeDiagnostic, _WallCurrentMonitorBase):
    """
    WCM charge diagnostic element.

    Attributes:
        hardware_type (str): The hardware type of the diagnostic.
    """

    hardware_type: str = Field(default="Wall_Current_Monitor", frozen=True, alias="WCM")
    """WCM hardware type."""


class Faraday_Cup_Monitor(ChargeDiagnostic, _FaradayCupMonitorBase):
    """
    FCM charge diagnostic element.

    Attributes:
        hardware_type (str): The hardware type of the diagnostic.
    """

    hardware_type: str = Field(default="Faraday_Cup_Monitor", frozen=True, alias="FCM")
    """FCM hardware type."""


class Integrated_Current_Transformer(ChargeDiagnostic, _IntegratedCurrentTransformerBase):
    """
    ICT charge diagnostic element.

    Attributes:
        hardware_type (str): The hardware type of the diagnostic.
    """

    hardware_type: str = Field(
        default="Integrated_Current_Transformer", frozen=True, alias="ICT"
    )
    """ICT hardware type."""


class Stage(PhysicalBaseElement, _StageBase):
    """
    Moveable stage element.

    Attributes:
        hardware_type (str): The hardware type of the stage.
        hardware_model (str): The hardware model of the stage.
    """

    hardware_class: str = Field(default="Stage", frozen=True)
    """Moveable stage hardware class."""

    hardware_type: str = Field(default="Stage", frozen=True)
    """Moveable stage hardware type."""

    hardware_model: str = Field(default="Stage", frozen=True)
    """Moveable stage hardware model."""


class VacuumGauge(PhysicalBaseElement, _VacuumGaugeBase):
    """
    Vacuum gauge element.

    Attributes:
        hardware_type (str): The hardware type of the gauge.
        hardware_model (str): The hardware model of the gauge.
    """

    hardware_class: str = Field(default="Vacuum", frozen=True)
    """Vacuum gauge hardware class."""

    hardware_type: str = Field(default="VacuumGauge", frozen=True)
    """Vacuum gauge hardware type."""

    hardware_model: str = Field(default="IMG", frozen=True)
    """Vacuum gauge hardware model."""


class Laser(PhysicalBaseElement, _LaserBase):
    """
    Laser element.

    Attributes:
        hardware_type (str): The hardware type of the laser.
        hardware_model (str): The hardware model of the laser.
        laser (:class:`~laura.models.laser.LaserElement`): The laser attributes of the laser.
    """

    hardware_class: str = Field(default="Laser", frozen=True)
    """Laser hardware type."""

    hardware_type: str = Field(default="Laser", frozen=True)
    """Laser hardware type."""

    hardware_model: str = Field(default="Laser", frozen=True)
    """Laser hardware model."""

    def model_post_init(self, __context: Any) -> None:
        super().model_post_init(__context)
        _ensure_nested_default(self, "laser", LaserElement)


class LaserEnergyMeter(Element, _LaserEnergyMeterBase):
    """
    Laser energy meter element.

    Attributes:
        hardware_type (str): The hardware type of the laser energy meter.
        hardware_model (str): The hardware model of the laser energy meter.
        laser (:class:`~laura.models.laser.LaserEnergyMeterElement`): The laser-related attributes of the
        energy meter.
    """

    hardware_class: str = Field(default="Laser", frozen=True)
    """Laser energy meter hardware class."""

    hardware_type: str = Field(default="LaserEnergyMeter", frozen=True)
    """Laser energy meter hardware type."""

    hardware_model: str = Field(default="Gentec Photodiode", frozen=True)
    """Laser energy meter hardware model.
    #TODO should be manufacturer?"""

    def model_post_init(self, __context: Any) -> None:
        super().model_post_init(__context)
        _ensure_nested_default(self, "laser", LaserEnergyMeterElement)


class LaserHalfWavePlate(Element, _LaserHalfWavePlateBase):
    """
    Laser half-wave plate element.

    Attributes:
        hardware_type (str): The hardware type of the HWP.
        hardware_model (str): The hardware model of the HWP.
        laser (:class:`~laura.models.laser.LaserHalfWavePlateElement`): The laser-related attributes of the
        HWP.
    """

    hardware_class: str = Field(default="Laser", frozen=True)
    """Laser half-wave plate hardware class."""

    hardware_type: str = Field(default="LaserHalfWavePlate", frozen=True)
    """Laser half-wave plate element type."""

    hardware_model: str = Field(default="Newport", frozen=True)
    """Laser half-wave plate hardware model.
    #TODO should be manufacturer?"""

    def model_post_init(self, __context: Any) -> None:
        super().model_post_init(__context)
        _ensure_nested_default(self, "laser", LaserHalfWavePlateElement)


class LaserMirror(Element, _LaserMirrorBase):
    """
    Laser mirror element.

    Attributes:
        hardware_type (str): The hardware type of the mirror.
        hardware_model (str): The hardware model of the mirror.
        controls (:class:`~laura.models.controls.MirrorControlsInformation`): The control-related attributes of the
        mirror.
    """

    hardware_class: str = Field(default="Laser", frozen=True)
    """Laser mirror hardware class."""

    hardware_type: str = Field(default="LaserMirror", frozen=True)
    """Laser mirror hardware type."""

    hardware_model: str = Field(default="Planar", frozen=True)
    """Laser mirror hardware model."""

    controls: MirrorControlsInformation | None = None
    """Laser mirror control attributes of the element."""


class LaserAttenuator(Element, _LaserAttenuatorBase):
    """
    Laser attenuator element.

    Attributes:
        hardware_type (str): The hardware type of the attenuator.
    """

    hardware_class: str = Field(default="Laser", frozen=True)
    """Laser attenuator hardware class."""

    hardware_type: str = Field(default="LaserAttenuator", frozen=True)
    """Laser attenuator hardware type."""

    pass


class Plasma(PhysicalBaseElement, _PlasmaBase):
    """
    Plasma element.

    Attributes:
        hardware_type (str): The hardware type of the element.
        simulation (:class:`~laura.models.simulation.PlasmaSimulationElement`): The simulation
        attributes of the plasma.
        plasma (:class:`~laura.models.plasma.PlasmaElement`): The plasma attributes of the plasma.
        laser (:class:`~laura.models.laser.LaserElement` or None): The laser assosicated with the plasma
    """

    hardware_class: str = Field(default="Plasma", frozen=True)
    """Plasma hardware class."""

    hardware_type: str = Field(default="Plasma", frozen=True)
    """Plasma hardware type."""

    simulation: Optional[PlasmaSimulationElement] = None
    """Plasma simulation attributes."""

    def model_post_init(self, __context: Any) -> None:
        super().model_post_init(__context)
        _ensure_nested_default(self, "simulation", PlasmaSimulationElement)
        _ensure_nested_default(self, "plasma", PlasmaElement)


class Lighting(Element, _LightingBase):
    """
    Lighting element.

    Attributes:
        hardware_type (str): The hardware type of the element.
        hardware_model (str): The hardware model of the element.
        lights (:class:`~laura.models.lighting.LightingElement`): The lighting element.
    """

    hardware_class: str = Field(default="Lighting", frozen=True)
    """Lighting hardware class."""

    hardware_type: str = Field(default="Lighting", frozen=True)
    """Lighting hardware type."""

    hardware_model: str = Field(default="LED", frozen=True)
    """Lighting hardware model."""

    def model_post_init(self, __context: Any) -> None:
        super().model_post_init(__context)
        _ensure_nested_default(self, "lights", LightingElement)


class PowerSupply(Element):
    """
    Generic power supply element.

    Used to represent standalone power-supply units that feed other components
    (for example magnets and RF chains) through control-signal connectivity.
    """

    hardware_type: str = Field(default="PowerSupply", frozen=True)
    """Power supply hardware type."""

    hardware_model: str = Field(default="GenericPowerSupply", frozen=True)
    """Power supply hardware model."""


class PID(Element, _PIDBase):
    """
    Proportional-integral-derivative feedback element.

    Attributes:
        hardware_type (str): The hardware type of the element.
        hardware_model (str): The hardware model of the element.
        PID (:class:`~laura.models.RF.PIDElement`): The PID element.
    """

    hardware_class: str = Field(default="Feedback", frozen=True)
    """PID hardware class."""

    hardware_type: str = Field(default="PID", frozen=True)
    """PID hardware type."""

    hardware_model: str = Field(default="RF", frozen=True)
    """PID hardware model."""

    PID: PIDElement = Field(default_factory=PIDElement)
    """PID attributes of the element."""


class Low_Level_RF(Element, _LowLevelRFBase):
    """
    Low-level RF element.

    Attributes:
        hardware_type (str): The hardware type of the element.
        hardware_model (str): The hardware model of the element.
        LLRF (:class:`~laura.models.RF.Low_Level_RF_Element`): The LLRF element.
    """

    hardware_class: str = Field(default="RF", frozen=True)
    """LLRF hardware class."""

    hardware_type: str = Field(default="Low_Level_RF", frozen=True)
    """LLRF hardware type."""

    hardware_model: str = Field(default="Libera", frozen=True)
    """LLRF hardware model."""

    LLRF: Low_Level_RF_Element = Field(default_factory=Low_Level_RF_Element)
    """LLRF attributes of the element."""


class RFCavity(PhysicalBaseElement, _RFCavityBase):
    """
    RFCavity element.

    Attributes:
        hardware_type (str): The hardware type of the RF cavity.
        hardware_model (str): The specific hardware model of the RF cavity.
        cavity (:class:`~laura.models.RF.RFCavityElement`): The RF cavity attributes of the element.
        simulation: (:class:`~laura.models.simulation.RFCavitySimulationElement`): The simulation
        attributes of the RF cavity.
    """

    hardware_class: str = Field(default="RF", frozen=True)
    """RF cavity hardware class."""

    hardware_type: str = Field(default="RFCavity", frozen=True)
    """RF cavity hardware type."""

    hardware_model: str = Field(default="SBand", frozen=True)
    """RF cavity hardware model."""

    simulation: Optional[RFCavitySimulationElement] = None
    """RF cavity simulation attributes."""

    def model_post_init(self, __context: Any) -> None:
        super().model_post_init(__context)
        _ensure_nested_default(self, "cavity", RFCavityElement)


class Wakefield(PhysicalBaseElement, _WakefieldBase):
    """
    Wakefield element.

    Attributes:
        hardware_type (str): The hardware type of the wakefield.
        hardware_model (str): The specific hardware model of the wakefield.
        cavity: (:class:`~laura.models.RF.WakefieldElement`): The wakefield cavity attributes of the element.
        simulation: (:class:`~laura.models.simulation.WakefieldSimulationElement`): The simulation
        attributes of the wakefield cavity.
    """

    hardware_class: str = Field(default="Wakefield", frozen=True)
    """Wakefield hardware class."""

    hardware_type: str = Field(default="Wakefield", frozen=True)
    """Wakefield hardware type."""

    hardware_model: str = Field(default="Dielectric", frozen=True)
    """Wakefield hardware model."""

    simulation: Optional[WakefieldSimulationElement] = None
    """Wakefield simulation attributes."""

    def model_post_init(self, __context: Any) -> None:
        super().model_post_init(__context)
        _ensure_nested_default(self, "cavity", WakefieldElement)
        _ensure_nested_default(self, "simulation", WakefieldSimulationElement)


class RFDeflectingCavity(RFCavity, _RFDeflectingCavityBase):
    """
    RF Deflecting Cavity element.

    Attributes:
        hardware_type (str): The hardware type of the RF cavity.
        hardware_model (str): The specific hardware model of the RF cavity.
        cavity (:class:`~laura.models.RF.RFDeflectingCavityElement`): The RF cavity attributes of the element.
        simulation: (:class:`~laura.models.simulation.RFCavitySimulationElement`): The simulation
        attributes of the RF cavity.
    """

    hardware_type: str = Field(default="RFDeflectingCavity", frozen=True)
    """RF deflecting cavity hardware type."""

    hardware_model: str = Field(default="SBand", frozen=True)
    """RF deflecting cavity hardware model."""

    def model_post_init(self, __context: Any) -> None:
        super().model_post_init(__context)
        _ensure_nested_default(self, "cavity", RFDeflectingCavityElement)
        _ensure_nested_default(self, "simulation", RFCavitySimulationElement)



class CrabCavity(RFCavity, _CrabCavityBase):
    """
    Crab Cavity element.

    Attributes:
        hardware_type (str): The hardware type of the crab cavity.
        hardware_model (str): The specific hardware model of the crab cavity.
        cavity (:class:`~laura.models.RF.RFDeflectingCavityElement`): The RF cavity attributes of the element.
        simulation: (:class:`~laura.models.simulation.RFCavitySimulationElement`): The simulation
        attributes of the crab cavity.
    """

    hardware_type: str = Field(default="CrabCavity", frozen=True)
    """Crab cavity hardware type."""

    hardware_model: str = Field(default="SBand", frozen=True)
    """Crab cavity hardware model."""

    cavity: Optional[RFDeflectingCavityElement] = None
    """Crab-cavity RF structure parameters."""

    def model_post_init(self, __context: Any) -> None:
        super().model_post_init(__context)
        _ensure_nested_default(self, "cavity", RFDeflectingCavityElement)
        _ensure_nested_default(self, "simulation", RFCavitySimulationElement)


class RFModulator(Element, _RFModulatorBase):
    """
    RF Modulator element.

    Attributes:
        hardware_type (str): The hardware type of the RF modulator.
        hardware_model (str): The specific hardware model of the RF modulator.
        modulator (:class:`~laura.models.RF.RFModulatorElement`): The RF modulator attributes of the element.
    """

    hardware_class: str = Field(default="RF", frozen=True)
    """RF modulator hardware class."""

    hardware_type: str = Field(default="RFModulator", frozen=True)
    """RF modulator hardware type."""

    hardware_model: str = Field(default="Thales", frozen=True)
    """RF modulator hardware model.
    #TODO move to manufacturer?"""

    def model_post_init(self, __context: Any) -> None:
        super().model_post_init(__context)
        _ensure_nested_default(self, "modulator", RFModulatorElement)


class RFProtection(Element, _RFProtectionBase):
    """
    RF Protection element.

    Attributes:
        hardware_type (str): The hardware type of the RF protection system.
        hardware_model (str): The specific hardware model of the RF protection system.
        modulator (:class:`~laura.models.RF.RFProtectionElement`): The RF protection attributes of the element.
    """

    hardware_class: str = Field(default="RF", frozen=True)
    """RF protection hardware class."""

    hardware_type: str = Field(default="RFProtection", frozen=True)
    """RF protection hardware type."""

    hardware_model: str = Field(default="PROT", frozen=True)
    """RF protection hardware model."""

    modulator: RFProtectionElement = Field(default_factory=RFProtectionElement)
    """RF protection attributes of the element."""


class RFHeartbeat(Element, _RFHeartbeatBase):
    """
    RF Heartbeat element.

    Attributes:
        hardware_type (str): The hardware type of the RF heartbeat system.
        heartbeat (:class:`~laura.models.RF.RFHeartbeatElement`): The RF heartbeat attributes of the element.
    """

    hardware_class: str = Field(default="RF", frozen=True)
    """RF heartbeat hardware class."""

    hardware_type: str = Field(default="RFHeartbeat", frozen=True)
    """RF heartbeat hardware type."""

    def model_post_init(self, __context: Any) -> None:
        super().model_post_init(__context)
        _ensure_nested_default(self, "heartbeat", RFHeartbeatElement)


class Shutter(PhysicalBaseElement, _ShutterBase):
    """
    Shutter element.

    Attributes:
        hardware_type (str): The hardware type of the shutter.
        shutter (:class:`~laura.models.shutter.ShutterElement`): The shutter attributes of the element.
    """

    hardware_class: str = Field(default="Shutter", frozen=True)
    """Shutter hardware class"""

    hardware_type: str = Field(default="Shutter", frozen=True)
    """Shutter hardware type"""

    controls: ShutterControlsInformation | None = None
    """Shutter control attributes of the element."""

    def model_post_init(self, __context: Any) -> None:
        super().model_post_init(__context)
        _ensure_nested_default(self, "shutter", ShutterElement)


class Valve(PhysicalBaseElement, _ValveBase):
    """
    Vacuum valve element.

    Attributes:
        hardware_type (str): The hardware type of the valve.
        valve (:class:`~laura.models.shutter.ValveElement`): The valve attributes of the element.
    """

    hardware_class: str = Field(default="Vacuum", frozen=True)
    """Valve hardware class."""

    hardware_type: str = Field(default="Valve", frozen=True)
    """Valve hardware type."""

    def model_post_init(self, __context: Any) -> None:
        super().model_post_init(__context)
        _ensure_nested_default(self, "valve", ValveElement)


class Marker(PhysicalBaseElement, _MarkerBase):
    """
    Marker element.

    Attributes:
        hardware_type (str): The hardware type of the marker.
        hardware_model (str): The hardware model of the marker.
        simulation (:class:`~laura.models.simulation.DiagnosticSimulationElement`): The simulation
        attributes of the marker.
    """

    hardware_class: str = Field(default="Marker", frozen=True)
    """Marker hardware type."""

    hardware_type: str = Field(default="Marker", frozen=True)
    """Marker hardware type."""

    hardware_model: str = Field(default="Simulation", frozen=True)
    """Marker hardware model."""

    simulation: Optional[DiagnosticSimulationElement] = None
    """Marker simulation attributes."""

    def model_post_init(self, __context: Any) -> None:
        super().model_post_init(__context)
        _ensure_nested_default(self, "simulation", DiagnosticSimulationElement)


class Aperture(PhysicalBaseElement, _ApertureBase):
    """
    Aperture element.

    Attributes:
        hardware_type (str): The hardware type of the aperture.
        hardware_model (str): The hardware model of the aperture.
        aperture (:class:`~laura.models.simulation.ApertureElement`): The simulation
        attributes of the aperture.
    """

    hardware_class: str = Field(default="Aperture", frozen=True)
    """Aperture hardware class."""

    hardware_type: str = Field(default="Aperture", frozen=True)
    """Aperture hardware type."""

    hardware_model: str = Field(default="Simulation", frozen=True)
    """Aperture hardware model."""

    def model_post_init(self, __context: Any) -> None:
        super().model_post_init(__context)
        _ensure_nested_default(self, "aperture", ApertureElement)


class Collimator(Aperture, _CollimatorBase):
    """
    Collimator element.

    Attributes:
        hardware_type (str): The hardware type of the collimator.
        hardware_model (str): The hardware model of the collimator.
    """

    hardware_type: str = Field(default="Collimator", frozen=True)
    """Collimator hardware type."""

    hardware_model: str = Field(default="Simulation", frozen=True)
    """Collimator hardware model."""


class Drift(PhysicalBaseElement, _DriftBase):
    """
    Drift element.

    Attributes:
        hardware_type (str): The hardware type of the marker.
        simulation (:class:`~laura.models.simulation.DriftSimulationElement`): The simulation
        attributes of the drift.
    """

    hardware_type: str = Field(default="Drift", frozen=True)
    """Drift hardware type."""

    simulation: Optional[DriftSimulationElement] = None
    """Drift simulation attributes."""

    def model_post_init(self, __context: Any) -> None:
        super().model_post_init(__context)
        _ensure_nested_default(self, "simulation", DriftSimulationElement)


class ElectrostaticSeparator(PhysicalBaseElement, _ElectrostaticSeparatorBase):
    """
    Electrostatic separator element: a static-field electrode pair providing a
    transverse deflection (see the MAD-X ``ELSEPARATOR`` element; no equivalent
    exists in ELEGANT or Xsuite).

    Attributes:
        hardware_type (str): The hardware type of the element.
        hardware_class (str): The hardware class of the element.
        simulation (:class:`~laura.models.simulation.ElectrostaticSeparatorSimulationElement`):
        The simulation attributes of the separator.
    """

    hardware_type: str = Field(default="ElectrostaticSeparator", frozen=True)
    """Electrostatic separator hardware type."""

    hardware_class: str = Field(default="Generic", frozen=True)
    """Electrostatic separator hardware class."""

    simulation: Optional[ElectrostaticSeparatorSimulationElement] = None
    """Electrostatic-separator simulation attributes."""

    def model_post_init(self, __context: Any) -> None:
        super().model_post_init(__context)
        _ensure_nested_default(self, "simulation", ElectrostaticSeparatorSimulationElement)


class ACDipole(PhysicalBaseElement, _ACDipoleBase):
    """
    Base class for AC dipole / tune-exciter elements: a thin, RF-driven kicker
    used for AC-dipole tune and optics measurements (see the MAD-X
    ``HACDIPOLE``/``VACDIPOLE`` elements and the Xsuite ``ACDipole`` element).

    Attributes:
        hardware_type (str): The hardware type of the element.
        hardware_class (str): The hardware class of the element.
        simulation (:class:`~laura.models.simulation.ACDipoleSimulationElement`):
        The simulation attributes of the exciter.
    """

    hardware_class: str = Field(default="Magnet", frozen=True)
    """AC dipole hardware class."""

    simulation: Optional[ACDipoleSimulationElement] = None
    """AC-dipole simulation attributes."""

    def model_post_init(self, __context: Any) -> None:
        super().model_post_init(__context)
        _ensure_nested_default(self, "simulation", ACDipoleSimulationElement)


class Horizontal_AC_Dipole(ACDipole, _HorizontalACDipoleBase):
    """
    Horizontal AC dipole / tune-exciter element.

    Attributes:
        hardware_type (str): The hardware type of the element.
    """

    hardware_type: str = Field(default="Horizontal_AC_Dipole", frozen=True)
    """Horizontal AC dipole hardware type."""


class Vertical_AC_Dipole(ACDipole, _VerticalACDipoleBase):
    """
    Vertical AC dipole / tune-exciter element.

    Attributes:
        hardware_type (str): The hardware type of the element.
    """

    hardware_type: str = Field(default="Vertical_AC_Dipole", frozen=True)
    """Vertical AC dipole hardware type."""


class Wire(PhysicalBaseElement, _WireBase):
    """
    Compensating wire element: a current-carrying wire used for long-range
    beam-beam compensation (see the MAD-X ``WIRE`` element and the Xsuite
    ``Wire`` element).

    Attributes:
        hardware_type (str): The hardware type of the element.
        hardware_class (str): The hardware class of the element.
        simulation (:class:`~laura.models.simulation.WireSimulationElement`):
        The simulation attributes of the wire.
    """

    hardware_type: str = Field(default="Wire", frozen=True)
    """Wire hardware type."""

    hardware_class: str = Field(default="Diagnostic", frozen=True)
    """Wire hardware class."""

    simulation: Optional[WireSimulationElement] = None
    """Wire simulation attributes."""

    def model_post_init(self, __context: Any) -> None:
        super().model_post_init(__context)
        _ensure_nested_default(self, "simulation", WireSimulationElement)


class BeamBeam(PhysicalBaseElement, _BeamBeamBase):
    """
    Beam-beam interaction element: a weak-strong kick representing the
    electromagnetic field of an opposing (colliding) bunch (see the MAD-X
    ``BEAMBEAM`` element).

    Attributes:
        hardware_type (str): The hardware type of the element.
        hardware_class (str): The hardware class of the element.
        simulation (:class:`~laura.models.simulation.BeamBeamSimulationElement`):
        The simulation attributes of the interaction.
    """

    hardware_type: str = Field(default="BeamBeam", frozen=True)
    """Beam-beam hardware type."""

    hardware_class: str = Field(default="Simulation", frozen=True)
    """Beam-beam hardware class."""

    simulation: Optional[BeamBeamSimulationElement] = None
    """Beam-beam simulation attributes."""

    def model_post_init(self, __context: Any) -> None:
        super().model_post_init(__context)
        _ensure_nested_default(self, "simulation", BeamBeamSimulationElement)


class RFMultipole(PhysicalBaseElement, _RFMultipoleBase):
    """
    Thin RF multipole element: a zero-length multipole kick whose strength
    oscillates at an RF frequency, up to 5th order (see the MAD-X
    ``RFMULTIPOLE`` element and the Xsuite ``RFMultipole`` element).

    Attributes:
        hardware_type (str): The hardware type of the element.
        hardware_class (str): The hardware class of the element.
        simulation (:class:`~laura.models.simulation.RFMultipoleSimulationElement`):
        The simulation attributes of the multipole.
    """

    hardware_type: str = Field(default="RFMultipole", frozen=True)
    """RF multipole hardware type."""

    hardware_class: str = Field(default="RF", frozen=True)
    """RF multipole hardware class."""

    simulation: Optional[RFMultipoleSimulationElement] = None
    """RF-multipole simulation attributes."""

    def model_post_init(self, __context: Any) -> None:
        super().model_post_init(__context)
        _ensure_nested_default(self, "simulation", RFMultipoleSimulationElement)


ELEMENT_REGISTRY: dict[str, type] = {
    _field.default: _cls
    for _cls in list(vars().values())
    if isinstance(_cls, type)
    and issubclass(_cls, Element)
    and (_field := _cls.model_fields.get("hardware_type")) is not None
    and isinstance(_field.default, str)
    and _field.default != "Generic"
}
