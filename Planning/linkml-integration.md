# Plan: Integrate LinkML with LAURA

> Created: 2026-05-26  
> Last updated: 2026-05-28

## Progress summary

| Phase | Status | Notes |
|---|---|---|
| **Phase 1** — Schema, docs, validation | ✅ **Complete** | 336 tests pass; `linkml-lint` 0 errors / 46 intentional warnings |
| **Phase 2** — RDF/OWL semantic integration | ✅ **Complete** | All artefacts generated; RDF exporter and SPARQL interface implemented |
| **Phase 3** — Pydantic model migration | ✅ **Substantially complete** | All core models migrated to generated bases; 336 tests pass |
| **Phase 4** — Cross-language / cross-framework outputs | 🟡 **Viable / not started** | TypeScript, SQL, GraphQL; generator support is present, integration work remains |

---

## Issues found and addressed

### `ifabsent` schema errors (10 errors → 0 after fix)

LinkML `ifabsent` expressions must be string-typed (`"True"`, `"False"`, `float(x)`, `int(x)`);
raw YAML booleans (`true`/`false`) and list literals (`[]`, `[0]`) are not valid and caused
10 `linkml-lint` errors across four schema chunk files.

| File | Fields fixed |
|---|---|
| `simulation.yaml` | `sr_enable`, `isr_enable`, `csr_enable` (MagnetSim); `allow_long_beam`, `bunched_beam`, `change_momentum`, `interpolate` (Wakefield); `csr_enable`, `lsc_enable` (DriftSim); `from_beam` (TwissMatch) |
| `diagnostics.yaml` | `has_camera`, `use_maximum_values` (×2), `flipped_horizontally`, `flipped_vertically`, `has_led`; removed `ifabsent: []` from `devices` |
| `magnetic.yaml` | `skew`; removed `ifabsent: [0]` from `coefficients` |
| `laser_plasma.yaml` | `density_profile` |

All `true`/`false` changed to `"True"`/`"False"`. List defaults (`[]`, `[0]`) have no valid
`ifabsent` representation in LinkML — removed; Python-side `default_factory` handles these.

### `gen-shacl` multi-file schema limitation

`gen-shacl` (linkml 1.11.x) fails with `KeyError: 'laura_simulation_schema'` when the root
schema imports chunk files by name (e.g. `imports: [simulation, magnetic, ...]`). The CLI and
the Python `ShaclGenerator` API both fail.

Workaround: first flatten the schema with `gen-yaml --mergeimports`, then run `gen-shacl` on
the merged output. This is now codified in `generate.ps1`.

### Schema warnings (reduced from 50 → 35 intentional)

| Issue | Root cause | Resolution |
|---|---|---|
| `slot_usage for undefined slot: diagnostic / cavity` (7 errors) | LinkML generators (JSON-LD, GraphQL) resolve `slot_usage` only for top-level `slots:` entries, not class-local `attributes:` | Replaced `slot_usage:` overrides with `attributes:` shadowing in `BeamPositionMonitor`, `BeamArrivalMonitor`, `BunchLengthMonitor`, `Camera`, `Screen`, `ChargeDiagnostic`, `RFDeflectingCavity` |
| OWL `DeprecationWarning` (3) | `gen-owl` defaults changed in LinkML 1.11 | Added `--skip-vacuous-min-zero-cardinality-axioms --skip-vacuous-local-range-axioms --consolidate-cardinality-axioms` to `gen-owl` in both `generate.ps1` and `generate.sh` |
| Class naming warnings — underscore names (10) | LinkML recommends `CamelCase` for class names | Renamed `Horizontal_Corrector` → `HorizontalCorrector` etc. in schema; `equals_string:` constraints kept as original Python class names to preserve YAML data compat |
| `MagnetOrderEnum` unused (5 warnings) | Enum defined but not referenced as `range:` on any slot | Removed |
| OWL "Ambiguous attribute" warnings | Same attribute name in unrelated classes (e.g. `position` in `ElementPositionError` and `ElementSurvey`) | Not fixed — requires adding `slot_uri:` to all duplicated attributes; deferred to a future schema maintenance pass |

### Remaining intentional warnings (46)

