"""The drift-free s positions against the drift-building ones they replaced.

``drift_lengths`` gives the names and lengths ``insert_drifts`` would, without
building a ``Drift`` per gap; ``SectionLattice.get_s_values`` and
``LAURA.get_elements_s_pos`` now go through it. The oracle each time is the
old route: build the drifts, then add up their lengths.
"""

import pytest

from laura import LAURA
from laura.models.element import (
    BeamPositionMonitor,
    CombinedCorrector,
    Drift,
    Marker,
    Quadrupole,
)
from laura.models.element_list import SectionLattice, drift_lengths, insert_drifts
from laura.models.physical import PhysicalElement, Position


def quad(name, z, length=0.5):
    return Quadrupole(
        name=name,
        machine_area="S",
        magnetic={"magnetic_length": length, "k1l": 0.3},
        physical=PhysicalElement(length=length, middle=Position(z=z)),
    )


def elements():
    """Gaps of every kind: a thick diagnostic, a hand-written drift that
    closes a gap itself, a subelement sitting inside a quad, a gap too short
    to fill, and a combined corrector whose s its sub-correctors share."""
    return [
        Marker(name="START", machine_area="S", physical={"middle": {"z": 0.0}}),
        quad("Q1", 0.75),
        BeamPositionMonitor(
            name="BPM",
            machine_area="S",
            physical=PhysicalElement(length=0.3, middle=Position(z=1.65)),
        ),
        quad("Q2", 2.55),
        Drift(
            name="D_HAND",
            hardware_class="Drift",
            machine_area="S",
            physical=PhysicalElement(length=0.4, middle=Position(z=3.0)),
        ),
        quad("Q3", 3.45),
        Marker(
            name="INSIDE_Q3",
            machine_area="S",
            subelement="Q3",
            physical={"middle": {"z": 3.45}},
        ),
        quad("Q4", 3.95 + 1e-14),
        CombinedCorrector(
            name="CC",
            machine_area="S",
            physical={"middle": {"z": 5.0}},
            Horizontal_Corrector="CC_H",
            Vertical_Corrector="CC_V",
        ),
        Marker(name="END", machine_area="S", physical={"middle": {"z": 6.0}}),
    ]


def section():
    elems = elements()
    return SectionLattice(
        name="S", order=[e.name for e in elems], elements=elems, geometry="open"
    )


@pytest.mark.parametrize("min_length", [0.0, 1e-12])
def test_drift_lengths_names_and_lengths_match_insert_drifts(min_length):
    beamline = {e.name: e for e in elements() if not e.subelement}

    built = insert_drifts(beamline, "d", min_length=min_length)
    lengths = drift_lengths(beamline, "d", min_length=min_length)

    assert list(lengths) == list(built)
    assert [length for length, _ in lengths.values()] == [
        e.physical.length for e in built.values()
    ]
    assert [drift for _, drift in lengths.values()] == [
        e.hardware_type == "Drift" for e in built.values()
    ]


def test_the_threshold_drops_the_sliver_before_q4():
    beamline = {e.name: e for e in elements() if not e.subelement}

    assert len(drift_lengths(beamline, "d")) == len(
        drift_lengths(beamline, "d", min_length=1e-12)
    ) + 1


@pytest.mark.parametrize("keep_diagnostic_length", [False, True])
def test_section_drift_lengths_match_create_drifts(keep_diagnostic_length):
    lattice = section()

    built = lattice.create_drifts(keep_diagnostic_length=keep_diagnostic_length)
    lengths = lattice.drift_lengths(keep_diagnostic_length=keep_diagnostic_length)

    assert "INSIDE_Q3" not in lengths
    assert lengths == {name: e.physical.length for name, e in built.items()}
    assert list(lengths) == list(built)


@pytest.mark.parametrize("at_entrance", [False, True])
def test_section_s_values_match_the_built_drifts(at_entrance):
    lattice = section()

    s = [1.5]
    for elem in lattice.create_drifts().values():
        s.append(s[-1] + elem.physical.length)
    s = s[:-1] if at_entrance else s[1:]
    expected = dict(zip(lattice.create_drifts(), s))

    got = lattice.get_s_values(as_dict=True, at_entrance=at_entrance, starting_s=1.5)

    assert got == expected
    assert list(got) == list(expected)
    assert lattice.get_s_values(at_entrance=at_entrance, starting_s=1.5) == s


def test_machine_s_positions_match_the_built_drifts():
    elems = elements()
    machine = LAURA(
        element_list=elems,
        layout={"default_layout": "beam1", "layouts": {"beam1": ["S"]}},
        section={"sections": {"S": [e.name for e in elems]}},
    )

    expected, s_pos = {}, 0
    for name, elem in machine.create_drifts().items():
        s_pos += elem.physical.length
        if elem.hardware_type != "Drift":
            expected[name] = round(s_pos, 6)
            for sub in ("Horizontal_Corrector", "Vertical_Corrector"):
                sub_name = getattr(machine.elements.get(name), sub, None)
                if sub_name:
                    expected[sub_name] = expected[name]

    got = machine.get_elements_s_pos()

    assert got == expected
    assert list(got) == list(expected)
    assert "D_HAND" not in got and "INSIDE_Q3" not in got
    assert got["CC_H"] == got["CC_V"] == got["CC"]
