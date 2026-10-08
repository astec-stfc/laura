"""Per-pass strength resolution: a multipass magnet holds one field, so its
normalised ``k_n = q*B^(n)/p`` differs on every pass.
"""

import math

import pytest

from laura.models.element import RFCavity
from laura.models.elementList import MachineModel
from laura.models.exceptions import LatticeError
from laura.models.magnetic import Dipole_Magnet, brho
from unit_tests.helpers import quad, quiet

SECTIONS = {
    "INJECTOR": ["INJ_Q"],
    "LINAC": ["CAV_01", "LIN_Q"],
    "ARC": ["ARC_B"],
    "DUMP": ["DMP_Q"],
}

P1 = 100e6  # eV/c on the accelerating pass
P2 = 200e6  # eV/c on the return pass -- twice the energy, half the k


def two_passes(first, second):
    """The ERL path, with *first* and *second* added to the two LINAC entries."""
    return [
        "INJECTOR",
        {"LINAC": {"multipass": 1, **first}},
        "ARC",
        {"LINAC": {"multipass": 2, **second}},
        "DUMP",
    ]


ERL = two_passes({"momentum": P1}, {"momentum": P2})


def elements(gradient=None):
    built = {
        name: quad(name, length, 1.0, "A")
        for name, length in (
            ("INJ_Q", 0.2),
            ("LIN_Q", 0.4),
            ("ARC_B", 0.4),
            ("DMP_Q", 0.2),
        )
    }
    if gradient is not None:
        built["LIN_Q"].magnetic.gradient = gradient
    # A cavity has no magnetic model at all, so it must not appear.
    built["CAV_01"] = RFCavity(
        name="CAV_01",
        machine_area="A",
        physical={"length": 0.6},
        cavity={"phase": 0.0},
    )
    return built


def machine(layout, gradient=None):
    with quiet():
        return MachineModel(
            elements=elements(gradient),
            section={"sections": SECTIONS},
            layout={"layouts": {"ERL": layout}, "default_layout": "ERL"},
        )


@pytest.fixture
def erl():
    return machine(ERL)


def test_pass_one_is_the_reference(erl):
    assert erl.lattices["ERL"].pass_strengths(1) == {"LIN_Q": pytest.approx(1.0)}


def test_doubling_the_momentum_halves_the_strength(erl):
    """k = qG/p, so twice the energy through one magnet is half the k."""
    assert erl.lattices["ERL"].pass_strengths(2)["LIN_Q"] == pytest.approx(0.5)


def test_the_scaling_is_the_rigidity_ratio(erl):
    layout = erl.lattices["ERL"]
    assert layout.pass_strengths(2)["LIN_Q"] == pytest.approx(
        1.0 * brho(P1) / brho(P2)
    )


def test_the_field_is_what_stays_fixed(erl):
    layout = erl.lattices["ERL"]
    magnet = erl["LIN_Q"].magnetic
    field_1 = layout.pass_strengths(1)["LIN_Q"] * brho(P1) / magnet.length
    field_2 = layout.pass_strengths(2)["LIN_Q"] * brho(P2) / magnet.length
    assert field_1 == pytest.approx(field_2)


def test_resolved_strength_inverts_get_gradient(erl):
    layout = erl.lattices["ERL"]
    magnet = erl["LIN_Q"].magnetic
    expected = magnet.get_gradient(P1)
    magnet.kl = layout.pass_strengths(2)["LIN_Q"]
    assert magnet.get_gradient(P2) == pytest.approx(expected)


def test_an_explicit_gradient_is_used_directly():
    """A stated field is pass-invariant, so it needs no reference."""
    layout = machine(ERL, gradient=0.35).lattices["ERL"]
    for number, momentum in ((1, P1), (2, P2)):
        assert layout.pass_strengths(number)["LIN_Q"] == pytest.approx(
            0.35 * 0.4 / brho(momentum)
        )


def test_a_stated_gradient_still_holds_one_field():
    layout = machine(ERL, gradient=0.35).lattices["ERL"]
    lengths = 0.4
    fields = [
        layout.pass_strengths(n)[name] * brho(p) / lengths
        for n, p in ((1, P1), (2, P2))
        for name in ["LIN_Q"]
    ]
    assert fields[0] == pytest.approx(fields[1]) == pytest.approx(0.35)


def test_only_the_traversed_section_is_reported(erl):
    assert set(erl.lattices["ERL"].pass_strengths(2)) == {"LIN_Q"}


def test_non_magnetic_elements_are_skipped(erl):
    assert "CAV_01" not in erl.lattices["ERL"].pass_strengths(1)


