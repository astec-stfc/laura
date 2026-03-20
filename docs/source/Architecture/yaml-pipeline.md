# YAML Loading Pipeline

How LAURA turns YAML files on disk into Pydantic element objects.

## Overview

```
YAML file on disk
       │
       ▼
yaml.load()  →  Python dict
       │
       ▼
interpret_YAML_Element(dict)
       │
       ├─ reads dict["hardware_type"]   (e.g. "Quadrupole")
       │
       ├─ ADAPTERS.get("Quadrupole")    (lazy TypeAdapter lookup)
       │     │
       │     └─ MODEL_REGISTRY["Quadrupole"] → Quadrupole class
       │           └─ TypeAdapter(Quadrupole) created on first use
       │
       └─ adapter.validate_python(dict) → Quadrupole instance
```

## Key Components

### File: `laura/Importers/YAML_Loader.py`

#### MODEL_REGISTRY

Built at import time by collecting **all** `BaseModel` subclasses:

```python
def get_all_subclasses(cls):
    subclasses = set()
    for sub in cls.__subclasses__():
        subclasses.add(sub)
        subclasses.update(get_all_subclasses(sub))
    return subclasses

ALL_MODELS = get_all_subclasses(BaseModel)

MODEL_REGISTRY = {
    cls.__name__: cls
    for cls in ALL_MODELS
}
```

Class names become the lookup keys. The YAML field `hardware_type` must
**exactly match** a Python class name (e.g. `"Quadrupole"`, `"Screen"`,
`"Shutter"`).

#### ADAPTERS (LazyAdapterDict)

Wraps `MODEL_REGISTRY` with lazy `TypeAdapter` creation. The first time a
`hardware_type` is encountered, a Pydantic `TypeAdapter` is created for that
class and cached.

#### interpret_YAML_Element

The core dispatch function:

```python
def interpret_YAML_Element(elem: dict, exclude_set=None):
    hw_type = elem.get("hardware_type")
    if not hw_type:
        return None
    adapter = ADAPTERS.get(hw_type)
    if adapter is None:
        return None
    if exclude_set:
        elem = {k: v for k, v in elem.items() if k not in exclude_set}
    try:
        return adapter.validate_python(elem)
    except Exception:
        return None
```

**Critical behaviour:** If validation fails (e.g. unexpected data), it
silently returns `None`. Check logs if elements are missing.

### Loading Modes

| Mode | Function | When Used |
|------|----------|-----------|
| Single YAML file | `read_YAML_Element_File(path)` | One element per file |
| Combined file | `read_YAML_Combined_File(path)` | Summary JSON/YAML with many elements |
| Directory (lazy) | `LazyElementDict(filenames)` | Directory of YAML files |

### LazyElementDict

When `element_list` is a directory, LAURA does **not** parse every YAML file
upfront. Instead:

1. `glob` finds all `*.yaml` files recursively
2. `fast_get_element_metadata()` extracts `name` and `machine_area` via **regex**
   (reads first 2000 chars only — no YAML parsing)
3. A `LazyElementDict` is created mapping `name → filepath`
4. Full YAML parsing + model validation happens only on first access to that element

This makes startup fast even for directories with hundreds of YAML files.

## IgnoreExtra Behaviour

All element models inherit from `IgnoreExtra`:

```python
class IgnoreExtra(ModelBase):
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        extra="ignore",
        populate_by_name=True,
    )
```

**Consequence:** If YAML contains a field that the Python class does not
declare, it is **silently dropped**. This means:

- If a YAML file has `physical:` data but the element class does not inherit
  from `PhysicalBaseElement`, the physical data is lost.
- No error or warning is raised.
- This is the most common cause of "missing data" bugs.

## hardware_type vs hardware_class

| Field | Purpose | Example |
|-------|---------|---------|
| `hardware_type` | **Class dispatch key** — must match Python class name exactly | `"Quadrupole"`, `"Screen"`, `"Shutter"` |
| `hardware_class` | Organisational category — used for directory structure | `"Magnet"`, `"Diagnostic"`, `"Shutter"` |

The YAML directory structure follows:
`YAML/{hardware_class}/{hardware_type}/{element_name}.yaml`

## Adding a New Element Type

1. Create the class in `laura/models/element.py`, inheriting from
   `PhysicalBaseElement` (if it has position data) or `Element` (if not)
2. Set `hardware_type` as a frozen `Field` default matching the class name
3. The class is **automatically** registered in `MODEL_REGISTRY` at import time
4. YAML files with matching `hardware_type` will be parsed into the new class
