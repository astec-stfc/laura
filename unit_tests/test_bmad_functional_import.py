import pytest
from pathlib import Path
from types import SimpleNamespace

from laura.translator.converters.codes.bmad import BmadLatticeImporter, BmadTaoInit
from laura.models.element import Marker
from laura.models.elementList import ElementList, MachineLayout, SectionLattice


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


def test_minimal_tao_init(tmp_path):
    output = tmp_path / "tao.init"

    result = BmadTaoInit(
        lattice_file="../lattices/ring.bmad", lines=["injection", "collision"]
    ).write(output)

    assert result == output
    assert output.read_text() == (
        "&tao_design_lattice\n"
        "  n_universes = 2\n"
        "  design_lattice(1)%file = '../lattices/ring.bmad@injection'\n"
        "  design_lattice(2)%file = '../lattices/ring.bmad@collision'\n"
        "/\n"
    )


def test_lattice_importer_generates_tao_init(tmp_path):
    lattice = tmp_path / "ring.bmad"
    lattice.write_text("use, injection\n")
    importer = SimpleNamespace(
        tao_init=None,
        lattice_file=str(lattice),
        lines=["injection"],
        _generated_tao_init=None,
    )

    generated = Path(BmadLatticeImporter._tao_init_path(importer))

    assert generated.read_text() == (
        "&tao_design_lattice\n"
        "  n_universes = 1\n"
        f"  design_lattice(1)%file = '{lattice.resolve()}@injection'\n"
        "/\n"
    )


def test_create_machine_model_uses_universes_and_reuses_elements(tmp_path):
    init = tmp_path / "floorplan.init"
    init.write_text(
        'design_lattice(1)%file = "../Lines/5.bmad"\n'
        'design_lattice(2)%file = "../Lines/4.bmad"\n'
        'design_lattice(3)%file = "../Lines/short.bmad"\n'
    )
    importer = SimpleNamespace(
        tao_init=str(init),
        lattice_file=None,
        branches={1: ["LINE1_1"], 2: ["LINE1_2"], 3: ["LINE1_3"]},
        functional_definitions={},
    )

    names = {
        1: ["shared", "shifted", "a3", "a4", "a5"],
        2: ["shared", "shifted", "b3", "b4", "b5"],
        3: ["c1", "c2", "c3"],
    }

    def create_layout(universe, name=None):
        elements = {
            element_name: Marker(
                name=element_name,
                machine_area=name,
                physical={
                    "middle": {
                        "z": index
                        + (10 if universe == 2 and element_name == "shifted" else 0)
                    }
                },
            )
            for index, element_name in enumerate(names[universe])
        }
        section_name = f"LINE1_{universe}"
        section = SectionLattice(
            name=section_name,
            order=list(elements),
            elements=ElementList(elements=elements),
        )
        return MachineLayout(name=name, sections={section_name: section})

    importer.create_layout = create_layout

    with pytest.warns(UserWarning, match="short/LINE1_3"):
        model = BmadLatticeImporter.create_machine_model(importer)

    assert list(model.lattices) == ["5", "4"]
    assert model.lattices["5"].names == ["LINE1_1"]
    assert model.lattices["4"].names == ["LINE1_2"]
    assert model.sections["LINE1_2"].order[:2] == ["shared", "shifted__4"]
    assert len(model.elements) == 9
