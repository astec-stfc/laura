"""Bmad short-range wakes: pseudo-modes sampled onto a grid, and back out again."""

import numpy as np
import pytest

from laura.translator.utils.bmad import (
    bmad_sr_wake_function,
    sample_bmad_sr_wake,
)


def _base(**overrides):
    base = {
        "sr%z_max": 0.01,
        "sr%z_scale": 1.0,
        "sr%amp_scale": 1.0,
        "sr%scale_with_length": False,
    }
    base.update(overrides)
    return base


def test_mode_sum_matches_the_formula_bmad_tracks_with():
    """phi is in turns, not radians: wake_mod.f90 evaluates twopi * mode%phi,
    the same convention as phi0 on a cavity. Reading it as radians makes a
    quarter-turn mode -- the common case, a pure cosine -- come out 24% low.
    """
    modes = [[2.0, 100.0, 3000.0, 0.25], [1.0, 0.0, 0.0, 0.5]]
    s = np.array([0.0, 1e-4, 5e-4])

    wake = bmad_sr_wake_function(modes, s)

    expected = 2.0 * np.exp(-100.0 * s) * np.sin(0.5 * np.pi - 3000.0 * s)
    expected += 1.0 * np.sin(np.pi)
    assert wake == pytest.approx(expected)


def test_z_scale_stretches_every_length_in_the_sum():
    """A fit done in scaled units -- the LCLS 1.3 GHz file writes
    z_scale = 1/0.0017 -- is reused at a physical scale by z_scale alone.
    """
    modes = [[1.0, 100.0, 3000.0, 0.25]]

    scaled = bmad_sr_wake_function(modes, 1e-3, z_scale=2.0)

    assert scaled == pytest.approx(bmad_sr_wake_function(modes, 2e-3))


def test_the_grid_ends_on_an_exact_zero():
    """Bmad's tabulated wake parser refuses a table with no z = 0 point, and
    negating a reversed linspace leaves -0.0 there, which is not it.
    """
    sampled = sample_bmad_sr_wake(_base(), [[1.0, 100.0, 0.0, 0.25, "none"]], samples=5)

    assert sampled["z"][-1] == 0.0
    assert np.signbit(sampled["z"][-1]) is np.False_
    assert np.all(np.diff(sampled["z"]) > 0)


def test_z_is_negative_because_that_is_how_bmad_indexes_a_table():
    """The mode sum takes the separation behind the source; the table takes the
    trailing particle's position minus the source's, which is the negative of
    it. Sampling one and labelling it the other reverses the wake.
    """
    modes = [[1.0, 100.0, 3000.0, 0.25, "none"]]

    sampled = sample_bmad_sr_wake(_base(), modes, samples=41)

    assert sampled["z"][0] < 0.0
    expected = bmad_sr_wake_function(modes, -sampled["z"])
    assert sampled["Wz"] == pytest.approx(expected)


def test_scale_with_length_folds_the_length_into_the_samples():
    """Bmad's per-metre wakes are scaled by the element length at tracking
    time. A sampled wake has nowhere to keep that instruction -- and every
    other code's wake files are absolute -- so the length goes into the
    samples, and the Bmad writer says scale_with_length = F to match.
    """
    modes = [[1.0, 0.0, 0.0, 0.25, "none"]]

    absolute = sample_bmad_sr_wake(_base(), modes, length=3.0, samples=3)
    per_metre = sample_bmad_sr_wake(
        _base(**{"sr%scale_with_length": True}), modes, length=3.0, samples=3
    )

    assert absolute["Wz"][-1] == pytest.approx(1.0)
    assert per_metre["Wz"][-1] == pytest.approx(3.0)


def test_amp_scale_multiplies_the_modes():
    """The lattice overrides it per element -- RWWAKE3H[sr_wake%amp_scale] = 182
    -- so it cannot be read off the wake file.
    """
    modes = [[1.0, 0.0, 0.0, 0.25, "none"]]

    sampled = sample_bmad_sr_wake(_base(**{"sr%amp_scale": 182.0}), modes, samples=3)

    assert sampled["Wz"][-1] == pytest.approx(182.0)


def test_an_amp_scale_of_zero_switches_the_wake_off():
    """Bmad's own tracking returns immediately on amp_scale == 0, so the wake
    is off rather than merely small, and importing zeros would be a lie about
    what the lattice does.
    """
    modes = [[1.0, 0.0, 0.0, 0.25, "none"]]

    assert sample_bmad_sr_wake(_base(**{"sr%amp_scale": 0.0}), modes) is None


def test_the_span_comes_from_the_modes_not_from_z_max():
    """z_max is a cap, not a scale: the LCLS resistive-wall files write a round
    100 m and decay within a fifth of a millimetre. Sampling across that z_max
    puts the entire wake inside the first grid cell.
    """
    modes = [[1.0, 5140.0, 0.0, 0.25, "none"]]

    sampled = sample_bmad_sr_wake(_base(**{"sr%z_max": 100.0}), modes, samples=101)

    assert -sampled["z"][0] == pytest.approx(12.0 / 5140.0)


def test_an_undamped_mode_keeps_the_full_z_max():
    """Nothing decays, so there is no shorter span to choose and z_max is the
    only statement of where the wake stops.
    """
    modes = [[1.0, 0.0, 3000.0, 0.25, "none"]]

    sampled = sample_bmad_sr_wake(_base(**{"sr%z_max": 0.05}), modes, samples=201)

    assert -sampled["z"][0] == pytest.approx(0.05)


def test_a_grid_too_coarse_for_the_modes_says_so():
    modes = [[1.0, 1.0e6, 0.0, 0.25, "none"]]

    with pytest.warns(UserWarning, match="points are needed to resolve it"):
        sample_bmad_sr_wake(_base(), modes, samples=3)


def test_position_dependent_longitudinal_modes_are_dropped_with_a_warning():
    """x_leading and friends scale the kick by a particle's transverse
    coordinate. A sampled W(s) carries no such dependence, so keeping them
    would silently apply a transverse-dependent kick to everything.
    """
    modes = [
        [1.0, 100.0, 0.0, 0.25, "none"],
        [5.0, 100.0, 0.0, 0.25, "x_leading"],
    ]

    with pytest.warns(UserWarning, match="x_leading"):
        sampled = sample_bmad_sr_wake(_base(), modes, samples=3)

    assert sampled["Wz"][-1] == pytest.approx(1.0)


def test_transverse_modes_are_split_by_polarization():
    """Bmad names the polarization None, X_Axis or Y_Axis; an unpolarised mode
    acts in both planes.
    """
    modes = [
        [1.0, 0.0, 0.0, 0.25, "X_Axis", "leading"],
        [2.0, 0.0, 0.0, 0.25, "None", "leading"],
    ]

    sampled = sample_bmad_sr_wake(_base(), (), modes, samples=3)

    assert sampled["Wx"][-1] == pytest.approx(3.0)
    assert sampled["Wy"][-1] == pytest.approx(2.0)


def test_transverse_modes_that_are_not_dipole_are_dropped():
    """``trailing`` is the quadrupole-like wake and ``none`` a constant
    deflection; neither is what a sampled Wx/Wy is read as.
    """
    modes = [[1.0, 0.0, 0.0, 0.25, "X_Axis", "trailing"]]

    with pytest.warns(UserWarning, match="trailing"):
        assert sample_bmad_sr_wake(_base(), (), modes, samples=3) is None
