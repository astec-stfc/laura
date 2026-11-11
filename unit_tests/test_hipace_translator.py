"""HiPACE++ export of plasma stages. Set HIPACE_EXE (or put ``hipace`` on PATH) to run the real binary."""

import os
import re
import shutil
import subprocess

import numpy as np
import pytest
from scipy.constants import c

from laura.models.element import Drift, Plasma, PlasmaLens
from laura.models.element_list import ElementList, SectionLattice
from laura.models.laser import LaserElement
from laura.translator.converters.converter import translate_elements
from laura.translator.converters.section import SectionLatticeTranslator
from laura.translator.utils.hipace import hipace_inputs

HIPACE = os.environ.get("HIPACE_EXE") or shutil.which("hipace")
needs_hipace = pytest.mark.skipif(not HIPACE, reason="no hipace binary (set HIPACE_EXE)")

# Numerics a stage leaves to simba's settings, but without which HiPACE++ will not start.
SETTINGS = {"boundary.field": "Dirichlet", "boundary.particle": "Periodic",
            "diagnostic.dimensions": "xyz", "max_step": 2}
# The incoming beam simba would write; HiPACE++'s adaptive time step needs one.
BEAM = {"beams.names": "beam", "beam.injection_type": "fixed_weight",
        "beam.num_particles": 1000, "beam.total_charge": 1e-10,
        "beam.position_mean": [0, 0, 0], "beam.position_std": [2e-6, 2e-6, 5e-6],
        "beam.u_mean": [0, 0, 2000], "beam.u_std": [0, 0, 0]}


def _plasma(laser=None, simulation=(), **plasma):
    return Plasma(
        name="P",
        machine_area="X",
        physical={"length": 0.012},
        plasma={"density": 1e23, "density_profile": True, "ramp_up": 0.001,
                "plateau": 0.01, "ramp_down": 0.001, **plasma},
        simulation={"r_max": 1e-4, "n_longitudinal": 16, "n_radial": 8,
                    "min_longitudinal_position": -5e-5,
                    "max_longitudinal_position": 5e-5, **dict(simulation)},
        laser=laser,
    )


def _laser(**kwargs):
    return LaserElement(**{"a0": 1.5, "wavelength": 8e-7, "waist": 3e-5,
                           "pulse_duration_fwhm": 3e-14, "initial_position": 1e-5,
                           "focal_position": 2e-3, **kwargs})


def _hipace(element, **kwargs):
    return translate_elements([element])["P"].to_hipace(**kwargs)


PROFILES = {
    "uniform": {"density_profile": False},
    "linear": {"density_profile_type": "linear"},
    "linear_no_upramp": {"density_profile_type": "linear", "ramp_up": 0.0},
    "decaying": {"density_profile_type": "decaying", "ramp_decay_length": 5e-4},
    "tabulated": {"density_profile_type": "tabulated", "density_profile_start": -0.001,
                  "density_profile_positions": [0.004, 0.0, 0.002, 0.009],
                  "density_profile_values": [1.0, 0.2, 0.7, 0.1]},
    "parabolic": {"density_profile_type": "linear", "parabolic_coefficient": 1e8},
}
Z = np.linspace(-0.002, 0.014, 161)
R = 2e-5


def _expected(element):
    return element.plasma._density_profile(Z, R)


@pytest.mark.parametrize("profile", PROFILES)
def test_density_expression_matches_the_model(profile):
    element = _plasma(**PROFILES[profile])
    expr = _hipace(element)["electrons.density(x,y,z)"]
    python = expr.replace("if(", "where(").replace("^", "**")
    got = eval(python, {"where": np.where}, {"x": R, "y": 0.0, "z": Z})
    np.testing.assert_allclose(np.broadcast_to(got, Z.shape), _expected(element),
                               rtol=1e-12, atol=1e-12 * element.plasma.density)


