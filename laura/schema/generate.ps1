<#
.SYNOPSIS
    Regenerate all LAURA LinkML artefacts from laura_schema.yaml.

.DESCRIPTION
    Requires: pip install "laura-accelerator[schema]"
    Run from the repository root:  .\laura\schema\generate.ps1
#>

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$SCHEMA   = "laura/schema/YAML/laura_schema.yaml"
$OUT_DIR  = "laura/schema/generated"
$DOCS_DIR = "docs/source/schema"
# NOTE: The hand-maintained element-er.md (docs/source/Architecture/element-er.md)
# contains a comprehensive classDiagram that gen-erdiagram cannot produce for
# multi-file schemas.  Auto-generated output is written to $OUT_DIR instead so
# the documented diagram is never overwritten.
$ER_FILE_AUTO = "$OUT_DIR/element-er-auto.md"

# ── Ensure output directories exist ──────────────────────────────────────────
New-Item -ItemType Directory -Force -Path $OUT_DIR  | Out-Null
New-Item -ItemType Directory -Force -Path $DOCS_DIR | Out-Null

# ── UTF-8 output ─────────────────────────────────────────────────────────────
# Every artefact below is written through Write-Utf8 rather than Set-Content.
$Utf8NoBom = New-Object System.Text.UTF8Encoding $false
function Write-Utf8 {
    param(
        [Parameter(Mandatory, Position = 0)][string] $Path,
        [Parameter(ValueFromPipeline)][string[]] $InputObject
    )
    begin { $lines = New-Object System.Collections.Generic.List[string] }
    process { if ($null -ne $InputObject) { $lines.AddRange($InputObject) } }
    end {
        $full = [System.IO.Path]::GetFullPath((Join-Path (Get-Location).Path $Path))
        [System.IO.File]::WriteAllLines($full, $lines, $Utf8NoBom)
    }
}

Write-Host "Linting schema..." -ForegroundColor Cyan
# Advisory only. The schema carries ~50 standard_naming warnings for physics
# conventions we intend to keep (slots named L, Kp, Ki, Kd, x, y, z, s; enum
# values like RF and TwissMatch), and linkml-lint exits non-zero on warnings --
# which, under $ErrorActionPreference = "Stop", aborted this script before it
# generated anything.
try {
    linkml-lint $SCHEMA
} catch {
    Write-Host "  (lint warnings above are advisory; continuing)" -ForegroundColor DarkGray
}
if ($LASTEXITCODE -ne 0) {
    Write-Host "  (lint warnings above are advisory; continuing)" -ForegroundColor DarkGray
    $global:LASTEXITCODE = 0
}

Write-Host "Generating JSON Schema..." -ForegroundColor Cyan
gen-json-schema $SCHEMA --indent 2 | Write-Utf8 "$OUT_DIR/laura_element.schema.json"

Write-Host "Generating OWL ontology..." -ForegroundColor Cyan
gen-owl $SCHEMA `
    --skip-vacuous-min-zero-cardinality-axioms `
    --skip-vacuous-local-range-axioms `
    --consolidate-cardinality-axioms `
  | Write-Utf8 "$OUT_DIR/laura_ontology.owl"

Write-Host "Generating JSON-LD context..." -ForegroundColor Cyan
gen-jsonld-context $SCHEMA | Write-Utf8 "$OUT_DIR/laura_context.jsonld"

Write-Host "Generating SHACL shapes..." -ForegroundColor Cyan
# Must go through generate_shacl.py, not raw gen-shacl: it does the gen-yaml
# merge gen-shacl needs to cope with a multi-file schema, then collapses the
# duplicate sh:property blocks gen-shacl emits -- which leave six classes
# unsatisfiable, because an overridden slot_usage keeps the inherited
# constraint alongside the overriding one.
python "laura/schema/generate_shacl.py"

Write-Host "Generating TypeScript types..." -ForegroundColor Cyan
gen-typescript $SCHEMA | Write-Utf8 "$OUT_DIR/laura_types.ts"

