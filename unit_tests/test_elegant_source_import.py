import os
import shutil

import pytest

from laura.translator.converters.codes.elegant import (
    ElegantLatticeImporter,
    _expand_line_member,
)
from laura.translator.converters.model import MachineModelTranslator
from laura.translator.converters.section import SectionLatticeTranslator
from laura.translator.utils.elegant.sdds_classes_aps import SddsParams
import laura.models.element as laura_elements
from laura.models.element import Marker
from laura.models.element_list import ElementList, SectionLattice

_needs_elegant = pytest.mark.skipif(
    os.environ.get("LAURA_RUN_ELEGANT_TESTS") != "1" or shutil.which("elegant") is None,
    reason="set LAURA_RUN_ELEGANT_TESTS=1 to run external Elegant tests",
)


def _lte(tmp_path, text):
    """An ``ElegantLatticeImporter`` reading ``text`` as a .lte source file."""
    source = tmp_path / "line.lte"
    source.write_text(text)
    return ElegantLatticeImporter(source_file=str(source))


def _layout_elements(importer, name="machine"):
    """Every element of every section in the ``name`` layout."""
    for section in importer.create_layout(name=name).sections.values():
        yield from section.elements.elements.values()


def _saved_lattice(tmp_path, text):
    """``(params, elements)`` from ELEGANT's saved-lattice ``text``."""
    saved = tmp_path / "saved.lte"
    saved.write_text(text)
    params = ElegantLatticeImporter._saved_lattice_params(str(saved))
    reader = SddsParams(str(saved))
    reader.elegant_params = params
    elements, _ = reader.create_element_dictionary()
    return params, elements


def _convert_one(name, element_type):
    """The converted dictionary of one parameterless ``element_type``."""
    params = SddsParams("unused")
    params.elegant_params = {
        name: {
            "ElementType": [element_type],
            "ElementParameter": [],
            "ParameterValue": [],
            "ParameterValueString": [],
        }
    }
    converted, _ = params.create_element_dictionary("AREA")
    return converted[name]


def _stub_source(monkeypatch, element_names, offsets=None):
    """Serve each line of ``element_names`` as Markers at z = index, plus any
    ``offsets[(line, element)]``."""

    def section(name):
        names = element_names[name]
        elements = {
            element_name: Marker(
                name=element_name,
                machine_area=name,
                physical={
                    "middle": {
                        "z": index + (offsets or {}).get((name, element_name), 0)
                    }
                },
            )
            for index, element_name in enumerate(names)
        }
        return SectionLattice(
            name=name, order=names, elements=ElementList(elements=elements)
        )

    monkeypatch.setattr(ElegantLatticeImporter, "_prepare_source", lambda self: None)
    monkeypatch.setattr(
        ElegantLatticeImporter, "_source_section", lambda self, name: section(name)
    )


@_needs_elegant
def test_bend_fringe_integrals_resolve_from_fint_and_fint1_fint2(tmp_path):
    """ELEGANT writes FINT1/FINT2 as -1 when they were never set, meaning "use
    FINT"; taken literally they import as a negative fringe integral."""
    importer = _lte(
        tmp_path,
        "b1: csbend, l=0.5, angle=0.1, hgap=0.02, fint=0.3\n"
        "b2: csbend, l=0.5, angle=0.1, hgap=0.02, fint1=0.3, fint2=0.5\n"
        "machine: line=(b1,b2)\n",
    )
    bends = {
        element.name: element.magnetic
        for element in _layout_elements(importer)
        if element.hardware_type == "Dipole"
    }

    assert bends["B1"].edge_field_integral_entrance == pytest.approx(0.3)
    assert bends["B1"].edge_field_integral_exit == pytest.approx(0.3)
    assert bends["B2"].edge_field_integral_entrance == pytest.approx(0.3)
    assert bends["B2"].edge_field_integral_exit == pytest.approx(0.5)
    assert bends["B1"].gap == pytest.approx(0.04), "HGAP is a half gap"


