"""
Tests for element inheritance -- an element declaring ``inherits_from``
(or ``inherit``, the PALS spelling) and overriding only what differs.

The merge itself is the easy half. What these mostly pin down is what must
not be inherited: in LAURA position lives on the element, so inheriting it either
trips ``_check_placement_exclusivity`` or -- worse -- silently co-locates two
elements.
"""

import warnings

import pytest
import yaml

from laura.Importers.YAML_Loader import (
    COMBINED_TEMPLATES_KEY,
    ElementLoadError,
    LazyElementDict,
    RawFileNamespace,
    collect_template_filenames,
    fast_get_element_metadata,
    read_YAML_Combined_File,
    read_YAML_Element_File,
    resolve_inheritance,
)
from laura.laura import LAURA

PARENT = {
    "name": "Q1",
    "hardware_class": "Magnet",
    "hardware_type": "Quadrupole",
    "machine_area": "SEC",
    "magnetic": {"length": 0.3, "k1l": -1.5},
    "physical": {"length": 0.3, "s": 4.0, "middle": {"x": 0.0, "y": 0.0, "z": 4.15}},
}


def _child(**overrides):
    child = {
        "name": "Q2",
        "hardware_class": "Magnet",
        "hardware_type": "Quadrupole",
        "inherits_from": "Q1",
    }
    child.update(overrides)
    return child


def _write(directory, data, filename=None):
    path = directory / (filename or f"{data['name']}.yaml")
    path.write_text(yaml.safe_dump(data))
    return str(path)


def _quiet(elem, namespace, **kwargs):
    """Resolve without letting the advisory warnings escape into the report."""
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        return resolve_inheritance(elem, namespace, **kwargs)


# ---------------------------------------------------------------------------
# The merge
# ---------------------------------------------------------------------------


def test_an_element_that_inherits_nothing_is_untouched():
    """The path has to be inert by default -- this is most elements."""
    elem = dict(PARENT)
    assert resolve_inheritance(elem, {}) is elem


def test_single_parent_merges_and_the_child_wins():
    merged = _quiet(_child(magnetic={"k1l": 2.5}), {"Q1": PARENT})
    assert merged["magnetic"]["k1l"] == 2.5  # child's own value
    assert merged["magnetic"]["length"] == 0.3  # merged key by key, not replaced
    assert merged["name"] == "Q2"


def test_length_is_inherited():
    """It is a property of the device, and most of what makes a lattice compact."""
    assert _quiet(_child(), {"Q1": PARENT})["physical"]["length"] == 0.3


def test_a_chain_resolves_depth_first():
    namespace = {
        "BASE": PARENT,
        "MID": {
            "name": "MID",
            "hardware_class": "Magnet",
            "hardware_type": "Quadrupole",
            "inherits_from": "BASE",
            "magnetic": {"k1l": 9.0},
        },
        "LEAF": {
            "name": "LEAF",
            "hardware_class": "Magnet",
            "hardware_type": "Quadrupole",
            "inherits_from": "MID",
        },
    }
    merged = _quiet(namespace["LEAF"], namespace)
    assert merged["physical"]["length"] == 0.3  # from BASE, two levels up
    assert merged["magnetic"]["k1l"] == 9.0  # from MID, overriding BASE


def test_a_parent_declared_after_its_child_still_resolves():
    """Resolution is by name, not by file order."""
    document = {
        "Q2": _child(),
        "Q1": PARENT,  # declared second
    }
    assert _quiet(document["Q2"], document)["physical"]["length"] == 0.3


def test_a_list_is_replaced_outright_not_merged():
    """A half-overridden list of coefficients is not meaningful."""
    parent = {**PARENT, "inputs": ["current", "voltage"]}
    merged = _quiet(_child(inputs=["power"]), {"Q1": parent})
    assert merged["inputs"] == ["power"]


def test_an_explicit_null_in_the_child_unsets_the_inherited_value():
    """Distinct from omitting the key, which inherits."""
    merged = _quiet(_child(machine_area=None), {"Q1": PARENT})
    assert "machine_area" in merged
    assert merged["machine_area"] is None


def test_the_link_is_kept_for_a_later_collapse_on_export():
    assert _quiet(_child(), {"Q1": PARENT})["inherits_from"] == "Q1"


