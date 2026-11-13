"""A laser in a wiggler (laser heater / modulator): carried through translation
and into elegant, with its time profile, and the energy modulation it gives."""

import os

import numpy as np
import pytest
from scipy.constants import c, epsilon_0, pi
from scipy.special import j0, j1

from laura.models.element import Wiggler
from laura.translator.converters.converter import translate_elements
from laura.translator.utils.fields import FieldMap
from laura.translator.utils.fields.field_parameter import set_field

LASER = {"wavelength": 1.03e-6, "waist": 6e-4, "pulse_energy": 5e-5, "pulse_duration_fwhm": 1e-11}


def _wiggler(laser=LASER, **magnetic):
    return Wiggler(
        name="LH",
        machine_area="X",
        physical={"length": 0.5},
        magnetic={"length": 0.5, "period": 0.05, "num_periods": 10, "strength": 1.53, **magnetic},
        laser=laser,
    )


def test_elegant_writes_a_laser_modulator():
    heater, plain = (translate_elements([w])["LH"] for w in (_wiggler(), _wiggler(laser=None)))
    assert heater.laser.pulse_energy == LASER["pulse_energy"]
    line = heater.to_elegant().replace("&\n", "")
    assert line.startswith("LH: lsrmdltr") and "periods = 10" in line
    assert "laser_w0 = 0.0006" in line and "accuracy = 1e-4" in line  # elegant's 0 loses every particle
    assert "laser_peak_power = 4697186" in line
    assert plain.to_elegant().startswith("LH: wiggler")
    no_energy = translate_elements([_wiggler(laser={**LASER, "pulse_energy": 0.0})])["LH"]
    assert no_energy.to_elegant() == plain.to_elegant()


def test_a_time_profile_file_reaches_elegant(tmp_path):
    """The profile is written next to the lattice, and the pulse energy is spread
    over it: a Gaussian field envelope of rms s has integral(f**2) = s*sqrt(pi)."""
    sigma, t = 1e-12, np.linspace(-8e-12, 8e-12, 401)
    profile = FieldMap()
    profile.reset_dicts()
    profile.field_type, profile.read = "LaserTimeProfile", True
    set_field(profile, "t", t, "s")
    set_field(profile, "Ex", np.exp(-t**2 / (2 * sigma**2)), "")
    profile.filename = str(tmp_path / "src" / "pulse.sdds")
    source = profile.write_field_file("sdds", location=str(tmp_path / "pulse.sdds"))
    laser = {**LASER, "pulse_duration_fwhm": None, "initial_position": 3e-4,
             "field_definition": os.path.abspath(source)}
    heater = translate_elements([_wiggler(laser=laser)])["LH"]
    heater.directory = str(tmp_path / "lattice")
    line = heater.to_elegant().replace("&\n", "")
    assert 'time_profile = "pulse.sdds=t+Ex"' in line and (tmp_path / "lattice" / "pulse.sdds").exists()
    assert heater.laser.peak_power == pytest.approx(LASER["pulse_energy"] / (sigma * np.sqrt(pi)), rel=1e-6)
    assert f"time_offset = {-3e-4 / c}" in line  # a laser ahead of the centroid meets earlier electrons


def test_modulation_matches_the_peak_laser_field():
    """dE = e*E0*K*[JJ]*L_u / (2*gamma), with E0 from the peak intensity."""
    gamma = 264.2
    heater = _wiggler()
    power = 0.9394 * LASER["pulse_energy"] / LASER["pulse_duration_fwhm"]
    field = np.sqrt(2 * (2 * power / (pi * LASER["waist"] ** 2)) / (c * epsilon_0))
    xi = 1.53**2 / (4 + 2 * 1.53**2)
    expected = field * 1.53 * (j0(xi) - j1(xi)) * 0.5 / (2 * gamma)
    assert heater.laser_energy_modulation(gamma) == pytest.approx(expected, rel=1e-4)


def test_k_from_the_peak_field_and_resonance():
    heater = _wiggler(strength=0.0, peak_magnetic_field=0.3277)
    assert heater.deflection_parameter == pytest.approx(1.53, rel=1e-3)
    # lambda = lambda_u * (1 + K^2/2) / (2 gamma^2)
    assert heater.resonant_wavelength(264.2) == pytest.approx(0.05 * (1 + 1.53**2 / 2) / (2 * 264.2**2), rel=1e-3)


def test_no_laser_or_no_energy_gives_no_modulation():
    assert _wiggler(laser=None).laser_energy_modulation(264.2) == 0.0
    assert _wiggler(laser={**LASER, "pulse_energy": 0.0}).laser_energy_modulation(264.2) == 0.0


def test_helical_is_refused():
    with pytest.raises(NotImplementedError):
        _wiggler(helical=True).laser_energy_modulation(264.2)