@needs_hipace
@pytest.mark.parametrize("profile", PROFILES)
def test_hipace_parser_agrees(profile, tmp_path):
    element = _plasma(**PROFILES[profile])
    expr = _hipace(element)["electrons.density(x,y,z)"]
    params = SETTINGS | {"amr.n_cell": [8, 8, 8], "geometry.prob_lo": [-1e-5] * 3,
                         "geometry.prob_hi": [1e-5] * 3,
                         "parser.debug_print": f'"{expr}" "x={R}" "y=0" "z=[{Z[0]},{Z[-1]},{Z.size}]"'}
    (tmp_path / "inputs").write_text(hipace_inputs(params))
    out = subprocess.run([HIPACE, "inputs"], cwd=tmp_path, capture_output=True, text=True,
                         timeout=120, env=os.environ | {"OMP_NUM_THREADS": "1"}).stdout
    values = re.search(r'Parser Debug Print ".*" = \[(.*)\]', out).group(1)
    np.testing.assert_allclose([float(v) for v in values.split(",")], _expected(element),
                               rtol=1e-9, atol=1e-9 * element.plasma.density)


@needs_hipace
@pytest.mark.parametrize("stage", ["beam_driven", "laser", "flattened_laser", "ionization"])
def test_stage_starts_in_hipace(stage, tmp_path):
    element = {
        "beam_driven": lambda: _plasma(),
        "laser": lambda: _plasma(laser=_laser(), simulation={"dt_bunch": "1e-13"}),
        "flattened_laser": lambda: _plasma(laser=_laser(profile_type="flattened-gaussian"),
                                           simulation={"dt_bunch": "1e-13"}),
        "ionization": lambda: _plasma(
            laser=_laser(), simulation={"dt_bunch": "1e-13"}, ionizable=True,
            ionization_element="N", ionization_initial_level=5, ionization_density=1e21),
    }[stage]()
    (tmp_path / "inputs").write_text(hipace_inputs(_hipace(element) | SETTINGS | BEAM))
    run = subprocess.run([HIPACE, "inputs"], cwd=tmp_path, capture_output=True, text=True,
                         timeout=300, env=os.environ | {"OMP_NUM_THREADS": "2"})
    assert run.returncode == 0, run.stdout[-3000:] + run.stderr[-3000:]


def test_box_grid_and_run_length():
    params = _hipace(_plasma(n_out=1))
    assert params["amr.n_cell"] == [16, 16, 16]
    assert params["geometry.prob_lo"] == [-1e-4, -1e-4, -5e-5]
    assert params["geometry.prob_hi"] == [1e-4, 1e-4, 5e-5]
    assert params["hipace.max_time"] == pytest.approx(0.012 / c)
    assert params["hipace.dt"] == "adaptive"


def test_fixed_time_step_spaces_the_dumps():
    params = _hipace(_plasma(simulation={"dt_bunch": "1e-12", "n_out": 4}))
    assert params["max_step"] == 41  # 0.012 m / c / 1 ps, rounded up
    assert params["diagnostic.output_period"] == 10


def test_laser_maps_to_a_gaussian_envelope():
    params = _hipace(_plasma(laser=_laser(polarization="circular"),
                             simulation={"dt_bunch": "1e-13", "laser_envelope_n_radial": 32}))
    assert params["laser.tau"] == pytest.approx(3e-14 / np.sqrt(2 * np.log(2)))
    assert params["laser.position_mean"] == [0.0, 0.0, 1e-5]
    assert params["laser.focal_distance"] == 2e-3
    assert params["lasers.polarization"] == "circular"
    assert params["lasers.n_cell"] == [64, 64]


def test_laser_needs_a_fixed_time_step():
    with pytest.raises(ValueError, match="adaptive"):
        _hipace(_plasma(laser=_laser()))


def test_unsupported_laser_profile_is_refused():
    with pytest.raises(ValueError, match="analytic"):
        _hipace(_plasma(laser=_laser(profile_type="file"), simulation={"dt_bunch": "1e-13"}))


def test_chirped_gaussian_keeps_fbpic_energy_and_drops_the_cep():
    tau = 3e-14 / np.sqrt(2 * np.log(2))
    params = _hipace(_plasma(laser=_laser(temporal_chirp_2nd_order=2e-28, cep_phase=np.pi),
                             simulation={"dt_bunch": "1e-13"}))
    assert params["laser.phi2"] == 2e-28  # same sign as FBPIC's phi2_chirp
    assert params["laser.a0"] == pytest.approx(1.5 * (1 + (4e-28 / tau**2) ** 2) ** -0.25)
    assert "laser.CEP" not in params  # HiPACE++ would scale a0 by exp(CEP)


