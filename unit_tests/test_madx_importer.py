"""Tests for the MAD-X TWISS TFS importer (``MadxLatticeImporter``).

A MAD-X TWISS TFS table supplies both element parameters and, via its own ``S``
column (MAD-X's cumulative arc-length at the exit of each element),
``position_mode="s"`` positioning. The fixture is a hand-written TFS table
exercising one element of each type.
"""

import os
import math
from pathlib import Path

import pytest

from laura.translator.converters.codes.madx import MadxLatticeImporter

_TWISS = os.path.join(os.path.dirname(__file__), "data", "madx_test_twiss.tfs")


@pytest.fixture
def importer():
    imp = MadxLatticeImporter(twiss_file=_TWISS)
    imp.create_laura_element_dictionary()
    return imp


class TestMadxImporter:
    def test_drift_not_imported(self, importer):
        assert "DR1" not in importer.elements

    def test_lattice_name_from_sequence_header(self, importer):
        assert importer.lattice_name == "TESTLINE"

    def test_marker(self, importer):
        assert importer.elements["BEG"].hardware_type == "Marker"

    def test_quadrupole_integrated_strength(self, importer):
        q = importer.elements["Q1"]
        assert q.hardware_type == "Quadrupole"
        assert q.magnetic.KnL(1) == pytest.approx(0.2)

    def test_dipole_angle_and_edges(self, importer):
        b = importer.elements["B1"]
        assert b.hardware_type == "Dipole"
        assert b.magnetic.KnL(0) == pytest.approx(0.1)
        assert b.magnetic.entrance_edge_angle == pytest.approx(0.05)
        assert b.magnetic.exit_edge_angle == pytest.approx(0.05)

    def test_sextupole_integrated_strength(self, importer):
        s = importer.elements["S1"]
        assert s.magnetic.KnL(2) == pytest.approx(0.18)

    def test_correctors_pick_up_plane_specific_kick(self, importer):
        hk = importer.elements["HK1"]
        vk = importer.elements["VK1"]
        cc = importer.elements["CC1"]
        assert hk.hardware_type == "Horizontal_Corrector"
        assert hk.magnetic.horizontal_kick == pytest.approx(0.03)
        assert vk.hardware_type == "Vertical_Corrector"
        assert vk.magnetic.vertical_kick == pytest.approx(0.04)
        assert cc.hardware_type == "Combined_Corrector"
        assert cc.magnetic.horizontal_kick == pytest.approx(0.02)
        assert cc.magnetic.vertical_kick == pytest.approx(0.03)

    def test_cavity_units_and_phase_convention(self, importer):
        c = importer.elements["C1"]
        assert c.hardware_type == "RFCavity"
        assert c.simulation.field_amplitude == pytest.approx(20.0e6)
        assert c.cavity.frequency == pytest.approx(2998.5e6)
        assert c.cavity.phase == pytest.approx(0.0)

    def test_solenoid_field(self, importer):
        sol = importer.elements["SOL1"]
        assert sol.hardware_type == "Solenoid"
        assert sol.magnetic.fields.S0L == pytest.approx(0.2)

    def test_rcollimator_disambiguated_and_sized(self, importer):
        col = importer.elements["COL1"]
        assert col.hardware_type == "Collimator"
        assert col.aperture.horizontal_size == pytest.approx(0.01)
        assert col.aperture.vertical_size == pytest.approx(0.02)

    def test_s_position_mode(self, importer):
        assert importer.elements["Q1"].physical.s == pytest.approx(1.5)
        assert importer.elements["Q1"].physical.s_point == "end"

    def test_create_section_resolves_positions(self, importer):
        section = importer.create_section()
        seclat = list(section.values())[0]
        assert seclat.elements.elements["Q1"].physical.middle is not None

    def test_create_layout(self, importer):
        layout = importer.create_layout()
        assert layout.name == "TESTLINE"
        assert len(layout.sections) == 1


