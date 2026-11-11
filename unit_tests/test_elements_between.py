"""Indexing a machine: ``elements_between`` and the methods built on it take
the start first, layouts and sections index by position, and a misspelt
attribute raises."""

import pytest

from laura import LAURA
from laura.models.exceptions import LatticeError
from unit_tests.helpers import quad, quiet

ALL = ["QA1", "QA2", "QB1"]


@pytest.fixture
def machine():
    with quiet():
        return LAURA(
            element_list=[
                quad("QA1", machine_area="A", middle={"z": 0.5}),
                quad("QA2", machine_area="A", middle={"z": 1.0}),
                quad("QB1", machine_area="B", middle={"z": 2.0}),
            ],
            section={"sections": {"A": ["QA1", "QA2"], "B": ["QB1"]}},
            # a layout named after a section, as well as the full path
            layout={"default_layout": "full", "layouts": {"full": ["A", "B"], "B": ["B"]}},
        )


def test_start_comes_first(machine):
    assert machine.elements_between("QA2", "QB1") == ["QA2", "QB1"]
    assert machine.lattices["full"].elements_between("QA2", "QB1") == ["QA2", "QB1"]
    assert machine.get_elements("QA2", "QB1") == ["QA2", "QB1"]
    assert list(machine.get_elements_s_pos("QA2", "QB1")) == ["QA2", "QB1"]
    assert "QA1" not in machine.create_drifts("QA2", "QB1")


def test_a_start_after_the_end_raises(machine):
    with pytest.raises(LatticeError, match="QB1.*after.*QA1"):
        machine.elements_between(start="QB1", end="QA1")


def test_an_explicit_path_is_used(machine):
    assert machine.elements_between(start="QA1", end="QB1", path="full") == ALL
    assert machine.elements_between(start="QA1", end="QB1") == ALL


def test_a_layout_indexes_its_sections_in_beam_order(machine):
    layout = machine.lattices["full"]
    assert [layout[0].name, layout[-1].name] == ["A", "B"]
    assert layout["B"].name == "B"


def test_a_section_slices_to_its_elements(machine):
    section = machine.sections["A"]
    assert [e.name for e in section[0:2]] == ["QA1", "QA2"]
    assert [e.name for e in section[::-1]] == ["QA2", "QA1"]


def test_a_misspelt_attribute_raises(machine):
    section = machine.sections["A"]
    assert section.elements.physical  # one every element has still works
    with pytest.raises(AttributeError, match="lenght"):
        section.elements.lenght
    with pytest.raises(AttributeError, match="lenght"):
        section.lenght
