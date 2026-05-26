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
     'description': 'Linked Data schema for the LAURA (Lattice And Unified '
                    'Representation of Accelerators) accelerator element model.  '
                    'Covers all element types, their physical, magnetic, '
                    'diagnostic, RF, and control-system properties.',
     'id': 'https://w3id.org/laura/schema',
     'imports': ['linkml:types'],
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
     'source_file': 'laura/schema/laura_schema.yaml',
     'subsets': {'diagnostic_properties': {'description': 'Slots specific to '
                                                          'beam-diagnostic '
                                                          'instruments.',
                                           'from_schema': 'https://w3id.org/laura/schema',
                                           'name': 'diagnostic_properties'},
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


class ApertureShapeEnum(str, Enum):
    """
    Cross-sectional shape of a beam-pipe aperture.
    """
    circular = "circular"
    rectangular = "rectangular"
    elliptical = "elliptical"



class _PositionBase(ConfiguredBaseModel):
    """
    Cartesian position in the global accelerator coordinate system. All components are in metres.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:Position',
         'from_schema': 'https://w3id.org/laura/schema',
         'in_subset': ['physical_properties']})

    x: Optional[float] = Field(default=None, description="""Horizontal component [m].""", json_schema_extra = { "linkml_meta": {'domain_of': ['Position'], 'unit': {'ucum_code': 'm'}} })
    y: Optional[float] = Field(default=None, description="""Vertical component [m].""", json_schema_extra = { "linkml_meta": {'domain_of': ['Position'], 'unit': {'ucum_code': 'm'}} })
    z: Optional[float] = Field(default=None, description="""Longitudinal (beam-direction) component [m].""", json_schema_extra = { "linkml_meta": {'domain_of': ['Position'], 'unit': {'ucum_code': 'm'}} })


class _RotationBase(ConfiguredBaseModel):
    """
    Euler-angle rotation relative to the global coordinate system. All angles are in radians, bounded to [-pi, pi].
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:Rotation',
         'from_schema': 'https://w3id.org/laura/schema',
         'in_subset': ['physical_properties']})

    phi: Optional[float] = Field(default=None, description="""Rotation about the horizontal (x) axis [rad].""", ge=-3.141592653589793, le=3.141592653589793, json_schema_extra = { "linkml_meta": {'domain_of': ['Rotation'], 'unit': {'ucum_code': 'rad'}} })
    psi: Optional[float] = Field(default=None, description="""Rotation about the vertical (y) axis [rad].""", ge=-3.141592653589793, le=3.141592653589793, json_schema_extra = { "linkml_meta": {'domain_of': ['Rotation'], 'unit': {'ucum_code': 'rad'}} })
    theta: Optional[float] = Field(default=None, description="""Rotation about the longitudinal (z) axis [rad].""", ge=-3.141592653589793, le=3.141592653589793, json_schema_extra = { "linkml_meta": {'domain_of': ['Rotation'], 'unit': {'ucum_code': 'rad'}} })


class _ElementPositionErrorBase(ConfiguredBaseModel):
    """
    Alignment position and rotation errors for a physically-located element.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:ElementPositionError',
         'from_schema': 'https://w3id.org/laura/schema'})

    position: Optional[_PositionBase] = Field(default=None, description="""Positional misalignment error [m].""", json_schema_extra = { "linkml_meta": {'domain_of': ['ElementPositionError', 'ElementSurvey']} })
    rotation: Optional[_RotationBase] = Field(default=None, description="""Angular misalignment error [rad].""", json_schema_extra = { "linkml_meta": {'domain_of': ['ElementPositionError',
                       'ElementSurvey',
                       'PhysicalElement',
                       'CameraDiagnosticElement']} })


class _ElementSurveyBase(ConfiguredBaseModel):
    """
    Survey-measured position and rotation of an element. Structure is identical to ElementPositionError.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:ElementSurvey',
         'from_schema': 'https://w3id.org/laura/schema'})

    position: Optional[_PositionBase] = Field(default=None, description="""Surveyed position.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ElementPositionError', 'ElementSurvey']} })
    rotation: Optional[_RotationBase] = Field(default=None, description="""Surveyed rotation.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ElementPositionError',
                       'ElementSurvey',
                       'PhysicalElement',
                       'CameraDiagnosticElement']} })


class _PhysicalElementBase(ConfiguredBaseModel):
    """
    Physical placement data: position, rotation, length, and associated survey / alignment-error information.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:PhysicalElement',
         'from_schema': 'https://w3id.org/laura/schema',
         'in_subset': ['physical_properties']})

    middle: Optional[_PositionBase] = Field(default=None, description="""Longitudinal midpoint (centre) of the element. Also accepted as ``position`` or ``centre`` in YAML.""", json_schema_extra = { "linkml_meta": {'aliases': ['position', 'centre'], 'domain_of': ['PhysicalElement']} })
    datum: Optional[_PositionBase] = Field(default=None, description="""Datum reference position.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PhysicalElement']} })
    rotation: Optional[_RotationBase] = Field(default=None, description="""Local rotation in the global frame.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ElementPositionError',
                       'ElementSurvey',
                       'PhysicalElement',
                       'CameraDiagnosticElement']} })
    global_rotation: Optional[_RotationBase] = Field(default=None, description="""Accumulated global rotation including parent-frame contributions.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PhysicalElement']} })
    error: Optional[_ElementPositionErrorBase] = Field(default=None, description="""Alignment errors.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PhysicalElement']} })
    survey: Optional[_ElementSurveyBase] = Field(default=None, description="""Survey-measured position and rotation.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PhysicalElement']} })
    length: Optional[float] = Field(default=None, description="""Effective length along the beam axis [m].""", ge=0.0, json_schema_extra = { "linkml_meta": {'domain_of': ['PhysicalElement'], 'unit': {'ucum_code': 'm'}} })
    maximum_position: Optional[float] = Field(default=None, description="""Maximum downstream s-coordinate [m].""", json_schema_extra = { "linkml_meta": {'domain_of': ['PhysicalElement'], 'unit': {'ucum_code': 'm'}} })
    minimum_position: Optional[float] = Field(default=None, description="""Minimum upstream s-coordinate [m].""", json_schema_extra = { "linkml_meta": {'domain_of': ['PhysicalElement'], 'unit': {'ucum_code': 'm'}} })
    physical_angle: Optional[float] = Field(default=None, description="""Bending angle in the horizontal plane [rad]. Derived from ``magnetic.angle`` when available.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PhysicalElement'], 'unit': {'ucum_code': 'rad'}} })


class _ElectricalElementBase(ConfiguredBaseModel):
    """
    Power-supply electrical limits for a beamline element.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:ElectricalElement',
         'from_schema': 'https://w3id.org/laura/schema'})

    min_i: Optional[float] = Field(default=None, description="""Minimum current [A].""", json_schema_extra = { "linkml_meta": {'aliases': ['minI'],
         'domain_of': ['ElectricalElement'],
         'unit': {'ucum_code': 'A'}} })
    max_i: Optional[float] = Field(default=None, description="""Maximum current [A].""", json_schema_extra = { "linkml_meta": {'aliases': ['maxI'],
         'domain_of': ['ElectricalElement'],
         'unit': {'ucum_code': 'A'}} })
    ri_tolerance: Optional[float] = Field(default=None, description="""Read-back vs. set-point tolerance fraction (default 0.1 = 10 %).""", json_schema_extra = { "linkml_meta": {'aliases': ['read_tolerance'], 'domain_of': ['ElectricalElement']} })


class _ManufacturerElementBase(ConfiguredBaseModel):
    """
    Manufacturer and serial-number metadata.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:ManufacturerElement',
         'from_schema': 'https://w3id.org/laura/schema'})

    manufacturer: Optional[str] = Field(default=None, description="""Name of the manufacturer.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ManufacturerElement', 'StandardElement'],
         'slot_uri': 'schema:manufacturer'} })
    serial_number: Optional[str] = Field(default=None, description="""Manufacturer serial number.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ManufacturerElement'], 'slot_uri': 'schema:serialNumber'} })


class _ReferenceElementBase(ConfiguredBaseModel):
    """
    Links to engineering drawings and design files.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:ReferenceElement',
         'from_schema': 'https://w3id.org/laura/schema'})

    drawings: Optional[list[str]] = Field(default=None, description="""Engineering-drawing identifiers or URIs.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ReferenceElement']} })
    design_files: Optional[list[str]] = Field(default=None, description="""Design-file paths or URIs.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ReferenceElement']} })


class _ControlVariableBase(ConfiguredBaseModel):
    """
    A single process-variable entry mapping a logical name to a control-system PV identifier.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:ControlVariable',
         'from_schema': 'https://w3id.org/laura/schema'})

    identifier: Optional[str] = Field(default=None, description="""Protocol-specific PV name (e.g., EPICS PV address).""", json_schema_extra = { "linkml_meta": {'domain_of': ['ControlVariable']} })
    dtype: Optional[str] = Field(default=None, description="""Data type (e.g., ``float``, ``int``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['ControlVariable']} })
    protocol: Optional[str] = Field(default=None, description="""Control-system protocol (e.g., ``EPICS``, ``Tango``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['ControlVariable']} })
    units: Optional[str] = Field(default=None, description="""Physical units string (e.g., ``A``, ``T/m``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['ControlVariable']} })
    description: Optional[str] = Field(default=None, description="""Human-readable description.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ControlVariable']} })
    read_only: Optional[bool] = Field(default=None, description="""Whether the variable is read-only.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ControlVariable']} })
    value: Optional[float] = Field(default=None, description="""Last-read value.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ControlVariable']} })
    target: Optional[float] = Field(default=None, description="""Set-point target value.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ControlVariable']} })
    expression: Optional[str] = Field(default=None, description="""Optional expression string for derived values.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ControlVariable']} })


class _ControlsInformationBase(ConfiguredBaseModel):
    """
    Collection of process-variable definitions for an element's control interface.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:ControlsInformation',
         'from_schema': 'https://w3id.org/laura/schema'})

    variables: Optional[list[_ControlVariableBase]] = Field(default=None, description="""Named control variables keyed by logical name.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ControlsInformation']} })


class _SimulationElementBase(ConfiguredBaseModel):
    """
    Base simulation attributes: field-map files and reference positions for tracking codes.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:SimulationElement',
         'from_schema': 'https://w3id.org/laura/schema'})

    field_definition: Optional[str] = Field(default=None, description="""Path to the 3-D field-map file.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SimulationElement']} })
    wakefield_definition: Optional[str] = Field(default=None, description="""Path to the wakefield impedance file.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SimulationElement']} })
    field_reference_position: Optional[float] = Field(default=None, description="""Longitudinal origin of the field map [m].""", json_schema_extra = { "linkml_meta": {'domain_of': ['SimulationElement'], 'unit': {'ucum_code': 'm'}} })
    scale_field: Optional[float] = Field(default=None, description="""Multiplicative scale factor applied to the field map.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SimulationElement']} })


class _MagnetSimulationElementBase(_SimulationElementBase):
    """
    Simulation attributes specific to magnets: integrator settings, fringe-field model, and radiation flags.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:MagnetSimulationElement',
         'from_schema': 'https://w3id.org/laura/schema'})

    n_kicks: Optional[int] = Field(default=None, description="""Number of integration kicks.""", ge=1, json_schema_extra = { "linkml_meta": {'domain_of': ['MagnetSimulationElement']} })
    n_slices: Optional[int] = Field(default=None, description="""Number of longitudinal slices for thick-lens tracking.""", ge=1, json_schema_extra = { "linkml_meta": {'domain_of': ['MagnetSimulationElement']} })
    smooth: Optional[bool] = Field(default=None, description="""Use a smoothed field profile.""", json_schema_extra = { "linkml_meta": {'domain_of': ['MagnetSimulationElement']} })
    edge_field_integral: Optional[float] = Field(default=None, description="""Fringe-field integral for edge focussing.""", json_schema_extra = { "linkml_meta": {'domain_of': ['MagnetSimulationElement', 'MagneticElement']} })
    edge1_effects: Optional[bool] = Field(default=None, description="""Enable entrance-edge focussing effects.""", json_schema_extra = { "linkml_meta": {'domain_of': ['MagnetSimulationElement']} })
    edge2_effects: Optional[bool] = Field(default=None, description="""Enable exit-edge focussing effects.""", json_schema_extra = { "linkml_meta": {'domain_of': ['MagnetSimulationElement']} })
    sr_enable: Optional[bool] = Field(default=None, description="""Enable synchrotron-radiation energy loss.""", json_schema_extra = { "linkml_meta": {'domain_of': ['MagnetSimulationElement']} })
    isr_enable: Optional[bool] = Field(default=None, description="""Enable incoherent synchrotron-radiation emittance growth.""", json_schema_extra = { "linkml_meta": {'domain_of': ['MagnetSimulationElement']} })
    csr_enable: Optional[bool] = Field(default=None, description="""Enable coherent synchrotron radiation.""", json_schema_extra = { "linkml_meta": {'domain_of': ['MagnetSimulationElement']} })
    csr_bins: Optional[int] = Field(default=None, description="""Number of longitudinal bins for the CSR mesh.""", json_schema_extra = { "linkml_meta": {'domain_of': ['MagnetSimulationElement']} })
    integration_order: Optional[int] = Field(default=None, description="""Order of the symplectic integrator.""", json_schema_extra = { "linkml_meta": {'domain_of': ['MagnetSimulationElement']} })
    nonlinear: Optional[bool] = Field(default=None, description="""Include higher-order (sextupole+) field components.""", json_schema_extra = { "linkml_meta": {'domain_of': ['MagnetSimulationElement']} })
    smoothing_half_width: Optional[int] = Field(default=None, description="""Half-width of the current-profile smoothing kernel.""", json_schema_extra = { "linkml_meta": {'domain_of': ['MagnetSimulationElement']} })
    edge_order: Optional[int] = Field(default=None, description="""Polynomial order of the edge-field expansion.""", json_schema_extra = { "linkml_meta": {'domain_of': ['MagnetSimulationElement']} })
    deltaL: Optional[float] = Field(default=None, description="""Longitudinal step-size override for thick-lens integration [m].""", json_schema_extra = { "linkml_meta": {'domain_of': ['MagnetSimulationElement'], 'unit': {'ucum_code': 'm'}} })
    field_definition: Optional[str] = Field(default=None, description="""Path to the 3-D field-map file.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SimulationElement']} })
    wakefield_definition: Optional[str] = Field(default=None, description="""Path to the wakefield impedance file.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SimulationElement']} })
    field_reference_position: Optional[float] = Field(default=None, description="""Longitudinal origin of the field map [m].""", json_schema_extra = { "linkml_meta": {'domain_of': ['SimulationElement'], 'unit': {'ucum_code': 'm'}} })
    scale_field: Optional[float] = Field(default=None, description="""Multiplicative scale factor applied to the field map.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SimulationElement']} })


class _RFCavitySimulationElementBase(_SimulationElementBase):
    """
    Simulation attributes for RF cavity elements.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:RFCavitySimulationElement',
         'from_schema': 'https://w3id.org/laura/schema'})

    field_definition: Optional[str] = Field(default=None, description="""Path to the 3-D field-map file.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SimulationElement']} })
    wakefield_definition: Optional[str] = Field(default=None, description="""Path to the wakefield impedance file.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SimulationElement']} })
    field_reference_position: Optional[float] = Field(default=None, description="""Longitudinal origin of the field map [m].""", json_schema_extra = { "linkml_meta": {'domain_of': ['SimulationElement'], 'unit': {'ucum_code': 'm'}} })
    scale_field: Optional[float] = Field(default=None, description="""Multiplicative scale factor applied to the field map.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SimulationElement']} })


class _WakefieldSimulationElementBase(_SimulationElementBase):
    """
    Simulation attributes for passive wakefield structures.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:WakefieldSimulationElement',
         'from_schema': 'https://w3id.org/laura/schema'})

    field_definition: Optional[str] = Field(default=None, description="""Path to the 3-D field-map file.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SimulationElement']} })
    wakefield_definition: Optional[str] = Field(default=None, description="""Path to the wakefield impedance file.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SimulationElement']} })
    field_reference_position: Optional[float] = Field(default=None, description="""Longitudinal origin of the field map [m].""", json_schema_extra = { "linkml_meta": {'domain_of': ['SimulationElement'], 'unit': {'ucum_code': 'm'}} })
    scale_field: Optional[float] = Field(default=None, description="""Multiplicative scale factor applied to the field map.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SimulationElement']} })


class _DriftSimulationElementBase(_SimulationElementBase):
    """
    Simulation attributes for field-free drift sections.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:DriftSimulationElement',
         'from_schema': 'https://w3id.org/laura/schema'})

    field_definition: Optional[str] = Field(default=None, description="""Path to the 3-D field-map file.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SimulationElement']} })
    wakefield_definition: Optional[str] = Field(default=None, description="""Path to the wakefield impedance file.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SimulationElement']} })
    field_reference_position: Optional[float] = Field(default=None, description="""Longitudinal origin of the field map [m].""", json_schema_extra = { "linkml_meta": {'domain_of': ['SimulationElement'], 'unit': {'ucum_code': 'm'}} })
    scale_field: Optional[float] = Field(default=None, description="""Multiplicative scale factor applied to the field map.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SimulationElement']} })


class _DiagnosticSimulationElementBase(_SimulationElementBase):
    """
    Simulation attributes for beam-diagnostic elements.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:DiagnosticSimulationElement',
         'from_schema': 'https://w3id.org/laura/schema'})

    field_definition: Optional[str] = Field(default=None, description="""Path to the 3-D field-map file.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SimulationElement']} })
    wakefield_definition: Optional[str] = Field(default=None, description="""Path to the wakefield impedance file.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SimulationElement']} })
    field_reference_position: Optional[float] = Field(default=None, description="""Longitudinal origin of the field map [m].""", json_schema_extra = { "linkml_meta": {'domain_of': ['SimulationElement'], 'unit': {'ucum_code': 'm'}} })
    scale_field: Optional[float] = Field(default=None, description="""Multiplicative scale factor applied to the field map.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SimulationElement']} })


class _PlasmaSimulationElementBase(_SimulationElementBase):
    """
    Simulation attributes for plasma-accelerator stages.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:PlasmaSimulationElement',
         'from_schema': 'https://w3id.org/laura/schema'})

    field_definition: Optional[str] = Field(default=None, description="""Path to the 3-D field-map file.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SimulationElement']} })
    wakefield_definition: Optional[str] = Field(default=None, description="""Path to the wakefield impedance file.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SimulationElement']} })
    field_reference_position: Optional[float] = Field(default=None, description="""Longitudinal origin of the field map [m].""", json_schema_extra = { "linkml_meta": {'domain_of': ['SimulationElement'], 'unit': {'ucum_code': 'm'}} })
    scale_field: Optional[float] = Field(default=None, description="""Multiplicative scale factor applied to the field map.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SimulationElement']} })


class _TwissMatchSimulationElementBase(_SimulationElementBase):
    """
    Simulation attributes for Twiss-matching points.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:TwissMatchSimulationElement',
         'from_schema': 'https://w3id.org/laura/schema'})

    field_definition: Optional[str] = Field(default=None, description="""Path to the 3-D field-map file.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SimulationElement']} })
    wakefield_definition: Optional[str] = Field(default=None, description="""Path to the wakefield impedance file.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SimulationElement']} })
    field_reference_position: Optional[float] = Field(default=None, description="""Longitudinal origin of the field map [m].""", json_schema_extra = { "linkml_meta": {'domain_of': ['SimulationElement'], 'unit': {'ucum_code': 'm'}} })
    scale_field: Optional[float] = Field(default=None, description="""Multiplicative scale factor applied to the field map.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SimulationElement']} })


class _MultipoleBase(ConfiguredBaseModel):
    """
    Individual multipole field component, characterised by order and integrated normal / skew strengths at a reference radius.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:Multipole', 'from_schema': 'https://w3id.org/laura/schema'})

    order: Optional[int] = Field(default=None, description="""Multipole order (0 = dipole, 1 = quadrupole, ?).""", ge=0, json_schema_extra = { "linkml_meta": {'domain_of': ['Multipole', 'MagneticElement']} })
    normal: Optional[float] = Field(default=None, description="""Integrated normal (upright) multipole strength [T.m^{1-n}].""", json_schema_extra = { "linkml_meta": {'domain_of': ['Multipole']} })
    skew: Optional[float] = Field(default=None, description="""Integrated skew (rotated) multipole strength [T.m^{1-n}].""", json_schema_extra = { "linkml_meta": {'domain_of': ['Multipole', 'MagneticElement']} })
    radius: Optional[float] = Field(default=None, description="""Reference radius for multipole normalisation [m].""", json_schema_extra = { "linkml_meta": {'domain_of': ['Multipole', 'ApertureElement'], 'unit': {'ucum_code': 'm'}} })


class _MultipolesBase(ConfiguredBaseModel):
    """
    Complete set of integrated multipole strengths up to decapole order, as named slots for efficient element look-up.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:Multipoles',
         'from_schema': 'https://w3id.org/laura/schema'})

    K0L: Optional[_MultipoleBase] = Field(default=None, description="""Integrated dipole field.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Multipoles']} })
    K1L: Optional[_MultipoleBase] = Field(default=None, description="""Integrated quadrupole gradient.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Multipoles']} })
    K2L: Optional[_MultipoleBase] = Field(default=None, description="""Integrated sextupole strength.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Multipoles']} })
    K3L: Optional[_MultipoleBase] = Field(default=None, description="""Integrated octupole strength.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Multipoles']} })
    K4L: Optional[_MultipoleBase] = Field(default=None, description="""Integrated decapole strength.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Multipoles']} })


class _FieldIntegralBase(ConfiguredBaseModel):
    """
    Polynomial fit of integrated field strength as a function of magnet current.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:FieldIntegral',
         'from_schema': 'https://w3id.org/laura/schema'})

    coefficients: Optional[list[float]] = Field(default=None, description="""Polynomial coefficients ordered from lowest to highest degree: ``FieldIntegral = sum c_n . I^n``.""", json_schema_extra = { "linkml_meta": {'domain_of': ['FieldIntegral']} })


class _LinearSaturationFitBase(ConfiguredBaseModel):
    """
    Bi-linear saturation model mapping magnet current to integrated field strength (K-value conversion).
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:LinearSaturationFit',
         'from_schema': 'https://w3id.org/laura/schema'})

    m: Optional[float] = Field(default=None, description="""Linear slope of the unsaturated region.""", json_schema_extra = { "linkml_meta": {'domain_of': ['LinearSaturationFit']} })
    I_max: Optional[float] = Field(default=None, description="""Current at which saturation begins [A].""", json_schema_extra = { "linkml_meta": {'domain_of': ['LinearSaturationFit'], 'unit': {'ucum_code': 'A'}} })
    f: Optional[float] = Field(default=None, description="""Saturation fraction (slope ratio below/above I_max).""", json_schema_extra = { "linkml_meta": {'domain_of': ['LinearSaturationFit']} })
    a: Optional[float] = Field(default=None, description="""Quadratic saturation coefficient.""", json_schema_extra = { "linkml_meta": {'domain_of': ['LinearSaturationFit']} })
    I0: Optional[float] = Field(default=None, description="""Current offset [A].""", json_schema_extra = { "linkml_meta": {'domain_of': ['LinearSaturationFit'], 'unit': {'ucum_code': 'A'}} })
    d: Optional[float] = Field(default=None, description="""Constant offset term.""", json_schema_extra = { "linkml_meta": {'domain_of': ['LinearSaturationFit']} })
    L: Optional[float] = Field(default=None, description="""Effective magnetic length [m].""", json_schema_extra = { "linkml_meta": {'domain_of': ['LinearSaturationFit'], 'unit': {'ucum_code': 'm'}} })


class _MagneticElementBase(ConfiguredBaseModel):
    """
    Magnetic field parameters for a beamline magnet, including multipole components, field integrals, and geometric edge parameters.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:MagneticElement',
         'from_schema': 'https://w3id.org/laura/schema',
         'in_subset': ['magnetic_properties']})

    order: Optional[int] = Field(default=None, description="""Principal multipole order (0 = dipole, 1 = quad, ?).""", ge=0, json_schema_extra = { "linkml_meta": {'domain_of': ['Multipole', 'MagneticElement']} })
    skew: Optional[bool] = Field(default=None, description="""Whether the magnet is rotated 45? to produce a skew field component.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Multipole', 'MagneticElement']} })
    magnetic_length: Optional[float] = Field(default=None, description="""Magnetic (effective) length [m].""", ge=0.0, json_schema_extra = { "linkml_meta": {'domain_of': ['MagneticElement'], 'unit': {'ucum_code': 'm'}} })
    multipoles: Optional[_MultipolesBase] = Field(default=None, description="""Integrated multipole field components.""", json_schema_extra = { "linkml_meta": {'domain_of': ['MagneticElement']} })
    systematic_multipoles: Optional[_MultipolesBase] = Field(default=None, description="""Systematic (design) multipole errors at the reference radius.""", json_schema_extra = { "linkml_meta": {'domain_of': ['MagneticElement']} })
    random_multipoles: Optional[_MultipolesBase] = Field(default=None, description="""Random multipole errors at the reference radius.""", json_schema_extra = { "linkml_meta": {'domain_of': ['MagneticElement']} })
    field_integral_coefficients: Optional[_FieldIntegralBase] = Field(default=None, description="""Polynomial calibration of integrated field vs. current.""", json_schema_extra = { "linkml_meta": {'domain_of': ['MagneticElement']} })
    linear_saturation_coefficients: Optional[_LinearSaturationFitBase] = Field(default=None, description="""Bi-linear saturation calibration.""", json_schema_extra = { "linkml_meta": {'domain_of': ['MagneticElement']} })
    settle_time: Optional[float] = Field(default=None, description="""Power-supply settle time after a change [s].""", json_schema_extra = { "linkml_meta": {'domain_of': ['MagneticElement'], 'unit': {'ucum_code': 's'}} })
    entrance_edge_angle: Optional[float] = Field(default=None, description="""Fringe-field entrance edge angle [rad].""", json_schema_extra = { "linkml_meta": {'domain_of': ['MagneticElement'], 'unit': {'ucum_code': 'rad'}} })
    exit_edge_angle: Optional[float] = Field(default=None, description="""Fringe-field exit edge angle [rad].""", json_schema_extra = { "linkml_meta": {'domain_of': ['MagneticElement'], 'unit': {'ucum_code': 'rad'}} })
    gap: Optional[float] = Field(default=None, description="""Full gap between pole faces [m].""", ge=0.0, json_schema_extra = { "linkml_meta": {'domain_of': ['MagneticElement'], 'unit': {'ucum_code': 'm'}} })
    bore: Optional[float] = Field(default=None, description="""Magnet bore radius [m].""", ge=0.0, json_schema_extra = { "linkml_meta": {'domain_of': ['MagneticElement'], 'unit': {'ucum_code': 'm'}} })
    plane: Optional[str] = Field(default=None, description="""Principal bending / focusing plane (``H``, ``V``, or ``HV``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['MagneticElement']} })
    width: Optional[float] = Field(default=None, description="""Physical width of the magnet in the bending plane [m].""", json_schema_extra = { "linkml_meta": {'domain_of': ['MagneticElement'], 'unit': {'ucum_code': 'm'}} })
    tilt: Optional[float] = Field(default=None, description="""Global tilt about the beam axis [rad].""", json_schema_extra = { "linkml_meta": {'domain_of': ['MagneticElement'], 'unit': {'ucum_code': 'rad'}} })
    edge_field_integral: Optional[float] = Field(default=None, description="""Enge fringe-field integral parameter (dimensionless).""", json_schema_extra = { "linkml_meta": {'domain_of': ['MagnetSimulationElement', 'MagneticElement']} })
    fringe_field_coefficient: Optional[float] = Field(default=None, description="""Coefficient controlling the fringe-field roll-off rate.""", json_schema_extra = { "linkml_meta": {'domain_of': ['MagneticElement']} })
    gradient: Optional[float] = Field(default=None, description="""Peak field gradient [T/m] (quads) or peak field [T] (dipoles).""", json_schema_extra = { "linkml_meta": {'domain_of': ['MagneticElement'], 'unit': {'ucum_code': 'T.m-1'}} })


class _ApertureElementBase(ConfiguredBaseModel):
    """
    Transverse aperture geometry for drift-space checks and collimators.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:ApertureElement',
         'from_schema': 'https://w3id.org/laura/schema'})

    number_of_elements: Optional[int] = Field(default=None, description="""Number of aperture sub-elements (e.g., for multi-leaf collimators).""", ge=1, json_schema_extra = { "linkml_meta": {'domain_of': ['ApertureElement']} })
    horizontal_size: Optional[float] = Field(default=None, description="""Full horizontal aperture [m].""", ge=0.0, json_schema_extra = { "linkml_meta": {'domain_of': ['ApertureElement'], 'unit': {'ucum_code': 'm'}} })
    vertical_size: Optional[float] = Field(default=None, description="""Full vertical aperture [m].""", ge=0.0, json_schema_extra = { "linkml_meta": {'domain_of': ['ApertureElement'], 'unit': {'ucum_code': 'm'}} })
    shape: Optional[ApertureShapeEnum] = Field(default=None, description="""Cross-sectional aperture shape.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ApertureElement']} })
    radius: Optional[float] = Field(default=None, description="""Radius for circular apertures [m].""", ge=0.0, json_schema_extra = { "linkml_meta": {'domain_of': ['Multipole', 'ApertureElement'], 'unit': {'ucum_code': 'm'}} })
    negative_extent: Optional[float] = Field(default=None, description="""Upstream / inner extent [m].""", json_schema_extra = { "linkml_meta": {'domain_of': ['ApertureElement'], 'unit': {'ucum_code': 'm'}} })
    positive_extent: Optional[float] = Field(default=None, description="""Downstream / outer extent [m].""", json_schema_extra = { "linkml_meta": {'domain_of': ['ApertureElement'], 'unit': {'ucum_code': 'm'}} })


class _RFCavityElementBase(ConfiguredBaseModel):
    """
    RF cavity accelerating-structure parameters.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:RFCavityElement',
         'from_schema': 'https://w3id.org/laura/schema',
         'in_subset': ['rf_properties']})

    structure_type: Optional[str] = Field(default=None, description="""RF structure type (e.g., ``SW`` standing-wave, ``TW`` travelling-wave).""", json_schema_extra = { "linkml_meta": {'aliases': ['structure_Type'], 'domain_of': ['RFCavityElement']} })
    attenuation_constant: Optional[float] = Field(default=None, description="""Attenuation constant ? of a travelling-wave structure [Np/m].""", json_schema_extra = { "linkml_meta": {'domain_of': ['RFCavityElement']} })
    cell_length: Optional[float] = Field(default=None, description="""Length of a single accelerating cell [m].""", ge=0.0, json_schema_extra = { "linkml_meta": {'domain_of': ['RFCavityElement', 'WakefieldElement'],
         'unit': {'ucum_code': 'm'}} })
    coupling_cell_length: Optional[float] = Field(default=None, description="""Length of a coupling cell [m].""", ge=0.0, json_schema_extra = { "linkml_meta": {'domain_of': ['RFCavityElement',
                       'WakefieldElement',
                       'RFDeflectingCavityElement'],
         'unit': {'ucum_code': 'm'}} })
    design_gamma: Optional[float] = Field(default=None, description="""Relativistic Lorentz factor ? at design operating point.""", ge=1.0, json_schema_extra = { "linkml_meta": {'domain_of': ['RFCavityElement', 'RFDeflectingCavityElement']} })
    design_power: Optional[float] = Field(default=None, description="""Design peak RF power [W].""", ge=0.0, json_schema_extra = { "linkml_meta": {'domain_of': ['RFCavityElement', 'RFDeflectingCavityElement'],
         'unit': {'ucum_code': 'W'}} })
    frequency: Optional[float] = Field(default=None, description="""RF operating frequency [Hz].""", ge=0.0, json_schema_extra = { "linkml_meta": {'domain_of': ['RFCavityElement', 'RFDeflectingCavityElement'],
         'unit': {'ucum_code': 'Hz'}} })
    n_cells: Optional[int] = Field(default=None, description="""Number of accelerating cells.""", ge=1, json_schema_extra = { "linkml_meta": {'domain_of': ['RFCavityElement',
                       'WakefieldElement',
                       'RFDeflectingCavityElement']} })
    crest: Optional[float] = Field(default=None, description="""On-crest phase offset providing maximum energy gain [deg].""", json_schema_extra = { "linkml_meta": {'domain_of': ['RFCavityElement'], 'unit': {'ucum_code': 'deg'}} })
    phase: Optional[float] = Field(default=None, description="""Operating phase relative to crest [deg].""", json_schema_extra = { "linkml_meta": {'domain_of': ['RFCavityElement', 'RFDeflectingCavityElement'],
         'unit': {'ucum_code': 'deg'}} })
    shunt_impedance: Optional[float] = Field(default=None, description="""Shunt impedance [M?/m].""", json_schema_extra = { "linkml_meta": {'domain_of': ['RFCavityElement', 'RFDeflectingCavityElement']} })
    mode_numerator: Optional[int] = Field(default=None, description="""Numerator of the operating mode fraction (e.g., 2 for 2pi/3).""", json_schema_extra = { "linkml_meta": {'domain_of': ['RFCavityElement', 'RFDeflectingCavityElement']} })
    mode_denominator: Optional[int] = Field(default=None, description="""Denominator of the operating mode fraction.""", json_schema_extra = { "linkml_meta": {'domain_of': ['RFCavityElement', 'RFDeflectingCavityElement']} })
    power_calibration: Optional[float] = Field(default=None, description="""Calibration constant relating measured power to cavity gradient.""", json_schema_extra = { "linkml_meta": {'domain_of': ['RFCavityElement']} })
    gradient_calibration: Optional[float] = Field(default=None, description="""Calibration relating measured signal to gradient [MV/m per a.u.].""", json_schema_extra = { "linkml_meta": {'domain_of': ['RFCavityElement']} })


