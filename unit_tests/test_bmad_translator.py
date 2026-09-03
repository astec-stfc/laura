"""Focused regression tests for native Bmad lattice export."""

import warnings
from itertools import permutations

import numpy as np
import pytest

pytest.importorskip("easygdf")
h5py = pytest.importorskip("h5py")

from laura.models.baseModels import (  # noqa: E402
    set_functional_definitions,
    set_resolve_functional,
)
from laura.models.element import (  # noqa: E402
    ELEMENT_REGISTRY,
    Aperture,
    BeamBeam,
    Combined_Corrector,
    CombinedSolenoidQuadrupole,
    Dipole,
    ElectrostaticSeparator,
    MatrixTransform,
    Marker,
    Quadrupole,
    RFCavity,
    RFDeflectingCavity,
    Screen,
    Solenoid,
    TwissMatch,
    Wakefield,
    Wiggler,
)
from laura.models.elementList import (  # noqa: E402
    ElementList,
    MachineLayout,
    MachineModel,
    SectionLattice,
)
from laura.models.physical import PhysicalElement, Position  # noqa: E402
from laura.models.simulation import TwissMatchSimulationElement  # noqa: E402
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


def _bmad(element, directory="."):
    return next(
        iter(translate_elements([element], directory=str(directory)).values())
    ).to_bmad()


def _write_field(path, field_type, **datasets):
    units = {
        "z": "m",
        "t": "s",
        "Bz": "T",
        "Wx": "V/C/m",
        "Wy": "V/C/m",
        "Wz": "V/C",
    }
    with h5py.File(path, "w") as output:
        output.attrs["type"] = field_type
        for name, values in datasets.items():
            dataset = output.create_dataset(name, data=values)
            dataset.attrs["units"] = units[name]


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


def test_bmad_short_range_wake_sidecars(tmp_path):
    wake_path = tmp_path / "wake.hdf5"
    _write_field(
        wake_path,
        "3DWake",
        z=[0, 0.01, 0.02],
        Wx=[0, 1, 2],
        Wy=[0, 1, 2],
        Wz=[10, 5, 0],
    )
    wake = Wakefield(
        name="W",
        machine_area="S",
        physical={"length": 0.2},
        simulation={"wakefield_definition": str(wake_path)},
    )
    text = _bmad(wake, tmp_path)
    assert text == "W: drift, l = 0.2, sr_wake = call::wake.bmad\n"
    sidecar = (tmp_path / "wake.bmad").read_text()
    assert "scale_with_length = F" in sidecar
    assert "time_based = F" in sidecar
    assert "0.01 5" in sidecar
    assert "0.02 0,\n" in sidecar

    cavity = RFCavity(
        name="C",
        machine_area="S",
        cavity={
            "phase": 0,
            "frequency": 1e9,
            "n_cells": 1,
            "cell_length": 0.2,
            "structure_Type": "StandingWave",
        },
        simulation={
            "field_amplitude": 1e6,
            "wakefield_definition": str(wake_path),
        },
    )
    assert "sr_wake = call::wake.bmad" in _bmad(cavity, tmp_path)


def test_bmad_transverse_only_wake_is_reported_and_omitted(tmp_path):
    wake_path = tmp_path / "transverse.hdf5"
    _write_field(
        wake_path,
        "TransverseWake",
        z=[0, 0.01, 0.02],
        Wx=[0, 1, 2],
        Wy=[0, 1, 2],
    )
    wake = Wakefield(
        name="W",
        machine_area="S",
        simulation={"wakefield_definition": str(wake_path)},
    )
    with pytest.warns(UserWarning, match="pseudo-modes"):
        text = _bmad(wake, tmp_path)
    assert "sr_wake" not in text


