# Model Structure

How LAURA represents an accelerator from top to bottom.

LAURA uses a **schema-first** design: the canonical element hierarchy lives in
the ``laura/schema/YAML/laura_schema.yaml`` LinkML ontology; Pydantic
classes are generated from it into `laura/models/_generated.py` and wrapped
by hand-written classes in `laura/models/element.py`.
See [element-hierarchy.md](element-hierarchy.md) for the class hierarchy and
[element-er.md](element-er.md) for the full class diagram.

## Composition Hierarchy

```
LAURA (MachineModel)
│
├── elements: Dict[str, AcceleratorElement]   (Python: baseElement)
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
└── element_list: str | List[AcceleratorElement]
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
- `elements_between(start, end, element_class, path, section_type)` — filtered element queries
- `get_sections_by_type(...)` / `get_layouts_by_type(...)` — filter by lattice type (`beam`, `rf`, `laser`)
- `resolve_positions()` — re-resolve placements and rebuild section trajectories
- `export_rdf(...)` / `sparql(...)` — linked-data export and querying (needs the `rdf` extra)

### SectionLattice (`laura/models/elementList.py`)

A beam-path segment with:
- `order: List[str]` — element names in beam-path order
- `elements: ElementList` — element container
- `section_type: "beam" | "rf" | "laser"` — which kind of lattice it belongs to
- Methods for S-position calculation, drift insertion, and position resolution

### MachineLayout (`laura/models/elementList.py`)

A full beam path composed of multiple sections, with its own
`layout_type: "beam" | "rf" | "laser"`. Used to define the path particles
(or RF power, or laser light) follow through the accelerator.

Every element in a layout must carry physical data — layouts are chained by
element start/end positions, so a position-less `Element` cannot take part.

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

Each getter has a matching `all_*` property (`all_magnets`, `all_screens_and_cameras`,
…) covering the whole machine rather than a range on one path.

Element access: `machine[element_name]` or `machine.get_element(name)`

### LAURAQuery (`laura/query.py`)

SPARQL interface over a machine model, backed by an in-memory rdflib graph that
is built lazily and cached (`invalidate()` forces a rebuild). Needs the `rdf`
extra. `MachineModel.sparql()` is a thin wrapper over it. See the
[Importing and Exporting](../Interfaces.html) page.

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
| `reference_placement` | `ReferencePlacement` | Placement relative to another element's frame |
| `s` | `float` | Arc-length position along the design orbit |
| `s_point` | `"start"\|"middle"\|"end"` | Which point of the element `s` refers to (default `middle`) |
| `length` | `float` | Element length [m] |

`middle`, `s` and `reference_placement` are three mutually exclusive ways of
saying the same thing. `SectionLattice.resolve_positions()` resolves whichever
is given into global coordinates *and* an `s` value, and attaches the section's
`Trajectory` to each element. After that the two stay in sync: assigning `s`
updates `middle`, and assigning `middle` updates `s`. See the
[positioning modes](Element.html#positioning-modes) section for the YAML forms.

### Computed Properties

| Property | Type | Description |
|----------|------|-------------|
| `start` | `Position` | Start position (middle − length/2, rotated) |
| `end` | `Position` | End position (middle + length/2, rotated) |
| `rotation_matrix` | `np.ndarray` | 3×3 combined rotation matrix |
| `end_rotation_matrix` | `np.ndarray` | Rotation matrix at the element exit (includes any bend) |

For bent elements (dipoles), `start` and `end` account for the bending angle.

### Serialisation

`model_dump()` writes `middle`; `model_dump_s()` writes `s` (and `s_point` when
it is not `middle`) instead, falling back to the standard output when no `s` has
been resolved. `laura.Exporters.YAML` exposes this as `position_mode`.

## Trajectory (`laura/models/trajectory.py`)

The design orbit of a section, parameterised by arc-length `s`. It stores
`(s, position, rotation_matrix)` samples and interpolates between them, giving
bidirectional `s ↔ xyz` mapping via `xyz_at_s(s)` and `s_at_xyz(position)`.
Built by `SectionLattice.resolve_positions()` and attached to each
`PhysicalElement` as the private `_trajectory` attribute.

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