class _WakefieldElementBase(ConfiguredBaseModel):
    """
    Passive wakefield structure parameters.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:WakefieldElement',
         'from_schema': 'https://w3id.org/laura/schema',
         'in_subset': ['rf_properties']})

    cell_length: Optional[float] = Field(default=None, description="""Length of a single cell [m].""", ge=0.0, json_schema_extra = { "linkml_meta": {'domain_of': ['RFCavityElement', 'WakefieldElement'],
         'unit': {'ucum_code': 'm'}} })
    n_cells: Optional[int] = Field(default=None, description="""Number of cells.""", ge=1, json_schema_extra = { "linkml_meta": {'domain_of': ['RFCavityElement',
                       'WakefieldElement',
                       'RFDeflectingCavityElement']} })
    coupling_cell_length: Optional[float] = Field(default=None, description="""Length of the coupling cell [m].""", json_schema_extra = { "linkml_meta": {'domain_of': ['RFCavityElement',
                       'WakefieldElement',
                       'RFDeflectingCavityElement'],
         'unit': {'ucum_code': 'm'}} })


class _RFDeflectingCavityElementBase(ConfiguredBaseModel):
    """
    Transverse-deflecting RF cavity parameters -- a subset of RFCavityElement for streak-mode operation.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:RFDeflectingCavityElement',
         'from_schema': 'https://w3id.org/laura/schema',
         'in_subset': ['rf_properties']})

    coupling_cell_length: Optional[float] = Field(default=None, description="""Length of the coupling cell [m].""", json_schema_extra = { "linkml_meta": {'domain_of': ['RFCavityElement',
                       'WakefieldElement',
                       'RFDeflectingCavityElement'],
         'unit': {'ucum_code': 'm'}} })
    design_gamma: Optional[float] = Field(default=None, description="""Design Lorentz factor ?.""", ge=1.0, json_schema_extra = { "linkml_meta": {'domain_of': ['RFCavityElement', 'RFDeflectingCavityElement']} })
    design_power: Optional[float] = Field(default=None, description="""Design peak power [W].""", json_schema_extra = { "linkml_meta": {'domain_of': ['RFCavityElement', 'RFDeflectingCavityElement'],
         'unit': {'ucum_code': 'W'}} })
    frequency: Optional[float] = Field(default=None, description="""Operating frequency [Hz].""", json_schema_extra = { "linkml_meta": {'domain_of': ['RFCavityElement', 'RFDeflectingCavityElement'],
         'unit': {'ucum_code': 'Hz'}} })
    n_cells: Optional[int] = Field(default=None, description="""Number of cells.""", ge=1, json_schema_extra = { "linkml_meta": {'domain_of': ['RFCavityElement',
                       'WakefieldElement',
                       'RFDeflectingCavityElement']} })
    phase: Optional[float] = Field(default=None, description="""Operating phase offset [deg].""", json_schema_extra = { "linkml_meta": {'domain_of': ['RFCavityElement', 'RFDeflectingCavityElement'],
         'unit': {'ucum_code': 'deg'}} })
    shunt_impedance: Optional[float] = Field(default=None, description="""Shunt impedance [M?/m].""", json_schema_extra = { "linkml_meta": {'domain_of': ['RFCavityElement', 'RFDeflectingCavityElement']} })
    mode_numerator: Optional[int] = Field(default=None, description="""Mode fraction numerator.""", json_schema_extra = { "linkml_meta": {'domain_of': ['RFCavityElement', 'RFDeflectingCavityElement']} })
    mode_denominator: Optional[int] = Field(default=None, description="""Mode fraction denominator.""", json_schema_extra = { "linkml_meta": {'domain_of': ['RFCavityElement', 'RFDeflectingCavityElement']} })


class _PIDElementBase(ConfiguredBaseModel):
    """
    PID feedback-controller parameters.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:PIDElement',
         'from_schema': 'https://w3id.org/laura/schema'})

    Kp: Optional[float] = Field(default=None, description="""Proportional gain.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PIDElement']} })
    Ki: Optional[float] = Field(default=None, description="""Integral gain.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PIDElement']} })
    Kd: Optional[float] = Field(default=None, description="""Derivative gain.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PIDElement']} })


class _LowLevelRFElementBase(ConfiguredBaseModel):
    """
    Low-level RF (LLRF) system parameters.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:LowLevelRFElement',
         'from_schema': 'https://w3id.org/laura/schema'})

    pass


class _RFModulatorElementBase(ConfiguredBaseModel):
    """
    RF modulator (klystron driver) parameters.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:RFModulatorElement',
         'from_schema': 'https://w3id.org/laura/schema'})

    pass


class _RFProtectionElementBase(ConfiguredBaseModel):
    """
    RF protection system parameters.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:RFProtectionElement',
         'from_schema': 'https://w3id.org/laura/schema'})

    pass


class _RFHeartbeatElementBase(ConfiguredBaseModel):
    """
    RF heartbeat / timing-monitor element parameters.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:RFHeartbeatElement',
         'from_schema': 'https://w3id.org/laura/schema'})

    pass


class _DiagnosticElementBase(ConfiguredBaseModel):
    """
    Base class for diagnostic instrument sub-models.  Concrete sub-models extend this with instrument-specific fields.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:DiagnosticElement',
         'from_schema': 'https://w3id.org/laura/schema'})

    pass


class _BPMDiagnosticElementBase(_DiagnosticElementBase):
    """
    Beam-position monitor (BPM) diagnostic data.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:BPMDiagnosticElement',
         'from_schema': 'https://w3id.org/laura/schema',
         'in_subset': ['diagnostic_properties']})

    type: Optional[str] = Field(default=None, description="""BPM type (e.g., ``Stripline``, ``Cavity``, ``Button``). Accepted in YAML as ``bpm_type``.""", json_schema_extra = { "linkml_meta": {'aliases': ['bpm_type'],
         'domain_of': ['BPMDiagnosticElement',
                       'BAMDiagnosticElement',
                       'BLMDiagnosticElement',
                       'ScreenDiagnosticElement',
                       'ChargeDiagnosticElement',
                       'CameraDiagnosticElement']} })


class _BAMDiagnosticElementBase(_DiagnosticElementBase):
    """
    Beam-arrival monitor (BAM) diagnostic data.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:BAMDiagnosticElement',
         'from_schema': 'https://w3id.org/laura/schema',
         'in_subset': ['diagnostic_properties']})

    type: Optional[str] = Field(default=None, description="""BAM type. Accepted in YAML as ``bam_type``.""", json_schema_extra = { "linkml_meta": {'aliases': ['bam_type'],
         'domain_of': ['BPMDiagnosticElement',
                       'BAMDiagnosticElement',
                       'BLMDiagnosticElement',
                       'ScreenDiagnosticElement',
                       'ChargeDiagnosticElement',
                       'CameraDiagnosticElement']} })


class _BLMDiagnosticElementBase(_DiagnosticElementBase):
    """
    Bunch-length monitor (BLM) diagnostic data.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:BLMDiagnosticElement',
         'from_schema': 'https://w3id.org/laura/schema',
         'in_subset': ['diagnostic_properties']})

    type: Optional[str] = Field(default=None, description="""BLM type (e.g., ``CDR``). Accepted in YAML as ``blm_type``.""", json_schema_extra = { "linkml_meta": {'aliases': ['blm_type'],
         'domain_of': ['BPMDiagnosticElement',
                       'BAMDiagnosticElement',
                       'BLMDiagnosticElement',
                       'ScreenDiagnosticElement',
                       'ChargeDiagnosticElement',
                       'CameraDiagnosticElement']} })


class _ScreenDiagnosticElementBase(_DiagnosticElementBase):
    """
    Scintillator or OTR screen diagnostic data.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:ScreenDiagnosticElement',
         'from_schema': 'https://w3id.org/laura/schema',
         'in_subset': ['diagnostic_properties']})

    type: Optional[str] = Field(default=None, description="""Screen type (e.g., ``OTR``, ``YAG``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['BPMDiagnosticElement',
                       'BAMDiagnosticElement',
                       'BLMDiagnosticElement',
                       'ScreenDiagnosticElement',
                       'ChargeDiagnosticElement',
                       'CameraDiagnosticElement']} })
    has_camera: Optional[bool] = Field(default=None, description="""Whether the screen has an associated camera.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ScreenDiagnosticElement']} })
    camera_name: Optional[str] = Field(default=None, description="""Name of the associated camera element.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ScreenDiagnosticElement']} })


class _ChargeDiagnosticElementBase(_DiagnosticElementBase):
    """
    Charge-measurement diagnostic data (base for ICT, FCM, WCM).
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:ChargeDiagnosticElement',
         'from_schema': 'https://w3id.org/laura/schema',
         'in_subset': ['diagnostic_properties']})

    type: Optional[str] = Field(default=None, description="""Charge-diagnostic type. Accepted in YAML as ``charge_type``.""", json_schema_extra = { "linkml_meta": {'aliases': ['charge_type'],
         'domain_of': ['BPMDiagnosticElement',
                       'BAMDiagnosticElement',
                       'BLMDiagnosticElement',
                       'ScreenDiagnosticElement',
                       'ChargeDiagnosticElement',
                       'CameraDiagnosticElement']} })


class _CameraDiagnosticElementBase(_DiagnosticElementBase):
    """
    Camera diagnostic data, including sensor parameters, analysis mask, and pixel-to-mm scale factors.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:CameraDiagnosticElement',
         'from_schema': 'https://w3id.org/laura/schema',
         'in_subset': ['diagnostic_properties']})

    type: Optional[str] = Field(default=None, description="""Camera type / model string (e.g., ``PCO``, ``Manta``). Accepted in YAML as ``CAM_TYPE``.""", json_schema_extra = { "linkml_meta": {'aliases': ['CAM_TYPE'],
         'domain_of': ['BPMDiagnosticElement',
                       'BAMDiagnosticElement',
                       'BLMDiagnosticElement',
                       'ScreenDiagnosticElement',
                       'ChargeDiagnosticElement',
                       'CameraDiagnosticElement']} })
    x_pixels: Optional[int] = Field(default=None, description="""Image width reported by the control system [pix].""", json_schema_extra = { "linkml_meta": {'domain_of': ['CameraDiagnosticElement']} })
    y_pixels: Optional[int] = Field(default=None, description="""Image height reported by the control system [pix].""", json_schema_extra = { "linkml_meta": {'domain_of': ['CameraDiagnosticElement']} })
    rotation: Optional[float] = Field(default=None, description="""Camera rotation relative to the screen plane [deg].""", json_schema_extra = { "linkml_meta": {'domain_of': ['ElementPositionError',
                       'ElementSurvey',
                       'PhysicalElement',
                       'CameraDiagnosticElement'],
         'unit': {'ucum_code': 'deg'}} })
    flipped_horizontally: Optional[bool] = Field(default=None, description="""True if the image is mirrored left-right.""", json_schema_extra = { "linkml_meta": {'domain_of': ['CameraDiagnosticElement']} })
    flipped_vertically: Optional[bool] = Field(default=None, description="""True if the image is mirrored top-bottom.""", json_schema_extra = { "linkml_meta": {'domain_of': ['CameraDiagnosticElement']} })
    screen_name: Optional[str] = Field(default=None, description="""Name of the screen element to which this camera is attached.""", json_schema_extra = { "linkml_meta": {'domain_of': ['CameraDiagnosticElement']} })
    has_led: Optional[bool] = Field(default=None, description="""True if the camera mount includes an LED backlight.""", json_schema_extra = { "linkml_meta": {'domain_of': ['CameraDiagnosticElement']} })


