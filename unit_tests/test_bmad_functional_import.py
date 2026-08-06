import pytest
from types import SimpleNamespace

from laura.translator.converters.codes.bmad import BmadLatticeImporter


def test_bmad_parser_retains_only_deferred_assignments(tmp_path):
    source = tmp_path / "line.bmad"
    source.write_text(
        "quad_k1l = 0.3\n"
        "fixed_k1 = 0.4\n"
        "q_live: quadrupole, l = 0.5, k1 := quad_k1l / 0.5\n"
        "q_fixed: quadrupole, l = 0.5, k1 = fixed_k1 / 0.5\n"
    )
    importer = SimpleNamespace(
        lattice_file=str(source), deferred_parameters={}, functional_definitions={}
    )

    BmadLatticeImporter._read_functional_definitions(importer)

    assert importer.functional_definitions == {"quad_k1l": pytest.approx(0.3)}
    assert BmadLatticeImporter._symbol(importer, "q_live", "K1", 0.5) == "quad_k1l"
    assert BmadLatticeImporter._symbol(importer, "q_fixed", "K1", 0.5) is None
