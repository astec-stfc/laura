"""Arc length along a *beam path*, as opposed to within a section.

An element carries one ``s``, resolved in its own section's frame, and that is
the right place to store it -- the magnet is installed once.  But placement runs
per section and a sequentially-placed section starts at its own ``s = 0``,
because the same section may sit after different predecessors in different
layouts.  Two such sections in one layout therefore both begin at the origin.

:meth:`MachineLayout.arc_lengths` is the view that resolves that: one offset per
section, plus an optional flip for a section the path runs backwards through.
It mutates nothing, so one section can report different arc lengths to different
beam paths.
"""

import warnings

import pytest

from laura.models.element import Drift
from laura.models.elementList import LatticeError, MachineModel


def drift(name, length, **physical):
    return Drift(
        name=name,
        hardware_class="Drift",
        machine_area="S",
        physical={"length": length, **physical},
    )


def machine(elements, sections, layout=("A", "B")):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        return MachineModel(
            elements={e.name: e for e in elements},
            section={"sections": sections},
            layout={"layouts": {"L": list(layout)}, "default_layout": "L"},
        )


@pytest.fixture
def sequential():
    """A = two 1 m drifts, B = two 2 m drifts. Nothing states a position."""
    return machine(
        [drift("a1", 1.0), drift("a2", 1.0), drift("b1", 2.0), drift("b2", 2.0)],
        {"A": ["a1", "a2"], "B": ["b1", "b2"]},
    )


@pytest.fixture
def absolute():
    """The same shape, but every element states where it is."""
    return machine(
        [
            drift("a1", 1.0, s=1.0, s_point="end"),
            drift("a2", 1.0, s=2.0, s_point="end"),
            drift("b1", 2.0, s=12.0, s_point="end"),
            drift("b2", 2.0, s=14.0, s_point="end"),
        ],
        {"A": ["a1", "a2"], "B": ["b1", "b2"]},
    )


class TestSequentialSectionsChain:
    def test_they_both_start_at_the_origin_when_stored(self, sequential):
        # the thing the view exists to fix: B's own frame restarts at zero
        assert sequential.elements["a1"].physical.s == pytest.approx(0.5)
        assert sequential.elements["b1"].physical.s == pytest.approx(1.0)

    def test_the_path_chains_them(self, sequential):
        assert sequential.lattices["L"].arc_lengths() == pytest.approx(
            {"a1": 0.0, "a2": 1.0, "b1": 2.0, "b2": 4.0}
        )

    def test_the_path_is_as_long_as_its_sections(self, sequential):
        lengths = sequential.lattices["L"].arc_lengths()
        assert lengths["b2"] + 2.0 == pytest.approx(1.0 + 1.0 + 2.0 + 2.0)

    def test_nothing_is_mutated(self, sequential):
        before = {n: e.physical.s for n, e in sequential.elements.items()}
        sequential.lattices["L"].arc_lengths()
        assert {n: e.physical.s for n, e in sequential.elements.items()} == before

    def test_one_section_is_unchanged_from_its_stored_entrances(self):
        single = machine(
            [drift("a1", 1.0), drift("a2", 1.0)], {"A": ["a1", "a2"]}, layout=("A",)
        )
        assert single.lattices["L"].arc_lengths() == pytest.approx(
            {"a1": 0.0, "a2": 1.0}
        )


class TestStatedPositionsAreNotShifted:
    """A surveyed machine's ``s`` is already global; chaining it would be wrong."""

    def test_they_keep_their_own_arc_lengths(self, absolute):
        assert absolute.lattices["L"].arc_lengths() == pytest.approx(
            {"a1": 0.0, "a2": 1.0, "b1": 10.0, "b2": 12.0}
        )

    def test_the_gap_between_sections_survives(self, absolute):
        lengths = absolute.lattices["L"].arc_lengths()
        assert lengths["b1"] - (lengths["a2"] + 1.0) == pytest.approx(8.0)

    def test_a_sequential_section_chains_from_a_stated_one(self):
        mixed = machine(
            [drift("a1", 1.0, s=10.0, s_point="end"), drift("b1", 2.0)],
            {"A": ["a1"], "B": ["b1"]},
        )
        # A occupies 9..10, so B starts at 10
        assert mixed.lattices["L"].arc_lengths() == pytest.approx(
            {"a1": 9.0, "b1": 10.0}
        )


class TestReversedSections:
    def test_a_reversed_section_flips_within_its_own_extent(self, sequential):
        lengths = sequential.lattices["L"].arc_lengths(direction={"B": -1})
        # B occupies 2..6 either way; b2 is met first going backwards
        assert lengths == pytest.approx({"a1": 0.0, "a2": 1.0, "b1": 4.0, "b2": 2.0})

    def test_the_unreversed_section_is_untouched(self, sequential):
        forward = sequential.lattices["L"].arc_lengths()
        reversed_ = sequential.lattices["L"].arc_lengths(direction={"B": -1})
        assert forward["a1"] == reversed_["a1"]
        assert forward["a2"] == reversed_["a2"]

    def test_a_reversed_call_does_not_poison_the_next_forward_one(self, sequential):
        # the view reads mutable models, so purity is worth pinning
        layout = sequential.lattices["L"]
        before = layout.arc_lengths()
        layout.arc_lengths(direction={"A": -1, "B": -1})
        assert layout.arc_lengths() == pytest.approx(before)

    def test_a_reversed_section_covers_the_same_span(self, sequential):
        forward = sequential.lattices["L"].arc_lengths()
        backward = sequential.lattices["L"].arc_lengths(direction={"B": -1})

        def span(lengths):
            return (
                min(lengths[n] for n in ("b1", "b2")),
                max(lengths[n] + 2.0 for n in ("b1", "b2")),
            )

        assert span(forward) == pytest.approx((2.0, 6.0))
        assert span(backward) == pytest.approx((2.0, 6.0))

    def test_a_positive_direction_is_the_default(self, sequential):
        layout = sequential.lattices["L"]
        assert layout.arc_lengths(direction={"B": 1}) == pytest.approx(
            layout.arc_lengths()
        )

    def test_reversing_every_section_reverses_the_path_order(self, sequential):
        lengths = sequential.lattices["L"].arc_lengths(direction={"A": -1, "B": -1})
        assert lengths == pytest.approx({"a1": 1.0, "a2": 0.0, "b1": 4.0, "b2": 2.0})

    def test_an_unknown_section_is_refused(self, sequential):
        with pytest.raises(LatticeError, match="no section"):
            sequential.lattices["L"].arc_lengths(direction={"NOPE": -1})


class TestSharedElements:
    def test_an_element_in_two_sections_is_reported_once(self):
        shared = machine(
            [
                drift("a1", 1.0, s=1.0, s_point="end"),
                drift("b1", 2.0, s=3.0, s_point="end"),
            ],
            {"A": ["a1", "b1"], "B": ["b1"]},
        )
        lengths = shared.lattices["L"].arc_lengths()
        assert lengths == pytest.approx({"a1": 0.0, "b1": 1.0})
