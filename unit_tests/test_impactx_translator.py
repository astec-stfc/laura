"""ImpactX export, tracked through ImpactX against PTC on LAURA's own MAD-X export."""

import json
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
import pytest

from laura.models.element import (
    Collimator,
    CombinedCorrector,
    CrabCavity,
    Dipole,
    MatrixTransform,
    Quadrupole,
    RFCavity,
    Sextupole,
    Solenoid,
    Wiggler,
)
from laura.models.element_list import ElementList, SectionLattice
from laura.translator.conversion_rules.codes.impactx_conversion import (
    fourier_coefficients,
    tier,
)
from laura.translator.converters.converter import translate_elements
from laura.translator.converters.section import SectionLatticeTranslator
from laura.translator.utils.fields import FieldMap
from laura.translator.utils.fields.field_parameter import FieldParameter
from laura.translator.utils.units import UnitValue
from unit_tests.helpers import quiet

E = 250.0  # total energy [MeV]
P = np.sqrt(E**2 - 0.51099895069**2)
# (x, px, y, py, t, pt), MAD-X's canonical coordinates
START = [
    [0, 0, 0, 0, 0, 0],
    [1e-3, 0, 0, 0, 0, 0],
    [0, 0, 1e-3, 0, 0, 0],
    [2e-3, 1e-4, -1.5e-3, 2e-4, 0, 0],
    [1e-3, 0, 1e-3, 0, 0, 5e-3],
    [0, 0, 0, 0, 1e-3, 0],
]

# ImpactX's AMReX runtime initialises once per process, so each run gets its own
IMPACTX = """
import json, sys, warnings
import numpy as np
from impactx import ImpactX
from laura.translator.conversion_rules.codes.impactx_conversion import lattice
warnings.simplefilter("ignore")
spec = json.load(sys.stdin)
sim = ImpactX()
sim.space_charge = False
sim.slice_step_diagnostics = False
sim.verbose = 0
sim.init_grids()
mass = 0.51099895069
sim.beam.ref.set_species("electron").set_kin_energy_MeV(spec["energy"] - mass)
x, px, y, py, t, pt = np.array(spec["start"], dtype=float).T
sim.beam.add_n_particles(x, y, -t, px, py, -pt, -1 / mass / 1e6, bunch_charge=1e-12)
for element in lattice(spec["dicts"]):
    sim.lattice.append(element)
sim.track_particles()
df = sim.beam.to_df(local=True).reset_index(drop=True).sort_values("idcpu")
ref = sim.beam.ref
p0, e0 = ref.beta_gamma * ref.mass_MeV, ref.gamma * ref.mass_MeV
out = np.column_stack([df.position_x, df.momentum_x * p0, df.position_y,
                       df.momentum_y * p0, -df.position_t, e0 - df.momentum_t * p0])
sim.finalize()
json.dump(out.tolist(), open("out.json", "w"))
"""


def impactx_track(dicts, start=START, energy=E):
    """``(x, px [MeV], y, py [MeV], t, E [MeV])`` of each surviving particle,
    ``t`` in MAD-X's sign."""
    pytest.importorskip("impactx")
    spec = json.dumps({"dicts": dicts, "energy": energy, "start": start})
    # ImpactX writes diags/ into its working directory
    with tempfile.TemporaryDirectory() as tmp:
        run = subprocess.run(
            [sys.executable, "-I", "-c", IMPACTX],
            input=spec,
            capture_output=True,
            text=True,
            cwd=tmp,
        )
        assert not run.returncode, run.stderr[-2000:]
        return np.array(json.loads(Path(tmp, "out.json").read_text()))


def ptc_track(madx, cwd):
    cpymad = pytest.importorskip("cpymad.madx")
    m = cpymad.Madx(stdout=False, cwd=cwd)
    m.input(f"beam, particle=electron, energy={E / 1e3};")
    m.input(madx.replace("line:", "seq:", 1))
    m.input("use, sequence=seq;")
    if "line_errors" in madx:
        m.input("exec, line_errors;")
    m.input("ptc_create_universe;")
    m.input("ptc_create_layout, model=2, method=6, nst=20, exact=true;")
    m.input("ptc_align;")
    for x, px, y, py, t, pt in START:
        m.input(f"ptc_start, x={x}, px={px}, y={y}, py={py}, t={t}, pt={pt};")
    m.input("ptc_track, icase=6, closed_orbit=false, onetable=true, dump=false;")
    m.input("ptc_track_end; ptc_end;")
    ts = m.table.tracksumm
    final = ts.turn == 1
    return np.column_stack([ts.x, ts.px * P, ts.y, ts.py * P, ts.t, E + ts.pt * P])[
        final
    ]


