"""``MachineLayout.passes`` is the beam order, one entry per traversal.

``sections`` is keyed by name, so on its own it cannot say that a path enters
a section twice. For *repetition* that is now handled before the layout exists
-- expansion gives each occurrence its own section -- but multipass is the case
where the occurrences are deliberately the same section, one piece of
hardware entered more than once, and no name-keyed structure can express it.
``passes`` is what carries it.

``multipass: N`` on a layout entry is the opt-in that separates the two
readings.  Without it a repeated section is repetition, which is what the
section level has always made of the same shape.
"""

import warnings

import pytest

from laura.models.element import Quadrupole
from laura.models.elementList import MachineModel
from laura.models.exceptions import LatticeError
from laura.translator.converters.layout import MachineLayoutTranslator

SECTIONS = {
    "INJECTOR": ["INJ_Q"],
    "LINAC": ["LIN_C"],
    "ARC": ["ARC_B"],
    "DUMP": ["DMP_Q"],
}

ERL = [
    "INJECTOR",
    {"LINAC": {"multipass": 1}},
    "ARC",
    {"LINAC": {"multipass": 2}},
    "DUMP",
]


def elements():
    return {
        name: Quadrupole(
            name=name,
            hardware_class="Magnet",
            machine_area="A",
            magnetic={"magnetic_length": length, "k1l": 1.0},
            physical={"length": length},
        )
        for name, length in (
            ("INJ_Q", 0.2),
            ("LIN_C", 0.6),
            ("ARC_B", 0.4),
            ("DMP_Q", 0.2),
        )
    }


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


def traversal(model):
    """``[(section, pass number)]`` in beam order."""
    return [(p.section, p.number) for p in model.lattices["ERL"].passes]


class TestPassesAreTheBeamOrder:
    def test_a_single_pass_layout_still_gets_passes(self):
        model = machine(["INJECTOR", "LINAC", "ARC", "DUMP"])
        assert traversal(model) == [
            ("INJECTOR", None),
            ("LINAC", None),
            ("ARC", None),
            ("DUMP", None),
        ]

    def test_a_multipass_section_appears_once_per_pass(self, erl):
        assert traversal(erl) == [
            ("INJECTOR", None),
            ("LINAC", 1),
            ("ARC", None),
            ("LINAC", 2),
            ("DUMP", None),
        ]

    def test_the_element_list_follows_the_passes(self, erl):
        assert erl.lattices["ERL"].elements == [
            "INJ_Q",
            "LIN_C",
            "ARC_B",
            "LIN_C",
            "DMP_Q",
        ]

    def test_the_section_is_built_once(self, erl):
        assert list(erl.lattices["ERL"].sections) == [
            "INJECTOR",
            "LINAC",
            "ARC",
            "DUMP",
        ]

    def test_both_passes_are_the_same_hardware(self, erl):
        # The point of multipass. Repetition deep-copies; this must not.
        erl.get_element("LIN_C").magnetic.k1l = 42.0
        assert erl.sections["LINAC"].elements.elements["LIN_C"].magnetic.k1l == 42.0

    def test_repetition_is_not_multipass(self):
        # Expansion has already run, so the occurrences are separate sections
        # and carry no pass number: they are devices, not passes.
        model = machine(["INJECTOR", "LINAC", "LINAC", "DUMP"])
        assert traversal(model) == [
            ("INJECTOR", None),
            ("LINAC.1", None),
            ("LINAC.2", None),
            ("DUMP", None),
        ]
        assert model.lattices["ERL"].is_multipass is False

    def test_a_multipass_path_says_so(self, erl):
        assert erl.lattices["ERL"].is_multipass is True


class TestDirectionIsPerPass:
    def test_a_pass_may_be_reversed_while_another_is_not(self):
        # Refused for repetition -- two devices with one built backwards is not
        # a machine -- but for multipass it is the recirculating case itself.
        model = machine(
            [
                "INJECTOR",
                {"LINAC": {"multipass": 1}},
                "ARC",
                {"LINAC": {"multipass": 2, "direction": -1}},
                "DUMP",
            ]
        )
        assert [
            (p.section, p.number, p.direction) for p in model.lattices["ERL"].passes
        ][1:4] == [("LINAC", 1, 1), ("ARC", None, 1), ("LINAC", 2, -1)]


class TestRefusesIncoherentMultipass:
    def test_marking_only_some_occurrences_is_refused(self):
        # Multipass is a claim about hardware, so it holds for every occurrence
        # or none: a section cannot be two devices on one pass and one on the
        # next.
        with pytest.raises(ValueError, match="on all of them or none"):
            machine(["INJECTOR", {"LINAC": {"multipass": 1}}, "ARC", "LINAC"])

    def test_a_section_entered_once_cannot_be_multipass(self):
        with pytest.raises(ValueError, match="enters it only once"):
            machine(["INJECTOR", {"LINAC": {"multipass": 1}}, "ARC"])

    def test_pass_numbers_must_run_from_one(self):
        with pytest.raises(ValueError, match=r"must be \[1, 2\]"):
            machine(
                [
                    "INJECTOR",
                    {"LINAC": {"multipass": 1}},
                    "ARC",
                    {"LINAC": {"multipass": 3}},
                ]
            )

    def test_pass_numbers_must_not_repeat(self):
        with pytest.raises(ValueError, match=r"must be \[1, 2\]"):
            machine(
                [
                    "INJECTOR",
                    {"LINAC": {"multipass": 1}},
                    "ARC",
                    {"LINAC": {"multipass": 1}},
                ]
            )

    @pytest.mark.parametrize("bad", [0, -1, 1.5, True, "2"])
    def test_a_pass_number_must_be_a_counting_number(self, bad):
        with pytest.raises(ValueError, match="counting from"):
            machine(
                [
                    "INJECTOR",
                    {"LINAC": {"multipass": bad}},
                    "ARC",
                    {"LINAC": {"multipass": 2}},
                ]
            )

    def test_an_unknown_option_is_still_refused(self):
        # Guards the widened option set: adding 'multipass' must not turn the
        # entry parser into one that accepts anything.
        with pytest.raises(TypeError, match="multipass"):
            machine(["INJECTOR", {"LINAC": {"nonsense": 1}}])


class TestNameKeyedLookupsRefuseRatherThanGuess:
    def test_arc_lengths_refuses(self, erl):
        # It returns Dict[str, float] and skips a name it has already seen, so
        # it would report one pass and drop the rest.
        with pytest.raises(LatticeError, match="multipass"):
            erl.lattices["ERL"].arc_lengths()

    def test_elements_between_refuses(self, erl):
        # This is the call simba builds every lattice line from, so answering
        # for the first pass would produce a malformed line, silently.
        with pytest.raises(LatticeError, match="multipass"):
            erl.elements_between(start="INJ_Q", end="DMP_Q", path="ERL")

    def test_the_refusal_names_the_passes(self, erl):
        with pytest.raises(LatticeError, match=r"LINAC#1, LINAC#2"):
            erl.lattices["ERL"].arc_lengths()

    def test_getting_the_element_still_works(self, erl):
        assert erl.get_element("LIN_C").name == "LIN_C"

    def test_a_single_pass_layout_is_unaffected(self):
        model = machine(["INJECTOR", "LINAC", "ARC", "DUMP"])
        assert model.lattices["ERL"].arc_lengths()
        assert model.elements_between(start="INJ_Q", end="DMP_Q", path="ERL")

    def test_export_refuses_a_multipass_path(self, erl):
        with pytest.raises(LatticeError, match="multipass"):
            MachineLayoutTranslator.from_layout(erl.lattices["ERL"])
