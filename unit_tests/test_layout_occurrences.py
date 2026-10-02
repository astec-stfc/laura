"""``NAME#N`` addresses one traversal of a multipass element.

A multipass path enters one device more than once, so the device's name is not
an address: ``LIN_A`` names the hardware, ``LIN_A#2`` names the second time the
beam reaches it.  PALS spells it the same way.

The oracle is repetition.  ``[INJ, LINAC, ARC, LINAC, DUMP]`` without
``multipass`` is two linacs, which LAURA already lays end to end; with it, one
linac traversed twice.  The beam covers the same ground either way, so the two
must agree on every arc length, and differ only in whether the second traversal
is a separate device.
"""

import warnings

import pytest

from laura.models.element import Drift, Quadrupole
from laura.models.elementList import MachineModel, split_occurrence
from laura.models.exceptions import LatticeError

SECTIONS = {
    "INJECTOR": ["INJ_Q"],
    "LINAC": ["LIN_A", "LIN_B"],
    "ARC": ["ARC_B"],
    "DUMP": ["DMP_Q"],
}

MULTIPASS = [
    "INJECTOR",
    {"LINAC": {"multipass": 1}},
    "ARC",
    {"LINAC": {"multipass": 2}},
    "DUMP",
]

REPETITION = ["INJECTOR", "LINAC", "ARC", "LINAC", "DUMP"]

SINGLE = ["INJECTOR", "LINAC", "ARC", "DUMP"]


def elements():
    magnets = {
        name: Quadrupole(
            name=name,
            hardware_class="Magnet",
            machine_area="A",
            magnetic={"magnetic_length": length, "k1l": 1.0},
            physical={"length": length},
        )
        for name, length in (
            ("INJ_Q", 0.2),
            ("LIN_A", 0.2),
            ("ARC_B", 0.4),
            ("DMP_Q", 0.2),
        )
    }
    # One non-magnet, so the type filters have something to cut on.
    magnets["LIN_B"] = Drift(
        name="LIN_B",
        hardware_class="Drift",
        machine_area="A",
        physical={"length": 0.4},
    )
    return magnets


def machine(layout):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        return MachineModel(
            elements=elements(),
            section={"sections": SECTIONS},
            layout={"layouts": {"ERL": layout}, "default_layout": "ERL"},
        )


@pytest.fixture
def erl():
    return machine(MULTIPASS).lattices["ERL"]


class TestTheSelector:
    @pytest.mark.parametrize(
        "name, expected",
        [
            ("LIN_A#2", ("LIN_A", 2)),
            ("LIN_A#12", ("LIN_A", 12)),
            ("LIN_A", ("LIN_A", None)),
            ("LIN_A#0", ("LIN_A#0", None)),
            ("LIN_A#-1", ("LIN_A#-1", None)),
            ("LIN_A#x", ("LIN_A#x", None)),
            ("#2", ("#2", None)),
            ("A#1#2", ("A#1", 2)),
        ],
    )
    def test_only_a_counting_number_is_a_selector(self, name, expected):
        # An element whose name happens to contain a '#' is left alone.
        assert split_occurrence(name) == expected


class TestTheElementListIsAddressable:
    def test_a_repeated_name_is_qualified(self, erl):
        assert erl.elements == [
            "INJ_Q",
            "LIN_A#1",
            "LIN_B#1",
            "ARC_B",
            "LIN_A#2",
            "LIN_B#2",
            "DMP_Q",
        ]

    def test_a_name_entered_once_is_left_bare(self, erl):
        # number_repeated_names' convention: suffix only what is ambiguous.
        assert "ARC_B" in erl.elements

    def test_a_single_pass_path_is_untouched(self):
        assert machine(SINGLE).lattices["ERL"].elements == [
            "INJ_Q",
            "LIN_A",
            "LIN_B",
            "ARC_B",
            "DMP_Q",
        ]

    def test_repetition_is_untouched(self):
        # Expansion has already made the occurrences distinct devices, so
        # there is nothing left for a selector to disambiguate.
        names = machine(REPETITION).lattices["ERL"].elements
        assert not any("#" in name for name in names)
        assert names[1:3] == ["LIN_A.1", "LIN_B.1"]

    def test_every_name_it_reports_is_one_it_accepts(self, erl):
        assert [erl.elements_between(start=n, end=n) for n in erl.elements] == [
            [n] for n in erl.elements
        ]


class TestArcLengthsReportEveryPass:
    def test_each_pass_gets_its_own_entry(self, erl):
        assert erl.arc_lengths() == pytest.approx(
            {
                "INJ_Q": 0.0,
                "LIN_A#1": 0.2,
                "LIN_B#1": 0.4,
                "ARC_B": 0.8,
                "LIN_A#2": 1.2,
                "LIN_B#2": 1.4,
                "DMP_Q": 1.8,
            }
        )

    def test_it_agrees_with_repetition(self):
        # The oracle: two linacs and one linac twice put the beam through the
        # same metres, so only the keys may differ.
        multipass = machine(MULTIPASS).lattices["ERL"].arc_lengths()
        repetition = machine(REPETITION).lattices["ERL"].arc_lengths()
        assert list(multipass.values()) == pytest.approx(list(repetition.values()))

    def test_the_path_is_longer_than_its_sections(self, erl):
        # The composed frames chain each section once, which is one linac
        # short; arc_lengths is the only view that has both passes.
        assert erl.arc_lengths()["DMP_Q"] == pytest.approx(1.8)
        assert erl.sections["DUMP"].elements.elements["DMP_Q"].physical.s < 1.8

    def test_a_single_pass_path_is_untouched(self):
        assert machine(SINGLE).lattices["ERL"].arc_lengths() == pytest.approx(
            {"INJ_Q": 0.0, "LIN_A": 0.2, "LIN_B": 0.4, "ARC_B": 0.8, "DMP_Q": 1.2}
        )

    def test_its_keys_are_the_names_the_path_reports(self, erl):
        # arc_lengths does its own walk, so this is what keeps the two
        # numberings from drifting apart.
        assert list(erl.arc_lengths()) == erl.elements

    def test_a_third_pass_is_numbered_in_beam_order(self):
        layout = machine(
            [
                "INJECTOR",
                {"LINAC": {"multipass": 1}},
                "ARC",
                {"LINAC": {"multipass": 2}},
                "DUMP",
                {"LINAC": {"multipass": 3}},
            ]
        ).lattices["ERL"]
        lengths = layout.arc_lengths()
        assert lengths["LIN_A#3"] == pytest.approx(2.0)
        assert lengths["LIN_A#1"] < lengths["LIN_A#2"] < lengths["LIN_A#3"]


