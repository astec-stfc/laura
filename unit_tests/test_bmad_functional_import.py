from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest

from laura.translator.converters.codes.bmad import (
    BmadLatticeImporter,
    BmadTaoInit,
    _native_keyword,
    _switch_dict,
    _taylor_matrices,
)
from laura.translator.converters import elements_Bmad, type_conversion_rules_Bmad
from laura.models.element import CombinedSolenoidQuadrupole, Marker, MatrixTransform
from laura.translator.converters.converter import translate_elements
from laura.models.elementList import ElementList, MachineLayout, SectionLattice
from laura.Exporters.YAML import export_as_yaml
from laura.Importers.YAML_Loader import read_YAML_Element_File


def test_bmad_conversion_rules_are_loaded():
    assert type_conversion_rules_Bmad["Dipole"] == "sbend"
    assert _switch_dict()["rbend"] == "Dipole"
    assert _switch_dict()["match"] == "MatrixTransform"
    assert _native_keyword("RFCavity", "frequency") == "RF_FREQUENCY"
    assert "bs_field" in elements_Bmad["sol_quad"]
    translated = translate_elements(
        [MatrixTransform(name="map", machine_area="test")]
    )["map"]
    assert translated._convertType_Bmad("MatrixTransform") == "taylor"
    assert translated._convertKeyword_Bmad("physical_length") == "l"


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


def test_bmad_parser_follows_call_file_statements(tmp_path):
    (tmp_path / "sub_files").mkdir()
    (tmp_path / "sub_files" / "definitions.bmad").write_text("quad_k1l = 0.3\n")
    source = tmp_path / "line.bmad"
    source.write_text(
        "call, file = sub_files/definitions.bmad\n"
        "q_live: quadrupole, l = 0.5, k1 := quad_k1l / 0.5\n"
    )
    importer = SimpleNamespace(
        lattice_file=str(source), deferred_parameters={}, functional_definitions={}
    )

    BmadLatticeImporter._read_functional_definitions(importer)

    assert importer.functional_definitions == {"quad_k1l": pytest.approx(0.3)}
    assert BmadLatticeImporter._symbol(importer, "q_live", "K1", 0.5) == "quad_k1l"


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


def test_bmad_additional_element_mappings():
    identity_taylor = {
        "data": [
            {
                "index": output,
                "ref": 0.0,
                "data": [
                    {
                        "coef": 1.0,
                        **{
                            f"exp{coordinate}": float(coordinate == output)
                            for coordinate in range(1, 7)
                        },
                    }
                ],
            }
            for output in range(1, 7)
        ]
    }
    identity_spin = [
        {"index": 0, "coef": 1.0, **{f"exp{i}": 0.0 for i in range(1, 7)}}
    ]
    names = [
        "h",
        "v",
        "sep",
        "match",
        "taylor",
        "sol_quad",
        "instrument",
        "pipe",
        "patch",
    ]
    importer = SimpleNamespace(
        names_numbered={1: {"LINE_1": names}},
        types={
            1: {
                "LINE_1": [
                    "HKicker",
                    "VKicker",
                    "ELSeparator",
                    "Match",
                    "Taylor",
                    "Sol_Quad",
                    "Instrument",
                    "Pipe",
                    "Patch",
                ]
            }
        },
        lengths={1: {"LINE_1": [0.1, 0.2, 1.0, 0.0, 0.0, 2.0, 0.3, 0.4, 0.0]}},
        spos={1: {"LINE_1": [0.1, 0.3, 1.3, 1.3, 1.3, 3.3, 3.6, 4.0, 4.0]}},
        params={
            1: {
                "LINE_1": [
                    {"KICK": 0.01},
                    {"KICK": -0.02},
                    {"E_FIELD": 5.0, "HKICK": 3.0, "VKICK": 4.0},
                    {"_VEC0": np.arange(6), "_MAT6": np.eye(6)},
                    {"_TAYLOR": identity_taylor, "_SPIN_TAYLOR": identity_spin},
                    {"K1": 0.3, "BS_FIELD": 0.4},
                    {},
                    {},
                    {},
                ]
            }
        },
        laura_elems={1: {"LINE_1": {}}},
        position_mode="s",
        deferred_parameters={},
        functional_definitions={},
    )
    importer._physical_common = BmadLatticeImporter._physical_common.__get__(importer)
    importer._symbol = BmadLatticeImporter._symbol.__get__(importer)

    with pytest.warns(UserWarning, match="element type 'Patch'"):
        elements = BmadLatticeImporter.create_laura_element_dictionary(importer, 1)[
            "LINE_1"
        ]

    assert elements["h"].magnetic.horizontal_kick == pytest.approx(0.01)
    assert elements["v"].magnetic.vertical_kick == pytest.approx(-0.02)
    assert elements["sep"].simulation.horizontal_field == pytest.approx(3.0)
    assert elements["sep"].simulation.vertical_field == pytest.approx(4.0)
    assert elements["match"].hardware_type == "MatrixTransform"
    np.testing.assert_array_equal(elements["match"].simulation.c_matrix, np.arange(6))
    np.testing.assert_array_equal(elements["match"].simulation.r_matrix, np.eye(6))
    np.testing.assert_array_equal(elements["taylor"].simulation.r_matrix, np.eye(6))
    assert elements["sol_quad"].hardware_type == "CombinedSolenoidQuadrupole"
    assert elements["sol_quad"].magnetic.KnL(1) == pytest.approx(0.6)
    assert elements["sol_quad"].magnetic.ks == pytest.approx(0.8)
    assert elements["instrument"].hardware_type == "Diagnostic"
    assert "pipe" not in elements


