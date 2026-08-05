# LAURA LinkML Schema

This directory contains the canonical [LinkML](https://linkml.io/) schema for all LAURA accelerator element types.

For the narrative description — what the ontology contains, the conventions its
slots follow, and how it reaches the Python classes — see
[The LAURA Schema](https://laura.readthedocs.io/en/latest/Schema.html) in the
documentation (`docs/source/Schema.rst`).

## Files

| File | Description |
|------|-------------|
| `YAML/laura_schema.yaml` | Root schema (source of truth). Always generate from this file. |
| `YAML/*.yaml` | The ten chunk files it imports — `geometry`, `controls`, `elements`, `machine`, `simulation`, `magnetic`, `magnets`, `rf`, `diagnostics`, `laser_plasma`. Not standalone models: each refers to classes defined in its siblings. |
| `generate.ps1` | Windows PowerShell generation script |
| `generate.sh` | Linux / macOS bash generation script |
| `generate_pydantic.py` | Wraps `gen-pydantic` with the post-processing the generated bases need |
| `generate_orm.py` | Wraps `gen-sqla` and adds the joins the self-referential `upstream`/`downstream` slots need |
| `postprocess_docs.py` | Strips the MkDocs front matter `gen-doc` emits, so Sphinx can render the pages |
| `generated/` | Auto-generated artefacts — **do not edit by hand** |

## Quick start

Install the tooling:

```bash
pip install "laura-accelerator[schema]"
```

Generate all artefacts:

```bash
# Windows
.\laura\schema\generate.ps1

# Linux / macOS
bash laura/schema/generate.sh
```

## Generated artefacts

| File | Generator | Purpose |
|------|-----------|---------|
| `laura/models/_generated.py` | `generate_pydantic.py` | Pydantic base classes wrapped by the hand-written models in `laura/models/` |
| `generated/laura_element.schema.json` | `gen-json-schema` | Runtime YAML validation via `jsonschema` |
| `generated/laura_ontology.owl` | `gen-owl` | OWL ontology for Protégé / reasoners |
| `generated/laura_context.jsonld` | `gen-jsonld-context` | JSON-LD context for linked-data export |
| `generated/laura_shacl.ttl` | `gen-shacl` | SHACL shapes for RDF validation |
| `generated/laura_orm.py` | `generate_orm.py` | SQLAlchemy ORM used by `laura.Exporters.SQL` |
| `generated/laura_schema.sql` | `gen-sqltables` | Plain SQL DDL |
| `generated/laura_schema.graphql` | `gen-graphql` | GraphQL schema |
| `generated/laura_types.ts` | `gen-typescript` | TypeScript types |
| `docs/source/schema/` | `gen-doc` | Per-class and per-slot reference documentation, published as part of the Sphinx site |
| `generated/element-er-auto.md` | `gen-erdiagram` | Auto-generated ER skeleton (incomplete for multi-file schemas) |
| `docs/source/Architecture/element-er.md` | *hand-maintained* | Full Mermaid `classDiagram` of the element hierarchy |

`gen-doc` writes but never prunes, so the generation scripts clear
`docs/source/schema/*.md` before running it — a renamed class would otherwise
leave its old page behind for the Sphinx build to pick up. Do not put anything
hand-written in that directory.

## Using validation in Python

Pass `validate=True` to any YAML loading function to check the raw YAML
against the JSON Schema before Pydantic parsing:

```python
from laura.Importers.YAML_Loader import read_YAML_Element_File

element = read_YAML_Element_File("path/to/element.yaml", validate=True)
```

The JSON Schema file (`generated/laura_element.schema.json`) must exist
first — run the generation script to create it.

## Schema design notes

- `hardware_type` is the dispatch key: `ELEMENT_REGISTRY` in Python maps its
  value to a class. Each concrete class pins it with a
  `slot_usage: hardware_type: equals_string:` constraint, so an unknown or
  misspelled value is caught by schema validation as well as at runtime.
- `identifier: true` marks a unique key. It is carried by
  `AcceleratorElement.name`, `SectionLattice.name` and `MachineLayout.name`.
- `Position` and `Rotation` are defined as simple classes; the hand-written
  Python subclasses add list/array coercion (`[x, y, z]` input), iteration,
  `.array`, `from_list()` and arithmetic.
- QUDT unit annotations (`unit.ucum_code`) are set on all physical quantity
  slots for ontology alignment.
- The Python class `Magnet` maps to the schema class `Magnet`. The concrete
  magnet types (`Dipole`, `Quadrupole`, …) live in `YAML/magnets.yaml` alongside
  their `*_Magnet` field models; the Python wrappers use the underscored
  spellings `Horizontal_Corrector`, `Vertical_Corrector`, `Combined_Corrector`
  and `Photon_Monitor` for the corresponding schema classes.
- Two subsets are load-bearing rather than descriptive: `functional_parameters`
  marks slots whose value may be a symbolic name instead of a number, and
  `bend_angle_reference` marks those that may additionally reference the dipole
  bend angle. Subsets are used rather than LinkML `annotations` because
  `gen-yaml` — which the SHACL step pipes through — cannot serialise
  `Annotation` objects.
