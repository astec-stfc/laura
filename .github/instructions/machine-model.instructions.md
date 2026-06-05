---
description: "Use when working with LAURA constructor, machine model, sections, layouts, element queries, laura-lattices package integration, or the lattice= keyword argument."
applyTo: ["laura/laura.py", "laura/models/elementList.py"]
---

# LAURA Machine Model Guidelines

## Construction
```python
# From laura-lattices package:
import laura_lattices.CLARA as CLARA
machine = LAURA(lattice=CLARA)

# From explicit paths:
machine = LAURA(layout="layouts.yaml", section="sections.yaml", element_list="/path/to/YAML/")
```

## model_validator: _resolve_lattice_package
Accepts `lattice=MODULE` and extracts `layout`, `section`, `element_list` from the module.
The module must have those three attributes (laura-lattices packages do).

## Element Loading
- File path (`.yaml`/`.json`): Reads combined file with all elements
- Directory path: Creates `LazyElementDict` — elements loaded on demand
- List of elements: Stored directly

## Element Access
- `machine[name]` or `machine.get_element(name)` → element object
- `machine.sections["S01"].elements` → ElementList for that section
- `machine.elements_between(start, end, element_class, path)` → filtered names

## Composition
```
LAURA > MachineModel > { lattices: MachineLayout, sections: SectionLattice, elements: dict }
```
- `MachineLayout`: Named beam path composed of sections
- `SectionLattice`: Ordered element sequence with drift insertion and S-position calculation
- `ElementList`: Dict wrapper with attribute propagation
