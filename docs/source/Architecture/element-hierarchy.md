# Element Class Hierarchy

LAURA uses a **schema-first** design.  The canonical class hierarchy is
defined in the ``laura/schema/YAML/laura_schema.yaml`` LinkML ontology
and auto-generates Pydantic base classes into `laura/models/_generated.py`.
Hand-written wrapper classes in `laura/models/element.py` inherit from those
generated bases and add Python-specific logic (validators, computed properties,
`IgnoreExtra`, cascading attribute access).

See [element-er.md](element-er.md) for the full class diagram.

## Schema hierarchy

The schema defines three abstract layers before reaching concrete elements:

```
AcceleratorElement              ← schema root  (Python: baseElement)
│   name, hardware_class, hardware_type, hardware_model,
│   machine_area, virtual_name, alias, subelement
│
└── StandardElement             ← adds composition sub-models  (Python: Element)
    │   + simulation, electrical, manufacturer, controls, reference
    │
    ├── Element                 ← thin schema layer, merged with StandardElement in Python
    │   │
    │   └── PhysicalAcceleratorElement   (Python: PhysicalBaseElement)
    │       │   + physical: PhysicalElement  ← position, rotation, length
    │       │
    │       ├── MagnetBaseElement          (Python: Magnet)
    │       │   │   + magnetic, degauss
    │       │   │   hardware_class = "Magnet"
    │       │   │
    │       │   │   ── Python-only concrete types (not in schema) ──
    │       │   ├── Dipole              (hardware_type = "Dipole")
    │       │   ├── Quadrupole          (hardware_type = "Quadrupole")
    │       │   ├── Sextupole           (hardware_type = "Sextupole")
    │       │   ├── Octupole            (hardware_type = "Octupole")
    │       │   ├── Solenoid            (hardware_type = "Solenoid")
    │       │   ├── NonLinearLens       (hardware_type = "NonLinearLens")
    │       │   ├── Wiggler             (hardware_type = "Wiggler")
    │       │   ├── Horizontal_Corrector (extends Dipole)
    │       │   ├── Vertical_Corrector   (extends Dipole)
    │       │   └── Combined_Corrector   (extends Dipole)
    │       │
    │       ├── Diagnostic             (+ diagnostic sub-model)
    │       │   ├── BeamPositionMonitor (hardware_type = "Beam_Position_Monitor")
    │       │   ├── BeamArrivalMonitor  (hardware_type = "Beam_Arrival_Monitor")
    │       │   ├── BunchLengthMonitor  (hardware_type = "Bunch_Length_Monitor")
    │       │   ├── Camera              (hardware_type = "Camera")
    │       │   ├── Screen              (hardware_type = "Screen")
    │       │   └── ChargeDiagnostic
    │       │       ├── WallCurrentMonitor          (hardware_type = "Wall_Current_Monitor")
    │       │       ├── FaradayCupMonitor            (hardware_type = "Faraday_Cup_Monitor")
    │       │       └── IntegratedCurrentTransformer (hardware_type = "Integrated_Current_Transformer")
    │       │
    │       ├── RFCavity               (+ cavity sub-model, hardware_class = "RF")
    │       │   └── RFDeflectingCavity
    │       ├── Wakefield              (+ cavity sub-model)
    │       ├── Laser                  (+ laser sub-model)
    │       ├── Plasma                 (+ plasma + laser sub-models)
    │       ├── Stage
    │       ├── VacuumGauge
    │       ├── Valve                  (+ valve sub-model)
    │       ├── Shutter                (+ shutter sub-model)
    │       ├── Marker
    │       ├── Aperture               (+ aperture sub-model)
    │       │   └── Collimator
    │       ├── TwissMatch
    │       └── Drift
    │
    └── Non-Physical Elements (inherit StandardElement directly — no physical field)
        ├── LowLevelRF         (hardware_type = "Low_Level_RF")
        ├── RFModulator
        ├── RFProtection
        ├── RFHeartbeat
        ├── PID
        ├── LaserEnergyMeter
        ├── LaserHalfWavePlate
        ├── LaserMirror
        ├── LaserAttenuator
        └── Lighting
```

## Schema ↔ Python name mapping

The schema uses longer names for abstract bases to avoid collision with
composition sub-model classes that share similar names:

| Schema class | Python wrapper | Module |
|---|---|---|
| `AcceleratorElement` | `baseElement` | `laura.models.element` |
| `StandardElement` + `Element` | `Element` | `laura.models.element` |
| `PhysicalAcceleratorElement` | `PhysicalBaseElement` | `laura.models.element` |
| `MagnetBaseElement` | `Magnet` | `laura.models.element` |
| All other schema classes | Same name | `laura.models.element` |

