import os
import shutil

import pytest

from laura.translator.converters.codes.elegant import (
    ElegantLatticeImporter,
    _expand_line_member,
)
from laura.translator.converters.model import MachineModelTranslator
from laura.translator.utils.elegant.sdds_classes_APS import SDDS_Params
import laura.models.element as LAURA_elements
from laura.models.element import Marker
from laura.models.elementList import ElementList, SectionLattice


@pytest.mark.skipif(
    os.environ.get("LAURA_RUN_ELEGANT_TESTS") != "1" or shutil.which("elegant") is None,
    reason="set LAURA_RUN_ELEGANT_TESTS=1 to run external Elegant tests",
)
def test_source_import_builds_sections_and_retains_store(tmp_path):
    source = tmp_path / "line.lte"
    source.write_text(
        "% 0.3 sto quad_k1l\n"
        'q: quad, l=0.5, k1="quad_k1l 0.5 /"\n'
        "m: mark\n"
        "section_a: line=(q,m)\n"
        "section_b: line=(m,q)\n"
        "machine: line=(section_a,section_b)\n"
    )

    importer = ElegantLatticeImporter(source_file=str(source))
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


@pytest.mark.skipif(
    os.environ.get("LAURA_RUN_ELEGANT_TESTS") != "1" or shutil.which("elegant") is None,
    reason="set LAURA_RUN_ELEGANT_TESTS=1 to run external Elegant tests",
)
def test_source_import_expands_root_line_shorthand(tmp_path):
    # A root LINE built purely from N*/- shorthand on a single sub-line
    # must stay one section, not be split into per-name "sections" the way
    # `machine: line=(section_a,section_b)` is above -- splitting on the
    # bare sub-line name would silently drop the repeat count/reversal.
    source = tmp_path / "shorthand.lte"
    source.write_text(
        "Q1: QUAD,L=0.5,K1=2\n"
        "D1: DRIF,L=1.0\n"
        "CELL: LINE=(Q1,D1)\n"
        "RING: LINE=(3*CELL,-CELL)\n"
    )

    importer = ElegantLatticeImporter(source_file=str(source))
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
    saved = tmp_path / "saved.lte"
    saved.write_text(
        "Q: QUAD,L=0.5,K1=2\n"
        "K: RFTM110,PHASE=90,FREQUENCY=3e9,VOLTAGE=1e6\n"
        "S: LINE=(Q,K,Q)\n"
        'USE,"S"\n'
    )

    params = ElegantLatticeImporter._saved_lattice_params(str(saved))

    assert list(params) == ["Q.1", "K", "Q.2"]
    assert params["K"]["ElementType"] == ["RFTM110"]
    reader = SDDS_Params(str(saved))
    reader.elegantParams = params
    elements, _ = reader.create_element_dictionary()
    assert elements["K"]["hardware_type"] == "RFDeflectingCavity"


def test_twiss_element_imports_beta_alpha_eta_and_from_beam(tmp_path):
    """Test import of ELEGANT's native TWISS element."""
    saved = tmp_path / "saved.lte"
    saved.write_text(
        "Q: QUAD,L=0.5,K1=2\n"
        "T: TWISS,BETAX=9.42,ALPHAX=-0.66,BETAY=22.19,ALPHAY=1.51,"
        "ETAX=0.1,ETAY=0.2,ETAXP=0.01,ETAYP=0.02,FROM_BEAM=0\n"
        "S: LINE=(T,Q)\n"
        'USE,"S"\n'
    )

    params = ElegantLatticeImporter._saved_lattice_params(str(saved))
    assert params["T"]["ElementType"] == ["TWISS"]
    reader = SDDS_Params(str(saved))
    reader.elegantParams = params
    elements, _ = reader.create_element_dictionary()

    assert elements["T"]["hardware_type"] == "TwissMatch"
    twiss = LAURA_elements.TwissMatch(**elements["T"])
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
    assert MachineModelTranslator.format_string(None, "M: mark;\n") == "M: mark;\n"


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

    def section(name):
        element_names = {
            "layout_short": ["c1", "c2", "c3"],
            "layout_a": [f"a{i}" for i in range(1, 8)],
            "layout_b": ["a1", "b2", "b3", "b4", "b5"],
        }[name]
        elements = {
            element_name: Marker(
                name=element_name,
                machine_area=name,
                physical={"middle": {"z": index}},
            )
            for index, element_name in enumerate(element_names)
        }
        return SectionLattice(
            name=name,
            order=element_names,
            elements=ElementList(elements=elements),
        )

    monkeypatch.setattr(ElegantLatticeImporter, "_prepare_source", lambda self: None)
    monkeypatch.setattr(ElegantLatticeImporter, "_source_section", lambda self, name: section(name))

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

    def section(name):
        element_names = {
            "layout_a": ["shared", "a2", "a3"],
            "layout_b": ["shared", "b2", "b3"],
        }[name]
        elements = {
            element_name: Marker(
                name=element_name,
                machine_area=name,
                physical={
                    "middle": {
                        "z": index
                        + (10 if name == "layout_b" and element_name == "shared" else 0)
                    }
                },
            )
            for index, element_name in enumerate(element_names)
        }
        return SectionLattice(
            name=name,
            order=element_names,
            elements=ElementList(elements=elements),
        )

    monkeypatch.setattr(ElegantLatticeImporter, "_prepare_source", lambda self: None)
    monkeypatch.setattr(ElegantLatticeImporter, "_source_section", lambda self, name: section(name))

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


def test_elegant_moni_maps_to_diagnostic_and_uses_machine_area():
    from laura.translator.utils.elegant.sdds_classes_APS import SDDS_Params

    params = SDDS_Params("unused")
    params.elegantParams = {
        "M": {
            "ElementType": ["MONI"],
            "ElementParameter": [],
            "ParameterValue": [],
            "ParameterValueString": [],
        }
    }

    converted, _ = params.create_element_dictionary("AREA")

    assert converted["M"]["hardware_type"] == "Diagnostic"
    assert converted["M"]["machine_area"] == "AREA"


def test_elegant_transverse_and_distinct_wakes_are_not_lost(tmp_path, monkeypatch):
    from laura.translator.utils.elegant.sdds_classes_APS import SDDS_Params

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
        SDDS_Params,
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
