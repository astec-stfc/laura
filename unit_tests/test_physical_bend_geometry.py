"""Exact chord geometry for ``PhysicalElement.start`` / ``.end`` on a bend.

An element of arc length ``L`` bending through ``theta`` has
radius ``rho = L / theta``.  Measuring from the arc's entry, the point at
angle ``phi`` sits at ``(rho(1 - cos phi), 0, rho sin phi)``.  The element's
``middle`` is the arc midpoint at ``theta/2``.
"""

import numpy as np
import pytest

from laura.models.element import Dipole, Quadrupole

ANGLES = [0.05, 0.1, 0.3, 0.6, -0.3]


def _bend(angle: float, length: float = 1.0) -> Dipole:
    return Dipole(
        name="B1",
        hardware_class="Magnet",
        machine_area="S",
        magnetic={"k0l": angle, "length": length},
        physical={"length": length, "middle": {"x": 0.0, "y": 0.0, "z": 0.0}},
    )


def _norm(position) -> float:
    return float(np.linalg.norm(np.array(position.array)))


@pytest.mark.parametrize("angle", ANGLES)
def test_middle_to_start_is_the_half_angle_chord(angle):
    phys = _bend(angle).physical
    rho = phys.length / phys._physical_angle
    assert _norm(phys.start) == pytest.approx(
        abs(2 * rho * np.sin(angle / 4)), rel=1e-12
    )


@pytest.mark.parametrize("angle", ANGLES)
def test_middle_to_end_is_the_half_angle_chord(angle):
    """The arc midpoint is equidistant from both faces."""
    phys = _bend(angle).physical
    rho = phys.length / phys._physical_angle
    assert _norm(phys.end) == pytest.approx(abs(2 * rho * np.sin(angle / 4)), rel=1e-12)


@pytest.mark.parametrize("angle", ANGLES)
def test_start_to_end_is_the_full_chord(angle):
    """Passes under the old formula too -- kept because it constrains the pair
    jointly, not because it discriminates."""
    phys = _bend(angle).physical
    rho = phys.length / phys._physical_angle
    span = np.array(phys.end.array) - np.array(phys.start.array)
    assert float(np.linalg.norm(span)) == pytest.approx(
        abs(2 * rho * np.sin(angle / 2)), rel=1e-12
    )


@pytest.mark.parametrize("angle", ANGLES)
def test_the_faces_lie_on_the_arc(angle):
    """Strongest form: both faces are exactly ``rho`` from the centre of
    curvature, which no chord-based approximation satisfies."""
    phys = _bend(angle).physical
    theta = phys._physical_angle
    rho = phys.length / theta
    # Centre of curvature, in the same entry frame the offsets are built in:
    # perpendicular to the trajectory at the arc midpoint.
    centre = np.array([rho * np.cos(theta / 2), 0.0, -rho * np.sin(theta / 2)])
    for face in (phys.start, phys.end):
        assert float(np.linalg.norm(np.array(face.array) - centre)) == pytest.approx(
            abs(rho), rel=1e-12
        )


def test_a_straight_element_is_unaffected():
    phys = Quadrupole(
        name="Q1",
        hardware_class="Magnet",
        machine_area="S",
        physical={"length": 0.4, "middle": {"x": 0.0, "y": 0.0, "z": 0.0}},
    ).physical
    assert phys.start.z == pytest.approx(-0.2)
    assert phys.end.z == pytest.approx(0.2)


@pytest.mark.parametrize("angle", [1e-10, 0.0])
def test_a_negligible_angle_takes_the_straight_branch(angle):
    """Guards the 1e-9 cutoff -- ``rho = L / theta`` would divide by ~zero."""
    phys = _bend(angle, length=0.4).physical
    assert phys.start.z == pytest.approx(-0.2)
    assert phys.end.z == pytest.approx(0.2)


@pytest.mark.parametrize("angle", [0.05, 0.3, 0.6])
def test_the_old_half_chord_formula_would_fail_these(angle):
    """Pins the size of the correction, so a silent revert is visible.

    The superseded expression was ``L(1 - cos theta) / (2 theta)`` and
    ``L sin(theta) / (2 theta)`` -- exactly half the full chord, i.e. the
    element treated as symmetric about the *chord* midpoint.
    """
    length = 1.0
    phys = _bend(angle, length=length).physical
    rho = length / angle
    superseded = np.hypot(
        length * (1 - np.cos(angle)) / (2 * angle),
        length * np.sin(angle) / (2 * angle),
    )
    exact = 2 * rho * np.sin(angle / 4)
    assert _norm(phys.start) == pytest.approx(exact, rel=1e-12)
    assert superseded < exact  # the old formula always under-read
    assert exact - superseded > 1e-5 * angle / 0.05  # and by a growing margin