def test_bmad_quadrupole_generalized_gradient_sidecar(tmp_path):
    field_path = tmp_path / "quadrupole.hdf5"
    _write_field(
        field_path,
        "1DMagnetoStatic",
        z=[-0.1, 0, 0.1],
        Bz=[0, 1, 0],
    )
    quadrupole = Quadrupole(
        name="Q",
        machine_area="S",
        magnetic={"magnetic_length": 0.2, "gradient": 4, "k1l": 0.3},
        simulation={"field_definition": str(field_path)},
    )
    text = _bmad(quadrupole, tmp_path)
    assert "field_calc = fieldmap" in text
    assert "gen_gradients = call::quadrupole.bmad" in text
    assert "k1 =" not in text
    sidecar = (tmp_path / "quadrupole.bmad").read_text()
    assert "field_scale = 4" in sidecar
    assert "ele_anchor_pt = center" in sidecar
    assert "curve = { kind = b, n = 2" in sidecar
    assert "0: 1" in sidecar


def test_bmad_solenoid_generalized_gradient_uses_zero_harmonic(tmp_path):
    field_path = tmp_path / "solenoid.hdf5"
    _write_field(
        field_path,
        "1DMagnetoStatic",
        z=[-0.1, 0, 0.1],
        Bz=[0, 1, 0],
    )
    solenoid = Solenoid(
        name="S",
        machine_area="S",
        magnetic={"magnetic_length": 0.2, "fields": {"S0L": 0.8}},
        simulation={"field_definition": str(field_path)},
    )
    text = _bmad(solenoid, tmp_path)
    assert "field_calc = fieldmap" in text
    assert "gen_gradients = call::solenoid.bmad" in text
    assert "bs_field =" not in text
    sidecar = (tmp_path / "solenoid.bmad").read_text()
    assert "field_scale = 4" in sidecar
    assert "curve = { kind = bs, n = 0" in sidecar