class _LaserElementBase(ConfiguredBaseModel):
    """
    Laser-beam parameters (wavelength, pulse energy, profile, etc.) for a laser element or laser-driven plasma stage.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:LaserElement',
         'from_schema': 'https://w3id.org/laura/schema',
         'in_subset': ['laser_properties']})

    initial_position: Optional[float] = Field(default=None, description="""Initial longitudinal position of the laser pulse [m].""", json_schema_extra = { "linkml_meta": {'domain_of': ['LaserElement'], 'unit': {'ucum_code': 'm'}} })
    waist: Optional[float] = Field(default=None, description="""Laser beam waist (1/e^2 radius) [m].""", ge=0.0, json_schema_extra = { "linkml_meta": {'domain_of': ['LaserElement'], 'unit': {'ucum_code': 'm'}} })
    wavelength: Optional[float] = Field(default=None, description="""Laser wavelength [m].""", ge=0.0, json_schema_extra = { "linkml_meta": {'domain_of': ['LaserElement'], 'unit': {'ucum_code': 'm'}} })
    pulse_energy: Optional[float] = Field(default=None, description="""Laser pulse energy [J].""", ge=0.0, json_schema_extra = { "linkml_meta": {'domain_of': ['LaserElement'], 'unit': {'ucum_code': 'J'}} })
    pulse_duration_fwhm: Optional[float] = Field(default=None, description="""Pulse duration at FWHM [s].""", ge=0.0, json_schema_extra = { "linkml_meta": {'domain_of': ['LaserElement'], 'unit': {'ucum_code': 's'}} })
    focal_position: Optional[float] = Field(default=None, description="""Focal (waist) position along the propagation axis [m].""", json_schema_extra = { "linkml_meta": {'domain_of': ['LaserElement'], 'unit': {'ucum_code': 'm'}} })
    cep_phase: Optional[float] = Field(default=None, description="""Carrier-envelope phase [rad].""", json_schema_extra = { "linkml_meta": {'domain_of': ['LaserElement'], 'unit': {'ucum_code': 'rad'}} })
    polarization: Optional[LaserPolarizationEnum] = Field(default=None, description="""Laser polarization state.""", json_schema_extra = { "linkml_meta": {'domain_of': ['LaserElement']} })
    profile_type: Optional[LaserProfileTypeEnum] = Field(default=None, description="""Transverse intensity profile model.""", json_schema_extra = { "linkml_meta": {'domain_of': ['LaserElement']} })
    laguerre_polynomial_order_p: Optional[int] = Field(default=None, description="""Radial Laguerre-Gaussian mode index p (for ``profile_type = laguerre-gaussian``).""", ge=0, json_schema_extra = { "linkml_meta": {'domain_of': ['LaserElement']} })
    flatness: Optional[int] = Field(default=None, description="""Flatness order N of a flattened-Gaussian profile (for ``profile_type = flattened-gaussian``).""", ge=1, json_schema_extra = { "linkml_meta": {'domain_of': ['LaserElement']} })


class _LaserEnergyMeterElementBase(ConfiguredBaseModel):
    """
    Laser energy-meter sub-model (no additional fields).
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:LaserEnergyMeterElement',
         'from_schema': 'https://w3id.org/laura/schema'})

    pass


class _LaserHalfWavePlateElementBase(ConfiguredBaseModel):
    """
    Half-wave plate sub-model (no additional fields).
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:LaserHalfWavePlateElement',
         'from_schema': 'https://w3id.org/laura/schema'})

    pass


class _PlasmaElementBase(ConfiguredBaseModel):
    """
    Plasma channel parameters for a laser-driven plasma-accelerator stage.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:PlasmaElement',
         'from_schema': 'https://w3id.org/laura/schema'})

    density: Optional[float] = Field(default=None, description="""Plasma (electron) number density [m^-^3].""", ge=0.0, json_schema_extra = { "linkml_meta": {'domain_of': ['PlasmaElement'], 'unit': {'ucum_code': 'm-3'}} })
    species: Optional[str] = Field(default=None, description="""Plasma species name (e.g., ``electron``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['PlasmaElement']} })
    ramp_up: Optional[float] = Field(default=None, description="""Entrance density-ramp length [m].""", ge=0.0, json_schema_extra = { "linkml_meta": {'domain_of': ['PlasmaElement'], 'unit': {'ucum_code': 'm'}} })
    plateau: Optional[float] = Field(default=None, description="""Flat-top plateau length [m].""", ge=0.0, json_schema_extra = { "linkml_meta": {'domain_of': ['PlasmaElement'], 'unit': {'ucum_code': 'm'}} })
    ramp_down: Optional[float] = Field(default=None, description="""Exit density-ramp length [m].""", ge=0.0, json_schema_extra = { "linkml_meta": {'domain_of': ['PlasmaElement'], 'unit': {'ucum_code': 'm'}} })
    ramp_decay_length: Optional[float] = Field(default=None, description="""Exponential decay length of the density ramp [m].""", ge=0.0, json_schema_extra = { "linkml_meta": {'domain_of': ['PlasmaElement'], 'unit': {'ucum_code': 'm'}} })
    density_profile: Optional[bool] = Field(default=None, description="""If True, use a user-defined profile; if False, use a flat-top model.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PlasmaElement']} })
    parabolic_coefficient: Optional[float] = Field(default=None, description="""Parabolic coefficient for a transverse density profile.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PlasmaElement']} })


class _ShutterElementBase(ConfiguredBaseModel):
    """
    Shutter interlock configuration.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:ShutterElement',
         'from_schema': 'https://w3id.org/laura/schema'})

    interlocks: Optional[list[str]] = Field(default=None, description="""Names of the interlocks guarding this shutter.""", json_schema_extra = { "linkml_meta": {'aliases': ['shutter_interlock_names'], 'domain_of': ['ShutterElement']} })


class _ValveElementBase(ConfiguredBaseModel):
    """
    Vacuum valve configuration (no additional fields).
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:ValveElement',
         'from_schema': 'https://w3id.org/laura/schema'})

    pass


class _LightingElementBase(ConfiguredBaseModel):
    """
    Lighting element (no additional fields currently defined).
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:LightingElement',
         'from_schema': 'https://w3id.org/laura/schema'})

    pass


