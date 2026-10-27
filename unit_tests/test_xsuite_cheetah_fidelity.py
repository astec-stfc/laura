"""Tests for Xsuite cavity focusing and Cheetah's tracking order."""

import warnings

import numpy as np
import pytest

xt = pytest.importorskip("xtrack")

from laura.models.element import Dipole, Quadrupole, RFCavity  # noqa: E402
from laura.models.element_list import SectionLattice  # noqa: E402
from laura.translator.converters.section import SectionLatticeTranslator  # noqa: E402

ME = 0.51099895e6


def _section(elements):
    return SectionLatticeTranslator.from_section(
        SectionLattice(name="S", order=[e.name for e in elements], elements=elements)
    )


def _cavity(structure_type="TravellingWave"):
    return RFCavity(
        name="C",
        machine_area="S",
        physical={"length": 3.0, "middle": [0, 0, 1.6]},
        cavity={"structure_type": structure_type, "frequency": 2.856e9, "phase": 20.0,
                "n_cells": 84, "cell_length": 3.0 / 84, "mode_numerator": 2, "mode_denominator": 3},
        simulation={"field_amplitude": 66.7e6},
    )


def _xsuite_matrices(section, E0):
    ref = xt.Particles(p0c=[np.sqrt(E0**2 - ME**2)], mass0=ME)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        line = section.to_xsuite(beam_length=1, particle_ref=ref, save=False)
    assert line.element_names == ["C_entrance", "C_p0c", "C", "C_exit"]
    line.build_tracker()
    line.freeze_longitudinal(False)
    line.freeze_energy(state=False, force=True)
    d = 1e-6
    p = line.build_particles(x=[0, d, 0, 0, 0], px=[0, 0, d, 0, 0],
                             y=[0, 0, 0, d, 0], py=[0, 0, 0, 0, d], zeta=0, delta=0)
    line.track(p)
    xp, yp = p.px / (1 + p.delta), p.py / (1 + p.delta)
    Mx = np.array([[p.x[1], p.x[2]], [xp[1], xp[2]]]) / d
    My = np.array([[p.y[3], p.y[4]], [yp[3], yp[4]]]) / d
    return line, Mx, My


def test_xsuite_cavity_focuses_as_chambers_hard_edges():
    """xt.Cavity has no transverse focusing, and was given a single kick, so its matrix
    was 20-25% off; it now matches the hard-edge (Chambers) matrix in both planes."""
    E0 = 100e6
    line, Mx, My = _xsuite_matrices(_section([_cavity()]), E0)
    gain = line["C_p0c"].Delta_p0c
    g_i, L = E0 / ME, 3.0
    gp = gain / ME / L
    g_f = g_i + gp * L
    entrance = np.array([[1, 0], [-gp / (2 * g_i), 1]])
    body = np.array([[1, g_i / gp * np.log(g_f / g_i)], [0, g_i / g_f]])
    exit_ = np.array([[1, 0], [gp / (2 * g_f), 1]])
    chambers = exit_ @ body @ entrance
    assert Mx == pytest.approx(chambers, rel=1e-3, abs=1e-4)
    assert My == pytest.approx(chambers, rel=1e-3, abs=1e-4)


@pytest.mark.parametrize("structure_type, tw_focusing", [
    ("StandingWave", True), ("TravellingWave", False),
])
def test_xsuite_standing_wave_focuses_as_cheetah(structure_type, tw_focusing):
    """A standing wave also has Rosenzweig-Serafini body focusing, as in Cheetah and
    ELEGANT; so does a travelling wave with tw_focusing off."""
    cheetah = pytest.importorskip("cheetah")
    import torch

    E0 = 100e6
    section = _section([_cavity(structure_type)])
    section.tw_focusing = tw_focusing
    line, Mx, My = _xsuite_matrices(section, E0)
    f64 = {"dtype": torch.float64}
    cavity = cheetah.Cavity(
        length=torch.tensor(3.0, **f64), voltage=torch.tensor(line["C"].voltage, **f64),
        phase=torch.tensor(20.0, **f64), frequency=torch.tensor(2.856e9, **f64),
        cavity_type="standing_wave", **f64,
    )
    R = cavity.first_order_transfer_map(torch.tensor(E0, **f64), cheetah.Species("electron"))
    R = R.squeeze().numpy()[:2, :2]
    assert Mx == pytest.approx(R, rel=1e-3, abs=1e-4)
    assert My == pytest.approx(R, rel=1e-3, abs=1e-4)


def test_xsuite_cavity_without_reference_warns_and_has_no_edges():
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        line = _section([_cavity()]).to_xsuite(beam_length=1, save=False)
    assert line.element_names == ["C"]
    assert any("without edge focusing" in str(w.message) for w in caught)


@pytest.mark.parametrize("method", [None, "second_order"])
def test_cheetah_tracking_method_is_written(method):
    """"auto" writes linear, for choose_cheetah_tracking_method to raise."""
    pytest.importorskip("cheetah")
    elements = [
        Quadrupole(name="Q", machine_area="S", physical={"length": 0.1, "middle": [0, 0, 0.5]},
                   magnetic={"k1l": 0.1}),
        Dipole(name="B", machine_area="S", physical={"length": 0.2, "middle": [0, 0, 1.0]},
               magnetic={"angle": 0.01}),
    ]
    section = _section(elements)
    if method:
        section.cheetah_tracking_method = method
    segment = section.to_cheetah()
    expected = method or "linear"
    methods = {type(e).__name__: e.tracking_method for e in segment.flattened().elements}
    assert methods == {"Drift": expected, "Quadrupole": expected, "Dipole": expected}


@pytest.mark.parametrize("sigma_p, expected", [(1e-4, "linear"), (2e-2, "second_order")])
def test_cheetah_auto_raises_to_second_order_when_the_beam_needs_it(sigma_p, expected):
    """Cheetah's linear tracking was ~12% off in beta through the LCLS linac, but is
    much faster, and the only order a ParameterBeam can take."""
    cheetah = pytest.importorskip("cheetah")
    import torch

    from laura.translator.converters.codes.cheetah import choose_cheetah_tracking_method

    quads = [
        Quadrupole(name=f"Q{i}", machine_area="S", physical={"length": 0.2, "middle": [0, 0, i + 0.5]},
                   magnetic={"k1l": 0.4 * (-1) ** i})
        for i in range(40)
    ]
    segment = _section(quads).to_cheetah()
    beam = cheetah.ParticleBeam.from_twiss(
        num_particles=2000, energy=torch.tensor(1e9), beta_x=torch.tensor(3.0),
        beta_y=torch.tensor(3.0), sigma_p=torch.tensor(sigma_p),
        emittance_x=torch.tensor(1e-9), emittance_y=torch.tensor(1e-9),
    ).to(torch.float64)
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        assert choose_cheetah_tracking_method(segment, beam) == expected
    raised = [w for w in caught if "set cheetah_tracking_method" in str(w.message)]
    assert len(raised) == (expected == "second_order")
    assert {e.tracking_method for e in segment.flattened().elements} == {expected}
    parameter_beam = cheetah.ParameterBeam.from_parameters(energy=torch.tensor(1e9)).to(torch.float64)
    assert choose_cheetah_tracking_method(segment, parameter_beam) == "linear"
