# This file is auto-generated from laura/schema/laura_schema.yaml.
# DO NOT EDIT MANUALLY – regenerate with:
#   python laura/schema/generate_pydantic.py
# or:
#   .\laura\schema\generate.ps1
#
# Class naming convention
# -----------------------
# * Enum classes keep their original names (HardwareClassEnum, etc.) so they
#   can be imported directly from this module.
# * All other schema-defined classes are renamed with a leading underscore and
#   a ``Base`` suffix (e.g., Quadrupole → _QuadrupoleBase) to avoid name
#   conflicts with the hand-written wrapper classes in laura/models/*.
#
# Migration guide
# ---------------
# To make a hand-written model use the generated base, import with an alias::
#
#     from laura.models._generated import ManufacturerElement as _ManufacturerElementBase
#
#     class ManufacturerElement(_ManufacturerElementBase):
#         # Override fields that differ from the generated defaults
#         manufacturer: str = ""
#         serial_number: str = ""
#         # Keep custom validators ...
#
# See laura/models/reference.py and laura/models/manufacturer.py for examples.

from __future__ import annotations

import re
import sys
from datetime import (
    date,
    datetime,
    time
)
from decimal import Decimal
from enum import Enum
from typing import (
    Any,
    ClassVar,
    Literal,
    Optional,
    Union
)

from pydantic import (
    AliasChoices,
    BaseModel,
    ConfigDict,
    Field,
    RootModel,
    SerializationInfo,
    SerializerFunctionWrapHandler,
    field_validator,
    model_serializer
)


metamodel_version = "1.11.0"
version = "0.1.0"


class ConfiguredBaseModel(BaseModel):
    model_config = ConfigDict(
        serialize_by_alias = True,
        validate_by_name = True,
        validate_assignment = True,
        validate_default = True,
        extra = "ignore",
        arbitrary_types_allowed = True,
        use_enum_values = True,
        strict = False,
    )





class LinkMLMeta(RootModel):
    root: dict[str, Any] = {}
    model_config = ConfigDict(frozen=True)

    def __getattr__(self, key:str):
        return getattr(self.root, key)

    def __getitem__(self, key:str):
        return self.root[key]

    def __setitem__(self, key:str, value):
        self.root[key] = value

    def __contains__(self, key:str) -> bool:
        return key in self.root


linkml_meta = LinkMLMeta({'default_prefix': 'laura',
     'default_range': 'string',
     'description': 'Linked Data schema for the LAURA (Lattice Architecture for a '
                    'Unified Representation of Accelerators) accelerator element '
                    'model.  Covers all element types, their physical, magnetic, '
                    'diagnostic, RF, and control-system properties.',
     'id': 'https://w3id.org/laura/schema',
     'imports': ['linkml:types',
                 'geometry',
                 'controls',
                 'elements',
                 'machine',
                 'simulation',
                 'magnetic',
                 'rf',
                 'diagnostics',
                 'laser_plasma',
                 'magnets'],
     'license': 'Apache Software License 2.0',
     'name': 'laura_schema',
     'prefixes': {'dcterms': {'prefix_prefix': 'dcterms',
                              'prefix_reference': 'http://purl.org/dc/terms/'},
                  'laura': {'prefix_prefix': 'laura',
                            'prefix_reference': 'https://w3id.org/laura/'},
                  'linkml': {'prefix_prefix': 'linkml',
                             'prefix_reference': 'https://w3id.org/linkml/'},
                  'obo': {'prefix_prefix': 'obo',
                          'prefix_reference': 'http://purl.obolibrary.org/obo/'},
                  'qudt': {'prefix_prefix': 'qudt',
                           'prefix_reference': 'http://qudt.org/schema/qudt/'},
                  'schema': {'prefix_prefix': 'schema',
                             'prefix_reference': 'http://schema.org/'},
                  'skos': {'prefix_prefix': 'skos',
                           'prefix_reference': 'http://www.w3.org/2004/02/skos/core#'},
                  'unit': {'prefix_prefix': 'unit',
                           'prefix_reference': 'http://qudt.org/vocab/unit/'},
                  'xsd': {'prefix_prefix': 'xsd',
                          'prefix_reference': 'http://www.w3.org/2001/XMLSchema#'}},
     'source_file': 'laura/schema/YAML/laura_schema.yaml',
     'subsets': {'bend_angle_reference': {'description': 'Slots that additionally '
                                                         'accept an expression '
                                                         'referencing the dipole '
                                                         'bend angle -- any string '
                                                         'containing the reserved '
                                                         'token "angle", e.g. '
                                                         '"angle" or "angle/2". '
                                                         'Such values are not '
                                                         'functional-definition '
                                                         'names and are skipped '
                                                         'when collecting '
                                                         'references.',
                                          'from_schema': 'https://w3id.org/laura/schema',
                                          'name': 'bend_angle_reference'},
                 'diagnostic_properties': {'description': 'Slots specific to '
                                                          'beam-diagnostic '
                                                          'instruments.',
                                           'from_schema': 'https://w3id.org/laura/schema',
                                           'name': 'diagnostic_properties'},
                 'functional_parameters': {'description': 'Slots whose value may '
                                                          'be the name of a '
                                                          'functional definition '
                                                          '(a symbolic parameter '
                                                          'resolved against the '
                                                          "lattice's "
                                                          'functional_definitions) '
                                                          'as well as a plain '
                                                          'number. Membership is '
                                                          'what '
                                                          'functional_references() '
                                                          'looks for when '
                                                          'collecting the symbols '
                                                          'an element refers to.',
                                           'from_schema': 'https://w3id.org/laura/schema',
                                           'name': 'functional_parameters'},
                 'laser_properties': {'description': 'Slots specific to '
                                                     'laser-related elements.',
                                      'from_schema': 'https://w3id.org/laura/schema',
                                      'name': 'laser_properties'},
                 'magnetic_properties': {'description': 'Slots specific to '
                                                        'magnetic elements.',
                                         'from_schema': 'https://w3id.org/laura/schema',
                                         'name': 'magnetic_properties'},
                 'physical_properties': {'description': 'Slots relevant to the '
                                                        'physical placement or '
                                                        'geometry of an element.',
                                         'from_schema': 'https://w3id.org/laura/schema',
                                         'name': 'physical_properties'},
                 'rf_properties': {'description': 'Slots specific to RF cavity '
                                                  'elements.',
                                   'from_schema': 'https://w3id.org/laura/schema',
                                   'name': 'rf_properties'}},
     'title': 'LAURA Accelerator Element Schema'} )

class IOTypeEnum(str, Enum):
    """
    Input types for accelerator elements.
    """
    current = "current"
    """
    Electrical current.
    """
    voltage = "voltage"
    """
    Electrical voltage.
    """
    phase = "phase"
    """
    Phase in radians.
    """
    setpoint = "setpoint"
    """
    Control setpoint.
    """
    on_off_state = "on_off_state"
    """
    On/Off state.
    """
    open_closed_state = "open_closed_state"
    """
    Open/Closed state.
    """
    position = "position"
    """
    Physical position.
    """
    rotation = "rotation"
    """
    Physical rotation.
    """
    power = "power"
    """
    Electrical power.
    """
    pressure = "pressure"
    """
    Gas pressure.
    """
    charge = "charge"
    """
    Electrical charge.
    """
    absolute_time = "absolute_time"
    """
    Absolute timing.
    """
    relative_time = "relative_time"
    """
    Relative timing.
    """
    shot_number = "shot_number"
    """
    Shot number.
    """
    value = "value"
    """
    Single value.
    """
    waveform = "waveform"
    """
    Multivalued waveform.
    """
    magnetic_field = "magnetic_field"
    """
    Magnetic field.
    """


class ControlTypeEnum(str, Enum):
    """
    Kind of quantity a control variable carries.
    """
    scalar = "scalar"
    """
    Single numeric value.
    """
    binary = "binary"
    """
    Two-state value.
    """
    state = "state"
    """
    Enumerated state, mapped through ``states``.
    """
    string = "string"
    """
    Textual value.
    """
    waveform = "waveform"
    """
    Array-valued trace.
    """
    statistical = "statistical"
    """
    Value with associated statistics (the default).
    """


class ApertureShapeEnum(str, Enum):
    """
    Cross-sectional shape of a beam-pipe aperture.
    """
    circular = "circular"
    rectangular = "rectangular"
    elliptical = "elliptical"


class BendingPlaneEnum(str, Enum):
    """
    Bending plane enum.
    """
    Horizontal = "Horizontal"
    """
    Horizontal bending plane.
    """
    Vertical = "Vertical"
    """
    Vertical bending plane.
    """
    Combined = "Combined"
    """
    Combined Horizontal and Vertical bending plane.
    """


class HardwareClassEnum(str, Enum):
    """
    High-level category organising elements by function within the accelerator.  Corresponds to the YAML ``hardware_class`` field.
    """
    Magnet = "Magnet"
    """
    Magnetic focusing or bending element.
    """
    Diagnostic = "Diagnostic"
    """
    Beam-diagnostic instrument.
    """
    RF = "RF"
    """
    Radio-frequency accelerating or deflecting structure.
    """
    Vacuum = "Vacuum"
    """
    Vacuum instrumentation (gauges, valves).
    """
    Laser = "Laser"
    """
    Laser optical element or complete laser system.
    """
    Plasma = "Plasma"
    """
    Plasma-based accelerating stage.
    """
    Feedback = "Feedback"
    """
    Control-system feedback element.
    """
    Marker = "Marker"
    """
    Virtual survey marker with no physical aperture.
    """
    Aperture = "Aperture"
    """
    Mechanical aperture or collimator.
    """
    Stage = "Stage"
    """
    Motorised positioning stage.
    """
    Lighting = "Lighting"
    """
    Experimental-hall lighting element.
    """
    Shutter = "Shutter"
    """
    Beam or laser shutter.
    """
    Wakefield = "Wakefield"
    """
    Passive wakefield structure.
    """
    TwissMatch = "TwissMatch"
    """
    Virtual Twiss-parameter matching point.
    """
    Drift = "Drift"
    """
    Drift element.
    """
    Generic = "Generic"
    """
    Generic element.
    """
    Monitor = "Monitor"
    """
    Beam monitor element.
    """
    Simulation = "Simulation"
    """
    Simulation element.
    """


class LaserPolarizationEnum(str, Enum):
    """
    Polarization state of a laser beam.
    """
    linear = "linear"
    circular = "circular"
    elliptical = "elliptical"


class LaserProfileTypeEnum(str, Enum):
    """
    Transverse intensity profile model for a laser beam.
    """
    gaussian = "gaussian"
    laguerre_gaussian = "laguerre-gaussian"
    flattened_gaussian = "flattened-gaussian"
    file = "file"



class _PositionBase(ConfiguredBaseModel):
    """
    Cartesian position in the global accelerator coordinate system. All components are in metres.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:Position',
         'from_schema': 'https://w3id.org/laura/schema/geometry',
         'in_subset': ['physical_properties']})

    x: float = Field(default=0, description="""Horizontal component [m].""", validation_alias=AliasChoices('x', 'X_POS'), json_schema_extra = { "linkml_meta": {'domain_of': ['Position',
                       'CameraPixelResultsIndices',
                       'CameraPixelResultsNames'],
         'ifabsent': 'float(0)',
         'unit': {'ucum_code': 'm'}} })
    """Horizontal component [m]."""
    y: float = Field(default=0, description="""Vertical component [m].""", validation_alias=AliasChoices('y', 'Y_POS'), json_schema_extra = { "linkml_meta": {'domain_of': ['Position',
                       'CameraPixelResultsIndices',
                       'CameraPixelResultsNames'],
         'ifabsent': 'float(0)',
         'unit': {'ucum_code': 'm'}} })
    """Vertical component [m]."""
    z: float = Field(default=0, description="""Longitudinal (beam-direction) component [m].""", json_schema_extra = { "linkml_meta": {'domain_of': ['Position'], 'ifabsent': 'float(0)', 'unit': {'ucum_code': 'm'}} })
    """Longitudinal (beam-direction) component [m]."""


class _RotationBase(ConfiguredBaseModel):
    """
    Euler-angle rotation relative to the global coordinate system. All angles are in radians, bounded to [-pi, pi].
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:Rotation',
         'from_schema': 'https://w3id.org/laura/schema/geometry',
         'in_subset': ['physical_properties']})

    phi: float = Field(default=0, description="""Rotation about the horizontal (x) axis [rad].""", ge=-3.141592653589793, le=3.141592653589793, json_schema_extra = { "linkml_meta": {'domain_of': ['Rotation'],
         'ifabsent': 'float(0)',
         'unit': {'ucum_code': 'rad'}} })
    """Rotation about the horizontal (x) axis [rad]."""
    psi: float = Field(default=0, description="""Rotation about the vertical (y) axis [rad].""", ge=-3.141592653589793, le=3.141592653589793, json_schema_extra = { "linkml_meta": {'domain_of': ['Rotation'],
         'ifabsent': 'float(0)',
         'unit': {'ucum_code': 'rad'}} })
    """Rotation about the vertical (y) axis [rad]."""
    theta: float = Field(default=0, description="""Rotation about the longitudinal (z) axis [rad].""", ge=-3.141592653589793, le=3.141592653589793, json_schema_extra = { "linkml_meta": {'domain_of': ['Rotation'],
         'ifabsent': 'float(0)',
         'unit': {'ucum_code': 'rad'}} })
    """Rotation about the longitudinal (z) axis [rad]."""


class _ElementPositionErrorBase(ConfiguredBaseModel):
    """
    Alignment position and rotation errors for a physically-located element.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:ElementPositionError',
         'from_schema': 'https://w3id.org/laura/schema/geometry'})

    position: Optional[_PositionBase] = Field(default=None, description="""Positional misalignment error [m].""", json_schema_extra = { "linkml_meta": {'domain_of': ['ElementPositionError', 'ElementSurvey']} })
    """Positional misalignment error [m]."""
    rotation: Optional[_RotationBase] = Field(default=None, description="""Angular misalignment error [rad].""", json_schema_extra = { "linkml_meta": {'domain_of': ['ElementPositionError',
                       'ElementSurvey',
                       'PhysicalElement',
                       'CameraDiagnosticElement']} })
    """Angular misalignment error [rad]."""


class _ElementSurveyBase(ConfiguredBaseModel):
    """
    Survey-measured position and rotation of an element. Structure is identical to ElementPositionError.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:ElementSurvey',
         'from_schema': 'https://w3id.org/laura/schema/geometry'})

    position: Optional[_PositionBase] = Field(default=None, description="""Surveyed position.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ElementPositionError', 'ElementSurvey']} })
    """Surveyed position."""
    rotation: Optional[_RotationBase] = Field(default=None, description="""Surveyed rotation.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ElementPositionError',
                       'ElementSurvey',
                       'PhysicalElement',
                       'CameraDiagnosticElement']} })
    """Surveyed rotation."""


class _ReferencePlacementBase(ConfiguredBaseModel):
    """
    Positions an element relative to a named reference element's local frame. The ``offset`` field is expressed in the reference element's local frame at the chosen ``point`` (start / middle / end).  Use ``world_offset`` instead to supply an offset already in global world coordinates.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:ReferencePlacement',
         'from_schema': 'https://w3id.org/laura/schema/geometry',
         'in_subset': ['physical_properties']})

    element: str = Field(default=..., description="""Name of the reference element.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ReferencePlacement']} })
    """Name of the reference element."""
    point: str = Field(default="end", description="""Which point on the reference element to use as the origin frame: 'start', 'middle', or 'end'.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ReferencePlacement'], 'ifabsent': 'string(end)'} })
    """Which point on the reference element to use as the origin frame: 'start', 'middle', or 'end'."""
    offset: Optional[_PositionBase] = Field(default=None, description="""Offset expressed in the reference element's local frame at the chosen point.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ReferencePlacement']} })
    """Offset expressed in the reference element's local frame at the chosen point."""
    world_offset: Optional[_PositionBase] = Field(default=None, description="""Offset already expressed in global world coordinates.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ReferencePlacement']} })
    """Offset already expressed in global world coordinates."""
    s_offset: Optional[float] = Field(default=None, description="""Scalar offset [m] along the local beam direction (s-axis) from the reference point.  Equivalent to ``offset: [0, 0, s_offset]`` but expressed as a single number.  Mutually exclusive with ``offset`` and ``world_offset``.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ReferencePlacement'], 'unit': {'ucum_code': 'm'}} })
    """Scalar offset [m] along the local beam direction (s-axis) from the reference point.  Equivalent to ``offset: [0, 0, s_offset]`` but expressed as a single number.  Mutually exclusive with ``offset`` and ``world_offset``."""


class _PhysicalElementBase(ConfiguredBaseModel):
    """
    Physical placement data: position, rotation, length, and associated survey / alignment-error information.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:PhysicalElement',
         'from_schema': 'https://w3id.org/laura/schema/geometry',
         'in_subset': ['physical_properties']})

    middle: Optional[_PositionBase] = Field(default=None, description="""Longitudinal midpoint (centre) of the element. Also accepted as ``position`` or ``centre`` in YAML.""", validation_alias=AliasChoices('middle', 'position', 'centre'), json_schema_extra = { "linkml_meta": {'aliases': ['position', 'centre'],
         'domain_of': ['PhysicalElement', 'CameraMask', 'CameraSensor']} })
    """Longitudinal midpoint (centre) of the element. Also accepted as ``position`` or ``centre`` in YAML."""
    datum: Optional[_PositionBase] = Field(default=None, description="""Datum reference position.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PhysicalElement']} })
    """Datum reference position."""
    rotation: Optional[_RotationBase] = Field(default=None, description="""Local rotation in the global frame.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ElementPositionError',
                       'ElementSurvey',
                       'PhysicalElement',
                       'CameraDiagnosticElement']} })
    """Local rotation in the global frame."""
    global_rotation: Optional[_RotationBase] = Field(default=None, description="""Accumulated global rotation including parent-frame contributions.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PhysicalElement']} })
    """Accumulated global rotation including parent-frame contributions."""
    error: Optional[_ElementPositionErrorBase] = Field(default=None, description="""Alignment errors.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PhysicalElement']} })
    """Alignment errors."""
    survey: Optional[_ElementSurveyBase] = Field(default=None, description="""Survey-measured position and rotation.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PhysicalElement']} })
    """Survey-measured position and rotation."""
    length: float = Field(default=0, description="""Effective length along the beam axis [m].""", ge=0.0, validation_alias=AliasChoices('length', 'magnetic_length'), json_schema_extra = { "linkml_meta": {'domain_of': ['PhysicalElement',
                       'MagneticElement',
                       'Solenoid_Magnet',
                       'Wiggler_Magnet',
                       'NonLinearLens_Magnet'],
         'ifabsent': 'float(0)',
         'unit': {'ucum_code': 'm'}} })
    """Effective length along the beam axis [m]."""
    physical_angle: float = Field(default=0, description="""Bending angle in the horizontal plane [rad]. Derived from ``magnetic.angle`` when available.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PhysicalElement'],
         'ifabsent': 'float(0)',
         'unit': {'ucum_code': 'rad'}} })
    """Bending angle in the horizontal plane [rad]. Derived from ``magnetic.angle`` when available."""
    reference_placement: Optional[_ReferencePlacementBase] = Field(default=None, description="""Place this element relative to another element's frame instead of using absolute world coordinates.  Mutually exclusive with ``middle``/``position``/``centre`` and ``s``.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PhysicalElement'], 'in_subset': ['physical_properties']} })
    """Place this element relative to another element's frame instead of using absolute world coordinates.  Mutually exclusive with ``middle``/``position``/``centre`` and ``s``."""
    s: Optional[float] = Field(default=None, description="""Arc-length position [m] along the design trajectory (s=0 at the global origin along +Z).  Alternative to absolute world coordinates (``middle``/``position``/``centre``) and ``reference_placement``. Converted to {x,y,z} by LAURA during lattice assembly.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PhysicalElement'], 'unit': {'ucum_code': 'm'}} })
    """Arc-length position [m] along the design trajectory (s=0 at the global origin along +Z).  Alternative to absolute world coordinates (``middle``/``position``/``centre``) and ``reference_placement``. Converted to {x,y,z} by LAURA during lattice assembly."""
    s_point: str = Field(default="middle", description="""Which point of the element the ``s`` value refers to: ``start``, ``middle``, or ``end``.  Defaults to ``middle``.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PhysicalElement'], 'ifabsent': 'string(middle)'} })
    """Which point of the element the ``s`` value refers to: ``start``, ``middle``, or ``end``.  Defaults to ``middle``."""


class _ControlVariableBase(ConfiguredBaseModel):
    """
    A single process-variable entry mapping a logical name to a control-system PV identifier.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:ControlVariable',
         'from_schema': 'https://w3id.org/laura/schema/controls'})

    identifier: Optional[str] = Field(default=None, description="""Protocol-specific PV name (e.g., EPICS PV address).""", json_schema_extra = { "linkml_meta": {'domain_of': ['ControlVariable']} })
    """Protocol-specific PV name (e.g., EPICS PV address)."""
    dtype: str = Field(default="float", description="""Data type, held as a Python type and serialised by name (e.g., ``float``, ``int``, ``str``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['ControlVariable'], 'ifabsent': 'string(float)'} })
    """Data type, held as a Python type and serialised by name (e.g., ``float``, ``int``, ``str``)."""
    protocol: Optional[str] = Field(default=None, description="""Control-system protocol (e.g., ``EPICS``, ``Tango``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['ControlVariable']} })
    """Control-system protocol (e.g., ``EPICS``, ``Tango``)."""
    units: str = Field(default="Arb. Units", description="""Physical units string (e.g., ``A``, ``T/m``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['ControlVariable'], 'ifabsent': 'string(Arb. Units)'} })
    """Physical units string (e.g., ``A``, ``T/m``)."""
    description: str = Field(default="Default Description", description="""Human-readable description.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ControlVariable'], 'ifabsent': 'string(Default Description)'} })
    """Human-readable description."""
    read_only: Optional[bool] = Field(default=True, description="""Whether the variable is read-only.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ControlVariable'], 'ifabsent': 'True'} })
    """Whether the variable is read-only."""
    value: Optional[Union[float, int, str]] = Field(default=None, description="""Last-read value. Scalar for most control types; a list for ``waveform``.""", json_schema_extra = { "linkml_meta": {'any_of': [{'range': 'float'}, {'range': 'integer'}, {'range': 'string'}],
         'domain_of': ['ControlVariable']} })
    """Last-read value. Scalar for most control types; a list for ``waveform``."""
    control_type: Optional[ControlTypeEnum] = Field(default=ControlTypeEnum.statistical, description="""Kind of quantity this variable carries. Accepted in YAML as ``type``.""", validation_alias=AliasChoices('control_type', 'type'), json_schema_extra = { "linkml_meta": {'aliases': ['type'],
         'domain_of': ['ControlVariable'],
         'ifabsent': 'string(statistical)'} })
    """Kind of quantity this variable carries. Accepted in YAML as ``type``."""
    target: Optional[str] = Field(default=None, description="""Dotted attribute path on the owning element that ``expression`` writes to (e.g., ``magnetic.k1l``). Not a set-point value.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ControlVariable']} })
    """Dotted attribute path on the owning element that ``expression`` writes to (e.g., ``magnetic.k1l``). Not a set-point value."""
    expression: Optional[str] = Field(default=None, description="""Expression graph computing the value written to ``target``, as nested mappings of the form ``{op: mul, args: [<symbol>, <symbol>]}``, where a symbol is a variable name or a dotted attribute path. Operators are ``add``, ``sub``, ``mul``, ``truediv`` and ``pow``.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ControlVariable']} })
    """Expression graph computing the value written to ``target``, as nested mappings of the form ``{op: mul, args: [<symbol>, <symbol>]}``, where a symbol is a variable name or a dotted attribute path. Operators are ``add``, ``sub``, ``mul``, ``truediv`` and ``pow``."""
    states: Optional[str] = Field(default=None, description="""Mapping of state name to underlying control-system value, for ``control_type: state``.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ControlVariable']} })
    """Mapping of state name to underlying control-system value, for ``control_type: state``."""
    readback: Optional[str] = Field(default=None, description="""Name of the readback variable this set-point drives.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ControlVariable']} })
    """Name of the readback variable this set-point drives."""
    setpoint: Optional[str] = Field(default=None, description="""Name of the set-point variable this readback follows.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ControlVariable']} })
    """Name of the set-point variable this readback follows."""
    update: Optional[str] = Field(default=None, description="""Signal generating this variable's value over time, as ``{function: <import path>, **kwargs}`` -- see ``laura.utils.signals``. Stored with ``function`` as a fully qualified import path so it resolves without LAURA.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ControlVariable']} })
    """Signal generating this variable's value over time, as ``{function: <import path>, **kwargs}`` -- see ``laura.utils.signals``. Stored with ``function`` as a fully qualified import path so it resolves without LAURA."""
    dynamics: Optional[str] = Field(default=None, description="""Response model describing how this variable's readback follows its set-point, as ``{model: <import path>, **kwargs}`` -- see ``laura.utils.dynamics``. Only meaningful alongside ``readback`` or ``setpoint``.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ControlVariable']} })
    """Response model describing how this variable's readback follows its set-point, as ``{model: <import path>, **kwargs}`` -- see ``laura.utils.dynamics``. Only meaningful alongside ``readback`` or ``setpoint``."""


class _ControlsInformationBase(ConfiguredBaseModel):
    """
    Collection of process-variable definitions for an element's control interface.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:ControlsInformation',
         'from_schema': 'https://w3id.org/laura/schema/controls'})

    variables: dict[str, _ControlVariableBase] = Field(default_factory=dict, description="""Named control variables keyed by logical name.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ControlsInformation']} })
    """Named control variables keyed by logical name."""


class _ShutterElementBase(ConfiguredBaseModel):
    """
    Shutter interlock configuration.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:ShutterElement',
         'from_schema': 'https://w3id.org/laura/schema/elements'})

    interlocks: list[str] = Field(default_factory=list, description="""Names of the interlocks guarding this shutter.""", validation_alias=AliasChoices('interlocks', 'shutter_interlock_names'), json_schema_extra = { "linkml_meta": {'aliases': ['shutter_interlock_names'], 'domain_of': ['ShutterElement']} })
    """Names of the interlocks guarding this shutter."""


class _ValveElementBase(ConfiguredBaseModel):
    """
    Vacuum valve configuration (no additional fields).
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:ValveElement',
         'from_schema': 'https://w3id.org/laura/schema/elements'})

    pass


class _LightingElementBase(ConfiguredBaseModel):
    """
    Lighting element (no additional fields currently defined).
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:LightingElement',
         'from_schema': 'https://w3id.org/laura/schema/elements'})

    pass


class _ApertureElementBase(ConfiguredBaseModel):
    """
    Transverse aperture geometry for drift-space checks and collimators.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:ApertureElement',
         'from_schema': 'https://w3id.org/laura/schema/elements'})

    number_of_elements: int = Field(default=0, description="""Number of aperture sub-elements (e.g., for multi-leaf collimators).""", ge=0, json_schema_extra = { "linkml_meta": {'domain_of': ['ApertureElement'], 'ifabsent': 'int(0)'} })
    """Number of aperture sub-elements (e.g., for multi-leaf collimators)."""
    horizontal_size: float = Field(default=0.0, description="""Full horizontal aperture [m].""", ge=0.0, json_schema_extra = { "linkml_meta": {'domain_of': ['ApertureElement'],
         'ifabsent': 'float(0.0)',
         'unit': {'ucum_code': 'm'}} })
    """Full horizontal aperture [m]."""
    vertical_size: float = Field(default=0.0, description="""Full vertical aperture [m].""", ge=0.0, json_schema_extra = { "linkml_meta": {'domain_of': ['ApertureElement'],
         'ifabsent': 'float(0.0)',
         'unit': {'ucum_code': 'm'}} })
    """Full vertical aperture [m]."""
    shape: Optional[ApertureShapeEnum] = Field(default=None, description="""Cross-sectional aperture shape.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ApertureElement']} })
    """Cross-sectional aperture shape."""
    radius: Optional[float] = Field(default=None, description="""Radius for circular apertures [m].""", ge=0.0, json_schema_extra = { "linkml_meta": {'domain_of': ['ApertureElement', 'Multipole', 'CameraMask'],
         'unit': {'ucum_code': 'm'}} })
    """Radius for circular apertures [m]."""
    negative_extent: Optional[float] = Field(default=None, description="""Upstream / inner extent [m].""", json_schema_extra = { "linkml_meta": {'domain_of': ['ApertureElement'], 'unit': {'ucum_code': 'm'}} })
    """Upstream / inner extent [m]."""
    positive_extent: Optional[float] = Field(default=None, description="""Downstream / outer extent [m].""", json_schema_extra = { "linkml_meta": {'domain_of': ['ApertureElement'], 'unit': {'ucum_code': 'm'}} })
    """Downstream / outer extent [m]."""


class _SectionLatticeBase(ConfiguredBaseModel):
    """
    An ordered list of element names defining a contiguous beamline section.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:SectionLattice',
         'from_schema': 'https://w3id.org/laura/schema/machine'})

    name: str = Field(default=..., description="""Unique section name.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SectionLattice', 'MachineLayout', 'AcceleratorElement']} })
    """Unique section name."""
    master_lattice: Optional[str] = Field(default=None, description="""Name of the master lattice this section belongs to.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SectionLattice', 'MachineLayout']} })
    """Name of the master lattice this section belongs to."""
    elements: list[str] = Field(default_factory=list, description="""Ordered list of element names in this section.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SectionLattice', 'MachineModel']} })
    """Ordered list of element names in this section."""


class _MachineLayoutBase(ConfiguredBaseModel):
    """
    An ordered list of section names defining a beamline layout (a contiguous sequence of sections).
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:MachineLayout',
         'from_schema': 'https://w3id.org/laura/schema/machine'})

    name: str = Field(default=..., description="""Unique layout name.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SectionLattice', 'MachineLayout', 'AcceleratorElement']} })
    """Unique layout name."""
    master_lattice: Optional[str] = Field(default=None, description="""Name of the master lattice this layout belongs to.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SectionLattice', 'MachineLayout']} })
    """Name of the master lattice this layout belongs to."""
    sections: list[str] = Field(default_factory=list, description="""Ordered list of section names.""", json_schema_extra = { "linkml_meta": {'domain_of': ['MachineLayout', 'MachineModel']} })
    """Ordered list of section names."""


class _MachineModelBase(ConfiguredBaseModel):
    """
    Top-level container for a complete accelerator lattice: elements, sections, layouts, and named lattice configurations.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:MachineModel',
         'from_schema': 'https://w3id.org/laura/schema/machine'})

    elements: list[str] = Field(default_factory=list, description="""All elements in the machine, keyed by name.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SectionLattice', 'MachineModel']} })
    """All elements in the machine, keyed by name."""
    sections: list[str] = Field(default_factory=list, description="""All named beamline sections.""", json_schema_extra = { "linkml_meta": {'domain_of': ['MachineLayout', 'MachineModel']} })
    """All named beamline sections."""
    layouts: list[str] = Field(default_factory=list, description="""All named beamline layouts.""", json_schema_extra = { "linkml_meta": {'domain_of': ['MachineModel']} })
    """All named beamline layouts."""


class _SimulationElementBase(ConfiguredBaseModel):
    """
    Base simulation attributes: field-map files and reference positions for tracking codes.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:SimulationElement',
         'from_schema': 'https://w3id.org/laura/schema/simulation'})

    field_definition: Optional[str] = Field(default=None, description="""Path to the 3-D field-map file.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SimulationElement']} })
    """Path to the 3-D field-map file."""
    wakefield_definition: Optional[str] = Field(default=None, description="""Path to the wakefield impedance file.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SimulationElement']} })
    """Path to the wakefield impedance file."""
    wakefield_enable: Optional[bool] = Field(default=True, description="""Whether the wakefield named by wakefield_definition is applied. Set false to track the element without its wakefield while keeping the definition itself.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SimulationElement'], 'ifabsent': 'true'} })
    """Whether the wakefield named by wakefield_definition is applied. Set false to track the element without its wakefield while keeping the definition itself."""
    field_reference_position: Optional[str] = Field(default=None, description="""Longitudinal origin of the field map [m].""", json_schema_extra = { "linkml_meta": {'domain_of': ['SimulationElement']} })
    """Longitudinal origin of the field map [m]."""
    scale_field: float = Field(default=1, description="""Multiplicative scale factor applied to the field map.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SimulationElement'], 'ifabsent': 'float(1)'} })
    """Multiplicative scale factor applied to the field map."""


class _MagnetSimulationElementBase(_SimulationElementBase):
    """
    Simulation attributes specific to magnets: integrator settings, fringe-field model, and radiation flags.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:MagnetSimulationElement',
         'from_schema': 'https://w3id.org/laura/schema/simulation',
         'slot_usage': {'field_amplitude': {'description': 'Field amplitude scaling '
                                                           'for magnet tracking.',
                                            'ifabsent': 'float(0.0)',
                                            'name': 'field_amplitude'},
                        'n_kicks': {'description': 'Number of integration kicks.',
                                    'ifabsent': 'int(4)',
                                    'minimum_value': 1,
                                    'name': 'n_kicks'}}})

    n_kicks: Optional[int] = Field(default=4, description="""Number of integration kicks.""", ge=1, json_schema_extra = { "linkml_meta": {'domain_of': ['MagnetSimulationElement', 'RFCavitySimulationElement'],
         'ifabsent': 'int(4)'} })
    """Number of integration kicks."""
    field_amplitude: Optional[Union[float, str]] = Field(default=0.0, description="""Field amplitude scaling for magnet tracking.""", json_schema_extra = { "linkml_meta": {'any_of': [{'range': 'float'}, {'range': 'string'}],
         'domain_of': ['MagnetSimulationElement',
                       'RFCavitySimulationElement',
                       'ACDipoleSimulationElement',
                       'RFMultipoleSimulationElement'],
         'ifabsent': 'float(0.0)',
         'in_subset': ['functional_parameters']} })
    """Field amplitude scaling for magnet tracking."""
    n_slices: int = Field(default=4, description="""Number of longitudinal slices for thick-lens tracking.""", ge=1, json_schema_extra = { "linkml_meta": {'domain_of': ['MagnetSimulationElement'], 'ifabsent': 'int(4)'} })
    """Number of longitudinal slices for thick-lens tracking."""
    smooth: Optional[int] = Field(default=None, description="""Number of smoothing passes applied to the field map (ASTRA Q_smooth / S_smooth).""", json_schema_extra = { "linkml_meta": {'domain_of': ['MagnetSimulationElement',
                       'RFCavitySimulationElement',
                       'WakefieldSimulationElement']} })
    """Number of smoothing passes applied to the field map (ASTRA Q_smooth / S_smooth)."""
    edge_field_integral: float = Field(default=0.5, description="""Fringe-field integral for edge focussing.""", json_schema_extra = { "linkml_meta": {'domain_of': ['MagnetSimulationElement', 'MagneticElement'],
         'ifabsent': 'float(0.5)'} })
    """Fringe-field integral for edge focussing."""
    edge1_effects: Optional[bool] = Field(default=None, description="""Enable entrance-edge focussing effects.""", json_schema_extra = { "linkml_meta": {'domain_of': ['MagnetSimulationElement']} })
    """Enable entrance-edge focussing effects."""
    edge2_effects: Optional[bool] = Field(default=None, description="""Enable exit-edge focussing effects.""", json_schema_extra = { "linkml_meta": {'domain_of': ['MagnetSimulationElement']} })
    """Enable exit-edge focussing effects."""
    sr_enable: Optional[bool] = Field(default=True, description="""Enable synchrotron-radiation energy loss.""", json_schema_extra = { "linkml_meta": {'domain_of': ['MagnetSimulationElement'], 'ifabsent': 'True'} })
    """Enable synchrotron-radiation energy loss."""
    isr_enable: Optional[bool] = Field(default=True, description="""Enable incoherent synchrotron-radiation emittance growth.""", json_schema_extra = { "linkml_meta": {'domain_of': ['MagnetSimulationElement'], 'ifabsent': 'True'} })
    """Enable incoherent synchrotron-radiation emittance growth."""
    csr_enable: Optional[bool] = Field(default=True, description="""Enable coherent synchrotron radiation.""", json_schema_extra = { "linkml_meta": {'domain_of': ['MagnetSimulationElement', 'DriftSimulationElement'],
         'ifabsent': 'True'} })
    """Enable coherent synchrotron radiation."""
    csr_bins: int = Field(default=100, description="""Number of longitudinal bins for the CSR mesh.""", json_schema_extra = { "linkml_meta": {'domain_of': ['MagnetSimulationElement'], 'ifabsent': 'int(100)'} })
    """Number of longitudinal bins for the CSR mesh."""
    integration_order: int = Field(default=4, description="""Order of the symplectic integrator.""", json_schema_extra = { "linkml_meta": {'domain_of': ['MagnetSimulationElement'], 'ifabsent': 'int(4)'} })
    """Order of the symplectic integrator."""
    nonlinear: Optional[bool] = Field(default=None, description="""Include higher-order (sextupole+) field components.""", json_schema_extra = { "linkml_meta": {'domain_of': ['MagnetSimulationElement']} })
    """Include higher-order (sextupole+) field components."""
    smoothing_half_width: int = Field(default=1, description="""Half-width of the current-profile smoothing kernel.""", json_schema_extra = { "linkml_meta": {'domain_of': ['MagnetSimulationElement'], 'ifabsent': 'int(1)'} })
    """Half-width of the current-profile smoothing kernel."""
    edge_order: int = Field(default=2, description="""Polynomial order of the edge-field expansion.""", json_schema_extra = { "linkml_meta": {'domain_of': ['MagnetSimulationElement'], 'ifabsent': 'int(2)'} })
    """Polynomial order of the edge-field expansion."""
    deltaL: float = Field(default=0.0, description="""Longitudinal step-size override for thick-lens integration [m].""", json_schema_extra = { "linkml_meta": {'domain_of': ['MagnetSimulationElement'],
         'ifabsent': 'float(0.0)',
         'unit': {'ucum_code': 'm'}} })
    """Longitudinal step-size override for thick-lens integration [m]."""
    smooth_points: float = Field(default=2, description="""Number of points used to smooth the field map [ASTRA].""", json_schema_extra = { "linkml_meta": {'domain_of': ['MagnetSimulationElement'], 'ifabsent': 'float(2)'} })
    """Number of points used to smooth the field map [ASTRA]."""
    field_definition: Optional[str] = Field(default=None, description="""Path to the 3-D field-map file.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SimulationElement']} })
    """Path to the 3-D field-map file."""
    wakefield_definition: Optional[str] = Field(default=None, description="""Path to the wakefield impedance file.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SimulationElement']} })
    """Path to the wakefield impedance file."""
    wakefield_enable: Optional[bool] = Field(default=True, description="""Whether the wakefield named by wakefield_definition is applied. Set false to track the element without its wakefield while keeping the definition itself.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SimulationElement'], 'ifabsent': 'true'} })
    """Whether the wakefield named by wakefield_definition is applied. Set false to track the element without its wakefield while keeping the definition itself."""
    field_reference_position: Optional[str] = Field(default=None, description="""Longitudinal origin of the field map [m].""", json_schema_extra = { "linkml_meta": {'domain_of': ['SimulationElement']} })
    """Longitudinal origin of the field map [m]."""
    scale_field: float = Field(default=1, description="""Multiplicative scale factor applied to the field map.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SimulationElement'], 'ifabsent': 'float(1)'} })
    """Multiplicative scale factor applied to the field map."""


class _RFCavitySimulationElementBase(_SimulationElementBase):
    """
    Simulation attributes for RF cavity elements.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:RFCavitySimulationElement',
         'from_schema': 'https://w3id.org/laura/schema/simulation',
         'slot_usage': {'lsc_bins': {'description': 'Number of longitudinal '
                                                    'space-charge bins.',
                                     'ifabsent': 'int(100)',
                                     'name': 'lsc_bins'},
                        'n_kicks': {'description': 'Number of cavity kicks to apply.',
                                    'ifabsent': 'int(0)',
                                    'name': 'n_kicks'}}})

    t_column: Optional[str] = Field(default=None, description="""Time column in the wake file.""", json_schema_extra = { "linkml_meta": {'domain_of': ['RFCavitySimulationElement', 'WakefieldSimulationElement']} })
    """Time column in the wake file."""
    z_column: Optional[str] = Field(default=None, description="""Longitudinal position column in the wake file.""", json_schema_extra = { "linkml_meta": {'domain_of': ['RFCavitySimulationElement', 'WakefieldSimulationElement']} })
    """Longitudinal position column in the wake file."""
    wx_column: Optional[str] = Field(default=None, description="""Horizontal wake column in the wake file.""", json_schema_extra = { "linkml_meta": {'domain_of': ['RFCavitySimulationElement', 'WakefieldSimulationElement']} })
    """Horizontal wake column in the wake file."""
    wy_column: Optional[str] = Field(default=None, description="""Vertical wake column in the wake file.""", json_schema_extra = { "linkml_meta": {'domain_of': ['RFCavitySimulationElement', 'WakefieldSimulationElement']} })
    """Vertical wake column in the wake file."""
    wz_column: Optional[str] = Field(default=None, description="""Longitudinal wake column in the wake file.""", json_schema_extra = { "linkml_meta": {'domain_of': ['RFCavitySimulationElement', 'WakefieldSimulationElement']} })
    """Longitudinal wake column in the wake file."""
    n_kicks: Optional[int] = Field(default=0, description="""Number of cavity kicks to apply.""", json_schema_extra = { "linkml_meta": {'domain_of': ['MagnetSimulationElement', 'RFCavitySimulationElement'],
         'ifabsent': 'int(0)'} })
    """Number of cavity kicks to apply."""
    lsc_bins: Optional[int] = Field(default=100, description="""Number of longitudinal space-charge bins.""", json_schema_extra = { "linkml_meta": {'domain_of': ['RFCavitySimulationElement', 'DriftSimulationElement'],
         'ifabsent': 'int(100)'} })
    """Number of longitudinal space-charge bins."""
    change_p0: int = Field(default=1, description="""Flag indicating whether the cavity changes reference momentum.""", json_schema_extra = { "linkml_meta": {'domain_of': ['RFCavitySimulationElement'], 'ifabsent': 'int(1)'} })
    """Flag indicating whether the cavity changes reference momentum."""
    end1_focus: int = Field(default=1, description="""Apply entrance focusing.""", json_schema_extra = { "linkml_meta": {'domain_of': ['RFCavitySimulationElement'], 'ifabsent': 'int(1)'} })
    """Apply entrance focusing."""
    end2_focus: int = Field(default=1, description="""Apply exit focusing.""", json_schema_extra = { "linkml_meta": {'domain_of': ['RFCavitySimulationElement'], 'ifabsent': 'int(1)'} })
    """Apply exit focusing."""
    body_focus_model: str = Field(default="SRS", description="""Cavity body focusing model.""", json_schema_extra = { "linkml_meta": {'domain_of': ['RFCavitySimulationElement'], 'ifabsent': 'string(SRS)'} })
    """Cavity body focusing model."""
    current_bins: int = Field(default=0, description="""Number of current bins.""", json_schema_extra = { "linkml_meta": {'domain_of': ['RFCavitySimulationElement'], 'ifabsent': 'int(0)'} })
    """Number of current bins."""
    interpolate_current_bins: int = Field(default=1, description="""Flag indicating current-bin interpolation.""", json_schema_extra = { "linkml_meta": {'domain_of': ['RFCavitySimulationElement'], 'ifabsent': 'int(1)'} })
    """Flag indicating current-bin interpolation."""
    smooth_current_bins: int = Field(default=1, description="""Flag indicating current-bin smoothing.""", json_schema_extra = { "linkml_meta": {'domain_of': ['RFCavitySimulationElement'], 'ifabsent': 'int(1)'} })
    """Flag indicating current-bin smoothing."""
    smooth: Optional[int] = Field(default=None, description="""Cavity smoothing parameter.""", json_schema_extra = { "linkml_meta": {'domain_of': ['MagnetSimulationElement',
                       'RFCavitySimulationElement',
                       'WakefieldSimulationElement']} })
    """Cavity smoothing parameter."""
    ez_peak: Optional[float] = Field(default=None, description="""Peak longitudinal electric field.""", json_schema_extra = { "linkml_meta": {'domain_of': ['RFCavitySimulationElement']} })
    """Peak longitudinal electric field."""
    field_file_name: Optional[str] = Field(default=None, description="""Cavity field file name.""", json_schema_extra = { "linkml_meta": {'domain_of': ['RFCavitySimulationElement']} })
    """Cavity field file name."""
    wakefile: Optional[str] = Field(default=None, description="""Wake file name.""", json_schema_extra = { "linkml_meta": {'domain_of': ['RFCavitySimulationElement']} })
    """Wake file name."""
    zwakefile: Optional[str] = Field(default=None, description="""Longitudinal wake file name.""", json_schema_extra = { "linkml_meta": {'domain_of': ['RFCavitySimulationElement']} })
    """Longitudinal wake file name."""
    trwakefile: Optional[str] = Field(default=None, description="""Transverse wake file name.""", json_schema_extra = { "linkml_meta": {'domain_of': ['RFCavitySimulationElement']} })
    """Transverse wake file name."""
    field_amplitude: Union[float, str] = Field(default=..., description="""Cavity field amplitude.""", json_schema_extra = { "linkml_meta": {'any_of': [{'range': 'float'}, {'range': 'string'}],
         'domain_of': ['MagnetSimulationElement',
                       'RFCavitySimulationElement',
                       'ACDipoleSimulationElement',
                       'RFMultipoleSimulationElement'],
         'in_subset': ['functional_parameters']} })
    """Cavity field amplitude."""
    field_definition: Optional[str] = Field(default=None, description="""Path to the 3-D field-map file.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SimulationElement']} })
    """Path to the 3-D field-map file."""
    wakefield_definition: Optional[str] = Field(default=None, description="""Path to the wakefield impedance file.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SimulationElement']} })
    """Path to the wakefield impedance file."""
    wakefield_enable: Optional[bool] = Field(default=True, description="""Whether the wakefield named by wakefield_definition is applied. Set false to track the element without its wakefield while keeping the definition itself.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SimulationElement'], 'ifabsent': 'true'} })
    """Whether the wakefield named by wakefield_definition is applied. Set false to track the element without its wakefield while keeping the definition itself."""
    field_reference_position: Optional[str] = Field(default=None, description="""Longitudinal origin of the field map [m].""", json_schema_extra = { "linkml_meta": {'domain_of': ['SimulationElement']} })
    """Longitudinal origin of the field map [m]."""
    scale_field: float = Field(default=1, description="""Multiplicative scale factor applied to the field map.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SimulationElement'], 'ifabsent': 'float(1)'} })
    """Multiplicative scale factor applied to the field map."""


class _WakefieldSimulationElementBase(_SimulationElementBase):
    """
    Simulation attributes for passive wakefield structures.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:WakefieldSimulationElement',
         'from_schema': 'https://w3id.org/laura/schema/simulation'})

    t_column: Optional[str] = Field(default=None, description="""Time column in the wake file.""", json_schema_extra = { "linkml_meta": {'domain_of': ['RFCavitySimulationElement', 'WakefieldSimulationElement']} })
    """Time column in the wake file."""
    z_column: Optional[str] = Field(default=None, description="""Longitudinal position column in the wake file.""", json_schema_extra = { "linkml_meta": {'domain_of': ['RFCavitySimulationElement', 'WakefieldSimulationElement']} })
    """Longitudinal position column in the wake file."""
    wx_column: Optional[str] = Field(default=None, description="""Horizontal wake column in the wake file.""", json_schema_extra = { "linkml_meta": {'domain_of': ['RFCavitySimulationElement', 'WakefieldSimulationElement']} })
    """Horizontal wake column in the wake file."""
    wy_column: Optional[str] = Field(default=None, description="""Vertical wake column in the wake file.""", json_schema_extra = { "linkml_meta": {'domain_of': ['RFCavitySimulationElement', 'WakefieldSimulationElement']} })
    """Vertical wake column in the wake file."""
    wz_column: Optional[str] = Field(default=None, description="""Longitudinal wake column in the wake file.""", json_schema_extra = { "linkml_meta": {'domain_of': ['RFCavitySimulationElement', 'WakefieldSimulationElement']} })
    """Longitudinal wake column in the wake file."""
    allow_long_beam: Optional[bool] = Field(default=True, description="""Allow beams longer than the wakefield.""", json_schema_extra = { "linkml_meta": {'domain_of': ['WakefieldSimulationElement'], 'ifabsent': 'True'} })
    """Allow beams longer than the wakefield."""
    bunched_beam: Optional[bool] = Field(default=False, description="""Use bunched beam mode.""", json_schema_extra = { "linkml_meta": {'domain_of': ['WakefieldSimulationElement'], 'ifabsent': 'False'} })
    """Use bunched beam mode."""
    change_momentum: Optional[bool] = Field(default=True, description="""Allow wakefield to change bunch momentum.""", json_schema_extra = { "linkml_meta": {'domain_of': ['WakefieldSimulationElement'], 'ifabsent': 'True'} })
    """Allow wakefield to change bunch momentum."""
    factor: float = Field(default=1, description="""Wake scaling factor.""", json_schema_extra = { "linkml_meta": {'domain_of': ['WakefieldSimulationElement'], 'ifabsent': 'float(1)'} })
    """Wake scaling factor."""
    interpolate: Optional[bool] = Field(default=True, description="""Interpolate points in wake file.""", json_schema_extra = { "linkml_meta": {'domain_of': ['WakefieldSimulationElement'], 'ifabsent': 'True'} })
    """Interpolate points in wake file."""
    scale_kick: float = Field(default=1, description="""Factor by which to scale wake kicks.""", json_schema_extra = { "linkml_meta": {'domain_of': ['WakefieldSimulationElement'], 'ifabsent': 'float(1)'} })
    """Factor by which to scale wake kicks."""
    scale_field_ex: float = Field(default=0.0, description="""x-component of the longitudinal direction vector.""", json_schema_extra = { "linkml_meta": {'domain_of': ['WakefieldSimulationElement'], 'ifabsent': 'float(0.0)'} })
    """x-component of the longitudinal direction vector."""
    scale_field_ey: float = Field(default=0.0, description="""y-component of the longitudinal direction vector.""", json_schema_extra = { "linkml_meta": {'domain_of': ['WakefieldSimulationElement'], 'ifabsent': 'float(0.0)'} })
    """y-component of the longitudinal direction vector."""
    scale_field_ez: float = Field(default=1.0, description="""z-component of the longitudinal direction vector.""", json_schema_extra = { "linkml_meta": {'domain_of': ['WakefieldSimulationElement'], 'ifabsent': 'float(1.0)'} })
    """z-component of the longitudinal direction vector."""
    scale_field_hx: float = Field(default=1.0, description="""x-component of the horizontal direction vector.""", json_schema_extra = { "linkml_meta": {'domain_of': ['WakefieldSimulationElement'], 'ifabsent': 'float(1.0)'} })
    """x-component of the horizontal direction vector."""
    scale_field_hy: float = Field(default=0.0, description="""y-component of the horizontal direction vector.""", json_schema_extra = { "linkml_meta": {'domain_of': ['WakefieldSimulationElement'], 'ifabsent': 'float(0.0)'} })
    """y-component of the horizontal direction vector."""
    scale_field_hz: float = Field(default=0.0, description="""z-component of the horizontal direction vector.""", json_schema_extra = { "linkml_meta": {'domain_of': ['WakefieldSimulationElement'], 'ifabsent': 'float(0.0)'} })
    """z-component of the horizontal direction vector."""
    equal_grid: float = Field(default=0.66, description="""Interpolation between equidistant and equal-charge grids.""", json_schema_extra = { "linkml_meta": {'domain_of': ['WakefieldSimulationElement'], 'ifabsent': 'float(0.66)'} })
    """Interpolation between equidistant and equal-charge grids."""
    interpolation_method: int = Field(default=2, description="""Interpolation method for ASTRA.""", json_schema_extra = { "linkml_meta": {'domain_of': ['WakefieldSimulationElement'], 'ifabsent': 'int(2)'} })
    """Interpolation method for ASTRA."""
    smooth: float = Field(default=0.25, description="""Smoothing parameter for Gaussian interpolation.""", json_schema_extra = { "linkml_meta": {'domain_of': ['MagnetSimulationElement',
                       'RFCavitySimulationElement',
                       'WakefieldSimulationElement'],
         'ifabsent': 'float(0.25)'} })
    """Smoothing parameter for Gaussian interpolation."""
    subbins: int = Field(default=10, description="""Sub-binning parameter.""", json_schema_extra = { "linkml_meta": {'domain_of': ['WakefieldSimulationElement'], 'ifabsent': 'int(10)'} })
    """Sub-binning parameter."""
    field_definition: Optional[str] = Field(default=None, description="""Path to the 3-D field-map file.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SimulationElement']} })
    """Path to the 3-D field-map file."""
    wakefield_definition: Optional[str] = Field(default=None, description="""Path to the wakefield impedance file.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SimulationElement']} })
    """Path to the wakefield impedance file."""
    wakefield_enable: Optional[bool] = Field(default=True, description="""Whether the wakefield named by wakefield_definition is applied. Set false to track the element without its wakefield while keeping the definition itself.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SimulationElement'], 'ifabsent': 'true'} })
    """Whether the wakefield named by wakefield_definition is applied. Set false to track the element without its wakefield while keeping the definition itself."""
    field_reference_position: Optional[str] = Field(default=None, description="""Longitudinal origin of the field map [m].""", json_schema_extra = { "linkml_meta": {'domain_of': ['SimulationElement']} })
    """Longitudinal origin of the field map [m]."""
    scale_field: float = Field(default=1, description="""Multiplicative scale factor applied to the field map.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SimulationElement'], 'ifabsent': 'float(1)'} })
    """Multiplicative scale factor applied to the field map."""


class _DriftSimulationElementBase(_SimulationElementBase):
    """
    Simulation attributes for field-free drift sections.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:DriftSimulationElement',
         'from_schema': 'https://w3id.org/laura/schema/simulation',
         'slot_usage': {'lsc_bins': {'description': 'Number of bins for LSC '
                                                    'calculations.',
                                     'ifabsent': 'int(20)',
                                     'name': 'lsc_bins'}}})

    lsc_bins: Optional[int] = Field(default=20, description="""Number of bins for LSC calculations.""", json_schema_extra = { "linkml_meta": {'domain_of': ['RFCavitySimulationElement', 'DriftSimulationElement'],
         'ifabsent': 'int(20)'} })
    """Number of bins for LSC calculations."""
    lsc_interpolate: int = Field(default=1, description="""Flag to allow interpolation of computed LSC wake.""", json_schema_extra = { "linkml_meta": {'domain_of': ['DriftSimulationElement'], 'ifabsent': 'int(1)'} })
    """Flag to allow interpolation of computed LSC wake."""
    csr_enable: Optional[bool] = Field(default=True, description="""Enable CSR drift calculations.""", json_schema_extra = { "linkml_meta": {'domain_of': ['MagnetSimulationElement', 'DriftSimulationElement'],
         'ifabsent': 'True'} })
    """Enable CSR drift calculations."""
    lsc_enable: Optional[bool] = Field(default=True, description="""Enable LSC drift calculations.""", json_schema_extra = { "linkml_meta": {'domain_of': ['DriftSimulationElement'], 'ifabsent': 'True'} })
    """Enable LSC drift calculations."""
    use_stupakov: int = Field(default=1, description="""Use Stupakov formula.""", json_schema_extra = { "linkml_meta": {'domain_of': ['DriftSimulationElement'], 'ifabsent': 'int(1)'} })
    """Use Stupakov formula."""
    csrdz: float = Field(default=0.01, description="""Step size for CSR calculations.""", json_schema_extra = { "linkml_meta": {'domain_of': ['DriftSimulationElement'], 'ifabsent': 'float(0.01)'} })
    """Step size for CSR calculations."""
    lsc_high_frequency_cutoff_start: Optional[float] = Field(default=None, description="""High-frequency cutoff start for LSC.""", json_schema_extra = { "linkml_meta": {'domain_of': ['DriftSimulationElement']} })
    """High-frequency cutoff start for LSC."""
    lsc_high_frequency_cutoff_end: Optional[float] = Field(default=None, description="""High-frequency cutoff end for LSC.""", json_schema_extra = { "linkml_meta": {'domain_of': ['DriftSimulationElement']} })
    """High-frequency cutoff end for LSC."""
    lsc_low_frequency_cutoff_start: Optional[float] = Field(default=None, description="""Low-frequency cutoff start for LSC.""", json_schema_extra = { "linkml_meta": {'domain_of': ['DriftSimulationElement']} })
    """Low-frequency cutoff start for LSC."""
    lsc_low_frequency_cutoff_end: Optional[float] = Field(default=None, description="""Low-frequency cutoff end for LSC.""", json_schema_extra = { "linkml_meta": {'domain_of': ['DriftSimulationElement']} })
    """Low-frequency cutoff end for LSC."""
    field_definition: Optional[str] = Field(default=None, description="""Path to the 3-D field-map file.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SimulationElement']} })
    """Path to the 3-D field-map file."""
    wakefield_definition: Optional[str] = Field(default=None, description="""Path to the wakefield impedance file.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SimulationElement']} })
    """Path to the wakefield impedance file."""
    wakefield_enable: Optional[bool] = Field(default=True, description="""Whether the wakefield named by wakefield_definition is applied. Set false to track the element without its wakefield while keeping the definition itself.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SimulationElement'], 'ifabsent': 'true'} })
    """Whether the wakefield named by wakefield_definition is applied. Set false to track the element without its wakefield while keeping the definition itself."""
    field_reference_position: Optional[str] = Field(default=None, description="""Longitudinal origin of the field map [m].""", json_schema_extra = { "linkml_meta": {'domain_of': ['SimulationElement']} })
    """Longitudinal origin of the field map [m]."""
    scale_field: float = Field(default=1, description="""Multiplicative scale factor applied to the field map.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SimulationElement'], 'ifabsent': 'float(1)'} })
    """Multiplicative scale factor applied to the field map."""


class _DiagnosticSimulationElementBase(_SimulationElementBase):
    """
    Simulation attributes for beam-diagnostic elements.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:DiagnosticSimulationElement',
         'from_schema': 'https://w3id.org/laura/schema/simulation'})

    output_filename: Optional[str] = Field(default=None, description="""Output filename for diagnostic data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['DiagnosticSimulationElement']} })
    """Output filename for diagnostic data."""
    field_definition: Optional[str] = Field(default=None, description="""Path to the 3-D field-map file.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SimulationElement']} })
    """Path to the 3-D field-map file."""
    wakefield_definition: Optional[str] = Field(default=None, description="""Path to the wakefield impedance file.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SimulationElement']} })
    """Path to the wakefield impedance file."""
    wakefield_enable: Optional[bool] = Field(default=True, description="""Whether the wakefield named by wakefield_definition is applied. Set false to track the element without its wakefield while keeping the definition itself.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SimulationElement'], 'ifabsent': 'true'} })
    """Whether the wakefield named by wakefield_definition is applied. Set false to track the element without its wakefield while keeping the definition itself."""
    field_reference_position: Optional[str] = Field(default=None, description="""Longitudinal origin of the field map [m].""", json_schema_extra = { "linkml_meta": {'domain_of': ['SimulationElement']} })
    """Longitudinal origin of the field map [m]."""
    scale_field: float = Field(default=1, description="""Multiplicative scale factor applied to the field map.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SimulationElement'], 'ifabsent': 'float(1)'} })
    """Multiplicative scale factor applied to the field map."""


class _PlasmaSimulationElementBase(_SimulationElementBase):
    """
    Simulation attributes for plasma-accelerator stages.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:PlasmaSimulationElement',
         'from_schema': 'https://w3id.org/laura/schema/simulation'})

    wakefield_model: Optional[str] = Field(default=None, description="""Wakefield model identifier.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PlasmaSimulationElement']} })
    """Wakefield model identifier."""
    bunch_pusher: str = Field(default="boris", description="""Pusher used to evolve bunch particles in time.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PlasmaSimulationElement'], 'ifabsent': 'string(boris)'} })
    """Pusher used to evolve bunch particles in time."""
    dt_bunch: str = Field(default="auto", description="""Time-step control for bunch evolution (or 'auto').""", json_schema_extra = { "linkml_meta": {'domain_of': ['PlasmaSimulationElement'], 'ifabsent': 'string(auto)'} })
    """Time-step control for bunch evolution (or 'auto')."""
    n_out: int = Field(default=1, description="""Number of distribution dumps during the plasma stage.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PlasmaSimulationElement'], 'ifabsent': 'int(1)'} })
    """Number of distribution dumps during the plasma stage."""
    min_longitudinal_position: float = Field(default=0, description="""Minimum longitudinal position [m].""", json_schema_extra = { "linkml_meta": {'domain_of': ['PlasmaSimulationElement'], 'ifabsent': 'float(0)'} })
    """Minimum longitudinal position [m]."""
    max_longitudinal_position: float = Field(default=0, description="""Maximum longitudinal position [m].""", json_schema_extra = { "linkml_meta": {'domain_of': ['PlasmaSimulationElement'], 'ifabsent': 'float(0)'} })
    """Maximum longitudinal position [m]."""
    n_longitudinal: int = Field(default=0, description="""Number of grid points in the longitudinal direction.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PlasmaSimulationElement'], 'ifabsent': 'int(0)'} })
    """Number of grid points in the longitudinal direction."""
    n_radial: int = Field(default=0, description="""Number of grid points in the radial direction.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PlasmaSimulationElement'], 'ifabsent': 'int(0)'} })
    """Number of grid points in the radial direction."""
    plasma_particles_per_cell: int = Field(default=2, description="""Number of plasma particles per cell.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PlasmaSimulationElement'], 'ifabsent': 'int(2)'} })
    """Number of plasma particles per cell."""
    r_max: float = Field(default=0, description="""Radial extent of the simulation box [m].""", json_schema_extra = { "linkml_meta": {'domain_of': ['PlasmaSimulationElement'], 'ifabsent': 'float(0)'} })
    """Radial extent of the simulation box [m]."""
    r_max_plasma: Optional[float] = Field(default=None, description="""Maximum radial extension of the plasma column.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PlasmaSimulationElement']} })
    """Maximum radial extension of the plasma column."""
    dz_fields: Optional[float] = Field(default=None, description="""Interval for plasma wakefield updates.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PlasmaSimulationElement']} })
    """Interval for plasma wakefield updates."""
    plasma_pusher: str = Field(default="boris", description="""Pusher used to evolve the plasma in time.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PlasmaSimulationElement'], 'ifabsent': 'string(boris)'} })
    """Pusher used to evolve the plasma in time."""
    field_definition: Optional[str] = Field(default=None, description="""Path to the 3-D field-map file.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SimulationElement']} })
    """Path to the 3-D field-map file."""
    wakefield_definition: Optional[str] = Field(default=None, description="""Path to the wakefield impedance file.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SimulationElement']} })
    """Path to the wakefield impedance file."""
    wakefield_enable: Optional[bool] = Field(default=True, description="""Whether the wakefield named by wakefield_definition is applied. Set false to track the element without its wakefield while keeping the definition itself.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SimulationElement'], 'ifabsent': 'true'} })
    """Whether the wakefield named by wakefield_definition is applied. Set false to track the element without its wakefield while keeping the definition itself."""
    field_reference_position: Optional[str] = Field(default=None, description="""Longitudinal origin of the field map [m].""", json_schema_extra = { "linkml_meta": {'domain_of': ['SimulationElement']} })
    """Longitudinal origin of the field map [m]."""
    scale_field: float = Field(default=1, description="""Multiplicative scale factor applied to the field map.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SimulationElement'], 'ifabsent': 'float(1)'} })
    """Multiplicative scale factor applied to the field map."""


class _TwissMatchSimulationElementBase(_SimulationElementBase):
    """
    Simulation attributes for Twiss-matching points.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:TwissMatchSimulationElement',
         'from_schema': 'https://w3id.org/laura/schema/simulation'})

    beta_x: Optional[float] = Field(default=None, description="""Horizontal beta.""", json_schema_extra = { "linkml_meta": {'domain_of': ['TwissMatchSimulationElement']} })
    """Horizontal beta."""
    beta_y: Optional[float] = Field(default=None, description="""Vertical beta.""", json_schema_extra = { "linkml_meta": {'domain_of': ['TwissMatchSimulationElement']} })
    """Vertical beta."""
    alpha_x: Optional[float] = Field(default=None, description="""Horizontal alpha.""", json_schema_extra = { "linkml_meta": {'domain_of': ['TwissMatchSimulationElement']} })
    """Horizontal alpha."""
    alpha_y: Optional[float] = Field(default=None, description="""Vertical alpha.""", json_schema_extra = { "linkml_meta": {'domain_of': ['TwissMatchSimulationElement']} })
    """Vertical alpha."""
    eta_x: float = Field(default=0.0, description="""Horizontal dispersion.""", json_schema_extra = { "linkml_meta": {'domain_of': ['TwissMatchSimulationElement'], 'ifabsent': 'float(0.0)'} })
    """Horizontal dispersion."""
    eta_y: float = Field(default=0.0, description="""Vertical dispersion.""", json_schema_extra = { "linkml_meta": {'domain_of': ['TwissMatchSimulationElement'], 'ifabsent': 'float(0.0)'} })
    """Vertical dispersion."""
    eta_xp: float = Field(default=0.0, description="""Horizontal dispersion derivative.""", json_schema_extra = { "linkml_meta": {'domain_of': ['TwissMatchSimulationElement'], 'ifabsent': 'float(0.0)'} })
    """Horizontal dispersion derivative."""
    eta_yp: float = Field(default=0.0, description="""Vertical dispersion derivative.""", json_schema_extra = { "linkml_meta": {'domain_of': ['TwissMatchSimulationElement'], 'ifabsent': 'float(0.0)'} })
    """Vertical dispersion derivative."""
    from_beam: Optional[bool] = Field(default=True, description="""Compute transform from tracked beam properties.""", json_schema_extra = { "linkml_meta": {'domain_of': ['TwissMatchSimulationElement'], 'ifabsent': 'True'} })
    """Compute transform from tracked beam properties."""
    field_definition: Optional[str] = Field(default=None, description="""Path to the 3-D field-map file.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SimulationElement']} })
    """Path to the 3-D field-map file."""
    wakefield_definition: Optional[str] = Field(default=None, description="""Path to the wakefield impedance file.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SimulationElement']} })
    """Path to the wakefield impedance file."""
    wakefield_enable: Optional[bool] = Field(default=True, description="""Whether the wakefield named by wakefield_definition is applied. Set false to track the element without its wakefield while keeping the definition itself.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SimulationElement'], 'ifabsent': 'true'} })
    """Whether the wakefield named by wakefield_definition is applied. Set false to track the element without its wakefield while keeping the definition itself."""
    field_reference_position: Optional[str] = Field(default=None, description="""Longitudinal origin of the field map [m].""", json_schema_extra = { "linkml_meta": {'domain_of': ['SimulationElement']} })
    """Longitudinal origin of the field map [m]."""
    scale_field: float = Field(default=1, description="""Multiplicative scale factor applied to the field map.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SimulationElement'], 'ifabsent': 'float(1)'} })
    """Multiplicative scale factor applied to the field map."""


class _MatrixTransformSimulationElementBase(_SimulationElementBase):
    """
    Zero-, first-, and second-order transfer-map coefficients for a matrix transform element. Each coefficient collection accepts the dense form or the named coefficient mapping understood by the Python model.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:MatrixTransformSimulationElement',
         'from_schema': 'https://w3id.org/laura/schema/simulation'})

    apply: Optional[bool] = Field(default=False, description="""Whether to apply the transfer map.""", json_schema_extra = { "linkml_meta": {'domain_of': ['MatrixTransformSimulationElement'], 'ifabsent': 'False'} })
    """Whether to apply the transfer map."""
    c_matrix: Optional[Any] = Field(default=None, description="""C-matrix (zeroth-order transfer vector).""", json_schema_extra = { "linkml_meta": {'domain_of': ['MatrixTransformSimulationElement']} })
    """C-matrix (zeroth-order transfer vector)."""
    r_matrix: Optional[Any] = Field(default=None, description="""R-matrix (first-order transfer matrix).""", json_schema_extra = { "linkml_meta": {'domain_of': ['MatrixTransformSimulationElement']} })
    """R-matrix (first-order transfer matrix)."""
    t_matrix: Optional[Any] = Field(default=None, description="""T-matrix (second-order transfer tensor).""", json_schema_extra = { "linkml_meta": {'domain_of': ['MatrixTransformSimulationElement']} })
    """T-matrix (second-order transfer tensor)."""
    field_definition: Optional[str] = Field(default=None, description="""Path to the 3-D field-map file.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SimulationElement']} })
    """Path to the 3-D field-map file."""
    wakefield_definition: Optional[str] = Field(default=None, description="""Path to the wakefield impedance file.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SimulationElement']} })
    """Path to the wakefield impedance file."""
    wakefield_enable: Optional[bool] = Field(default=True, description="""Whether the wakefield named by wakefield_definition is applied. Set false to track the element without its wakefield while keeping the definition itself.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SimulationElement'], 'ifabsent': 'true'} })
    """Whether the wakefield named by wakefield_definition is applied. Set false to track the element without its wakefield while keeping the definition itself."""
    field_reference_position: Optional[str] = Field(default=None, description="""Longitudinal origin of the field map [m].""", json_schema_extra = { "linkml_meta": {'domain_of': ['SimulationElement']} })
    """Longitudinal origin of the field map [m]."""
    scale_field: float = Field(default=1, description="""Multiplicative scale factor applied to the field map.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SimulationElement'], 'ifabsent': 'float(1)'} })
    """Multiplicative scale factor applied to the field map."""


class _ElectrostaticSeparatorSimulationElementBase(_SimulationElementBase):
    """
    Simulation attributes for a static electrostatic separator.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:ElectrostaticSeparatorSimulationElement',
         'from_schema': 'https://w3id.org/laura/schema/simulation'})

    horizontal_field: Optional[Union[float, str]] = Field(default=0.0, description="""Horizontal deflecting electric field [V/m].""", json_schema_extra = { "linkml_meta": {'any_of': [{'range': 'float'}, {'range': 'string'}],
         'domain_of': ['ElectrostaticSeparatorSimulationElement'],
         'ifabsent': 'float(0.0)',
         'in_subset': ['functional_parameters'],
         'unit': {'ucum_code': 'V/m'}} })
    """Horizontal deflecting electric field [V/m]."""
    vertical_field: Optional[Union[float, str]] = Field(default=0.0, description="""Vertical deflecting electric field [V/m].""", json_schema_extra = { "linkml_meta": {'any_of': [{'range': 'float'}, {'range': 'string'}],
         'domain_of': ['ElectrostaticSeparatorSimulationElement'],
         'ifabsent': 'float(0.0)',
         'in_subset': ['functional_parameters'],
         'unit': {'ucum_code': 'V/m'}} })
    """Vertical deflecting electric field [V/m]."""
    tilt: float = Field(default=0.0, description="""Rotation about the beam axis [rad].""", json_schema_extra = { "linkml_meta": {'domain_of': ['ElectrostaticSeparatorSimulationElement',
                       'MagneticElement',
                       'Corrector_Magnet'],
         'ifabsent': 'float(0.0)',
         'unit': {'ucum_code': 'rad'}} })
    """Rotation about the beam axis [rad]."""
    field_definition: Optional[str] = Field(default=None, description="""Path to the 3-D field-map file.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SimulationElement']} })
    """Path to the 3-D field-map file."""
    wakefield_definition: Optional[str] = Field(default=None, description="""Path to the wakefield impedance file.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SimulationElement']} })
    """Path to the wakefield impedance file."""
    wakefield_enable: Optional[bool] = Field(default=True, description="""Whether the wakefield named by wakefield_definition is applied. Set false to track the element without its wakefield while keeping the definition itself.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SimulationElement'], 'ifabsent': 'true'} })
    """Whether the wakefield named by wakefield_definition is applied. Set false to track the element without its wakefield while keeping the definition itself."""
    field_reference_position: Optional[str] = Field(default=None, description="""Longitudinal origin of the field map [m].""", json_schema_extra = { "linkml_meta": {'domain_of': ['SimulationElement']} })
    """Longitudinal origin of the field map [m]."""
    scale_field: float = Field(default=1, description="""Multiplicative scale factor applied to the field map.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SimulationElement'], 'ifabsent': 'float(1)'} })
    """Multiplicative scale factor applied to the field map."""


class _ACDipoleSimulationElementBase(_SimulationElementBase):
    """
    Simulation attributes for an AC dipole / tune exciter.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:ACDipoleSimulationElement',
         'from_schema': 'https://w3id.org/laura/schema/simulation',
         'slot_usage': {'field_amplitude': {'description': 'Peak kick '
                                                           'voltage/amplitude of the '
                                                           'exciter.',
                                            'ifabsent': 'float(0.0)',
                                            'name': 'field_amplitude'},
                        'frequency': {'description': 'Drive frequency [Hz].',
                                      'ifabsent': 'float(0.0)',
                                      'name': 'frequency'},
                        'phase': {'description': 'Phase lag [deg].',
                                  'ifabsent': 'float(0.0)',
                                  'name': 'phase'}}})

    field_amplitude: Optional[Union[float, str]] = Field(default=0.0, description="""Peak kick voltage/amplitude of the exciter.""", json_schema_extra = { "linkml_meta": {'any_of': [{'range': 'float'}, {'range': 'string'}],
         'domain_of': ['MagnetSimulationElement',
                       'RFCavitySimulationElement',
                       'ACDipoleSimulationElement',
                       'RFMultipoleSimulationElement'],
         'ifabsent': 'float(0.0)',
         'in_subset': ['functional_parameters']} })
    """Peak kick voltage/amplitude of the exciter."""
    frequency: Optional[float] = Field(default=0.0, description="""Drive frequency [Hz].""", ge=0.0, json_schema_extra = { "linkml_meta": {'domain_of': ['ACDipoleSimulationElement',
                       'RFMultipoleSimulationElement',
                       'RFCavityElement',
                       'RFDeflectingCavityElement'],
         'ifabsent': 'float(0.0)',
         'unit': {'ucum_code': 'Hz'}} })
    """Drive frequency [Hz]."""
    phase: Optional[Union[float, str]] = Field(default=0.0, description="""Phase lag [deg].""", json_schema_extra = { "linkml_meta": {'any_of': [{'range': 'float'}, {'range': 'string'}],
         'domain_of': ['ACDipoleSimulationElement',
                       'RFMultipoleSimulationElement',
                       'RFCavityElement',
                       'RFDeflectingCavityElement'],
         'ifabsent': 'float(0.0)',
         'in_subset': ['functional_parameters'],
         'unit': {'ucum_code': 'deg'}} })
    """Phase lag [deg]."""
    ramp: list[int] = Field(default_factory=list, description="""Turn numbers [ramp1, ramp2, ramp3, ramp4] defining the drive ramp.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ACDipoleSimulationElement']} })
    """Turn numbers [ramp1, ramp2, ramp3, ramp4] defining the drive ramp."""
    field_definition: Optional[str] = Field(default=None, description="""Path to the 3-D field-map file.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SimulationElement']} })
    """Path to the 3-D field-map file."""
    wakefield_definition: Optional[str] = Field(default=None, description="""Path to the wakefield impedance file.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SimulationElement']} })
    """Path to the wakefield impedance file."""
    wakefield_enable: Optional[bool] = Field(default=True, description="""Whether the wakefield named by wakefield_definition is applied. Set false to track the element without its wakefield while keeping the definition itself.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SimulationElement'], 'ifabsent': 'true'} })
    """Whether the wakefield named by wakefield_definition is applied. Set false to track the element without its wakefield while keeping the definition itself."""
    field_reference_position: Optional[str] = Field(default=None, description="""Longitudinal origin of the field map [m].""", json_schema_extra = { "linkml_meta": {'domain_of': ['SimulationElement']} })
    """Longitudinal origin of the field map [m]."""
    scale_field: float = Field(default=1, description="""Multiplicative scale factor applied to the field map.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SimulationElement'], 'ifabsent': 'float(1)'} })
    """Multiplicative scale factor applied to the field map."""


class _WireSimulationElementBase(_SimulationElementBase):
    """
    Simulation attributes for a compensating wire.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:WireSimulationElement',
         'from_schema': 'https://w3id.org/laura/schema/simulation'})

    current: float = Field(default=0.0, description="""Current carried by the wire [A].""", json_schema_extra = { "linkml_meta": {'domain_of': ['WireSimulationElement'],
         'ifabsent': 'float(0.0)',
         'unit': {'ucum_code': 'A'}} })
    """Current carried by the wire [A]."""
    interaction_length: float = Field(default=0.0, description="""Effective interaction length [m].""", json_schema_extra = { "linkml_meta": {'domain_of': ['WireSimulationElement'],
         'ifabsent': 'float(0.0)',
         'unit': {'ucum_code': 'm'}} })
    """Effective interaction length [m]."""
    horizontal_offset: float = Field(default=0.0, description="""Horizontal wire offset from the reference orbit [m].""", json_schema_extra = { "linkml_meta": {'domain_of': ['WireSimulationElement', 'BeamBeamSimulationElement'],
         'ifabsent': 'float(0.0)',
         'unit': {'ucum_code': 'm'}} })
    """Horizontal wire offset from the reference orbit [m]."""
    vertical_offset: float = Field(default=0.0, description="""Vertical wire offset from the reference orbit [m].""", json_schema_extra = { "linkml_meta": {'domain_of': ['WireSimulationElement', 'BeamBeamSimulationElement'],
         'ifabsent': 'float(0.0)',
         'unit': {'ucum_code': 'm'}} })
    """Vertical wire offset from the reference orbit [m]."""
    field_definition: Optional[str] = Field(default=None, description="""Path to the 3-D field-map file.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SimulationElement']} })
    """Path to the 3-D field-map file."""
    wakefield_definition: Optional[str] = Field(default=None, description="""Path to the wakefield impedance file.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SimulationElement']} })
    """Path to the wakefield impedance file."""
    wakefield_enable: Optional[bool] = Field(default=True, description="""Whether the wakefield named by wakefield_definition is applied. Set false to track the element without its wakefield while keeping the definition itself.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SimulationElement'], 'ifabsent': 'true'} })
    """Whether the wakefield named by wakefield_definition is applied. Set false to track the element without its wakefield while keeping the definition itself."""
    field_reference_position: Optional[str] = Field(default=None, description="""Longitudinal origin of the field map [m].""", json_schema_extra = { "linkml_meta": {'domain_of': ['SimulationElement']} })
    """Longitudinal origin of the field map [m]."""
    scale_field: float = Field(default=1, description="""Multiplicative scale factor applied to the field map.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SimulationElement'], 'ifabsent': 'float(1)'} })
    """Multiplicative scale factor applied to the field map."""


class _BeamBeamSimulationElementBase(_SimulationElementBase):
    """
    Simulation attributes for a weak-strong beam-beam interaction.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:BeamBeamSimulationElement',
         'from_schema': 'https://w3id.org/laura/schema/simulation'})

    charge: float = Field(default=1.0, description="""Opposing-beam particle charge in units of the elementary charge.""", json_schema_extra = { "linkml_meta": {'domain_of': ['BeamBeamSimulationElement'], 'ifabsent': 'float(1.0)'} })
    """Opposing-beam particle charge in units of the elementary charge."""
    n_particles: float = Field(default=0.0, description="""Number of particles in the opposing bunch.""", json_schema_extra = { "linkml_meta": {'domain_of': ['BeamBeamSimulationElement'], 'ifabsent': 'float(0.0)'} })
    """Number of particles in the opposing bunch."""
    horizontal_offset: float = Field(default=0.0, description="""Horizontal opposing-bunch centroid offset [m].""", json_schema_extra = { "linkml_meta": {'domain_of': ['WireSimulationElement', 'BeamBeamSimulationElement'],
         'ifabsent': 'float(0.0)',
         'unit': {'ucum_code': 'm'}} })
    """Horizontal opposing-bunch centroid offset [m]."""
    vertical_offset: float = Field(default=0.0, description="""Vertical opposing-bunch centroid offset [m].""", json_schema_extra = { "linkml_meta": {'domain_of': ['WireSimulationElement', 'BeamBeamSimulationElement'],
         'ifabsent': 'float(0.0)',
         'unit': {'ucum_code': 'm'}} })
    """Vertical opposing-bunch centroid offset [m]."""
    horizontal_sigma: float = Field(default=0.0, description="""Horizontal RMS size of the opposing bunch [m].""", json_schema_extra = { "linkml_meta": {'domain_of': ['BeamBeamSimulationElement'],
         'ifabsent': 'float(0.0)',
         'unit': {'ucum_code': 'm'}} })
    """Horizontal RMS size of the opposing bunch [m]."""
    vertical_sigma: float = Field(default=0.0, description="""Vertical RMS size of the opposing bunch [m].""", json_schema_extra = { "linkml_meta": {'domain_of': ['BeamBeamSimulationElement'],
         'ifabsent': 'float(0.0)',
         'unit': {'ucum_code': 'm'}} })
    """Vertical RMS size of the opposing bunch [m]."""
    width: float = Field(default=0.0, description="""Opposing-bunch length for the 3-D weak-strong model [m].""", json_schema_extra = { "linkml_meta": {'domain_of': ['BeamBeamSimulationElement', 'MagneticElement'],
         'ifabsent': 'float(0.0)',
         'unit': {'ucum_code': 'm'}} })
    """Opposing-bunch length for the 3-D weak-strong model [m]."""
    field_definition: Optional[str] = Field(default=None, description="""Path to the 3-D field-map file.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SimulationElement']} })
    """Path to the 3-D field-map file."""
    wakefield_definition: Optional[str] = Field(default=None, description="""Path to the wakefield impedance file.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SimulationElement']} })
    """Path to the wakefield impedance file."""
    wakefield_enable: Optional[bool] = Field(default=True, description="""Whether the wakefield named by wakefield_definition is applied. Set false to track the element without its wakefield while keeping the definition itself.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SimulationElement'], 'ifabsent': 'true'} })
    """Whether the wakefield named by wakefield_definition is applied. Set false to track the element without its wakefield while keeping the definition itself."""
    field_reference_position: Optional[str] = Field(default=None, description="""Longitudinal origin of the field map [m].""", json_schema_extra = { "linkml_meta": {'domain_of': ['SimulationElement']} })
    """Longitudinal origin of the field map [m]."""
    scale_field: float = Field(default=1, description="""Multiplicative scale factor applied to the field map.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SimulationElement'], 'ifabsent': 'float(1)'} })
    """Multiplicative scale factor applied to the field map."""


class _RFMultipoleSimulationElementBase(_SimulationElementBase):
    """
    Simulation attributes for a thin RF multipole kick.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:RFMultipoleSimulationElement',
         'from_schema': 'https://w3id.org/laura/schema/simulation',
         'slot_usage': {'field_amplitude': {'description': 'Longitudinal voltage [V].',
                                            'ifabsent': 'float(0.0)',
                                            'name': 'field_amplitude'},
                        'frequency': {'description': 'RF frequency [Hz].',
                                      'ifabsent': 'float(0.0)',
                                      'name': 'frequency'},
                        'phase': {'description': 'Overall phase lag [deg].',
                                  'ifabsent': 'float(0.0)',
                                  'name': 'phase'}}})

    frequency: Optional[float] = Field(default=0.0, description="""RF frequency [Hz].""", ge=0.0, json_schema_extra = { "linkml_meta": {'domain_of': ['ACDipoleSimulationElement',
                       'RFMultipoleSimulationElement',
                       'RFCavityElement',
                       'RFDeflectingCavityElement'],
         'ifabsent': 'float(0.0)',
         'unit': {'ucum_code': 'Hz'}} })
    """RF frequency [Hz]."""
    phase: Optional[Union[float, str]] = Field(default=0.0, description="""Overall phase lag [deg].""", json_schema_extra = { "linkml_meta": {'any_of': [{'range': 'float'}, {'range': 'string'}],
         'domain_of': ['ACDipoleSimulationElement',
                       'RFMultipoleSimulationElement',
                       'RFCavityElement',
                       'RFDeflectingCavityElement'],
         'ifabsent': 'float(0.0)',
         'in_subset': ['functional_parameters'],
         'unit': {'ucum_code': 'deg'}} })
    """Overall phase lag [deg]."""
    field_amplitude: Optional[Union[float, str]] = Field(default=0.0, description="""Longitudinal voltage [V].""", json_schema_extra = { "linkml_meta": {'any_of': [{'range': 'float'}, {'range': 'string'}],
         'domain_of': ['MagnetSimulationElement',
                       'RFCavitySimulationElement',
                       'ACDipoleSimulationElement',
                       'RFMultipoleSimulationElement'],
         'ifabsent': 'float(0.0)',
         'in_subset': ['functional_parameters']} })
    """Longitudinal voltage [V]."""
    knl: list[float] = Field(default_factory=list, description="""Integrated normal multipole strengths, dipole through decapole.""", json_schema_extra = { "linkml_meta": {'domain_of': ['RFMultipoleSimulationElement']} })
    """Integrated normal multipole strengths, dipole through decapole."""
    ksl: list[float] = Field(default_factory=list, description="""Integrated skew multipole strengths, dipole through decapole.""", json_schema_extra = { "linkml_meta": {'domain_of': ['RFMultipoleSimulationElement']} })
    """Integrated skew multipole strengths, dipole through decapole."""
    pnl: list[float] = Field(default_factory=list, description="""Normal multipole phases [deg], dipole through decapole.""", json_schema_extra = { "linkml_meta": {'domain_of': ['RFMultipoleSimulationElement']} })
    """Normal multipole phases [deg], dipole through decapole."""
    psl: list[float] = Field(default_factory=list, description="""Skew multipole phases [deg], dipole through decapole.""", json_schema_extra = { "linkml_meta": {'domain_of': ['RFMultipoleSimulationElement']} })
    """Skew multipole phases [deg], dipole through decapole."""
    field_definition: Optional[str] = Field(default=None, description="""Path to the 3-D field-map file.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SimulationElement']} })
    """Path to the 3-D field-map file."""
    wakefield_definition: Optional[str] = Field(default=None, description="""Path to the wakefield impedance file.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SimulationElement']} })
    """Path to the wakefield impedance file."""
    wakefield_enable: Optional[bool] = Field(default=True, description="""Whether the wakefield named by wakefield_definition is applied. Set false to track the element without its wakefield while keeping the definition itself.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SimulationElement'], 'ifabsent': 'true'} })
    """Whether the wakefield named by wakefield_definition is applied. Set false to track the element without its wakefield while keeping the definition itself."""
    field_reference_position: Optional[str] = Field(default=None, description="""Longitudinal origin of the field map [m].""", json_schema_extra = { "linkml_meta": {'domain_of': ['SimulationElement']} })
    """Longitudinal origin of the field map [m]."""
    scale_field: float = Field(default=1, description="""Multiplicative scale factor applied to the field map.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SimulationElement'], 'ifabsent': 'float(1)'} })
    """Multiplicative scale factor applied to the field map."""


class _MultipoleBase(ConfiguredBaseModel):
    """
    Individual multipole field component, characterised by order and integrated normal / skew strengths at a reference radius.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:Multipole',
         'from_schema': 'https://w3id.org/laura/schema/magnetic'})

    order: int = Field(default=0, description="""Multipole order (0 = dipole, 1 = quadrupole, ?).""", ge=0, json_schema_extra = { "linkml_meta": {'domain_of': ['Multipole', 'MagneticElement', 'Solenoid_Magnet'],
         'ifabsent': 'int(0)'} })
    """Multipole order (0 = dipole, 1 = quadrupole, ?)."""
    normal: Optional[Union[float, str]] = Field(default=0, description="""Integrated normal (upright) multipole strength [T.m^{1-n}].""", json_schema_extra = { "linkml_meta": {'any_of': [{'range': 'float'}, {'range': 'string'}],
         'domain_of': ['Multipole'],
         'ifabsent': 'float(0)',
         'in_subset': ['functional_parameters']} })
    """Integrated normal (upright) multipole strength [T.m^{1-n}]."""
    skew: Optional[Union[float, str]] = Field(default=0, description="""Integrated skew (rotated) multipole strength [T.m^{1-n}].""", json_schema_extra = { "linkml_meta": {'any_of': [{'range': 'float'}, {'range': 'string'}],
         'domain_of': ['Multipole', 'MagneticElement'],
         'ifabsent': 'float(0)',
         'in_subset': ['functional_parameters']} })
    """Integrated skew (rotated) multipole strength [T.m^{1-n}]."""
    radius: float = Field(default=0, description="""Reference radius for multipole normalisation [m].""", json_schema_extra = { "linkml_meta": {'domain_of': ['ApertureElement', 'Multipole', 'CameraMask'],
         'ifabsent': 'float(0)',
         'unit': {'ucum_code': 'm'}} })
    """Reference radius for multipole normalisation [m]."""


class _MultipolesBase(ConfiguredBaseModel):
    """
    Complete set of integrated multipole strengths up to decapole order, as named slots for efficient element look-up.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:MultipoleList',
         'from_schema': 'https://w3id.org/laura/schema/magnetic'})

    K0L: Optional[_MultipoleBase] = Field(default=None, description="""Integrated dipole field.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Multipoles']} })
    """Integrated dipole field."""
    K1L: Optional[_MultipoleBase] = Field(default=None, description="""Integrated quadrupole gradient.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Multipoles']} })
    """Integrated quadrupole gradient."""
    K2L: Optional[_MultipoleBase] = Field(default=None, description="""Integrated sextupole strength.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Multipoles']} })
    """Integrated sextupole strength."""
    K3L: Optional[_MultipoleBase] = Field(default=None, description="""Integrated octupole strength.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Multipoles']} })
    """Integrated octupole strength."""
    K4L: Optional[_MultipoleBase] = Field(default=None, description="""Integrated decapole strength.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Multipoles']} })
    """Integrated decapole strength."""


class _FieldIntegralBase(ConfiguredBaseModel):
    """
    Polynomial fit of integrated field strength as a function of magnet current.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:FieldIntegral',
         'from_schema': 'https://w3id.org/laura/schema/magnetic'})

    coefficients: list[float] = Field(default_factory=list, description="""Polynomial coefficients ordered from lowest to highest degree: ``FieldIntegral = sum c_n . I^n``.""", json_schema_extra = { "linkml_meta": {'domain_of': ['FieldIntegral']} })
    """Polynomial coefficients ordered from lowest to highest degree: ``FieldIntegral = sum c_n . I^n``."""


class _LinearSaturationFitBase(ConfiguredBaseModel):
    """
    Bi-linear saturation model mapping magnet current to integrated field strength (K-value conversion).
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:LinearSaturationFit',
         'from_schema': 'https://w3id.org/laura/schema/magnetic'})

    m: float = Field(default=0, description="""Linear slope of the unsaturated region.""", json_schema_extra = { "linkml_meta": {'domain_of': ['LinearSaturationFit'], 'ifabsent': 'float(0)'} })
    """Linear slope of the unsaturated region."""
    I_max: float = Field(default=0, description="""Current at which saturation begins [A].""", json_schema_extra = { "linkml_meta": {'domain_of': ['LinearSaturationFit'],
         'ifabsent': 'float(0)',
         'unit': {'ucum_code': 'A'}} })
    """Current at which saturation begins [A]."""
    f: float = Field(default=0, description="""Saturation fraction (slope ratio below/above I_max).""", json_schema_extra = { "linkml_meta": {'domain_of': ['LinearSaturationFit'], 'ifabsent': 'float(0)'} })
    """Saturation fraction (slope ratio below/above I_max)."""
    a: float = Field(default=0, description="""Quadratic saturation coefficient.""", json_schema_extra = { "linkml_meta": {'domain_of': ['LinearSaturationFit'], 'ifabsent': 'float(0)'} })
    """Quadratic saturation coefficient."""
    I0: float = Field(default=0, description="""Current offset [A].""", json_schema_extra = { "linkml_meta": {'domain_of': ['LinearSaturationFit'],
         'ifabsent': 'float(0)',
         'unit': {'ucum_code': 'A'}} })
    """Current offset [A]."""
    d: float = Field(default=0, description="""Constant offset term.""", json_schema_extra = { "linkml_meta": {'domain_of': ['LinearSaturationFit'], 'ifabsent': 'float(0)'} })
    """Constant offset term."""
    L: float = Field(default=0, description="""Effective magnetic length [m].""", json_schema_extra = { "linkml_meta": {'domain_of': ['LinearSaturationFit'],
         'ifabsent': 'float(0)',
         'unit': {'ucum_code': 'm'}} })
    """Effective magnetic length [m]."""


class _MagneticElementBase(ConfiguredBaseModel):
    """
    Magnetic field parameters for a beamline magnet, including multipole components, field integrals, and geometric edge parameters.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:MagneticElement',
         'from_schema': 'https://w3id.org/laura/schema/magnetic',
         'in_subset': ['magnetic_properties']})

    order: int = Field(default=-1, description="""Principal multipole order (0 = dipole, 1 = quad, ?).""", ge=-1, json_schema_extra = { "linkml_meta": {'domain_of': ['Multipole', 'MagneticElement', 'Solenoid_Magnet'],
         'ifabsent': 'int(-1)'} })
    """Principal multipole order (0 = dipole, 1 = quad, ?)."""
    skew: bool = Field(default=False, description="""Whether the magnet is rotated 45? to produce a skew field component.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Multipole', 'MagneticElement'], 'ifabsent': 'False'} })
    """Whether the magnet is rotated 45? to produce a skew field component."""
    length: float = Field(default=0, description="""Magnetic (effective) length [m].""", ge=0.0, validation_alias=AliasChoices('length', 'magnetic_length'), json_schema_extra = { "linkml_meta": {'aliases': ['magnetic_length'],
         'domain_of': ['PhysicalElement',
                       'MagneticElement',
                       'Solenoid_Magnet',
                       'Wiggler_Magnet',
                       'NonLinearLens_Magnet'],
         'ifabsent': 'float(0)',
         'unit': {'ucum_code': 'm'}} })
    """Magnetic (effective) length [m]."""
    multipoles: Optional[_MultipolesBase] = Field(default=None, description="""Integrated multipole field components.""", json_schema_extra = { "linkml_meta": {'domain_of': ['MagneticElement']} })
    """Integrated multipole field components."""
    systematic_multipoles: Optional[_MultipolesBase] = Field(default=None, description="""Systematic (design) multipole errors at the reference radius.""", json_schema_extra = { "linkml_meta": {'domain_of': ['MagneticElement']} })
    """Systematic (design) multipole errors at the reference radius."""
    random_multipoles: Optional[_MultipolesBase] = Field(default=None, description="""Random multipole errors at the reference radius.""", json_schema_extra = { "linkml_meta": {'domain_of': ['MagneticElement']} })
    """Random multipole errors at the reference radius."""
    field_integral_coefficients: Optional[_FieldIntegralBase] = Field(default=None, description="""Polynomial calibration of integrated field vs. current.""", json_schema_extra = { "linkml_meta": {'domain_of': ['MagneticElement', 'Solenoid_Magnet']} })
    """Polynomial calibration of integrated field vs. current."""
    linear_saturation_coefficients: Optional[_LinearSaturationFitBase] = Field(default=None, description="""Bi-linear saturation calibration.""", json_schema_extra = { "linkml_meta": {'domain_of': ['MagneticElement', 'Solenoid_Magnet']} })
    """Bi-linear saturation calibration."""
    settle_time: Optional[float] = Field(default=None, description="""Power-supply settle time after a change [s].""", json_schema_extra = { "linkml_meta": {'domain_of': ['MagneticElement', 'Solenoid_Magnet'],
         'unit': {'ucum_code': 's'}} })
    """Power-supply settle time after a change [s]."""
    entrance_edge_angle: Optional[Union[float, str]] = Field(default=None, description="""Fringe-field entrance edge angle [rad].""", json_schema_extra = { "linkml_meta": {'any_of': [{'range': 'float'}, {'range': 'string'}],
         'domain_of': ['MagneticElement'],
         'in_subset': ['functional_parameters', 'bend_angle_reference'],
         'unit': {'ucum_code': 'rad'}} })
    """Fringe-field entrance edge angle [rad]."""
    exit_edge_angle: Optional[Union[float, str]] = Field(default=None, description="""Fringe-field exit edge angle [rad].""", json_schema_extra = { "linkml_meta": {'any_of': [{'range': 'float'}, {'range': 'string'}],
         'domain_of': ['MagneticElement'],
         'in_subset': ['functional_parameters', 'bend_angle_reference'],
         'unit': {'ucum_code': 'rad'}} })
    """Fringe-field exit edge angle [rad]."""
    gap: float = Field(default=0.032, description="""Full gap between pole faces [m].""", ge=0.0, json_schema_extra = { "linkml_meta": {'domain_of': ['MagneticElement'],
         'ifabsent': 'float(0.032)',
         'unit': {'ucum_code': 'm'}} })
    """Full gap between pole faces [m]."""
    bore: float = Field(default=0.037, description="""Magnet bore radius [m].""", ge=0.0, json_schema_extra = { "linkml_meta": {'domain_of': ['MagneticElement'],
         'ifabsent': 'float(0.037)',
         'unit': {'ucum_code': 'm'}} })
    """Magnet bore radius [m]."""
    plane: Optional[BendingPlaneEnum] = Field(default=BendingPlaneEnum.Horizontal, description="""Principal bending / focusing plane (``Horizontal``, ``Vertical``, or ``Combined``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['MagneticElement'], 'ifabsent': 'string(Horizontal)'} })
    """Principal bending / focusing plane (``Horizontal``, ``Vertical``, or ``Combined``)."""
    width: float = Field(default=0.2, description="""Physical width of the magnet in the bending plane [m].""", json_schema_extra = { "linkml_meta": {'domain_of': ['BeamBeamSimulationElement', 'MagneticElement'],
         'ifabsent': 'float(0.2)',
         'unit': {'ucum_code': 'm'}} })
    """Physical width of the magnet in the bending plane [m]."""
    tilt: float = Field(default=0.0, description="""Global tilt about the beam axis [rad].""", json_schema_extra = { "linkml_meta": {'domain_of': ['ElectrostaticSeparatorSimulationElement',
                       'MagneticElement',],
         'ifabsent': 'float(0.0)',
         'unit': {'ucum_code': 'rad'}} })
    """Global tilt about the beam axis [rad]."""
    edge_field_integral: float = Field(default=0.5, description="""Enge fringe-field integral parameter (dimensionless).""", json_schema_extra = { "linkml_meta": {'domain_of': ['MagnetSimulationElement', 'MagneticElement'],
         'ifabsent': 'float(0.5)'} })
    """Enge fringe-field integral parameter (dimensionless)."""
    fringe_field_coefficient: float = Field(default=0.0, description="""Coefficient controlling the fringe-field roll-off rate.""", json_schema_extra = { "linkml_meta": {'domain_of': ['MagneticElement'], 'ifabsent': 'float(0.0)'} })
    """Coefficient controlling the fringe-field roll-off rate."""
    gradient: Optional[float] = Field(default=None, description="""Peak field gradient [T/m] (quads) or peak field [T] (dipoles).""", json_schema_extra = { "linkml_meta": {'domain_of': ['MagneticElement'], 'unit': {'ucum_code': 'T.m-1'}} })
    """Peak field gradient [T/m] (quads) or peak field [T] (dipoles)."""


class _DegaussableElementBase(ConfiguredBaseModel):
    """
    Degaussing (demagnetisation cycle) parameters for magnets that require a field-reset procedure.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:DegaussableElement',
         'from_schema': 'https://w3id.org/laura/schema/magnetic',
         'in_subset': ['magnetic_properties']})

    tolerance: float = Field(default=0.5, description="""Current tolerance band during the degauss cycle [A].""", validation_alias=AliasChoices('tolerance', 'degauss_tolerance'), json_schema_extra = { "linkml_meta": {'aliases': ['degauss_tolerance'],
         'domain_of': ['DegaussableElement'],
         'ifabsent': 'float(0.5)',
         'unit': {'ucum_code': 'A'}} })
    """Current tolerance band during the degauss cycle [A]."""
    values: list[float] = Field(default_factory=list, description="""Sequence of peak currents applied during the degauss cycle [A].""", validation_alias=AliasChoices('values', 'degauss_values'), json_schema_extra = { "linkml_meta": {'aliases': ['degauss_values'],
         'domain_of': ['DegaussableElement'],
         'unit': {'ucum_code': 'A'}} })
    """Sequence of peak currents applied during the degauss cycle [A]."""
    steps: int = Field(default=11, description="""Number of degauss steps per half-cycle.""", ge=1, validation_alias=AliasChoices('steps', 'num_degauss_steps'), json_schema_extra = { "linkml_meta": {'aliases': ['num_degauss_steps'],
         'domain_of': ['DegaussableElement'],
         'ifabsent': 'int(11)'} })
    """Number of degauss steps per half-cycle."""


class _RFCavityElementBase(ConfiguredBaseModel):
    """
    RF cavity accelerating-structure parameters.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:RFCavityElement',
         'from_schema': 'https://w3id.org/laura/schema/rf',
         'in_subset': ['rf_properties']})

    cell_length: Optional[float] = Field(default=0.03333333333333333, description="""Length of a single cell [m].""", ge=0.0, json_schema_extra = { "linkml_meta": {'domain_of': ['RFCavityElement',
                       'WakefieldElement',
                       'RFDeflectingCavityElement'],
         'ifabsent': 'float(0.03333333333333333)',
         'unit': {'ucum_code': 'm'}} })
    """Length of a single cell [m]."""
    coupling_cell_length: Optional[float] = Field(default=0.0, description="""Length of the coupling cell [m].""", ge=0.0, json_schema_extra = { "linkml_meta": {'domain_of': ['RFCavityElement',
                       'WakefieldElement',
                       'RFDeflectingCavityElement'],
         'ifabsent': 'float(0.0)',
         'unit': {'ucum_code': 'm'}} })
    """Length of the coupling cell [m]."""
    design_gamma: Optional[float] = Field(default=None, description="""Design Lorentz factor.""", ge=1.0, json_schema_extra = { "linkml_meta": {'domain_of': ['RFCavityElement', 'RFDeflectingCavityElement']} })
    """Design Lorentz factor."""
    design_power: Optional[float] = Field(default=25000000, description="""Design peak power [W].""", ge=0.0, json_schema_extra = { "linkml_meta": {'domain_of': ['RFCavityElement', 'RFDeflectingCavityElement'],
         'ifabsent': 'float(25000000)',
         'unit': {'ucum_code': 'W'}} })
    """Design peak power [W]."""
    frequency: Optional[float] = Field(default=2998500000.0, description="""Operating frequency [Hz].""", ge=0.0, json_schema_extra = { "linkml_meta": {'domain_of': ['ACDipoleSimulationElement',
                       'RFMultipoleSimulationElement',
                       'RFCavityElement',
                       'RFDeflectingCavityElement'],
         'ifabsent': 'float(2998500000.0)',
         'unit': {'ucum_code': 'Hz'}} })
    """Operating frequency [Hz]."""
    n_cells: Optional[float] = Field(default=1, description="""Number of cells.""", ge=0, json_schema_extra = { "linkml_meta": {'domain_of': ['RFCavityElement',
                       'WakefieldElement',
                       'RFDeflectingCavityElement'],
         'ifabsent': 'float(1)'} })
    """Number of cells."""
    crest: Optional[float] = Field(default=0, description="""On-crest phase offset providing maximum energy gain [deg].""", json_schema_extra = { "linkml_meta": {'domain_of': ['RFCavityElement', 'RFDeflectingCavityElement'],
         'ifabsent': 'float(0)',
         'unit': {'ucum_code': 'deg'}} })
    """On-crest phase offset providing maximum energy gain [deg]."""
    phase: Optional[Union[float, str]] = Field(default=0.0, description="""Operating phase offset [deg].""", json_schema_extra = { "linkml_meta": {'any_of': [{'range': 'float'}, {'range': 'string'}],
         'domain_of': ['ACDipoleSimulationElement',
                       'RFMultipoleSimulationElement',
                       'RFCavityElement',
                       'RFDeflectingCavityElement'],
         'ifabsent': 'float(0.0)',
         'in_subset': ['functional_parameters'],
         'unit': {'ucum_code': 'deg'}} })
    """Operating phase offset [deg]."""
    shunt_impedance: Optional[float] = Field(default=None, description="""Shunt impedance [M?/m].""", json_schema_extra = { "linkml_meta": {'domain_of': ['RFCavityElement', 'RFDeflectingCavityElement']} })
    """Shunt impedance [M?/m]."""
    mode_numerator: Optional[float] = Field(default=None, description="""Mode fraction numerator.""", json_schema_extra = { "linkml_meta": {'domain_of': ['RFCavityElement', 'RFDeflectingCavityElement']} })
    """Mode fraction numerator."""
    mode_denominator: Optional[int] = Field(default=None, description="""Mode fraction denominator.""", json_schema_extra = { "linkml_meta": {'domain_of': ['RFCavityElement', 'RFDeflectingCavityElement']} })
    """Mode fraction denominator."""
    structure_type: str = Field(default="StandingWave", description="""RF structure type (e.g., ``SW`` standing-wave, ``TW`` travelling-wave).""", validation_alias=AliasChoices('structure_type', 'structure_Type'), json_schema_extra = { "linkml_meta": {'aliases': ['structure_Type'],
         'domain_of': ['RFCavityElement'],
         'ifabsent': 'string(StandingWave)'} })
    """RF structure type (e.g., ``SW`` standing-wave, ``TW`` travelling-wave)."""
    attenuation_constant: float = Field(default=0, description="""Attenuation constant ? of a travelling-wave structure [Np/m].""", json_schema_extra = { "linkml_meta": {'domain_of': ['RFCavityElement'], 'ifabsent': 'float(0)'} })
    """Attenuation constant ? of a travelling-wave structure [Np/m]."""
    power_calibration: list[float] = Field(default_factory=list, description="""Calibration constant relating measured power to cavity gradient.""", json_schema_extra = { "linkml_meta": {'domain_of': ['RFCavityElement']} })
    """Calibration constant relating measured power to cavity gradient."""
    gradient_calibration: list[float] = Field(default_factory=list, description="""Calibration relating measured signal to gradient [MV/m per a.u.].""", json_schema_extra = { "linkml_meta": {'domain_of': ['RFCavityElement']} })
    """Calibration relating measured signal to gradient [MV/m per a.u.]."""


class _WakefieldElementBase(ConfiguredBaseModel):
    """
    Passive wakefield structure parameters.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:WakefieldElement',
         'from_schema': 'https://w3id.org/laura/schema/rf',
         'in_subset': ['rf_properties']})

    cell_length: Optional[float] = Field(default=0.03333333333333333, description="""Length of a single cell [m].""", ge=0.0, json_schema_extra = { "linkml_meta": {'domain_of': ['RFCavityElement',
                       'WakefieldElement',
                       'RFDeflectingCavityElement'],
         'ifabsent': 'float(0.03333333333333333)',
         'unit': {'ucum_code': 'm'}} })
    """Length of a single cell [m]."""
    n_cells: Optional[float] = Field(default=1, description="""Number of cells.""", ge=0, json_schema_extra = { "linkml_meta": {'domain_of': ['RFCavityElement',
                       'WakefieldElement',
                       'RFDeflectingCavityElement'],
         'ifabsent': 'float(1)'} })
    """Number of cells."""
    coupling_cell_length: Optional[float] = Field(default=0.0, description="""Length of the coupling cell [m].""", ge=0.0, json_schema_extra = { "linkml_meta": {'domain_of': ['RFCavityElement',
                       'WakefieldElement',
                       'RFDeflectingCavityElement'],
         'ifabsent': 'float(0.0)',
         'unit': {'ucum_code': 'm'}} })
    """Length of the coupling cell [m]."""


class _RFDeflectingCavityElementBase(ConfiguredBaseModel):
    """
    Transverse-deflecting RF cavity parameters -- a subset of RFCavityElement for streak-mode operation.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:RFDeflectingCavityElement',
         'from_schema': 'https://w3id.org/laura/schema/rf',
         'in_subset': ['rf_properties']})

    cell_length: Optional[float] = Field(default=0.03333333333333333, description="""Length of a single cell [m].""", ge=0.0, json_schema_extra = { "linkml_meta": {'domain_of': ['RFCavityElement',
                       'WakefieldElement',
                       'RFDeflectingCavityElement'],
         'ifabsent': 'float(0.03333333333333333)',
         'unit': {'ucum_code': 'm'}} })
    """Length of a single cell [m]."""
    coupling_cell_length: Optional[float] = Field(default=0.0, description="""Length of the coupling cell [m].""", ge=0.0, json_schema_extra = { "linkml_meta": {'domain_of': ['RFCavityElement',
                       'WakefieldElement',
                       'RFDeflectingCavityElement'],
         'ifabsent': 'float(0.0)',
         'unit': {'ucum_code': 'm'}} })
    """Length of the coupling cell [m]."""
    crest: Optional[float] = Field(default=0, description="""On-crest phase offset providing maximum energy gain [deg].""", json_schema_extra = { "linkml_meta": {'domain_of': ['RFCavityElement', 'RFDeflectingCavityElement'],
         'ifabsent': 'float(0)',
         'unit': {'ucum_code': 'deg'}} })
    """On-crest phase offset providing maximum energy gain [deg]."""
    design_gamma: Optional[float] = Field(default=None, description="""Design Lorentz factor.""", ge=1.0, json_schema_extra = { "linkml_meta": {'domain_of': ['RFCavityElement', 'RFDeflectingCavityElement']} })
    """Design Lorentz factor."""
    design_power: Optional[float] = Field(default=25000000, description="""Design peak power [W].""", ge=0.0, json_schema_extra = { "linkml_meta": {'domain_of': ['RFCavityElement', 'RFDeflectingCavityElement'],
         'ifabsent': 'float(25000000)',
         'unit': {'ucum_code': 'W'}} })
    """Design peak power [W]."""
    frequency: Optional[float] = Field(default=2998500000.0, description="""Operating frequency [Hz].""", ge=0.0, json_schema_extra = { "linkml_meta": {'domain_of': ['ACDipoleSimulationElement',
                       'RFMultipoleSimulationElement',
                       'RFCavityElement',
                       'RFDeflectingCavityElement'],
         'ifabsent': 'float(2998500000.0)',
         'unit': {'ucum_code': 'Hz'}} })
    """Operating frequency [Hz]."""
    n_cells: Optional[float] = Field(default=1, description="""Number of cells.""", ge=0, json_schema_extra = { "linkml_meta": {'domain_of': ['RFCavityElement',
                       'WakefieldElement',
                       'RFDeflectingCavityElement'],
         'ifabsent': 'float(1)'} })
    """Number of cells."""
    phase: Optional[Union[float, str]] = Field(default=0.0, description="""Operating phase offset [deg].""", json_schema_extra = { "linkml_meta": {'any_of': [{'range': 'float'}, {'range': 'string'}],
         'domain_of': ['ACDipoleSimulationElement',
                       'RFMultipoleSimulationElement',
                       'RFCavityElement',
                       'RFDeflectingCavityElement'],
         'ifabsent': 'float(0.0)',
         'in_subset': ['functional_parameters'],
         'unit': {'ucum_code': 'deg'}} })
    """Operating phase offset [deg]."""
    shunt_impedance: Optional[float] = Field(default=None, description="""Shunt impedance [M?/m].""", json_schema_extra = { "linkml_meta": {'domain_of': ['RFCavityElement', 'RFDeflectingCavityElement']} })
    """Shunt impedance [M?/m]."""
    mode_numerator: Optional[float] = Field(default=None, description="""Mode fraction numerator.""", json_schema_extra = { "linkml_meta": {'domain_of': ['RFCavityElement', 'RFDeflectingCavityElement']} })
    """Mode fraction numerator."""
    mode_denominator: Optional[int] = Field(default=None, description="""Mode fraction denominator.""", json_schema_extra = { "linkml_meta": {'domain_of': ['RFCavityElement', 'RFDeflectingCavityElement']} })
    """Mode fraction denominator."""


class _PIDElementBase(ConfiguredBaseModel):
    """
    PID feedback-controller parameters.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:PIDElement',
         'from_schema': 'https://w3id.org/laura/schema/rf'})

    Kp: Optional[float] = Field(default=None, description="""Proportional gain.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PIDElement']} })
    """Proportional gain."""
    Ki: Optional[float] = Field(default=None, description="""Integral gain.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PIDElement']} })
    """Integral gain."""
    Kd: Optional[float] = Field(default=None, description="""Derivative gain.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PIDElement']} })
    """Derivative gain."""
    forward_channel: Optional[int] = Field(default=None, description="""Forward channel index.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PIDElement']} })
    """Forward channel index."""
    probe_channel: Optional[int] = Field(default=None, description="""Probe channel index.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PIDElement']} })
    """Probe channel index."""
    enable: Optional[str] = Field(default=None, description="""Enable command/value.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PIDElement']} })
    """Enable command/value."""
    disable: Optional[str] = Field(default=None, description="""Disable command/value.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PIDElement']} })
    """Disable command/value."""
    phase_range: Optional[_PIDPhaseRangeBase] = Field(default=None, description="""Phase tuning range.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PIDElement']} })
    """Phase tuning range."""
    phase_weight_range: Optional[_PIDWeightRangeBase] = Field(default=None, description="""Phase weighting range.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PIDElement']} })
    """Phase weighting range."""


class _PIDPhaseRangeBase(ConfiguredBaseModel):
    """
    Numeric min/max range for PID phase control.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:PIDPhaseRange',
         'from_schema': 'https://w3id.org/laura/schema/rf'})

    min: Optional[float] = Field(default=None, description="""Minimum value.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PIDPhaseRange']} })
    """Minimum value."""
    max: Optional[float] = Field(default=None, description="""Maximum value.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PIDPhaseRange']} })
    """Maximum value."""


class _PIDWeightRangeBase(_PIDPhaseRangeBase):
    """
    Numeric min/max range for PID phase weighting.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:PIDWeightRange',
         'from_schema': 'https://w3id.org/laura/schema/rf'})

    min: Optional[float] = Field(default=None, description="""Minimum value.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PIDPhaseRange']} })
    """Minimum value."""
    max: Optional[float] = Field(default=None, description="""Maximum value.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PIDPhaseRange']} })
    """Maximum value."""


class _TraceBase(ConfiguredBaseModel):
    """
    LLRF trace metadata.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:Trace', 'from_schema': 'https://w3id.org/laura/schema/rf'})

    data_size: Optional[int] = Field(default=None, description="""Number of points in a trace.""", validation_alias=AliasChoices('data_size', 'trace_data_size'), json_schema_extra = { "linkml_meta": {'aliases': ['trace_data_size'], 'domain_of': ['Trace']} })
    """Number of points in a trace."""
    data_count: Optional[int] = Field(default=None, description="""Number of one-record trace entries.""", validation_alias=AliasChoices('data_count', 'one_trace_data_count'), json_schema_extra = { "linkml_meta": {'aliases': ['one_trace_data_count'], 'domain_of': ['Trace']} })
    """Number of one-record trace entries."""
    data_chunk_size: Optional[int] = Field(default=None, description="""Chunk size for one-record traces.""", validation_alias=AliasChoices('data_chunk_size', 'one_trace_data_chunk_size'), json_schema_extra = { "linkml_meta": {'aliases': ['one_trace_data_chunk_size'], 'domain_of': ['Trace']} })
    """Chunk size for one-record traces."""
    number_of_start_zeros: Optional[int] = Field(default=None, description="""Number of leading zeros in a trace.""", validation_alias=AliasChoices('number_of_start_zeros', 'trace_num_of_start_zeros'), json_schema_extra = { "linkml_meta": {'aliases': ['trace_num_of_start_zeros'], 'domain_of': ['Trace']} })
    """Number of leading zeros in a trace."""


class _ChannelNamesBase(ConfiguredBaseModel):
    """
    Names for LLRF channels 1..8.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:ChannelNames',
         'from_schema': 'https://w3id.org/laura/schema/rf'})

    ch1: str = Field(default="", validation_alias=AliasChoices('ch1', 'CH1'), json_schema_extra = { "linkml_meta": {'aliases': ['CH1'], 'domain_of': ['ChannelNames'], 'ifabsent': 'string()'} })
    ch2: str = Field(default="", validation_alias=AliasChoices('ch2', 'CH2'), json_schema_extra = { "linkml_meta": {'aliases': ['CH2'], 'domain_of': ['ChannelNames'], 'ifabsent': 'string()'} })
    ch3: str = Field(default="", validation_alias=AliasChoices('ch3', 'CH3'), json_schema_extra = { "linkml_meta": {'aliases': ['CH3'], 'domain_of': ['ChannelNames'], 'ifabsent': 'string()'} })
    ch4: str = Field(default="", validation_alias=AliasChoices('ch4', 'CH4'), json_schema_extra = { "linkml_meta": {'aliases': ['CH4'], 'domain_of': ['ChannelNames'], 'ifabsent': 'string()'} })
    ch5: str = Field(default="", validation_alias=AliasChoices('ch5', 'CH5'), json_schema_extra = { "linkml_meta": {'aliases': ['CH5'], 'domain_of': ['ChannelNames'], 'ifabsent': 'string()'} })
    ch6: str = Field(default="", validation_alias=AliasChoices('ch6', 'CH6'), json_schema_extra = { "linkml_meta": {'aliases': ['CH6'], 'domain_of': ['ChannelNames'], 'ifabsent': 'string()'} })
    ch7: str = Field(default="", validation_alias=AliasChoices('ch7', 'CH7'), json_schema_extra = { "linkml_meta": {'aliases': ['CH7'], 'domain_of': ['ChannelNames'], 'ifabsent': 'string()'} })
    ch8: str = Field(default="", validation_alias=AliasChoices('ch8', 'CH8'), json_schema_extra = { "linkml_meta": {'aliases': ['CH8'], 'domain_of': ['ChannelNames'], 'ifabsent': 'string()'} })


class _LLRFTimingBase(ConfiguredBaseModel):
    """
    Start/end window timing definition.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:LLRFTiming',
         'from_schema': 'https://w3id.org/laura/schema/rf'})

    start: Optional[float] = Field(default=None, description="""Start time.""", json_schema_extra = { "linkml_meta": {'domain_of': ['LLRFTiming']} })
    """Start time."""
    end: Optional[float] = Field(default=None, description="""End time.""", json_schema_extra = { "linkml_meta": {'domain_of': ['LLRFTiming']} })
    """End time."""


class _LLRFTimingsBase(ConfiguredBaseModel):
    """
    Collection of timing windows for key LLRF channels.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:LLRFTimings',
         'from_schema': 'https://w3id.org/laura/schema/rf'})

    klystron_forward: Optional[_LLRFTimingBase] = Field(default=None, description="""Timing for klystron forward power.""", json_schema_extra = { "linkml_meta": {'domain_of': ['LLRFTimings']} })
    """Timing for klystron forward power."""
    klystron_reverse: Optional[_LLRFTimingBase] = Field(default=None, description="""Timing for klystron reverse power.""", json_schema_extra = { "linkml_meta": {'domain_of': ['LLRFTimings']} })
    """Timing for klystron reverse power."""
    cavity_forward: Optional[_LLRFTimingBase] = Field(default=None, description="""Timing for cavity forward power.""", json_schema_extra = { "linkml_meta": {'domain_of': ['LLRFTimings']} })
    """Timing for cavity forward power."""
    cavity_reverse: Optional[_LLRFTimingBase] = Field(default=None, description="""Timing for cavity reverse power.""", json_schema_extra = { "linkml_meta": {'domain_of': ['LLRFTimings']} })
    """Timing for cavity reverse power."""
    cavity_probe: Optional[_LLRFTimingBase] = Field(default=None, description="""Timing for cavity probe.""", json_schema_extra = { "linkml_meta": {'domain_of': ['LLRFTimings']} })
    """Timing for cavity probe."""


class _LowLevelRFElementBase(ConfiguredBaseModel):
    """
    Low-level RF (LLRF) system parameters.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:LowLevelRFElement',
         'from_schema': 'https://w3id.org/laura/schema/rf'})

    trace: Optional[_TraceBase] = Field(default=None, description="""Trace metadata.""", json_schema_extra = { "linkml_meta": {'domain_of': ['LowLevelRFElement']} })
    """Trace metadata."""
    max_amplitude: Optional[float] = Field(default=None, description="""Maximum allowed amplitude.""", validation_alias=AliasChoices('max_amplitude', 'MAX_AMPLITUDE'), json_schema_extra = { "linkml_meta": {'aliases': ['MAX_AMPLITUDE'], 'domain_of': ['LowLevelRFElement']} })
    """Maximum allowed amplitude."""
    channel_names: Optional[_ChannelNamesBase] = Field(default=None, description="""Channel labels.""", json_schema_extra = { "linkml_meta": {'domain_of': ['LowLevelRFElement']} })
    """Channel labels."""
    crest_phase: Optional[float] = Field(default=None, description="""Cavity crest phase.""", json_schema_extra = { "linkml_meta": {'domain_of': ['LowLevelRFElement']} })
    """Cavity crest phase."""
    timings: Optional[_LLRFTimingsBase] = Field(default=None, description="""Timing windows for LLRF channels.""", json_schema_extra = { "linkml_meta": {'domain_of': ['LowLevelRFElement']} })
    """Timing windows for LLRF channels."""


class _RFModulatorElementBase(ConfiguredBaseModel):
    """
    RF modulator (klystron driver) parameters.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:RFModulatorElement',
         'from_schema': 'https://w3id.org/laura/schema/rf'})

    pass


class _RFProtectionElementBase(ConfiguredBaseModel):
    """
    RF protection system parameters.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:RFProtectionElement',
         'from_schema': 'https://w3id.org/laura/schema/rf'})

    prot_type: Optional[str] = Field(default=None, description="""Protection system type.""", json_schema_extra = { "linkml_meta": {'domain_of': ['RFProtectionElement']} })
    """Protection system type."""


class _RFHeartbeatElementBase(ConfiguredBaseModel):
    """
    RF heartbeat / timing-monitor element parameters.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:RFHeartbeatElement',
         'from_schema': 'https://w3id.org/laura/schema/rf'})

    pass


class _DiagnosticElementBase(ConfiguredBaseModel):
    """
    Base class for diagnostic instrument sub-models.  Concrete sub-models extend this with instrument-specific fields.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:DiagnosticElement',
         'from_schema': 'https://w3id.org/laura/schema/diagnostics'})

    pass


class _BPMDiagnosticElementBase(_DiagnosticElementBase):
    """
    Beam-position monitor (BPM) diagnostic data.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:BPMDiagnosticElement',
         'from_schema': 'https://w3id.org/laura/schema/diagnostics',
         'in_subset': ['diagnostic_properties']})

    type: str = Field(default="Stripline", description="""BPM type (e.g., ``Stripline``, ``Cavity``, ``Button``). Accepted in YAML as ``bpm_type``.""", validation_alias=AliasChoices('type', 'bpm_type'), json_schema_extra = { "linkml_meta": {'aliases': ['bpm_type'],
         'domain_of': ['BPMDiagnosticElement',
                       'BAMDiagnosticElement',
                       'PhotonIntensityMonitorDiagnostic',
                       'BLMDiagnosticElement',
                       'ScreenDiagnosticElement',
                       'ChargeDiagnosticElement',
                       'CameraDiagnosticElement'],
         'ifabsent': 'string(Stripline)'} })
    """BPM type (e.g., ``Stripline``, ``Cavity``, ``Button``). Accepted in YAML as ``bpm_type``."""


class _BAMDiagnosticElementBase(_DiagnosticElementBase):
    """
    Beam-arrival monitor (BAM) diagnostic data.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:BAMDiagnosticElement',
         'from_schema': 'https://w3id.org/laura/schema/diagnostics',
         'in_subset': ['diagnostic_properties']})

    type: str = Field(default="DESY", description="""BAM type. Accepted in YAML as ``bam_type``.""", validation_alias=AliasChoices('type', 'bam_type'), json_schema_extra = { "linkml_meta": {'aliases': ['bam_type'],
         'domain_of': ['BPMDiagnosticElement',
                       'BAMDiagnosticElement',
                       'PhotonIntensityMonitorDiagnostic',
                       'BLMDiagnosticElement',
                       'ScreenDiagnosticElement',
                       'ChargeDiagnosticElement',
                       'CameraDiagnosticElement'],
         'ifabsent': 'string(DESY)'} })
    """BAM type. Accepted in YAML as ``bam_type``."""


class _PhotonIntensityMonitorDiagnosticBase(_DiagnosticElementBase):
    """
    Photon intensity monitor diagnostic data.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:PhotonIntensityMonitorDiagnostic',
         'from_schema': 'https://w3id.org/laura/schema/diagnostics',
         'in_subset': ['diagnostic_properties']})

    type: str = Field(default="I0", description="""Photon intensity monitor type. Accepted in YAML as ``intensity_monitor_type``.""", validation_alias=AliasChoices('type', 'intensity_monitor_type'), json_schema_extra = { "linkml_meta": {'aliases': ['intensity_monitor_type'],
         'domain_of': ['BPMDiagnosticElement',
                       'BAMDiagnosticElement',
                       'PhotonIntensityMonitorDiagnostic',
                       'BLMDiagnosticElement',
                       'ScreenDiagnosticElement',
                       'ChargeDiagnosticElement',
                       'CameraDiagnosticElement'],
         'ifabsent': 'string(I0)'} })
    """Photon intensity monitor type. Accepted in YAML as ``intensity_monitor_type``."""
    intensity: float = Field(default=0.0, description="""Measured photon intensity.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PhotonIntensityMonitorDiagnostic'], 'ifabsent': 'float(0.0)'} })
    """Measured photon intensity."""


class _BLMDiagnosticElementBase(_DiagnosticElementBase):
    """
    Bunch-length monitor (BLM) diagnostic data.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:BLMDiagnosticElement',
         'from_schema': 'https://w3id.org/laura/schema/diagnostics',
         'in_subset': ['diagnostic_properties']})

    type: str = Field(default="CDR", description="""BLM type (e.g., ``CDR``). Accepted in YAML as ``blm_type``.""", validation_alias=AliasChoices('type', 'blm_type'), json_schema_extra = { "linkml_meta": {'aliases': ['blm_type'],
         'domain_of': ['BPMDiagnosticElement',
                       'BAMDiagnosticElement',
                       'PhotonIntensityMonitorDiagnostic',
                       'BLMDiagnosticElement',
                       'ScreenDiagnosticElement',
                       'ChargeDiagnosticElement',
                       'CameraDiagnosticElement'],
         'ifabsent': 'string(CDR)'} })
    """BLM type (e.g., ``CDR``). Accepted in YAML as ``blm_type``."""


class _ScreenDiagnosticElementBase(_DiagnosticElementBase):
    """
    Scintillator or OTR screen diagnostic data.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:ScreenDiagnosticElement',
         'from_schema': 'https://w3id.org/laura/schema/diagnostics',
         'in_subset': ['diagnostic_properties']})

    type: str = Field(default="CLARA_HV_MOVER", description="""Screen type (e.g., ``OTR``, ``YAG``).""", validation_alias=AliasChoices('type', 'screen_type'), json_schema_extra = { "linkml_meta": {'aliases': ['screen_type'],
         'domain_of': ['BPMDiagnosticElement',
                       'BAMDiagnosticElement',
                       'PhotonIntensityMonitorDiagnostic',
                       'BLMDiagnosticElement',
                       'ScreenDiagnosticElement',
                       'ChargeDiagnosticElement',
                       'CameraDiagnosticElement'],
         'ifabsent': 'string(CLARA_HV_MOVER)'} })
    """Screen type (e.g., ``OTR``, ``YAG``)."""
    has_camera: Optional[bool] = Field(default=True, description="""Whether the screen has an associated camera.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ScreenDiagnosticElement'], 'ifabsent': 'True'} })
    """Whether the screen has an associated camera."""
    camera_name: str = Field(default="", description="""Name of the associated camera element.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ScreenDiagnosticElement'], 'ifabsent': 'string()'} })
    """Name of the associated camera element."""
    devices: list[str] = Field(default_factory=list, description="""List of attached devices.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ScreenDiagnosticElement']} })
    """List of attached devices."""


class _ChargeDiagnosticElementBase(_DiagnosticElementBase):
    """
    Charge-measurement diagnostic data (base for ICT, FCM, WCM).
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:ChargeDiagnosticElement',
         'from_schema': 'https://w3id.org/laura/schema/diagnostics',
         'in_subset': ['diagnostic_properties']})

    type: Optional[str] = Field(default=None, description="""Charge-diagnostic type. Accepted in YAML as ``charge_type``.""", validation_alias=AliasChoices('type', 'charge_type'), json_schema_extra = { "linkml_meta": {'aliases': ['charge_type'],
         'domain_of': ['BPMDiagnosticElement',
                       'BAMDiagnosticElement',
                       'PhotonIntensityMonitorDiagnostic',
                       'BLMDiagnosticElement',
                       'ScreenDiagnosticElement',
                       'ChargeDiagnosticElement',
                       'CameraDiagnosticElement']} })
    """Charge-diagnostic type. Accepted in YAML as ``charge_type``."""


class _CameraPixelResultsIndicesBase(ConfiguredBaseModel):
    """
    Indices into camera pixel-analysis result arrays.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:CameraPixelResultsIndices',
         'from_schema': 'https://w3id.org/laura/schema/diagnostics'})

    x: int = Field(default=0, description="""Beam centroid index in x.""", validation_alias=AliasChoices('x', 'X_POS'), json_schema_extra = { "linkml_meta": {'aliases': ['X_POS'],
         'domain_of': ['Position',
                       'CameraPixelResultsIndices',
                       'CameraPixelResultsNames'],
         'ifabsent': 'int(0)'} })
    """Beam centroid index in x."""
    y: int = Field(default=1, description="""Beam centroid index in y.""", validation_alias=AliasChoices('y', 'Y_POS'), json_schema_extra = { "linkml_meta": {'aliases': ['Y_POS'],
         'domain_of': ['Position',
                       'CameraPixelResultsIndices',
                       'CameraPixelResultsNames'],
         'ifabsent': 'int(1)'} })
    """Beam centroid index in y."""
    x_sigma: int = Field(default=2, description="""Beam sigma index in x.""", validation_alias=AliasChoices('x_sigma', 'X_SIGMA_POS'), json_schema_extra = { "linkml_meta": {'aliases': ['X_SIGMA_POS'],
         'domain_of': ['CameraPixelResultsIndices', 'CameraPixelResultsNames'],
         'ifabsent': 'int(2)'} })
    """Beam sigma index in x."""
    y_sigma: int = Field(default=3, description="""Beam sigma index in y.""", validation_alias=AliasChoices('y_sigma', 'Y_SIGMA_POS'), json_schema_extra = { "linkml_meta": {'aliases': ['Y_SIGMA_POS'],
         'domain_of': ['CameraPixelResultsIndices', 'CameraPixelResultsNames'],
         'ifabsent': 'int(3)'} })
    """Beam sigma index in y."""
    covariance: int = Field(default=4, description="""Beam covariance index.""", validation_alias=AliasChoices('covariance', 'COV_POS'), json_schema_extra = { "linkml_meta": {'aliases': ['COV_POS'],
         'domain_of': ['CameraPixelResultsIndices', 'CameraPixelResultsNames'],
         'ifabsent': 'int(4)'} })
    """Beam covariance index."""


class _CameraPixelResultsNamesBase(ConfiguredBaseModel):
    """
    Names of camera pixel-analysis result arrays.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:CameraPixelResultsNames',
         'from_schema': 'https://w3id.org/laura/schema/diagnostics'})

    x: str = Field(default="X", description="""Beam centroid name in x.""", validation_alias=AliasChoices('x', 'X_NAME'), json_schema_extra = { "linkml_meta": {'aliases': ['X_NAME'],
         'domain_of': ['Position',
                       'CameraPixelResultsIndices',
                       'CameraPixelResultsNames'],
         'ifabsent': 'string(X)'} })
    """Beam centroid name in x."""
    y: str = Field(default="Y", description="""Beam centroid name in y.""", validation_alias=AliasChoices('y', 'Y_NAME'), json_schema_extra = { "linkml_meta": {'aliases': ['Y_NAME'],
         'domain_of': ['Position',
                       'CameraPixelResultsIndices',
                       'CameraPixelResultsNames'],
         'ifabsent': 'string(Y)'} })
    """Beam centroid name in y."""
    x_sigma: str = Field(default="X_SIGMA", description="""Beam sigma name in x.""", validation_alias=AliasChoices('x_sigma', 'X_SIGMA_NAME'), json_schema_extra = { "linkml_meta": {'aliases': ['X_SIGMA_NAME'],
         'domain_of': ['CameraPixelResultsIndices', 'CameraPixelResultsNames'],
         'ifabsent': 'string(X_SIGMA)'} })
    """Beam sigma name in x."""
    y_sigma: str = Field(default="Y_SIGMA", description="""Beam sigma name in y.""", validation_alias=AliasChoices('y_sigma', 'Y_SIGMA_NAME'), json_schema_extra = { "linkml_meta": {'aliases': ['Y_SIGMA_NAME'],
         'domain_of': ['CameraPixelResultsIndices', 'CameraPixelResultsNames'],
         'ifabsent': 'string(Y_SIGMA)'} })
    """Beam sigma name in y."""
    covariance: str = Field(default="COV", description="""Beam covariance name.""", validation_alias=AliasChoices('covariance', 'COV_NAME'), json_schema_extra = { "linkml_meta": {'aliases': ['COV_NAME'],
         'domain_of': ['CameraPixelResultsIndices', 'CameraPixelResultsNames'],
         'ifabsent': 'string(COV)'} })
    """Beam covariance name."""


class _CameraMaskBase(ConfiguredBaseModel):
    """
    Camera analysis mask parameters.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:CameraMask',
         'from_schema': 'https://w3id.org/laura/schema/diagnostics'})

    middle: list[float] = Field(default_factory=list, description="""Center of the mask in pixels [x, y].""", validation_alias=AliasChoices('middle', 'position', 'centre'), json_schema_extra = { "linkml_meta": {'domain_of': ['PhysicalElement', 'CameraMask', 'CameraSensor']} })
    """Center of the mask in pixels [x, y]."""
    radius: list[float] = Field(default_factory=list, description="""Mask radius in pixels [x, y].""", json_schema_extra = { "linkml_meta": {'domain_of': ['ApertureElement', 'Multipole', 'CameraMask']} })
    """Mask radius in pixels [x, y]."""
    maximum: list[float] = Field(default_factory=list, description="""Maximum mask radius in pixels [x, y].""", json_schema_extra = { "linkml_meta": {'domain_of': ['CameraMask', 'CameraSensor', 'LaserAttenuator']} })
    """Maximum mask radius in pixels [x, y]."""
    use_maximum_values: Optional[bool] = Field(default=True, description="""If True, use maximum mask radius constraints.""", validation_alias=AliasChoices('use_maximum_values', 'USE_MASK_RAD_LIMITS'), json_schema_extra = { "linkml_meta": {'aliases': ['USE_MASK_RAD_LIMITS'],
         'domain_of': ['CameraMask'],
         'ifabsent': 'True'} })
    """If True, use maximum mask radius constraints."""


class _CameraSensorBase(ConfiguredBaseModel):
    """
    Camera sensor hardware configuration.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:CameraSensor',
         'from_schema': 'https://w3id.org/laura/schema/diagnostics'})

    x_pixels: int = Field(default=2160, description="""Raw sensor pixel count in x.""", validation_alias=AliasChoices('x_pixels', 'BINARY_NUM_PIX_X'), json_schema_extra = { "linkml_meta": {'aliases': ['BINARY_NUM_PIX_X'],
         'domain_of': ['CameraSensor', 'CameraDiagnosticElement'],
         'ifabsent': 'int(2160)'} })
    """Raw sensor pixel count in x."""
    y_pixels: int = Field(default=2560, description="""Raw sensor pixel count in y.""", validation_alias=AliasChoices('y_pixels', 'BINARY_NUM_PIX_Y'), json_schema_extra = { "linkml_meta": {'aliases': ['BINARY_NUM_PIX_Y'],
         'domain_of': ['CameraSensor', 'CameraDiagnosticElement'],
         'ifabsent': 'int(2560)'} })
    """Raw sensor pixel count in y."""
    x_scale_factor: int = Field(default=2, description="""Pixel binning factor in x.""", validation_alias=AliasChoices('x_scale_factor', 'X_PIX_SCALE_FACTOR'), json_schema_extra = { "linkml_meta": {'aliases': ['X_PIX_SCALE_FACTOR'],
         'domain_of': ['CameraSensor'],
         'ifabsent': 'int(2)'} })
    """Pixel binning factor in x."""
    y_scale_factor: int = Field(default=2, description="""Pixel binning factor in y.""", validation_alias=AliasChoices('y_scale_factor', 'Y_PIX_SCALE_FACTOR'), json_schema_extra = { "linkml_meta": {'aliases': ['Y_PIX_SCALE_FACTOR'],
         'domain_of': ['CameraSensor'],
         'ifabsent': 'int(2)'} })
    """Pixel binning factor in y."""
    beam_pixel_average: float = Field(default=97.2, description="""Average pixel value for beam detection.""", validation_alias=AliasChoices('beam_pixel_average', 'AVG_PIXEL_VALUE_FOR_BEAM'), json_schema_extra = { "linkml_meta": {'aliases': ['AVG_PIXEL_VALUE_FOR_BEAM'],
         'domain_of': ['CameraSensor'],
         'ifabsent': 'float(97.2)'} })
    """Average pixel value for beam detection."""
    middle: list[float] = Field(default_factory=list, description="""Sensor optical center in pixels [x, y].""", validation_alias=AliasChoices('middle', 'position', 'centre'), json_schema_extra = { "linkml_meta": {'domain_of': ['PhysicalElement', 'CameraMask', 'CameraSensor']} })
    """Sensor optical center in pixels [x, y]."""
    x_pixels_to_mm: float = Field(default=0.0134, description="""Pixel-to-mm scale factor in x.""", json_schema_extra = { "linkml_meta": {'domain_of': ['CameraSensor'], 'ifabsent': 'float(0.0134)'} })
    """Pixel-to-mm scale factor in x."""
    y_pixels_to_mm: float = Field(default=0.0134, description="""Pixel-to-mm scale factor in y.""", json_schema_extra = { "linkml_meta": {'domain_of': ['CameraSensor'], 'ifabsent': 'float(0.0134)'} })
    """Pixel-to-mm scale factor in y."""
    minimum: list[float] = Field(default_factory=list, description="""Minimum pixel positions [x, y].""", json_schema_extra = { "linkml_meta": {'domain_of': ['CameraSensor', 'LaserAttenuator']} })
    """Minimum pixel positions [x, y]."""
    maximum: list[float] = Field(default_factory=list, description="""Maximum pixel positions [x, y].""", json_schema_extra = { "linkml_meta": {'domain_of': ['CameraMask', 'CameraSensor', 'LaserAttenuator']} })
    """Maximum pixel positions [x, y]."""
    bit_depth: int = Field(default=16, description="""Camera bit depth.""", json_schema_extra = { "linkml_meta": {'domain_of': ['CameraSensor'], 'ifabsent': 'int(16)'} })
    """Camera bit depth."""
    operating_middle: list[float] = Field(default_factory=list, description="""Operating center positions in pixels [x, y].""", json_schema_extra = { "linkml_meta": {'domain_of': ['CameraSensor']} })
    """Operating center positions in pixels [x, y]."""
    mechanical_middle: list[float] = Field(default_factory=list, description="""Mechanical center of the camera in pixels [x, y].""", json_schema_extra = { "linkml_meta": {'domain_of': ['CameraSensor']} })
    """Mechanical center of the camera in pixels [x, y]."""


class _CameraDiagnosticElementBase(_DiagnosticElementBase):
    """
    Camera diagnostic data, including sensor parameters, analysis mask, and pixel-to-mm scale factors.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:CameraDiagnosticElement',
         'from_schema': 'https://w3id.org/laura/schema/diagnostics',
         'in_subset': ['diagnostic_properties']})

    type: Optional[str] = Field(default=None, description="""Camera type / model string (e.g., ``PCO``, ``Manta``). Accepted in YAML as ``CAM_TYPE``.""", validation_alias=AliasChoices('type', 'CAM_TYPE'), json_schema_extra = { "linkml_meta": {'aliases': ['CAM_TYPE'],
         'domain_of': ['BPMDiagnosticElement',
                       'BAMDiagnosticElement',
                       'PhotonIntensityMonitorDiagnostic',
                       'BLMDiagnosticElement',
                       'ScreenDiagnosticElement',
                       'ChargeDiagnosticElement',
                       'CameraDiagnosticElement']} })
    """Camera type / model string (e.g., ``PCO``, ``Manta``). Accepted in YAML as ``CAM_TYPE``."""
    x_pixels: int = Field(default=1080, description="""Image width reported by the control system [pix].""", validation_alias=AliasChoices('x_pixels', 'ARRAY_DATA_NUM_PIX_X', 'epics_x_pixels'), json_schema_extra = { "linkml_meta": {'aliases': ['ARRAY_DATA_NUM_PIX_X', 'epics_x_pixels'],
         'domain_of': ['CameraSensor', 'CameraDiagnosticElement'],
         'ifabsent': 'int(1080)'} })
    """Image width reported by the control system [pix]."""
    y_pixels: int = Field(default=1280, description="""Image height reported by the control system [pix].""", validation_alias=AliasChoices('y_pixels', 'ARRAY_DATA_NUM_PIX_Y', 'epics_y_pixels'), json_schema_extra = { "linkml_meta": {'aliases': ['ARRAY_DATA_NUM_PIX_Y', 'epics_y_pixels'],
         'domain_of': ['CameraSensor', 'CameraDiagnosticElement'],
         'ifabsent': 'int(1280)'} })
    """Image height reported by the control system [pix]."""
    rotation: float = Field(default=0, description="""Camera rotation relative to the screen plane [deg].""", json_schema_extra = { "linkml_meta": {'domain_of': ['ElementPositionError',
                       'ElementSurvey',
                       'PhysicalElement',
                       'CameraDiagnosticElement'],
         'ifabsent': 'float(0)',
         'unit': {'ucum_code': 'deg'}} })
    """Camera rotation relative to the screen plane [deg]."""
    flipped_horizontally: Optional[bool] = Field(default=True, description="""True if the image is mirrored left-right.""", validation_alias=AliasChoices('flipped_horizontally', 'IMAGE_FLIP_LR'), json_schema_extra = { "linkml_meta": {'aliases': ['IMAGE_FLIP_LR'],
         'domain_of': ['CameraDiagnosticElement'],
         'ifabsent': 'True'} })
    """True if the image is mirrored left-right."""
    flipped_vertically: Optional[bool] = Field(default=False, description="""True if the image is mirrored top-bottom.""", validation_alias=AliasChoices('flipped_vertically', 'IMAGE_FLIP_UD'), json_schema_extra = { "linkml_meta": {'aliases': ['IMAGE_FLIP_UD'],
         'domain_of': ['CameraDiagnosticElement'],
         'ifabsent': 'False'} })
    """True if the image is mirrored top-bottom."""
    screen_name: Optional[str] = Field(default=None, description="""Name of the screen element to which this camera is attached.""", json_schema_extra = { "linkml_meta": {'domain_of': ['CameraDiagnosticElement']} })
    """Name of the screen element to which this camera is attached."""
    has_led: Optional[bool] = Field(default=True, description="""True if the camera mount includes an LED backlight.""", json_schema_extra = { "linkml_meta": {'domain_of': ['CameraDiagnosticElement'], 'ifabsent': 'True'} })
    """True if the camera mount includes an LED backlight."""
    pixel_results_indices: Optional[_CameraPixelResultsIndicesBase] = Field(default=None, description="""Indices of pixel analysis result arrays.""", json_schema_extra = { "linkml_meta": {'domain_of': ['CameraDiagnosticElement']} })
    """Indices of pixel analysis result arrays."""
    pixel_results_names: Optional[_CameraPixelResultsNamesBase] = Field(default=None, description="""Names of pixel analysis result arrays.""", json_schema_extra = { "linkml_meta": {'domain_of': ['CameraDiagnosticElement']} })
    """Names of pixel analysis result arrays."""
    mask: Optional[_CameraMaskBase] = Field(default=None, description="""Camera analysis mask configuration.""", json_schema_extra = { "linkml_meta": {'domain_of': ['CameraDiagnosticElement']} })
    """Camera analysis mask configuration."""
    sensor: Optional[_CameraSensorBase] = Field(default=None, description="""Camera sensor hardware configuration.""", json_schema_extra = { "linkml_meta": {'domain_of': ['CameraDiagnosticElement']} })
    """Camera sensor hardware configuration."""


class _LaserMirrorElementBase(ConfiguredBaseModel):
    """
    Mirror steering parameters for a laser mirror.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:LaserMirrorElement',
         'from_schema': 'https://w3id.org/laura/schema/laser_plasma'})

    step_max: Optional[float] = Field(default=None, description="""Maximum step size for mirror adjustment.""", json_schema_extra = { "linkml_meta": {'domain_of': ['LaserMirrorElement']} })
    """Maximum step size for mirror adjustment."""
    sense: Optional[_LaserMirrorSenseBase] = Field(default=None, description="""Mirror sense/interlock configuration.""", json_schema_extra = { "linkml_meta": {'domain_of': ['LaserMirrorElement']} })
    """Mirror sense/interlock configuration."""
    vertical_channel: Optional[int] = Field(default=None, description="""Vertical control channel index.""", json_schema_extra = { "linkml_meta": {'domain_of': ['LaserMirrorElement']} })
    """Vertical control channel index."""
    horizontal_channel: Optional[int] = Field(default=None, description="""Horizontal control channel index.""", json_schema_extra = { "linkml_meta": {'domain_of': ['LaserMirrorElement']} })
    """Horizontal control channel index."""


class _LaserMirrorSenseBase(ConfiguredBaseModel):
    """
    Mirror sense switch values.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:LaserMirrorSense',
         'from_schema': 'https://w3id.org/laura/schema/laser_plasma'})

    left: Optional[float] = Field(default=None, description="""Left sense value.""", validation_alias=AliasChoices('left', 'left_sense'), json_schema_extra = { "linkml_meta": {'aliases': ['left_sense'], 'domain_of': ['LaserMirrorSense']} })
    """Left sense value."""
    right: Optional[float] = Field(default=None, description="""Right sense value.""", validation_alias=AliasChoices('right', 'right_sense'), json_schema_extra = { "linkml_meta": {'aliases': ['right_sense'], 'domain_of': ['LaserMirrorSense']} })
    """Right sense value."""
    up: Optional[float] = Field(default=None, description="""Up sense value.""", validation_alias=AliasChoices('up', 'up_sense'), json_schema_extra = { "linkml_meta": {'aliases': ['up_sense'], 'domain_of': ['LaserMirrorSense']} })
    """Up sense value."""
    down: Optional[float] = Field(default=None, description="""Down sense value.""", validation_alias=AliasChoices('down', 'down_sense'), json_schema_extra = { "linkml_meta": {'aliases': ['down_sense'], 'domain_of': ['LaserMirrorSense']} })
    """Down sense value."""


class _LaserElementBase(ConfiguredBaseModel):
    """
    Laser-beam parameters (wavelength, pulse energy, profile, etc.) for a laser element or laser-driven plasma stage.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:LaserElement',
         'from_schema': 'https://w3id.org/laura/schema/laser_plasma',
         'in_subset': ['laser_properties']})

    initial_position: float = Field(default=0, description="""Initial longitudinal position of the laser pulse [m].""", json_schema_extra = { "linkml_meta": {'domain_of': ['LaserElement'],
         'ifabsent': 'float(0)',
         'unit': {'ucum_code': 'm'}} })
    """Initial longitudinal position of the laser pulse [m]."""
    waist: float = Field(default=0, description="""Laser beam waist (1/e^2 radius) [m].""", ge=0.0, json_schema_extra = { "linkml_meta": {'domain_of': ['LaserElement'],
         'ifabsent': 'float(0)',
         'unit': {'ucum_code': 'm'}} })
    """Laser beam waist (1/e^2 radius) [m]."""
    wavelength: Optional[float] = Field(default=None, description="""Laser wavelength [m].""", ge=0.0, json_schema_extra = { "linkml_meta": {'domain_of': ['LaserElement'], 'unit': {'ucum_code': 'm'}} })
    """Laser wavelength [m]."""
    pulse_energy: Optional[float] = Field(default=None, description="""Laser pulse energy [J].""", ge=0.0, json_schema_extra = { "linkml_meta": {'domain_of': ['LaserElement'], 'unit': {'ucum_code': 'J'}} })
    """Laser pulse energy [J]."""
    pulse_duration_fwhm: Optional[float] = Field(default=None, description="""Pulse duration at FWHM [s].""", ge=0.0, json_schema_extra = { "linkml_meta": {'domain_of': ['LaserElement'], 'unit': {'ucum_code': 's'}} })
    """Pulse duration at FWHM [s]."""
    focal_position: float = Field(default=0.0, description="""Focal (waist) position along the propagation axis [m].""", json_schema_extra = { "linkml_meta": {'domain_of': ['LaserElement'],
         'ifabsent': 'float(0.0)',
         'unit': {'ucum_code': 'm'}} })
    """Focal (waist) position along the propagation axis [m]."""
    cep_phase: float = Field(default=0, description="""Carrier-envelope phase [rad].""", json_schema_extra = { "linkml_meta": {'domain_of': ['LaserElement'],
         'ifabsent': 'float(0)',
         'unit': {'ucum_code': 'rad'}} })
    """Carrier-envelope phase [rad]."""
    polarization: Optional[LaserPolarizationEnum] = Field(default=None, description="""Laser polarization state.""", json_schema_extra = { "linkml_meta": {'domain_of': ['LaserElement']} })
    """Laser polarization state."""
    profile_type: Optional[LaserProfileTypeEnum] = Field(default=LaserProfileTypeEnum.gaussian, description="""Transverse intensity profile model.""", json_schema_extra = { "linkml_meta": {'domain_of': ['LaserElement'], 'ifabsent': 'string(gaussian)'} })
    """Transverse intensity profile model."""
    laguerre_polynomial_order_p: int = Field(default=0, description="""Radial Laguerre-Gaussian mode index p (for ``profile_type = laguerre-gaussian``).""", ge=0, json_schema_extra = { "linkml_meta": {'domain_of': ['LaserElement'], 'ifabsent': 'int(0)'} })
    """Radial Laguerre-Gaussian mode index p (for ``profile_type = laguerre-gaussian``)."""
    flatness: int = Field(default=6, description="""Flatness order N of a flattened-Gaussian profile (for ``profile_type = flattened-gaussian``).""", ge=1, json_schema_extra = { "linkml_meta": {'domain_of': ['LaserElement'], 'ifabsent': 'int(6)'} })
    """Flatness order N of a flattened-Gaussian profile (for ``profile_type = flattened-gaussian``)."""


class _LaserEnergyMeterElementBase(ConfiguredBaseModel):
    """
    Laser energy-meter sub-model (no additional fields).
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:LaserEnergyMeterElement',
         'from_schema': 'https://w3id.org/laura/schema/laser_plasma'})

    pass


class _LaserHalfWavePlateElementBase(ConfiguredBaseModel):
    """
    Half-wave plate sub-model (no additional fields).
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:LaserHalfWavePlateElement',
         'from_schema': 'https://w3id.org/laura/schema/laser_plasma'})

    pass


class _PlasmaElementBase(ConfiguredBaseModel):
    """
    Plasma channel parameters for a laser-driven plasma-accelerator stage.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:PlasmaElement',
         'from_schema': 'https://w3id.org/laura/schema/laser_plasma'})

    density: Optional[float] = Field(default=None, description="""Plasma (electron) number density [m^-^3].""", ge=0.0, json_schema_extra = { "linkml_meta": {'domain_of': ['PlasmaElement'], 'unit': {'ucum_code': 'm-3'}} })
    """Plasma (electron) number density [m^-^3]."""
    species: str = Field(default="electron", description="""Plasma species name (e.g., ``electron``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['PlasmaElement'], 'ifabsent': 'string(electron)'} })
    """Plasma species name (e.g., ``electron``)."""
    ramp_up: float = Field(default=0.001, description="""Entrance density-ramp length [m].""", ge=0.0, json_schema_extra = { "linkml_meta": {'domain_of': ['PlasmaElement'],
         'ifabsent': 'float(0.001)',
         'unit': {'ucum_code': 'm'}} })
    """Entrance density-ramp length [m]."""
    plateau: float = Field(default=0.001, description="""Flat-top plateau length [m].""", ge=0.0, json_schema_extra = { "linkml_meta": {'domain_of': ['PlasmaElement'],
         'ifabsent': 'float(0.001)',
         'unit': {'ucum_code': 'm'}} })
    """Flat-top plateau length [m]."""
    ramp_down: float = Field(default=0.001, description="""Exit density-ramp length [m].""", ge=0.0, json_schema_extra = { "linkml_meta": {'domain_of': ['PlasmaElement'],
         'ifabsent': 'float(0.001)',
         'unit': {'ucum_code': 'm'}} })
    """Exit density-ramp length [m]."""
    ramp_decay_length: float = Field(default=0.001, description="""Exponential decay length of the density ramp [m].""", ge=0.0, json_schema_extra = { "linkml_meta": {'domain_of': ['PlasmaElement'],
         'ifabsent': 'float(0.001)',
         'unit': {'ucum_code': 'm'}} })
    """Exponential decay length of the density ramp [m]."""
    density_profile: Optional[bool] = Field(default=False, description="""If True, use a user-defined profile; if False, use a flat-top model.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PlasmaElement'], 'ifabsent': 'False'} })
    """If True, use a user-defined profile; if False, use a flat-top model."""
    parabolic_coefficient: float = Field(default=0, description="""Parabolic coefficient for a transverse density profile.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PlasmaElement'], 'ifabsent': 'float(0)'} })
    """Parabolic coefficient for a transverse density profile."""


class _DipoleMagnetBase(_MagneticElementBase):
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://w3id.org/laura/schema/magnetic',
         'slot_usage': {'order': {'equals_number': 0,
                                  'ifabsent': '0',
                                  'name': 'order'}}})

    order: int = Field(default=0, description="""Principal multipole order (0 = dipole, 1 = quad, ?)."""    , le=0, ge=0, json_schema_extra = { "linkml_meta": {'domain_of': ['Multipole', 'MagneticElement', 'Solenoid_Magnet'],
         'ifabsent': '0'} })
    """Principal multipole order (0 = dipole, 1 = quad, ?)."""
    skew: bool = Field(default=False, description="""Whether the magnet is rotated 45? to produce a skew field component.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Multipole', 'MagneticElement'], 'ifabsent': 'False'} })
    """Whether the magnet is rotated 45? to produce a skew field component."""
    length: float = Field(default=0, description="""Magnetic (effective) length [m].""", ge=0.0, validation_alias=AliasChoices('length', 'magnetic_length'), json_schema_extra = { "linkml_meta": {'aliases': ['magnetic_length'],
         'domain_of': ['PhysicalElement',
                       'MagneticElement',
                       'Solenoid_Magnet',
                       'Wiggler_Magnet',
                       'NonLinearLens_Magnet'],
         'ifabsent': 'float(0)',
         'unit': {'ucum_code': 'm'}} })
    """Magnetic (effective) length [m]."""
    multipoles: Optional[_MultipolesBase] = Field(default=None, description="""Integrated multipole field components.""", json_schema_extra = { "linkml_meta": {'domain_of': ['MagneticElement']} })
    """Integrated multipole field components."""
    systematic_multipoles: Optional[_MultipolesBase] = Field(default=None, description="""Systematic (design) multipole errors at the reference radius.""", json_schema_extra = { "linkml_meta": {'domain_of': ['MagneticElement']} })
    """Systematic (design) multipole errors at the reference radius."""
    random_multipoles: Optional[_MultipolesBase] = Field(default=None, description="""Random multipole errors at the reference radius.""", json_schema_extra = { "linkml_meta": {'domain_of': ['MagneticElement']} })
    """Random multipole errors at the reference radius."""
    field_integral_coefficients: Optional[_FieldIntegralBase] = Field(default=None, description="""Polynomial calibration of integrated field vs. current.""", json_schema_extra = { "linkml_meta": {'domain_of': ['MagneticElement', 'Solenoid_Magnet']} })
    """Polynomial calibration of integrated field vs. current."""
    linear_saturation_coefficients: Optional[_LinearSaturationFitBase] = Field(default=None, description="""Bi-linear saturation calibration.""", json_schema_extra = { "linkml_meta": {'domain_of': ['MagneticElement', 'Solenoid_Magnet']} })
    """Bi-linear saturation calibration."""
    settle_time: Optional[float] = Field(default=None, description="""Power-supply settle time after a change [s].""", json_schema_extra = { "linkml_meta": {'domain_of': ['MagneticElement', 'Solenoid_Magnet'],
         'unit': {'ucum_code': 's'}} })
    """Power-supply settle time after a change [s]."""
    entrance_edge_angle: Optional[Union[float, str]] = Field(default=None, description="""Fringe-field entrance edge angle [rad].""", json_schema_extra = { "linkml_meta": {'any_of': [{'range': 'float'}, {'range': 'string'}],
         'domain_of': ['MagneticElement'],
         'in_subset': ['functional_parameters', 'bend_angle_reference'],
         'unit': {'ucum_code': 'rad'}} })
    """Fringe-field entrance edge angle [rad]."""
    exit_edge_angle: Optional[Union[float, str]] = Field(default=None, description="""Fringe-field exit edge angle [rad].""", json_schema_extra = { "linkml_meta": {'any_of': [{'range': 'float'}, {'range': 'string'}],
         'domain_of': ['MagneticElement'],
         'in_subset': ['functional_parameters', 'bend_angle_reference'],
         'unit': {'ucum_code': 'rad'}} })
    """Fringe-field exit edge angle [rad]."""
    gap: float = Field(default=0.032, description="""Full gap between pole faces [m].""", ge=0.0, json_schema_extra = { "linkml_meta": {'domain_of': ['MagneticElement'],
         'ifabsent': 'float(0.032)',
         'unit': {'ucum_code': 'm'}} })
    """Full gap between pole faces [m]."""
    bore: float = Field(default=0.037, description="""Magnet bore radius [m].""", ge=0.0, json_schema_extra = { "linkml_meta": {'domain_of': ['MagneticElement'],
         'ifabsent': 'float(0.037)',
         'unit': {'ucum_code': 'm'}} })
    """Magnet bore radius [m]."""
    plane: Optional[BendingPlaneEnum] = Field(default=BendingPlaneEnum.Horizontal, description="""Principal bending / focusing plane (``Horizontal``, ``Vertical``, or ``Combined``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['MagneticElement'], 'ifabsent': 'string(Horizontal)'} })
    """Principal bending / focusing plane (``Horizontal``, ``Vertical``, or ``Combined``)."""
    width: float = Field(default=0.2, description="""Physical width of the magnet in the bending plane [m].""", json_schema_extra = { "linkml_meta": {'domain_of': ['BeamBeamSimulationElement', 'MagneticElement'],
         'ifabsent': 'float(0.2)',
         'unit': {'ucum_code': 'm'}} })
    """Physical width of the magnet in the bending plane [m]."""
    tilt: float = Field(default=0.0, description="""Global tilt about the beam axis [rad].""", json_schema_extra = { "linkml_meta": {'domain_of': ['ElectrostaticSeparatorSimulationElement',
                       'MagneticElement',],
         'ifabsent': 'float(0.0)',
         'unit': {'ucum_code': 'rad'}} })
    """Global tilt about the beam axis [rad]."""
    edge_field_integral: float = Field(default=0.5, description="""Enge fringe-field integral parameter (dimensionless).""", json_schema_extra = { "linkml_meta": {'domain_of': ['MagnetSimulationElement', 'MagneticElement'],
         'ifabsent': 'float(0.5)'} })
    """Enge fringe-field integral parameter (dimensionless)."""
    fringe_field_coefficient: float = Field(default=0.0, description="""Coefficient controlling the fringe-field roll-off rate.""", json_schema_extra = { "linkml_meta": {'domain_of': ['MagneticElement'], 'ifabsent': 'float(0.0)'} })
    """Coefficient controlling the fringe-field roll-off rate."""
    gradient: Optional[float] = Field(default=None, description="""Peak field gradient [T/m] (quads) or peak field [T] (dipoles).""", json_schema_extra = { "linkml_meta": {'domain_of': ['MagneticElement'], 'unit': {'ucum_code': 'T.m-1'}} })
    """Peak field gradient [T/m] (quads) or peak field [T] (dipoles)."""


class _QuadrupoleMagnetBase(_MagneticElementBase):
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://w3id.org/laura/schema/magnetic',
         'slot_usage': {'order': {'equals_number': 1,
                                  'ifabsent': '1',
                                  'name': 'order'}}})

    order: int = Field(default=1, description="""Principal multipole order (0 = dipole, 1 = quad, ?)."""    , le=1, ge=1, json_schema_extra = { "linkml_meta": {'domain_of': ['Multipole', 'MagneticElement', 'Solenoid_Magnet'],
         'ifabsent': '1'} })
    """Principal multipole order (0 = dipole, 1 = quad, ?)."""
    skew: bool = Field(default=False, description="""Whether the magnet is rotated 45? to produce a skew field component.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Multipole', 'MagneticElement'], 'ifabsent': 'False'} })
    """Whether the magnet is rotated 45? to produce a skew field component."""
    length: float = Field(default=0, description="""Magnetic (effective) length [m].""", ge=0.0, validation_alias=AliasChoices('length', 'magnetic_length'), json_schema_extra = { "linkml_meta": {'aliases': ['magnetic_length'],
         'domain_of': ['PhysicalElement',
                       'MagneticElement',
                       'Solenoid_Magnet',
                       'Wiggler_Magnet',
                       'NonLinearLens_Magnet'],
         'ifabsent': 'float(0)',
         'unit': {'ucum_code': 'm'}} })
    """Magnetic (effective) length [m]."""
    multipoles: Optional[_MultipolesBase] = Field(default=None, description="""Integrated multipole field components.""", json_schema_extra = { "linkml_meta": {'domain_of': ['MagneticElement']} })
    """Integrated multipole field components."""
    systematic_multipoles: Optional[_MultipolesBase] = Field(default=None, description="""Systematic (design) multipole errors at the reference radius.""", json_schema_extra = { "linkml_meta": {'domain_of': ['MagneticElement']} })
    """Systematic (design) multipole errors at the reference radius."""
    random_multipoles: Optional[_MultipolesBase] = Field(default=None, description="""Random multipole errors at the reference radius.""", json_schema_extra = { "linkml_meta": {'domain_of': ['MagneticElement']} })
    """Random multipole errors at the reference radius."""
    field_integral_coefficients: Optional[_FieldIntegralBase] = Field(default=None, description="""Polynomial calibration of integrated field vs. current.""", json_schema_extra = { "linkml_meta": {'domain_of': ['MagneticElement', 'Solenoid_Magnet']} })
    """Polynomial calibration of integrated field vs. current."""
    linear_saturation_coefficients: Optional[_LinearSaturationFitBase] = Field(default=None, description="""Bi-linear saturation calibration.""", json_schema_extra = { "linkml_meta": {'domain_of': ['MagneticElement', 'Solenoid_Magnet']} })
    """Bi-linear saturation calibration."""
    settle_time: Optional[float] = Field(default=None, description="""Power-supply settle time after a change [s].""", json_schema_extra = { "linkml_meta": {'domain_of': ['MagneticElement', 'Solenoid_Magnet'],
         'unit': {'ucum_code': 's'}} })
    """Power-supply settle time after a change [s]."""
    entrance_edge_angle: Optional[Union[float, str]] = Field(default=None, description="""Fringe-field entrance edge angle [rad].""", json_schema_extra = { "linkml_meta": {'any_of': [{'range': 'float'}, {'range': 'string'}],
         'domain_of': ['MagneticElement'],
         'in_subset': ['functional_parameters', 'bend_angle_reference'],
         'unit': {'ucum_code': 'rad'}} })
    """Fringe-field entrance edge angle [rad]."""
    exit_edge_angle: Optional[Union[float, str]] = Field(default=None, description="""Fringe-field exit edge angle [rad].""", json_schema_extra = { "linkml_meta": {'any_of': [{'range': 'float'}, {'range': 'string'}],
         'domain_of': ['MagneticElement'],
         'in_subset': ['functional_parameters', 'bend_angle_reference'],
         'unit': {'ucum_code': 'rad'}} })
    """Fringe-field exit edge angle [rad]."""
    gap: float = Field(default=0.032, description="""Full gap between pole faces [m].""", ge=0.0, json_schema_extra = { "linkml_meta": {'domain_of': ['MagneticElement'],
         'ifabsent': 'float(0.032)',
         'unit': {'ucum_code': 'm'}} })
    """Full gap between pole faces [m]."""
    bore: float = Field(default=0.037, description="""Magnet bore radius [m].""", ge=0.0, json_schema_extra = { "linkml_meta": {'domain_of': ['MagneticElement'],
         'ifabsent': 'float(0.037)',
         'unit': {'ucum_code': 'm'}} })
    """Magnet bore radius [m]."""
    plane: Optional[BendingPlaneEnum] = Field(default=BendingPlaneEnum.Horizontal, description="""Principal bending / focusing plane (``Horizontal``, ``Vertical``, or ``Combined``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['MagneticElement'], 'ifabsent': 'string(Horizontal)'} })
    """Principal bending / focusing plane (``Horizontal``, ``Vertical``, or ``Combined``)."""
    width: float = Field(default=0.2, description="""Physical width of the magnet in the bending plane [m].""", json_schema_extra = { "linkml_meta": {'domain_of': ['BeamBeamSimulationElement', 'MagneticElement'],
         'ifabsent': 'float(0.2)',
         'unit': {'ucum_code': 'm'}} })
    """Physical width of the magnet in the bending plane [m]."""
    tilt: float = Field(default=0.0, description="""Global tilt about the beam axis [rad].""", json_schema_extra = { "linkml_meta": {'domain_of': ['ElectrostaticSeparatorSimulationElement',
                       'MagneticElement',],
         'ifabsent': 'float(0.0)',
         'unit': {'ucum_code': 'rad'}} })
    """Global tilt about the beam axis [rad]."""
    edge_field_integral: float = Field(default=0.5, description="""Enge fringe-field integral parameter (dimensionless).""", json_schema_extra = { "linkml_meta": {'domain_of': ['MagnetSimulationElement', 'MagneticElement'],
         'ifabsent': 'float(0.5)'} })
    """Enge fringe-field integral parameter (dimensionless)."""
    fringe_field_coefficient: float = Field(default=0.0, description="""Coefficient controlling the fringe-field roll-off rate.""", json_schema_extra = { "linkml_meta": {'domain_of': ['MagneticElement'], 'ifabsent': 'float(0.0)'} })
    """Coefficient controlling the fringe-field roll-off rate."""
    gradient: Optional[float] = Field(default=None, description="""Peak field gradient [T/m] (quads) or peak field [T] (dipoles).""", json_schema_extra = { "linkml_meta": {'domain_of': ['MagneticElement'], 'unit': {'ucum_code': 'T.m-1'}} })
    """Peak field gradient [T/m] (quads) or peak field [T] (dipoles)."""


class _SextupoleMagnetBase(_MagneticElementBase):
    """
    Sextupole magnet field, principal multipole order 2.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://w3id.org/laura/schema/magnetic',
         'slot_usage': {'order': {'equals_number': 2,
                                  'ifabsent': '2',
                                  'name': 'order'}}})

    order: int = Field(default=2, description="""Principal multipole order (0 = dipole, 1 = quad, ?)."""    , le=2, ge=2, json_schema_extra = { "linkml_meta": {'domain_of': ['Multipole', 'MagneticElement', 'Solenoid_Magnet'],
         'ifabsent': '2'} })
    """Principal multipole order (0 = dipole, 1 = quad, ?)."""
    skew: bool = Field(default=False, description="""Whether the magnet is rotated 45? to produce a skew field component.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Multipole', 'MagneticElement'], 'ifabsent': 'False'} })
    """Whether the magnet is rotated 45? to produce a skew field component."""
    length: float = Field(default=0, description="""Magnetic (effective) length [m].""", ge=0.0, validation_alias=AliasChoices('length', 'magnetic_length'), json_schema_extra = { "linkml_meta": {'aliases': ['magnetic_length'],
         'domain_of': ['PhysicalElement',
                       'MagneticElement',
                       'Solenoid_Magnet',
                       'Wiggler_Magnet',
                       'NonLinearLens_Magnet'],
         'ifabsent': 'float(0)',
         'unit': {'ucum_code': 'm'}} })
    """Magnetic (effective) length [m]."""
    multipoles: Optional[_MultipolesBase] = Field(default=None, description="""Integrated multipole field components.""", json_schema_extra = { "linkml_meta": {'domain_of': ['MagneticElement']} })
    """Integrated multipole field components."""
    systematic_multipoles: Optional[_MultipolesBase] = Field(default=None, description="""Systematic (design) multipole errors at the reference radius.""", json_schema_extra = { "linkml_meta": {'domain_of': ['MagneticElement']} })
    """Systematic (design) multipole errors at the reference radius."""
    random_multipoles: Optional[_MultipolesBase] = Field(default=None, description="""Random multipole errors at the reference radius.""", json_schema_extra = { "linkml_meta": {'domain_of': ['MagneticElement']} })
    """Random multipole errors at the reference radius."""
    field_integral_coefficients: Optional[_FieldIntegralBase] = Field(default=None, description="""Polynomial calibration of integrated field vs. current.""", json_schema_extra = { "linkml_meta": {'domain_of': ['MagneticElement', 'Solenoid_Magnet']} })
    """Polynomial calibration of integrated field vs. current."""
    linear_saturation_coefficients: Optional[_LinearSaturationFitBase] = Field(default=None, description="""Bi-linear saturation calibration.""", json_schema_extra = { "linkml_meta": {'domain_of': ['MagneticElement', 'Solenoid_Magnet']} })
    """Bi-linear saturation calibration."""
    settle_time: Optional[float] = Field(default=None, description="""Power-supply settle time after a change [s].""", json_schema_extra = { "linkml_meta": {'domain_of': ['MagneticElement', 'Solenoid_Magnet'],
         'unit': {'ucum_code': 's'}} })
    """Power-supply settle time after a change [s]."""
    entrance_edge_angle: Optional[Union[float, str]] = Field(default=None, description="""Fringe-field entrance edge angle [rad].""", json_schema_extra = { "linkml_meta": {'any_of': [{'range': 'float'}, {'range': 'string'}],
         'domain_of': ['MagneticElement'],
         'in_subset': ['functional_parameters', 'bend_angle_reference'],
         'unit': {'ucum_code': 'rad'}} })
    """Fringe-field entrance edge angle [rad]."""
    exit_edge_angle: Optional[Union[float, str]] = Field(default=None, description="""Fringe-field exit edge angle [rad].""", json_schema_extra = { "linkml_meta": {'any_of': [{'range': 'float'}, {'range': 'string'}],
         'domain_of': ['MagneticElement'],
         'in_subset': ['functional_parameters', 'bend_angle_reference'],
         'unit': {'ucum_code': 'rad'}} })
    """Fringe-field exit edge angle [rad]."""
    gap: float = Field(default=0.032, description="""Full gap between pole faces [m].""", ge=0.0, json_schema_extra = { "linkml_meta": {'domain_of': ['MagneticElement'],
         'ifabsent': 'float(0.032)',
         'unit': {'ucum_code': 'm'}} })
    """Full gap between pole faces [m]."""
    bore: float = Field(default=0.037, description="""Magnet bore radius [m].""", ge=0.0, json_schema_extra = { "linkml_meta": {'domain_of': ['MagneticElement'],
         'ifabsent': 'float(0.037)',
         'unit': {'ucum_code': 'm'}} })
    """Magnet bore radius [m]."""
    plane: Optional[BendingPlaneEnum] = Field(default=BendingPlaneEnum.Horizontal, description="""Principal bending / focusing plane (``Horizontal``, ``Vertical``, or ``Combined``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['MagneticElement'], 'ifabsent': 'string(Horizontal)'} })
    """Principal bending / focusing plane (``Horizontal``, ``Vertical``, or ``Combined``)."""
    width: float = Field(default=0.2, description="""Physical width of the magnet in the bending plane [m].""", json_schema_extra = { "linkml_meta": {'domain_of': ['BeamBeamSimulationElement', 'MagneticElement'],
         'ifabsent': 'float(0.2)',
         'unit': {'ucum_code': 'm'}} })
    """Physical width of the magnet in the bending plane [m]."""
    tilt: float = Field(default=0.0, description="""Global tilt about the beam axis [rad].""", json_schema_extra = { "linkml_meta": {'domain_of': ['ElectrostaticSeparatorSimulationElement',
                       'MagneticElement',],
         'ifabsent': 'float(0.0)',
         'unit': {'ucum_code': 'rad'}} })
    """Global tilt about the beam axis [rad]."""
    edge_field_integral: float = Field(default=0.5, description="""Enge fringe-field integral parameter (dimensionless).""", json_schema_extra = { "linkml_meta": {'domain_of': ['MagnetSimulationElement', 'MagneticElement'],
         'ifabsent': 'float(0.5)'} })
    """Enge fringe-field integral parameter (dimensionless)."""
    fringe_field_coefficient: float = Field(default=0.0, description="""Coefficient controlling the fringe-field roll-off rate.""", json_schema_extra = { "linkml_meta": {'domain_of': ['MagneticElement'], 'ifabsent': 'float(0.0)'} })
    """Coefficient controlling the fringe-field roll-off rate."""
    gradient: Optional[float] = Field(default=None, description="""Peak field gradient [T/m] (quads) or peak field [T] (dipoles).""", json_schema_extra = { "linkml_meta": {'domain_of': ['MagneticElement'], 'unit': {'ucum_code': 'T.m-1'}} })
    """Peak field gradient [T/m] (quads) or peak field [T] (dipoles)."""
    angle: Optional[float] = Field(default=None, description="""Integrated bending angle [rad]. Dipoles only. Part of the data model (lattice YAML may set it), but derived from multipoles.K0L rather than stored: the MagneticElement wrapper implements it as a read/write property so a symbolic bend angle survives round-tripping and reads follow the global resolution mode. Listed in _PYDANTIC_EXCLUDED_SLOTS in generate_pydantic.py so the generated base does not also declare it as a field, which would make pydantic treat the property object as the field default.""", json_schema_extra = { "linkml_meta": {'domain_of': ['MagneticElement'], 'unit': {'ucum_code': 'rad'}} })
    """Integrated bending angle [rad]. Dipoles only. Part of the data model (lattice YAML may set it), but derived from multipoles.K0L rather than stored: the MagneticElement wrapper implements it as a read/write property so a symbolic bend angle survives round-tripping and reads follow the global resolution mode. Listed in _PYDANTIC_EXCLUDED_SLOTS in generate_pydantic.py so the generated base does not also declare it as a field, which would make pydantic treat the property object as the field default."""


class _OctupoleMagnetBase(_MagneticElementBase):
    """
    Octupole magnet field, principal multipole order 3.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://w3id.org/laura/schema/magnetic',
         'slot_usage': {'order': {'equals_number': 3,
                                  'ifabsent': '3',
                                  'name': 'order'}}})

    order: int = Field(default=3, description="""Principal multipole order (0 = dipole, 1 = quad, ?)."""    , le=3, ge=3, json_schema_extra = { "linkml_meta": {'domain_of': ['Multipole', 'MagneticElement', 'Solenoid_Magnet'],
         'ifabsent': '3'} })
    """Principal multipole order (0 = dipole, 1 = quad, ?)."""
    skew: bool = Field(default=False, description="""Whether the magnet is rotated 45? to produce a skew field component.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Multipole', 'MagneticElement'], 'ifabsent': 'False'} })
    """Whether the magnet is rotated 45? to produce a skew field component."""
    length: float = Field(default=0, description="""Magnetic (effective) length [m].""", ge=0.0, validation_alias=AliasChoices('length', 'magnetic_length'), json_schema_extra = { "linkml_meta": {'aliases': ['magnetic_length'],
         'domain_of': ['PhysicalElement',
                       'MagneticElement',
                       'Solenoid_Magnet',
                       'Wiggler_Magnet',
                       'NonLinearLens_Magnet'],
         'ifabsent': 'float(0)',
         'unit': {'ucum_code': 'm'}} })
    """Magnetic (effective) length [m]."""
    multipoles: Optional[_MultipolesBase] = Field(default=None, description="""Integrated multipole field components.""", json_schema_extra = { "linkml_meta": {'domain_of': ['MagneticElement']} })
    """Integrated multipole field components."""
    systematic_multipoles: Optional[_MultipolesBase] = Field(default=None, description="""Systematic (design) multipole errors at the reference radius.""", json_schema_extra = { "linkml_meta": {'domain_of': ['MagneticElement']} })
    """Systematic (design) multipole errors at the reference radius."""
    random_multipoles: Optional[_MultipolesBase] = Field(default=None, description="""Random multipole errors at the reference radius.""", json_schema_extra = { "linkml_meta": {'domain_of': ['MagneticElement']} })
    """Random multipole errors at the reference radius."""
    field_integral_coefficients: Optional[_FieldIntegralBase] = Field(default=None, description="""Polynomial calibration of integrated field vs. current.""", json_schema_extra = { "linkml_meta": {'domain_of': ['MagneticElement', 'Solenoid_Magnet']} })
    """Polynomial calibration of integrated field vs. current."""
    linear_saturation_coefficients: Optional[_LinearSaturationFitBase] = Field(default=None, description="""Bi-linear saturation calibration.""", json_schema_extra = { "linkml_meta": {'domain_of': ['MagneticElement', 'Solenoid_Magnet']} })
    """Bi-linear saturation calibration."""
    settle_time: Optional[float] = Field(default=None, description="""Power-supply settle time after a change [s].""", json_schema_extra = { "linkml_meta": {'domain_of': ['MagneticElement', 'Solenoid_Magnet'],
         'unit': {'ucum_code': 's'}} })
    """Power-supply settle time after a change [s]."""
    entrance_edge_angle: Optional[Union[float, str]] = Field(default=None, description="""Fringe-field entrance edge angle [rad].""", json_schema_extra = { "linkml_meta": {'any_of': [{'range': 'float'}, {'range': 'string'}],
         'domain_of': ['MagneticElement'],
         'in_subset': ['functional_parameters', 'bend_angle_reference'],
         'unit': {'ucum_code': 'rad'}} })
    """Fringe-field entrance edge angle [rad]."""
    exit_edge_angle: Optional[Union[float, str]] = Field(default=None, description="""Fringe-field exit edge angle [rad].""", json_schema_extra = { "linkml_meta": {'any_of': [{'range': 'float'}, {'range': 'string'}],
         'domain_of': ['MagneticElement'],
         'in_subset': ['functional_parameters', 'bend_angle_reference'],
         'unit': {'ucum_code': 'rad'}} })
    """Fringe-field exit edge angle [rad]."""
    gap: float = Field(default=0.032, description="""Full gap between pole faces [m].""", ge=0.0, json_schema_extra = { "linkml_meta": {'domain_of': ['MagneticElement'],
         'ifabsent': 'float(0.032)',
         'unit': {'ucum_code': 'm'}} })
    """Full gap between pole faces [m]."""
    bore: float = Field(default=0.037, description="""Magnet bore radius [m].""", ge=0.0, json_schema_extra = { "linkml_meta": {'domain_of': ['MagneticElement'],
         'ifabsent': 'float(0.037)',
         'unit': {'ucum_code': 'm'}} })
    """Magnet bore radius [m]."""
    plane: Optional[BendingPlaneEnum] = Field(default=BendingPlaneEnum.Horizontal, description="""Principal bending / focusing plane (``Horizontal``, ``Vertical``, or ``Combined``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['MagneticElement'], 'ifabsent': 'string(Horizontal)'} })
    """Principal bending / focusing plane (``Horizontal``, ``Vertical``, or ``Combined``)."""
    width: float = Field(default=0.2, description="""Physical width of the magnet in the bending plane [m].""", json_schema_extra = { "linkml_meta": {'domain_of': ['BeamBeamSimulationElement', 'MagneticElement'],
         'ifabsent': 'float(0.2)',
         'unit': {'ucum_code': 'm'}} })
    """Physical width of the magnet in the bending plane [m]."""
    tilt: float = Field(default=0.0, description="""Global tilt about the beam axis [rad].""", json_schema_extra = { "linkml_meta": {'domain_of': ['ElectrostaticSeparatorSimulationElement',
                       'MagneticElement',],
         'ifabsent': 'float(0.0)',
         'unit': {'ucum_code': 'rad'}} })
    """Global tilt about the beam axis [rad]."""
    edge_field_integral: float = Field(default=0.5, description="""Enge fringe-field integral parameter (dimensionless).""", json_schema_extra = { "linkml_meta": {'domain_of': ['MagnetSimulationElement', 'MagneticElement'],
         'ifabsent': 'float(0.5)'} })
    """Enge fringe-field integral parameter (dimensionless)."""
    fringe_field_coefficient: float = Field(default=0.0, description="""Coefficient controlling the fringe-field roll-off rate.""", json_schema_extra = { "linkml_meta": {'domain_of': ['MagneticElement'], 'ifabsent': 'float(0.0)'} })
    """Coefficient controlling the fringe-field roll-off rate."""
    gradient: Optional[float] = Field(default=None, description="""Peak field gradient [T/m] (quads) or peak field [T] (dipoles).""", json_schema_extra = { "linkml_meta": {'domain_of': ['MagneticElement'], 'unit': {'ucum_code': 'T.m-1'}} })
    """Peak field gradient [T/m] (quads) or peak field [T] (dipoles)."""
    angle: Optional[float] = Field(default=None, description="""Integrated bending angle [rad]. Dipoles only. Part of the data model (lattice YAML may set it), but derived from multipoles.K0L rather than stored: the MagneticElement wrapper implements it as a read/write property so a symbolic bend angle survives round-tripping and reads follow the global resolution mode. Listed in _PYDANTIC_EXCLUDED_SLOTS in generate_pydantic.py so the generated base does not also declare it as a field, which would make pydantic treat the property object as the field default.""", json_schema_extra = { "linkml_meta": {'domain_of': ['MagneticElement'], 'unit': {'ucum_code': 'rad'}} })
    """Integrated bending angle [rad]. Dipoles only. Part of the data model (lattice YAML may set it), but derived from multipoles.K0L rather than stored: the MagneticElement wrapper implements it as a read/write property so a symbolic bend angle survives round-tripping and reads follow the global resolution mode. Listed in _PYDANTIC_EXCLUDED_SLOTS in generate_pydantic.py so the generated base does not also declare it as a field, which would make pydantic treat the property object as the field default."""


class _CorrectorMagnetBase(_DipoleMagnetBase):
    """
    Steering-corrector field. A dipole magnet whose order-0 multipole is addressed by beam plane: the normal component is the horizontal kick and the skew component is the vertical kick. Inherits from  Dipole_Magnet / MagneticElement.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:Corrector_Magnet',
         'from_schema': 'https://w3id.org/laura/schema/magnetic'})

    order: int = Field(default=0, description="""Principal multipole order (0 = dipole, 1 = quad, ?)."""    , le=0, ge=0, json_schema_extra = { "linkml_meta": {'domain_of': ['Multipole', 'MagneticElement', 'Solenoid_Magnet'],
         'ifabsent': '0'} })
    """Principal multipole order (0 = dipole, 1 = quad, ?)."""
    skew: bool = Field(default=False, description="""Whether the magnet is rotated 45? to produce a skew field component.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Multipole', 'MagneticElement'], 'ifabsent': 'False'} })
    """Whether the magnet is rotated 45? to produce a skew field component."""
    length: float = Field(default=0, description="""Magnetic (effective) length [m].""", ge=0.0, validation_alias=AliasChoices('length', 'magnetic_length'), json_schema_extra = { "linkml_meta": {'aliases': ['magnetic_length'],
         'domain_of': ['PhysicalElement',
                       'MagneticElement',
                       'Solenoid_Magnet',
                       'Wiggler_Magnet',
                       'NonLinearLens_Magnet'],
         'ifabsent': 'float(0)',
         'unit': {'ucum_code': 'm'}} })
    """Magnetic (effective) length [m]."""
    multipoles: Optional[_MultipolesBase] = Field(default=None, description="""Integrated multipole field components.""", json_schema_extra = { "linkml_meta": {'domain_of': ['MagneticElement']} })
    """Integrated multipole field components."""
    systematic_multipoles: Optional[_MultipolesBase] = Field(default=None, description="""Systematic (design) multipole errors at the reference radius.""", json_schema_extra = { "linkml_meta": {'domain_of': ['MagneticElement']} })
    """Systematic (design) multipole errors at the reference radius."""
    random_multipoles: Optional[_MultipolesBase] = Field(default=None, description="""Random multipole errors at the reference radius.""", json_schema_extra = { "linkml_meta": {'domain_of': ['MagneticElement']} })
    """Random multipole errors at the reference radius."""
    field_integral_coefficients: Optional[_FieldIntegralBase] = Field(default=None, description="""Polynomial calibration of integrated field vs. current.""", json_schema_extra = { "linkml_meta": {'domain_of': ['MagneticElement', 'Solenoid_Magnet']} })
    """Polynomial calibration of integrated field vs. current."""
    linear_saturation_coefficients: Optional[_LinearSaturationFitBase] = Field(default=None, description="""Bi-linear saturation calibration.""", json_schema_extra = { "linkml_meta": {'domain_of': ['MagneticElement', 'Solenoid_Magnet']} })
    """Bi-linear saturation calibration."""
    settle_time: Optional[float] = Field(default=None, description="""Power-supply settle time after a change [s].""", json_schema_extra = { "linkml_meta": {'domain_of': ['MagneticElement', 'Solenoid_Magnet'],
         'unit': {'ucum_code': 's'}} })
    """Power-supply settle time after a change [s]."""
    entrance_edge_angle: Optional[Union[float, str]] = Field(default=None, description="""Fringe-field entrance edge angle [rad].""", json_schema_extra = { "linkml_meta": {'any_of': [{'range': 'float'}, {'range': 'string'}],
         'domain_of': ['MagneticElement'],
         'in_subset': ['functional_parameters', 'bend_angle_reference'],
         'unit': {'ucum_code': 'rad'}} })
    """Fringe-field entrance edge angle [rad]."""
    exit_edge_angle: Optional[Union[float, str]] = Field(default=None, description="""Fringe-field exit edge angle [rad].""", json_schema_extra = { "linkml_meta": {'any_of': [{'range': 'float'}, {'range': 'string'}],
         'domain_of': ['MagneticElement'],
         'in_subset': ['functional_parameters', 'bend_angle_reference'],
         'unit': {'ucum_code': 'rad'}} })
    """Fringe-field exit edge angle [rad]."""
    gap: float = Field(default=0.032, description="""Full gap between pole faces [m].""", ge=0.0, json_schema_extra = { "linkml_meta": {'domain_of': ['MagneticElement'],
         'ifabsent': 'float(0.032)',
         'unit': {'ucum_code': 'm'}} })
    """Full gap between pole faces [m]."""
    bore: float = Field(default=0.037, description="""Magnet bore radius [m].""", ge=0.0, json_schema_extra = { "linkml_meta": {'domain_of': ['MagneticElement'],
         'ifabsent': 'float(0.037)',
         'unit': {'ucum_code': 'm'}} })
    """Magnet bore radius [m]."""
    plane: Optional[BendingPlaneEnum] = Field(default=BendingPlaneEnum.Horizontal, description="""Principal bending / focusing plane (``Horizontal``, ``Vertical``, or ``Combined``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['MagneticElement'], 'ifabsent': 'string(Horizontal)'} })
    """Principal bending / focusing plane (``Horizontal``, ``Vertical``, or ``Combined``)."""
    width: float = Field(default=0.2, description="""Physical width of the magnet in the bending plane [m].""", json_schema_extra = { "linkml_meta": {'domain_of': ['MagneticElement'],
         'ifabsent': 'float(0.2)',
         'unit': {'ucum_code': 'm'}} })
    """Physical width of the magnet in the bending plane [m]."""
    tilt: float = Field(default=0.0, description="""Global tilt about the beam axis [rad].""", json_schema_extra = { "linkml_meta": {'domain_of': ['MagneticElement'],
         'ifabsent': 'float(0.0)',
         'unit': {'ucum_code': 'rad'}} })
    """Global tilt about the beam axis [rad]."""
    edge_field_integral: float = Field(default=0.5, description="""Enge fringe-field integral parameter (dimensionless).""", json_schema_extra = { "linkml_meta": {'domain_of': ['MagnetSimulationElement', 'MagneticElement'],
         'ifabsent': 'float(0.5)'} })
    """Enge fringe-field integral parameter (dimensionless)."""
    fringe_field_coefficient: float = Field(default=0.0, description="""Coefficient controlling the fringe-field roll-off rate.""", json_schema_extra = { "linkml_meta": {'domain_of': ['MagneticElement'], 'ifabsent': 'float(0.0)'} })
    """Coefficient controlling the fringe-field roll-off rate."""
    gradient: Optional[float] = Field(default=None, description="""Peak field gradient [T/m] (quads) or peak field [T] (dipoles).""", json_schema_extra = { "linkml_meta": {'domain_of': ['MagneticElement'], 'unit': {'ucum_code': 'T.m-1'}} })
    """Peak field gradient [T/m] (quads) or peak field [T] (dipoles)."""


class _CombinedCorrectorMagnetBase(ConfiguredBaseModel):
    """
    The pair of steering-corrector fields inside one combined corrector. The two planes are separate magnets with separate windings, so they must not share a magnetic model: in the CLARA magnet table the horizontal and vertical halves of a single unit have different slope [units/A] and different magnetic lengths, so one shared calibration converts current to angle correctly for at most one of the two planes.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:Combined_Corrector_Magnet',
         'from_schema': 'https://w3id.org/laura/schema/magnetic'})

    horizontal: Optional[_CorrectorMagnetBase] = Field(default=None, description="""Horizontal-plane corrector field, with its own calibration.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Combined_Corrector_Magnet']} })
    """Horizontal-plane corrector field, with its own calibration."""
    vertical: Optional[_CorrectorMagnetBase] = Field(default=None, description="""Vertical-plane corrector field, with its own calibration.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Combined_Corrector_Magnet']} })
    """Vertical-plane corrector field, with its own calibration."""


class _SolenoidFieldsBase(ConfiguredBaseModel):
    """
    Solenoid integrated axial field components ``S0L``–``S12L`` [T.m].
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:SolenoidFields',
         'from_schema': 'https://w3id.org/laura/schema/magnetic'})

    S0L: float = Field(default=0.0, description="""Integrated solenoid field, order 0 [T.m].""", json_schema_extra = { "linkml_meta": {'domain_of': ['SolenoidFields'], 'ifabsent': 'float(0.0)'} })
    """Integrated solenoid field, order 0 [T.m]."""
    S1L: float = Field(default=0.0, description="""Integrated solenoid field, order 1 [T.m].""", json_schema_extra = { "linkml_meta": {'domain_of': ['SolenoidFields'], 'ifabsent': 'float(0.0)'} })
    """Integrated solenoid field, order 1 [T.m]."""
    S2L: float = Field(default=0.0, description="""Integrated solenoid field, order 2 [T.m].""", json_schema_extra = { "linkml_meta": {'domain_of': ['SolenoidFields'], 'ifabsent': 'float(0.0)'} })
    """Integrated solenoid field, order 2 [T.m]."""
    S3L: float = Field(default=0.0, description="""Integrated solenoid field, order 3 [T.m].""", json_schema_extra = { "linkml_meta": {'domain_of': ['SolenoidFields'], 'ifabsent': 'float(0.0)'} })
    """Integrated solenoid field, order 3 [T.m]."""
    S4L: float = Field(default=0.0, description="""Integrated solenoid field, order 4 [T.m].""", json_schema_extra = { "linkml_meta": {'domain_of': ['SolenoidFields'], 'ifabsent': 'float(0.0)'} })
    """Integrated solenoid field, order 4 [T.m]."""
    S5L: float = Field(default=0.0, description="""Integrated solenoid field, order 5 [T.m].""", json_schema_extra = { "linkml_meta": {'domain_of': ['SolenoidFields'], 'ifabsent': 'float(0.0)'} })
    """Integrated solenoid field, order 5 [T.m]."""
    S6L: float = Field(default=0.0, description="""Integrated solenoid field, order 6 [T.m].""", json_schema_extra = { "linkml_meta": {'domain_of': ['SolenoidFields'], 'ifabsent': 'float(0.0)'} })
    """Integrated solenoid field, order 6 [T.m]."""
    S7L: float = Field(default=0.0, description="""Integrated solenoid field, order 7 [T.m].""", json_schema_extra = { "linkml_meta": {'domain_of': ['SolenoidFields'], 'ifabsent': 'float(0.0)'} })
    """Integrated solenoid field, order 7 [T.m]."""
    S8L: float = Field(default=0.0, description="""Integrated solenoid field, order 8 [T.m].""", json_schema_extra = { "linkml_meta": {'domain_of': ['SolenoidFields'], 'ifabsent': 'float(0.0)'} })
    """Integrated solenoid field, order 8 [T.m]."""
    S9L: float = Field(default=0.0, description="""Integrated solenoid field, order 9 [T.m].""", json_schema_extra = { "linkml_meta": {'domain_of': ['SolenoidFields'], 'ifabsent': 'float(0.0)'} })
    """Integrated solenoid field, order 9 [T.m]."""
    S10L: float = Field(default=0.0, description="""Integrated solenoid field, order 10 [T.m].""", json_schema_extra = { "linkml_meta": {'domain_of': ['SolenoidFields'], 'ifabsent': 'float(0.0)'} })
    """Integrated solenoid field, order 10 [T.m]."""
    S11L: float = Field(default=0.0, description="""Integrated solenoid field, order 11 [T.m].""", json_schema_extra = { "linkml_meta": {'domain_of': ['SolenoidFields'], 'ifabsent': 'float(0.0)'} })
    """Integrated solenoid field, order 11 [T.m]."""
    S12L: float = Field(default=0.0, description="""Integrated solenoid field, order 12 [T.m].""", json_schema_extra = { "linkml_meta": {'domain_of': ['SolenoidFields'], 'ifabsent': 'float(0.0)'} })
    """Integrated solenoid field, order 12 [T.m]."""


class _SolenoidMagnetBase(ConfiguredBaseModel):
    """
    Solenoid field model, including systematic and random field errors and the current-to-field calibration.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:Solenoid_Magnet',
         'from_schema': 'https://w3id.org/laura/schema/magnetic'})

    length: float = Field(default=0.0, description="""Magnetic length [m].""", ge=0, validation_alias=AliasChoices('length', 'magnetic_length'), json_schema_extra = { "linkml_meta": {'domain_of': ['PhysicalElement',
                       'MagneticElement',
                       'Solenoid_Magnet',
                       'Wiggler_Magnet',
                       'NonLinearLens_Magnet'],
         'ifabsent': 'float(0.0)'} })
    """Magnetic length [m]."""
    order: int = Field(default=0, description="""Principal solenoid multipole order.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Multipole', 'MagneticElement', 'Solenoid_Magnet'],
         'ifabsent': 'int(0)'} })
    """Principal solenoid multipole order."""
    fields: Optional[_SolenoidFieldsBase] = Field(default=None, description="""Nominal integrated axial field components.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Solenoid_Magnet']} })
    """Nominal integrated axial field components."""
    systematic_fields: Optional[_SolenoidFieldsBase] = Field(default=None, description="""Systematic field errors.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Solenoid_Magnet']} })
    """Systematic field errors."""
    random_fields: Optional[_SolenoidFieldsBase] = Field(default=None, description="""Random field errors.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Solenoid_Magnet']} })
    """Random field errors."""
    field_integral_coefficients: Optional[_FieldIntegralBase] = Field(default=None, description="""Polynomial current-to-integrated-field coefficients.""", json_schema_extra = { "linkml_meta": {'domain_of': ['MagneticElement', 'Solenoid_Magnet']} })
    """Polynomial current-to-integrated-field coefficients."""
    linear_saturation_coefficients: Optional[_LinearSaturationFitBase] = Field(default=None, description="""Linear-plus-saturation fit of field against current.""", json_schema_extra = { "linkml_meta": {'domain_of': ['MagneticElement', 'Solenoid_Magnet']} })
    """Linear-plus-saturation fit of field against current."""
    settle_time: float = Field(default=45.0, description="""Time to wait after a set before the field is stable [s].""", ge=0, json_schema_extra = { "linkml_meta": {'domain_of': ['MagneticElement', 'Solenoid_Magnet'], 'ifabsent': 'float(45.0)'} })
    """Time to wait after a set before the field is stable [s]."""


class _WigglerMagnetBase(ConfiguredBaseModel):
    """
    Periodic wiggler/undulator field.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:Wiggler_Magnet',
         'from_schema': 'https://w3id.org/laura/schema/magnetic'})

    length: float = Field(default=0.0, description="""Magnetic length [m].""", ge=0, validation_alias=AliasChoices('length', 'magnetic_length'), json_schema_extra = { "linkml_meta": {'domain_of': ['PhysicalElement',
                       'MagneticElement',
                       'Solenoid_Magnet',
                       'Wiggler_Magnet',
                       'NonLinearLens_Magnet'],
         'ifabsent': 'float(0.0)'} })
    """Magnetic length [m]."""
    strength: float = Field(default=0.0, description="""Deflection parameter K. May be a functional expression.""", ge=0, json_schema_extra = { "linkml_meta": {'domain_of': ['Wiggler_Magnet'], 'ifabsent': 'float(0.0)'} })
    """Deflection parameter K. May be a functional expression."""
    peak_magnetic_field: float = Field(default=0.0, description="""Peak on-axis field [T].""", json_schema_extra = { "linkml_meta": {'domain_of': ['Wiggler_Magnet'], 'ifabsent': 'float(0.0)'} })
    """Peak on-axis field [T]."""
    period: float = Field(default=0.0, description="""Magnetic period length [m].""", json_schema_extra = { "linkml_meta": {'domain_of': ['Wiggler_Magnet'], 'ifabsent': 'float(0.0)'} })
    """Magnetic period length [m]."""
    num_periods: int = Field(default=0, description="""Number of full magnetic periods.""", ge=0, json_schema_extra = { "linkml_meta": {'domain_of': ['Wiggler_Magnet'], 'ifabsent': 'int(0)'} })
    """Number of full magnetic periods."""
    helical: Optional[bool] = Field(default=False, description="""True for a helical device, False for planar.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Wiggler_Magnet'], 'ifabsent': 'False'} })
    """True for a helical device, False for planar."""
    quadratic_roll_off_x: float = Field(default=0.0, description="""Quadratic field roll-off in x [1/m^2].""", json_schema_extra = { "linkml_meta": {'domain_of': ['Wiggler_Magnet'], 'ifabsent': 'float(0.0)'} })
    """Quadratic field roll-off in x [1/m^2]."""
    quadratic_roll_off_y: float = Field(default=0.0, description="""Quadratic field roll-off in y [1/m^2].""", json_schema_extra = { "linkml_meta": {'domain_of': ['Wiggler_Magnet'], 'ifabsent': 'float(0.0)'} })
    """Quadratic field roll-off in y [1/m^2]."""
    transverse_gradient_x: float = Field(default=0.0, description="""Transverse field gradient in x [1/m].""", json_schema_extra = { "linkml_meta": {'domain_of': ['Wiggler_Magnet'], 'ifabsent': 'float(0.0)'} })
    """Transverse field gradient in x [1/m]."""
    transverse_gradient_y: float = Field(default=0.0, description="""Transverse field gradient in y [1/m].""", json_schema_extra = { "linkml_meta": {'domain_of': ['Wiggler_Magnet'], 'ifabsent': 'float(0.0)'} })
    """Transverse field gradient in y [1/m]."""


class _NonLinearLensMagnetBase(ConfiguredBaseModel):
    """
    Integrable-optics non-linear lens field.  See the MAD-X manual and Danilov/Nagaitsev, PAC2011 WEP070.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:NonLinearLens_Magnet',
         'from_schema': 'https://w3id.org/laura/schema/magnetic'})

    length: float = Field(default=0.0, description="""Magnetic length [m].""", ge=0, validation_alias=AliasChoices('length', 'magnetic_length'), json_schema_extra = { "linkml_meta": {'domain_of': ['PhysicalElement',
                       'MagneticElement',
                       'Solenoid_Magnet',
                       'Wiggler_Magnet',
                       'NonLinearLens_Magnet'],
         'ifabsent': 'float(0.0)'} })
    """Magnetic length [m]."""
    integrated_strength: float = Field(default=0.0, description="""Integrated lens strength (MAD-X ``knll``). May be a functional expression.""", ge=0, json_schema_extra = { "linkml_meta": {'domain_of': ['NonLinearLens_Magnet'], 'ifabsent': 'float(0.0)'} })
    """Integrated lens strength (MAD-X ``knll``). May be a functional expression."""
    dimensional_parameter: float = Field(default=0.0, description="""Dimensional parameter setting the transverse scale (MAD-X ``cnll``). May be a functional expression.""", json_schema_extra = { "linkml_meta": {'domain_of': ['NonLinearLens_Magnet'], 'ifabsent': 'float(0.0)'} })
    """Dimensional parameter setting the transverse scale (MAD-X ``cnll``). May be a functional expression."""


class _ElectricalElementBase(ConfiguredBaseModel):
    """
    Power-supply electrical limits for a beamline element.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:ElectricalElement',
         'from_schema': 'https://w3id.org/laura/schema'})

    min_i: float = Field(default=0, description="""Minimum current [A].""", validation_alias=AliasChoices('min_i', 'minI'), json_schema_extra = { "linkml_meta": {'aliases': ['minI'],
         'domain_of': ['ElectricalElement'],
         'ifabsent': 'float(0)',
         'unit': {'ucum_code': 'A'}} })
    """Minimum current [A]."""
    max_i: float = Field(default=0, description="""Maximum current [A].""", validation_alias=AliasChoices('max_i', 'maxI'), json_schema_extra = { "linkml_meta": {'aliases': ['maxI'],
         'domain_of': ['ElectricalElement'],
         'ifabsent': 'float(0)',
         'unit': {'ucum_code': 'A'}} })
    """Maximum current [A]."""
    read_tolerance: float = Field(default=0.1, description="""Read-back vs. set-point tolerance fraction (default 0.1 = 10 %).""", validation_alias=AliasChoices('read_tolerance', 'ri_tolerance'), json_schema_extra = { "linkml_meta": {'aliases': ['ri_tolerance'],
         'domain_of': ['ElectricalElement'],
         'ifabsent': 'float(0.1)'} })
    """Read-back vs. set-point tolerance fraction (default 0.1 = 10 %)."""


class _ManufacturerElementBase(ConfiguredBaseModel):
    """
    Manufacturer and serial-number metadata.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:ManufacturerElement',
         'from_schema': 'https://w3id.org/laura/schema'})

    manufacturer: str = Field(default="", description="""Name of the manufacturer.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ManufacturerElement', 'StandardElement'],
         'ifabsent': 'string()',
         'slot_uri': 'schema:manufacturer'} })
    """Name of the manufacturer."""
    serial_number: str = Field(default="", description="""Manufacturer serial number.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ManufacturerElement'],
         'ifabsent': 'string()',
         'slot_uri': 'schema:serialNumber'} })
    """Manufacturer serial number."""


class _ReferenceElementBase(ConfiguredBaseModel):
    """
    Links to engineering drawings and design files.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:ReferenceElement',
         'from_schema': 'https://w3id.org/laura/schema'})

    drawings: list[str] = Field(default_factory=list, description="""Engineering-drawing identifiers or URIs.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ReferenceElement']} })
    """Engineering-drawing identifiers or URIs."""
    design_files: list[str] = Field(default_factory=list, description="""Design-file paths or URIs.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ReferenceElement']} })
    """Design-file paths or URIs."""


class _AcceleratorElementBase(ConfiguredBaseModel):
    """
    Root base class for all LAURA accelerator elements.  Every lattice element is an instance of a concrete subclass identified by ``hardware_type``.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:AcceleratorElement',
         'from_schema': 'https://w3id.org/laura/schema',
         'tree_root': True})

    name: str = Field(default=..., description="""Unique element name within the machine.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SectionLattice', 'MachineLayout', 'AcceleratorElement']} })
    """Unique element name within the machine."""
    hardware_class: HardwareClassEnum = Field(default=..., description="""Functional category (e.g., ``Magnet``, ``Diagnostic``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Functional category (e.g., ``Magnet``, ``Diagnostic``)."""
    hardware_type: str = Field(default="Generic", description="""Python class name used for ELEMENT_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string(Generic)'} })
    """Python class name used for ELEMENT_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML."""
    hardware_model: str = Field(default="Generic", description="""Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string(Generic)'} })
    """Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``)."""
    machine_area: Optional[str] = Field(default=None, description="""Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``)."""
    virtual_name: str = Field(default="", description="""Alternative internal name used by the control system when the physical name is inaccessible.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string()'} })
    """Alternative internal name used by the control system when the physical name is inaccessible."""
    alias: list[str] = Field(default_factory=list, description="""Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.""", validation_alias=AliasChoices('alias', 'name_alias'), json_schema_extra = { "linkml_meta": {'aliases': ['name_alias'], 'domain_of': ['AcceleratorElement']} })
    """Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings."""
    subelement: Optional[str] = Field(default=None, description="""If set, this element is a logical sub-component of the named parent element.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """If set, this element is a logical sub-component of the named parent element."""
    inputs: list[IOTypeEnum] = Field(default_factory=list, description="""Signal types this element consumes (e.g. ``[current, voltage]``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Signal types this element consumes (e.g. ``[current, voltage]``)."""
    outputs: list[IOTypeEnum] = Field(default_factory=list, description="""Signal types this element produces (e.g. ``[power, phase]``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Signal types this element produces (e.g. ``[power, phase]``)."""
    upstream: list[str] = Field(default_factory=list, description="""Names of elements feeding this one, whose ``outputs`` supply its ``inputs``.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Names of elements feeding this one, whose ``outputs`` supply its ``inputs``."""
    downstream: list[str] = Field(default_factory=list, description="""Names of elements this one feeds; the inverse of ``upstream``.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Names of elements this one feeds; the inverse of ``upstream``."""


class _StandardElementBase(_AcceleratorElementBase):
    """
    Accelerator element with control-system, electrical, manufacturer, simulation, and reference sub-models.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:StandardElement',
         'from_schema': 'https://w3id.org/laura/schema'})

    simulation: Optional[_SimulationElementBase] = Field(default=None, description="""Simulation / tracking attributes.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Simulation / tracking attributes."""
    electrical: Optional[_ElectricalElementBase] = Field(default=None, description="""Power-supply electrical limits.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Power-supply electrical limits."""
    manufacturer: Optional[_ManufacturerElementBase] = Field(default=None, description="""Manufacturer and serial-number data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ManufacturerElement', 'StandardElement']} })
    """Manufacturer and serial-number data."""
    controls: Optional[_ControlsInformationBase] = Field(default=None, description="""Control-system process-variable definitions.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Control-system process-variable definitions."""
    reference: Optional[_ReferenceElementBase] = Field(default=None, description="""Links to design drawings and files.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Links to design drawings and files."""
    name: str = Field(default=..., description="""Unique element name within the machine.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SectionLattice', 'MachineLayout', 'AcceleratorElement']} })
    """Unique element name within the machine."""
    hardware_class: HardwareClassEnum = Field(default=..., description="""Functional category (e.g., ``Magnet``, ``Diagnostic``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Functional category (e.g., ``Magnet``, ``Diagnostic``)."""
    hardware_type: str = Field(default="Generic", description="""Python class name used for ELEMENT_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string(Generic)'} })
    """Python class name used for ELEMENT_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML."""
    hardware_model: str = Field(default="Generic", description="""Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string(Generic)'} })
    """Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``)."""
    machine_area: Optional[str] = Field(default=None, description="""Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``)."""
    virtual_name: str = Field(default="", description="""Alternative internal name used by the control system when the physical name is inaccessible.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string()'} })
    """Alternative internal name used by the control system when the physical name is inaccessible."""
    alias: list[str] = Field(default_factory=list, description="""Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.""", validation_alias=AliasChoices('alias', 'name_alias'), json_schema_extra = { "linkml_meta": {'aliases': ['name_alias'], 'domain_of': ['AcceleratorElement']} })
    """Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings."""
    subelement: Optional[str] = Field(default=None, description="""If set, this element is a logical sub-component of the named parent element.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """If set, this element is a logical sub-component of the named parent element."""
    inputs: list[IOTypeEnum] = Field(default_factory=list, description="""Signal types this element consumes (e.g. ``[current, voltage]``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Signal types this element consumes (e.g. ``[current, voltage]``)."""
    outputs: list[IOTypeEnum] = Field(default_factory=list, description="""Signal types this element produces (e.g. ``[power, phase]``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Signal types this element produces (e.g. ``[power, phase]``)."""
    upstream: list[str] = Field(default_factory=list, description="""Names of elements feeding this one, whose ``outputs`` supply its ``inputs``.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Names of elements feeding this one, whose ``outputs`` supply its ``inputs``."""
    downstream: list[str] = Field(default_factory=list, description="""Names of elements this one feeds; the inverse of ``upstream``.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Names of elements this one feeds; the inverse of ``upstream``."""


class _LightingBase(_StandardElementBase):
    """
    Experimental-hall lighting element.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:Lighting',
         'from_schema': 'https://w3id.org/laura/schema/elements',
         'slot_usage': {'hardware_type': {'equals_string': 'Lighting',
                                          'name': 'hardware_type'}}})

    lights: Optional[_LightingElementBase] = Field(default=None, description="""Lighting configuration.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Lighting']} })
    """Lighting configuration."""
    simulation: Optional[_SimulationElementBase] = Field(default=None, description="""Simulation / tracking attributes.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Simulation / tracking attributes."""
    electrical: Optional[_ElectricalElementBase] = Field(default=None, description="""Power-supply electrical limits.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Power-supply electrical limits."""
    manufacturer: Optional[_ManufacturerElementBase] = Field(default=None, description="""Manufacturer and serial-number data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ManufacturerElement', 'StandardElement']} })
    """Manufacturer and serial-number data."""
    controls: Optional[_ControlsInformationBase] = Field(default=None, description="""Control-system process-variable definitions.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Control-system process-variable definitions."""
    reference: Optional[_ReferenceElementBase] = Field(default=None, description="""Links to design drawings and files.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Links to design drawings and files."""
    name: str = Field(default=..., description="""Unique element name within the machine.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SectionLattice', 'MachineLayout', 'AcceleratorElement']} })
    """Unique element name within the machine."""
    hardware_class: HardwareClassEnum = Field(default=..., description="""Functional category (e.g., ``Magnet``, ``Diagnostic``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Functional category (e.g., ``Magnet``, ``Diagnostic``)."""
    hardware_type: Optional[Literal["Lighting"]] = Field(default="Generic", description="""Python class name used for ELEMENT_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'],
         'equals_string': 'Lighting',
         'ifabsent': 'string(Generic)'} })
    """Python class name used for ELEMENT_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML."""
    hardware_model: str = Field(default="Generic", description="""Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string(Generic)'} })
    """Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``)."""
    machine_area: Optional[str] = Field(default=None, description="""Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``)."""
    virtual_name: str = Field(default="", description="""Alternative internal name used by the control system when the physical name is inaccessible.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string()'} })
    """Alternative internal name used by the control system when the physical name is inaccessible."""
    alias: list[str] = Field(default_factory=list, description="""Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.""", validation_alias=AliasChoices('alias', 'name_alias'), json_schema_extra = { "linkml_meta": {'aliases': ['name_alias'], 'domain_of': ['AcceleratorElement']} })
    """Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings."""
    subelement: Optional[str] = Field(default=None, description="""If set, this element is a logical sub-component of the named parent element.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """If set, this element is a logical sub-component of the named parent element."""
    inputs: list[IOTypeEnum] = Field(default_factory=list, description="""Signal types this element consumes (e.g. ``[current, voltage]``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Signal types this element consumes (e.g. ``[current, voltage]``)."""
    outputs: list[IOTypeEnum] = Field(default_factory=list, description="""Signal types this element produces (e.g. ``[power, phase]``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Signal types this element produces (e.g. ``[power, phase]``)."""
    upstream: list[str] = Field(default_factory=list, description="""Names of elements feeding this one, whose ``outputs`` supply its ``inputs``.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Names of elements feeding this one, whose ``outputs`` supply its ``inputs``."""
    downstream: list[str] = Field(default_factory=list, description="""Names of elements this one feeds; the inverse of ``upstream``.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Names of elements this one feeds; the inverse of ``upstream``."""


class _PowerSupplyBase(_StandardElementBase):
    """
    Generic power-supply unit providing control/setpoint-driven outputs (for example current/voltage) to other accelerator components.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:PowerSupply',
         'from_schema': 'https://w3id.org/laura/schema/elements',
         'slot_usage': {'hardware_type': {'equals_string': 'PowerSupply',
                                          'name': 'hardware_type'}}})

    simulation: Optional[_SimulationElementBase] = Field(default=None, description="""Simulation / tracking attributes.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Simulation / tracking attributes."""
    electrical: Optional[_ElectricalElementBase] = Field(default=None, description="""Power-supply electrical limits.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Power-supply electrical limits."""
    manufacturer: Optional[_ManufacturerElementBase] = Field(default=None, description="""Manufacturer and serial-number data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ManufacturerElement', 'StandardElement']} })
    """Manufacturer and serial-number data."""
    controls: Optional[_ControlsInformationBase] = Field(default=None, description="""Control-system process-variable definitions.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Control-system process-variable definitions."""
    reference: Optional[_ReferenceElementBase] = Field(default=None, description="""Links to design drawings and files.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Links to design drawings and files."""
    name: str = Field(default=..., description="""Unique element name within the machine.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SectionLattice', 'MachineLayout', 'AcceleratorElement']} })
    """Unique element name within the machine."""
    hardware_class: HardwareClassEnum = Field(default=..., description="""Functional category (e.g., ``Magnet``, ``Diagnostic``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Functional category (e.g., ``Magnet``, ``Diagnostic``)."""
    hardware_type: Optional[Literal["PowerSupply"]] = Field(default="Generic", description="""Python class name used for ELEMENT_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'],
         'equals_string': 'PowerSupply',
         'ifabsent': 'string(Generic)'} })
    """Python class name used for ELEMENT_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML."""
    hardware_model: str = Field(default="Generic", description="""Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string(Generic)'} })
    """Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``)."""
    machine_area: Optional[str] = Field(default=None, description="""Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``)."""
    virtual_name: str = Field(default="", description="""Alternative internal name used by the control system when the physical name is inaccessible.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string()'} })
    """Alternative internal name used by the control system when the physical name is inaccessible."""
    alias: list[str] = Field(default_factory=list, description="""Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.""", validation_alias=AliasChoices('alias', 'name_alias'), json_schema_extra = { "linkml_meta": {'aliases': ['name_alias'], 'domain_of': ['AcceleratorElement']} })
    """Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings."""
    subelement: Optional[str] = Field(default=None, description="""If set, this element is a logical sub-component of the named parent element.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """If set, this element is a logical sub-component of the named parent element."""
    inputs: list[IOTypeEnum] = Field(default_factory=list, description="""Signal types this element consumes (e.g. ``[current, voltage]``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Signal types this element consumes (e.g. ``[current, voltage]``)."""
    outputs: list[IOTypeEnum] = Field(default_factory=list, description="""Signal types this element produces (e.g. ``[power, phase]``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Signal types this element produces (e.g. ``[power, phase]``)."""
    upstream: list[str] = Field(default_factory=list, description="""Names of elements feeding this one, whose ``outputs`` supply its ``inputs``.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Names of elements feeding this one, whose ``outputs`` supply its ``inputs``."""
    downstream: list[str] = Field(default_factory=list, description="""Names of elements this one feeds; the inverse of ``upstream``.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Names of elements this one feeds; the inverse of ``upstream``."""


class _LowLevelRFBase(_StandardElementBase):
    """
    Low-level RF (LLRF) controller.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:LowLevelRF',
         'from_schema': 'https://w3id.org/laura/schema/rf',
         'slot_usage': {'hardware_type': {'equals_string': 'Low_Level_RF',
                                          'name': 'hardware_type'}}})

    llrf: Optional[_LowLevelRFElementBase] = Field(default=None, description="""LLRF parameters.""", json_schema_extra = { "linkml_meta": {'domain_of': ['LowLevelRF']} })
    """LLRF parameters."""
    simulation: Optional[_SimulationElementBase] = Field(default=None, description="""Simulation / tracking attributes.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Simulation / tracking attributes."""
    electrical: Optional[_ElectricalElementBase] = Field(default=None, description="""Power-supply electrical limits.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Power-supply electrical limits."""
    manufacturer: Optional[_ManufacturerElementBase] = Field(default=None, description="""Manufacturer and serial-number data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ManufacturerElement', 'StandardElement']} })
    """Manufacturer and serial-number data."""
    controls: Optional[_ControlsInformationBase] = Field(default=None, description="""Control-system process-variable definitions.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Control-system process-variable definitions."""
    reference: Optional[_ReferenceElementBase] = Field(default=None, description="""Links to design drawings and files.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Links to design drawings and files."""
    name: str = Field(default=..., description="""Unique element name within the machine.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SectionLattice', 'MachineLayout', 'AcceleratorElement']} })
    """Unique element name within the machine."""
    hardware_class: HardwareClassEnum = Field(default=..., description="""Functional category (e.g., ``Magnet``, ``Diagnostic``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Functional category (e.g., ``Magnet``, ``Diagnostic``)."""
    hardware_type: Optional[Literal["Low_Level_RF"]] = Field(default="Generic", description="""Python class name used for ELEMENT_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'],
         'equals_string': 'Low_Level_RF',
         'ifabsent': 'string(Generic)'} })
    """Python class name used for ELEMENT_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML."""
    hardware_model: str = Field(default="Generic", description="""Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string(Generic)'} })
    """Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``)."""
    machine_area: Optional[str] = Field(default=None, description="""Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``)."""
    virtual_name: str = Field(default="", description="""Alternative internal name used by the control system when the physical name is inaccessible.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string()'} })
    """Alternative internal name used by the control system when the physical name is inaccessible."""
    alias: list[str] = Field(default_factory=list, description="""Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.""", validation_alias=AliasChoices('alias', 'name_alias'), json_schema_extra = { "linkml_meta": {'aliases': ['name_alias'], 'domain_of': ['AcceleratorElement']} })
    """Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings."""
    subelement: Optional[str] = Field(default=None, description="""If set, this element is a logical sub-component of the named parent element.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """If set, this element is a logical sub-component of the named parent element."""
    inputs: list[IOTypeEnum] = Field(default_factory=list, description="""Signal types this element consumes (e.g. ``[current, voltage]``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Signal types this element consumes (e.g. ``[current, voltage]``)."""
    outputs: list[IOTypeEnum] = Field(default_factory=list, description="""Signal types this element produces (e.g. ``[power, phase]``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Signal types this element produces (e.g. ``[power, phase]``)."""
    upstream: list[str] = Field(default_factory=list, description="""Names of elements feeding this one, whose ``outputs`` supply its ``inputs``.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Names of elements feeding this one, whose ``outputs`` supply its ``inputs``."""
    downstream: list[str] = Field(default_factory=list, description="""Names of elements this one feeds; the inverse of ``upstream``.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Names of elements this one feeds; the inverse of ``upstream``."""


class _RFModulatorBase(_StandardElementBase):
    """
    RF modulator (klystron driver) element.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:RFModulator',
         'from_schema': 'https://w3id.org/laura/schema/rf',
         'slot_usage': {'hardware_type': {'equals_string': 'RFModulator',
                                          'name': 'hardware_type'}}})

    modulator: Optional[_RFModulatorElementBase] = Field(default=None, description="""Modulator parameters.""", json_schema_extra = { "linkml_meta": {'domain_of': ['RFModulator']} })
    """Modulator parameters."""
    simulation: Optional[_SimulationElementBase] = Field(default=None, description="""Simulation / tracking attributes.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Simulation / tracking attributes."""
    electrical: Optional[_ElectricalElementBase] = Field(default=None, description="""Power-supply electrical limits.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Power-supply electrical limits."""
    manufacturer: Optional[_ManufacturerElementBase] = Field(default=None, description="""Manufacturer and serial-number data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ManufacturerElement', 'StandardElement']} })
    """Manufacturer and serial-number data."""
    controls: Optional[_ControlsInformationBase] = Field(default=None, description="""Control-system process-variable definitions.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Control-system process-variable definitions."""
    reference: Optional[_ReferenceElementBase] = Field(default=None, description="""Links to design drawings and files.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Links to design drawings and files."""
    name: str = Field(default=..., description="""Unique element name within the machine.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SectionLattice', 'MachineLayout', 'AcceleratorElement']} })
    """Unique element name within the machine."""
    hardware_class: HardwareClassEnum = Field(default=..., description="""Functional category (e.g., ``Magnet``, ``Diagnostic``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Functional category (e.g., ``Magnet``, ``Diagnostic``)."""
    hardware_type: Optional[Literal["RFModulator"]] = Field(default="Generic", description="""Python class name used for ELEMENT_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'],
         'equals_string': 'RFModulator',
         'ifabsent': 'string(Generic)'} })
    """Python class name used for ELEMENT_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML."""
    hardware_model: str = Field(default="Generic", description="""Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string(Generic)'} })
    """Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``)."""
    machine_area: Optional[str] = Field(default=None, description="""Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``)."""
    virtual_name: str = Field(default="", description="""Alternative internal name used by the control system when the physical name is inaccessible.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string()'} })
    """Alternative internal name used by the control system when the physical name is inaccessible."""
    alias: list[str] = Field(default_factory=list, description="""Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.""", validation_alias=AliasChoices('alias', 'name_alias'), json_schema_extra = { "linkml_meta": {'aliases': ['name_alias'], 'domain_of': ['AcceleratorElement']} })
    """Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings."""
    subelement: Optional[str] = Field(default=None, description="""If set, this element is a logical sub-component of the named parent element.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """If set, this element is a logical sub-component of the named parent element."""
    inputs: list[IOTypeEnum] = Field(default_factory=list, description="""Signal types this element consumes (e.g. ``[current, voltage]``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Signal types this element consumes (e.g. ``[current, voltage]``)."""
    outputs: list[IOTypeEnum] = Field(default_factory=list, description="""Signal types this element produces (e.g. ``[power, phase]``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Signal types this element produces (e.g. ``[power, phase]``)."""
    upstream: list[str] = Field(default_factory=list, description="""Names of elements feeding this one, whose ``outputs`` supply its ``inputs``.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Names of elements feeding this one, whose ``outputs`` supply its ``inputs``."""
    downstream: list[str] = Field(default_factory=list, description="""Names of elements this one feeds; the inverse of ``upstream``.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Names of elements this one feeds; the inverse of ``upstream``."""


class _RFProtectionBase(_StandardElementBase):
    """
    RF protection system element.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:RFProtection',
         'from_schema': 'https://w3id.org/laura/schema/rf',
         'slot_usage': {'hardware_type': {'equals_string': 'RFProtection',
                                          'name': 'hardware_type'}}})

    protection: Optional[_RFProtectionElementBase] = Field(default=None, description="""RF protection parameters.""", json_schema_extra = { "linkml_meta": {'domain_of': ['RFProtection']} })
    """RF protection parameters."""
    simulation: Optional[_SimulationElementBase] = Field(default=None, description="""Simulation / tracking attributes.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Simulation / tracking attributes."""
    electrical: Optional[_ElectricalElementBase] = Field(default=None, description="""Power-supply electrical limits.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Power-supply electrical limits."""
    manufacturer: Optional[_ManufacturerElementBase] = Field(default=None, description="""Manufacturer and serial-number data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ManufacturerElement', 'StandardElement']} })
    """Manufacturer and serial-number data."""
    controls: Optional[_ControlsInformationBase] = Field(default=None, description="""Control-system process-variable definitions.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Control-system process-variable definitions."""
    reference: Optional[_ReferenceElementBase] = Field(default=None, description="""Links to design drawings and files.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Links to design drawings and files."""
    name: str = Field(default=..., description="""Unique element name within the machine.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SectionLattice', 'MachineLayout', 'AcceleratorElement']} })
    """Unique element name within the machine."""
    hardware_class: HardwareClassEnum = Field(default=..., description="""Functional category (e.g., ``Magnet``, ``Diagnostic``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Functional category (e.g., ``Magnet``, ``Diagnostic``)."""
    hardware_type: Optional[Literal["RFProtection"]] = Field(default="Generic", description="""Python class name used for ELEMENT_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'],
         'equals_string': 'RFProtection',
         'ifabsent': 'string(Generic)'} })
    """Python class name used for ELEMENT_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML."""
    hardware_model: str = Field(default="Generic", description="""Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string(Generic)'} })
    """Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``)."""
    machine_area: Optional[str] = Field(default=None, description="""Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``)."""
    virtual_name: str = Field(default="", description="""Alternative internal name used by the control system when the physical name is inaccessible.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string()'} })
    """Alternative internal name used by the control system when the physical name is inaccessible."""
    alias: list[str] = Field(default_factory=list, description="""Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.""", validation_alias=AliasChoices('alias', 'name_alias'), json_schema_extra = { "linkml_meta": {'aliases': ['name_alias'], 'domain_of': ['AcceleratorElement']} })
    """Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings."""
    subelement: Optional[str] = Field(default=None, description="""If set, this element is a logical sub-component of the named parent element.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """If set, this element is a logical sub-component of the named parent element."""
    inputs: list[IOTypeEnum] = Field(default_factory=list, description="""Signal types this element consumes (e.g. ``[current, voltage]``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Signal types this element consumes (e.g. ``[current, voltage]``)."""
    outputs: list[IOTypeEnum] = Field(default_factory=list, description="""Signal types this element produces (e.g. ``[power, phase]``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Signal types this element produces (e.g. ``[power, phase]``)."""
    upstream: list[str] = Field(default_factory=list, description="""Names of elements feeding this one, whose ``outputs`` supply its ``inputs``.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Names of elements feeding this one, whose ``outputs`` supply its ``inputs``."""
    downstream: list[str] = Field(default_factory=list, description="""Names of elements this one feeds; the inverse of ``upstream``.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Names of elements this one feeds; the inverse of ``upstream``."""


class _RFHeartbeatBase(_StandardElementBase):
    """
    RF timing heartbeat / signal-monitor element.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:RFHeartbeat',
         'from_schema': 'https://w3id.org/laura/schema/rf',
         'slot_usage': {'hardware_type': {'equals_string': 'RFHeartbeat',
                                          'name': 'hardware_type'}}})

    heartbeat: Optional[_RFHeartbeatElementBase] = Field(default=None, description="""RF heartbeat parameters.""", json_schema_extra = { "linkml_meta": {'domain_of': ['RFHeartbeat']} })
    """RF heartbeat parameters."""
    simulation: Optional[_SimulationElementBase] = Field(default=None, description="""Simulation / tracking attributes.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Simulation / tracking attributes."""
    electrical: Optional[_ElectricalElementBase] = Field(default=None, description="""Power-supply electrical limits.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Power-supply electrical limits."""
    manufacturer: Optional[_ManufacturerElementBase] = Field(default=None, description="""Manufacturer and serial-number data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ManufacturerElement', 'StandardElement']} })
    """Manufacturer and serial-number data."""
    controls: Optional[_ControlsInformationBase] = Field(default=None, description="""Control-system process-variable definitions.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Control-system process-variable definitions."""
    reference: Optional[_ReferenceElementBase] = Field(default=None, description="""Links to design drawings and files.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Links to design drawings and files."""
    name: str = Field(default=..., description="""Unique element name within the machine.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SectionLattice', 'MachineLayout', 'AcceleratorElement']} })
    """Unique element name within the machine."""
    hardware_class: HardwareClassEnum = Field(default=..., description="""Functional category (e.g., ``Magnet``, ``Diagnostic``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Functional category (e.g., ``Magnet``, ``Diagnostic``)."""
    hardware_type: Optional[Literal["RFHeartbeat"]] = Field(default="Generic", description="""Python class name used for ELEMENT_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'],
         'equals_string': 'RFHeartbeat',
         'ifabsent': 'string(Generic)'} })
    """Python class name used for ELEMENT_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML."""
    hardware_model: str = Field(default="Generic", description="""Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string(Generic)'} })
    """Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``)."""
    machine_area: Optional[str] = Field(default=None, description="""Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``)."""
    virtual_name: str = Field(default="", description="""Alternative internal name used by the control system when the physical name is inaccessible.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string()'} })
    """Alternative internal name used by the control system when the physical name is inaccessible."""
    alias: list[str] = Field(default_factory=list, description="""Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.""", validation_alias=AliasChoices('alias', 'name_alias'), json_schema_extra = { "linkml_meta": {'aliases': ['name_alias'], 'domain_of': ['AcceleratorElement']} })
    """Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings."""
    subelement: Optional[str] = Field(default=None, description="""If set, this element is a logical sub-component of the named parent element.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """If set, this element is a logical sub-component of the named parent element."""
    inputs: list[IOTypeEnum] = Field(default_factory=list, description="""Signal types this element consumes (e.g. ``[current, voltage]``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Signal types this element consumes (e.g. ``[current, voltage]``)."""
    outputs: list[IOTypeEnum] = Field(default_factory=list, description="""Signal types this element produces (e.g. ``[power, phase]``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Signal types this element produces (e.g. ``[power, phase]``)."""
    upstream: list[str] = Field(default_factory=list, description="""Names of elements feeding this one, whose ``outputs`` supply its ``inputs``.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Names of elements feeding this one, whose ``outputs`` supply its ``inputs``."""
    downstream: list[str] = Field(default_factory=list, description="""Names of elements this one feeds; the inverse of ``upstream``.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Names of elements this one feeds; the inverse of ``upstream``."""


class _PIDBase(_StandardElementBase):
    """
    Proportional-integral-derivative (PID) feedback controller.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:PID',
         'from_schema': 'https://w3id.org/laura/schema/rf',
         'slot_usage': {'hardware_type': {'equals_string': 'PID',
                                          'name': 'hardware_type'}}})

    pid: Optional[_PIDElementBase] = Field(default=None, description="""PID gain parameters.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PID']} })
    """PID gain parameters."""
    simulation: Optional[_SimulationElementBase] = Field(default=None, description="""Simulation / tracking attributes.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Simulation / tracking attributes."""
    electrical: Optional[_ElectricalElementBase] = Field(default=None, description="""Power-supply electrical limits.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Power-supply electrical limits."""
    manufacturer: Optional[_ManufacturerElementBase] = Field(default=None, description="""Manufacturer and serial-number data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ManufacturerElement', 'StandardElement']} })
    """Manufacturer and serial-number data."""
    controls: Optional[_ControlsInformationBase] = Field(default=None, description="""Control-system process-variable definitions.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Control-system process-variable definitions."""
    reference: Optional[_ReferenceElementBase] = Field(default=None, description="""Links to design drawings and files.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Links to design drawings and files."""
    name: str = Field(default=..., description="""Unique element name within the machine.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SectionLattice', 'MachineLayout', 'AcceleratorElement']} })
    """Unique element name within the machine."""
    hardware_class: HardwareClassEnum = Field(default=..., description="""Functional category (e.g., ``Magnet``, ``Diagnostic``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Functional category (e.g., ``Magnet``, ``Diagnostic``)."""
    hardware_type: Optional[Literal["PID"]] = Field(default="Generic", description="""Python class name used for ELEMENT_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'],
         'equals_string': 'PID',
         'ifabsent': 'string(Generic)'} })
    """Python class name used for ELEMENT_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML."""
    hardware_model: str = Field(default="Generic", description="""Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string(Generic)'} })
    """Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``)."""
    machine_area: Optional[str] = Field(default=None, description="""Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``)."""
    virtual_name: str = Field(default="", description="""Alternative internal name used by the control system when the physical name is inaccessible.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string()'} })
    """Alternative internal name used by the control system when the physical name is inaccessible."""
    alias: list[str] = Field(default_factory=list, description="""Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.""", validation_alias=AliasChoices('alias', 'name_alias'), json_schema_extra = { "linkml_meta": {'aliases': ['name_alias'], 'domain_of': ['AcceleratorElement']} })
    """Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings."""
    subelement: Optional[str] = Field(default=None, description="""If set, this element is a logical sub-component of the named parent element.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """If set, this element is a logical sub-component of the named parent element."""
    inputs: list[IOTypeEnum] = Field(default_factory=list, description="""Signal types this element consumes (e.g. ``[current, voltage]``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Signal types this element consumes (e.g. ``[current, voltage]``)."""
    outputs: list[IOTypeEnum] = Field(default_factory=list, description="""Signal types this element produces (e.g. ``[power, phase]``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Signal types this element produces (e.g. ``[power, phase]``)."""
    upstream: list[str] = Field(default_factory=list, description="""Names of elements feeding this one, whose ``outputs`` supply its ``inputs``.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Names of elements feeding this one, whose ``outputs`` supply its ``inputs``."""
    downstream: list[str] = Field(default_factory=list, description="""Names of elements this one feeds; the inverse of ``upstream``.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Names of elements this one feeds; the inverse of ``upstream``."""


class _LaserEnergyMeterBase(_StandardElementBase):
    """
    Laser pulse-energy diagnostic (photodiode / pyroelectric).
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:LaserEnergyMeter',
         'from_schema': 'https://w3id.org/laura/schema/laser_plasma',
         'in_subset': ['laser_properties'],
         'slot_usage': {'hardware_type': {'equals_string': 'LaserEnergyMeter',
                                          'name': 'hardware_type'}}})

    laser: Optional[_LaserEnergyMeterElementBase] = Field(default=None, description="""Energy-meter instrument parameters.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Laser',
                       'Plasma',
                       'LaserEnergyMeter',
                       'LaserHalfWavePlate',
                       'LaserMirror',
                       'Wiggler']} })
    """Energy-meter instrument parameters."""
    simulation: Optional[_SimulationElementBase] = Field(default=None, description="""Simulation / tracking attributes.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Simulation / tracking attributes."""
    electrical: Optional[_ElectricalElementBase] = Field(default=None, description="""Power-supply electrical limits.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Power-supply electrical limits."""
    manufacturer: Optional[_ManufacturerElementBase] = Field(default=None, description="""Manufacturer and serial-number data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ManufacturerElement', 'StandardElement']} })
    """Manufacturer and serial-number data."""
    controls: Optional[_ControlsInformationBase] = Field(default=None, description="""Control-system process-variable definitions.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Control-system process-variable definitions."""
    reference: Optional[_ReferenceElementBase] = Field(default=None, description="""Links to design drawings and files.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Links to design drawings and files."""
    name: str = Field(default=..., description="""Unique element name within the machine.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SectionLattice', 'MachineLayout', 'AcceleratorElement']} })
    """Unique element name within the machine."""
    hardware_class: HardwareClassEnum = Field(default=..., description="""Functional category (e.g., ``Magnet``, ``Diagnostic``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Functional category (e.g., ``Magnet``, ``Diagnostic``)."""
    hardware_type: Optional[Literal["LaserEnergyMeter"]] = Field(default="Generic", description="""Python class name used for ELEMENT_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'],
         'equals_string': 'LaserEnergyMeter',
         'ifabsent': 'string(Generic)'} })
    """Python class name used for ELEMENT_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML."""
    hardware_model: str = Field(default="Generic", description="""Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string(Generic)'} })
    """Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``)."""
    machine_area: Optional[str] = Field(default=None, description="""Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``)."""
    virtual_name: str = Field(default="", description="""Alternative internal name used by the control system when the physical name is inaccessible.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string()'} })
    """Alternative internal name used by the control system when the physical name is inaccessible."""
    alias: list[str] = Field(default_factory=list, description="""Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.""", validation_alias=AliasChoices('alias', 'name_alias'), json_schema_extra = { "linkml_meta": {'aliases': ['name_alias'], 'domain_of': ['AcceleratorElement']} })
    """Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings."""
    subelement: Optional[str] = Field(default=None, description="""If set, this element is a logical sub-component of the named parent element.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """If set, this element is a logical sub-component of the named parent element."""
    inputs: list[IOTypeEnum] = Field(default_factory=list, description="""Signal types this element consumes (e.g. ``[current, voltage]``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Signal types this element consumes (e.g. ``[current, voltage]``)."""
    outputs: list[IOTypeEnum] = Field(default_factory=list, description="""Signal types this element produces (e.g. ``[power, phase]``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Signal types this element produces (e.g. ``[power, phase]``)."""
    upstream: list[str] = Field(default_factory=list, description="""Names of elements feeding this one, whose ``outputs`` supply its ``inputs``.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Names of elements feeding this one, whose ``outputs`` supply its ``inputs``."""
    downstream: list[str] = Field(default_factory=list, description="""Names of elements this one feeds; the inverse of ``upstream``.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Names of elements this one feeds; the inverse of ``upstream``."""


class _LaserHalfWavePlateBase(_StandardElementBase):
    """
    Half-wave plate for laser polarisation rotation.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:LaserHalfWavePlate',
         'from_schema': 'https://w3id.org/laura/schema/laser_plasma',
         'in_subset': ['laser_properties'],
         'slot_usage': {'hardware_type': {'equals_string': 'LaserHalfWavePlate',
                                          'name': 'hardware_type'}}})

    laser: Optional[_LaserHalfWavePlateElementBase] = Field(default=None, description="""Half-wave plate parameters.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Laser',
                       'Plasma',
                       'LaserEnergyMeter',
                       'LaserHalfWavePlate',
                       'LaserMirror',
                       'Wiggler']} })
    """Half-wave plate parameters."""
    simulation: Optional[_SimulationElementBase] = Field(default=None, description="""Simulation / tracking attributes.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Simulation / tracking attributes."""
    electrical: Optional[_ElectricalElementBase] = Field(default=None, description="""Power-supply electrical limits.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Power-supply electrical limits."""
    manufacturer: Optional[_ManufacturerElementBase] = Field(default=None, description="""Manufacturer and serial-number data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ManufacturerElement', 'StandardElement']} })
    """Manufacturer and serial-number data."""
    controls: Optional[_ControlsInformationBase] = Field(default=None, description="""Control-system process-variable definitions.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Control-system process-variable definitions."""
    reference: Optional[_ReferenceElementBase] = Field(default=None, description="""Links to design drawings and files.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Links to design drawings and files."""
    name: str = Field(default=..., description="""Unique element name within the machine.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SectionLattice', 'MachineLayout', 'AcceleratorElement']} })
    """Unique element name within the machine."""
    hardware_class: HardwareClassEnum = Field(default=..., description="""Functional category (e.g., ``Magnet``, ``Diagnostic``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Functional category (e.g., ``Magnet``, ``Diagnostic``)."""
    hardware_type: Optional[Literal["LaserHalfWavePlate"]] = Field(default="Generic", description="""Python class name used for ELEMENT_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'],
         'equals_string': 'LaserHalfWavePlate',
         'ifabsent': 'string(Generic)'} })
    """Python class name used for ELEMENT_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML."""
    hardware_model: str = Field(default="Generic", description="""Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string(Generic)'} })
    """Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``)."""
    machine_area: Optional[str] = Field(default=None, description="""Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``)."""
    virtual_name: str = Field(default="", description="""Alternative internal name used by the control system when the physical name is inaccessible.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string()'} })
    """Alternative internal name used by the control system when the physical name is inaccessible."""
    alias: list[str] = Field(default_factory=list, description="""Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.""", validation_alias=AliasChoices('alias', 'name_alias'), json_schema_extra = { "linkml_meta": {'aliases': ['name_alias'], 'domain_of': ['AcceleratorElement']} })
    """Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings."""
    subelement: Optional[str] = Field(default=None, description="""If set, this element is a logical sub-component of the named parent element.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """If set, this element is a logical sub-component of the named parent element."""
    inputs: list[IOTypeEnum] = Field(default_factory=list, description="""Signal types this element consumes (e.g. ``[current, voltage]``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Signal types this element consumes (e.g. ``[current, voltage]``)."""
    outputs: list[IOTypeEnum] = Field(default_factory=list, description="""Signal types this element produces (e.g. ``[power, phase]``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Signal types this element produces (e.g. ``[power, phase]``)."""
    upstream: list[str] = Field(default_factory=list, description="""Names of elements feeding this one, whose ``outputs`` supply its ``inputs``.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Names of elements feeding this one, whose ``outputs`` supply its ``inputs``."""
    downstream: list[str] = Field(default_factory=list, description="""Names of elements this one feeds; the inverse of ``upstream``.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Names of elements this one feeds; the inverse of ``upstream``."""


class _LaserMirrorBase(_StandardElementBase):
    """
    Laser steering or focusing mirror.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:LaserMirror',
         'from_schema': 'https://w3id.org/laura/schema/laser_plasma',
         'in_subset': ['laser_properties'],
         'slot_usage': {'hardware_type': {'equals_string': 'LaserMirror',
                                          'name': 'hardware_type'}}})

    laser: Optional[_LaserMirrorElementBase] = Field(default=None, description="""Mirror steering parameters.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Laser',
                       'Plasma',
                       'LaserEnergyMeter',
                       'LaserHalfWavePlate',
                       'LaserMirror',
                       'Wiggler']} })
    """Mirror steering parameters."""
    simulation: Optional[_SimulationElementBase] = Field(default=None, description="""Simulation / tracking attributes.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Simulation / tracking attributes."""
    electrical: Optional[_ElectricalElementBase] = Field(default=None, description="""Power-supply electrical limits.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Power-supply electrical limits."""
    manufacturer: Optional[_ManufacturerElementBase] = Field(default=None, description="""Manufacturer and serial-number data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ManufacturerElement', 'StandardElement']} })
    """Manufacturer and serial-number data."""
    controls: Optional[_ControlsInformationBase] = Field(default=None, description="""Control-system process-variable definitions.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Control-system process-variable definitions."""
    reference: Optional[_ReferenceElementBase] = Field(default=None, description="""Links to design drawings and files.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Links to design drawings and files."""
    name: str = Field(default=..., description="""Unique element name within the machine.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SectionLattice', 'MachineLayout', 'AcceleratorElement']} })
    """Unique element name within the machine."""
    hardware_class: HardwareClassEnum = Field(default=..., description="""Functional category (e.g., ``Magnet``, ``Diagnostic``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Functional category (e.g., ``Magnet``, ``Diagnostic``)."""
    hardware_type: Optional[Literal["LaserMirror"]] = Field(default="Generic", description="""Python class name used for ELEMENT_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'],
         'equals_string': 'LaserMirror',
         'ifabsent': 'string(Generic)'} })
    """Python class name used for ELEMENT_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML."""
    hardware_model: str = Field(default="Generic", description="""Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string(Generic)'} })
    """Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``)."""
    machine_area: Optional[str] = Field(default=None, description="""Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``)."""
    virtual_name: str = Field(default="", description="""Alternative internal name used by the control system when the physical name is inaccessible.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string()'} })
    """Alternative internal name used by the control system when the physical name is inaccessible."""
    alias: list[str] = Field(default_factory=list, description="""Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.""", validation_alias=AliasChoices('alias', 'name_alias'), json_schema_extra = { "linkml_meta": {'aliases': ['name_alias'], 'domain_of': ['AcceleratorElement']} })
    """Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings."""
    subelement: Optional[str] = Field(default=None, description="""If set, this element is a logical sub-component of the named parent element.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """If set, this element is a logical sub-component of the named parent element."""
    inputs: list[IOTypeEnum] = Field(default_factory=list, description="""Signal types this element consumes (e.g. ``[current, voltage]``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Signal types this element consumes (e.g. ``[current, voltage]``)."""
    outputs: list[IOTypeEnum] = Field(default_factory=list, description="""Signal types this element produces (e.g. ``[power, phase]``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Signal types this element produces (e.g. ``[power, phase]``)."""
    upstream: list[str] = Field(default_factory=list, description="""Names of elements feeding this one, whose ``outputs`` supply its ``inputs``.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Names of elements feeding this one, whose ``outputs`` supply its ``inputs``."""
    downstream: list[str] = Field(default_factory=list, description="""Names of elements this one feeds; the inverse of ``upstream``.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Names of elements this one feeds; the inverse of ``upstream``."""


class _LaserAttenuatorBase(_StandardElementBase):
    """
    Laser power attenuator (waveplate + polariser combination).
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:LaserAttenuator',
         'from_schema': 'https://w3id.org/laura/schema/laser_plasma',
         'in_subset': ['laser_properties'],
         'slot_usage': {'hardware_type': {'equals_string': 'LaserAttenuator',
                                          'name': 'hardware_type'}}})

    maximum: Optional[float] = Field(default=None, description="""Maximum attenuation angle [deg].""", json_schema_extra = { "linkml_meta": {'domain_of': ['CameraMask', 'CameraSensor', 'LaserAttenuator'],
         'unit': {'ucum_code': 'deg'}} })
    """Maximum attenuation angle [deg]."""
    minimum: Optional[float] = Field(default=None, description="""Minimum attenuation angle [deg].""", json_schema_extra = { "linkml_meta": {'domain_of': ['CameraSensor', 'LaserAttenuator'], 'unit': {'ucum_code': 'deg'}} })
    """Minimum attenuation angle [deg]."""
    simulation: Optional[_SimulationElementBase] = Field(default=None, description="""Simulation / tracking attributes.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Simulation / tracking attributes."""
    electrical: Optional[_ElectricalElementBase] = Field(default=None, description="""Power-supply electrical limits.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Power-supply electrical limits."""
    manufacturer: Optional[_ManufacturerElementBase] = Field(default=None, description="""Manufacturer and serial-number data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ManufacturerElement', 'StandardElement']} })
    """Manufacturer and serial-number data."""
    controls: Optional[_ControlsInformationBase] = Field(default=None, description="""Control-system process-variable definitions.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Control-system process-variable definitions."""
    reference: Optional[_ReferenceElementBase] = Field(default=None, description="""Links to design drawings and files.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Links to design drawings and files."""
    name: str = Field(default=..., description="""Unique element name within the machine.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SectionLattice', 'MachineLayout', 'AcceleratorElement']} })
    """Unique element name within the machine."""
    hardware_class: HardwareClassEnum = Field(default=..., description="""Functional category (e.g., ``Magnet``, ``Diagnostic``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Functional category (e.g., ``Magnet``, ``Diagnostic``)."""
    hardware_type: Optional[Literal["LaserAttenuator"]] = Field(default="Generic", description="""Python class name used for ELEMENT_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'],
         'equals_string': 'LaserAttenuator',
         'ifabsent': 'string(Generic)'} })
    """Python class name used for ELEMENT_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML."""
    hardware_model: str = Field(default="Generic", description="""Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string(Generic)'} })
    """Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``)."""
    machine_area: Optional[str] = Field(default=None, description="""Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``)."""
    virtual_name: str = Field(default="", description="""Alternative internal name used by the control system when the physical name is inaccessible.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string()'} })
    """Alternative internal name used by the control system when the physical name is inaccessible."""
    alias: list[str] = Field(default_factory=list, description="""Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.""", validation_alias=AliasChoices('alias', 'name_alias'), json_schema_extra = { "linkml_meta": {'aliases': ['name_alias'], 'domain_of': ['AcceleratorElement']} })
    """Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings."""
    subelement: Optional[str] = Field(default=None, description="""If set, this element is a logical sub-component of the named parent element.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """If set, this element is a logical sub-component of the named parent element."""
    inputs: list[IOTypeEnum] = Field(default_factory=list, description="""Signal types this element consumes (e.g. ``[current, voltage]``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Signal types this element consumes (e.g. ``[current, voltage]``)."""
    outputs: list[IOTypeEnum] = Field(default_factory=list, description="""Signal types this element produces (e.g. ``[power, phase]``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Signal types this element produces (e.g. ``[power, phase]``)."""
    upstream: list[str] = Field(default_factory=list, description="""Names of elements feeding this one, whose ``outputs`` supply its ``inputs``.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Names of elements feeding this one, whose ``outputs`` supply its ``inputs``."""
    downstream: list[str] = Field(default_factory=list, description="""Names of elements this one feeds; the inverse of ``upstream``.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Names of elements this one feeds; the inverse of ``upstream``."""


class _ElementBase(_StandardElementBase):
    """
    Concrete schema counterpart of the Python ``Element`` wrapper class. Inherits standard element composition fields.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:Element', 'from_schema': 'https://w3id.org/laura/schema'})

    simulation: Optional[_SimulationElementBase] = Field(default=None, description="""Simulation / tracking attributes.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Simulation / tracking attributes."""
    electrical: Optional[_ElectricalElementBase] = Field(default=None, description="""Power-supply electrical limits.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Power-supply electrical limits."""
    manufacturer: Optional[_ManufacturerElementBase] = Field(default=None, description="""Manufacturer and serial-number data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ManufacturerElement', 'StandardElement']} })
    """Manufacturer and serial-number data."""
    controls: Optional[_ControlsInformationBase] = Field(default=None, description="""Control-system process-variable definitions.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Control-system process-variable definitions."""
    reference: Optional[_ReferenceElementBase] = Field(default=None, description="""Links to design drawings and files.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Links to design drawings and files."""
    name: str = Field(default=..., description="""Unique element name within the machine.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SectionLattice', 'MachineLayout', 'AcceleratorElement']} })
    """Unique element name within the machine."""
    hardware_class: HardwareClassEnum = Field(default=..., description="""Functional category (e.g., ``Magnet``, ``Diagnostic``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Functional category (e.g., ``Magnet``, ``Diagnostic``)."""
    hardware_type: str = Field(default="Generic", description="""Python class name used for ELEMENT_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string(Generic)'} })
    """Python class name used for ELEMENT_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML."""
    hardware_model: str = Field(default="Generic", description="""Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string(Generic)'} })
    """Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``)."""
    machine_area: Optional[str] = Field(default=None, description="""Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``)."""
    virtual_name: str = Field(default="", description="""Alternative internal name used by the control system when the physical name is inaccessible.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string()'} })
    """Alternative internal name used by the control system when the physical name is inaccessible."""
    alias: list[str] = Field(default_factory=list, description="""Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.""", validation_alias=AliasChoices('alias', 'name_alias'), json_schema_extra = { "linkml_meta": {'aliases': ['name_alias'], 'domain_of': ['AcceleratorElement']} })
    """Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings."""
    subelement: Optional[str] = Field(default=None, description="""If set, this element is a logical sub-component of the named parent element.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """If set, this element is a logical sub-component of the named parent element."""
    inputs: list[IOTypeEnum] = Field(default_factory=list, description="""Signal types this element consumes (e.g. ``[current, voltage]``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Signal types this element consumes (e.g. ``[current, voltage]``)."""
    outputs: list[IOTypeEnum] = Field(default_factory=list, description="""Signal types this element produces (e.g. ``[power, phase]``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Signal types this element produces (e.g. ``[power, phase]``)."""
    upstream: list[str] = Field(default_factory=list, description="""Names of elements feeding this one, whose ``outputs`` supply its ``inputs``.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Names of elements feeding this one, whose ``outputs`` supply its ``inputs``."""
    downstream: list[str] = Field(default_factory=list, description="""Names of elements this one feeds; the inverse of ``upstream``.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Names of elements this one feeds; the inverse of ``upstream``."""


class _PhysicalAcceleratorElementBase(_ElementBase):
    """
    Accelerator element with a well-defined physical position and orientation in the beamline.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:PhysicalAcceleratorElement',
         'from_schema': 'https://w3id.org/laura/schema'})

    physical: Optional[_PhysicalElementBase] = Field(default=None, description="""Position, rotation, and length data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PhysicalAcceleratorElement'],
         'in_subset': ['physical_properties']} })
    """Position, rotation, and length data."""
    simulation: Optional[_SimulationElementBase] = Field(default=None, description="""Simulation / tracking attributes.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Simulation / tracking attributes."""
    electrical: Optional[_ElectricalElementBase] = Field(default=None, description="""Power-supply electrical limits.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Power-supply electrical limits."""
    manufacturer: Optional[_ManufacturerElementBase] = Field(default=None, description="""Manufacturer and serial-number data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ManufacturerElement', 'StandardElement']} })
    """Manufacturer and serial-number data."""
    controls: Optional[_ControlsInformationBase] = Field(default=None, description="""Control-system process-variable definitions.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Control-system process-variable definitions."""
    reference: Optional[_ReferenceElementBase] = Field(default=None, description="""Links to design drawings and files.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Links to design drawings and files."""
    name: str = Field(default=..., description="""Unique element name within the machine.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SectionLattice', 'MachineLayout', 'AcceleratorElement']} })
    """Unique element name within the machine."""
    hardware_class: HardwareClassEnum = Field(default=..., description="""Functional category (e.g., ``Magnet``, ``Diagnostic``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Functional category (e.g., ``Magnet``, ``Diagnostic``)."""
    hardware_type: str = Field(default="Generic", description="""Python class name used for ELEMENT_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string(Generic)'} })
    """Python class name used for ELEMENT_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML."""
    hardware_model: str = Field(default="Generic", description="""Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string(Generic)'} })
    """Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``)."""
    machine_area: Optional[str] = Field(default=None, description="""Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``)."""
    virtual_name: str = Field(default="", description="""Alternative internal name used by the control system when the physical name is inaccessible.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string()'} })
    """Alternative internal name used by the control system when the physical name is inaccessible."""
    alias: list[str] = Field(default_factory=list, description="""Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.""", validation_alias=AliasChoices('alias', 'name_alias'), json_schema_extra = { "linkml_meta": {'aliases': ['name_alias'], 'domain_of': ['AcceleratorElement']} })
    """Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings."""
    subelement: Optional[str] = Field(default=None, description="""If set, this element is a logical sub-component of the named parent element.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """If set, this element is a logical sub-component of the named parent element."""
    inputs: list[IOTypeEnum] = Field(default_factory=list, description="""Signal types this element consumes (e.g. ``[current, voltage]``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Signal types this element consumes (e.g. ``[current, voltage]``)."""
    outputs: list[IOTypeEnum] = Field(default_factory=list, description="""Signal types this element produces (e.g. ``[power, phase]``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Signal types this element produces (e.g. ``[power, phase]``)."""
    upstream: list[str] = Field(default_factory=list, description="""Names of elements feeding this one, whose ``outputs`` supply its ``inputs``.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Names of elements feeding this one, whose ``outputs`` supply its ``inputs``."""
    downstream: list[str] = Field(default_factory=list, description="""Names of elements this one feeds; the inverse of ``upstream``.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Names of elements this one feeds; the inverse of ``upstream``."""


class _TwissMatchBase(_PhysicalAcceleratorElementBase):
    """
    Virtual Twiss-parameter matching point -- a zero-length marker that defines the desired optical functions at a location in the lattice.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:TwissMatch',
         'from_schema': 'https://w3id.org/laura/schema/elements',
         'slot_usage': {'hardware_type': {'equals_string': 'TwissMatch',
                                          'name': 'hardware_type'},
                        'simulation': {'name': 'simulation',
                                       'range': 'TwissMatchSimulationElement'}}})

    physical: Optional[_PhysicalElementBase] = Field(default=None, description="""Position, rotation, and length data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PhysicalAcceleratorElement'],
         'in_subset': ['physical_properties']} })
    """Position, rotation, and length data."""
    simulation: Optional[_TwissMatchSimulationElementBase] = Field(default=None, description="""Simulation / tracking attributes.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Simulation / tracking attributes."""
    electrical: Optional[_ElectricalElementBase] = Field(default=None, description="""Power-supply electrical limits.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Power-supply electrical limits."""
    manufacturer: Optional[_ManufacturerElementBase] = Field(default=None, description="""Manufacturer and serial-number data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ManufacturerElement', 'StandardElement']} })
    """Manufacturer and serial-number data."""
    controls: Optional[_ControlsInformationBase] = Field(default=None, description="""Control-system process-variable definitions.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Control-system process-variable definitions."""
    reference: Optional[_ReferenceElementBase] = Field(default=None, description="""Links to design drawings and files.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Links to design drawings and files."""
    name: str = Field(default=..., description="""Unique element name within the machine.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SectionLattice', 'MachineLayout', 'AcceleratorElement']} })
    """Unique element name within the machine."""
    hardware_class: HardwareClassEnum = Field(default=..., description="""Functional category (e.g., ``Magnet``, ``Diagnostic``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Functional category (e.g., ``Magnet``, ``Diagnostic``)."""
    hardware_type: Optional[Literal["TwissMatch"]] = Field(default="Generic", description="""Python class name used for ELEMENT_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'],
         'equals_string': 'TwissMatch',
         'ifabsent': 'string(Generic)'} })
    """Python class name used for ELEMENT_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML."""
    hardware_model: str = Field(default="Generic", description="""Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string(Generic)'} })
    """Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``)."""
    machine_area: Optional[str] = Field(default=None, description="""Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``)."""
    virtual_name: str = Field(default="", description="""Alternative internal name used by the control system when the physical name is inaccessible.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string()'} })
    """Alternative internal name used by the control system when the physical name is inaccessible."""
    alias: list[str] = Field(default_factory=list, description="""Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.""", validation_alias=AliasChoices('alias', 'name_alias'), json_schema_extra = { "linkml_meta": {'aliases': ['name_alias'], 'domain_of': ['AcceleratorElement']} })
    """Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings."""
    subelement: Optional[str] = Field(default=None, description="""If set, this element is a logical sub-component of the named parent element.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """If set, this element is a logical sub-component of the named parent element."""
    inputs: list[IOTypeEnum] = Field(default_factory=list, description="""Signal types this element consumes (e.g. ``[current, voltage]``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Signal types this element consumes (e.g. ``[current, voltage]``)."""
    outputs: list[IOTypeEnum] = Field(default_factory=list, description="""Signal types this element produces (e.g. ``[power, phase]``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Signal types this element produces (e.g. ``[power, phase]``)."""
    upstream: list[str] = Field(default_factory=list, description="""Names of elements feeding this one, whose ``outputs`` supply its ``inputs``.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Names of elements feeding this one, whose ``outputs`` supply its ``inputs``."""
    downstream: list[str] = Field(default_factory=list, description="""Names of elements this one feeds; the inverse of ``upstream``.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Names of elements this one feeds; the inverse of ``upstream``."""


class _MatrixTransformBase(_PhysicalAcceleratorElementBase):
    """
    Transfer-map element with zero-, first-, and second-order coefficients.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:MatrixTransform',
         'from_schema': 'https://w3id.org/laura/schema/elements',
         'slot_usage': {'hardware_type': {'equals_string': 'MatrixTransform',
                                          'name': 'hardware_type'},
                        'simulation': {'name': 'simulation',
                                       'range': 'MatrixTransformSimulationElement'}}})

    physical: Optional[_PhysicalElementBase] = Field(default=None, description="""Position, rotation, and length data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PhysicalAcceleratorElement'],
         'in_subset': ['physical_properties']} })
    """Position, rotation, and length data."""
    simulation: Optional[_MatrixTransformSimulationElementBase] = Field(default=None, description="""Simulation / tracking attributes.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Simulation / tracking attributes."""
    electrical: Optional[_ElectricalElementBase] = Field(default=None, description="""Power-supply electrical limits.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Power-supply electrical limits."""
    manufacturer: Optional[_ManufacturerElementBase] = Field(default=None, description="""Manufacturer and serial-number data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ManufacturerElement', 'StandardElement']} })
    """Manufacturer and serial-number data."""
    controls: Optional[_ControlsInformationBase] = Field(default=None, description="""Control-system process-variable definitions.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Control-system process-variable definitions."""
    reference: Optional[_ReferenceElementBase] = Field(default=None, description="""Links to design drawings and files.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Links to design drawings and files."""
    name: str = Field(default=..., description="""Unique element name within the machine.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SectionLattice', 'MachineLayout', 'AcceleratorElement']} })
    """Unique element name within the machine."""
    hardware_class: HardwareClassEnum = Field(default=..., description="""Functional category (e.g., ``Magnet``, ``Diagnostic``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Functional category (e.g., ``Magnet``, ``Diagnostic``)."""
    hardware_type: Optional[Literal["MatrixTransform"]] = Field(default="Generic", description="""Python class name used for ELEMENT_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'],
         'equals_string': 'MatrixTransform',
         'ifabsent': 'string(Generic)'} })
    """Python class name used for ELEMENT_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML."""
    hardware_model: str = Field(default="Generic", description="""Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string(Generic)'} })
    """Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``)."""
    machine_area: Optional[str] = Field(default=None, description="""Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``)."""
    virtual_name: str = Field(default="", description="""Alternative internal name used by the control system when the physical name is inaccessible.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string()'} })
    """Alternative internal name used by the control system when the physical name is inaccessible."""
    alias: list[str] = Field(default_factory=list, description="""Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.""", validation_alias=AliasChoices('alias', 'name_alias'), json_schema_extra = { "linkml_meta": {'aliases': ['name_alias'], 'domain_of': ['AcceleratorElement']} })
    """Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings."""
    subelement: Optional[str] = Field(default=None, description="""If set, this element is a logical sub-component of the named parent element.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """If set, this element is a logical sub-component of the named parent element."""
    inputs: list[IOTypeEnum] = Field(default_factory=list, description="""Signal types this element consumes (e.g. ``[current, voltage]``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Signal types this element consumes (e.g. ``[current, voltage]``)."""
    outputs: list[IOTypeEnum] = Field(default_factory=list, description="""Signal types this element produces (e.g. ``[power, phase]``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Signal types this element produces (e.g. ``[power, phase]``)."""
    upstream: list[str] = Field(default_factory=list, description="""Names of elements feeding this one, whose ``outputs`` supply its ``inputs``.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Names of elements feeding this one, whose ``outputs`` supply its ``inputs``."""
    downstream: list[str] = Field(default_factory=list, description="""Names of elements this one feeds; the inverse of ``upstream``.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Names of elements this one feeds; the inverse of ``upstream``."""


class _ElectrostaticSeparatorBase(_PhysicalAcceleratorElementBase):
    """
    Static electrostatic transverse-deflection element.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:ElectrostaticSeparator',
         'from_schema': 'https://w3id.org/laura/schema/elements',
         'slot_usage': {'hardware_type': {'equals_string': 'ElectrostaticSeparator',
                                          'name': 'hardware_type'},
                        'simulation': {'name': 'simulation',
                                       'range': 'ElectrostaticSeparatorSimulationElement'}}})

    physical: Optional[_PhysicalElementBase] = Field(default=None, description="""Position, rotation, and length data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PhysicalAcceleratorElement'],
         'in_subset': ['physical_properties']} })
    """Position, rotation, and length data."""
    simulation: Optional[_ElectrostaticSeparatorSimulationElementBase] = Field(default=None, description="""Simulation / tracking attributes.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Simulation / tracking attributes."""
    electrical: Optional[_ElectricalElementBase] = Field(default=None, description="""Power-supply electrical limits.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Power-supply electrical limits."""
    manufacturer: Optional[_ManufacturerElementBase] = Field(default=None, description="""Manufacturer and serial-number data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ManufacturerElement', 'StandardElement']} })
    """Manufacturer and serial-number data."""
    controls: Optional[_ControlsInformationBase] = Field(default=None, description="""Control-system process-variable definitions.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Control-system process-variable definitions."""
    reference: Optional[_ReferenceElementBase] = Field(default=None, description="""Links to design drawings and files.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Links to design drawings and files."""
    name: str = Field(default=..., description="""Unique element name within the machine.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SectionLattice', 'MachineLayout', 'AcceleratorElement']} })
    """Unique element name within the machine."""
    hardware_class: HardwareClassEnum = Field(default=..., description="""Functional category (e.g., ``Magnet``, ``Diagnostic``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Functional category (e.g., ``Magnet``, ``Diagnostic``)."""
    hardware_type: Optional[Literal["ElectrostaticSeparator"]] = Field(default="Generic", description="""Python class name used for ELEMENT_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'],
         'equals_string': 'ElectrostaticSeparator',
         'ifabsent': 'string(Generic)'} })
    """Python class name used for ELEMENT_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML."""
    hardware_model: str = Field(default="Generic", description="""Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string(Generic)'} })
    """Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``)."""
    machine_area: Optional[str] = Field(default=None, description="""Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``)."""
    virtual_name: str = Field(default="", description="""Alternative internal name used by the control system when the physical name is inaccessible.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string()'} })
    """Alternative internal name used by the control system when the physical name is inaccessible."""
    alias: list[str] = Field(default_factory=list, description="""Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.""", validation_alias=AliasChoices('alias', 'name_alias'), json_schema_extra = { "linkml_meta": {'aliases': ['name_alias'], 'domain_of': ['AcceleratorElement']} })
    """Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings."""
    subelement: Optional[str] = Field(default=None, description="""If set, this element is a logical sub-component of the named parent element.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """If set, this element is a logical sub-component of the named parent element."""
    inputs: list[IOTypeEnum] = Field(default_factory=list, description="""Signal types this element consumes (e.g. ``[current, voltage]``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Signal types this element consumes (e.g. ``[current, voltage]``)."""
    outputs: list[IOTypeEnum] = Field(default_factory=list, description="""Signal types this element produces (e.g. ``[power, phase]``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Signal types this element produces (e.g. ``[power, phase]``)."""
    upstream: list[str] = Field(default_factory=list, description="""Names of elements feeding this one, whose ``outputs`` supply its ``inputs``.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Names of elements feeding this one, whose ``outputs`` supply its ``inputs``."""
    downstream: list[str] = Field(default_factory=list, description="""Names of elements this one feeds; the inverse of ``upstream``.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Names of elements this one feeds; the inverse of ``upstream``."""


class _ACDipoleBase(_PhysicalAcceleratorElementBase):
    """
    Base class for horizontal and vertical AC-dipole tune exciters.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'abstract': True,
         'class_uri': 'laura:ACDipole',
         'from_schema': 'https://w3id.org/laura/schema/elements',
         'slot_usage': {'simulation': {'name': 'simulation',
                                       'range': 'ACDipoleSimulationElement'}}})

    physical: Optional[_PhysicalElementBase] = Field(default=None, description="""Position, rotation, and length data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PhysicalAcceleratorElement'],
         'in_subset': ['physical_properties']} })
    """Position, rotation, and length data."""
    simulation: Optional[_ACDipoleSimulationElementBase] = Field(default=None, description="""Simulation / tracking attributes.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Simulation / tracking attributes."""
    electrical: Optional[_ElectricalElementBase] = Field(default=None, description="""Power-supply electrical limits.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Power-supply electrical limits."""
    manufacturer: Optional[_ManufacturerElementBase] = Field(default=None, description="""Manufacturer and serial-number data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ManufacturerElement', 'StandardElement']} })
    """Manufacturer and serial-number data."""
    controls: Optional[_ControlsInformationBase] = Field(default=None, description="""Control-system process-variable definitions.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Control-system process-variable definitions."""
    reference: Optional[_ReferenceElementBase] = Field(default=None, description="""Links to design drawings and files.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Links to design drawings and files."""
    name: str = Field(default=..., description="""Unique element name within the machine.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SectionLattice', 'MachineLayout', 'AcceleratorElement']} })
    """Unique element name within the machine."""
    hardware_class: HardwareClassEnum = Field(default=..., description="""Functional category (e.g., ``Magnet``, ``Diagnostic``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Functional category (e.g., ``Magnet``, ``Diagnostic``)."""
    hardware_type: str = Field(default="Generic", description="""Python class name used for ELEMENT_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string(Generic)'} })
    """Python class name used for ELEMENT_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML."""
    hardware_model: str = Field(default="Generic", description="""Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string(Generic)'} })
    """Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``)."""
    machine_area: Optional[str] = Field(default=None, description="""Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``)."""
    virtual_name: str = Field(default="", description="""Alternative internal name used by the control system when the physical name is inaccessible.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string()'} })
    """Alternative internal name used by the control system when the physical name is inaccessible."""
    alias: list[str] = Field(default_factory=list, description="""Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.""", validation_alias=AliasChoices('alias', 'name_alias'), json_schema_extra = { "linkml_meta": {'aliases': ['name_alias'], 'domain_of': ['AcceleratorElement']} })
    """Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings."""
    subelement: Optional[str] = Field(default=None, description="""If set, this element is a logical sub-component of the named parent element.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """If set, this element is a logical sub-component of the named parent element."""
    inputs: list[IOTypeEnum] = Field(default_factory=list, description="""Signal types this element consumes (e.g. ``[current, voltage]``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Signal types this element consumes (e.g. ``[current, voltage]``)."""
    outputs: list[IOTypeEnum] = Field(default_factory=list, description="""Signal types this element produces (e.g. ``[power, phase]``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Signal types this element produces (e.g. ``[power, phase]``)."""
    upstream: list[str] = Field(default_factory=list, description="""Names of elements feeding this one, whose ``outputs`` supply its ``inputs``.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Names of elements feeding this one, whose ``outputs`` supply its ``inputs``."""
    downstream: list[str] = Field(default_factory=list, description="""Names of elements this one feeds; the inverse of ``upstream``.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Names of elements this one feeds; the inverse of ``upstream``."""


class _HorizontalACDipoleBase(_ACDipoleBase):
    """
    Horizontally deflecting AC-dipole tune exciter.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:Horizontal_AC_Dipole',
         'from_schema': 'https://w3id.org/laura/schema/elements',
         'slot_usage': {'hardware_type': {'equals_string': 'Horizontal_AC_Dipole',
                                          'name': 'hardware_type'}}})

    physical: Optional[_PhysicalElementBase] = Field(default=None, description="""Position, rotation, and length data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PhysicalAcceleratorElement'],
         'in_subset': ['physical_properties']} })
    """Position, rotation, and length data."""
    simulation: Optional[_ACDipoleSimulationElementBase] = Field(default=None, description="""Simulation / tracking attributes.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Simulation / tracking attributes."""
    electrical: Optional[_ElectricalElementBase] = Field(default=None, description="""Power-supply electrical limits.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Power-supply electrical limits."""
    manufacturer: Optional[_ManufacturerElementBase] = Field(default=None, description="""Manufacturer and serial-number data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ManufacturerElement', 'StandardElement']} })
    """Manufacturer and serial-number data."""
    controls: Optional[_ControlsInformationBase] = Field(default=None, description="""Control-system process-variable definitions.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Control-system process-variable definitions."""
    reference: Optional[_ReferenceElementBase] = Field(default=None, description="""Links to design drawings and files.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Links to design drawings and files."""
    name: str = Field(default=..., description="""Unique element name within the machine.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SectionLattice', 'MachineLayout', 'AcceleratorElement']} })
    """Unique element name within the machine."""
    hardware_class: HardwareClassEnum = Field(default=..., description="""Functional category (e.g., ``Magnet``, ``Diagnostic``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Functional category (e.g., ``Magnet``, ``Diagnostic``)."""
    hardware_type: Optional[Literal["Horizontal_AC_Dipole"]] = Field(default="Generic", description="""Python class name used for ELEMENT_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'],
         'equals_string': 'Horizontal_AC_Dipole',
         'ifabsent': 'string(Generic)'} })
    """Python class name used for ELEMENT_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML."""
    hardware_model: str = Field(default="Generic", description="""Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string(Generic)'} })
    """Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``)."""
    machine_area: Optional[str] = Field(default=None, description="""Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``)."""
    virtual_name: str = Field(default="", description="""Alternative internal name used by the control system when the physical name is inaccessible.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string()'} })
    """Alternative internal name used by the control system when the physical name is inaccessible."""
    alias: list[str] = Field(default_factory=list, description="""Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.""", validation_alias=AliasChoices('alias', 'name_alias'), json_schema_extra = { "linkml_meta": {'aliases': ['name_alias'], 'domain_of': ['AcceleratorElement']} })
    """Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings."""
    subelement: Optional[str] = Field(default=None, description="""If set, this element is a logical sub-component of the named parent element.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """If set, this element is a logical sub-component of the named parent element."""
    inputs: list[IOTypeEnum] = Field(default_factory=list, description="""Signal types this element consumes (e.g. ``[current, voltage]``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Signal types this element consumes (e.g. ``[current, voltage]``)."""
    outputs: list[IOTypeEnum] = Field(default_factory=list, description="""Signal types this element produces (e.g. ``[power, phase]``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Signal types this element produces (e.g. ``[power, phase]``)."""
    upstream: list[str] = Field(default_factory=list, description="""Names of elements feeding this one, whose ``outputs`` supply its ``inputs``.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Names of elements feeding this one, whose ``outputs`` supply its ``inputs``."""
    downstream: list[str] = Field(default_factory=list, description="""Names of elements this one feeds; the inverse of ``upstream``.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Names of elements this one feeds; the inverse of ``upstream``."""


class _VerticalACDipoleBase(_ACDipoleBase):
    """
    Vertically deflecting AC-dipole tune exciter.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:Vertical_AC_Dipole',
         'from_schema': 'https://w3id.org/laura/schema/elements',
         'slot_usage': {'hardware_type': {'equals_string': 'Vertical_AC_Dipole',
                                          'name': 'hardware_type'}}})

    physical: Optional[_PhysicalElementBase] = Field(default=None, description="""Position, rotation, and length data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PhysicalAcceleratorElement'],
         'in_subset': ['physical_properties']} })
    """Position, rotation, and length data."""
    simulation: Optional[_ACDipoleSimulationElementBase] = Field(default=None, description="""Simulation / tracking attributes.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Simulation / tracking attributes."""
    electrical: Optional[_ElectricalElementBase] = Field(default=None, description="""Power-supply electrical limits.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Power-supply electrical limits."""
    manufacturer: Optional[_ManufacturerElementBase] = Field(default=None, description="""Manufacturer and serial-number data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ManufacturerElement', 'StandardElement']} })
    """Manufacturer and serial-number data."""
    controls: Optional[_ControlsInformationBase] = Field(default=None, description="""Control-system process-variable definitions.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Control-system process-variable definitions."""
    reference: Optional[_ReferenceElementBase] = Field(default=None, description="""Links to design drawings and files.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Links to design drawings and files."""
    name: str = Field(default=..., description="""Unique element name within the machine.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SectionLattice', 'MachineLayout', 'AcceleratorElement']} })
    """Unique element name within the machine."""
    hardware_class: HardwareClassEnum = Field(default=..., description="""Functional category (e.g., ``Magnet``, ``Diagnostic``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Functional category (e.g., ``Magnet``, ``Diagnostic``)."""
    hardware_type: Optional[Literal["Vertical_AC_Dipole"]] = Field(default="Generic", description="""Python class name used for ELEMENT_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'],
         'equals_string': 'Vertical_AC_Dipole',
         'ifabsent': 'string(Generic)'} })
    """Python class name used for ELEMENT_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML."""
    hardware_model: str = Field(default="Generic", description="""Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string(Generic)'} })
    """Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``)."""
    machine_area: Optional[str] = Field(default=None, description="""Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``)."""
    virtual_name: str = Field(default="", description="""Alternative internal name used by the control system when the physical name is inaccessible.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string()'} })
    """Alternative internal name used by the control system when the physical name is inaccessible."""
    alias: list[str] = Field(default_factory=list, description="""Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.""", validation_alias=AliasChoices('alias', 'name_alias'), json_schema_extra = { "linkml_meta": {'aliases': ['name_alias'], 'domain_of': ['AcceleratorElement']} })
    """Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings."""
    subelement: Optional[str] = Field(default=None, description="""If set, this element is a logical sub-component of the named parent element.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """If set, this element is a logical sub-component of the named parent element."""
    inputs: list[IOTypeEnum] = Field(default_factory=list, description="""Signal types this element consumes (e.g. ``[current, voltage]``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Signal types this element consumes (e.g. ``[current, voltage]``)."""
    outputs: list[IOTypeEnum] = Field(default_factory=list, description="""Signal types this element produces (e.g. ``[power, phase]``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Signal types this element produces (e.g. ``[power, phase]``)."""
    upstream: list[str] = Field(default_factory=list, description="""Names of elements feeding this one, whose ``outputs`` supply its ``inputs``.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Names of elements feeding this one, whose ``outputs`` supply its ``inputs``."""
    downstream: list[str] = Field(default_factory=list, description="""Names of elements this one feeds; the inverse of ``upstream``.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Names of elements this one feeds; the inverse of ``upstream``."""


class _WireBase(_PhysicalAcceleratorElementBase):
    """
    Current-carrying wire for long-range beam-beam compensation.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:Wire',
         'from_schema': 'https://w3id.org/laura/schema/elements',
         'slot_usage': {'hardware_type': {'equals_string': 'Wire',
                                          'name': 'hardware_type'},
                        'simulation': {'name': 'simulation',
                                       'range': 'WireSimulationElement'}}})

    physical: Optional[_PhysicalElementBase] = Field(default=None, description="""Position, rotation, and length data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PhysicalAcceleratorElement'],
         'in_subset': ['physical_properties']} })
    """Position, rotation, and length data."""
    simulation: Optional[_WireSimulationElementBase] = Field(default=None, description="""Simulation / tracking attributes.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Simulation / tracking attributes."""
    electrical: Optional[_ElectricalElementBase] = Field(default=None, description="""Power-supply electrical limits.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Power-supply electrical limits."""
    manufacturer: Optional[_ManufacturerElementBase] = Field(default=None, description="""Manufacturer and serial-number data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ManufacturerElement', 'StandardElement']} })
    """Manufacturer and serial-number data."""
    controls: Optional[_ControlsInformationBase] = Field(default=None, description="""Control-system process-variable definitions.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Control-system process-variable definitions."""
    reference: Optional[_ReferenceElementBase] = Field(default=None, description="""Links to design drawings and files.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Links to design drawings and files."""
    name: str = Field(default=..., description="""Unique element name within the machine.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SectionLattice', 'MachineLayout', 'AcceleratorElement']} })
    """Unique element name within the machine."""
    hardware_class: HardwareClassEnum = Field(default=..., description="""Functional category (e.g., ``Magnet``, ``Diagnostic``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Functional category (e.g., ``Magnet``, ``Diagnostic``)."""
    hardware_type: Optional[Literal["Wire"]] = Field(default="Generic", description="""Python class name used for ELEMENT_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'],
         'equals_string': 'Wire',
         'ifabsent': 'string(Generic)'} })
    """Python class name used for ELEMENT_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML."""
    hardware_model: str = Field(default="Generic", description="""Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string(Generic)'} })
    """Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``)."""
    machine_area: Optional[str] = Field(default=None, description="""Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``)."""
    virtual_name: str = Field(default="", description="""Alternative internal name used by the control system when the physical name is inaccessible.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string()'} })
    """Alternative internal name used by the control system when the physical name is inaccessible."""
    alias: list[str] = Field(default_factory=list, description="""Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.""", validation_alias=AliasChoices('alias', 'name_alias'), json_schema_extra = { "linkml_meta": {'aliases': ['name_alias'], 'domain_of': ['AcceleratorElement']} })
    """Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings."""
    subelement: Optional[str] = Field(default=None, description="""If set, this element is a logical sub-component of the named parent element.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """If set, this element is a logical sub-component of the named parent element."""
    inputs: list[IOTypeEnum] = Field(default_factory=list, description="""Signal types this element consumes (e.g. ``[current, voltage]``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Signal types this element consumes (e.g. ``[current, voltage]``)."""
    outputs: list[IOTypeEnum] = Field(default_factory=list, description="""Signal types this element produces (e.g. ``[power, phase]``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Signal types this element produces (e.g. ``[power, phase]``)."""
    upstream: list[str] = Field(default_factory=list, description="""Names of elements feeding this one, whose ``outputs`` supply its ``inputs``.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Names of elements feeding this one, whose ``outputs`` supply its ``inputs``."""
    downstream: list[str] = Field(default_factory=list, description="""Names of elements this one feeds; the inverse of ``upstream``.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Names of elements this one feeds; the inverse of ``upstream``."""


class _BeamBeamBase(_PhysicalAcceleratorElementBase):
    """
    Weak-strong beam-beam interaction element.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:BeamBeam',
         'from_schema': 'https://w3id.org/laura/schema/elements',
         'slot_usage': {'hardware_type': {'equals_string': 'BeamBeam',
                                          'name': 'hardware_type'},
                        'simulation': {'name': 'simulation',
                                       'range': 'BeamBeamSimulationElement'}}})

    physical: Optional[_PhysicalElementBase] = Field(default=None, description="""Position, rotation, and length data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PhysicalAcceleratorElement'],
         'in_subset': ['physical_properties']} })
    """Position, rotation, and length data."""
    simulation: Optional[_BeamBeamSimulationElementBase] = Field(default=None, description="""Simulation / tracking attributes.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Simulation / tracking attributes."""
    electrical: Optional[_ElectricalElementBase] = Field(default=None, description="""Power-supply electrical limits.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Power-supply electrical limits."""
    manufacturer: Optional[_ManufacturerElementBase] = Field(default=None, description="""Manufacturer and serial-number data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ManufacturerElement', 'StandardElement']} })
    """Manufacturer and serial-number data."""
    controls: Optional[_ControlsInformationBase] = Field(default=None, description="""Control-system process-variable definitions.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Control-system process-variable definitions."""
    reference: Optional[_ReferenceElementBase] = Field(default=None, description="""Links to design drawings and files.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Links to design drawings and files."""
    name: str = Field(default=..., description="""Unique element name within the machine.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SectionLattice', 'MachineLayout', 'AcceleratorElement']} })
    """Unique element name within the machine."""
    hardware_class: HardwareClassEnum = Field(default=..., description="""Functional category (e.g., ``Magnet``, ``Diagnostic``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Functional category (e.g., ``Magnet``, ``Diagnostic``)."""
    hardware_type: Optional[Literal["BeamBeam"]] = Field(default="Generic", description="""Python class name used for ELEMENT_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'],
         'equals_string': 'BeamBeam',
         'ifabsent': 'string(Generic)'} })
    """Python class name used for ELEMENT_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML."""
    hardware_model: str = Field(default="Generic", description="""Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string(Generic)'} })
    """Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``)."""
    machine_area: Optional[str] = Field(default=None, description="""Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``)."""
    virtual_name: str = Field(default="", description="""Alternative internal name used by the control system when the physical name is inaccessible.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string()'} })
    """Alternative internal name used by the control system when the physical name is inaccessible."""
    alias: list[str] = Field(default_factory=list, description="""Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.""", validation_alias=AliasChoices('alias', 'name_alias'), json_schema_extra = { "linkml_meta": {'aliases': ['name_alias'], 'domain_of': ['AcceleratorElement']} })
    """Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings."""
    subelement: Optional[str] = Field(default=None, description="""If set, this element is a logical sub-component of the named parent element.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """If set, this element is a logical sub-component of the named parent element."""
    inputs: list[IOTypeEnum] = Field(default_factory=list, description="""Signal types this element consumes (e.g. ``[current, voltage]``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Signal types this element consumes (e.g. ``[current, voltage]``)."""
    outputs: list[IOTypeEnum] = Field(default_factory=list, description="""Signal types this element produces (e.g. ``[power, phase]``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Signal types this element produces (e.g. ``[power, phase]``)."""
    upstream: list[str] = Field(default_factory=list, description="""Names of elements feeding this one, whose ``outputs`` supply its ``inputs``.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Names of elements feeding this one, whose ``outputs`` supply its ``inputs``."""
    downstream: list[str] = Field(default_factory=list, description="""Names of elements this one feeds; the inverse of ``upstream``.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Names of elements this one feeds; the inverse of ``upstream``."""


class _RFMultipoleBase(_PhysicalAcceleratorElementBase):
    """
    Thin RF-driven multipole kick.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:RFMultipole',
         'from_schema': 'https://w3id.org/laura/schema/elements',
         'slot_usage': {'hardware_type': {'equals_string': 'RFMultipole',
                                          'name': 'hardware_type'},
                        'simulation': {'name': 'simulation',
                                       'range': 'RFMultipoleSimulationElement'}}})

    physical: Optional[_PhysicalElementBase] = Field(default=None, description="""Position, rotation, and length data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PhysicalAcceleratorElement'],
         'in_subset': ['physical_properties']} })
    """Position, rotation, and length data."""
    simulation: Optional[_RFMultipoleSimulationElementBase] = Field(default=None, description="""Simulation / tracking attributes.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Simulation / tracking attributes."""
    electrical: Optional[_ElectricalElementBase] = Field(default=None, description="""Power-supply electrical limits.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Power-supply electrical limits."""
    manufacturer: Optional[_ManufacturerElementBase] = Field(default=None, description="""Manufacturer and serial-number data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ManufacturerElement', 'StandardElement']} })
    """Manufacturer and serial-number data."""
    controls: Optional[_ControlsInformationBase] = Field(default=None, description="""Control-system process-variable definitions.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Control-system process-variable definitions."""
    reference: Optional[_ReferenceElementBase] = Field(default=None, description="""Links to design drawings and files.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Links to design drawings and files."""
    name: str = Field(default=..., description="""Unique element name within the machine.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SectionLattice', 'MachineLayout', 'AcceleratorElement']} })
    """Unique element name within the machine."""
    hardware_class: HardwareClassEnum = Field(default=..., description="""Functional category (e.g., ``Magnet``, ``Diagnostic``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Functional category (e.g., ``Magnet``, ``Diagnostic``)."""
    hardware_type: Optional[Literal["RFMultipole"]] = Field(default="Generic", description="""Python class name used for ELEMENT_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'],
         'equals_string': 'RFMultipole',
         'ifabsent': 'string(Generic)'} })
    """Python class name used for ELEMENT_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML."""
    hardware_model: str = Field(default="Generic", description="""Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string(Generic)'} })
    """Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``)."""
    machine_area: Optional[str] = Field(default=None, description="""Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``)."""
    virtual_name: str = Field(default="", description="""Alternative internal name used by the control system when the physical name is inaccessible.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string()'} })
    """Alternative internal name used by the control system when the physical name is inaccessible."""
    alias: list[str] = Field(default_factory=list, description="""Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.""", validation_alias=AliasChoices('alias', 'name_alias'), json_schema_extra = { "linkml_meta": {'aliases': ['name_alias'], 'domain_of': ['AcceleratorElement']} })
    """Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings."""
    subelement: Optional[str] = Field(default=None, description="""If set, this element is a logical sub-component of the named parent element.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """If set, this element is a logical sub-component of the named parent element."""
    inputs: list[IOTypeEnum] = Field(default_factory=list, description="""Signal types this element consumes (e.g. ``[current, voltage]``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Signal types this element consumes (e.g. ``[current, voltage]``)."""
    outputs: list[IOTypeEnum] = Field(default_factory=list, description="""Signal types this element produces (e.g. ``[power, phase]``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Signal types this element produces (e.g. ``[power, phase]``)."""
    upstream: list[str] = Field(default_factory=list, description="""Names of elements feeding this one, whose ``outputs`` supply its ``inputs``.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Names of elements feeding this one, whose ``outputs`` supply its ``inputs``."""
    downstream: list[str] = Field(default_factory=list, description="""Names of elements this one feeds; the inverse of ``upstream``.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Names of elements this one feeds; the inverse of ``upstream``."""


class _StageBase(_PhysicalAcceleratorElementBase):
    """
    Motorised positioning stage.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:Stage',
         'from_schema': 'https://w3id.org/laura/schema/elements',
         'slot_usage': {'hardware_type': {'equals_string': 'Stage',
                                          'name': 'hardware_type'}}})

    physical: Optional[_PhysicalElementBase] = Field(default=None, description="""Position, rotation, and length data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PhysicalAcceleratorElement'],
         'in_subset': ['physical_properties']} })
    """Position, rotation, and length data."""
    simulation: Optional[_SimulationElementBase] = Field(default=None, description="""Simulation / tracking attributes.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Simulation / tracking attributes."""
    electrical: Optional[_ElectricalElementBase] = Field(default=None, description="""Power-supply electrical limits.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Power-supply electrical limits."""
    manufacturer: Optional[_ManufacturerElementBase] = Field(default=None, description="""Manufacturer and serial-number data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ManufacturerElement', 'StandardElement']} })
    """Manufacturer and serial-number data."""
    controls: Optional[_ControlsInformationBase] = Field(default=None, description="""Control-system process-variable definitions.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Control-system process-variable definitions."""
    reference: Optional[_ReferenceElementBase] = Field(default=None, description="""Links to design drawings and files.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Links to design drawings and files."""
    name: str = Field(default=..., description="""Unique element name within the machine.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SectionLattice', 'MachineLayout', 'AcceleratorElement']} })
    """Unique element name within the machine."""
    hardware_class: HardwareClassEnum = Field(default=..., description="""Functional category (e.g., ``Magnet``, ``Diagnostic``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Functional category (e.g., ``Magnet``, ``Diagnostic``)."""
    hardware_type: Optional[Literal["Stage"]] = Field(default="Generic", description="""Python class name used for ELEMENT_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'],
         'equals_string': 'Stage',
         'ifabsent': 'string(Generic)'} })
    """Python class name used for ELEMENT_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML."""
    hardware_model: str = Field(default="Generic", description="""Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string(Generic)'} })
    """Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``)."""
    machine_area: Optional[str] = Field(default=None, description="""Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``)."""
    virtual_name: str = Field(default="", description="""Alternative internal name used by the control system when the physical name is inaccessible.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string()'} })
    """Alternative internal name used by the control system when the physical name is inaccessible."""
    alias: list[str] = Field(default_factory=list, description="""Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.""", validation_alias=AliasChoices('alias', 'name_alias'), json_schema_extra = { "linkml_meta": {'aliases': ['name_alias'], 'domain_of': ['AcceleratorElement']} })
    """Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings."""
    subelement: Optional[str] = Field(default=None, description="""If set, this element is a logical sub-component of the named parent element.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """If set, this element is a logical sub-component of the named parent element."""
    inputs: list[IOTypeEnum] = Field(default_factory=list, description="""Signal types this element consumes (e.g. ``[current, voltage]``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Signal types this element consumes (e.g. ``[current, voltage]``)."""
    outputs: list[IOTypeEnum] = Field(default_factory=list, description="""Signal types this element produces (e.g. ``[power, phase]``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Signal types this element produces (e.g. ``[power, phase]``)."""
    upstream: list[str] = Field(default_factory=list, description="""Names of elements feeding this one, whose ``outputs`` supply its ``inputs``.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Names of elements feeding this one, whose ``outputs`` supply its ``inputs``."""
    downstream: list[str] = Field(default_factory=list, description="""Names of elements this one feeds; the inverse of ``upstream``.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Names of elements this one feeds; the inverse of ``upstream``."""


class _VacuumGaugeBase(_PhysicalAcceleratorElementBase):
    """
    Vacuum-pressure gauge.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:VacuumGauge',
         'from_schema': 'https://w3id.org/laura/schema/elements',
         'slot_usage': {'hardware_type': {'equals_string': 'VacuumGauge',
                                          'name': 'hardware_type'}}})

    physical: Optional[_PhysicalElementBase] = Field(default=None, description="""Position, rotation, and length data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PhysicalAcceleratorElement'],
         'in_subset': ['physical_properties']} })
    """Position, rotation, and length data."""
    simulation: Optional[_SimulationElementBase] = Field(default=None, description="""Simulation / tracking attributes.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Simulation / tracking attributes."""
    electrical: Optional[_ElectricalElementBase] = Field(default=None, description="""Power-supply electrical limits.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Power-supply electrical limits."""
    manufacturer: Optional[_ManufacturerElementBase] = Field(default=None, description="""Manufacturer and serial-number data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ManufacturerElement', 'StandardElement']} })
    """Manufacturer and serial-number data."""
    controls: Optional[_ControlsInformationBase] = Field(default=None, description="""Control-system process-variable definitions.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Control-system process-variable definitions."""
    reference: Optional[_ReferenceElementBase] = Field(default=None, description="""Links to design drawings and files.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Links to design drawings and files."""
    name: str = Field(default=..., description="""Unique element name within the machine.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SectionLattice', 'MachineLayout', 'AcceleratorElement']} })
    """Unique element name within the machine."""
    hardware_class: HardwareClassEnum = Field(default=..., description="""Functional category (e.g., ``Magnet``, ``Diagnostic``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Functional category (e.g., ``Magnet``, ``Diagnostic``)."""
    hardware_type: Optional[Literal["VacuumGauge"]] = Field(default="Generic", description="""Python class name used for ELEMENT_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'],
         'equals_string': 'VacuumGauge',
         'ifabsent': 'string(Generic)'} })
    """Python class name used for ELEMENT_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML."""
    hardware_model: str = Field(default="Generic", description="""Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string(Generic)'} })
    """Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``)."""
    machine_area: Optional[str] = Field(default=None, description="""Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``)."""
    virtual_name: str = Field(default="", description="""Alternative internal name used by the control system when the physical name is inaccessible.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string()'} })
    """Alternative internal name used by the control system when the physical name is inaccessible."""
    alias: list[str] = Field(default_factory=list, description="""Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.""", validation_alias=AliasChoices('alias', 'name_alias'), json_schema_extra = { "linkml_meta": {'aliases': ['name_alias'], 'domain_of': ['AcceleratorElement']} })
    """Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings."""
    subelement: Optional[str] = Field(default=None, description="""If set, this element is a logical sub-component of the named parent element.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """If set, this element is a logical sub-component of the named parent element."""
    inputs: list[IOTypeEnum] = Field(default_factory=list, description="""Signal types this element consumes (e.g. ``[current, voltage]``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Signal types this element consumes (e.g. ``[current, voltage]``)."""
    outputs: list[IOTypeEnum] = Field(default_factory=list, description="""Signal types this element produces (e.g. ``[power, phase]``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Signal types this element produces (e.g. ``[power, phase]``)."""
    upstream: list[str] = Field(default_factory=list, description="""Names of elements feeding this one, whose ``outputs`` supply its ``inputs``.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Names of elements feeding this one, whose ``outputs`` supply its ``inputs``."""
    downstream: list[str] = Field(default_factory=list, description="""Names of elements this one feeds; the inverse of ``upstream``.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Names of elements this one feeds; the inverse of ``upstream``."""


class _LaserBase(_PhysicalAcceleratorElementBase):
    """
    Laser system element (full laser setup including beam parameters).
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:Laser',
         'from_schema': 'https://w3id.org/laura/schema/elements',
         'in_subset': ['laser_properties'],
         'slot_usage': {'hardware_type': {'equals_string': 'Laser',
                                          'name': 'hardware_type'}}})

    laser: Optional[_LaserElementBase] = Field(default=None, description="""Laser-beam parameters.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Laser',
                       'Plasma',
                       'LaserEnergyMeter',
                       'LaserHalfWavePlate',
                       'LaserMirror',
                       'Wiggler']} })
    """Laser-beam parameters."""
    physical: Optional[_PhysicalElementBase] = Field(default=None, description="""Position, rotation, and length data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PhysicalAcceleratorElement'],
         'in_subset': ['physical_properties']} })
    """Position, rotation, and length data."""
    simulation: Optional[_SimulationElementBase] = Field(default=None, description="""Simulation / tracking attributes.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Simulation / tracking attributes."""
    electrical: Optional[_ElectricalElementBase] = Field(default=None, description="""Power-supply electrical limits.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Power-supply electrical limits."""
    manufacturer: Optional[_ManufacturerElementBase] = Field(default=None, description="""Manufacturer and serial-number data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ManufacturerElement', 'StandardElement']} })
    """Manufacturer and serial-number data."""
    controls: Optional[_ControlsInformationBase] = Field(default=None, description="""Control-system process-variable definitions.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Control-system process-variable definitions."""
    reference: Optional[_ReferenceElementBase] = Field(default=None, description="""Links to design drawings and files.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Links to design drawings and files."""
    name: str = Field(default=..., description="""Unique element name within the machine.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SectionLattice', 'MachineLayout', 'AcceleratorElement']} })
    """Unique element name within the machine."""
    hardware_class: HardwareClassEnum = Field(default=..., description="""Functional category (e.g., ``Magnet``, ``Diagnostic``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Functional category (e.g., ``Magnet``, ``Diagnostic``)."""
    hardware_type: Optional[Literal["Laser"]] = Field(default="Generic", description="""Python class name used for ELEMENT_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'],
         'equals_string': 'Laser',
         'ifabsent': 'string(Generic)'} })
    """Python class name used for ELEMENT_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML."""
    hardware_model: str = Field(default="Generic", description="""Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string(Generic)'} })
    """Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``)."""
    machine_area: Optional[str] = Field(default=None, description="""Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``)."""
    virtual_name: str = Field(default="", description="""Alternative internal name used by the control system when the physical name is inaccessible.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string()'} })
    """Alternative internal name used by the control system when the physical name is inaccessible."""
    alias: list[str] = Field(default_factory=list, description="""Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.""", validation_alias=AliasChoices('alias', 'name_alias'), json_schema_extra = { "linkml_meta": {'aliases': ['name_alias'], 'domain_of': ['AcceleratorElement']} })
    """Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings."""
    subelement: Optional[str] = Field(default=None, description="""If set, this element is a logical sub-component of the named parent element.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """If set, this element is a logical sub-component of the named parent element."""
    inputs: list[IOTypeEnum] = Field(default_factory=list, description="""Signal types this element consumes (e.g. ``[current, voltage]``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Signal types this element consumes (e.g. ``[current, voltage]``)."""
    outputs: list[IOTypeEnum] = Field(default_factory=list, description="""Signal types this element produces (e.g. ``[power, phase]``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Signal types this element produces (e.g. ``[power, phase]``)."""
    upstream: list[str] = Field(default_factory=list, description="""Names of elements feeding this one, whose ``outputs`` supply its ``inputs``.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Names of elements feeding this one, whose ``outputs`` supply its ``inputs``."""
    downstream: list[str] = Field(default_factory=list, description="""Names of elements this one feeds; the inverse of ``upstream``.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Names of elements this one feeds; the inverse of ``upstream``."""


class _ShutterBase(_PhysicalAcceleratorElementBase):
    """
    Beam or laser shutter with interlock logic.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:Shutter',
         'from_schema': 'https://w3id.org/laura/schema/elements',
         'slot_usage': {'hardware_type': {'equals_string': 'Shutter',
                                          'name': 'hardware_type'}}})

    shutter: Optional[_ShutterElementBase] = Field(default=None, description="""Shutter interlock configuration.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Shutter']} })
    """Shutter interlock configuration."""
    physical: Optional[_PhysicalElementBase] = Field(default=None, description="""Position, rotation, and length data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PhysicalAcceleratorElement'],
         'in_subset': ['physical_properties']} })
    """Position, rotation, and length data."""
    simulation: Optional[_SimulationElementBase] = Field(default=None, description="""Simulation / tracking attributes.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Simulation / tracking attributes."""
    electrical: Optional[_ElectricalElementBase] = Field(default=None, description="""Power-supply electrical limits.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Power-supply electrical limits."""
    manufacturer: Optional[_ManufacturerElementBase] = Field(default=None, description="""Manufacturer and serial-number data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ManufacturerElement', 'StandardElement']} })
    """Manufacturer and serial-number data."""
    controls: Optional[_ControlsInformationBase] = Field(default=None, description="""Control-system process-variable definitions.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Control-system process-variable definitions."""
    reference: Optional[_ReferenceElementBase] = Field(default=None, description="""Links to design drawings and files.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Links to design drawings and files."""
    name: str = Field(default=..., description="""Unique element name within the machine.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SectionLattice', 'MachineLayout', 'AcceleratorElement']} })
    """Unique element name within the machine."""
    hardware_class: HardwareClassEnum = Field(default=..., description="""Functional category (e.g., ``Magnet``, ``Diagnostic``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Functional category (e.g., ``Magnet``, ``Diagnostic``)."""
    hardware_type: Optional[Literal["Shutter"]] = Field(default="Generic", description="""Python class name used for ELEMENT_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'],
         'equals_string': 'Shutter',
         'ifabsent': 'string(Generic)'} })
    """Python class name used for ELEMENT_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML."""
    hardware_model: str = Field(default="Generic", description="""Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string(Generic)'} })
    """Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``)."""
    machine_area: Optional[str] = Field(default=None, description="""Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``)."""
    virtual_name: str = Field(default="", description="""Alternative internal name used by the control system when the physical name is inaccessible.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string()'} })
    """Alternative internal name used by the control system when the physical name is inaccessible."""
    alias: list[str] = Field(default_factory=list, description="""Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.""", validation_alias=AliasChoices('alias', 'name_alias'), json_schema_extra = { "linkml_meta": {'aliases': ['name_alias'], 'domain_of': ['AcceleratorElement']} })
    """Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings."""
    subelement: Optional[str] = Field(default=None, description="""If set, this element is a logical sub-component of the named parent element.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """If set, this element is a logical sub-component of the named parent element."""
    inputs: list[IOTypeEnum] = Field(default_factory=list, description="""Signal types this element consumes (e.g. ``[current, voltage]``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Signal types this element consumes (e.g. ``[current, voltage]``)."""
    outputs: list[IOTypeEnum] = Field(default_factory=list, description="""Signal types this element produces (e.g. ``[power, phase]``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Signal types this element produces (e.g. ``[power, phase]``)."""
    upstream: list[str] = Field(default_factory=list, description="""Names of elements feeding this one, whose ``outputs`` supply its ``inputs``.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Names of elements feeding this one, whose ``outputs`` supply its ``inputs``."""
    downstream: list[str] = Field(default_factory=list, description="""Names of elements this one feeds; the inverse of ``upstream``.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Names of elements this one feeds; the inverse of ``upstream``."""


class _ValveBase(_PhysicalAcceleratorElementBase):
    """
    Vacuum gate valve.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:Valve',
         'from_schema': 'https://w3id.org/laura/schema/elements',
         'slot_usage': {'hardware_type': {'equals_string': 'Valve',
                                          'name': 'hardware_type'}}})

    valve: Optional[_ValveElementBase] = Field(default=None, description="""Valve configuration.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Valve']} })
    """Valve configuration."""
    physical: Optional[_PhysicalElementBase] = Field(default=None, description="""Position, rotation, and length data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PhysicalAcceleratorElement'],
         'in_subset': ['physical_properties']} })
    """Position, rotation, and length data."""
    simulation: Optional[_SimulationElementBase] = Field(default=None, description="""Simulation / tracking attributes.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Simulation / tracking attributes."""
    electrical: Optional[_ElectricalElementBase] = Field(default=None, description="""Power-supply electrical limits.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Power-supply electrical limits."""
    manufacturer: Optional[_ManufacturerElementBase] = Field(default=None, description="""Manufacturer and serial-number data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ManufacturerElement', 'StandardElement']} })
    """Manufacturer and serial-number data."""
    controls: Optional[_ControlsInformationBase] = Field(default=None, description="""Control-system process-variable definitions.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Control-system process-variable definitions."""
    reference: Optional[_ReferenceElementBase] = Field(default=None, description="""Links to design drawings and files.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Links to design drawings and files."""
    name: str = Field(default=..., description="""Unique element name within the machine.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SectionLattice', 'MachineLayout', 'AcceleratorElement']} })
    """Unique element name within the machine."""
    hardware_class: HardwareClassEnum = Field(default=..., description="""Functional category (e.g., ``Magnet``, ``Diagnostic``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Functional category (e.g., ``Magnet``, ``Diagnostic``)."""
    hardware_type: Optional[Literal["Valve"]] = Field(default="Generic", description="""Python class name used for ELEMENT_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'],
         'equals_string': 'Valve',
         'ifabsent': 'string(Generic)'} })
    """Python class name used for ELEMENT_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML."""
    hardware_model: str = Field(default="Generic", description="""Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string(Generic)'} })
    """Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``)."""
    machine_area: Optional[str] = Field(default=None, description="""Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``)."""
    virtual_name: str = Field(default="", description="""Alternative internal name used by the control system when the physical name is inaccessible.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string()'} })
    """Alternative internal name used by the control system when the physical name is inaccessible."""
    alias: list[str] = Field(default_factory=list, description="""Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.""", validation_alias=AliasChoices('alias', 'name_alias'), json_schema_extra = { "linkml_meta": {'aliases': ['name_alias'], 'domain_of': ['AcceleratorElement']} })
    """Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings."""
    subelement: Optional[str] = Field(default=None, description="""If set, this element is a logical sub-component of the named parent element.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """If set, this element is a logical sub-component of the named parent element."""
    inputs: list[IOTypeEnum] = Field(default_factory=list, description="""Signal types this element consumes (e.g. ``[current, voltage]``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Signal types this element consumes (e.g. ``[current, voltage]``)."""
    outputs: list[IOTypeEnum] = Field(default_factory=list, description="""Signal types this element produces (e.g. ``[power, phase]``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Signal types this element produces (e.g. ``[power, phase]``)."""
    upstream: list[str] = Field(default_factory=list, description="""Names of elements feeding this one, whose ``outputs`` supply its ``inputs``.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Names of elements feeding this one, whose ``outputs`` supply its ``inputs``."""
    downstream: list[str] = Field(default_factory=list, description="""Names of elements this one feeds; the inverse of ``upstream``.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Names of elements this one feeds; the inverse of ``upstream``."""


class _MarkerBase(_PhysicalAcceleratorElementBase):
    """
    Virtual survey marker -- a zero-length reference point used for alignment.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:Marker',
         'from_schema': 'https://w3id.org/laura/schema/elements',
         'slot_usage': {'hardware_type': {'equals_string': 'Marker',
                                          'name': 'hardware_type'}}})

    physical: Optional[_PhysicalElementBase] = Field(default=None, description="""Position, rotation, and length data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PhysicalAcceleratorElement'],
         'in_subset': ['physical_properties']} })
    """Position, rotation, and length data."""
    simulation: Optional[_SimulationElementBase] = Field(default=None, description="""Simulation / tracking attributes.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Simulation / tracking attributes."""
    electrical: Optional[_ElectricalElementBase] = Field(default=None, description="""Power-supply electrical limits.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Power-supply electrical limits."""
    manufacturer: Optional[_ManufacturerElementBase] = Field(default=None, description="""Manufacturer and serial-number data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ManufacturerElement', 'StandardElement']} })
    """Manufacturer and serial-number data."""
    controls: Optional[_ControlsInformationBase] = Field(default=None, description="""Control-system process-variable definitions.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Control-system process-variable definitions."""
    reference: Optional[_ReferenceElementBase] = Field(default=None, description="""Links to design drawings and files.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Links to design drawings and files."""
    name: str = Field(default=..., description="""Unique element name within the machine.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SectionLattice', 'MachineLayout', 'AcceleratorElement']} })
    """Unique element name within the machine."""
    hardware_class: HardwareClassEnum = Field(default=..., description="""Functional category (e.g., ``Magnet``, ``Diagnostic``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Functional category (e.g., ``Magnet``, ``Diagnostic``)."""
    hardware_type: Optional[Literal["Marker"]] = Field(default="Generic", description="""Python class name used for ELEMENT_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'],
         'equals_string': 'Marker',
         'ifabsent': 'string(Generic)'} })
    """Python class name used for ELEMENT_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML."""
    hardware_model: str = Field(default="Generic", description="""Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string(Generic)'} })
    """Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``)."""
    machine_area: Optional[str] = Field(default=None, description="""Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``)."""
    virtual_name: str = Field(default="", description="""Alternative internal name used by the control system when the physical name is inaccessible.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string()'} })
    """Alternative internal name used by the control system when the physical name is inaccessible."""
    alias: list[str] = Field(default_factory=list, description="""Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.""", validation_alias=AliasChoices('alias', 'name_alias'), json_schema_extra = { "linkml_meta": {'aliases': ['name_alias'], 'domain_of': ['AcceleratorElement']} })
    """Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings."""
    subelement: Optional[str] = Field(default=None, description="""If set, this element is a logical sub-component of the named parent element.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """If set, this element is a logical sub-component of the named parent element."""
    inputs: list[IOTypeEnum] = Field(default_factory=list, description="""Signal types this element consumes (e.g. ``[current, voltage]``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Signal types this element consumes (e.g. ``[current, voltage]``)."""
    outputs: list[IOTypeEnum] = Field(default_factory=list, description="""Signal types this element produces (e.g. ``[power, phase]``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Signal types this element produces (e.g. ``[power, phase]``)."""
    upstream: list[str] = Field(default_factory=list, description="""Names of elements feeding this one, whose ``outputs`` supply its ``inputs``.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Names of elements feeding this one, whose ``outputs`` supply its ``inputs``."""
    downstream: list[str] = Field(default_factory=list, description="""Names of elements this one feeds; the inverse of ``upstream``.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Names of elements this one feeds; the inverse of ``upstream``."""


class _ApertureBase(_PhysicalAcceleratorElementBase):
    """
    Mechanical aperture restriction in the beam pipe.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:Aperture',
         'from_schema': 'https://w3id.org/laura/schema/elements',
         'slot_usage': {'hardware_type': {'equals_string': 'Aperture',
                                          'name': 'hardware_type'}}})

    aperture: Optional[_ApertureElementBase] = Field(default=None, description="""Aperture geometry parameters.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Aperture']} })
    """Aperture geometry parameters."""
    physical: Optional[_PhysicalElementBase] = Field(default=None, description="""Position, rotation, and length data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PhysicalAcceleratorElement'],
         'in_subset': ['physical_properties']} })
    """Position, rotation, and length data."""
    simulation: Optional[_SimulationElementBase] = Field(default=None, description="""Simulation / tracking attributes.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Simulation / tracking attributes."""
    electrical: Optional[_ElectricalElementBase] = Field(default=None, description="""Power-supply electrical limits.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Power-supply electrical limits."""
    manufacturer: Optional[_ManufacturerElementBase] = Field(default=None, description="""Manufacturer and serial-number data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ManufacturerElement', 'StandardElement']} })
    """Manufacturer and serial-number data."""
    controls: Optional[_ControlsInformationBase] = Field(default=None, description="""Control-system process-variable definitions.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Control-system process-variable definitions."""
    reference: Optional[_ReferenceElementBase] = Field(default=None, description="""Links to design drawings and files.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Links to design drawings and files."""
    name: str = Field(default=..., description="""Unique element name within the machine.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SectionLattice', 'MachineLayout', 'AcceleratorElement']} })
    """Unique element name within the machine."""
    hardware_class: HardwareClassEnum = Field(default=..., description="""Functional category (e.g., ``Magnet``, ``Diagnostic``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Functional category (e.g., ``Magnet``, ``Diagnostic``)."""
    hardware_type: Optional[Literal["Aperture"]] = Field(default="Generic", description="""Python class name used for ELEMENT_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'],
         'equals_string': 'Aperture',
         'ifabsent': 'string(Generic)'} })
    """Python class name used for ELEMENT_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML."""
    hardware_model: str = Field(default="Generic", description="""Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string(Generic)'} })
    """Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``)."""
    machine_area: Optional[str] = Field(default=None, description="""Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``)."""
    virtual_name: str = Field(default="", description="""Alternative internal name used by the control system when the physical name is inaccessible.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string()'} })
    """Alternative internal name used by the control system when the physical name is inaccessible."""
    alias: list[str] = Field(default_factory=list, description="""Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.""", validation_alias=AliasChoices('alias', 'name_alias'), json_schema_extra = { "linkml_meta": {'aliases': ['name_alias'], 'domain_of': ['AcceleratorElement']} })
    """Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings."""
    subelement: Optional[str] = Field(default=None, description="""If set, this element is a logical sub-component of the named parent element.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """If set, this element is a logical sub-component of the named parent element."""
    inputs: list[IOTypeEnum] = Field(default_factory=list, description="""Signal types this element consumes (e.g. ``[current, voltage]``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Signal types this element consumes (e.g. ``[current, voltage]``)."""
    outputs: list[IOTypeEnum] = Field(default_factory=list, description="""Signal types this element produces (e.g. ``[power, phase]``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Signal types this element produces (e.g. ``[power, phase]``)."""
    upstream: list[str] = Field(default_factory=list, description="""Names of elements feeding this one, whose ``outputs`` supply its ``inputs``.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Names of elements feeding this one, whose ``outputs`` supply its ``inputs``."""
    downstream: list[str] = Field(default_factory=list, description="""Names of elements this one feeds; the inverse of ``upstream``.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Names of elements this one feeds; the inverse of ``upstream``."""


class _CollimatorBase(_ApertureBase):
    """
    Movable collimator jaw (extends Aperture).
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:Collimator',
         'from_schema': 'https://w3id.org/laura/schema/elements',
         'slot_usage': {'hardware_type': {'equals_string': 'Collimator',
                                          'name': 'hardware_type'}}})

    aperture: Optional[_ApertureElementBase] = Field(default=None, description="""Aperture geometry parameters.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Aperture']} })
    """Aperture geometry parameters."""
    physical: Optional[_PhysicalElementBase] = Field(default=None, description="""Position, rotation, and length data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PhysicalAcceleratorElement'],
         'in_subset': ['physical_properties']} })
    """Position, rotation, and length data."""
    simulation: Optional[_SimulationElementBase] = Field(default=None, description="""Simulation / tracking attributes.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Simulation / tracking attributes."""
    electrical: Optional[_ElectricalElementBase] = Field(default=None, description="""Power-supply electrical limits.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Power-supply electrical limits."""
    manufacturer: Optional[_ManufacturerElementBase] = Field(default=None, description="""Manufacturer and serial-number data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ManufacturerElement', 'StandardElement']} })
    """Manufacturer and serial-number data."""
    controls: Optional[_ControlsInformationBase] = Field(default=None, description="""Control-system process-variable definitions.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Control-system process-variable definitions."""
    reference: Optional[_ReferenceElementBase] = Field(default=None, description="""Links to design drawings and files.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Links to design drawings and files."""
    name: str = Field(default=..., description="""Unique element name within the machine.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SectionLattice', 'MachineLayout', 'AcceleratorElement']} })
    """Unique element name within the machine."""
    hardware_class: HardwareClassEnum = Field(default=..., description="""Functional category (e.g., ``Magnet``, ``Diagnostic``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Functional category (e.g., ``Magnet``, ``Diagnostic``)."""
    hardware_type: Optional[Literal["Collimator"]] = Field(default="Generic", description="""Python class name used for ELEMENT_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'],
         'equals_string': 'Collimator',
         'ifabsent': 'string(Generic)'} })
    """Python class name used for ELEMENT_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML."""
    hardware_model: str = Field(default="Generic", description="""Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string(Generic)'} })
    """Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``)."""
    machine_area: Optional[str] = Field(default=None, description="""Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``)."""
    virtual_name: str = Field(default="", description="""Alternative internal name used by the control system when the physical name is inaccessible.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string()'} })
    """Alternative internal name used by the control system when the physical name is inaccessible."""
    alias: list[str] = Field(default_factory=list, description="""Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.""", validation_alias=AliasChoices('alias', 'name_alias'), json_schema_extra = { "linkml_meta": {'aliases': ['name_alias'], 'domain_of': ['AcceleratorElement']} })
    """Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings."""
    subelement: Optional[str] = Field(default=None, description="""If set, this element is a logical sub-component of the named parent element.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """If set, this element is a logical sub-component of the named parent element."""
    inputs: list[IOTypeEnum] = Field(default_factory=list, description="""Signal types this element consumes (e.g. ``[current, voltage]``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Signal types this element consumes (e.g. ``[current, voltage]``)."""
    outputs: list[IOTypeEnum] = Field(default_factory=list, description="""Signal types this element produces (e.g. ``[power, phase]``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Signal types this element produces (e.g. ``[power, phase]``)."""
    upstream: list[str] = Field(default_factory=list, description="""Names of elements feeding this one, whose ``outputs`` supply its ``inputs``.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Names of elements feeding this one, whose ``outputs`` supply its ``inputs``."""
    downstream: list[str] = Field(default_factory=list, description="""Names of elements this one feeds; the inverse of ``upstream``.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Names of elements this one feeds; the inverse of ``upstream``."""


class _DriftBase(_PhysicalAcceleratorElementBase):
    """
    Field-free drift space between elements.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:Drift',
         'from_schema': 'https://w3id.org/laura/schema/elements',
         'slot_usage': {'hardware_type': {'equals_string': 'Drift',
                                          'name': 'hardware_type'},
                        'simulation': {'name': 'simulation',
                                       'range': 'DriftSimulationElement'}}})

    physical: Optional[_PhysicalElementBase] = Field(default=None, description="""Position, rotation, and length data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PhysicalAcceleratorElement'],
         'in_subset': ['physical_properties']} })
    """Position, rotation, and length data."""
    simulation: Optional[_DriftSimulationElementBase] = Field(default=None, description="""Simulation / tracking attributes.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Simulation / tracking attributes."""
    electrical: Optional[_ElectricalElementBase] = Field(default=None, description="""Power-supply electrical limits.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Power-supply electrical limits."""
    manufacturer: Optional[_ManufacturerElementBase] = Field(default=None, description="""Manufacturer and serial-number data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ManufacturerElement', 'StandardElement']} })
    """Manufacturer and serial-number data."""
    controls: Optional[_ControlsInformationBase] = Field(default=None, description="""Control-system process-variable definitions.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Control-system process-variable definitions."""
    reference: Optional[_ReferenceElementBase] = Field(default=None, description="""Links to design drawings and files.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Links to design drawings and files."""
    name: str = Field(default=..., description="""Unique element name within the machine.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SectionLattice', 'MachineLayout', 'AcceleratorElement']} })
    """Unique element name within the machine."""
    hardware_class: HardwareClassEnum = Field(default=..., description="""Functional category (e.g., ``Magnet``, ``Diagnostic``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Functional category (e.g., ``Magnet``, ``Diagnostic``)."""
    hardware_type: Optional[Literal["Drift"]] = Field(default="Generic", description="""Python class name used for ELEMENT_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'],
         'equals_string': 'Drift',
         'ifabsent': 'string(Generic)'} })
    """Python class name used for ELEMENT_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML."""
    hardware_model: str = Field(default="Generic", description="""Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string(Generic)'} })
    """Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``)."""
    machine_area: Optional[str] = Field(default=None, description="""Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``)."""
    virtual_name: str = Field(default="", description="""Alternative internal name used by the control system when the physical name is inaccessible.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string()'} })
    """Alternative internal name used by the control system when the physical name is inaccessible."""
    alias: list[str] = Field(default_factory=list, description="""Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.""", validation_alias=AliasChoices('alias', 'name_alias'), json_schema_extra = { "linkml_meta": {'aliases': ['name_alias'], 'domain_of': ['AcceleratorElement']} })
    """Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings."""
    subelement: Optional[str] = Field(default=None, description="""If set, this element is a logical sub-component of the named parent element.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """If set, this element is a logical sub-component of the named parent element."""
    inputs: list[IOTypeEnum] = Field(default_factory=list, description="""Signal types this element consumes (e.g. ``[current, voltage]``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Signal types this element consumes (e.g. ``[current, voltage]``)."""
    outputs: list[IOTypeEnum] = Field(default_factory=list, description="""Signal types this element produces (e.g. ``[power, phase]``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Signal types this element produces (e.g. ``[power, phase]``)."""
    upstream: list[str] = Field(default_factory=list, description="""Names of elements feeding this one, whose ``outputs`` supply its ``inputs``.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Names of elements feeding this one, whose ``outputs`` supply its ``inputs``."""
    downstream: list[str] = Field(default_factory=list, description="""Names of elements this one feeds; the inverse of ``upstream``.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Names of elements this one feeds; the inverse of ``upstream``."""


class _MagnetBase(_PhysicalAcceleratorElementBase):
    """
    Base class for all magnetic focusing and bending elements. (Named ``MagnetBaseElement`` in the schema to avoid collision with the ``magnetic`` composition-model class; maps to ``Magnet`` in Python.)
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:Magnet',
         'from_schema': 'https://w3id.org/laura/schema/magnetic',
         'slot_usage': {'simulation': {'name': 'simulation',
                                       'range': 'MagnetSimulationElement'}}})

    magnetic: Optional[_MagneticElementBase] = Field(default=None, description="""Magnetic field parameters.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Magnet'], 'in_subset': ['magnetic_properties']} })
    """Magnetic field parameters."""
    degauss: Optional[_DegaussableElementBase] = Field(default=None, description="""Degaussing-cycle parameters.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Magnet']} })
    """Degaussing-cycle parameters."""
    physical: Optional[_PhysicalElementBase] = Field(default=None, description="""Position, rotation, and length data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PhysicalAcceleratorElement'],
         'in_subset': ['physical_properties']} })
    """Position, rotation, and length data."""
    simulation: Optional[_MagnetSimulationElementBase] = Field(default=None, description="""Simulation / tracking attributes.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Simulation / tracking attributes."""
    electrical: Optional[_ElectricalElementBase] = Field(default=None, description="""Power-supply electrical limits.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Power-supply electrical limits."""
    manufacturer: Optional[_ManufacturerElementBase] = Field(default=None, description="""Manufacturer and serial-number data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ManufacturerElement', 'StandardElement']} })
    """Manufacturer and serial-number data."""
    controls: Optional[_ControlsInformationBase] = Field(default=None, description="""Control-system process-variable definitions.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Control-system process-variable definitions."""
    reference: Optional[_ReferenceElementBase] = Field(default=None, description="""Links to design drawings and files.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Links to design drawings and files."""
    name: str = Field(default=..., description="""Unique element name within the machine.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SectionLattice', 'MachineLayout', 'AcceleratorElement']} })
    """Unique element name within the machine."""
    hardware_class: HardwareClassEnum = Field(default=..., description="""Functional category (e.g., ``Magnet``, ``Diagnostic``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Functional category (e.g., ``Magnet``, ``Diagnostic``)."""
    hardware_type: str = Field(default="Generic", description="""Python class name used for ELEMENT_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string(Generic)'} })
    """Python class name used for ELEMENT_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML."""
    hardware_model: str = Field(default="Generic", description="""Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string(Generic)'} })
    """Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``)."""
    machine_area: Optional[str] = Field(default=None, description="""Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``)."""
    virtual_name: str = Field(default="", description="""Alternative internal name used by the control system when the physical name is inaccessible.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string()'} })
    """Alternative internal name used by the control system when the physical name is inaccessible."""
    alias: list[str] = Field(default_factory=list, description="""Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.""", validation_alias=AliasChoices('alias', 'name_alias'), json_schema_extra = { "linkml_meta": {'aliases': ['name_alias'], 'domain_of': ['AcceleratorElement']} })
    """Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings."""
    subelement: Optional[str] = Field(default=None, description="""If set, this element is a logical sub-component of the named parent element.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """If set, this element is a logical sub-component of the named parent element."""
    inputs: list[IOTypeEnum] = Field(default_factory=list, description="""Signal types this element consumes (e.g. ``[current, voltage]``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Signal types this element consumes (e.g. ``[current, voltage]``)."""
    outputs: list[IOTypeEnum] = Field(default_factory=list, description="""Signal types this element produces (e.g. ``[power, phase]``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Signal types this element produces (e.g. ``[power, phase]``)."""
    upstream: list[str] = Field(default_factory=list, description="""Names of elements feeding this one, whose ``outputs`` supply its ``inputs``.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Names of elements feeding this one, whose ``outputs`` supply its ``inputs``."""
    downstream: list[str] = Field(default_factory=list, description="""Names of elements this one feeds; the inverse of ``upstream``.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Names of elements this one feeds; the inverse of ``upstream``."""


class _RFCavityBase(_PhysicalAcceleratorElementBase):
    """
    Accelerating RF cavity.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:RFCavity',
         'from_schema': 'https://w3id.org/laura/schema/rf',
         'slot_usage': {'hardware_type': {'equals_string': 'RFCavity',
                                          'name': 'hardware_type'},
                        'simulation': {'name': 'simulation',
                                       'range': 'RFCavitySimulationElement'}}})

    cavity: Optional[_RFCavityElementBase] = Field(default=None, description="""RF structure parameters.""", json_schema_extra = { "linkml_meta": {'domain_of': ['RFCavity', 'RFDeflectingCavity', 'CrabCavity', 'Wakefield'],
         'in_subset': ['rf_properties']} })
    """RF structure parameters."""
    physical: Optional[_PhysicalElementBase] = Field(default=None, description="""Position, rotation, and length data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PhysicalAcceleratorElement'],
         'in_subset': ['physical_properties']} })
    """Position, rotation, and length data."""
    simulation: Optional[_RFCavitySimulationElementBase] = Field(default=None, description="""Simulation / tracking attributes.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Simulation / tracking attributes."""
    electrical: Optional[_ElectricalElementBase] = Field(default=None, description="""Power-supply electrical limits.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Power-supply electrical limits."""
    manufacturer: Optional[_ManufacturerElementBase] = Field(default=None, description="""Manufacturer and serial-number data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ManufacturerElement', 'StandardElement']} })
    """Manufacturer and serial-number data."""
    controls: Optional[_ControlsInformationBase] = Field(default=None, description="""Control-system process-variable definitions.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Control-system process-variable definitions."""
    reference: Optional[_ReferenceElementBase] = Field(default=None, description="""Links to design drawings and files.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Links to design drawings and files."""
    name: str = Field(default=..., description="""Unique element name within the machine.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SectionLattice', 'MachineLayout', 'AcceleratorElement']} })
    """Unique element name within the machine."""
    hardware_class: HardwareClassEnum = Field(default=..., description="""Functional category (e.g., ``Magnet``, ``Diagnostic``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Functional category (e.g., ``Magnet``, ``Diagnostic``)."""
    hardware_type: Optional[Literal["RFCavity"]] = Field(default="Generic", description="""Python class name used for ELEMENT_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'],
         'equals_string': 'RFCavity',
         'ifabsent': 'string(Generic)'} })
    """Python class name used for ELEMENT_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML."""
    hardware_model: str = Field(default="Generic", description="""Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string(Generic)'} })
    """Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``)."""
    machine_area: Optional[str] = Field(default=None, description="""Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``)."""
    virtual_name: str = Field(default="", description="""Alternative internal name used by the control system when the physical name is inaccessible.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string()'} })
    """Alternative internal name used by the control system when the physical name is inaccessible."""
    alias: list[str] = Field(default_factory=list, description="""Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.""", validation_alias=AliasChoices('alias', 'name_alias'), json_schema_extra = { "linkml_meta": {'aliases': ['name_alias'], 'domain_of': ['AcceleratorElement']} })
    """Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings."""
    subelement: Optional[str] = Field(default=None, description="""If set, this element is a logical sub-component of the named parent element.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """If set, this element is a logical sub-component of the named parent element."""
    inputs: list[IOTypeEnum] = Field(default_factory=list, description="""Signal types this element consumes (e.g. ``[current, voltage]``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Signal types this element consumes (e.g. ``[current, voltage]``)."""
    outputs: list[IOTypeEnum] = Field(default_factory=list, description="""Signal types this element produces (e.g. ``[power, phase]``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Signal types this element produces (e.g. ``[power, phase]``)."""
    upstream: list[str] = Field(default_factory=list, description="""Names of elements feeding this one, whose ``outputs`` supply its ``inputs``.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Names of elements feeding this one, whose ``outputs`` supply its ``inputs``."""
    downstream: list[str] = Field(default_factory=list, description="""Names of elements this one feeds; the inverse of ``upstream``.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Names of elements this one feeds; the inverse of ``upstream``."""


class _RFDeflectingCavityBase(_RFCavityBase):
    """
    Transverse-deflecting (streak) RF cavity.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:RFDeflectingCavity',
         'from_schema': 'https://w3id.org/laura/schema/rf',
         'slot_usage': {'hardware_type': {'equals_string': 'RFDeflectingCavity',
                                          'name': 'hardware_type'}}})

    cavity: Optional[_RFDeflectingCavityElementBase] = Field(default=None, description="""RF structure parameters.""", json_schema_extra = { "linkml_meta": {'domain_of': ['RFCavity', 'RFDeflectingCavity', 'CrabCavity', 'Wakefield'],
         'in_subset': ['rf_properties']} })
    """RF structure parameters."""
    physical: Optional[_PhysicalElementBase] = Field(default=None, description="""Position, rotation, and length data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PhysicalAcceleratorElement'],
         'in_subset': ['physical_properties']} })
    """Position, rotation, and length data."""
    simulation: Optional[_RFCavitySimulationElementBase] = Field(default=None, description="""Simulation / tracking attributes.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Simulation / tracking attributes."""
    electrical: Optional[_ElectricalElementBase] = Field(default=None, description="""Power-supply electrical limits.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Power-supply electrical limits."""
    manufacturer: Optional[_ManufacturerElementBase] = Field(default=None, description="""Manufacturer and serial-number data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ManufacturerElement', 'StandardElement']} })
    """Manufacturer and serial-number data."""
    controls: Optional[_ControlsInformationBase] = Field(default=None, description="""Control-system process-variable definitions.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Control-system process-variable definitions."""
    reference: Optional[_ReferenceElementBase] = Field(default=None, description="""Links to design drawings and files.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Links to design drawings and files."""
    name: str = Field(default=..., description="""Unique element name within the machine.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SectionLattice', 'MachineLayout', 'AcceleratorElement']} })
    """Unique element name within the machine."""
    hardware_class: HardwareClassEnum = Field(default=..., description="""Functional category (e.g., ``Magnet``, ``Diagnostic``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Functional category (e.g., ``Magnet``, ``Diagnostic``)."""
    hardware_type: Optional[Literal["RFDeflectingCavity"]] = Field(default="Generic", description="""Python class name used for ELEMENT_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'],
         'equals_string': 'RFDeflectingCavity',
         'ifabsent': 'string(Generic)'} })
    """Python class name used for ELEMENT_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML."""
    hardware_model: str = Field(default="Generic", description="""Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string(Generic)'} })
    """Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``)."""
    machine_area: Optional[str] = Field(default=None, description="""Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``)."""
    virtual_name: str = Field(default="", description="""Alternative internal name used by the control system when the physical name is inaccessible.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string()'} })
    """Alternative internal name used by the control system when the physical name is inaccessible."""
    alias: list[str] = Field(default_factory=list, description="""Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.""", validation_alias=AliasChoices('alias', 'name_alias'), json_schema_extra = { "linkml_meta": {'aliases': ['name_alias'], 'domain_of': ['AcceleratorElement']} })
    """Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings."""
    subelement: Optional[str] = Field(default=None, description="""If set, this element is a logical sub-component of the named parent element.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """If set, this element is a logical sub-component of the named parent element."""
    inputs: list[IOTypeEnum] = Field(default_factory=list, description="""Signal types this element consumes (e.g. ``[current, voltage]``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Signal types this element consumes (e.g. ``[current, voltage]``)."""
    outputs: list[IOTypeEnum] = Field(default_factory=list, description="""Signal types this element produces (e.g. ``[power, phase]``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Signal types this element produces (e.g. ``[power, phase]``)."""
    upstream: list[str] = Field(default_factory=list, description="""Names of elements feeding this one, whose ``outputs`` supply its ``inputs``.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Names of elements feeding this one, whose ``outputs`` supply its ``inputs``."""
    downstream: list[str] = Field(default_factory=list, description="""Names of elements this one feeds; the inverse of ``upstream``.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Names of elements this one feeds; the inverse of ``upstream``."""


class _CrabCavityBase(_RFCavityBase):
    """
    Transverse-deflecting crab cavity for crossing-angle compensation.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:CrabCavity',
         'from_schema': 'https://w3id.org/laura/schema/rf',
         'slot_usage': {'hardware_type': {'equals_string': 'CrabCavity',
                                          'name': 'hardware_type'}}})

    cavity: Optional[_RFDeflectingCavityElementBase] = Field(default=None, description="""Crab-cavity RF structure parameters.""", json_schema_extra = { "linkml_meta": {'domain_of': ['RFCavity', 'RFDeflectingCavity', 'CrabCavity', 'Wakefield'],
         'in_subset': ['rf_properties']} })
    """Crab-cavity RF structure parameters."""
    physical: Optional[_PhysicalElementBase] = Field(default=None, description="""Position, rotation, and length data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PhysicalAcceleratorElement'],
         'in_subset': ['physical_properties']} })
    """Position, rotation, and length data."""
    simulation: Optional[_RFCavitySimulationElementBase] = Field(default=None, description="""Simulation / tracking attributes.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Simulation / tracking attributes."""
    electrical: Optional[_ElectricalElementBase] = Field(default=None, description="""Power-supply electrical limits.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Power-supply electrical limits."""
    manufacturer: Optional[_ManufacturerElementBase] = Field(default=None, description="""Manufacturer and serial-number data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ManufacturerElement', 'StandardElement']} })
    """Manufacturer and serial-number data."""
    controls: Optional[_ControlsInformationBase] = Field(default=None, description="""Control-system process-variable definitions.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Control-system process-variable definitions."""
    reference: Optional[_ReferenceElementBase] = Field(default=None, description="""Links to design drawings and files.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Links to design drawings and files."""
    name: str = Field(default=..., description="""Unique element name within the machine.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SectionLattice', 'MachineLayout', 'AcceleratorElement']} })
    """Unique element name within the machine."""
    hardware_class: HardwareClassEnum = Field(default=..., description="""Functional category (e.g., ``Magnet``, ``Diagnostic``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Functional category (e.g., ``Magnet``, ``Diagnostic``)."""
    hardware_type: Optional[Literal["CrabCavity"]] = Field(default="Generic", description="""Python class name used for ELEMENT_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'],
         'equals_string': 'CrabCavity',
         'ifabsent': 'string(Generic)'} })
    """Python class name used for ELEMENT_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML."""
    hardware_model: str = Field(default="Generic", description="""Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string(Generic)'} })
    """Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``)."""
    machine_area: Optional[str] = Field(default=None, description="""Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``)."""
    virtual_name: str = Field(default="", description="""Alternative internal name used by the control system when the physical name is inaccessible.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string()'} })
    """Alternative internal name used by the control system when the physical name is inaccessible."""
    alias: list[str] = Field(default_factory=list, description="""Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.""", validation_alias=AliasChoices('alias', 'name_alias'), json_schema_extra = { "linkml_meta": {'aliases': ['name_alias'], 'domain_of': ['AcceleratorElement']} })
    """Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings."""
    subelement: Optional[str] = Field(default=None, description="""If set, this element is a logical sub-component of the named parent element.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """If set, this element is a logical sub-component of the named parent element."""
    inputs: list[IOTypeEnum] = Field(default_factory=list, description="""Signal types this element consumes (e.g. ``[current, voltage]``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Signal types this element consumes (e.g. ``[current, voltage]``)."""
    outputs: list[IOTypeEnum] = Field(default_factory=list, description="""Signal types this element produces (e.g. ``[power, phase]``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Signal types this element produces (e.g. ``[power, phase]``)."""
    upstream: list[str] = Field(default_factory=list, description="""Names of elements feeding this one, whose ``outputs`` supply its ``inputs``.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Names of elements feeding this one, whose ``outputs`` supply its ``inputs``."""
    downstream: list[str] = Field(default_factory=list, description="""Names of elements this one feeds; the inverse of ``upstream``.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Names of elements this one feeds; the inverse of ``upstream``."""


class _WakefieldBase(_PhysicalAcceleratorElementBase):
    """
    Passive wakefield structure (dielectric, corrugated, etc.).
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:Wakefield',
         'from_schema': 'https://w3id.org/laura/schema/rf',
         'slot_usage': {'hardware_type': {'equals_string': 'Wakefield',
                                          'name': 'hardware_type'},
                        'simulation': {'name': 'simulation',
                                       'range': 'WakefieldSimulationElement'}}})

    cavity: Optional[_WakefieldElementBase] = Field(default=None, description="""Wakefield structure parameters.""", json_schema_extra = { "linkml_meta": {'domain_of': ['RFCavity', 'RFDeflectingCavity', 'CrabCavity', 'Wakefield']} })
    """Wakefield structure parameters."""
    physical: Optional[_PhysicalElementBase] = Field(default=None, description="""Position, rotation, and length data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PhysicalAcceleratorElement'],
         'in_subset': ['physical_properties']} })
    """Position, rotation, and length data."""
    simulation: Optional[_WakefieldSimulationElementBase] = Field(default=None, description="""Simulation / tracking attributes.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Simulation / tracking attributes."""
    electrical: Optional[_ElectricalElementBase] = Field(default=None, description="""Power-supply electrical limits.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Power-supply electrical limits."""
    manufacturer: Optional[_ManufacturerElementBase] = Field(default=None, description="""Manufacturer and serial-number data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ManufacturerElement', 'StandardElement']} })
    """Manufacturer and serial-number data."""
    controls: Optional[_ControlsInformationBase] = Field(default=None, description="""Control-system process-variable definitions.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Control-system process-variable definitions."""
    reference: Optional[_ReferenceElementBase] = Field(default=None, description="""Links to design drawings and files.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Links to design drawings and files."""
    name: str = Field(default=..., description="""Unique element name within the machine.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SectionLattice', 'MachineLayout', 'AcceleratorElement']} })
    """Unique element name within the machine."""
    hardware_class: HardwareClassEnum = Field(default=..., description="""Functional category (e.g., ``Magnet``, ``Diagnostic``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Functional category (e.g., ``Magnet``, ``Diagnostic``)."""
    hardware_type: Optional[Literal["Wakefield"]] = Field(default="Generic", description="""Python class name used for ELEMENT_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'],
         'equals_string': 'Wakefield',
         'ifabsent': 'string(Generic)'} })
    """Python class name used for ELEMENT_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML."""
    hardware_model: str = Field(default="Generic", description="""Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string(Generic)'} })
    """Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``)."""
    machine_area: Optional[str] = Field(default=None, description="""Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``)."""
    virtual_name: str = Field(default="", description="""Alternative internal name used by the control system when the physical name is inaccessible.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string()'} })
    """Alternative internal name used by the control system when the physical name is inaccessible."""
    alias: list[str] = Field(default_factory=list, description="""Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.""", validation_alias=AliasChoices('alias', 'name_alias'), json_schema_extra = { "linkml_meta": {'aliases': ['name_alias'], 'domain_of': ['AcceleratorElement']} })
    """Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings."""
    subelement: Optional[str] = Field(default=None, description="""If set, this element is a logical sub-component of the named parent element.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """If set, this element is a logical sub-component of the named parent element."""
    inputs: list[IOTypeEnum] = Field(default_factory=list, description="""Signal types this element consumes (e.g. ``[current, voltage]``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Signal types this element consumes (e.g. ``[current, voltage]``)."""
    outputs: list[IOTypeEnum] = Field(default_factory=list, description="""Signal types this element produces (e.g. ``[power, phase]``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Signal types this element produces (e.g. ``[power, phase]``)."""
    upstream: list[str] = Field(default_factory=list, description="""Names of elements feeding this one, whose ``outputs`` supply its ``inputs``.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Names of elements feeding this one, whose ``outputs`` supply its ``inputs``."""
    downstream: list[str] = Field(default_factory=list, description="""Names of elements this one feeds; the inverse of ``upstream``.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Names of elements this one feeds; the inverse of ``upstream``."""


class _DiagnosticBase(_PhysicalAcceleratorElementBase):
    """
    Base class for all beam-diagnostic instruments.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:Diagnostic',
         'from_schema': 'https://w3id.org/laura/schema/diagnostics',
         'slot_usage': {'simulation': {'name': 'simulation',
                                       'range': 'DiagnosticSimulationElement'}}})

    diagnostic: Optional[_DiagnosticElementBase] = Field(default=None, description="""Instrument-specific diagnostic parameters.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Diagnostic',
                       'BeamPositionMonitor',
                       'BeamArrivalMonitor',
                       'BunchLengthMonitor',
                       'Camera',
                       'Screen',
                       'ChargeDiagnostic',
                       'PhotonMonitor'],
         'in_subset': ['diagnostic_properties']} })
    """Instrument-specific diagnostic parameters."""
    physical: Optional[_PhysicalElementBase] = Field(default=None, description="""Position, rotation, and length data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PhysicalAcceleratorElement'],
         'in_subset': ['physical_properties']} })
    """Position, rotation, and length data."""
    simulation: Optional[_DiagnosticSimulationElementBase] = Field(default=None, description="""Simulation / tracking attributes.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Simulation / tracking attributes."""
    electrical: Optional[_ElectricalElementBase] = Field(default=None, description="""Power-supply electrical limits.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Power-supply electrical limits."""
    manufacturer: Optional[_ManufacturerElementBase] = Field(default=None, description="""Manufacturer and serial-number data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ManufacturerElement', 'StandardElement']} })
    """Manufacturer and serial-number data."""
    controls: Optional[_ControlsInformationBase] = Field(default=None, description="""Control-system process-variable definitions.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Control-system process-variable definitions."""
    reference: Optional[_ReferenceElementBase] = Field(default=None, description="""Links to design drawings and files.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Links to design drawings and files."""
    name: str = Field(default=..., description="""Unique element name within the machine.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SectionLattice', 'MachineLayout', 'AcceleratorElement']} })
    """Unique element name within the machine."""
    hardware_class: HardwareClassEnum = Field(default=..., description="""Functional category (e.g., ``Magnet``, ``Diagnostic``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Functional category (e.g., ``Magnet``, ``Diagnostic``)."""
    hardware_type: str = Field(default="Generic", description="""Python class name used for ELEMENT_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string(Generic)'} })
    """Python class name used for ELEMENT_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML."""
    hardware_model: str = Field(default="Generic", description="""Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string(Generic)'} })
    """Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``)."""
    machine_area: Optional[str] = Field(default=None, description="""Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``)."""
    virtual_name: str = Field(default="", description="""Alternative internal name used by the control system when the physical name is inaccessible.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string()'} })
    """Alternative internal name used by the control system when the physical name is inaccessible."""
    alias: list[str] = Field(default_factory=list, description="""Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.""", validation_alias=AliasChoices('alias', 'name_alias'), json_schema_extra = { "linkml_meta": {'aliases': ['name_alias'], 'domain_of': ['AcceleratorElement']} })
    """Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings."""
    subelement: Optional[str] = Field(default=None, description="""If set, this element is a logical sub-component of the named parent element.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """If set, this element is a logical sub-component of the named parent element."""
    inputs: list[IOTypeEnum] = Field(default_factory=list, description="""Signal types this element consumes (e.g. ``[current, voltage]``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Signal types this element consumes (e.g. ``[current, voltage]``)."""
    outputs: list[IOTypeEnum] = Field(default_factory=list, description="""Signal types this element produces (e.g. ``[power, phase]``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Signal types this element produces (e.g. ``[power, phase]``)."""
    upstream: list[str] = Field(default_factory=list, description="""Names of elements feeding this one, whose ``outputs`` supply its ``inputs``.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Names of elements feeding this one, whose ``outputs`` supply its ``inputs``."""
    downstream: list[str] = Field(default_factory=list, description="""Names of elements this one feeds; the inverse of ``upstream``.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Names of elements this one feeds; the inverse of ``upstream``."""


class _BeamPositionMonitorBase(_DiagnosticBase):
    """
    Beam-position monitor (BPM).
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:BeamPositionMonitor',
         'from_schema': 'https://w3id.org/laura/schema/diagnostics',
         'slot_usage': {'hardware_type': {'equals_string': 'Beam_Position_Monitor',
                                          'name': 'hardware_type'}}})

    diagnostic: Optional[_BPMDiagnosticElementBase] = Field(default=None, description="""Instrument-specific diagnostic parameters.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Diagnostic',
                       'BeamPositionMonitor',
                       'BeamArrivalMonitor',
                       'BunchLengthMonitor',
                       'Camera',
                       'Screen',
                       'ChargeDiagnostic',
                       'PhotonMonitor'],
         'in_subset': ['diagnostic_properties']} })
    """Instrument-specific diagnostic parameters."""
    physical: Optional[_PhysicalElementBase] = Field(default=None, description="""Position, rotation, and length data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PhysicalAcceleratorElement'],
         'in_subset': ['physical_properties']} })
    """Position, rotation, and length data."""
    simulation: Optional[_DiagnosticSimulationElementBase] = Field(default=None, description="""Simulation / tracking attributes.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Simulation / tracking attributes."""
    electrical: Optional[_ElectricalElementBase] = Field(default=None, description="""Power-supply electrical limits.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Power-supply electrical limits."""
    manufacturer: Optional[_ManufacturerElementBase] = Field(default=None, description="""Manufacturer and serial-number data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ManufacturerElement', 'StandardElement']} })
    """Manufacturer and serial-number data."""
    controls: Optional[_ControlsInformationBase] = Field(default=None, description="""Control-system process-variable definitions.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Control-system process-variable definitions."""
    reference: Optional[_ReferenceElementBase] = Field(default=None, description="""Links to design drawings and files.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Links to design drawings and files."""
    name: str = Field(default=..., description="""Unique element name within the machine.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SectionLattice', 'MachineLayout', 'AcceleratorElement']} })
    """Unique element name within the machine."""
    hardware_class: HardwareClassEnum = Field(default=..., description="""Functional category (e.g., ``Magnet``, ``Diagnostic``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Functional category (e.g., ``Magnet``, ``Diagnostic``)."""
    hardware_type: Optional[Literal["Beam_Position_Monitor"]] = Field(default="Generic", description="""Python class name used for ELEMENT_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'],
         'equals_string': 'Beam_Position_Monitor',
         'ifabsent': 'string(Generic)'} })
    """Python class name used for ELEMENT_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML."""
    hardware_model: str = Field(default="Generic", description="""Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string(Generic)'} })
    """Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``)."""
    machine_area: Optional[str] = Field(default=None, description="""Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``)."""
    virtual_name: str = Field(default="", description="""Alternative internal name used by the control system when the physical name is inaccessible.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string()'} })
    """Alternative internal name used by the control system when the physical name is inaccessible."""
    alias: list[str] = Field(default_factory=list, description="""Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.""", validation_alias=AliasChoices('alias', 'name_alias'), json_schema_extra = { "linkml_meta": {'aliases': ['name_alias'], 'domain_of': ['AcceleratorElement']} })
    """Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings."""
    subelement: Optional[str] = Field(default=None, description="""If set, this element is a logical sub-component of the named parent element.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """If set, this element is a logical sub-component of the named parent element."""
    inputs: list[IOTypeEnum] = Field(default_factory=list, description="""Signal types this element consumes (e.g. ``[current, voltage]``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Signal types this element consumes (e.g. ``[current, voltage]``)."""
    outputs: list[IOTypeEnum] = Field(default_factory=list, description="""Signal types this element produces (e.g. ``[power, phase]``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Signal types this element produces (e.g. ``[power, phase]``)."""
    upstream: list[str] = Field(default_factory=list, description="""Names of elements feeding this one, whose ``outputs`` supply its ``inputs``.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Names of elements feeding this one, whose ``outputs`` supply its ``inputs``."""
    downstream: list[str] = Field(default_factory=list, description="""Names of elements this one feeds; the inverse of ``upstream``.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Names of elements this one feeds; the inverse of ``upstream``."""


class _BeamArrivalMonitorBase(_DiagnosticBase):
    """
    Beam-arrival-time monitor (BAM).
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:BeamArrivalMonitor',
         'from_schema': 'https://w3id.org/laura/schema/diagnostics',
         'slot_usage': {'hardware_type': {'equals_string': 'Beam_Arrival_Monitor',
                                          'name': 'hardware_type'}}})

    diagnostic: Optional[_BAMDiagnosticElementBase] = Field(default=None, description="""Instrument-specific diagnostic parameters.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Diagnostic',
                       'BeamPositionMonitor',
                       'BeamArrivalMonitor',
                       'BunchLengthMonitor',
                       'Camera',
                       'Screen',
                       'ChargeDiagnostic',
                       'PhotonMonitor'],
         'in_subset': ['diagnostic_properties']} })
    """Instrument-specific diagnostic parameters."""
    physical: Optional[_PhysicalElementBase] = Field(default=None, description="""Position, rotation, and length data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PhysicalAcceleratorElement'],
         'in_subset': ['physical_properties']} })
    """Position, rotation, and length data."""
    simulation: Optional[_DiagnosticSimulationElementBase] = Field(default=None, description="""Simulation / tracking attributes.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Simulation / tracking attributes."""
    electrical: Optional[_ElectricalElementBase] = Field(default=None, description="""Power-supply electrical limits.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Power-supply electrical limits."""
    manufacturer: Optional[_ManufacturerElementBase] = Field(default=None, description="""Manufacturer and serial-number data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ManufacturerElement', 'StandardElement']} })
    """Manufacturer and serial-number data."""
    controls: Optional[_ControlsInformationBase] = Field(default=None, description="""Control-system process-variable definitions.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Control-system process-variable definitions."""
    reference: Optional[_ReferenceElementBase] = Field(default=None, description="""Links to design drawings and files.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Links to design drawings and files."""
    name: str = Field(default=..., description="""Unique element name within the machine.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SectionLattice', 'MachineLayout', 'AcceleratorElement']} })
    """Unique element name within the machine."""
    hardware_class: HardwareClassEnum = Field(default=..., description="""Functional category (e.g., ``Magnet``, ``Diagnostic``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Functional category (e.g., ``Magnet``, ``Diagnostic``)."""
    hardware_type: Optional[Literal["Beam_Arrival_Monitor"]] = Field(default="Generic", description="""Python class name used for ELEMENT_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'],
         'equals_string': 'Beam_Arrival_Monitor',
         'ifabsent': 'string(Generic)'} })
    """Python class name used for ELEMENT_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML."""
    hardware_model: str = Field(default="Generic", description="""Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string(Generic)'} })
    """Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``)."""
    machine_area: Optional[str] = Field(default=None, description="""Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``)."""
    virtual_name: str = Field(default="", description="""Alternative internal name used by the control system when the physical name is inaccessible.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string()'} })
    """Alternative internal name used by the control system when the physical name is inaccessible."""
    alias: list[str] = Field(default_factory=list, description="""Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.""", validation_alias=AliasChoices('alias', 'name_alias'), json_schema_extra = { "linkml_meta": {'aliases': ['name_alias'], 'domain_of': ['AcceleratorElement']} })
    """Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings."""
    subelement: Optional[str] = Field(default=None, description="""If set, this element is a logical sub-component of the named parent element.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """If set, this element is a logical sub-component of the named parent element."""
    inputs: list[IOTypeEnum] = Field(default_factory=list, description="""Signal types this element consumes (e.g. ``[current, voltage]``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Signal types this element consumes (e.g. ``[current, voltage]``)."""
    outputs: list[IOTypeEnum] = Field(default_factory=list, description="""Signal types this element produces (e.g. ``[power, phase]``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Signal types this element produces (e.g. ``[power, phase]``)."""
    upstream: list[str] = Field(default_factory=list, description="""Names of elements feeding this one, whose ``outputs`` supply its ``inputs``.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Names of elements feeding this one, whose ``outputs`` supply its ``inputs``."""
    downstream: list[str] = Field(default_factory=list, description="""Names of elements this one feeds; the inverse of ``upstream``.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Names of elements this one feeds; the inverse of ``upstream``."""


class _BunchLengthMonitorBase(_DiagnosticBase):
    """
    Bunch-length monitor (BLM / CDR detector).
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:BunchLengthMonitor',
         'from_schema': 'https://w3id.org/laura/schema/diagnostics',
         'slot_usage': {'hardware_type': {'equals_string': 'Bunch_Length_Monitor',
                                          'name': 'hardware_type'}}})

    diagnostic: Optional[_BLMDiagnosticElementBase] = Field(default=None, description="""Instrument-specific diagnostic parameters.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Diagnostic',
                       'BeamPositionMonitor',
                       'BeamArrivalMonitor',
                       'BunchLengthMonitor',
                       'Camera',
                       'Screen',
                       'ChargeDiagnostic',
                       'PhotonMonitor'],
         'in_subset': ['diagnostic_properties']} })
    """Instrument-specific diagnostic parameters."""
    physical: Optional[_PhysicalElementBase] = Field(default=None, description="""Position, rotation, and length data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PhysicalAcceleratorElement'],
         'in_subset': ['physical_properties']} })
    """Position, rotation, and length data."""
    simulation: Optional[_DiagnosticSimulationElementBase] = Field(default=None, description="""Simulation / tracking attributes.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Simulation / tracking attributes."""
    electrical: Optional[_ElectricalElementBase] = Field(default=None, description="""Power-supply electrical limits.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Power-supply electrical limits."""
    manufacturer: Optional[_ManufacturerElementBase] = Field(default=None, description="""Manufacturer and serial-number data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ManufacturerElement', 'StandardElement']} })
    """Manufacturer and serial-number data."""
    controls: Optional[_ControlsInformationBase] = Field(default=None, description="""Control-system process-variable definitions.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Control-system process-variable definitions."""
    reference: Optional[_ReferenceElementBase] = Field(default=None, description="""Links to design drawings and files.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Links to design drawings and files."""
    name: str = Field(default=..., description="""Unique element name within the machine.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SectionLattice', 'MachineLayout', 'AcceleratorElement']} })
    """Unique element name within the machine."""
    hardware_class: HardwareClassEnum = Field(default=..., description="""Functional category (e.g., ``Magnet``, ``Diagnostic``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Functional category (e.g., ``Magnet``, ``Diagnostic``)."""
    hardware_type: Optional[Literal["Bunch_Length_Monitor"]] = Field(default="Generic", description="""Python class name used for ELEMENT_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'],
         'equals_string': 'Bunch_Length_Monitor',
         'ifabsent': 'string(Generic)'} })
    """Python class name used for ELEMENT_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML."""
    hardware_model: str = Field(default="Generic", description="""Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string(Generic)'} })
    """Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``)."""
    machine_area: Optional[str] = Field(default=None, description="""Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``)."""
    virtual_name: str = Field(default="", description="""Alternative internal name used by the control system when the physical name is inaccessible.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string()'} })
    """Alternative internal name used by the control system when the physical name is inaccessible."""
    alias: list[str] = Field(default_factory=list, description="""Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.""", validation_alias=AliasChoices('alias', 'name_alias'), json_schema_extra = { "linkml_meta": {'aliases': ['name_alias'], 'domain_of': ['AcceleratorElement']} })
    """Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings."""
    subelement: Optional[str] = Field(default=None, description="""If set, this element is a logical sub-component of the named parent element.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """If set, this element is a logical sub-component of the named parent element."""
    inputs: list[IOTypeEnum] = Field(default_factory=list, description="""Signal types this element consumes (e.g. ``[current, voltage]``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Signal types this element consumes (e.g. ``[current, voltage]``)."""
    outputs: list[IOTypeEnum] = Field(default_factory=list, description="""Signal types this element produces (e.g. ``[power, phase]``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Signal types this element produces (e.g. ``[power, phase]``)."""
    upstream: list[str] = Field(default_factory=list, description="""Names of elements feeding this one, whose ``outputs`` supply its ``inputs``.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Names of elements feeding this one, whose ``outputs`` supply its ``inputs``."""
    downstream: list[str] = Field(default_factory=list, description="""Names of elements this one feeds; the inverse of ``upstream``.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Names of elements this one feeds; the inverse of ``upstream``."""


class _CameraBase(_DiagnosticBase):
    """
    Camera-based beam-profile monitor.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:Camera',
         'from_schema': 'https://w3id.org/laura/schema/diagnostics',
         'slot_usage': {'hardware_type': {'equals_string': 'Camera',
                                          'name': 'hardware_type'}}})

    diagnostic: Optional[_CameraDiagnosticElementBase] = Field(default=None, description="""Instrument-specific diagnostic parameters.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Diagnostic',
                       'BeamPositionMonitor',
                       'BeamArrivalMonitor',
                       'BunchLengthMonitor',
                       'Camera',
                       'Screen',
                       'ChargeDiagnostic',
                       'PhotonMonitor'],
         'in_subset': ['diagnostic_properties']} })
    """Instrument-specific diagnostic parameters."""
    physical: Optional[_PhysicalElementBase] = Field(default=None, description="""Position, rotation, and length data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PhysicalAcceleratorElement'],
         'in_subset': ['physical_properties']} })
    """Position, rotation, and length data."""
    simulation: Optional[_DiagnosticSimulationElementBase] = Field(default=None, description="""Simulation / tracking attributes.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Simulation / tracking attributes."""
    electrical: Optional[_ElectricalElementBase] = Field(default=None, description="""Power-supply electrical limits.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Power-supply electrical limits."""
    manufacturer: Optional[_ManufacturerElementBase] = Field(default=None, description="""Manufacturer and serial-number data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ManufacturerElement', 'StandardElement']} })
    """Manufacturer and serial-number data."""
    controls: Optional[_ControlsInformationBase] = Field(default=None, description="""Control-system process-variable definitions.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Control-system process-variable definitions."""
    reference: Optional[_ReferenceElementBase] = Field(default=None, description="""Links to design drawings and files.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Links to design drawings and files."""
    name: str = Field(default=..., description="""Unique element name within the machine.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SectionLattice', 'MachineLayout', 'AcceleratorElement']} })
    """Unique element name within the machine."""
    hardware_class: HardwareClassEnum = Field(default=..., description="""Functional category (e.g., ``Magnet``, ``Diagnostic``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Functional category (e.g., ``Magnet``, ``Diagnostic``)."""
    hardware_type: Optional[Literal["Camera"]] = Field(default="Generic", description="""Python class name used for ELEMENT_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'],
         'equals_string': 'Camera',
         'ifabsent': 'string(Generic)'} })
    """Python class name used for ELEMENT_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML."""
    hardware_model: str = Field(default="Generic", description="""Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string(Generic)'} })
    """Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``)."""
    machine_area: Optional[str] = Field(default=None, description="""Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``)."""
    virtual_name: str = Field(default="", description="""Alternative internal name used by the control system when the physical name is inaccessible.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string()'} })
    """Alternative internal name used by the control system when the physical name is inaccessible."""
    alias: list[str] = Field(default_factory=list, description="""Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.""", validation_alias=AliasChoices('alias', 'name_alias'), json_schema_extra = { "linkml_meta": {'aliases': ['name_alias'], 'domain_of': ['AcceleratorElement']} })
    """Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings."""
    subelement: Optional[str] = Field(default=None, description="""If set, this element is a logical sub-component of the named parent element.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """If set, this element is a logical sub-component of the named parent element."""
    inputs: list[IOTypeEnum] = Field(default_factory=list, description="""Signal types this element consumes (e.g. ``[current, voltage]``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Signal types this element consumes (e.g. ``[current, voltage]``)."""
    outputs: list[IOTypeEnum] = Field(default_factory=list, description="""Signal types this element produces (e.g. ``[power, phase]``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Signal types this element produces (e.g. ``[power, phase]``)."""
    upstream: list[str] = Field(default_factory=list, description="""Names of elements feeding this one, whose ``outputs`` supply its ``inputs``.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Names of elements feeding this one, whose ``outputs`` supply its ``inputs``."""
    downstream: list[str] = Field(default_factory=list, description="""Names of elements this one feeds; the inverse of ``upstream``.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Names of elements this one feeds; the inverse of ``upstream``."""


class _ScreenBase(_DiagnosticBase):
    """
    Scintillator or OTR screen with an associated camera.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:Screen',
         'from_schema': 'https://w3id.org/laura/schema/diagnostics',
         'slot_usage': {'hardware_type': {'equals_string': 'Screen',
                                          'name': 'hardware_type'}}})

    diagnostic: Optional[_ScreenDiagnosticElementBase] = Field(default=None, description="""Instrument-specific diagnostic parameters.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Diagnostic',
                       'BeamPositionMonitor',
                       'BeamArrivalMonitor',
                       'BunchLengthMonitor',
                       'Camera',
                       'Screen',
                       'ChargeDiagnostic',
                       'PhotonMonitor'],
         'in_subset': ['diagnostic_properties']} })
    """Instrument-specific diagnostic parameters."""
    physical: Optional[_PhysicalElementBase] = Field(default=None, description="""Position, rotation, and length data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PhysicalAcceleratorElement'],
         'in_subset': ['physical_properties']} })
    """Position, rotation, and length data."""
    simulation: Optional[_DiagnosticSimulationElementBase] = Field(default=None, description="""Simulation / tracking attributes.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Simulation / tracking attributes."""
    electrical: Optional[_ElectricalElementBase] = Field(default=None, description="""Power-supply electrical limits.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Power-supply electrical limits."""
    manufacturer: Optional[_ManufacturerElementBase] = Field(default=None, description="""Manufacturer and serial-number data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ManufacturerElement', 'StandardElement']} })
    """Manufacturer and serial-number data."""
    controls: Optional[_ControlsInformationBase] = Field(default=None, description="""Control-system process-variable definitions.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Control-system process-variable definitions."""
    reference: Optional[_ReferenceElementBase] = Field(default=None, description="""Links to design drawings and files.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Links to design drawings and files."""
    name: str = Field(default=..., description="""Unique element name within the machine.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SectionLattice', 'MachineLayout', 'AcceleratorElement']} })
    """Unique element name within the machine."""
    hardware_class: HardwareClassEnum = Field(default=..., description="""Functional category (e.g., ``Magnet``, ``Diagnostic``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Functional category (e.g., ``Magnet``, ``Diagnostic``)."""
    hardware_type: Optional[Literal["Screen"]] = Field(default="Generic", description="""Python class name used for ELEMENT_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'],
         'equals_string': 'Screen',
         'ifabsent': 'string(Generic)'} })
    """Python class name used for ELEMENT_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML."""
    hardware_model: str = Field(default="Generic", description="""Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string(Generic)'} })
    """Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``)."""
    machine_area: Optional[str] = Field(default=None, description="""Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``)."""
    virtual_name: str = Field(default="", description="""Alternative internal name used by the control system when the physical name is inaccessible.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string()'} })
    """Alternative internal name used by the control system when the physical name is inaccessible."""
    alias: list[str] = Field(default_factory=list, description="""Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.""", validation_alias=AliasChoices('alias', 'name_alias'), json_schema_extra = { "linkml_meta": {'aliases': ['name_alias'], 'domain_of': ['AcceleratorElement']} })
    """Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings."""
    subelement: Optional[str] = Field(default=None, description="""If set, this element is a logical sub-component of the named parent element.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """If set, this element is a logical sub-component of the named parent element."""
    inputs: list[IOTypeEnum] = Field(default_factory=list, description="""Signal types this element consumes (e.g. ``[current, voltage]``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Signal types this element consumes (e.g. ``[current, voltage]``)."""
    outputs: list[IOTypeEnum] = Field(default_factory=list, description="""Signal types this element produces (e.g. ``[power, phase]``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Signal types this element produces (e.g. ``[power, phase]``)."""
    upstream: list[str] = Field(default_factory=list, description="""Names of elements feeding this one, whose ``outputs`` supply its ``inputs``.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Names of elements feeding this one, whose ``outputs`` supply its ``inputs``."""
    downstream: list[str] = Field(default_factory=list, description="""Names of elements this one feeds; the inverse of ``upstream``.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Names of elements this one feeds; the inverse of ``upstream``."""


class _ChargeDiagnosticBase(_DiagnosticBase):
    """
    Base class for charge-measurement diagnostics.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:ChargeDiagnostic',
         'from_schema': 'https://w3id.org/laura/schema/diagnostics',
         'slot_usage': {'hardware_type': {'equals_string': 'ChargeDiagnostic',
                                          'name': 'hardware_type'}}})

    diagnostic: Optional[_ChargeDiagnosticElementBase] = Field(default=None, description="""Instrument-specific diagnostic parameters.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Diagnostic',
                       'BeamPositionMonitor',
                       'BeamArrivalMonitor',
                       'BunchLengthMonitor',
                       'Camera',
                       'Screen',
                       'ChargeDiagnostic',
                       'PhotonMonitor'],
         'in_subset': ['diagnostic_properties']} })
    """Instrument-specific diagnostic parameters."""
    physical: Optional[_PhysicalElementBase] = Field(default=None, description="""Position, rotation, and length data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PhysicalAcceleratorElement'],
         'in_subset': ['physical_properties']} })
    """Position, rotation, and length data."""
    simulation: Optional[_DiagnosticSimulationElementBase] = Field(default=None, description="""Simulation / tracking attributes.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Simulation / tracking attributes."""
    electrical: Optional[_ElectricalElementBase] = Field(default=None, description="""Power-supply electrical limits.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Power-supply electrical limits."""
    manufacturer: Optional[_ManufacturerElementBase] = Field(default=None, description="""Manufacturer and serial-number data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ManufacturerElement', 'StandardElement']} })
    """Manufacturer and serial-number data."""
    controls: Optional[_ControlsInformationBase] = Field(default=None, description="""Control-system process-variable definitions.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Control-system process-variable definitions."""
    reference: Optional[_ReferenceElementBase] = Field(default=None, description="""Links to design drawings and files.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Links to design drawings and files."""
    name: str = Field(default=..., description="""Unique element name within the machine.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SectionLattice', 'MachineLayout', 'AcceleratorElement']} })
    """Unique element name within the machine."""
    hardware_class: HardwareClassEnum = Field(default=..., description="""Functional category (e.g., ``Magnet``, ``Diagnostic``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Functional category (e.g., ``Magnet``, ``Diagnostic``)."""
    hardware_type: Optional[Literal["ChargeDiagnostic"]] = Field(default="Generic", description="""Python class name used for ELEMENT_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'],
         'equals_string': 'ChargeDiagnostic',
         'ifabsent': 'string(Generic)'} })
    """Python class name used for ELEMENT_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML."""
    hardware_model: str = Field(default="Generic", description="""Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string(Generic)'} })
    """Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``)."""
    machine_area: Optional[str] = Field(default=None, description="""Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``)."""
    virtual_name: str = Field(default="", description="""Alternative internal name used by the control system when the physical name is inaccessible.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string()'} })
    """Alternative internal name used by the control system when the physical name is inaccessible."""
    alias: list[str] = Field(default_factory=list, description="""Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.""", validation_alias=AliasChoices('alias', 'name_alias'), json_schema_extra = { "linkml_meta": {'aliases': ['name_alias'], 'domain_of': ['AcceleratorElement']} })
    """Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings."""
    subelement: Optional[str] = Field(default=None, description="""If set, this element is a logical sub-component of the named parent element.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """If set, this element is a logical sub-component of the named parent element."""
    inputs: list[IOTypeEnum] = Field(default_factory=list, description="""Signal types this element consumes (e.g. ``[current, voltage]``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Signal types this element consumes (e.g. ``[current, voltage]``)."""
    outputs: list[IOTypeEnum] = Field(default_factory=list, description="""Signal types this element produces (e.g. ``[power, phase]``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Signal types this element produces (e.g. ``[power, phase]``)."""
    upstream: list[str] = Field(default_factory=list, description="""Names of elements feeding this one, whose ``outputs`` supply its ``inputs``.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Names of elements feeding this one, whose ``outputs`` supply its ``inputs``."""
    downstream: list[str] = Field(default_factory=list, description="""Names of elements this one feeds; the inverse of ``upstream``.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Names of elements this one feeds; the inverse of ``upstream``."""


class _WallCurrentMonitorBase(_ChargeDiagnosticBase):
    """
    Wall-current monitor (WCM) for non-destructive charge measurement.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:WallCurrentMonitor',
         'from_schema': 'https://w3id.org/laura/schema/diagnostics',
         'slot_usage': {'hardware_type': {'equals_string': 'Wall_Current_Monitor',
                                          'name': 'hardware_type'}}})

    diagnostic: Optional[_ChargeDiagnosticElementBase] = Field(default=None, description="""Instrument-specific diagnostic parameters.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Diagnostic',
                       'BeamPositionMonitor',
                       'BeamArrivalMonitor',
                       'BunchLengthMonitor',
                       'Camera',
                       'Screen',
                       'ChargeDiagnostic',
                       'PhotonMonitor'],
         'in_subset': ['diagnostic_properties']} })
    """Instrument-specific diagnostic parameters."""
    physical: Optional[_PhysicalElementBase] = Field(default=None, description="""Position, rotation, and length data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PhysicalAcceleratorElement'],
         'in_subset': ['physical_properties']} })
    """Position, rotation, and length data."""
    simulation: Optional[_DiagnosticSimulationElementBase] = Field(default=None, description="""Simulation / tracking attributes.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Simulation / tracking attributes."""
    electrical: Optional[_ElectricalElementBase] = Field(default=None, description="""Power-supply electrical limits.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Power-supply electrical limits."""
    manufacturer: Optional[_ManufacturerElementBase] = Field(default=None, description="""Manufacturer and serial-number data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ManufacturerElement', 'StandardElement']} })
    """Manufacturer and serial-number data."""
    controls: Optional[_ControlsInformationBase] = Field(default=None, description="""Control-system process-variable definitions.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Control-system process-variable definitions."""
    reference: Optional[_ReferenceElementBase] = Field(default=None, description="""Links to design drawings and files.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Links to design drawings and files."""
    name: str = Field(default=..., description="""Unique element name within the machine.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SectionLattice', 'MachineLayout', 'AcceleratorElement']} })
    """Unique element name within the machine."""
    hardware_class: HardwareClassEnum = Field(default=..., description="""Functional category (e.g., ``Magnet``, ``Diagnostic``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Functional category (e.g., ``Magnet``, ``Diagnostic``)."""
    hardware_type: Optional[Literal["Wall_Current_Monitor"]] = Field(default="Generic", description="""Python class name used for ELEMENT_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'],
         'equals_string': 'Wall_Current_Monitor',
         'ifabsent': 'string(Generic)'} })
    """Python class name used for ELEMENT_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML."""
    hardware_model: str = Field(default="Generic", description="""Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string(Generic)'} })
    """Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``)."""
    machine_area: Optional[str] = Field(default=None, description="""Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``)."""
    virtual_name: str = Field(default="", description="""Alternative internal name used by the control system when the physical name is inaccessible.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string()'} })
    """Alternative internal name used by the control system when the physical name is inaccessible."""
    alias: list[str] = Field(default_factory=list, description="""Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.""", validation_alias=AliasChoices('alias', 'name_alias'), json_schema_extra = { "linkml_meta": {'aliases': ['name_alias'], 'domain_of': ['AcceleratorElement']} })
    """Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings."""
    subelement: Optional[str] = Field(default=None, description="""If set, this element is a logical sub-component of the named parent element.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """If set, this element is a logical sub-component of the named parent element."""
    inputs: list[IOTypeEnum] = Field(default_factory=list, description="""Signal types this element consumes (e.g. ``[current, voltage]``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Signal types this element consumes (e.g. ``[current, voltage]``)."""
    outputs: list[IOTypeEnum] = Field(default_factory=list, description="""Signal types this element produces (e.g. ``[power, phase]``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Signal types this element produces (e.g. ``[power, phase]``)."""
    upstream: list[str] = Field(default_factory=list, description="""Names of elements feeding this one, whose ``outputs`` supply its ``inputs``.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Names of elements feeding this one, whose ``outputs`` supply its ``inputs``."""
    downstream: list[str] = Field(default_factory=list, description="""Names of elements this one feeds; the inverse of ``upstream``.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Names of elements this one feeds; the inverse of ``upstream``."""


class _FaradayCupMonitorBase(_ChargeDiagnosticBase):
    """
    Faraday cup for destructive charge measurement.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:FaradayCupMonitor',
         'from_schema': 'https://w3id.org/laura/schema/diagnostics',
         'slot_usage': {'hardware_type': {'equals_string': 'Faraday_Cup_Monitor',
                                          'name': 'hardware_type'}}})

    diagnostic: Optional[_ChargeDiagnosticElementBase] = Field(default=None, description="""Instrument-specific diagnostic parameters.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Diagnostic',
                       'BeamPositionMonitor',
                       'BeamArrivalMonitor',
                       'BunchLengthMonitor',
                       'Camera',
                       'Screen',
                       'ChargeDiagnostic',
                       'PhotonMonitor'],
         'in_subset': ['diagnostic_properties']} })
    """Instrument-specific diagnostic parameters."""
    physical: Optional[_PhysicalElementBase] = Field(default=None, description="""Position, rotation, and length data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PhysicalAcceleratorElement'],
         'in_subset': ['physical_properties']} })
    """Position, rotation, and length data."""
    simulation: Optional[_DiagnosticSimulationElementBase] = Field(default=None, description="""Simulation / tracking attributes.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Simulation / tracking attributes."""
    electrical: Optional[_ElectricalElementBase] = Field(default=None, description="""Power-supply electrical limits.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Power-supply electrical limits."""
    manufacturer: Optional[_ManufacturerElementBase] = Field(default=None, description="""Manufacturer and serial-number data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ManufacturerElement', 'StandardElement']} })
    """Manufacturer and serial-number data."""
    controls: Optional[_ControlsInformationBase] = Field(default=None, description="""Control-system process-variable definitions.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Control-system process-variable definitions."""
    reference: Optional[_ReferenceElementBase] = Field(default=None, description="""Links to design drawings and files.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Links to design drawings and files."""
    name: str = Field(default=..., description="""Unique element name within the machine.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SectionLattice', 'MachineLayout', 'AcceleratorElement']} })
    """Unique element name within the machine."""
    hardware_class: HardwareClassEnum = Field(default=..., description="""Functional category (e.g., ``Magnet``, ``Diagnostic``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Functional category (e.g., ``Magnet``, ``Diagnostic``)."""
    hardware_type: Optional[Literal["Faraday_Cup_Monitor"]] = Field(default="Generic", description="""Python class name used for ELEMENT_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'],
         'equals_string': 'Faraday_Cup_Monitor',
         'ifabsent': 'string(Generic)'} })
    """Python class name used for ELEMENT_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML."""
    hardware_model: str = Field(default="Generic", description="""Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string(Generic)'} })
    """Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``)."""
    machine_area: Optional[str] = Field(default=None, description="""Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``)."""
    virtual_name: str = Field(default="", description="""Alternative internal name used by the control system when the physical name is inaccessible.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string()'} })
    """Alternative internal name used by the control system when the physical name is inaccessible."""
    alias: list[str] = Field(default_factory=list, description="""Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.""", validation_alias=AliasChoices('alias', 'name_alias'), json_schema_extra = { "linkml_meta": {'aliases': ['name_alias'], 'domain_of': ['AcceleratorElement']} })
    """Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings."""
    subelement: Optional[str] = Field(default=None, description="""If set, this element is a logical sub-component of the named parent element.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """If set, this element is a logical sub-component of the named parent element."""
    inputs: list[IOTypeEnum] = Field(default_factory=list, description="""Signal types this element consumes (e.g. ``[current, voltage]``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Signal types this element consumes (e.g. ``[current, voltage]``)."""
    outputs: list[IOTypeEnum] = Field(default_factory=list, description="""Signal types this element produces (e.g. ``[power, phase]``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Signal types this element produces (e.g. ``[power, phase]``)."""
    upstream: list[str] = Field(default_factory=list, description="""Names of elements feeding this one, whose ``outputs`` supply its ``inputs``.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Names of elements feeding this one, whose ``outputs`` supply its ``inputs``."""
    downstream: list[str] = Field(default_factory=list, description="""Names of elements this one feeds; the inverse of ``upstream``.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Names of elements this one feeds; the inverse of ``upstream``."""


class _IntegratedCurrentTransformerBase(_ChargeDiagnosticBase):
    """
    Integrated current transformer (ICT) for non-destructive single-shot charge measurement.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:IntegratedCurrentTransformer',
         'from_schema': 'https://w3id.org/laura/schema/diagnostics',
         'slot_usage': {'hardware_type': {'equals_string': 'Integrated_Current_Transformer',
                                          'name': 'hardware_type'}}})

    diagnostic: Optional[_ChargeDiagnosticElementBase] = Field(default=None, description="""Instrument-specific diagnostic parameters.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Diagnostic',
                       'BeamPositionMonitor',
                       'BeamArrivalMonitor',
                       'BunchLengthMonitor',
                       'Camera',
                       'Screen',
                       'ChargeDiagnostic',
                       'PhotonMonitor'],
         'in_subset': ['diagnostic_properties']} })
    """Instrument-specific diagnostic parameters."""
    physical: Optional[_PhysicalElementBase] = Field(default=None, description="""Position, rotation, and length data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PhysicalAcceleratorElement'],
         'in_subset': ['physical_properties']} })
    """Position, rotation, and length data."""
    simulation: Optional[_DiagnosticSimulationElementBase] = Field(default=None, description="""Simulation / tracking attributes.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Simulation / tracking attributes."""
    electrical: Optional[_ElectricalElementBase] = Field(default=None, description="""Power-supply electrical limits.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Power-supply electrical limits."""
    manufacturer: Optional[_ManufacturerElementBase] = Field(default=None, description="""Manufacturer and serial-number data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ManufacturerElement', 'StandardElement']} })
    """Manufacturer and serial-number data."""
    controls: Optional[_ControlsInformationBase] = Field(default=None, description="""Control-system process-variable definitions.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Control-system process-variable definitions."""
    reference: Optional[_ReferenceElementBase] = Field(default=None, description="""Links to design drawings and files.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Links to design drawings and files."""
    name: str = Field(default=..., description="""Unique element name within the machine.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SectionLattice', 'MachineLayout', 'AcceleratorElement']} })
    """Unique element name within the machine."""
    hardware_class: HardwareClassEnum = Field(default=..., description="""Functional category (e.g., ``Magnet``, ``Diagnostic``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Functional category (e.g., ``Magnet``, ``Diagnostic``)."""
    hardware_type: Optional[Literal["Integrated_Current_Transformer"]] = Field(default="Generic", description="""Python class name used for ELEMENT_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'],
         'equals_string': 'Integrated_Current_Transformer',
         'ifabsent': 'string(Generic)'} })
    """Python class name used for ELEMENT_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML."""
    hardware_model: str = Field(default="Generic", description="""Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string(Generic)'} })
    """Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``)."""
    machine_area: Optional[str] = Field(default=None, description="""Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``)."""
    virtual_name: str = Field(default="", description="""Alternative internal name used by the control system when the physical name is inaccessible.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string()'} })
    """Alternative internal name used by the control system when the physical name is inaccessible."""
    alias: list[str] = Field(default_factory=list, description="""Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.""", validation_alias=AliasChoices('alias', 'name_alias'), json_schema_extra = { "linkml_meta": {'aliases': ['name_alias'], 'domain_of': ['AcceleratorElement']} })
    """Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings."""
    subelement: Optional[str] = Field(default=None, description="""If set, this element is a logical sub-component of the named parent element.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """If set, this element is a logical sub-component of the named parent element."""
    inputs: list[IOTypeEnum] = Field(default_factory=list, description="""Signal types this element consumes (e.g. ``[current, voltage]``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Signal types this element consumes (e.g. ``[current, voltage]``)."""
    outputs: list[IOTypeEnum] = Field(default_factory=list, description="""Signal types this element produces (e.g. ``[power, phase]``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Signal types this element produces (e.g. ``[power, phase]``)."""
    upstream: list[str] = Field(default_factory=list, description="""Names of elements feeding this one, whose ``outputs`` supply its ``inputs``.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Names of elements feeding this one, whose ``outputs`` supply its ``inputs``."""
    downstream: list[str] = Field(default_factory=list, description="""Names of elements this one feeds; the inverse of ``upstream``.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Names of elements this one feeds; the inverse of ``upstream``."""


class _PhotonMonitorBase(_DiagnosticBase):
    """
    Photon intensity monitor.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:PhotonMonitor',
         'from_schema': 'https://w3id.org/laura/schema/diagnostics',
         'slot_usage': {'hardware_model': {'ifabsent': 'string(Photon_Monitor)',
                                           'name': 'hardware_model'},
                        'hardware_type': {'equals_string': 'Photon_Monitor',
                                          'name': 'hardware_type'}}})

    diagnostic: Optional[_PhotonIntensityMonitorDiagnosticBase] = Field(default=None, description="""Instrument-specific diagnostic parameters.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Diagnostic',
                       'BeamPositionMonitor',
                       'BeamArrivalMonitor',
                       'BunchLengthMonitor',
                       'Camera',
                       'Screen',
                       'ChargeDiagnostic',
                       'PhotonMonitor'],
         'in_subset': ['diagnostic_properties']} })
    """Instrument-specific diagnostic parameters."""
    physical: Optional[_PhysicalElementBase] = Field(default=None, description="""Position, rotation, and length data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PhysicalAcceleratorElement'],
         'in_subset': ['physical_properties']} })
    """Position, rotation, and length data."""
    simulation: Optional[_DiagnosticSimulationElementBase] = Field(default=None, description="""Simulation / tracking attributes.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Simulation / tracking attributes."""
    electrical: Optional[_ElectricalElementBase] = Field(default=None, description="""Power-supply electrical limits.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Power-supply electrical limits."""
    manufacturer: Optional[_ManufacturerElementBase] = Field(default=None, description="""Manufacturer and serial-number data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ManufacturerElement', 'StandardElement']} })
    """Manufacturer and serial-number data."""
    controls: Optional[_ControlsInformationBase] = Field(default=None, description="""Control-system process-variable definitions.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Control-system process-variable definitions."""
    reference: Optional[_ReferenceElementBase] = Field(default=None, description="""Links to design drawings and files.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Links to design drawings and files."""
    name: str = Field(default=..., description="""Unique element name within the machine.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SectionLattice', 'MachineLayout', 'AcceleratorElement']} })
    """Unique element name within the machine."""
    hardware_class: HardwareClassEnum = Field(default=..., description="""Functional category (e.g., ``Magnet``, ``Diagnostic``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Functional category (e.g., ``Magnet``, ``Diagnostic``)."""
    hardware_type: Optional[Literal["Photon_Monitor"]] = Field(default="Generic", description="""Python class name used for ELEMENT_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'],
         'equals_string': 'Photon_Monitor',
         'ifabsent': 'string(Generic)'} })
    """Python class name used for ELEMENT_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML."""
    hardware_model: str = Field(default="Photon_Monitor", description="""Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string(Photon_Monitor)'} })
    """Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``)."""
    machine_area: Optional[str] = Field(default=None, description="""Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``)."""
    virtual_name: str = Field(default="", description="""Alternative internal name used by the control system when the physical name is inaccessible.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string()'} })
    """Alternative internal name used by the control system when the physical name is inaccessible."""
    alias: list[str] = Field(default_factory=list, description="""Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.""", validation_alias=AliasChoices('alias', 'name_alias'), json_schema_extra = { "linkml_meta": {'aliases': ['name_alias'], 'domain_of': ['AcceleratorElement']} })
    """Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings."""
    subelement: Optional[str] = Field(default=None, description="""If set, this element is a logical sub-component of the named parent element.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """If set, this element is a logical sub-component of the named parent element."""
    inputs: list[IOTypeEnum] = Field(default_factory=list, description="""Signal types this element consumes (e.g. ``[current, voltage]``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Signal types this element consumes (e.g. ``[current, voltage]``)."""
    outputs: list[IOTypeEnum] = Field(default_factory=list, description="""Signal types this element produces (e.g. ``[power, phase]``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Signal types this element produces (e.g. ``[power, phase]``)."""
    upstream: list[str] = Field(default_factory=list, description="""Names of elements feeding this one, whose ``outputs`` supply its ``inputs``.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Names of elements feeding this one, whose ``outputs`` supply its ``inputs``."""
    downstream: list[str] = Field(default_factory=list, description="""Names of elements this one feeds; the inverse of ``upstream``.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Names of elements this one feeds; the inverse of ``upstream``."""


class _PlasmaBase(_PhysicalAcceleratorElementBase):
    """
    Laser-driven plasma-accelerator stage.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:Plasma',
         'from_schema': 'https://w3id.org/laura/schema/laser_plasma',
         'slot_usage': {'hardware_type': {'equals_string': 'Plasma',
                                          'name': 'hardware_type'},
                        'simulation': {'name': 'simulation',
                                       'range': 'PlasmaSimulationElement'}}})

    plasma: Optional[_PlasmaElementBase] = Field(default=None, description="""Plasma channel parameters.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Plasma']} })
    """Plasma channel parameters."""
    laser: Optional[_LaserElementBase] = Field(default=None, description="""Laser driving the plasma stage.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Laser',
                       'Plasma',
                       'LaserEnergyMeter',
                       'LaserHalfWavePlate',
                       'LaserMirror',
                       'Wiggler']} })
    """Laser driving the plasma stage."""
    physical: Optional[_PhysicalElementBase] = Field(default=None, description="""Position, rotation, and length data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PhysicalAcceleratorElement'],
         'in_subset': ['physical_properties']} })
    """Position, rotation, and length data."""
    simulation: Optional[_PlasmaSimulationElementBase] = Field(default=None, description="""Simulation / tracking attributes.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Simulation / tracking attributes."""
    electrical: Optional[_ElectricalElementBase] = Field(default=None, description="""Power-supply electrical limits.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Power-supply electrical limits."""
    manufacturer: Optional[_ManufacturerElementBase] = Field(default=None, description="""Manufacturer and serial-number data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ManufacturerElement', 'StandardElement']} })
    """Manufacturer and serial-number data."""
    controls: Optional[_ControlsInformationBase] = Field(default=None, description="""Control-system process-variable definitions.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Control-system process-variable definitions."""
    reference: Optional[_ReferenceElementBase] = Field(default=None, description="""Links to design drawings and files.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Links to design drawings and files."""
    name: str = Field(default=..., description="""Unique element name within the machine.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SectionLattice', 'MachineLayout', 'AcceleratorElement']} })
    """Unique element name within the machine."""
    hardware_class: HardwareClassEnum = Field(default=..., description="""Functional category (e.g., ``Magnet``, ``Diagnostic``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Functional category (e.g., ``Magnet``, ``Diagnostic``)."""
    hardware_type: Optional[Literal["Plasma"]] = Field(default="Generic", description="""Python class name used for ELEMENT_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'],
         'equals_string': 'Plasma',
         'ifabsent': 'string(Generic)'} })
    """Python class name used for ELEMENT_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML."""
    hardware_model: str = Field(default="Generic", description="""Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string(Generic)'} })
    """Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``)."""
    machine_area: Optional[str] = Field(default=None, description="""Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``)."""
    virtual_name: str = Field(default="", description="""Alternative internal name used by the control system when the physical name is inaccessible.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string()'} })
    """Alternative internal name used by the control system when the physical name is inaccessible."""
    alias: list[str] = Field(default_factory=list, description="""Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.""", validation_alias=AliasChoices('alias', 'name_alias'), json_schema_extra = { "linkml_meta": {'aliases': ['name_alias'], 'domain_of': ['AcceleratorElement']} })
    """Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings."""
    subelement: Optional[str] = Field(default=None, description="""If set, this element is a logical sub-component of the named parent element.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """If set, this element is a logical sub-component of the named parent element."""
    inputs: list[IOTypeEnum] = Field(default_factory=list, description="""Signal types this element consumes (e.g. ``[current, voltage]``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Signal types this element consumes (e.g. ``[current, voltage]``)."""
    outputs: list[IOTypeEnum] = Field(default_factory=list, description="""Signal types this element produces (e.g. ``[power, phase]``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Signal types this element produces (e.g. ``[power, phase]``)."""
    upstream: list[str] = Field(default_factory=list, description="""Names of elements feeding this one, whose ``outputs`` supply its ``inputs``.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Names of elements feeding this one, whose ``outputs`` supply its ``inputs``."""
    downstream: list[str] = Field(default_factory=list, description="""Names of elements this one feeds; the inverse of ``upstream``.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Names of elements this one feeds; the inverse of ``upstream``."""


class _DipoleBase(_MagnetBase):
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://w3id.org/laura/schema/magnetic',
         'slot_usage': {'hardware_type': {'equals_string': 'Dipole',
                                          'ifabsent': 'Dipole',
                                          'name': 'hardware_type'},
                        'magnetic': {'name': 'magnetic', 'range': 'Dipole_Magnet'}}})

    magnetic: Optional[_DipoleMagnetBase] = Field(default=None, description="""Magnetic field parameters.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Magnet'], 'in_subset': ['magnetic_properties']} })
    """Magnetic field parameters."""
    degauss: Optional[_DegaussableElementBase] = Field(default=None, description="""Degaussing-cycle parameters.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Magnet']} })
    """Degaussing-cycle parameters."""
    physical: Optional[_PhysicalElementBase] = Field(default=None, description="""Position, rotation, and length data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PhysicalAcceleratorElement'],
         'in_subset': ['physical_properties']} })
    """Position, rotation, and length data."""
    simulation: Optional[_MagnetSimulationElementBase] = Field(default=None, description="""Simulation / tracking attributes.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Simulation / tracking attributes."""
    electrical: Optional[_ElectricalElementBase] = Field(default=None, description="""Power-supply electrical limits.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Power-supply electrical limits."""
    manufacturer: Optional[_ManufacturerElementBase] = Field(default=None, description="""Manufacturer and serial-number data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ManufacturerElement', 'StandardElement']} })
    """Manufacturer and serial-number data."""
    controls: Optional[_ControlsInformationBase] = Field(default=None, description="""Control-system process-variable definitions.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Control-system process-variable definitions."""
    reference: Optional[_ReferenceElementBase] = Field(default=None, description="""Links to design drawings and files.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Links to design drawings and files."""
    name: str = Field(default=..., description="""Unique element name within the machine.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SectionLattice', 'MachineLayout', 'AcceleratorElement']} })
    """Unique element name within the machine."""
    hardware_class: HardwareClassEnum = Field(default=..., description="""Functional category (e.g., ``Magnet``, ``Diagnostic``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Functional category (e.g., ``Magnet``, ``Diagnostic``)."""
    hardware_type: Optional[Literal["Dipole"]] = Field(default="Dipole", description="""Python class name used for ELEMENT_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'],
         'equals_string': 'Dipole',
         'ifabsent': 'Dipole'} })
    """Python class name used for ELEMENT_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML."""
    hardware_model: str = Field(default="Generic", description="""Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string(Generic)'} })
    """Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``)."""
    machine_area: Optional[str] = Field(default=None, description="""Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``)."""
    virtual_name: str = Field(default="", description="""Alternative internal name used by the control system when the physical name is inaccessible.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string()'} })
    """Alternative internal name used by the control system when the physical name is inaccessible."""
    alias: list[str] = Field(default_factory=list, description="""Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.""", validation_alias=AliasChoices('alias', 'name_alias'), json_schema_extra = { "linkml_meta": {'aliases': ['name_alias'], 'domain_of': ['AcceleratorElement']} })
    """Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings."""
    subelement: Optional[str] = Field(default=None, description="""If set, this element is a logical sub-component of the named parent element.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """If set, this element is a logical sub-component of the named parent element."""
    inputs: list[IOTypeEnum] = Field(default_factory=list, description="""Signal types this element consumes (e.g. ``[current, voltage]``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Signal types this element consumes (e.g. ``[current, voltage]``)."""
    outputs: list[IOTypeEnum] = Field(default_factory=list, description="""Signal types this element produces (e.g. ``[power, phase]``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Signal types this element produces (e.g. ``[power, phase]``)."""
    upstream: list[str] = Field(default_factory=list, description="""Names of elements feeding this one, whose ``outputs`` supply its ``inputs``.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Names of elements feeding this one, whose ``outputs`` supply its ``inputs``."""
    downstream: list[str] = Field(default_factory=list, description="""Names of elements this one feeds; the inverse of ``upstream``.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Names of elements this one feeds; the inverse of ``upstream``."""


class _QuadrupoleBase(_MagnetBase):
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://w3id.org/laura/schema/magnetic',
         'slot_usage': {'hardware_type': {'equals_string': 'Quadrupole',
                                          'ifabsent': 'Quadrupole',
                                          'name': 'hardware_type'},
                        'magnetic': {'name': 'magnetic', 'range': 'Quadrupole_Magnet'}}})

    magnetic: Optional[_QuadrupoleMagnetBase] = Field(default=None, description="""Magnetic field parameters.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Magnet'], 'in_subset': ['magnetic_properties']} })
    """Magnetic field parameters."""
    degauss: Optional[_DegaussableElementBase] = Field(default=None, description="""Degaussing-cycle parameters.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Magnet']} })
    """Degaussing-cycle parameters."""
    physical: Optional[_PhysicalElementBase] = Field(default=None, description="""Position, rotation, and length data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PhysicalAcceleratorElement'],
         'in_subset': ['physical_properties']} })
    """Position, rotation, and length data."""
    simulation: Optional[_MagnetSimulationElementBase] = Field(default=None, description="""Simulation / tracking attributes.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Simulation / tracking attributes."""
    electrical: Optional[_ElectricalElementBase] = Field(default=None, description="""Power-supply electrical limits.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Power-supply electrical limits."""
    manufacturer: Optional[_ManufacturerElementBase] = Field(default=None, description="""Manufacturer and serial-number data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ManufacturerElement', 'StandardElement']} })
    """Manufacturer and serial-number data."""
    controls: Optional[_ControlsInformationBase] = Field(default=None, description="""Control-system process-variable definitions.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Control-system process-variable definitions."""
    reference: Optional[_ReferenceElementBase] = Field(default=None, description="""Links to design drawings and files.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Links to design drawings and files."""
    name: str = Field(default=..., description="""Unique element name within the machine.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SectionLattice', 'MachineLayout', 'AcceleratorElement']} })
    """Unique element name within the machine."""
    hardware_class: HardwareClassEnum = Field(default=..., description="""Functional category (e.g., ``Magnet``, ``Diagnostic``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Functional category (e.g., ``Magnet``, ``Diagnostic``)."""
    hardware_type: Optional[Literal["Quadrupole"]] = Field(default="Quadrupole", description="""Python class name used for ELEMENT_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'],
         'equals_string': 'Quadrupole',
         'ifabsent': 'Quadrupole'} })
    """Python class name used for ELEMENT_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML."""
    hardware_model: str = Field(default="Generic", description="""Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string(Generic)'} })
    """Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``)."""
    machine_area: Optional[str] = Field(default=None, description="""Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``)."""
    virtual_name: str = Field(default="", description="""Alternative internal name used by the control system when the physical name is inaccessible.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string()'} })
    """Alternative internal name used by the control system when the physical name is inaccessible."""
    alias: list[str] = Field(default_factory=list, description="""Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.""", validation_alias=AliasChoices('alias', 'name_alias'), json_schema_extra = { "linkml_meta": {'aliases': ['name_alias'], 'domain_of': ['AcceleratorElement']} })
    """Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings."""
    subelement: Optional[str] = Field(default=None, description="""If set, this element is a logical sub-component of the named parent element.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """If set, this element is a logical sub-component of the named parent element."""
    inputs: list[IOTypeEnum] = Field(default_factory=list, description="""Signal types this element consumes (e.g. ``[current, voltage]``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Signal types this element consumes (e.g. ``[current, voltage]``)."""
    outputs: list[IOTypeEnum] = Field(default_factory=list, description="""Signal types this element produces (e.g. ``[power, phase]``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Signal types this element produces (e.g. ``[power, phase]``)."""
    upstream: list[str] = Field(default_factory=list, description="""Names of elements feeding this one, whose ``outputs`` supply its ``inputs``.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Names of elements feeding this one, whose ``outputs`` supply its ``inputs``."""
    downstream: list[str] = Field(default_factory=list, description="""Names of elements this one feeds; the inverse of ``upstream``.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Names of elements this one feeds; the inverse of ``upstream``."""


class _SextupoleBase(_MagnetBase):
    """
    Sextupole chromaticity-correction magnet.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:Sextupole',
         'from_schema': 'https://w3id.org/laura/schema/magnetic',
         'slot_usage': {'hardware_type': {'equals_string': 'Sextupole',
                                          'ifabsent': 'Sextupole',
                                          'name': 'hardware_type'},
                        'magnetic': {'name': 'magnetic', 'range': 'Sextupole_Magnet'}}})

    magnetic: Optional[_SextupoleMagnetBase] = Field(default=None, description="""Magnetic field parameters.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Magnet'], 'in_subset': ['magnetic_properties']} })
    """Magnetic field parameters."""
    degauss: Optional[_DegaussableElementBase] = Field(default=None, description="""Degaussing-cycle parameters.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Magnet']} })
    """Degaussing-cycle parameters."""
    physical: Optional[_PhysicalElementBase] = Field(default=None, description="""Position, rotation, and length data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PhysicalAcceleratorElement'],
         'in_subset': ['physical_properties']} })
    """Position, rotation, and length data."""
    simulation: Optional[_MagnetSimulationElementBase] = Field(default=None, description="""Simulation / tracking attributes.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Simulation / tracking attributes."""
    electrical: Optional[_ElectricalElementBase] = Field(default=None, description="""Power-supply electrical limits.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Power-supply electrical limits."""
    manufacturer: Optional[_ManufacturerElementBase] = Field(default=None, description="""Manufacturer and serial-number data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ManufacturerElement', 'StandardElement']} })
    """Manufacturer and serial-number data."""
    controls: Optional[_ControlsInformationBase] = Field(default=None, description="""Control-system process-variable definitions.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Control-system process-variable definitions."""
    reference: Optional[_ReferenceElementBase] = Field(default=None, description="""Links to design drawings and files.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Links to design drawings and files."""
    name: str = Field(default=..., description="""Unique element name within the machine.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SectionLattice', 'MachineLayout', 'AcceleratorElement']} })
    """Unique element name within the machine."""
    hardware_class: HardwareClassEnum = Field(default=..., description="""Functional category (e.g., ``Magnet``, ``Diagnostic``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Functional category (e.g., ``Magnet``, ``Diagnostic``)."""
    hardware_type: Optional[Literal["Sextupole"]] = Field(default="Sextupole", description="""Python class name used for ELEMENT_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'],
         'equals_string': 'Sextupole',
         'ifabsent': 'Sextupole'} })
    """Python class name used for ELEMENT_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML."""
    hardware_model: str = Field(default="Generic", description="""Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string(Generic)'} })
    """Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``)."""
    machine_area: Optional[str] = Field(default=None, description="""Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``)."""
    virtual_name: str = Field(default="", description="""Alternative internal name used by the control system when the physical name is inaccessible.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string()'} })
    """Alternative internal name used by the control system when the physical name is inaccessible."""
    alias: list[str] = Field(default_factory=list, description="""Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.""", validation_alias=AliasChoices('alias', 'name_alias'), json_schema_extra = { "linkml_meta": {'aliases': ['name_alias'], 'domain_of': ['AcceleratorElement']} })
    """Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings."""
    subelement: Optional[str] = Field(default=None, description="""If set, this element is a logical sub-component of the named parent element.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """If set, this element is a logical sub-component of the named parent element."""
    inputs: list[IOTypeEnum] = Field(default_factory=list, description="""Signal types this element consumes (e.g. ``[current, voltage]``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Signal types this element consumes (e.g. ``[current, voltage]``)."""
    outputs: list[IOTypeEnum] = Field(default_factory=list, description="""Signal types this element produces (e.g. ``[power, phase]``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Signal types this element produces (e.g. ``[power, phase]``)."""
    upstream: list[str] = Field(default_factory=list, description="""Names of elements feeding this one, whose ``outputs`` supply its ``inputs``.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Names of elements feeding this one, whose ``outputs`` supply its ``inputs``."""
    downstream: list[str] = Field(default_factory=list, description="""Names of elements this one feeds; the inverse of ``upstream``.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Names of elements this one feeds; the inverse of ``upstream``."""


class _OctupoleBase(_MagnetBase):
    """
    Octupole magnet.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:Octupole',
         'from_schema': 'https://w3id.org/laura/schema/magnetic',
         'slot_usage': {'hardware_type': {'equals_string': 'Octupole',
                                          'ifabsent': 'Octupole',
                                          'name': 'hardware_type'},
                        'magnetic': {'name': 'magnetic', 'range': 'Octupole_Magnet'}}})

    magnetic: Optional[_OctupoleMagnetBase] = Field(default=None, description="""Magnetic field parameters.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Magnet'], 'in_subset': ['magnetic_properties']} })
    """Magnetic field parameters."""
    degauss: Optional[_DegaussableElementBase] = Field(default=None, description="""Degaussing-cycle parameters.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Magnet']} })
    """Degaussing-cycle parameters."""
    physical: Optional[_PhysicalElementBase] = Field(default=None, description="""Position, rotation, and length data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PhysicalAcceleratorElement'],
         'in_subset': ['physical_properties']} })
    """Position, rotation, and length data."""
    simulation: Optional[_MagnetSimulationElementBase] = Field(default=None, description="""Simulation / tracking attributes.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Simulation / tracking attributes."""
    electrical: Optional[_ElectricalElementBase] = Field(default=None, description="""Power-supply electrical limits.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Power-supply electrical limits."""
    manufacturer: Optional[_ManufacturerElementBase] = Field(default=None, description="""Manufacturer and serial-number data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ManufacturerElement', 'StandardElement']} })
    """Manufacturer and serial-number data."""
    controls: Optional[_ControlsInformationBase] = Field(default=None, description="""Control-system process-variable definitions.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Control-system process-variable definitions."""
    reference: Optional[_ReferenceElementBase] = Field(default=None, description="""Links to design drawings and files.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Links to design drawings and files."""
    name: str = Field(default=..., description="""Unique element name within the machine.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SectionLattice', 'MachineLayout', 'AcceleratorElement']} })
    """Unique element name within the machine."""
    hardware_class: HardwareClassEnum = Field(default=..., description="""Functional category (e.g., ``Magnet``, ``Diagnostic``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Functional category (e.g., ``Magnet``, ``Diagnostic``)."""
    hardware_type: Optional[Literal["Octupole"]] = Field(default="Octupole", description="""Python class name used for ELEMENT_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'],
         'equals_string': 'Octupole',
         'ifabsent': 'Octupole'} })
    """Python class name used for ELEMENT_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML."""
    hardware_model: str = Field(default="Generic", description="""Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string(Generic)'} })
    """Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``)."""
    machine_area: Optional[str] = Field(default=None, description="""Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``)."""
    virtual_name: str = Field(default="", description="""Alternative internal name used by the control system when the physical name is inaccessible.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string()'} })
    """Alternative internal name used by the control system when the physical name is inaccessible."""
    alias: list[str] = Field(default_factory=list, description="""Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.""", validation_alias=AliasChoices('alias', 'name_alias'), json_schema_extra = { "linkml_meta": {'aliases': ['name_alias'], 'domain_of': ['AcceleratorElement']} })
    """Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings."""
    subelement: Optional[str] = Field(default=None, description="""If set, this element is a logical sub-component of the named parent element.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """If set, this element is a logical sub-component of the named parent element."""
    inputs: list[IOTypeEnum] = Field(default_factory=list, description="""Signal types this element consumes (e.g. ``[current, voltage]``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Signal types this element consumes (e.g. ``[current, voltage]``)."""
    outputs: list[IOTypeEnum] = Field(default_factory=list, description="""Signal types this element produces (e.g. ``[power, phase]``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Signal types this element produces (e.g. ``[power, phase]``)."""
    upstream: list[str] = Field(default_factory=list, description="""Names of elements feeding this one, whose ``outputs`` supply its ``inputs``.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Names of elements feeding this one, whose ``outputs`` supply its ``inputs``."""
    downstream: list[str] = Field(default_factory=list, description="""Names of elements this one feeds; the inverse of ``upstream``.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Names of elements this one feeds; the inverse of ``upstream``."""


class _HorizontalCorrectorBase(_DipoleBase):
    """
    Horizontal steering corrector.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:HorizontalCorrector',
         'from_schema': 'https://w3id.org/laura/schema/magnetic',
         'slot_usage': {'hardware_type': {'equals_string': 'Horizontal_Corrector',
                                          'ifabsent': 'Horizontal_Corrector',
                                          'name': 'hardware_type'},
                        'magnetic': {'name': 'magnetic', 'range': 'Corrector_Magnet'}}})

    magnetic: Optional[_CorrectorMagnetBase] = Field(default=None, description="""Magnetic field parameters.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Magnet'], 'in_subset': ['magnetic_properties']} })
    """Magnetic field parameters."""
    degauss: Optional[_DegaussableElementBase] = Field(default=None, description="""Degaussing-cycle parameters.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Magnet']} })
    """Degaussing-cycle parameters."""
    physical: Optional[_PhysicalElementBase] = Field(default=None, description="""Position, rotation, and length data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PhysicalAcceleratorElement'],
         'in_subset': ['physical_properties']} })
    """Position, rotation, and length data."""
    simulation: Optional[_MagnetSimulationElementBase] = Field(default=None, description="""Simulation / tracking attributes.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Simulation / tracking attributes."""
    electrical: Optional[_ElectricalElementBase] = Field(default=None, description="""Power-supply electrical limits.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Power-supply electrical limits."""
    manufacturer: Optional[_ManufacturerElementBase] = Field(default=None, description="""Manufacturer and serial-number data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ManufacturerElement', 'StandardElement']} })
    """Manufacturer and serial-number data."""
    controls: Optional[_ControlsInformationBase] = Field(default=None, description="""Control-system process-variable definitions.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Control-system process-variable definitions."""
    reference: Optional[_ReferenceElementBase] = Field(default=None, description="""Links to design drawings and files.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Links to design drawings and files."""
    name: str = Field(default=..., description="""Unique element name within the machine.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SectionLattice', 'MachineLayout', 'AcceleratorElement']} })
    """Unique element name within the machine."""
    hardware_class: HardwareClassEnum = Field(default=..., description="""Functional category (e.g., ``Magnet``, ``Diagnostic``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Functional category (e.g., ``Magnet``, ``Diagnostic``)."""
    hardware_type: Optional[Literal["Horizontal_Corrector"]] = Field(default="Horizontal_Corrector", description="""Python class name used for ELEMENT_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'],
         'equals_string': 'Horizontal_Corrector',
         'ifabsent': 'Horizontal_Corrector'} })
    """Python class name used for ELEMENT_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML."""
    hardware_model: str = Field(default="Generic", description="""Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string(Generic)'} })
    """Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``)."""
    machine_area: Optional[str] = Field(default=None, description="""Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``)."""
    virtual_name: str = Field(default="", description="""Alternative internal name used by the control system when the physical name is inaccessible.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string()'} })
    """Alternative internal name used by the control system when the physical name is inaccessible."""
    alias: list[str] = Field(default_factory=list, description="""Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.""", validation_alias=AliasChoices('alias', 'name_alias'), json_schema_extra = { "linkml_meta": {'aliases': ['name_alias'], 'domain_of': ['AcceleratorElement']} })
    """Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings."""
    subelement: Optional[str] = Field(default=None, description="""If set, this element is a logical sub-component of the named parent element.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """If set, this element is a logical sub-component of the named parent element."""
    inputs: list[IOTypeEnum] = Field(default_factory=list, description="""Signal types this element consumes (e.g. ``[current, voltage]``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Signal types this element consumes (e.g. ``[current, voltage]``)."""
    outputs: list[IOTypeEnum] = Field(default_factory=list, description="""Signal types this element produces (e.g. ``[power, phase]``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Signal types this element produces (e.g. ``[power, phase]``)."""
    upstream: list[str] = Field(default_factory=list, description="""Names of elements feeding this one, whose ``outputs`` supply its ``inputs``.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Names of elements feeding this one, whose ``outputs`` supply its ``inputs``."""
    downstream: list[str] = Field(default_factory=list, description="""Names of elements this one feeds; the inverse of ``upstream``.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Names of elements this one feeds; the inverse of ``upstream``."""


class _VerticalCorrectorBase(_DipoleBase):
    """
    Vertical steering corrector.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:VerticalCorrector',
         'from_schema': 'https://w3id.org/laura/schema/magnetic',
         'slot_usage': {'hardware_type': {'equals_string': 'Vertical_Corrector',
                                          'ifabsent': 'Vertical_Corrector',
                                          'name': 'hardware_type'},
                        'magnetic': {'name': 'magnetic', 'range': 'Corrector_Magnet'}}})

    magnetic: Optional[_CorrectorMagnetBase] = Field(default=None, description="""Magnetic field parameters.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Magnet'], 'in_subset': ['magnetic_properties']} })
    """Magnetic field parameters."""
    degauss: Optional[_DegaussableElementBase] = Field(default=None, description="""Degaussing-cycle parameters.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Magnet']} })
    """Degaussing-cycle parameters."""
    physical: Optional[_PhysicalElementBase] = Field(default=None, description="""Position, rotation, and length data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PhysicalAcceleratorElement'],
         'in_subset': ['physical_properties']} })
    """Position, rotation, and length data."""
    simulation: Optional[_MagnetSimulationElementBase] = Field(default=None, description="""Simulation / tracking attributes.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Simulation / tracking attributes."""
    electrical: Optional[_ElectricalElementBase] = Field(default=None, description="""Power-supply electrical limits.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Power-supply electrical limits."""
    manufacturer: Optional[_ManufacturerElementBase] = Field(default=None, description="""Manufacturer and serial-number data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ManufacturerElement', 'StandardElement']} })
    """Manufacturer and serial-number data."""
    controls: Optional[_ControlsInformationBase] = Field(default=None, description="""Control-system process-variable definitions.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Control-system process-variable definitions."""
    reference: Optional[_ReferenceElementBase] = Field(default=None, description="""Links to design drawings and files.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Links to design drawings and files."""
    name: str = Field(default=..., description="""Unique element name within the machine.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SectionLattice', 'MachineLayout', 'AcceleratorElement']} })
    """Unique element name within the machine."""
    hardware_class: HardwareClassEnum = Field(default=..., description="""Functional category (e.g., ``Magnet``, ``Diagnostic``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Functional category (e.g., ``Magnet``, ``Diagnostic``)."""
    hardware_type: Optional[Literal["Vertical_Corrector"]] = Field(default="Vertical_Corrector", description="""Python class name used for ELEMENT_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'],
         'equals_string': 'Vertical_Corrector',
         'ifabsent': 'Vertical_Corrector'} })
    """Python class name used for ELEMENT_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML."""
    hardware_model: str = Field(default="Generic", description="""Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string(Generic)'} })
    """Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``)."""
    machine_area: Optional[str] = Field(default=None, description="""Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``)."""
    virtual_name: str = Field(default="", description="""Alternative internal name used by the control system when the physical name is inaccessible.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string()'} })
    """Alternative internal name used by the control system when the physical name is inaccessible."""
    alias: list[str] = Field(default_factory=list, description="""Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.""", validation_alias=AliasChoices('alias', 'name_alias'), json_schema_extra = { "linkml_meta": {'aliases': ['name_alias'], 'domain_of': ['AcceleratorElement']} })
    """Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings."""
    subelement: Optional[str] = Field(default=None, description="""If set, this element is a logical sub-component of the named parent element.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """If set, this element is a logical sub-component of the named parent element."""
    inputs: list[IOTypeEnum] = Field(default_factory=list, description="""Signal types this element consumes (e.g. ``[current, voltage]``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Signal types this element consumes (e.g. ``[current, voltage]``)."""
    outputs: list[IOTypeEnum] = Field(default_factory=list, description="""Signal types this element produces (e.g. ``[power, phase]``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Signal types this element produces (e.g. ``[power, phase]``)."""
    upstream: list[str] = Field(default_factory=list, description="""Names of elements feeding this one, whose ``outputs`` supply its ``inputs``.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Names of elements feeding this one, whose ``outputs`` supply its ``inputs``."""
    downstream: list[str] = Field(default_factory=list, description="""Names of elements this one feeds; the inverse of ``upstream``.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Names of elements this one feeds; the inverse of ``upstream``."""


class _CombinedCorrectorBase(_DipoleBase):
    """
    Combined horizontal/vertical steering corrector, naming the two single-plane correctors it stands in for.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:CombinedCorrector',
         'from_schema': 'https://w3id.org/laura/schema/magnetic',
         'slot_usage': {'hardware_type': {'equals_string': 'Combined_Corrector',
                                          'ifabsent': 'Combined_Corrector',
                                          'name': 'hardware_type'},
                        'magnetic': {'name': 'magnetic',
                                     'range': 'Combined_Corrector_Magnet'}}})

    Horizontal_Corrector: Optional[str] = Field(default=None, description="""Name of the horizontal-plane corrector element.""", json_schema_extra = { "linkml_meta": {'domain_of': ['CombinedCorrector']} })
    """Name of the horizontal-plane corrector element."""
    Vertical_Corrector: Optional[str] = Field(default=None, description="""Name of the vertical-plane corrector element.""", json_schema_extra = { "linkml_meta": {'domain_of': ['CombinedCorrector']} })
    """Name of the vertical-plane corrector element."""
    magnetic: Optional[_CombinedCorrectorMagnetBase] = Field(default=None, description="""Magnetic field parameters.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Magnet'], 'in_subset': ['magnetic_properties']} })
    """Magnetic field parameters."""
    degauss: Optional[_DegaussableElementBase] = Field(default=None, description="""Degaussing-cycle parameters.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Magnet']} })
    """Degaussing-cycle parameters."""
    physical: Optional[_PhysicalElementBase] = Field(default=None, description="""Position, rotation, and length data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PhysicalAcceleratorElement'],
         'in_subset': ['physical_properties']} })
    """Position, rotation, and length data."""
    simulation: Optional[_MagnetSimulationElementBase] = Field(default=None, description="""Simulation / tracking attributes.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Simulation / tracking attributes."""
    electrical: Optional[_ElectricalElementBase] = Field(default=None, description="""Power-supply electrical limits.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Power-supply electrical limits."""
    manufacturer: Optional[_ManufacturerElementBase] = Field(default=None, description="""Manufacturer and serial-number data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ManufacturerElement', 'StandardElement']} })
    """Manufacturer and serial-number data."""
    controls: Optional[_ControlsInformationBase] = Field(default=None, description="""Control-system process-variable definitions.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Control-system process-variable definitions."""
    reference: Optional[_ReferenceElementBase] = Field(default=None, description="""Links to design drawings and files.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Links to design drawings and files."""
    name: str = Field(default=..., description="""Unique element name within the machine.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SectionLattice', 'MachineLayout', 'AcceleratorElement']} })
    """Unique element name within the machine."""
    hardware_class: HardwareClassEnum = Field(default=..., description="""Functional category (e.g., ``Magnet``, ``Diagnostic``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Functional category (e.g., ``Magnet``, ``Diagnostic``)."""
    hardware_type: Optional[Literal["Combined_Corrector"]] = Field(default="Combined_Corrector", description="""Python class name used for ELEMENT_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'],
         'equals_string': 'Combined_Corrector',
         'ifabsent': 'Combined_Corrector'} })
    """Python class name used for ELEMENT_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML."""
    hardware_model: str = Field(default="Generic", description="""Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string(Generic)'} })
    """Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``)."""
    machine_area: Optional[str] = Field(default=None, description="""Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``)."""
    virtual_name: str = Field(default="", description="""Alternative internal name used by the control system when the physical name is inaccessible.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string()'} })
    """Alternative internal name used by the control system when the physical name is inaccessible."""
    alias: list[str] = Field(default_factory=list, description="""Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.""", validation_alias=AliasChoices('alias', 'name_alias'), json_schema_extra = { "linkml_meta": {'aliases': ['name_alias'], 'domain_of': ['AcceleratorElement']} })
    """Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings."""
    subelement: Optional[str] = Field(default=None, description="""If set, this element is a logical sub-component of the named parent element.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """If set, this element is a logical sub-component of the named parent element."""
    inputs: list[IOTypeEnum] = Field(default_factory=list, description="""Signal types this element consumes (e.g. ``[current, voltage]``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Signal types this element consumes (e.g. ``[current, voltage]``)."""
    outputs: list[IOTypeEnum] = Field(default_factory=list, description="""Signal types this element produces (e.g. ``[power, phase]``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Signal types this element produces (e.g. ``[power, phase]``)."""
    upstream: list[str] = Field(default_factory=list, description="""Names of elements feeding this one, whose ``outputs`` supply its ``inputs``.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Names of elements feeding this one, whose ``outputs`` supply its ``inputs``."""
    downstream: list[str] = Field(default_factory=list, description="""Names of elements this one feeds; the inverse of ``upstream``.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Names of elements this one feeds; the inverse of ``upstream``."""


class _SolenoidBase(_MagnetBase):
    """
    Solenoid focusing magnet.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:Solenoid',
         'from_schema': 'https://w3id.org/laura/schema/magnetic',
         'slot_usage': {'hardware_type': {'equals_string': 'Solenoid',
                                          'ifabsent': 'Solenoid',
                                          'name': 'hardware_type'},
                        'magnetic': {'name': 'magnetic', 'range': 'Solenoid_Magnet'}}})

    magnetic: Optional[_SolenoidMagnetBase] = Field(default=None, description="""Magnetic field parameters.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Magnet'], 'in_subset': ['magnetic_properties']} })
    """Magnetic field parameters."""
    degauss: Optional[_DegaussableElementBase] = Field(default=None, description="""Degaussing-cycle parameters.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Magnet']} })
    """Degaussing-cycle parameters."""
    physical: Optional[_PhysicalElementBase] = Field(default=None, description="""Position, rotation, and length data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PhysicalAcceleratorElement'],
         'in_subset': ['physical_properties']} })
    """Position, rotation, and length data."""
    simulation: Optional[_MagnetSimulationElementBase] = Field(default=None, description="""Simulation / tracking attributes.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Simulation / tracking attributes."""
    electrical: Optional[_ElectricalElementBase] = Field(default=None, description="""Power-supply electrical limits.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Power-supply electrical limits."""
    manufacturer: Optional[_ManufacturerElementBase] = Field(default=None, description="""Manufacturer and serial-number data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ManufacturerElement', 'StandardElement']} })
    """Manufacturer and serial-number data."""
    controls: Optional[_ControlsInformationBase] = Field(default=None, description="""Control-system process-variable definitions.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Control-system process-variable definitions."""
    reference: Optional[_ReferenceElementBase] = Field(default=None, description="""Links to design drawings and files.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Links to design drawings and files."""
    name: str = Field(default=..., description="""Unique element name within the machine.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SectionLattice', 'MachineLayout', 'AcceleratorElement']} })
    """Unique element name within the machine."""
    hardware_class: HardwareClassEnum = Field(default=..., description="""Functional category (e.g., ``Magnet``, ``Diagnostic``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Functional category (e.g., ``Magnet``, ``Diagnostic``)."""
    hardware_type: Optional[Literal["Solenoid"]] = Field(default="Solenoid", description="""Python class name used for ELEMENT_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'],
         'equals_string': 'Solenoid',
         'ifabsent': 'Solenoid'} })
    """Python class name used for ELEMENT_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML."""
    hardware_model: str = Field(default="Generic", description="""Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string(Generic)'} })
    """Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``)."""
    machine_area: Optional[str] = Field(default=None, description="""Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``)."""
    virtual_name: str = Field(default="", description="""Alternative internal name used by the control system when the physical name is inaccessible.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string()'} })
    """Alternative internal name used by the control system when the physical name is inaccessible."""
    alias: list[str] = Field(default_factory=list, description="""Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.""", validation_alias=AliasChoices('alias', 'name_alias'), json_schema_extra = { "linkml_meta": {'aliases': ['name_alias'], 'domain_of': ['AcceleratorElement']} })
    """Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings."""
    subelement: Optional[str] = Field(default=None, description="""If set, this element is a logical sub-component of the named parent element.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """If set, this element is a logical sub-component of the named parent element."""
    inputs: list[IOTypeEnum] = Field(default_factory=list, description="""Signal types this element consumes (e.g. ``[current, voltage]``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Signal types this element consumes (e.g. ``[current, voltage]``)."""
    outputs: list[IOTypeEnum] = Field(default_factory=list, description="""Signal types this element produces (e.g. ``[power, phase]``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Signal types this element produces (e.g. ``[power, phase]``)."""
    upstream: list[str] = Field(default_factory=list, description="""Names of elements feeding this one, whose ``outputs`` supply its ``inputs``.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Names of elements feeding this one, whose ``outputs`` supply its ``inputs``."""
    downstream: list[str] = Field(default_factory=list, description="""Names of elements this one feeds; the inverse of ``upstream``.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Names of elements this one feeds; the inverse of ``upstream``."""


class _WigglerBase(_MagnetBase):
    """
    Wiggler / undulator insertion device.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:Wiggler',
         'from_schema': 'https://w3id.org/laura/schema/magnetic',
         'slot_usage': {'hardware_type': {'equals_string': 'Wiggler',
                                          'ifabsent': 'Wiggler',
                                          'name': 'hardware_type'},
                        'magnetic': {'name': 'magnetic', 'range': 'Wiggler_Magnet'}}})

    laser: Optional[_LaserElementBase] = Field(default=None, description="""Drive laser, for laser-undulator (inverse-Compton) configurations.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Laser',
                       'Plasma',
                       'LaserEnergyMeter',
                       'LaserHalfWavePlate',
                       'LaserMirror',
                       'Wiggler']} })
    """Drive laser, for laser-undulator (inverse-Compton) configurations."""
    magnetic: Optional[_WigglerMagnetBase] = Field(default=None, description="""Magnetic field parameters.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Magnet'], 'in_subset': ['magnetic_properties']} })
    """Magnetic field parameters."""
    degauss: Optional[_DegaussableElementBase] = Field(default=None, description="""Degaussing-cycle parameters.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Magnet']} })
    """Degaussing-cycle parameters."""
    physical: Optional[_PhysicalElementBase] = Field(default=None, description="""Position, rotation, and length data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PhysicalAcceleratorElement'],
         'in_subset': ['physical_properties']} })
    """Position, rotation, and length data."""
    simulation: Optional[_MagnetSimulationElementBase] = Field(default=None, description="""Simulation / tracking attributes.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Simulation / tracking attributes."""
    electrical: Optional[_ElectricalElementBase] = Field(default=None, description="""Power-supply electrical limits.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Power-supply electrical limits."""
    manufacturer: Optional[_ManufacturerElementBase] = Field(default=None, description="""Manufacturer and serial-number data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ManufacturerElement', 'StandardElement']} })
    """Manufacturer and serial-number data."""
    controls: Optional[_ControlsInformationBase] = Field(default=None, description="""Control-system process-variable definitions.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Control-system process-variable definitions."""
    reference: Optional[_ReferenceElementBase] = Field(default=None, description="""Links to design drawings and files.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Links to design drawings and files."""
    name: str = Field(default=..., description="""Unique element name within the machine.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SectionLattice', 'MachineLayout', 'AcceleratorElement']} })
    """Unique element name within the machine."""
    hardware_class: HardwareClassEnum = Field(default=..., description="""Functional category (e.g., ``Magnet``, ``Diagnostic``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Functional category (e.g., ``Magnet``, ``Diagnostic``)."""
    hardware_type: Optional[Literal["Wiggler"]] = Field(default="Wiggler", description="""Python class name used for ELEMENT_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'],
         'equals_string': 'Wiggler',
         'ifabsent': 'Wiggler'} })
    """Python class name used for ELEMENT_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML."""
    hardware_model: str = Field(default="Generic", description="""Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string(Generic)'} })
    """Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``)."""
    machine_area: Optional[str] = Field(default=None, description="""Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``)."""
    virtual_name: str = Field(default="", description="""Alternative internal name used by the control system when the physical name is inaccessible.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string()'} })
    """Alternative internal name used by the control system when the physical name is inaccessible."""
    alias: list[str] = Field(default_factory=list, description="""Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.""", validation_alias=AliasChoices('alias', 'name_alias'), json_schema_extra = { "linkml_meta": {'aliases': ['name_alias'], 'domain_of': ['AcceleratorElement']} })
    """Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings."""
    subelement: Optional[str] = Field(default=None, description="""If set, this element is a logical sub-component of the named parent element.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """If set, this element is a logical sub-component of the named parent element."""
    inputs: list[IOTypeEnum] = Field(default_factory=list, description="""Signal types this element consumes (e.g. ``[current, voltage]``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Signal types this element consumes (e.g. ``[current, voltage]``)."""
    outputs: list[IOTypeEnum] = Field(default_factory=list, description="""Signal types this element produces (e.g. ``[power, phase]``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Signal types this element produces (e.g. ``[power, phase]``)."""
    upstream: list[str] = Field(default_factory=list, description="""Names of elements feeding this one, whose ``outputs`` supply its ``inputs``.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Names of elements feeding this one, whose ``outputs`` supply its ``inputs``."""
    downstream: list[str] = Field(default_factory=list, description="""Names of elements this one feeds; the inverse of ``upstream``.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Names of elements this one feeds; the inverse of ``upstream``."""


class _NonLinearLensBase(_MagnetBase):
    """
    Non-linear integrable-optics lens.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:NonLinearLens',
         'from_schema': 'https://w3id.org/laura/schema/magnetic',
         'slot_usage': {'hardware_type': {'equals_string': 'NonLinearLens',
                                          'ifabsent': 'NonLinearLens',
                                          'name': 'hardware_type'},
                        'magnetic': {'name': 'magnetic',
                                     'range': 'NonLinearLens_Magnet'}}})

    magnetic: Optional[_NonLinearLensMagnetBase] = Field(default=None, description="""Magnetic field parameters.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Magnet'], 'in_subset': ['magnetic_properties']} })
    """Magnetic field parameters."""
    degauss: Optional[_DegaussableElementBase] = Field(default=None, description="""Degaussing-cycle parameters.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Magnet']} })
    """Degaussing-cycle parameters."""
    physical: Optional[_PhysicalElementBase] = Field(default=None, description="""Position, rotation, and length data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PhysicalAcceleratorElement'],
         'in_subset': ['physical_properties']} })
    """Position, rotation, and length data."""
    simulation: Optional[_MagnetSimulationElementBase] = Field(default=None, description="""Simulation / tracking attributes.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Simulation / tracking attributes."""
    electrical: Optional[_ElectricalElementBase] = Field(default=None, description="""Power-supply electrical limits.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Power-supply electrical limits."""
    manufacturer: Optional[_ManufacturerElementBase] = Field(default=None, description="""Manufacturer and serial-number data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ManufacturerElement', 'StandardElement']} })
    """Manufacturer and serial-number data."""
    controls: Optional[_ControlsInformationBase] = Field(default=None, description="""Control-system process-variable definitions.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Control-system process-variable definitions."""
    reference: Optional[_ReferenceElementBase] = Field(default=None, description="""Links to design drawings and files.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    """Links to design drawings and files."""
    name: str = Field(default=..., description="""Unique element name within the machine.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SectionLattice', 'MachineLayout', 'AcceleratorElement']} })
    """Unique element name within the machine."""
    hardware_class: HardwareClassEnum = Field(default=..., description="""Functional category (e.g., ``Magnet``, ``Diagnostic``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Functional category (e.g., ``Magnet``, ``Diagnostic``)."""
    hardware_type: Optional[Literal["NonLinearLens"]] = Field(default="NonLinearLens", description="""Python class name used for ELEMENT_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'],
         'equals_string': 'NonLinearLens',
         'ifabsent': 'NonLinearLens'} })
    """Python class name used for ELEMENT_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML."""
    hardware_model: str = Field(default="Generic", description="""Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string(Generic)'} })
    """Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``)."""
    machine_area: Optional[str] = Field(default=None, description="""Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``)."""
    virtual_name: str = Field(default="", description="""Alternative internal name used by the control system when the physical name is inaccessible.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string()'} })
    """Alternative internal name used by the control system when the physical name is inaccessible."""
    alias: list[str] = Field(default_factory=list, description="""Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.""", validation_alias=AliasChoices('alias', 'name_alias'), json_schema_extra = { "linkml_meta": {'aliases': ['name_alias'], 'domain_of': ['AcceleratorElement']} })
    """Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings."""
    subelement: Optional[str] = Field(default=None, description="""If set, this element is a logical sub-component of the named parent element.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """If set, this element is a logical sub-component of the named parent element."""
    inputs: list[IOTypeEnum] = Field(default_factory=list, description="""Signal types this element consumes (e.g. ``[current, voltage]``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Signal types this element consumes (e.g. ``[current, voltage]``)."""
    outputs: list[IOTypeEnum] = Field(default_factory=list, description="""Signal types this element produces (e.g. ``[power, phase]``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Signal types this element produces (e.g. ``[power, phase]``)."""
    upstream: list[str] = Field(default_factory=list, description="""Names of elements feeding this one, whose ``outputs`` supply its ``inputs``.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Names of elements feeding this one, whose ``outputs`` supply its ``inputs``."""
    downstream: list[str] = Field(default_factory=list, description="""Names of elements this one feeds; the inverse of ``upstream``.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    """Names of elements this one feeds; the inverse of ``upstream``."""


# Model rebuild
# see https://pydantic-docs.helpmanual.io/usage/models/#rebuilding-a-model
_PositionBase.model_rebuild()
_RotationBase.model_rebuild()
_ElementPositionErrorBase.model_rebuild()
_ElementSurveyBase.model_rebuild()
_ReferencePlacementBase.model_rebuild()
_PhysicalElementBase.model_rebuild()
_ControlVariableBase.model_rebuild()
_ControlsInformationBase.model_rebuild()
_ShutterElementBase.model_rebuild()
_ValveElementBase.model_rebuild()
_LightingElementBase.model_rebuild()
_ApertureElementBase.model_rebuild()
_SectionLatticeBase.model_rebuild()
_MachineLayoutBase.model_rebuild()
_MachineModelBase.model_rebuild()
_SimulationElementBase.model_rebuild()
_MagnetSimulationElementBase.model_rebuild()
_RFCavitySimulationElementBase.model_rebuild()
_WakefieldSimulationElementBase.model_rebuild()
_DriftSimulationElementBase.model_rebuild()
_DiagnosticSimulationElementBase.model_rebuild()
_PlasmaSimulationElementBase.model_rebuild()
_TwissMatchSimulationElementBase.model_rebuild()
_MatrixTransformSimulationElementBase.model_rebuild()
_ElectrostaticSeparatorSimulationElementBase.model_rebuild()
_ACDipoleSimulationElementBase.model_rebuild()
_WireSimulationElementBase.model_rebuild()
_BeamBeamSimulationElementBase.model_rebuild()
_RFMultipoleSimulationElementBase.model_rebuild()
_MultipoleBase.model_rebuild()
_MultipolesBase.model_rebuild()
_FieldIntegralBase.model_rebuild()
_LinearSaturationFitBase.model_rebuild()
_MagneticElementBase.model_rebuild()
_DegaussableElementBase.model_rebuild()
_RFCavityElementBase.model_rebuild()
_WakefieldElementBase.model_rebuild()
_RFDeflectingCavityElementBase.model_rebuild()
_PIDElementBase.model_rebuild()
_PIDPhaseRangeBase.model_rebuild()
_PIDWeightRangeBase.model_rebuild()
_TraceBase.model_rebuild()
_ChannelNamesBase.model_rebuild()
_LLRFTimingBase.model_rebuild()
_LLRFTimingsBase.model_rebuild()
_LowLevelRFElementBase.model_rebuild()
_RFModulatorElementBase.model_rebuild()
_RFProtectionElementBase.model_rebuild()
_RFHeartbeatElementBase.model_rebuild()
_DiagnosticElementBase.model_rebuild()
_BPMDiagnosticElementBase.model_rebuild()
_BAMDiagnosticElementBase.model_rebuild()
_PhotonIntensityMonitorDiagnosticBase.model_rebuild()
_BLMDiagnosticElementBase.model_rebuild()
_ScreenDiagnosticElementBase.model_rebuild()
_ChargeDiagnosticElementBase.model_rebuild()
_CameraPixelResultsIndicesBase.model_rebuild()
_CameraPixelResultsNamesBase.model_rebuild()
_CameraMaskBase.model_rebuild()
_CameraSensorBase.model_rebuild()
_CameraDiagnosticElementBase.model_rebuild()
_LaserMirrorElementBase.model_rebuild()
_LaserMirrorSenseBase.model_rebuild()
_LaserElementBase.model_rebuild()
_LaserEnergyMeterElementBase.model_rebuild()
_LaserHalfWavePlateElementBase.model_rebuild()
_PlasmaElementBase.model_rebuild()
_DipoleMagnetBase.model_rebuild()
_QuadrupoleMagnetBase.model_rebuild()
_SextupoleMagnetBase.model_rebuild()
_OctupoleMagnetBase.model_rebuild()
_CorrectorMagnetBase.model_rebuild()
_CombinedCorrectorMagnetBase.model_rebuild()
_SolenoidFieldsBase.model_rebuild()
_SolenoidMagnetBase.model_rebuild()
_WigglerMagnetBase.model_rebuild()
_NonLinearLensMagnetBase.model_rebuild()
_ElectricalElementBase.model_rebuild()
_ManufacturerElementBase.model_rebuild()
_ReferenceElementBase.model_rebuild()
_AcceleratorElementBase.model_rebuild()
_StandardElementBase.model_rebuild()
_LightingBase.model_rebuild()
_PowerSupplyBase.model_rebuild()
_LowLevelRFBase.model_rebuild()
_RFModulatorBase.model_rebuild()
_RFProtectionBase.model_rebuild()
_RFHeartbeatBase.model_rebuild()
_PIDBase.model_rebuild()
_LaserEnergyMeterBase.model_rebuild()
_LaserHalfWavePlateBase.model_rebuild()
_LaserMirrorBase.model_rebuild()
_LaserAttenuatorBase.model_rebuild()
_ElementBase.model_rebuild()
_PhysicalAcceleratorElementBase.model_rebuild()
_TwissMatchBase.model_rebuild()
_MatrixTransformBase.model_rebuild()
_ElectrostaticSeparatorBase.model_rebuild()
_ACDipoleBase.model_rebuild()
_HorizontalACDipoleBase.model_rebuild()
_VerticalACDipoleBase.model_rebuild()
_WireBase.model_rebuild()
_BeamBeamBase.model_rebuild()
_RFMultipoleBase.model_rebuild()
_StageBase.model_rebuild()
_VacuumGaugeBase.model_rebuild()
_LaserBase.model_rebuild()
_ShutterBase.model_rebuild()
_ValveBase.model_rebuild()
_MarkerBase.model_rebuild()
_ApertureBase.model_rebuild()
_CollimatorBase.model_rebuild()
_DriftBase.model_rebuild()
_MagnetBase.model_rebuild()
_RFCavityBase.model_rebuild()
_RFDeflectingCavityBase.model_rebuild()
_CrabCavityBase.model_rebuild()
_WakefieldBase.model_rebuild()
_DiagnosticBase.model_rebuild()
_BeamPositionMonitorBase.model_rebuild()
_BeamArrivalMonitorBase.model_rebuild()
_BunchLengthMonitorBase.model_rebuild()
_CameraBase.model_rebuild()
_ScreenBase.model_rebuild()
_ChargeDiagnosticBase.model_rebuild()
_WallCurrentMonitorBase.model_rebuild()
_FaradayCupMonitorBase.model_rebuild()
_IntegratedCurrentTransformerBase.model_rebuild()
_PhotonMonitorBase.model_rebuild()
_PlasmaBase.model_rebuild()
_DipoleBase.model_rebuild()
_QuadrupoleBase.model_rebuild()
_SextupoleBase.model_rebuild()
_OctupoleBase.model_rebuild()
_HorizontalCorrectorBase.model_rebuild()
_VerticalCorrectorBase.model_rebuild()
_CombinedCorrectorBase.model_rebuild()
_SolenoidBase.model_rebuild()
_WigglerBase.model_rebuild()
_NonLinearLensBase.model_rebuild()
