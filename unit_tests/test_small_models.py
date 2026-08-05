"""Tests for small/low-coverage model modules: degauss, shutter, laser, trajectory,
plus edge cases in CascadingAccessMixin not exercised by test_element_attrs.py."""

import numpy as np
import pytest
from pydantic import ValidationError

from laura.models.degauss import DegaussableElement
from laura.models.shutter import ShutterElement, ValveElement
from laura.models.laser import LaserElement, LaserHalfWavePlateElement
from laura.models.trajectory import Trajectory
from laura.models.physical import Position
from laura.models.element import Element


class TestDegaussableElement:
    def test_values_from_csv_string(self):
        d = DegaussableElement(values="1.0, 2.5, -3.0")
        assert d.values == [1.0, 2.5, -3.0]

    def test_values_from_list(self):
        d = DegaussableElement(values=[1, 2, 3])
        assert d.values == [1, 2, 3]

    def test_values_invalid_type_raises(self):
        with pytest.raises(ValidationError):
            DegaussableElement(values=5)


class TestShutterElement:
    def test_interlocks_from_csv_string(self):
        s = ShutterElement(interlocks="A, B ,C")
        assert s.interlocks == ["A", "B", "C"]

    def test_interlocks_from_list(self):
        s = ShutterElement(interlocks=["A", "B"])
        assert s.interlocks == ["A", "B"]

    def test_interlocks_invalid_type_raises(self):
        with pytest.raises(ValidationError):
            ShutterElement(interlocks=5)


class TestValveElement:
    def test_construction(self):
        ValveElement()


class TestLaserElement:
    def test_angular_frequency(self):
        laser = LaserElement(wavelength=800e-9)
        assert laser.angular_frequency == pytest.approx(2 * np.pi * 299792458.0 / 800e-9)

    def test_angular_frequency_nonpositive_raises(self):
        laser = LaserElement(wavelength=0)
        with pytest.raises(ValueError):
            laser.angular_frequency

    def test_amplitude_zero_when_missing_params(self):
        laser = LaserElement()
        with pytest.warns(UserWarning):
            assert laser.amplitude == 0

    def test_amplitude_positive_when_params_set(self):
        laser = LaserElement(
            wavelength=800e-9, waist=1e-3, pulse_energy=1e-3, pulse_duration_fwhm=1e-13
        )
        assert laser.amplitude > 0


class TestLaserHalfWavePlate:
    def test_construction(self):
        LaserHalfWavePlateElement()


class TestTrajectory:
    def _traj(self):
        s = np.array([0.0, 1.0, 2.0])
        pos = np.array([[0, 0, 0], [0, 0, 1], [0, 0, 2]], dtype=float)
        rots = np.array([np.eye(3)] * 3)
        return Trajectory(s, pos, rots)

    def test_xyz_at_s_interpolates(self):
        t = self._traj()
        p = t.xyz_at_s(0.5)
        assert p.z == pytest.approx(0.5)

    def test_xyz_at_s_extrapolates_below(self):
        t = self._traj()
        p = t.xyz_at_s(-1.0)
        assert p.z == pytest.approx(-1.0)

    def test_xyz_at_s_extrapolates_above(self):
        t = self._traj()
        p = t.xyz_at_s(3.0)
        assert p.z == pytest.approx(3.0)

    def test_rotation_at_s(self):
        t = self._traj()
        np.testing.assert_array_almost_equal(t.rotation_at_s(0.5), np.eye(3))

    def test_s_at_xyz_projects_to_nearest_point(self):
        t = self._traj()
        s = t.s_at_xyz(Position(x=0, y=0, z=1.5))
        assert s == pytest.approx(1.5)

    def test_empty_trajectory(self):
        t = Trajectory(np.array([]), np.array([]).reshape(0, 3), np.array([]).reshape(0, 3, 3))
        p = t.xyz_at_s(1.0)
        assert p.x == 0.0 and p.y == 0.0 and p.z == 0.0
        np.testing.assert_array_equal(t.rotation_at_s(1.0), np.eye(3))

    def test_single_sample_trajectory(self):
        t = Trajectory(np.array([0.0]), np.array([[0.0, 0.0, 0.0]]), np.array([np.eye(3)]))
        p = t.xyz_at_s(2.0)
        assert p.z == pytest.approx(2.0)


class TestCascadingAccessEdgeCases:
    def _element(self):
        return Element(name="E1", hardware_class="Generic", hardware_type="HT", machine_area="MA")

    def test_get_through_none_intermediate_raises(self):
        e = self._element()
        assert e.controls is None
        with pytest.raises(AttributeError, match="Cannot access"):
            e.variables

    def test_set_through_none_intermediate_raises(self):
        e = self._element()
        with pytest.raises(AttributeError, match="Cannot set attribute"):
            e.variables = ["x"]

    def test_unknown_attribute_falls_through_to_pydantic(self):
        e = self._element()
        with pytest.raises(ValidationError):
            e.totally_unknown_attribute = 1

    def test_private_attribute_access_raises(self):
        e = self._element()
        with pytest.raises(AttributeError):
            e._private_thing