def translator(element):
    return next(iter(translate_elements([element]).values()))


def section(*elements):
    registry = {e.name: e for e in elements}
    lattice = SectionLattice(
        name="line", order=list(registry), elements=ElementList(elements=registry)
    )
    lattice.resolve_positions(lattice.elements.elements)
    return SectionLatticeTranslator.from_section(lattice)


def bend(physical=None, name="b1", **magnetic):
    return Dipole(
        name=name,
        machine_area="S",
        physical={"s": 0.5, "length": 1.0, **(physical or {})},
        magnetic={
            "length": 1.0,
            "angle": 0.2,
            "entrance_edge_angle": 0.1,
            "exit_edge_angle": 0.05,
            **magnetic,
        },
    )


SOLENOID = Solenoid(
    name="sol",
    machine_area="S",
    physical={"s": 0.1, "length": 0.2},
    magnetic={"length": 0.2, "fields": {"S0L": 0.4}},
)
LINE = [
    Quadrupole(
        name="q1",
        machine_area="S",
        physical={"s": 0.5, "length": 0.3, "error": {"position": {"x": 1e-3}}},
        magnetic={"length": 0.3, "k1l": 0.6, "tilt": 0.05},
    ),
    Dipole(
        name="b1",
        machine_area="S",
        physical={"s": 1.5, "length": 1.0},
        magnetic={"length": 1.0, "angle": 0.2, "entrance_edge_angle": 0.1},
    ),
    Sextupole(
        name="s1",
        machine_area="S",
        physical={"s": 2.5, "length": 0.2},
        magnetic={"length": 0.2, "k2l": 5.0},
    ),
]


# tol is in m / rad: the linear tier and the nonlinear fringe drift furthest
@pytest.mark.parametrize(
    "elements, model, tol",
    [
        (LINE, "exact", 1e-8),
        ([bend(tilt=0.3)], "exact", 1e-8),
        (
            [bend(physical={"error": {"position": {"x": 1e-3, "y": -5e-4}}})],
            "exact",
            1e-6,
        ),
        ([bend(k1l=0.3)], "exact", 1e-6),
        ([bend(edge_field_integral=0.5)], "exact", 1e-5),
        ([bend(edge_field_integral=0.5)], "linear", 1e-5),
        ([bend(k1l=0.3)], "linear", 1e-5),
        ([SOLENOID], "linear", 1e-5),
        ([SOLENOID], "paraxial", 1e-7),
        (
            [
                CombinedCorrector(
                    name="c1",
                    machine_area="S",
                    physical={"s": 0.05, "length": 0.1},
                    magnetic={
                        "length": 0.1,
                        "horizontal_kick": 1e-3,
                        "vertical_kick": -2e-3,
                    },
                )
            ],
            "exact",
            1e-8,
        ),
        # thin: PTC's thick cavity applies a transit-time factor MAD-X's volt excludes
        (
            [
                RFCavity(
                    name="cav",
                    machine_area="S",
                    physical={"s": 0.0, "length": 0.0},
                    cavity={
                        "frequency": 1.3e9,
                        "phase": 20.0,
                        "structure_type": "StandingWave",
                    },
                    simulation={"field_amplitude": 5e6},
                ),
                Quadrupole(
                    name="pad",
                    machine_area="S",
                    physical={"s": 0.5, "length": 1.0},
                    magnetic={"length": 1.0, "k1l": 0.0},
                ),
            ],
            "exact",
            1e-8,
        ),
    ],
    ids=[
        "line",
        "bend-tilt",
        "bend-offset",
        "cfbend",
        "fint",
        "fint-linear",
        "cfbend-linear",
        "sol",
        "sol-chracc",
        "corrector",
        "rf",
    ],
)
def test_tracks_as_ptc(elements, model, tol, tmp_path):
    lattice = section(*elements)
    with quiet():
        dicts = lattice.to_impactx(model=model, energy=E * 1e6)
        madx = lattice.to_madx(Brho=-P * 1e6 / 299792458.0)
    diff = abs(impactx_track(dicts) - ptc_track(madx, tmp_path))
    # not t: ImpactX's reference particle gains energy in RF and follows the
    # nonlinear fringe, and a bend's dx moves each face, adding angle * dx
    assert diff[:, [0, 2]].max() < tol
    assert diff[:, [1, 3, 5]].max() < tol * P