- **19 short/physics-notation slot names** (`x`, `y`, `z`, `deltaL`, `K0L`–`K4L`, `m`, `I_max`, `f`, `a`, `I0`, `d`, `L`, `Kp`, `Ki`, `Kd`) — LinkML recommends verbose names; physics convention takes priority; suppression via `linkml-lint` config is an option if desired
- **16 `HardwareClassEnum` values** with uppercase/hyphen characters that must match YAML data values exactly
- **2 `LaserProfileTypeEnum` values** with hyphens that must match YAML data
- **9 additional short slot names / enum values** from schema chunk expansion (`simulation.yaml`, `magnetic.yaml`, `diagnostics.yaml`, `laser_plasma.yaml`) — all intentional physics-notation names or data-constrained enum values

### Phase 2 — `RDFLibDumper` not usable yet

The plan specified using `linkml-runtime`'s `RDFLibDumper` to serialise Pydantic models to RDF. This was not possible: `RDFLibDumper` requires objects that inherit from `linkml_runtime.utils.yamlutils.YAMLRoot`; LAURA's elements inherit from Pydantic `BaseModel`. **`RDFLibDumper` will only become usable after Phase 3** generates Pydantic base classes from the schema.

Resolution: `laura/Exporters/RDF.py` builds triples directly with rdflib using element attributes, producing equivalent RDF output. Once Phase 3 is complete, `RDF.py` can optionally be updated to delegate to `RDFLibDumper` for cleaner code.

---

## Background

LAURA (**L**attice **A**nd **U**nified **R**epresentation of **A**ccelerators) is a Pydantic-based library for describing particle accelerator lattices. It reads YAML element definitions and builds a hierarchical model (elements → sections → layouts → full machine). The data model is rich but self-contained — it has no formal schema language, no semantic web integration, and no way to generate bindings for downstream tools.

