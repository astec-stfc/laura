"""Tests for element attribute resolution, cascading and model helpers."""

import pytest
from pydantic import ValidationError

from laura.models.element import (
    BaseElement,
    PhysicalBaseElement,
    Quadrupole,
    Dipole,
    Sextupole,
    Marker,
    RFCavity,
    Drift,
    Magnet,
    flatten,
    PhotonMonitor,
    _coerce_nested_model,
    TwissMatch,
    BeamPositionMonitor,
    BeamArrivalMonitor,
    BunchLengthMonitor,
    Camera,
    Screen,
    Laser,
    LaserEnergyMeter,
    LaserHalfWavePlate,
    Plasma,
    Lighting,
    Wakefield,
    RFDeflectingCavity,
    RFModulator,
    RFHeartbeat,
    Shutter,
    Valve,
)
from laura.models.physical import Position, Rotation, PhysicalElement


def make_quad(name="Q1", k1l=0.5, z=1.0, length=0.3):
    return Quadrupole(
        name=name,
        machine_area="AREA",
        magnetic={"length": length, "k1l": k1l},
        physical={"length": length, "middle": {"x": 0.0, "y": 0.0, "z": z}},
    )


class TestGetAttr:
    def test_access_nested_magnetic_field(self):
        q = make_quad(k1l=1.5)
        assert q.k1l == pytest.approx(1.5)

    def test_access_nested_physical_length(self):
        q = make_quad(length=0.4)
        # 'length' is in both physical and magnetic
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
        assert m.simulation is not None

    def test_access_rotation(self):
        q = make_quad()
        # rotation is ambiguous (physical.rotation, physical.error.rotation, etc.)
        with pytest.raises(AttributeError, match="ambiguous"):
            _ = q.rotation


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
        q = make_quad()
        with pytest.raises((ValueError, Exception), match="no attribute|has no field|no such attribute"):
            q.totally_new_attr = 42


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


def _base(**kwargs):
    return BaseElement(
        name="B1", hardware_class="Generic", hardware_type="HT", machine_area="MA", **kwargs
    )


class TestBaseElement:
    def test_default_hardware_model(self):
        assert _base().hardware_model == "Generic"

    @pytest.mark.parametrize(
        "kwargs, expected",
        [
            ({"alias": "a1, a2"}, ["a1", "a2"]),
            ({"alias": ["x", "y"]}, ["x", "y"]),
            ({"alias": {"aliases": ["a1", "a2"]}}, ["a1", "a2"]),
            ({"alias": None}, []),
            ({}, []),
        ],
        ids=["string", "list", "dict", "none", "default"],
    )
    def test_alias(self, kwargs, expected):
        assert list(_base(**kwargs).alias) == expected

    def test_alias_invalid_type_raises(self):
        with pytest.raises(ValidationError):
            _base(alias=5)

    def test_hardware_info(self):
        assert _base().hardware_info == {"class": "Generic", "type": "HT"}

    def test_flat(self):
        flat = _base().flat()
        assert "name" in flat
        assert flat["name"] == "B1"

    @pytest.mark.parametrize(
        "subelement, expected", [(False, False), (True, True), ("PARENT_ELEM", True)]
    )
    def test_is_subelement(self, subelement, expected):
        assert _base(subelement=subelement).is_subelement() is expected

    def test_subdirectory(self):
        subdir = _base().subdirectory
        assert "Generic" in subdir
        assert "HT" in subdir

    def test_escape_string_list(self):
        assert _base().escape_string_list(["a", "b"]) == "a,b"
        assert _base().escape_string_list([]) == ""

    def test_yaml_filename(self):
        assert _base().yaml_filename.endswith("B1.yaml")


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


class TestCascading:
    def test_dipole_bend_angle(self):
        d = Dipole(
            name="D1",
            machine_area="SEC",
            magnetic={"length": 1.0, "k0l": 0.05},
            physical={"length": 1.0, "middle": {"x": 0.0, "y": 0.0, "z": 5.0}},
        )
        assert d.bend_angle.theta == pytest.approx(0.05)

    def test_quadrupole_bend_angle_zero(self):
        q = make_quad()
        # Quadrupole_Magnet has no angle, so bend_angle is zero.
        assert q.bend_angle == Rotation.from_list([0, 0, 0])


