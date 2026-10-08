"""Multipass export: one ``.N``-suffixed section copy per traversal.

Names must match the plain-repetition reading of the same layout exactly.
"""

import pytest

from laura.models.element import RFCavity
from laura.models.elementList import MachineModel
from laura.translator.converters.layout import MachineLayoutTranslator
from unit_tests.helpers import quad, quiet

P1, P2 = 100e6, 200e6

SECTIONS = {
    "INJECTOR": ["INJ_Q"],
    # DRIFT gets both a repeat index and a pass number
    "LINAC": ["DRIFT", "CAV_01", "DRIFT", "LIN_Q"],
    "ARC": ["ARC_Q"],
    "DUMP": ["DMP_Q"],
}

MULTIPASS = [
    "INJECTOR",
    {"LINAC": {"multipass": 1, "momentum": P1}},
    "ARC",
    {
        "LINAC": {
            "multipass": 2,
            "momentum": P2,
            "overrides": {"CAV_01": {"cavity.phase": 180.0}},
        }
    },
    "DUMP",
]

REPETITION = ["INJECTOR", "LINAC", "ARC", "LINAC", "DUMP"]


def elements():
    built = {
        name: quad(name, 0.2, 1.0, "A") for name in ("INJ_Q", "LIN_Q", "ARC_Q", "DMP_Q")
    }
    built["DRIFT"] = quad("DRIFT", 0.1, 0.0, "A")
    built["CAV_01"] = RFCavity(
        name="CAV_01",
        machine_area="A",
        physical={"length": 0.5},
        cavity={"frequency": 1.3e9, "phase": 0.0},
    )
    return built


def machine(layout):
    with quiet():
        return MachineModel(
            elements=elements(),
            section={"sections": SECTIONS},
            layout={"layouts": {"ERL": layout}, "default_layout": "ERL"},
        )


def exported(layout):
    return MachineLayoutTranslator.from_layout(machine(layout).lattices["ERL"])


@pytest.fixture
def flat():
    return exported(MULTIPASS)


def test_every_pass_gets_its_own_section(flat):
    assert list(flat.sections) == [
        "INJECTOR",
        "LINAC.1",
        "ARC",
        "LINAC.2",
        "DUMP",
    ]


def test_a_section_entered_once_keeps_its_name(flat):
    assert "ARC" in flat.sections
    assert flat.sections["ARC"].order == ["ARC_Q"]


def test_elements_are_pass_numbered(flat):
    assert flat.sections["LINAC.1"].order == [
        "DRIFT.1.1",
        "CAV_01.1",
        "DRIFT.1.2",
        "LIN_Q.1",
    ]


def test_no_name_is_shared_between_passes(flat):
    first = set(flat.sections["LINAC.1"].order)
    assert first.isdisjoint(flat.sections["LINAC.2"].order)


def test_names_carry_no_hash(flat):
    """``#`` is illegal in elegant/MAD-X names and ``sanitize_string`` keeps it."""
    for section in flat.sections.values():
        assert "#" not in section.name
        assert not any("#" in name for name in section.order)


def test_section_names_match_the_repetition_reading(flat):
    assert list(flat.sections) == list(exported(REPETITION).sections)


def test_element_names_match_the_repetition_reading(flat):
    repetition = exported(REPETITION)
    for name, section in flat.sections.items():
        assert section.order == repetition.sections[name].order, name


def test_the_pass_number_precedes_a_repeat_index(flat):
    """``DRIFT.1.2`` is pass 1, drift 2, as in the repetition reading."""
    assert "DRIFT.1.2" in flat.sections["LINAC.1"].order
    assert "DRIFT.2.1" in flat.sections["LINAC.2"].order


def test_each_pass_carries_its_own_strength(flat):
    first = flat.sections["LINAC.1"].elements.elements["LIN_Q.1"]
    second = flat.sections["LINAC.2"].elements.elements["LIN_Q.2"]
    assert first.magnetic.KnL(1) == pytest.approx(1.0)
    assert second.magnetic.KnL(1) == pytest.approx(0.5)


def test_each_pass_carries_its_own_override(flat):
    first = flat.sections["LINAC.1"].elements.elements["CAV_01.1"]
    second = flat.sections["LINAC.2"].elements.elements["CAV_01.2"]
    assert first.cavity.phase == pytest.approx(0.0)
    assert second.cavity.phase == pytest.approx(180.0)


def test_an_override_wins_over_a_derived_strength():
    layout = list(MULTIPASS)
    layout[3] = {
        "LINAC": {
            "multipass": 2,
            "momentum": P2,
            "overrides": {"LIN_Q": {"magnetic.k1l": 7.0}},
        }
    }
    section = exported(layout).sections["LINAC.2"]
    assert section.elements.elements["LIN_Q.2"].magnetic.KnL(1) == pytest.approx(7.0)


def test_the_source_model_is_untouched():
    model = machine(MULTIPASS)
    MachineLayoutTranslator.from_layout(model.lattices["ERL"])
    assert model["LIN_Q"].magnetic.KnL(1) == pytest.approx(1.0)
    assert model["CAV_01"].cavity.phase == pytest.approx(0.0)


def test_the_passes_do_not_share_element_objects(flat):
    first = flat.sections["LINAC.1"].elements.elements["LIN_Q.1"]
    second = flat.sections["LINAC.2"].elements.elements["LIN_Q.2"]
    assert first is not second
    first.magnetic.kl = 99.0
    assert second.magnetic.KnL(1) == pytest.approx(0.5)


def test_a_reversed_pass_is_reversed_and_scaled():
    layout = list(MULTIPASS)
    layout[3] = {"LINAC": {"multipass": 2, "momentum": P2, "direction": -1}}
    section = exported(layout).sections["LINAC.2"]
    assert section.order == ["LIN_Q.2", "DRIFT.2.2", "CAV_01.2", "DRIFT.2.1"]
    # one negation, not two: reverse_section flips, pass_strengths sets the value
    assert section.elements.elements["LIN_Q.2"].magnetic.KnL(1) == pytest.approx(-0.5)


def test_elegant_emits_one_line_per_pass(flat):
    out = str(flat.to_elegant()).replace("&\n", "")
    for name in ("INJECTOR", "LINAC.1", "ARC", "LINAC.2", "DUMP"):
        assert f"{name}: LINE = (" in out


def test_elegant_defines_each_pass_separately(flat):
    out = str(flat.to_elegant()).replace("&\n", "")
    assert "LIN_Q.1: quad" in out
    assert "LIN_Q.2: quad" in out


def test_a_single_pass_layout_exports_as_before():
    plain = exported(["INJECTOR", "ARC", "DUMP"])
    assert list(plain.sections) == ["INJECTOR", "ARC", "DUMP"]
    assert plain.sections["ARC"].order == ["ARC_Q"]
