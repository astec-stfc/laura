"""Tests for element __getattr__ / __setattr__ transparent attribute resolution and cascading."""

import pytest
import numpy as np

from laura.models.element import (
    BaseElement,
    Element,
    PhysicalBaseElement,
    Quadrupole,
    Dipole,
    Sextupole,
    Marker,
    RFCavity,
    Drift,
    Magnet,
    flatten,
)
from laura.models.physical import Position, Rotation, PhysicalElement
from laura.models.magnetic import QuadrupoleMagnet, DipoleMagnet


# ---------------------------------------------------------------------------
# Helper: create a positioned quadrupole
# ---------------------------------------------------------------------------

def make_quad(name="Q1", k1l=0.5, z=1.0, length=0.3):
    return Quadrupole(
        name=name,
        machine_area="AREA",
        magnetic={"length": length, "k1l": k1l},
        physical={"length": length, "middle": {"x": 0.0, "y": 0.0, "z": z}},
    )


# ---------------------------------------------------------------------------
# Transparent nested attribute access (__getattr__)
# ---------------------------------------------------------------------------

class TestGetAttr:
    def test_access_nested_magnetic_field(self):
        q = make_quad(k1l=1.5)
        assert q.k1l == pytest.approx(1.5)

    def test_access_nested_physical_length(self):
        q = make_quad(length=0.4)
        # 'length' exists in both physical and magnetic; should raise ambiguity
        with pytest.raises(AttributeError, match="ambiguous"):
            _ = q.length

    def test_access_physical_middle(self):
        q = make_quad(z=2.5)
        assert q.middle == Position(x=0, y=0, z=2.5)

    def test_nonexistent_attr_raises(self):
        q = make_quad()
        with pytest.raises(AttributeError):
            _ = q.nonexistent_attribute

    def test_private_attr_raises(self):
        q = make_quad()
        with pytest.raises(AttributeError):
            _ = q._some_private_thing

    def test_access_element_simulation(self):
        m = Marker(
            name="M1",
            machine_area="AREA",
            hardware_class="Marker",
            physical={"middle": {"x": 0.0, "y": 0.0, "z": 0.0}},
        )
        # simulation should be accessible directly
        assert m.simulation is not None

    def test_access_rotation(self):
        q = make_quad()
        # rotation is ambiguous (physical.rotation, physical.error.rotation, etc.)
        with pytest.raises(AttributeError, match="ambiguous"):
            _ = q.rotation


# ---------------------------------------------------------------------------
# Transparent nested attribute setting (__setattr__)
# ---------------------------------------------------------------------------

class TestSetAttr:
    def test_set_nested_magnetic_k1l(self):
        q = make_quad(k1l=0.5)
        q.k1l = 2.0
        assert q.magnetic.k1l == pytest.approx(2.0)

    def test_set_direct_field(self):
        q = make_quad()
        q.name = "NEW_NAME"
        assert q.name == "NEW_NAME"

    def test_set_ambiguous_raises(self):
        q = make_quad()
        # 'length' is ambiguous (physical.length and magnetic.length)
        with pytest.raises(AttributeError, match="ambiguous"):
            q.length = 999

    def test_set_nonexistent_raises(self):
        """Setting an unknown field raises ValueError in Pydantic models."""
        q = make_quad()
        with pytest.raises((ValueError, Exception), match="no attribute|has no field|no such attribute"):
            q.totally_new_attr = 42


# ---------------------------------------------------------------------------
# flatten utility
# ---------------------------------------------------------------------------

class TestFlatten:
    def test_simple(self):
        d = {"a": {"b": 1, "c": 2}, "d": 3}
        flat = flatten(d)
        assert flat["a_b"] == 1
        assert flat["a_c"] == 2
        assert flat["d"] == 3

    def test_deeper_nesting(self):
        d = {"a": {"b": {"c": 99}}}
        flat = flatten(d)
        assert flat["a_b_c"] == 99

    def test_empty(self):
        assert flatten({}) == {}

    def test_with_custom_separator(self):
        d = {"x": {"y": 10}}
        flat = flatten(d, separator=".")
        assert flat["x.y"] == 10


# ---------------------------------------------------------------------------
# baseElement
# ---------------------------------------------------------------------------

