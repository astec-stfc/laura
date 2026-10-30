"""BDSIM multipole, quadrupole and octupole kicks, misaligned or not, match
MAD-X for an electron, despite the BDSIM 1.7.7 bugs the exporter works around."""

import math
import subprocess
import warnings
from shutil import which

import numpy as np
import pytest

from laura.models.element import Octupole, Quadrupole, RFMultipole
from laura.models.physical import PhysicalElement
from unit_tests.test_misalignment_export import section

P0C, X0, Y0 = 1e9, 1e-3, 0.6e-3

pytestmark = pytest.mark.skipif(which("bdsim") is None, reason="BDSIM is not installed")


def madx_kick(knl, ksl, dx=0.0, dy=0.0, roll=0.0):
    """(dpx, dpy) at (X0, Y0): dpx - i dpy = -sum (knl + i ksl) z^n / n!, in
    the frame of a magnet offset by (dx, dy) and rolled by `roll`."""
    rotation = np.exp(1j * roll)
    z = (complex(X0, Y0) - complex(dx, dy)) / rotation
    kick = -sum((kn + 1j * ks) * z**n / math.factorial(n) for n, (kn, ks) in enumerate(zip(knl, ksl)))
    kick = np.conj(kick) * rotation  # dpx + i dpy, back in the lab frame
    return kick.real, kick.imag


def track(element, tmp_path, integrator_set="bdsimmatrix"):
    """(dpx, dpy) of one electron through `element`, starting on axis-parallel at (X0, Y0)."""
    pybdsim = pytest.importorskip("pybdsim")
    pytest.importorskip("ROOT")
    from pybdsim.Beam import Beam
    from pybdsim.Options import Options

    beam = Beam("e-", np.hypot(P0C, 0.51099895e6) / 1e9, "reference")
    beam.SetX0(X0, unitsstring="m")
    beam.SetY0(Y0, unitsstring="m")
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        machine = section(element).to_bdsim(beam=beam, charge_sign=-1, integrator_set=integrator_set)
    machine.AddOptions(Options(integratorSet=f'"{integrator_set}"'))
    machine.AddSampler("all")
    machine.Write(str(tmp_path / "lat.gmad"))
    subprocess.run(
        ["bdsim", "--file=lat.gmad", "--batch", "--outfile=out", "--ngenerate=1"],
        cwd=tmp_path, check=True, capture_output=True,
    )
    data = pybdsim.Data.Load(str(tmp_path / "out.root"))
    last = data.GetSamplerNames()[-1]
    hit = pybdsim.Data.SamplerData(data, last).data
    return hit["xp"][0], hit["yp"][0]


def rf_multipole(length, knl, ksl, error=None):
    physical = PhysicalElement(length=length, **({"error": error} if error else {}))
    element = RFMultipole(name="M1", machine_area="T", physical=physical)
    element.simulation.knl = list(knl)
    element.simulation.ksl = list(ksl)
    return element


STRENGTHS = [
    pytest.param((0, 0.2, 30.0), (0, 0, 0), id="normal"),
    pytest.param((0, 0, 0), (0, 0.2, 0), id="skew-quad"),
    pytest.param((0, 0, 0), (0, 0, 30.0), id="skew-sextupole"),
    pytest.param((0, 0.2, 30.0), (0, -0.1, 20.0), id="mixed"),
]


@pytest.mark.parametrize("knl, ksl", STRENGTHS)
def test_thin_multipole(tmp_path, knl, ksl):
    assert track(rf_multipole(0.0, knl, ksl), tmp_path) == pytest.approx(madx_kick(knl, ksl), rel=1e-6)


@pytest.mark.parametrize("knl, ksl", STRENGTHS)
def test_thick_multipole(tmp_path, knl, ksl):
    """Short enough that a thin kick is accurate to ~1e-3."""
    assert track(rf_multipole(0.01, knl, ksl), tmp_path) == pytest.approx(madx_kick(knl, ksl), rel=2e-3)


ERROR = {"position": {"x": 3e-4, "y": -2e-4}, "rotation": {"psi": 0.3}}


def test_misaligned_thin_multipole(tmp_path):
    """A roll error has no ``tilt`` of the element's own to fold into."""
    knl, ksl = (0, 0.2, 30.0), (0, -0.1, 20.0)
    got = track(rf_multipole(0.0, knl, ksl, ERROR), tmp_path)
    assert got == pytest.approx(madx_kick(knl, ksl, 3e-4, -2e-4, 0.3), rel=1e-6)


@pytest.mark.parametrize("integrator_set", ["bdsimmatrix", "geant4"])
@pytest.mark.parametrize("tilt, error", [(0.3, {}), (0.0, ERROR), (0.1, ERROR)])
def test_misaligned_quadrupole(tmp_path, integrator_set, tilt, error):
    """bdsim* sets track a quadrupole in the reference frame, so an offset or
    tilted one goes out as a thick multipole."""
    madx = pytest.importorskip("cpymad.madx").Madx(stdout=False)
    quad = Quadrupole(
        name="Q1", machine_area="T", physical={"length": 0.2, "error": error},
        magnetic={"length": 0.2, "k1l": 0.5, "tilt": tilt},
    )
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        madx.input(section(quad).to_madx(beam={"particle": "electron", "pc": P0C / 1e9}))
    twiss = madx.twiss(betx=1, bety=1, x=X0, y=Y0)
    expected = (twiss.px[-1], twiss.py[-1])
    assert track(quad, tmp_path, integrator_set) == pytest.approx(expected, rel=1e-5)


@pytest.mark.parametrize("integrator_set", ["bdsimmatrix", "bdsimone", "geant4"])
def test_octupole(tmp_path, integrator_set):
    k3l, length = 2000.0, 0.01
    element = Octupole(
        name="O1", machine_area="T", physical={"length": length},
        magnetic={"length": length, "multipoles": {"K3L": {"normal": k3l}}},
    )
    expected = madx_kick((0, 0, 0, k3l), (0, 0, 0, 0))
    assert track(element, tmp_path, integrator_set) == pytest.approx(expected, rel=2e-3)
