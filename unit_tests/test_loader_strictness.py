"""
Tests for explicit, rejectable element-load failures.

LAURA's loader skips an element it cannot parse and returns ``None``, so a
machine can load "successfully" while missing elements.
These tests check that losses can be made visible.
"""

import pytest
import yaml

from laura.Importers.YAML_Loader import (
    DuplicateElementError,
    ElementLoadError,
    LazyElementDict,
    collect_unique_by_name,
    collect_unique_filenames,
    interpret_YAML_Element,
    read_YAML_Combined_File,
    read_YAML_Element_File,
)
from laura.laura import LAURA

GOOD_QUAD = {
    "name": "Q1",
    "hardware_class": "Magnet",
    "hardware_type": "Quadrupole",
    "machine_area": "SEC",
    "magnetic": {"length": 0.3, "k1l": -1.5},
    "physical": {"length": 0.3, "middle": {"x": 0.0, "y": 0.0, "z": 1.0}},
}

NO_TYPE = {"name": "NOTYPE", "machine_area": "SEC"}

UNREGISTERED = {
    "name": "UNREG",
    "hardware_type": "UnknownWidgetFoo",
    "machine_area": "SEC",
}

INVALID = {
    "name": "BADLEN",
    "hardware_class": "Magnet",
    "hardware_type": "Quadrupole",
    "machine_area": "SEC",
    "magnetic": {"length": 0.3},
    "physical": {"length": -1.0, "middle": {"x": 0.0, "y": 0.0, "z": 1.0}},
}

BAD_ELEMENTS = [
    pytest.param(NO_TYPE, "no_hardware_type", id="no_hardware_type"),
    pytest.param(
        UNREGISTERED, "unregistered_hardware_type", id="unregistered_hardware_type"
    ),
    pytest.param(INVALID, "validation_error", id="validation_error"),
]

# Inheritance is resolved on the raw dict, one layer above
# ``interpret_YAML_Element``, so its two failure reasons cannot join
# BAD_ELEMENTS.  They meet the others at the file level, below.
ORPHAN = {**GOOD_QUAD, "name": "ORPHAN", "inherits_from": "NOT_A_REAL_ELEMENT"}

CYCLE = {
    "A": {**GOOD_QUAD, "name": "A", "inherits_from": "B"},
    "B": {**GOOD_QUAD, "name": "B", "inherits_from": "A"},
}

BAD_DOCUMENTS = [
    pytest.param({"NOTYPE": NO_TYPE}, "no_hardware_type", id="no_hardware_type"),
    pytest.param(
        {"UNREG": UNREGISTERED},
        "unregistered_hardware_type",
        id="unregistered_hardware_type",
    ),
    pytest.param({"BADLEN": INVALID}, "validation_error", id="validation_error"),
    pytest.param({"ORPHAN": ORPHAN}, "missing_parent", id="missing_parent"),
    pytest.param(CYCLE, "inheritance_cycle", id="inheritance_cycle"),
]


def _write(directory, data, filename=None):
    path = directory / (filename or f"{data['name']}.yaml")
    path.write_text(yaml.safe_dump(data))
    return str(path)


# ---------------------------------------------------------------------------
# interpret_YAML_Element
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("data,reason", BAD_ELEMENTS)
def test_failure_is_recorded_on_the_errors_list(data, reason):
    """The default stays permissive, but the loss is now itemised."""
    errors = []
    assert interpret_YAML_Element(data, errors=errors) is None
    assert len(errors) == 1
    assert errors[0].reason == reason
    assert errors[0].name == data["name"]
    assert data["name"] in str(errors[0])


@pytest.mark.parametrize("data,reason", BAD_ELEMENTS)
def test_strict_raises_instead_of_skipping(data, reason):
    with pytest.raises(ElementLoadError) as exc:
        interpret_YAML_Element(data, strict=True)
    assert exc.value.reason == reason
    assert exc.value.name == data["name"]


@pytest.mark.parametrize("data,reason", BAD_ELEMENTS)
def test_strict_failure_is_recorded_before_it_is_raised(data, reason):
    """A strict caller that catches the error still finds it on the report."""
    errors = []
    with pytest.raises(ElementLoadError):
        interpret_YAML_Element(data, strict=True, errors=errors)
    assert [e.reason for e in errors] == [reason]


def test_validation_error_keeps_the_underlying_exception():
    errors = []
    interpret_YAML_Element(INVALID, errors=errors)
    assert errors[0].__cause__ is not None
    assert errors[0].hardware_type == "Quadrupole"


def test_a_good_element_records_nothing():
    errors = []
    assert interpret_YAML_Element(GOOD_QUAD, errors=errors) is not None
    assert errors == []


@pytest.mark.parametrize("data,reason", BAD_ELEMENTS)
def test_default_behaviour_is_unchanged(data, reason):
    """No errors list, no strict flag: skip and return None, as before."""
    assert interpret_YAML_Element(data) is None


# ---------------------------------------------------------------------------
# read_YAML_Element_File / read_YAML_Combined_File
# ---------------------------------------------------------------------------


