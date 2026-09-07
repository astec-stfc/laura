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
       ├─ resolve_inheritance(dict, namespace)
       │       If the dict names a parent via `inherits_from` / `inherit`,
       │       merges the parent's raw dict underneath it. Recurses up the
       │       chain. Position, identity and topology are never inherited.
       │       No-op — and returns the same object — for the vast majority
       │       of elements, which inherit nothing.
       │
       ▼
interpret_YAML_Element(dict)
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

#### interpret_YAML_Element

The core dispatch function:

```python
def interpret_YAML_Element(elem: dict, exclude_set=None):
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
from laura.Importers.YAML_Loader import read_YAML_Element_File

element = read_YAML_Element_File("path/to/element.yaml", validate=True)
```

When `validate=True` the raw dict is checked against
`laura/schema/generated/laura_element.schema.json` before Pydantic parsing,
surfacing schema violations with explicit error messages rather than silent
`None` returns.

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
2. `fast_get_element_metadata()` extracts `name`, `machine_area` and
   `inherits_from` via **regex** (reads first 2000 chars only — no YAML parsing)
3. A `LazyElementDict` is created mapping `name → filepath`
4. Full YAML parsing + model validation happens only on first access to that element

This makes startup fast even for directories with hundreds of YAML files.

Inheritance does not undo that. The dict also holds a `RawFileNamespace` over
the same `name → filepath` map, which reads and caches a parent's **raw** dict
on demand — so resolving a child costs one extra file read per distinct parent,
not per child, and only for children that actually declare one.

## Element Inheritance

An element may name another element's definition and state only what differs:

```yaml
INJ_QUAD_01:
  name: INJ_QUAD_01
  inherits_from: QUAD_TYPE_A    # `inherit:` also accepted, matching PALS
  physical: {s: 0.50}
  magnetic: {k1l: 0.85}
```

See `examples/testing/inheritance_example.py` for a worked FODO cell.

### Why it merges raw dicts, not models

Resolution happens on the parsed-YAML dict, **before** `interpret_YAML_Element`.
This is the whole reason the step sits where it does: a parent that has already
been through Pydantic has every default filled in, so a merge of *models* cannot
tell "the parent set `length: 1.0`" from "the parent never mentioned `length`
and 1.0 is the default". On raw dicts, a key that is absent is absent.

The merge is recursive and key-by-key, with the child winning. A non-dict value
(a list of coefficients, say) is replaced outright rather than merged, and an
explicit `null` in the child unsets the inherited value — distinct from omitting
the key, which inherits it.

Both sides are canonicalised to the model's own field names before merging.
Without that, a parent writing `length:` and a child writing `magnetic_length:`
would produce a dict carrying both — two spellings of one field — and
`AliasChoices` order would hand the *parent* the win, silently discarding the
child's override.

### What is never inherited

| Excluded | Why |
|----------|-----|
| `name`, `alias`, `virtual_name` | Identity. A child is a different element. |
| `subelement`, `upstream`, `downstream` | Topology. Inherited neighbours are wrong neighbours. |
| `physical.middle` / `s` / `s_point` / `datum` / `reference_placement` | Position. |
| `physical.rotation`, `global_rotation` | Orientation, which is placement. |
| `physical.survey`, `error`, `physical_angle` | Measured for one specific device. |

Position is the one that matters. In PALS an element carries no position — the
line places it — so inheriting a definition wholesale is safe. In LAURA position
lives on the element, so a child that states no position of its own would land
exactly on top of its parent: a lattice that is wrong but perfectly valid, and
wrong in every export downstream. Inheriting `reference_placement` alongside a
parent's `s` would instead trip `_check_placement_exclusivity`, and a failing
element is a skipped one.

`physical.length` **is** inherited — it is a property of the device, and it is
most of what makes the compact form worth writing.

### Templates

A definition that exists only to be inherited from should not also become a
machine element, appearing in the lattice and in every export. Two ways to say
so, one per loading mode:

| Mode | Template lives in |
|------|-------------------|
| Combined file | the top-level `_templates:` key |
| Directory | any `_`-prefixed filename (`_quad_type_a.yaml`) |

