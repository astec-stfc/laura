"""A section listed twice in a layout is entered twice, as ``expand_section_order``
already does one level down.
"""

import pytest

from laura.models.element import Drift
from laura.models.elementList import MachineModel
from unit_tests.helpers import quad, quiet


def elements():
    return {
        "Q1": quad("Q1", 0.2, 1.0, "ARC"),
        "D1": Drift(
            name="D1",
            hardware_class="Drift",
            machine_area="ARC",
            physical={"length": 0.5},
        ),
        "Q2": quad("Q2", 0.2, 1.0, "ARC"),
    }


def machine(sections, layout):
    with quiet():
        return MachineModel(
            elements=elements(),
            section={"sections": sections},
            layout={"layouts": {"PATH": layout}, "default_layout": "PATH"},
        )


def cell(times):
    """``PATH`` entering the one-cell section ``CELL`` ``times`` over."""
    return machine({"CELL": ["Q1", "D1"]}, ["CELL"] * times)


def profile(model):
    """``[(name, s)]`` along the beam path."""
    layout = model.lattices["PATH"]
    return [
        (name, round(layout.get_element(name).physical.s, 6))
        for name in layout.elements
    ]


class TestARepeatedSectionIsEnteredEachTime:
    def test_one_occurrence_is_left_alone(self):
        model = cell(1)
        assert list(model.sections) == ["CELL"]
        assert model.lattices["PATH"].elements == ["Q1", "D1"]

    @pytest.mark.parametrize("times", [2, 3, 4])
    def test_each_occurrence_becomes_its_own_section(self, times):
        model = cell(times)
        assert list(model.sections) == [f"CELL.{n}" for n in range(1, times + 1)]

    @pytest.mark.parametrize("times", [2, 3, 4])
    def test_every_occurrence_contributes_its_elements(self, times):
        assert len(cell(times).lattices["PATH"].elements) == 2 * times

    def test_the_copies_are_numbered_in_beam_order(self):
        assert cell(2).lattices["PATH"].elements == ["Q1.1", "D1.1", "Q1.2", "D1.2"]

    def test_the_occurrences_are_laid_end_to_end(self):
        assert profile(cell(2)) == [
            ("Q1.1", 0.1),
            ("D1.1", 0.45),
            ("Q1.2", 0.8),
            ("D1.2", 1.15),
        ]

    def test_a_repeat_is_separate_devices(self):
        model = cell(2)
        model.get_element("Q1.1").magnetic.k1l = 99.0
        assert model.get_element("Q1.2").magnetic.k1l == 1.0


class TestAgreesWithTheSectionLevel:
    """The same duplication one level down is the oracle."""

    @staticmethod
    def both():
        at_section = machine({"MAIN": ["CELL", "CELL"], "CELL": ["Q1", "D1"]}, ["MAIN"])
        return at_section, cell(2)

    def test_the_element_names_match(self):
        at_section, at_layout = self.both()
        assert [n for n, _ in profile(at_layout)] == [n for n, _ in profile(at_section)]

    def test_the_positions_match(self):
        at_section, at_layout = self.both()
        assert profile(at_layout) == profile(at_section)


class TestNonAdjacentRepeats:
    @staticmethod
    def there_and_back():
        return machine({"CELL": ["Q1"], "OTHER": ["D1"]}, ["CELL", "OTHER", "CELL"])

    def test_the_intervening_section_is_untouched(self):
        model = self.there_and_back()
        assert list(model.sections) == ["CELL.1", "OTHER", "CELL.2"]
        # OTHER is entered once, so it keeps its name and its element keeps its.
        assert model.sections["OTHER"].order == ["D1"]

    def test_the_second_occurrence_follows_the_intervening_section(self):
        assert profile(self.there_and_back()) == [
            ("Q1.1", 0.1),
            ("D1", 0.45),
            ("Q1.2", 0.8),
        ]


class TestDirectionFollowsTheOccurrence:
    @staticmethod
    def reversed_twice():
        return machine({"CELL": ["Q1", "D1"]}, [{"CELL": {"direction": -1}}] * 2)

    def test_a_direction_is_rekeyed_onto_the_occurrences(self):
        model = self.reversed_twice()
        assert model._layout_directions["PATH"] == {"CELL.1": -1, "CELL.2": -1}

    def test_the_same_direction_twice_is_still_a_repeat(self):
        assert list(self.reversed_twice().sections) == ["CELL.1", "CELL.2"]


class TestRefusesWhatCannotBeRepetition:
    # Match the condition, not the prose half of the message, which gets trimmed.
    @pytest.mark.parametrize(
        "match",
        [
            pytest.param("different 'direction' each time", id="refused"),
            pytest.param(
                "Layout 'PATH'.*section 'CELL'", id="names-layout-and-section"
            ),
        ],
    )
    def test_occurrences_with_different_directions_are_refused(self, match):
        with pytest.raises(ValueError, match=match):
            machine(
                {"CELL": ["Q1", "D1"]},
                ["CELL", {"CELL": {"direction": -1}}],
            )

    def test_a_positioned_section_cannot_be_repeated(self):
        with pytest.raises(ValueError, match="states its own positions"):
            MachineModel(
                elements={"QP": quad("QP", 0.2, 1.0, "ARC", s=1.0, s_point="middle")},
                section={"sections": {"POS": ["QP"]}},
                layout={"layouts": {"PATH": ["POS", "POS"]}, "default_layout": "PATH"},
            )

    def test_a_positioned_section_entered_once_is_fine(self):
        model = MachineModel(
            elements={"QP": quad("QP", 0.2, 1.0, "ARC", s=1.0, s_point="middle")},
            section={"sections": {"POS": ["QP"]}},
            layout={"layouts": {"PATH": ["POS"]}, "default_layout": "PATH"},
        )
        assert model.lattices["PATH"].elements == ["QP"]
