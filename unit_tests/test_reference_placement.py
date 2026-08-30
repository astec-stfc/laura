"""Tests for reference-frame element positioning (ReferencePlacement)."""

import math
import pytest
import numpy as np

from laura.models.physical import Position, Rotation, PhysicalElement, ReferencePlacement
from laura.models.element import Quadrupole, Dipole, Marker, PhysicalBaseElement
from laura.models.elementList import SectionLattice, MachineModel


# ---------------------------------------------------------------------------
# ReferencePlacement model validation
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# PhysicalElement mutual-exclusivity
# ---------------------------------------------------------------------------

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

    def test_unresolved_start_raises(self):
        pe = PhysicalElement(
            length=0.3,
            reference_placement=ReferencePlacement(element="x"),
        )
        with pytest.raises(RuntimeError, match="unresolved"):
            _ = pe.start

    def test_unresolved_end_raises(self):
        pe = PhysicalElement(
            length=0.3,
            reference_placement=ReferencePlacement(element="x"),
        )
        with pytest.raises(RuntimeError, match="unresolved"):
            _ = pe.end


# ---------------------------------------------------------------------------
# end_rotation_matrix
# ---------------------------------------------------------------------------

class TestEndRotationMatrix:
    def test_straight_element_matches_rotation_matrix(self):
        pe = PhysicalElement(length=1.0, middle=[0, 0, 1.0])
        np.testing.assert_array_almost_equal(pe.end_rotation_matrix, pe.rotation_matrix)

    def test_straight_element_with_yaw(self):
        pe = PhysicalElement(length=1.0, middle=[0, 0, 1.0], rotation=Rotation(theta=0.3))
        np.testing.assert_array_almost_equal(pe.end_rotation_matrix, pe.rotation_matrix)


# ---------------------------------------------------------------------------
# Helpers for building test lattices
# ---------------------------------------------------------------------------

def _straight_quad(name, z_mid, length=0.3, area="S1"):
    return Quadrupole(
        name=name,
        machine_area=area,
        magnetic={"length": length, "k1l": 1.0},
        physical={"length": length, "middle": {"x": 0, "y": 0, "z": z_mid}},
    )


def _ref_quad(name, ref_element, offset_z, length=0.3, area="S1"):
    """Quad placed via reference_placement with a longitudinal local offset."""
    return Quadrupole(
        name=name,
        machine_area=area,
        magnetic={"length": length, "k1l": 1.0},
        physical={
            "length": length,
            "reference_placement": {
                "element": ref_element,
                "point": "end",
                "offset": [0, 0, offset_z],
            },
        },
    )


def _ref_quad_world(name, ref_element, world_offset, length=0.3, area="S1"):
    return Quadrupole(
        name=name,
        machine_area=area,
        magnetic={"length": length, "k1l": 1.0},
        physical={
            "length": length,
            "reference_placement": {
                "element": ref_element,
                "world_offset": list(world_offset),
            },
        },
    )


# ---------------------------------------------------------------------------
# SectionLattice.resolve_reference_placements — straight elements
# ---------------------------------------------------------------------------

class TestResolveStraightElements:
    def _build(self):
        q1 = _straight_quad("Q1", z_mid=1.0, length=0.4)
        q2 = _ref_quad("Q2", ref_element="Q1", offset_z=0.5)
        elems = {"Q1": q1, "Q2": q2}
        sec = SectionLattice(name="S1", order=["Q1", "Q2"], elements=[q1, q2])
        sec.resolve_reference_placements(elems)
        return q1, q2

    def test_middle_set_after_resolution(self):
        q1, q2 = self._build()
        assert q2.physical.middle is not None

    def test_position_is_correct(self):
        """Q2 should be centred at Q1.end + 0.5 m along beam axis (global Z)."""
        q1, q2 = self._build()
        # Q1 end = Q1.middle.z + Q1.length/2 = 1.0 + 0.2 = 1.2
        # offset [0,0,0.5] in frame aligned with Z → delta = [0,0,0.5]
        # Q2 middle should be at z = 1.2 + 0.5 = 1.7
        expected_z = q1.physical.end.z + 0.5
        assert q2.physical.middle.z == pytest.approx(expected_z)

    def test_rotation_inherited(self):
        """Straight element: Q2 rotation should match Q1 exit frame (identity)."""
        q1, q2 = self._build()
        np.testing.assert_array_almost_equal(
            q2.physical.rotation_matrix, np.eye(3), decimal=10
        )

    def test_world_offset(self):
        """world_offset shifts in global frame, not local frame."""
        q1 = _straight_quad("Q1", z_mid=1.0, length=0.4)
        q2 = _ref_quad_world("Q2", ref_element="Q1", world_offset=[0.1, 0, 0])
        elems = {"Q1": q1, "Q2": q2}
        sec = SectionLattice(name="S1", order=["Q1", "Q2"], elements=[q1, q2])
        sec.resolve_reference_placements(elems)
        # Q2 middle should be at Q1.end + [0.1, 0, 0]
        assert q2.physical.middle.x == pytest.approx(q1.physical.end.x + 0.1)
        assert q2.physical.middle.z == pytest.approx(q1.physical.end.z)

    def test_missing_reference_raises(self):
        q1 = _straight_quad("Q1", z_mid=1.0)
        q2 = _ref_quad("Q2", ref_element="NONEXISTENT", offset_z=0.5)
        sec = SectionLattice(name="S1", order=["Q1", "Q2"], elements=[q1, q2])
        with pytest.raises(ValueError, match="does not exist"):
            sec.resolve_reference_placements({"Q1": q1, "Q2": q2})