def test_names_are_bare(erl):
    """A pass is already one traversal; there is nothing to disambiguate."""
    assert not any("#" in name for name in erl.lattices["ERL"].pass_strengths(2))


def test_a_single_pass_path_is_refused():
    layout = machine(["INJECTOR", "LINAC", "ARC", "DUMP"]).lattices["ERL"]
    with pytest.raises(LatticeError, match="not multipass"):
        layout.pass_strengths(1)


def test_an_unknown_pass_number_is_refused(erl):
    with pytest.raises(LatticeError, match="no pass 3"):
        erl.lattices["ERL"].pass_strengths(3)


def test_multipass_without_momentum_is_refused():
    """Returning the stored value would quietly claim the passes are identical."""
    layout = machine(two_passes({}, {})).lattices["ERL"]
    with pytest.raises(LatticeError, match="states no 'momentum'"):
        layout.pass_strengths(2)


def test_momentum_on_only_some_passes_is_refused():
    with pytest.raises(ValueError, match="every pass, or on none"):
        machine(two_passes({"momentum": P1}, {}))


@pytest.mark.parametrize(
    "layout",
    [
        pytest.param(
            ["INJECTOR", {"LINAC": {"momentum": P1}}, "ARC", "DUMP"],
            id="without-multipass",
        ),
        pytest.param(
            [
                "INJECTOR",
                {"LINAC": {"momentum": P1}},
                "ARC",
                {"LINAC": {"momentum": P2}},
                "DUMP",
            ],
            id="on-a-repetition-occurrence",
        ),
    ],
)
def test_momentum_off_a_multipass_pass_is_refused(layout):
    with pytest.raises(ValueError, match="does not mark it 'multipass'"):
        machine(layout)


@pytest.mark.parametrize("momentum", [0, -100e6, "abc", True, [100e6]])
def test_a_non_positive_or_non_numeric_momentum_is_refused(momentum):
    with pytest.raises(ValueError, match="momentum"):
        machine(two_passes({"momentum": momentum}, {"momentum": P2}))


@pytest.mark.parametrize("momentum", ["100e6", "1.0e+8", 100_000_000])
def test_a_numeric_momentum_is_coerced(momentum):
    """PyYAML hands over ``100.0e6`` as a string."""
    layout = machine(two_passes({"momentum": momentum}, {"momentum": P2})).lattices[
        "ERL"
    ]
    assert layout.passes[1].momentum == pytest.approx(P1)
    assert layout.pass_strengths(2)["LIN_Q"] == pytest.approx(0.5)


# Multi-turn ERL: LINAC and ARC both have a pass 2, so a pass number can be ambiguous.

TURNS = [
    "INJECTOR",
    {"LINAC": {"multipass": 1, "momentum": P1}},
    {"ARC": {"multipass": 1, "momentum": P1}},
    {"LINAC": {"multipass": 2, "momentum": P2}},
    {"ARC": {"multipass": 2, "momentum": P2}},
    {"LINAC": {"multipass": 3, "momentum": P1}},
    "DUMP",
]


@pytest.fixture
def multi_turn():
    return machine(TURNS).lattices["ERL"]


@pytest.mark.parametrize(
    "match",
    [
        pytest.param("Name the section as well", id="refused"),
        pytest.param(r"\['ARC', 'LINAC'\]", id="names-both-sections"),
    ],
)
def test_an_ambiguous_pass_number_is_refused(multi_turn, match):
    with pytest.raises(LatticeError, match=match):
        multi_turn.pass_strengths(2)


def test_naming_the_section_resolves_it(multi_turn):
    assert multi_turn.pass_strengths(2, "LINAC") == {"LIN_Q": pytest.approx(0.5)}
    assert multi_turn.pass_strengths(2, "ARC") == {"ARC_B": pytest.approx(0.5)}


def test_each_section_scales_against_its_own_first_pass(multi_turn):
    assert multi_turn.pass_strengths(1, "LINAC") == {"LIN_Q": pytest.approx(1.0)}
    assert multi_turn.pass_strengths(1, "ARC") == {"ARC_B": pytest.approx(1.0)}


def test_the_arc_holds_one_field_across_its_passes(multi_turn):
    fields = [
        multi_turn.pass_strengths(n, "ARC")["ARC_B"] * brho(p) / 0.4
        for n, p in ((1, P1), (2, P2))
    ]
    assert fields[0] == pytest.approx(fields[1])


def test_a_number_unambiguous_on_its_own_still_needs_no_section(multi_turn):
    """Only LINAC makes a third pass, so 3 is unambiguous."""
    assert multi_turn.pass_strengths(3) == {"LIN_Q": pytest.approx(1.0)}