@_needs_elegant
def test_edge_order_is_imported_only_when_the_lattice_sets_it(tmp_path):
    """ELEGANT's parameter dump gives every bend its default EDGE_ORDER = 1;
    importing that would pin first-order edges no other code shares."""
    importer = _lte(
        tmp_path,
        "b1: csbend, l=0.5, angle=0.1\n"
        "b2: csbend, l=0.5, angle=0.1, edge_order=1\n"
        "machine: line=(b1,b2,b1)\n",
    )
    orders = {
        element.name: element.simulation.edge_order
        for element in _layout_elements(importer)
        if element.hardware_type == "Dipole"
    }

    assert orders == {"B1.1": None, "B2": 1, "B1.2": None}


@_needs_elegant
def test_imported_hardware_type_is_the_registry_key_not_the_class_name(tmp_path):
    """``hardware_type`` is the wire format; class renames left the keys alone."""
    importer = _lte(
        tmp_path,
        "k1: kicker, l=0.1\n" 'w1: watch, filename="%s.w1"\n' "machine: line=(k1,w1)\n",
    )
    types = {
        element.name: element.hardware_type for element in _layout_elements(importer)
    }
    assert types["K1"] == "Combined_Corrector"
    assert types["W1"] == "Marker"


@_needs_elegant
def test_source_import_builds_sections_and_retains_store(tmp_path):
    importer = _lte(
        tmp_path,
        "% 0.3 sto quad_k1l\n"
        'q: quad, l=0.5, k1="quad_k1l 0.5 /"\n'
        "m: mark\n"
        "section_a: line=(q,m)\n"
        "section_b: line=(m,q)\n"
        "machine: line=(section_a,section_b)\n",
    )
    layout = importer.create_layout(name="machine")

    assert list(layout.sections) == ["section_a", "section_b"]
    assert layout.functional_definitions == {"quad_k1l": pytest.approx(0.3)}
    for section in layout.sections.values():
        quadrupole = next(
            element
            for element in section.elements.elements.values()
            if element.hardware_type == "Quadrupole"
        )
        assert quadrupole.magnetic.multipoles.K1L.normal == "quad_k1l"


@_needs_elegant
def test_source_import_expands_root_line_shorthand(tmp_path):
    importer = _lte(
        tmp_path,
        "Q1: QUAD,L=0.5,K1=2\n"
        "D1: DRIF,L=1.0\n"
        "CELL: LINE=(Q1,D1)\n"
        "RING: LINE=(3*CELL,-CELL)\n",
    )
    layout = importer.create_layout(name="RING")

    section = next(iter(layout.sections.values()))
    types = [
        section.elements.elements[name].hardware_type for name in section.order
    ]
    assert types == [
        "Quadrupole", "Drift", "Quadrupole", "Drift",
        "Quadrupole", "Drift", "Drift", "Quadrupole",
    ]


def test_saved_lattice_parser_expands_repeated_elements(tmp_path):
    params, elements = _saved_lattice(
        tmp_path,
        "Q: QUAD,L=0.5,K1=2\n"
        "K: RFTM110,PHASE=90,FREQUENCY=3e9,VOLTAGE=1e6\n"
        "S: LINE=(Q,K,Q)\n"
        'USE,"S"\n',
    )

    assert list(params) == ["Q.1", "K", "Q.2"]
    assert params["K"]["ElementType"] == ["RFTM110"]
    assert elements["K"]["hardware_type"] == "RFDeflectingCavity"


def test_twiss_element_imports_beta_alpha_eta_and_from_beam(tmp_path):
    params, elements = _saved_lattice(
        tmp_path,
        "Q: QUAD,L=0.5,K1=2\n"
        "T: TWISS,BETAX=9.42,ALPHAX=-0.66,BETAY=22.19,ALPHAY=1.51,"
        "ETAX=0.1,ETAY=0.2,ETAXP=0.01,ETAYP=0.02,FROM_BEAM=0\n"
        "S: LINE=(T,Q)\n"
        'USE,"S"\n',
    )
    assert params["T"]["ElementType"] == ["TWISS"]

    assert elements["T"]["hardware_type"] == "TwissMatch"
    twiss = laura_elements.TwissMatch(**elements["T"])
    assert twiss.simulation.beta_x == pytest.approx(9.42)
    assert twiss.simulation.beta_y == pytest.approx(22.19)
    assert twiss.simulation.alpha_x == pytest.approx(-0.66)
    assert twiss.simulation.alpha_y == pytest.approx(1.51)
    assert twiss.simulation.eta_x == pytest.approx(0.1)
    assert twiss.simulation.eta_y == pytest.approx(0.2)
    assert twiss.simulation.eta_xp == pytest.approx(0.01)
    assert twiss.simulation.eta_yp == pytest.approx(0.02)
    assert twiss.simulation.from_beam is False


