"""Tests that the LinkML schema covers every element LAURA can actually load.

This is the answer to "how do I check that everything is defined?" — the schema
YAML in ``laura/schema/YAML/`` and the Python classes in ``laura/models/`` are
two hand-maintained halves of the same model, and they drift silently: a new
element class loads and exports fine with no schema class behind it, so nothing
fails until someone turns on ``validate=True`` or reads the generated docs.

These tests only need PyYAML, so they run without the ``[schema]`` extra
installed. They compare names, not field-by-field structure — a schema class
whose slots have gone stale still passes. Regenerating is what catches that:

    python laura/schema/generate_pydantic.py
"""

import pathlib

import pytest
import yaml

from laura.models.element import ELEMENT_REGISTRY

SCHEMA_DIR = pathlib.Path(__file__).resolve().parent.parent / "laura" / "schema" / "YAML"


def _schema_class_names() -> dict[str, str]:
    """Map every class defined across the schema chunk files to its filename."""
    found: dict[str, str] = {}
    for path in sorted(SCHEMA_DIR.glob("*.yaml")):
        doc = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        for class_name, class_def in (doc.get("classes") or {}).items():
            if (class_def or {}).get("class_uri") == "linkml:Any":
                continue
            found[class_name] = path.name
    return found


def _normalise(name: str) -> str:
    """Collapse the two naming conventions onto one key.

    Schema classes are CamelCase (``BeamPositionMonitor``); the Python classes
    and the ``hardware_type`` values they dispatch on are Snake_Case
    (``Beam_Position_Monitor``).
    """
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
    """Every loadable ``hardware_type`` needs a schema class behind it.

    Regressions here mean YAML for that element cannot be schema-validated and
    the generated docs/ontology will not mention it.
    """
    by_norm = {_normalise(c): c for c in _schema_class_names()}
    assert _normalise(hardware_type) in by_norm, (
        f"'{hardware_type}' is in ELEMENT_REGISTRY but has no class in "
        f"{SCHEMA_DIR.name}/. Add it (see laura/schema/YAML/magnets.yaml for "
        f"the pattern), then regenerate with "
        f"`python laura/schema/generate_pydantic.py`."
    )


def test_hardware_type_constraints_match_the_registry():
    """A concrete element's ``equals_string`` must be a real registry key.

    Catches the reverse drift: a schema class pinning a ``hardware_type`` that
    no Python class answers to, so schema-valid YAML fails to load.
    """
    unknown: list[tuple[str, str, str]] = []
    for path in sorted(SCHEMA_DIR.glob("*.yaml")):
        doc = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        for class_name, class_def in (doc.get("classes") or {}).items():
            constraint = (
                ((class_def or {}).get("slot_usage") or {}).get("hardware_type") or {}
            ).get("equals_string")
            if constraint is not None and constraint not in ELEMENT_REGISTRY:
                unknown.append((path.name, class_name, constraint))
    assert not unknown, "schema pins hardware_type values no Python class provides: " + ", ".join(
        f"{f}:{c} -> '{v}'" for f, c, v in unknown
    )


def test_generated_module_covers_the_schema():
    """Every schema class should appear in the committed ``_generated.py``.

    Guards against editing the schema and forgetting to regenerate — the failure
    mode that leaves the two halves out of step for a whole release.
    """
    generated = (
        pathlib.Path(__file__).resolve().parent.parent
        / "laura"
        / "models"
        / "_generated.py"
    ).read_text(encoding="utf-8")
    missing = [
        name
        for name in _schema_class_names()
        # Enums keep their own name; models get the _XxxBase treatment. Either
        # way gen-pydantic drops underscores, so Solenoid_Magnet arrives as
        # _SolenoidMagnetBase.
        if f"class {name}(" not in generated
        and f"class _{name.replace('_', '')}Base(" not in generated
    ]
    assert not missing, (
        "schema classes absent from laura/models/_generated.py: "
        + ", ".join(sorted(missing))
        + ". Regenerate with `python laura/schema/generate_pydantic.py`."
    )