# ---------------------------------------------------------------------------
# Dipole exit frame — the primary motivating use case
# ---------------------------------------------------------------------------

class TestDipoleExitFrame:
    """
    A dipole bending in the horizontal plane (XZ) by angle theta.
    An element placed 'L' metres downstream along the dipole exit axis
    should end up at the correct world position and orientation.
    """

    def _make_dipole(self, theta, rho=1.0):
        """Dipole with bend angle theta, radius rho, placed with entry along Z."""
        L = rho * theta
        # For entry along global Z, rotation.theta = 0 (canonical orientation)
        return Dipole(
            name="D1",
            machine_area="S1",
            magnetic={"length": L, "k0l": theta},
            physical={"length": L, "middle": [0, 0, 0]},
        )

    def test_end_rotation_matrix_exit_beam(self):
        """end_rotation_matrix Z-axis should point along the exit beam direction."""
        theta = math.pi / 6  # 30-degree bend
        rho = 1.0
        d = self._make_dipole(theta, rho)
        R_exit = d.physical.end_rotation_matrix
        # Exit beam direction (canonical): [sin(theta), 0, cos(theta)]
        exit_beam = R_exit @ np.array([0, 0, 1])
        expected = np.array([math.sin(theta), 0, math.cos(theta)])
        np.testing.assert_array_almost_equal(exit_beam, expected, decimal=10)

    def test_element_placed_downstream_of_dipole(self):
        """Quad placed 0.5 m downstream of dipole exit should be at correct world position."""
        theta = math.pi / 4  # 45-degree bend
        rho = 1.0
        L_dip = rho * theta
        L_quad = 0.3
        offset_z = 0.5

        dipole = self._make_dipole(theta, rho)
        quad = Quadrupole(
            name="Q1",
            machine_area="S1",
            magnetic={"length": L_quad, "k1l": 1.0},
            physical={
                "length": L_quad,
                "reference_placement": {
                    "element": "D1",
                    "offset": [0, 0, offset_z],
                },
            },
        )

        registry = {"D1": dipole, "Q1": quad}
        sec = SectionLattice(name="S1", order=["D1", "Q1"], elements=[dipole, quad])
        sec.resolve_reference_placements(registry)

        # Expected middle of quad: dipole exit + 0.5 m along exit beam direction
        d_end = dipole.physical.end
        exit_dir = np.array([math.sin(theta), 0, math.cos(theta)])
        expected = np.array([d_end.x, d_end.y, d_end.z]) + offset_z * exit_dir

        got = np.array([quad.physical.middle.x, quad.physical.middle.y, quad.physical.middle.z])
        np.testing.assert_array_almost_equal(got, expected, decimal=10)

    def test_quad_rotation_matches_dipole_exit(self):
        """Quad placed after dipole should inherit the dipole exit orientation."""
        theta = math.pi / 4
        dipole = self._make_dipole(theta, rho=1.0)
        quad = Quadrupole(
            name="Q1",
            machine_area="S1",
            magnetic={"length": 0.3, "k1l": 1.0},
            physical={
                "length": 0.3,
                "reference_placement": {"element": "D1"},
            },
        )

        registry = {"D1": dipole, "Q1": quad}
        sec = SectionLattice(name="S1", order=["D1", "Q1"], elements=[dipole, quad])
        sec.resolve_reference_placements(registry)

        # Quad rotation matrix should equal dipole exit_rotation_matrix
        np.testing.assert_array_almost_equal(
            quad.physical.rotation_matrix,
            dipole.physical.end_rotation_matrix,
            decimal=10,
        )

    def test_user_rotation_composed_with_exit_frame(self):
        """If the user specifies a rotation on the element, it is composed on top
        of the exit frame rather than discarded."""
        theta = math.pi / 4
        dipole = self._make_dipole(theta, rho=1.0)
        # Small additional yaw of 0.1 rad in local frame
        extra_yaw = 0.1
        quad = Quadrupole(
            name="Q1",
            machine_area="S1",
            magnetic={"length": 0.3, "k1l": 1.0},
            physical={
                "length": 0.3,
                "rotation": [0, 0, extra_yaw],
                "reference_placement": {"element": "D1"},
            },
        )

        registry = {"D1": dipole, "Q1": quad}
        sec = SectionLattice(name="S1", order=["D1", "Q1"], elements=[dipole, quad])
        sec.resolve_reference_placements(registry)

        # Composed R = R_exit @ Ry(extra_yaw)  (LAURA Ry convention)
        from laura.utils.rotation_matrix import euler_angles_to_rotation_matrix
        R_exit = dipole.physical.end_rotation_matrix
        R_extra = euler_angles_to_rotation_matrix(extra_yaw, 0.0, 0.0)
        expected_R = R_exit @ R_extra

        np.testing.assert_array_almost_equal(
            quad.physical.rotation_matrix, expected_R, decimal=10
        )


# ---------------------------------------------------------------------------
# MachineModel auto-resolution
# ---------------------------------------------------------------------------

class TestMachineModelAutoResolve:
    def test_auto_resolved_on_construction(self):
        """MachineModel should auto-resolve reference placements."""
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
