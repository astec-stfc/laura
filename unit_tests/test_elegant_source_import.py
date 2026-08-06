import os
import shutil

import pytest

from laura.translator.converters.codes.elegant import ElegantLatticeImporter


@pytest.mark.skipif(
    os.environ.get("LAURA_RUN_ELEGANT_TESTS") != "1"
    or shutil.which("elegant") is None,
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
