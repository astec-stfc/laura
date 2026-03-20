# Element Class Hierarchy

All accelerator components are represented as Pydantic models in
`laura/models/element.py`. The inheritance chain determines what data each
element type can hold.

## Inheritance Tree

```
baseElement (IgnoreExtra)
│   Fields: name, hardware_class, hardware_type, hardware_model,
│           machine_area, virtual_name, alias, subelement
│   Custom __getattr__/__setattr__ for nested attribute access
│
└── Element (baseElement)
    │   Adds: simulation, electrical, manufacturer, controls, reference
    │
    ├── PhysicalBaseElement (Element)
    │   │   Adds: physical: PhysicalElement  ← position, rotation, length
    │   │
    │   ├── Magnet
    │   │   │   Adds: magnetic, degauss
    │   │   │   hardware_class = "Magnet"
    │   │   │
    │   │   ├── Dipole              (hardware_type = "Dipole")
    │   │   ├── Quadrupole          (hardware_type = "Quadrupole")
    │   │   ├── Sextupole           (hardware_type = "Sextupole")
    │   │   ├── Octupole            (hardware_type = "Octupole")
    │   │   ├── Solenoid            (hardware_type = "Solenoid")
    │   │   ├── NonLinearLens       (hardware_type = "NonLinearLens")
    │   │   ├── Wiggler             (hardware_type = "Wiggler")
    │   │   ├── Horizontal_Corrector (extends Dipole)
    │   │   ├── Vertical_Corrector   (extends Dipole)
    │   │   └── Combined_Corrector   (extends Dipole)
    │   │
    │   ├── Diagnostic
    │   │   │   Adds: diagnostic
    │   │   │   hardware_class = "Diagnostic"
    │   │   │
    │   │   ├── Beam_Position_Monitor
    │   │   ├── Beam_Arrival_Monitor
    │   │   ├── Bunch_Length_Monitor
    │   │   ├── Camera
    │   │   ├── Screen
    │   │   └── ChargeDiagnostic
    │   │       ├── Wall_Current_Monitor
    │   │       ├── Faraday_Cup_Monitor
    │   │       └── Integrated_Current_Transformer
    │   │
    │   ├── RFCavity               (hardware_class = "RF")
    │   │   └── RFDeflectingCavity
    │   ├── Wakefield
    │   ├── Laser
    │   ├── Plasma
    │   ├── Stage
    │   ├── VacuumGauge
    │   ├── Valve
    │   ├── Shutter              ← recently moved here from Element
    │   ├── Marker
    │   ├── Aperture
    │   │   └── Collimator
    │   ├── TwissMatch
    │   └── Drift
    │
    └── Non-Physical Elements (inherit from Element, NO physical field)
        ├── LaserEnergyMeter
        ├── LaserHalfWavePlate
        ├── LaserMirror
        ├── LaserAttenuator
        ├── Lighting
        ├── PID
        ├── Low_Level_RF
        ├── RFModulator
        ├── RFProtection
        └── RFHeartbeat
```

## PhysicalBaseElement vs Element

The critical distinction:

- **PhysicalBaseElement**: Has `physical: PhysicalElement` field. Used for
  anything with a position/length in the beamline (magnets, diagnostics, RF
  cavities, shutters, valves, etc.)
- **Element**: No physical field. Used for control-system-only elements
  (laser optics controls, RF electronics, lighting, etc.)

### Rule for Choosing Parent Class

> If the YAML definition for an element type includes `physical:` data with
> position/length, the Python class **must** inherit from `PhysicalBaseElement`.
> Otherwise the physical data is silently dropped by `IgnoreExtra`.

## Custom Attribute Access

`baseElement` implements custom `__getattr__` and `__setattr__` that search
nested Pydantic models. This allows:

```python
# Instead of:
element.physical.middle
element.magnetic.field_amplitude

# You can write:
element.middle          # searches nested models for 'middle'
element.field_amplitude # searches nested models for 'field_amplitude'
```

If the attribute is ambiguous (found in multiple nested models), an
`AttributeError` is raised asking for explicit access.

## hardware_type Field

Each leaf class sets `hardware_type` as a frozen Field default:

```python
class Quadrupole(Magnet):
    hardware_type: str = Field(default="Quadrupole", frozen=True)
```

This value must match the `hardware_type` string in YAML files for the
MODEL_REGISTRY dispatch to work (see yaml-pipeline.md).

## Adding a New Physical Element

```python
class NewElement(PhysicalBaseElement):
    """Description."""
    hardware_class: str = Field(default="Category", frozen=True)
    hardware_type: str = Field(default="NewElement", frozen=True)
    # Add element-specific fields...
```

The class is automatically registered in MODEL_REGISTRY at import time.
YAML files with `hardware_type: NewElement` will be parsed as this class.