Write-Host "Generating SQL DDL..." -ForegroundColor Cyan
# Must go through generate_sql.py, not raw gen-sqltables: it narrows the
# all-columns primary key gen-sqltables emits for a class with a key slot
# (ControlVariable) down to the key the same run emits as UNIQUE.
python "laura/schema/generate_sql.py"

Write-Host "Generating SQLAlchemy ORM..." -ForegroundColor Cyan
python "laura/schema/generate_orm.py"

Write-Host "Generating GraphQL schema..." -ForegroundColor Cyan
gen-graphql $SCHEMA | Write-Utf8 "$OUT_DIR/laura_schema.graphql"
# gen-graphql emits empty type bodies for abstract classes, which is invalid
# GraphQL SDL (object types must have at least one field).  Patch them in-place.
Write-Host "  Patching empty GraphQL types..." -ForegroundColor DarkGray
$gql = Get-Content "$OUT_DIR/laura_schema.graphql" -Raw
# The replacement must be double-quoted for `n to be a newline: in a
# single-quoted string PowerShell writes the two characters back-tick + n
# literally, which produced `_placeholder: Boolean`n  }` -- invalid GraphQL SDL.
# $1 is escaped so PowerShell leaves the regex group reference alone.
$gql = [regex]::Replace($gql, '(?m)(type \w+\r?\n  \{\r?\n)  \}', "`$1    _placeholder: Boolean`n  }")
$gql | Write-Utf8 "$OUT_DIR/laura_schema.graphql"

Write-Host "Generating reference documentation..." -ForegroundColor Cyan
# gen-doc writes but never prunes, so a renamed class or slot would leave its old
# page behind for the Sphinx build to pick up. Clear the directory first.
Get-ChildItem $DOCS_DIR -Filter *.md | Remove-Item -Force
gen-doc -d $DOCS_DIR $SCHEMA | Out-Null   # gen-doc prints a stray "None"
# Strip the MkDocs front matter gen-doc emits; see postprocess_docs.py.
python "laura/schema/postprocess_docs.py" $DOCS_DIR

Write-Host "Generating ER diagram (auto, written to generated/)..." -ForegroundColor Cyan
# Written to generated/ — does NOT overwrite the hand-maintained
# docs/source/Architecture/element-er.md (which has the full classDiagram).
gen-erdiagram $SCHEMA | Write-Utf8 $ER_FILE_AUTO

Write-Host "Generating Pydantic base classes (_generated.py)..." -ForegroundColor Cyan
python "laura/schema/generate_pydantic.py"

Write-Host ""
Write-Host "All artefacts generated successfully." -ForegroundColor Green
Write-Host "NOTE: gen-owl, gen-shacl and gen-sqltables emit their statements in a" -ForegroundColor DarkGray
Write-Host "      non-deterministic order, so those three files show large diffs even" -ForegroundColor DarkGray
Write-Host "      when the schema has not changed. Check the diff is only reordering" -ForegroundColor DarkGray
Write-Host "      before committing them." -ForegroundColor DarkGray
Write-Host "  JSON Schema : $OUT_DIR/laura_element.schema.json"
Write-Host "  OWL         : $OUT_DIR/laura_ontology.owl"
Write-Host "  JSON-LD ctx : $OUT_DIR/laura_context.jsonld"
Write-Host "  SHACL       : $OUT_DIR/laura_shacl.ttl"
Write-Host "  TypeScript  : $OUT_DIR/laura_types.ts"
Write-Host "  SQL DDL     : $OUT_DIR/laura_schema.sql"
Write-Host "  SQLAlchemy  : $OUT_DIR/laura_orm.py"
Write-Host "  GraphQL     : $OUT_DIR/laura_schema.graphql"
Write-Host "  Reference   : $DOCS_DIR/"
Write-Host "  ER diagram  : $ER_FILE_AUTO (auto-generated skeleton)
  Full diagram: docs/source/Architecture/element-er.md (hand-maintained)"
Write-Host "  Pydantic    : laura/models/_generated.py"
