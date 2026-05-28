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
     'description': 'Linked Data schema for the LAURA (Lattice And Unified '
                    'Representation of Accelerators) accelerator element model.  '
                    'Covers all element types, their physical, magnetic, '
                    'diagnostic, RF, and control-system properties.',
     'id': 'https://w3id.org/laura/schema',
     'imports': ['linkml:types',
                 'simulation',
                 'magnetic',
                 'rf',
                 'diagnostics',
                 'laser_plasma'],
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



class _SimulationElementBase(ConfiguredBaseModel):
    """
    Base simulation attributes: field-map files and reference positions for tracking codes.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:SimulationElement',
         'from_schema': 'https://w3id.org/laura/schema/simulation'})

    field_definition: Optional[str] = Field(default=None, description="""Path to the 3-D field-map file.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SimulationElement']} })
    wakefield_definition: Optional[str] = Field(default=None, description="""Path to the wakefield impedance file.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SimulationElement']} })
    field_reference_position: Optional[str] = Field(default=None, description="""Longitudinal origin of the field map [m].""", json_schema_extra = { "linkml_meta": {'domain_of': ['SimulationElement']} })
    scale_field: float = Field(default=1, description="""Multiplicative scale factor applied to the field map.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SimulationElement'], 'ifabsent': 'float(1)'} })


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
    field_amplitude: Optional[float] = Field(default=0.0, description="""Field amplitude scaling for magnet tracking.""", json_schema_extra = { "linkml_meta": {'domain_of': ['MagnetSimulationElement', 'RFCavitySimulationElement'],
         'ifabsent': 'float(0.0)'} })
    n_slices: int = Field(default=4, description="""Number of longitudinal slices for thick-lens tracking.""", ge=1, json_schema_extra = { "linkml_meta": {'domain_of': ['MagnetSimulationElement'], 'ifabsent': 'int(4)'} })
    smooth: Optional[bool] = Field(default=None, description="""Use a smoothed field profile.""", json_schema_extra = { "linkml_meta": {'domain_of': ['MagnetSimulationElement',
                       'RFCavitySimulationElement',
                       'WakefieldSimulationElement']} })
    edge_field_integral: float = Field(default=0.5, description="""Fringe-field integral for edge focussing.""", json_schema_extra = { "linkml_meta": {'domain_of': ['MagnetSimulationElement', 'MagneticElement'],
         'ifabsent': 'float(0.5)'} })
    edge1_effects: Optional[bool] = Field(default=None, description="""Enable entrance-edge focussing effects.""", json_schema_extra = { "linkml_meta": {'domain_of': ['MagnetSimulationElement']} })
    edge2_effects: Optional[bool] = Field(default=None, description="""Enable exit-edge focussing effects.""", json_schema_extra = { "linkml_meta": {'domain_of': ['MagnetSimulationElement']} })
    sr_enable: Optional[bool] = Field(default=True, description="""Enable synchrotron-radiation energy loss.""", json_schema_extra = { "linkml_meta": {'domain_of': ['MagnetSimulationElement'], 'ifabsent': 'True'} })
    isr_enable: Optional[bool] = Field(default=True, description="""Enable incoherent synchrotron-radiation emittance growth.""", json_schema_extra = { "linkml_meta": {'domain_of': ['MagnetSimulationElement'], 'ifabsent': 'True'} })
    csr_enable: Optional[bool] = Field(default=True, description="""Enable coherent synchrotron radiation.""", json_schema_extra = { "linkml_meta": {'domain_of': ['MagnetSimulationElement', 'DriftSimulationElement'],
         'ifabsent': 'True'} })
    csr_bins: int = Field(default=100, description="""Number of longitudinal bins for the CSR mesh.""", json_schema_extra = { "linkml_meta": {'domain_of': ['MagnetSimulationElement'], 'ifabsent': 'int(100)'} })
    integration_order: int = Field(default=4, description="""Order of the symplectic integrator.""", json_schema_extra = { "linkml_meta": {'domain_of': ['MagnetSimulationElement'], 'ifabsent': 'int(4)'} })
    nonlinear: Optional[bool] = Field(default=None, description="""Include higher-order (sextupole+) field components.""", json_schema_extra = { "linkml_meta": {'domain_of': ['MagnetSimulationElement']} })
    smoothing_half_width: int = Field(default=1, description="""Half-width of the current-profile smoothing kernel.""", json_schema_extra = { "linkml_meta": {'domain_of': ['MagnetSimulationElement'], 'ifabsent': 'int(1)'} })
    edge_order: int = Field(default=2, description="""Polynomial order of the edge-field expansion.""", json_schema_extra = { "linkml_meta": {'domain_of': ['MagnetSimulationElement'], 'ifabsent': 'int(2)'} })
    deltaL: float = Field(default=0.0, description="""Longitudinal step-size override for thick-lens integration [m].""", json_schema_extra = { "linkml_meta": {'domain_of': ['MagnetSimulationElement'],
         'ifabsent': 'float(0.0)',
         'unit': {'ucum_code': 'm'}} })
    smooth_points: float = Field(default=2, description="""Number of points used to smooth the field map [ASTRA].""", json_schema_extra = { "linkml_meta": {'domain_of': ['MagnetSimulationElement'], 'ifabsent': 'float(2)'} })
    field_definition: Optional[str] = Field(default=None, description="""Path to the 3-D field-map file.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SimulationElement']} })
    wakefield_definition: Optional[str] = Field(default=None, description="""Path to the wakefield impedance file.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SimulationElement']} })
    field_reference_position: Optional[str] = Field(default=None, description="""Longitudinal origin of the field map [m].""", json_schema_extra = { "linkml_meta": {'domain_of': ['SimulationElement']} })
    scale_field: float = Field(default=1, description="""Multiplicative scale factor applied to the field map.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SimulationElement'], 'ifabsent': 'float(1)'} })


class _RFCavitySimulationElementBase(_SimulationElementBase):
    """
    Simulation attributes for RF cavity elements.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:RFCavitySimulationElement',
         'from_schema': 'https://w3id.org/laura/schema/simulation',
         'slot_usage': {'field_amplitude': {'description': 'Cavity field amplitude.',
                                            'ifabsent': 'float(0)',
                                            'name': 'field_amplitude'},
                        'lsc_bins': {'description': 'Number of longitudinal '
                                                    'space-charge bins.',
                                     'ifabsent': 'int(100)',
                                     'name': 'lsc_bins'},
                        'n_kicks': {'description': 'Number of cavity kicks to apply.',
                                    'ifabsent': 'int(0)',
                                    'name': 'n_kicks'}}})

    t_column: Optional[str] = Field(default=None, description="""Time column in the wake file.""", json_schema_extra = { "linkml_meta": {'domain_of': ['RFCavitySimulationElement', 'WakefieldSimulationElement']} })
    z_column: Optional[str] = Field(default=None, description="""Longitudinal position column in the wake file.""", json_schema_extra = { "linkml_meta": {'domain_of': ['RFCavitySimulationElement', 'WakefieldSimulationElement']} })
    wx_column: Optional[str] = Field(default=None, description="""Horizontal wake column in the wake file.""", json_schema_extra = { "linkml_meta": {'domain_of': ['RFCavitySimulationElement', 'WakefieldSimulationElement']} })
    wy_column: Optional[str] = Field(default=None, description="""Vertical wake column in the wake file.""", json_schema_extra = { "linkml_meta": {'domain_of': ['RFCavitySimulationElement', 'WakefieldSimulationElement']} })
    wz_column: Optional[str] = Field(default=None, description="""Longitudinal wake column in the wake file.""", json_schema_extra = { "linkml_meta": {'domain_of': ['RFCavitySimulationElement', 'WakefieldSimulationElement']} })
    n_kicks: Optional[int] = Field(default=0, description="""Number of cavity kicks to apply.""", json_schema_extra = { "linkml_meta": {'domain_of': ['MagnetSimulationElement', 'RFCavitySimulationElement'],
         'ifabsent': 'int(0)'} })
    lsc_bins: Optional[int] = Field(default=100, description="""Number of longitudinal space-charge bins.""", json_schema_extra = { "linkml_meta": {'domain_of': ['RFCavitySimulationElement', 'DriftSimulationElement'],
         'ifabsent': 'int(100)'} })
    field_amplitude: Optional[float] = Field(default=0, description="""Cavity field amplitude.""", json_schema_extra = { "linkml_meta": {'domain_of': ['MagnetSimulationElement', 'RFCavitySimulationElement'],
         'ifabsent': 'float(0)'} })
    change_p0: int = Field(default=1, description="""Flag indicating whether the cavity changes reference momentum.""", json_schema_extra = { "linkml_meta": {'domain_of': ['RFCavitySimulationElement'], 'ifabsent': 'int(1)'} })
    end1_focus: int = Field(default=1, description="""Apply entrance focusing.""", json_schema_extra = { "linkml_meta": {'domain_of': ['RFCavitySimulationElement'], 'ifabsent': 'int(1)'} })
    end2_focus: int = Field(default=1, description="""Apply exit focusing.""", json_schema_extra = { "linkml_meta": {'domain_of': ['RFCavitySimulationElement'], 'ifabsent': 'int(1)'} })
    body_focus_model: str = Field(default="SRS", description="""Cavity body focusing model.""", json_schema_extra = { "linkml_meta": {'domain_of': ['RFCavitySimulationElement'], 'ifabsent': 'string(SRS)'} })
    current_bins: int = Field(default=0, description="""Number of current bins.""", json_schema_extra = { "linkml_meta": {'domain_of': ['RFCavitySimulationElement'], 'ifabsent': 'int(0)'} })
    interpolate_current_bins: int = Field(default=1, description="""Flag indicating current-bin interpolation.""", json_schema_extra = { "linkml_meta": {'domain_of': ['RFCavitySimulationElement'], 'ifabsent': 'int(1)'} })
    smooth_current_bins: int = Field(default=1, description="""Flag indicating current-bin smoothing.""", json_schema_extra = { "linkml_meta": {'domain_of': ['RFCavitySimulationElement'], 'ifabsent': 'int(1)'} })
    smooth: Optional[int] = Field(default=None, description="""Cavity smoothing parameter.""", json_schema_extra = { "linkml_meta": {'domain_of': ['MagnetSimulationElement',
                       'RFCavitySimulationElement',
                       'WakefieldSimulationElement']} })
    ez_peak: Optional[float] = Field(default=None, description="""Peak longitudinal electric field.""", json_schema_extra = { "linkml_meta": {'domain_of': ['RFCavitySimulationElement']} })
    field_file_name: Optional[str] = Field(default=None, description="""Cavity field file name.""", json_schema_extra = { "linkml_meta": {'domain_of': ['RFCavitySimulationElement']} })
    wakefile: Optional[str] = Field(default=None, description="""Wake file name.""", json_schema_extra = { "linkml_meta": {'domain_of': ['RFCavitySimulationElement']} })
    zwakefile: Optional[str] = Field(default=None, description="""Longitudinal wake file name.""", json_schema_extra = { "linkml_meta": {'domain_of': ['RFCavitySimulationElement']} })
    trwakefile: Optional[str] = Field(default=None, description="""Transverse wake file name.""", json_schema_extra = { "linkml_meta": {'domain_of': ['RFCavitySimulationElement']} })
    field_definition: Optional[str] = Field(default=None, description="""Path to the 3-D field-map file.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SimulationElement']} })
    wakefield_definition: Optional[str] = Field(default=None, description="""Path to the wakefield impedance file.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SimulationElement']} })
    field_reference_position: Optional[str] = Field(default=None, description="""Longitudinal origin of the field map [m].""", json_schema_extra = { "linkml_meta": {'domain_of': ['SimulationElement']} })
    scale_field: float = Field(default=1, description="""Multiplicative scale factor applied to the field map.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SimulationElement'], 'ifabsent': 'float(1)'} })


class _WakefieldSimulationElementBase(_SimulationElementBase):
    """
    Simulation attributes for passive wakefield structures.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:WakefieldSimulationElement',
         'from_schema': 'https://w3id.org/laura/schema/simulation'})

    t_column: Optional[str] = Field(default=None, description="""Time column in the wake file.""", json_schema_extra = { "linkml_meta": {'domain_of': ['RFCavitySimulationElement', 'WakefieldSimulationElement']} })
    z_column: Optional[str] = Field(default=None, description="""Longitudinal position column in the wake file.""", json_schema_extra = { "linkml_meta": {'domain_of': ['RFCavitySimulationElement', 'WakefieldSimulationElement']} })
    wx_column: Optional[str] = Field(default=None, description="""Horizontal wake column in the wake file.""", json_schema_extra = { "linkml_meta": {'domain_of': ['RFCavitySimulationElement', 'WakefieldSimulationElement']} })
    wy_column: Optional[str] = Field(default=None, description="""Vertical wake column in the wake file.""", json_schema_extra = { "linkml_meta": {'domain_of': ['RFCavitySimulationElement', 'WakefieldSimulationElement']} })
    wz_column: Optional[str] = Field(default=None, description="""Longitudinal wake column in the wake file.""", json_schema_extra = { "linkml_meta": {'domain_of': ['RFCavitySimulationElement', 'WakefieldSimulationElement']} })
    allow_long_beam: Optional[bool] = Field(default=True, description="""Allow beams longer than the wakefield.""", json_schema_extra = { "linkml_meta": {'domain_of': ['WakefieldSimulationElement'], 'ifabsent': 'True'} })
    bunched_beam: Optional[bool] = Field(default=False, description="""Use bunched beam mode.""", json_schema_extra = { "linkml_meta": {'domain_of': ['WakefieldSimulationElement'], 'ifabsent': 'False'} })
    change_momentum: Optional[bool] = Field(default=True, description="""Allow wakefield to change bunch momentum.""", json_schema_extra = { "linkml_meta": {'domain_of': ['WakefieldSimulationElement'], 'ifabsent': 'True'} })
    factor: float = Field(default=1, description="""Wake scaling factor.""", json_schema_extra = { "linkml_meta": {'domain_of': ['WakefieldSimulationElement'], 'ifabsent': 'float(1)'} })
    interpolate: Optional[bool] = Field(default=True, description="""Interpolate points in wake file.""", json_schema_extra = { "linkml_meta": {'domain_of': ['WakefieldSimulationElement'], 'ifabsent': 'True'} })
    scale_kick: float = Field(default=1, description="""Factor by which to scale wake kicks.""", json_schema_extra = { "linkml_meta": {'domain_of': ['WakefieldSimulationElement'], 'ifabsent': 'float(1)'} })
    scale_field_ex: float = Field(default=0.0, description="""x-component of the longitudinal direction vector.""", json_schema_extra = { "linkml_meta": {'domain_of': ['WakefieldSimulationElement'], 'ifabsent': 'float(0.0)'} })
    scale_field_ey: float = Field(default=0.0, description="""y-component of the longitudinal direction vector.""", json_schema_extra = { "linkml_meta": {'domain_of': ['WakefieldSimulationElement'], 'ifabsent': 'float(0.0)'} })
    scale_field_ez: float = Field(default=1.0, description="""z-component of the longitudinal direction vector.""", json_schema_extra = { "linkml_meta": {'domain_of': ['WakefieldSimulationElement'], 'ifabsent': 'float(1.0)'} })
    scale_field_hx: float = Field(default=1.0, description="""x-component of the horizontal direction vector.""", json_schema_extra = { "linkml_meta": {'domain_of': ['WakefieldSimulationElement'], 'ifabsent': 'float(1.0)'} })
    scale_field_hy: float = Field(default=0.0, description="""y-component of the horizontal direction vector.""", json_schema_extra = { "linkml_meta": {'domain_of': ['WakefieldSimulationElement'], 'ifabsent': 'float(0.0)'} })
    scale_field_hz: float = Field(default=0.0, description="""z-component of the horizontal direction vector.""", json_schema_extra = { "linkml_meta": {'domain_of': ['WakefieldSimulationElement'], 'ifabsent': 'float(0.0)'} })
    equal_grid: float = Field(default=0.66, description="""Interpolation between equidistant and equal-charge grids.""", json_schema_extra = { "linkml_meta": {'domain_of': ['WakefieldSimulationElement'], 'ifabsent': 'float(0.66)'} })
    interpolation_method: int = Field(default=2, description="""Interpolation method for ASTRA.""", json_schema_extra = { "linkml_meta": {'domain_of': ['WakefieldSimulationElement'], 'ifabsent': 'int(2)'} })
    smooth: float = Field(default=0.25, description="""Smoothing parameter for Gaussian interpolation.""", json_schema_extra = { "linkml_meta": {'domain_of': ['MagnetSimulationElement',
                       'RFCavitySimulationElement',
                       'WakefieldSimulationElement'],
         'ifabsent': 'float(0.25)'} })
    subbins: int = Field(default=10, description="""Sub-binning parameter.""", json_schema_extra = { "linkml_meta": {'domain_of': ['WakefieldSimulationElement'], 'ifabsent': 'int(10)'} })
    field_definition: Optional[str] = Field(default=None, description="""Path to the 3-D field-map file.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SimulationElement']} })
    wakefield_definition: Optional[str] = Field(default=None, description="""Path to the wakefield impedance file.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SimulationElement']} })
    field_reference_position: Optional[str] = Field(default=None, description="""Longitudinal origin of the field map [m].""", json_schema_extra = { "linkml_meta": {'domain_of': ['SimulationElement']} })
    scale_field: float = Field(default=1, description="""Multiplicative scale factor applied to the field map.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SimulationElement'], 'ifabsent': 'float(1)'} })


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
    lsc_interpolate: int = Field(default=1, description="""Flag to allow interpolation of computed LSC wake.""", json_schema_extra = { "linkml_meta": {'domain_of': ['DriftSimulationElement'], 'ifabsent': 'int(1)'} })
    csr_enable: Optional[bool] = Field(default=True, description="""Enable CSR drift calculations.""", json_schema_extra = { "linkml_meta": {'domain_of': ['MagnetSimulationElement', 'DriftSimulationElement'],
         'ifabsent': 'True'} })
    lsc_enable: Optional[bool] = Field(default=True, description="""Enable LSC drift calculations.""", json_schema_extra = { "linkml_meta": {'domain_of': ['DriftSimulationElement'], 'ifabsent': 'True'} })
    use_stupakov: int = Field(default=1, description="""Use Stupakov formula.""", json_schema_extra = { "linkml_meta": {'domain_of': ['DriftSimulationElement'], 'ifabsent': 'int(1)'} })
    csrdz: float = Field(default=0.01, description="""Step size for CSR calculations.""", json_schema_extra = { "linkml_meta": {'domain_of': ['DriftSimulationElement'], 'ifabsent': 'float(0.01)'} })
    lsc_high_frequency_cutoff_start: Optional[float] = Field(default=None, description="""High-frequency cutoff start for LSC.""", json_schema_extra = { "linkml_meta": {'domain_of': ['DriftSimulationElement']} })
    lsc_high_frequency_cutoff_end: Optional[float] = Field(default=None, description="""High-frequency cutoff end for LSC.""", json_schema_extra = { "linkml_meta": {'domain_of': ['DriftSimulationElement']} })
    lsc_low_frequency_cutoff_start: Optional[float] = Field(default=None, description="""Low-frequency cutoff start for LSC.""", json_schema_extra = { "linkml_meta": {'domain_of': ['DriftSimulationElement']} })
    lsc_low_frequency_cutoff_end: Optional[float] = Field(default=None, description="""Low-frequency cutoff end for LSC.""", json_schema_extra = { "linkml_meta": {'domain_of': ['DriftSimulationElement']} })
    field_definition: Optional[str] = Field(default=None, description="""Path to the 3-D field-map file.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SimulationElement']} })
    wakefield_definition: Optional[str] = Field(default=None, description="""Path to the wakefield impedance file.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SimulationElement']} })
    field_reference_position: Optional[str] = Field(default=None, description="""Longitudinal origin of the field map [m].""", json_schema_extra = { "linkml_meta": {'domain_of': ['SimulationElement']} })
    scale_field: float = Field(default=1, description="""Multiplicative scale factor applied to the field map.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SimulationElement'], 'ifabsent': 'float(1)'} })


class _DiagnosticSimulationElementBase(_SimulationElementBase):
    """
    Simulation attributes for beam-diagnostic elements.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:DiagnosticSimulationElement',
         'from_schema': 'https://w3id.org/laura/schema/simulation'})

    output_filename: Optional[str] = Field(default=None, description="""Output filename for diagnostic data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['DiagnosticSimulationElement']} })
    field_definition: Optional[str] = Field(default=None, description="""Path to the 3-D field-map file.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SimulationElement']} })
    wakefield_definition: Optional[str] = Field(default=None, description="""Path to the wakefield impedance file.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SimulationElement']} })
    field_reference_position: Optional[str] = Field(default=None, description="""Longitudinal origin of the field map [m].""", json_schema_extra = { "linkml_meta": {'domain_of': ['SimulationElement']} })
    scale_field: float = Field(default=1, description="""Multiplicative scale factor applied to the field map.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SimulationElement'], 'ifabsent': 'float(1)'} })


class _PlasmaSimulationElementBase(_SimulationElementBase):
    """
    Simulation attributes for plasma-accelerator stages.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:PlasmaSimulationElement',
         'from_schema': 'https://w3id.org/laura/schema/simulation'})

    wakefield_model: Optional[str] = Field(default=None, description="""Wakefield model identifier.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PlasmaSimulationElement']} })
    bunch_pusher: str = Field(default="boris", description="""Pusher used to evolve bunch particles in time.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PlasmaSimulationElement'], 'ifabsent': 'string(boris)'} })
    dt_bunch: str = Field(default="auto", description="""Time-step control for bunch evolution (or 'auto').""", json_schema_extra = { "linkml_meta": {'domain_of': ['PlasmaSimulationElement'], 'ifabsent': 'string(auto)'} })
    n_out: int = Field(default=1, description="""Number of distribution dumps during the plasma stage.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PlasmaSimulationElement'], 'ifabsent': 'int(1)'} })
    min_longitudinal_position: float = Field(default=0, description="""Minimum longitudinal position [m].""", json_schema_extra = { "linkml_meta": {'domain_of': ['PlasmaSimulationElement'], 'ifabsent': 'float(0)'} })
    max_longitudinal_position: float = Field(default=0, description="""Maximum longitudinal position [m].""", json_schema_extra = { "linkml_meta": {'domain_of': ['PlasmaSimulationElement'], 'ifabsent': 'float(0)'} })
    n_longitudinal: int = Field(default=0, description="""Number of grid points in the longitudinal direction.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PlasmaSimulationElement'], 'ifabsent': 'int(0)'} })
    n_radial: int = Field(default=0, description="""Number of grid points in the radial direction.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PlasmaSimulationElement'], 'ifabsent': 'int(0)'} })
    plasma_particles_per_cell: int = Field(default=2, description="""Number of plasma particles per cell.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PlasmaSimulationElement'], 'ifabsent': 'int(2)'} })
    r_max: float = Field(default=0, description="""Radial extent of the simulation box [m].""", json_schema_extra = { "linkml_meta": {'domain_of': ['PlasmaSimulationElement'], 'ifabsent': 'float(0)'} })
    r_max_plasma: Optional[float] = Field(default=None, description="""Maximum radial extension of the plasma column.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PlasmaSimulationElement']} })
    dz_fields: Optional[float] = Field(default=None, description="""Interval for plasma wakefield updates.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PlasmaSimulationElement']} })
    plasma_pusher: str = Field(default="boris", description="""Pusher used to evolve the plasma in time.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PlasmaSimulationElement'], 'ifabsent': 'string(boris)'} })
    field_definition: Optional[str] = Field(default=None, description="""Path to the 3-D field-map file.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SimulationElement']} })
    wakefield_definition: Optional[str] = Field(default=None, description="""Path to the wakefield impedance file.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SimulationElement']} })
    field_reference_position: Optional[str] = Field(default=None, description="""Longitudinal origin of the field map [m].""", json_schema_extra = { "linkml_meta": {'domain_of': ['SimulationElement']} })
    scale_field: float = Field(default=1, description="""Multiplicative scale factor applied to the field map.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SimulationElement'], 'ifabsent': 'float(1)'} })


class _TwissMatchSimulationElementBase(_SimulationElementBase):
    """
    Simulation attributes for Twiss-matching points.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:TwissMatchSimulationElement',
         'from_schema': 'https://w3id.org/laura/schema/simulation'})

    beta_x: Optional[float] = Field(default=None, description="""Horizontal beta.""", json_schema_extra = { "linkml_meta": {'domain_of': ['TwissMatchSimulationElement']} })
    beta_y: Optional[float] = Field(default=None, description="""Vertical beta.""", json_schema_extra = { "linkml_meta": {'domain_of': ['TwissMatchSimulationElement']} })
    alpha_x: Optional[float] = Field(default=None, description="""Horizontal alpha.""", json_schema_extra = { "linkml_meta": {'domain_of': ['TwissMatchSimulationElement']} })
    alpha_y: Optional[float] = Field(default=None, description="""Vertical alpha.""", json_schema_extra = { "linkml_meta": {'domain_of': ['TwissMatchSimulationElement']} })
    eta_x: float = Field(default=0.0, description="""Horizontal dispersion.""", json_schema_extra = { "linkml_meta": {'domain_of': ['TwissMatchSimulationElement'], 'ifabsent': 'float(0.0)'} })
    eta_y: float = Field(default=0.0, description="""Vertical dispersion.""", json_schema_extra = { "linkml_meta": {'domain_of': ['TwissMatchSimulationElement'], 'ifabsent': 'float(0.0)'} })
    eta_xp: float = Field(default=0.0, description="""Horizontal dispersion derivative.""", json_schema_extra = { "linkml_meta": {'domain_of': ['TwissMatchSimulationElement'], 'ifabsent': 'float(0.0)'} })
    eta_yp: float = Field(default=0.0, description="""Vertical dispersion derivative.""", json_schema_extra = { "linkml_meta": {'domain_of': ['TwissMatchSimulationElement'], 'ifabsent': 'float(0.0)'} })
    from_beam: Optional[bool] = Field(default=True, description="""Compute transform from tracked beam properties.""", json_schema_extra = { "linkml_meta": {'domain_of': ['TwissMatchSimulationElement'], 'ifabsent': 'True'} })
    field_definition: Optional[str] = Field(default=None, description="""Path to the 3-D field-map file.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SimulationElement']} })
    wakefield_definition: Optional[str] = Field(default=None, description="""Path to the wakefield impedance file.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SimulationElement']} })
    field_reference_position: Optional[str] = Field(default=None, description="""Longitudinal origin of the field map [m].""", json_schema_extra = { "linkml_meta": {'domain_of': ['SimulationElement']} })
    scale_field: float = Field(default=1, description="""Multiplicative scale factor applied to the field map.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SimulationElement'], 'ifabsent': 'float(1)'} })


class _MultipoleBase(ConfiguredBaseModel):
    """
    Individual multipole field component, characterised by order and integrated normal / skew strengths at a reference radius.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:Multipole',
         'from_schema': 'https://w3id.org/laura/schema/magnetic'})

    order: int = Field(default=0, description="""Multipole order (0 = dipole, 1 = quadrupole, ?).""", ge=0, json_schema_extra = { "linkml_meta": {'domain_of': ['Multipole', 'MagneticElement'], 'ifabsent': 'int(0)'} })
    normal: float = Field(default=0, description="""Integrated normal (upright) multipole strength [T.m^{1-n}].""", json_schema_extra = { "linkml_meta": {'domain_of': ['Multipole'], 'ifabsent': 'float(0)'} })
    skew: float = Field(default=0, description="""Integrated skew (rotated) multipole strength [T.m^{1-n}].""", json_schema_extra = { "linkml_meta": {'domain_of': ['Multipole', 'MagneticElement'], 'ifabsent': 'float(0)'} })
    radius: float = Field(default=0, description="""Reference radius for multipole normalisation [m].""", json_schema_extra = { "linkml_meta": {'domain_of': ['Multipole', 'ApertureElement', 'CameraMask'],
         'ifabsent': 'float(0)',
         'unit': {'ucum_code': 'm'}} })


class _MultipolesBase(ConfiguredBaseModel):
    """
    Complete set of integrated multipole strengths up to decapole order, as named slots for efficient element look-up.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:MultipoleList',
         'from_schema': 'https://w3id.org/laura/schema/magnetic'})

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
         'from_schema': 'https://w3id.org/laura/schema/magnetic'})

    coefficients: list[float] = Field(default_factory=list, description="""Polynomial coefficients ordered from lowest to highest degree: ``FieldIntegral = sum c_n . I^n``.""", json_schema_extra = { "linkml_meta": {'domain_of': ['FieldIntegral']} })


class _LinearSaturationFitBase(ConfiguredBaseModel):
    """
    Bi-linear saturation model mapping magnet current to integrated field strength (K-value conversion).
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:LinearSaturationFit',
         'from_schema': 'https://w3id.org/laura/schema/magnetic'})

    m: float = Field(default=0, description="""Linear slope of the unsaturated region.""", json_schema_extra = { "linkml_meta": {'domain_of': ['LinearSaturationFit'], 'ifabsent': 'float(0)'} })
    I_max: float = Field(default=0, description="""Current at which saturation begins [A].""", json_schema_extra = { "linkml_meta": {'domain_of': ['LinearSaturationFit'],
         'ifabsent': 'float(0)',
         'unit': {'ucum_code': 'A'}} })
    f: float = Field(default=0, description="""Saturation fraction (slope ratio below/above I_max).""", json_schema_extra = { "linkml_meta": {'domain_of': ['LinearSaturationFit'], 'ifabsent': 'float(0)'} })
    a: float = Field(default=0, description="""Quadratic saturation coefficient.""", json_schema_extra = { "linkml_meta": {'domain_of': ['LinearSaturationFit'], 'ifabsent': 'float(0)'} })
    I0: float = Field(default=0, description="""Current offset [A].""", json_schema_extra = { "linkml_meta": {'domain_of': ['LinearSaturationFit'],
         'ifabsent': 'float(0)',
         'unit': {'ucum_code': 'A'}} })
    d: float = Field(default=0, description="""Constant offset term.""", json_schema_extra = { "linkml_meta": {'domain_of': ['LinearSaturationFit'], 'ifabsent': 'float(0)'} })
    L: float = Field(default=0, description="""Effective magnetic length [m].""", json_schema_extra = { "linkml_meta": {'domain_of': ['LinearSaturationFit'],
         'ifabsent': 'float(0)',
         'unit': {'ucum_code': 'm'}} })


class _MagneticElementBase(ConfiguredBaseModel):
    """
    Magnetic field parameters for a beamline magnet, including multipole components, field integrals, and geometric edge parameters.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:MagneticElement',
         'from_schema': 'https://w3id.org/laura/schema/magnetic',
         'in_subset': ['magnetic_properties']})

    order: int = Field(default=-1, description="""Principal multipole order (0 = dipole, 1 = quad, ?).""", ge=-1, json_schema_extra = { "linkml_meta": {'domain_of': ['Multipole', 'MagneticElement'], 'ifabsent': 'int(-1)'} })
    skew: bool = Field(default=False, description="""Whether the magnet is rotated 45? to produce a skew field component.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Multipole', 'MagneticElement'], 'ifabsent': 'False'} })
    length: float = Field(default=0, description="""Magnetic (effective) length [m].""", ge=0.0, json_schema_extra = { "linkml_meta": {'domain_of': ['MagneticElement'],
         'ifabsent': 'float(0)',
         'unit': {'ucum_code': 'm'}} })
    multipoles: Optional[_MultipolesBase] = Field(default=None, description="""Integrated multipole field components.""", json_schema_extra = { "linkml_meta": {'domain_of': ['MagneticElement']} })
    systematic_multipoles: Optional[_MultipolesBase] = Field(default=None, description="""Systematic (design) multipole errors at the reference radius.""", json_schema_extra = { "linkml_meta": {'domain_of': ['MagneticElement']} })
    random_multipoles: Optional[_MultipolesBase] = Field(default=None, description="""Random multipole errors at the reference radius.""", json_schema_extra = { "linkml_meta": {'domain_of': ['MagneticElement']} })
    field_integral_coefficients: Optional[_FieldIntegralBase] = Field(default=None, description="""Polynomial calibration of integrated field vs. current.""", json_schema_extra = { "linkml_meta": {'domain_of': ['MagneticElement']} })
    linear_saturation_coefficients: Optional[_LinearSaturationFitBase] = Field(default=None, description="""Bi-linear saturation calibration.""", json_schema_extra = { "linkml_meta": {'domain_of': ['MagneticElement']} })
    settle_time: Optional[float] = Field(default=None, description="""Power-supply settle time after a change [s].""", json_schema_extra = { "linkml_meta": {'domain_of': ['MagneticElement'], 'unit': {'ucum_code': 's'}} })
    entrance_edge_angle: Optional[float] = Field(default=None, description="""Fringe-field entrance edge angle [rad].""", json_schema_extra = { "linkml_meta": {'domain_of': ['MagneticElement'], 'unit': {'ucum_code': 'rad'}} })
    exit_edge_angle: Optional[float] = Field(default=None, description="""Fringe-field exit edge angle [rad].""", json_schema_extra = { "linkml_meta": {'domain_of': ['MagneticElement'], 'unit': {'ucum_code': 'rad'}} })
    gap: float = Field(default=0.032, description="""Full gap between pole faces [m].""", ge=0.0, json_schema_extra = { "linkml_meta": {'domain_of': ['MagneticElement'],
         'ifabsent': 'float(0.032)',
         'unit': {'ucum_code': 'm'}} })
    bore: float = Field(default=0.037, description="""Magnet bore radius [m].""", ge=0.0, json_schema_extra = { "linkml_meta": {'domain_of': ['MagneticElement'],
         'ifabsent': 'float(0.037)',
         'unit': {'ucum_code': 'm'}} })
    plane: Optional[BendingPlaneEnum] = Field(default=BendingPlaneEnum.Horizontal, description="""Principal bending / focusing plane (``Horizontal``, ``Vertical``, or ``Combined``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['MagneticElement'], 'ifabsent': 'string(Horizontal)'} })
    width: float = Field(default=0.2, description="""Physical width of the magnet in the bending plane [m].""", json_schema_extra = { "linkml_meta": {'domain_of': ['MagneticElement'],
         'ifabsent': 'float(0.2)',
         'unit': {'ucum_code': 'm'}} })
    tilt: float = Field(default=0.0, description="""Global tilt about the beam axis [rad].""", json_schema_extra = { "linkml_meta": {'domain_of': ['MagneticElement'],
         'ifabsent': 'float(0.0)',
         'unit': {'ucum_code': 'rad'}} })
    edge_field_integral: float = Field(default=0.5, description="""Enge fringe-field integral parameter (dimensionless).""", json_schema_extra = { "linkml_meta": {'domain_of': ['MagnetSimulationElement', 'MagneticElement'],
         'ifabsent': 'float(0.5)'} })
    fringe_field_coefficient: float = Field(default=0.0, description="""Coefficient controlling the fringe-field roll-off rate.""", json_schema_extra = { "linkml_meta": {'domain_of': ['MagneticElement'], 'ifabsent': 'float(0.0)'} })
    gradient: Optional[float] = Field(default=None, description="""Peak field gradient [T/m] (quads) or peak field [T] (dipoles).""", json_schema_extra = { "linkml_meta": {'domain_of': ['MagneticElement'], 'unit': {'ucum_code': 'T.m-1'}} })


class _ApertureElementBase(ConfiguredBaseModel):
    """
    Transverse aperture geometry for drift-space checks and collimators.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:ApertureElement',
         'from_schema': 'https://w3id.org/laura/schema/magnetic'})

    number_of_elements: Optional[int] = Field(default=None, description="""Number of aperture sub-elements (e.g., for multi-leaf collimators).""", ge=1, json_schema_extra = { "linkml_meta": {'domain_of': ['ApertureElement']} })
    horizontal_size: float = Field(default=0.0, description="""Full horizontal aperture [m].""", ge=0.0, json_schema_extra = { "linkml_meta": {'domain_of': ['ApertureElement'],
         'ifabsent': 'float(0.0)',
         'unit': {'ucum_code': 'm'}} })
    vertical_size: float = Field(default=0.0, description="""Full vertical aperture [m].""", ge=0.0, json_schema_extra = { "linkml_meta": {'domain_of': ['ApertureElement'],
         'ifabsent': 'float(0.0)',
         'unit': {'ucum_code': 'm'}} })
    shape: Optional[ApertureShapeEnum] = Field(default=None, description="""Cross-sectional aperture shape.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ApertureElement']} })
    radius: Optional[float] = Field(default=None, description="""Radius for circular apertures [m].""", ge=0.0, json_schema_extra = { "linkml_meta": {'domain_of': ['Multipole', 'ApertureElement', 'CameraMask'],
         'unit': {'ucum_code': 'm'}} })
    negative_extent: Optional[float] = Field(default=None, description="""Upstream / inner extent [m].""", json_schema_extra = { "linkml_meta": {'domain_of': ['ApertureElement'], 'unit': {'ucum_code': 'm'}} })
    positive_extent: Optional[float] = Field(default=None, description="""Downstream / outer extent [m].""", json_schema_extra = { "linkml_meta": {'domain_of': ['ApertureElement'], 'unit': {'ucum_code': 'm'}} })


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
    values: list[float] = Field(default_factory=list, description="""Sequence of peak currents applied during the degauss cycle [A].""", validation_alias=AliasChoices('values', 'degauss_values'), json_schema_extra = { "linkml_meta": {'aliases': ['degauss_values'],
         'domain_of': ['DegaussableElement'],
         'unit': {'ucum_code': 'A'}} })
    steps: int = Field(default=11, description="""Number of degauss steps per half-cycle.""", ge=1, validation_alias=AliasChoices('steps', 'num_degauss_steps'), json_schema_extra = { "linkml_meta": {'aliases': ['num_degauss_steps'],
         'domain_of': ['DegaussableElement'],
         'ifabsent': 'int(11)'} })


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
    coupling_cell_length: Optional[float] = Field(default=0.0, description="""Length of the coupling cell [m].""", ge=0.0, json_schema_extra = { "linkml_meta": {'domain_of': ['RFCavityElement',
                       'WakefieldElement',
                       'RFDeflectingCavityElement'],
         'ifabsent': 'float(0.0)',
         'unit': {'ucum_code': 'm'}} })
    design_gamma: Optional[float] = Field(default=None, description="""Design Lorentz factor.""", ge=1.0, json_schema_extra = { "linkml_meta": {'domain_of': ['RFCavityElement', 'RFDeflectingCavityElement']} })
    design_power: Optional[float] = Field(default=25000000, description="""Design peak power [W].""", ge=0.0, json_schema_extra = { "linkml_meta": {'domain_of': ['RFCavityElement', 'RFDeflectingCavityElement'],
         'ifabsent': 'float(25000000)',
         'unit': {'ucum_code': 'W'}} })
    frequency: Optional[float] = Field(default=2998500000.0, description="""Operating frequency [Hz].""", ge=0.0, json_schema_extra = { "linkml_meta": {'domain_of': ['RFCavityElement', 'RFDeflectingCavityElement'],
         'ifabsent': 'float(2998500000.0)',
         'unit': {'ucum_code': 'Hz'}} })
    n_cells: Optional[int] = Field(default=1, description="""Number of cells.""", ge=1, json_schema_extra = { "linkml_meta": {'domain_of': ['RFCavityElement',
                       'WakefieldElement',
                       'RFDeflectingCavityElement'],
         'ifabsent': 'int(1)'} })
    crest: Optional[float] = Field(default=0, description="""On-crest phase offset providing maximum energy gain [deg].""", json_schema_extra = { "linkml_meta": {'domain_of': ['RFCavityElement', 'RFDeflectingCavityElement'],
         'ifabsent': 'float(0)',
         'unit': {'ucum_code': 'deg'}} })
    phase: Optional[float] = Field(default=0.0, description="""Operating phase offset [deg].""", json_schema_extra = { "linkml_meta": {'domain_of': ['RFCavityElement', 'RFDeflectingCavityElement'],
         'ifabsent': 'float(0.0)',
         'unit': {'ucum_code': 'deg'}} })
    shunt_impedance: Optional[float] = Field(default=None, description="""Shunt impedance [M?/m].""", json_schema_extra = { "linkml_meta": {'domain_of': ['RFCavityElement', 'RFDeflectingCavityElement']} })
    mode_numerator: Optional[int] = Field(default=None, description="""Mode fraction numerator.""", json_schema_extra = { "linkml_meta": {'domain_of': ['RFCavityElement', 'RFDeflectingCavityElement']} })
    mode_denominator: Optional[int] = Field(default=None, description="""Mode fraction denominator.""", json_schema_extra = { "linkml_meta": {'domain_of': ['RFCavityElement', 'RFDeflectingCavityElement']} })
    structure_type: str = Field(default="StandingWave", description="""RF structure type (e.g., ``SW`` standing-wave, ``TW`` travelling-wave).""", validation_alias=AliasChoices('structure_type', 'structure_Type'), json_schema_extra = { "linkml_meta": {'aliases': ['structure_Type'],
         'domain_of': ['RFCavityElement'],
         'ifabsent': 'string(StandingWave)'} })
    attenuation_constant: float = Field(default=0, description="""Attenuation constant ? of a travelling-wave structure [Np/m].""", json_schema_extra = { "linkml_meta": {'domain_of': ['RFCavityElement'], 'ifabsent': 'float(0)'} })
    power_calibration: list[float] = Field(default_factory=list, description="""Calibration constant relating measured power to cavity gradient.""", json_schema_extra = { "linkml_meta": {'domain_of': ['RFCavityElement']} })
    gradient_calibration: list[float] = Field(default_factory=list, description="""Calibration relating measured signal to gradient [MV/m per a.u.].""", json_schema_extra = { "linkml_meta": {'domain_of': ['RFCavityElement']} })


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
    n_cells: Optional[int] = Field(default=1, description="""Number of cells.""", ge=1, json_schema_extra = { "linkml_meta": {'domain_of': ['RFCavityElement',
                       'WakefieldElement',
                       'RFDeflectingCavityElement'],
         'ifabsent': 'int(1)'} })
    coupling_cell_length: Optional[float] = Field(default=0.0, description="""Length of the coupling cell [m].""", ge=0.0, json_schema_extra = { "linkml_meta": {'domain_of': ['RFCavityElement',
                       'WakefieldElement',
                       'RFDeflectingCavityElement'],
         'ifabsent': 'float(0.0)',
         'unit': {'ucum_code': 'm'}} })


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
    coupling_cell_length: Optional[float] = Field(default=0.0, description="""Length of the coupling cell [m].""", ge=0.0, json_schema_extra = { "linkml_meta": {'domain_of': ['RFCavityElement',
                       'WakefieldElement',
                       'RFDeflectingCavityElement'],
         'ifabsent': 'float(0.0)',
         'unit': {'ucum_code': 'm'}} })
    crest: Optional[float] = Field(default=0, description="""On-crest phase offset providing maximum energy gain [deg].""", json_schema_extra = { "linkml_meta": {'domain_of': ['RFCavityElement', 'RFDeflectingCavityElement'],
         'ifabsent': 'float(0)',
         'unit': {'ucum_code': 'deg'}} })
    design_gamma: Optional[float] = Field(default=None, description="""Design Lorentz factor.""", ge=1.0, json_schema_extra = { "linkml_meta": {'domain_of': ['RFCavityElement', 'RFDeflectingCavityElement']} })
    design_power: Optional[float] = Field(default=25000000, description="""Design peak power [W].""", ge=0.0, json_schema_extra = { "linkml_meta": {'domain_of': ['RFCavityElement', 'RFDeflectingCavityElement'],
         'ifabsent': 'float(25000000)',
         'unit': {'ucum_code': 'W'}} })
    frequency: Optional[float] = Field(default=2998500000.0, description="""Operating frequency [Hz].""", ge=0.0, json_schema_extra = { "linkml_meta": {'domain_of': ['RFCavityElement', 'RFDeflectingCavityElement'],
         'ifabsent': 'float(2998500000.0)',
         'unit': {'ucum_code': 'Hz'}} })
    n_cells: Optional[int] = Field(default=1, description="""Number of cells.""", ge=1, json_schema_extra = { "linkml_meta": {'domain_of': ['RFCavityElement',
                       'WakefieldElement',
                       'RFDeflectingCavityElement'],
         'ifabsent': 'int(1)'} })
    phase: Optional[float] = Field(default=0.0, description="""Operating phase offset [deg].""", json_schema_extra = { "linkml_meta": {'domain_of': ['RFCavityElement', 'RFDeflectingCavityElement'],
         'ifabsent': 'float(0.0)',
         'unit': {'ucum_code': 'deg'}} })
    shunt_impedance: Optional[float] = Field(default=None, description="""Shunt impedance [M?/m].""", json_schema_extra = { "linkml_meta": {'domain_of': ['RFCavityElement', 'RFDeflectingCavityElement']} })
    mode_numerator: Optional[int] = Field(default=None, description="""Mode fraction numerator.""", json_schema_extra = { "linkml_meta": {'domain_of': ['RFCavityElement', 'RFDeflectingCavityElement']} })
    mode_denominator: Optional[int] = Field(default=None, description="""Mode fraction denominator.""", json_schema_extra = { "linkml_meta": {'domain_of': ['RFCavityElement', 'RFDeflectingCavityElement']} })


class _PIDElementBase(ConfiguredBaseModel):
    """
    PID feedback-controller parameters.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:PIDElement',
         'from_schema': 'https://w3id.org/laura/schema/rf'})

    Kp: Optional[float] = Field(default=None, description="""Proportional gain.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PIDElement']} })
    Ki: Optional[float] = Field(default=None, description="""Integral gain.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PIDElement']} })
    Kd: Optional[float] = Field(default=None, description="""Derivative gain.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PIDElement']} })
    forward_channel: Optional[int] = Field(default=None, description="""Forward channel index.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PIDElement']} })
    probe_channel: Optional[int] = Field(default=None, description="""Probe channel index.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PIDElement']} })
    enable: Optional[str] = Field(default=None, description="""Enable command/value.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PIDElement']} })
    disable: Optional[str] = Field(default=None, description="""Disable command/value.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PIDElement']} })
    phase_range: Optional[_PIDPhaseRangeBase] = Field(default=None, description="""Phase tuning range.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PIDElement']} })
    phase_weight_range: Optional[_PIDWeightRangeBase] = Field(default=None, description="""Phase weighting range.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PIDElement']} })


class _PIDPhaseRangeBase(ConfiguredBaseModel):
    """
    Numeric min/max range for PID phase control.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:PIDPhaseRange',
         'from_schema': 'https://w3id.org/laura/schema/rf'})

    min: Optional[float] = Field(default=None, description="""Minimum value.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PIDPhaseRange']} })
    max: Optional[float] = Field(default=None, description="""Maximum value.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PIDPhaseRange']} })


class _PIDWeightRangeBase(_PIDPhaseRangeBase):
    """
    Numeric min/max range for PID phase weighting.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:PIDWeightRange',
         'from_schema': 'https://w3id.org/laura/schema/rf'})

    min: Optional[float] = Field(default=None, description="""Minimum value.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PIDPhaseRange']} })
    max: Optional[float] = Field(default=None, description="""Maximum value.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PIDPhaseRange']} })


class _TraceBase(ConfiguredBaseModel):
    """
    LLRF trace metadata.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:Trace', 'from_schema': 'https://w3id.org/laura/schema/rf'})

    data_size: Optional[int] = Field(default=None, description="""Number of points in a trace.""", validation_alias=AliasChoices('data_size', 'trace_data_size'), json_schema_extra = { "linkml_meta": {'aliases': ['trace_data_size'], 'domain_of': ['Trace']} })
    data_count: Optional[int] = Field(default=None, description="""Number of one-record trace entries.""", validation_alias=AliasChoices('data_count', 'one_trace_data_count'), json_schema_extra = { "linkml_meta": {'aliases': ['one_trace_data_count'], 'domain_of': ['Trace']} })
    data_chunk_size: Optional[int] = Field(default=None, description="""Chunk size for one-record traces.""", validation_alias=AliasChoices('data_chunk_size', 'one_trace_data_chunk_size'), json_schema_extra = { "linkml_meta": {'aliases': ['one_trace_data_chunk_size'], 'domain_of': ['Trace']} })
    number_of_start_zeros: Optional[int] = Field(default=None, description="""Number of leading zeros in a trace.""", validation_alias=AliasChoices('number_of_start_zeros', 'trace_num_of_start_zeros'), json_schema_extra = { "linkml_meta": {'aliases': ['trace_num_of_start_zeros'], 'domain_of': ['Trace']} })


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
    end: Optional[float] = Field(default=None, description="""End time.""", json_schema_extra = { "linkml_meta": {'domain_of': ['LLRFTiming']} })


class _LLRFTimingsBase(ConfiguredBaseModel):
    """
    Collection of timing windows for key LLRF channels.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:LLRFTimings',
         'from_schema': 'https://w3id.org/laura/schema/rf'})

    klystron_forward: Optional[_LLRFTimingBase] = Field(default=None, description="""Timing for klystron forward power.""", json_schema_extra = { "linkml_meta": {'domain_of': ['LLRFTimings']} })
    klystron_reverse: Optional[_LLRFTimingBase] = Field(default=None, description="""Timing for klystron reverse power.""", json_schema_extra = { "linkml_meta": {'domain_of': ['LLRFTimings']} })
    cavity_forward: Optional[_LLRFTimingBase] = Field(default=None, description="""Timing for cavity forward power.""", json_schema_extra = { "linkml_meta": {'domain_of': ['LLRFTimings']} })
    cavity_reverse: Optional[_LLRFTimingBase] = Field(default=None, description="""Timing for cavity reverse power.""", json_schema_extra = { "linkml_meta": {'domain_of': ['LLRFTimings']} })
    cavity_probe: Optional[_LLRFTimingBase] = Field(default=None, description="""Timing for cavity probe.""", json_schema_extra = { "linkml_meta": {'domain_of': ['LLRFTimings']} })


class _LowLevelRFElementBase(ConfiguredBaseModel):
    """
    Low-level RF (LLRF) system parameters.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:LowLevelRFElement',
         'from_schema': 'https://w3id.org/laura/schema/rf'})

    trace: Optional[_TraceBase] = Field(default=None, description="""Trace metadata.""", json_schema_extra = { "linkml_meta": {'domain_of': ['LowLevelRFElement']} })
    max_amplitude: Optional[float] = Field(default=None, description="""Maximum allowed amplitude.""", validation_alias=AliasChoices('max_amplitude', 'MAX_AMPLITUDE'), json_schema_extra = { "linkml_meta": {'aliases': ['MAX_AMPLITUDE'], 'domain_of': ['LowLevelRFElement']} })
    channel_names: Optional[_ChannelNamesBase] = Field(default=None, description="""Channel labels.""", json_schema_extra = { "linkml_meta": {'domain_of': ['LowLevelRFElement']} })
    crest_phase: Optional[float] = Field(default=None, description="""Cavity crest phase.""", json_schema_extra = { "linkml_meta": {'domain_of': ['LowLevelRFElement']} })
    timings: Optional[_LLRFTimingsBase] = Field(default=None, description="""Timing windows for LLRF channels.""", json_schema_extra = { "linkml_meta": {'domain_of': ['LowLevelRFElement']} })


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
                       'BLMDiagnosticElement',
                       'ScreenDiagnosticElement',
                       'ChargeDiagnosticElement',
                       'CameraDiagnosticElement'],
         'ifabsent': 'string(Stripline)'} })


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
                       'BLMDiagnosticElement',
                       'ScreenDiagnosticElement',
                       'ChargeDiagnosticElement',
                       'CameraDiagnosticElement'],
         'ifabsent': 'string(DESY)'} })


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
                       'BLMDiagnosticElement',
                       'ScreenDiagnosticElement',
                       'ChargeDiagnosticElement',
                       'CameraDiagnosticElement'],
         'ifabsent': 'string(CDR)'} })


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
                       'BLMDiagnosticElement',
                       'ScreenDiagnosticElement',
                       'ChargeDiagnosticElement',
                       'CameraDiagnosticElement'],
         'ifabsent': 'string(CLARA_HV_MOVER)'} })
    has_camera: Optional[bool] = Field(default=True, description="""Whether the screen has an associated camera.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ScreenDiagnosticElement'], 'ifabsent': 'True'} })
    camera_name: str = Field(default="", description="""Name of the associated camera element.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ScreenDiagnosticElement'], 'ifabsent': 'string()'} })
    devices: list[str] = Field(default_factory=list, description="""List of attached devices.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ScreenDiagnosticElement']} })


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
                       'BLMDiagnosticElement',
                       'ScreenDiagnosticElement',
                       'ChargeDiagnosticElement',
                       'CameraDiagnosticElement']} })


