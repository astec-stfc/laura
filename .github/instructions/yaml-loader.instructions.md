---
description: "Use when working with YAML loading, element parsing, MODEL_REGISTRY, ADAPTERS, LazyElementDict, or debugging why elements fail to load from YAML files."
applyTo: "laura/Importers/YAML_Loader.py"
---

# YAML Loader Guidelines

## Pipeline
```
YAML file → yaml.load() → dict → interpret_YAML_Element(dict) → Element object
```

## Critical Details
- `interpret_YAML_Element` returns `None` on ANY exception — errors are silent
- `hardware_type` in the dict must exactly match a Python class name in `MODEL_REGISTRY`
- `MODEL_REGISTRY` is built automatically from all `BaseModel` subclasses at import time
- `ADAPTERS` lazily creates `TypeAdapter` instances on first use per class

## LazyElementDict
- Maps element names to file paths; loads YAML only on first `__getitem__` access
- `fast_get_element_metadata()` uses regex (not YAML parsing) for name/area extraction
- Calling `.values()` triggers full load of all elements
- `.keys()` works without loading (uses pre-extracted metadata)

## Common Issues
- Element returns `None`: Check `hardware_type` matches class name exactly
- Physical data missing: Element class probably inherits from `Element` not `PhysicalBaseElement`
- Element not found: Check file naming — metadata extraction reads first 2000 chars for `name:`
