# YAML Loading Pipeline

How LAURA turns YAML files on disk into Pydantic element objects.

## Overview

```
YAML file on disk
       │
       ▼
yaml.load()  →  Python dict
       │
       ├─ (optional) validate_element_dict(dict)
       │       JSON Schema validation against laura_element.schema.json
       │       Raises ValidationError on schema violations.
       │       Pass validate=True to any loader to enable.
       │
       ▼
interpret_yaml_element(dict)
       │
       ├─ reads dict["hardware_type"]   (e.g. "Quadrupole")
       │
       ├─ ADAPTERS.get("Quadrupole")    (lazy TypeAdapter lookup)
       │     │
       │     └─ ELEMENT_REGISTRY["Quadrupole"] → Quadrupole class
       │           └─ TypeAdapter(Quadrupole) created on first use
       │
       └─ adapter.validate_python(dict) → Quadrupole instance
```

## Key Components

### File: `laura/models/element.py`

#### ELEMENT_REGISTRY

Defined at the bottom of `laura/models/element.py`, and derived from that
module's own classes — every `Element` subclass carrying a concrete
`hardware_type` default is registered under that default:

```python
ELEMENT_REGISTRY: dict[str, type] = {
    _field.default: _cls
    for _cls in list(vars().values())
    if isinstance(_cls, type)
    and issubclass(_cls, Element)
    and (_field := _cls.model_fields.get("hardware_type")) is not None
    and isinstance(_field.default, str)
    and _field.default != "Generic"
}
```

The `hardware_type` **default** is the lookup key, not the class name — the two
happen to coincide for every element defined so far, but it is the field default
that is authoritative. A YAML file's `hardware_type` must match one of them
(e.g. `"Quadrupole"`, `"Screen"`, `"Shutter"`).

Because the registry is derived rather than hand-listed, a new element class is
picked up with no separate registration step.

The schema enforces this via `slot_usage: equals_string:` constraints on
each concrete class — violations are caught at the ontology level as well as
at runtime.

### File: `laura/Importers/YAML_Loader.py`

#### ADAPTERS (LazyAdapterDict)

Wraps `ELEMENT_REGISTRY` with lazy `TypeAdapter` creation. The first time a
`hardware_type` is encountered, a Pydantic `TypeAdapter` is created for that
class and cached.

#### interpret_yaml_element

The core dispatch function:

```python
def interpret_yaml_element(elem: dict, exclude_set=None):
    hw_type = elem.get("hardware_type")
    if not hw_type:
        _log.warning("Skipping element '%s': no hardware_type field", name)
        return None
    adapter = ADAPTERS.get(hw_type)
    if adapter is None:
        _log.warning("Skipping element '%s': unregistered hardware_type '%s'", name, hw_type)
        return None
    if exclude_set:
        elem = {k: v for k, v in elem.items() if k not in exclude_set}
    try:
        return adapter.validate_python(elem)
    except Exception as exc:
        _log.error("Failed to parse '%s' [%s]: %s", name, hw_type, exc)
        return None
```

**Critical behaviour:** the return value on failure is `None`, not an
exception — a bad element is dropped rather than aborting the load. The reason
is logged, so raise the log level to see it:

```python
from laura import set_log_level
set_log_level("DEBUG")     # or "WARNING" for skips and errors only
```

The relevant loggers are `laura.loader` (one DEBUG line per parsed element,
WARNING on skip, ERROR on validation failure) and `laura.model` (layout and
section building). Pass `validate=True` to turn schema violations into raised
errors instead.

#### validate_element_dict (optional schema validation)

An optional pre-parse check against the generated JSON Schema:

```python
from laura.importers.yaml_loader import read_yaml_element_file

element = read_yaml_element_file("path/to/element.yaml", validate=True)
```

When `validate=True` the raw dict is checked against
`laura/schema/generated/laura_element.schema.json` before Pydantic parsing,
surfacing schema violations with explicit error messages rather than silent
`None` returns.

### Loading Modes

| Mode | Function | When Used |
|------|----------|-----------|
| Single YAML file | `read_yaml_element_file(path)` | One element per file |
| Combined file | `read_yaml_combined_file(path)` | Summary JSON/YAML with many elements |
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
class IgnoreExtra(ModelBase, FunctionalMixin):
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

Using `validate=True` on load can surface these issues before they reach
Pydantic parsing.

## hardware_type vs hardware_class

| Field | Purpose | Example |
|-------|---------|---------|
| `hardware_type` | **Class dispatch key** — must match a class's `hardware_type` field default exactly | `"Quadrupole"`, `"Screen"`, `"Shutter"` |
| `hardware_class` | Organisational category (a `HardwareClassEnum` value) — used for directory structure | `"Magnet"`, `"Diagnostic"`, `"Shutter"` |

The YAML directory structure follows:
`YAML/{hardware_class}/{hardware_type}/{element_name}.yaml`

The `hardware_type` values in YAML are validated by the LinkML schema via
`slot_usage: equals_string:` constraints on each concrete class.

## Adding a New Element Type

1. Add the class definition to `laura/schema/YAML/laura_schema.yaml`
   (see [element-hierarchy.md](element-hierarchy.md#adding-a-new-element-type))
2. Regenerate `_generated.py`:  `python laura/schema/generate_pydantic.py`
3. Create the Python wrapper in `laura/models/element.py`, inheriting from
   `PhysicalBaseElement` (if it has position data) or `Element` (if not),
   plus the generated base class
4. Set `hardware_type` as a frozen `Field` default matching the class name
5. The class is **automatically** registered in `ELEMENT_REGISTRY` at import
   time; YAML files with matching `hardware_type` will be parsed into the new
   class
