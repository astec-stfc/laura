"""
LAURA's alignment errors moved to another code's pivot and frame.

LAURA pivots an element about its centre: a bend's offsets and
pitches about its arc midpoint, but its roll about its chord. The axes there
are unrolled by a bend's design tilt .
A code that pivots elsewhere takes the same rigid
motion as the offset of its pivot and a rotation in its frame. First order in
the errors, exact in the bend angle.

Vectors are ``(x, y, s)``; the rotation is ``(dy_rot, -dx_rot, dz_rot)``, about
those axes. A positive bend curves toward -x.
"""

from math import cos, sin
from typing import Dict, Tuple

import numpy as np

Vector = Tuple[float, float, float]


def sagitta(length: float, angle: float) -> float:
    """How far a bend's arc midpoint lies outside its chord's (in +x)."""
    return length / angle * (1 - cos(angle / 2)) if angle else 0.0


def arc_point(length: float, angle: float, s: float) -> Tuple[Vector, float]:
    """``(pivot, turn)`` for the point ``s`` along the arc from its midpoint:
    where it sits in the bend's centre frame, and how far its frame is turned
    about y."""
    if not angle:
        return (0.0, 0.0, s), 0.0
    radius, phi = length / angle, s * angle / length
    return (-radius * (1 - cos(phi)), 0.0, radius * sin(phi)), phi


def to_frame(
    errors: Dict[str, float],
    pivot: Vector = (0.0, 0.0, 0.0),
    turn: float = 0.0,
    tilt: float = 0.0,
    rolled: bool = True,
    chord: float = 0.0,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    ``errors``, keyed as LAURA's attributes, as ``(offset, rotation)`` of the
    point ``pivot`` in a frame turned by ``turn`` about y. ``pivot`` and
    ``turn`` are in the bend's own frame, rolled by its design ``tilt``; the
    result is in that frame, or unrolled. ``chord`` is the bend's
    :func:`sagitta`, which moves its roll axis.
    """
    get = lambda key: errors.get(key, 0.0)  # noqa: E731
    offset = np.array([get("dx"), get("dy"), get("dz")])
    rotation = np.array([get("dy_rot"), -get("dx_rot"), get("dz_rot")])
    basis = _basis(turn, tilt, rolled)
    offset = offset + _lever(rotation, pivot, tilt, chord)
    return basis.T @ offset, basis.T @ rotation


def from_frame(
    offset: Vector,
    rotation: Vector,
    pivot: Vector = (0.0, 0.0, 0.0),
    turn: float = 0.0,
    tilt: float = 0.0,
    rolled: bool = True,
    chord: float = 0.0,
) -> Dict[str, float]:
    """Inverse of :func:`to_frame`."""
    basis = _basis(turn, tilt, rolled)
    rotation = basis @ rotation
    offset = basis @ offset - _lever(rotation, pivot, tilt, chord)
    return dict(
        dx=offset[0],
        dy=offset[1],
        dz=offset[2],
        dx_rot=-rotation[1],
        dy_rot=rotation[0],
        dz_rot=rotation[2],
    )


def _lever(rotation: np.ndarray, pivot: Vector, tilt: float, chord: float) -> np.ndarray:
    """How far ``rotation`` moves ``pivot``; the roll turns about the chord."""
    roll = _roll(tilt)
    axis = roll @ (-chord, 0.0, 0.0)
    return np.cross(rotation, roll @ pivot) - np.cross([0.0, 0.0, rotation[2]], axis)


def _roll(angle: float) -> np.ndarray:
    c, s = cos(angle), sin(angle)
    return np.array([[c, -s, 0.0], [s, c, 0.0], [0.0, 0.0, 1.0]])


def _basis(turn: float, tilt: float, rolled: bool) -> np.ndarray:
    """The target frame's axes, as columns, in LAURA's."""
    c, s = cos(turn), sin(turn)
    turned = np.array([[c, 0.0, -s], [0.0, 1.0, 0.0], [s, 0.0, c]])
    return _roll(tilt) @ turned @ (np.eye(3) if rolled else _roll(-tilt))
