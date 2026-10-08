"""Exact chord geometry for ``PhysicalElement.start`` / ``.end`` on a bend.

With ``rho = L / theta`` and ``middle`` at the *arc* midpoint, ``middle -> start/end``
is ``2 rho sin(theta/4)`` and ``start -> end`` is ``2 rho sin(theta/2)``.
"""

import numpy as np
import pytest

from laura.models.element import Dipole
from unit_tests.helpers import quad

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
    phys = _bend(angle).physical
    rho = phys.length / phys._physical_angle
    assert _norm(phys.end) == pytest.approx(abs(2 * rho * np.sin(angle / 4)), rel=1e-12)


@pytest.mark.parametrize("angle", ANGLES)
def test_start_to_end_is_the_full_chord(angle):
    """Doesn't discriminate alone; constrains the pair jointly."""
    phys = _bend(angle).physical
    rho = phys.length / phys._physical_angle
    span = np.array(phys.end.array) - np.array(phys.start.array)
    assert float(np.linalg.norm(span)) == pytest.approx(
        abs(2 * rho * np.sin(angle / 2)), rel=1e-12
    )


@pytest.mark.parametrize("angle", ANGLES)
def test_the_faces_lie_on_the_arc(angle):
    """Both faces are exactly ``rho`` from the centre of curvature."""
    phys = _bend(angle).physical
    theta = phys._physical_angle
    rho = phys.length / theta
    centre = np.array([rho * np.cos(theta / 2), 0.0, -rho * np.sin(theta / 2)])
    for face in (phys.start, phys.end):
        assert float(np.linalg.norm(np.array(face.array) - centre)) == pytest.approx(
            abs(rho), rel=1e-12
        )


def test_a_straight_element_is_unaffected():
    phys = quad(length=0.4, middle={"x": 0.0, "y": 0.0, "z": 0.0}).physical
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
    """Pins the correction over the old half-chord ``L(1 - cos theta) / (2 theta)``."""
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


def test_a_pinned_layout_angle_outranks_an_authored_one():
    """A pinned angle (a moving chicane) is newer intent than the authored one."""
    bend = Dipole(
        name="B1",
        hardware_class="Magnet",
        machine_area="S",
        magnetic={"k0l": 0.1, "length": 1.0},
        physical={
            "length": 1.0,
            "middle": {"x": 0.0, "y": 0.0, "z": 0.0},
            "physical_angle": 0.13,
        },
    )
    assert bend.physical._physical_angle == pytest.approx(0.13)

    bend.physical.set_physical_angle(0.1)
    assert bend.physical._physical_angle == pytest.approx(0.1)
    # and the faces move with it, rather than staying where the file put them
    assert bend.physical.end.x == pytest.approx(
        (1.0 / 0.1) * (np.cos(0.05) - np.cos(0.1))
    )