def test_bmad_special_element_conversions():
    set_functional_definitions({"kq": 0.3})
    marker = Marker(name="M1", machine_area="S")
    assert _bmad(marker) == "M1: marker\n"

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
            "tilt": 0.1,
        },
    )
    bend = _bmad(dipole)
    assert "angle = 0.2" in bend
    assert "hgap = 0.02" in bend
    assert "fint = 0.3" in bend
    assert "ref_tilt = 0.1" in bend
    assert ", gap =" not in bend
    assert ", tilt =" not in bend

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
    assert "C1: lcavity" in rf
    assert "n_cell = 1" in rf
    assert "phi0 = -0.25" in rf
    assert "cavity_type = standing_wave" in rf
    assert "CR1: crab_cavity" in _bmad(crab)
    assert "phi0 = -0.5" in _bmad(crab)

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

    rect = Aperture(
        name="A2",
        machine_area="S",
        physical={"length": 0.0},
        aperture={
            "shape": "rectangular",
            "horizontal_size": 0.017,
            "vertical_size": 0.0085,
        },
    )
    # ``horizontal_size``/``vertical_size`` are full apertures and Bmad's
    # limits are half widths, so these are halved on the way out; ``radius``
    # above is already a half width and is not. Writing the full width into
    # the limit doubled the collimator on every round trip.
    assert (
        _bmad(rect) == "A2: rcollimator, l = 0.0, x1_limit = 0.0085, "
        "x2_limit = 0.0085, y1_limit = 0.00425, y2_limit = 0.00425\n"
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


def test_bmad_optional_tracking_controls_and_aliases():
    quadrupole = Quadrupole(
        name="Q_TRACK",
        machine_area="S",
        magnetic={"magnetic_length": 1, "k1l": 0},
        simulation={
            "tracking_method": "runge_kutta",
            "mat6_calc_method": "tracking",
            "spin_tracking_method": "symp_lie_ptc",
            "integrator_order": 6,
            "num_steps": 12,
            "ds_step": 0.02,
            "csr_method": "1_dim",
            "space_charge_method": "slice",
            "csr_ds_step": 0.003,
        },
    )
    simulation = quadrupole.simulation
    assert (
        simulation.integration_order,
        simulation.deltaL,
        simulation.csrdz,
    ) == (6, 0.02, 0.003)
    assert {
        "integrator_order",
        "ds_step",
        "csr_ds_step",
    }.isdisjoint(type(simulation).model_fields)

    text = _bmad(quadrupole)
    expected = {
        "tracking_method": "runge_kutta",
        "mat6_calc_method": "tracking",
        "spin_tracking_method": "symp_lie_ptc",
        "integrator_order": "6",
        "num_steps": "12",
        "ds_step": "0.02",
        "csr_method": "1_dim",
        "space_charge_method": "slice",
        "csr_ds_step": "0.003",
    }
    for key, value in expected.items():
        assert f"{key} = {value}" in text
        assert text.count(f", {key} =") == 1

    offset = BeamBeam(
        name="BB_OFFSET",
        machine_area="S",
        simulation={"horizontal_offset": 0.001},
    )
    offset_text = _bmad(offset)
    assert "x_offset = 0.001" in offset_text
    assert "y_offset =" not in offset_text


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
            "tracking_method": "linear",
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
    assert "tracking_method = linear" in text

    match = TwissMatch(
        name="TW",
        machine_area="S",
        simulation={"beta_x": 2, "beta_y": 3, "alpha_x": -0.5},
    )
    text = _bmad(match)
    assert "TW: match, l = 0.0, beta_a1 = 2.0, beta_b1 = 3.0" in text
    assert "alpha_a1 = -0.5" in text
    assert "matrix = match_twiss" in text


def test_bmad_leading_twiss_match_becomes_beginning_not_a_match_element():
    """A TwissMatch at the head of a section stands in for Bmad's beginning_ele
    (or an active fixer), which does not touch the beam. Exporting it as a
    `match` element would put a real transfer matrix at the start of the line.
    """
    seed = TwissMatch(
        name="BEGINNING",
        machine_area="S",
        simulation={
            "beta_x": 2,
            "alpha_x": -0.5,
            "beta_y": 3,
            "alpha_y": 0.25,
            "eta_x": 0.4,
            "eta_xp": -0.05,
        },
        physical=PhysicalElement(length=0, middle=Position(z=0)),
    )
    quadrupole = Quadrupole(
        name="Q-1",
        machine_area="S",
        magnetic={"magnetic_length": 0.5, "k1l": 0.3},
        physical=PhysicalElement(length=0.5, middle=Position(z=0.25)),
    )
    section = SectionLattice(
        name="S-1",
        order=["BEGINNING", "Q-1"],
        elements=[seed, quadrupole],
        geometry="open",
    )
    text = SectionLatticeTranslator.from_section(section).to_bmad()

    assert "beginning[beta_a] = 2.0" in text
    assert "beginning[alpha_a] = -0.5" in text
    assert "beginning[beta_b] = 3.0" in text
    assert "beginning[alpha_b] = 0.25" in text
    assert "beginning[eta_x] = 0.4" in text
    assert "beginning[etap_x] = -0.05" in text
    # Zero dispersion is Bmad's default and is left out.
    assert "beginning[eta_y]" not in text
    assert "matrix = match_twiss" not in text
    assert "BEGINNING:" not in text
    assert "S_1: line = (Q_1)" in text

    # An explicit initial_twiss overrides the seed rather than doubling up.
    override = SectionLatticeTranslator.from_section(section).to_bmad(
        initial_twiss=TwissMatchSimulationElement(
            beta_x=7, alpha_x=0.0, beta_y=8, alpha_y=0.0
        )
    )
    assert "beginning[beta_a] = 7.0" in override
    assert "beginning[beta_a] = 2.0" not in override
    assert "matrix = match_twiss" not in override

    # A TwissMatch anywhere else really is a matching element.
    interior = SectionLattice(
        name="S-2",
        order=["Q-1", "BEGINNING"],
        elements=[
            quadrupole,
            seed.model_copy(
                update={
                    "physical": PhysicalElement(length=0, middle=Position(z=1.0))
                }
            ),
        ],
        geometry="open",
    )
    interior_text = SectionLatticeTranslator.from_section(interior).to_bmad()
    assert "matrix = match_twiss" in interior_text
    assert "beginning[beta_a]" not in interior_text


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
    translator = SectionLatticeTranslator.from_section(section)
    translator.lsc_enable = False
    text = translator.to_bmad(
        particle="electron",
        space_charge_n_bin=64,
        initial_twiss=TwissMatchSimulationElement(
            beta_x=2,
            alpha_x=0.1,
            beta_y=3,
            alpha_y=-0.2,
        ),
    )
    assert "parameter[particle] = electron" in text
    assert "bmad_com[csr_and_space_charge_on] = T" in text
    assert "space_charge_com[n_bin] = 64" in text
    assert "parameter[geometry] = open" in text
    assert "beginning[e_tot] = 10000000.0" in text
    assert "beginning[beta_a] = 2.0" in text
    assert "beginning[alpha_a] = 0.1" in text
    assert "beginning[beta_b] = 3.0" in text
    assert "beginning[alpha_b] = -0.2" in text
    assert "S_1_drift_1: drift, l = 0.25" in text
    assert "S_1: line = (Q_1, S_1_drift_1, C1)" in text
    assert text.endswith("use, S_1\n")

    translator.csr_enable = False
    assert "bmad_com[csr_and_space_charge_on] = F" in translator.to_bmad()

    with pytest.raises(ValueError, match="space_charge_n_bin must be positive"):
        translator.to_bmad(space_charge_n_bin=0)

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
    model_text = MachineModelTranslator.from_machine(machine).to_bmad(
        space_charge_n_bin=32,
    )
    assert "parameter[particle] = electron" in model_text["L_1"]["S_1"]
    assert "bmad_com[csr_and_space_charge_on] = T" in model_text["L_1"]["S_1"]
    assert "space_charge_com[n_bin] = 32" in model_text["L_1"]["S_1"]


def test_bmad_section_superimposes_overlapping_elements():
    base = Quadrupole(
        name="Q-BASE",
        machine_area="S",
        magnetic={"magnetic_length": 4, "k1l": 0.4},
        physical=PhysicalElement(length=4, middle=Position(z=2)),
    )
    overlap = Quadrupole(
        name="Q-OVER",
        machine_area="S",
        magnetic={"magnetic_length": 2, "k1l": 0.2},
        physical=PhysicalElement(length=2, middle=Position(z=3)),
    )
    embedded = Solenoid(
        name="S-EMBED",
        machine_area="S",
        subelement="Q-BASE",
        magnetic={"magnetic_length": 4, "fields": {"S0L": 0.8}},
        physical=PhysicalElement(length=4, middle=Position(z=2)),
    )
    downstream = Quadrupole(
        name="Q-NEXT",
        machine_area="S",
        magnetic={"magnetic_length": 2, "k1l": 0.2},
        physical=PhysicalElement(length=2, middle=Position(z=7)),
    )
    section = SectionLattice(
        name="OVERLAP",
        order=["Q-BASE", "Q-OVER", "Q-NEXT"],
        elements=ElementList(
            elements={
                element.name: element
                for element in (base, overlap, embedded, downstream)
            }
        ),
    )

    text = SectionLatticeTranslator.from_section(section).to_bmad()

    assert "parameter[geometry] = open" in text
    assert "Q_OVER: quadrupole" in text
    assert "S_EMBED: solenoid" in text
    assert "OVERLAP: line = (Q_BASE, OVERLAP_drift_1, Q_NEXT)" in text
    assert (
        "superimpose, element = Q_OVER, offset = 2, "
        "ele_origin = beginning"
    ) in text
    assert (
        "superimpose, element = S_EMBED, offset = 0, "
        "ele_origin = beginning"
    ) in text


def test_bmad_section_uses_thin_kicker_inside_bend():
    bend = Dipole(
        name="B",
        machine_area="S",
        magnetic={"magnetic_length": 1, "k0l": 0.1},
        physical=PhysicalElement(length=1, middle=Position(z=0.5)),
    )
    corrector = Combined_Corrector(
        name="K",
        machine_area="S",
        magnetic={
            "magnetic_length": 0.2,
            "horizontal_kick": 0.01,
            "vertical_kick": -0.02,
        },
        physical=PhysicalElement(length=0.2, middle=Position(z=0.5)),
    )
    section = SectionLattice(
        name="BEND_KICKER",
        order=["B", "K"],
        elements=ElementList(elements={"B": bend, "K": corrector}),
    )

    text = SectionLatticeTranslator.from_section(section).to_bmad()

    assert "K: kicker, l = 0.0, hkick = 0.01, vkick = -0.02" in text
    assert (
        "superimpose, element = K, offset = 0.5, ele_origin = beginning"
    ) in text


def _cavity_ring(geometry):
    """A one-cavity, one-quadrupole section in the given geometry."""
    cavity = RFCavity(
        name="RF",
        machine_area="S",
        cavity={
            "phase": 0,
            "frequency": 2.5e8,
            "n_cells": 1,
            "cell_length": 1.2,
            "structure_Type": "StandingWave",
        },
        simulation={"field_amplitude": 1e6},
        physical=PhysicalElement(length=1.2, middle=Position(z=0.6)),
    )
    quadrupole = Quadrupole(
        name="Q",
        machine_area="S",
        magnetic={"magnetic_length": 0.5, "k1l": 0.3},
        physical=PhysicalElement(length=0.5, middle=Position(z=2.0)),
    )
    return SectionLattice(
        name="R",
        order=["RF", "Q"],
        elements=[cavity, quadrupole],
        geometry=geometry,
    )


def test_bmad_closed_geometry_exports_a_cavity_as_rfcavity():
    """Bmad refuses an lcavity in a closed branch outright, so a ring with any
    cavity used to export to a file that would not parse at all. rfcavity takes
    the same attributes, and the swap must still go through the cavity's own
    to_bmad so cavity_type keeps its Bmad spelling.
    """
    closed = SectionLatticeTranslator.from_section(_cavity_ring("closed")).to_bmad()
    assert "RF: rfcavity" in closed
    assert "lcavity" not in closed
    # Bmad's switch is Standing_Wave -- LAURA's own "StandingWave" is rejected.
    assert "cavity_type = standing_wave" in closed

    # An open line still accelerates, so it keeps the lcavity.
    open_line = SectionLatticeTranslator.from_section(_cavity_ring("open")).to_bmad()
    assert "RF: lcavity" in open_line
    assert "rfcavity" not in open_line
    assert "cavity_type = standing_wave" in open_line


def test_bmad_export_writes_the_global_datum_when_the_line_is_placed():
    """Without beginning[..._position] Bmad starts every line at the origin
    along +Z, so a machine that sits anywhere else loses its placement -- and
    the run-up to the first element goes with it.
    """
    quadrupole = Quadrupole(
        name="Q",
        machine_area="S",
        magnetic={"magnetic_length": 0.5, "k1l": 0.3},
        physical=PhysicalElement(
            length=0.5,
            middle=Position(x=3.0, z=10.0),
            global_rotation={"phi": 0.0, "psi": 0.0, "theta": 0.25},
        ),
    )
    section = SectionLattice(
        name="S", order=["Q"], elements=[quadrupole], geometry="open"
    )
    text = SectionLatticeTranslator.from_section(section).to_bmad()

    # The datum is the *entrance* of the first element, not its centre, and the
    # angle is Bmad's floor convention rather than LAURA's.
    assert "beginning[x_position] = 3.06185098" in text
    assert "beginning[z_position] = 9.75777189" in text
    assert "beginning[theta_position] = -0.25" in text
    # y is zero here and Bmad defaults it, so it is left out.
    assert "beginning[y_position]" not in text
    assert "beginning[phi_position]" not in text


def test_bmad_export_omits_the_datum_for_a_line_starting_at_the_origin():
    """A section with no global placement to record -- which includes every
    position_mode="s" import, whose world coordinates are integrated from the
    origin -- must not be given a surveyed-looking datum it never had.
    """
    quadrupole = Quadrupole(
        name="Q",
        machine_area="S",
        magnetic={"magnetic_length": 0.5, "k1l": 0.3},
        physical=PhysicalElement(length=0.5, middle=Position(z=0.25)),
    )
    section = SectionLattice(
        name="S", order=["Q"], elements=[quadrupole], geometry="open"
    )
    text = SectionLatticeTranslator.from_section(section).to_bmad()

    assert "_position" not in text


def _lead_section(with_origin):
    """A section whose first magnet sits 2.5 m downstream of its own start."""
    elements = [
        Quadrupole(
            name="Q",
            machine_area="S",
            magnetic={"magnetic_length": 0.5, "k1l": 0.3},
            physical=PhysicalElement(length=0.5, middle=Position(z=2.75)),
        )
    ]
    order = ["Q"]
    if with_origin:
        elements.insert(
            0,
            TwissMatch(
                name="BEGINNING",
                machine_area="S",
                physical=PhysicalElement(length=0.0, middle=Position(z=0.0)),
                simulation={"beta_x": 2.0, "alpha_x": 0.0, "beta_y": 3.0, "alpha_y": 0.0},
            ),
        )
        order.insert(0, "BEGINNING")
    return SectionLattice(
        name="S", order=order, elements=elements, geometry="open"
    )


def test_bmad_export_restores_the_run_up_to_the_first_element():
    """createDrifts() only fills the gaps *between* elements, so the stretch
    from a section's own start to its first element used to vanish -- the
    exported lattice came out physically shorter than the one it was read from.
    Bmad's Dragt_PSR_small_ring opens with a 2.286 m drift, and losing it
    shortened the whole ring by exactly that.
    """
    text = SectionLatticeTranslator.from_section(_lead_section(True)).to_bmad()

    assert "S_lead_drift: drift, l = 2.5" in text
    assert "S: line = (S_lead_drift, Q)" in text


def test_bmad_export_invents_no_run_up_without_a_declared_start():
    """A leading TwissMatch is what declares where a section begins -- it is
    what a Bmad Beginning_Ele imports as. Without one there is no origin to
    measure a run-up from, and an element that merely sits away from the world
    origin must not be handed a drift it never had.
    """
    text = SectionLatticeTranslator.from_section(_lead_section(False)).to_bmad()

    assert "lead_drift" not in text
    assert "S: line = (Q)" in text


def _reserved_name_section(extra=()):
    """A section whose markers carry names Bmad keeps for itself."""
    elements = [
        Quadrupole(
            name="Q",
            machine_area="S",
            magnetic={"magnetic_length": 0.5, "k1l": 0.3},
            physical=PhysicalElement(length=0.5, middle=Position(z=0.25)),
        ),
        Marker(
            name="BEGINNING",
            machine_area="S",
            physical=PhysicalElement(length=0.0, middle=Position(z=0.5)),
        ),
        Marker(
            name="END",
            machine_area="S",
            physical=PhysicalElement(length=0.0, middle=Position(z=1.0)),
        ),
    ]
    order = ["Q", "BEGINNING", "END"]
    for offset, name in enumerate(extra, start=2):
        elements.append(
            Marker(
                name=name,
                machine_area="S",
                physical=PhysicalElement(length=0.0, middle=Position(z=offset)),
            )
        )
        order.append(name)
    return SectionLattice(name="S", order=order, elements=elements, geometry="open")


def test_bmad_export_renames_the_names_bmad_keeps_for_itself():
    """Bmad refuses a lattice outright if an element is called BEGINNING --
    ``RESERVED WORD`` from the parser -- and silently confuses one called END
    with the end-of-branch element it makes itself. Neither is hypothetical:
    the LCLS cu_hxr lattice ends on a marker named END, and importing it and
    writing it back produced a file Bmad could not round-trip.
    """
    with pytest.warns(UserWarning, match="END -> END_ELEMENT"):
        text = SectionLatticeTranslator.from_section(_reserved_name_section()).to_bmad()

    assert "END_ELEMENT: marker" in text
    assert "BEGINNING_ELEMENT: marker" in text
    assert "END_ELEMENT, " in text or "END_ELEMENT)" in text
    assert "BEGINNING_ELEMENT," in text
    # The definitions and the line have to agree, or the line names an element
    # that was never defined.
    line = next(line for line in text.splitlines() if line.startswith("S: line"))
    assert "END_ELEMENT" in line and "BEGINNING_ELEMENT" in line


def test_bmad_export_leaves_unreserved_names_exactly_as_they_were():
    """The rename must be surgical. ENDGUN, ENDL0 and ENDDMPH all sit in the
    same lattice as END and none of them are reserved.
    """
    section = _reserved_name_section(extra=("ENDGUN", "ENDL0"))
    with pytest.warns(UserWarning, match="reserves"):
        text = SectionLatticeTranslator.from_section(section).to_bmad()

    assert "ENDGUN: marker" in text
    assert "ENDL0: marker" in text
    assert "ENDGUN_ELEMENT" not in text
    assert "ENDL0_ELEMENT" not in text


def test_bmad_export_does_not_collide_a_rename_with_itself():
    """The exporter offers every name twice -- once as a definition, once as a
    line member. Renaming on the second sighting used to walk into the
    replacement the first sighting had just claimed, so cu_hxr's END came out
    as END_ELEMENT_2 with nothing called END_ELEMENT anywhere in the file.
    """
    with pytest.warns(UserWarning, match="reserves"):
        text = SectionLatticeTranslator.from_section(_reserved_name_section()).to_bmad()

    assert "END_ELEMENT_2" not in text
    assert "BEGINNING_ELEMENT_2" not in text


def test_bmad_rename_steps_over_a_name_already_in_the_lattice():
    """Only if the obvious replacement is taken does the counter come out."""
    section = _reserved_name_section(extra=("END_ELEMENT",))
    with pytest.warns(UserWarning, match="END -> END_ELEMENT_2"):
        text = SectionLatticeTranslator.from_section(section).to_bmad()

    # The pre-existing element keeps its name; the reserved one steps past it.
    assert text.count("END_ELEMENT: marker") == 1
    assert "END_ELEMENT_2: marker" in text


def test_bmad_export_of_an_unreserved_lattice_warns_about_nothing():
    section = SectionLattice(
        name="S",
        order=["Q"],
        elements=[
            Quadrupole(
                name="Q",
                machine_area="S",
                magnetic={"magnetic_length": 0.5, "k1l": 0.3},
                physical=PhysicalElement(length=0.5, middle=Position(z=0.25)),
            )
        ],
        geometry="open",
    )
    with warnings.catch_warnings():
        warnings.simplefilter("error", UserWarning)
        text = SectionLatticeTranslator.from_section(section).to_bmad()

    assert "_ELEMENT" not in text


def _thick_diagnostic_section():
    """A screen that genuinely occupies 0.3 m, between two quadrupoles."""
    return SectionLattice(
        name="S",
        order=["Q1", "SCR", "Q2"],
        elements=[
            Quadrupole(
                name="Q1",
                machine_area="S",
                magnetic={"magnetic_length": 0.5, "k1l": 0.3},
                physical=PhysicalElement(length=0.5, middle=Position(z=0.25)),
            ),
            Screen(
                name="SCR",
                machine_area="S",
                physical=PhysicalElement(length=0.3, middle=Position(z=1.15)),
            ),
            Quadrupole(
                name="Q2",
                machine_area="S",
                magnetic={"magnetic_length": 0.5, "k1l": -0.3},
                physical=PhysicalElement(length=0.5, middle=Position(z=2.05)),
            ),
        ],
        geometry="open",
    )


def test_bmad_export_keeps_a_thick_diagnostic_thick():
    """createDrifts() collapses a Diagnostic to a point because not every code
    can express a marker that occupies space. Bmad's monitor and instrument
    both take an ``l``, so collapsing it there moves the recorded position half
    an element-length upstream of where the diagnostic really sits -- worth
    150 mm on an LCLS screen.
    """
    text = SectionLatticeTranslator.from_section(_thick_diagnostic_section()).to_bmad()

    assert "SCR: instrument, l = 0.3" in text


def test_bmad_export_does_not_shorten_the_lattice_it_was_given():
    """Whether the diagnostic keeps its length or the drifts either side
    absorb it, the section has to come out the same length.
    """
    text = SectionLatticeTranslator.from_section(_thick_diagnostic_section()).to_bmad()

    total = 0.0
    for line in text.splitlines():
        if ": drift, l = " in line or ": instrument, l = " in line:
            total += float(line.rsplit("= ", 1)[1])
        elif ": quadrupole" in line:
            total += float(line.split("l = ")[1].split(",")[0])
    assert total == pytest.approx(2.3)


def test_bmad_export_leaves_the_model_it_exported_alone():
    """The collapse used to be an assignment straight into the caller's model,
    so one export permanently zeroed every diagnostic length in it -- and
    every later export, to any code or back to YAML, inherited the loss.
    """
    section = _thick_diagnostic_section()
    SectionLatticeTranslator.from_section(section).to_bmad()
    SectionLatticeTranslator.from_section(section).to_bmad()

    assert section.elements["SCR"].physical.length == 0.3