## Generated base classes (`_generated.py`)

`laura/models/_generated.py` is auto-generated from the LinkML schema by
running `generate_pydantic.py` (called by `generate.ps1` / `generate.sh`).
Generated classes are prefixed with `_` and suffixed with `Base`
(e.g., `AcceleratorElement` → `_AcceleratorElementBase`) to avoid name
conflicts.  The hand-written wrappers import these bases:

```python
# In laura/models/element.py
from laura.models._generated import (
    AcceleratorElement as _AcceleratorElementBase,
    Element as _ElementBase,
    PhysicalAcceleratorElement as _PhysicalAcceleratorElementBase,
    MagnetBaseElement as _MagnetBaseElementBase,
    ...
)

class baseElement(CascadingAccessMixin, _AcceleratorElementBase, IgnoreExtra):
    ...

class Element(baseElement, _ElementBase):
    ...

class PhysicalBaseElement(Element, _PhysicalAcceleratorElementBase):
    ...

class Magnet(PhysicalBaseElement, _MagnetBaseElementBase):
    ...
```

**Do not edit `_generated.py` manually** — regenerate it with:

```bash
python laura/schema/generate_pydantic.py
```

## PhysicalBaseElement vs Element

The critical distinction:

- **`PhysicalBaseElement`** (`PhysicalAcceleratorElement` in schema): Has
  `physical: PhysicalElement` field.  Use for anything with a position/length
  in the beamline (magnets, diagnostics, RF cavities, shutters, valves, etc.)
- **`Element`** (`StandardElement`/`Element` in schema): No physical field.
  Use for control-system-only elements (LLRF modules, laser optics, lighting,
  feedback controllers, etc.)

### Rule for choosing the parent class

> If the YAML definition for an element type includes `physical:` data with
> position/length, the Python class **must** inherit from `PhysicalBaseElement`.
> Otherwise the physical data is silently dropped by `IgnoreExtra`.

## Custom Attribute Access

`baseElement` mixes in `CascadingAccessMixin` which implements
`__getattr__`/`__setattr__` to search nested Pydantic sub-models:

```python
# Instead of:
element.physical.middle
element.magnetic.field_amplitude

# You can write:
element.middle          # searches nested models for 'middle'
element.field_amplitude # searches nested models for 'field_amplitude'
```

If the attribute is ambiguous (present in multiple nested models), an
`AttributeError` is raised asking for explicit access.

## `hardware_type` Field

Each leaf class sets `hardware_type` as a frozen `Field` default:

```python
class Quadrupole(Magnet):
    hardware_type: str = Field(default="Quadrupole", frozen=True)
```

This value must exactly match the `hardware_type` string in YAML files for
`ELEMENT_REGISTRY` dispatch to work (see [yaml-pipeline.md](yaml-pipeline.md)).

The schema enforces this via `slot_usage` constraints
(e.g., `equals_string: Quadrupole`), providing ontology-level validation in
addition to the runtime Python check.

## Adding a new element type

### New schema class (add to `laura_schema.yaml`)

```yaml
  MyNewElement:
    is_a: PhysicalAcceleratorElement   # or StandardElement for non-physical
    description: My new element type.
    class_uri: laura:MyNewElement
    slot_usage:
      hardware_type:
        equals_string: MyNewElement
    attributes:
      my_field:
        range: float
        description: Some new field.
```

Then regenerate the bases:

```bash
python laura/schema/generate_pydantic.py
```

### New Python wrapper (add to `laura/models/element.py`)

```python
from laura.models._generated import MyNewElement as _MyNewElementBase

class MyNewElement(PhysicalBaseElement, _MyNewElementBase):
    """Description."""
    hardware_class: str = Field(default="Category", frozen=True)
    hardware_type: str = Field(default="MyNewElement", frozen=True)
    # Custom validators / properties...
```

The class is automatically registered in `ELEMENT_REGISTRY` at import time.
YAML files with `hardware_type: MyNewElement` will be parsed as this class.

## Adding a concrete magnet type (Python-only)

Concrete magnet types (Dipole, Quadrupole, …) are not individually listed in
the schema — `MagnetBaseElement` covers all of them.  Simply subclass `Magnet`:

```python
class NewMagnet(Magnet):
    hardware_type: str = Field(default="NewMagnet", frozen=True)
```

No schema change is required unless the new magnet introduces unique fields
that should be validated at the ontology level.
