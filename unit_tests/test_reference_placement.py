import math
import pytest
import numpy as np

from laura.models.physical import Position, Rotation, PhysicalElement, ReferencePlacement
from laura.models.element import Dipole, Marker, PhysicalBaseElement
from laura.models.element_list import SectionLattice, MachineModel
from unit_tests.helpers import quad


class TestReferencePlacementModel:
    def test_default_point_is_end(self):
        rp = ReferencePlacement(element="some_dipole")
        assert rp.point == "end"
        assert rp.offset is None
        assert rp.world_offset is None

    def test_offset_from_list(self):
        rp = ReferencePlacement(element="d1", offset=[0, 0, 1.0])
        assert rp.offset.z == pytest.approx(1.0)

    def test_world_offset_from_list(self):
        rp = ReferencePlacement(element="d1", world_offset=[0.05, 0, 0])
        assert rp.world_offset.x == pytest.approx(0.05)

    def test_both_offsets_raises(self):
        with pytest.raises(Exception, match="offset"):
            ReferencePlacement(element="d1", offset=[0, 0, 1], world_offset=[1, 0, 0])

    def test_point_values(self):
        for pt in ("start", "middle", "end"):
            rp = ReferencePlacement(element="x", point=pt)
            assert rp.point == pt

    def test_invalid_point_raises(self):
        with pytest.raises(Exception):
            ReferencePlacement(element="x", point="centre")


class TestPhysicalElementExclusivity:
    def test_middle_and_reference_placement_raises(self):
        with pytest.raises(Exception, match="Cannot specify both"):
            PhysicalElement(
                length=0.3,
                middle=[0, 0, 1.0],
                reference_placement=ReferencePlacement(element="x"),
            )

    def test_reference_placement_alone_leaves_middle_none(self):
        pe = PhysicalElement(
            length=0.3,
            reference_placement=ReferencePlacement(element="x"),
        )
        assert pe.middle is None

    def test_normal_middle_works(self):
        pe = PhysicalElement(length=0.3, middle=[0, 0, 2.0])
        assert pe.middle.z == pytest.approx(2.0)

    @pytest.mark.parametrize("end", ["start", "end"])
    def test_unresolved_end_raises(self, end):
        pe = PhysicalElement(
            length=0.3,
            reference_placement=ReferencePlacement(element="x"),
        )
        with pytest.raises(RuntimeError, match="unresolved"):
            getattr(pe, end)


class TestEndRotationMatrix:
    @pytest.mark.parametrize("rotation", [{}, {"rotation": Rotation(theta=0.3)}], ids=["unrotated", "yawed"])
    def test_straight_element_matches_rotation_matrix(self, rotation):
        pe = PhysicalElement(length=1.0, middle=[0, 0, 1.0], **rotation)
        np.testing.assert_array_almost_equal(pe.end_rotation_matrix, pe.rotation_matrix)


def _straight_quad(name, z_mid, length=0.3):
    return quad(name, length, 1.0, "S1", middle={"x": 0, "y": 0, "z": z_mid})


def _ref_quad(name, ref_element, offset_z=None, world_offset=None, **physical):
    placement = {"element": ref_element}
    if offset_z is not None:
        placement |= {"point": "end", "offset": [0, 0, offset_z]}
    if world_offset is not None:
        placement["world_offset"] = list(world_offset)
    return quad(name, 0.3, 1.0, "S1", reference_placement=placement, **physical)


def _resolve(*elements):
    sec = SectionLattice(name="S1", order=[e.name for e in elements], elements=list(elements))
    sec.resolve_reference_placements({e.name: e for e in elements})


