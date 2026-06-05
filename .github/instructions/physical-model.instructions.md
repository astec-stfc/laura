---
description: "Use when working with Position, Rotation, PhysicalElement, element positions, start/end calculations, rotation matrices, or serialising position data."
applyTo: "laura/models/physical.py"
---

# Physical Model Guidelines

## Position Serialisation — CRITICAL
- `list(position)` → `[x, y, z]` (correct for JSON/API)
- `position.array` → `numpy.ndarray` (correct for math)
- `position.model_dump()` → `{"x": ..., "y": ..., "z": ...}` (dict, NOT a list!)
- **Always use `list()` when converting Position to a list**, never `model_dump()`

## PhysicalElement
- `middle`: Centre position (aliases: `position`, `centre` in YAML)
- `start`: Computed from middle − length/2, accounting for rotation and bending
- `end`: Computed from middle + length/2, accounting for rotation and bending
- `rotation_matrix`: Combined local + global rotation, cached after first computation
- For bent elements (dipoles), start/end use the physical_angle from the parent's magnetic model

## Validators
- `middle` and `datum`: Accept float (→ z only), list, dict, Position
- `rotation` and `global_rotation`: Accept float (→ theta only), list, Rotation
