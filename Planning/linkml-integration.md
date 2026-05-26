# Plan: Integrate LinkML with LAURA

> Created: 2026-05-26

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

## Phase 1 — Schema definition, documentation, validation

**Goal:** schema file authored and all static artefacts generated; YAML validation working; existing Pydantic models unchanged.

### Step 1 — Bootstrap with `schema-automator`

Run `schema-automator` against a representative sample of element YAML files from `laura-lattices` to get an initial schema. Compare the output against all classes in `laura/models/` (`element.py`, `physical.py`, `magnetic.py`, `diagnostic.py`, `RF.py`, `electrical.py`, `control.py`, `simulation.py`, `laser.py`, `plasma.py`, `lighting.py`, `shutter.py`, `degauss.py`, `manufacturer.py`, `reference.py`). Correct and extend the auto-generated schema to match the full class hierarchy.

```bash
pip install schema-automator
schemauto generalize-from-yaml <path-to-sample-elements/*.yaml> \
    --output laura/schema/laura_schema_bootstrap.yaml
```

### Step 2 — Write `laura/schema/laura_schema.yaml` (canonical)

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

### Step 3 — Define semantic enumerations

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

### Step 4 — Generate JSON Schema and wire into `YAML_Loader.py`

```bash
gen-json-schema laura/schema/laura_schema.yaml \
    --output laura/schema/generated/laura_element.schema.json
```

Add an optional `validate: bool = False` parameter to `read_YAML_Element_File()` and `read_YAML_Combined_File()` in `laura/Importers/YAML_Loader.py`. When `validate=True`, run `jsonschema.validate(raw_dict, schema_json)` before Pydantic parsing — surfacing schema violations explicitly rather than silently dropping unknown fields.

### Step 5 — Generate documentation and diagrams

```bash
gen-doc -d docs/source/schema/ laura/schema/laura_schema.yaml
gen-erdiagram laura/schema/laura_schema.yaml \
    > docs/source/Architecture/element-er.md
gen-plantuml laura/schema/laura_schema.yaml \
    > docs/source/Architecture/element-uml.puml
```

Add a `Schema Reference` section to `docs/source/index.rst` linking to the generated pages.

### Step 6 — Add optional dependencies to `pyproject.toml`

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

### Phase 1 verification checklist

- [ ] `linkml lint laura/schema/laura_schema.yaml` — zero errors
- [ ] `linkml validate --schema laura/schema/laura_schema.yaml <sample-element.yaml>` — passes
- [ ] JSON Schema round-trips a sample element correctly
- [ ] `gen-doc` site builds and shows all ~25 element class pages with inheritance diagrams
- [ ] All existing unit tests still pass: `python -m pytest unit_tests/`

### Phase 1 file summary

| File | Status | Notes |
|---|---|---|
| `laura/schema/laura_schema.yaml` | **new** | Canonical schema — edited by humans |
| `laura/schema/generated/laura_element.schema.json` | generated | Do not edit |
| `laura/schema/generated/element-er.md` | generated | Do not edit |
| `laura/schema/generated/element-uml.puml` | generated | Do not edit |
| `docs/source/schema/` | generated | Do not edit |
| `laura/Importers/YAML_Loader.py` | modified | Add `validate=` parameter |
| `pyproject.toml` | modified | Add `[schema]` and `[rdf]` optional dep groups |
| `docs/source/index.rst` | modified | Link to schema docs |

---

## Phase 2 — RDF/OWL semantic integration

**Goal:** LAURA machine data is exportable as RDF; SPARQL queries work against a loaded machine.

### Step 7 — Generate OWL ontology

```bash
gen-owl laura/schema/laura_schema.yaml \
    --output laura/schema/generated/laura_ontology.owl
```

Hand-extend the generated OWL to add:
- QUDT unit annotations on physical quantity slots
- `qudt:QuantityValue` typing for `length`, `k1l`, field integrals
- Candidate mappings to CERN REDI ontology terms (once confirmed available)

### Step 8 — Generate JSON-LD context

```bash
gen-jsonld-context laura/schema/laura_schema.yaml \
    --output laura/schema/generated/laura_context.jsonld
```

The JSON-LD context makes every element YAML file instantly convertible to RDF by adding `@context`.

### Step 9 — Write `laura/Exporters/RDF.py`

Use `linkml-runtime`'s `RDFLibDumper` to serialise a `MachineModel` instance to RDF.

