"""Focused regression tests for native Bmad lattice export."""

import warnings
from itertools import permutations

import numpy as np
import pytest

pytest.importorskip("easygdf")
h5py = pytest.importorskip("h5py")

from laura.models.baseModels import set_functional_definitions  # noqa: E402
from laura.models.element import (  # noqa: E402
    ELEMENT_REGISTRY,
    Aperture,
    BeamBeam,
    Combined_Corrector,
    CombinedSolenoidQuadrupole,
    Dipole,
    ElectrostaticSeparator,
    Marker,
    MatrixTransform,
    Octupole,
    Quadrupole,
    RFCavity,
    RFDeflectingCavity,
    Screen,
    Sextupole,
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
from laura.models.physical import (  # noqa: E402
    PhysicalElement,
    Position,
    Rotation,
)
from laura.models.simulation import TwissMatchSimulationElement  # noqa: E402
from laura.translator.converters import (  # noqa: E402
    elements_bmad,
    type_conversion_rules_bmad,
)
from laura.translator.converters.codes import bmad_unsupported  # noqa: E402
from laura.translator.converters.converter import translate_elements  # noqa: E402
from laura.translator.converters.layout import MachineLayoutTranslator  # noqa: E402
from laura.translator.converters.model import MachineModelTranslator  # noqa: E402
from laura.translator.converters.section import (  # noqa: E402
    SectionLatticeTranslator,
)
from laura.translator.utils.bmad import bmad_survey_frame  # noqa: E402
from unit_tests.helpers import quad  # noqa: E402


def _bmad(element, directory="."):
    return next(
        iter(translate_elements([element], directory=str(directory)).values())
    ).to_bmad()


def _export(section, **kwargs):
    return SectionLatticeTranslator.from_section(section).to_bmad(**kwargs)


def _assert_terms(text, present, absent=()):
    for term in present:
        assert term in text
    for term in absent:
        assert term not in text


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
        for source, target in type_conversion_rules_bmad.items()
        if target not in elements_bmad
    } == {}
    assert set(type_conversion_rules_bmad) - set(ELEMENT_REGISTRY) == {"Decapole"}
    assert set(ELEMENT_REGISTRY) - set(type_conversion_rules_bmad) == set(
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


@pytest.mark.parametrize(
    "cls, magnetic, stem, present, absent, sidecar_present",
    [
        pytest.param(
            Quadrupole,
            {"magnetic_length": 0.2, "gradient": 4, "k1l": 0.3},
            "quadrupole",
            ["field_calc = fieldmap", "gen_gradients = call::quadrupole.bmad"],
            "k1 =",
            [
                "field_scale = 4",
                "ele_anchor_pt = center",
                "curve = { kind = b, n = 2",
                "0: 1",
            ],
            id="quadrupole",
        ),
        pytest.param(
            Solenoid,
            {"magnetic_length": 0.2, "fields": {"S0L": 0.8}},
            "solenoid",
            ["field_calc = fieldmap", "gen_gradients = call::solenoid.bmad"],
            "ks =",
            ["field_scale = 4", "curve = { kind = bs, n = 0"],
            id="solenoid-zero-harmonic",
        ),
    ],
)
def test_bmad_generalized_gradient_sidecar(
    tmp_path, cls, magnetic, stem, present, absent, sidecar_present
):
    field_path = tmp_path / f"{stem}.hdf5"
    _write_field(
        field_path,
        "1DMagnetoStatic",
        z=[-0.1, 0, 0.1],
        Bz=[0, 1, 0],
    )
    element = cls(
        name="X",
        machine_area="S",
        magnetic=magnetic,
        simulation={"field_definition": str(field_path)},
    )
    text = _bmad(element, tmp_path)
    _assert_terms(text, present, [absent])
    _assert_terms((tmp_path / f"{stem}.bmad").read_text(), sidecar_present)


_STANDING_WAVE = {
    "frequency": 1e9,
    "n_cells": 1,
    "cell_length": 1,
    "structure_Type": "StandingWave",
}


@pytest.mark.parametrize(
    "cls, fields, present, absent",
    [
        # A string is the exact expected output; a list, substrings of it.
        pytest.param(Marker, {"name": "M1"}, "M1: marker\n", (), id="marker"),
        pytest.param(
            Quadrupole,
            {"name": "Q-1", "magnetic": {"magnetic_length": 0.5, "k1l": "kq"}},
            ["Q_1: quadrupole, l = 0.5", "k1 = kq / 0.5"],
            (),
            id="quadrupole-functional",
        ),
        pytest.param(
            Dipole,
            {
                "name": "B1",
                "magnetic": {
                    "magnetic_length": 1.0,
                    "k0l": 0.2,
                    "gap": 0.04,
                    "edge_field_integral": 0.3,
                    "tilt": 0.1,
                },
            },
            ["angle = 0.2", "hgap = 0.02", "fint = 0.3", "ref_tilt = 0.1"],
            [", gap =", ", tilt ="],
            id="dipole",
        ),
        # Bmad's `ks` is normalised like LAURA's S0L; `bs_field` is in tesla.
        pytest.param(
            Solenoid,
            {
                "name": "S1",
                "magnetic": {"magnetic_length": 2.0, "fields": {"S0L": 0.8}},
            },
            ["ks = 0.4"],
            (),
            id="solenoid",
        ),
        pytest.param(
            CombinedSolenoidQuadrupole,
            {
                "name": "SQ",
                "magnetic": {
                    "magnetic_length": 2.0,
                    "k1l": 0.6,
                    "solenoid_fields": {"S0L": 0.8},
                },
            },
            ["SQ: sol_quad, l = 2.0, k1 = 0.3, ks = 0.4"],
            (),
            id="sol_quad",
        ),
        pytest.param(
            RFCavity,
            {
                "name": "C1",
                "cavity": {"phase": 90, **_STANDING_WAVE},
                "simulation": {"field_amplitude": 2e6},
            },
            [
                "C1: lcavity",
                "n_cell = 1",
                "phi0 = -0.25",
                "cavity_type = standing_wave",
            ],
            (),
            id="lcavity",
        ),
        pytest.param(
            RFDeflectingCavity,
            {
                "name": "CR1",
                "cavity": {"phase": 180, **_STANDING_WAVE},
                "simulation": {"field_amplitude": 1e6},
            },
            ["CR1: crab_cavity", "phi0 = -0.5"],
            (),
            id="crab_cavity",
        ),
        pytest.param(
            Aperture,
            {
                "name": "A1",
                "physical": {"length": 0.2},
                "aperture": {"shape": "circular", "radius": 0.01},
            },
            "A1: ecollimator, l = 0.2, x1_limit = 0.01, "
            "x2_limit = 0.01, y1_limit = 0.01, y2_limit = 0.01\n",
            (),
            id="ecollimator",
        ),
        # LAURA sizes are full apertures, Bmad limits half widths; ``radius`` is
        # already a half width.
        pytest.param(
            Aperture,
            {
                "name": "A2",
                "physical": {"length": 0.0},
                "aperture": {
                    "shape": "rectangular",
                    "horizontal_size": 0.017,
                    "vertical_size": 0.0085,
                },
            },
            "A2: rcollimator, l = 0.0, x1_limit = 0.0085, "
            "x2_limit = 0.0085, y1_limit = 0.00425, y2_limit = 0.00425\n",
            (),
            id="rcollimator",
        ),
        pytest.param(
            ElectrostaticSeparator,
            {"name": "ES", "simulation": {"horizontal_field": 3, "vertical_field": 4}},
            ["e_field = 5.0", "tilt = 0.6435011087932844"],
            (),
            id="separator",
        ),
        pytest.param(
            BeamBeam,
            {
                "name": "BB",
                "simulation": {
                    "charge": 1,
                    "n_particles": 1e10,
                    "horizontal_sigma": 1e-3,
                },
            },
            ["BB: beambeam, charge = 1.0, n_particle = 10000000000.0"],
            [", l ="],
            id="beambeam",
        ),
        pytest.param(
            Wiggler,
            {
                "name": "W1",
                "magnetic": {
                    "magnetic_length": 2,
                    "peak_magnetic_field": 1.2,
                    "period": 0.2,
                    "num_periods": 10,
                },
            },
            ["b_max = 1.2"],
            (),
            id="wiggler",
        ),
    ],
)
def test_bmad_special_element_conversions(cls, fields, present, absent):
    set_functional_definitions({"kq": 0.3})
    text = _bmad(cls(machine_area="S", **fields))
    if isinstance(present, str):
        assert text == present
    else:
        _assert_terms(text, present, absent)


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
    assert "TW: fixer, beta_a_stored = 2.0, beta_b_stored = 3.0" in text
    assert "alpha_a_stored = -0.5" in text
    assert "is_on = T" in text
    assert "match_twiss" not in text
    assert "l = " not in text


def test_bmad_leading_twiss_match_becomes_beginning_not_a_match_element():
    """A TwissMatch is ``beginning[...]`` at a section head and a ``fixer`` elsewhere;
    a ``match`` would put a real transfer matrix in the line.
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
    quadrupole = quad("Q-1", 0.5, 0.3, middle=Position(z=0.25))
    section = SectionLattice(
        name="S-1",
        order=["BEGINNING", "Q-1"],
        elements=[seed, quadrupole],
        geometry="open",
    )
    text = _export(section)

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

    override = _export(
        section,
        initial_twiss=TwissMatchSimulationElement(
            beta_x=7, alpha_x=0.0, beta_y=8, alpha_y=0.0
        ),
    )
    assert "beginning[beta_a] = 7.0" in override
    assert "beginning[beta_a] = 2.0" not in override
    assert "matrix = match_twiss" not in override

    interior = SectionLattice(
        name="S-2",
        order=["Q-1", "BEGINNING"],
        elements=[
            quadrupole,
            seed.model_copy(
                update={"physical": PhysicalElement(length=0, middle=Position(z=1.0))}
            ),
        ],
        geometry="open",
    )
    interior_text = _export(interior)
    # ``BEGINNING`` is reserved in Bmad, hence the bmad_safe_names rename.
    assert "BEGINNING_ELEMENT: fixer, beta_a_stored = 2.0" in interior_text
    assert "eta_x_stored = 0.4" in interior_text
    assert "is_on = T" in interior_text
    assert "match_twiss" not in interior_text
    assert "beginning[beta_a]" not in interior_text


def test_bmad_section_layout_and_model_export():
    quadrupole = quad("Q-1", 0.5, 0.3, middle=Position(z=1))
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


def test_bmad_header_states_radiation_the_way_the_elements_asked():
    """Radiation is a ``bmad_com`` global in Bmad but a per-element flag in LAURA."""
    radiating = quad("Q-RAD", 0.5, 0.3, middle=Position(z=1))
    section = SectionLattice(
        name="S-1",
        order=["Q-RAD"],
        elements=[radiating],
        geometry="open",
    )
    # LAURA's defaults radiate, as elegant's `synch_rad = 1` does.
    text = _export(section)
    assert "bmad_com[radiation_damping_on] = T" in text
    assert "bmad_com[radiation_fluctuations_on] = T" in text

    radiating.simulation.sr_enable = False
    radiating.simulation.isr_enable = False
    text = _export(section)
    assert "bmad_com[radiation_damping_on] = F" in text
    assert "bmad_com[radiation_fluctuations_on] = F" in text


def test_bmad_cavity_carries_its_rf_step_count():
    """Bmad's ``n_rf_steps`` is LAURA's ``n_kicks``."""
    cavity = RFCavity(
        name="C-STEPPED",
        machine_area="S",
        cavity={
            "phase": 0,
            "frequency": 1e9,
            "n_cells": 1,
            "cell_length": 1,
            "structure_type": "StandingWave",
        },
        simulation={"field_amplitude": 2e6, "n_kicks": 1000},
        physical=PhysicalElement(length=1, middle=Position(z=2)),
    )
    assert "n_rf_steps = 1000" in _bmad(cavity)

    # `n_rf_steps = 0` is Bmad's older lcavity model, so it is written.
    old_model = cavity.model_copy(deep=True)
    old_model.simulation.n_kicks = 0
    assert "n_rf_steps = 0" in _bmad(old_model)
    unset = cavity.model_copy(deep=True)
    unset.simulation = type(cavity.simulation)(field_amplitude=2e6)
    assert "n_rf_steps" not in _bmad(unset)


def test_bmad_fringe_model_reaches_bmad_and_nowhere_it_would_be_misread():
    """Not ``fringe_type``: elegant's ``fringe_type`` means something else."""
    dipole = Dipole(
        name="B-FRINGED",
        machine_area="S",
        magnetic={"magnetic_length": 1, "k0l": 0.1},
        simulation={"fringe_model": "full"},
        physical=PhysicalElement(length=1, middle=Position(z=2)),
    )
    quadrupole = Quadrupole(
        name="Q-FRINGED",
        machine_area="S",
        magnetic={"magnetic_length": 1, "k1l": 0.1},
        simulation={"fringe_model": "soft_edge_only"},
        physical=PhysicalElement(length=1, middle=Position(z=2)),
    )
    assert "fringe_type = full" in _bmad(dipole)
    assert "fringe_type = soft_edge_only" in _bmad(quadrupole)

    converted = next(
        iter(translate_elements([quadrupole], directory=".").values())
    )
    assert "fringe" not in converted.to_elegant()

    plain = quadrupole.model_copy(deep=True)
    plain.simulation.fringe_model = None
    assert "fringe_type" not in _bmad(plain)


def test_bmad_element_aperture_is_written_without_a_collimator_standing_in():
    """LAURA widths are full, Bmad limits half; rectangular is Bmad's default shape."""
    bore = {"horizontal_size": 0.032, "vertical_size": 0.032}
    quadrupole = Quadrupole(
        name="QA01",
        machine_area="S",
        magnetic={"magnetic_length": 1, "k1l": 0.1},
        physical=PhysicalElement(length=1, middle=Position(z=2)),
        aperture=bore | {"shape": "rectangular"},
    )
    written = _bmad(quadrupole)
    assert "x1_limit = 0.016" in written
    assert "y2_limit = 0.016" in written
    assert "aperture_type" not in written

    elliptical = quadrupole.model_copy(deep=True)
    elliptical.aperture.shape = "elliptical"
    assert "aperture_type = elliptical" in _bmad(elliptical)

    bare = quadrupole.model_copy(deep=True)
    bare.aperture = None
    assert "limit" not in _bmad(bare)


def test_bmad_section_states_its_space_charge_resolution():
    """Bmad reads ``n_bin = 0``/``ds_track_step = 0`` as unconfigured and loses the
    bunch, so CSR without ``space_charge_com`` is worse than neither.
    """
    quadrupole = quad("Q-1", 0.5, 0.1, middle=Position(z=0.25))
    section = SectionLattice(
        name="S-1",
        order=["Q-1"],
        elements=[quadrupole],
        geometry="open",
        space_charge={
            "number_of_bins": 40,
            "step_size": 0.01,
            "chamber_height": 0.024,
            "bin_span": 2,
            "sigma_cutoff": 0.1,
        },
    )
    text = _export(section)
    assert "space_charge_com[n_bin] = 40" in text
    assert "space_charge_com[ds_track_step] = 0.01" in text
    assert "space_charge_com[beam_chamber_height] = 0.024" in text
    # Bmad's parser will not take `2.0` for an integer.
    assert "space_charge_com[particle_bin_span] = 2\n" in text
    assert "space_charge_com[lsc_sigma_cutoff] = 0.1" in text
    # Unset (zero images, unshielded) is left to Bmad.
    assert "n_shield_images" not in text

    overridden = _export(section, space_charge_n_bin=64)
    assert "space_charge_com[n_bin] = 64" in overridden
    assert "space_charge_com[n_bin] = 40" not in overridden

    quiet = section.model_copy(deep=True)
    quiet.space_charge = None
    assert "space_charge_com" not in _export(quiet)


def test_bmad_section_superimposes_overlapping_elements():
    base = quad("Q-BASE", 4, 0.4, middle=Position(z=2))
    overlap = quad("Q-OVER", 2, 0.2, middle=Position(z=3))
    embedded = Solenoid(
        name="S-EMBED",
        machine_area="S",
        subelement="Q-BASE",
        magnetic={"magnetic_length": 4, "fields": {"S0L": 0.8}},
        physical=PhysicalElement(length=4, middle=Position(z=2)),
    )
    downstream = quad("Q-NEXT", 2, 0.2, middle=Position(z=7))
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

    text = _export(section)

    assert "parameter[geometry] = open" in text
    assert "Q_OVER: quadrupole" in text
    assert "S_EMBED: solenoid" in text
    assert "OVERLAP: line = (Q_BASE, OVERLAP_drift_1, Q_NEXT)" in text
    assert ("superimpose, element = Q_OVER, offset = 2, ele_origin = beginning") in text
    assert (
        "superimpose, element = S_EMBED, offset = 0, ele_origin = beginning"
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

    text = _export(section)

    assert "K: kicker, l = 0.0, hkick = 0.01, vkick = -0.02" in text
    assert ("superimpose, element = K, offset = 0.5, ele_origin = beginning") in text


def _cavity_ring(geometry):
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
    quadrupole = quad("Q", 0.5, 0.3, middle=Position(z=2.0))
    return SectionLattice(
        name="R",
        order=["RF", "Q"],
        elements=[cavity, quadrupole],
        geometry=geometry,
    )


def test_bmad_closed_geometry_exports_a_cavity_as_rfcavity():
    """Bmad refuses an lcavity in a closed branch."""
    closed = _export(_cavity_ring("closed"))
    assert "RF: rfcavity" in closed
    assert "lcavity" not in closed
    # Bmad's switch is Standing_Wave -- LAURA's own "StandingWave" is rejected.
    assert "cavity_type = standing_wave" in closed

    open_line = _export(_cavity_ring("open"))
    assert "RF: lcavity" in open_line
    assert "rfcavity" not in open_line
    assert "cavity_type = standing_wave" in open_line


def test_bmad_export_writes_the_global_datum_when_the_line_is_placed():
    """Without beginning[..._position] Bmad starts every line at the origin along +Z."""
    quadrupole = quad(
        "Q",
        0.5,
        0.3,
        middle=Position(x=3.0, z=10.0),
        global_rotation={"phi": 0.0, "psi": 0.0, "theta": 0.25},
    )
    section = SectionLattice(
        name="S", order=["Q"], elements=[quadrupole], geometry="open"
    )
    text = _export(section)

    # The datum is the first element's entrance, in Bmad's floor angle convention.
    assert "beginning[x_position] = 3.06185098" in text
    assert "beginning[z_position] = 9.75777189" in text
    assert "beginning[theta_position] = -0.25" in text
    # y is zero, Bmad's default.
    assert "beginning[y_position]" not in text
    assert "beginning[phi_position]" not in text


def test_bmad_export_omits_the_datum_for_a_line_starting_at_the_origin():
    """Includes every position_mode="s" import, whose world frame starts at 0."""
    quadrupole = quad("Q", 0.5, 0.3, middle=Position(z=0.25))
    section = SectionLattice(
        name="S", order=["Q"], elements=[quadrupole], geometry="open"
    )
    text = _export(section)

    assert "_position" not in text


def _lead_section(with_origin):
    """A section whose first magnet sits 2.5 m downstream of its own start."""
    elements = [quad("Q", 0.5, 0.3, middle=Position(z=2.75))]
    order = ["Q"]
    if with_origin:
        elements.insert(
            0,
            TwissMatch(
                name="BEGINNING",
                machine_area="S",
                physical=PhysicalElement(length=0.0, middle=Position(z=0.0)),
                simulation={
                    "beta_x": 2.0,
                    "alpha_x": 0.0,
                    "beta_y": 3.0,
                    "alpha_y": 0.0,
                },
            ),
        )
        order.insert(0, "BEGINNING")
    return SectionLattice(name="S", order=order, elements=elements, geometry="open")


def test_bmad_export_restores_the_run_up_to_the_first_element():
    """createDrifts() only fills gaps between elements, not the run-up to the first."""
    text = _export(_lead_section(True))

    assert "S_lead_drift: drift, l = 2.5" in text
    assert "S: line = (S_lead_drift, Q)" in text


def test_bmad_export_invents_no_run_up_without_a_declared_start():
    """Only a leading TwissMatch (Bmad's Beginning_Ele) declares the section start."""
    text = _export(_lead_section(False))

    assert "lead_drift" not in text
    assert "S: line = (Q)" in text


def _reserved_name_section(extra=()):
    elements = [
        quad("Q", 0.5, 0.3, middle=Position(z=0.25)),
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
    """Bmad rejects an element named BEGINNING and confuses END with its own."""
    with pytest.warns(UserWarning, match="END -> END_ELEMENT"):
        text = _export(_reserved_name_section())

    assert "END_ELEMENT: marker" in text
    assert "BEGINNING_ELEMENT: marker" in text
    assert "END_ELEMENT, " in text or "END_ELEMENT)" in text
    assert "BEGINNING_ELEMENT," in text
    line = next(line for line in text.splitlines() if line.startswith("S: line"))
    assert "END_ELEMENT" in line and "BEGINNING_ELEMENT" in line


def test_bmad_export_leaves_unreserved_names_exactly_as_they_were():
    """ENDGUN, ENDL0 and ENDDMPH sit beside END in LCLS cu_hxr and are not reserved."""
    section = _reserved_name_section(extra=("ENDGUN", "ENDL0"))
    with pytest.warns(UserWarning, match="reserves"):
        text = _export(section)

    assert "ENDGUN: marker" in text
    assert "ENDL0: marker" in text
    assert "ENDGUN_ELEMENT" not in text
    assert "ENDL0_ELEMENT" not in text


def test_bmad_export_does_not_collide_a_rename_with_itself():
    """Every name is offered twice (definition, then line); renames must agree."""
    with pytest.warns(UserWarning, match="reserves"):
        text = _export(_reserved_name_section())

    assert "END_ELEMENT_2" not in text
    assert "BEGINNING_ELEMENT_2" not in text


def test_bmad_rename_steps_over_a_name_already_in_the_lattice():
    section = _reserved_name_section(extra=("END_ELEMENT",))
    with pytest.warns(UserWarning, match="END -> END_ELEMENT_2"):
        text = _export(section)

    assert text.count("END_ELEMENT: marker") == 1
    assert "END_ELEMENT_2: marker" in text


def test_bmad_export_of_an_unreserved_lattice_warns_about_nothing():
    section = SectionLattice(
        name="S",
        order=["Q"],
        elements=[quad("Q", 0.5, 0.3, middle=Position(z=0.25))],
        geometry="open",
    )
    with warnings.catch_warnings():
        warnings.simplefilter("error", UserWarning)
        text = _export(section)

    assert "_ELEMENT" not in text


def _thick_diagnostic_section():
    return SectionLattice(
        name="S",
        order=["Q1", "SCR", "Q2"],
        elements=[
            quad("Q1", 0.5, 0.3, middle=Position(z=0.25)),
            Screen(
                name="SCR",
                machine_area="S",
                physical=PhysicalElement(length=0.3, middle=Position(z=1.15)),
            ),
            quad("Q2", 0.5, -0.3, middle=Position(z=2.05)),
        ],
        geometry="open",
    )


def test_bmad_export_keeps_a_thick_diagnostic_thick():
    """Bmad monitors take ``l``; collapsing one moves it half a length upstream."""
    text = _export(_thick_diagnostic_section())

    assert "SCR: instrument, l = 0.3" in text


def test_bmad_export_does_not_shorten_the_lattice_it_was_given():
    text = _export(_thick_diagnostic_section())

    total = 0.0
    for line in text.splitlines():
        if ": drift, l = " in line or ": instrument, l = " in line:
            total += float(line.rsplit("= ", 1)[1])
        elif ": quadrupole" in line:
            total += float(line.split("l = ")[1].split(",")[0])
    assert total == pytest.approx(2.3)


def test_bmad_export_leaves_the_model_it_exported_alone():
    section = _thick_diagnostic_section()
    _export(section)
    _export(section)

    assert section.elements["SCR"].physical.length == 0.3


@pytest.mark.parametrize(
    "magnetic, present, absent",
    [
        pytest.param(
            {
                "magnetic_length": 1.0,
                "k0l": 0.2,
                "gap": 0.04,
                "edge_field_integral": 0.3,
            },
            ["hgap = 0.02", "fint = 0.3"],
            ["fintx", "hgapx"],
            id="symmetric",
        ),
        pytest.param(
            {
                "magnetic_length": 0.5,
                "k0l": 0.1,
                "gap": 0.03,
                "edge_field_integral": 0.45,
                "exit_gap": 0.0,
                "edge_field_integral_exit": 0.0,
            },
            ["fint = 0.45", "hgap = 0.015", "fintx = 0", "hgapx = 0"],
            [],
            id="entrance-half",
        ),
        pytest.param(
            {
                "magnetic_length": 0.5,
                "k0l": 0.1,
                "gap": 0.0,
                "edge_field_integral": 0.0,
                "exit_gap": 0.03,
                "edge_field_integral_exit": 0.45,
            },
            ["fint = 0", "hgap = 0", "fintx = 0.45", "hgapx = 0.015"],
            [],
            id="exit-half",
        ),
    ],
)
def test_bmad_bend_writes_fintx_only_when_the_exit_face_differs(
    magnetic, present, absent
):
    """Bmad defaults ``fintx``/``hgapx`` to their entrance twins."""
    bend = _bmad(Dipole(name="B-1", machine_area="S", magnetic=magnetic))
    _assert_terms(bend, present, absent)


def test_bmad_bend_leaves_an_unset_fringe_integral_to_bmad():
    """A gap with no fringe integral writes ``hgap`` alone; ``fint = None``
    stops Bmad's parser."""
    bend = _bmad(
        Dipole(
            name="B-GAP",
            machine_area="S",
            magnetic={"magnetic_length": 1.0, "k0l": 0.2, "gap": 0.032},
        )
    )
    assert "hgap = 0.016" in bend
    assert "fint" not in bend
    assert "None" not in bend


@pytest.mark.parametrize("geometry, etype, length", [("closed", "rfcavity", "l = 0.0"),
                                                      ("open", "lcavity", "l = 0.0333")])
def test_bmad_thin_cavity_stays_thin_where_bmad_allows(geometry, etype, length):
    """Bmad refuses a zero-length lcavity, so a linac's gets its cells' length;
    a ring's rfcavity may be thin, and lengthening it moved CLIC DR's tunes."""
    cavity = RFCavity(
        name="RF", machine_area="S", physical={"length": 0.0},
        cavity={"phase": 0.0, "frequency": 3e9, "structure_type": "StandingWave"},
        simulation={"field_amplitude": 4.5e6},
    )
    translator = next(iter(translate_elements([cavity]).values()))
    translator.bmad_geometry = geometry
    written = translator.to_bmad()
    assert f"RF: {etype}" in written
    assert length in written


@pytest.mark.parametrize(
    "simulation, written",
    [
        ({}, ["tracking_method = runge_kutta", "mat6_calc_method = tracking"]),
        ({"tracking_method": "symp_lie_ptc"}, ["tracking_method = symp_lie_ptc"]),
    ],
)
def test_bmad_bend_is_tracked_exactly_unless_the_lattice_chose(simulation, written):
    """``bmad_standard`` is not converged on combined-function bends; the
    matrix has to come from the same tracking, or Tao's optics disagree."""
    bend = _bmad(
        Dipole(
            name="B1",
            machine_area="S",
            magnetic={"magnetic_length": 1.3, "k0l": 0.11, "k1l": -0.9},
            simulation=simulation,
        )
    )
    for term in written:
        assert term in bend
    if simulation:
        assert "mat6_calc_method" not in bend


def test_bmad_sextupole_is_tracked_exactly():
    """``bmad_standard`` takes one step through a sextupole: CLIC DR's corrected
    chromaticity came out -0.6/-0.7 rather than 0/0."""
    sextupole = _bmad(
        Sextupole(
            name="S1", machine_area="S", physical={"length": 0.15},
            magnetic={"magnetic_length": 0.15, "k2l": 5.0},
        )
    )
    assert "tracking_method = runge_kutta" in sextupole
    assert "mat6_calc_method = tracking" in sextupole


@pytest.mark.parametrize(
    "k0l, tilt, written",
    [
        ({"normal": 0.02}, 0.0, "k0l = 0.02, k0l_status = bends_reference"),
        # As imported: the angle, and the roll of its plane.
        (
            {"normal": -0.01},
            np.pi / 2,
            f"k0l = -0.01, t0 = {np.pi / 2}, k0l_status = bends_reference",
        ),
        # normal + i skew = k0l exp(-i t0): a skew bend is -k0l at t0 = pi/2.
        (
            {"skew": 0.01},
            0.0,
            f"k0l = -0.01, t0 = {np.pi / 2}, k0l_status = bends_reference",
        ),
    ],
)
def test_bmad_thin_dipole_is_a_multipole_that_bends_the_reference(k0l, tilt, written):
    """A zero-length Dipole is Bmad's ``multipole, k0l_status = bends_reference``;
    Bmad refuses a zero-length ``sbend`` that bends.
    """
    thin = Dipole(
        name="DY-THIN",
        machine_area="S",
        magnetic={"order": 0, "multipoles": {"K0L": k0l}, "tilt": tilt},
        physical={"length": 0.0, "global_rotation": {"theta": 0.1, "psi": 0.001}},
    )
    text = _bmad(thin)
    assert text.startswith("DY_THIN: multipole, ")
    assert written in text
    assert "angle" not in text and "a0" not in text


@pytest.mark.parametrize(
    "cls, magnetic, present, absent",
    [
        # k3 = KnL / length; a3 = Ks3L / 3!, integrated and unscaled by the length.
        pytest.param(
            Octupole,
            {
                "magnetic_length": 0.5,
                "order": 3,
                "multipoles": {"K3L": {"order": 3, "normal": 7.5, "skew": 1.0}},
            },
            ["k3 = 15.0", "a3 = 0.16666666666666666", "scale_multipoles = F"],
            [],
            id="same-order-skew",
        ),
        # An off-order term is dropped just as silently, and lands in `bn`.
        pytest.param(
            Quadrupole,
            {
                "magnetic_length": 0.5,
                "order": 1,
                "multipoles": {
                    "K1L": {"order": 1, "normal": 2.0, "skew": 0.4},
                    "K2L": {"order": 2, "normal": 0.9},
                },
            },
            ["k1 = 4.0", "a1 = 0.4", "b2 = 0.45", "scale_multipoles = F"],
            [],
            id="off-order",
        ),
        pytest.param(
            Quadrupole,
            {"magnetic_length": 0.5, "k1l": 1.0},
            ["k1 = 2.0"],
            ["scale_multipoles", ", a1 =", ", b1 ="],
            id="plain",
        ),
    ],
)
def test_bmad_writes_the_multipole_content_the_main_attributes_cannot_hold(
    cls, magnetic, present, absent
):
    """A Bmad element carries one component of one order (``k3`` on an octupole)."""
    text = _bmad(cls(name="M-1", machine_area="S", magnetic=magnetic))
    _assert_terms(text, present, absent)


def _rolled_bend_section(order):
    elements = {
        "Q-1": quad("Q-1", 0.5, 0.3, s=0.5, s_point="end"),
        "B-1": Dipole(
            name="B-1",
            machine_area="S",
            magnetic={"magnetic_length": 2.0, "angle": 0.05, "tilt": 0.1},
            physical=PhysicalElement(length=2.0, s=2.5, s_point="end"),
        ),
        "Q-2": quad("Q-2", 0.5, 0.3, s=3.0, s_point="end"),
    }
    chosen = [elements[name] for name in order]
    section = SectionLattice(
        name="S-1", order=list(order), elements=chosen, geometry="open"
    )
    section.resolve_positions({element.name: element for element in chosen})
    return section


def test_bmad_rolled_bend_closes_its_own_roll_without_patches():
    """``ref_tilt`` is self-closing: Bmad rolls at the entrance and un-rolls at exit."""
    text = _export(_rolled_bend_section(["Q-1", "B-1", "Q-2"]))
    assert "ref_tilt = 0.1" in text
    assert "patch" not in text
    assert "S_1: line = (Q_1, B_1, Q_2)" in text

    trailing = _export(_rolled_bend_section(["Q-1", "B-1"]))
    assert "ref_tilt = 0.1" in trailing
    assert "patch" not in trailing
    assert "S_1: line = (Q_1, B_1)" in trailing


def test_bmad_survey_frame_neutralises_only_a_roll_that_is_really_there():
    """Tao's floor record cannot report ``ref_tilt``, so the importer folds it into
    ``global_rotation``; it must come back out here or a needless patch is written.
    """
    psi, angle = 0.1, 0.05
    common = {"magnetic_length": 2.0, "angle": angle, "tilt": psi}
    floor_placed = Dipole(
        name="B-F",
        machine_area="S",
        magnetic=common,
        physical=PhysicalElement(
            length=2.0,
            middle=Position(z=1.0),
            global_rotation=Rotation(theta=0.0, phi=0.0, psi=psi),
        ),
    )
    arc_placed = Dipole(
        name="B-S",
        machine_area="S",
        magnetic=common,
        physical=PhysicalElement(length=2.0, s=2.0, s_point="end"),
    )

    def _rz(a):
        return np.array(
            [[np.cos(a), -np.sin(a), 0], [np.sin(a), np.cos(a), 0], [0, 0, 1]]
        )

    ry_neg = np.array(
        [
            [np.cos(angle), 0, np.sin(angle)],
            [0, 1, 0],
            [-np.sin(angle), 0, np.cos(angle)],
        ]
    )

    assert not np.allclose(
        floor_placed.physical.rotation_matrix, arc_placed.physical.rotation_matrix
    )
    assert np.allclose(
        bmad_survey_frame(floor_placed, "start"), bmad_survey_frame(arc_placed, "start")
    )
    assert np.allclose(bmad_survey_frame(arc_placed, "start"), np.eye(3))

    # Placement mode must not change which plane the magnet bends in.
    assert np.allclose(
        bmad_survey_frame(floor_placed, "end"), _rz(psi) @ ry_neg @ _rz(-psi)
    )
    assert np.allclose(
        bmad_survey_frame(arc_placed, "end"), _rz(psi) @ ry_neg @ _rz(-psi)
    )


def test_bmad_rolled_bend_in_a_rolled_line_bends_in_its_own_plane():
    """The LCLS dump line is patch-rolled before its ``ref_tilt = pi/2`` bends, so the
    placed roll already includes the tilt, which must not be applied again.
    """
    line_roll, tilt, angle = 0.1745, np.pi / 2, 0.0224
    bend = Dipole(
        name="B-R",
        machine_area="S",
        magnetic={"magnetic_length": 1.45, "angle": angle, "tilt": tilt},
        physical=PhysicalElement(
            length=1.45,
            middle=Position(z=1.0),
            global_rotation=Rotation(theta=0.0, phi=0.0, psi=line_roll + tilt),
        ),
    )
    ry_neg = np.array(
        [
            [np.cos(angle), 0, np.sin(angle)],
            [0, 1, 0],
            [-np.sin(angle), 0, np.cos(angle)],
        ]
    )
    physical = bend.physical
    assert np.allclose(physical.end_rotation_matrix, physical.rotation_matrix @ ry_neg)
    # Bmad's exit frame is the entrance frame turned by the bend alone.
    relative = bmad_survey_frame(bend, "start").T @ bmad_survey_frame(bend, "end")
    rz = np.array(
        [[np.cos(tilt), -np.sin(tilt), 0], [np.sin(tilt), np.cos(tilt), 0], [0, 0, 1]]
    )
    assert np.allclose(relative, rz @ ry_neg @ rz.T)


@pytest.mark.parametrize(
    "cls, magnetic, present, absent",
    [
        # a1 is integrated (1! = 1), so it is KsL itself and not KsL / length.
        pytest.param(
            Quadrupole,
            {"magnetic_length": 0.5, "order": 1, "kl": 0.15, "skew": True},
            ["a1 = 0.15", "k1 = 0.0", "scale_multipoles = F"],
            [],
            id="skew-quadrupole",
        ),
        # The upright magnet of the same strength is a different lattice element.
        pytest.param(
            Quadrupole,
            {"magnetic_length": 0.5, "order": 1, "kl": 0.15},
            ["k1 = 0.3"],
            [", a1 =", "scale_multipoles"],
            id="upright-quadrupole",
        ),
        # Higher orders carry the 1/n! that `kN` does not.
        pytest.param(
            Octupole,
            {"magnetic_length": 0.5, "order": 3, "kl": 1.0, "skew": True},
            ["a3 = 0.16666666666666666", "k3 = 0.0"],
            [],
            id="skew-octupole",
        ),
        # A bend keeps `angle`: Bmad rolls its plane with `ref_tilt`, not a multipole.
        pytest.param(
            Dipole,
            {"magnetic_length": 2.0, "angle": 0.05, "skew": True},
            ["angle = 0.05"],
            [", a0 ="],
            id="skew-bend",
        ),
    ],
)
def test_bmad_skew_magnet_writes_its_strength_into_bmads_skew_slot(
    cls, magnetic, present, absent
):
    """Bmad's skew slot is ``a1``; ``k1`` keeps the element's real normal component."""
    text = _bmad(cls(name="M-S", machine_area="S", magnetic=magnetic))
    _assert_terms(text, present, absent)
