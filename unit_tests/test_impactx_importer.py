"""ImpactX import: LAURA's own export reads back to the same export, and
native ImpactX lattices and inputs files read as their users write them."""

from pathlib import Path

import numpy as np
import pytest

from laura.models.element import (
    Collimator,
    CombinedCorrector,
    MatrixTransform,
    NonLinearLens,
    RFCavity,
    Sextupole,
    Solenoid,
)
from laura.translator import ImpactXLatticeImporter
from laura.translator.converters.section import SectionLatticeTranslator
from unit_tests.helpers import quiet
from unit_tests.test_impactx_translator import LINE, bend, impactx_track, section

E = 250e6  # total energy [eV]
FODO = Path.home() / "Documents/impactx/examples/fodo/input_fodo.in"

ELEMENTS = [
    *(e.model_copy(deep=True) for e in LINE),  # placing them would move LINE's
    # unique names: a repeated one keeps the last bend in the first one's slot, out of order
    bend(physical={"s": 3.5, "error": {"position": {"x": 1e-3}}}, name="b2", tilt=0.3),
    bend(physical={"s": 4.5}, name="b3", k1l=0.3, edge_field_integral=0.5, gap=0.02),
    bend(physical={"s": 5.5}, name="b4", k2l=1.0),
    Solenoid(
        name="sol",
        machine_area="S",
        physical={"s": 6.0, "length": 0.2},
        magnetic={"length": 0.2, "fields": {"S0L": 0.4}},
    ),
    CombinedCorrector(
        name="c1",
        machine_area="S",
        physical={"s": 6.5, "length": 0.1},
        magnetic={"length": 0.1, "horizontal_kick": 1e-3, "vertical_kick": -2e-3},
    ),
    RFCavity(
        name="cav",
        machine_area="S",
        physical={"s": 7.0, "length": 0.4},
        cavity={"frequency": 1.3e9, "phase": 20.0, "structure_type": "StandingWave"},
        simulation={"field_amplitude": 5e6},
    ),
    NonLinearLens(
        name="nl",
        machine_area="S",
        physical={"s": 7.5, "length": 0.0},
        magnetic={"integrated_strength": 1e-3, "dimensional_parameter": 0.01},
    ),
    Sextupole(
        name="s_thin",
        machine_area="S",
        physical={"s": 7.6, "length": 0.0},
        magnetic={"length": 0.0, "k2l": 2.0, "k3l": 1.0},
    ),
    Collimator(
        name="col",
        machine_area="S",
        physical={"s": 8.0, "length": 0.1},
        aperture={
            "shape": "rectangular",
            "horizontal_size": 0.01,
            "vertical_size": 0.02,
            "horizontal_offset": 0.002,
        },
    ),
    MatrixTransform(
        name="m",
        machine_area="S",
        physical={"s": 9.0, "length": 0.5},
        simulation={"r_matrix": np.eye(6) + 0.1 * np.arange(36).reshape(6, 6)},
    ),
]


def imported(dicts, **kwargs):
    lattice = ImpactXLatticeImporter(lattice=dicts, **kwargs)
    return SectionLatticeTranslator.from_section(*lattice.create_section().values())


@pytest.mark.parametrize("model", ["linear", "paraxial", "exact"])
def test_export_reads_back_to_the_same_export(model):
    with quiet():
        dicts = section(*ELEMENTS).to_impactx(model=model, energy=E)
        again = imported(dicts, name="line", energy=E).to_impactx(model=model, energy=E)
    assert [d["type"] for d in again] == [d["type"] for d in dicts]
    for before, after in zip(dicts, again):
        assert after == pytest.approx(before, abs=1e-12), before["name"]


def test_native_edges_merge_into_their_bend_and_names_repeat():
    edge = {"type": "DipEdge", "name": "edge", "psi": 0.1, "rc": 5.0, "g": 0.0}
    sbend = {"type": "Sbend", "name": "sb", "ds": 1.0, "rc": 5.0}
    drift = {"type": "Drift", "name": "dr", "ds": 0.5}
    lattice = ImpactXLatticeImporter(lattice=[edge, sbend, edge, drift, sbend])
    elements = lattice.create_laura_element_dictionary()
    assert list(elements) == ["sb.1", "sb.2"]
    first, second = elements.values()
    assert first.magnetic.entrance_edge_angle == first.magnetic.exit_edge_angle == 0.1
    assert first.magnetic.angle == pytest.approx(0.2)
    assert second.simulation.edge1_effects == second.simulation.edge2_effects == 0
    assert second.physical.s == pytest.approx(2.5)


def test_fields_in_tesla_track_as_imported():
    native = [
        {"type": "ChrQuad", "name": "q", "ds": 0.5, "k": 2.0, "unit": 1},
        # an electron bends to +x in -0.3 T, through 1 m at this phi
        {"type": "ExactSbend", "name": "b", "ds": 1.0, "phi": 20.6122541, "B": -0.3},
        {"type": "Kicker", "name": "k", "xkick": 1e-3, "ykick": 2e-3, "unit": "T-m"},
    ]
    with pytest.raises(ValueError, match="energy"):
        ImpactXLatticeImporter(lattice=native).create_laura_element_dictionary()
    with quiet():
        dicts = imported(native, energy=E).to_impactx(model="paraxial", energy=E)
    assert [d.get("unit") for d in dicts] == [0, None, "dimensionless"]
    # phi is rounded, so 1 m and the field's radius differ slightly
    np.testing.assert_allclose(
        impactx_track(dicts), impactx_track(native), rtol=0, atol=1e-9
    )


@pytest.mark.skipif(not FODO.is_file(), reason="needs the ImpactX examples")
def test_reads_an_inputs_file():
    pytest.importorskip("impactx")
    lattice = ImpactXLatticeImporter(source_file=str(FODO))
    assert lattice.energy == pytest.approx(2.0e9 + 0.51099895e6)
    elements = lattice.create_laura_element_dictionary()
    q1, q2 = (elements[n] for n in ("quad1", "quad2"))
    assert (q1.magnetic.multipoles.K1L.normal, q2.magnetic.multipoles.K1L.normal) == (
        1.0,
        -1.0,
    )
    assert q2.physical.s == pytest.approx(2.75)
    assert sum(name.startswith("monitor") for name in elements) == 6


def test_an_inputs_file_includes_files_beside_it_and_leaves_diags_alone(tmp_path):
    pytest.importorskip("impactx")
    (tmp_path / "input_fodo.in").write_text(FODO.read_text())
    (tmp_path / "main.in").write_text("FILE = input_fodo.in\n")
    (tmp_path / "diags").mkdir()
    (tmp_path / "diags" / "keep").touch()
    lattice = ImpactXLatticeImporter(source_file=str(tmp_path / "main.in"))
    assert "quad1" in lattice.create_laura_element_dictionary()
    assert sorted(p.name for p in tmp_path.iterdir()) == [
        "diags",
        "input_fodo.in",
        "main.in",
    ]
    assert (tmp_path / "diags" / "keep").exists()