class TestCoerceNestedModel:
    """Tested directly: pydantic validation makes the dict/foreign-instance branches
    unreachable via Element construction.
    """

    def test_none_uses_factory(self):
        result = _coerce_nested_model(None, PhysicalElement)
        assert isinstance(result, PhysicalElement)

    def test_existing_instance_passthrough(self):
        pe = PhysicalElement(length=1.0)
        assert _coerce_nested_model(pe, PhysicalElement) is pe

    def test_foreign_model_instance_converted_via_model_dump(self):
        from laura.models._generated import _PhysicalElementBase

        base = _PhysicalElementBase(length=2.0)
        result = _coerce_nested_model(base, PhysicalElement)
        assert isinstance(result, PhysicalElement)
        assert result.length == 2.0

    def test_dict_converted(self):
        result = _coerce_nested_model({"length": 3.0}, PhysicalElement)
        assert isinstance(result, PhysicalElement)
        assert result.length == 3.0

    def test_unsupported_type_passthrough(self):
        assert _coerce_nested_model(5, PhysicalElement) == 5


class TestPhysicalBaseElementAngles:
    def test_bend_angle_is_zero_rotation(self):
        p = PhysicalBaseElement(name="P1", hardware_class="Generic", hardware_type="HT", machine_area="MA")
        assert p.bend_angle.theta == 0.0

    def test_start_angle_sums_rotations(self):
        p = PhysicalBaseElement(
            name="P1", hardware_class="Generic", hardware_type="HT", machine_area="MA",
            physical={"rotation": {"theta": 0.1}, "global_rotation": {"theta": 0.2}},
        )
        assert p.start_angle.theta == pytest.approx(0.3)

    def test_end_angle_equals_start_angle(self):
        p = PhysicalBaseElement(name="P1", hardware_class="Generic", hardware_type="HT", machine_area="MA")
        assert p.end_angle == p.start_angle


class TestMagnetAngles:
    def test_bend_angle_zero_without_magnetic_angle(self):
        m = Magnet(name="M1", machine_area="MA", hardware_type="Generic")
        assert m.bend_angle.theta == 0.0

    def test_end_angle_is_start_plus_bend(self):
        d = Dipole(name="D1", machine_area="MA", magnetic={"k0l": 0.2, "length": 1.0})
        assert d.end_angle == pytest.approx(d.start_angle.theta + 0.2)


class TestElementSubclassNestedDefaults:
    @pytest.mark.parametrize(
        "cls,attr",
        [
            (TwissMatch, "simulation"),
            (BeamPositionMonitor, "diagnostic"),
            (BeamArrivalMonitor, "diagnostic"),
            (BunchLengthMonitor, "diagnostic"),
            (Camera, "diagnostic"),
            (Screen, "diagnostic"),
            (Laser, "laser"),
            (LaserEnergyMeter, "laser"),
            (LaserHalfWavePlate, "laser"),
            (Lighting, "lights"),
            # cavity defaults are type-checked in test_cavity_nested_models.py
            (RFDeflectingCavity, "simulation"),
            (Wakefield, "simulation"),
            (Plasma, "simulation"),
            (Plasma, "plasma"),
            (RFModulator, "modulator"),
            (RFHeartbeat, "heartbeat"),
            (Shutter, "shutter"),
            (Valve, "valve"),
        ],
    )
    def test_nested_default_created(self, cls, attr):
        instance = cls(name="X1", machine_area="MA")
        assert getattr(instance, attr) is not None

    def test_photon_monitor_diagnostic_round_trips(self):
        pm = PhotonMonitor(
            name="PM1", machine_area="MA", diagnostic={"type": "Diode", "intensity": 3.0}
        )
        assert pm.model_dump()["diagnostic"] == {"type": "Diode", "intensity": 3.0}
        assert PhotonMonitor(name="PM1", machine_area="MA").diagnostic.type == "I0"
