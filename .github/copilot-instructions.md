# LAURA Project Guidelines

## What is LAURA?

LAURA (**L**attice **A**nd **U**nified **R**epresentation of **A**ccelerators) is a
Pydantic-based Python library for representing particle accelerator lattices.
It reads YAML element definitions and builds a hierarchical model:
elements → sections → layouts → full machine.

## Architecture Overview

Full internal documentation lives in `docs/source/Architecture/`:
- [yaml-pipeline.md](docs/source/Architecture/yaml-pipeline.md) — How YAML files become Python objects
- [element-hierarchy.md](docs/source/Architecture/element-hierarchy.md) — Element class inheritance tree
- [model-structure.md](docs/source/Architecture/model-structure.md) — MachineModel composition and construction flow

## Key Design Rules

### Element Class Inheritance

- If an element type has physical position data in its YAML (`physical:` field),
  its Python class **must** inherit from `PhysicalBaseElement`, not `Element`.
- `IgnoreExtra` silently drops unknown fields — if a class doesn't declare
  `physical`, YAML physical data is lost with no error.
- The class name must exactly match the `hardware_type` string used in YAML files.

### YAML ↔ Python Dispatch

- `hardware_type` in YAML maps to Python class name via `MODEL_REGISTRY`
- `hardware_class` is for directory organisation, not dispatch
- New classes are auto-registered at import time — no manual registration needed

### Position Serialisation

- `Position` and `Rotation` are `NumpyVectorModel` with `__iter__`
- Use `list(position)` to get `[x, y, z]` — **not** `model_dump()` which gives `{"x":…, "y":…, "z":…}`
- Use `position.array` for numpy arrays

### Lazy Loading

- Large YAML directories use `LazyElementDict` — elements parsed on first access
- `fast_get_element_metadata()` extracts name/area via regex without full parsing
- Don't assume all elements are loaded; accessing `.values()` triggers full load

## Code Style

- Pydantic v2 models throughout
- Type annotations on all public methods
- `Field(default_factory=...)` for mutable defaults
- `Field(default=..., frozen=True)` for constants like `hardware_type`

## Build and Test

```bash
pip install -e .                    # Install in dev mode
pip install -e .[docs]              # With docs dependencies
cd docs && make html                # Build documentation
python -m pytest unit_tests/        # Run tests
```

## Related Repositories

- **laura-lattices**: Accelerator data packages (YAML files, field maps, lattice definitions)
- **LauraAPI**: FastAPI server exposing LAURA data over HTTP (in clara-control-room-applications)
- **LauraAPIClient**: Python client for LauraAPI
- **LauraGUI**: PyQt GUI for browsing accelerator data
