# Model Structure

How LAURA represents an accelerator from top to bottom.

## Composition Hierarchy

```
LAURA (MachineModel)
│
├── elements: Dict[str, baseElement]
│       All elements in the machine, keyed by name.
│       May be a LazyElementDict (loads from YAML on first access).
│
├── sections: Dict[str, SectionLattice]
│       Named beam-path segments, each with an ordered list of elements.
│       e.g. {"S01": SectionLattice, "L01": SectionLattice, ...}
│
├── lattices: Dict[str, MachineLayout]
│       Named beam paths composed of sections.
│       e.g. {"BA1": MachineLayout(sections=["S01", "L01", "S02", "BA1"])}
│
├── layout: str | Dict     (layouts.yaml path or dict)
├── section: str | Dict    (sections.yaml path or dict)
└── element_list: str | List[baseElement]
        Path to summary file, YAML directory, or list of element objects.
```

## Construction Flow

```
LAURA(lattice=CLARA)
       │
       ▼
model_validator: _resolve_lattice_package
       │  Extracts layout, section, element_list from lattice module
       ▼
field_validator: validate_element_list
       │  Resolves paths (file, directory, or list)
       ▼
model_post_init
       │
       ├─ If element_list is a file:
       │     read_YAML_Combined_File → parse all elements → dict
       │
       ├─ If element_list is a directory:
       │     glob *.yaml → fast_get_element_metadata → LazyElementDict
       │     (elements loaded on demand, not upfront)
       │
       └─ If element_list is a list of elements:
             Store directly in elements dict
       │
       ▼
MachineModel.model_post_init (super)
       │
       ├─ Read layouts.yaml → self._layouts
       ├─ Read sections.yaml → self._section_definitions
       └─ _build_layouts(elements)
             Creates SectionLattice and MachineLayout objects
```

## Key Classes

### MachineModel (`laura/models/elementList.py`)

Top-level model. Provides:
- `elements` dict — all elements by name
- `sections` dict — ordered groupings
- `lattices` dict — beam path definitions
- `elements_between(start, end, element_class, path)` — filtered element queries

### SectionLattice (`laura/models/elementList.py`)

A beam-path segment with:
- `order: List[str]` — element names in beam-path order
- `elements: ElementList` — element container
- Methods for S-position calculation, drift insertion

### MachineLayout (`laura/models/elementList.py`)

A full beam path composed of multiple sections. Used to define the path
particles follow through the accelerator.

### LAURA (`laura/laura.py`)

Extends `MachineModel` with convenience getters:

| Method | Returns |
|--------|---------|
| `get_elements(start, end, path)` | All element names |
| `get_magnets(start, end, path)` | Magnet names |
| `get_quadrupoles(...)` | Quadrupole names |
| `get_dipoles(...)` | Dipole names |
| `get_correctors(...)` | Corrector names |
| `get_solenoids(...)` | Solenoid names |
| `get_diagnostics(...)` | Diagnostic names |
| `get_screens_and_cameras(...)` | Screen→camera mapping |
| `get_rf_cavities(...)` | RF cavity names |
| `get_elements_s_pos(...)` | Dict of s-positions |
| `createDrifts(start, end, path)` | Elements with drifts inserted |

Element access: `machine[element_name]` or `machine.get_element(name)`

## PhysicalElement (`laura/models/physical.py`)

Represents an element's position and orientation in 3D space.

### Fields

| Field | Type | Description |
|-------|------|-------------|
| `middle` | `Position` | Centre position (aliases: `position`, `centre`) |
| `datum` | `Position` | Datum position |
| `rotation` | `Rotation` | Local rotation |
| `global_rotation` | `Rotation` | Global rotation |
| `error` | `ElementError` | Position/rotation errors |
| `survey` | `ElementSurvey` | Survey positions |
| `length` | `float` | Element length [m] |

### Computed Properties

| Property | Type | Description |
|----------|------|-------------|
| `start` | `Position` | Start position (middle − length/2, rotated) |
| `end` | `Position` | End position (middle + length/2, rotated) |
| `rotation_matrix` | `np.ndarray` | 3×3 combined rotation matrix |

For bent elements (dipoles), `start` and `end` account for the bending angle.

### Position (`laura/models/physical.py`)

```python
class Position(NumpyVectorModel):
    x: float = 0.0  # Horizontal [m]
    y: float = 0.0  # Vertical [m]
    z: float = 0.0  # Longitudinal [m]
```

Key interfaces:
- `list(position)` → `[x, y, z]` (via `__iter__`)
- `position.array` → `np.ndarray([x, y, z])`
- `Position.from_list([x, y, z])` → Position
- Supports `+`, `-`, `.dot()`, `.length()`
- `model_dump()` → `{"x": ..., "y": ..., "z": ...}` (NOT a list!)

**Warning:** Use `list(position)` not `model_dump()` when you need `[x, y, z]`.

### Rotation (`laura/models/physical.py`)

```python
class Rotation(NumpyVectorModel):
    phi: float    # Horizontal axis rotation [rad], constrained ±π
    psi: float    # Vertical axis rotation [rad], constrained ±π
    theta: float  # Longitudinal axis rotation [rad], constrained ±π
```

Same interfaces as Position: `list()`, `.array`, `.from_list()`, arithmetic.

## laura-lattices Integration

The `lattice=` keyword connects to `laura-lattices` packages:

```python
import laura_lattices.CLARA as CLARA
machine = LAURA(lattice=CLARA)
```

The module exposes `layout`, `section`, `element_list` file paths that the
`_resolve_lattice_package` validator unpacks into constructor arguments.
