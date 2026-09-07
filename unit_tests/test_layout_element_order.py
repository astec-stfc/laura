"""A layout's element list must follow the beam, not a dict's insertion order.

``MachineLayout._all_elements`` is what ``elements``, ``_lookup_index`` and
``elements_between`` are all built on, and ``elements_between`` is in turn how
downstream code (SIMBA) carves a lattice into tracking lines.

The oracle throughout is ``section.order``: it is the beam path, and the
layout's view of it must agree.
"""

import warnings

import pytest

from laura.models.element import Drift, Quadrupole
from laura.models.elementList import MachineLayout, MachineModel, SectionLattice

TWO_OCCURRENCES = [
    "QUAD_A",
    "DRIFT_IN",
    "BEND",
    "DRIFT_OUT",
    "QUAD_B",
    "DRIFT_IN",
    "QUAD_A",
]

NUMBERED = [
    "QUAD_A.1",
    "DRIFT_IN.1",
    "BEND",
    "DRIFT_OUT",
    "QUAD_B",
    "DRIFT_IN.2",
    "QUAD_A.2",
]


def drift(name, length):
    return Drift(
        name=name,
        hardware_class="Drift",
        machine_area="ARC",
        physical={"length": length},
    )


def quad(name, length, k1l):
    return Quadrupole(
        name=name,
        hardware_class="Magnet",
        machine_area="ARC",
        magnetic={"magnetic_length": length, "k1l": k1l},
        physical={"length": length},
    )


def elements():
    return {
        e.name: e
        for e in (
            quad("QUAD_A", 0.2, 1.0),
            drift("DRIFT_IN", 0.5),
            quad("BEND", 0.8, 0.0),
            drift("DRIFT_OUT", 0.4),
            quad("QUAD_B", 0.2, -1.0),
        )
    }


def machine(order):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        return MachineModel(
            elements=elements(),
            section={"sections": {"ARC": list(order)}},
            layout={
                "layouts": {"PATH": ["ARC"]},
                "default_layout": "PATH",
            },
        )


@pytest.fixture
def repeated():
    """A model whose one section enters two of its elements twice."""
    return machine(TWO_OCCURRENCES)


@pytest.fixture
def plain():
    """The same section with every name used once."""
    return machine(["QUAD_A", "DRIFT_IN", "BEND", "DRIFT_OUT", "QUAD_B"])


class TestFollowsSectionOrder:
    def test_the_repeats_were_numbered(self, repeated):
        assert repeated.sections["ARC"].order == NUMBERED

    def test_layout_elements_match_the_section_order(self, repeated):
        assert repeated.lattices["PATH"].elements == NUMBERED

    def test_layout_elements_are_in_increasing_s(self, repeated):
        layout = repeated.lattices["PATH"]
        positions = [layout.get_element(name).physical.s for name in layout.elements]
        assert positions == sorted(positions)

    def test_an_unrepeated_section_is_unaffected(self, plain):
        section = plain.sections["ARC"]
        assert plain.lattices["PATH"].elements == section.order


class TestRetiredOriginals:
    def test_originals_are_not_listed_by_the_layout(self, repeated):
        listed = repeated.lattices["PATH"].elements
        assert "QUAD_A" not in listed
        assert "DRIFT_IN" not in listed

    def test_originals_are_not_left_in_the_section(self, repeated):
        registry = repeated.sections["ARC"].elements.elements
        assert "QUAD_A" not in registry
        assert "DRIFT_IN" not in registry

    def test_the_layout_lists_nothing_the_model_cannot_resolve(self, repeated):
        for name in repeated.lattices["PATH"].elements:
            assert repeated.get_element(name) is not None

    def test_element_count_matches_the_order(self, repeated):
        section = repeated.sections["ARC"]
        assert len(repeated.lattices["PATH"].elements) == len(section.order)


class TestElementsBetween:
    def test_a_range_excludes_everything_upstream_of_its_start(self, repeated):
        found = repeated.elements_between(start="BEND", end="QUAD_A.2", path="PATH")
        assert found == ["BEND", "DRIFT_OUT", "QUAD_B", "DRIFT_IN.2", "QUAD_A.2"]

    def test_a_range_is_contiguous_in_the_section_order(self, repeated):
        order = repeated.sections["ARC"].order
        found = repeated.elements_between(start="DRIFT_IN.1", end="QUAD_B", path="PATH")
        first = order.index("DRIFT_IN.1")
        assert found == order[first : order.index("QUAD_B") + 1]

    def test_the_second_occurrence_is_reachable(self, repeated):
        # ``.index()`` on a name list returns the first hit; the numbered
        # copies are distinct names, so both must be addressable.
        found = repeated.elements_between(start="QUAD_A.2", end="QUAD_A.2", path="PATH")
        assert found == ["QUAD_A.2"]

    def test_the_whole_path_is_the_whole_order(self, repeated):
        found = repeated.elements_between(
            start=NUMBERED[0], end=NUMBERED[-1], path="PATH"
        )
        assert found == NUMBERED


class TestSharedAcrossSections:
    """An element used by two sections of one path is listed by each.

    The layout is assembled from ``SectionLattice`` objects rather than
    through ``MachineModel``.
    """

    @staticmethod
    def positioned(name, length, s):
        return Quadrupole(
            name=name,
            hardware_class="Magnet",
            machine_area="ARC",
            magnetic={"magnetic_length": length, "k1l": 1.0},
            physical={"length": length, "s": s, "s_point": "middle"},
        )

    @classmethod
    def shared(cls):
        first = cls.positioned("FIRST", 0.2, 0.5)
        both = cls.positioned("SHARED", 0.2, 1.5)
        last = cls.positioned("LAST", 0.2, 2.5)
        return MachineLayout(
            name="PATH",
            sections={
                "ONE": SectionLattice(
                    name="ONE",
                    elements=[first, both],
                    order=["FIRST", "SHARED"],
                ),
                "TWO": SectionLattice(
                    name="TWO",
                    elements=[both, last],
                    order=["SHARED", "LAST"],
                ),
            },
        )

    def test_the_shared_element_is_listed_once_per_section(self):
        assert self.shared().elements.count("SHARED") == 2

    def test_the_path_is_as_long_as_the_two_orders_together(self):
        layout = self.shared()
        expected = sum(len(section.order) for section in layout.sections.values())
        assert len(layout.elements) == expected
