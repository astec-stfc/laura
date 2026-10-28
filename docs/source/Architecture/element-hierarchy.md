# Element Class Hierarchy

LAURA uses a **schema-first** design.  The canonical class hierarchy is
defined in the ``laura/schema/YAML/laura_schema.yaml`` LinkML ontology
and auto-generates Pydantic base classes into `laura/models/_generated.py`.
Hand-written wrapper classes in `laura/models/element.py` inherit from those
generated bases and add Python-specific logic (validators, computed properties,
`IgnoreExtra`, cascading attribute access).

See [The LAURA Schema](../Schema.html) for what the ontology contains, the
conventions its slots follow, and the full list of artefacts generated from it.

See [element-er.md](element-er.md) for the full class diagram.

## Schema hierarchy

The schema defines three abstract layers before reaching concrete elements:

```
AcceleratorElement              ← schema root  (Python: BaseElement)
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
    │       ├── Magnet                     (Python: Magnet)
    │       │   │   + magnetic, degauss
    │       │   │   hardware_class = "Magnet"
    │       │   │
    │       │   ├── Dipole              (hardware_type = "Dipole")
    │       │   ├── Quadrupole          (hardware_type = "Quadrupole")
    │       │   ├── Sextupole           (hardware_type = "Sextupole")
    │       │   ├── Octupole            (hardware_type = "Octupole")
    │       │   ├── Solenoid            (hardware_type = "Solenoid")
    │       │   ├── NonLinearLens       (hardware_type = "NonLinearLens")
    │       │   ├── Wiggler             (hardware_type = "Wiggler")
    │       │   ├── HorizontalCorrector (extends Dipole; Python: Horizontal_Corrector)
    │       │   ├── VerticalCorrector   (extends Dipole; Python: Vertical_Corrector)
    │       │   └── CombinedCorrector   (extends Dipole; Python: Combined_Corrector)
    │       │
    │       ├── Diagnostic             (+ diagnostic sub-model)
    │       │   ├── BeamPositionMonitor (hardware_type = "Beam_Position_Monitor")
    │       │   ├── BeamArrivalMonitor  (hardware_type = "Beam_Arrival_Monitor")
    │       │   ├── BunchLengthMonitor  (hardware_type = "Bunch_Length_Monitor")
    │       │   ├── Camera              (hardware_type = "Camera")
    │       │   ├── Screen              (hardware_type = "Screen")
    │       │   ├── PhotonMonitor       (hardware_type = "Photon_Monitor")
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
        ├── PowerSupply
        ├── LaserEnergyMeter
        ├── LaserHalfWavePlate
        ├── LaserMirror
        ├── LaserAttenuator
        └── Lighting
```

## Schema ↔ Python name mapping

Most schema classes map one-to-one onto a Python class of the same name. The
exceptions are the abstract bases, renamed to avoid collision with composition
sub-model classes, and the correctors, which use the underscored spelling
familiar from accelerator-physics code:

| Schema class | Python wrapper | Module |
|---|---|---|
| `AcceleratorElement` | `BaseElement` | `laura.models.element` |
| `StandardElement` + `Element` | `Element` | `laura.models.element` |
| `PhysicalAcceleratorElement` | `PhysicalBaseElement` | `laura.models.element` |
| `HorizontalCorrector` | `Horizontal_Corrector` | `laura.models.element` |
| `VerticalCorrector` | `Vertical_Corrector` | `laura.models.element` |
| `CombinedCorrector` | `Combined_Corrector` | `laura.models.element` |
| `PhotonMonitor` | `Photon_Monitor` | `laura.models.element` |
| All other schema classes | Same name | `laura.models.element` |

> The Python class `Magnet` and the schema class `Magnet` do correspond, despite
> the schema's own description still calling it `MagnetBaseElement` — that name
> was dropped when the concrete magnet types moved into the schema.

## Generated base classes (`_generated.py`)

`laura/models/_generated.py` is auto-generated from the LinkML schema by
running `generate_pydantic.py` (called by `generate.ps1` / `generate.sh`).
Generated classes are prefixed with `_` and suffixed with `Base`
(e.g., `AcceleratorElement` → `_AcceleratorElementBase`) to avoid name
conflicts — the renaming happens inside `_generated.py`, so the hand-written
wrappers import the already-prefixed names directly:

```python
# In laura/models/element.py
from ._generated import (
    _AcceleratorElementBase,
    _ElementBase,
    _PhysicalAcceleratorElementBase,
    _MagnetBase,
    _QuadrupoleBase,
    ...
)

class BaseElement(CascadingAccessMixin, _AcceleratorElementBase, IgnoreExtra):
    ...

class Element(BaseElement, _ElementBase):
    ...

class PhysicalBaseElement(Element, _PhysicalAcceleratorElementBase):
    ...

class Magnet(PhysicalBaseElement, _MagnetBase):
    ...

class Quadrupole(Magnet, _QuadrupoleBase):
    hardware_type: str = Field(default="Quadrupole", frozen=True)
```

> **Two exceptions.** `PowerSupply` and `Photon_Monitor` are defined in the
> schema (`_PowerSupplyBase`, `_PhotonMonitorBase`) but their Python wrappers do
> not yet inherit from those bases, so schema-only slots on them are not
> validated at runtime.

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

`BaseElement` mixes in `CascadingAccessMixin` which implements
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

The **default value** of this field is the `ELEMENT_REGISTRY` key, so it must
match the `hardware_type` string in YAML files for dispatch to work
(see [yaml-pipeline.md](yaml-pipeline.md)). For every element defined so far the
default happens to equal the Python class name, but it is the field default that
is authoritative.

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
from ._generated import _MyNewElementBase

class MyNewElement(PhysicalBaseElement, _MyNewElementBase):
    """Description."""
    hardware_class: str = Field(default="Category", frozen=True)
    hardware_type: str = Field(default="MyNewElement", frozen=True)
    # Custom validators / properties...
```

The class is automatically registered in `ELEMENT_REGISTRY` at import time.
YAML files with `hardware_type: MyNewElement` will be parsed as this class.

## Adding a concrete magnet type

Concrete magnet types live in `laura/schema/YAML/magnets.yaml` alongside their
`*_Magnet` composition models, so a new one is added the same way as any other
element — schema class first, then the Python wrapper:

```yaml
  NewMagnet:
    is_a: Magnet
    class_uri: laura:NewMagnet
    slot_usage:
      hardware_type:
        equals_string: NewMagnet
      magnetic:
        range: NewMagnet_Magnet
```

```python
class NewMagnet(Magnet, _NewMagnetBase):
    hardware_type: str = Field(default="NewMagnet", frozen=True)
    magnetic: NewMagnet_Magnet = Field(default_factory=NewMagnet_Magnet)
```

A Python-only subclass of `Magnet` still works and is still registered, but it
gets no ontology-level validation of its `hardware_type` or its fields.