def test_a_pass_number_that_section_does_not_make_is_refused(multi_turn):
    with pytest.raises(LatticeError, match="no pass 3 of section 'ARC'"):
        multi_turn.pass_strengths(3, "ARC")


# A reversed pass sees every normal multipole sign-flipped (via `reverse_element`).


def reversed_second_pass(momentum=P1):
    second = {"momentum": momentum, "direction": -1}
    return machine(two_passes({"momentum": P1}, second)).lattices["ERL"]


def test_a_reversed_pass_flips_a_normal_multipole():
    assert reversed_second_pass().pass_strengths(2) == {"LIN_Q": pytest.approx(-1.0)}


def test_a_forward_pass_at_the_same_momentum_does_not():
    """Isolates the sign from the scaling."""
    assert reversed_second_pass().pass_strengths(1) == {"LIN_Q": pytest.approx(1.0)}


def test_reversal_and_rigidity_scaling_compose():
    assert reversed_second_pass(P2).pass_strengths(2) == {
        "LIN_Q": pytest.approx(-0.5)
    }


def test_a_reversed_pass_still_holds_one_field_magnitude():
    """Only the frame the beam reads it in has changed."""
    layout = reversed_second_pass(P2)
    magnitudes = [
        abs(layout.pass_strengths(n)["LIN_Q"]) * brho(p) / 0.4
        for n, p in ((1, P1), (2, P2))
    ]
    assert magnitudes[0] == pytest.approx(magnitudes[1])


# `get_element` returns the shared device; simba needs a per-pass copy.


def test_element_on_pass_applies_that_passs_strength(erl):
    layout = erl.lattices["ERL"]
    assert layout.element_on_pass("LIN_Q#1").magnetic.KnL(1) == pytest.approx(1.0)
    assert layout.element_on_pass("LIN_Q#2").magnetic.KnL(1) == pytest.approx(0.5)


def test_element_on_pass_applies_overrides():
    second = {"momentum": P2, "overrides": {"CAV_01": {"cavity.phase": 180.0}}}
    layout = machine(two_passes({"momentum": P1}, second)).lattices["ERL"]
    assert layout.element_on_pass("CAV_01#1").cavity.phase == pytest.approx(0.0)
    assert layout.element_on_pass("CAV_01#2").cavity.phase == pytest.approx(180.0)


def test_element_on_pass_names_it_as_export_would(erl):
    assert erl.lattices["ERL"].element_on_pass("LIN_Q#2").name == "LIN_Q.2"


def test_element_on_pass_returns_independent_copies(erl):
    layout = erl.lattices["ERL"]
    first, second = (layout.element_on_pass(f"LIN_Q#{n}") for n in (1, 2))
    assert first is not second
    first.magnetic.kl = 99.0
    assert second.magnetic.KnL(1) == pytest.approx(0.5)


def test_element_on_pass_leaves_the_shared_device_alone(erl):
    erl.lattices["ERL"].element_on_pass("LIN_Q#2")
    assert erl["LIN_Q"].magnetic.KnL(1) == pytest.approx(1.0)


@pytest.mark.parametrize("name", ["LIN_Q", "LIN_Q#9", "NOPE#1"])
def test_element_on_pass_returns_none_when_it_cannot_answer(erl, name):
    """So a caller can fall back to the shared device."""
    assert erl.lattices["ERL"].element_on_pass(name) is None


def test_a_ring_needs_no_momentum_and_is_untouched():
    """A booster ramps B and p together, so its stored k is already invariant."""
    model = machine(["INJECTOR", "LINAC", "ARC", "DUMP"])
    layout = model.lattices["ERL"]
    assert layout.is_multipass is False
    assert all(entry.momentum is None for entry in layout.passes)


def test_dipole_field_strength_is_brho_over_rho():
    """``field_strength`` is the dipole's ``get_gradient``: B = Brho/rho."""
    angle, length, momentum = math.radians(30), 1.0, 240e6
    dipole = Dipole_Magnet(length=length, magnet_type="dipole", k0l=angle)
    assert dipole.field_strength(momentum) == pytest.approx(
        brho(momentum) / dipole.rho
    )
    # ... which is the same relation get_gradient uses, at order 0.
    assert dipole.field_strength(momentum) == pytest.approx(
        dipole.KnL(0) * brho(momentum) / length
    )


def test_dipole_field_strength_handles_a_zero_angle():
    straight = Dipole_Magnet(length=1.0, magnet_type="dipole", k0l=0.0)
    assert straight.field_strength(240e6) == 0.0
