<#
.SYNOPSIS
    Regenerate all LAURA LinkML artefacts from laura_schema.yaml.

.DESCRIPTION
    Requires: pip install "laura-accelerator[schema]"
    Run from the repository root:  .\laura\schema\generate.ps1
#>

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$SCHEMA   = "laura/schema/laura_schema.yaml"
$OUT_DIR  = "laura/schema/generated"
$DOCS_DIR = "docs/source/schema"
$ER_FILE  = "docs/source/Architecture/element-er.md"

# ── Ensure output directories exist ──────────────────────────────────────────
New-Item -ItemType Directory -Force -Path $OUT_DIR  | Out-Null
New-Item -ItemType Directory -Force -Path $DOCS_DIR | Out-Null
New-Item -ItemType Directory -Force -Path (Split-Path $ER_FILE) | Out-Null

Write-Host "Linting schema..." -ForegroundColor Cyan
linkml-lint $SCHEMA

Write-Host "Generating JSON Schema..." -ForegroundColor Cyan
gen-json-schema $SCHEMA --indent 2 | Set-Content "$OUT_DIR/laura_element.schema.json" -Encoding ascii

Write-Host "Generating OWL ontology..." -ForegroundColor Cyan
gen-owl $SCHEMA `
    --skip-vacuous-min-zero-cardinality-axioms `
    --skip-vacuous-local-range-axioms `
    --consolidate-cardinality-axioms `
  | Set-Content "$OUT_DIR/laura_ontology.owl"

Write-Host "Generating JSON-LD context..." -ForegroundColor Cyan
gen-jsonld-context $SCHEMA | Set-Content "$OUT_DIR/laura_context.jsonld"

Write-Host "Generating SHACL shapes..." -ForegroundColor Cyan
gen-shacl $SCHEMA | Set-Content "$OUT_DIR/laura_shacl.ttl"

Write-Host "Generating GraphQL schema..." -ForegroundColor Cyan
gen-graphql $SCHEMA | Set-Content "$OUT_DIR/laura_schema.graphql"

Write-Host "Generating HTML documentation..." -ForegroundColor Cyan
gen-doc -d $DOCS_DIR $SCHEMA

Write-Host "Generating ER diagram..." -ForegroundColor Cyan
gen-erdiagram $SCHEMA | Set-Content $ER_FILE

Write-Host "Generating Pydantic base classes (_generated.py)..." -ForegroundColor Cyan
python "laura/schema/generate_pydantic.py"

Write-Host ""
Write-Host "All artefacts generated successfully." -ForegroundColor Green
Write-Host "  JSON Schema : $OUT_DIR/laura_element.schema.json"
Write-Host "  OWL         : $OUT_DIR/laura_ontology.owl"
Write-Host "  JSON-LD ctx : $OUT_DIR/laura_context.jsonld"
Write-Host "  SHACL       : $OUT_DIR/laura_shacl.ttl"
Write-Host "  GraphQL     : $OUT_DIR/laura_schema.graphql"
Write-Host "  HTML docs   : $DOCS_DIR/"
Write-Host "  ER diagram  : $ER_FILE"
Write-Host "  Pydantic    : laura/models/_generated.py"
