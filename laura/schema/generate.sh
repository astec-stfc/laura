#!/usr/bin/env bash
# Regenerate all LAURA LinkML artefacts from laura_schema.yaml.
#
# Requirements: pip install "laura-accelerator[schema]"
# Run from the repository root:  bash laura/schema/generate.sh

set -euo pipefail

# Every generator below writes through a plain `>` redirect, so its stdout
# encoding decides what lands in generated/.
export PYTHONUTF8=1

SCHEMA="laura/schema/YAML/laura_schema.yaml"
OUT_DIR="laura/schema/generated"
DOCS_DIR="docs/source/schema"
# NOTE: The hand-maintained element-er.md (docs/source/Architecture/element-er.md)
# contains a comprehensive classDiagram that gen-erdiagram cannot produce for
# multi-file schemas.  Auto-generated output is written to $OUT_DIR instead so
# the documented diagram is never overwritten.
ER_FILE_AUTO="$OUT_DIR/element-er-auto.md"

# ── Ensure output directories exist ──────────────────────────────────────────
mkdir -p "$OUT_DIR" "$DOCS_DIR"

echo "Linting schema..."
# Advisory only. The schema carries ~50 standard_naming warnings for physics
# conventions we intend to keep (slots named L, Kp, Ki, Kd, x, y, z, s; enum
# values like RF and TwissMatch), and linkml-lint exits non-zero on warnings --
# which, under `set -e`, aborted this script before it generated anything.
linkml-lint "$SCHEMA" || echo "  (lint warnings above are advisory; continuing)"

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
# NOTE: gen-shacl (linkml 1.11.x) fails on multi-file schemas with a KeyError.
# Workaround: merge with gen-yaml first, then run gen-shacl on the merged output.
(
  cd "laura/schema/YAML"
  gen-yaml --mergeimports laura_schema.yaml \
    | grep -v "UserWarning\|warnings.warn\|RequestsDependency" \
    > _merged_temp.yaml
  gen-shacl _merged_temp.yaml > ../generated/laura_shacl.ttl
  rm -f _merged_temp.yaml
)

echo "Generating TypeScript types..."
gen-typescript "$SCHEMA" > "$OUT_DIR/laura_types.ts"

echo "Generating SQL DDL..."
gen-sqltables "$SCHEMA" > "$OUT_DIR/laura_schema.sql"

echo "Generating SQLAlchemy ORM..."
# Must go through generate_orm.py, not raw gen-sqla: it runs gen-sqla and then
# adds the primaryjoin/secondaryjoin that self-referential many-to-many slots
# (AcceleratorElement.upstream/downstream) need. Without that post-processing
# SQLAlchemy 2.0 raises AmbiguousForeignKeysError and every SQL export fails.
# generate.ps1 already did this correctly; this script called gen-sqla directly
# and silently clobbered the fix.
python "laura/schema/generate_orm.py"

echo "Generating GraphQL schema..."
gen-graphql "$SCHEMA" > "$OUT_DIR/laura_schema.graphql"
# gen-graphql emits empty type bodies for abstract classes, which is invalid
# GraphQL SDL (object types must have at least one field).  Patch them in-place.
echo "  Patching empty GraphQL types..."
python - <<'EOF'
import re, pathlib
path = pathlib.Path("laura/schema/generated/laura_schema.graphql")
content = path.read_text()
patched = re.sub(r'(type \w+\n  \{\n)  \}', r'\1    _placeholder: Boolean\n  }', content)
path.write_text(patched)
print(f"  Patched {content.count(chr(10)+'  {'+chr(10)+'  }')} empty types")
EOF

echo "Generating reference documentation..."
# gen-doc writes but never prunes, so a renamed class or slot would leave its old
# page behind for the Sphinx build to pick up. Clear the directory first.
rm -f "$DOCS_DIR"/*.md
gen-doc -d "$DOCS_DIR" "$SCHEMA"
# Strip the MkDocs front matter gen-doc emits; see postprocess_docs.py.
python "laura/schema/postprocess_docs.py" "$DOCS_DIR"

echo "Generating ER diagram (auto, written to generated/)..."
# Written to generated/ — does NOT overwrite the hand-maintained
# docs/source/Architecture/element-er.md (which has the full classDiagram).
gen-erdiagram "$SCHEMA" > "$ER_FILE_AUTO"

echo "Generating Pydantic base classes (_generated.py)..."
python "laura/schema/generate_pydantic.py"

echo ""
echo "All artefacts generated successfully."
echo "NOTE: gen-owl, gen-shacl and gen-sqltables emit their statements in a"
echo "      non-deterministic order, so those three files show large diffs even"
echo "      when the schema has not changed. Check the diff is only reordering"
echo "      before committing them."
echo "  JSON Schema : $OUT_DIR/laura_element.schema.json"
echo "  OWL         : $OUT_DIR/laura_ontology.owl"
echo "  JSON-LD ctx : $OUT_DIR/laura_context.jsonld"
echo "  SHACL       : $OUT_DIR/laura_shacl.ttl"
echo "  TypeScript  : $OUT_DIR/laura_types.ts"
echo "  SQL DDL     : $OUT_DIR/laura_schema.sql"
echo "  SQLAlchemy  : $OUT_DIR/laura_orm.py"
echo "  GraphQL     : $OUT_DIR/laura_schema.graphql"
echo "  Reference   : $DOCS_DIR/"
echo "  ER diagram  : $ER_FILE_AUTO (auto-generated skeleton)"
echo "  Full diagram: docs/source/Architecture/element-er.md (hand-maintained)"
echo "  Pydantic    : laura/models/_generated.py"
