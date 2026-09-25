"""Additional tests for laura.models.physical covering branches not exercised by
test_physical_extended.py: coercion-helper error paths, JSON serialisation,
dead-typo dunders reached via direct call, s<->middle trajectory sync, and
ReferencePlacement offset coercion."""

import numpy as np
import pytest

from laura.models.physical import (
    Position,
    Rotation,
    ElementError,
    PhysicalElement,
    ReferencePlacement,
)
from laura.models.trajectory import Trajectory
from laura.models.element import Dipole


class TestPositionJsonAndDunders:
    def test_json_serialization(self):
        p = Position(x=1, y=2, z=3)
        assert p.model_dump(mode="json") == [1.0, 2.0, 3.0]

    def test_vector_angle_with_list_other(self):
        p = Position(x=0, y=0, z=5)
        result = p.vector_angle([0, 0, 0], [0, 0, 1])
        assert result == pytest.approx(5.0)


class TestRotationJsonAndDunders:
    def test_json_serialization(self):
        r = Rotation(phi=0.1, psi=0.2, theta=0.3)
        assert r.model_dump(mode="json") == pytest.approx([0.1, 0.2, 0.3])

    def test_array_property(self):
        r = Rotation(phi=0.1, psi=0.2, theta=0.3)
        np.testing.assert_array_almost_equal(r.array, [0.1, 0.2, 0.3])

    def test_from_values(self):
        r = Rotation.from_values(0.1, 0.2, 0.3)
        assert (r.phi, r.psi, r.theta) == pytest.approx((0.1, 0.2, 0.3))

    def test_radd_direct_call(self):
        r1 = Rotation(phi=0.1, psi=0.2, theta=0.3)
        r2 = Rotation(phi=1.0, psi=1.0, theta=1.0)
        result = r1.__radd__(r2)
        assert result.phi == pytest.approx(1.1)

    def test_rsub_direct_call(self):
        r1 = Rotation(phi=0.1, psi=0.2, theta=0.3)
        r2 = Rotation(phi=1.0, psi=1.0, theta=1.0)
        result = r1.__rsub__(r2)
        assert result.phi == pytest.approx(0.9)

    def test_gt_list(self):
        r = Rotation(phi=0.5, psi=0.5, theta=0.5)
        assert r > [0.0, 0.0, 0.0]

    def test_gt_rotation_zero(self):
        r = Rotation(phi=0.5, psi=0.0, theta=0.0)
        assert r > Rotation(phi=0.0, psi=0.0, theta=0.0)


@pytest.mark.parametrize(
    "model, field",
    [
        (PhysicalElement, "middle"),
        (PhysicalElement, "datum"),
        (PhysicalElement, "rotation"),
        (ElementError, "position"),
        (ElementError, "rotation"),
    ],
)
class TestCoercionHelperErrorPaths:
    """The ValueError branches of the module-level _coerce_* helpers, through the
    public models that call them. Every vector-valued field shares the helpers, so
    the cases are the field's, not the model's."""

    @pytest.mark.parametrize("bad", [[1], object()], ids=["short_list", "wrong_type"])
    def test_rejects_anything_that_is_not_three_numbers(self, model, field, bad):
        with pytest.raises(ValueError, match=f"{field} should be a number or a list"):
            model(**{field: bad})

    def test_rejects_a_dict_without_the_component_keys(self, model, field):
        with pytest.raises(ValueError, match=f"setting {field} as dictionary must"):
            model(**{field: {"bad": 1}})


class TestCoercionHelperAcceptedForms:
    def test_list_and_dict_both_build_the_same_position(self):
        assert (
            PhysicalElement(datum=[1, 2, 3]).datum
            == PhysicalElement(datum={"x": 1.0, "y": 2.0, "z": 3.0}).datum
            == Position(x=1, y=2, z=3)
        )

    def test_an_instance_is_kept_rather_than_rebuilt(self):
        pos, rot = Position(x=1, y=2, z=3), Rotation(phi=0.1, psi=0.2, theta=0.3)
        error = ElementError(position=pos, rotation=rot)
        assert error.position is pos and error.rotation is rot

    def test_element_error_str_nonzero(self):
        ee = ElementError(position=[1, 2, 3])
        assert str(ee) != str(None)


class TestPhysicalAngleDegradesOnUndefinedFunctional:
    def test_undefined_bend_angle_degrades_to_zero(self):
        d = Dipole(
            name="D1",
            machine_area="A",
            magnetic={"k0l": "undefined_ref", "length": 1.0},
            physical={"length": 1.0, "middle": {"x": 0, "y": 0, "z": 1}},
        )
        assert d.physical._physical_angle == 0.0


class TestPhysicalElementSyncingGuard:
    def test_syncing_flag_settable_directly(self):
        pe = PhysicalElement()
        pe._syncing = True
        assert pe._syncing is True


class TestPhysicalElementTrajectorySync:
    def _traj(self):
        return Trajectory(
            np.array([0.0, 1.0, 2.0]),
            np.array([[0, 0, 0], [0, 0, 1], [0, 0, 2]], dtype=float),
            np.array([np.eye(3)] * 3),
        )

    def test_setting_middle_updates_s(self):
        pe = PhysicalElement(middle=Position(x=0, y=0, z=0))
        pe._trajectory = self._traj()
        pe.middle = Position(x=0, y=0, z=1.5)
        assert pe.s == pytest.approx(1.5)

    def test_setting_s_updates_middle(self):
        pe = PhysicalElement(middle=Position(x=0, y=0, z=0))
        pe._trajectory = self._traj()
        pe.s = 0.5
        assert pe.middle.z == pytest.approx(0.5)

    def test_model_dump_s_includes_s_point_when_not_middle(self):
        pe = PhysicalElement(middle=Position(x=0, y=0, z=0))
        pe._trajectory = self._traj()
        pe.middle = Position(x=0, y=0, z=0.5)
        pe.s_point = "start"
        dumped = pe.model_dump_s()
        assert dumped["s"] == pytest.approx(0.5)
        assert dumped["s_point"] == "start"
        assert "middle" not in dumped


class TestReferencePlacementOffsetCoercion:
    def test_offset_from_position_instance(self):
        rp = ReferencePlacement(element="foo", offset=Position(x=1, y=2, z=3))
        assert rp.offset == Position(x=1, y=2, z=3)

    def test_offset_from_dict(self):
        rp = ReferencePlacement(element="foo", offset={"x": 1.0, "y": 2.0, "z": 3.0})
        assert rp.offset == Position(x=1, y=2, z=3)

    def test_offset_bad_length_list_raises(self):
        with pytest.raises(ValueError, match="offset must be a list of 3 floats"):
            ReferencePlacement(element="foo", offset=[1])

    def test_offset_bad_dict_raises(self):
        with pytest.raises(ValueError, match="offset dict must contain"):
            ReferencePlacement(element="foo", offset={"bad": 1})

    def test_offset_unsupported_type_raises(self):
        with pytest.raises(ValueError, match="offset must be a list of 3 floats or"):
            ReferencePlacement(element="foo", offset=5)
