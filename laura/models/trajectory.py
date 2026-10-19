"""Beamline design trajectory for s-coordinate resolution and querying."""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    from .physical import Position


class Trajectory:
    """
    Design trajectory of a beamline, parameterised by arc-length s.

    Stores a sequence of (s, position, rotation_matrix) samples and
    provides interpolation/projection for bidirectional s ↔ xyz mapping.

    Built automatically by :meth:`~laura.models.elementList.SectionLattice.resolve_positions`
    and stored on each :class:`~laura.models.physical.PhysicalElement` via its
    ``_trajectory`` private attribute.
    """

    def __init__(
        self,
        s_vals: np.ndarray,
        positions: np.ndarray,
        rot_matrices: np.ndarray,
    ) -> None:
        self._s = np.asarray(s_vals, dtype=float)
        self._pos = np.asarray(positions, dtype=float)  # (N, 3)
        self._rots = np.asarray(rot_matrices, dtype=float)  # (N, 3, 3)

    # ── public interface ───────────────────────────────────────────────────────

    def xyz_at_s(self, s: float) -> Position:
        """Return the global position at arc-length *s*.

        Linearly interpolates between stored samples; extrapolates along the
        local beam direction outside the stored range.
        """
        from .physical import Position

        return Position.from_list(self._lerp_pos(float(s)).tolist())

    def rotation_at_s(self, s: float) -> np.ndarray:
        """Return the 3×3 rotation matrix at arc-length *s* (nearest sample)."""
        return self._nearest_rot(float(s))

    def s_at_xyz(self, pos: Position) -> float:
        """Return arc-length at the nearest point on the trajectory to *pos*."""
        return self._project(pos)

    # ── internals ─────────────────────────────────────────────────────────────

    def _lerp_pos(self, s: float) -> np.ndarray:
        n = len(self._s)
        if n == 0:
            return np.zeros(3)
        if n == 1:
            d = self._rots[0] @ np.array([0.0, 0.0, 1.0])
            return self._pos[0] + d * (s - self._s[0])

        idx = int(np.searchsorted(self._s, s, side="right"))

        if idx == 0:
            d = self._rots[0] @ np.array([0.0, 0.0, 1.0])
            return self._pos[0] + d * (s - self._s[0])
        if idx >= n:
            d = self._rots[-1] @ np.array([0.0, 0.0, 1.0])
            return self._pos[-1] + d * (s - self._s[-1])

        s0, p0 = self._s[idx - 1], self._pos[idx - 1]
        s1, p1 = self._s[idx], self._pos[idx]
        ds = s1 - s0
        t = (s - s0) / ds if abs(ds) > 1e-12 else 0.0
        return p0 + t * (p1 - p0)

    def _nearest_rot(self, s: float) -> np.ndarray:
        if len(self._s) == 0:
            return np.eye(3)
        idx = int(np.searchsorted(self._s, s, side="right"))
        idx = max(0, min(idx, len(self._s) - 1))
        return self._rots[idx].copy()

    def _project(self, pos: Position) -> float:
        p = np.array([pos.x, pos.y, pos.z])
        best_s, best_dist = 0.0, np.inf
        for i in range(len(self._s) - 1):
            s0, p0 = self._s[i], self._pos[i]
            s1, p1 = self._s[i + 1], self._pos[i + 1]
            seg = p1 - p0
            sq = float(np.dot(seg, seg))
            if sq < 1e-24:
                continue
            t = float(np.clip(np.dot(p - p0, seg) / sq, 0.0, 1.0))
            dist = float(np.linalg.norm(p - p0 - t * seg))
            if dist < best_dist:
                best_dist = dist
                best_s = float(s0 + t * (s1 - s0))
        return best_s
