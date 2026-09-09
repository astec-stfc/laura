"""Bmad short-range wakes: pseudo-modes in, a sampled wake function out.

Bmad stores a short-range wake as a sum of damped sinusoids rather than as
samples::

    W(s) = sum_i amp_i * exp(-damp_i * z_scale * s) * sin(2*pi*phi_i - k_i * z_scale * s)

for *s*, the distance a trailing particle sits behind the source, non-negative.
``phi`` is in turns. LAURA's :class:`~laura.translator.utils.fields.field`
holds sampled arrays and nothing else, so the modes are evaluated onto a grid on the way in.
"""

from typing import Any, Dict, List, Sequence
from warnings import warn

import numpy as np

__all__ = [
    "BMAD_SR_WAKE_SAMPLES",
    "bmad_sr_wake_function",
    "sample_bmad_sr_wake",
]

BMAD_SR_WAKE_SAMPLES = 4001
"""Points across ``z_max``, endpoints included."""

_DECAY_EFOLDS = 12.0
"""Exponential decay past the slowest mode."""

_POINTS_PER_EFOLD = 2.0
_POINTS_PER_PERIOD = 8.0

_MONOPOLE = "none"

_DIPOLE = "leading"


def bmad_sr_wake_function(
    modes: Sequence[Sequence[Any]], s, *, z_scale: float = 1.0
) -> np.ndarray:
    """Evaluate a set of Bmad pseudo-modes at separation(s) *s*.

    Parameters
    ----------
    modes: sequence
        Rows as ``ele_wake(..., who="sr_long_table")`` returns them:
        ``[amp, damp, k, phi, ...]``.
    s: float or array
        Distance behind the source particle, non-negative and in metres.
    z_scale: float
        The element's ``sr%z_scale``.

    Returns
    -------
    numpy.ndarray
        The wake in the modes' own units (V/C, or V/C/m when the element's
        ``scale_with_length`` is set).
    """
    scaled = np.asarray(s, dtype=float) * z_scale
    total = np.zeros(scaled.shape, dtype=float)
    for row in modes:
        amp, damp, k, phi = (float(value) for value in row[:4])
        total += amp * np.exp(-damp * scaled) * np.sin(2.0 * np.pi * phi - k * scaled)
    return total


def _usable(
    rows: Sequence[Sequence[Any]],
    column: int,
    wanted: str,
    kind: str,
    name: str,
    verbose: bool,
) -> List[Sequence[Any]]:
    """Drop the modes a sampled wake cannot represent, saying which and why."""
    keep, dropped = [], []
    for row in rows:
        dependence = str(row[column]).lower() if len(row) > column else wanted
        (keep if dependence == wanted else dropped).append((row, dependence))
    if dropped and verbose:
        listed = ", ".join(sorted({dependence for _, dependence in dropped}))
        warn(
            f"Bmad element {name!r} has {len(dropped)} {kind} short-range wake "
            f"mode(s) with position dependence {listed}, which scale the kick "
            "by a particle's transverse coordinate. Only the "
            f"{wanted!r} mode(s) are sampled."
        )
    return [row for row, _ in keep]


def _grid(
    rows: Sequence[Sequence[Any]],
    z_max: float,
    z_scale: float,
    samples: int,
    name: str,
    verbose: bool,
) -> np.ndarray:
    """Choose the separations to sample these modes at.

    The grid stays uniform: Bmad's tabulated wake parser derives ``dz`` from the
    spacing of the first two points and assumes the rest match.
    """
    rates = [abs(float(row[1])) * z_scale for row in rows]
    span = z_max
    if rates and min(rates) > 0.0:
        span = min(z_max, _DECAY_EFOLDS / min(rates))

    if verbose:
        wavenumbers = [abs(float(row[2])) * z_scale for row in rows]
        features = [1.0 / rate for rate in rates if rate > 0.0]
        features += [2.0 * np.pi / k for k in wavenumbers if k > 0.0]
        per_feature = [_POINTS_PER_EFOLD] * sum(rate > 0.0 for rate in rates)
        per_feature += [_POINTS_PER_PERIOD] * sum(k > 0.0 for k in wavenumbers)
        needed = max(
            (
                int(np.ceil(points * span / feature)) + 1
                for feature, points in zip(features, per_feature)
            ),
            default=0,
        )
        if needed > samples:
            finest = min(features)
            warn(
                f"Bmad element {name!r} has a short-range wake structure "
                f"{finest:.3g} m across sampled every {span / (samples - 1):.3g} m; "
                f"about {needed} points are needed to resolve it and {samples} "
                "were used. Raise the importer's wake_samples."
            )
    return np.linspace(0.0, span, samples)


def sample_bmad_sr_wake(
    base: Dict[str, Any],
    long_modes: Sequence[Sequence[Any]] = (),
    trans_modes: Sequence[Sequence[Any]] = (),
    *,
    length: float = 0.0,
    name: str = "",
    samples: int = BMAD_SR_WAKE_SAMPLES,
    verbose: bool = True,
) -> Dict[str, np.ndarray] | None:
    """Sample one element's short-range wake onto a uniform grid.

    Parameters
    ----------
    base: dict
        ``ele_wake(..., who="base")``, taken from Tao.
    long_modes, trans_modes: sequence
        ``who="sr_long_table"`` and ``who="sr_trans_table"`` rows.
    name: str
        Element name, used only in warnings.
    samples: int
        Points across the sampled span. See :data:`BMAD_SR_WAKE_SAMPLES`.

    Returns
    -------
    dict or None
        ``{"z": ..., "Wz": ..., "Wx": ..., "Wy": ...}`` on a common grid, or
        ``None`` if there is nothing to sample.
    """
    z_max = float(base.get("sr%z_max") or 0.0)
    if z_max <= 0.0 or samples < 2:
        if verbose:
            warn(
                f"Bmad element {name!r} carries a short-range wake with no "
                f"usable z_max ({z_max}), so it cannot be sampled and is "
                "dropped."
            )
        return None

    z_scale = float(base.get("sr%z_scale") or 1.0)
    amp_scale = float(base.get("sr%amp_scale") or 0.0)
    if amp_scale == 0.0:
        return None

    long_rows = _usable(long_modes, 4, _MONOPOLE, "longitudinal", name, verbose)
    trans_rows = _usable(trans_modes, 5, _DIPOLE, "transverse", name, verbose)
    if not long_rows and not trans_rows:
        return None

    scale = amp_scale
    if base.get("sr%scale_with_length", True):
        scale *= float(length)
    if scale == 0.0:
        return None

    separation = _grid(
        list(long_rows) + list(trans_rows), z_max, z_scale, samples, name, verbose
    )
    axis_z = -separation[::-1]
    axis_z[-1] = 0.0
    sampled: Dict[str, np.ndarray] = {"z": axis_z}
    if long_rows:
        wake = scale * bmad_sr_wake_function(long_rows, separation, z_scale=z_scale)
        sampled["Wz"] = wake[::-1]
    for key, polarizations in (("Wx", ("x_axis", "none")), ("Wy", ("y_axis", "none"))):
        rows = [row for row in trans_rows if str(row[4]).lower() in polarizations]
        if rows:
            wake = scale * bmad_sr_wake_function(rows, separation, z_scale=z_scale)
            sampled[key] = wake[::-1]
    return sampled