class _CameraPixelResultsIndicesBase(ConfiguredBaseModel):
    """
    Indices into camera pixel-analysis result arrays.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:CameraPixelResultsIndices',
         'from_schema': 'https://w3id.org/laura/schema/diagnostics'})

    x: int = Field(default=0, description="""Beam centroid index in x.""", validation_alias=AliasChoices('x', 'X_POS'), json_schema_extra = { "linkml_meta": {'aliases': ['X_POS'],
         'domain_of': ['CameraPixelResultsIndices',
                       'CameraPixelResultsNames',
                       'Position'],
         'ifabsent': 'int(0)'} })
    y: int = Field(default=1, description="""Beam centroid index in y.""", validation_alias=AliasChoices('y', 'Y_POS'), json_schema_extra = { "linkml_meta": {'aliases': ['Y_POS'],
         'domain_of': ['CameraPixelResultsIndices',
                       'CameraPixelResultsNames',
                       'Position'],
         'ifabsent': 'int(1)'} })
    x_sigma: int = Field(default=2, description="""Beam sigma index in x.""", validation_alias=AliasChoices('x_sigma', 'X_SIGMA_POS'), json_schema_extra = { "linkml_meta": {'aliases': ['X_SIGMA_POS'],
         'domain_of': ['CameraPixelResultsIndices', 'CameraPixelResultsNames'],
         'ifabsent': 'int(2)'} })
    y_sigma: int = Field(default=3, description="""Beam sigma index in y.""", validation_alias=AliasChoices('y_sigma', 'Y_SIGMA_POS'), json_schema_extra = { "linkml_meta": {'aliases': ['Y_SIGMA_POS'],
         'domain_of': ['CameraPixelResultsIndices', 'CameraPixelResultsNames'],
         'ifabsent': 'int(3)'} })
    covariance: int = Field(default=4, description="""Beam covariance index.""", validation_alias=AliasChoices('covariance', 'COV_POS'), json_schema_extra = { "linkml_meta": {'aliases': ['COV_POS'],
         'domain_of': ['CameraPixelResultsIndices', 'CameraPixelResultsNames'],
         'ifabsent': 'int(4)'} })


class _CameraPixelResultsNamesBase(ConfiguredBaseModel):
    """
    Names of camera pixel-analysis result arrays.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:CameraPixelResultsNames',
         'from_schema': 'https://w3id.org/laura/schema/diagnostics'})

    x: str = Field(default="X", description="""Beam centroid name in x.""", validation_alias=AliasChoices('x', 'X_NAME'), json_schema_extra = { "linkml_meta": {'aliases': ['X_NAME'],
         'domain_of': ['CameraPixelResultsIndices',
                       'CameraPixelResultsNames',
                       'Position'],
         'ifabsent': 'string(X)'} })
    y: str = Field(default="Y", description="""Beam centroid name in y.""", validation_alias=AliasChoices('y', 'Y_NAME'), json_schema_extra = { "linkml_meta": {'aliases': ['Y_NAME'],
         'domain_of': ['CameraPixelResultsIndices',
                       'CameraPixelResultsNames',
                       'Position'],
         'ifabsent': 'string(Y)'} })
    x_sigma: str = Field(default="X_SIGMA", description="""Beam sigma name in x.""", validation_alias=AliasChoices('x_sigma', 'X_SIGMA_NAME'), json_schema_extra = { "linkml_meta": {'aliases': ['X_SIGMA_NAME'],
         'domain_of': ['CameraPixelResultsIndices', 'CameraPixelResultsNames'],
         'ifabsent': 'string(X_SIGMA)'} })
    y_sigma: str = Field(default="Y_SIGMA", description="""Beam sigma name in y.""", validation_alias=AliasChoices('y_sigma', 'Y_SIGMA_NAME'), json_schema_extra = { "linkml_meta": {'aliases': ['Y_SIGMA_NAME'],
         'domain_of': ['CameraPixelResultsIndices', 'CameraPixelResultsNames'],
         'ifabsent': 'string(Y_SIGMA)'} })
    covariance: str = Field(default="COV", description="""Beam covariance name.""", validation_alias=AliasChoices('covariance', 'COV_NAME'), json_schema_extra = { "linkml_meta": {'aliases': ['COV_NAME'],
         'domain_of': ['CameraPixelResultsIndices', 'CameraPixelResultsNames'],
         'ifabsent': 'string(COV)'} })


