"""Focused regression tests for native Bmad lattice export."""

from itertools import permutations

import numpy as np
import pytest

pytest.importorskip("easygdf")
pytest.importorskip("h5py")

from laura.models.baseModels import (  # noqa: E402
    set_functional_definitions,
    set_resolve_functional,
)
from laura.models.element import (  # noqa: E402
    ELEMENT_REGISTRY,
    Aperture,
    BeamBeam,
    CombinedSolenoidQuadrupole,
    Dipole,
    ElectrostaticSeparator,
    MatrixTransform,
    Quadrupole,
    RFCavity,
    RFDeflectingCavity,
    Solenoid,
    TwissMatch,
    Wiggler,
)
from laura.models.elementList import (  # noqa: E402
    MachineLayout,
    MachineModel,
    SectionLattice,
)
from laura.models.physical import PhysicalElement, Position  # noqa: E402
from laura.translator.converters import (  # noqa: E402
    elements_Bmad,
    type_conversion_rules_Bmad,
)
from laura.translator.converters.codes import bmad_unsupported  # noqa: E402
from laura.translator.converters.converter import translate_elements  # noqa: E402
from laura.translator.converters.layout import MachineLayoutTranslator  # noqa: E402
from laura.translator.converters.model import MachineModelTranslator  # noqa: E402
from laura.translator.converters.section import SectionLatticeTranslator  # noqa: E402


@pytest.fixture(autouse=True)
def _reset_functionals():
    set_functional_definitions({}, merge=False)
    set_resolve_functional(False)
    yield
    set_functional_definitions({}, merge=False)
    set_resolve_functional(False)


def _bmad(element):
    return next(iter(translate_elements([element]).values())).to_bmad()


def test_bmad_rule_coverage_matches_the_element_registry():
    assert {
        source: target
        for source, target in type_conversion_rules_Bmad.items()
        if target not in elements_Bmad
    } == {}
    assert set(type_conversion_rules_Bmad) - set(ELEMENT_REGISTRY) == {"Decapole"}
    assert set(ELEMENT_REGISTRY) - set(type_conversion_rules_Bmad) == set(
        bmad_unsupported
    )


def test_bmad_special_element_conversions():
    set_functional_definitions({"kq": 0.3})
    quadrupole = Quadrupole(
        name="Q-1",
        machine_area="S",
        magnetic={"magnetic_length": 0.5, "k1l": "kq"},
    )
    assert "Q_1: quadrupole, l = 0.5" in _bmad(quadrupole)
    assert "k1 = kq / 0.5" in _bmad(quadrupole)

    dipole = Dipole(
        name="B1",
        machine_area="S",
        magnetic={
            "magnetic_length": 1.0,
            "k0l": 0.2,
            "gap": 0.04,
            "edge_field_integral": 0.3,
        },
    )
    bend = _bmad(dipole)
    assert "angle = 0.2" in bend
    assert "hgap = 0.02" in bend
    assert "fint = 0.3" in bend

    solenoid = Solenoid(
        name="S1",
        machine_area="S",
        magnetic={"magnetic_length": 2.0, "fields": {"S0L": 0.8}},
    )
    sol_quad = CombinedSolenoidQuadrupole(
        name="SQ",
        machine_area="S",
        magnetic={
            "magnetic_length": 2.0,
            "k1l": 0.6,
            "solenoid_fields": {"S0L": 0.8},
        },
    )
    assert "bs_field = 0.4" in _bmad(solenoid)
    assert "SQ: sol_quad, l = 2.0, k1 = 0.3, bs_field = 0.4" in _bmad(sol_quad)

    cavity = RFCavity(
        name="C1",
        machine_area="S",
        cavity={
            "phase": 90,
            "frequency": 1e9,
            "n_cells": 1,
            "cell_length": 1,
            "structure_Type": "StandingWave",
        },
        simulation={"field_amplitude": 2e6},
    )
    crab = RFDeflectingCavity(
        name="CR1",
        machine_area="S",
        cavity={
            "phase": 180,
            "frequency": 1e9,
            "n_cells": 1,
            "cell_length": 1,
            "structure_Type": "StandingWave",
        },
        simulation={"field_amplitude": 1e6},
    )
    rf = _bmad(cavity)
    assert "C1: rfcavity" in rf
    assert "n_cell = 1" in rf
    assert "phi0 = 0.25" in rf
    assert "cavity_type = standing_wave" in rf
    assert "CR1: crab_cavity" in _bmad(crab)
    assert "phi0 = 0.5" in _bmad(crab)

    aperture = Aperture(
        name="A1",
        machine_area="S",
        physical={"length": 0.2},
        aperture={"shape": "circular", "radius": 0.01},
    )
    assert (
        _bmad(aperture) == "A1: ecollimator, l = 0.2, x1_limit = 0.01, "
        "x2_limit = 0.01, y1_limit = 0.01, y2_limit = 0.01\n"
    )

    separator = ElectrostaticSeparator(
        name="ES",
        machine_area="S",
        simulation={"horizontal_field": 3, "vertical_field": 4},
    )
    assert "e_field = 5.0" in _bmad(separator)
    assert "tilt = 0.6435011087932844" in _bmad(separator)

    beambeam = BeamBeam(
        name="BB",
        machine_area="S",
        simulation={"charge": 1, "n_particles": 1e10, "horizontal_sigma": 1e-3},
    )
    beambeam_text = _bmad(beambeam)
    assert "BB: beambeam, charge = 1.0, n_particle = 10000000000.0" in beambeam_text
    assert ", l =" not in beambeam_text

    wiggler = Wiggler(
        name="W1",
        machine_area="S",
        magnetic={
            "magnetic_length": 2,
            "peak_magnetic_field": 1.2,
            "period": 0.2,
            "num_periods": 10,
        },
    )
    assert "b_max = 1.2" in _bmad(wiggler)


