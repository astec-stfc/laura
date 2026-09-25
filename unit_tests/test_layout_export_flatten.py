"""Tier-1 multipass export: one exported section per traversal.

``MachineLayoutTranslator.sections`` is name-keyed and every backend body
iterates it, so a path that enters one section twice has to become a set of
*distinct* sections before any of them sees it. Each pass gets its own deep
copy, suffixed ``.N``, carrying the values that pass sees.

The oracle throughout is the same one §2 of the scope doc established for the
model: **a multipass path and the repetition reading of the same file must
agree**. Here that is sharpened -- they must emit byte-identical section and
element names, so the two readings of one lattice can be diffed against each
other. Only what the author declared to differ per pass may differ.
"""

import warnings

import pytest

from laura.models.element import Quadrupole, RFCavity
from laura.models.elementList import MachineModel
from laura.translator.converters.layout import MachineLayoutTranslator

P1, P2 = 100e6, 200e6

SECTIONS = {
    "INJECTOR": ["INJ_Q"],
    # DRIFT repeated inside the section, so an element carries a repeat index
    # *and* a pass number -- the case where the two numbering schemes meet.
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
        name: Quadrupole(
            name=name,
            hardware_class="Magnet",
            machine_area="A",
            magnetic={"magnetic_length": 0.2, "k1l": 1.0},
            physical={"length": 0.2},
        )
        for name in ("INJ_Q", "LIN_Q", "ARC_Q", "DMP_Q")
    }
    built["DRIFT"] = Quadrupole(
        name="DRIFT",
        hardware_class="Magnet",
        machine_area="A",
        magnetic={"magnetic_length": 0.1, "k1l": 0.0},
        physical={"length": 0.1},
    )
    built["CAV_01"] = RFCavity(
        name="CAV_01",
        machine_area="A",
        physical={"length": 0.5},
        cavity={"frequency": 1.3e9, "phase": 0.0},
    )
    return built


def exported(layout):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        model = MachineModel(
            elements=elements(),
            section={"sections": SECTIONS},
            layout={"layouts": {"ERL": layout}, "default_layout": "ERL"},
        )
    return MachineLayoutTranslator.from_layout(model.lattices["ERL"])


@pytest.fixture
def flat():
    return exported(MULTIPASS)


# --- one section per traversal ------------------------------------------


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
    """``#`` addresses a pass but is not a legal name in elegant or MAD-X,
    and ``sanitize_string`` only rewrites hyphens, so it would reach the
    file intact and break it."""
    for section in flat.sections.values():
        assert "#" not in section.name
        assert not any("#" in name for name in section.order)


# --- the oracle: identical to the repetition reading --------------------


def test_section_names_match_the_repetition_reading(flat):
    assert list(flat.sections) == list(exported(REPETITION).sections)


def test_element_names_match_the_repetition_reading(flat):
    repetition = exported(REPETITION)
    for name, section in flat.sections.items():
        assert section.order == repetition.sections[name].order, name


def test_the_pass_number_precedes_a_repeat_index(flat):
    """``DRIFT.1.2`` is occurrence 1, drift 2 -- in both readings.

    Appending instead gave ``DRIFT.2.1``, a name repetition also emits and
    means something else by. Two readings of one lattice must not disagree
    about what a name denotes.
    """
    assert "DRIFT.1.2" in flat.sections["LINAC.1"].order
    assert "DRIFT.2.1" in flat.sections["LINAC.2"].order


# --- what the pass sees -------------------------------------------------


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
    """The author's explicit statement is applied last."""
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
    """Export is a view. The passes share one device in the model."""
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        model = MachineModel(
            elements=elements(),
            section={"sections": SECTIONS},
            layout={"layouts": {"ERL": MULTIPASS}, "default_layout": "ERL"},
        )
    MachineLayoutTranslator.from_layout(model.lattices["ERL"])
    assert model["LIN_Q"].magnetic.KnL(1) == pytest.approx(1.0)
    assert model["CAV_01"].cavity.phase == pytest.approx(0.0)


def test_the_passes_do_not_share_element_objects(flat):
    first = flat.sections["LINAC.1"].elements.elements["LIN_Q.1"]
    second = flat.sections["LINAC.2"].elements.elements["LIN_Q.2"]
    assert first is not second
    first.magnetic.kl = 99.0
    assert second.magnetic.KnL(1) == pytest.approx(0.5)


# --- a reversed pass ----------------------------------------------------


def test_a_reversed_pass_is_reversed_and_scaled():
    layout = list(MULTIPASS)
    layout[3] = {"LINAC": {"multipass": 2, "momentum": P2, "direction": -1}}
    section = exported(layout).sections["LINAC.2"]
    assert section.order == ["LIN_Q.2", "DRIFT.2.2", "CAV_01.2", "DRIFT.2.1"]
    # reverse_section flips the normal multipole, pass_strengths sets the
    # final value: one negation, not two.
    assert section.elements.elements["LIN_Q.2"].magnetic.KnL(1) == pytest.approx(-0.5)


# --- backends, which need no changes at all -----------------------------


def test_elegant_emits_one_line_per_pass(flat):
    out = str(flat.to_elegant()).replace("&\n", "")
    for name in ("INJECTOR", "LINAC.1", "ARC", "LINAC.2", "DUMP"):
        assert f"{name}: LINE = (" in out


def test_elegant_defines_each_pass_separately(flat):
    out = str(flat.to_elegant()).replace("&\n", "")
    assert "LIN_Q.1: quad" in out
    assert "LIN_Q.2: quad" in out


def test_a_single_pass_layout_exports_as_before():
    """Nothing without ``multipass:`` may change shape."""
    plain = exported(["INJECTOR", "ARC", "DUMP"])
    assert list(plain.sections) == ["INJECTOR", "ARC", "DUMP"]
    assert plain.sections["ARC"].order == ["ARC_Q"]
