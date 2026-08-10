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


def test_property_backed_slots_are_excluded_from_every_generated_base():
    """No generated base may declare a slot a wrapper implements as a property.

    ``gen-pydantic`` re-declares every inherited slot in each subclass, so
    excluding a slot only on the class that introduces it leaves it behind on
    all the descendants. When such a base is then mixed into its wrapper, the
    field reappears — ``Sextupole_Magnet`` picked up a meaningless ``angle``
    this way, and a property on the wrapper would instead have become the
    field's default and failed validation.

    ``_PYDANTIC_EXCLUDED_SLOTS`` in ``generate_pydantic.py`` is inherited
    through the generated class tree so one entry covers a whole branch; this
    checks the committed output actually reflects that.
    """
    from laura.models import _generated

    offenders = [
        f"{name}.{slot}"
        for name in dir(_generated)
        if name.endswith("Base")
        for cls in [getattr(_generated, name)]
        if hasattr(cls, "model_fields")
        for slot in ("angle",)
        if slot in cls.model_fields
    ]
    assert not offenders, (
        "generated bases declare property-backed slots: "
        + ", ".join(sorted(offenders))
        + ". Add the slot to _PYDANTIC_EXCLUDED_SLOTS on the class that "
        "introduces it and regenerate."
    )


def test_json_schema_any_of_slots_accept_every_branch():
    """An ``any_of`` slot must not also carry a sibling ``type``.

    ``gen-json-schema`` emits the slot's own range alongside the union, and
    JSON Schema conjoins siblings — so every branch except that one is dead and
    ``read_YAML_Element_File(..., validate=True)`` rejects values the Python
    model accepts (a numeric ``entrance_edge_angle``, a symbolic ``phase``, a
    two-element ``beampipe_size``). ``postprocess_json_schema.py`` strips the
    sibling; this checks it ran.
    """
    import json

    schema_path = (
        pathlib.Path(__file__).resolve().parent.parent
        / "laura"
        / "schema"
        / "generated"
        / "laura_element.schema.json"
    )
    if not schema_path.is_file():
        pytest.skip("JSON Schema artefact not generated")
    schema = json.loads(schema_path.read_text(encoding="utf-8"))

    offenders = [
        f"{class_name}.{slot}"
        for class_name, class_def in (schema.get("$defs") or {}).items()
        for slot, slot_def in ((class_def or {}).get("properties") or {}).items()
        if isinstance(slot_def, dict) and "anyOf" in slot_def and "type" in slot_def
    ]
    assert not offenders, (
        "any_of slots narrowed by a sibling 'type': "
        + ", ".join(sorted(offenders))
        + ". Run `python laura/schema/postprocess_json_schema.py`."
    )


def test_every_diagnostic_payload_survives_a_dump_and_revalidate():
    """A diagnostic's instrument-specific fields must round-trip.

    ``Diagnostic`` annotates its ``diagnostic`` slot as the schema base, which
    has no fields, and pydantic serialises *and* validates by the declared type.
    Left inherited, every subclass dumped ``{}`` -- and since
    ``translate_elements`` round-trips elements through ``model_dump()``, no
    diagnostic data reached any translator, nor survived YAML export.

    Each concrete class therefore re-declares the field with its own payload
    type, the way ``magnetic``/``cavity``/``controls`` already are. This checks
    the whole family at once so a new diagnostic cannot quietly skip it.
    """
    losses: list[str] = []
    for hardware_type, cls in sorted(ELEMENT_REGISTRY.items()):
        if "diagnostic" not in cls.model_fields:
            continue
        try:
            element = cls(name="X", machine_area="T")
        except Exception:  # needs constructor arguments; covered elsewhere
            continue
        payload = element.diagnostic
        if payload is None or not type(payload).model_fields:
            continue
        expected = len(type(payload).model_fields)
        dumped = element.model_dump(by_alias=False).get("diagnostic") or {}
        revalidated = cls.model_validate(element.model_dump(by_alias=False)).diagnostic
        survived = len(type(revalidated).model_fields) if revalidated is not None else 0
        if len(dumped) != expected or survived != expected:
            losses.append(
                f"{hardware_type} ({type(payload).__name__}): "
                f"{expected} fields -> {len(dumped)} dumped, {survived} revalidated"
            )
    assert not losses, "diagnostic payloads lost on round-trip:\n  " + "\n  ".join(losses)


