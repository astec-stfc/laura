"""``MachineLayout.passes``: beam order, one entry per traversal.

``multipass: N`` marks the same hardware entered again; without it a repeated section is repetition.
"""

import pytest

from laura.models.elementList import MachineModel
from laura.translator.converters.layout import MachineLayoutTranslator
from unit_tests.helpers import quad, quiet

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
        name: quad(name, length, 1.0, "A")
        for name, length in (
            ("INJ_Q", 0.2),
            ("LIN_C", 0.6),
            ("ARC_B", 0.4),
            ("DMP_Q", 0.2),
        )
    }


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


def traversal(model):
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
        # A multipass name is not an address; see test_layout_occurrences.py.
        assert erl.lattices["ERL"].elements == [
            "INJ_Q",
            "LIN_C#1",
            "ARC_B",
            "LIN_C#2",
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
        # Repetition deep-copies; multipass must not.
        erl.get_element("LIN_C").magnetic.k1l = 42.0
        assert erl.sections["LINAC"].elements.elements["LIN_C"].magnetic.k1l == 42.0

    def test_repetition_is_not_multipass(self):
        # Expansion has already made the occurrences separate sections.
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
        # Refused for repetition, but the recirculating case for multipass.
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
    # Multipass is a claim about hardware, so it holds for every occurrence or none.
    @pytest.mark.parametrize(
        "second, match",
        [
            pytest.param("LINAC", "marks some occurrences", id="only-some-marked"),
            pytest.param(None, "enters it only once", id="entered-once"),
            pytest.param(
                {"LINAC": {"multipass": 3}}, r"must be \[1, 2\]", id="not-from-one"
            ),
            pytest.param(
                {"LINAC": {"multipass": 1}}, r"must be \[1, 2\]", id="repeated"
            ),
        ],
    )
    def test_incoherent_pass_marking_is_refused(self, second, match):
        layout = ["INJECTOR", {"LINAC": {"multipass": 1}}, "ARC"]
        with pytest.raises(ValueError, match=match):
            machine(layout + ([second] if second else []))

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
        with pytest.raises(TypeError, match="multipass"):
            machine(["INJECTOR", {"LINAC": {"nonsense": 1}}])


class TestNameKeyedLookups:
    """Occurrence addressing is covered in ``test_layout_occurrences.py``."""

    def test_getting_the_element_still_works(self, erl):
        assert erl.get_element("LIN_C").name == "LIN_C"

    def test_a_single_pass_layout_is_unaffected(self):
        model = machine(["INJECTOR", "LINAC", "ARC", "DUMP"])
        assert model.lattices["ERL"].arc_lengths()
        assert model.elements_between(start="INJ_Q", end="DMP_Q", path="ERL")

    def test_export_writes_one_section_per_pass(self, erl):
        """Covered properly in ``test_layout_export_flatten.py``."""
        translator = MachineLayoutTranslator.from_layout(erl.lattices["ERL"])
        assert list(translator.sections) == [
            "INJECTOR",
            "LINAC.1",
            "ARC",
            "LINAC.2",
            "DUMP",
        ]
