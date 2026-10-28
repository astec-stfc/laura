"""Crab and deflecting cavities kick ``px = V/pc * cos(phase - w*dt)`` in every
code, ``dt`` being the arrival delay: phase 0 is the full kick at the reference."""

import subprocess
import warnings
from shutil import which

import numpy as np
import pytest

from laura.models.element import CrabCavity, Marker, RFDeflectingCavity
from unit_tests import test_ac_dipole_export as ac
from unit_tests.test_misalignment_export import section, translator

F, V, P0C, C = 4e8, 1e6, 1e9, 299792458.0
DT = (-1e-10, 0.0, 1e-10)
PHASE = 30.0
EXPECTED = [V / P0C * np.cos(np.radians(PHASE) - 2 * np.pi * F * dt) for dt in DT]


def cavity(cls):
    return cls(
        name="C1",
        machine_area="S",
        physical={"s": 0.1, "length": 0.0},
        cavity={"frequency": F, "phase": PHASE},
        simulation={"field_amplitude": V},
    )


def line(cls):
    end = Marker(name="M1", machine_area="S", physical={"s": 0.5, "length": 0.0})
    return section(cavity(cls), end)


pytestmark = pytest.mark.parametrize("cls", [CrabCavity, RFDeflectingCavity])


def test_madx(cls):
    madx = pytest.importorskip("cpymad.madx").Madx(stdout=False)
    madx.input(line(cls).to_madx(beam={"particle": "electron", "pc": P0C / 1e9}))
    kicks = [madx.twiss(betx=1, bety=1, t=-C * dt).px[-1] for dt in DT]
    assert kicks == pytest.approx(EXPECTED, abs=1e-9)


def test_xsuite_and_its_import(cls):
    xt = pytest.importorskip("xtrack")
    from laura.translator.converters.codes.xsuite import XsuiteLatticeImporter

    native = line(cls).to_xsuite(beam_length=1, save=False)
    native.particle_ref = xt.Particles(p0c=P0C, mass0=xt.ELECTRON_MASS_EV)
    particles = native.build_particles(zeta=[-C * dt for dt in DT])
    native.track(particles)
    assert particles.px[np.argsort(particles.particle_id)] == pytest.approx(
        EXPECTED, abs=1e-9
    )
    imported = XsuiteLatticeImporter(line=native).create_element_dictionary()["C1"]
    assert imported.cavity.phase == pytest.approx(PHASE)


@pytest.mark.skipif(which("elegant") is None, reason="elegant is not installed")
def test_elegant(cls, tmp_path):
    pc = P0C / 0.51099895e6
    (tmp_path / "lat.lte").write_text(
        translator(cavity(cls)).to_elegant() + "LN: line=(C1)\n"
    )
    rows = "".join(f"0 0 0 0 {dt} {pc} {i}\n" for i, dt in enumerate(DT))
    (tmp_path / "beam.sdds").write_text(
        "SDDS1\n"
        + "".join(
            f"&column name={n}, units={u}, type=double &end\n"
            for n, u in (("x", "m"), ("xp", '""'), ("y", "m"), ("yp", '""'))
            + (("t", "s"), ("p", '"m$be$nc"'))
        )
        + "&column name=particleID, type=long &end\n"
        "&data mode=ascii, no_row_counts=1 &end\n" + rows
    )
    (tmp_path / "run.ele").write_text(
        f"&run_setup lattice=lat.lte, use_beamline=LN, p_central={pc}, "
        "output=out.sdds &end\n&run_control &end\n"
        "&sdds_beam input=beam.sdds &end\n&track &end\n"
    )
    subprocess.run(["elegant", "run.ele"], cwd=tmp_path, check=True, capture_output=True)
    output = subprocess.run(
        ["sdds2stream", "-col=particleID,xp", "out.sdds"],
        cwd=tmp_path, check=True, capture_output=True, text=True,
    ).stdout
    kicks = [float(xp) for _, xp in sorted(row.split() for row in output.splitlines())]
    # elegant phases a deflector to the bunch's mean arrival time, here dt = 0
    assert kicks == pytest.approx(EXPECTED, abs=1e-9)


@pytest.mark.skipif(not ac.LIBTAO.exists(), reason="libtao is not installed")
def test_bmad_and_its_import(cls, tmp_path):
    from laura.translator.converters.codes.bmad import BmadLatticeImporter

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        tao = ac.TestBmadParity.parsed(tmp_path, translator(cavity(cls)))
        kicks = []
        for dt in DT:
            tao.cmd(f"set particle_start z = {-C * dt}")
            kicks.append(tao.ele_orbit("C1")["px"])
        assert kicks == pytest.approx(EXPECTED, abs=1e-9)
        imported = BmadLatticeImporter(
            lattice_file=str(tmp_path / "lat.bmad"), libtao=str(ac.LIBTAO)
        ).create_laura_element_dictionary(1)["LN_1"]["C1"]
    assert imported.cavity.phase == pytest.approx(PHASE)


def test_elegant_import_inverts_the_export(cls):
    from laura.translator.converters.codes.elegant import ElegantLatticeImporter

    v = {"hardware_type": cls.__name__, "cavity": {"phase": -PHASE}}
    converted = ElegantLatticeImporter.model_construct()._convert_ele_phase_to_phase(v)
    assert converted["cavity"]["phase"] == pytest.approx(PHASE)
