"""Tests for laura.utils.rotation_matrix, vector_math, magnet_conversions."""

import numpy as np
import pytest

from laura.utils.rotation_matrix import (
    euler_angles_to_rotation_matrix,
    position_rotated,
    rotation_matrix_to_euler,
)
from laura.utils.vector_math import (
    vector_length,
    vector_angle,
    normalized_vector,
    dot_product,
    cross_product,
)
from laura.utils.magnet_conversions import k_to_current, current_to_k, scale_order
from laura.models.physical import Position, Rotation


class TestEulerRoundtrip:
    def test_identity(self):
        r = euler_angles_to_rotation_matrix(0.0, 0.0, 0.0)
        np.testing.assert_array_almost_equal(r, np.eye(3))

    @pytest.mark.parametrize("yaw,pitch,roll", [
        (0.1, 0.2, 0.3),
        (-0.5, 0.4, -0.2),
        (1.0, 0.0, 0.0),
        (0.0, 1.0, 0.0),
        (0.0, 0.0, 1.0),
    ])
    def test_roundtrip(self, yaw, pitch, roll):
        r = euler_angles_to_rotation_matrix(yaw, pitch, roll)
        y2, p2, r2 = rotation_matrix_to_euler(r)
        assert y2 == pytest.approx(yaw, abs=1e-9)
        assert p2 == pytest.approx(pitch, abs=1e-9)
        assert r2 == pytest.approx(roll, abs=1e-9)

    def test_gimbal_lock(self):
        r = euler_angles_to_rotation_matrix(0.3, np.pi / 2, 0.4)
        yaw, pitch, roll = rotation_matrix_to_euler(r)
        assert pitch == pytest.approx(np.pi / 2, abs=1e-6)
        assert roll == 0.0


class TestPositionRotated:
    def test_no_rotation(self):
        p = position_rotated(Position(x=1, y=2, z=3), Rotation(phi=0, psi=0, theta=0))
        assert p.x == pytest.approx(1.0)
        assert p.y == pytest.approx(2.0)
        assert p.z == pytest.approx(3.0)

    def test_yaw_90(self):
        p = position_rotated(Position(x=0, y=0, z=1), Rotation(phi=0, psi=0, theta=np.pi / 2))
        assert p.x == pytest.approx(-1.0, abs=1e-9)
        assert p.z == pytest.approx(0.0, abs=1e-9)


class TestVectorMath:
    @pytest.mark.parametrize("args, expected", [((3, 4), 5.0), ((1, 2, 2), 3.0)], ids=["2d", "3d"])
    def test_vector_length(self, args, expected):
        assert vector_length(*args) == pytest.approx(expected)

    def test_vector_angle_perpendicular(self):
        angle = vector_angle(1, 0, 0, 1)
        assert angle == pytest.approx(np.pi / 2)

    def test_vector_angle_parallel(self):
        angle = vector_angle(1, 0, 1, 0)
        assert angle == pytest.approx(0.0, abs=1e-4)

    def test_normalized_vector(self):
        x, y, z = normalized_vector(3, 4, 0)
        assert vector_length(x, y, z) == pytest.approx(1.0)

    def test_normalized_vector_zero(self):
        assert normalized_vector(0, 0, 0) == (0.0, 0.0, 0.0)

    def test_dot_product(self):
        assert dot_product(1, 2, 3, 4, z1=5, z2=6) == 1 * 3 + 2 * 4 + 5 * 6

    def test_cross_product(self):
        result = cross_product(1, 0, 0, 0, 1, 0)
        assert result == pytest.approx((0.0, 0.0, 1.0))


class TestMagnetConversions:
    @pytest.mark.parametrize("magnet_type", [
        "Dipole", "Dipole_Magnet", "Bending",
        "Quadrupole", "Quadrupole_Magnet",
        "Sextupole", "Sextupole_Magnet",
        "Octupole", "Octupole_Magnet",
        "Solenoid", "Solenoid_Magnet",
    ])
    def test_k_current_roundtrip(self, magnet_type):
        k = current_to_k(k_to_current(0.5, magnet_type, momentum=100.0), magnet_type, momentum=100.0)
        assert k == pytest.approx(0.5)

    @pytest.mark.parametrize(
        "convert, magnet_type, momentum",
        [
            (k_to_current, "Dipole", 0),
            (current_to_k, "Dipole", -1),
            (k_to_current, "Unobtainium", 100.0),
            (current_to_k, "Unobtainium", 100.0),
        ],
        ids=["k_to_current-momentum", "current_to_k-momentum", "k_to_current-type", "current_to_k-type"],
    )
    def test_invalid_input_raises(self, convert, magnet_type, momentum):
        with pytest.raises(ValueError):
            convert(0.5, magnet_type, momentum=momentum)

    def test_scale_order_passthrough(self):
        assert scale_order(2, 1.23) == 1.23
        assert scale_order(2, 1.23, direction="from_canonical") == 1.23
