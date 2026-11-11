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


def test_injector_laser_is_not_a_driver():
    pytest.importorskip("wake_t")
    plasma = _plasma()
    plasma.laser = LaserElement(role="injector", a0=0.03, wavelength=8e-7,
                                waist=5e-6, pulse_duration_fwhm=3e-14)
    translator = translate_elements([plasma])["P"]
    assert translator.driver_laser is None
    with pytest.warns(UserWarning, match="injector"):
        assert translator.to_wake_t().wakefield.laser is None


def test_wake_t_and_fbpic_focus_in_the_same_place():
    # Wake-T's z_foc is a distance from the pulse centre; FBPIC's zf a position.
    pytest.importorskip("wake_t")
    pytest.importorskip("fbpic")
    laser = LaserElement(a0=2.0, wavelength=8e-7, waist=4e-5, pulse_duration_fwhm=3e-14,
                         initial_position=1e-3, focal_position=3e-3)
    plasma = _plasma()
    plasma.laser = laser
    translator = translate_elements([plasma])["P"]
    r = np.linspace(0, 1e-4, 50)
    wake_t = translator.to_wake_t().wakefield.laser.envelope_function(1e-3, r, 0.0)
    fbpic = translator.laser_to_fbpic().transverse_profile.evaluate(r, 0 * r, 1e-3 + 0 * r)
    assert np.abs(wake_t) == pytest.approx(2.0 * np.abs(fbpic), rel=1e-9)


def test_fbpic_circular_laser_has_a0_in_each_component():
    pytest.importorskip("fbpic")

    def fields(polarization):
        # Long pulse, so the envelope is flat to 3e-5 over the wavelength sampled.
        plasma = _plasma()
        plasma.laser = LaserElement(a0=2.0, wavelength=8e-7, waist=4e-5,
                                    pulse_duration_fwhm=3e-13, polarization=polarization)
        profile = translate_elements([plasma])["P"].laser_to_fbpic()
        z = np.linspace(-4e-7, 4e-7, 41)  # one wavelength about the pulse centre
        return profile.E_field(0 * z, 0 * z, z, 0.0)

    ex_lin, _ = fields("linear")
    ex, ey = fields("circular")
    assert ex == pytest.approx(ex_lin, abs=1e-12 * np.max(np.abs(ex_lin)))
    # A quarter period apart: |E| does not oscillate with the carrier.
    assert np.hypot(ex, ey) == pytest.approx(np.max(np.abs(ex_lin)), rel=1e-3)


def test_laser_is_linearly_polarized_by_default_in_wake_t():
    # Wake-T treats anything but "linear" as circular, doubling the
    # ponderomotive force on the plasma.
    pytest.importorskip("wake_t")
    plasma = _plasma()
    plasma.laser = LaserElement(a0=3.0, wavelength=8e-7, waist=4e-5, pulse_duration_fwhm=3e-14)
    laser = translate_elements([plasma])["P"].to_wake_t().wakefield.laser
    assert laser.polarization == "linear"
