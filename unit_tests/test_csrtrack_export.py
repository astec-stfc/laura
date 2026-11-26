"""CSRTrack takes each field boundary in Hesse form in the global frame: ``rho``
the line's distance from the origin, ``psi`` its normal's angle in degrees. The
dipole writer gave psi as the local rotation plus the edge angle, in radians,
with ``rho`` the face's z, so only a bend whose faces were all square to z came
out right."""

import math
import re

import pytest

from laura.models.element import Dipole
from laura.translator.converters.converter import translate_elements

ANGLE = 0.2


def faces(**edges):
    element = Dipole(
        name="B1", machine_area="A",
        physical={"length": 0.2, "middle": [0, 0, 10.1]},
        magnetic={"angle": ANGLE, "length": 0.2, **edges},
    )
    # Lay it out first, as a loaded lattice does: the translator copies physical_angle
    # as given, so a bend never laid out is translated straight.
    element.physical.end
    bend = translate_elements([element])["B1"]
    written = re.findall(r"rho=([-\d.e]+), psi=([-\d.e]+)", bend.to_csrtrack(n=1))
    return bend.physical, [(float(r), float(p)) for r, p in written]


def test_a_sector_bend_exits_normal_to_the_bent_trajectory():
    physical, ((rho1, psi1), (rho2, psi2)) = faces()
    assert psi1 == 0.0 and rho1 == pytest.approx(physical.start.z)
    # LAURA bends a positive angle towards +x; CSRTrack wants the exit normal at -angle
    assert psi2 == pytest.approx(-math.degrees(ANGLE))
    end = physical.end
    assert end.x > 0
    assert rho2 == pytest.approx(end.z * math.cos(ANGLE) + end.x * math.sin(ANGLE))


def test_a_rectangular_bend_has_parallel_faces():
    _, ((_, psi1), (_, psi2)) = faces(
        entrance_edge_angle=ANGLE / 2, exit_edge_angle=ANGLE / 2
    )
    assert psi1 == pytest.approx(psi2) == pytest.approx(-math.degrees(ANGLE / 2))
