"""``overrides`` on a layout entry: what differs between passes of one device.

A multipass section's passes share one element, so a value that differs per
pass has nowhere on the element to live -- there is only one of it. It lives
on :class:`~laura.models.elementList.LayoutPass` instead, which is the thing
there are N of.

L4 parses, checks and carries them. Nothing applies them yet: export flattens
a multipass path and applies them on the way out (L7), and rigidity resolution
reads a per-pass reference energy from them (L5). So these tests are about the
overrides arriving intact on the right pass, and about every way of naming a
target that does not exist being refused rather than silently doing nothing.
"""

import warnings

import pytest

from laura.models.element import Quadrupole, RFCavity
from laura.models.elementList import MachineModel

SECTIONS = {
    "INJECTOR": ["INJ_Q"],
    "LINAC": ["CAV_01", "LIN_Q"],
    "ARC": ["ARC_B"],
    "DUMP": ["DMP_Q"],
}

# The decelerating return leg of an ERL: same cavity, ~180 degrees apart.
ERL = [
    "INJECTOR",
    {"LINAC": {"multipass": 1}},
    "ARC",
    {"LINAC": {"multipass": 2, "overrides": {"CAV_01": {"cavity.phase": 180}}}},
    "DUMP",
]


def elements():
    built = {
        name: Quadrupole(
            name=name,
            hardware_class="Magnet",
            machine_area="A",
            magnetic={"magnetic_length": length, "k1l": 1.0},
            physical={"length": length},
        )
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


def machine(layout, sections=None):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        return MachineModel(
            elements=elements(),
            section={"sections": sections or SECTIONS},
            layout={"layouts": {"ERL": layout}, "default_layout": "ERL"},
        )


@pytest.fixture
def erl():
    return machine(ERL)


def passes(model, section):
    return [p for p in model.lattices["ERL"].passes if p.section == section]


# --- carried, on the pass that stated them -------------------------------


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
    """Two passes' overrides must not be the same dict object."""
    first, second = passes(erl, "LINAC")
    second.overrides["CAV_01"]["cavity.phase"] = 90
    assert first.overrides == {}


def test_several_elements_and_paths_survive():
    model = machine(
        [
            "INJECTOR",
            {"LINAC": {"multipass": 1}},
            "ARC",
            {
                "LINAC": {
                    "multipass": 2,
                    "overrides": {
                        "CAV_01": {"cavity.phase": 180, "physical.length": 0.6},
                        "LIN_Q": {"magnetic.k1l": -1.0},
                    },
                }
            },
            "DUMP",
        ]
    )
    _, second = passes(model, "LINAC")
    assert second.overrides == {
        "CAV_01": {"cavity.phase": 180, "physical.length": 0.6},
        "LIN_Q": {"magnetic.k1l": -1.0},
    }


def test_overrides_ride_alongside_direction():
    model = machine(
        [
            "INJECTOR",
            {"LINAC": {"multipass": 1}},
            "ARC",
            {
                "LINAC": {
                    "multipass": 2,
                    "direction": -1,
                    "overrides": {"CAV_01": {"cavity.phase": 180}},
                }
            },
            "DUMP",
        ]
    )
    _, second = passes(model, "LINAC")
    assert second.direction == -1
    assert second.overrides == {"CAV_01": {"cavity.phase": 180}}


# --- refused ------------------------------------------------------------


def test_unknown_element_is_refused():
    with pytest.raises(ValueError, match="contains no such element"):
        machine(
            [
                "INJECTOR",
                {"LINAC": {"multipass": 1}},
                "ARC",
                {"LINAC": {"multipass": 2, "overrides": {"NOPE": {"cavity.phase": 1}}}},
                "DUMP",
            ]
        )


def test_element_in_another_section_is_refused():
    """The override is scoped to the section this pass traverses."""
    with pytest.raises(ValueError, match="contains no such element"):
        machine(
            [
                "INJECTOR",
                {"LINAC": {"multipass": 1}},
                "ARC",
                {
                    "LINAC": {
                        "multipass": 2,
                        "overrides": {"ARC_B": {"magnetic.k1l": 1.0}},
                    }
                },
                "DUMP",
            ]
        )


def test_unknown_attribute_path_is_refused():
    with pytest.raises(ValueError, match="no such attribute"):
        machine(
            [
                "INJECTOR",
                {"LINAC": {"multipass": 1}},
                "ARC",
                {
                    "LINAC": {
                        "multipass": 2,
                        "overrides": {"CAV_01": {"cavity.nonsense": 1}},
                    }
                },
                "DUMP",
            ]
        )


def test_wrong_attribute_for_the_element_type_is_refused():
    """A cavity has no magnetic strength, however plausible the path reads."""
    with pytest.raises(ValueError, match="no such attribute"):
        machine(
            [
                "INJECTOR",
                {"LINAC": {"multipass": 1}},
                "ARC",
                {
                    "LINAC": {
                        "multipass": 2,
                        "overrides": {"CAV_01": {"magnetic.k1l": 1.0}},
                    }
                },
                "DUMP",
            ]
        )


def test_overrides_without_multipass_are_refused():
    """A single traversal has an element of its own to carry the value."""
    with pytest.raises(ValueError, match="does not mark it 'multipass'"):
        machine(
            [
                "INJECTOR",
                {"LINAC": {"overrides": {"CAV_01": {"cavity.phase": 180}}}},
                "ARC",
                "DUMP",
            ]
        )


def test_overrides_on_a_repetition_occurrence_are_refused():
    """Repetition gives each occurrence its own deep copy to write on."""
    with pytest.raises(ValueError, match="does not mark it 'multipass'"):
        machine(
            [
                "INJECTOR",
                "LINAC",
                "ARC",
                {"LINAC": {"overrides": {"CAV_01": {"cavity.phase": 180}}}},
                "DUMP",
            ]
        )


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
        machine(
            [
                "INJECTOR",
                {"LINAC": {"multipass": 1}},
                "ARC",
                {"LINAC": {"multipass": 2, "overrides": overrides}},
                "DUMP",
            ]
        )


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


# --- untouched ----------------------------------------------------------


def test_path_without_overrides_is_unchanged():
    model = machine(["INJECTOR", "LINAC", "ARC", "DUMP"])
    assert [p.overrides for p in model.lattices["ERL"].passes] == [{}] * 4