Both are resolvable as parents by name; neither reaches `machine.elements`.
`collect_template_filenames()` requires an `_`-prefixed file to have both a
`name:` and a `hardware_type:` before treating it as a template, which keeps
controls `_schema.yaml` files out.

### Failures and warnings

Two new `ElementLoadError` reasons, on the same channel as every other load
failure — recorded on `errors` / `machine.load_errors` by default, raised under
`strict=True`:

| Reason | Condition |
|--------|-----------|
| `missing_parent` | the named parent is not in the namespace |
| `inheritance_cycle` | the chain revisits a name; the detail spells out `A -> B -> A` |

An unresolvable parent is precisely the kind of silent loss the errors list
exists for: without it the element still parses, just without its length, its
strength or its controls.

Two conditions warn instead, because the element is fine but something about it
is quietly wrong:

- **Parent keys the child's model cannot hold.** `baseElement` is
  `extra="ignore"` (see below), so inheriting a `Magnet` block into a `Drift`
  drops it without a word.
- **An inherited literal identifier naming an ancestor.** A parent spelling its
  PVs out as `Q1:SETI` rather than `{name}:SETI` hands every child the parent's
  power supply. The whole ancestor chain is checked, not just the immediate
  parent.

## Sequential (drift-based) placement

An element may state where it sits in one of three ways — global xyz
(`middle` / `position` / `centre`), an arc length (`s` with `s_point`), or
`reference_placement` against another element's frame. It may also state none
of them, and let the section's `order` and the lengths in it do the work:

```yaml
sections:
  S01:
    elements: [Q1, D1, Q2, D2, Q3]   # order + lengths fix everything
```

This is how MAD-X, elegant and PALS define a lattice, hand-written `Drift`
elements and all. Before it was supported such a section resolved with every
element stacked on top of the others at the origin, silently.

### How it resolves

`MachineModel._resolve_all_positions` runs two steps per section ahead of the
existing `resolve_positions`:

```
_number_sequential_repeats()               # one element per occurrence
   └─ section.number_repeated_elements()
section._resolve_sequential_placement()    # accumulate, write s / s_point
section.resolve_positions()                # unchanged
```

The section is **normalised to `s`** rather than given a coordinate system of
its own. From `resolve_positions` onwards a hand-written drift lattice and an
imported MAD-X one take the identical, already-tested path — the same bend arc
geometry, orientation inheritance and trajectory construction — and `s` is left
on each element afterwards as a real value, so `machine["Q2"].physical.s`
answers the obvious question.

### Details that matter

- **The trigger** is any element in the section awaiting a position
  (`SectionLattice.is_sequential`). Sections where everything states a position
  are untouched.
- **Drifts stay elements.** The importers consume drifts, absorbing their
  length into `s`; a hand-written one is kept, because the user named it and
  will expect `machine["D1"]` to resolve. The exporters synthesise drifts from
  *gaps*, so a kept drift leaves no gap and nothing is doubled up.
- **Anchoring.** The first element that states an `s` anchors the line and
  accumulation resumes from its exit; that is how "this line starts at s=12" is
  written. An `s` stated mid-line re-anchors the rest, and warns if it disagrees
  with what the elements before it accumulate to. The anchor has to use `s`:
  converting a stated xyz back to an arc length needs the trajectory that does
  not exist yet, so a section mixing sequential elements with xyz-positioned
  ones still raises from `_detect_coordinate_system`.
- **Repeated names are split.** Reusing one drift a dozen times over is
  idiomatic, but a `MachineModel` stores one placement per name, so each
  occurrence gets its own copy — `D1.1`, `D1.2`, … — matching what the
  importers produce. The bare original is retired if no other section still
  lists it.
- **Section order is the tie-break.** Every `s` here is a sum of floats rather
  than a number anyone typed, so `_resolve_s_coordinates` compares entrance
  positions within a tolerance (`math.isclose`) instead of sorting on the raw
  float. Without that, a zero-length marker immediately before a cavity could
  come back on either side of it.