def test_source_import_retains_deferred_strength(tmp_path):
    pytest.importorskip("cpymad")
    source = tmp_path / "line.madx"
    source.write_text(
        "beam, particle=electron, energy=1;\n"
        "quad_k1l = 0.3;\n"
        "q: quadrupole, l=0.5, k1 := quad_k1l / 0.5;\n"
        "line: sequence, l=1; q, at=0.5; endsequence;\n"
    )

    importer = MadxLatticeImporter(source_file=str(source))
    elements = importer.create_laura_element_dictionary()
    layout = importer.create_layout()

    assert importer.functional_definitions == {"quad_k1l": pytest.approx(0.3)}
    assert elements["q"].magnetic.multipoles.K1L.normal == "quad_k1l"
    assert layout.functional_definitions == {"quad_k1l": pytest.approx(0.3)}


def test_source_import_numbers_occurrences_and_integrates_direct_strength(tmp_path):
    pytest.importorskip("cpymad")
    source = tmp_path / "repeated.madx"
    source.write_text(
        "beam, particle=electron, energy=1;\n"
        "quad_k1 = 0.4;\n"
        "q: quadrupole, l=0.5, k1 := quad_k1;\n"
        "bpm: monitor;\n"
        "line: sequence, l=2; q, at=0.5; bpm, at=1; q, at=1.5; endsequence;\n"
    )

    importer = MadxLatticeImporter(source_file=str(source))
    elements = importer.create_laura_element_dictionary()

    assert list(elements) == ["line_start", "q.1", "bpm", "q.2", "line_end"]
    assert elements["bpm"].hardware_type == "Beam_Position_Monitor"
    assert elements["q.1"].magnetic.multipoles.K1L.normal == "quad_k1"
    assert importer.functional_definitions == {"quad_k1": pytest.approx(0.2)}


def test_source_import_follows_call_statements(tmp_path):
    pytest.importorskip("cpymad")
    (tmp_path / "sub").mkdir()
    (tmp_path / "sub" / "definitions.madx").write_text(
        "qk1 = 0.3;\nq: quadrupole, l = 0.5, k1 = qk1;\n"
    )
    source = tmp_path / "main.madx"
    source.write_text(
        'call, file = "sub/definitions.madx";\n'
        "beam, particle=electron, energy=1;\n"
        "line: sequence, l=1; q, at=0.5; endsequence;\n"
    )

    importer = MadxLatticeImporter(source_file=str(source))
    elements = importer.create_laura_element_dictionary()

    assert elements["q"].magnetic.KnL(1) == pytest.approx(0.15)


def test_declared_constants_in_called_files_are_preserved(tmp_path):
    """A constant declared only in a call'd file, and not referenced by any
    element's deferred expression, must still show up in
    functional_definitions."""
    pytest.importorskip("cpymad")
    (tmp_path / "sub.madx").write_text("unused_const = 3.14;\n")
    source = tmp_path / "main.madx"
    source.write_text(
        'call, file = "sub.madx";\n'
        "beam, particle=electron, energy=1;\n"
        "q: quadrupole, l=0.5, k1=0.4;\n"
        "line: sequence, l=1; q, at=0.5; endsequence;\n"
    )

    importer = MadxLatticeImporter(source_file=str(source))
    importer.create_laura_element_dictionary()

    assert importer.functional_definitions["unused_const"] == pytest.approx(3.14)


def test_create_machine_model_builds_one_layout_per_sequence(tmp_path):
    pytest.importorskip("cpymad")
    source = tmp_path / "two_sequences.madx"
    source.write_text(
        "beam, particle=electron, energy=1;\n"
        "q1: quadrupole, l=0.5, k1=0.4;\n"
        "line1: sequence, l=1; q1, at=0.5; endsequence;\n"
        "q2: quadrupole, l=0.5, k1=0.6;\n"
        "line2: sequence, l=1; q2, at=0.5; endsequence;\n"
    )

    importer = MadxLatticeImporter(source_file=str(source))
    model = importer.create_machine_model(min_section_length=1)

    assert set(model.lattices) == {"line1", "line2"}
    assert model.elements["q1"].magnetic.KnL(1) == pytest.approx(0.2)
    assert model.elements["q2"].magnetic.KnL(1) == pytest.approx(0.3)


def test_create_machine_model_requires_source_file_for_multiple_sequences(tmp_path):
    importer = MadxLatticeImporter(twiss_file=_TWISS)
    model = importer.create_machine_model(min_section_length=1)

    assert list(model.lattices) == ["TESTLINE"]


