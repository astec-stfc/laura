import os
import shutil

import pytest

from laura.translator.converters.codes.elegant import ElegantLatticeImporter
from laura.translator.converters.model import MachineModelTranslator
from laura.translator.utils.elegant.sdds_classes_APS import SDDS_Params
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
