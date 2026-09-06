"""Drift-based (sequential) placement: order + lengths, no stated positions.

A section whose elements carry no ``s`` and no xyz is placed by accumulating
lengths along ``order``, hand-written ``Drift`` elements included .

The strongest test here is :class:`TestAgreesWithExplicitS`: the same lattice
written both ways must land in the same place.  That is a real oracle rather
than a captured number, and it covers the bend arc geometry for free.
"""

import warnings

import numpy as np
import pytest
from pydantic import ValidationError

from laura.models.element import Dipole, Drift, Marker, Quadrupole
from laura.models.elementList import MachineModel
from laura.models.physical import PhysicalElement

# ---------------------------------------------------------------------------
# fixtures
# ---------------------------------------------------------------------------


def drift(name, length, **physical):
    return Drift(
        name=name,
        hardware_class="Drift",
        machine_area="S",
        physical={"length": length, **physical},
    )


def quad(name, length=0.1, **physical):
    return Quadrupole(
        name=name,
        hardware_class="Magnet",
        machine_area="S",
        magnetic={"magnetic_length": length, "k1l": 0.1},
        physical={"length": length, **physical},
    )


def bend(name, length=1.0, angle=0.3, **physical):
    return Dipole(
        name=name,
        hardware_class="Magnet",
        machine_area="S",
        magnetic={"magnetic_length": length, "k0l": angle},
        physical={"length": length, **physical},
    )


def marker(name, **physical):
    return Marker(name=name, machine_area="S", physical={"length": 0.0, **physical})


def machine(elements, order=None):
    """Build a one-section MachineModel, discarding the no-layouts warning."""
    order = order or [e.name for e in elements]
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", message="No layouts")
        return MachineModel(
            elements={e.name: e for e in elements},
            section={"sections": {"S": {"elements": order}}},
        )


def caught(elements, order=None):
    """``(machine, [warning messages])`` -- the no-layouts noise filtered out."""
    with warnings.catch_warnings(record=True) as records:
        warnings.simplefilter("always")
        m = machine(elements, order)
    return m, [str(r.message) for r in records if "No layouts" not in str(r.message)]


def s_values(m, names):
    return [m.elements[n].physical.s for n in names]


# ---------------------------------------------------------------------------
# the flag the whole feature rests on
# ---------------------------------------------------------------------------


class TestPositionStated:
    """``middle`` gets an origin default at construction, so 'no position' and
    'positioned at the origin' are indistinguishable afterwards.  The flag is
    taken before that default lands."""

    @pytest.mark.parametrize(
        "kwargs",
        [
            {},
            {"length": 0.5},
        ],
    )
    def test_unpositioned(self, kwargs):
        assert PhysicalElement(**kwargs)._position_stated is False

    @pytest.mark.parametrize(
        "kwargs",
        [
            {"middle": {"x": 0, "y": 0, "z": 1.0}},
            {"middle": {"x": 0, "y": 0, "z": 0.0}},  # deliberately at the origin
            {"centre": [0, 0, 3.0]},  # alias
            {"position": [0, 0, 3.0]},  # alias
            {"s": 2.0},
            {"s": 0.0},  # deliberately at s=0
            {"reference_placement": {"element": "Q0", "s_offset": 1.0}},
        ],
    )
    def test_positioned(self, kwargs):
        assert PhysicalElement(**kwargs)._position_stated is True

    def test_a_later_assignment_does_not_change_it(self):
        phys = PhysicalElement(length=0.5)
        phys.s = 3.0
        assert phys._position_stated is False


# ---------------------------------------------------------------------------
# the basic line
# ---------------------------------------------------------------------------


class TestSequentialLine:
    def test_five_element_line(self):
        """The case that used to resolve with everything at z=0."""
        m = machine(
            [quad("Q1"), drift("D1", 0.5), quad("Q2"), drift("D2", 1.0), quad("Q3")]
        )
        names = ["Q1", "D1", "Q2", "D2", "Q3"]
        assert s_values(m, names) == pytest.approx([0.05, 0.35, 0.65, 1.2, 1.75])
        assert [m.elements[n].physical.middle.z for n in names] == pytest.approx(
            [0.05, 0.35, 0.65, 1.2, 1.75]
        )

    def test_elements_abut_when_there_are_no_drifts(self):
        m = machine([quad("Q1", 0.2), quad("Q2", 0.4), quad("Q3", 0.6)])
        assert s_values(m, ["Q1", "Q2", "Q3"]) == pytest.approx([0.1, 0.4, 0.9])

    def test_drifts_survive_as_elements(self):
        """Decided against importer parity: the user named the drift, so
        ``machine['D1']`` must resolve."""
        m = machine([quad("Q1"), drift("D1", 0.5), quad("Q2")])
        assert "D1" in m.elements
        assert m.elements["D1"].physical.length == pytest.approx(0.5)

    def test_a_zero_length_marker_holds_its_place(self):
        m = machine([quad("Q1"), marker("MK"), quad("Q2")])
        assert m.sections["S"].order == ["Q1", "MK", "Q2"]
        assert s_values(m, ["Q1", "MK", "Q2"]) == pytest.approx([0.05, 0.1, 0.15])

    def test_consecutive_coincident_elements_keep_section_order(self):
        """Every s here is a sum of floats rather than a number anyone typed,
        so the sort has to tie-break on section order within a tolerance."""
        m = machine([quad("Q1"), marker("MK1"), marker("MK2"), quad("Q2")])
        assert m.sections["S"].order == ["Q1", "MK1", "MK2", "Q2"]
        assert s_values(m, ["MK1", "MK2"]) == pytest.approx([0.1, 0.1])


