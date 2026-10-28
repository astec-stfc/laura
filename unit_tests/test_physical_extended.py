"""Extended tests for laura.models.physical — Position, Rotation, PhysicalElement."""

import pytest
import numpy as np

from laura.models.physical import (
    Position,
    Rotation,
    ElementError,
    ElementSurvey,
    PhysicalElement,
    ReferencePlacement,
)
from laura.models.trajectory import Trajectory
from laura.models.element import Dipole


class TestPositionExtended:
    def test_from_list(self):
        p = Position.from_list([1.0, 2.0, 3.0])
        assert p.x == 1.0
        assert p.y == 2.0
        assert p.z == 3.0

    def test_from_values(self):
        p = Position.from_values(4.0, 5.0, 6.0)
        assert p.x == 4.0
        assert p.z == 6.0

    def test_array_property(self):
        p = Position(x=1, y=2, z=3)
        np.testing.assert_array_equal(p.array, [1, 2, 3])

    def test_iter(self):
        p = Position(x=1, y=2, z=3)
        assert list(p) == [1.0, 2.0, 3.0]

    def test_add(self):
        p1 = Position(x=1, y=2, z=3)
        p2 = Position(x=10, y=20, z=30)
        result = p1 + p2
        assert result == Position(x=11, y=22, z=33)

    def test_sub(self):
        p1 = Position(x=10, y=20, z=30)
        p2 = Position(x=1, y=2, z=3)
        result = p1 - p2
        assert result == Position(x=9, y=18, z=27)

    def test_radd(self):
        p1 = Position(x=1, y=2, z=3)
        p2 = Position(x=4, y=5, z=6)
        # radd is called when right operand supports it
        result = p2.__radd__(p1)
        assert result == Position(x=5, y=7, z=9)

    def test_rsub(self):
        p1 = Position(x=10, y=20, z=30)
        p2 = Position(x=1, y=2, z=3)
        result = p2.__rsub__(p1)
        assert result == Position(x=9, y=18, z=27)

    def test_dot_with_position(self):
        p1 = Position(x=1, y=0, z=0)
        p2 = Position(x=0, y=1, z=0)
        assert p1.dot(p2) == 0.0

    def test_dot_with_list(self):
        p = Position(x=1, y=2, z=3)
        assert p.dot([1, 1, 1]) == 6.0

    def test_vector_angle(self):
        p1 = Position(x=0, y=0, z=5)
        p2 = Position(x=0, y=0, z=0)
        result = p1.vector_angle(p2, [0, 0, 1])
        assert result == pytest.approx(5.0)

    def test_length(self):
        p = Position(x=3, y=4, z=0)
        assert p.length() == pytest.approx(5.0)

    def test_eq_zero(self):
        p = Position()
        assert p == 0

    def test_eq_none(self):
        p = Position()
        assert p == None  # noqa: E711

    def test_neq_nonzero(self):
        p = Position(x=1, y=0, z=0)
        assert p != 0

    def test_json_serialization(self):
        p = Position(x=1, y=2, z=3)
        assert p.model_dump(mode="json") == [1.0, 2.0, 3.0]

    def test_vector_angle_with_list_other(self):
        p = Position(x=0, y=0, z=5)
        result = p.vector_angle([0, 0, 0], [0, 0, 1])
        assert result == pytest.approx(5.0)


class TestRotationExtended:
    def test_from_list(self):
        r = Rotation.from_list([0.1, 0.2, 0.3])
        assert r.phi == pytest.approx(0.1)
        assert r.psi == pytest.approx(0.2)
        assert r.theta == pytest.approx(0.3)

    def test_add(self):
        r1 = Rotation(phi=0.1, psi=0.2, theta=0.3)
        r2 = Rotation(phi=0.4, psi=0.5, theta=0.6)
        result = r1 + r2
        assert result.phi == pytest.approx(0.5)
        assert result.psi == pytest.approx(0.7)
        assert result.theta == pytest.approx(0.9)

    def test_sub(self):
        r1 = Rotation(phi=0.5, psi=0.7, theta=0.9)
        r2 = Rotation(phi=0.1, psi=0.2, theta=0.3)
        result = r1 - r2
        assert result.phi == pytest.approx(0.4)

    def test_abs(self):
        r = Rotation(phi=-0.1, psi=-0.2, theta=-0.3)
        result = abs(r)
        assert result.phi == pytest.approx(0.1)
        assert result.psi == pytest.approx(0.2)
        assert result.theta == pytest.approx(0.3)

    def test_gt_float(self):
        r = Rotation(phi=0.5, psi=0.0, theta=0.0)
        assert r > 0.4

    def test_gt_rotation(self):
        r1 = Rotation(phi=0.5, psi=0.0, theta=0.0)
        r2 = Rotation(phi=0.4, psi=0.0, theta=0.0)
        assert r1 > r2

    def test_constrained_range(self):
        """phi, psi, theta must be in [-pi, pi]."""
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            Rotation(phi=4.0)  # > pi

    def test_eq_zero(self):
        r = Rotation()
        assert r == 0

    def test_iter(self):
        r = Rotation(phi=0.1, psi=0.2, theta=0.3)
        assert list(r) == pytest.approx([0.1, 0.2, 0.3])

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