def test_source_import_folds_dipedges_into_dipole(tmp_path):
    pytest.importorskip("cpymad")
    source = tmp_path / "edges.madx"
    source.write_text(
        "beam, particle=electron, energy=1;\n"
        "edge: dipedge, h=0.2, e1=0.03, hgap=0.01, fint=0.4;\n"
        "bend: sbend, l=1, angle=0.2;\n"
        "line: sequence, l=2; edge, at=0.5; bend, at=1; "
        "edge, at=1.5; endsequence;\n"
    )

    elements = MadxLatticeImporter(
        source_file=str(source)
    ).create_laura_element_dictionary()
    bend = elements["bend"]

    assert not any(name.startswith("edge") for name in elements)
    assert bend.magnetic.entrance_edge_angle == pytest.approx(0.03)
    assert bend.magnetic.exit_edge_angle == pytest.approx(0.03)
    assert bend.magnetic.gap == pytest.approx(0.02)
    assert bend.magnetic.edge_field_integral == pytest.approx(0.4)


def test_twiss_file_start_marker_imports_as_twiss_match(tmp_path):
    """Every MAD-X TWISS table carries its own synthetic ``<sequence>$start``
    marker at s=0, whose betx/alfx/bety/alfy/dx/dpx/dy/dpy columns are the
    initial optics the TWISS command was given -- explicit betx=/alfx=/...,
    a BETA0= reference, or a ring's own periodic solution."""
    twiss = tmp_path / "twiss.tfs"
    twiss.write_text(
        '@ SEQUENCE %s "SEQ"\n'
        "* NAME KEYWORD S L BETX ALFX BETY ALFY DX DPX DY DPY\n"
        "$ %s %s %le %le %le %le %le %le %le %le %le %le\n"
        '"SEQ$START" "MARKER" 0.0 0.0 9.42 -0.66 22.19 1.51 0.1 0.01 0.2 0.02\n'
        '"Q1" "QUADRUPOLE" 0.5 0.5 10.0 -0.3 20.0 0.4 0.11 0.01 0.22 0.03\n'
        '"SEQ$END" "MARKER" 0.5 0.0 10.0 -0.3 20.0 0.4 0.11 0.01 0.22 0.03\n'
    )

    importer = MadxLatticeImporter(twiss_file=str(twiss))
    elements = importer.create_laura_element_dictionary()

    start = elements["SEQ$START"]
    assert start.hardware_type == "TwissMatch"
    assert start.physical.s == pytest.approx(0.0)
    assert start.physical.length == pytest.approx(0.0)
    assert start.simulation.beta_x == pytest.approx(9.42)
    assert start.simulation.beta_y == pytest.approx(22.19)
    assert start.simulation.alpha_x == pytest.approx(-0.66)
    assert start.simulation.alpha_y == pytest.approx(1.51)
    assert start.simulation.eta_x == pytest.approx(0.1)
    assert start.simulation.eta_y == pytest.approx(0.2)
    assert start.simulation.eta_xp == pytest.approx(0.01)
    assert start.simulation.eta_yp == pytest.approx(0.02)
    assert start.simulation.from_beam is False
    assert elements["SEQ$END"].hardware_type == "Marker"
    assert next(iter(elements)) == "SEQ$START"


def test_nested_sequence_is_flattened(tmp_path):
    """A ring assembled from sub-sequences (e.g. LEIR's SS10/Arc10/SS20/...)
    has those sub-sequences as opaque `Sequence` entries in
    `madx.sequence[...].elements`."""
    source = tmp_path / "nested.madx"
    source.write_text(
        "q1: quadrupole, l=0.5, k1=0.2;\n"
        "q2: quadrupole, l=0.5, k1=0.3;\n"
        "sub1: sequence, l=1; q1, at=0.5; endsequence;\n"
        "sub2: sequence, l=1; q2, at=0.5; endsequence;\n"
        "main: sequence, l=2;\n"
        "  sub1, at=0.5;\n"
        "  sub2, at=1.5;\n"
        "endsequence;\n"
    )

    elements = MadxLatticeImporter(
        source_file=str(source), sequence="main"
    ).create_laura_element_dictionary()

    quads = [name for name, el in elements.items() if el.hardware_type == "Quadrupole"]
    assert len(quads) == 2