def test_bmad_taylor_reference_orbit_feeddown():
    sections = [
        {"index": output, "ref": 2.0 if output == 1 else 0.0, "data": []}
        for output in range(1, 7)
    ]
    sections[0]["data"] = [
        {"coef": 3.0, **{f"exp{i}": 0.0 for i in range(1, 7)}},
        {"coef": 4.0, "exp1": 1.0, **{f"exp{i}": 0.0 for i in range(2, 7)}},
        {"coef": 5.0, "exp1": 2.0, **{f"exp{i}": 0.0 for i in range(2, 7)}},
    ]
    c_matrix, r_matrix, t_matrix, u_matrix = _taylor_matrices({"data": sections})

    assert c_matrix[0] == pytest.approx(15.0)
    assert r_matrix[0, 0] == pytest.approx(-16.0)
    assert t_matrix[0, 0, 0] == pytest.approx(5.0)
    assert not u_matrix.any()


def test_bmad_cubic_taylor_reference_orbit_feeddown():
    sections = [
        {"index": output, "ref": 2.0 if output == 1 else 0.0, "data": []}
        for output in range(1, 7)
    ]
    sections[0]["data"] = [
        {"coef": 7.0, "exp1": 3.0, **{f"exp{i}": 0.0 for i in range(2, 7)}}
    ]

    c_matrix, r_matrix, t_matrix, u_matrix = _taylor_matrices({"data": sections})

    assert c_matrix[0] == pytest.approx(-56.0)
    assert r_matrix[0, 0] == pytest.approx(84.0)
    assert t_matrix[0, 0, 0] == pytest.approx(-42.0)
    assert u_matrix[0, 0, 0, 0] == pytest.approx(7.0)


def test_bmad_taylor_rejects_unrepresentable_terms():
    term = {
        "coef": 1.0,
        "exp1": 4.0,
        **{f"exp{i}": 0.0 for i in range(2, 7)},
    }
    taylor = {
        "data": [
            {"index": output, "ref": 0.0, "data": [term] if output == 1 else []}
            for output in range(1, 7)
        ]
    }
    with pytest.raises(ValueError, match="order 4"):
        _taylor_matrices(taylor)


def test_combined_solenoid_quadrupole_yaml_round_trip(tmp_path):
    element = CombinedSolenoidQuadrupole(
        name="sq",
        machine_area="test",
        magnetic={"length": 2.0, "k1l": 0.6, "solenoid_fields": {"S0L": 0.8}},
    )
    path = tmp_path / "sq.yaml"
    export_as_yaml(str(path), element)

    loaded = read_YAML_Element_File(str(path), validate=True)

    assert loaded.hardware_type == "CombinedSolenoidQuadrupole"
    assert loaded.magnetic.KnL(1) == pytest.approx(0.6)
    assert loaded.magnetic.ks == pytest.approx(0.8)


def test_spin_taylor_yaml_round_trip(tmp_path):
    term = {
        "index": 1,
        "coef": 0.25,
        **{f"exp{i}": float(i == 1) for i in range(1, 7)},
    }
    element = MatrixTransform(
        name="spin_map", machine_area="test", simulation={"spin_taylor": [term]}
    )
    path = tmp_path / "spin_map.yaml"
    export_as_yaml(str(path), element)

    loaded = read_YAML_Element_File(str(path), validate=True)

    assert loaded.simulation.spin_taylor == [term]