class _CameraMaskBase(ConfiguredBaseModel):
    """
    Camera analysis mask parameters.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:CameraMask',
         'from_schema': 'https://w3id.org/laura/schema/diagnostics'})

    middle: list[float] = Field(default_factory=list, description="""Center of the mask in pixels [x, y].""", validation_alias=AliasChoices('middle', 'position', 'centre'), json_schema_extra = { "linkml_meta": {'domain_of': ['CameraMask', 'CameraSensor', 'PhysicalElement']} })
    radius: list[float] = Field(default_factory=list, description="""Mask radius in pixels [x, y].""", json_schema_extra = { "linkml_meta": {'domain_of': ['Multipole', 'ApertureElement', 'CameraMask']} })
    maximum: list[float] = Field(default_factory=list, description="""Maximum mask radius in pixels [x, y].""", json_schema_extra = { "linkml_meta": {'domain_of': ['CameraMask', 'CameraSensor', 'LaserAttenuator']} })
    use_maximum_values: Optional[bool] = Field(default=True, description="""If True, use maximum mask radius constraints.""", validation_alias=AliasChoices('use_maximum_values', 'USE_MASK_RAD_LIMITS'), json_schema_extra = { "linkml_meta": {'aliases': ['USE_MASK_RAD_LIMITS'],
         'domain_of': ['CameraMask'],
         'ifabsent': 'True'} })


class _CameraSensorBase(ConfiguredBaseModel):
    """
    Camera sensor hardware configuration.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:CameraSensor',
         'from_schema': 'https://w3id.org/laura/schema/diagnostics'})

    x_pixels: int = Field(default=2160, description="""Raw sensor pixel count in x.""", validation_alias=AliasChoices('x_pixels', 'BINARY_NUM_PIX_X'), json_schema_extra = { "linkml_meta": {'aliases': ['BINARY_NUM_PIX_X'],
         'domain_of': ['CameraSensor', 'CameraDiagnosticElement'],
         'ifabsent': 'int(2160)'} })
    y_pixels: int = Field(default=2560, description="""Raw sensor pixel count in y.""", validation_alias=AliasChoices('y_pixels', 'BINARY_NUM_PIX_Y'), json_schema_extra = { "linkml_meta": {'aliases': ['BINARY_NUM_PIX_Y'],
         'domain_of': ['CameraSensor', 'CameraDiagnosticElement'],
         'ifabsent': 'int(2560)'} })
    x_scale_factor: int = Field(default=2, description="""Pixel binning factor in x.""", validation_alias=AliasChoices('x_scale_factor', 'X_PIX_SCALE_FACTOR'), json_schema_extra = { "linkml_meta": {'aliases': ['X_PIX_SCALE_FACTOR'],
         'domain_of': ['CameraSensor'],
         'ifabsent': 'int(2)'} })
    y_scale_factor: int = Field(default=2, description="""Pixel binning factor in y.""", validation_alias=AliasChoices('y_scale_factor', 'Y_PIX_SCALE_FACTOR'), json_schema_extra = { "linkml_meta": {'aliases': ['Y_PIX_SCALE_FACTOR'],
         'domain_of': ['CameraSensor'],
         'ifabsent': 'int(2)'} })
    beam_pixel_average: float = Field(default=97.2, description="""Average pixel value for beam detection.""", validation_alias=AliasChoices('beam_pixel_average', 'AVG_PIXEL_VALUE_FOR_BEAM'), json_schema_extra = { "linkml_meta": {'aliases': ['AVG_PIXEL_VALUE_FOR_BEAM'],
         'domain_of': ['CameraSensor'],
         'ifabsent': 'float(97.2)'} })
    middle: list[float] = Field(default_factory=list, description="""Sensor optical center in pixels [x, y].""", validation_alias=AliasChoices('middle', 'position', 'centre'), json_schema_extra = { "linkml_meta": {'domain_of': ['CameraMask', 'CameraSensor', 'PhysicalElement']} })
    x_pixels_to_mm: float = Field(default=0.0134, description="""Pixel-to-mm scale factor in x.""", json_schema_extra = { "linkml_meta": {'domain_of': ['CameraSensor'], 'ifabsent': 'float(0.0134)'} })
    y_pixels_to_mm: float = Field(default=0.0134, description="""Pixel-to-mm scale factor in y.""", json_schema_extra = { "linkml_meta": {'domain_of': ['CameraSensor'], 'ifabsent': 'float(0.0134)'} })
    minimum: list[float] = Field(default_factory=list, description="""Minimum pixel positions [x, y].""", json_schema_extra = { "linkml_meta": {'domain_of': ['CameraSensor', 'LaserAttenuator']} })
    maximum: list[float] = Field(default_factory=list, description="""Maximum pixel positions [x, y].""", json_schema_extra = { "linkml_meta": {'domain_of': ['CameraMask', 'CameraSensor', 'LaserAttenuator']} })
    bit_depth: int = Field(default=16, description="""Camera bit depth.""", json_schema_extra = { "linkml_meta": {'domain_of': ['CameraSensor'], 'ifabsent': 'int(16)'} })
    operating_middle: list[float] = Field(default_factory=list, description="""Operating center positions in pixels [x, y].""", json_schema_extra = { "linkml_meta": {'domain_of': ['CameraSensor']} })
    mechanical_middle: list[float] = Field(default_factory=list, description="""Mechanical center of the camera in pixels [x, y].""", json_schema_extra = { "linkml_meta": {'domain_of': ['CameraSensor']} })


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
                       'BLMDiagnosticElement',
                       'ScreenDiagnosticElement',
                       'ChargeDiagnosticElement',
                       'CameraDiagnosticElement']} })
    x_pixels: int = Field(default=1080, description="""Image width reported by the control system [pix].""", validation_alias=AliasChoices('x_pixels', 'ARRAY_DATA_NUM_PIX_X', 'epics_x_pixels'), json_schema_extra = { "linkml_meta": {'aliases': ['ARRAY_DATA_NUM_PIX_X', 'epics_x_pixels'],
         'domain_of': ['CameraSensor', 'CameraDiagnosticElement'],
         'ifabsent': 'int(1080)'} })
    y_pixels: int = Field(default=1280, description="""Image height reported by the control system [pix].""", validation_alias=AliasChoices('y_pixels', 'ARRAY_DATA_NUM_PIX_Y', 'epics_y_pixels'), json_schema_extra = { "linkml_meta": {'aliases': ['ARRAY_DATA_NUM_PIX_Y', 'epics_y_pixels'],
         'domain_of': ['CameraSensor', 'CameraDiagnosticElement'],
         'ifabsent': 'int(1280)'} })
    rotation: float = Field(default=0, description="""Camera rotation relative to the screen plane [deg].""", json_schema_extra = { "linkml_meta": {'domain_of': ['CameraDiagnosticElement',
                       'ElementPositionError',
                       'ElementSurvey',
                       'PhysicalElement'],
         'ifabsent': 'float(0)',
         'unit': {'ucum_code': 'deg'}} })
    flipped_horizontally: Optional[bool] = Field(default=True, description="""True if the image is mirrored left-right.""", validation_alias=AliasChoices('flipped_horizontally', 'IMAGE_FLIP_LR'), json_schema_extra = { "linkml_meta": {'aliases': ['IMAGE_FLIP_LR'],
         'domain_of': ['CameraDiagnosticElement'],
         'ifabsent': 'True'} })
    flipped_vertically: Optional[bool] = Field(default=False, description="""True if the image is mirrored top-bottom.""", validation_alias=AliasChoices('flipped_vertically', 'IMAGE_FLIP_UD'), json_schema_extra = { "linkml_meta": {'aliases': ['IMAGE_FLIP_UD'],
         'domain_of': ['CameraDiagnosticElement'],
         'ifabsent': 'False'} })
    screen_name: Optional[str] = Field(default=None, description="""Name of the screen element to which this camera is attached.""", json_schema_extra = { "linkml_meta": {'domain_of': ['CameraDiagnosticElement']} })
    has_led: Optional[bool] = Field(default=True, description="""True if the camera mount includes an LED backlight.""", json_schema_extra = { "linkml_meta": {'domain_of': ['CameraDiagnosticElement'], 'ifabsent': 'True'} })
    pixel_results_indices: Optional[_CameraPixelResultsIndicesBase] = Field(default=None, description="""Indices of pixel analysis result arrays.""", json_schema_extra = { "linkml_meta": {'domain_of': ['CameraDiagnosticElement']} })
    pixel_results_names: Optional[_CameraPixelResultsNamesBase] = Field(default=None, description="""Names of pixel analysis result arrays.""", json_schema_extra = { "linkml_meta": {'domain_of': ['CameraDiagnosticElement']} })
    mask: Optional[_CameraMaskBase] = Field(default=None, description="""Camera analysis mask configuration.""", json_schema_extra = { "linkml_meta": {'domain_of': ['CameraDiagnosticElement']} })
    sensor: Optional[_CameraSensorBase] = Field(default=None, description="""Camera sensor hardware configuration.""", json_schema_extra = { "linkml_meta": {'domain_of': ['CameraDiagnosticElement']} })


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
    waist: float = Field(default=0, description="""Laser beam waist (1/e^2 radius) [m].""", ge=0.0, json_schema_extra = { "linkml_meta": {'domain_of': ['LaserElement'],
         'ifabsent': 'float(0)',
         'unit': {'ucum_code': 'm'}} })
    wavelength: Optional[float] = Field(default=None, description="""Laser wavelength [m].""", ge=0.0, json_schema_extra = { "linkml_meta": {'domain_of': ['LaserElement'], 'unit': {'ucum_code': 'm'}} })
    pulse_energy: Optional[float] = Field(default=None, description="""Laser pulse energy [J].""", ge=0.0, json_schema_extra = { "linkml_meta": {'domain_of': ['LaserElement'], 'unit': {'ucum_code': 'J'}} })
    pulse_duration_fwhm: Optional[float] = Field(default=None, description="""Pulse duration at FWHM [s].""", ge=0.0, json_schema_extra = { "linkml_meta": {'domain_of': ['LaserElement'], 'unit': {'ucum_code': 's'}} })
    focal_position: float = Field(default=0.0, description="""Focal (waist) position along the propagation axis [m].""", json_schema_extra = { "linkml_meta": {'domain_of': ['LaserElement'],
         'ifabsent': 'float(0.0)',
         'unit': {'ucum_code': 'm'}} })
    cep_phase: float = Field(default=0, description="""Carrier-envelope phase [rad].""", json_schema_extra = { "linkml_meta": {'domain_of': ['LaserElement'],
         'ifabsent': 'float(0)',
         'unit': {'ucum_code': 'rad'}} })
    polarization: Optional[LaserPolarizationEnum] = Field(default=None, description="""Laser polarization state.""", json_schema_extra = { "linkml_meta": {'domain_of': ['LaserElement']} })
    profile_type: Optional[LaserProfileTypeEnum] = Field(default=LaserProfileTypeEnum.gaussian, description="""Transverse intensity profile model.""", json_schema_extra = { "linkml_meta": {'domain_of': ['LaserElement'], 'ifabsent': 'string(gaussian)'} })
    laguerre_polynomial_order_p: int = Field(default=0, description="""Radial Laguerre-Gaussian mode index p (for ``profile_type = laguerre-gaussian``).""", ge=0, json_schema_extra = { "linkml_meta": {'domain_of': ['LaserElement'], 'ifabsent': 'int(0)'} })
    flatness: int = Field(default=6, description="""Flatness order N of a flattened-Gaussian profile (for ``profile_type = flattened-gaussian``).""", ge=1, json_schema_extra = { "linkml_meta": {'domain_of': ['LaserElement'], 'ifabsent': 'int(6)'} })


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
    species: str = Field(default="electron", description="""Plasma species name (e.g., ``electron``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['PlasmaElement'], 'ifabsent': 'string(electron)'} })
    ramp_up: float = Field(default=0.001, description="""Entrance density-ramp length [m].""", ge=0.0, json_schema_extra = { "linkml_meta": {'domain_of': ['PlasmaElement'],
         'ifabsent': 'float(0.001)',
         'unit': {'ucum_code': 'm'}} })
    plateau: float = Field(default=0.001, description="""Flat-top plateau length [m].""", ge=0.0, json_schema_extra = { "linkml_meta": {'domain_of': ['PlasmaElement'],
         'ifabsent': 'float(0.001)',
         'unit': {'ucum_code': 'm'}} })
    ramp_down: float = Field(default=0.001, description="""Exit density-ramp length [m].""", ge=0.0, json_schema_extra = { "linkml_meta": {'domain_of': ['PlasmaElement'],
         'ifabsent': 'float(0.001)',
         'unit': {'ucum_code': 'm'}} })
    ramp_decay_length: float = Field(default=0.001, description="""Exponential decay length of the density ramp [m].""", ge=0.0, json_schema_extra = { "linkml_meta": {'domain_of': ['PlasmaElement'],
         'ifabsent': 'float(0.001)',
         'unit': {'ucum_code': 'm'}} })
    density_profile: Optional[bool] = Field(default=False, description="""If True, use a user-defined profile; if False, use a flat-top model.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PlasmaElement'], 'ifabsent': 'False'} })
    parabolic_coefficient: float = Field(default=0, description="""Parabolic coefficient for a transverse density profile.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PlasmaElement'], 'ifabsent': 'float(0)'} })


class _PositionBase(ConfiguredBaseModel):
    """
    Cartesian position in the global accelerator coordinate system. All components are in metres.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:Position',
         'from_schema': 'https://w3id.org/laura/schema',
         'in_subset': ['physical_properties']})

    x: float = Field(default=0, description="""Horizontal component [m].""", validation_alias=AliasChoices('x', 'X_POS'), json_schema_extra = { "linkml_meta": {'domain_of': ['CameraPixelResultsIndices',
                       'CameraPixelResultsNames',
                       'Position'],
         'ifabsent': 'float(0)',
         'unit': {'ucum_code': 'm'}} })
    y: float = Field(default=0, description="""Vertical component [m].""", validation_alias=AliasChoices('y', 'Y_POS'), json_schema_extra = { "linkml_meta": {'domain_of': ['CameraPixelResultsIndices',
                       'CameraPixelResultsNames',
                       'Position'],
         'ifabsent': 'float(0)',
         'unit': {'ucum_code': 'm'}} })
    z: float = Field(default=0, description="""Longitudinal (beam-direction) component [m].""", json_schema_extra = { "linkml_meta": {'domain_of': ['Position'], 'ifabsent': 'float(0)', 'unit': {'ucum_code': 'm'}} })


