"""MachineLayoutTranslator.as_section: a whole layout as one lattice."""

import math

import pytest

from laura.models.element import Dipole
from laura.models.element_list import LatticeError
from laura.translator.converters.layout import MachineLayoutTranslator
from unit_tests.test_layout_arc_lengths import drift, line, machine


def merged(model, layout="L"):
    return MachineLayoutTranslator.from_layout(model.lattices[layout]).as_section()


def test_sequential_sections_chain():
    section = merged(line())
    assert section.order == ["a1", "a2", "b1", "b2"]
    lengths = {k: v.physical.length for k, v in section.create_drifts().items()}
    assert sum(lengths.values()) == pytest.approx(6.0)


def test_a_gap_between_sections_becomes_a_drift():
    model = machine(
        [
            drift("a1", 1.0, s=1.0, s_point="end"),
            drift("a2", 1.0, s=2.0, s_point="end"),
            drift("b1", 2.0, s=12.0, s_point="end"),
            drift("b2", 2.0, s=14.0, s_point="end"),
        ],
        {"A": ["a1", "a2"], "B": ["b1", "b2"]},
    )
    section = merged(model)
    assert section.elements.elements["b1"].physical.s == pytest.approx(11.0)
    lengths = [v.physical.length for v in section.create_drifts().values()]
    assert lengths == pytest.approx([1.0, 1.0, 8.0, 2.0, 2.0])


def test_a_ring_split_in_two_is_closed():
    def bend(name):
        return Dipole(
            name=name,
            hardware_class="Magnet",
            machine_area="S",
            physical={"length": 1.0},
            magnetic={"angle": math.pi / 2, "length": 1.0},
        )

    model = machine(
        [bend("a1"), bend("a2"), bend("b1"), bend("b2")],
        {"A": ["a1", "a2"], "B": ["b1", "b2"]},
    )
    section = merged(model)
    assert section.geometry == "closed"
    assert "a1" in section.to_madx() and "b2" in section.to_madx()


def test_an_element_in_two_sections_is_refused():
    translator = MachineLayoutTranslator.from_layout(line().lattices["L"])
    translator.sections["A2"] = translator.sections["A"]
    with pytest.raises(LatticeError, match="twice"):
        translator.as_section()