def test_the_pals_inherit_spelling_is_accepted():
    child = _child()
    del child["inherits_from"]
    child["inherit"] = "Q1"
    merged = _quiet(child, {"Q1": PARENT})
    assert merged["physical"]["length"] == 0.3
    # Normalised to the canonical slot, whichever spelling was written.
    assert merged["inherits_from"] == "Q1"


def test_hardware_type_is_inherited_from_a_template_that_carries_it():
    template = {"name": "T", "hardware_class": "Magnet", "hardware_type": "Quadrupole"}
    child = {"name": "Q2", "inherits_from": "T", "physical": {"length": 0.2}}
    assert _quiet(child, {"T": template})["hardware_type"] == "Quadrupole"


# ---------------------------------------------------------------------------
# What must not be inherited
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "field,value",
    [
        ("s", 4.0),
        ("middle", {"x": 0.0, "y": 0.0, "z": 4.15}),
        ("s_point", 4.0),
        ("datum", {"x": 0.0, "y": 0.0, "z": 1.0}),
        ("reference_placement", {"element": "Q0", "s_offset": 1.0}),
        ("rotation", {"psi": 0.1}),
        ("global_rotation", {"psi": 0.1}),
        ("survey", {"x": 1.0}),
        ("error", {"x": 1.0}),
        ("physical_angle", 0.2),
    ],
)
def test_placement_and_measured_fields_are_never_inherited(field, value):
    """The quiet failure is the dangerous one: without this, a child that
    states no position of its own lands exactly on top of its parent, and
    every export then works from a lattice that is wrong but valid."""
    parent = {**PARENT, "physical": {"length": 0.3, field: value}}
    merged = _quiet(_child(), {"Q1": parent})
    assert field not in merged.get("physical", {})
    assert merged["physical"]["length"] == 0.3  # ...but length still comes across


@pytest.mark.parametrize(
    "field,value",
    [
        ("name", "Q1"),
        ("alias", ["QUAD-ONE"]),
        ("virtual_name", "VQ1"),
        ("subelement", "PARENT-MAGNET"),
        ("upstream", ["A"]),
        ("downstream", ["B"]),
    ],
)
def test_identity_and_topology_fields_are_never_inherited(field, value):
    merged = _quiet(_child(), {"Q1": {**PARENT, field: value}})
    assert merged.get(field) != value or field == "name"
    assert merged["name"] == "Q2"


def test_a_physical_block_of_only_excluded_keys_does_not_appear():
    parent = {**PARENT, "physical": {"s": 4.0}}
    assert "physical" not in _quiet(_child(), {"Q1": parent})


def test_a_child_may_state_its_own_position():
    merged = _quiet(_child(physical={"s": 12.0}), {"Q1": PARENT})
    assert merged["physical"]["s"] == 12.0
    assert merged["physical"]["length"] == 0.3


def test_a_positioned_parent_does_not_trip_placement_exclusivity(tmp_path):
    """The `physical.py` trap: `reference_placement` may not meet `s`/`middle`.

    Excluding position is what keeps this child constructible -- otherwise it
    inherits the parent's `s` and fails to validate, and a failing element is
    a skipped one.
    """
    document = {
        "Q1": PARENT,  # carries both `s` and `middle`
        "Q2": _child(physical={"reference_placement": {"element": "Q1"}}),
    }
    path = tmp_path / "m.yaml"
    path.write_text(yaml.safe_dump(document))
    errors = []
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        loaded = [e for e in read_YAML_Combined_File(str(path), errors=errors) if e]
    assert [e.name for e in loaded] == ["Q1", "Q2"]
    assert errors == []


# ---------------------------------------------------------------------------
# Aliases
#
# A field may be written under any of its validation_alias choices, and a
# raw-key merge would treat those as unrelated keys.
# ---------------------------------------------------------------------------


def test_a_child_overriding_under_an_alias_still_wins():
    """The trap: `length` and `magnetic_length` are the same field, both
    survive a raw-key merge, and AliasChoices order would hand the parent the
    win -- silently ignoring the child's override."""
    merged = _quiet(_child(physical={"magnetic_length": 0.9}), {"Q1": PARENT})
    assert merged["physical"]["length"] == 0.9
    assert "magnetic_length" not in merged["physical"]


@pytest.mark.parametrize("spelling", ["middle", "position", "centre"])
def test_position_is_excluded_under_every_spelling(spelling):
    """Excluding only the canonical name would let `position:` sneak through."""
    parent = {**PARENT, "physical": {"length": 0.3, spelling: {"z": 4.15}}}
    merged = _quiet(_child(), {"Q1": parent})
    assert "middle" not in merged["physical"]
    assert spelling not in merged["physical"]


