# LAURA LinkML Schema

This directory contains the canonical [LinkML](https://linkml.io/) schema for all LAURA accelerator element types.

## Files

| File | Description |
|------|-------------|
| `laura_schema.yaml` | Canonical LinkML schema (source of truth) |
| `generate.ps1` | Windows PowerShell generation script |
| `generate.sh` | Linux / macOS bash generation script |
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
| `generated/laura_element.schema.json` | `gen-json-schema` | Runtime YAML validation via `jsonschema` |
| `generated/laura_ontology.owl` | `gen-owl` | OWL ontology for Protégé / reasoners |
| `generated/laura_context.jsonld` | `gen-jsonld-context` | JSON-LD context for linked-data export |
| `generated/laura_shacl.ttl` | `gen-shacl` | SHACL shapes for RDF validation |
| `generated/laura_schema.graphql` | `gen-graphql` | GraphQL schema |
| `docs/source/schema/` | `gen-doc` | Human-readable HTML documentation |
| `docs/source/Architecture/element-er.md` | `gen-erdiagram` | Mermaid ER diagram |

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

- `hardware_type` carries `designates_type: true` — it is the dispatch key
  used by `MODEL_REGISTRY` in Python and the type discriminator in LinkML.
- `name` carries `identifier: true` — it is the unique element key.
- `Position` and `Rotation` are defined as simple classes; the actual Python
  backing uses `NumpyVectorModel` which also accepts list input (`[x, y, z]`).
- QUDT unit annotations (`unit.ucum_code`) are set on all physical quantity
  slots for ontology alignment.
- The Python class `Magnet` maps to `MagnetBaseElement` in the schema to
  avoid name collision with the `MagneticElement` composition model.
