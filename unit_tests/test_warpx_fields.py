"""1D field maps as analytic WarpX particle fields, and auto-phasing by the reference particle."""

import numpy as np
import pytest
from scipy.constants import c

from laura.models.element import Octupole, Quadrupole, Sextupole, Solenoid, Wiggler
from laura.translator.converters.converter import translate_elements
from laura.translator.utils.fields.onaxis import FieldTerm, Profile, autophase, render, track
from laura.translator.utils.functions import cavity_energy_gain
from unit_tests.test_gpt_export import WAVELENGTH, _cavity, _cavity_element, _rf_map
from unit_tests.test_warpx_translator import _line

ME = 0.51099895e6
P0C = 1e9  # beta = 1 to 1e-7, so transit-time integrals apply


def _evaluate(expression, **variables):
    """Python value of a quoted AMReX parser expression with local variables."""
    *statements, result = expression.strip('"').replace("if(", "where(").replace("^", "**").split(";")
    names = {"cos": np.cos, "sin": np.sin, "cosh": np.cosh, "sinh": np.sinh, "sqrt": np.sqrt, "pi": np.pi,
             "where": np.where, **variables}
    for statement in statements:
        if statement.strip():
            name, value = statement.split("=", 1)
            names[name.strip()] = eval(value, names)
    return eval(result, names)


def test_profile_reproduces_the_map_and_its_slope():
    z = np.linspace(-0.1, 0.3, 801)
    f = np.exp(-((z - 0.1) / 0.03) ** 2) * np.cos(2 * np.pi * z / 0.035)
    profile = Profile.fit(z, f)
    assert len(profile.a) < 100
    assert np.abs(profile(z) - f).max() <= 1e-3
    np.testing.assert_allclose(profile.derivative(z[5:-5]), np.gradient(f, z)[5:-5],
                               atol=3e-3 * np.abs(np.gradient(f, z)).max())
    assert profile(np.array([-0.2, 0.4])) == pytest.approx([0, 0])  # zero outside the map


def test_rendered_fields_are_the_paraxial_expansion():
    z = np.linspace(0, 0.2, 401)
    profile = Profile.fit(z, np.sin(np.pi * z / 0.2) ** 2)
    sol = FieldTerm(profile, 0.3, "B", z=0.5, x=1e-3)
    rf = FieldTerm(profile, 2e7, "E", z=0.5, frequency=3e9, phase=0.4)
    x, y, zz, t = 2e-3, -1e-3, np.linspace(0.45, 0.75, 31), 1.7e-10
    f, d = profile(zz - 0.5), profile.derivative(zz - 0.5)
    b = render([sol])
    assert b["particles.B_ext_particle_init_style"] == "parse_B_ext_particle_function"
    assert "particles.E_ext_particle_init_style" not in b
    get = {k: _evaluate(b[f"particles.B{k}_external_particle_function(x,y,z,t)"], x=x, y=y, z=zz, t=t)
           for k in "xyz"}
    np.testing.assert_allclose(get["z"], 0.3 * f, atol=1e-9)
    np.testing.assert_allclose(get["x"], -0.5 * (x - 1e-3) * 0.3 * d, atol=1e-9)
    np.testing.assert_allclose(get["y"], -0.5 * y * 0.3 * d, atol=1e-9)
    e = render([rf])
    w, arg = 2 * np.pi * 3e9, 2 * np.pi * 3e9 * t + 0.4
    ez = _evaluate(e["particles.Ez_external_particle_function(x,y,z,t)"], x=x, y=y, z=zz, t=t)
    ex = _evaluate(e["particles.Ex_external_particle_function(x,y,z,t)"], x=x, y=y, z=zz, t=t)
    by = _evaluate(e["particles.By_external_particle_function(x,y,z,t)"], x=x, y=y, z=zz, t=t)
    np.testing.assert_allclose(ez, 2e7 * f * np.cos(arg), atol=1e-3)
    np.testing.assert_allclose(ex, -0.5 * x * 2e7 * d * np.cos(arg), atol=1e-3)
    np.testing.assert_allclose(by, -x * w / (2 * c**2) * 2e7 * f * np.sin(arg), atol=1e-12)


def _gain(cavity, phase=0.0):
    cavity.cavity.phase = phase
    terms = cavity.warpx_field_terms(0.0)
    start = min(t.z + t.profile.z0 for t in terms) - 0.01
    end = max(t.z + t.profile.z0 + t.profile.length for t in terms)
    autophase(terms, start, P0C, ME, -1)
    return track(terms, start, P0C, ME, -1, end)[1] - (np.hypot(P0C, ME) - ME)