def test_element_file_records_its_filename(tmp_path):
    errors = []
    path = _write(tmp_path, INVALID)
    assert read_YAML_Element_File(path, errors=errors) is None
    assert errors[0].filename == path
    assert path in str(errors[0])


def test_element_file_strict_raises(tmp_path):
    with pytest.raises(ElementLoadError):
        read_YAML_Element_File(_write(tmp_path, INVALID), strict=True)


def test_combined_file_reports_every_failure(tmp_path):
    combined = tmp_path / "summary.yaml"
    combined.write_text(
        yaml.safe_dump(
            {d["name"]: d for d in (GOOD_QUAD, NO_TYPE, UNREGISTERED, INVALID)}
        )
    )
    errors = []
    results = read_YAML_Combined_File(str(combined), errors=errors)
    assert sum(1 for r in results if r is not None) == 1
    assert {e.reason for e in errors} == {
        "no_hardware_type",
        "unregistered_hardware_type",
        "validation_error",
    }


@pytest.mark.parametrize("document,reason", BAD_DOCUMENTS)
def test_every_reason_is_recorded_at_the_file_level(tmp_path, document, reason):
    """Both failure channels, over the whole set of reasons — including the
    two that inheritance added, which never reach ``interpret_YAML_Element``."""
    combined = tmp_path / "summary.yaml"
    combined.write_text(yaml.safe_dump(document))
    errors = []
    read_YAML_Combined_File(str(combined), errors=errors)
    assert errors
    assert {e.reason for e in errors} == {reason}


@pytest.mark.parametrize("document,reason", BAD_DOCUMENTS)
def test_every_reason_is_raised_under_strict(tmp_path, document, reason):
    combined = tmp_path / "summary.yaml"
    combined.write_text(yaml.safe_dump(document))
    with pytest.raises(ElementLoadError) as exc:
        read_YAML_Combined_File(str(combined), strict=True)
    assert exc.value.reason == reason


def test_combined_file_strict_raises_on_the_first_failure(tmp_path):
    combined = tmp_path / "summary.yaml"
    combined.write_text(yaml.safe_dump({d["name"]: d for d in (GOOD_QUAD, INVALID)}))
    with pytest.raises(ElementLoadError) as exc:
        read_YAML_Combined_File(str(combined), strict=True)
    assert exc.value.name == "BADLEN"


# ---------------------------------------------------------------------------
# LazyElementDict
# ---------------------------------------------------------------------------


def test_lazy_dict_records_on_access(tmp_path):
    lazy = LazyElementDict(
        {"Q1": _write(tmp_path, GOOD_QUAD), "BADLEN": _write(tmp_path, INVALID)}
    )
    assert lazy.load_errors == []  # nothing read yet
    assert lazy["Q1"] is not None
    assert lazy.load_errors == []
    assert lazy["BADLEN"] is None
    assert [e.reason for e in lazy.load_errors] == ["validation_error"]


def test_lazy_dict_does_not_re_read_a_failed_element(tmp_path):
    """A failed element used to be re-parsed from disk on every access, and
    each attempt would now append a duplicate error record."""
    path = _write(tmp_path, INVALID)
    lazy = LazyElementDict({"BADLEN": path})
    for _ in range(3):
        assert lazy["BADLEN"] is None
    assert len(lazy.load_errors) == 1


def test_lazy_dict_strict_raises_on_access(tmp_path):
    lazy = LazyElementDict({"BADLEN": _write(tmp_path, INVALID)}, strict=True)
    with pytest.raises(ElementLoadError):
        lazy["BADLEN"]
    # Nothing cached, so a retry raises again rather than yielding None.
    with pytest.raises(ElementLoadError):
        lazy["BADLEN"]


def test_lazy_dict_shares_an_external_errors_list(tmp_path):
    errors = []
    lazy = LazyElementDict({"BADLEN": _write(tmp_path, INVALID)}, errors=errors)
    lazy["BADLEN"]
    assert len(errors) == 1


# ---------------------------------------------------------------------------
# LAURA
# ---------------------------------------------------------------------------


def _machine_dir(tmp_path):
    directory = tmp_path / "elements"
    directory.mkdir(exist_ok=True)
    _write(directory, GOOD_QUAD)
    _write(directory, INVALID)
    return directory


def test_machine_load_errors_are_itemised_eagerly(tmp_path):
    machine = LAURA(element_list=str(_machine_dir(tmp_path)), eager_mode=True)
    assert "Q1" in machine.elements
    assert [e.name for e in machine.load_errors] == ["BADLEN"]


@pytest.mark.parametrize(
    "section", [None, {"sections": {"S1": ["Q1"]}}], ids=["no_section", "section"]
)
def test_machine_reports_at_construction_even_in_lazy_mode(tmp_path, section):
    """Lazy mode still resolves every element while the machine is built."""
    machine = LAURA(element_list=str(_machine_dir(tmp_path)), section=section)
    assert [e.name for e in machine.load_errors] == ["BADLEN"]
    assert machine.elements["BADLEN"] is None
    assert len(machine.load_errors) == 1  # not re-read, not double-recorded