def test_machine_formatter_does_not_prefix_element_with_comma():
    assert SectionLatticeTranslator.format_string(None, "M: mark;\n") == "M: mark;\n"


def test_create_machine_model_uses_top_level_lines_and_minimum_section_length(
    monkeypatch,
):
    importer = ElegantLatticeImporter(source_file="unused.lte")
    importer._source_roots = ["layout_short", "layout_a", "layout_b"]
    importer._source_lines = {
        "layout_short": ["c1", "c2", "c3"],
        "short": ["a1", "a2"],
        "long_a": ["a3", "a4", "a5", "a6", "a7"],
        "long_b": ["a1", "b2", "b3", "b4", "b5"],
        "layout_a": ["short", "long_a"],
        "layout_b": ["long_b"],
    }

    _stub_source(
        monkeypatch,
        {
            "layout_short": ["c1", "c2", "c3"],
            "layout_a": [f"a{i}" for i in range(1, 8)],
            "layout_b": ["a1", "b2", "b3", "b4", "b5"],
        },
    )

    with pytest.warns(UserWarning, match="layout_short"):
        model = importer.create_machine_model()

    assert list(model.lattices) == ["layout_a", "layout_b"]
    assert model.lattices["layout_a"].names == ["long_a"]
    assert model.lattices["layout_b"].names == ["long_b"]
    assert model.sections["long_a"].order == [f"a{i}" for i in range(1, 8)]
    assert model.sections["long_b"].order[0] == "a1"
    assert len(model.elements) == 11
    assert importer._source_section_blocks("layout_a", 6) == [("layout_a", 7)]


def test_create_machine_model_renames_colliding_elements_at_different_placements(
    monkeypatch,
):
    importer = ElegantLatticeImporter(source_file="unused.lte")
    importer._source_roots = ["layout_a", "layout_b"]
    importer._source_lines = {
        "layout_a": ["shared", "a2", "a3"],
        "layout_b": ["shared", "b2", "b3"],
    }

    _stub_source(
        monkeypatch,
        {"layout_a": ["shared", "a2", "a3"], "layout_b": ["shared", "b2", "b3"]},
        offsets={("layout_b", "shared"): 10},
    )

    model = importer.create_machine_model(min_section_length=1)

    assert model.sections["layout_a"].order[0] == "shared"
    assert model.sections["layout_b"].order[0] == "shared__layout_b"
    assert model.elements["shared"].physical.middle.z == pytest.approx(0)
    assert model.elements["shared__layout_b"].physical.middle.z == pytest.approx(10)


def test_expand_line_member_handles_repeat_count_and_reversal_shorthand():
    # Ground truth from a real `elegant` run with `output_seq=2` on
    # `CELL: LINE=(Q1,D1)` / `RING: LINE=(3*CELL,-CELL)`.
    lookup = {"cell": ("CELL", "Q1,D1")}
    sequence = [
        element
        for member in "3*CELL,-CELL".split(",")
        for element in _expand_line_member(member, lookup)
    ]
    assert sequence == ["Q1", "D1", "Q1", "D1", "Q1", "D1", "D1", "Q1"]