def test_circular_a0_from_energy_is_per_component():
    energy = {"wavelength": 8e-7, "waist": 3e-5, "pulse_energy": 1.0, "pulse_duration_fwhm": 3e-14}
    linear = LaserElement(**energy).amplitude
    assert LaserElement(**energy, polarization="circular").amplitude == pytest.approx(linear / np.sqrt(2))


def _evaluate(expression, x, y, z):
    """Python value of a quoted HiPACE++ parser expression with local variables."""
    *statements, result = expression.strip('"').replace("^", "**").split(";")
    names = {"x": x, "y": y, "z": z, "exp": np.exp, "sqrt": np.sqrt, "cos": np.cos,
             "sin": np.sin, "atan": np.arctan, "atan2": np.arctan2}
    for statement in statements:
        name, value = statement.split("=", 1)
        names[name.strip()] = eval(value, names)
    return eval(result, names)


LASERS = {
    "laguerre_p1": {"profile_type": "laguerre-gaussian", "laguerre_polynomial_order_p": 1},
    "laguerre_p1_m2": {"profile_type": "laguerre-gaussian", "laguerre_polynomial_order_p": 1,
                       "laguerre_polynomial_order_m": 2},
    "donut_m1": {"profile_type": "laguerre-gaussian-donut", "laguerre_polynomial_order_m": 1},
    "flattened_chirped": {"profile_type": "flattened-gaussian", "flatness": 4,
                          "temporal_chirp_2nd_order": 2e-28},
}


@pytest.mark.parametrize("name", LASERS)
def test_parser_laser_is_fbpics_pulse(name):
    pytest.importorskip("fbpic")
    from fbpic.lpa_utils.laser.longitudinal_laser_profiles import GaussianChirpedLongitudinalProfile

    laser = _laser(**LASERS[name])
    params = _hipace(_plasma(laser=laser, simulation={"dt_bunch": "1e-13"}))
    assert params["laser.init_type"] == "parser"
    fbpic = translate_elements([_plasma(laser=laser)])["P"].laser_to_fbpic()
    tau, z0, k0 = laser.pulse_duration_1e_field, laser.initial_position, 2 * np.pi / laser.wavelength
    longitudinal = GaussianChirpedLongitudinalProfile(  # FBPIC's chirp only for its Gaussian
        tau, z0, laser.wavelength, phi2_chirp=laser.temporal_chirp_2nd_order)
    x, y, z = np.meshgrid(np.linspace(-6e-5, 6e-5, 13), [-2e-5, 1e-5], np.linspace(-4e-5, 6e-5, 11))
    expected = (laser.amplitude * fbpic.transverse_profile.evaluate(x, y, z)
                * longitudinal.evaluate(z, 0.0) * np.exp(-1j * k0 * (z - z0)))
    got = (_evaluate(params["laser.laser_real(x,y,z)"], x, y, z)
           + 1j * _evaluate(params["laser.laser_imag(x,y,z)"], x, y, z))
    np.testing.assert_allclose(got, expected, rtol=1e-9, atol=1e-12)


@needs_hipace
@pytest.mark.parametrize("phi2", [0.0, 2e-28])
def test_parser_laser_matches_hipaces_gaussian(phi2, tmp_path):
    """LG(0,0) through the parser against HiPACE++'s own Gaussian: the same envelope,
    up to the constant phase of FBPIC's chirp normalisation."""
    def envelope(profile, run):
        run.mkdir()
        laser = _laser(profile_type=profile, focal_position=3e-5, temporal_chirp_2nd_order=phi2)
        settings = SETTINGS | {"diagnostic.output_period": 1, "max_step": 0}
        params = _hipace(_plasma(laser=laser, simulation={"dt_bunch": "1e-13"})) | settings
        (run / "inputs").write_text(hipace_inputs(params))
        done = subprocess.run([HIPACE, "inputs"], cwd=run, capture_output=True, text=True,
                              timeout=300, env=os.environ | {"OMP_NUM_THREADS": "2"})
        assert done.returncode == 0, done.stdout[-3000:] + done.stderr[-3000:]
        return _openpmd_mesh(_diagnostic(run, 0), "laserEnvelope")[0]

    builtin = envelope("gaussian", tmp_path / "gaussian")
    parser = envelope("laguerre-gaussian", tmp_path / "parser")
    assert np.abs(builtin).max() > 0.1
    if phi2:
        builtin, parser = np.abs(builtin), np.abs(parser)
    np.testing.assert_allclose(parser, builtin, rtol=0, atol=1e-6 * np.abs(builtin).max())