def test_machine_strict_eager_rejects_the_whole_load(tmp_path):
    with pytest.raises(ElementLoadError):
        LAURA(element_list=str(_machine_dir(tmp_path)), eager_mode=True, strict=True)


def test_machine_strict_lazy_rejects_the_whole_load(tmp_path):
    """Strict lazy mode fails at construction only because of the force-load
    above; the guarantee being pinned is that it fails, not when."""
    with pytest.raises(ElementLoadError):
        LAURA(element_list=str(_machine_dir(tmp_path)), strict=True)


# ---------------------------------------------------------------------------
# Duplicate names
# ---------------------------------------------------------------------------


def test_collect_unique_by_name_keeps_the_last_and_reports_the_loss():
    errors = []
    result = collect_unique_by_name(
        [
            ("Q1", "a.yaml", "first"),
            ("Q2", "b.yaml", "other"),
            ("Q1", "c.yaml", "second"),
        ],
        errors=errors,
    )
    assert result == {"Q1": "second", "Q2": "other"}  # later wins, as before
    assert len(errors) == 1
    assert isinstance(errors[0], DuplicateElementError)
    assert errors[0].reason == "duplicate_name"
    assert errors[0].name == "Q1"
    assert errors[0].filename == "a.yaml"  # the definition that was lost
    assert errors[0].superseded_by == "c.yaml"  # the one that replaced it


def test_collect_unique_by_name_strict_raises():
    with pytest.raises(DuplicateElementError):
        collect_unique_by_name([("Q1", "a.yaml", 1), ("Q1", "b.yaml", 2)], strict=True)


def test_a_duplicate_is_an_element_load_error():
    """So `except ElementLoadError` and a strict load both cover it."""
    assert issubclass(DuplicateElementError, ElementLoadError)


def test_three_definitions_report_two_losses():
    errors = []
    collect_unique_by_name(
        [("Q1", "a.yaml", 1), ("Q1", "b.yaml", 2), ("Q1", "c.yaml", 3)], errors=errors
    )
    assert [(e.filename, e.superseded_by) for e in errors] == [
        ("a.yaml", "b.yaml"),
        ("b.yaml", "c.yaml"),
    ]


def test_duplicate_filenames_are_found_without_parsing(tmp_path):
    """Two files declaring the same ``name:``, found from the metadata scan."""
    first = _write(tmp_path, GOOD_QUAD, filename="one.yaml")
    second = _write(tmp_path, GOOD_QUAD, filename="two.yaml")
    errors = []
    filenames = collect_unique_filenames([first, second], errors=errors)
    assert filenames == {"Q1": second}
    assert errors[0].name == "Q1"
    assert (errors[0].filename, errors[0].superseded_by) == (first, second)


def test_a_name_disagreeing_with_its_filename_collides(tmp_path):
    """The UKXFEL fault: `FEL1_START.1.yaml` declares `name: FEL1_END.1`, so
    `FEL1_START.1` does not exist and `FEL1_END.1` exists twice."""
    real = _write(
        tmp_path, {**GOOD_QUAD, "name": "FEL1_END.1"}, filename="FEL1_END.1.yaml"
    )
    liar = _write(
        tmp_path, {**GOOD_QUAD, "name": "FEL1_END.1"}, filename="FEL1_START.1.yaml"
    )
    errors = []
    filenames = collect_unique_filenames([real, liar], errors=errors)
    assert "FEL1_START.1" not in filenames
    assert [e.name for e in errors] == ["FEL1_END.1"]


def test_machine_reports_duplicate_element_files(tmp_path):
    directory = tmp_path / "elements"
    directory.mkdir()
    _write(directory, GOOD_QUAD, filename="one.yaml")
    _write(directory, GOOD_QUAD, filename="two.yaml")
    machine = LAURA(element_list=str(directory))
    assert [e.reason for e in machine.load_errors] == ["duplicate_name"]
    assert len(machine.elements) == 1


def test_machine_strict_rejects_duplicate_element_files(tmp_path):
    directory = tmp_path / "elements"
    directory.mkdir()
    _write(directory, GOOD_QUAD, filename="one.yaml")
    _write(directory, GOOD_QUAD, filename="two.yaml")
    with pytest.raises(DuplicateElementError):
        LAURA(element_list=str(directory), strict=True)


def test_machine_reports_duplicates_from_an_element_list():
    """Elements handed over as objects have no filename to name."""
    quads = [interpret_YAML_Element(GOOD_QUAD), interpret_YAML_Element(GOOD_QUAD)]
    machine = LAURA(element_list=quads)
    assert [e.name for e in machine.load_errors] == ["Q1"]
    assert machine.load_errors[0].filename is None


def test_machine_without_failures_reports_none(tmp_path):
    directory = tmp_path / "elements"
    directory.mkdir()
    _write(directory, GOOD_QUAD)
    machine = LAURA(element_list=str(directory), eager_mode=True, strict=True)
    assert machine.load_errors == []
    assert "Q1" in machine.elements