class TestElementError:
    def test_from_lists(self):
        err = ElementError(position=[1, 2, 3], rotation=[0.1, 0.2, 0.3])
        assert err.position == Position(x=1, y=2, z=3)
        assert isinstance(err.rotation, Rotation)

    def test_from_dicts(self):
        err = ElementError(
            position={"x": 1.0, "y": 2.0, "z": 3.0},
            rotation={"phi": 0.1, "psi": 0.2, "theta": 0.3},
        )
        assert err.position.x == 1.0

    def test_eq_zero(self):
        err = ElementError()
        assert err == 0

    def test_str_none_when_zero(self):
        err = ElementError()
        assert str(err) == str(None)

    def test_repr(self):
        err = ElementError()
        assert "ElementError" in repr(err)


class TestElementSurvey:
    def test_inherits_element_error(self):
        assert issubclass(ElementSurvey, ElementError)


class TestPhysicalElementExtended:
    def test_validate_middle_from_float(self):
        pe = PhysicalElement(middle=5.0)
        assert pe.middle == Position(x=0, y=0, z=5.0)

    def test_validate_middle_from_list_3(self):
        pe = PhysicalElement(middle=[1.0, 2.0, 3.0])
        assert pe.middle == Position(x=1, y=2, z=3)

    def test_validate_middle_from_list_2(self):
        pe = PhysicalElement(middle=[1.0, 3.0])
        assert pe.middle == Position(x=1, y=0, z=3)

    def test_validate_middle_from_dict(self):
        pe = PhysicalElement(middle={"x": 1.0, "y": 2.0, "z": 3.0})
        assert pe.middle.x == 1.0

    def test_validate_rotation_from_float(self):
        pe = PhysicalElement(rotation=0.5)
        assert pe.rotation.theta == pytest.approx(0.5)

    def test_validate_rotation_from_list(self):
        pe = PhysicalElement(rotation=[0.1, 0.2, 0.3])
        assert pe.rotation.phi == pytest.approx(0.1)

    def test_start_straight_element(self):
        pe = PhysicalElement(
            length=2.0,
            middle=Position(x=0, y=0, z=5),
        )
        start = pe.start
        assert start.z == pytest.approx(4.0)

    def test_end_straight_element(self):
        pe = PhysicalElement(
            length=2.0,
            middle=Position(x=0, y=0, z=5),
        )
        end = pe.end
        assert end.z == pytest.approx(6.0)

    def test_start_end_zero_length(self):
        pe = PhysicalElement(
            length=0.0,
            middle=Position(x=0, y=0, z=3),
        )
        assert pe.start.z == pytest.approx(3.0)
        assert pe.end.z == pytest.approx(3.0)

    def test_rotation_matrix_identity(self):
        pe = PhysicalElement()
        np.testing.assert_array_almost_equal(pe.rotation_matrix, np.eye(3))

    def test_rotation_matrix_with_yaw(self):
        pe = PhysicalElement(rotation=Rotation(theta=np.pi / 2))
        r = pe.rotation_matrix
        # For yaw=pi/2: [cos, 0, -sin; 0, 1, 0; sin, 0, cos]
        expected_ry = np.array([[0, 0, -1], [0, 1, 0], [1, 0, 0]])
        np.testing.assert_array_almost_equal(r, expected_ry)

    def test_rotated_position(self):
        pe = PhysicalElement()
        result = pe.rotated_position([1, 0, 0])
        np.testing.assert_array_almost_equal(result, [1, 0, 0])

    def test_str_nonempty(self):
        pe = PhysicalElement(
            length=1.0,
            middle=Position(x=0, y=0, z=5),
        )
        s = str(pe)
        assert len(s) > 0

    def test_repr(self):
        pe = PhysicalElement()
        assert "PhysicalElement" in repr(pe)

    def test_datum_from_int(self):
        pe = PhysicalElement(datum=0)
        assert pe.datum == Position(x=0, y=0, z=0)


class TestRotationMatrixFollowsRotation:
    """The matrix is memoised on the angles it was built from, not on first access."""

    @staticmethod
    def _drift():
        from laura.models.element import Drift

        return Drift(
            name="D",
            hardware_class="Drift",
            machine_area="S",
            physical={"length": 1.0},
        ).physical

    def test_a_whole_object_assignment_is_picked_up(self):
        from laura.models.physical import Rotation

        phys = self._drift()
        assert phys.end.z == pytest.approx(0.5)  # reads, and memoises, the matrix
        phys.rotation = Rotation(theta=1.0)
        assert phys.end.z == pytest.approx(0.5 * np.cos(1.0))

    def test_an_in_place_mutation_is_picked_up(self):
        # an invalidation hook on __setattr__ would miss this one
        phys = self._drift()
        assert phys.end.z == pytest.approx(0.5)
        phys.rotation.theta = 1.0
        assert phys.end.z == pytest.approx(0.5 * np.cos(1.0))

    def test_global_rotation_counts_too(self):
        from laura.models.physical import Rotation

        phys = self._drift()
        assert phys.end.z == pytest.approx(0.5)
        phys.global_rotation = Rotation(theta=1.0)
        assert phys.end.z == pytest.approx(0.5 * np.cos(1.0))

    def test_an_unchanged_rotation_returns_the_same_object(self):
        # the memo still has to memoise
        phys = self._drift()
        assert phys.rotation_matrix is phys.rotation_matrix


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
    """ValueError branches of the ``_coerce_*`` helpers, via the public models."""

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