def test_matrix_acts_in_bmad_coordinates():
    """At 1 MeV, beta = 0.86, so the scaling of t and pt shows."""
    energy = 1.0
    p = np.sqrt(energy**2 - 0.51099895069**2)
    beta = p / energy
    r = np.eye(6)
    r[0, 1], r[2, 0], r[0, 5], r[4, 5], r[5, 4], r[4, 0] = 2, 0.3, 0.1, 0.5, -0.2, 0.05
    m = MatrixTransform(
        name="m",
        machine_area="S",
        physical={"length": 0.5},
        simulation={"r_matrix": r, "t_matrix": np.full((6, 6, 6), 0.1)},
    )
    with pytest.warns(UserWarning, match="assume beta = 1"):
        translator(m).to_impactx()
    with pytest.warns(UserWarning, match="T matrix was dropped"):
        dicts = translator(m).to_impactx(energy=energy * 1e6)
    start = np.array(
        [
            [1e-3, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 1e-3],
            [0, 0, 0, 0, 1e-3, 0],
            [1e-3, 2e-4, -1e-3, 1e-4, 2e-4, -5e-4],
        ]
    )
    # the harness takes MAD-X's t = z / beta and pt = beta pz
    madx = start * [1, 1, 1, 1, 1 / beta, beta]
    x, px, y, py, t, e = impactx_track(dicts, madx.tolist(), energy).T
    tracked = np.column_stack([x, px / p, y, py / p, t * beta, (e - energy) / p / beta])
    np.testing.assert_allclose(tracked, start @ r.T, rtol=0, atol=1e-9)


def test_collimator_cuts_at_both_ends_about_its_offset():
    rect = {
        "shape": "rectangular",
        "horizontal_size": 0.01,
        "vertical_size": 0.02,
        "horizontal_offset": 0.002,
    }
    c = Collimator(
        name="c1", machine_area="S", physical={"s": 0.5, "length": 0.1}, aperture=rect
    )
    dicts = section(c).to_impactx()
    assert [d["type"] for d in dicts] == ["Aperture", "ExactDrift", "Aperture"]
    # x from -8 mm to +12 mm; the last particle drifts out through the exit
    xs = [(-0.0085, 0), (-0.0075, 0), (0.0115, 0), (0.0125, 0), (0.0115, 0.02)]
    survivors = impactx_track(dicts, [[x, px, 0, 0, 0, 0] for x, px in xs])[:, 0]
    np.testing.assert_allclose(survivors, [-0.0075, 0.0115])


def test_round_bore_rides_on_magnet_parts():
    q = Quadrupole(
        name="q",
        machine_area="S",
        physical={"length": 0.3},
        magnetic={"length": 0.3, "k1l": 0.6},
        aperture={
            "shape": "elliptical",
            "horizontal_size": 0.01,
            "vertical_size": 0.02,
        },
    )
    (d,) = translator(q).to_impactx()
    assert (d["aperture_x"], d["aperture_y"]) == (0.01, 0.02)


def test_fringe_integrals_reach_the_edges():
    d = translator(bend(fringe_k0=0.1, fringe_k6=0.2)).to_impactx()
    assert d[0]["K0"] == d[-1]["K0"] == 0.1
    assert d[0]["K6"] == 0.2 and "K1" not in d[0]


def test_hard_edge_without_fint():
    entry, body, exit_ = translator(bend()).to_impactx()
    assert entry["g"] == exit_["g"] == 0.0
    assert body["type"] == "ExactSbend"


def test_bend_roll_error_is_dropped_with_a_warning():
    b = bend(physical={"error": {"rotation": {"psi": 0.01}}}, tilt=0.3)
    with pytest.warns(UserWarning, match="ImpactX"):
        parts = translator(b).to_impactx()
    assert all(p.get("rotation", np.degrees(0.3)) == np.degrees(0.3) for p in parts)


@pytest.mark.parametrize("cls", [CrabCavity, Wiggler])
def test_unsupported_types_become_drifts_with_a_warning(cls):
    element = cls(name="x", machine_area="S", physical={"length": 0.5})
    with pytest.warns(UserWarning, match="not supported by ImpactX"):
        parts = translator(element).to_impactx()
    assert parts == [{"type": "ExactDrift", "name": "x", "ds": 0.5}]


