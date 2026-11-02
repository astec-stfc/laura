"""Plasma/laser model behaviour shared by the Wake-T and FBPIC paths."""

import warnings

import numpy as np
import pytest
from scipy.constants import c, e, epsilon_0, m_e, pi

from laura.models.element import Plasma, PlasmaLens
from laura.models.laser import LaserElement
from laura.translator.converters.converter import translate_elements


def _plasma(**plasma):
    return Plasma(
        name="P",
        machine_area="X",
        physical={"length": 0.012},
        plasma={"density": 1e23, "density_profile": True, "ramp_up": 0.001,
                "plateau": 0.01, "ramp_down": 0.001, **plasma},
        simulation={"wakefield_model": "quasistatic_2d", "r_max": 1e-4,
                    "n_longitudinal": 20, "n_radial": 20,
                    "min_longitudinal_position": -5e-5,
                    "max_longitudinal_position": 5e-5},
    )


def test_explicit_a0_wins_over_pulse_energy():
    laser = LaserElement(a0=2.5, wavelength=8e-7, waist=4e-5,
                         pulse_energy=1.0, pulse_duration_fwhm=3e-14)
    assert laser.amplitude == 2.5


def test_a0_from_energy_uses_gaussian_peak_power():
    lam, w0, E, tau = 8e-7, 4e-5, 1.0, 3e-14
    laser = LaserElement(wavelength=lam, waist=w0, pulse_energy=E, pulse_duration_fwhm=tau)
    peak_intensity = 2 * (0.9394 * E / tau) / (pi * w0**2)
    a0 = e * lam / (2 * pi * m_e * c**2) * np.sqrt(2 * peak_intensity / (epsilon_0 * c))
    assert laser.amplitude == pytest.approx(a0, rel=1e-4)


def test_profile_past_element_end_warns():
    with pytest.warns(UserWarning, match="past the element length"):
        _plasma(plateau=0.02)
    with warnings.catch_warnings():
        warnings.simplefilter("error", UserWarning)
        _plasma()


def test_uniform_plasma_keeps_its_parabolic_channel():
    plasma = _plasma(density_profile=False, parabolic_coefficient=1e9).plasma
    assert not plasma.is_uniform
    assert plasma.relative_density_profile(0.5, np.array([0.0, 1e-5])) == pytest.approx([1.0, 1.1])


def test_wake_t_applies_the_parabolic_channel_once():
    pytest.importorskip("wake_t")
    stage = translate_elements([_plasma(parabolic_coefficient=1e9)])["P"].to_wake_t()
    wf = stage.wakefield
    assert wf.parabolic_coefficient is None
    ratio = wf.density_function(0.006, 1e-5) / wf.density_function(0.006, 0.0)
    assert ratio == pytest.approx(1.1)


def test_plasma_lens_to_wake_t():
    wake_t = pytest.importorskip("wake_t")
    lens = PlasmaLens(name="APL", machine_area="X", physical={"length": 0.02},
                      focusing_strength=400.0)
    obj = translate_elements([lens])["APL"].to_wake_t()
    assert isinstance(obj, wake_t.ActivePlasmaLens)
    assert obj.length == pytest.approx(0.02)


def test_stage_without_laser_is_beam_driven():
    pytest.importorskip("wake_t")
    plasma = _plasma()
    assert plasma.laser is None
    assert translate_elements([plasma])["P"].to_wake_t().wakefield.laser is None