class _DegaussableElementBase(ConfiguredBaseModel):
    """
    Degaussing (demagnetisation cycle) parameters for magnets that require a field-reset procedure.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:DegaussableElement',
         'from_schema': 'https://w3id.org/laura/schema',
         'in_subset': ['magnetic_properties']})

    tolerance: Optional[float] = Field(default=None, description="""Current tolerance band during the degauss cycle [A].""", json_schema_extra = { "linkml_meta": {'aliases': ['degauss_tolerance'],
         'domain_of': ['DegaussableElement'],
         'unit': {'ucum_code': 'A'}} })
    values: Optional[list[float]] = Field(default=None, description="""Sequence of peak currents applied during the degauss cycle [A].""", json_schema_extra = { "linkml_meta": {'aliases': ['degauss_values'],
         'domain_of': ['DegaussableElement'],
         'unit': {'ucum_code': 'A'}} })
    steps: Optional[int] = Field(default=None, description="""Number of degauss steps per half-cycle.""", ge=1, json_schema_extra = { "linkml_meta": {'aliases': ['num_degauss_steps'], 'domain_of': ['DegaussableElement']} })


class _AcceleratorElementBase(ConfiguredBaseModel):
    """
    Root base class for all LAURA accelerator elements.  Every lattice element is an instance of a concrete subclass identified by ``hardware_type``.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:AcceleratorElement',
         'from_schema': 'https://w3id.org/laura/schema',
         'tree_root': True})

    name: str = Field(default=..., description="""Unique element name within the machine.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement', 'SectionLattice', 'MachineLayout']} })
    hardware_class: Optional[HardwareClassEnum] = Field(default=None, description="""Functional category (e.g., ``Magnet``, ``Diagnostic``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    hardware_type: Literal["AcceleratorElement"] = Field(default="AcceleratorElement", description="""Python class name used for MODEL_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.""", json_schema_extra = { "linkml_meta": {'designates_type': True, 'domain_of': ['AcceleratorElement']} })
    hardware_model: Optional[str] = Field(default=None, description="""Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    machine_area: Optional[str] = Field(default=None, description="""Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    virtual_name: Optional[str] = Field(default=None, description="""Alternative internal name used by the control system when the physical name is inaccessible.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    alias: Optional[list[str]] = Field(default=None, description="""Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.""", json_schema_extra = { "linkml_meta": {'aliases': ['name_alias'], 'domain_of': ['AcceleratorElement']} })
    subelement: Optional[str] = Field(default=None, description="""If set, this element is a logical sub-component of the named parent element.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })


class _StandardElementBase(_AcceleratorElementBase):
    """
    Accelerator element with control-system, electrical, manufacturer, simulation, and reference sub-models.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:StandardElement',
         'from_schema': 'https://w3id.org/laura/schema'})

    simulation: Optional[_SimulationElementBase] = Field(default=None, description="""Simulation / tracking attributes.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    electrical: Optional[_ElectricalElementBase] = Field(default=None, description="""Power-supply electrical limits.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    manufacturer: Optional[_ManufacturerElementBase] = Field(default=None, description="""Manufacturer and serial-number data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ManufacturerElement', 'StandardElement']} })
    controls: Optional[_ControlsInformationBase] = Field(default=None, description="""Control-system process-variable definitions.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    reference: Optional[_ReferenceElementBase] = Field(default=None, description="""Links to design drawings and files.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    name: str = Field(default=..., description="""Unique element name within the machine.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement', 'SectionLattice', 'MachineLayout']} })
    hardware_class: Optional[HardwareClassEnum] = Field(default=None, description="""Functional category (e.g., ``Magnet``, ``Diagnostic``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    hardware_type: Literal["StandardElement"] = Field(default="StandardElement", description="""Python class name used for MODEL_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.""", json_schema_extra = { "linkml_meta": {'designates_type': True, 'domain_of': ['AcceleratorElement']} })
    hardware_model: Optional[str] = Field(default=None, description="""Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    machine_area: Optional[str] = Field(default=None, description="""Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    virtual_name: Optional[str] = Field(default=None, description="""Alternative internal name used by the control system when the physical name is inaccessible.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    alias: Optional[list[str]] = Field(default=None, description="""Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.""", json_schema_extra = { "linkml_meta": {'aliases': ['name_alias'], 'domain_of': ['AcceleratorElement']} })
    subelement: Optional[str] = Field(default=None, description="""If set, this element is a logical sub-component of the named parent element.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })


class _PhysicalAcceleratorElementBase(_StandardElementBase):
    """
    Accelerator element with a well-defined physical position and orientation in the beamline.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:PhysicalAcceleratorElement',
         'from_schema': 'https://w3id.org/laura/schema'})

    physical: Optional[_PhysicalElementBase] = Field(default=None, description="""Position, rotation, and length data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PhysicalAcceleratorElement'],
         'in_subset': ['physical_properties']} })
    simulation: Optional[_SimulationElementBase] = Field(default=None, description="""Simulation / tracking attributes.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    electrical: Optional[_ElectricalElementBase] = Field(default=None, description="""Power-supply electrical limits.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    manufacturer: Optional[_ManufacturerElementBase] = Field(default=None, description="""Manufacturer and serial-number data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ManufacturerElement', 'StandardElement']} })
    controls: Optional[_ControlsInformationBase] = Field(default=None, description="""Control-system process-variable definitions.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    reference: Optional[_ReferenceElementBase] = Field(default=None, description="""Links to design drawings and files.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    name: str = Field(default=..., description="""Unique element name within the machine.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement', 'SectionLattice', 'MachineLayout']} })
    hardware_class: Optional[HardwareClassEnum] = Field(default=None, description="""Functional category (e.g., ``Magnet``, ``Diagnostic``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    hardware_type: Literal["PhysicalAcceleratorElement"] = Field(default="PhysicalAcceleratorElement", description="""Python class name used for MODEL_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.""", json_schema_extra = { "linkml_meta": {'designates_type': True, 'domain_of': ['AcceleratorElement']} })
    hardware_model: Optional[str] = Field(default=None, description="""Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    machine_area: Optional[str] = Field(default=None, description="""Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    virtual_name: Optional[str] = Field(default=None, description="""Alternative internal name used by the control system when the physical name is inaccessible.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    alias: Optional[list[str]] = Field(default=None, description="""Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.""", json_schema_extra = { "linkml_meta": {'aliases': ['name_alias'], 'domain_of': ['AcceleratorElement']} })
    subelement: Optional[str] = Field(default=None, description="""If set, this element is a logical sub-component of the named parent element.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })


class _MagnetBaseElementBase(_PhysicalAcceleratorElementBase):
    """
    Base class for all magnetic focusing and bending elements. (Named ``MagnetBaseElement`` in the schema to avoid collision with the ``magnetic`` composition-model class; maps to ``Magnet`` in Python.)
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:MagnetBaseElement',
         'from_schema': 'https://w3id.org/laura/schema',
         'slot_usage': {'simulation': {'name': 'simulation',
                                       'range': 'MagnetSimulationElement'}}})

    magnetic: Optional[_MagneticElementBase] = Field(default=None, description="""Magnetic field parameters.""", json_schema_extra = { "linkml_meta": {'domain_of': ['MagnetBaseElement'], 'in_subset': ['magnetic_properties']} })
    degauss: Optional[_DegaussableElementBase] = Field(default=None, description="""Degaussing-cycle parameters.""", json_schema_extra = { "linkml_meta": {'domain_of': ['MagnetBaseElement']} })
    physical: Optional[_PhysicalElementBase] = Field(default=None, description="""Position, rotation, and length data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PhysicalAcceleratorElement'],
         'in_subset': ['physical_properties']} })
    simulation: Optional[_MagnetSimulationElementBase] = Field(default=None, description="""Simulation / tracking attributes.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    electrical: Optional[_ElectricalElementBase] = Field(default=None, description="""Power-supply electrical limits.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    manufacturer: Optional[_ManufacturerElementBase] = Field(default=None, description="""Manufacturer and serial-number data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ManufacturerElement', 'StandardElement']} })
    controls: Optional[_ControlsInformationBase] = Field(default=None, description="""Control-system process-variable definitions.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    reference: Optional[_ReferenceElementBase] = Field(default=None, description="""Links to design drawings and files.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    name: str = Field(default=..., description="""Unique element name within the machine.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement', 'SectionLattice', 'MachineLayout']} })
    hardware_class: Optional[HardwareClassEnum] = Field(default=None, description="""Functional category (e.g., ``Magnet``, ``Diagnostic``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    hardware_type: Literal["MagnetBaseElement"] = Field(default="MagnetBaseElement", description="""Python class name used for MODEL_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.""", json_schema_extra = { "linkml_meta": {'designates_type': True, 'domain_of': ['AcceleratorElement']} })
    hardware_model: Optional[str] = Field(default=None, description="""Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    machine_area: Optional[str] = Field(default=None, description="""Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    virtual_name: Optional[str] = Field(default=None, description="""Alternative internal name used by the control system when the physical name is inaccessible.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    alias: Optional[list[str]] = Field(default=None, description="""Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.""", json_schema_extra = { "linkml_meta": {'aliases': ['name_alias'], 'domain_of': ['AcceleratorElement']} })
    subelement: Optional[str] = Field(default=None, description="""If set, this element is a logical sub-component of the named parent element.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })


class _DipoleBase(_MagnetBaseElementBase):
    """
    Dipole bending magnet.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:Dipole',
         'from_schema': 'https://w3id.org/laura/schema',
         'slot_usage': {'hardware_type': {'equals_string': 'Dipole',
                                          'name': 'hardware_type'}}})

    magnetic: Optional[_MagneticElementBase] = Field(default=None, description="""Magnetic field parameters.""", json_schema_extra = { "linkml_meta": {'domain_of': ['MagnetBaseElement'], 'in_subset': ['magnetic_properties']} })
    degauss: Optional[_DegaussableElementBase] = Field(default=None, description="""Degaussing-cycle parameters.""", json_schema_extra = { "linkml_meta": {'domain_of': ['MagnetBaseElement']} })
    physical: Optional[_PhysicalElementBase] = Field(default=None, description="""Position, rotation, and length data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PhysicalAcceleratorElement'],
         'in_subset': ['physical_properties']} })
    simulation: Optional[_MagnetSimulationElementBase] = Field(default=None, description="""Simulation / tracking attributes.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    electrical: Optional[_ElectricalElementBase] = Field(default=None, description="""Power-supply electrical limits.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    manufacturer: Optional[_ManufacturerElementBase] = Field(default=None, description="""Manufacturer and serial-number data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ManufacturerElement', 'StandardElement']} })
    controls: Optional[_ControlsInformationBase] = Field(default=None, description="""Control-system process-variable definitions.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    reference: Optional[_ReferenceElementBase] = Field(default=None, description="""Links to design drawings and files.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    name: str = Field(default=..., description="""Unique element name within the machine.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement', 'SectionLattice', 'MachineLayout']} })
    hardware_class: Optional[HardwareClassEnum] = Field(default=None, description="""Functional category (e.g., ``Magnet``, ``Diagnostic``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    hardware_type: Literal["Dipole"] = Field(default="Dipole", description="""Python class name used for MODEL_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.""", json_schema_extra = { "linkml_meta": {'designates_type': True,
         'domain_of': ['AcceleratorElement'],
         'equals_string': 'Dipole'} })
    hardware_model: Optional[str] = Field(default=None, description="""Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    machine_area: Optional[str] = Field(default=None, description="""Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    virtual_name: Optional[str] = Field(default=None, description="""Alternative internal name used by the control system when the physical name is inaccessible.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    alias: Optional[list[str]] = Field(default=None, description="""Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.""", json_schema_extra = { "linkml_meta": {'aliases': ['name_alias'], 'domain_of': ['AcceleratorElement']} })
    subelement: Optional[str] = Field(default=None, description="""If set, this element is a logical sub-component of the named parent element.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })


class _QuadrupoleBase(_MagnetBaseElementBase):
    """
    Quadrupole focusing magnet.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:Quadrupole',
         'from_schema': 'https://w3id.org/laura/schema',
         'slot_usage': {'hardware_type': {'equals_string': 'Quadrupole',
                                          'name': 'hardware_type'}}})

    magnetic: Optional[_MagneticElementBase] = Field(default=None, description="""Magnetic field parameters.""", json_schema_extra = { "linkml_meta": {'domain_of': ['MagnetBaseElement'], 'in_subset': ['magnetic_properties']} })
    degauss: Optional[_DegaussableElementBase] = Field(default=None, description="""Degaussing-cycle parameters.""", json_schema_extra = { "linkml_meta": {'domain_of': ['MagnetBaseElement']} })
    physical: Optional[_PhysicalElementBase] = Field(default=None, description="""Position, rotation, and length data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PhysicalAcceleratorElement'],
         'in_subset': ['physical_properties']} })
    simulation: Optional[_MagnetSimulationElementBase] = Field(default=None, description="""Simulation / tracking attributes.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    electrical: Optional[_ElectricalElementBase] = Field(default=None, description="""Power-supply electrical limits.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    manufacturer: Optional[_ManufacturerElementBase] = Field(default=None, description="""Manufacturer and serial-number data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ManufacturerElement', 'StandardElement']} })
    controls: Optional[_ControlsInformationBase] = Field(default=None, description="""Control-system process-variable definitions.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    reference: Optional[_ReferenceElementBase] = Field(default=None, description="""Links to design drawings and files.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    name: str = Field(default=..., description="""Unique element name within the machine.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement', 'SectionLattice', 'MachineLayout']} })
    hardware_class: Optional[HardwareClassEnum] = Field(default=None, description="""Functional category (e.g., ``Magnet``, ``Diagnostic``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    hardware_type: Literal["Quadrupole"] = Field(default="Quadrupole", description="""Python class name used for MODEL_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.""", json_schema_extra = { "linkml_meta": {'designates_type': True,
         'domain_of': ['AcceleratorElement'],
         'equals_string': 'Quadrupole'} })
    hardware_model: Optional[str] = Field(default=None, description="""Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    machine_area: Optional[str] = Field(default=None, description="""Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    virtual_name: Optional[str] = Field(default=None, description="""Alternative internal name used by the control system when the physical name is inaccessible.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    alias: Optional[list[str]] = Field(default=None, description="""Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.""", json_schema_extra = { "linkml_meta": {'aliases': ['name_alias'], 'domain_of': ['AcceleratorElement']} })
    subelement: Optional[str] = Field(default=None, description="""If set, this element is a logical sub-component of the named parent element.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })


class _SextupoleBase(_MagnetBaseElementBase):
    """
    Sextupole chromaticity-correction magnet.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:Sextupole',
         'from_schema': 'https://w3id.org/laura/schema',
         'slot_usage': {'hardware_type': {'equals_string': 'Sextupole',
                                          'name': 'hardware_type'}}})

    magnetic: Optional[_MagneticElementBase] = Field(default=None, description="""Magnetic field parameters.""", json_schema_extra = { "linkml_meta": {'domain_of': ['MagnetBaseElement'], 'in_subset': ['magnetic_properties']} })
    degauss: Optional[_DegaussableElementBase] = Field(default=None, description="""Degaussing-cycle parameters.""", json_schema_extra = { "linkml_meta": {'domain_of': ['MagnetBaseElement']} })
    physical: Optional[_PhysicalElementBase] = Field(default=None, description="""Position, rotation, and length data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PhysicalAcceleratorElement'],
         'in_subset': ['physical_properties']} })
    simulation: Optional[_MagnetSimulationElementBase] = Field(default=None, description="""Simulation / tracking attributes.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    electrical: Optional[_ElectricalElementBase] = Field(default=None, description="""Power-supply electrical limits.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    manufacturer: Optional[_ManufacturerElementBase] = Field(default=None, description="""Manufacturer and serial-number data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ManufacturerElement', 'StandardElement']} })
    controls: Optional[_ControlsInformationBase] = Field(default=None, description="""Control-system process-variable definitions.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    reference: Optional[_ReferenceElementBase] = Field(default=None, description="""Links to design drawings and files.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    name: str = Field(default=..., description="""Unique element name within the machine.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement', 'SectionLattice', 'MachineLayout']} })
    hardware_class: Optional[HardwareClassEnum] = Field(default=None, description="""Functional category (e.g., ``Magnet``, ``Diagnostic``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    hardware_type: Literal["Sextupole"] = Field(default="Sextupole", description="""Python class name used for MODEL_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.""", json_schema_extra = { "linkml_meta": {'designates_type': True,
         'domain_of': ['AcceleratorElement'],
         'equals_string': 'Sextupole'} })
    hardware_model: Optional[str] = Field(default=None, description="""Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    machine_area: Optional[str] = Field(default=None, description="""Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    virtual_name: Optional[str] = Field(default=None, description="""Alternative internal name used by the control system when the physical name is inaccessible.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    alias: Optional[list[str]] = Field(default=None, description="""Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.""", json_schema_extra = { "linkml_meta": {'aliases': ['name_alias'], 'domain_of': ['AcceleratorElement']} })
    subelement: Optional[str] = Field(default=None, description="""If set, this element is a logical sub-component of the named parent element.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })


class _OctupoleBase(_MagnetBaseElementBase):
    """
    Octupole magnet.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:Octupole',
         'from_schema': 'https://w3id.org/laura/schema',
         'slot_usage': {'hardware_type': {'equals_string': 'Octupole',
                                          'name': 'hardware_type'}}})

    magnetic: Optional[_MagneticElementBase] = Field(default=None, description="""Magnetic field parameters.""", json_schema_extra = { "linkml_meta": {'domain_of': ['MagnetBaseElement'], 'in_subset': ['magnetic_properties']} })
    degauss: Optional[_DegaussableElementBase] = Field(default=None, description="""Degaussing-cycle parameters.""", json_schema_extra = { "linkml_meta": {'domain_of': ['MagnetBaseElement']} })
    physical: Optional[_PhysicalElementBase] = Field(default=None, description="""Position, rotation, and length data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PhysicalAcceleratorElement'],
         'in_subset': ['physical_properties']} })
    simulation: Optional[_MagnetSimulationElementBase] = Field(default=None, description="""Simulation / tracking attributes.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    electrical: Optional[_ElectricalElementBase] = Field(default=None, description="""Power-supply electrical limits.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    manufacturer: Optional[_ManufacturerElementBase] = Field(default=None, description="""Manufacturer and serial-number data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ManufacturerElement', 'StandardElement']} })
    controls: Optional[_ControlsInformationBase] = Field(default=None, description="""Control-system process-variable definitions.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    reference: Optional[_ReferenceElementBase] = Field(default=None, description="""Links to design drawings and files.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    name: str = Field(default=..., description="""Unique element name within the machine.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement', 'SectionLattice', 'MachineLayout']} })
    hardware_class: Optional[HardwareClassEnum] = Field(default=None, description="""Functional category (e.g., ``Magnet``, ``Diagnostic``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    hardware_type: Literal["Octupole"] = Field(default="Octupole", description="""Python class name used for MODEL_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.""", json_schema_extra = { "linkml_meta": {'designates_type': True,
         'domain_of': ['AcceleratorElement'],
         'equals_string': 'Octupole'} })
    hardware_model: Optional[str] = Field(default=None, description="""Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    machine_area: Optional[str] = Field(default=None, description="""Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    virtual_name: Optional[str] = Field(default=None, description="""Alternative internal name used by the control system when the physical name is inaccessible.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    alias: Optional[list[str]] = Field(default=None, description="""Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.""", json_schema_extra = { "linkml_meta": {'aliases': ['name_alias'], 'domain_of': ['AcceleratorElement']} })
    subelement: Optional[str] = Field(default=None, description="""If set, this element is a logical sub-component of the named parent element.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })


class _HorizontalCorrectorBase(_DipoleBase):
    """
    Horizontal orbit-corrector dipole.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:HorizontalCorrector',
         'from_schema': 'https://w3id.org/laura/schema',
         'slot_usage': {'hardware_type': {'equals_string': 'Horizontal_Corrector',
                                          'name': 'hardware_type'}}})

    magnetic: Optional[_MagneticElementBase] = Field(default=None, description="""Magnetic field parameters.""", json_schema_extra = { "linkml_meta": {'domain_of': ['MagnetBaseElement'], 'in_subset': ['magnetic_properties']} })
    degauss: Optional[_DegaussableElementBase] = Field(default=None, description="""Degaussing-cycle parameters.""", json_schema_extra = { "linkml_meta": {'domain_of': ['MagnetBaseElement']} })
    physical: Optional[_PhysicalElementBase] = Field(default=None, description="""Position, rotation, and length data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PhysicalAcceleratorElement'],
         'in_subset': ['physical_properties']} })
    simulation: Optional[_MagnetSimulationElementBase] = Field(default=None, description="""Simulation / tracking attributes.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    electrical: Optional[_ElectricalElementBase] = Field(default=None, description="""Power-supply electrical limits.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    manufacturer: Optional[_ManufacturerElementBase] = Field(default=None, description="""Manufacturer and serial-number data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ManufacturerElement', 'StandardElement']} })
    controls: Optional[_ControlsInformationBase] = Field(default=None, description="""Control-system process-variable definitions.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    reference: Optional[_ReferenceElementBase] = Field(default=None, description="""Links to design drawings and files.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    name: str = Field(default=..., description="""Unique element name within the machine.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement', 'SectionLattice', 'MachineLayout']} })
    hardware_class: Optional[HardwareClassEnum] = Field(default=None, description="""Functional category (e.g., ``Magnet``, ``Diagnostic``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    hardware_type: Literal["HorizontalCorrector"] = Field(default="HorizontalCorrector", description="""Python class name used for MODEL_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.""", json_schema_extra = { "linkml_meta": {'designates_type': True,
         'domain_of': ['AcceleratorElement'],
         'equals_string': 'Horizontal_Corrector'} })
    hardware_model: Optional[str] = Field(default=None, description="""Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    machine_area: Optional[str] = Field(default=None, description="""Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    virtual_name: Optional[str] = Field(default=None, description="""Alternative internal name used by the control system when the physical name is inaccessible.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    alias: Optional[list[str]] = Field(default=None, description="""Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.""", json_schema_extra = { "linkml_meta": {'aliases': ['name_alias'], 'domain_of': ['AcceleratorElement']} })
    subelement: Optional[str] = Field(default=None, description="""If set, this element is a logical sub-component of the named parent element.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })


class _VerticalCorrectorBase(_DipoleBase):
    """
    Vertical orbit-corrector dipole.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:VerticalCorrector',
         'from_schema': 'https://w3id.org/laura/schema',
         'slot_usage': {'hardware_type': {'equals_string': 'Vertical_Corrector',
                                          'name': 'hardware_type'}}})

    magnetic: Optional[_MagneticElementBase] = Field(default=None, description="""Magnetic field parameters.""", json_schema_extra = { "linkml_meta": {'domain_of': ['MagnetBaseElement'], 'in_subset': ['magnetic_properties']} })
    degauss: Optional[_DegaussableElementBase] = Field(default=None, description="""Degaussing-cycle parameters.""", json_schema_extra = { "linkml_meta": {'domain_of': ['MagnetBaseElement']} })
    physical: Optional[_PhysicalElementBase] = Field(default=None, description="""Position, rotation, and length data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PhysicalAcceleratorElement'],
         'in_subset': ['physical_properties']} })
    simulation: Optional[_MagnetSimulationElementBase] = Field(default=None, description="""Simulation / tracking attributes.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    electrical: Optional[_ElectricalElementBase] = Field(default=None, description="""Power-supply electrical limits.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    manufacturer: Optional[_ManufacturerElementBase] = Field(default=None, description="""Manufacturer and serial-number data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ManufacturerElement', 'StandardElement']} })
    controls: Optional[_ControlsInformationBase] = Field(default=None, description="""Control-system process-variable definitions.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    reference: Optional[_ReferenceElementBase] = Field(default=None, description="""Links to design drawings and files.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    name: str = Field(default=..., description="""Unique element name within the machine.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement', 'SectionLattice', 'MachineLayout']} })
    hardware_class: Optional[HardwareClassEnum] = Field(default=None, description="""Functional category (e.g., ``Magnet``, ``Diagnostic``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    hardware_type: Literal["VerticalCorrector"] = Field(default="VerticalCorrector", description="""Python class name used for MODEL_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.""", json_schema_extra = { "linkml_meta": {'designates_type': True,
         'domain_of': ['AcceleratorElement'],
         'equals_string': 'Vertical_Corrector'} })
    hardware_model: Optional[str] = Field(default=None, description="""Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    machine_area: Optional[str] = Field(default=None, description="""Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    virtual_name: Optional[str] = Field(default=None, description="""Alternative internal name used by the control system when the physical name is inaccessible.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    alias: Optional[list[str]] = Field(default=None, description="""Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.""", json_schema_extra = { "linkml_meta": {'aliases': ['name_alias'], 'domain_of': ['AcceleratorElement']} })
    subelement: Optional[str] = Field(default=None, description="""If set, this element is a logical sub-component of the named parent element.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })


class _CombinedCorrectorBase(_DipoleBase):
    """
    Combined horizontal and vertical orbit-corrector magnet.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:CombinedCorrector',
         'from_schema': 'https://w3id.org/laura/schema',
         'slot_usage': {'hardware_type': {'equals_string': 'Combined_Corrector',
                                          'name': 'hardware_type'}}})

    magnetic: Optional[_MagneticElementBase] = Field(default=None, description="""Magnetic field parameters.""", json_schema_extra = { "linkml_meta": {'domain_of': ['MagnetBaseElement'], 'in_subset': ['magnetic_properties']} })
    degauss: Optional[_DegaussableElementBase] = Field(default=None, description="""Degaussing-cycle parameters.""", json_schema_extra = { "linkml_meta": {'domain_of': ['MagnetBaseElement']} })
    physical: Optional[_PhysicalElementBase] = Field(default=None, description="""Position, rotation, and length data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PhysicalAcceleratorElement'],
         'in_subset': ['physical_properties']} })
    simulation: Optional[_MagnetSimulationElementBase] = Field(default=None, description="""Simulation / tracking attributes.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    electrical: Optional[_ElectricalElementBase] = Field(default=None, description="""Power-supply electrical limits.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    manufacturer: Optional[_ManufacturerElementBase] = Field(default=None, description="""Manufacturer and serial-number data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ManufacturerElement', 'StandardElement']} })
    controls: Optional[_ControlsInformationBase] = Field(default=None, description="""Control-system process-variable definitions.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    reference: Optional[_ReferenceElementBase] = Field(default=None, description="""Links to design drawings and files.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    name: str = Field(default=..., description="""Unique element name within the machine.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement', 'SectionLattice', 'MachineLayout']} })
    hardware_class: Optional[HardwareClassEnum] = Field(default=None, description="""Functional category (e.g., ``Magnet``, ``Diagnostic``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    hardware_type: Literal["CombinedCorrector"] = Field(default="CombinedCorrector", description="""Python class name used for MODEL_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.""", json_schema_extra = { "linkml_meta": {'designates_type': True,
         'domain_of': ['AcceleratorElement'],
         'equals_string': 'Combined_Corrector'} })
    hardware_model: Optional[str] = Field(default=None, description="""Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    machine_area: Optional[str] = Field(default=None, description="""Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    virtual_name: Optional[str] = Field(default=None, description="""Alternative internal name used by the control system when the physical name is inaccessible.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    alias: Optional[list[str]] = Field(default=None, description="""Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.""", json_schema_extra = { "linkml_meta": {'aliases': ['name_alias'], 'domain_of': ['AcceleratorElement']} })
    subelement: Optional[str] = Field(default=None, description="""If set, this element is a logical sub-component of the named parent element.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })


class _SolenoidBase(_MagnetBaseElementBase):
    """
    Solenoid focussing magnet.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:Solenoid',
         'from_schema': 'https://w3id.org/laura/schema',
         'slot_usage': {'hardware_type': {'equals_string': 'Solenoid',
                                          'name': 'hardware_type'}}})

    magnetic: Optional[_MagneticElementBase] = Field(default=None, description="""Magnetic field parameters.""", json_schema_extra = { "linkml_meta": {'domain_of': ['MagnetBaseElement'], 'in_subset': ['magnetic_properties']} })
    degauss: Optional[_DegaussableElementBase] = Field(default=None, description="""Degaussing-cycle parameters.""", json_schema_extra = { "linkml_meta": {'domain_of': ['MagnetBaseElement']} })
    physical: Optional[_PhysicalElementBase] = Field(default=None, description="""Position, rotation, and length data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PhysicalAcceleratorElement'],
         'in_subset': ['physical_properties']} })
    simulation: Optional[_MagnetSimulationElementBase] = Field(default=None, description="""Simulation / tracking attributes.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    electrical: Optional[_ElectricalElementBase] = Field(default=None, description="""Power-supply electrical limits.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    manufacturer: Optional[_ManufacturerElementBase] = Field(default=None, description="""Manufacturer and serial-number data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ManufacturerElement', 'StandardElement']} })
    controls: Optional[_ControlsInformationBase] = Field(default=None, description="""Control-system process-variable definitions.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    reference: Optional[_ReferenceElementBase] = Field(default=None, description="""Links to design drawings and files.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    name: str = Field(default=..., description="""Unique element name within the machine.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement', 'SectionLattice', 'MachineLayout']} })
    hardware_class: Optional[HardwareClassEnum] = Field(default=None, description="""Functional category (e.g., ``Magnet``, ``Diagnostic``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    hardware_type: Literal["Solenoid"] = Field(default="Solenoid", description="""Python class name used for MODEL_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.""", json_schema_extra = { "linkml_meta": {'designates_type': True,
         'domain_of': ['AcceleratorElement'],
         'equals_string': 'Solenoid'} })
    hardware_model: Optional[str] = Field(default=None, description="""Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    machine_area: Optional[str] = Field(default=None, description="""Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    virtual_name: Optional[str] = Field(default=None, description="""Alternative internal name used by the control system when the physical name is inaccessible.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    alias: Optional[list[str]] = Field(default=None, description="""Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.""", json_schema_extra = { "linkml_meta": {'aliases': ['name_alias'], 'domain_of': ['AcceleratorElement']} })
    subelement: Optional[str] = Field(default=None, description="""If set, this element is a logical sub-component of the named parent element.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })


class _NonLinearLensBase(_MagnetBaseElementBase):
    """
    Non-linear focusing lens (IOTA-style).
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:NonLinearLens',
         'from_schema': 'https://w3id.org/laura/schema',
         'slot_usage': {'hardware_type': {'equals_string': 'NonLinearLens',
                                          'name': 'hardware_type'}}})

    magnetic: Optional[_MagneticElementBase] = Field(default=None, description="""Magnetic field parameters.""", json_schema_extra = { "linkml_meta": {'domain_of': ['MagnetBaseElement'], 'in_subset': ['magnetic_properties']} })
    degauss: Optional[_DegaussableElementBase] = Field(default=None, description="""Degaussing-cycle parameters.""", json_schema_extra = { "linkml_meta": {'domain_of': ['MagnetBaseElement']} })
    physical: Optional[_PhysicalElementBase] = Field(default=None, description="""Position, rotation, and length data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PhysicalAcceleratorElement'],
         'in_subset': ['physical_properties']} })
    simulation: Optional[_MagnetSimulationElementBase] = Field(default=None, description="""Simulation / tracking attributes.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    electrical: Optional[_ElectricalElementBase] = Field(default=None, description="""Power-supply electrical limits.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    manufacturer: Optional[_ManufacturerElementBase] = Field(default=None, description="""Manufacturer and serial-number data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ManufacturerElement', 'StandardElement']} })
    controls: Optional[_ControlsInformationBase] = Field(default=None, description="""Control-system process-variable definitions.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    reference: Optional[_ReferenceElementBase] = Field(default=None, description="""Links to design drawings and files.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    name: str = Field(default=..., description="""Unique element name within the machine.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement', 'SectionLattice', 'MachineLayout']} })
    hardware_class: Optional[HardwareClassEnum] = Field(default=None, description="""Functional category (e.g., ``Magnet``, ``Diagnostic``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    hardware_type: Literal["NonLinearLens"] = Field(default="NonLinearLens", description="""Python class name used for MODEL_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.""", json_schema_extra = { "linkml_meta": {'designates_type': True,
         'domain_of': ['AcceleratorElement'],
         'equals_string': 'NonLinearLens'} })
    hardware_model: Optional[str] = Field(default=None, description="""Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    machine_area: Optional[str] = Field(default=None, description="""Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    virtual_name: Optional[str] = Field(default=None, description="""Alternative internal name used by the control system when the physical name is inaccessible.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    alias: Optional[list[str]] = Field(default=None, description="""Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.""", json_schema_extra = { "linkml_meta": {'aliases': ['name_alias'], 'domain_of': ['AcceleratorElement']} })
    subelement: Optional[str] = Field(default=None, description="""If set, this element is a logical sub-component of the named parent element.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })


class _WigglerBase(_MagnetBaseElementBase):
    """
    Wiggler / undulator permanent-magnet array.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:Wiggler',
         'from_schema': 'https://w3id.org/laura/schema',
         'slot_usage': {'hardware_type': {'equals_string': 'Wiggler',
                                          'name': 'hardware_type'}}})

    magnetic: Optional[_MagneticElementBase] = Field(default=None, description="""Magnetic field parameters.""", json_schema_extra = { "linkml_meta": {'domain_of': ['MagnetBaseElement'], 'in_subset': ['magnetic_properties']} })
    degauss: Optional[_DegaussableElementBase] = Field(default=None, description="""Degaussing-cycle parameters.""", json_schema_extra = { "linkml_meta": {'domain_of': ['MagnetBaseElement']} })
    physical: Optional[_PhysicalElementBase] = Field(default=None, description="""Position, rotation, and length data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PhysicalAcceleratorElement'],
         'in_subset': ['physical_properties']} })
    simulation: Optional[_MagnetSimulationElementBase] = Field(default=None, description="""Simulation / tracking attributes.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    electrical: Optional[_ElectricalElementBase] = Field(default=None, description="""Power-supply electrical limits.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    manufacturer: Optional[_ManufacturerElementBase] = Field(default=None, description="""Manufacturer and serial-number data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ManufacturerElement', 'StandardElement']} })
    controls: Optional[_ControlsInformationBase] = Field(default=None, description="""Control-system process-variable definitions.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    reference: Optional[_ReferenceElementBase] = Field(default=None, description="""Links to design drawings and files.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    name: str = Field(default=..., description="""Unique element name within the machine.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement', 'SectionLattice', 'MachineLayout']} })
    hardware_class: Optional[HardwareClassEnum] = Field(default=None, description="""Functional category (e.g., ``Magnet``, ``Diagnostic``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    hardware_type: Literal["Wiggler"] = Field(default="Wiggler", description="""Python class name used for MODEL_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.""", json_schema_extra = { "linkml_meta": {'designates_type': True,
         'domain_of': ['AcceleratorElement'],
         'equals_string': 'Wiggler'} })
    hardware_model: Optional[str] = Field(default=None, description="""Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    machine_area: Optional[str] = Field(default=None, description="""Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    virtual_name: Optional[str] = Field(default=None, description="""Alternative internal name used by the control system when the physical name is inaccessible.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    alias: Optional[list[str]] = Field(default=None, description="""Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.""", json_schema_extra = { "linkml_meta": {'aliases': ['name_alias'], 'domain_of': ['AcceleratorElement']} })
    subelement: Optional[str] = Field(default=None, description="""If set, this element is a logical sub-component of the named parent element.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })


class _DiagnosticBase(_PhysicalAcceleratorElementBase):
    """
    Base class for all beam-diagnostic instruments.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:Diagnostic',
         'from_schema': 'https://w3id.org/laura/schema',
         'slot_usage': {'simulation': {'name': 'simulation',
                                       'range': 'DiagnosticSimulationElement'}}})

    diagnostic: Optional[_DiagnosticElementBase] = Field(default=None, description="""Instrument-specific diagnostic parameters.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Diagnostic',
                       'BeamPositionMonitor',
                       'BeamArrivalMonitor',
                       'BunchLengthMonitor',
                       'Camera',
                       'Screen',
                       'ChargeDiagnostic'],
         'in_subset': ['diagnostic_properties']} })
    physical: Optional[_PhysicalElementBase] = Field(default=None, description="""Position, rotation, and length data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PhysicalAcceleratorElement'],
         'in_subset': ['physical_properties']} })
    simulation: Optional[_DiagnosticSimulationElementBase] = Field(default=None, description="""Simulation / tracking attributes.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    electrical: Optional[_ElectricalElementBase] = Field(default=None, description="""Power-supply electrical limits.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    manufacturer: Optional[_ManufacturerElementBase] = Field(default=None, description="""Manufacturer and serial-number data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ManufacturerElement', 'StandardElement']} })
    controls: Optional[_ControlsInformationBase] = Field(default=None, description="""Control-system process-variable definitions.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    reference: Optional[_ReferenceElementBase] = Field(default=None, description="""Links to design drawings and files.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    name: str = Field(default=..., description="""Unique element name within the machine.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement', 'SectionLattice', 'MachineLayout']} })
    hardware_class: Optional[HardwareClassEnum] = Field(default=None, description="""Functional category (e.g., ``Magnet``, ``Diagnostic``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    hardware_type: Literal["Diagnostic"] = Field(default="Diagnostic", description="""Python class name used for MODEL_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.""", json_schema_extra = { "linkml_meta": {'designates_type': True, 'domain_of': ['AcceleratorElement']} })
    hardware_model: Optional[str] = Field(default=None, description="""Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    machine_area: Optional[str] = Field(default=None, description="""Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    virtual_name: Optional[str] = Field(default=None, description="""Alternative internal name used by the control system when the physical name is inaccessible.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    alias: Optional[list[str]] = Field(default=None, description="""Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.""", json_schema_extra = { "linkml_meta": {'aliases': ['name_alias'], 'domain_of': ['AcceleratorElement']} })
    subelement: Optional[str] = Field(default=None, description="""If set, this element is a logical sub-component of the named parent element.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })


class _BeamPositionMonitorBase(_DiagnosticBase):
    """
    Beam-position monitor (BPM).
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:BeamPositionMonitor',
         'from_schema': 'https://w3id.org/laura/schema',
         'slot_usage': {'hardware_type': {'equals_string': 'Beam_Position_Monitor',
                                          'name': 'hardware_type'}}})

    diagnostic: Optional[_BPMDiagnosticElementBase] = Field(default=None, description="""Instrument-specific diagnostic parameters.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Diagnostic',
                       'BeamPositionMonitor',
                       'BeamArrivalMonitor',
                       'BunchLengthMonitor',
                       'Camera',
                       'Screen',
                       'ChargeDiagnostic'],
         'in_subset': ['diagnostic_properties']} })
    physical: Optional[_PhysicalElementBase] = Field(default=None, description="""Position, rotation, and length data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PhysicalAcceleratorElement'],
         'in_subset': ['physical_properties']} })
    simulation: Optional[_DiagnosticSimulationElementBase] = Field(default=None, description="""Simulation / tracking attributes.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    electrical: Optional[_ElectricalElementBase] = Field(default=None, description="""Power-supply electrical limits.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    manufacturer: Optional[_ManufacturerElementBase] = Field(default=None, description="""Manufacturer and serial-number data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ManufacturerElement', 'StandardElement']} })
    controls: Optional[_ControlsInformationBase] = Field(default=None, description="""Control-system process-variable definitions.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    reference: Optional[_ReferenceElementBase] = Field(default=None, description="""Links to design drawings and files.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    name: str = Field(default=..., description="""Unique element name within the machine.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement', 'SectionLattice', 'MachineLayout']} })
    hardware_class: Optional[HardwareClassEnum] = Field(default=None, description="""Functional category (e.g., ``Magnet``, ``Diagnostic``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    hardware_type: Literal["BeamPositionMonitor"] = Field(default="BeamPositionMonitor", description="""Python class name used for MODEL_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.""", json_schema_extra = { "linkml_meta": {'designates_type': True,
         'domain_of': ['AcceleratorElement'],
         'equals_string': 'Beam_Position_Monitor'} })
    hardware_model: Optional[str] = Field(default=None, description="""Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    machine_area: Optional[str] = Field(default=None, description="""Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    virtual_name: Optional[str] = Field(default=None, description="""Alternative internal name used by the control system when the physical name is inaccessible.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    alias: Optional[list[str]] = Field(default=None, description="""Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.""", json_schema_extra = { "linkml_meta": {'aliases': ['name_alias'], 'domain_of': ['AcceleratorElement']} })
    subelement: Optional[str] = Field(default=None, description="""If set, this element is a logical sub-component of the named parent element.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })


class _BeamArrivalMonitorBase(_DiagnosticBase):
    """
    Beam-arrival-time monitor (BAM).
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:BeamArrivalMonitor',
         'from_schema': 'https://w3id.org/laura/schema',
         'slot_usage': {'hardware_type': {'equals_string': 'Beam_Arrival_Monitor',
                                          'name': 'hardware_type'}}})

    diagnostic: Optional[_BAMDiagnosticElementBase] = Field(default=None, description="""Instrument-specific diagnostic parameters.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Diagnostic',
                       'BeamPositionMonitor',
                       'BeamArrivalMonitor',
                       'BunchLengthMonitor',
                       'Camera',
                       'Screen',
                       'ChargeDiagnostic'],
         'in_subset': ['diagnostic_properties']} })
    physical: Optional[_PhysicalElementBase] = Field(default=None, description="""Position, rotation, and length data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PhysicalAcceleratorElement'],
         'in_subset': ['physical_properties']} })
    simulation: Optional[_DiagnosticSimulationElementBase] = Field(default=None, description="""Simulation / tracking attributes.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    electrical: Optional[_ElectricalElementBase] = Field(default=None, description="""Power-supply electrical limits.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    manufacturer: Optional[_ManufacturerElementBase] = Field(default=None, description="""Manufacturer and serial-number data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ManufacturerElement', 'StandardElement']} })
    controls: Optional[_ControlsInformationBase] = Field(default=None, description="""Control-system process-variable definitions.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    reference: Optional[_ReferenceElementBase] = Field(default=None, description="""Links to design drawings and files.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    name: str = Field(default=..., description="""Unique element name within the machine.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement', 'SectionLattice', 'MachineLayout']} })
    hardware_class: Optional[HardwareClassEnum] = Field(default=None, description="""Functional category (e.g., ``Magnet``, ``Diagnostic``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    hardware_type: Literal["BeamArrivalMonitor"] = Field(default="BeamArrivalMonitor", description="""Python class name used for MODEL_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.""", json_schema_extra = { "linkml_meta": {'designates_type': True,
         'domain_of': ['AcceleratorElement'],
         'equals_string': 'Beam_Arrival_Monitor'} })
    hardware_model: Optional[str] = Field(default=None, description="""Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    machine_area: Optional[str] = Field(default=None, description="""Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    virtual_name: Optional[str] = Field(default=None, description="""Alternative internal name used by the control system when the physical name is inaccessible.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    alias: Optional[list[str]] = Field(default=None, description="""Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.""", json_schema_extra = { "linkml_meta": {'aliases': ['name_alias'], 'domain_of': ['AcceleratorElement']} })
    subelement: Optional[str] = Field(default=None, description="""If set, this element is a logical sub-component of the named parent element.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })


class _BunchLengthMonitorBase(_DiagnosticBase):
    """
    Bunch-length monitor (BLM / CDR detector).
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:BunchLengthMonitor',
         'from_schema': 'https://w3id.org/laura/schema',
         'slot_usage': {'hardware_type': {'equals_string': 'Bunch_Length_Monitor',
                                          'name': 'hardware_type'}}})

    diagnostic: Optional[_BLMDiagnosticElementBase] = Field(default=None, description="""Instrument-specific diagnostic parameters.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Diagnostic',
                       'BeamPositionMonitor',
                       'BeamArrivalMonitor',
                       'BunchLengthMonitor',
                       'Camera',
                       'Screen',
                       'ChargeDiagnostic'],
         'in_subset': ['diagnostic_properties']} })
    physical: Optional[_PhysicalElementBase] = Field(default=None, description="""Position, rotation, and length data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PhysicalAcceleratorElement'],
         'in_subset': ['physical_properties']} })
    simulation: Optional[_DiagnosticSimulationElementBase] = Field(default=None, description="""Simulation / tracking attributes.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    electrical: Optional[_ElectricalElementBase] = Field(default=None, description="""Power-supply electrical limits.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    manufacturer: Optional[_ManufacturerElementBase] = Field(default=None, description="""Manufacturer and serial-number data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ManufacturerElement', 'StandardElement']} })
    controls: Optional[_ControlsInformationBase] = Field(default=None, description="""Control-system process-variable definitions.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    reference: Optional[_ReferenceElementBase] = Field(default=None, description="""Links to design drawings and files.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    name: str = Field(default=..., description="""Unique element name within the machine.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement', 'SectionLattice', 'MachineLayout']} })
    hardware_class: Optional[HardwareClassEnum] = Field(default=None, description="""Functional category (e.g., ``Magnet``, ``Diagnostic``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    hardware_type: Literal["BunchLengthMonitor"] = Field(default="BunchLengthMonitor", description="""Python class name used for MODEL_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.""", json_schema_extra = { "linkml_meta": {'designates_type': True,
         'domain_of': ['AcceleratorElement'],
         'equals_string': 'Bunch_Length_Monitor'} })
    hardware_model: Optional[str] = Field(default=None, description="""Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    machine_area: Optional[str] = Field(default=None, description="""Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    virtual_name: Optional[str] = Field(default=None, description="""Alternative internal name used by the control system when the physical name is inaccessible.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    alias: Optional[list[str]] = Field(default=None, description="""Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.""", json_schema_extra = { "linkml_meta": {'aliases': ['name_alias'], 'domain_of': ['AcceleratorElement']} })
    subelement: Optional[str] = Field(default=None, description="""If set, this element is a logical sub-component of the named parent element.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })


class _CameraBase(_DiagnosticBase):
    """
    Camera-based beam-profile monitor.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:Camera',
         'from_schema': 'https://w3id.org/laura/schema',
         'slot_usage': {'hardware_type': {'equals_string': 'Camera',
                                          'name': 'hardware_type'}}})

    diagnostic: Optional[_CameraDiagnosticElementBase] = Field(default=None, description="""Instrument-specific diagnostic parameters.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Diagnostic',
                       'BeamPositionMonitor',
                       'BeamArrivalMonitor',
                       'BunchLengthMonitor',
                       'Camera',
                       'Screen',
                       'ChargeDiagnostic'],
         'in_subset': ['diagnostic_properties']} })
    physical: Optional[_PhysicalElementBase] = Field(default=None, description="""Position, rotation, and length data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PhysicalAcceleratorElement'],
         'in_subset': ['physical_properties']} })
    simulation: Optional[_DiagnosticSimulationElementBase] = Field(default=None, description="""Simulation / tracking attributes.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    electrical: Optional[_ElectricalElementBase] = Field(default=None, description="""Power-supply electrical limits.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    manufacturer: Optional[_ManufacturerElementBase] = Field(default=None, description="""Manufacturer and serial-number data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ManufacturerElement', 'StandardElement']} })
    controls: Optional[_ControlsInformationBase] = Field(default=None, description="""Control-system process-variable definitions.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    reference: Optional[_ReferenceElementBase] = Field(default=None, description="""Links to design drawings and files.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    name: str = Field(default=..., description="""Unique element name within the machine.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement', 'SectionLattice', 'MachineLayout']} })
    hardware_class: Optional[HardwareClassEnum] = Field(default=None, description="""Functional category (e.g., ``Magnet``, ``Diagnostic``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    hardware_type: Literal["Camera"] = Field(default="Camera", description="""Python class name used for MODEL_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.""", json_schema_extra = { "linkml_meta": {'designates_type': True,
         'domain_of': ['AcceleratorElement'],
         'equals_string': 'Camera'} })
    hardware_model: Optional[str] = Field(default=None, description="""Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    machine_area: Optional[str] = Field(default=None, description="""Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    virtual_name: Optional[str] = Field(default=None, description="""Alternative internal name used by the control system when the physical name is inaccessible.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    alias: Optional[list[str]] = Field(default=None, description="""Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.""", json_schema_extra = { "linkml_meta": {'aliases': ['name_alias'], 'domain_of': ['AcceleratorElement']} })
    subelement: Optional[str] = Field(default=None, description="""If set, this element is a logical sub-component of the named parent element.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })


class _ScreenBase(_DiagnosticBase):
    """
    Scintillator or OTR screen with an associated camera.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:Screen',
         'from_schema': 'https://w3id.org/laura/schema',
         'slot_usage': {'hardware_type': {'equals_string': 'Screen',
                                          'name': 'hardware_type'}}})

    diagnostic: Optional[_ScreenDiagnosticElementBase] = Field(default=None, description="""Instrument-specific diagnostic parameters.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Diagnostic',
                       'BeamPositionMonitor',
                       'BeamArrivalMonitor',
                       'BunchLengthMonitor',
                       'Camera',
                       'Screen',
                       'ChargeDiagnostic'],
         'in_subset': ['diagnostic_properties']} })
    physical: Optional[_PhysicalElementBase] = Field(default=None, description="""Position, rotation, and length data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PhysicalAcceleratorElement'],
         'in_subset': ['physical_properties']} })
    simulation: Optional[_DiagnosticSimulationElementBase] = Field(default=None, description="""Simulation / tracking attributes.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    electrical: Optional[_ElectricalElementBase] = Field(default=None, description="""Power-supply electrical limits.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    manufacturer: Optional[_ManufacturerElementBase] = Field(default=None, description="""Manufacturer and serial-number data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ManufacturerElement', 'StandardElement']} })
    controls: Optional[_ControlsInformationBase] = Field(default=None, description="""Control-system process-variable definitions.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    reference: Optional[_ReferenceElementBase] = Field(default=None, description="""Links to design drawings and files.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    name: str = Field(default=..., description="""Unique element name within the machine.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement', 'SectionLattice', 'MachineLayout']} })
    hardware_class: Optional[HardwareClassEnum] = Field(default=None, description="""Functional category (e.g., ``Magnet``, ``Diagnostic``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    hardware_type: Literal["Screen"] = Field(default="Screen", description="""Python class name used for MODEL_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.""", json_schema_extra = { "linkml_meta": {'designates_type': True,
         'domain_of': ['AcceleratorElement'],
         'equals_string': 'Screen'} })
    hardware_model: Optional[str] = Field(default=None, description="""Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    machine_area: Optional[str] = Field(default=None, description="""Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    virtual_name: Optional[str] = Field(default=None, description="""Alternative internal name used by the control system when the physical name is inaccessible.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    alias: Optional[list[str]] = Field(default=None, description="""Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.""", json_schema_extra = { "linkml_meta": {'aliases': ['name_alias'], 'domain_of': ['AcceleratorElement']} })
    subelement: Optional[str] = Field(default=None, description="""If set, this element is a logical sub-component of the named parent element.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })


class _ChargeDiagnosticBase(_DiagnosticBase):
    """
    Base class for charge-measurement diagnostics.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:ChargeDiagnostic',
         'from_schema': 'https://w3id.org/laura/schema',
         'slot_usage': {'hardware_type': {'equals_string': 'ChargeDiagnostic',
                                          'name': 'hardware_type'}}})

    diagnostic: Optional[_ChargeDiagnosticElementBase] = Field(default=None, description="""Instrument-specific diagnostic parameters.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Diagnostic',
                       'BeamPositionMonitor',
                       'BeamArrivalMonitor',
                       'BunchLengthMonitor',
                       'Camera',
                       'Screen',
                       'ChargeDiagnostic'],
         'in_subset': ['diagnostic_properties']} })
    physical: Optional[_PhysicalElementBase] = Field(default=None, description="""Position, rotation, and length data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PhysicalAcceleratorElement'],
         'in_subset': ['physical_properties']} })
    simulation: Optional[_DiagnosticSimulationElementBase] = Field(default=None, description="""Simulation / tracking attributes.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    electrical: Optional[_ElectricalElementBase] = Field(default=None, description="""Power-supply electrical limits.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    manufacturer: Optional[_ManufacturerElementBase] = Field(default=None, description="""Manufacturer and serial-number data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ManufacturerElement', 'StandardElement']} })
    controls: Optional[_ControlsInformationBase] = Field(default=None, description="""Control-system process-variable definitions.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    reference: Optional[_ReferenceElementBase] = Field(default=None, description="""Links to design drawings and files.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    name: str = Field(default=..., description="""Unique element name within the machine.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement', 'SectionLattice', 'MachineLayout']} })
    hardware_class: Optional[HardwareClassEnum] = Field(default=None, description="""Functional category (e.g., ``Magnet``, ``Diagnostic``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    hardware_type: Literal["ChargeDiagnostic"] = Field(default="ChargeDiagnostic", description="""Python class name used for MODEL_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.""", json_schema_extra = { "linkml_meta": {'designates_type': True,
         'domain_of': ['AcceleratorElement'],
         'equals_string': 'ChargeDiagnostic'} })
    hardware_model: Optional[str] = Field(default=None, description="""Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    machine_area: Optional[str] = Field(default=None, description="""Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    virtual_name: Optional[str] = Field(default=None, description="""Alternative internal name used by the control system when the physical name is inaccessible.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    alias: Optional[list[str]] = Field(default=None, description="""Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.""", json_schema_extra = { "linkml_meta": {'aliases': ['name_alias'], 'domain_of': ['AcceleratorElement']} })
    subelement: Optional[str] = Field(default=None, description="""If set, this element is a logical sub-component of the named parent element.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })


class _WallCurrentMonitorBase(_ChargeDiagnosticBase):
    """
    Wall-current monitor (WCM) for non-destructive charge measurement.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:WallCurrentMonitor',
         'from_schema': 'https://w3id.org/laura/schema',
         'slot_usage': {'hardware_type': {'equals_string': 'Wall_Current_Monitor',
                                          'name': 'hardware_type'}}})

    diagnostic: Optional[_ChargeDiagnosticElementBase] = Field(default=None, description="""Instrument-specific diagnostic parameters.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Diagnostic',
                       'BeamPositionMonitor',
                       'BeamArrivalMonitor',
                       'BunchLengthMonitor',
                       'Camera',
                       'Screen',
                       'ChargeDiagnostic'],
         'in_subset': ['diagnostic_properties']} })
    physical: Optional[_PhysicalElementBase] = Field(default=None, description="""Position, rotation, and length data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PhysicalAcceleratorElement'],
         'in_subset': ['physical_properties']} })
    simulation: Optional[_DiagnosticSimulationElementBase] = Field(default=None, description="""Simulation / tracking attributes.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    electrical: Optional[_ElectricalElementBase] = Field(default=None, description="""Power-supply electrical limits.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    manufacturer: Optional[_ManufacturerElementBase] = Field(default=None, description="""Manufacturer and serial-number data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ManufacturerElement', 'StandardElement']} })
    controls: Optional[_ControlsInformationBase] = Field(default=None, description="""Control-system process-variable definitions.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    reference: Optional[_ReferenceElementBase] = Field(default=None, description="""Links to design drawings and files.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    name: str = Field(default=..., description="""Unique element name within the machine.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement', 'SectionLattice', 'MachineLayout']} })
    hardware_class: Optional[HardwareClassEnum] = Field(default=None, description="""Functional category (e.g., ``Magnet``, ``Diagnostic``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    hardware_type: Literal["WallCurrentMonitor"] = Field(default="WallCurrentMonitor", description="""Python class name used for MODEL_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.""", json_schema_extra = { "linkml_meta": {'designates_type': True,
         'domain_of': ['AcceleratorElement'],
         'equals_string': 'Wall_Current_Monitor'} })
    hardware_model: Optional[str] = Field(default=None, description="""Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    machine_area: Optional[str] = Field(default=None, description="""Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    virtual_name: Optional[str] = Field(default=None, description="""Alternative internal name used by the control system when the physical name is inaccessible.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    alias: Optional[list[str]] = Field(default=None, description="""Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.""", json_schema_extra = { "linkml_meta": {'aliases': ['name_alias'], 'domain_of': ['AcceleratorElement']} })
    subelement: Optional[str] = Field(default=None, description="""If set, this element is a logical sub-component of the named parent element.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })


class _FaradayCupMonitorBase(_ChargeDiagnosticBase):
    """
    Faraday cup for destructive charge measurement.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:FaradayCupMonitor',
         'from_schema': 'https://w3id.org/laura/schema',
         'slot_usage': {'hardware_type': {'equals_string': 'Faraday_Cup_Monitor',
                                          'name': 'hardware_type'}}})

    diagnostic: Optional[_ChargeDiagnosticElementBase] = Field(default=None, description="""Instrument-specific diagnostic parameters.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Diagnostic',
                       'BeamPositionMonitor',
                       'BeamArrivalMonitor',
                       'BunchLengthMonitor',
                       'Camera',
                       'Screen',
                       'ChargeDiagnostic'],
         'in_subset': ['diagnostic_properties']} })
    physical: Optional[_PhysicalElementBase] = Field(default=None, description="""Position, rotation, and length data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PhysicalAcceleratorElement'],
         'in_subset': ['physical_properties']} })
    simulation: Optional[_DiagnosticSimulationElementBase] = Field(default=None, description="""Simulation / tracking attributes.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    electrical: Optional[_ElectricalElementBase] = Field(default=None, description="""Power-supply electrical limits.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    manufacturer: Optional[_ManufacturerElementBase] = Field(default=None, description="""Manufacturer and serial-number data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ManufacturerElement', 'StandardElement']} })
    controls: Optional[_ControlsInformationBase] = Field(default=None, description="""Control-system process-variable definitions.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    reference: Optional[_ReferenceElementBase] = Field(default=None, description="""Links to design drawings and files.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    name: str = Field(default=..., description="""Unique element name within the machine.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement', 'SectionLattice', 'MachineLayout']} })
    hardware_class: Optional[HardwareClassEnum] = Field(default=None, description="""Functional category (e.g., ``Magnet``, ``Diagnostic``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    hardware_type: Literal["FaradayCupMonitor"] = Field(default="FaradayCupMonitor", description="""Python class name used for MODEL_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.""", json_schema_extra = { "linkml_meta": {'designates_type': True,
         'domain_of': ['AcceleratorElement'],
         'equals_string': 'Faraday_Cup_Monitor'} })
    hardware_model: Optional[str] = Field(default=None, description="""Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    machine_area: Optional[str] = Field(default=None, description="""Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    virtual_name: Optional[str] = Field(default=None, description="""Alternative internal name used by the control system when the physical name is inaccessible.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    alias: Optional[list[str]] = Field(default=None, description="""Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.""", json_schema_extra = { "linkml_meta": {'aliases': ['name_alias'], 'domain_of': ['AcceleratorElement']} })
    subelement: Optional[str] = Field(default=None, description="""If set, this element is a logical sub-component of the named parent element.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })


class _IntegratedCurrentTransformerBase(_ChargeDiagnosticBase):
    """
    Integrated current transformer (ICT) for non-destructive single-shot charge measurement.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:IntegratedCurrentTransformer',
         'from_schema': 'https://w3id.org/laura/schema',
         'slot_usage': {'hardware_type': {'equals_string': 'Integrated_Current_Transformer',
                                          'name': 'hardware_type'}}})

    diagnostic: Optional[_ChargeDiagnosticElementBase] = Field(default=None, description="""Instrument-specific diagnostic parameters.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Diagnostic',
                       'BeamPositionMonitor',
                       'BeamArrivalMonitor',
                       'BunchLengthMonitor',
                       'Camera',
                       'Screen',
                       'ChargeDiagnostic'],
         'in_subset': ['diagnostic_properties']} })
    physical: Optional[_PhysicalElementBase] = Field(default=None, description="""Position, rotation, and length data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PhysicalAcceleratorElement'],
         'in_subset': ['physical_properties']} })
    simulation: Optional[_DiagnosticSimulationElementBase] = Field(default=None, description="""Simulation / tracking attributes.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    electrical: Optional[_ElectricalElementBase] = Field(default=None, description="""Power-supply electrical limits.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    manufacturer: Optional[_ManufacturerElementBase] = Field(default=None, description="""Manufacturer and serial-number data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ManufacturerElement', 'StandardElement']} })
    controls: Optional[_ControlsInformationBase] = Field(default=None, description="""Control-system process-variable definitions.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    reference: Optional[_ReferenceElementBase] = Field(default=None, description="""Links to design drawings and files.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    name: str = Field(default=..., description="""Unique element name within the machine.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement', 'SectionLattice', 'MachineLayout']} })
    hardware_class: Optional[HardwareClassEnum] = Field(default=None, description="""Functional category (e.g., ``Magnet``, ``Diagnostic``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    hardware_type: Literal["IntegratedCurrentTransformer"] = Field(default="IntegratedCurrentTransformer", description="""Python class name used for MODEL_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.""", json_schema_extra = { "linkml_meta": {'designates_type': True,
         'domain_of': ['AcceleratorElement'],
         'equals_string': 'Integrated_Current_Transformer'} })
    hardware_model: Optional[str] = Field(default=None, description="""Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    machine_area: Optional[str] = Field(default=None, description="""Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    virtual_name: Optional[str] = Field(default=None, description="""Alternative internal name used by the control system when the physical name is inaccessible.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    alias: Optional[list[str]] = Field(default=None, description="""Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.""", json_schema_extra = { "linkml_meta": {'aliases': ['name_alias'], 'domain_of': ['AcceleratorElement']} })
    subelement: Optional[str] = Field(default=None, description="""If set, this element is a logical sub-component of the named parent element.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })


class _RFCavityBase(_PhysicalAcceleratorElementBase):
    """
    Accelerating RF cavity.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:RFCavity',
         'from_schema': 'https://w3id.org/laura/schema',
         'slot_usage': {'hardware_type': {'equals_string': 'RFCavity',
                                          'name': 'hardware_type'},
                        'simulation': {'name': 'simulation',
                                       'range': 'RFCavitySimulationElement'}}})

    cavity: Optional[_RFCavityElementBase] = Field(default=None, description="""RF structure parameters.""", json_schema_extra = { "linkml_meta": {'domain_of': ['RFCavity', 'RFDeflectingCavity', 'Wakefield'],
         'in_subset': ['rf_properties']} })
    physical: Optional[_PhysicalElementBase] = Field(default=None, description="""Position, rotation, and length data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PhysicalAcceleratorElement'],
         'in_subset': ['physical_properties']} })
    simulation: Optional[_RFCavitySimulationElementBase] = Field(default=None, description="""Simulation / tracking attributes.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    electrical: Optional[_ElectricalElementBase] = Field(default=None, description="""Power-supply electrical limits.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    manufacturer: Optional[_ManufacturerElementBase] = Field(default=None, description="""Manufacturer and serial-number data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ManufacturerElement', 'StandardElement']} })
    controls: Optional[_ControlsInformationBase] = Field(default=None, description="""Control-system process-variable definitions.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    reference: Optional[_ReferenceElementBase] = Field(default=None, description="""Links to design drawings and files.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    name: str = Field(default=..., description="""Unique element name within the machine.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement', 'SectionLattice', 'MachineLayout']} })
    hardware_class: Optional[HardwareClassEnum] = Field(default=None, description="""Functional category (e.g., ``Magnet``, ``Diagnostic``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    hardware_type: Literal["RFCavity"] = Field(default="RFCavity", description="""Python class name used for MODEL_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.""", json_schema_extra = { "linkml_meta": {'designates_type': True,
         'domain_of': ['AcceleratorElement'],
         'equals_string': 'RFCavity'} })
    hardware_model: Optional[str] = Field(default=None, description="""Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    machine_area: Optional[str] = Field(default=None, description="""Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    virtual_name: Optional[str] = Field(default=None, description="""Alternative internal name used by the control system when the physical name is inaccessible.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    alias: Optional[list[str]] = Field(default=None, description="""Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.""", json_schema_extra = { "linkml_meta": {'aliases': ['name_alias'], 'domain_of': ['AcceleratorElement']} })
    subelement: Optional[str] = Field(default=None, description="""If set, this element is a logical sub-component of the named parent element.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })


class _RFDeflectingCavityBase(_RFCavityBase):
    """
    Transverse-deflecting (streak) RF cavity.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:RFDeflectingCavity',
         'from_schema': 'https://w3id.org/laura/schema',
         'slot_usage': {'hardware_type': {'equals_string': 'RFDeflectingCavity',
                                          'name': 'hardware_type'}}})

    cavity: Optional[_RFDeflectingCavityElementBase] = Field(default=None, description="""RF structure parameters.""", json_schema_extra = { "linkml_meta": {'domain_of': ['RFCavity', 'RFDeflectingCavity', 'Wakefield'],
         'in_subset': ['rf_properties']} })
    physical: Optional[_PhysicalElementBase] = Field(default=None, description="""Position, rotation, and length data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PhysicalAcceleratorElement'],
         'in_subset': ['physical_properties']} })
    simulation: Optional[_RFCavitySimulationElementBase] = Field(default=None, description="""Simulation / tracking attributes.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    electrical: Optional[_ElectricalElementBase] = Field(default=None, description="""Power-supply electrical limits.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    manufacturer: Optional[_ManufacturerElementBase] = Field(default=None, description="""Manufacturer and serial-number data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ManufacturerElement', 'StandardElement']} })
    controls: Optional[_ControlsInformationBase] = Field(default=None, description="""Control-system process-variable definitions.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    reference: Optional[_ReferenceElementBase] = Field(default=None, description="""Links to design drawings and files.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    name: str = Field(default=..., description="""Unique element name within the machine.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement', 'SectionLattice', 'MachineLayout']} })
    hardware_class: Optional[HardwareClassEnum] = Field(default=None, description="""Functional category (e.g., ``Magnet``, ``Diagnostic``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    hardware_type: Literal["RFDeflectingCavity"] = Field(default="RFDeflectingCavity", description="""Python class name used for MODEL_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.""", json_schema_extra = { "linkml_meta": {'designates_type': True,
         'domain_of': ['AcceleratorElement'],
         'equals_string': 'RFDeflectingCavity'} })
    hardware_model: Optional[str] = Field(default=None, description="""Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    machine_area: Optional[str] = Field(default=None, description="""Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    virtual_name: Optional[str] = Field(default=None, description="""Alternative internal name used by the control system when the physical name is inaccessible.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    alias: Optional[list[str]] = Field(default=None, description="""Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.""", json_schema_extra = { "linkml_meta": {'aliases': ['name_alias'], 'domain_of': ['AcceleratorElement']} })
    subelement: Optional[str] = Field(default=None, description="""If set, this element is a logical sub-component of the named parent element.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })


class _WakefieldBase(_PhysicalAcceleratorElementBase):
    """
    Passive wakefield structure (dielectric, corrugated, etc.).
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:Wakefield',
         'from_schema': 'https://w3id.org/laura/schema',
         'slot_usage': {'hardware_type': {'equals_string': 'Wakefield',
                                          'name': 'hardware_type'},
                        'simulation': {'name': 'simulation',
                                       'range': 'WakefieldSimulationElement'}}})

    cavity: Optional[_WakefieldElementBase] = Field(default=None, description="""Wakefield structure parameters.""", json_schema_extra = { "linkml_meta": {'domain_of': ['RFCavity', 'RFDeflectingCavity', 'Wakefield']} })
    physical: Optional[_PhysicalElementBase] = Field(default=None, description="""Position, rotation, and length data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PhysicalAcceleratorElement'],
         'in_subset': ['physical_properties']} })
    simulation: Optional[_WakefieldSimulationElementBase] = Field(default=None, description="""Simulation / tracking attributes.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    electrical: Optional[_ElectricalElementBase] = Field(default=None, description="""Power-supply electrical limits.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    manufacturer: Optional[_ManufacturerElementBase] = Field(default=None, description="""Manufacturer and serial-number data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ManufacturerElement', 'StandardElement']} })
    controls: Optional[_ControlsInformationBase] = Field(default=None, description="""Control-system process-variable definitions.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    reference: Optional[_ReferenceElementBase] = Field(default=None, description="""Links to design drawings and files.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    name: str = Field(default=..., description="""Unique element name within the machine.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement', 'SectionLattice', 'MachineLayout']} })
    hardware_class: Optional[HardwareClassEnum] = Field(default=None, description="""Functional category (e.g., ``Magnet``, ``Diagnostic``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    hardware_type: Literal["Wakefield"] = Field(default="Wakefield", description="""Python class name used for MODEL_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.""", json_schema_extra = { "linkml_meta": {'designates_type': True,
         'domain_of': ['AcceleratorElement'],
         'equals_string': 'Wakefield'} })
    hardware_model: Optional[str] = Field(default=None, description="""Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    machine_area: Optional[str] = Field(default=None, description="""Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    virtual_name: Optional[str] = Field(default=None, description="""Alternative internal name used by the control system when the physical name is inaccessible.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    alias: Optional[list[str]] = Field(default=None, description="""Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.""", json_schema_extra = { "linkml_meta": {'aliases': ['name_alias'], 'domain_of': ['AcceleratorElement']} })
    subelement: Optional[str] = Field(default=None, description="""If set, this element is a logical sub-component of the named parent element.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })


class _LowLevelRFBase(_StandardElementBase):
    """
    Low-level RF (LLRF) controller.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:LowLevelRF',
         'from_schema': 'https://w3id.org/laura/schema',
         'slot_usage': {'hardware_type': {'equals_string': 'Low_Level_RF',
                                          'name': 'hardware_type'}}})

    llrf: Optional[_LowLevelRFElementBase] = Field(default=None, description="""LLRF parameters.""", json_schema_extra = { "linkml_meta": {'domain_of': ['LowLevelRF']} })
    simulation: Optional[_SimulationElementBase] = Field(default=None, description="""Simulation / tracking attributes.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    electrical: Optional[_ElectricalElementBase] = Field(default=None, description="""Power-supply electrical limits.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    manufacturer: Optional[_ManufacturerElementBase] = Field(default=None, description="""Manufacturer and serial-number data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ManufacturerElement', 'StandardElement']} })
    controls: Optional[_ControlsInformationBase] = Field(default=None, description="""Control-system process-variable definitions.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    reference: Optional[_ReferenceElementBase] = Field(default=None, description="""Links to design drawings and files.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    name: str = Field(default=..., description="""Unique element name within the machine.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement', 'SectionLattice', 'MachineLayout']} })
    hardware_class: Optional[HardwareClassEnum] = Field(default=None, description="""Functional category (e.g., ``Magnet``, ``Diagnostic``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    hardware_type: Literal["LowLevelRF"] = Field(default="LowLevelRF", description="""Python class name used for MODEL_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.""", json_schema_extra = { "linkml_meta": {'designates_type': True,
         'domain_of': ['AcceleratorElement'],
         'equals_string': 'Low_Level_RF'} })
    hardware_model: Optional[str] = Field(default=None, description="""Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    machine_area: Optional[str] = Field(default=None, description="""Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    virtual_name: Optional[str] = Field(default=None, description="""Alternative internal name used by the control system when the physical name is inaccessible.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    alias: Optional[list[str]] = Field(default=None, description="""Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.""", json_schema_extra = { "linkml_meta": {'aliases': ['name_alias'], 'domain_of': ['AcceleratorElement']} })
    subelement: Optional[str] = Field(default=None, description="""If set, this element is a logical sub-component of the named parent element.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })


class _RFModulatorBase(_StandardElementBase):
    """
    RF modulator (klystron driver) element.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:RFModulator',
         'from_schema': 'https://w3id.org/laura/schema',
         'slot_usage': {'hardware_type': {'equals_string': 'RFModulator',
                                          'name': 'hardware_type'}}})

    modulator: Optional[_RFModulatorElementBase] = Field(default=None, description="""Modulator parameters.""", json_schema_extra = { "linkml_meta": {'domain_of': ['RFModulator']} })
    simulation: Optional[_SimulationElementBase] = Field(default=None, description="""Simulation / tracking attributes.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    electrical: Optional[_ElectricalElementBase] = Field(default=None, description="""Power-supply electrical limits.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    manufacturer: Optional[_ManufacturerElementBase] = Field(default=None, description="""Manufacturer and serial-number data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ManufacturerElement', 'StandardElement']} })
    controls: Optional[_ControlsInformationBase] = Field(default=None, description="""Control-system process-variable definitions.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    reference: Optional[_ReferenceElementBase] = Field(default=None, description="""Links to design drawings and files.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    name: str = Field(default=..., description="""Unique element name within the machine.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement', 'SectionLattice', 'MachineLayout']} })
    hardware_class: Optional[HardwareClassEnum] = Field(default=None, description="""Functional category (e.g., ``Magnet``, ``Diagnostic``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    hardware_type: Literal["RFModulator"] = Field(default="RFModulator", description="""Python class name used for MODEL_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.""", json_schema_extra = { "linkml_meta": {'designates_type': True,
         'domain_of': ['AcceleratorElement'],
         'equals_string': 'RFModulator'} })
    hardware_model: Optional[str] = Field(default=None, description="""Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    machine_area: Optional[str] = Field(default=None, description="""Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    virtual_name: Optional[str] = Field(default=None, description="""Alternative internal name used by the control system when the physical name is inaccessible.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    alias: Optional[list[str]] = Field(default=None, description="""Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.""", json_schema_extra = { "linkml_meta": {'aliases': ['name_alias'], 'domain_of': ['AcceleratorElement']} })
    subelement: Optional[str] = Field(default=None, description="""If set, this element is a logical sub-component of the named parent element.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })


class _RFProtectionBase(_StandardElementBase):
    """
    RF protection system element.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:RFProtection',
         'from_schema': 'https://w3id.org/laura/schema',
         'slot_usage': {'hardware_type': {'equals_string': 'RFProtection',
                                          'name': 'hardware_type'}}})

    protection: Optional[_RFProtectionElementBase] = Field(default=None, description="""RF protection parameters.""", json_schema_extra = { "linkml_meta": {'domain_of': ['RFProtection']} })
    simulation: Optional[_SimulationElementBase] = Field(default=None, description="""Simulation / tracking attributes.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    electrical: Optional[_ElectricalElementBase] = Field(default=None, description="""Power-supply electrical limits.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    manufacturer: Optional[_ManufacturerElementBase] = Field(default=None, description="""Manufacturer and serial-number data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ManufacturerElement', 'StandardElement']} })
    controls: Optional[_ControlsInformationBase] = Field(default=None, description="""Control-system process-variable definitions.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    reference: Optional[_ReferenceElementBase] = Field(default=None, description="""Links to design drawings and files.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    name: str = Field(default=..., description="""Unique element name within the machine.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement', 'SectionLattice', 'MachineLayout']} })
    hardware_class: Optional[HardwareClassEnum] = Field(default=None, description="""Functional category (e.g., ``Magnet``, ``Diagnostic``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    hardware_type: Literal["RFProtection"] = Field(default="RFProtection", description="""Python class name used for MODEL_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.""", json_schema_extra = { "linkml_meta": {'designates_type': True,
         'domain_of': ['AcceleratorElement'],
         'equals_string': 'RFProtection'} })
    hardware_model: Optional[str] = Field(default=None, description="""Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    machine_area: Optional[str] = Field(default=None, description="""Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    virtual_name: Optional[str] = Field(default=None, description="""Alternative internal name used by the control system when the physical name is inaccessible.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    alias: Optional[list[str]] = Field(default=None, description="""Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.""", json_schema_extra = { "linkml_meta": {'aliases': ['name_alias'], 'domain_of': ['AcceleratorElement']} })
    subelement: Optional[str] = Field(default=None, description="""If set, this element is a logical sub-component of the named parent element.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })


class _RFHeartbeatBase(_StandardElementBase):
    """
    RF timing heartbeat / signal-monitor element.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:RFHeartbeat',
         'from_schema': 'https://w3id.org/laura/schema',
         'slot_usage': {'hardware_type': {'equals_string': 'RFHeartbeat',
                                          'name': 'hardware_type'}}})

    heartbeat: Optional[_RFHeartbeatElementBase] = Field(default=None, description="""RF heartbeat parameters.""", json_schema_extra = { "linkml_meta": {'domain_of': ['RFHeartbeat']} })
    simulation: Optional[_SimulationElementBase] = Field(default=None, description="""Simulation / tracking attributes.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    electrical: Optional[_ElectricalElementBase] = Field(default=None, description="""Power-supply electrical limits.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    manufacturer: Optional[_ManufacturerElementBase] = Field(default=None, description="""Manufacturer and serial-number data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ManufacturerElement', 'StandardElement']} })
    controls: Optional[_ControlsInformationBase] = Field(default=None, description="""Control-system process-variable definitions.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    reference: Optional[_ReferenceElementBase] = Field(default=None, description="""Links to design drawings and files.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    name: str = Field(default=..., description="""Unique element name within the machine.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement', 'SectionLattice', 'MachineLayout']} })
    hardware_class: Optional[HardwareClassEnum] = Field(default=None, description="""Functional category (e.g., ``Magnet``, ``Diagnostic``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    hardware_type: Literal["RFHeartbeat"] = Field(default="RFHeartbeat", description="""Python class name used for MODEL_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.""", json_schema_extra = { "linkml_meta": {'designates_type': True,
         'domain_of': ['AcceleratorElement'],
         'equals_string': 'RFHeartbeat'} })
    hardware_model: Optional[str] = Field(default=None, description="""Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    machine_area: Optional[str] = Field(default=None, description="""Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    virtual_name: Optional[str] = Field(default=None, description="""Alternative internal name used by the control system when the physical name is inaccessible.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    alias: Optional[list[str]] = Field(default=None, description="""Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.""", json_schema_extra = { "linkml_meta": {'aliases': ['name_alias'], 'domain_of': ['AcceleratorElement']} })
    subelement: Optional[str] = Field(default=None, description="""If set, this element is a logical sub-component of the named parent element.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })


class _PIDBase(_StandardElementBase):
    """
    Proportional-integral-derivative (PID) feedback controller.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:PID',
         'from_schema': 'https://w3id.org/laura/schema',
         'slot_usage': {'hardware_type': {'equals_string': 'PID',
                                          'name': 'hardware_type'}}})

    pid: Optional[_PIDElementBase] = Field(default=None, description="""PID gain parameters.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PID']} })
    simulation: Optional[_SimulationElementBase] = Field(default=None, description="""Simulation / tracking attributes.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    electrical: Optional[_ElectricalElementBase] = Field(default=None, description="""Power-supply electrical limits.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    manufacturer: Optional[_ManufacturerElementBase] = Field(default=None, description="""Manufacturer and serial-number data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ManufacturerElement', 'StandardElement']} })
    controls: Optional[_ControlsInformationBase] = Field(default=None, description="""Control-system process-variable definitions.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    reference: Optional[_ReferenceElementBase] = Field(default=None, description="""Links to design drawings and files.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    name: str = Field(default=..., description="""Unique element name within the machine.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement', 'SectionLattice', 'MachineLayout']} })
    hardware_class: Optional[HardwareClassEnum] = Field(default=None, description="""Functional category (e.g., ``Magnet``, ``Diagnostic``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    hardware_type: Literal["PID"] = Field(default="PID", description="""Python class name used for MODEL_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.""", json_schema_extra = { "linkml_meta": {'designates_type': True,
         'domain_of': ['AcceleratorElement'],
         'equals_string': 'PID'} })
    hardware_model: Optional[str] = Field(default=None, description="""Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    machine_area: Optional[str] = Field(default=None, description="""Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    virtual_name: Optional[str] = Field(default=None, description="""Alternative internal name used by the control system when the physical name is inaccessible.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    alias: Optional[list[str]] = Field(default=None, description="""Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.""", json_schema_extra = { "linkml_meta": {'aliases': ['name_alias'], 'domain_of': ['AcceleratorElement']} })
    subelement: Optional[str] = Field(default=None, description="""If set, this element is a logical sub-component of the named parent element.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })


class _TwissMatchBase(_PhysicalAcceleratorElementBase):
    """
    Virtual Twiss-parameter matching point -- a zero-length marker that defines the desired optical functions at a location in the lattice.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:TwissMatch',
         'from_schema': 'https://w3id.org/laura/schema',
         'slot_usage': {'hardware_type': {'equals_string': 'TwissMatch',
                                          'name': 'hardware_type'},
                        'simulation': {'name': 'simulation',
                                       'range': 'TwissMatchSimulationElement'}}})

    physical: Optional[_PhysicalElementBase] = Field(default=None, description="""Position, rotation, and length data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PhysicalAcceleratorElement'],
         'in_subset': ['physical_properties']} })
    simulation: Optional[_TwissMatchSimulationElementBase] = Field(default=None, description="""Simulation / tracking attributes.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    electrical: Optional[_ElectricalElementBase] = Field(default=None, description="""Power-supply electrical limits.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    manufacturer: Optional[_ManufacturerElementBase] = Field(default=None, description="""Manufacturer and serial-number data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ManufacturerElement', 'StandardElement']} })
    controls: Optional[_ControlsInformationBase] = Field(default=None, description="""Control-system process-variable definitions.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    reference: Optional[_ReferenceElementBase] = Field(default=None, description="""Links to design drawings and files.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    name: str = Field(default=..., description="""Unique element name within the machine.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement', 'SectionLattice', 'MachineLayout']} })
    hardware_class: Optional[HardwareClassEnum] = Field(default=None, description="""Functional category (e.g., ``Magnet``, ``Diagnostic``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    hardware_type: Literal["TwissMatch"] = Field(default="TwissMatch", description="""Python class name used for MODEL_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.""", json_schema_extra = { "linkml_meta": {'designates_type': True,
         'domain_of': ['AcceleratorElement'],
         'equals_string': 'TwissMatch'} })
    hardware_model: Optional[str] = Field(default=None, description="""Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    machine_area: Optional[str] = Field(default=None, description="""Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    virtual_name: Optional[str] = Field(default=None, description="""Alternative internal name used by the control system when the physical name is inaccessible.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    alias: Optional[list[str]] = Field(default=None, description="""Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.""", json_schema_extra = { "linkml_meta": {'aliases': ['name_alias'], 'domain_of': ['AcceleratorElement']} })
    subelement: Optional[str] = Field(default=None, description="""If set, this element is a logical sub-component of the named parent element.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })


class _StageBase(_PhysicalAcceleratorElementBase):
    """
    Motorised positioning stage.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:Stage',
         'from_schema': 'https://w3id.org/laura/schema',
         'slot_usage': {'hardware_type': {'equals_string': 'Stage',
                                          'name': 'hardware_type'}}})

    physical: Optional[_PhysicalElementBase] = Field(default=None, description="""Position, rotation, and length data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PhysicalAcceleratorElement'],
         'in_subset': ['physical_properties']} })
    simulation: Optional[_SimulationElementBase] = Field(default=None, description="""Simulation / tracking attributes.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    electrical: Optional[_ElectricalElementBase] = Field(default=None, description="""Power-supply electrical limits.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    manufacturer: Optional[_ManufacturerElementBase] = Field(default=None, description="""Manufacturer and serial-number data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ManufacturerElement', 'StandardElement']} })
    controls: Optional[_ControlsInformationBase] = Field(default=None, description="""Control-system process-variable definitions.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    reference: Optional[_ReferenceElementBase] = Field(default=None, description="""Links to design drawings and files.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    name: str = Field(default=..., description="""Unique element name within the machine.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement', 'SectionLattice', 'MachineLayout']} })
    hardware_class: Optional[HardwareClassEnum] = Field(default=None, description="""Functional category (e.g., ``Magnet``, ``Diagnostic``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    hardware_type: Literal["Stage"] = Field(default="Stage", description="""Python class name used for MODEL_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.""", json_schema_extra = { "linkml_meta": {'designates_type': True,
         'domain_of': ['AcceleratorElement'],
         'equals_string': 'Stage'} })
    hardware_model: Optional[str] = Field(default=None, description="""Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    machine_area: Optional[str] = Field(default=None, description="""Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    virtual_name: Optional[str] = Field(default=None, description="""Alternative internal name used by the control system when the physical name is inaccessible.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    alias: Optional[list[str]] = Field(default=None, description="""Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.""", json_schema_extra = { "linkml_meta": {'aliases': ['name_alias'], 'domain_of': ['AcceleratorElement']} })
    subelement: Optional[str] = Field(default=None, description="""If set, this element is a logical sub-component of the named parent element.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })


class _VacuumGaugeBase(_PhysicalAcceleratorElementBase):
    """
    Vacuum-pressure gauge.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:VacuumGauge',
         'from_schema': 'https://w3id.org/laura/schema',
         'slot_usage': {'hardware_type': {'equals_string': 'VacuumGauge',
                                          'name': 'hardware_type'}}})

    physical: Optional[_PhysicalElementBase] = Field(default=None, description="""Position, rotation, and length data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PhysicalAcceleratorElement'],
         'in_subset': ['physical_properties']} })
    simulation: Optional[_SimulationElementBase] = Field(default=None, description="""Simulation / tracking attributes.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    electrical: Optional[_ElectricalElementBase] = Field(default=None, description="""Power-supply electrical limits.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    manufacturer: Optional[_ManufacturerElementBase] = Field(default=None, description="""Manufacturer and serial-number data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ManufacturerElement', 'StandardElement']} })
    controls: Optional[_ControlsInformationBase] = Field(default=None, description="""Control-system process-variable definitions.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    reference: Optional[_ReferenceElementBase] = Field(default=None, description="""Links to design drawings and files.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    name: str = Field(default=..., description="""Unique element name within the machine.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement', 'SectionLattice', 'MachineLayout']} })
    hardware_class: Optional[HardwareClassEnum] = Field(default=None, description="""Functional category (e.g., ``Magnet``, ``Diagnostic``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    hardware_type: Literal["VacuumGauge"] = Field(default="VacuumGauge", description="""Python class name used for MODEL_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.""", json_schema_extra = { "linkml_meta": {'designates_type': True,
         'domain_of': ['AcceleratorElement'],
         'equals_string': 'VacuumGauge'} })
    hardware_model: Optional[str] = Field(default=None, description="""Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    machine_area: Optional[str] = Field(default=None, description="""Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    virtual_name: Optional[str] = Field(default=None, description="""Alternative internal name used by the control system when the physical name is inaccessible.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    alias: Optional[list[str]] = Field(default=None, description="""Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.""", json_schema_extra = { "linkml_meta": {'aliases': ['name_alias'], 'domain_of': ['AcceleratorElement']} })
    subelement: Optional[str] = Field(default=None, description="""If set, this element is a logical sub-component of the named parent element.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })


class _LaserBase(_PhysicalAcceleratorElementBase):
    """
    Laser system element (full laser setup including beam parameters).
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:Laser',
         'from_schema': 'https://w3id.org/laura/schema',
         'in_subset': ['laser_properties'],
         'slot_usage': {'hardware_type': {'equals_string': 'Laser',
                                          'name': 'hardware_type'}}})

    laser: Optional[_LaserElementBase] = Field(default=None, description="""Laser-beam parameters.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Laser', 'Plasma', 'LaserEnergyMeter', 'LaserHalfWavePlate']} })
    physical: Optional[_PhysicalElementBase] = Field(default=None, description="""Position, rotation, and length data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PhysicalAcceleratorElement'],
         'in_subset': ['physical_properties']} })
    simulation: Optional[_SimulationElementBase] = Field(default=None, description="""Simulation / tracking attributes.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    electrical: Optional[_ElectricalElementBase] = Field(default=None, description="""Power-supply electrical limits.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    manufacturer: Optional[_ManufacturerElementBase] = Field(default=None, description="""Manufacturer and serial-number data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ManufacturerElement', 'StandardElement']} })
    controls: Optional[_ControlsInformationBase] = Field(default=None, description="""Control-system process-variable definitions.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    reference: Optional[_ReferenceElementBase] = Field(default=None, description="""Links to design drawings and files.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    name: str = Field(default=..., description="""Unique element name within the machine.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement', 'SectionLattice', 'MachineLayout']} })
    hardware_class: Optional[HardwareClassEnum] = Field(default=None, description="""Functional category (e.g., ``Magnet``, ``Diagnostic``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    hardware_type: Literal["Laser"] = Field(default="Laser", description="""Python class name used for MODEL_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.""", json_schema_extra = { "linkml_meta": {'designates_type': True,
         'domain_of': ['AcceleratorElement'],
         'equals_string': 'Laser'} })
    hardware_model: Optional[str] = Field(default=None, description="""Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    machine_area: Optional[str] = Field(default=None, description="""Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    virtual_name: Optional[str] = Field(default=None, description="""Alternative internal name used by the control system when the physical name is inaccessible.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    alias: Optional[list[str]] = Field(default=None, description="""Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.""", json_schema_extra = { "linkml_meta": {'aliases': ['name_alias'], 'domain_of': ['AcceleratorElement']} })
    subelement: Optional[str] = Field(default=None, description="""If set, this element is a logical sub-component of the named parent element.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })


class _ShutterBase(_PhysicalAcceleratorElementBase):
    """
    Beam or laser shutter with interlock logic.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:Shutter',
         'from_schema': 'https://w3id.org/laura/schema',
         'slot_usage': {'hardware_type': {'equals_string': 'Shutter',
                                          'name': 'hardware_type'}}})

    shutter: Optional[_ShutterElementBase] = Field(default=None, description="""Shutter interlock configuration.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Shutter']} })
    physical: Optional[_PhysicalElementBase] = Field(default=None, description="""Position, rotation, and length data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PhysicalAcceleratorElement'],
         'in_subset': ['physical_properties']} })
    simulation: Optional[_SimulationElementBase] = Field(default=None, description="""Simulation / tracking attributes.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    electrical: Optional[_ElectricalElementBase] = Field(default=None, description="""Power-supply electrical limits.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    manufacturer: Optional[_ManufacturerElementBase] = Field(default=None, description="""Manufacturer and serial-number data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ManufacturerElement', 'StandardElement']} })
    controls: Optional[_ControlsInformationBase] = Field(default=None, description="""Control-system process-variable definitions.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    reference: Optional[_ReferenceElementBase] = Field(default=None, description="""Links to design drawings and files.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    name: str = Field(default=..., description="""Unique element name within the machine.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement', 'SectionLattice', 'MachineLayout']} })
    hardware_class: Optional[HardwareClassEnum] = Field(default=None, description="""Functional category (e.g., ``Magnet``, ``Diagnostic``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    hardware_type: Literal["Shutter"] = Field(default="Shutter", description="""Python class name used for MODEL_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.""", json_schema_extra = { "linkml_meta": {'designates_type': True,
         'domain_of': ['AcceleratorElement'],
         'equals_string': 'Shutter'} })
    hardware_model: Optional[str] = Field(default=None, description="""Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    machine_area: Optional[str] = Field(default=None, description="""Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    virtual_name: Optional[str] = Field(default=None, description="""Alternative internal name used by the control system when the physical name is inaccessible.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    alias: Optional[list[str]] = Field(default=None, description="""Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.""", json_schema_extra = { "linkml_meta": {'aliases': ['name_alias'], 'domain_of': ['AcceleratorElement']} })
    subelement: Optional[str] = Field(default=None, description="""If set, this element is a logical sub-component of the named parent element.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })


class _ValveBase(_PhysicalAcceleratorElementBase):
    """
    Vacuum gate valve.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:Valve',
         'from_schema': 'https://w3id.org/laura/schema',
         'slot_usage': {'hardware_type': {'equals_string': 'Valve',
                                          'name': 'hardware_type'}}})

    valve: Optional[_ValveElementBase] = Field(default=None, description="""Valve configuration.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Valve']} })
    physical: Optional[_PhysicalElementBase] = Field(default=None, description="""Position, rotation, and length data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PhysicalAcceleratorElement'],
         'in_subset': ['physical_properties']} })
    simulation: Optional[_SimulationElementBase] = Field(default=None, description="""Simulation / tracking attributes.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    electrical: Optional[_ElectricalElementBase] = Field(default=None, description="""Power-supply electrical limits.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    manufacturer: Optional[_ManufacturerElementBase] = Field(default=None, description="""Manufacturer and serial-number data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ManufacturerElement', 'StandardElement']} })
    controls: Optional[_ControlsInformationBase] = Field(default=None, description="""Control-system process-variable definitions.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    reference: Optional[_ReferenceElementBase] = Field(default=None, description="""Links to design drawings and files.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    name: str = Field(default=..., description="""Unique element name within the machine.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement', 'SectionLattice', 'MachineLayout']} })
    hardware_class: Optional[HardwareClassEnum] = Field(default=None, description="""Functional category (e.g., ``Magnet``, ``Diagnostic``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    hardware_type: Literal["Valve"] = Field(default="Valve", description="""Python class name used for MODEL_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.""", json_schema_extra = { "linkml_meta": {'designates_type': True,
         'domain_of': ['AcceleratorElement'],
         'equals_string': 'Valve'} })
    hardware_model: Optional[str] = Field(default=None, description="""Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    machine_area: Optional[str] = Field(default=None, description="""Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    virtual_name: Optional[str] = Field(default=None, description="""Alternative internal name used by the control system when the physical name is inaccessible.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    alias: Optional[list[str]] = Field(default=None, description="""Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.""", json_schema_extra = { "linkml_meta": {'aliases': ['name_alias'], 'domain_of': ['AcceleratorElement']} })
    subelement: Optional[str] = Field(default=None, description="""If set, this element is a logical sub-component of the named parent element.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })


class _MarkerBase(_PhysicalAcceleratorElementBase):
    """
    Virtual survey marker -- a zero-length reference point used for alignment.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:Marker',
         'from_schema': 'https://w3id.org/laura/schema',
         'slot_usage': {'hardware_type': {'equals_string': 'Marker',
                                          'name': 'hardware_type'}}})

    physical: Optional[_PhysicalElementBase] = Field(default=None, description="""Position, rotation, and length data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PhysicalAcceleratorElement'],
         'in_subset': ['physical_properties']} })
    simulation: Optional[_SimulationElementBase] = Field(default=None, description="""Simulation / tracking attributes.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    electrical: Optional[_ElectricalElementBase] = Field(default=None, description="""Power-supply electrical limits.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    manufacturer: Optional[_ManufacturerElementBase] = Field(default=None, description="""Manufacturer and serial-number data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ManufacturerElement', 'StandardElement']} })
    controls: Optional[_ControlsInformationBase] = Field(default=None, description="""Control-system process-variable definitions.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    reference: Optional[_ReferenceElementBase] = Field(default=None, description="""Links to design drawings and files.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    name: str = Field(default=..., description="""Unique element name within the machine.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement', 'SectionLattice', 'MachineLayout']} })
    hardware_class: Optional[HardwareClassEnum] = Field(default=None, description="""Functional category (e.g., ``Magnet``, ``Diagnostic``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    hardware_type: Literal["Marker"] = Field(default="Marker", description="""Python class name used for MODEL_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.""", json_schema_extra = { "linkml_meta": {'designates_type': True,
         'domain_of': ['AcceleratorElement'],
         'equals_string': 'Marker'} })
    hardware_model: Optional[str] = Field(default=None, description="""Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    machine_area: Optional[str] = Field(default=None, description="""Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    virtual_name: Optional[str] = Field(default=None, description="""Alternative internal name used by the control system when the physical name is inaccessible.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    alias: Optional[list[str]] = Field(default=None, description="""Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.""", json_schema_extra = { "linkml_meta": {'aliases': ['name_alias'], 'domain_of': ['AcceleratorElement']} })
    subelement: Optional[str] = Field(default=None, description="""If set, this element is a logical sub-component of the named parent element.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })


class _ApertureBase(_PhysicalAcceleratorElementBase):
    """
    Mechanical aperture restriction in the beam pipe.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:Aperture',
         'from_schema': 'https://w3id.org/laura/schema',
         'slot_usage': {'hardware_type': {'equals_string': 'Aperture',
                                          'name': 'hardware_type'}}})

    aperture: Optional[_ApertureElementBase] = Field(default=None, description="""Aperture geometry parameters.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Aperture']} })
    physical: Optional[_PhysicalElementBase] = Field(default=None, description="""Position, rotation, and length data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PhysicalAcceleratorElement'],
         'in_subset': ['physical_properties']} })
    simulation: Optional[_SimulationElementBase] = Field(default=None, description="""Simulation / tracking attributes.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    electrical: Optional[_ElectricalElementBase] = Field(default=None, description="""Power-supply electrical limits.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    manufacturer: Optional[_ManufacturerElementBase] = Field(default=None, description="""Manufacturer and serial-number data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ManufacturerElement', 'StandardElement']} })
    controls: Optional[_ControlsInformationBase] = Field(default=None, description="""Control-system process-variable definitions.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    reference: Optional[_ReferenceElementBase] = Field(default=None, description="""Links to design drawings and files.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    name: str = Field(default=..., description="""Unique element name within the machine.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement', 'SectionLattice', 'MachineLayout']} })
    hardware_class: Optional[HardwareClassEnum] = Field(default=None, description="""Functional category (e.g., ``Magnet``, ``Diagnostic``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    hardware_type: Literal["Aperture"] = Field(default="Aperture", description="""Python class name used for MODEL_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.""", json_schema_extra = { "linkml_meta": {'designates_type': True,
         'domain_of': ['AcceleratorElement'],
         'equals_string': 'Aperture'} })
    hardware_model: Optional[str] = Field(default=None, description="""Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    machine_area: Optional[str] = Field(default=None, description="""Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    virtual_name: Optional[str] = Field(default=None, description="""Alternative internal name used by the control system when the physical name is inaccessible.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    alias: Optional[list[str]] = Field(default=None, description="""Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.""", json_schema_extra = { "linkml_meta": {'aliases': ['name_alias'], 'domain_of': ['AcceleratorElement']} })
    subelement: Optional[str] = Field(default=None, description="""If set, this element is a logical sub-component of the named parent element.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })


class _CollimatorBase(_ApertureBase):
    """
    Movable collimator jaw (extends Aperture).
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:Collimator',
         'from_schema': 'https://w3id.org/laura/schema',
         'slot_usage': {'hardware_type': {'equals_string': 'Collimator',
                                          'name': 'hardware_type'}}})

    aperture: Optional[_ApertureElementBase] = Field(default=None, description="""Aperture geometry parameters.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Aperture']} })
    physical: Optional[_PhysicalElementBase] = Field(default=None, description="""Position, rotation, and length data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PhysicalAcceleratorElement'],
         'in_subset': ['physical_properties']} })
    simulation: Optional[_SimulationElementBase] = Field(default=None, description="""Simulation / tracking attributes.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    electrical: Optional[_ElectricalElementBase] = Field(default=None, description="""Power-supply electrical limits.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    manufacturer: Optional[_ManufacturerElementBase] = Field(default=None, description="""Manufacturer and serial-number data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ManufacturerElement', 'StandardElement']} })
    controls: Optional[_ControlsInformationBase] = Field(default=None, description="""Control-system process-variable definitions.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    reference: Optional[_ReferenceElementBase] = Field(default=None, description="""Links to design drawings and files.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    name: str = Field(default=..., description="""Unique element name within the machine.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement', 'SectionLattice', 'MachineLayout']} })
    hardware_class: Optional[HardwareClassEnum] = Field(default=None, description="""Functional category (e.g., ``Magnet``, ``Diagnostic``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    hardware_type: Literal["Collimator"] = Field(default="Collimator", description="""Python class name used for MODEL_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.""", json_schema_extra = { "linkml_meta": {'designates_type': True,
         'domain_of': ['AcceleratorElement'],
         'equals_string': 'Collimator'} })
    hardware_model: Optional[str] = Field(default=None, description="""Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    machine_area: Optional[str] = Field(default=None, description="""Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    virtual_name: Optional[str] = Field(default=None, description="""Alternative internal name used by the control system when the physical name is inaccessible.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    alias: Optional[list[str]] = Field(default=None, description="""Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.""", json_schema_extra = { "linkml_meta": {'aliases': ['name_alias'], 'domain_of': ['AcceleratorElement']} })
    subelement: Optional[str] = Field(default=None, description="""If set, this element is a logical sub-component of the named parent element.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })


class _DriftBase(_PhysicalAcceleratorElementBase):
    """
    Field-free drift space between elements.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:Drift',
         'from_schema': 'https://w3id.org/laura/schema',
         'slot_usage': {'hardware_type': {'equals_string': 'Drift',
                                          'name': 'hardware_type'},
                        'simulation': {'name': 'simulation',
                                       'range': 'DriftSimulationElement'}}})

    physical: Optional[_PhysicalElementBase] = Field(default=None, description="""Position, rotation, and length data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PhysicalAcceleratorElement'],
         'in_subset': ['physical_properties']} })
    simulation: Optional[_DriftSimulationElementBase] = Field(default=None, description="""Simulation / tracking attributes.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    electrical: Optional[_ElectricalElementBase] = Field(default=None, description="""Power-supply electrical limits.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    manufacturer: Optional[_ManufacturerElementBase] = Field(default=None, description="""Manufacturer and serial-number data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ManufacturerElement', 'StandardElement']} })
    controls: Optional[_ControlsInformationBase] = Field(default=None, description="""Control-system process-variable definitions.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    reference: Optional[_ReferenceElementBase] = Field(default=None, description="""Links to design drawings and files.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    name: str = Field(default=..., description="""Unique element name within the machine.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement', 'SectionLattice', 'MachineLayout']} })
    hardware_class: Optional[HardwareClassEnum] = Field(default=None, description="""Functional category (e.g., ``Magnet``, ``Diagnostic``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    hardware_type: Literal["Drift"] = Field(default="Drift", description="""Python class name used for MODEL_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.""", json_schema_extra = { "linkml_meta": {'designates_type': True,
         'domain_of': ['AcceleratorElement'],
         'equals_string': 'Drift'} })
    hardware_model: Optional[str] = Field(default=None, description="""Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    machine_area: Optional[str] = Field(default=None, description="""Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    virtual_name: Optional[str] = Field(default=None, description="""Alternative internal name used by the control system when the physical name is inaccessible.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    alias: Optional[list[str]] = Field(default=None, description="""Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.""", json_schema_extra = { "linkml_meta": {'aliases': ['name_alias'], 'domain_of': ['AcceleratorElement']} })
    subelement: Optional[str] = Field(default=None, description="""If set, this element is a logical sub-component of the named parent element.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })


class _PlasmaBase(_PhysicalAcceleratorElementBase):
    """
    Laser-driven plasma-accelerator stage.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:Plasma',
         'from_schema': 'https://w3id.org/laura/schema',
         'slot_usage': {'hardware_type': {'equals_string': 'Plasma',
                                          'name': 'hardware_type'},
                        'simulation': {'name': 'simulation',
                                       'range': 'PlasmaSimulationElement'}}})

    plasma: Optional[_PlasmaElementBase] = Field(default=None, description="""Plasma channel parameters.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Plasma']} })
    laser: Optional[_LaserElementBase] = Field(default=None, description="""Laser driving the plasma stage.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Laser', 'Plasma', 'LaserEnergyMeter', 'LaserHalfWavePlate']} })
    physical: Optional[_PhysicalElementBase] = Field(default=None, description="""Position, rotation, and length data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PhysicalAcceleratorElement'],
         'in_subset': ['physical_properties']} })
    simulation: Optional[_PlasmaSimulationElementBase] = Field(default=None, description="""Simulation / tracking attributes.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    electrical: Optional[_ElectricalElementBase] = Field(default=None, description="""Power-supply electrical limits.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    manufacturer: Optional[_ManufacturerElementBase] = Field(default=None, description="""Manufacturer and serial-number data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ManufacturerElement', 'StandardElement']} })
    controls: Optional[_ControlsInformationBase] = Field(default=None, description="""Control-system process-variable definitions.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    reference: Optional[_ReferenceElementBase] = Field(default=None, description="""Links to design drawings and files.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    name: str = Field(default=..., description="""Unique element name within the machine.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement', 'SectionLattice', 'MachineLayout']} })
    hardware_class: Optional[HardwareClassEnum] = Field(default=None, description="""Functional category (e.g., ``Magnet``, ``Diagnostic``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    hardware_type: Literal["Plasma"] = Field(default="Plasma", description="""Python class name used for MODEL_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.""", json_schema_extra = { "linkml_meta": {'designates_type': True,
         'domain_of': ['AcceleratorElement'],
         'equals_string': 'Plasma'} })
    hardware_model: Optional[str] = Field(default=None, description="""Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    machine_area: Optional[str] = Field(default=None, description="""Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    virtual_name: Optional[str] = Field(default=None, description="""Alternative internal name used by the control system when the physical name is inaccessible.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    alias: Optional[list[str]] = Field(default=None, description="""Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.""", json_schema_extra = { "linkml_meta": {'aliases': ['name_alias'], 'domain_of': ['AcceleratorElement']} })
    subelement: Optional[str] = Field(default=None, description="""If set, this element is a logical sub-component of the named parent element.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })


class _LaserEnergyMeterBase(_StandardElementBase):
    """
    Laser pulse-energy diagnostic (photodiode / pyroelectric).
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:LaserEnergyMeter',
         'from_schema': 'https://w3id.org/laura/schema',
         'in_subset': ['laser_properties'],
         'slot_usage': {'hardware_type': {'equals_string': 'LaserEnergyMeter',
                                          'name': 'hardware_type'}}})

    laser: Optional[_LaserEnergyMeterElementBase] = Field(default=None, description="""Energy-meter instrument parameters.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Laser', 'Plasma', 'LaserEnergyMeter', 'LaserHalfWavePlate']} })
    simulation: Optional[_SimulationElementBase] = Field(default=None, description="""Simulation / tracking attributes.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    electrical: Optional[_ElectricalElementBase] = Field(default=None, description="""Power-supply electrical limits.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    manufacturer: Optional[_ManufacturerElementBase] = Field(default=None, description="""Manufacturer and serial-number data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ManufacturerElement', 'StandardElement']} })
    controls: Optional[_ControlsInformationBase] = Field(default=None, description="""Control-system process-variable definitions.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    reference: Optional[_ReferenceElementBase] = Field(default=None, description="""Links to design drawings and files.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    name: str = Field(default=..., description="""Unique element name within the machine.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement', 'SectionLattice', 'MachineLayout']} })
    hardware_class: Optional[HardwareClassEnum] = Field(default=None, description="""Functional category (e.g., ``Magnet``, ``Diagnostic``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    hardware_type: Literal["LaserEnergyMeter"] = Field(default="LaserEnergyMeter", description="""Python class name used for MODEL_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.""", json_schema_extra = { "linkml_meta": {'designates_type': True,
         'domain_of': ['AcceleratorElement'],
         'equals_string': 'LaserEnergyMeter'} })
    hardware_model: Optional[str] = Field(default=None, description="""Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    machine_area: Optional[str] = Field(default=None, description="""Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    virtual_name: Optional[str] = Field(default=None, description="""Alternative internal name used by the control system when the physical name is inaccessible.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    alias: Optional[list[str]] = Field(default=None, description="""Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.""", json_schema_extra = { "linkml_meta": {'aliases': ['name_alias'], 'domain_of': ['AcceleratorElement']} })
    subelement: Optional[str] = Field(default=None, description="""If set, this element is a logical sub-component of the named parent element.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })


class _LaserHalfWavePlateBase(_StandardElementBase):
    """
    Half-wave plate for laser polarisation rotation.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:LaserHalfWavePlate',
         'from_schema': 'https://w3id.org/laura/schema',
         'in_subset': ['laser_properties'],
         'slot_usage': {'hardware_type': {'equals_string': 'LaserHalfWavePlate',
                                          'name': 'hardware_type'}}})

    laser: Optional[_LaserHalfWavePlateElementBase] = Field(default=None, description="""Half-wave plate parameters.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Laser', 'Plasma', 'LaserEnergyMeter', 'LaserHalfWavePlate']} })
    simulation: Optional[_SimulationElementBase] = Field(default=None, description="""Simulation / tracking attributes.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    electrical: Optional[_ElectricalElementBase] = Field(default=None, description="""Power-supply electrical limits.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    manufacturer: Optional[_ManufacturerElementBase] = Field(default=None, description="""Manufacturer and serial-number data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ManufacturerElement', 'StandardElement']} })
    controls: Optional[_ControlsInformationBase] = Field(default=None, description="""Control-system process-variable definitions.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    reference: Optional[_ReferenceElementBase] = Field(default=None, description="""Links to design drawings and files.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    name: str = Field(default=..., description="""Unique element name within the machine.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement', 'SectionLattice', 'MachineLayout']} })
    hardware_class: Optional[HardwareClassEnum] = Field(default=None, description="""Functional category (e.g., ``Magnet``, ``Diagnostic``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    hardware_type: Literal["LaserHalfWavePlate"] = Field(default="LaserHalfWavePlate", description="""Python class name used for MODEL_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.""", json_schema_extra = { "linkml_meta": {'designates_type': True,
         'domain_of': ['AcceleratorElement'],
         'equals_string': 'LaserHalfWavePlate'} })
    hardware_model: Optional[str] = Field(default=None, description="""Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    machine_area: Optional[str] = Field(default=None, description="""Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    virtual_name: Optional[str] = Field(default=None, description="""Alternative internal name used by the control system when the physical name is inaccessible.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    alias: Optional[list[str]] = Field(default=None, description="""Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.""", json_schema_extra = { "linkml_meta": {'aliases': ['name_alias'], 'domain_of': ['AcceleratorElement']} })
    subelement: Optional[str] = Field(default=None, description="""If set, this element is a logical sub-component of the named parent element.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })


class _LaserMirrorBase(_StandardElementBase):
    """
    Laser steering or focusing mirror.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:LaserMirror',
         'from_schema': 'https://w3id.org/laura/schema',
         'in_subset': ['laser_properties'],
         'slot_usage': {'hardware_type': {'equals_string': 'LaserMirror',
                                          'name': 'hardware_type'}}})

    simulation: Optional[_SimulationElementBase] = Field(default=None, description="""Simulation / tracking attributes.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    electrical: Optional[_ElectricalElementBase] = Field(default=None, description="""Power-supply electrical limits.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    manufacturer: Optional[_ManufacturerElementBase] = Field(default=None, description="""Manufacturer and serial-number data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ManufacturerElement', 'StandardElement']} })
    controls: Optional[_ControlsInformationBase] = Field(default=None, description="""Control-system process-variable definitions.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    reference: Optional[_ReferenceElementBase] = Field(default=None, description="""Links to design drawings and files.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    name: str = Field(default=..., description="""Unique element name within the machine.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement', 'SectionLattice', 'MachineLayout']} })
    hardware_class: Optional[HardwareClassEnum] = Field(default=None, description="""Functional category (e.g., ``Magnet``, ``Diagnostic``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    hardware_type: Literal["LaserMirror"] = Field(default="LaserMirror", description="""Python class name used for MODEL_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.""", json_schema_extra = { "linkml_meta": {'designates_type': True,
         'domain_of': ['AcceleratorElement'],
         'equals_string': 'LaserMirror'} })
    hardware_model: Optional[str] = Field(default=None, description="""Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    machine_area: Optional[str] = Field(default=None, description="""Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    virtual_name: Optional[str] = Field(default=None, description="""Alternative internal name used by the control system when the physical name is inaccessible.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    alias: Optional[list[str]] = Field(default=None, description="""Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.""", json_schema_extra = { "linkml_meta": {'aliases': ['name_alias'], 'domain_of': ['AcceleratorElement']} })
    subelement: Optional[str] = Field(default=None, description="""If set, this element is a logical sub-component of the named parent element.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })


class _LaserAttenuatorBase(_StandardElementBase):
    """
    Laser power attenuator (waveplate + polariser combination).
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:LaserAttenuator',
         'from_schema': 'https://w3id.org/laura/schema',
         'in_subset': ['laser_properties'],
         'slot_usage': {'hardware_type': {'equals_string': 'LaserAttenuator',
                                          'name': 'hardware_type'}}})

    maximum: Optional[float] = Field(default=None, description="""Maximum attenuation angle [deg].""", json_schema_extra = { "linkml_meta": {'domain_of': ['LaserAttenuator'], 'unit': {'ucum_code': 'deg'}} })
    minimum: Optional[float] = Field(default=None, description="""Minimum attenuation angle [deg].""", json_schema_extra = { "linkml_meta": {'domain_of': ['LaserAttenuator'], 'unit': {'ucum_code': 'deg'}} })
    simulation: Optional[_SimulationElementBase] = Field(default=None, description="""Simulation / tracking attributes.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    electrical: Optional[_ElectricalElementBase] = Field(default=None, description="""Power-supply electrical limits.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    manufacturer: Optional[_ManufacturerElementBase] = Field(default=None, description="""Manufacturer and serial-number data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ManufacturerElement', 'StandardElement']} })
    controls: Optional[_ControlsInformationBase] = Field(default=None, description="""Control-system process-variable definitions.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    reference: Optional[_ReferenceElementBase] = Field(default=None, description="""Links to design drawings and files.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    name: str = Field(default=..., description="""Unique element name within the machine.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement', 'SectionLattice', 'MachineLayout']} })
    hardware_class: Optional[HardwareClassEnum] = Field(default=None, description="""Functional category (e.g., ``Magnet``, ``Diagnostic``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    hardware_type: Literal["LaserAttenuator"] = Field(default="LaserAttenuator", description="""Python class name used for MODEL_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.""", json_schema_extra = { "linkml_meta": {'designates_type': True,
         'domain_of': ['AcceleratorElement'],
         'equals_string': 'LaserAttenuator'} })
    hardware_model: Optional[str] = Field(default=None, description="""Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    machine_area: Optional[str] = Field(default=None, description="""Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    virtual_name: Optional[str] = Field(default=None, description="""Alternative internal name used by the control system when the physical name is inaccessible.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    alias: Optional[list[str]] = Field(default=None, description="""Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.""", json_schema_extra = { "linkml_meta": {'aliases': ['name_alias'], 'domain_of': ['AcceleratorElement']} })
    subelement: Optional[str] = Field(default=None, description="""If set, this element is a logical sub-component of the named parent element.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })


class _LightingBase(_StandardElementBase):
    """
    Experimental-hall lighting element.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:Lighting',
         'from_schema': 'https://w3id.org/laura/schema',
         'slot_usage': {'hardware_type': {'equals_string': 'Lighting',
                                          'name': 'hardware_type'}}})

    lights: Optional[_LightingElementBase] = Field(default=None, description="""Lighting configuration.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Lighting']} })
    simulation: Optional[_SimulationElementBase] = Field(default=None, description="""Simulation / tracking attributes.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    electrical: Optional[_ElectricalElementBase] = Field(default=None, description="""Power-supply electrical limits.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    manufacturer: Optional[_ManufacturerElementBase] = Field(default=None, description="""Manufacturer and serial-number data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ManufacturerElement', 'StandardElement']} })
    controls: Optional[_ControlsInformationBase] = Field(default=None, description="""Control-system process-variable definitions.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    reference: Optional[_ReferenceElementBase] = Field(default=None, description="""Links to design drawings and files.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    name: str = Field(default=..., description="""Unique element name within the machine.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement', 'SectionLattice', 'MachineLayout']} })
    hardware_class: Optional[HardwareClassEnum] = Field(default=None, description="""Functional category (e.g., ``Magnet``, ``Diagnostic``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    hardware_type: Literal["Lighting"] = Field(default="Lighting", description="""Python class name used for MODEL_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.""", json_schema_extra = { "linkml_meta": {'designates_type': True,
         'domain_of': ['AcceleratorElement'],
         'equals_string': 'Lighting'} })
    hardware_model: Optional[str] = Field(default=None, description="""Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    machine_area: Optional[str] = Field(default=None, description="""Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    virtual_name: Optional[str] = Field(default=None, description="""Alternative internal name used by the control system when the physical name is inaccessible.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    alias: Optional[list[str]] = Field(default=None, description="""Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.""", json_schema_extra = { "linkml_meta": {'aliases': ['name_alias'], 'domain_of': ['AcceleratorElement']} })
    subelement: Optional[str] = Field(default=None, description="""If set, this element is a logical sub-component of the named parent element.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })


class _SectionLatticeBase(ConfiguredBaseModel):
    """
    An ordered list of element names defining a contiguous beamline section.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:SectionLattice',
         'from_schema': 'https://w3id.org/laura/schema'})

    name: str = Field(default=..., description="""Unique section name.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement', 'SectionLattice', 'MachineLayout']} })
    master_lattice: Optional[str] = Field(default=None, description="""Name of the master lattice this section belongs to.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SectionLattice', 'MachineLayout']} })
    elements: Optional[list[str]] = Field(default=None, description="""Ordered list of element names in this section.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SectionLattice', 'MachineModel']} })


class _MachineLayoutBase(ConfiguredBaseModel):
    """
    An ordered list of section names defining a beamline layout (a contiguous sequence of sections).
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:MachineLayout',
         'from_schema': 'https://w3id.org/laura/schema'})

    name: str = Field(default=..., description="""Unique layout name.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement', 'SectionLattice', 'MachineLayout']} })
    master_lattice: Optional[str] = Field(default=None, description="""Name of the master lattice this layout belongs to.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SectionLattice', 'MachineLayout']} })
    sections: Optional[list[str]] = Field(default=None, description="""Ordered list of section names.""", json_schema_extra = { "linkml_meta": {'domain_of': ['MachineLayout', 'MachineModel']} })


class _MachineModelBase(ConfiguredBaseModel):
    """
    Top-level container for a complete accelerator lattice: elements, sections, layouts, and named lattice configurations.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:MachineModel',
         'from_schema': 'https://w3id.org/laura/schema'})

    elements: Optional[list[str]] = Field(default=None, description="""All elements in the machine, keyed by name.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SectionLattice', 'MachineModel']} })
    sections: Optional[list[str]] = Field(default=None, description="""All named beamline sections.""", json_schema_extra = { "linkml_meta": {'domain_of': ['MachineLayout', 'MachineModel']} })
    layouts: Optional[list[str]] = Field(default=None, description="""All named beamline layouts.""", json_schema_extra = { "linkml_meta": {'domain_of': ['MachineModel']} })


# Model rebuild
# see https://pydantic-docs.helpmanual.io/usage/models/#rebuilding-a-model
_PositionBase.model_rebuild()
_RotationBase.model_rebuild()
_ElementPositionErrorBase.model_rebuild()
_ElementSurveyBase.model_rebuild()
_PhysicalElementBase.model_rebuild()
_ElectricalElementBase.model_rebuild()
_ManufacturerElementBase.model_rebuild()
_ReferenceElementBase.model_rebuild()
_ControlVariableBase.model_rebuild()
_ControlsInformationBase.model_rebuild()
_SimulationElementBase.model_rebuild()
_MagnetSimulationElementBase.model_rebuild()
_RFCavitySimulationElementBase.model_rebuild()
_WakefieldSimulationElementBase.model_rebuild()
_DriftSimulationElementBase.model_rebuild()
_DiagnosticSimulationElementBase.model_rebuild()
_PlasmaSimulationElementBase.model_rebuild()
_TwissMatchSimulationElementBase.model_rebuild()
_MultipoleBase.model_rebuild()
_MultipolesBase.model_rebuild()
_FieldIntegralBase.model_rebuild()
_LinearSaturationFitBase.model_rebuild()
_MagneticElementBase.model_rebuild()
_ApertureElementBase.model_rebuild()
_RFCavityElementBase.model_rebuild()
_WakefieldElementBase.model_rebuild()
_RFDeflectingCavityElementBase.model_rebuild()
_PIDElementBase.model_rebuild()
_LowLevelRFElementBase.model_rebuild()
_RFModulatorElementBase.model_rebuild()
_RFProtectionElementBase.model_rebuild()
_RFHeartbeatElementBase.model_rebuild()
_DiagnosticElementBase.model_rebuild()
_BPMDiagnosticElementBase.model_rebuild()
_BAMDiagnosticElementBase.model_rebuild()
_BLMDiagnosticElementBase.model_rebuild()
_ScreenDiagnosticElementBase.model_rebuild()
_ChargeDiagnosticElementBase.model_rebuild()
_CameraDiagnosticElementBase.model_rebuild()
_LaserElementBase.model_rebuild()
_LaserEnergyMeterElementBase.model_rebuild()
_LaserHalfWavePlateElementBase.model_rebuild()
_PlasmaElementBase.model_rebuild()
_ShutterElementBase.model_rebuild()
_ValveElementBase.model_rebuild()
_LightingElementBase.model_rebuild()
_DegaussableElementBase.model_rebuild()
_AcceleratorElementBase.model_rebuild()
_StandardElementBase.model_rebuild()
_PhysicalAcceleratorElementBase.model_rebuild()
_MagnetBaseElementBase.model_rebuild()
_DipoleBase.model_rebuild()
_QuadrupoleBase.model_rebuild()
_SextupoleBase.model_rebuild()
_OctupoleBase.model_rebuild()
_HorizontalCorrectorBase.model_rebuild()
_VerticalCorrectorBase.model_rebuild()
_CombinedCorrectorBase.model_rebuild()
_SolenoidBase.model_rebuild()
_NonLinearLensBase.model_rebuild()
_WigglerBase.model_rebuild()
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
_RFCavityBase.model_rebuild()
_RFDeflectingCavityBase.model_rebuild()
_WakefieldBase.model_rebuild()
_LowLevelRFBase.model_rebuild()
_RFModulatorBase.model_rebuild()
_RFProtectionBase.model_rebuild()
_RFHeartbeatBase.model_rebuild()
_PIDBase.model_rebuild()
_TwissMatchBase.model_rebuild()
_StageBase.model_rebuild()
_VacuumGaugeBase.model_rebuild()
_LaserBase.model_rebuild()
_ShutterBase.model_rebuild()
_ValveBase.model_rebuild()
_MarkerBase.model_rebuild()
_ApertureBase.model_rebuild()
_CollimatorBase.model_rebuild()
_DriftBase.model_rebuild()
_PlasmaBase.model_rebuild()
_LaserEnergyMeterBase.model_rebuild()
_LaserHalfWavePlateBase.model_rebuild()
_LaserMirrorBase.model_rebuild()
_LaserAttenuatorBase.model_rebuild()
_LightingBase.model_rebuild()
_SectionLatticeBase.model_rebuild()
_MachineLayoutBase.model_rebuild()
_MachineModelBase.model_rebuild()