class TestBaseElement:
    def test_default_hardware_model(self):
        be = BaseElement(
            name="E1",
            hardware_class="Generic",
            hardware_type="HT",
            machine_area="MA",
        )
        assert be.hardware_model == "Generic"

    def test_alias_from_string(self):
        be = BaseElement(
            name="E1",
            hardware_class="Generic",
            hardware_type="HT",
            machine_area="MA",
            alias="a1, a2",
        )
        assert list(be.alias) == ["a1", "a2"]

    def test_alias_from_list(self):
        be = BaseElement(
            name="E1",
            hardware_class="Generic",
            hardware_type="HT",
            machine_area="MA",
            alias=["x", "y"],
        )
        assert list(be.alias) == ["x", "y"]

    def test_alias_none_default(self):
        be = BaseElement(
            name="E1",
            hardware_class="Generic",
            hardware_type="HT",
            machine_area="MA",
        )
        # Default alias is an empty list
        assert be.alias == []

    def test_hardware_info(self):
        be = BaseElement(
            name="E1",
            hardware_class="Generic",
            hardware_type="HT",
            machine_area="MA",
        )
        assert be.hardware_info == {"class": "Generic", "type": "HT"}

    def test_flat(self):
        be = BaseElement(
            name="E1",
            hardware_class="Generic",
            hardware_type="HT",
            machine_area="MA",
        )
        flat = be.flat()
        assert "name" in flat
        assert flat["name"] == "E1"

    def test_is_subelement_false(self):
        be = BaseElement(
            name="E1",
            hardware_class="Generic",
            hardware_type="HT",
            machine_area="MA",
            subelement=False,
        )
        assert be.is_subelement() is False

    def test_is_subelement_true(self):
        be = BaseElement(
            name="E1",
            hardware_class="Generic",
            hardware_type="HT",
            machine_area="MA",
            subelement=True,
        )
        assert be.is_subelement() is True

    def test_is_subelement_string(self):
        be = BaseElement(
            name="E1",
            hardware_class="Generic",
            hardware_type="HT",
            machine_area="MA",
            subelement="PARENT_ELEM",
        )
        assert be.is_subelement() is True

    def test_subdirectory(self):
        be = BaseElement(
            name="E1",
            hardware_class="Generic",
            hardware_type="HT",
            machine_area="MA",
        )
        subdir = be.subdirectory
        assert "Generic" in subdir
        assert "HT" in subdir


# ---------------------------------------------------------------------------
# Element types – construction with nested dicts
# ---------------------------------------------------------------------------

class TestElementTypes:
    def test_quadrupole_from_dicts(self):
        q = Quadrupole(
            name="Q1",
            machine_area="SEC",
            magnetic={"length": 0.3, "k1l": -1.5},
            physical={"length": 0.3, "middle": {"x": 0.0, "y": 0.0, "z": 1.0}},
        )
        assert q.hardware_type == "Quadrupole"
        assert q.hardware_class == "Magnet"
        assert q.magnetic.k1l == pytest.approx(-1.5)
        assert q.physical.middle.z == pytest.approx(1.0)

    def test_dipole_from_dicts(self):
        d = Dipole(
            name="D1",
            machine_area="SEC",
            magnetic={"length": 1.0, "k0l": 0.1},
            physical={"length": 1.0, "middle": {"x": 0.0, "y": 0.0, "z": 5.0}},
        )
        assert d.hardware_type == "Dipole"
        assert d.magnetic.angle == pytest.approx(0.1)

    def test_sextupole(self):
        s = Sextupole(
            name="S1",
            machine_area="SEC",
            magnetic={"length": 0.1, "k2l": 10.0},
            physical={"length": 0.1, "middle": {"x": 0.0, "y": 0.0, "z": 2.0}},
        )
        assert s.hardware_type == "Sextupole"
        assert s.magnetic.k2l == pytest.approx(10.0)

    def test_marker_minimal(self):
        m = Marker(
            name="M1",
            machine_area="SEC",
            hardware_class="Marker",
            physical={"middle": {"x": 0.0, "y": 0.0, "z": 0.0}},
        )
        assert m.hardware_type == "Marker"
        assert m.physical.length == 0.0

    def test_drift(self):
        d = Drift(
            name="DR1",
            machine_area="SEC",
            hardware_class="Drift",
            physical={"length": 1.5, "middle": {"x": 0.0, "y": 0.0, "z": 5.0}},
        )
        assert d.hardware_type == "Drift"
        assert d.physical.length == pytest.approx(1.5)

    def test_rf_cavity_basic(self):
        cav = RFCavity(
            name="CAV1",
            machine_area="SEC",
            hardware_class="RF",
            cavity={"frequency": 1.3e9, "phase": 10.0},
            physical={"length": 1.0, "middle": {"x": 0.0, "y": 0.0, "z": 3.0}},
        )
        assert cav.hardware_type == "RFCavity"
        assert cav.cavity.frequency == pytest.approx(1.3e9)
        assert cav.cavity.phase == pytest.approx(10.0)


# ---------------------------------------------------------------------------
# Cascading rules on Magnet (physical angle <- magnetic angle)
# ---------------------------------------------------------------------------

class TestCascading:
    def test_dipole_bend_angle(self):
        d = Dipole(
            name="D1",
            machine_area="SEC",
            magnetic={"length": 1.0, "k0l": 0.05},
            physical={"length": 1.0, "middle": {"x": 0.0, "y": 0.0, "z": 5.0}},
        )
        # bend_angle is a property of Magnet reading magnetic.angle
        assert d.bend_angle.theta == pytest.approx(0.05)

    def test_quadrupole_bend_angle_zero(self):
        q = make_quad()
        # Quadrupole_Magnet has no angle property, so bend_angle
        # returns zero rotation (no bending).
        assert q.bend_angle == Rotation.from_list([0, 0, 0])
