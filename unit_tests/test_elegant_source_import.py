import os
import shutil

import pytest

from laura.translator.converters.codes.elegant import ElegantLatticeImporter
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
