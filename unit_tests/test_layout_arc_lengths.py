"""Arc length along a *beam path*, as opposed to within a section."""

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
    def test_the_stored_geometry_is_composed(self, sequential):
        # B is placed after A rather than back at the origin. Before
        # composition existed, b1 resolved to s = 1.0 and sat inside A.
        assert sequential.elements["a1"].physical.s == pytest.approx(0.5)
        assert sequential.elements["b1"].physical.s == pytest.approx(3.0)

    def test_the_sections_no_longer_overlap_in_space(self, sequential):
        a_exit = max(
            e.physical.middle.z + e.physical.length / 2
            for e in (sequential.elements[n] for n in ("a1", "a2"))
        )
        b_entrance = min(
            e.physical.middle.z - e.physical.length / 2
            for e in (sequential.elements[n] for n in ("b1", "b2"))
        )
        assert b_entrance >= a_exit - 1e-9

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


class TestLayoutDirectionSyntax:
    """``direction: -1`` on a layout's section reference.

    Direction belongs to the beam path, not the section: the same section can
    be traversed forwards by one layout and backwards by another.
    """

    def build(self, entries):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            return MachineModel(
                elements={
                    e.name: e
                    for e in (
                        drift("a1", 1.0),
                        drift("a2", 1.0),
                        drift("b1", 2.0),
                        drift("b2", 2.0),
                    )
                },
                section={"sections": {"A": ["a1", "a2"], "B": ["b1", "b2"]}},
                layout={"layouts": {"L": entries}, "default_layout": "L"},
            )

    def test_a_bare_name_is_forwards(self):
        assert self.build(["A", "B"]).lattices["L"]._direction == {}

    def test_a_marked_section_is_recorded(self):
        machine = self.build(["A", {"B": {"direction": -1}}])
        assert machine.lattices["L"]._direction == {"B": -1}

    def test_an_explicit_positive_direction_is_forwards(self):
        assert self.build(["A", {"B": {"direction": 1}}]).lattices["L"]._direction == {}

    def test_the_sections_are_still_built(self):
        machine = self.build(["A", {"B": {"direction": -1}}])
        assert list(machine.lattices["L"].sections) == ["A", "B"]

    def test_arc_lengths_uses_it_by_default(self):
        machine = self.build(["A", {"B": {"direction": -1}}])
        assert machine.lattices["L"].arc_lengths() == pytest.approx(
            {"a1": 0.0, "a2": 1.0, "b1": 4.0, "b2": 2.0}
        )

    def test_an_explicit_argument_overrides_it(self):
        machine = self.build(["A", {"B": {"direction": -1}}])
        assert machine.lattices["L"].arc_lengths(direction={}) == pytest.approx(
            {"a1": 0.0, "a2": 1.0, "b1": 2.0, "b2": 4.0}
        )

    @pytest.mark.parametrize("direction", [0, 2, -2, "backwards", None])
    def test_a_direction_that_is_not_plus_or_minus_one(self, direction):
        with pytest.raises(ValueError, match="must be 1 or -1"):
            self.build(["A", {"B": {"direction": direction}}])

    def test_an_unknown_option(self):
        with pytest.raises(TypeError, match="'direction'"):
            self.build(["A", {"B": {"reversed": True}}])

    @pytest.mark.parametrize("entry", [3, None, ["B"], {"B": 1, "A": 1}])
    def test_an_entry_that_is_neither_a_name_nor_a_name_with_options(self, entry):
        with pytest.raises(TypeError):
            self.build(["A", entry])