def test_crest_gain_of_a_standing_wave_is_its_transit_time_integral():
    z = np.linspace(0, 2 * WAVELENGTH, 2001)
    cavity = _cavity(_rf_map(z, np.cos(2 * np.pi * z / WAVELENGTH)), "StandingWave")
    assert _gain(cavity) == pytest.approx(cavity_energy_gain(cavity) * 1e6, rel=1e-3)
    # LAURA's phase is off crest: 60 degrees halves the gain, as for ASTRA and GPT
    assert _gain(cavity, 60.0) == pytest.approx(cavity_energy_gain(cavity, phase=60) * 1e6, rel=1e-3)


def test_travelling_wave_is_two_standing_waves_with_the_maps_gain():
    z = np.linspace(0, 0.3, 3001)
    body = (z >= z[800]) & (z < z[800] + WAVELENGTH)  # no couplers: cavity_energy_gain counts the body only
    field = _rf_map(z, np.where(body, np.cos(2 * np.pi * z / WAVELENGTH), 0.0), start_cell_z=z[800])
    cavity = _cavity(field, "TravellingWave")
    terms = cavity.warpx_field_terms(0.0)
    assert [t.phase for t in terms] == pytest.approx([0.0, np.pi / 2])  # T cos - S sin
    assert _gain(cavity) == pytest.approx(cavity_energy_gain(cavity) * 1e6, rel=1e-2)


def test_solenoid_without_a_map_is_a_current_sheet():
    solenoid = Solenoid(name="S", machine_area="X", physical={"length": 0.2, "middle": {"z": 0.1}},
                        magnetic={"length": 0.2, "ks": 0.06})
    translator = translate_elements([solenoid])["S"]
    with pytest.warns(UserWarning, match="current sheet"):
        (term,) = translator.warpx_field_terms(0.0)
    p = render([term])
    zz, x = np.linspace(-0.5, 0.7, 24001), 1e-4
    bz, bx = (_evaluate(p[f"particles.B{k}_external_particle_function(x,y,z,t)"], x=x, y=0.0, z=zz, t=0.0)
              for k in "zx")
    assert np.trapezoid(bz, zz) == pytest.approx(0.06, rel=2e-3)  # S0L, as for ASTRA and OPAL
    sampled = translator._field_map("warpx")  # the map ASTRA and OPAL get: the same sheet, in closed form here
    z0 = sampled.z.value.val + translator.get_field_reference_position()[2]
    np.testing.assert_allclose(np.interp(z0, zz, bz), translator._map_amplitude("warpx") * sampled.Bz.value.val,
                               atol=2e-4 * term.peak_field)
    # the closed-form slope against a finite difference, which is good to ~0.1 % at the 1 mm-wide edges
    np.testing.assert_allclose(bx, -0.5 * x * np.gradient(bz, zz), atol=2e-3 * np.abs(bx).max())


def _wiggler(**magnetic):
    return Wiggler(name="U", machine_area="X", physical={"length": 0.3, "middle": {"z": 0.15}},
                   magnetic={"length": 0.3, "period": 0.03, "strength": 1.4, **magnetic})


def test_planar_undulator_is_a_vacuum_field_of_whole_periods():
    (term,) = translate_elements([_wiggler()])["U"].warpx_field_terms(0.0)
    assert term.peak_field == pytest.approx(1.4 / (93.3728962 * 0.03))  # K -> B0, as for elegant
    assert term.length == pytest.approx(0.3)  # 10 periods: no net kick
    p = render([term])
    zz, x, y = np.linspace(-0.01, 0.31, 6401), 1e-4, 2e-4
    by, bz = (_evaluate(p[f"particles.B{k}_external_particle_function(x,y,z,t)"], x=x, y=y, z=zz, t=0.0)
              for k in "yz")
    k = 2 * np.pi / 0.03
    inside = (zz >= 0) & (zz <= 0.3)
    np.testing.assert_allclose(by, np.where(inside, term.peak_field * np.cosh(k * y) * np.cos(k * zz), 0), atol=1e-12)
    # curl B = 0: dBy/dz = dBz/dy, exactly
    dbz_dy = -term.peak_field * k * np.cosh(k * y) * np.sin(k * zz)
    np.testing.assert_allclose(np.gradient(by, zz)[inside][2:-2], dbz_dy[inside][2:-2], rtol=1e-3, atol=1e-3)
    assert np.all(bz[~inside] == 0)


