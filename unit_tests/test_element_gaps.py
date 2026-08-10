"""Additional tests for laura.models.element covering branches not exercised by
unit_tests/models/test_element.py or unit_tests/test_element_attrs.py: baseElement
validator/helper branches, PhysicalBaseElement/Magnet angle properties, and the
model_post_init nested-default wiring of the many element subclasses that aren't
otherwise constructed anywhere in the suite."""

import pytest
from pydantic import ValidationError

from laura.models.element import (
    baseElement,
    PhysicalBaseElement,
    Magnet,
    Dipole,
    _coerce_nested_model,
    TwissMatch,
    Beam_Position_Monitor,
    Beam_Arrival_Monitor,
    Bunch_Length_Monitor,
    Camera,
    Screen,
    Laser,
    LaserEnergyMeter,
    LaserHalfWavePlate,
    Plasma,
    Lighting,
    RFCavity,
    Wakefield,
    RFDeflectingCavity,
    RFModulator,
    RFHeartbeat,
    Shutter,
    Valve,
)


def _base(**kwargs):
    return baseElement(
        name="B1", hardware_class="Generic", hardware_type="HT", machine_area="MA", **kwargs
    )


class TestBaseElementAliasValidator:
    def test_alias_from_dict(self):
        b = _base(alias={"aliases": ["a1", "a2"]})
        assert b.alias == ["a1", "a2"]

    def test_alias_from_none(self):
        b = _base(alias=None)
        assert b.alias == []

    def test_alias_invalid_type_raises(self):
        with pytest.raises(ValidationError):
            _base(alias=5)


class TestCoerceNestedModel:
    """`_coerce_nested_model` is a standalone helper backing
    PhysicalBaseElement.model_post_init's `physical` coercion; test it directly
    since pydantic's own field validation means the dict/foreign-instance
    branches are never reached via normal Element construction."""

    def test_none_uses_factory(self):
        from laura.models.physical import PhysicalElement

        result = _coerce_nested_model(None, PhysicalElement)
        assert isinstance(result, PhysicalElement)

    def test_existing_instance_passthrough(self):
        from laura.models.physical import PhysicalElement

        pe = PhysicalElement(length=1.0)
        assert _coerce_nested_model(pe, PhysicalElement) is pe

    def test_foreign_model_instance_converted_via_model_dump(self):
        from laura.models.physical import PhysicalElement
        from laura.models._generated import _PhysicalElementBase

        base = _PhysicalElementBase(length=2.0)
        result = _coerce_nested_model(base, PhysicalElement)
        assert isinstance(result, PhysicalElement)
        assert result.length == 2.0

    def test_dict_converted(self):
        from laura.models.physical import PhysicalElement

        result = _coerce_nested_model({"length": 3.0}, PhysicalElement)
        assert isinstance(result, PhysicalElement)
        assert result.length == 3.0

    def test_unsupported_type_passthrough(self):
        from laura.models.physical import PhysicalElement

        assert _coerce_nested_model(5, PhysicalElement) == 5


class TestBaseElementEscapeStringList:
    def test_nonempty(self):
        b = _base()
        assert b.escape_string_list(["a", "b"]) == "a,b"

    def test_empty(self):
        b = _base()
        assert b.escape_string_list([]) == ""


class TestBaseElementYamlFilename:
    def test_yaml_filename(self):
        b = _base()
        assert b.YAML_filename.endswith("B1.yaml")


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

    def test_bend_angle_reflects_dipole_strength(self):
        d = Dipole(name="D1", machine_area="MA", magnetic={"k0l": 0.2, "length": 1.0})
        assert d.bend_angle.theta == pytest.approx(0.2)

    def test_end_angle_is_start_plus_bend(self):
        d = Dipole(name="D1", machine_area="MA", magnetic={"k0l": 0.2, "length": 1.0})
        assert d.end_angle == pytest.approx(d.start_angle.theta + 0.2)


class TestElementSubclassNestedDefaults:
    """These subclasses are otherwise never constructed anywhere in the suite;
    each just wires a nested-default in model_post_init via _ensure_nested_default."""

    @pytest.mark.parametrize(
        "cls,attr",
        [
            (TwissMatch, "simulation"),
            (Beam_Position_Monitor, "diagnostic"),
            (Beam_Arrival_Monitor, "diagnostic"),
            (Bunch_Length_Monitor, "diagnostic"),
            (Camera, "diagnostic"),
            (Screen, "diagnostic"),
            (Laser, "laser"),
            (LaserEnergyMeter, "laser"),
            (LaserHalfWavePlate, "laser"),
            (Lighting, "lights"),
            (RFCavity, "cavity"),
            (RFDeflectingCavity, "cavity"),
            (RFModulator, "modulator"),
            (RFHeartbeat, "heartbeat"),
            (Shutter, "shutter"),
            (Valve, "valve"),
        ],
    )
    def test_nested_default_created(self, cls, attr):
        instance = cls(name="X1", machine_area="MA")
        assert getattr(instance, attr) is not None

    def test_wakefield_creates_both_defaults(self):
        w = Wakefield(name="W1", machine_area="MA")
        assert w.cavity is not None
        assert w.simulation is not None

    def test_plasma_creates_both_defaults(self):
        p = Plasma(name="PL1", machine_area="MA")
        assert p.simulation is not None
        assert p.plasma is not None

    def test_rf_deflecting_cavity_creates_both_defaults(self):
        rfd = RFDeflectingCavity(name="RFD1", machine_area="MA")
        assert rfd.cavity is not None
        assert rfd.simulation is not None
