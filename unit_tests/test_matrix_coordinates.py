"""A MatrixTransform's map is in Bmad's (x, px, y, py, z, pz), z = -beta c dt and
pz = dp / p0, which Tao tracks unchanged. MAD-X and Xsuite get it in their own
coordinates, exact to second order; checked at 1 MeV, where beta = 0.86."""

import numpy as np
import pytest

from laura.models.element import MatrixTransform
from unit_tests.test_misalignment_export import section, translator

M, E = 0.51099895e-3, 1e-3  # GeV
P = np.sqrt(E**2 - M**2)
rng = np.random.default_rng(1)
C = np.array([1e-4, 0, 0, 0, 2e-4, 1e-4])
R = np.eye(6) + 0.3 * rng.standard_normal((6, 6))
T = 0.5 * rng.standard_normal((6, 6, 6))
START = 1e-4 * np.array(
    [
        [1, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 1],
        [0, 0, 0, 0, 1, 0],
        [0, 0, 0, 0, 1, 1],
        [1, 0.2, -1, 0.1, 0.2, -0.5],
    ]
)
EXPECTED = C + START @ R.T + np.einsum("ijk,nj,nk->ni", T, START, START)
TOL = 1e-10
"""Third order in the amplitudes; ignoring 1/gamma^2 in T is 7e-10."""


def matrix():
    return MatrixTransform(
        name="m",
        machine_area="S",
        physical={"length": 0.5},
        simulation={"c_matrix": C, "r_matrix": R, "t_matrix": T},
    )


def test_madx_keeps_a_linear_map_linear():
    """MAD-X's TRACK refuses a MATRIX with T terms."""
    linear = MatrixTransform(name="m", machine_area="S", simulation={"r_matrix": R})
    text = translator(linear).to_madx(gamma=E / M)
    assert "rm56" in text and "tm" not in text


def test_madx():
    madx = pytest.importorskip("cpymad.madx").Madx(stdout=False)
    with pytest.warns(UserWarning, match="beta = 1"):
        translator(matrix()).to_madx()
    madx.input(section(matrix()).to_madx(beam={"particle": "electron", "energy": E}))
    tracked = []
    for x, px, y, py, z, pz in START:
        energy = np.hypot((1 + pz) * P, M)
        # MAD-X's t = z / beta and pt = dE / p0c
        start = {"x": x, "px": px, "y": y, "py": py, "t": z * energy / (1 + pz) / P}
        end = madx.twiss(betx=1, bety=1, pt=(energy - E) / P, **start).dframe().iloc[-1]
        energy = E + end.pt * P
        p = np.sqrt(energy**2 - M**2)
        tracked.append([end.x, end.px, end.y, end.py, end.t * p / energy, p / P - 1])
    np.testing.assert_allclose(tracked, EXPECTED, rtol=0, atol=TOL)


def test_xsuite():
    xt = pytest.importorskip("xtrack")
    reference = xt.Particles(mass0=M * 1e9, gamma0=E / M)
    line = section(matrix()).to_xsuite(
        beam_length=1, particle_ref=reference, save=False
    )
    x, px, y, py, z, pz = START.T
    particles = line.build_particles(x=x, px=px, y=y, py=py, delta=pz)
    # zeta = beta0 z / beta
    particles.zeta = z / particles.rvv
    line.track(particles)
    order = np.argsort(particles.particle_id)
    tracked = np.column_stack(
        [
            particles.x,
            particles.px,
            particles.y,
            particles.py,
            particles.zeta * particles.rvv,
            particles.delta,
        ]
    )[order]
    np.testing.assert_allclose(tracked, EXPECTED, rtol=0, atol=TOL)