def test_helical_undulator_has_both_components():
    (term,) = translate_elements([_wiggler(helical=True)])["U"].warpx_field_terms(0.0)
    p = render([term])
    bx = _evaluate(p["particles.Bx_external_particle_function(x,y,z,t)"], x=0.0, y=0.0, z=0.0075, t=0.0)
    by = _evaluate(p["particles.By_external_particle_function(x,y,z,t)"], x=0.0, y=0.0, z=0.0075, t=0.0)
    assert (bx, by) == pytest.approx((0.0, term.peak_field), abs=1e-12)  # a quarter period in


def test_ignored_wiggler_attributes_warn():
    with pytest.warns(UserWarning, match="tilt"):
        translate_elements([_wiggler(tilt=0.1)])["U"].warpx_field_terms(0.0)


@pytest.mark.parametrize("magnet, n", [(Sextupole, 2), (Octupole, 3)])
def test_multipoles_are_madx_fields_over_their_length(magnet, n):
    """By + i Bx = charge_sign Brho K_n (x + i y)^n / n!: MAD-X's kick of (x' - i y') by -K_n L (x + i y)^n / n!
    for the design particle, as the quadrupole's dBdx = charge_sign Brho k1."""
    from math import factorial

    knl, length, brho = 4.0 * 10**n, 0.2, 0.3
    element = magnet(name="M", machine_area="X", physical={"length": length},
                     magnetic={"length": length, f"k{n}l": knl})
    p = _line(element, Brho=brho, charge_sign=-1)
    assert p["lattice.elements"] == ["M"] and p["M.type"] == "drift"
    x, y, zz = 1.3e-3, -0.7e-3, np.array([-0.01, 0.1, 0.21])
    by, bx = (_evaluate(p[f"particles.B{k}_external_particle_function(x,y,z,t)"], x=x, y=y, z=zz, t=0.0) for k in "yx")
    expected = -brho * knl / length / factorial(n) * (x + 1j * y) ** n
    np.testing.assert_allclose(by + 1j * bx, [0, expected, 0], rtol=1e-12, atol=1e-15)  # zero outside the magnet


def test_gaps_warn_when_met():
    z = np.linspace(0, 2 * WAVELENGTH, 2001)
    tilted = Quadrupole(name="Q", machine_area="X", physical={"length": 0.1}, magnetic={"length": 0.1, "tilt": 0.1})
    with pytest.warns(UserWarning, match="upright"):
        _line(tilted, Brho=1.0)
    gun = _cavity_element("StandingWave")
    gun.physical.length = 2 * WAVELENGTH
    field = _rf_map(z, np.cos(2 * np.pi * z / WAVELENGTH))
    field.field_type = "2DElectroDynamic"
    gun.simulation.field_definition = field
    with pytest.warns(UserWarning, match="2DElectroDynamic field map is not supported"):
        _line(gun)
    rolled = _cavity_element("StandingWave")
    rolled.physical.length = 2 * WAVELENGTH
    rolled.simulation.field_definition = _rf_map(z, np.cos(2 * np.pi * z / WAVELENGTH))
    rolled.physical.error.rotation.theta = 1e-3  # dx_rot
    with pytest.warns(UserWarning, match="dx_rot"):
        _line(rolled, Brho=P0C / c, z_reference=0.0)
    slow = _cavity_element("StandingWave")
    slow.physical.length = 2 * WAVELENGTH
    slow.simulation.field_definition = _rf_map(z, np.cos(2 * np.pi * z / WAVELENGTH))
    with pytest.warns(UserWarning, match="speed goes from"):  # 1 MeV/c through 10 MV/m
        _line(slow, Brho=1e6 / c, z_reference=0.0)


def test_line_writes_the_fields_and_runs_until_the_reference_arrives():
    z = np.linspace(0, 2 * WAVELENGTH, 2001)
    rf = _cavity_element("StandingWave")
    rf.physical.length = 2 * WAVELENGTH
    rf.simulation.field_definition = _rf_map(z, np.cos(2 * np.pi * z / WAVELENGTH))
    params = _line(rf, Brho=P0C / c, z_reference=0.0)
    assert params["particles.E_ext_particle_init_style"] == "parse_E_ext_particle_function"
    assert params["lattice.elements"] == ["C"]  # spacing only: no warning, no lattice field
    assert params["stop_time"] == pytest.approx(2 * WAVELENGTH / c, rel=1e-6, abs=0)
    with pytest.raises(ValueError, match="z_reference"):
        _line(rf)
    assert "stop_time" not in _line(rf, auto_phase=False)