- **`_position_stated`** is the flag the whole thing rests on, taken in
  `PhysicalElement.model_post_init` *before* `middle` gets its origin default.
  Afterwards an unpositioned element is indistinguishable from one deliberately
  placed at the origin — by value and via `model_fields_set` alike, since the
  default assignment re-runs the validators and marks `middle` set. It does not
  survive a `model_dump()` round-trip, so placement runs on freshly-loaded
  objects.

### Interaction with inheritance

Position is never inherited (see above), so every child of a shared template
arrives unpositioned — which is exactly the sequential trigger. A template
carrying `length` plus a section order is enough to define a whole lattice.

## Repeated and nested lines

A section's element list may repeat an entry and may splice in another section,
so a channel of identical cells is written once:

```yaml
sections:
  fodo_channel:
    - fodo_cell: {repeat: 3}

  fodo_cell: [drift1, quad1, drift2, quad2, drift1]
```

`expand_section_order` (`laura/models/elementList.py`) flattens this into the
ordinary `List[str]` during `_normalise_section_definitions`, which is the one
funnel every authored section passes through. Nothing downstream changes: the
machine sees the fifteen-name order it would have seen had the channel been
typed out in full, and sequential placement then splits the repeated names per
occurrence exactly as it does for a name written twice by hand.

Three rules, all chosen so nothing has to be guessed:

* **An entry is a bare name, or a single-key mapping carrying options.**
  `repeat` is the only option. Anything else is a `TypeError` naming the entry
  and its section, rather than a silently ignored key.
* **A name that matches another section is a nested line**; anything else is an
  element name. Expansion runs as a second pass, once every section is known, so
  a line may be used before it is defined. A line no layout lists never becomes
  a section of the machine, so defining one purely to be reused costs nothing.
* **A cycle is a `LatticeError`, and a `repeat` of zero is a `ValueError`.**
  A cycle would otherwise be an infinite lattice; a zero count is more likely a
  mistake than a deliberately empty entry.
* **A negative count reverses the entry, then repeats it** — MAD-X's `-LINE`,
  so `(cell, -cell)` is a mirror-symmetric line from one definition. This is
  reversal of the *order* only. Every element is still entered at its own
  entrance face, so nothing about the elements changes and the result is a
  different lattice built from the same definitions. It is **not** the line
  traversed backwards: `m dv/dt = qv × B` is not invariant under `t → −t`, so a
  reversed traversal is equivalent to a forward one with the opposite-sign
  particle, and every normal multipole's effect changes sign in the beam frame.
  That transform is `laura.models.reversal.reverse_element`, and it is
  deliberately not applied here: a negative `repeat` changes the order and
  nothing else.

The authored list is kept on the section as `_authored_order` — the same bargain
as `inherits_from` and `_repeat_origins` — so the exporter can write the compact
form back out.

One combination is refused, by machinery that predates this: a line that repeats
a name **and** is itself listed in a layout, so that it is both a section of the
machine and spliced into another one. Both sections then want their own
placement of the same numbered copies, and the load fails with the mixed
positioning error rather than picking one. Nesting a line that repeats nothing,
or nesting a line that no layout lists, is fine.

## Writing the compact form back out

Loading expands: a template is merged into its children, an order plus lengths
becomes an `s` on every element. Exporting with the defaults writes that
expansion, so a lattice written in two hundred compact lines comes back as two
thousand explicit ones. `laura.Exporters.YAML` can invert each expansion
instead, and the two are independent flags on the same call:

```python
export_machine_combined_file(
    "out", machine,
    position_mode="sequential",     # order + lengths, no positions
    collapse_inheritance=True,      # inherits_from + only what differs
)
```

Both are off by default. Each is a diff against what the loader would have
produced, and each fails in the verbose direction: anything that cannot be
shown to be redundant is written out in full.

### `position_mode="sequential"`

The inverse of the accumulator. An element that abuts its predecessor is
written with no `s`, `s_point`, `middle` or `reference_placement` at all; the
first element of a section may drop its position when the section starts at the
origin. An element that does **not** abut keeps an explicit `s` at
`s_point: start`, anchoring what follows it, and warns — a gap with no `Drift`
element in it is spacing that exists nowhere else in the file, and dropping the
position would close it.

