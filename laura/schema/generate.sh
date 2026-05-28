#!/usr/bin/env bash
# Regenerate all LAURA LinkML artefacts from laura_schema.yaml.
#
# Requirements: pip install "laura-accelerator[schema]"
# Run from the repository root:  bash laura/schema/generate.sh

set -euo pipefail

SCHEMA="laura/schema/YAML/laura_schema.yaml"
OUT_DIR="laura/schema/generated"
DOCS_DIR="docs/source/schema"
ER_FILE="docs/source/Architecture/element-er.md"

# ── Ensure output directories exist ──────────────────────────────────────────
mkdir -p "$OUT_DIR" "$DOCS_DIR" "$(dirname "$ER_FILE")"

echo "Linting schema..."
linkml-lint "$SCHEMA"

echo "Generating JSON Schema..."
gen-json-schema "$SCHEMA" --indent 2 > "$OUT_DIR/laura_element.schema.json"

echo "Generating OWL ontology..."
gen-owl "$SCHEMA" \
    --skip-vacuous-min-zero-cardinality-axioms \
    --skip-vacuous-local-range-axioms \
    --consolidate-cardinality-axioms \
  > "$OUT_DIR/laura_ontology.owl"

echo "Generating JSON-LD context..."
gen-jsonld-context "$SCHEMA" > "$OUT_DIR/laura_context.jsonld"

echo "Generating SHACL shapes..."
gen-shacl "$SCHEMA" > "$OUT_DIR/laura_shacl.ttl"

echo "Generating GraphQL schema..."
gen-graphql "$SCHEMA" > "$OUT_DIR/laura_schema.graphql"

echo "Generating HTML documentation..."
gen-doc -d "$DOCS_DIR" "$SCHEMA"

echo "Generating ER diagram..."
gen-erdiagram "$SCHEMA" > "$ER_FILE"

echo "Generating Pydantic base classes (_generated.py)..."
python "laura/schema/generate_pydantic.py"

echo ""
echo "All artefacts generated successfully."
echo "  JSON Schema : $OUT_DIR/laura_element.schema.json"
echo "  OWL         : $OUT_DIR/laura_ontology.owl"
echo "  JSON-LD ctx : $OUT_DIR/laura_context.jsonld"
echo "  SHACL       : $OUT_DIR/laura_shacl.ttl"
echo "  GraphQL     : $OUT_DIR/laura_schema.graphql"
echo "  HTML docs   : $DOCS_DIR/"
echo "  ER diagram  : $ER_FILE"
echo "  Pydantic    : laura/models/_generated.py"