# ---------------------------------------------------------------------------
# Failure handling -- none of this may go through the silent-skip path
# ---------------------------------------------------------------------------


def test_a_missing_parent_is_recorded_naming_both_elements():
    errors = []
    resolve_inheritance(_child(inherits_from="NOPE"), {}, errors=errors)
    assert len(errors) == 1
    assert errors[0].reason == "missing_parent"
    assert errors[0].name == "Q2"
    assert "NOPE" in errors[0].detail


def test_a_missing_parent_raises_under_strict():
    with pytest.raises(ElementLoadError) as excinfo:
        resolve_inheritance(_child(inherits_from="NOPE"), {}, strict=True)
    assert excinfo.value.reason == "missing_parent"


def test_a_cycle_is_recorded_naming_the_whole_chain():
    namespace = {
        "A": {"name": "A", "hardware_type": "Quadrupole", "inherits_from": "B"},
        "B": {"name": "B", "hardware_type": "Quadrupole", "inherits_from": "A"},
    }
    errors = []
    resolve_inheritance(namespace["A"], namespace, errors=errors)
    assert len(errors) == 1
    assert errors[0].reason == "inheritance_cycle"
    assert "A -> B -> A" in errors[0].detail


def test_self_inheritance_is_a_cycle():
    elem = {"name": "A", "hardware_type": "Quadrupole", "inherits_from": "A"}
    errors = []
    resolve_inheritance(elem, {"A": elem}, errors=errors)
    assert errors[0].reason == "inheritance_cycle"


def test_a_cycle_raises_under_strict():
    namespace = {
        "A": {"name": "A", "hardware_type": "Quadrupole", "inherits_from": "B"},
        "B": {"name": "B", "hardware_type": "Quadrupole", "inherits_from": "A"},
    }
    with pytest.raises(ElementLoadError) as excinfo:
        resolve_inheritance(namespace["A"], namespace, strict=True)
    assert excinfo.value.reason == "inheritance_cycle"


@pytest.mark.parametrize("reason", ["missing_parent", "inheritance_cycle"])
def test_the_new_reasons_are_declared(reason):
    assert reason in ElementLoadError.REASONS


def test_a_lone_file_naming_a_parent_is_reported_not_silently_stripped(tmp_path):
    """A single file has no namespace to resolve against. Losing the parent's
    values quietly would produce a quadrupole with no strength."""
    path = _write(tmp_path, _child())
    errors = []
    read_YAML_Element_File(path, errors=errors)
    assert [e.reason for e in errors] == ["missing_parent"]


def test_a_lone_file_naming_a_parent_raises_under_strict(tmp_path):
    path = _write(tmp_path, _child())
    with pytest.raises(ElementLoadError):
        read_YAML_Element_File(path, strict=True)


# ---------------------------------------------------------------------------
# Warnings -- the element is fine, but something about it is quietly wrong
# ---------------------------------------------------------------------------


def test_parent_keys_the_childs_model_cannot_hold_are_warned_about():
    """`baseElement` is extra="ignore", so these vanish without a word."""
    parent = {**PARENT, "degauss": {"tolerance": 0.1}}
    child = _child(hardware_type="Drift", hardware_class="Drift")
    with pytest.warns(UserWarning, match="degauss"):
        resolve_inheritance(child, {"Q1": parent})


def test_an_inherited_literal_identifier_is_warned_about():
    """A parent spelling its PVs out literally hands the child the parent's
    power supply."""
    parent = {
        **PARENT,
        "controls": {
            "variables": {"SETI": {"identifier": "Q1:SETI", "protocol": "CA"}}
        },
    }
    with pytest.warns(UserWarning, match="process variables"):
        resolve_inheritance(_child(), {"Q1": parent})


def test_a_literal_identifier_from_a_grandparent_is_warned_about():
    """Inheriting a grandparent's PVs is just as wrong as a parent's."""
    namespace = {
        "BASE": {
            **PARENT,
            "name": "BASE",
            "controls": {
                "variables": {"SETI": {"identifier": "BASE:SETI", "protocol": "CA"}}
            },
        },
        "MID": {
            "name": "MID",
            "hardware_class": "Magnet",
            "hardware_type": "Quadrupole",
            "inherits_from": "BASE",
        },
        "LEAF": {
            "name": "LEAF",
            "hardware_class": "Magnet",
            "hardware_type": "Quadrupole",
            "inherits_from": "MID",
        },
    }
    with pytest.warns(UserWarning, match="BASE"):
        resolve_inheritance(namespace["LEAF"], namespace)