def channel(z, r):
    """A ``custom`` profile: the ``tabulated`` + parabolic one of :data:`CHANNEL`."""
    return np.interp(z, [0.0, 0.006, 0.012], [0.5, 1.0, 0.3]) * (1 + 1e8 * r**2)


CUSTOM = {"density_profile_type": "custom",
          "density_profile_function": "unit_tests.test_hipace_translator:channel"}
CHANNEL = {"density_profile_type": "tabulated", "density_profile_positions": [0.0, 0.006, 0.012],
           "density_profile_values": [0.5, 1.0, 0.3], "parabolic_coefficient": 1e8}


def _openpmd_mesh(path, name, iteration=0):
    """``(data, axis values)`` of a scalar openPMD mesh, e.g. the density file or a
    HiPACE++ diagnostic. h5py, not openpmd_api, which crashes once ROOT is imported."""
    import h5py

    with h5py.File(path) as f:
        mesh = f[f"data/{iteration}/meshes/{name}"]
        data = mesh[()] * mesh.attrs.get("unitSI", 1.0)
        axes = [o + d * np.arange(n) for o, d, n in
                zip(mesh.attrs["gridGlobalOffset"], mesh.attrs["gridSpacing"], data.shape)]
    return data, axes


def _diagnostic(run, iteration):
    return run / f"diags/hdf5/openpmd_{iteration:06d}.h5"


def test_custom_profile_is_written_as_a_density_file(tmp_path):
    params = _hipace(_plasma(**CUSTOM), directory=str(tmp_path))
    assert "electrons.density(x,y,z)" not in params
    path = params["electrons.read_density_from_path"]
    assert path == str(tmp_path / "P_electrons_density.h5")
    data, (z, r) = _openpmd_mesh(path, "density")
    assert z[0] == 0.0 and z[-1] == pytest.approx(0.012)
    assert r[0] < 0 and r[-1] > np.sqrt(2) * 1e-4  # ghosts round the axis, box corners covered
    np.testing.assert_allclose(data, 1e23 * channel(z[:, None], np.abs(r)[None, :]), rtol=1e-12)


def test_custom_profile_needs_a_directory():
    with pytest.raises(ValueError, match="directory"):
        _hipace(_plasma(**CUSTOM))


@needs_hipace
def test_hipace_reads_the_custom_profile_as_the_expression(tmp_path):
    def rho(profile, run):
        run.mkdir()
        settings = SETTINGS | {"hipace.dt": 1e-12, "diagnostic.output_period": 1,
                               "diagnostic.field_data": "rho_electrons",
                               "hipace.deposit_rho_individual": 1}
        params = _hipace(_plasma(**profile), directory=str(run)) | settings
        (run / "inputs").write_text(hipace_inputs(params))
        done = subprocess.run([HIPACE, "inputs"], cwd=run, capture_output=True, text=True,
                              timeout=300, env=os.environ | {"OMP_NUM_THREADS": "2"})
        assert done.returncode == 0, done.stdout[-3000:] + done.stderr[-3000:]
        return [_openpmd_mesh(_diagnostic(run, i), "rho_electrons", i)[0] for i in (0, 1)]

    for expression, from_file in zip(rho(CHANNEL, tmp_path / "expr"), rho(CUSTOM, tmp_path / "file")):
        # Quadratic-spline interpolation of the file adds ~dr^2/4 to the r^2 term.
        np.testing.assert_allclose(from_file, expression, rtol=1e-2, atol=1e-3 * np.abs(expression).max())


