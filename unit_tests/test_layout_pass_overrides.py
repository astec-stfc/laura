"""Per-pass ``overrides``: carried intact, not applied; bad targets refused."""

import pytest

from laura.models.element import RFCavity
from laura.models.elementList import MachineModel
from unit_tests.helpers import quad, quiet

SECTIONS = {
    "INJECTOR": ["INJ_Q"],
    "LINAC": ["CAV_01", "LIN_Q"],
    "ARC": ["ARC_B"],
    "DUMP": ["DMP_Q"],
}


def second_pass(overrides, **options):
    """The ERL path, with *overrides* (and *options*) on the second LINAC pass."""
    return [
        "INJECTOR",
        {"LINAC": {"multipass": 1}},
        "ARC",
        {"LINAC": {"multipass": 2, **options, "overrides": overrides}},
        "DUMP",
    ]


# The decelerating return leg of an ERL: same cavity, ~180 degrees apart.
ERL = second_pass({"CAV_01": {"cavity.phase": 180}})


def elements():
    built = {
        name: quad(name, length, 1.0, "A")
        for name, length in (
            ("INJ_Q", 0.2),
            ("LIN_Q", 0.3),
            ("ARC_B", 0.4),
            ("DMP_Q", 0.2),
        )
    }
    built["CAV_01"] = RFCavity(
        name="CAV_01",
        machine_area="A",
        physical={"length": 0.6},
        cavity={"phase": 0.0},
    )
    return built


def machine(layout):
    with quiet():
        return MachineModel(
            elements=elements(),
            section={"sections": SECTIONS},
            layout={"layouts": {"ERL": layout}, "default_layout": "ERL"},
        )


@pytest.fixture
def erl():
    return machine(ERL)


def passes(model, section):
    return [p for p in model.lattices["ERL"].passes if p.section == section]


def test_override_lands_on_the_pass_that_stated_it(erl):
    first, second = passes(erl, "LINAC")
    assert first.overrides == {}
    assert second.overrides == {"CAV_01": {"cavity.phase": 180}}


def test_pass_without_overrides_gets_an_empty_mapping(erl):
    assert all(p.overrides == {} for p in passes(erl, "INJECTOR"))


def test_overrides_do_not_touch_the_element(erl):
    """Carried, not applied -- L7 applies them at export."""
    assert erl.elements["CAV_01"].cavity.phase == 0.0


def test_overrides_are_independent_per_pass(erl):
    first, second = passes(erl, "LINAC")
    second.overrides["CAV_01"]["cavity.phase"] = 90
    assert first.overrides == {}


def test_several_elements_and_paths_survive():
    overrides = {
        "CAV_01": {"cavity.phase": 180, "physical.length": 0.6},
        "LIN_Q": {"magnetic.k1l": -1.0},
    }
    _, second = passes(machine(second_pass(overrides)), "LINAC")
    assert second.overrides == overrides


def test_overrides_ride_alongside_direction():
    model = machine(second_pass({"CAV_01": {"cavity.phase": 180}}, direction=-1))
    _, second = passes(model, "LINAC")
    assert second.direction == -1
    assert second.overrides == {"CAV_01": {"cavity.phase": 180}}


@pytest.mark.parametrize(
    "overrides, match",
    [
        pytest.param(
            {"NOPE": {"cavity.phase": 1}},
            "contains no such element",
            id="unknown-element",
        ),
        # The override is scoped to the section this pass traverses.
        pytest.param(
            {"ARC_B": {"magnetic.k1l": 1.0}},
            "contains no such element",
            id="element-in-another-section",
        ),
        pytest.param(
            {"CAV_01": {"cavity.nonsense": 1}}, "no such attribute", id="unknown-path"
        ),
        # A cavity has no magnetic strength, however plausible the path reads.
        pytest.param(
            {"CAV_01": {"magnetic.k1l": 1.0}},
            "no such attribute",
            id="wrong-attribute-for-the-type",
        ),
    ],
)
def test_a_target_that_does_not_exist_is_refused(overrides, match):
    with pytest.raises(ValueError, match=match):
        machine(second_pass(overrides))


PHASE_180 = {"CAV_01": {"cavity.phase": 180}}


@pytest.mark.parametrize(
    "layout",
    [
        # A single traversal has an element of its own to carry the value.
        pytest.param(
            ["INJECTOR", {"LINAC": {"overrides": PHASE_180}}, "ARC", "DUMP"],
            id="without-multipass",
        ),
        # Repetition gives each occurrence its own deep copy to write on.
        pytest.param(
            ["INJECTOR", "LINAC", "ARC", {"LINAC": {"overrides": PHASE_180}}, "DUMP"],
            id="on-a-repetition-occurrence",
        ),
    ],
)
def test_overrides_off_a_multipass_pass_are_refused(layout):
    with pytest.raises(ValueError, match="does not mark it 'multipass'"):
        machine(layout)


@pytest.mark.parametrize(
    "overrides",
    [
        ["CAV_01", "cavity.phase"],  # not a mapping at all
        "CAV_01.cavity.phase",
        {"CAV_01": 180},  # element name straight to a value, no path
        {"CAV_01": ["cavity.phase", 180]},
    ],
)
def test_malformed_overrides_are_refused(overrides):
    with pytest.raises(TypeError, match="overrides"):
        machine(second_pass(overrides))


def test_unknown_entry_option_is_still_refused():
    with pytest.raises(TypeError, match="'overrides'"):
        machine(
            [
                "INJECTOR",
                {"LINAC": {"multipass": 1}},
                "ARC",
                {"LINAC": {"multipass": 2, "overides": {}}},  # typo
                "DUMP",
            ]
        )


def test_path_without_overrides_is_unchanged():
    model = machine(["INJECTOR", "LINAC", "ARC", "DUMP"])
    assert [p.overrides for p in model.lattices["ERL"].passes] == [{}] * 4
