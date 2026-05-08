"""Extended tests for laura.models.physical — Position, Rotation, PhysicalElement."""

import pytest
import numpy as np

from laura.models.physical import (
    Position,
    Rotation,
    ElementError,
    ElementSurvey,
    PhysicalElement,
)

# ---------------------------------------------------------------------------
# Position
# ---------------------------------------------------------------------------


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


# ---------------------------------------------------------------------------
# Rotation
# ---------------------------------------------------------------------------


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


# ---------------------------------------------------------------------------
# ElementError
# ---------------------------------------------------------------------------


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


# ---------------------------------------------------------------------------
# PhysicalElement
# ---------------------------------------------------------------------------


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
        R = pe.rotation_matrix
        # For yaw=pi/2: [cos, 0, -sin; 0, 1, 0; sin, 0, cos]
        expected_Ry = np.array([[0, 0, -1], [0, 1, 0], [1, 0, 0]])
        np.testing.assert_array_almost_equal(R, expected_Ry)

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