def test_a_templated_identifier_does_not_warn():
    """`{name}` re-templates per element, which is the correct pattern."""
    parent = {
        **PARENT,
        "controls": {
            "variables": {"SETI": {"identifier": "{name}:SETI", "protocol": "CA"}}
        },
    }
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        resolve_inheritance(_child(), {"Q1": parent})


def test_warnings_are_not_load_failures():
    """They do not reject the element, even under strict."""
    parent = {
        **PARENT,
        "controls": {
            "variables": {"SETI": {"identifier": "Q1:SETI", "protocol": "CA"}}
        },
    }
    errors = []
    with pytest.warns(UserWarning):
        merged = resolve_inheritance(
            _child(), {"Q1": parent}, errors=errors, strict=True
        )
    assert errors == []
    assert merged["name"] == "Q2"


# ---------------------------------------------------------------------------
# Combined-file mode
# ---------------------------------------------------------------------------


def test_combined_file_resolves_inheritance(tmp_path):
    document = {"Q1": PARENT, "Q2": _child(magnetic={"k1l": 7.0})}
    path = tmp_path / "m.yaml"
    path.write_text(yaml.safe_dump(document))
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        loaded = {e.name: e for e in read_YAML_Combined_File(str(path)) if e}
    assert loaded["Q2"].physical.length == 0.3
    assert loaded["Q2"].magnetic.k1l == 7.0


def test_a_template_key_defines_without_becoming_an_element(tmp_path):
    """Without this every template is also a real element in the machine and
    in every export."""
    document = {
        COMBINED_TEMPLATES_KEY: {"TPL": {**PARENT, "name": "TPL"}},
        "Q2": _child(inherits_from="TPL"),
    }
    path = tmp_path / "m.yaml"
    path.write_text(yaml.safe_dump(document))
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        loaded = [e for e in read_YAML_Combined_File(str(path)) if e]
    assert [e.name for e in loaded] == ["Q2"]
    assert loaded[0].physical.length == 0.3


def test_validate_true_accepts_a_file_that_declares_a_parent(tmp_path):
    path = tmp_path / "m.yaml"
    path.write_text(yaml.safe_dump({"Q1": PARENT, "Q2": _child()}))
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        loaded = [e for e in read_YAML_Combined_File(str(path), validate=True) if e]
    assert len(loaded) == 2


# ---------------------------------------------------------------------------
# Lazy directory mode
# ---------------------------------------------------------------------------


def test_the_inherit_slot_is_found_by_the_metadata_scanner(tmp_path):
    """One more regex over the same 2000-char head -- no extra I/O to know
    whether a lazily-loaded element inherits at all."""
    assert (
        fast_get_element_metadata(_write(tmp_path, _child()))["inherits_from"] == "Q1"
    )


def test_the_metadata_scanner_finds_the_pals_spelling(tmp_path):
    child = _child()
    del child["inherits_from"]
    child["inherit"] = "Q1"
    assert fast_get_element_metadata(_write(tmp_path, child))["inherits_from"] == "Q1"


def test_an_element_without_a_parent_reports_none(tmp_path):
    assert fast_get_element_metadata(_write(tmp_path, PARENT))["inherits_from"] is None


def test_lazy_dict_resolves_against_its_directory(tmp_path):
    _write(tmp_path, PARENT)
    _write(tmp_path, _child(magnetic={"k1l": 4.0}))
    elements = LazyElementDict(
        {"Q1": str(tmp_path / "Q1.yaml"), "Q2": str(tmp_path / "Q2.yaml")}
    )
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        child = elements["Q2"]
    assert child.physical.length == 0.3
    assert child.magnetic.k1l == 4.0
    assert child.physical.s is None  # the parent's position did not come across


def test_lazy_dict_resolves_against_an_underscore_template(tmp_path):
    """`_`-prefixed files never become elements, but must stay findable."""
    _write(tmp_path, {**PARENT, "name": "TPL"}, filename="_template.yaml")
    _write(tmp_path, _child(inherits_from="TPL"))
    elements = LazyElementDict(
        {"Q2": str(tmp_path / "Q2.yaml")},
        templates={"TPL": str(tmp_path / "_template.yaml")},
    )
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        assert elements["Q2"].physical.length == 0.3
    assert "TPL" not in elements