def test_elegant_include_inlines_nested_relative_files(tmp_path):
    from laura.translator.converters.codes.elegant import _read_lattice_text

    sub = tmp_path / "sub"
    sub.mkdir()
    (tmp_path / "definitions.lte").write_text("q: quadrupole, l=1\n")
    (sub / "section.lte").write_text(
        '#include "../definitions.lte"\nsec: line=(q)\n'
    )
    source = tmp_path / "main.lte"
    source.write_text('#include "sub/section.lte"\nmain: line=(sec)\n')

    text = _read_lattice_text(source)

    assert "q: quadrupole" in text
    assert "sec: line=(q)" in text
    assert "main: line=(sec)" in text


def test_elegant_moni_maps_to_a_bpm_and_uses_machine_area():
    converted = _convert_one("M", "MONI")

    assert converted["hardware_type"] == "Beam_Position_Monitor"
    assert converted["machine_area"] == "AREA"


def test_elegant_watch_maps_back_to_marker():
    """``Marker`` exports as ``watch`` (a BPM as ``moni``), so ``watch`` maps back."""
    assert _convert_one("W", "WATCH")["hardware_type"] == "Marker"


def test_only_a_watch_point_is_given_an_output_filename():
    """ELEGANT's MONI takes no FILENAME (the .lte won't parse); only ``watch`` does."""
    from laura.translator.converters.converter import translate_elements

    bpm = laura_elements.BeamPositionMonitor(
        name="BPM1", machine_area="AREA", physical={"length": 0.0}
    )
    marker = laura_elements.Marker(name="MARK1", machine_area="AREA")
    translated = translate_elements([bpm, marker])

    assert "moni" in translated["BPM1"].to_elegant()
    assert "filename" not in translated["BPM1"].to_elegant()
    assert "filename" in translated["MARK1"].to_elegant()


def test_elegant_transverse_and_distinct_wakes_are_not_lost(tmp_path, monkeypatch):
    data = {
        "TR": {
            "hardware_type": "RFCavity",
            "name": "TR",
            "machine_area": "AREA",
            "simulation": {"trwakefile": "tr.sdds", "t_column": "t", "wx_column": "wx"},
        },
        "BOTH": {
            "hardware_type": "RFCavity",
            "name": "BOTH",
            "machine_area": "AREA",
            "simulation": {"zwakefile": "z.sdds", "trwakefile": "tr.sdds"},
        },
    }
    filenames = {
        "TR": {"trwakefile": "tr.sdds"},
        "BOTH": {"zwakefile": "z.sdds", "trwakefile": "tr.sdds"},
    }

    monkeypatch.setattr(
        SddsParams,
        "create_element_dictionary",
        lambda self, machine_area="Lattice": (data, filenames),
    )
    importer = ElegantLatticeImporter(
        params_file=str(tmp_path / "params.sdds"), machine_area="AREA"
    )

    with pytest.warns(UserWarning, match="separate longitudinal and transverse"):
        converted, _ = importer.create_element_dictionary()

    wake = converted["TR"]["simulation"]["wakefield_definition"]
    assert wake.field_type == "TransverseWake"
    assert wake.filename == str((tmp_path / "tr.sdds").resolve())
    assert converted["BOTH"]["simulation"]["zwakefile"] == "z.sdds"
    assert converted["BOTH"]["simulation"]["trwakefile"] == "tr.sdds"


@_needs_elegant
def test_bare_per_metre_strength_symbol_is_integrated(tmp_path):
    """``k1="kx"`` is per metre; LAURA's K1L needs ``kx * L``, and a symbol
    two lengths share cannot hold both, so it imports as numbers."""
    importer = _lte(
        tmp_path,
        "% 0.4 sto kx\n"
        "% 0.2 sto kw\n"
        'q1: kquad, l=0.5, k1="kx"\n'
        'q4: kquad, l=0.5, k1="kw"\n'
        'q5: kquad, l=0.25, k1="kw"\n'
        "machine: line=(q1,q4,q5)\n",
    )
    elements = importer.create_section()["machine"].elements.elements

    assert elements["Q1"].magnetic.multipoles.K1L.normal == "kx"
    assert importer.functional_definitions["kx"] == pytest.approx(0.2)
    assert elements["Q4"].magnetic.multipoles.K1L.normal == pytest.approx(0.1)
    assert elements["Q5"].magnetic.multipoles.K1L.normal == pytest.approx(0.05)