# ---------------------------------------------------------------------------
# the oracle
# ---------------------------------------------------------------------------


class TestAgreesWithExplicitS:
    """A sequential line and the same line written with explicit ``s`` must
    resolve identically.  Both go through ``_resolve_s_coordinates``, which is
    the point of normalising rather than adding a fourth coordinate system."""

    LINE = [
        ("quad", "Q1", 0.1),
        ("drift", "D1", 0.5),
        ("bend", "B1", 1.0),
        ("drift", "D2", 0.5),
        ("quad", "Q2", 0.1),
    ]

    def _build(self, explicit):
        makers = {"quad": quad, "drift": drift, "bend": bend}
        elements, cumulative = [], 0.0
        for kind, name, length in self.LINE:
            cumulative += length
            extra = {"s": cumulative, "s_point": "end"} if explicit else {}
            elements.append(makers[kind](name, length, **extra))
        return machine(elements)

    @pytest.mark.parametrize("name", ["Q1", "D1", "B1", "D2", "Q2"])
    def test_positions_match_through_a_bend(self, name):
        sequential = self._build(explicit=False).elements[name].physical
        explicit = self._build(explicit=True).elements[name].physical
        assert np.array(sequential.middle.array) == pytest.approx(
            np.array(explicit.middle.array), abs=1e-15
        )
        assert sequential.s == pytest.approx(explicit.s)

    def test_the_bend_actually_curves(self):
        """Guards the oracle: two identically-wrong answers would also agree."""
        phys = self._build(explicit=False).elements["Q2"].physical
        assert abs(phys.middle.x) > 0.3
        assert phys.middle.z < 2.15  # shorter in z than the arc length


# ---------------------------------------------------------------------------
# anchoring
# ---------------------------------------------------------------------------


class TestAnchoring:
    def test_a_leading_s_anchors_the_line(self):
        m, messages = caught(
            [quad("Q1", 0.1, s=12.0, s_point="start"), drift("D1", 0.5), quad("Q2")]
        )
        assert s_values(m, ["Q1", "D1", "Q2"]) == pytest.approx([12.05, 12.35, 12.65])
        assert messages == []

    def test_a_mid_line_s_that_agrees_is_silent(self):
        m, messages = caught(
            [quad("Q1"), drift("D1", 0.5), quad("Q2", 0.1, s=0.6, s_point="start")]
        )
        assert s_values(m, ["Q1", "D1", "Q2"]) == pytest.approx([0.05, 0.35, 0.65])
        assert messages == []

    def test_a_mid_line_s_that_disagrees_re_anchors_and_warns(self):
        m, messages = caught(
            [
                quad("Q1"),
                drift("D1", 0.5),
                quad("Q2", 0.1, s=5.0, s_point="start"),
                quad("Q3"),
            ]
        )
        assert s_values(m, ["Q2", "Q3"]) == pytest.approx([5.05, 5.15])
        assert len(messages) == 1
        assert "Q2" in messages[0] and "5" in messages[0] and "0.6" in messages[0]

    def test_an_xyz_anchor_is_still_rejected(self):
        """Converting a stated xyz back to an arc length needs the trajectory
        that does not exist yet, so the anchor has to be written with ``s``."""
        with pytest.raises(ValueError, match="anchor it with 's'"):
            machine(
                [quad("Q1", 0.1, middle=[0, 0, 12.0]), drift("D1", 0.5), quad("Q2")]
            )


# ---------------------------------------------------------------------------
# repeated names
# ---------------------------------------------------------------------------


class TestRepeatedNames:
    ORDER = ["Q1", "D", "Q2", "D", "Q3", "D"]

    def _fodo(self):
        return caught(
            [quad("Q1"), drift("D", 0.5), quad("Q2"), quad("Q3")], order=self.ORDER
        )

    def test_each_occurrence_gets_its_own_element(self):
        m, _ = self._fodo()
        assert m.sections["S"].order == ["Q1", "D.1", "Q2", "D.2", "Q3", "D.3"]
        assert {"D.1", "D.2", "D.3"} <= set(m.elements)

    def test_each_copy_is_placed_separately(self):
        m, _ = self._fodo()
        assert s_values(m, ["D.1", "D.2", "D.3"]) == pytest.approx([0.35, 0.95, 1.55])

    def test_the_original_bare_name_is_retired(self):
        m, _ = self._fodo()
        assert "D" not in m.elements

    def test_it_says_so(self):
        _, messages = self._fodo()
        assert any("D.1 (from D)" in message for message in messages)

    def test_a_name_used_once_is_left_alone(self):
        m, messages = caught([quad("Q1"), drift("D1", 0.5), quad("Q2")])
        assert m.sections["S"].order == ["Q1", "D1", "Q2"]
        assert messages == []