The geometry now lives in the section order, so the export is not reloadable
without it. `export_machine` and `export_machine_combined_file` therefore write
`_sections.yaml` alongside the elements in this mode (`write_sections=False` to
suppress it). The `_` prefix keeps a directory-mode reload from reading it as an
element.

The repeated-name split is undone on the way out, by `_repeat_aliases`: `D1`
listed three times was expanded into `D1.1`, `D1.2`, `D1.3` on load only to give
each occurrence somewhere to hold its own position, and this mode writes no
positions, so it comes back out as one `D1` element listed three times — the
order as it was authored, reloading to the same placements. A group stays
expanded, with a warning, if one of the copies has been changed since load (the
copies no longer mean the same thing) or if the bare name is still an element in
its own right (another section's placement of it would be overwritten). Nothing
happens in the other position modes, where the copies differ by exactly the
position they were made to hold.

`_authored_sections` does the same for authored repetition, and for the whole
`_sections.yaml` at once rather than per group. The compact list replaces the
flat one, the definition of every line it refers to is added beside it, and then
the result is re-expanded and compared against the order the machine actually
holds. Only if that matches is the compact map written; otherwise every section
goes out fully expanded with a warning. Checking the finished file rather than
each section in isolation costs one extra expansion and removes the need to
enumerate the ways a collapse could go wrong.

### `collapse_inheritance=True`

The inverse of `resolve_inheritance`. The parent named by `inherits_from` is
resolved from `template_root` (defaulting to `machine.element_list`, as
`schema_root` already does) and every key the child holds identically is
dropped. The comparison is on raw values, so a parent and child that merely
*look* different — a list against an `{x, y, z}` mapping — keep the key.
`NON_INHERITED_FIELDS` is honoured in reverse: `name` and the position keys are
kept however well they match, because dropping one would lose it outright
rather than shorten it.

The definitions inherited from travel with the export, whole chains of them:
into the combined file's `_templates:` block, or, in directory mode, to
`_<name>.yaml` at the export root (`copy_templates=False` to suppress). A
parent that is itself an exported element is left where it is rather than
duplicated. A parent that cannot be found warns and the element is written out
expanded, with the now-dangling `inherits_from` dropped — the same failure
behaviour as `collapse_schema` one level down.

### Empty containers are pruned

Unconditional, and it applies to every export. `exclude_defaults=True` drops a
field equal to its default, but a *sub-model* whose own fields are all defaults
is not equal to anything and dumps as `{}` — so every element used to carry
`manufacturer: {}`, `simulation: {}`, `electrical: {}`,
`physical: {error: {}, survey: {}}` and one entry per unused multipole order
around the two lines that said what it was. `_prune_empty` drops them
depth-first, along with any key a collapse emptied. Nothing is lost: an absent
key is rebuilt from the same defaults the empty container stood in for.

`0`, `0.0`, `False` and `""` are values someone may have written and are never
empty by this test. Two things are pruned only under a rule, both established
by measurement rather than by reading:

- **`_MEANINGFUL_WHEN_EMPTY`** — `physical.middle` and its siblings are kept
  even when empty. `Position(0, 0, 0)` *equals* its own default, so a resolved
  element at the origin exports as `middle: {}`; drop it and the element
  reloads **unpositioned**, which turns a globally positioned section into a
  sequential one and raises on the mix. The same "an absent value is not the
  same as a default one" trap as the `_position_stated` capture, reached from
  the export side.
- **`_MULTIPOLE_SLOTS`** — a multipole slot carrying nothing but its own
  `order` (`K2L: {order: 2}`) is restating its key, and is dropped whole. The
  container fills `order` in from the slot name for entries the file omits, so
  that is lossless. Dropping `order` from a slot that *does* carry a strength
  is not: a supplied entry keeps what the file gave it and would come back as
  order 0.

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

`validate=True` does **not** currently catch this. `validate_element_dict`
checks against the document root of `laura_element.schema.json`, which sets
`additionalProperties: true` — so an unknown key passes validation and is then
dropped by Pydantic exactly as before. Tightening it would reject files that
load today, so it is tracked as a known issue rather than fixed in passing.

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