class _RotationBase(ConfiguredBaseModel):
    """
    Euler-angle rotation relative to the global coordinate system. All angles are in radians, bounded to [-pi, pi].
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:Rotation',
         'from_schema': 'https://w3id.org/laura/schema',
         'in_subset': ['physical_properties']})

    phi: float = Field(default=0, description="""Rotation about the horizontal (x) axis [rad].""", ge=-3.141592653589793, le=3.141592653589793, json_schema_extra = { "linkml_meta": {'domain_of': ['Rotation'],
         'ifabsent': 'float(0)',
         'unit': {'ucum_code': 'rad'}} })
    psi: float = Field(default=0, description="""Rotation about the vertical (y) axis [rad].""", ge=-3.141592653589793, le=3.141592653589793, json_schema_extra = { "linkml_meta": {'domain_of': ['Rotation'],
         'ifabsent': 'float(0)',
         'unit': {'ucum_code': 'rad'}} })
    theta: float = Field(default=0, description="""Rotation about the longitudinal (z) axis [rad].""", ge=-3.141592653589793, le=3.141592653589793, json_schema_extra = { "linkml_meta": {'domain_of': ['Rotation'],
         'ifabsent': 'float(0)',
         'unit': {'ucum_code': 'rad'}} })


class _ElementPositionErrorBase(ConfiguredBaseModel):
    """
    Alignment position and rotation errors for a physically-located element.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:ElementPositionError',
         'from_schema': 'https://w3id.org/laura/schema'})

    position: Optional[_PositionBase] = Field(default=None, description="""Positional misalignment error [m].""", json_schema_extra = { "linkml_meta": {'domain_of': ['ElementPositionError', 'ElementSurvey']} })
    rotation: Optional[_RotationBase] = Field(default=None, description="""Angular misalignment error [rad].""", json_schema_extra = { "linkml_meta": {'domain_of': ['CameraDiagnosticElement',
                       'ElementPositionError',
                       'ElementSurvey',
                       'PhysicalElement']} })


