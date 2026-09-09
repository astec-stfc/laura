"""Bmad's floor-angle conventions, and the conversion to and from LAURA's."""

import math
from typing import Dict

import numpy as np

__all__ = [
    "bmad_floor_angles_from_matrix",
    "bmad_floor_angles_to_laura",
    "bmad_floor_rotation_matrix",
    "is_flat_roll",
    "is_half_turn",
]


def bmad_floor_rotation_matrix(theta: float, phi: float, psi: float) -> np.ndarray:
    """Build Bmad's floor orientation matrix from its three floor angles.

    Bmad composes it as ``W = Ry(theta) Rx(-phi) Rz(psi)`` (manual sec. 16.2,
    Eq. 16.2) using ordinary right-handed rotations, where ``theta`` is the
    azimuth about the vertical, ``phi`` the elevation and ``psi`` the roll about
    the longitudinal axis.
    """
    ct, st = math.cos(theta), math.sin(theta)
    cf, sf = math.cos(phi), math.sin(-phi)
    cp, sp = math.cos(psi), math.sin(psi)
    return (
        np.array([[ct, 0.0, st], [0.0, 1.0, 0.0], [-st, 0.0, ct]])
        @ np.array([[1.0, 0.0, 0.0], [0.0, cf, -sf], [0.0, sf, cf]])
        @ np.array([[cp, -sp, 0.0], [sp, cp, 0.0], [0.0, 0.0, 1.0]])
    )


def bmad_floor_angles_to_laura(
    theta: float, phi: float, psi: float
) -> Dict[str, float]:
    """Re-express Bmad's floor angles in LAURA's ``Rotation``.

    The two describe the *same* orientation with incompatible conventions, and
    not merely by naming the axes differently: LAURA's ``rotation_matrix``
    composes ``Rz(psi) Rx(phi) Ry_L(theta)`` -- the reverse order -- and its
    ``Ry_L`` carries the opposite sign to a standard ``Ry``.
    """
    matrix = bmad_floor_rotation_matrix(theta, phi, psi)
    return {
        "phi": float(math.asin(max(-1.0, min(1.0, matrix[2, 1])))),
        "psi": float(math.atan2(-matrix[0, 1], matrix[1, 1])),
        "theta": float(math.atan2(matrix[2, 0], matrix[2, 2])),
    }


def bmad_floor_angles_from_matrix(matrix: np.ndarray) -> Dict[str, float]:
    """Read Bmad's three floor angles back out of an orientation matrix.

    The inverse of :func:`bmad_floor_angles_to_laura`, for writing a lattice
    back out.
    """
    return {
        "phi": float(math.asin(max(-1.0, min(1.0, matrix[1, 2])))),
        "psi": float(math.atan2(matrix[1, 0], matrix[1, 1])),
        "theta": float(math.atan2(matrix[0, 2], matrix[2, 2])),
    }


_ROLL_TOLERANCE = 1e-12


def is_flat_roll(roll: float) -> bool:
    """Whether a bend's ``REF_TILT`` keeps it in the horizontal plane.

    A roll of 0 or a half turn leaves the bend flat; anything else tips the
    reference frame out of the plane and has to be carried as an orientation.
    """
    return abs(math.remainder(roll, math.pi)) <= _ROLL_TOLERANCE


def is_half_turn(roll: float) -> bool:
    """Whether a flat ``REF_TILT`` is the half turn rather than no roll at all."""
    return abs(math.remainder(roll, 2.0 * math.pi)) > _ROLL_TOLERANCE