class TestDirectionIsTakenPerPass:
    @staticmethod
    def there_and_back():
        return machine(
            [
                "INJECTOR",
                {"LINAC": {"multipass": 1}},
                "ARC",
                {"LINAC": {"multipass": 2, "direction": -1}},
                "DUMP",
            ]
        ).lattices["ERL"]

    def test_only_the_reversed_pass_is_mirrored(self):
        # _direction is keyed by section name and so cannot say 'pass 2 only'.
        lengths = self.there_and_back().arc_lengths()
        assert (lengths["LIN_A#1"], lengths["LIN_B#1"]) == pytest.approx((0.2, 0.4))
        assert (lengths["LIN_A#2"], lengths["LIN_B#2"]) == pytest.approx((1.6, 1.2))

    def test_the_path_is_still_the_same_length(self):
        assert self.there_and_back().arc_lengths()["DMP_Q"] == pytest.approx(1.8)

    def test_an_explicit_argument_still_overrides(self):
        # Documented behaviour: the argument replaces the path's directions
        # outright rather than merging with them.
        lengths = self.there_and_back().arc_lengths(direction={})
        assert (lengths["LIN_A#2"], lengths["LIN_B#2"]) == pytest.approx((1.2, 1.4))


class TestLookupNeedsToKnowWhichPass:
    def test_a_bare_ambiguous_name_is_refused(self, erl):
        with pytest.raises(LatticeError, match="enters 'LIN_A' 2 times"):
            erl.elements_between(start="LIN_A", end="DMP_Q")

    def test_the_refusal_offers_the_addresses(self, erl):
        with pytest.raises(LatticeError, match=r"LIN_A#1, LIN_A#2"):
            erl.elements_between(start="LIN_A", end="DMP_Q")

    def test_a_bare_unambiguous_name_still_works(self, erl):
        assert erl.elements_between(start="ARC_B", end="ARC_B") == ["ARC_B"]

    def test_the_selector_picks_the_pass(self, erl):
        assert erl._lookup_index("LIN_A#1") == 1
        assert erl._lookup_index("LIN_A#2") == 4

    def test_a_pass_that_does_not_exist_is_refused(self, erl):
        with pytest.raises(LatticeError, match="no LIN_A#3"):
            erl._lookup_index("LIN_A#3")

    def test_an_unknown_name_is_still_unknown(self, erl):
        with pytest.raises(LatticeError, match="does not exist"):
            erl._lookup_index("NOPE#1")

    def test_a_selector_on_a_single_pass_name_is_allowed(self, erl):
        assert erl._lookup_index("ARC_B#1") == erl._lookup_index("ARC_B")


class TestElementsBetweenSpansThePasses:
    def test_a_span_may_start_and_end_on_the_same_device(self, erl):
        assert erl.elements_between(start="LIN_A#1", end="LIN_A#2") == [
            "LIN_A#1",
            "LIN_B#1",
            "ARC_B",
            "LIN_A#2",
        ]

    def test_the_two_passes_give_different_spans(self, erl):
        assert erl.elements_between(start="LIN_A#2") == ["LIN_A#2", "LIN_B#2", "DMP_Q"]

    def test_blank_ends_are_the_whole_path(self, erl):
        assert erl.elements_between() == erl.elements

    def test_filters_keep_the_qualified_names(self, erl):
        assert erl.elements_between(element_class="Magnet") == [
            "INJ_Q",
            "LIN_A#1",
            "ARC_B",
            "LIN_A#2",
            "DMP_Q",
        ]

    def test_the_model_level_call_agrees(self):
        model = machine(MULTIPASS)
        assert model.elements_between(path="ERL") == model.lattices["ERL"].elements

    def test_the_model_level_call_takes_a_selector(self):
        model = machine(MULTIPASS)
        assert model.elements_between(start="LIN_A#2", path="ERL") == [
            "LIN_A#2",
            "LIN_B#2",
            "DMP_Q",
        ]


class TestGettingTheDeviceIgnoresThePass:
    def test_both_selectors_reach_the_same_object(self, erl):
        assert erl.get_element("LIN_A#1") is erl.get_element("LIN_A#2")

    def test_the_bare_name_still_reaches_it(self, erl):
        assert erl.get_element("LIN_A") is erl.get_element("LIN_A#2")

    def test_editing_through_one_selector_is_seen_through_the_other(self, erl):
        erl.get_element("LIN_A#2").magnetic.k1l = 42.0
        assert erl.get_element("LIN_A#1").magnetic.k1l == 42.0

    def test_the_model_takes_a_selector_too(self):
        assert machine(MULTIPASS).get_element("LIN_A#2").name == "LIN_A"

    def test_an_unknown_name_is_reported_as_given(self, erl):
        with pytest.raises(LatticeError, match="NOPE#2"):
            erl.get_element("NOPE#2")