class _ElementSurveyBase(ConfiguredBaseModel):
    """
    Survey-measured position and rotation of an element. Structure is identical to ElementPositionError.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:ElementSurvey',
         'from_schema': 'https://w3id.org/laura/schema'})

    position: Optional[_PositionBase] = Field(default=None, description="""Surveyed position.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ElementPositionError', 'ElementSurvey']} })
    rotation: Optional[_RotationBase] = Field(default=None, description="""Surveyed rotation.""", json_schema_extra = { "linkml_meta": {'domain_of': ['CameraDiagnosticElement',
                       'ElementPositionError',
                       'ElementSurvey',
                       'PhysicalElement']} })


class _PhysicalElementBase(ConfiguredBaseModel):
    """
    Physical placement data: position, rotation, length, and associated survey / alignment-error information.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:PhysicalElement',
         'from_schema': 'https://w3id.org/laura/schema',
         'in_subset': ['physical_properties']})

    middle: Optional[_PositionBase] = Field(default=None, description="""Longitudinal midpoint (centre) of the element. Also accepted as ``position`` or ``centre`` in YAML.""", validation_alias=AliasChoices('middle', 'position', 'centre'), json_schema_extra = { "linkml_meta": {'aliases': ['position', 'centre'],
         'domain_of': ['CameraMask', 'CameraSensor', 'PhysicalElement']} })
    datum: Optional[_PositionBase] = Field(default=None, description="""Datum reference position.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PhysicalElement']} })
    rotation: Optional[_RotationBase] = Field(default=None, description="""Local rotation in the global frame.""", json_schema_extra = { "linkml_meta": {'domain_of': ['CameraDiagnosticElement',
                       'ElementPositionError',
                       'ElementSurvey',
                       'PhysicalElement']} })
    global_rotation: Optional[_RotationBase] = Field(default=None, description="""Accumulated global rotation including parent-frame contributions.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PhysicalElement']} })
    error: Optional[_ElementPositionErrorBase] = Field(default=None, description="""Alignment errors.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PhysicalElement']} })
    survey: Optional[_ElementSurveyBase] = Field(default=None, description="""Survey-measured position and rotation.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PhysicalElement']} })
    length: float = Field(default=0, description="""Effective length along the beam axis [m].""", ge=0.0, json_schema_extra = { "linkml_meta": {'domain_of': ['PhysicalElement'],
         'ifabsent': 'float(0)',
         'unit': {'ucum_code': 'm'}} })
    maximum_position: Optional[float] = Field(default=None, description="""Maximum downstream s-coordinate [m].""", json_schema_extra = { "linkml_meta": {'domain_of': ['PhysicalElement'], 'unit': {'ucum_code': 'm'}} })
    minimum_position: Optional[float] = Field(default=None, description="""Minimum upstream s-coordinate [m].""", json_schema_extra = { "linkml_meta": {'domain_of': ['PhysicalElement'], 'unit': {'ucum_code': 'm'}} })
    physical_angle: float = Field(default=0, description="""Bending angle in the horizontal plane [rad]. Derived from ``magnetic.angle`` when available.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PhysicalElement'],
         'ifabsent': 'float(0)',
         'unit': {'ucum_code': 'rad'}} })


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
    max_i: float = Field(default=0, description="""Maximum current [A].""", validation_alias=AliasChoices('max_i', 'maxI'), json_schema_extra = { "linkml_meta": {'aliases': ['maxI'],
         'domain_of': ['ElectricalElement'],
         'ifabsent': 'float(0)',
         'unit': {'ucum_code': 'A'}} })
    read_tolerance: float = Field(default=0.1, description="""Read-back vs. set-point tolerance fraction (default 0.1 = 10 %).""", validation_alias=AliasChoices('read_tolerance', 'ri_tolerance'), json_schema_extra = { "linkml_meta": {'aliases': ['ri_tolerance'],
         'domain_of': ['ElectricalElement'],
         'ifabsent': 'float(0.1)'} })


class _ManufacturerElementBase(ConfiguredBaseModel):
    """
    Manufacturer and serial-number metadata.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:ManufacturerElement',
         'from_schema': 'https://w3id.org/laura/schema'})

    manufacturer: str = Field(default="", description="""Name of the manufacturer.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ManufacturerElement', 'StandardElement'],
         'ifabsent': 'string()',
         'slot_uri': 'schema:manufacturer'} })
    serial_number: str = Field(default="", description="""Manufacturer serial number.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ManufacturerElement'],
         'ifabsent': 'string()',
         'slot_uri': 'schema:serialNumber'} })


class _ReferenceElementBase(ConfiguredBaseModel):
    """
    Links to engineering drawings and design files.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:ReferenceElement',
         'from_schema': 'https://w3id.org/laura/schema'})

    drawings: list[str] = Field(default_factory=list, description="""Engineering-drawing identifiers or URIs.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ReferenceElement']} })
    design_files: list[str] = Field(default_factory=list, description="""Design-file paths or URIs.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ReferenceElement']} })


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

    variables: list[_ControlVariableBase] = Field(default_factory=list, description="""Named control variables keyed by logical name.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ControlsInformation']} })


class _ShutterElementBase(ConfiguredBaseModel):
    """
    Shutter interlock configuration.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:ShutterElement',
         'from_schema': 'https://w3id.org/laura/schema'})

    interlocks: list[str] = Field(default_factory=list, description="""Names of the interlocks guarding this shutter.""", validation_alias=AliasChoices('interlocks', 'shutter_interlock_names'), json_schema_extra = { "linkml_meta": {'aliases': ['shutter_interlock_names'], 'domain_of': ['ShutterElement']} })


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


