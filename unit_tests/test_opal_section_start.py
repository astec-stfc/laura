"""OPAL starts the beam at s = 0, so a section is written from its first element, wherever it is.

A section that began at 16 m in the machine used to be written with ``ELEMEDGE`` of 16 m and
``ZSTOP`` of its end position, so OPAL drifted the beam for 16 m before the first element and
dumped every step of it.
"""

import re

import pytest

from laura.models.element import Collimator, Drift
from laura.models.element_list import ElementList, SectionLattice
from laura.translator.converters.codes.opal import (
    OpalBeam,
    OpalDistribution,
    OpalFieldSolver,
    OpalOption,
    OpalRun,
    OpalTrack,
)
from laura.translator.converters.section import SectionLatticeTranslator

SIZE = {"shape": "rectangular", "horizontal_size": 0.01, "vertical_size": 0.01}


def collimator(name, s):
    return Collimator(
        name=name, machine_area="S", physical={"s": s, "length": 0.1}, aperture=SIZE
    )


def drift(name, s, length):
    return Drift(
        name=name,
        hardware_class="Drift",
        hardware_type="Drift",
        machine_area="S",
        physical={"s": s, "length": length},
    )


def opal_deck(*elements):
    registry = {e.name: e for e in elements}
    lattice = SectionLattice(
        name="line", order=list(registry), elements=ElementList(elements=registry)
    )
    lattice.resolve_positions(lattice.elements.elements)
    section = SectionLatticeTranslator.from_section(lattice)
    section.opal_headers = {
        "option": OpalOption(),
        "distribution": OpalDistribution(input_particle_definition='"beam.opal"'),
        "fieldsolver": OpalFieldSolver(npart=16, space_charge_mode="False"),
        "beam": OpalBeam(PC=0.1, NPART=16, CHARGE=-1, PARTICLE="ELECTRON", BCURRENT=1e-3),
        "track": OpalTrack(DT=2e-12, MAXSTEPS=1000, LINE="line", ZSTOP=0.0),
        "run": OpalRun(),
    }
    return section.to_opal(0.0)


def edges(deck):
    return [float(x) for x in re.findall(r"ELEMEDGE = ([-\d.e]+);", deck)]


def zstop(deck):
    return float(re.search(r"ZSTOP = \{([-\d.e]+)\}", deck).group(1))


@pytest.mark.parametrize("start", [0.0, 16.0])
def test_the_first_element_is_at_the_start_wherever_the_section_is(start):
    deck = opal_deck(
        collimator("c1", start + 0.05),
        collimator("c2", start + 1.05),
        collimator("c3", start + 3.05),
    )
    assert edges(deck) == pytest.approx([0.0, 1.0, 3.0])
    assert zstop(deck) == pytest.approx(3.1 + 0.1)  # the length, and OPAL's 0.1 m margin


def test_a_leading_drift_is_part_of_the_section():
    """The beam travels the first element, so a drift that comes first is tracked."""
    deck = opal_deck(drift("d0", 20.5, 1.0), collimator("c1", 22.05))  # the drift is 20 to 21 m
    assert edges(deck) == pytest.approx([2.0])
    assert zstop(deck) == pytest.approx(2.1 + 0.1)
