"""
Conventions LAURA's Accelerator Toolbox (pyAT) exporter and importer share.

Dependency-free, so the importer can use them without the exporter's builders.
"""

from math import factorial
from typing import Dict, List, Tuple

from .alignment import sagitta

CLIGHT = 299792458.0
"""Speed of light [m/s]; AT's ``TimeLag`` is a path length."""

FRINGE_BEND_MODEL = {1: 1, 2: 3}
"""LAURA ``edge_order`` -> AT ``FringeBendEntrance``/``Exit``. AT's model 1 is
first-order Brown; of its second-order models, 3 is the one that matches the
other codes on CLIC DR and br14. Only the ``BndMPoleSymplectic4Pass`` fallback
reads it; 0 means the edge is off."""


def polynoms(
    normal: Dict[int, float], skew: Dict[int, float], length: float
) -> Tuple[List[float], List[float]]:
    """
    ``(PolynomA, PolynomB)`` from LAURA's integrated ``KnL`` by order.

    AT stores ``Kn / n!``: per metre on a thick element, integrated on a thin
    one (``length == 0``).
    """
    order = max([0, *normal, *skew])
    scale = length or 1.0
    poly_a = [skew.get(n, 0.0) / factorial(n) / scale for n in range(order + 1)]
    poly_b = [normal.get(n, 0.0) / factorial(n) / scale for n in range(order + 1)]
    return poly_a, poly_b


def integrated(polynom, length: float) -> Dict[int, float]:
    """Inverse of :func:`polynoms` for one array: non-zero ``KnL`` by order."""
    scale = length or 1.0
    return {
        n: float(value) * factorial(n) * scale
        for n, value in enumerate(polynom)
        if value
    }


def time_lag(phase: float, frequency: float, crest: float = 90.0) -> float:
    """
    AT ``TimeLag`` [m] for LAURA's cavity ``phase`` [deg], 0 on crest.

    ``RFCavityPass`` kicks by ``-V sin(2 pi f (ct - TimeLag) / c)``, so its
    crest is a quarter wavelength after ``TimeLag = 0``. ``CrabCavityPass``
    deflects by ``+V sin(...)``, so pass ``crest=-90``; that matches MAD-X
    ``CRABCAVITY`` (as xtrack reads it).
    """
    return (crest + phase) / 360.0 * CLIGHT / frequency


def cavity_phase(lag: float, frequency: float, crest: float = 90.0) -> float:
    """Inverse of :func:`time_lag`."""
    return lag * frequency / CLIGHT * 360.0 - crest


def at_pivot(length: float, angle: float) -> dict:
    """:func:`~laura.translator.utils.alignment.to_frame` arguments, bar the
    tilt, for pyAT's ``ReferencePoint.CENTRE``: a bend's chord midpoint, in its
    rolled frame."""
    chord = sagitta(length, angle)
    return {"pivot": (-chord, 0.0, 0.0), "chord": chord}