def test_background_is_neutralised_unless_ions_move():
    params = _hipace(_plasma())
    assert params["plasmas.names"] == ["electrons"]
    assert "electrons.neutralize_background" not in params  # HiPACE++ default: immobile ions
    params = _hipace(_plasma(), include_ions=True)
    assert params["plasmas.names"] == ["electrons", "ions"]
    assert params["ions.element"] == "proton"
    assert params["electrons.neutralize_background"] == params["ions.neutralize_background"] == 0


def test_ionizable_atoms_bring_their_freed_electrons():
    params = _hipace(_plasma(density_profile=False, ionizable=True, ionization_element="N",
                             ionization_initial_level=5, ionization_density=1e21))
    assert params["plasmas.names"] == ["electrons", "atoms", "atom_electrons", "injected"]
    assert params["atoms.density(x,y,z)"] == "1e+21"
    assert params["atom_electrons.density(x,y,z)"] == "5e+21"
    assert params["atoms.ionization_product"] == "injected"
    assert params["atoms.can_laser_ionize"] == 0


def test_section_exports_only_plasma_stages():
    registry = {"D": Drift(name="D", machine_area="X", physical={"length": 0.1}),
                "P": _plasma()}
    lattice = SectionLattice(name="S", order=list(registry), elements=ElementList(elements=registry))
    assert list(SectionLatticeTranslator.from_section(lattice).to_hipace()) == ["P"]


def _lens(**kwargs):
    return PlasmaLens(name="P", machine_area="X", physical={"length": 0.02},
                      simulation={"r_max": 1e-4, "n_longitudinal": 16, "n_radial": 8,
                                  "min_longitudinal_position": -5e-5,
                                  "max_longitudinal_position": 5e-5, "dt_bunch": "1e-12"},
                      focusing_strength=500.0, **kwargs)


def test_plasma_lens_is_a_field_on_the_beams():
    params = _hipace(_lens())
    assert params["plasmas.names"] == "no_plasma"
    assert params["beams.external_B(x,y,z,t)"] == ["500.0*y", "-500.0*x", 0.0]
    assert params["hipace.max_time"] == pytest.approx(0.02 / c)


def test_plasma_lens_with_wakefields_has_its_plasma():
    params = _hipace(_lens(wakefields=True, plasma={"density": 1e22}))
    assert params["plasmas.names"] == ["electrons"]
    assert params["electrons.density(x,y,z)"] == "1e+22"


def test_plasma_lens_without_plasma_needs_a_fixed_time_step():
    lens = _lens()
    lens.simulation.dt_bunch = "auto"
    with pytest.raises(ValueError, match="adaptive"):
        _hipace(lens)


@needs_hipace
def test_plasma_lens_focuses_electrons_in_hipace(tmp_path):
    """Thin lens: an electron beam offset by x0 leaves with px = -e g L x0, towards the axis."""
    import h5py
    from scipy.constants import e

    x0 = 1e-5
    lens = _hipace(_lens())
    beam = BEAM | {"beam.position_mean": [x0, 0, 0], "beam.position_std": [1e-8, 1e-8, 5e-6],
                   "beam.u_mean": [0, 0, 2e4]}
    params = lens | SETTINGS | beam | {"max_step": lens["max_step"],
                                       "diagnostic.beam_output_period": lens["max_step"]}
    (tmp_path / "inputs").write_text(hipace_inputs(params))
    run = subprocess.run([HIPACE, "inputs"], cwd=tmp_path, capture_output=True, text=True,
                         timeout=300, env=os.environ | {"OMP_NUM_THREADS": "2"})
    assert run.returncode == 0, run.stdout[-3000:] + run.stderr[-3000:]
    step = lens["max_step"]
    with h5py.File(_diagnostic(tmp_path, step)) as f:
        px = f[f"data/{step}/particles/beam/momentum/x"]
        mean_px = np.mean(px[()]) * px.attrs["unitSI"]
    assert mean_px == pytest.approx(-e * 500.0 * 0.02 * x0, rel=1e-3)


def test_inputs_rendering():
    text = hipace_inputs({"a": [1, 2.5], "b": True, "c": np.float64(0.1), "d": "if(z<0,1,2)"})
    assert text == "a = 1 2.5\nb = 1\nc = 0.1\nd = if(z<0,1,2)\n"
