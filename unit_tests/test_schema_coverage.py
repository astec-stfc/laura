"""Checks the hand-maintained LinkML schema against ``laura/models``, by name only."""

import pathlib

import pytest
import yaml

from laura.models.element import ELEMENT_REGISTRY

SCHEMA_DIR = pathlib.Path(__file__).resolve().parent.parent / "laura" / "schema" / "YAML"


def _schema_class_names() -> dict[str, str]:
    """Map schema classes that gen-pydantic materializes to their filename."""
    found: dict[str, str] = {}
    for path in sorted(SCHEMA_DIR.glob("*.yaml")):
        doc = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        for class_name, class_def in (doc.get("classes") or {}).items():
            if (class_def or {}).get("class_uri") == "linkml:Any":
                continue
            found[class_name] = path.name
    return found


def _normalise(name: str) -> str:
    """Schema classes are CamelCase, Python classes Snake_Case; map both to one key."""
    return name.replace("_", "").lower()


def test_schema_dir_is_found():
    assert SCHEMA_DIR.is_dir(), f"schema directory missing: {SCHEMA_DIR}"
    assert list(SCHEMA_DIR.glob("*.yaml")), "no schema YAML files found"


def test_every_schema_file_parses():
    for path in sorted(SCHEMA_DIR.glob("*.yaml")):
        doc = yaml.safe_load(path.read_text(encoding="utf-8"))
        assert isinstance(doc, dict), f"{path.name} did not parse to a mapping"


@pytest.mark.parametrize("hardware_type", sorted(ELEMENT_REGISTRY))
def test_every_element_has_a_schema_class(hardware_type):
    by_norm = {_normalise(c): c for c in _schema_class_names()}
    assert _normalise(hardware_type) in by_norm, (
        f"'{hardware_type}' is in ELEMENT_REGISTRY but has no class in "
        f"{SCHEMA_DIR.name}/. Add it (see laura/schema/YAML/magnets.yaml for "
        f"the pattern), then regenerate with "
        f"`python laura/schema/generate_pydantic.py`."
    )


def _pinned_hardware_types():
    """Yield ``(filename, class_name, class_def, hardware_type)`` per pinning class."""
    for path in sorted(SCHEMA_DIR.glob("*.yaml")):
        doc = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        for class_name, class_def in (doc.get("classes") or {}).items():
            constraint = (
                ((class_def or {}).get("slot_usage") or {}).get("hardware_type") or {}
            ).get("equals_string")
            if constraint is not None:
                yield path.name, class_name, class_def, constraint


def test_hardware_type_constraints_match_the_registry():
    """Catches a schema class pinning a ``hardware_type`` no Python class answers to."""
    unknown = [
        (f, c, v) for f, c, _, v in _pinned_hardware_types() if v not in ELEMENT_REGISTRY
    ]
    assert not unknown, "schema pins hardware_type values no Python class provides: " + ", ".join(
        f"{f}:{c} -> '{v}'" for f, c, v in unknown
    )


def test_schema_mappings_name_the_pals_kind_the_writer_emits():
    """Catches the PALS type rules and the schema's ``pals:`` mappings drifting apart."""
    rules_path = (
        SCHEMA_DIR.parent.parent
        / "translator"
        / "conversion_rules"
        / "types"
        / "type_conversion_rules.yaml"
    )
    kinds = yaml.safe_load(rules_path.read_text(encoding="utf-8"))["pals"]
    missing = []
    for f, c, class_def, hardware_type in _pinned_hardware_types():
        if hardware_type not in kinds:
            continue
        mapped = {
            term
            for key in ("exact", "close", "broad", "narrow", "related")
            for term in class_def.get(f"{key}_mappings") or []
        }
        if f"pals:{kinds[hardware_type]}" not in mapped:
            missing.append(f"{f}:{c} -> pals:{kinds[hardware_type]}")
    assert not missing, "schema classes missing the PALS kind they export as: " + ", ".join(
        missing
    )


def test_generated_module_covers_the_schema():
    """Catches a schema edit without regenerating."""
    generated = (
        pathlib.Path(__file__).resolve().parent.parent
        / "laura"
        / "models"
        / "_generated.py"
    ).read_text(encoding="utf-8")
    missing = [
        name
        for name in _schema_class_names()
        # gen-pydantic drops underscores (Solenoid_Magnet -> _SolenoidMagnetBase); enums
        # keep their name.
        if f"class {name}(" not in generated
        and f"class _{name.replace('_', '')}Base(" not in generated
    ]
    assert not missing, (
        "schema classes absent from laura/models/_generated.py: "
        + ", ".join(sorted(missing))
        + ". Regenerate with `python laura/schema/generate_pydantic.py`."
    )
