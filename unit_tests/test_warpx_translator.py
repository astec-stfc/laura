"""WarpX export of plasma stages. Set WARPX_EXE to an RZ build (``warpx.rz``) to run the real binary."""

import os
import shutil
import subprocess

import numpy as np
import pytest
from scipy.constants import c, e, m_e

from laura.models.element import BeamBeam, Dipole, Drift, Quadrupole
from laura.models.element_list import ElementList, SectionLattice
from laura.translator.converters.converter import translate_elements
from laura.translator.converters.section import SectionLatticeTranslator
from laura.translator.utils.hipace import hipace_inputs
from unit_tests.test_hipace_translator import (
    CHANNEL,
    CUSTOM,
    PROFILES,
    R,
    Z,
    _expected,
    _laser,
    _lens,
    _plasma,
    channel,
)

WARPX = os.environ.get("WARPX_EXE") or shutil.which("warpx.rz")
needs_warpx = pytest.mark.skipif(not WARPX, reason="no WarpX RZ binary (set WARPX_EXE)")

# Numerics a stage leaves to simba's settings, as in WarpX's RZ laser-acceleration example.
SETTINGS = {"max_step": 2, "warpx.n_rz_azimuthal_modes": 2, "boundary.field_lo": ["none", "pec"],
            # shape 2-3 with 2 RZ modes crashes single-precision CUDA builds (WarpX's own RZ example
            # too; double precision is fine); 1 runs on both
            "boundary.field_hi": ["pec", "pec"], "algo.particle_shape": 1, "amr.max_level": 0,
            # AMReX takes 3/4 of the GPU up front by default; a small card shared with a display hasn't got it
            "amrex.the_arena_init_size": 2**28}
BEAM = {"beam.charge": "-q_e", "beam.mass": "m_e", "beam.injection_style": "gaussian_beam",
        "beam.x_rms": 2e-6, "beam.y_rms": 2e-6, "beam.z_rms": 5e-6, "beam.x_m": 0.0,
        "beam.y_m": 0.0, "beam.z_m": 0.0, "beam.npart": 1000, "beam.q_tot": -1e-10,
        "beam.momentum_distribution_type": "constant", "beam.uz": 2000.0}


def _warpx(element, **kwargs):
    return translate_elements([element])[element.name].to_warpx(**kwargs)


def _with_beam(params):
    return params | BEAM | {"particles.species_names": params.get("particles.species_names", []) + ["beam"]}


@pytest.mark.parametrize("profile", PROFILES)
def test_density_expression_is_the_model_from_the_entrance(profile):
    element = _plasma(**PROFILES[profile])
    expr = _warpx(element, z_entrance=3e-4)["electrons.density_function(x,y,z)"]
    python = expr.replace("if(", "where(").replace("^", "**")
    got = eval(python, {"where": np.where}, {"x": R, "y": 0.0, "z": Z + 3e-4})
    np.testing.assert_allclose(np.broadcast_to(got, Z.shape), _expected(element),
                               rtol=1e-12, atol=1e-12 * element.plasma.density)


def test_box_grid_moving_window_and_run_length():
    params = _warpx(_plasma(), z_entrance=1e-4)
    assert params["geometry.dims"] == "RZ"
    assert params["amr.n_cell"] == [8, 16]
    assert params["geometry.prob_lo"] == [0.0, -5e-5]
    assert params["geometry.prob_hi"] == [1e-4, 5e-5]
    assert params["warpx.moving_window_v"] == 1.0
    assert params["stop_time"] == pytest.approx((1e-4 + 0.012) / c, rel=1e-9, abs=0)


def test_plasma_column_is_the_stage_unless_stated():
    params = _warpx(_plasma(simulation={"particles_per_radial_cell": 2,
                                        "particles_per_angular_cell": 4,
                                        "particles_per_longitudinal_cell": 1,
                                        "r_max_plasma": 8e-5}), z_entrance=1e-4)
    assert params["particles.species_names"] == ["electrons"]
    assert params["electrons.num_particles_per_cell_each_dim"] == [2, 4, 1]  # r, theta, z
    assert params["electrons.zmin"] == 1e-4
    assert params["electrons.zmax"] == pytest.approx(1e-4 + 0.012)
    assert params["electrons.xmax"] == 8e-5
    assert params["electrons.momentum_distribution_type"] == "at_rest"
    stated = _warpx(_plasma(simulation={"plasma_min_longitudinal_position": -2e-5}))
    assert stated["electrons.zmin"] == -2e-5


def test_hot_plasma_and_mobile_ions():
    params = _warpx(_plasma(temperature=10.0), include_ions=True)
    assert params["particles.species_names"] == ["electrons", "ions"]
    assert params["ions.species_type"] == "proton"
    assert params["electrons.ux_th"] == pytest.approx(np.sqrt(10.0 * e / (m_e * c**2)))
    assert params["ions.ux_th"] < params["electrons.ux_th"]