URI strategy for element instances:
```
https://w3id.org/laura/{accelerator_name}/{machine_area}/{element_name}
# e.g. https://w3id.org/laura/clara/S01/S01-QD01
```

Compute the URI from `machine_area` + `name` fields (no new YAML fields required).

Export modes: Turtle (`.ttl`), JSON-LD (`.jsonld`), N-Triples (`.nt`).

New method on `LAURA`: `export_rdf(path: str, format: str = 'turtle') -> None`.

Model the exporter on the existing `laura/Exporters/YAML.py`.

### Step 10 — Add SPARQL query interface

Add `MachineModel.sparql(query: str) -> list[dict]` (or a new `laura/query.py`):
- Lazily builds an in-memory RDFLib `ConjunctiveGraph` from `self.elements` on first call
- Caches the graph for reuse across queries
- Exposes standard PREFIX declarations for `laura:`, `qudt:`, `schema:`

Example built-in helper queries:
- `get_elements_in_area(area: str) -> list[str]`
- `get_elements_by_property(slot: str, value, operator: str = '=') -> list[str]`

SPARQL is a power-user feature; document it alongside the existing `elements_between()` API.

### Step 11 — Map to existing accelerator ontologies *(stretch goal)*

- Map LAURA element classes to CERN REDI entries (when publicly accessible)
- Map `k1l`, `k0l`, `k2l` MAD-X field names to any formal MAD-X vocabulary URIs
- Map physical units to QUDT: `qudt:Metre`, `qudt:RadianPerMetre`, `qudt:Tesla`
- Map spatial positions to GeoSPARQL `geo:sfWithin` / `geo:Geometry` if needed

### Phase 2 verification checklist

- [ ] Load a small machine, export to Turtle, validate the triples against the OWL ontology
- [ ] Round-trip: export to JSON-LD → reload via `linkml-runtime` loader → matches original
- [ ] SPARQL query returns the same elements as the equivalent `elements_between()` call
- [ ] OWL consistency check passes (no contradictions)

### Phase 2 file summary

| File | Status | Notes |
|---|---|---|
| `laura/schema/generated/laura_ontology.owl` | generated + hand-extended | OWL ontology |
| `laura/schema/generated/laura_context.jsonld` | generated | JSON-LD context |
| `laura/Exporters/RDF.py` | **new** | Turtle / JSON-LD export |
| `laura/models/elementList.py` | modified | Add `sparql()` method (or new `laura/query.py`) |

---

## Phase 3 — Pydantic model migration (incremental, long-term)

**Goal:** gradually replace hand-written Pydantic models with generated ones; the schema becomes the only place model shapes are edited.

### Step 12 — Establish the generated + mixin pattern

```bash
gen-pydantic laura/schema/laura_schema.yaml \
    --pydantic-version 2 \
    --template-dir laura/schema/templates/ \
    --output laura/models/_generated.py
```

Write `laura/schema/templates/class.py.jinja2` to inject:
- `model_config = ConfigDict(extra='ignore')` matching the `IgnoreExtra` pattern
- Any standard imports (`from __future__ import annotations` etc.)

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

### Step 13 — Migrate simple element classes first

Start with elements that have no custom validators (e.g., `Drift`, `Aperture`, simple diagnostic types). For each:
1. Remove the hand-written field declarations from the class
2. Inherit from the corresponding generated base
3. Run `python -m pytest unit_tests/` — must pass before proceeding

### Step 14 — Migrate complex elements with custom logic

Elements with validators (`Combined_Corrector`, elements with `CASCADING_RULES`) keep thin wrapper subclasses that add only the custom validator methods.

`Position` and `Rotation` (`NumpyVectorModel`) **cannot** be expressed in LinkML arrays natively — they remain as custom types in `laura/models/physical.py`. They are referenced in the schema as `range: PositionType` with a note explaining the custom Python backing.

### Step 15 — Remove redundant hand-written field declarations

Once all elements are migrated and all tests pass, delete duplicate field declarations from the wrapper classes. The schema is now the single source of truth for all element fields.

### Phase 3 verification checklist

- [ ] After each batch migration: `python -m pytest unit_tests/` — all pass
- [ ] `python check_laura_load.py` — full machine loads correctly
- [ ] No regressions in `elements_between()`, `createDrifts()`, physical position calculations
- [ ] `linkml lint` still passes after each schema change

---

## Phase 4 — Cross-language and cross-framework outputs

**Goal:** downstream tools consume the schema directly rather than hand-written bindings.

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