def test_bmad_taylor_and_match_syntax():
    t_matrix = np.zeros((6, 6, 6))
    t_matrix[0, 1, 1] = 2
    u_matrix = np.zeros((6, 6, 6, 6))
    for order in set(permutations((0, 1, 2))):
        u_matrix[(0, *order)] = 1
    spin = {
        "index": 1,
        "coef": 0.25,
        **{f"exp{i}": float(i == 1) for i in range(1, 7)},
    }
    transform = MatrixTransform(
        name="MAP",
        machine_area="S",
        simulation={
            "c_matrix": {"c1": 3},
            "t_matrix": t_matrix,
            "u_matrix": u_matrix,
            "spin_taylor": [spin],
        },
    )
    text = _bmad(transform)
    assert "{1: 3.0 |}" in text
    assert "{1: 2.0 |22}" in text
    assert "{1: 6.0 |123}" in text
    assert "{Sx: 0.25 |1}" in text

    match = TwissMatch(
        name="TW",
        machine_area="S",
        simulation={"beta_x": 2, "beta_y": 3, "alpha_x": -0.5},
    )
    text = _bmad(match)
    assert "TW: match, l = 0.0, beta_a1 = 2.0, beta_b1 = 3.0" in text
    assert "alpha_a1 = -0.5" in text
    assert "matrix = match_twiss" in text


def test_bmad_section_layout_and_model_export():
    quadrupole = Quadrupole(
        name="Q-1",
        machine_area="S",
        magnetic={"magnetic_length": 0.5, "k1l": 0.3},
        physical=PhysicalElement(length=0.5, middle=Position(z=1)),
    )
    cavity = RFCavity(
        name="C1",
        machine_area="S",
        cavity={
            "phase": 90,
            "frequency": 1e9,
            "n_cells": 1,
            "cell_length": 1,
            "structure_Type": "StandingWave",
        },
        simulation={"field_amplitude": 2e6},
        physical=PhysicalElement(length=1, middle=Position(z=2)),
    )
    section = SectionLattice(
        name="S-1",
        order=["Q-1", "C1"],
        elements=[quadrupole, cavity],
        geometry="open",
        reference_energy=10e6,
    )
    text = SectionLatticeTranslator.from_section(section).to_bmad(particle="electron")
    assert "parameter[particle] = electron" in text
    assert "parameter[geometry] = open" in text
    assert "beginning[e_tot] = 10000000.0" in text
    assert "S_1_drift_1: drift, l = 0.25" in text
    assert "S_1: line = (Q_1, S_1_drift_1, C1)" in text
    assert text.endswith("use, S_1\n")

    layout = MachineLayout(
        name="L-1",
        sections={"S-1": section},
        particle="positron",
    )
    layout_text = MachineLayoutTranslator.from_layout(layout).to_bmad(
        particle="electron"
    )
    assert "parameter[particle] = positron" in layout_text["S_1"]

    machine = MachineModel(
        elements={"Q-1": quadrupole, "C1": cavity},
        section={"sections": {"S-1": ["Q-1", "C1"]}},
        layout={"default_layout": "L-1", "layouts": {"L-1": ["S-1"]}},
        particle="electron",
    )
    model_text = MachineModelTranslator.from_machine(machine).to_bmad()
    assert "parameter[particle] = electron" in model_text["L_1"]["S_1"]