# ---------------------------------------------------------------------------
# sections that are not sequential are untouched
# ---------------------------------------------------------------------------


class TestNonSequentialSectionsUnchanged:
    def test_a_section_written_entirely_with_s(self):
        m = machine([quad("Q1", 0.1, s=1.0), quad("Q2", 0.1, s=2.0)])
        assert s_values(m, ["Q1", "Q2"]) == pytest.approx([1.0, 2.0])

    def test_a_section_written_entirely_with_middle(self):
        m = machine(
            [quad("Q1", 0.1, middle=[0, 0, 1.0]), quad("Q2", 0.1, middle=[0, 0, 2.0])]
        )
        assert [m.elements[n].physical.middle.z for n in ["Q1", "Q2"]] == (
            pytest.approx([1.0, 2.0])
        )

    def test_repeated_names_are_not_numbered_outside_a_sequential_section(self):
        m, messages = caught(
            [quad("Q1", 0.1, s=1.0), quad("Q2", 0.1, s=2.0)], order=["Q1", "Q2", "Q1"]
        )
        assert m.sections["S"].order == ["Q1", "Q2", "Q1"]
        assert messages == []


# ---------------------------------------------------------------------------
# an element shared between sections
# ---------------------------------------------------------------------------


class TestSharedElements:
    def test_an_element_in_two_sections_is_placed_once(self):
        """A name holds one placement, so the second section resolves against
        an element that already states a position and does not re-place it."""
        elements = [quad("Q1"), drift("D1", 0.5), quad("Q2")]
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", message="No layouts")
            m = MachineModel(
                elements={e.name: e for e in elements},
                section={
                    "sections": {
                        "A": {"elements": ["Q1", "D1", "Q2"]},
                        "B": {"elements": ["Q2"]},
                    }
                },
            )
        assert m.elements["Q2"].physical.s == pytest.approx(0.65)


# ---------------------------------------------------------------------------
# failures and warnings
# ---------------------------------------------------------------------------


class TestFailures:
    """The design called for placement-time guards on missing, negative and NaN
    lengths.  They turned out to be unreachable: ``length`` is a non-nullable,
    ``ge=0`` schema slot, so the accumulator can only ever be handed a real
    length.  These pin that, so the guards stay unnecessary."""

    @pytest.mark.parametrize("length", [-0.5, float("nan")])
    def test_the_schema_refuses_an_unplaceable_length(self, length):
        with pytest.raises(ValidationError, match="greater than or equal to 0"):
            drift("D1", length)

    def test_the_schema_refuses_a_missing_length(self):
        with pytest.raises(ValidationError, match="valid number"):
            PhysicalElement(length=None)

    def test_a_zero_length_element_is_fine(self):
        m = machine([quad("Q1"), drift("D0", 0.0), quad("Q2")])
        assert s_values(m, ["Q1", "D0", "Q2"]) == pytest.approx([0.05, 0.1, 0.15])


# ---------------------------------------------------------------------------
# interaction with element inheritance
# ---------------------------------------------------------------------------


class TestWithInheritance:
    def test_a_line_of_children_of_one_template_is_placed_sequentially(self):
        """Position is never inherited, so children of a shared template all
        arrive unpositioned -- which is exactly the sequential trigger."""
        from laura.Importers.YAML_Loader import resolve_inheritance

        namespace = {
            "STD_QUAD": {
                "name": "STD_QUAD",
                "hardware_type": "Quadrupole",
                "hardware_class": "Magnet",
                "machine_area": "S",
                "magnetic": {"magnetic_length": 0.1, "k1l": 0.1},
                # the template is itself placed; that must not come down
                "physical": {"length": 0.1, "s": 4.0},
            }
        }
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            merged = [
                resolve_inheritance(
                    {"name": name, "inherits_from": "STD_QUAD"}, namespace
                )
                for name in ("Q1", "Q2")
            ]

        assert all("s" not in child["physical"] for child in merged)
        assert all(child["physical"]["length"] == 0.1 for child in merged)

        elements = [
            Quadrupole(**{k: v for k, v in child.items() if k != "inherits_from"})
            for child in merged
        ]
        assert all(e.physical._position_stated is False for e in elements)

        m = machine([elements[0], drift("D1", 0.5), elements[1]])
        assert s_values(m, ["Q1", "D1", "Q2"]) == pytest.approx([0.05, 0.35, 0.65])