def test_ionizable_atoms_free_into_their_own_species():
    params = _warpx(_plasma(density_profile=False, ionizable=True, ionization_element="N",
                            ionization_initial_level=5, ionization_density=1e21))
    assert params["particles.species_names"] == ["electrons", "atoms", "injected"]
    assert params["atoms.density_function(x,y,z)"] == "1e+21"
    assert params["atoms.charge"] == e
    assert params["atoms.mass"] == pytest.approx(2.3259e-26, rel=1e-3)  # WarpX's example: 14 u
    assert params["atoms.physical_element"] == "N"
    assert params["atoms.ionization_initial_level"] == 5
    assert params["atoms.ionization_product_species"] == "injected"
    assert params["injected.injection_style"] == "none"


def test_custom_profile_is_a_density_file_in_warpx_layout(tmp_path):
    import h5py

    params = _warpx(_plasma(**CUSTOM), z_entrance=3e-4, directory=str(tmp_path))
    assert params["electrons.profile"] == "read_from_file"
    path = params["electrons.read_density_from_path"]
    with h5py.File(path) as f:
        mesh = f["data/0/meshes/density"]
        assert [a.decode() for a in mesh.attrs["axisLabels"]] == ["z", "r"]  # WarpX reads {z, r}
        data = mesh[()]
        assert data.shape[0] == 1  # mode 0 only
        z0, r0 = mesh.attrs["gridGlobalOffset"]
        dz, dr = mesh.attrs["gridSpacing"]
    assert z0 == pytest.approx(3e-4)  # the stage entrance, in lab z
    z = z0 + dz * np.arange(data.shape[1])
    r = r0 + dr * np.arange(data.shape[2])
    np.testing.assert_allclose(data[0], 1e23 * channel(z[:, None] - 3e-4, np.abs(r)[None, :]), rtol=1e-12)


def test_custom_profile_needs_a_directory():
    with pytest.raises(ValueError, match="directory"):
        _warpx(_plasma(**CUSTOM))


def test_laser_antenna_sits_ahead_of_the_pulse():
    laser = _laser()
    params = _warpx(_plasma(laser=laser))
    tau = laser.pulse_duration_1e_field
    assert params["lasers.names"] == ["laser"]
    assert params["laser.profile_duration"] == tau
    assert params["laser.position"] == [0.0, 0.0, pytest.approx(1e-5 + 3 * c * tau)]
    assert params["laser.profile_t_peak"] == pytest.approx(3 * tau, rel=1e-9, abs=0)
    assert params["laser.profile_focal_distance"] == pytest.approx(2e-3 - 1e-5 - 3 * c * tau)
    params = _warpx(_plasma(laser=laser), antenna_offset=2e-5)
    assert params["laser.position"][2] == pytest.approx(3e-5)


def test_antenna_outside_the_box_warns():
    with pytest.warns(UserWarning, match="outside the simulation box"):
        _warpx(_plasma(laser=_laser(initial_position=4e-5)))


@pytest.mark.parametrize("laser", [{"profile_type": "flattened-gaussian"}, {"propagation_direction": -1},
                                   {"polarization": "elliptical"}])
def test_unsupported_lasers_are_refused(laser):
    with pytest.raises(ValueError, match="Gaussian"):
        _warpx(_plasma(laser=_laser(**laser)))


def _warpx_antenna_field(params, name, x, y, t):
    """
    (Ex, Ey) WarpX's Gaussian antenna emits: ``GaussianLaserProfile::fill_amplitude``
    (``Source/Laser/LaserProfilesImpl/LaserProfileGaussian.cpp``, RZ/3D, zeta = beta = 0)
    times the polarization vector.
    """
    p = {key.split(".", 1)[1]: value for key, value in params.items() if key.startswith(name + ".")}
    k0 = 2 * np.pi / p["wavelength"]
    e_max = m_e * k0 * c**2 * p["a0"] / e  # LaserParticleContainer.cpp
    inv_tau2 = 1 / p["profile_duration"] ** 2
    diffract = 1 + 1j * p["profile_focal_distance"] * 2 / (k0 * p["profile_waist"] ** 2)
    stretch = 1 + 2j * p["phi2"] * inv_tau2
    dt = t - p["profile_t_peak"]
    amplitude = (e_max * np.exp(1j * (k0 * c * dt + p["phi0"])) / diffract
                 * np.exp(-dt**2 * inv_tau2 / stretch)
                 * np.exp(-(x**2 + y**2) / (p["profile_waist"] ** 2 * diffract))).real
    pol = np.asarray(p["polarization"]) / np.linalg.norm(p["polarization"])
    return amplitude * pol[0], amplitude * pol[1]