def test_a_missing_parent_in_lazy_mode_is_recorded(tmp_path):
    _write(tmp_path, _child(inherits_from="NOPE"))
    elements = LazyElementDict({"Q2": str(tmp_path / "Q2.yaml")})
    elements["Q2"]
    assert [e.reason for e in elements.load_errors] == ["missing_parent"]


def test_the_raw_namespace_reads_each_parent_once(tmp_path):
    path = _write(tmp_path, PARENT)
    namespace = RawFileNamespace({"Q1": path})
    first = namespace.get("Q1")
    assert first is not None
    assert namespace.get("Q1") is first  # cached, not re-read


def test_the_raw_namespace_returns_none_for_an_unknown_name():
    assert RawFileNamespace({}).get("NOPE") is None


def test_a_shared_template_is_resolved_once(tmp_path):
    """A template used by many children should not be re-resolved per child."""
    namespace = {"Q1": PARENT}
    memo = {}
    _quiet(_child(name="A"), namespace, memo=memo)
    _quiet(_child(name="B"), namespace, memo=memo)
    assert set(memo) == {"A", "B"}


# ---------------------------------------------------------------------------
# collect_template_filenames
# ---------------------------------------------------------------------------


def test_templates_are_collected_by_declared_name(tmp_path):
    path = _write(tmp_path, {**PARENT, "name": "TPL"}, filename="_tpl.yaml")
    assert collect_template_filenames([path]) == {"TPL": path}


def test_a_controls_schema_is_not_mistaken_for_a_template(tmp_path):
    """`_schema.yaml` is `_`-prefixed too, but holds a bare `variables:`
    mapping rather than an element."""
    path = tmp_path / "_schema.yaml"
    path.write_text(
        yaml.safe_dump({"variables": {"SETI": {"identifier": "{name}:SETI"}}})
    )
    assert collect_template_filenames([str(path)]) == {}


def test_a_file_without_a_hardware_type_is_not_a_template(tmp_path):
    path = tmp_path / "_partial.yaml"
    path.write_text(yaml.safe_dump({"name": "TPL", "machine_area": "SEC"}))
    assert collect_template_filenames([str(path)]) == {}


def test_duplicate_templates_warn(tmp_path):
    first = _write(tmp_path, {**PARENT, "name": "TPL"}, filename="_a.yaml")
    second = _write(tmp_path, {**PARENT, "name": "TPL"}, filename="_b.yaml")
    with pytest.warns(UserWarning, match="TPL"):
        collected = collect_template_filenames([first, second])
    assert collected == {"TPL": second}  # last wins, as elsewhere


# ---------------------------------------------------------------------------
# Through LAURA itself
# ---------------------------------------------------------------------------


def test_machine_resolves_inheritance_from_a_directory(tmp_path):
    directory = tmp_path / "elements"
    directory.mkdir()
    _write(directory, {**PARENT, "name": "TPL"}, filename="_tpl.yaml")
    _write(directory, _child(inherits_from="TPL"))
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        machine = LAURA(element_list=str(directory), eager_mode=True)
    assert machine.elements["Q2"].physical.length == 0.3
    assert "TPL" not in machine.elements  # the template is not a machine element


def test_machine_reports_a_missing_parent(tmp_path):
    directory = tmp_path / "elements"
    directory.mkdir()
    _write(directory, _child(inherits_from="NOPE"))
    machine = LAURA(element_list=str(directory), eager_mode=True)
    assert [e.reason for e in machine.load_errors] == ["missing_parent"]


def test_machine_strict_rejects_a_missing_parent(tmp_path):
    directory = tmp_path / "elements"
    directory.mkdir()
    _write(directory, _child(inherits_from="NOPE"))
    with pytest.raises(ElementLoadError):
        LAURA(element_list=str(directory), eager_mode=True, strict=True)


def test_a_machine_without_inheritance_records_nothing(tmp_path):
    directory = tmp_path / "elements"
    directory.mkdir()
    _write(directory, PARENT)
    machine = LAURA(element_list=str(directory), eager_mode=True)
    assert machine.load_errors == []
    assert machine.elements["Q1"].inherits_from is None
