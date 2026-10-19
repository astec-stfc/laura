"""A solenoid's ``S0L`` is its integrated field [T*m]: every code turns an
electron the same way, and each import gets the field back."""

import subprocess
import warnings
from shutil import which

import numpy as np
import pytest

from laura.models.element import Solenoid
from unit_tests import test_ac_dipole_export as ac
from unit_tests.test_misalignment_export import section, translator

B, L, P0C, C, X0 = 1.0, 0.5, 1e9, 299792458.0, 1e-3
BRHO = -P0C / C  # p / q for an electron
K = B / (2 * BRHO)
c, s = np.cos(K * L), np.sin(K * L)
# (x, px, y, py) at the exit for x = X0 at the entrance
EXPECTED = [c * c * X0, -K * s * c * X0, -s * c * X0, K * s * s * X0]


def solenoid():
    return Solenoid(
        name="S1",
        machine_area="S",
        physical={"s": L, "length": L},
        magnetic={"length": L, "fields": {"S0L": B * L}},
    )


def test_madx_and_its_import(tmp_path):
    madx = pytest.importorskip("cpymad.madx").Madx(stdout=False)
    from laura.translator.converters.codes.madx import MadxLatticeImporter

    text = section(solenoid()).to_madx(
        beam={"particle": "electron", "pc": P0C / 1e9}, Brho=BRHO
    )
    madx.input(text)
    tw = madx.twiss(betx=1, bety=1, x=X0)
    assert [tw.x[-1], tw.px[-1], tw.y[-1], tw.py[-1]] == pytest.approx(EXPECTED)
    (tmp_path / "line.madx").write_text(text)
    imported = MadxLatticeImporter(
        source_file=str(tmp_path / "line.madx")
    ).create_laura_element_dictionary()
    assert imported["s1"].magnetic.fields.S0L == pytest.approx(B * L)


def test_xsuite_and_its_import():
    xt = pytest.importorskip("xtrack")
    from laura.translator.converters.codes.xsuite import XsuiteLatticeImporter

    ref = xt.Particles(p0c=P0C, mass0=xt.ELECTRON_MASS_EV, q0=-1)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", FutureWarning)
        native = section(solenoid()).to_xsuite(
            beam_length=1, save=False, particle_ref=ref
        )
    particles = native.build_particles(x=[X0])
    native.track(particles)
    final = [particles.x[0], particles.px[0], particles.y[0], particles.py[0]]
    assert final == pytest.approx(EXPECTED)
    imported = XsuiteLatticeImporter(line=native).create_element_dictionary()["S1"]
    assert imported.magnetic.fields.S0L == pytest.approx(B * L)


@pytest.mark.skipif(which("elegant") is None, reason="elegant is not installed")
def test_elegant_and_its_import(tmp_path):
    from laura.translator.converters.codes.elegant import ElegantLatticeImporter

    pc = P0C / 0.51099895e6
    (tmp_path / "lat.lte").write_text(
        translator(solenoid()).to_elegant() + "LN: line=(S1)\n"
    )
    (tmp_path / "beam.sdds").write_text(
        "SDDS1\n"
        + "".join(
            f"&column name={n}, units={u}, type=double &end\n"
            for n, u in (("x", "m"), ("xp", '""'), ("y", "m"), ("yp", '""'))
            + (("t", "s"), ("p", '"m$be$nc"'))
        )
        + "&data mode=ascii, no_row_counts=1 &end\n"
        + f"{X0} 0 0 0 0 {pc}\n"
    )
    (tmp_path / "run.ele").write_text(
        f"&run_setup lattice=lat.lte, use_beamline=LN, p_central={pc}, "
        "output=out.sdds &end\n&run_control &end\n"
        "&sdds_beam input=beam.sdds &end\n&track &end\n"
    )
    subprocess.run(["elegant", "run.ele"], cwd=tmp_path, check=True, capture_output=True)
    output = subprocess.run(
        ["sdds2stream", "-col=x,xp,y,yp", "out.sdds"],
        cwd=tmp_path, check=True, capture_output=True, text=True,
    ).stdout
    assert [float(v) for v in output.split()] == pytest.approx(EXPECTED, rel=1e-6)
    imported = ElegantLatticeImporter(
        source_file=str(tmp_path / "lat.lte"), beamline="LN"
    ).create_laura_element_dictionary()["S1"]
    assert imported.magnetic.fields.S0L == pytest.approx(B * L)


@pytest.mark.skipif(not ac.LIBTAO.exists(), reason="libtao is not installed")
def test_bmad_and_its_import(tmp_path):
    from laura.translator.converters.codes.bmad import BmadLatticeImporter

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        tao = ac.TestBmadParity.parsed(tmp_path, translator(solenoid()))
        tao.cmd(f"set particle_start x = {X0}")
        orbit = tao.ele_orbit("S1")
        imported = BmadLatticeImporter(
            lattice_file=str(tmp_path / "lat.bmad"), libtao=str(ac.LIBTAO)
        ).create_laura_element_dictionary(1)["LN_1"]["S1"]
    final = [orbit["x"], orbit["px"], orbit["y"], orbit["py"]]
    assert final == pytest.approx(EXPECTED, rel=1e-6)
    assert imported.magnetic.fields.S0L == pytest.approx(B * L)


def test_normalised_codes_warn_without_the_rigidity():
    with pytest.warns(UserWarning, match="rigidity"):
        text = translator(solenoid()).to_madx()
    assert "ks" not in text