def test_previously_unmapped_native_types_are_imported(tmp_path):
    source = tmp_path / "types.madx"
    source.write_text(
        "rb: rbend, l=1, angle=0.05;\n"
        "hm: hmonitor;\n"
        "vm: vmonitor;\n"
        "ins: instrument;\n"
        "col: collimator, l=0.3;\n"
        "tk: tkicker, l=0.1;\n"
        "line: sequence, l=3;\n"
        "  rb, at=0.5; hm, at=1.1; vm, at=1.2; ins, at=1.3; col, at=1.6; tk, at=1.9;\n"
        "endsequence;\n"
    )

    elements = MadxLatticeImporter(
        source_file=str(source), sequence="line"
    ).create_laura_element_dictionary()

    assert elements["rb"].hardware_type == "Dipole"
    assert elements["rb"].magnetic.KnL(0) == pytest.approx(0.05)
    assert elements["hm"].hardware_type == "Diagnostic"
    assert elements["vm"].hardware_type == "Diagnostic"
    assert elements["ins"].hardware_type == "Diagnostic"
    assert elements["col"].hardware_type == "Collimator"
    assert elements["tk"].hardware_type == "Combined_Corrector"


def test_multipole_resolves_order_from_knl_ksl(tmp_path):
    source = tmp_path / "multipole.madx"
    source.write_text(
        "sext: multipole, knl={0, 0, 1.117};\n"
        "skewquad: multipole, ksl={0, -0.05};\n"
        "line: sequence, l=2; sext, at=0.5; skewquad, at=1.5; endsequence;\n"
    )

    elements = MadxLatticeImporter(
        source_file=str(source), sequence="line"
    ).create_laura_element_dictionary()

    assert elements["sext"].hardware_type == "Sextupole"
    assert elements["sext"].magnetic.KnL(2) == pytest.approx(1.117)
    assert elements["skewquad"].hardware_type == "Quadrupole"
    assert elements["skewquad"].magnetic.multipoles.K1L.skew == pytest.approx(-0.05)


def test_symbolic_bend_angle_does_not_crash_physical_angle(tmp_path):
    source = tmp_path / "symbolic_angle.madx"
    source.write_text(
        "kminwr = 0.01;\n"
        "b: sbend, l=1, angle:=kminwr;\n"
        "line: sequence, l=1; b, at=0.5; endsequence;\n"
    )

    elements = MadxLatticeImporter(
        source_file=str(source), sequence="line"
    ).create_laura_element_dictionary()

    assert elements["b"].hardware_type == "Dipole"
    assert elements["b"].magnetic.multipoles.K0L.normal == "kminwr"
    assert elements["b"].physical.physical_angle == pytest.approx(0.0)


def test_native_element_list_is_not_self_referential(tmp_path):
    import argparse
    import sys

    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "examples"))
    import import_lattice_example as example

    source = tmp_path / "unmapped.madx"
    source.write_text(
        "unmapped_elem: translation, dx=0.001;\n"
        "line: sequence, l=1; unmapped_elem, at=0.5; endsequence;\n"
    )
    args = argparse.Namespace(
        code="madx",
        lattice=str(source),
        kind="auto",
        sequence=None,
        beamline=None,
        libtao=None,
        universe=1,
        line_name=None,
        variable=None,
    )

    importer, native, layout, strengths = example.load(args)

    assert any(row.name == "unmapped_elem" for row in native)
    result = example.compare(native, example.resolved_elements(layout), 1e-9, strengths)
    assert result["unexpected_drops"]
    assert result["unexpected_drops"][0].name == "unmapped_elem"


def test_placeholder_is_imported_as_marker(tmp_path):
    """Robustness check against a real 27 km LHC lattice found PLACEHOLDER
    (a reserved-space slot for hardware not yet installed/modelled, e.g.
    "Superconducting Cavity Place Holder" -- a real, named, positioned
    element, not an anonymous gap) had no `_switch_dict` entry and was
    silently dropped (311 of them in the LHC beam-1 sequence alone)."""
    source = tmp_path / "placeholder.madx"
    source.write_text(
        "ph: placeholder, l=0.5;\n"
        "line: sequence, l=1; ph, at=0.5; endsequence;\n"
    )

    elements = MadxLatticeImporter(
        source_file=str(source), sequence="line"
    ).create_laura_element_dictionary()

    assert elements["ph"].hardware_type == "Marker"
    assert elements["ph"].physical.length == pytest.approx(0.5)