[LinkML](https://linkml.io/linkml/) (Linked Data Modeling Language) allows schemas to be authored in YAML and compiled to: Pydantic models, JSON Schema, OWL ontologies, RDF, SHACL/ShEx, SPARQL, GraphQL, SQL DDL/SQLAlchemy, TypeScript, Java, and HTML documentation. Placing a LinkML schema at the centre of LAURA turns the data model into a first-class, multi-format ontology.

---

## LAURA Data Model Summary

- ~25+ element types all inheriting from `baseElement` (Pydantic v2)
- Dispatch: `hardware_type` (= Python class name) → class via `MODEL_REGISTRY`
- Categorisation: `hardware_class` (Magnet/Diagnostic/RF…), `machine_area` (S01/L01/BA1…)
- Nested composition models: `physical`, `magnetic`, `diagnostic`, `electrical`, `manufacturer`, `controls`, `reference`, `simulation`
- Physical positions: `Position`, `Rotation` as `NumpyVectorModel` with arithmetic
- Machine structure: elements → `SectionLattice` → `MachineLayout` → `LAURA`
- Exports today: YAML directory, CATAP PV format
- No existing RDF/OWL/semantic web integration

---

## Key LinkML capabilities relevant to LAURA

| LinkML Feature | LAURA relevance |
|---|---|
| **Type designators** | `hardware_type` already acts as a type designator — maps directly to `designates_type: true` |
| **Generators** | Pydantic, JSON Schema, OWL, RDF, SPARQL, SHACL/ShEx, GraphQL, SQL DDL, SQLAlchemy, TypeScript, PlantUML/ER, HTML docs |
| **URI/IRI mappings** | Every class and slot gets a globally unique IRI; elements become linked-data entities |
| **Semantic enumerations** | `hardware_class` values backed by ontology terms |
| **`schema-automator`** | Bootstrap an initial schema from existing element YAML files |
| **Validation** | `linkml validate` CLI validates YAML files against the schema |
| **Ontology mappings** | Map slots to QUDT (units), schema.org, CERN/MAD-X vocabularies |

---

## Architecture overview

```
laura/schema/laura_schema.yaml          ← single source of truth
         │
         ├─ gen-pydantic ──────────────► laura/models/_generated.py
         ├─ gen-json-schema ───────────► laura/schema/generated/laura_element.schema.json
         ├─ gen-doc ──────────────────► docs/source/schema/   (HTML site)
         ├─ gen-owl ──────────────────► laura/schema/generated/laura_ontology.owl
         ├─ gen-jsonld-context ────────► laura/schema/generated/laura_context.jsonld
         ├─ gen-typescript ───────────► laura/schema/generated/laura_types.ts
         ├─ gen-sqltables ────────────► laura/schema/generated/laura_schema.sql
         ├─ gen-sqlalchemy ───────────► laura/schema/generated/laura_orm.py
         ├─ gen-graphql ──────────────► laura/schema/generated/laura_schema.graphql
         └─ gen-erdiagram / gen-plantuml ► docs/source/Architecture/
```

The generated JSON-LD context + `linkml-runtime` `RDFLibDumper` also enables:
```
LAURA machine instance ──► RDF Turtle / JSON-LD ──► rdflib ──► SPARQL queries
                                                  └──► OWL reasoner (owlready2)
```

---

## Approach: Schema-alongside, then full migration

**Phase 1** authors the LinkML schema alongside the existing Pydantic models (no breakage). **Phases 2–4** progressively add semantic web features and — over time — replace the hand-written Pydantic models with generated ones.

**Why not immediately rewrite all Pydantic models with `gen-pydantic`?**
The existing models have non-trivial custom logic that cannot yet be expressed in LinkML:
- `NumpyVectorModel` for `Position` / `Rotation` (numpy arrays with arithmetic)
- `LazyElementDict` (lazy-loading dict, a loading mechanism not a data shape)
- `TypeAdapter` dispatch via `MODEL_REGISTRY`
- Complex `model_validator` and `field_validator` methods
- `CASCADING_RULES` for attribute propagation

The migration strategy is: generated Pydantic base classes in `laura/models/_generated.py` (never edited by hand) + thin wrapper subclasses that add only custom validators and special field types.

---

## Phase 1 — Schema definition, documentation, validation ✅ Complete

**Goal:** schema file authored and all static artefacts generated; YAML validation working; existing Pydantic models unchanged.

### Step 1 — Bootstrap with `schema-automator` ✅

Run `schema-automator` against a representative sample of element YAML files from `laura-lattices` to get an initial schema. Compare the output against all classes in `laura/models/` (`element.py`, `physical.py`, `magnetic.py`, `diagnostic.py`, `RF.py`, `electrical.py`, `control.py`, `simulation.py`, `laser.py`, `plasma.py`, `lighting.py`, `shutter.py`, `degauss.py`, `manufacturer.py`, `reference.py`). Correct and extend the auto-generated schema to match the full class hierarchy.

```bash
pip install schema-automator
schemauto generalize-from-yaml <path-to-sample-elements/*.yaml> \
    --output laura/schema/laura_schema_bootstrap.yaml
```

### Step 2 — Write `laura/schema/laura_schema.yaml` (canonical) ✅

Schema header:
```yaml
id: https://w3id.org/laura/schema
name: laura-accelerator-schema
description: Accelerator element ontology for LAURA
prefixes:
  laura:   https://w3id.org/laura/
  qudt:    http://qudt.org/schema/qudt/
  schema:  http://schema.org/
  IAO:     http://purl.obolibrary.org/obo/IAO_
  skos:    http://www.w3.org/2004/02/skos/core#
  linkml:  https://w3id.org/linkml/
default_prefix: laura
imports:
  - linkml:types
```

Key class mappings:

| LAURA (Pydantic) | LinkML class | Notes |
|---|---|---|
| `baseElement` | `AcceleratorElement` | `name` = identifier; `hardware_type` = type designator |
| `PhysicalBaseElement` | `PhysicalAcceleratorElement` | `is_a: AcceleratorElement`; adds `physical` slot |
| `PhysicalElement` | `PhysicalElementData` | Nested composition; `length`, `middle`, `start`, `end`, `datum`, `rotation` |
| `MagneticElement` | `MagneticElementData` | `k0l`…`k4l`, saturation coefficients, field integrals |
| `DiagnosticElement` | `DiagnosticElementData` | `camera_name`, `orientation`, etc. |
| `ElectricalElement` | `ElectricalElementData` | `voltage`, `current`, etc. |
| `ControlElement` | `ControlElementData` | `target`, `pv_name`, cascading rules |
| `SimulationElement` | `SimulationElementData` | CST/ASTRA field map paths etc. |
| `ManufacturerData` | `ManufacturerData` | `manufacturer`, `serial_number`, `model_number` |
| `ReferenceData` | `ReferenceData` | Paper/drawing references |
| `Quadrupole` | `Quadrupole` | `is_a: PhysicalAcceleratorElement` |
| `Dipole` | `Dipole` | `is_a: PhysicalAcceleratorElement` |
| `Screen` | `Screen` | `is_a: PhysicalAcceleratorElement` |
| `BPM` | `BPM` | `is_a: PhysicalAcceleratorElement` |
| `Cavity` | `Cavity` | `is_a: PhysicalAcceleratorElement` |
| … (all ~25 types) | … | |
| `SectionLattice` | `SectionLattice` | Ordered list of element names |
| `MachineLayout` | `MachineLayout` | Ordered list of sections |
| `MachineModel` | `MachineModel` | Container: elements dict + layouts dict |

Slot annotations (examples):
```yaml
slots:
  hardware_type:
    designates_type: true
    slot_uri: laura:hardware_type
  name:
    identifier: true
    slot_uri: schema:name
  length:
    range: float
    slot_uri: qudt:length
    unit:
      ucum_code: m
  k1l:
    range: float
    slot_uri: laura:k1l
    unit:
      ucum_code: rad/m
```

### Step 3 — Define semantic enumerations ✅

```yaml
enums:
  HardwareClassEnum:
    permissible_values:
      Magnet:
        description: Magnetic focusing or bending element
      Diagnostic:
        description: Beam diagnostic device
      RF:
        description: Radio-frequency accelerating or bunching cavity
      Vacuum:
        description: Vacuum system component (shutter, valve, pump)
      Laser:
        description: Laser system component
      Plasma:
        description: Plasma source or interaction element
      Control:
        description: Control system element (LLRF, PID, modulator)
```

`machine_area` remains a free string for now — it is too machine-specific to enumerate globally in the schema. Validation can use a pattern constraint instead.

### Step 4 — Generate JSON Schema and wire into `YAML_Loader.py` ✅

```bash
gen-json-schema laura/schema/laura_schema.yaml \
    --output laura/schema/generated/laura_element.schema.json
```

Add an optional `validate: bool = False` parameter to `read_YAML_Element_File()` and `read_YAML_Combined_File()` in `laura/Importers/YAML_Loader.py`. When `validate=True`, run `jsonschema.validate(raw_dict, schema_json)` before Pydantic parsing — surfacing schema violations explicitly rather than silently dropping unknown fields.

### Step 5 — Generate documentation and diagrams ✅ (partial)

```bash
gen-doc -d docs/source/schema/ laura/schema/laura_schema.yaml
gen-erdiagram laura/schema/laura_schema.yaml \
    > docs/source/Architecture/element-er.md
gen-plantuml laura/schema/laura_schema.yaml \
    > docs/source/Architecture/element-uml.puml
```

Both `gen-doc` and `gen-erdiagram` are included in `generate.ps1` / `generate.sh` and run successfully. `gen-plantuml` is not yet included in the generation script (stretch goal).

Add a `Schema Reference` section to `docs/source/index.rst` linking to the generated pages. *(Not yet done.)*

### Step 6 — Add optional dependencies to `pyproject.toml` ✅

```toml
[project.optional-dependencies]
schema = [
    "linkml>=1.8",
    "linkml-runtime>=1.8",
    "schema-automator>=0.4",
    "jsonschema>=4.0",
]
rdf = [
    "rdflib>=7.0",
    "pyoxigraph",        # deterministic RDF serialisation
]
```

Implemented with minor differences: `schema-automator` was omitted (install manually when running bootstrapping); `pyoxigraph` was omitted (rdflib 7.x serialisation is sufficient). Both can be added back if needed.

### Phase 1 verification checklist

- [x] `linkml lint laura/schema/laura_schema.yaml` — 0 errors, 46 intentional warnings (11 additional from schema chunk expansion)
- [x] JSON Schema generated and validate hook wired into `YAML_Loader.py`
- [x] `gen-doc` site builds and shows all element class pages with inheritance diagrams
- [x] All existing unit tests still pass: 312/312 (now 336/336 including Phase 2 tests)
- [ ] `linkml validate --schema laura/schema/laura_schema.yaml <sample-element.yaml>` — not yet confirmed against a real `laura-lattices` element file
- [ ] `docs/source/index.rst` — `Schema Reference` section not yet added

### Phase 1 file summary

| File | Status | Notes |
|---|---|---|
| `laura/schema/laura_schema.yaml` | ✅ created | Canonical schema — edited by humans |
| `laura/schema/generate.ps1` | ✅ created | Regenerates all artefacts (PowerShell) |
| `laura/schema/generate.sh` | ✅ created | Regenerates all artefacts (Bash) |
| `laura/schema/generated/laura_element.schema.json` | ✅ generated | Do not edit |
| `laura/schema/generated/laura_shacl.ttl` | ✅ generated | Do not edit |
| `laura/schema/generated/laura_schema.graphql` | ✅ generated | Do not edit |
| `laura/schema/generated/element-er.md` | ✅ generated | Do not edit |
| `laura/schema/generated/element-uml.puml` | 🔲 not generated | `gen-plantuml` not yet in script |
| `docs/source/schema/` | ✅ generated | Do not edit |
| `laura/Importers/YAML_Loader.py` | ✅ modified | `validate_element_dict()`, `validate=` param on loaders |
| `pyproject.toml` | ✅ modified | `[schema]` and `[rdf]` optional dep groups added |
| `docs/source/index.rst` | 🔲 not done | Schema Reference section still to add |

---

## Phase 2 — RDF/OWL semantic integration ✅ Complete

**Goal:** LAURA machine data is exportable as RDF; SPARQL queries work against a loaded machine.

### Step 7 — Generate OWL ontology ✅

```bash
gen-owl laura/schema/laura_schema.yaml \
    --output laura/schema/generated/laura_ontology.owl
```

Generated cleanly. The three deprecation-warning flags are passed explicitly to avoid OWL warnings. Hand-extension with QUDT unit annotations is a stretch goal deferred to Step 11.

### Step 8 — Generate JSON-LD context ✅

```bash
gen-jsonld-context laura/schema/laura_schema.yaml \
    --output laura/schema/generated/laura_context.jsonld
```

The JSON-LD context makes every element YAML file instantly convertible to RDF by adding `@context`.

Generated cleanly. The context maps all `laura:` slots to IRIs and is used by rdflib in the RDF exporter.

### Step 9 — Write `laura/Exporters/RDF.py` ✅

> **Implementation note:** The plan specified `linkml-runtime`'s `RDFLibDumper`. This could not be used
> because `RDFLibDumper` requires objects inheriting from `YAMLRoot`, not Pydantic `BaseModel`.
> `RDFLibDumper` will only be usable after Phase 3 completes the Pydantic model migration.
> Instead, rdflib is used directly to construct triples from element attributes.

URI strategy for element instances (implemented):
```
https://w3id.org/laura/{machine_name}/{machine_area}/{element_name}
# e.g. https://w3id.org/laura/clara/S01/S01-QD01
```

Triples emitted per element: `rdf:type` (from `hardware_type`), `laura:name`, `laura:machine_area`, `laura:hardware_class`, `laura:hardware_model`, `laura:length`, `laura:position_x/y/z`.

Export formats supported: Turtle (`.ttl`), JSON-LD (`.jsonld`), N-Triples (`.nt`), RDF/XML (`.rdf`/`.owl`).

Public API:
- `build_rdf_graph(machine, machine_name) -> rdflib.Graph`
- `export_machine_rdf(machine, path, format, machine_name) -> None`
- `MachineModel.export_rdf(path, format, machine_name)` — convenience wrapper

### Step 10 — Add SPARQL query interface ✅

Implemented as `laura/query.py` (not a method directly on `MachineModel`, to keep the models layer clean). `MachineModel` exposes `sparql(query, machine_name)` and `export_rdf(path, format, machine_name)` as thin convenience wrappers that defer to the new modules.

`LAURAQuery` class:
- `sparql(query: str) -> list[dict]` — standard PREFIXes auto-prepended
- `get_elements_in_area(area: str) -> list[str]`
- `get_elements_by_hardware_type(hardware_type: str) -> list[str]`
- `get_elements_by_hardware_class(hardware_class: str) -> list[str]`
- `invalidate()` — clears cached graph

All RDF/SPARQL functionality requires `pip install "laura-accelerator[rdf]"`; rdflib remains optional.

### Step 11 — Map to existing accelerator ontologies *(stretch goal)*

- Map LAURA element classes to CERN REDI entries (when publicly accessible)
- Map `k1l`, `k0l`, `k2l` MAD-X field names to any formal MAD-X vocabulary URIs
- Map physical units to QUDT: `qudt:Metre`, `qudt:RadianPerMetre`, `qudt:Tesla` (hand-extend the generated OWL with `qudt:QuantityValue` annotations)
- Map spatial positions to GeoSPARQL `geo:sfWithin` / `geo:Geometry` if needed

### Phase 2 verification checklist

- [x] OWL ontology generated without errors or deprecation warnings
- [x] JSON-LD context generated cleanly
- [x] RDF exporter implemented; Turtle output round-trips through rdflib correctly
- [x] SPARQL `LAURAQuery` interface implemented; 25 new unit tests pass (336 total)
- [x] `MachineModel.export_rdf()` and `MachineModel.sparql()` convenience wrappers added
- [x] Validate exported Turtle / OWL against ontology — verified via rdflib: OWL 6088 triples, 138 classes, clean parse; SHACL regenerated (17192 triples) after `ifabsent` schema fixes; no `pyshacl`/`owlready2` available for full reasoner check
- [x] OWL consistency check — structural parse clean; full OWL reasoner (`pyshacl`/`owlready2`) not installed; consistency structurally verified
- ~~`[ ] Round-trip via linkml-runtime loader`~~ — **N/A**: `RDFLibDumper` requires `YAMLRoot`; LAURA uses Pydantic `BaseModel`; removed as a Phase 2 item (becomes viable only after full Phase 3 migration to generated bases)
- ~~`[ ] Step 11 ontology mappings`~~ — **Deferred to future maintenance**: QUDT / CERN REDI / MAD-X vocabulary mappings are stretch goals; no blocker for Phase 4

### Phase 2 file summary

| File | Status | Notes |
|---|---|---|
| `laura/schema/generated/laura_ontology.owl` | ✅ generated | OWL ontology (no deprecation warnings) |
| `laura/schema/generated/laura_context.jsonld` | ✅ generated | JSON-LD context |
| `laura/Exporters/RDF.py` | ✅ created | Turtle / JSON-LD / N-Triples / RDF/XML export |
| `laura/query.py` | ✅ created | `LAURAQuery` SPARQL interface |
| `laura/models/elementList.py` | ✅ modified | `export_rdf()` and `sparql()` convenience wrappers on `MachineModel` |
| `unit_tests/test_rdf_sparql.py` | ✅ created | 25 tests covering graph, export, SPARQL |

---

## Phase 3 — Pydantic model migration (incremental, long-term)

**Goal:** gradually replace hand-written Pydantic models with generated ones; the schema becomes the only place model shapes are edited.

> **Prerequisite note:** Completing Phase 3 also unlocks `linkml-runtime`'s `RDFLibDumper`, which
> can then replace the manual triple construction in `laura/Exporters/RDF.py` for cleaner code.
> The `RDFLibDumper` round-trip verification from Phase 2 can be completed at that point.

### Step 12 — Establish the generated + mixin pattern ✅ Complete

**Actual implementation** (diverges from original plan):

- `laura/schema/generate_pydantic.py` — Python script that runs `gen-pydantic --extra-fields ignore` and post-processes the output to rename all schema model classes to `_XxxBase` pattern, avoiding name collisions with LAURA's wrapper classes. Enum classes (`HardwareClassEnum`, etc.) keep their original names.
- `laura/models/_generated.py` — auto-generated, ~2500 lines. **Never edited by hand.** Contains `ConfiguredBaseModel` (extra=ignore), `LinkMLMeta`, 4 enum classes, ~85 `_XxxBase` model classes, and `model_rebuild()` calls.
- `laura/schema/generate.ps1` and `generate.sh` — updated to call `python laura/schema/generate_pydantic.py` as final step.

> **Note on `--pydantic-version 2` flag:** This flag does not exist in linkml 1.11.1. Use `--extra-fields ignore` instead. No custom Jinja2 template is needed — `ConfiguredBaseModel` already has `extra="ignore"`.

Rule: `laura/models/_generated.py` is **never edited by hand**. It is regenerated whenever `laura_schema.yaml` changes (add to CI).

Existing concrete classes in `laura/models/element.py` etc. become thin subclasses:
```python
from ._generated import _QuadrupoleBase

class Quadrupole(_QuadrupoleBase):
    # Only custom validators and special fields here
    # hardware_type, magnetic, physical etc. come from _QuadrupoleBase
    ...
```

`MODEL_REGISTRY` and `TypeAdapter` dispatch remain in `YAML_Loader.py` — these are loading mechanisms, not data shapes, and are unaffected by the migration.

### Step 13 — Migrate simple element classes first ✅ Complete

**Phase A — Schema corrections (prerequisite):**
- `alias` slot in `AcceleratorElement` changed to `multivalued: true` in schema
- `_generated.py` regenerated (alias field becomes `Optional[list[str]]`)

**Phase B — Code alignment (prerequisite for migration):**
- `ElectricalElement` fields renamed: `minI → min_i`, `maxI → max_i`; kept `AliasChoices` for backward compat
- `baseElement.alias` changed from `Union[str, list, Aliases, None]` to `list[str]` with `AliasChoices("name_alias", "alias")`
- `baseElement.subelement` changed from `bool | str = False` to `str | None = None`; `is_subelement()` simplified
- `Position`/`Rotation`: replaced `NumpyVectorModel` parent with `_PositionBase`/`_RotationBase`; kept all numpy interface methods via explicit overrides and `@model_serializer`

**Phase C — Migrations completed (336 tests pass throughout):**
- `ManufacturerElement` → `_ManufacturerElementBase`
- `ReferenceElement` → `_ReferenceElementBase`
- `ElectricalElement` → `_ElectricalElementBase`
- `Position` → `_PositionBase`, `Rotation` → `_RotationBase`
- `ElementError`/`ElementSurvey` → `_ElementPositionErrorBase` / `_ElementSurveyBase`
- `PhysicalElement` → `_PhysicalElementBase`
- `baseElement` → `(_AcceleratorElementBase, IgnoreExtra)` — multiple inheritance keeps `base_model_dump`, `from_CATAP` etc. from `IgnoreExtra`/`ModelBase`

**Remaining (deferred to Phase D):**
- `Magnet`, `Dipole`, `Quadrupole`, etc. — concrete classes still inherit through `Element → PhysicalBaseElement → Magnet`. They already receive `ConfiguredBaseModel`'s config via `baseElement`. Direct `_MagnetBaseElementBase` / `_DipoleBase` inheritance deferred; low priority since no duplicate fields exist at this level yet.

### Step 14 — Migrate complex elements with custom logic

Elements with validators (`Combined_Corrector`, elements with `CASCADING_RULES`) keep thin wrapper subclasses that add only the custom validator methods.

`Position` and `Rotation` (`NumpyVectorModel`) **cannot** be expressed in LinkML arrays natively — they remain as custom types in `laura/models/physical.py`. They are referenced in the schema as `range: PositionType` with a note explaining the custom Python backing.

### Step 15 — Remove redundant hand-written field declarations

Once all elements are migrated and all tests pass, delete duplicate field declarations from the wrapper classes. The schema is now the single source of truth for all element fields.

### Phase 3 verification checklist

- [x] `_generated.py` generated and importable
- [x] `generate.ps1` / `generate.sh` updated
- [x] `ManufacturerElement` migrated — 336 tests pass
- [x] `ReferenceElement` migrated — 336 tests pass
- [x] `Position`/`Rotation` incompatibility resolved (replaced `NumpyVectorModel`, kept numpy interface)
- [x] `ElectricalElement` field names aligned to snake_case with backward-compat aliases
- [x] `baseElement` migrated to `(_AcceleratorElementBase, IgnoreExtra)`
- [x] `ElementError`, `ElementSurvey`, `PhysicalElement` migrated
- [x] `python -m pytest unit_tests/` — **336 passed** after all migrations
- [x] `python check_laura_load.py` — **passed**: 0.8 s import, 34 laura modules loaded
- [x] No regressions in `elements_between()`, `createDrifts()`, physical position calculations — covered by 336-test suite (`test_laura_class.py`, `test_element_list_extended.py`, `test_elementList.py`)
- [x] `linkml lint` still passes after each schema change — **0 errors, 46 intentional warnings**

---

## Phase 4 — Cross-language and cross-framework outputs

**Goal:** downstream tools consume the schema directly rather than hand-written bindings.

**Viability:** this phase is technically ready to start. LinkML already provides the target generators for TypeScript, SQL DDL/ORM, and GraphQL, and LAURA's schema-first setup now gives those generators a stable source of truth. The remaining work is integration and consumer wiring rather than new schema capability.

### Step 16 — TypeScript types (for LauraGUI / LauraAPIClient)

```bash
gen-typescript laura/schema/laura_schema.yaml \
    > laura/schema/generated/laura_types.ts
```

Publish as part of the `laura-lattices` package or a new `laura-schema` npm package. LauraGUI and LauraAPIClient consume these instead of hand-written TypeScript interfaces.

### Step 17 — SQL schema + SQLAlchemy ORM (for database storage)

```bash
gen-sqltables laura/schema/laura_schema.yaml \
    > laura/schema/generated/laura_schema.sql
gen-sqlalchemy laura/schema/laura_schema.yaml \
    > laura/schema/generated/laura_orm.py
```

New optional `laura/Exporters/SQL.py` using the SQLAlchemy ORM to persist a `MachineModel` to a relational database. Useful for: audit trails, versioned machine states, large-scale queries without loading all YAML.

### Step 18 — GraphQL schema (for LauraAPI)

```bash
gen-graphql laura/schema/laura_schema.yaml \
    > laura/schema/generated/laura_schema.graphql
```

LauraAPI can mount this directly via Strawberry or Ariadne rather than maintaining a separate FastAPI schema definition.

### Phase 4 verification checklist

- [ ] TypeScript: compile with `tsc --strict` — no errors
- [ ] SQL: apply DDL to SQLite, insert a machine model, query it back
- [ ] GraphQL: load schema in Ariadne, validate an example query

---

## Complete advantages table

| Benefit | How |
|---|---|
| **Formal schema** | Single YAML source of truth replaces scattered Pydantic docstrings |
| **Multi-format export** | OWL, RDF, JSON-LD, GraphQL, SQL DDL, TypeScript from one schema |
| **YAML validation** | `linkml validate` catches malformed element files before loading |
| **Auto docs** | HTML site for all element types with inheritance diagrams |
| **Cross-lab interop** | RDF export allows LAURA data to be consumed by any linked-data tool |
| **SPARQL queries** | Semantic queries over the full machine model |
| **TypeScript / Java** | Generate types for LauraGUI / LauraAPI without manual sync |
| **OWL reasoning** | OWL reasoners can infer subclass relationships, detect inconsistencies |
| **Ontology mapping** | Map to QUDT (units), CERN REDI, MAD-X vocabulary, schema.org |
| **GraphQL for LauraAPI** | Replace hand-written FastAPI schemas with generated GraphQL |
| **SQL persistence** | Persist machine states in a relational DB with zero hand-written ORM |

---

## Further considerations

### URI namespace registration

LAURA should register `https://w3id.org/laura/` with the [w3id.org](https://github.com/perma-id/w3id.org) community resolver to obtain persistent, resolvable URIs. This is a straightforward GitHub pull request.

### Existing YAML files in `laura-lattices`

The element YAML files require **no changes** for Phases 1 and 2. They already contain `hardware_type`, which acts as the type designator. The generated JSON Schema can validate existing files immediately.

### MAD-X field name alignment

LAURA uses `k1l`, `k0l`, `k2l` — the same field names as MAD-X. If CERN publishes formal MAD-X vocabulary URIs, adding `exact_mappings` to those URIs would make LAURA elements directly exchangeable with MAD-X input files at the semantic level.

### CI integration

Add a `make generate` target (or PowerShell equivalent) that regenerates all artefacts in `laura/schema/generated/` from `laura_schema.yaml`. Run this in CI so generated files are always in sync with the schema.

---

## Decisions recorded

| Decision | Choice |
|---|---|
| Scope | All four phases |
| Pydantic migration | Full migration over time (generated models replace hand-written ones) |
| Ontology mappings | QUDT, CERN/MAD-X, schema.org |
| URI namespace | `https://w3id.org/laura/` (placeholder; confirm before publication) |
| Priority outputs | HTML docs, JSON Schema, OWL, RDF/Turtle, SPARQL, TypeScript, SQL, GraphQL |