@pytest.mark.parametrize("laser", [{}, {"temporal_chirp_2nd_order": 2e-28, "cep_phase": 0.7},
                                   {"polarization": "circular", "polarization_angle": 0.3},
                                   {"focal_position": -1e-3, "cep_phase": -2.0}])
def test_antenna_emits_fbpics_pulse(laser):
    """At the antenna plane WarpX's field is FBPIC's, a0, CEP, chirp and polarization included."""
    pytest.importorskip("fbpic")
    element = _plasma(laser=_laser(**laser))
    params = _warpx(element)
    fbpic = translate_elements([element])["P"].laser_to_fbpic()
    z_antenna = params["laser.position"][2]
    x, y, t = np.meshgrid(np.linspace(-6e-5, 6e-5, 7), [-2e-5, 1e-5],
                          params["laser.profile_t_peak"] + np.linspace(-8e-14, 8e-14, 401))
    expected = np.array(fbpic.E_field(x, y, z_antenna, t))
    got = sum(np.array(_warpx_antenna_field(params, name, x, y, t)) for name in params["lasers.names"])
    np.testing.assert_allclose(got, expected, rtol=0, atol=1e-9 * np.abs(expected).max())


def _line(*elements, **kwargs):
    """``to_warpx`` of a section of ``elements``, placed end to end from z = 0."""
    s = 0.0
    for element in elements:
        element.physical.middle.z = s + element.physical.length / 2
        s += element.physical.length
    registry = {element.name: element for element in elements}
    lattice = SectionLattice(name="S", order=list(registry), elements=ElementList(elements=registry))
    return SectionLatticeTranslator.from_section(lattice).to_warpx(**kwargs)


def _quad(name, k1, length=0.1):
    return Quadrupole(name=name, machine_area="X", physical={"length": length},
                      magnetic={"length": length, "k1l": k1 * length})


def test_fodo_is_a_lattice_of_drifts_and_quads():
    params = _line(_quad("QF", 2.0), Drift(name="D-1", machine_area="X", physical={"length": 0.3}),
                   _quad("QD", -2.0), Brho=0.5, charge_sign=-1)
    assert params["lattice.elements"] == ["QF", "D_1", "QD"]  # names ParmParse-safe
    assert params["QF.type"] == "quad"
    assert params["QF.ds"] == pytest.approx(0.1)
    assert params["QF.dBdx"] == pytest.approx(-1.0)  # electrons: k1 > 0 needs dBy/dx < 0
    assert params["QD.dBdx"] == pytest.approx(1.0)
    assert params["D_1.type"] == "drift"
    assert "geometry.dims" not in params  # no stage, no box: the caller sets it


def test_quad_gradient_needs_brho():
    with pytest.raises(ValueError, match="Brho"):
        _line(_quad("QF", 2.0))


def test_other_elements_are_drifts_of_their_length():
    bend = Dipole(name="B", machine_area="X", physical={"length": 0.2}, magnetic={"length": 0.2})
    with pytest.warns(UserWarning, match="B is a drift"):
        params = _line(bend)
    assert params["B.type"] == "drift"
    assert params["B.ds"] == pytest.approx(0.2)


def test_line_starts_after_a_lead_in_from_box_z_zero():
    params = _line(_quad("QF", 0.0), zstart=-0.05)
    assert params["lattice.elements"] == ["lead_in", "QF"]
    assert params["lead_in.ds"] == pytest.approx(0.05)


def test_line_behind_box_z_zero_is_left_out():
    """A beam starting inside the line: WarpX's lattice holds what is ahead of it."""
    params = _line(_quad("QF", 0.0), _quad("QD", 0.0), zstart=0.15)
    assert params["lattice.elements"] == ["QD"]
    assert params["QD.ds"] == pytest.approx(0.05)
    params = _line(_quad("QF", 0.0), _plasma(), zstart=0.103)
    assert params["P.ds"] == pytest.approx(0.009)
    assert params["electrons.zmin"] == pytest.approx(-0.003)  # the stage entrance, behind the beam


def test_plasma_lens_is_a_lattice_element():
    params = _line(Drift(name="D", machine_area="X", physical={"length": 1e-4}), _lens())
    assert "particles.species_names" not in params
    assert params["lattice.elements"] == ["D", "P"]
    assert params["P.type"] == "plasmalens"
    assert params["P.ds"] == pytest.approx(0.02)
    assert params["P.dBdx"] == 500.0  # B = g (y, -x): HiPACE++'s sign
    assert params["stop_time"] == pytest.approx((1e-4 + 0.02) / c, rel=1e-9, abs=0)  # the lens's own box