def test_tiers_round_up():
    assert tier(("linear", "exact"), "paraxial") == "exact"
    assert tier(("linear", "paraxial"), "exact") == "paraxial"
    with pytest.raises(ValueError):
        tier(("linear",), "symplectic")
    assert [d["type"] for d in translator(SOLENOID).to_impactx("exact", 250e6)] == [
        "ChrAcc"
    ]


def field_map_cavity(
    tmp_path, span=1.0, cavity_type="StandingWave", phase=0.0, crest=0.0
):
    """A 3-cell pi-mode cavity at 1.3 GHz whose on-axis map spans ``span`` of it."""
    length = 1.5 * 299792458.0 / 1.3e9
    z = np.linspace(0, span * length, 301)
    field = FieldMap()
    field.filename = str(tmp_path / f"{cavity_type}{span}.hdf5")
    field.field_type, field.cavity_type, field.frequency = (
        "1DElectroDynamic",
        cavity_type,
        1.3e9,
    )
    field.z = FieldParameter(name="z", value=UnitValue(z, "m"))
    field.Ez = FieldParameter(
        name="Ez", value=UnitValue(np.sin(3 * np.pi * z / z[-1]), "V/m")
    )
    field.read = True
    if cavity_type == "TravellingWave":
        field.start_cell_z, field.end_cell_z = z[0], z[-1]
        field.mode_numerator, field.mode_denominator = 2, 3
    return RFCavity(
        name="cav",
        machine_area="S",
        physical={"s": length / 2, "length": length},
        cavity={
            "frequency": 1.3e9,
            "structure_type": "StandingWave",
            "phase": phase,
            "crest": crest,
        },
        simulation={
            "field_amplitude": 20e6,
            "field_definition": field.write_field_file(code="hdf5"),
        },
    )


def test_fourier_coefficients_match_impactx():
    impactx = pytest.importorskip("impactx")
    z = np.sort(np.random.default_rng(1).uniform(-0.5, 0.5, 200))
    field = np.cos(3 * np.pi * z) + 0.3 * z
    ours = fourier_coefficients(z, field, 40)
    np.testing.assert_allclose(
        ours, impactx.fourier_coefficients(z, field, 40), atol=1e-14
    )


def test_a_standing_wave_field_map_tracks_with_its_transit_time_gain(tmp_path):
    """At 250 MeV the reference particle crosses at c, so its crest and gain
    are those of the field map's transit-time integral."""
    k = 2 * np.pi * 1.3e9 / 299792458.0
    cavity = field_map_cavity(tmp_path)
    z = np.linspace(0, cavity.physical.length, 3001)
    integral = np.trapezoid(np.sin(3 * np.pi * z / z[-1]) * np.exp(1j * k * z), z)
    crest = -np.degrees(np.angle(integral))
    energies = []
    for phase in (0.0, 30.0):
        (d,) = translator(
            field_map_cavity(tmp_path, phase=phase, crest=crest)
        ).to_impactx(energy=E * 1e6, field_maps=True)
        assert d["type"] == "RFCavity" and d["phase"] == pytest.approx(crest - phase)
        energies.append(impactx_track([d])[:, 5])
    gain = 20.0 * abs(integral)
    np.testing.assert_allclose(
        [e[0] - E for e in energies], [gain, gain * np.cos(np.radians(30))], rtol=1e-4
    )
    # linear in the beam: an early particle (MAD-X t = 1 mm) sits k t further
    # from crest, with no RF curvature
    e = energies[1]
    chirp = (e[5] - e[0]) / (e[0] - E)
    assert chirp == pytest.approx(-np.tan(np.radians(30)) * k * 1e-3, rel=1e-3)


@pytest.mark.parametrize(
    "span, cavity_type, field_maps, warns",
    [
        (1.0, "StandingWave", False, False),
        (0.5, "StandingWave", True, True),
        (1.0, "TravellingWave", True, False),
    ],
)
def test_other_cavities_stay_thin(tmp_path, span, cavity_type, field_maps, warns):
    cavity = translator(field_map_cavity(tmp_path, span, cavity_type))
    with pytest.warns(UserWarning, match="field map spans") if warns else quiet():
        parts = cavity.to_impactx(energy=E * 1e6, field_maps=field_maps)
    assert [p["type"] for p in parts] == ["ExactDrift", "ShortRF", "ExactDrift"]


def test_save_writes_json_in_directory(tmp_path):
    lattice = section(*LINE)
    lattice.directory = str(tmp_path)
    dicts = lattice.to_impactx(save=True)
    assert json.loads((tmp_path / "line.impactx.json").read_text()) == dicts