def test_every_code_has_an_unsupported_list_and_checks_it():
    """A code with no list, or a list nothing consults, reports nothing.

    ``to_bdsim`` had a populated ``bdsim_unsupported`` it never checked, and
    MAD-X/RF-Track had no list at all -- so an element a code cannot represent
    was either silently degraded or died with a bare ``KeyError``.
    """
    import ast

    from laura.translator.converters.section import unsupported_elements

    source = (
        pathlib.Path(__file__).resolve().parent.parent
        / "laura"
        / "translator"
        / "converters"
        / "section.py"
    ).read_text(encoding="utf-8")
    unchecked = []
    for node in ast.walk(ast.parse(source)):
        if not (isinstance(node, ast.ClassDef) and node.name == "SectionLatticeTranslator"):
            continue
        for method in node.body:
            if not (isinstance(method, ast.FunctionDef) and method.name.startswith("to_")):
                continue
            checked = any(
                isinstance(call, ast.Call)
                and getattr(call.func, "attr", "") == "_check_elements_supported"
                for call in ast.walk(method)
            )
            if not checked:
                unchecked.append(method.name)
    assert not unchecked, f"to_<code> methods that never report unsupported elements: {unchecked}"
    assert set(unsupported_elements) >= {"madx", "rftrack", "bdsim"}

    # The madx/rftrack lists were derived from the live conversion tables, so
    # every name in them must be a real hardware_type -- a typo would silently
    # stop the warning firing. The older lists carry aspirational names
    # (ActivePlasmaLens, RCollimator, and ocelot's APContour/Center/Cleaner/
    # Scatter) that no class declares yet; those are shared with the type tables
    # of other codes and are left alone deliberately.
    for code in ("madx", "rftrack"):
        unknown = sorted(set(unsupported_elements[code]) - set(ELEMENT_REGISTRY))
        assert not unknown, f"{code}_unsupported names types no class declares: {unknown}"


def test_every_constructible_element_can_be_translated():
    """An element built in code must reach the translators.

    ``translate_elements`` revalidates each element against its translator, and
    several translators require a non-``None`` payload (``RFCavityTranslator``
    needs ``simulation``). A model whose ``model_post_init`` does not install
    that default therefore constructs fine and then fails to translate to *any*
    code -- which is what happened to ``RFCavity`` while its RFDeflectingCavity
    and CrabCavity siblings installed theirs.
    """
    from laura.models.physical import PhysicalElement
    from laura.translator.converters.converter import translate_elements

    failures = []
    for hardware_type, cls in sorted(ELEMENT_REGISTRY.items()):
        try:
            element = cls(
                name="X1", machine_area="S", physical=PhysicalElement(length=0.1)
            )
        except Exception:
            continue  # needs explicit constructor arguments; not this test's concern
        try:
            translate_elements([element])
        except Exception as exc:  # noqa: BLE001 - report them all at once
            failures.append(f"{hardware_type}: {type(exc).__name__}: {str(exc)[:80]}")
    assert not failures, "elements that construct but cannot translate:\n  " + "\n  ".join(
        failures
    )


def test_every_element_constructs_with_only_a_name_and_area():
    """A registered element must be buildable from its identity alone.

    Everything else has a default, so needing an extra argument is an oversight
    rather than a design choice -- ``Drift``/``PowerSupply`` were missing the
    frozen ``hardware_class`` every other element pins, ``CrabCavity``'s parent
    installed an ``RFCavityElement`` into a slot typed for the (sibling, not
    subclass) ``RFDeflectingCavityElement``, and ``Low_Level_RF_Element`` had a
    required ``one_record``.
    """
    failures = []
    for hardware_type, cls in sorted(ELEMENT_REGISTRY.items()):
        try:
            cls(name="X1", machine_area="S")
        except Exception as exc:  # noqa: BLE001 - report them all at once
            failures.append(f"{hardware_type}: {type(exc).__name__}: {str(exc)[:90]}")
    assert not failures, "elements that cannot be constructed bare:\n  " + "\n  ".join(
        failures
    )


def test_crab_cavity_keeps_its_deflecting_payload():
    """Its cavity slot is typed for the deflecting model, not the accelerating one."""
    from laura.models.element import CrabCavity
    from laura.models.RF import RFDeflectingCavityElement

    assert isinstance(CrabCavity(name="CC1", machine_area="L").cavity, RFDeflectingCavityElement)