class TestResolveStraightElements:
    def _build(self):
        q1 = _straight_quad("Q1", z_mid=1.0, length=0.4)
        q2 = _ref_quad("Q2", ref_element="Q1", offset_z=0.5)
        _resolve(q1, q2)
        return q1, q2

    def test_middle_set_after_resolution(self):
        q1, q2 = self._build()
        assert q2.physical.middle is not None

    def test_position_is_correct(self):
        q1, q2 = self._build()
        expected_z = q1.physical.end.z + 0.5
        assert q2.physical.middle.z == pytest.approx(expected_z)

    def test_rotation_inherited(self):
        q1, q2 = self._build()
        np.testing.assert_array_almost_equal(
            q2.physical.rotation_matrix, np.eye(3), decimal=10
        )

    def test_world_offset(self):
        q1 = _straight_quad("Q1", z_mid=1.0, length=0.4)
        q2 = _ref_quad("Q2", ref_element="Q1", world_offset=[0.1, 0, 0])
        _resolve(q1, q2)
        assert q2.physical.middle.x == pytest.approx(q1.physical.end.x + 0.1)
        assert q2.physical.middle.z == pytest.approx(q1.physical.end.z)

    def test_missing_reference_raises(self):
        q1 = _straight_quad("Q1", z_mid=1.0)
        q2 = _ref_quad("Q2", ref_element="NONEXISTENT", offset_z=0.5)
        with pytest.raises(ValueError, match="does not exist"):
            _resolve(q1, q2)


class TestDipoleExitFrame:
    def _make_dipole(self, theta, rho=1.0):
        length = rho * theta
        return Dipole(
            name="D1",
            machine_area="S1",
            magnetic={"length": length, "k0l": theta},
            physical={"length": length, "middle": [0, 0, 0]},
        )

    def test_end_rotation_matrix_exit_beam(self):
        theta = math.pi / 6
        rho = 1.0
        d = self._make_dipole(theta, rho)
        r_exit = d.physical.end_rotation_matrix
        exit_beam = r_exit @ np.array([0, 0, 1])
        expected = np.array([math.sin(theta), 0, math.cos(theta)])
        np.testing.assert_array_almost_equal(exit_beam, expected, decimal=10)

    def test_element_placed_downstream_of_dipole(self):
        theta = math.pi / 4
        rho = 1.0
        l_dip = rho * theta
        offset_z = 0.5

        dipole = self._make_dipole(theta, rho)
        q1 = _ref_quad("Q1", "D1", offset_z=offset_z)
        _resolve(dipole, q1)

        d_end = dipole.physical.end
        exit_dir = np.array([math.sin(theta), 0, math.cos(theta)])
        expected = np.array([d_end.x, d_end.y, d_end.z]) + offset_z * exit_dir

        got = np.array([q1.physical.middle.x, q1.physical.middle.y, q1.physical.middle.z])
        np.testing.assert_array_almost_equal(got, expected, decimal=10)

    def test_quad_rotation_matches_dipole_exit(self):
        theta = math.pi / 4
        dipole = self._make_dipole(theta, rho=1.0)
        q1 = _ref_quad("Q1", "D1")
        _resolve(dipole, q1)

        np.testing.assert_array_almost_equal(
            q1.physical.rotation_matrix,
            dipole.physical.end_rotation_matrix,
            decimal=10,
        )

    def test_user_rotation_composed_with_exit_frame(self):
        theta = math.pi / 4
        dipole = self._make_dipole(theta, rho=1.0)
        extra_yaw = 0.1
        q1 = _ref_quad("Q1", "D1", rotation=[0, 0, extra_yaw])
        _resolve(dipole, q1)

        from laura.utils.rotation_matrix import euler_angles_to_rotation_matrix
        r_exit = dipole.physical.end_rotation_matrix
        r_extra = euler_angles_to_rotation_matrix(extra_yaw, 0.0, 0.0)
        expected_r = r_exit @ r_extra

        np.testing.assert_array_almost_equal(
            q1.physical.rotation_matrix, expected_r, decimal=10
        )


class TestMachineModelAutoResolve:
    def test_auto_resolved_on_construction(self):
        q1 = _straight_quad("Q1", z_mid=1.0, length=0.4)
        q2 = _ref_quad("Q2", ref_element="Q1", offset_z=0.5)

        with pytest.warns(Warning):
            mm = MachineModel(
                elements={"Q1": q1, "Q2": q2},
                section={
                    "sections": {
                        "S1": {"elements": ["Q1", "Q2"]},
                    }
                },
            )

        assert mm.elements["Q2"].physical.middle is not None
        expected_z = q1.physical.end.z + 0.5
        assert mm.elements["Q2"].physical.middle.z == pytest.approx(expected_z)
