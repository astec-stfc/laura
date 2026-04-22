---
description: "Use when modifying element classes, adding new element types, changing element inheritance, or debugging missing YAML data in element models."
applyTo: "laura/models/element.py"
---

# Element Model Guidelines

## Inheritance Rule
- If YAML files for this element type contain `physical:` data → inherit from `PhysicalBaseElement`
- If no physical data exists → inherit from `Element`
- Getting this wrong causes **silent data loss** due to `IgnoreExtra`

## Class Registration
- Each class sets `hardware_type: str = Field(default="ClassName", frozen=True)`
- The class name must exactly match the YAML `hardware_type` value
- Classes are auto-registered in `MODEL_REGISTRY` at import time via `get_all_subclasses(BaseModel)`

## Full Hierarchy (quick reference)
```
baseElement → Element → PhysicalBaseElement → Magnet, Diagnostic, RFCavity, ...
                     → LaserEnergyMeter, LaserMirror, Lighting, PID, ... (no physical)
```

## Checklist for Adding a New Element
1. Create class inheriting from `PhysicalBaseElement` or `Element`
2. Set `hardware_type` as frozen Field default matching class name
3. Set `hardware_class` if it groups with other elements
4. Add element-specific sub-model fields
5. Verify YAML files parse correctly: `from laura.Importers.YAML_Loader import read_YAML_Element_File`
