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


GENERATED_DIR = (
    pathlib.Path(__file__).resolve().parent.parent / "laura" / "schema" / "generated"
)


@pytest.mark.parametrize(
    "path", sorted(p for p in GENERATED_DIR.iterdir() if p.is_file()), ids=lambda p: p.name
)
def test_generated_artefact_is_utf8(path):
    """Every committed artefact must decode as UTF-8."""
    try:
        path.read_bytes().decode("utf-8")
    except UnicodeDecodeError as exc:
        pytest.fail(
            f"{path.name} is not valid UTF-8 at byte {exc.start}: {exc.reason}. "
            "Regenerate it with laura/schema/generate.sh (or generate.ps1)."
        )


def test_control_variable_name_is_not_a_pydantic_field():
    """``ControlVariable.name`` must stay out of the generated model.

    The slot exists so the formats without a native map type have somewhere to
    put the logical name, and because LinkML cannot inline a collection as a
    dict without a key. But a key slot is required, and lattice YAML gives the
    name as the mapping key rather than inside the entry, so materialising it
    would make every existing controls block fail validation.
    """
    from laura.models.control import ControlsInformation

    assert "name" not in ControlsInformation.model_fields["variables"].annotation.__args__[1].model_fields

    # The shape lattice YAML actually uses still loads.
    info = ControlsInformation(
        variables={"SETI": {"identifier": "MAG-01:SETI", "protocol": "EPICS"}}
    )
    assert list(info.variables) == ["SETI"]
    assert info.variables["SETI"].identifier == "MAG-01:SETI"


def test_control_variable_extras_still_ride_along():
    """Declaring ``auto_buffer``/``buffer_size`` must not close the class.

    They are modelled because they are widespread enough to be worth exporting,
    but ControlVariable keeps ``extra="allow"`` so a protocol LAURA has never
    seen still round-trips. Declared slots that are absent stay absent from the
    dump, so nothing gains a spurious default.
    """
    from laura.models.control import ControlVariable

    cv = ControlVariable(
        identifier="MAG-01:SETI",
        protocol="EPICS",
        auto_buffer=True,
        some_future_protocol_field="kept",
    )
    dumped = cv.serialize()
    assert dumped["auto_buffer"] is True
    assert dumped["some_future_protocol_field"] == "kept"
    assert "buffer_size" not in dumped


@pytest.mark.parametrize("artefact", ["laura_orm.py", "laura_schema.sql"])
def test_control_variable_primary_key_is_narrow(artefact):
    """gen-sqla and gen-sqltables put every column in ControlVariable's key.

    A primary-key column cannot be NULL and almost every ControlVariable column
    is optional, so the table would be unwritable. generate_orm.py and
    generate_sql.py narrow it to (ControlsInformation_id, name); this is the
    check that they still run.
    """
    text = (GENERATED_DIR / artefact).read_text(encoding="utf-8")
    if artefact.endswith(".sql"):
        block = text.split('CREATE TABLE "ControlVariable" (')[1].split("\n);")[0]
        pk = [line for line in block.splitlines() if line.strip().startswith("PRIMARY KEY")]
        assert pk, "no PRIMARY KEY found for ControlVariable"
        cols = pk[0].split("(", 1)[1].rsplit(")", 1)[0].split(",")
        assert len(cols) <= 2, f"primary key is too wide: {pk[0].strip()}"
    else:
        block = text.split("class ControlVariable(Base):")[1].split("\nclass ")[0]
        pk_cols = [ln for ln in block.splitlines() if "primary_key=True" in ln]
        assert 0 < len(pk_cols) <= 2, (
            f"ControlVariable has {len(pk_cols)} primary-key columns; "
            "generate_orm.py should have narrowed it to two"
        )


# These three Python classes do not inherit from their generated base at all --
# _MatrixTransformBase, _PhotonMonitorBase and _PowerSupplyBase are in
# _generated.py but nothing in laura/models/ subclasses them -- so there is no
# class_uri anywhere in the MRO and the element resolves to its parent.  Not a
# linkml_class_name() bug: wiring them up would also pull in the generated
# fields and validators, which is a model-layer change, not an exporter one.
_UNWIRED_TO_THEIR_GENERATED_BASE = {"MatrixTransform", "Photon_Monitor", "PowerSupply"}


@pytest.mark.parametrize("hardware_type", sorted(ELEMENT_REGISTRY))
def test_linkml_class_name_resolves_to_this_element_own_class(hardware_type):
    """``linkml_class_name()`` must name the element's own class, not an ancestor.

    It drives ``rdf:type`` in the RDF exporter, so an ancestor here silently
    mistypes the element.  ``LaserMirror(Element, _LaserMirrorBase)`` linearises
    ``_ElementBase`` ahead of ``_LaserMirrorBase``, which typed every laser
    mirror, energy meter and attenuator as the generic ``laura:Element``.
    """
    if hardware_type in _UNWIRED_TO_THEIR_GENERATED_BASE:
        pytest.xfail(f"{hardware_type} does not subclass its generated base")
    resolved = ELEMENT_REGISTRY[hardware_type].linkml_class_name()
    assert _normalise(resolved) == _normalise(hardware_type), (
        f"'{hardware_type}' resolves to schema class '{resolved}'"
    )


def test_ontology_declares_every_schema_class():
    """Every schema class should have an ``owl:Class`` in the committed ontology.

    The generated artefacts drift silently — nothing imports them, so a schema
    class added without a regeneration is invisible until someone reasons over
    the ontology and finds a third of the lattice untyped.
    """
    owl = (GENERATED_DIR / "laura_ontology.owl").read_text(encoding="utf-8")
    # gen-owl drops underscores, so Solenoid_Magnet becomes laura:SolenoidMagnet.
    missing = [
        name
        for name in _schema_class_names()
        if f"laura:{name.replace('_', '')} a owl:Class" not in owl
    ]
    assert not missing, (
        "schema classes absent from laura/schema/generated/laura_ontology.owl: "
        + ", ".join(sorted(missing))
        + ". Regenerate with `bash laura/schema/generate.sh`."
    )