def test_plasma_lens_with_wakefields_has_its_plasma():
    params = _line(_lens(wakefields=True, plasma={"density": 1e22}))
    assert params["particles.species_names"] == ["electrons"]
    assert params["P.type"] == "plasmalens"


def test_stage_sits_in_the_line_as_a_drift():
    params = _line(_quad("QF", 0.0), _plasma(), zstart=-0.01)
    assert params["lattice.elements"] == ["lead_in", "QF", "P"]
    assert params["P.type"] == "drift"
    assert params["electrons.zmin"] == pytest.approx(0.11)


def _beam_beam(**simulation):
    return BeamBeam(name="BB", machine_area="X", physical={"middle": {"z": 0.0}},
                    simulation={"charge": 1.0, "n_particles": 2e10, "horizontal_sigma": 5e-6,
                                "vertical_sigma": 2e-6, "horizontal_offset": 1e-6, **simulation})


def test_beam_beam_is_an_opposing_gaussian_bunch():
    params = translate_elements([_beam_beam()])["BB"].to_warpx(
        1e9, 0.51099895e6, z_centre=0.01, sigma_z=1e-3, macroparticles=500)
    assert params["opposing.charge"] == pytest.approx(e)
    assert params["opposing.q_tot"] == pytest.approx(2e10 * e)
    assert params["opposing.npart"] == 500
    assert (params["opposing.x_rms"], params["opposing.y_rms"]) == (5e-6, 2e-6)
    assert params["opposing.z_rms"] == 1e-3  # no width: the given length
    assert params["opposing.x_m"] == 1e-6
    assert params["opposing.z_m"] == 0.01
    assert params["opposing.uz"] == pytest.approx(-1e9 / 0.51099895e6)  # towards -z
    assert params["opposing.mass"] == pytest.approx(m_e, rel=1e-6)
    stated = translate_elements([_beam_beam(width=2e-3)])["BB"].to_warpx(1e9, 0.51099895e6, 0.0, 1e-3)
    assert stated["opposing.z_rms"] == 2e-3
    with pytest.raises(ValueError, match="n_particles"):
        translate_elements([_beam_beam(n_particles=0)])["BB"].to_warpx(1e9, 0.51099895e6, 0.0, 1e-3)


def test_one_stage_per_line():
    second = _plasma()
    second.name = "P2"
    with pytest.raises(ValueError, match="one plasma stage"):
        _line(_plasma(), second)


@needs_warpx
def test_warpx_reads_the_custom_profile_as_the_expression(tmp_path):
    """The file and the parser expression give the same plasma: WarpX's rho at step 0."""
    def rho(profile, run):
        run.mkdir()
        params = _line(_plasma(**profile), directory=str(run)) | SETTINGS | {
            "max_step": 0, "diagnostics.diags_names": "d", "d.diag_type": "Full", "d.intervals": 1,
            "d.format": "openpmd", "d.openpmd_backend": "h5", "d.fields_to_plot": "rho"}
        (run / "inputs").write_text(hipace_inputs(params))
        done = subprocess.run([WARPX, "inputs"], cwd=run, capture_output=True, text=True,
                              timeout=300, env=os.environ | {"OMP_NUM_THREADS": "2"})
        assert done.returncode == 0, done.stdout[-3000:] + done.stderr[-3000:]
        import h5py
        with h5py.File(next((run / "diags" / "d").glob("*.h5"))) as f:
            return next(iter(f["data"].values()))["fields/rho"][()][0]  # WarpX's meshesPath

    expression, from_file = rho(CHANNEL, tmp_path / "expr"), rho(CUSTOM, tmp_path / "file")
    np.testing.assert_allclose(from_file, expression, rtol=2e-2, atol=1e-3 * np.abs(expression).max())


@needs_warpx
@pytest.mark.parametrize("stage", ["beam_driven", "laser", "circular_laser", "ionization", "lens"])
def test_stage_starts_in_warpx(stage, tmp_path):
    element = {
        "beam_driven": lambda: _plasma(),
        "laser": lambda: _plasma(laser=_laser()),
        "circular_laser": lambda: _plasma(laser=_laser(polarization="circular")),
        "ionization": lambda: _plasma(laser=_laser(), ionizable=True, ionization_element="N",
                                      ionization_initial_level=5, ionization_density=1e21),
        "lens": lambda: _lens(),
    }[stage]()
    (tmp_path / "inputs").write_text(hipace_inputs(_with_beam(_line(element)) | SETTINGS))
    run = subprocess.run([WARPX, "inputs"], cwd=tmp_path, capture_output=True, text=True,
                         timeout=300, env=os.environ | {"OMP_NUM_THREADS": "2"})
    assert run.returncode == 0, run.stdout[-3000:] + run.stderr[-3000:]