class _AcceleratorElementBase(ConfiguredBaseModel):
    """
    Root base class for all LAURA accelerator elements.  Every lattice element is an instance of a concrete subclass identified by ``hardware_type``.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:AcceleratorElement',
         'from_schema': 'https://w3id.org/laura/schema',
         'tree_root': True})

    name: str = Field(default=..., description="""Unique element name within the machine.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement', 'SectionLattice', 'MachineLayout']} })
    hardware_class: HardwareClassEnum = Field(default=..., description="""Functional category (e.g., ``Magnet``, ``Diagnostic``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    hardware_type: str = Field(default="Generic", description="""Python class name used for MODEL_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string(Generic)'} })
    hardware_model: str = Field(default="Generic", description="""Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string(Generic)'} })
    machine_area: Optional[str] = Field(default=None, description="""Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    virtual_name: str = Field(default="", description="""Alternative internal name used by the control system when the physical name is inaccessible.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string()'} })
    alias: list[str] = Field(default_factory=list, description="""Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.""", validation_alias=AliasChoices('alias', 'name_alias'), json_schema_extra = { "linkml_meta": {'aliases': ['name_alias'], 'domain_of': ['AcceleratorElement']} })
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
    hardware_class: HardwareClassEnum = Field(default=..., description="""Functional category (e.g., ``Magnet``, ``Diagnostic``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    hardware_type: str = Field(default="Generic", description="""Python class name used for MODEL_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string(Generic)'} })
    hardware_model: str = Field(default="Generic", description="""Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string(Generic)'} })
    machine_area: Optional[str] = Field(default=None, description="""Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    virtual_name: str = Field(default="", description="""Alternative internal name used by the control system when the physical name is inaccessible.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string()'} })
    alias: list[str] = Field(default_factory=list, description="""Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.""", validation_alias=AliasChoices('alias', 'name_alias'), json_schema_extra = { "linkml_meta": {'aliases': ['name_alias'], 'domain_of': ['AcceleratorElement']} })
    subelement: Optional[str] = Field(default=None, description="""If set, this element is a logical sub-component of the named parent element.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })


class _ElementBase(_StandardElementBase):
    """
    Concrete schema counterpart of the Python ``Element`` wrapper class. Inherits standard element composition fields.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:Element', 'from_schema': 'https://w3id.org/laura/schema'})

    simulation: Optional[_SimulationElementBase] = Field(default=None, description="""Simulation / tracking attributes.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    electrical: Optional[_ElectricalElementBase] = Field(default=None, description="""Power-supply electrical limits.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    manufacturer: Optional[_ManufacturerElementBase] = Field(default=None, description="""Manufacturer and serial-number data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ManufacturerElement', 'StandardElement']} })
    controls: Optional[_ControlsInformationBase] = Field(default=None, description="""Control-system process-variable definitions.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    reference: Optional[_ReferenceElementBase] = Field(default=None, description="""Links to design drawings and files.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    name: str = Field(default=..., description="""Unique element name within the machine.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement', 'SectionLattice', 'MachineLayout']} })
    hardware_class: HardwareClassEnum = Field(default=..., description="""Functional category (e.g., ``Magnet``, ``Diagnostic``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    hardware_type: str = Field(default="Generic", description="""Python class name used for MODEL_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string(Generic)'} })
    hardware_model: str = Field(default="Generic", description="""Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string(Generic)'} })
    machine_area: Optional[str] = Field(default=None, description="""Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    virtual_name: str = Field(default="", description="""Alternative internal name used by the control system when the physical name is inaccessible.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string()'} })
    alias: list[str] = Field(default_factory=list, description="""Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.""", validation_alias=AliasChoices('alias', 'name_alias'), json_schema_extra = { "linkml_meta": {'aliases': ['name_alias'], 'domain_of': ['AcceleratorElement']} })
    subelement: Optional[str] = Field(default=None, description="""If set, this element is a logical sub-component of the named parent element.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })


class _PhysicalAcceleratorElementBase(_ElementBase):
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
    hardware_class: HardwareClassEnum = Field(default=..., description="""Functional category (e.g., ``Magnet``, ``Diagnostic``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    hardware_type: str = Field(default="Generic", description="""Python class name used for MODEL_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string(Generic)'} })
    hardware_model: str = Field(default="Generic", description="""Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string(Generic)'} })
    machine_area: Optional[str] = Field(default=None, description="""Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    virtual_name: str = Field(default="", description="""Alternative internal name used by the control system when the physical name is inaccessible.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string()'} })
    alias: list[str] = Field(default_factory=list, description="""Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.""", validation_alias=AliasChoices('alias', 'name_alias'), json_schema_extra = { "linkml_meta": {'aliases': ['name_alias'], 'domain_of': ['AcceleratorElement']} })
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
    hardware_class: HardwareClassEnum = Field(default=..., description="""Functional category (e.g., ``Magnet``, ``Diagnostic``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    hardware_type: str = Field(default="Generic", description="""Python class name used for MODEL_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string(Generic)'} })
    hardware_model: str = Field(default="Generic", description="""Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string(Generic)'} })
    machine_area: Optional[str] = Field(default=None, description="""Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    virtual_name: str = Field(default="", description="""Alternative internal name used by the control system when the physical name is inaccessible.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string()'} })
    alias: list[str] = Field(default_factory=list, description="""Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.""", validation_alias=AliasChoices('alias', 'name_alias'), json_schema_extra = { "linkml_meta": {'aliases': ['name_alias'], 'domain_of': ['AcceleratorElement']} })
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
    hardware_class: HardwareClassEnum = Field(default=..., description="""Functional category (e.g., ``Magnet``, ``Diagnostic``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    hardware_type: str = Field(default="Generic", description="""Python class name used for MODEL_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string(Generic)'} })
    hardware_model: str = Field(default="Generic", description="""Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string(Generic)'} })
    machine_area: Optional[str] = Field(default=None, description="""Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    virtual_name: str = Field(default="", description="""Alternative internal name used by the control system when the physical name is inaccessible.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string()'} })
    alias: list[str] = Field(default_factory=list, description="""Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.""", validation_alias=AliasChoices('alias', 'name_alias'), json_schema_extra = { "linkml_meta": {'aliases': ['name_alias'], 'domain_of': ['AcceleratorElement']} })
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
    hardware_class: HardwareClassEnum = Field(default=..., description="""Functional category (e.g., ``Magnet``, ``Diagnostic``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    hardware_type: Optional[Literal["Beam_Position_Monitor"]] = Field(default="Generic", description="""Python class name used for MODEL_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'],
         'equals_string': 'Beam_Position_Monitor',
         'ifabsent': 'string(Generic)'} })
    hardware_model: str = Field(default="Generic", description="""Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string(Generic)'} })
    machine_area: Optional[str] = Field(default=None, description="""Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    virtual_name: str = Field(default="", description="""Alternative internal name used by the control system when the physical name is inaccessible.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string()'} })
    alias: list[str] = Field(default_factory=list, description="""Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.""", validation_alias=AliasChoices('alias', 'name_alias'), json_schema_extra = { "linkml_meta": {'aliases': ['name_alias'], 'domain_of': ['AcceleratorElement']} })
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
    hardware_class: HardwareClassEnum = Field(default=..., description="""Functional category (e.g., ``Magnet``, ``Diagnostic``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    hardware_type: Optional[Literal["Beam_Arrival_Monitor"]] = Field(default="Generic", description="""Python class name used for MODEL_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'],
         'equals_string': 'Beam_Arrival_Monitor',
         'ifabsent': 'string(Generic)'} })
    hardware_model: str = Field(default="Generic", description="""Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string(Generic)'} })
    machine_area: Optional[str] = Field(default=None, description="""Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    virtual_name: str = Field(default="", description="""Alternative internal name used by the control system when the physical name is inaccessible.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string()'} })
    alias: list[str] = Field(default_factory=list, description="""Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.""", validation_alias=AliasChoices('alias', 'name_alias'), json_schema_extra = { "linkml_meta": {'aliases': ['name_alias'], 'domain_of': ['AcceleratorElement']} })
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
    hardware_class: HardwareClassEnum = Field(default=..., description="""Functional category (e.g., ``Magnet``, ``Diagnostic``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    hardware_type: Optional[Literal["Bunch_Length_Monitor"]] = Field(default="Generic", description="""Python class name used for MODEL_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'],
         'equals_string': 'Bunch_Length_Monitor',
         'ifabsent': 'string(Generic)'} })
    hardware_model: str = Field(default="Generic", description="""Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string(Generic)'} })
    machine_area: Optional[str] = Field(default=None, description="""Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    virtual_name: str = Field(default="", description="""Alternative internal name used by the control system when the physical name is inaccessible.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string()'} })
    alias: list[str] = Field(default_factory=list, description="""Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.""", validation_alias=AliasChoices('alias', 'name_alias'), json_schema_extra = { "linkml_meta": {'aliases': ['name_alias'], 'domain_of': ['AcceleratorElement']} })
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
    hardware_class: HardwareClassEnum = Field(default=..., description="""Functional category (e.g., ``Magnet``, ``Diagnostic``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    hardware_type: Optional[Literal["Camera"]] = Field(default="Generic", description="""Python class name used for MODEL_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'],
         'equals_string': 'Camera',
         'ifabsent': 'string(Generic)'} })
    hardware_model: str = Field(default="Generic", description="""Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string(Generic)'} })
    machine_area: Optional[str] = Field(default=None, description="""Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    virtual_name: str = Field(default="", description="""Alternative internal name used by the control system when the physical name is inaccessible.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string()'} })
    alias: list[str] = Field(default_factory=list, description="""Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.""", validation_alias=AliasChoices('alias', 'name_alias'), json_schema_extra = { "linkml_meta": {'aliases': ['name_alias'], 'domain_of': ['AcceleratorElement']} })
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
    hardware_class: HardwareClassEnum = Field(default=..., description="""Functional category (e.g., ``Magnet``, ``Diagnostic``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    hardware_type: Optional[Literal["Screen"]] = Field(default="Generic", description="""Python class name used for MODEL_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'],
         'equals_string': 'Screen',
         'ifabsent': 'string(Generic)'} })
    hardware_model: str = Field(default="Generic", description="""Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string(Generic)'} })
    machine_area: Optional[str] = Field(default=None, description="""Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    virtual_name: str = Field(default="", description="""Alternative internal name used by the control system when the physical name is inaccessible.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string()'} })
    alias: list[str] = Field(default_factory=list, description="""Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.""", validation_alias=AliasChoices('alias', 'name_alias'), json_schema_extra = { "linkml_meta": {'aliases': ['name_alias'], 'domain_of': ['AcceleratorElement']} })
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
    hardware_class: HardwareClassEnum = Field(default=..., description="""Functional category (e.g., ``Magnet``, ``Diagnostic``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    hardware_type: Optional[Literal["ChargeDiagnostic"]] = Field(default="Generic", description="""Python class name used for MODEL_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'],
         'equals_string': 'ChargeDiagnostic',
         'ifabsent': 'string(Generic)'} })
    hardware_model: str = Field(default="Generic", description="""Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string(Generic)'} })
    machine_area: Optional[str] = Field(default=None, description="""Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    virtual_name: str = Field(default="", description="""Alternative internal name used by the control system when the physical name is inaccessible.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string()'} })
    alias: list[str] = Field(default_factory=list, description="""Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.""", validation_alias=AliasChoices('alias', 'name_alias'), json_schema_extra = { "linkml_meta": {'aliases': ['name_alias'], 'domain_of': ['AcceleratorElement']} })
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
    hardware_class: HardwareClassEnum = Field(default=..., description="""Functional category (e.g., ``Magnet``, ``Diagnostic``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    hardware_type: Optional[Literal["Wall_Current_Monitor"]] = Field(default="Generic", description="""Python class name used for MODEL_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'],
         'equals_string': 'Wall_Current_Monitor',
         'ifabsent': 'string(Generic)'} })
    hardware_model: str = Field(default="Generic", description="""Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string(Generic)'} })
    machine_area: Optional[str] = Field(default=None, description="""Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    virtual_name: str = Field(default="", description="""Alternative internal name used by the control system when the physical name is inaccessible.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string()'} })
    alias: list[str] = Field(default_factory=list, description="""Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.""", validation_alias=AliasChoices('alias', 'name_alias'), json_schema_extra = { "linkml_meta": {'aliases': ['name_alias'], 'domain_of': ['AcceleratorElement']} })
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
    hardware_class: HardwareClassEnum = Field(default=..., description="""Functional category (e.g., ``Magnet``, ``Diagnostic``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    hardware_type: Optional[Literal["Faraday_Cup_Monitor"]] = Field(default="Generic", description="""Python class name used for MODEL_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'],
         'equals_string': 'Faraday_Cup_Monitor',
         'ifabsent': 'string(Generic)'} })
    hardware_model: str = Field(default="Generic", description="""Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string(Generic)'} })
    machine_area: Optional[str] = Field(default=None, description="""Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    virtual_name: str = Field(default="", description="""Alternative internal name used by the control system when the physical name is inaccessible.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string()'} })
    alias: list[str] = Field(default_factory=list, description="""Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.""", validation_alias=AliasChoices('alias', 'name_alias'), json_schema_extra = { "linkml_meta": {'aliases': ['name_alias'], 'domain_of': ['AcceleratorElement']} })
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
    hardware_class: HardwareClassEnum = Field(default=..., description="""Functional category (e.g., ``Magnet``, ``Diagnostic``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    hardware_type: Optional[Literal["Integrated_Current_Transformer"]] = Field(default="Generic", description="""Python class name used for MODEL_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'],
         'equals_string': 'Integrated_Current_Transformer',
         'ifabsent': 'string(Generic)'} })
    hardware_model: str = Field(default="Generic", description="""Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string(Generic)'} })
    machine_area: Optional[str] = Field(default=None, description="""Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    virtual_name: str = Field(default="", description="""Alternative internal name used by the control system when the physical name is inaccessible.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string()'} })
    alias: list[str] = Field(default_factory=list, description="""Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.""", validation_alias=AliasChoices('alias', 'name_alias'), json_schema_extra = { "linkml_meta": {'aliases': ['name_alias'], 'domain_of': ['AcceleratorElement']} })
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
    hardware_class: HardwareClassEnum = Field(default=..., description="""Functional category (e.g., ``Magnet``, ``Diagnostic``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    hardware_type: Optional[Literal["RFCavity"]] = Field(default="Generic", description="""Python class name used for MODEL_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'],
         'equals_string': 'RFCavity',
         'ifabsent': 'string(Generic)'} })
    hardware_model: str = Field(default="Generic", description="""Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string(Generic)'} })
    machine_area: Optional[str] = Field(default=None, description="""Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    virtual_name: str = Field(default="", description="""Alternative internal name used by the control system when the physical name is inaccessible.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string()'} })
    alias: list[str] = Field(default_factory=list, description="""Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.""", validation_alias=AliasChoices('alias', 'name_alias'), json_schema_extra = { "linkml_meta": {'aliases': ['name_alias'], 'domain_of': ['AcceleratorElement']} })
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
    hardware_class: HardwareClassEnum = Field(default=..., description="""Functional category (e.g., ``Magnet``, ``Diagnostic``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    hardware_type: Optional[Literal["RFDeflectingCavity"]] = Field(default="Generic", description="""Python class name used for MODEL_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'],
         'equals_string': 'RFDeflectingCavity',
         'ifabsent': 'string(Generic)'} })
    hardware_model: str = Field(default="Generic", description="""Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string(Generic)'} })
    machine_area: Optional[str] = Field(default=None, description="""Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    virtual_name: str = Field(default="", description="""Alternative internal name used by the control system when the physical name is inaccessible.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string()'} })
    alias: list[str] = Field(default_factory=list, description="""Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.""", validation_alias=AliasChoices('alias', 'name_alias'), json_schema_extra = { "linkml_meta": {'aliases': ['name_alias'], 'domain_of': ['AcceleratorElement']} })
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
    hardware_class: HardwareClassEnum = Field(default=..., description="""Functional category (e.g., ``Magnet``, ``Diagnostic``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    hardware_type: Optional[Literal["Wakefield"]] = Field(default="Generic", description="""Python class name used for MODEL_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'],
         'equals_string': 'Wakefield',
         'ifabsent': 'string(Generic)'} })
    hardware_model: str = Field(default="Generic", description="""Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string(Generic)'} })
    machine_area: Optional[str] = Field(default=None, description="""Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    virtual_name: str = Field(default="", description="""Alternative internal name used by the control system when the physical name is inaccessible.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string()'} })
    alias: list[str] = Field(default_factory=list, description="""Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.""", validation_alias=AliasChoices('alias', 'name_alias'), json_schema_extra = { "linkml_meta": {'aliases': ['name_alias'], 'domain_of': ['AcceleratorElement']} })
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
    hardware_class: HardwareClassEnum = Field(default=..., description="""Functional category (e.g., ``Magnet``, ``Diagnostic``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    hardware_type: Optional[Literal["Low_Level_RF"]] = Field(default="Generic", description="""Python class name used for MODEL_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'],
         'equals_string': 'Low_Level_RF',
         'ifabsent': 'string(Generic)'} })
    hardware_model: str = Field(default="Generic", description="""Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string(Generic)'} })
    machine_area: Optional[str] = Field(default=None, description="""Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    virtual_name: str = Field(default="", description="""Alternative internal name used by the control system when the physical name is inaccessible.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string()'} })
    alias: list[str] = Field(default_factory=list, description="""Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.""", validation_alias=AliasChoices('alias', 'name_alias'), json_schema_extra = { "linkml_meta": {'aliases': ['name_alias'], 'domain_of': ['AcceleratorElement']} })
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
    hardware_class: HardwareClassEnum = Field(default=..., description="""Functional category (e.g., ``Magnet``, ``Diagnostic``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    hardware_type: Optional[Literal["RFModulator"]] = Field(default="Generic", description="""Python class name used for MODEL_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'],
         'equals_string': 'RFModulator',
         'ifabsent': 'string(Generic)'} })
    hardware_model: str = Field(default="Generic", description="""Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string(Generic)'} })
    machine_area: Optional[str] = Field(default=None, description="""Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    virtual_name: str = Field(default="", description="""Alternative internal name used by the control system when the physical name is inaccessible.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string()'} })
    alias: list[str] = Field(default_factory=list, description="""Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.""", validation_alias=AliasChoices('alias', 'name_alias'), json_schema_extra = { "linkml_meta": {'aliases': ['name_alias'], 'domain_of': ['AcceleratorElement']} })
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
    hardware_class: HardwareClassEnum = Field(default=..., description="""Functional category (e.g., ``Magnet``, ``Diagnostic``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    hardware_type: Optional[Literal["RFProtection"]] = Field(default="Generic", description="""Python class name used for MODEL_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'],
         'equals_string': 'RFProtection',
         'ifabsent': 'string(Generic)'} })
    hardware_model: str = Field(default="Generic", description="""Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string(Generic)'} })
    machine_area: Optional[str] = Field(default=None, description="""Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    virtual_name: str = Field(default="", description="""Alternative internal name used by the control system when the physical name is inaccessible.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string()'} })
    alias: list[str] = Field(default_factory=list, description="""Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.""", validation_alias=AliasChoices('alias', 'name_alias'), json_schema_extra = { "linkml_meta": {'aliases': ['name_alias'], 'domain_of': ['AcceleratorElement']} })
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
    hardware_class: HardwareClassEnum = Field(default=..., description="""Functional category (e.g., ``Magnet``, ``Diagnostic``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    hardware_type: Optional[Literal["RFHeartbeat"]] = Field(default="Generic", description="""Python class name used for MODEL_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'],
         'equals_string': 'RFHeartbeat',
         'ifabsent': 'string(Generic)'} })
    hardware_model: str = Field(default="Generic", description="""Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string(Generic)'} })
    machine_area: Optional[str] = Field(default=None, description="""Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    virtual_name: str = Field(default="", description="""Alternative internal name used by the control system when the physical name is inaccessible.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string()'} })
    alias: list[str] = Field(default_factory=list, description="""Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.""", validation_alias=AliasChoices('alias', 'name_alias'), json_schema_extra = { "linkml_meta": {'aliases': ['name_alias'], 'domain_of': ['AcceleratorElement']} })
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
    hardware_class: HardwareClassEnum = Field(default=..., description="""Functional category (e.g., ``Magnet``, ``Diagnostic``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    hardware_type: Optional[Literal["PID"]] = Field(default="Generic", description="""Python class name used for MODEL_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'],
         'equals_string': 'PID',
         'ifabsent': 'string(Generic)'} })
    hardware_model: str = Field(default="Generic", description="""Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string(Generic)'} })
    machine_area: Optional[str] = Field(default=None, description="""Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    virtual_name: str = Field(default="", description="""Alternative internal name used by the control system when the physical name is inaccessible.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string()'} })
    alias: list[str] = Field(default_factory=list, description="""Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.""", validation_alias=AliasChoices('alias', 'name_alias'), json_schema_extra = { "linkml_meta": {'aliases': ['name_alias'], 'domain_of': ['AcceleratorElement']} })
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
    hardware_class: HardwareClassEnum = Field(default=..., description="""Functional category (e.g., ``Magnet``, ``Diagnostic``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    hardware_type: Optional[Literal["TwissMatch"]] = Field(default="Generic", description="""Python class name used for MODEL_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'],
         'equals_string': 'TwissMatch',
         'ifabsent': 'string(Generic)'} })
    hardware_model: str = Field(default="Generic", description="""Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string(Generic)'} })
    machine_area: Optional[str] = Field(default=None, description="""Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    virtual_name: str = Field(default="", description="""Alternative internal name used by the control system when the physical name is inaccessible.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string()'} })
    alias: list[str] = Field(default_factory=list, description="""Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.""", validation_alias=AliasChoices('alias', 'name_alias'), json_schema_extra = { "linkml_meta": {'aliases': ['name_alias'], 'domain_of': ['AcceleratorElement']} })
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
    hardware_class: HardwareClassEnum = Field(default=..., description="""Functional category (e.g., ``Magnet``, ``Diagnostic``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    hardware_type: Optional[Literal["Stage"]] = Field(default="Generic", description="""Python class name used for MODEL_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'],
         'equals_string': 'Stage',
         'ifabsent': 'string(Generic)'} })
    hardware_model: str = Field(default="Generic", description="""Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string(Generic)'} })
    machine_area: Optional[str] = Field(default=None, description="""Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    virtual_name: str = Field(default="", description="""Alternative internal name used by the control system when the physical name is inaccessible.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string()'} })
    alias: list[str] = Field(default_factory=list, description="""Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.""", validation_alias=AliasChoices('alias', 'name_alias'), json_schema_extra = { "linkml_meta": {'aliases': ['name_alias'], 'domain_of': ['AcceleratorElement']} })
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
    hardware_class: HardwareClassEnum = Field(default=..., description="""Functional category (e.g., ``Magnet``, ``Diagnostic``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    hardware_type: Optional[Literal["VacuumGauge"]] = Field(default="Generic", description="""Python class name used for MODEL_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'],
         'equals_string': 'VacuumGauge',
         'ifabsent': 'string(Generic)'} })
    hardware_model: str = Field(default="Generic", description="""Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string(Generic)'} })
    machine_area: Optional[str] = Field(default=None, description="""Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    virtual_name: str = Field(default="", description="""Alternative internal name used by the control system when the physical name is inaccessible.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string()'} })
    alias: list[str] = Field(default_factory=list, description="""Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.""", validation_alias=AliasChoices('alias', 'name_alias'), json_schema_extra = { "linkml_meta": {'aliases': ['name_alias'], 'domain_of': ['AcceleratorElement']} })
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

    laser: Optional[_LaserElementBase] = Field(default=None, description="""Laser-beam parameters.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Laser',
                       'Plasma',
                       'LaserEnergyMeter',
                       'LaserHalfWavePlate',
                       'LaserMirror']} })
    physical: Optional[_PhysicalElementBase] = Field(default=None, description="""Position, rotation, and length data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PhysicalAcceleratorElement'],
         'in_subset': ['physical_properties']} })
    simulation: Optional[_SimulationElementBase] = Field(default=None, description="""Simulation / tracking attributes.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    electrical: Optional[_ElectricalElementBase] = Field(default=None, description="""Power-supply electrical limits.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    manufacturer: Optional[_ManufacturerElementBase] = Field(default=None, description="""Manufacturer and serial-number data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ManufacturerElement', 'StandardElement']} })
    controls: Optional[_ControlsInformationBase] = Field(default=None, description="""Control-system process-variable definitions.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    reference: Optional[_ReferenceElementBase] = Field(default=None, description="""Links to design drawings and files.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    name: str = Field(default=..., description="""Unique element name within the machine.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement', 'SectionLattice', 'MachineLayout']} })
    hardware_class: HardwareClassEnum = Field(default=..., description="""Functional category (e.g., ``Magnet``, ``Diagnostic``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    hardware_type: Optional[Literal["Laser"]] = Field(default="Generic", description="""Python class name used for MODEL_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'],
         'equals_string': 'Laser',
         'ifabsent': 'string(Generic)'} })
    hardware_model: str = Field(default="Generic", description="""Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string(Generic)'} })
    machine_area: Optional[str] = Field(default=None, description="""Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    virtual_name: str = Field(default="", description="""Alternative internal name used by the control system when the physical name is inaccessible.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string()'} })
    alias: list[str] = Field(default_factory=list, description="""Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.""", validation_alias=AliasChoices('alias', 'name_alias'), json_schema_extra = { "linkml_meta": {'aliases': ['name_alias'], 'domain_of': ['AcceleratorElement']} })
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
    hardware_class: HardwareClassEnum = Field(default=..., description="""Functional category (e.g., ``Magnet``, ``Diagnostic``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    hardware_type: Optional[Literal["Shutter"]] = Field(default="Generic", description="""Python class name used for MODEL_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'],
         'equals_string': 'Shutter',
         'ifabsent': 'string(Generic)'} })
    hardware_model: str = Field(default="Generic", description="""Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string(Generic)'} })
    machine_area: Optional[str] = Field(default=None, description="""Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    virtual_name: str = Field(default="", description="""Alternative internal name used by the control system when the physical name is inaccessible.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string()'} })
    alias: list[str] = Field(default_factory=list, description="""Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.""", validation_alias=AliasChoices('alias', 'name_alias'), json_schema_extra = { "linkml_meta": {'aliases': ['name_alias'], 'domain_of': ['AcceleratorElement']} })
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
    hardware_class: HardwareClassEnum = Field(default=..., description="""Functional category (e.g., ``Magnet``, ``Diagnostic``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    hardware_type: Optional[Literal["Valve"]] = Field(default="Generic", description="""Python class name used for MODEL_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'],
         'equals_string': 'Valve',
         'ifabsent': 'string(Generic)'} })
    hardware_model: str = Field(default="Generic", description="""Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string(Generic)'} })
    machine_area: Optional[str] = Field(default=None, description="""Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    virtual_name: str = Field(default="", description="""Alternative internal name used by the control system when the physical name is inaccessible.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string()'} })
    alias: list[str] = Field(default_factory=list, description="""Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.""", validation_alias=AliasChoices('alias', 'name_alias'), json_schema_extra = { "linkml_meta": {'aliases': ['name_alias'], 'domain_of': ['AcceleratorElement']} })
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
    hardware_class: HardwareClassEnum = Field(default=..., description="""Functional category (e.g., ``Magnet``, ``Diagnostic``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    hardware_type: Optional[Literal["Marker"]] = Field(default="Generic", description="""Python class name used for MODEL_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'],
         'equals_string': 'Marker',
         'ifabsent': 'string(Generic)'} })
    hardware_model: str = Field(default="Generic", description="""Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string(Generic)'} })
    machine_area: Optional[str] = Field(default=None, description="""Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    virtual_name: str = Field(default="", description="""Alternative internal name used by the control system when the physical name is inaccessible.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string()'} })
    alias: list[str] = Field(default_factory=list, description="""Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.""", validation_alias=AliasChoices('alias', 'name_alias'), json_schema_extra = { "linkml_meta": {'aliases': ['name_alias'], 'domain_of': ['AcceleratorElement']} })
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
    hardware_class: HardwareClassEnum = Field(default=..., description="""Functional category (e.g., ``Magnet``, ``Diagnostic``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    hardware_type: Optional[Literal["Aperture"]] = Field(default="Generic", description="""Python class name used for MODEL_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'],
         'equals_string': 'Aperture',
         'ifabsent': 'string(Generic)'} })
    hardware_model: str = Field(default="Generic", description="""Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string(Generic)'} })
    machine_area: Optional[str] = Field(default=None, description="""Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    virtual_name: str = Field(default="", description="""Alternative internal name used by the control system when the physical name is inaccessible.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string()'} })
    alias: list[str] = Field(default_factory=list, description="""Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.""", validation_alias=AliasChoices('alias', 'name_alias'), json_schema_extra = { "linkml_meta": {'aliases': ['name_alias'], 'domain_of': ['AcceleratorElement']} })
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
    hardware_class: HardwareClassEnum = Field(default=..., description="""Functional category (e.g., ``Magnet``, ``Diagnostic``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    hardware_type: Optional[Literal["Collimator"]] = Field(default="Generic", description="""Python class name used for MODEL_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'],
         'equals_string': 'Collimator',
         'ifabsent': 'string(Generic)'} })
    hardware_model: str = Field(default="Generic", description="""Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string(Generic)'} })
    machine_area: Optional[str] = Field(default=None, description="""Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    virtual_name: str = Field(default="", description="""Alternative internal name used by the control system when the physical name is inaccessible.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string()'} })
    alias: list[str] = Field(default_factory=list, description="""Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.""", validation_alias=AliasChoices('alias', 'name_alias'), json_schema_extra = { "linkml_meta": {'aliases': ['name_alias'], 'domain_of': ['AcceleratorElement']} })
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
    hardware_class: HardwareClassEnum = Field(default=..., description="""Functional category (e.g., ``Magnet``, ``Diagnostic``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    hardware_type: Optional[Literal["Drift"]] = Field(default="Generic", description="""Python class name used for MODEL_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'],
         'equals_string': 'Drift',
         'ifabsent': 'string(Generic)'} })
    hardware_model: str = Field(default="Generic", description="""Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string(Generic)'} })
    machine_area: Optional[str] = Field(default=None, description="""Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    virtual_name: str = Field(default="", description="""Alternative internal name used by the control system when the physical name is inaccessible.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string()'} })
    alias: list[str] = Field(default_factory=list, description="""Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.""", validation_alias=AliasChoices('alias', 'name_alias'), json_schema_extra = { "linkml_meta": {'aliases': ['name_alias'], 'domain_of': ['AcceleratorElement']} })
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
    laser: Optional[_LaserElementBase] = Field(default=None, description="""Laser driving the plasma stage.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Laser',
                       'Plasma',
                       'LaserEnergyMeter',
                       'LaserHalfWavePlate',
                       'LaserMirror']} })
    physical: Optional[_PhysicalElementBase] = Field(default=None, description="""Position, rotation, and length data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PhysicalAcceleratorElement'],
         'in_subset': ['physical_properties']} })
    simulation: Optional[_PlasmaSimulationElementBase] = Field(default=None, description="""Simulation / tracking attributes.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    electrical: Optional[_ElectricalElementBase] = Field(default=None, description="""Power-supply electrical limits.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    manufacturer: Optional[_ManufacturerElementBase] = Field(default=None, description="""Manufacturer and serial-number data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ManufacturerElement', 'StandardElement']} })
    controls: Optional[_ControlsInformationBase] = Field(default=None, description="""Control-system process-variable definitions.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    reference: Optional[_ReferenceElementBase] = Field(default=None, description="""Links to design drawings and files.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    name: str = Field(default=..., description="""Unique element name within the machine.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement', 'SectionLattice', 'MachineLayout']} })
    hardware_class: HardwareClassEnum = Field(default=..., description="""Functional category (e.g., ``Magnet``, ``Diagnostic``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    hardware_type: Optional[Literal["Plasma"]] = Field(default="Generic", description="""Python class name used for MODEL_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'],
         'equals_string': 'Plasma',
         'ifabsent': 'string(Generic)'} })
    hardware_model: str = Field(default="Generic", description="""Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string(Generic)'} })
    machine_area: Optional[str] = Field(default=None, description="""Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    virtual_name: str = Field(default="", description="""Alternative internal name used by the control system when the physical name is inaccessible.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string()'} })
    alias: list[str] = Field(default_factory=list, description="""Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.""", validation_alias=AliasChoices('alias', 'name_alias'), json_schema_extra = { "linkml_meta": {'aliases': ['name_alias'], 'domain_of': ['AcceleratorElement']} })
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

    laser: Optional[_LaserEnergyMeterElementBase] = Field(default=None, description="""Energy-meter instrument parameters.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Laser',
                       'Plasma',
                       'LaserEnergyMeter',
                       'LaserHalfWavePlate',
                       'LaserMirror']} })
    simulation: Optional[_SimulationElementBase] = Field(default=None, description="""Simulation / tracking attributes.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    electrical: Optional[_ElectricalElementBase] = Field(default=None, description="""Power-supply electrical limits.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    manufacturer: Optional[_ManufacturerElementBase] = Field(default=None, description="""Manufacturer and serial-number data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ManufacturerElement', 'StandardElement']} })
    controls: Optional[_ControlsInformationBase] = Field(default=None, description="""Control-system process-variable definitions.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    reference: Optional[_ReferenceElementBase] = Field(default=None, description="""Links to design drawings and files.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    name: str = Field(default=..., description="""Unique element name within the machine.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement', 'SectionLattice', 'MachineLayout']} })
    hardware_class: HardwareClassEnum = Field(default=..., description="""Functional category (e.g., ``Magnet``, ``Diagnostic``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    hardware_type: Optional[Literal["LaserEnergyMeter"]] = Field(default="Generic", description="""Python class name used for MODEL_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'],
         'equals_string': 'LaserEnergyMeter',
         'ifabsent': 'string(Generic)'} })
    hardware_model: str = Field(default="Generic", description="""Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string(Generic)'} })
    machine_area: Optional[str] = Field(default=None, description="""Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    virtual_name: str = Field(default="", description="""Alternative internal name used by the control system when the physical name is inaccessible.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string()'} })
    alias: list[str] = Field(default_factory=list, description="""Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.""", validation_alias=AliasChoices('alias', 'name_alias'), json_schema_extra = { "linkml_meta": {'aliases': ['name_alias'], 'domain_of': ['AcceleratorElement']} })
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

    laser: Optional[_LaserHalfWavePlateElementBase] = Field(default=None, description="""Half-wave plate parameters.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Laser',
                       'Plasma',
                       'LaserEnergyMeter',
                       'LaserHalfWavePlate',
                       'LaserMirror']} })
    simulation: Optional[_SimulationElementBase] = Field(default=None, description="""Simulation / tracking attributes.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    electrical: Optional[_ElectricalElementBase] = Field(default=None, description="""Power-supply electrical limits.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    manufacturer: Optional[_ManufacturerElementBase] = Field(default=None, description="""Manufacturer and serial-number data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ManufacturerElement', 'StandardElement']} })
    controls: Optional[_ControlsInformationBase] = Field(default=None, description="""Control-system process-variable definitions.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    reference: Optional[_ReferenceElementBase] = Field(default=None, description="""Links to design drawings and files.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    name: str = Field(default=..., description="""Unique element name within the machine.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement', 'SectionLattice', 'MachineLayout']} })
    hardware_class: HardwareClassEnum = Field(default=..., description="""Functional category (e.g., ``Magnet``, ``Diagnostic``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    hardware_type: Optional[Literal["LaserHalfWavePlate"]] = Field(default="Generic", description="""Python class name used for MODEL_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'],
         'equals_string': 'LaserHalfWavePlate',
         'ifabsent': 'string(Generic)'} })
    hardware_model: str = Field(default="Generic", description="""Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string(Generic)'} })
    machine_area: Optional[str] = Field(default=None, description="""Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    virtual_name: str = Field(default="", description="""Alternative internal name used by the control system when the physical name is inaccessible.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string()'} })
    alias: list[str] = Field(default_factory=list, description="""Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.""", validation_alias=AliasChoices('alias', 'name_alias'), json_schema_extra = { "linkml_meta": {'aliases': ['name_alias'], 'domain_of': ['AcceleratorElement']} })
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

    laser: Optional[_LaserMirrorElementBase] = Field(default=None, description="""Mirror steering parameters.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Laser',
                       'Plasma',
                       'LaserEnergyMeter',
                       'LaserHalfWavePlate',
                       'LaserMirror']} })
    simulation: Optional[_SimulationElementBase] = Field(default=None, description="""Simulation / tracking attributes.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    electrical: Optional[_ElectricalElementBase] = Field(default=None, description="""Power-supply electrical limits.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    manufacturer: Optional[_ManufacturerElementBase] = Field(default=None, description="""Manufacturer and serial-number data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ManufacturerElement', 'StandardElement']} })
    controls: Optional[_ControlsInformationBase] = Field(default=None, description="""Control-system process-variable definitions.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    reference: Optional[_ReferenceElementBase] = Field(default=None, description="""Links to design drawings and files.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    name: str = Field(default=..., description="""Unique element name within the machine.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement', 'SectionLattice', 'MachineLayout']} })
    hardware_class: HardwareClassEnum = Field(default=..., description="""Functional category (e.g., ``Magnet``, ``Diagnostic``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    hardware_type: Optional[Literal["LaserMirror"]] = Field(default="Generic", description="""Python class name used for MODEL_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'],
         'equals_string': 'LaserMirror',
         'ifabsent': 'string(Generic)'} })
    hardware_model: str = Field(default="Generic", description="""Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string(Generic)'} })
    machine_area: Optional[str] = Field(default=None, description="""Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    virtual_name: str = Field(default="", description="""Alternative internal name used by the control system when the physical name is inaccessible.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string()'} })
    alias: list[str] = Field(default_factory=list, description="""Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.""", validation_alias=AliasChoices('alias', 'name_alias'), json_schema_extra = { "linkml_meta": {'aliases': ['name_alias'], 'domain_of': ['AcceleratorElement']} })
    subelement: Optional[str] = Field(default=None, description="""If set, this element is a logical sub-component of the named parent element.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })


class _LaserMirrorElementBase(ConfiguredBaseModel):
    """
    Mirror steering parameters for a laser mirror.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:LaserMirrorElement',
         'from_schema': 'https://w3id.org/laura/schema'})

    step_max: Optional[float] = Field(default=None, description="""Maximum step size for mirror adjustment.""", json_schema_extra = { "linkml_meta": {'domain_of': ['LaserMirrorElement']} })
    sense: Optional[_LaserMirrorSenseBase] = Field(default=None, description="""Mirror sense/interlock configuration.""", json_schema_extra = { "linkml_meta": {'domain_of': ['LaserMirrorElement']} })
    vertical_channel: Optional[int] = Field(default=None, description="""Vertical control channel index.""", json_schema_extra = { "linkml_meta": {'domain_of': ['LaserMirrorElement']} })
    horizontal_channel: Optional[int] = Field(default=None, description="""Horizontal control channel index.""", json_schema_extra = { "linkml_meta": {'domain_of': ['LaserMirrorElement']} })


class _LaserMirrorSenseBase(ConfiguredBaseModel):
    """
    Mirror sense switch values.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:LaserMirrorSense',
         'from_schema': 'https://w3id.org/laura/schema'})

    left: Optional[float] = Field(default=None, description="""Left sense value.""", validation_alias=AliasChoices('left', 'left_sense'), json_schema_extra = { "linkml_meta": {'aliases': ['left_sense'], 'domain_of': ['LaserMirrorSense']} })
    right: Optional[float] = Field(default=None, description="""Right sense value.""", validation_alias=AliasChoices('right', 'right_sense'), json_schema_extra = { "linkml_meta": {'aliases': ['right_sense'], 'domain_of': ['LaserMirrorSense']} })
    up: Optional[float] = Field(default=None, description="""Up sense value.""", validation_alias=AliasChoices('up', 'up_sense'), json_schema_extra = { "linkml_meta": {'aliases': ['up_sense'], 'domain_of': ['LaserMirrorSense']} })
    down: Optional[float] = Field(default=None, description="""Down sense value.""", validation_alias=AliasChoices('down', 'down_sense'), json_schema_extra = { "linkml_meta": {'aliases': ['down_sense'], 'domain_of': ['LaserMirrorSense']} })


class _LaserAttenuatorBase(_StandardElementBase):
    """
    Laser power attenuator (waveplate + polariser combination).
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:LaserAttenuator',
         'from_schema': 'https://w3id.org/laura/schema',
         'in_subset': ['laser_properties'],
         'slot_usage': {'hardware_type': {'equals_string': 'LaserAttenuator',
                                          'name': 'hardware_type'}}})

    maximum: Optional[float] = Field(default=None, description="""Maximum attenuation angle [deg].""", json_schema_extra = { "linkml_meta": {'domain_of': ['CameraMask', 'CameraSensor', 'LaserAttenuator'],
         'unit': {'ucum_code': 'deg'}} })
    minimum: Optional[float] = Field(default=None, description="""Minimum attenuation angle [deg].""", json_schema_extra = { "linkml_meta": {'domain_of': ['CameraSensor', 'LaserAttenuator'], 'unit': {'ucum_code': 'deg'}} })
    simulation: Optional[_SimulationElementBase] = Field(default=None, description="""Simulation / tracking attributes.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    electrical: Optional[_ElectricalElementBase] = Field(default=None, description="""Power-supply electrical limits.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    manufacturer: Optional[_ManufacturerElementBase] = Field(default=None, description="""Manufacturer and serial-number data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ManufacturerElement', 'StandardElement']} })
    controls: Optional[_ControlsInformationBase] = Field(default=None, description="""Control-system process-variable definitions.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    reference: Optional[_ReferenceElementBase] = Field(default=None, description="""Links to design drawings and files.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StandardElement']} })
    name: str = Field(default=..., description="""Unique element name within the machine.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement', 'SectionLattice', 'MachineLayout']} })
    hardware_class: HardwareClassEnum = Field(default=..., description="""Functional category (e.g., ``Magnet``, ``Diagnostic``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    hardware_type: Optional[Literal["LaserAttenuator"]] = Field(default="Generic", description="""Python class name used for MODEL_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'],
         'equals_string': 'LaserAttenuator',
         'ifabsent': 'string(Generic)'} })
    hardware_model: str = Field(default="Generic", description="""Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string(Generic)'} })
    machine_area: Optional[str] = Field(default=None, description="""Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    virtual_name: str = Field(default="", description="""Alternative internal name used by the control system when the physical name is inaccessible.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string()'} })
    alias: list[str] = Field(default_factory=list, description="""Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.""", validation_alias=AliasChoices('alias', 'name_alias'), json_schema_extra = { "linkml_meta": {'aliases': ['name_alias'], 'domain_of': ['AcceleratorElement']} })
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
    hardware_class: HardwareClassEnum = Field(default=..., description="""Functional category (e.g., ``Magnet``, ``Diagnostic``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    hardware_type: Optional[Literal["Lighting"]] = Field(default="Generic", description="""Python class name used for MODEL_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'],
         'equals_string': 'Lighting',
         'ifabsent': 'string(Generic)'} })
    hardware_model: str = Field(default="Generic", description="""Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string(Generic)'} })
    machine_area: Optional[str] = Field(default=None, description="""Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })
    virtual_name: str = Field(default="", description="""Alternative internal name used by the control system when the physical name is inaccessible.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement'], 'ifabsent': 'string()'} })
    alias: list[str] = Field(default_factory=list, description="""Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.""", validation_alias=AliasChoices('alias', 'name_alias'), json_schema_extra = { "linkml_meta": {'aliases': ['name_alias'], 'domain_of': ['AcceleratorElement']} })
    subelement: Optional[str] = Field(default=None, description="""If set, this element is a logical sub-component of the named parent element.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement']} })


class _SectionLatticeBase(ConfiguredBaseModel):
    """
    An ordered list of element names defining a contiguous beamline section.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:SectionLattice',
         'from_schema': 'https://w3id.org/laura/schema'})

    name: str = Field(default=..., description="""Unique section name.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement', 'SectionLattice', 'MachineLayout']} })
    master_lattice: Optional[str] = Field(default=None, description="""Name of the master lattice this section belongs to.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SectionLattice', 'MachineLayout']} })
    elements: list[str] = Field(default_factory=list, description="""Ordered list of element names in this section.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SectionLattice', 'MachineModel']} })


class _MachineLayoutBase(ConfiguredBaseModel):
    """
    An ordered list of section names defining a beamline layout (a contiguous sequence of sections).
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:MachineLayout',
         'from_schema': 'https://w3id.org/laura/schema'})

    name: str = Field(default=..., description="""Unique layout name.""", json_schema_extra = { "linkml_meta": {'domain_of': ['AcceleratorElement', 'SectionLattice', 'MachineLayout']} })
    master_lattice: Optional[str] = Field(default=None, description="""Name of the master lattice this layout belongs to.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SectionLattice', 'MachineLayout']} })
    sections: list[str] = Field(default_factory=list, description="""Ordered list of section names.""", json_schema_extra = { "linkml_meta": {'domain_of': ['MachineLayout', 'MachineModel']} })


class _MachineModelBase(ConfiguredBaseModel):
    """
    Top-level container for a complete accelerator lattice: elements, sections, layouts, and named lattice configurations.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'class_uri': 'laura:MachineModel',
         'from_schema': 'https://w3id.org/laura/schema'})

    elements: list[str] = Field(default_factory=list, description="""All elements in the machine, keyed by name.""", json_schema_extra = { "linkml_meta": {'domain_of': ['SectionLattice', 'MachineModel']} })
    sections: list[str] = Field(default_factory=list, description="""All named beamline sections.""", json_schema_extra = { "linkml_meta": {'domain_of': ['MachineLayout', 'MachineModel']} })
    layouts: list[str] = Field(default_factory=list, description="""All named beamline layouts.""", json_schema_extra = { "linkml_meta": {'domain_of': ['MachineModel']} })


# Model rebuild
# see https://pydantic-docs.helpmanual.io/usage/models/#rebuilding-a-model
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
_BLMDiagnosticElementBase.model_rebuild()
_ScreenDiagnosticElementBase.model_rebuild()
_ChargeDiagnosticElementBase.model_rebuild()
_CameraPixelResultsIndicesBase.model_rebuild()
_CameraPixelResultsNamesBase.model_rebuild()
_CameraMaskBase.model_rebuild()
_CameraSensorBase.model_rebuild()
_CameraDiagnosticElementBase.model_rebuild()
_LaserElementBase.model_rebuild()
_LaserEnergyMeterElementBase.model_rebuild()
_LaserHalfWavePlateElementBase.model_rebuild()
_PlasmaElementBase.model_rebuild()
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
_ShutterElementBase.model_rebuild()
_ValveElementBase.model_rebuild()
_LightingElementBase.model_rebuild()
_AcceleratorElementBase.model_rebuild()
_StandardElementBase.model_rebuild()
_ElementBase.model_rebuild()
_PhysicalAcceleratorElementBase.model_rebuild()
_MagnetBaseElementBase.model_rebuild()
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
_LaserMirrorElementBase.model_rebuild()
_LaserMirrorSenseBase.model_rebuild()
_LaserAttenuatorBase.model_rebuild()
_LightingBase.model_rebuild()
_SectionLatticeBase.model_rebuild()
_MachineLayoutBase.model_rebuild()
_MachineModelBase.model_rebuild()