class TestComposition:
    """Chaining a layout's sequential sections into one frame.

    The oracle is :meth:`test_split_and_whole_place_identically`: the same
    lattice written as one section and as two must land in the same place,
    including through bends, where a mis-composed frame would show up at once.
    """

    SPEC = [
        ("A1", 0.1, 0.5),
        ("A2", 0.4, None),
        ("A3", 1.0, 0.3),
        ("B1", 0.5, None),
        ("B2", 0.2, -0.5),
        ("B3", 0.8, -0.2),
        ("B4", 0.3, None),
    ]

    def elements(self):
        from laura.models.element import Dipole, Quadrupole

        built = []
        for name, length, strength in self.SPEC:
            if strength is None:
                built.append(drift(name, length))
            elif name in ("A3", "B3"):
                built.append(
                    Dipole(
                        name=name,
                        hardware_class="Magnet",
                        machine_area="S",
                        magnetic={"magnetic_length": length, "k0l": strength},
                        physical={"length": length},
                    )
                )
            else:
                built.append(
                    Quadrupole(
                        name=name,
                        hardware_class="Magnet",
                        machine_area="S",
                        magnetic={"magnetic_length": length, "k1l": strength},
                        physical={"length": length},
                    )
                )
        return built

    def build(self, sections, layouts):
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            model = MachineModel(
                elements={e.name: e for e in self.elements()},
                section={"sections": sections},
                layout={"layouts": layouts, "default_layout": list(layouts)[0]},
            )
        return model, [str(w.message) for w in caught]

    @pytest.fixture
    def names(self):
        return [s[0] for s in self.SPEC]

    def test_split_and_whole_place_identically(self, names):
        whole, _ = self.build({"ALL": names}, {"L": ["ALL"]})
        split, _ = self.build({"A": names[:3], "B": names[3:]}, {"L": ["A", "B"]})
        for name in names:
            one, two = whole.elements[name].physical, split.elements[name].physical
            assert two.s == pytest.approx(one.s, abs=1e-12)
            assert two.middle.x == pytest.approx(one.middle.x, abs=1e-12)
            assert two.middle.z == pytest.approx(one.middle.z, abs=1e-12)

    def test_the_bend_rotation_carries_across_the_join(self, names):
        # B's elements must inherit A's exit orientation, not restart at +z
        split, _ = self.build({"A": names[:3], "B": names[3:]}, {"L": ["A", "B"]})
        assert split.elements["B1"].physical.rotation.theta != pytest.approx(0.0)

    def test_a_stated_section_is_not_moved(self):
        stated = [
            drift("s1", 1.0, s=10.0, s_point="end"),
            drift("q1", 1.0),
        ]
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            model = MachineModel(
                elements={e.name: e for e in stated},
                section={"sections": {"A": ["s1"], "B": ["q1"]}},
                layout={"layouts": {"L": ["A", "B"]}, "default_layout": "L"},
            )
        assert model.elements["s1"].physical.s == pytest.approx(9.5)
        # ...but a sequential section following it starts from its exit
        assert model.elements["q1"].physical.s == pytest.approx(10.5)

    def test_a_section_outside_any_layout_is_not_built_at_all(self, names):
        # so there is nothing for composition to touch
        model, _ = self.build({"A": names[:3], "B": names[3:]}, {"L": ["A"]})
        assert list(model.sections) == ["A"]
        assert model.elements["B1"].physical.s is None

    def test_the_non_owning_path_still_gets_its_own_arc_lengths(self):
        """The case `arc_lengths` exists for, and the one easiest to get wrong.

        ``X`` is composed into ``L1``'s frame, so its stored ``s`` is right for
        ``L1`` and wrong for ``L2``.  A composed section must therefore be
        re-offset from its *section-local* coordinates when a different path
        asks -- reporting it as stored, or adding the running offset on top of
        the stored value, are both wrong.
        """
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            model = MachineModel(
                elements={
                    e.name: e
                    for e in (drift("P1", 1.0), drift("P2", 3.0), drift("X1", 2.0))
                },
                section={"sections": {"P": ["P1"], "Q": ["P2"], "X": ["X1"]}},
                layout={
                    "layouts": {"L1": ["P", "X"], "L2": ["Q", "X"]},
                    "default_layout": "L1",
                },
            )
        stored = model.elements["X1"].physical
        assert stored.s - stored.length / 2 == pytest.approx(1.0)  # L1's frame
        assert model.lattices["L1"].arc_lengths()["X1"] == pytest.approx(1.0)
        assert model.lattices["L2"].arc_lengths()["X1"] == pytest.approx(3.0)

    def test_a_shared_section_is_composed_once_and_says_so(self, names):
        _, messages = self.build(
            {"A": names[:3], "B": names[3:]},
            {"L1": ["A", "B"], "L2": ["B"], "L3": ["A", "A", "B"]},
        )
        assert any("different" in m and "predecessors" in m for m in messages)

    def test_composition_is_idempotent(self, names):
        split, _ = self.build({"A": names[:3], "B": names[3:]}, {"L": ["A", "B"]})
        before = {n: split.elements[n].physical.s for n in names}
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            split.resolve_positions()
        for name in names:
            assert split.elements[name].physical.s == pytest.approx(before[name])
