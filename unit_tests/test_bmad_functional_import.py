import inspect
import warnings
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest

from laura.exporters.yaml_exporter import export_as_yaml
from laura.importers.yaml_loader import read_yaml_element_file
from laura.models.element import CombinedSolenoidQuadrupole, Marker, MatrixTransform
from laura.models.element_list import ElementList, MachineLayout, SectionLattice
from laura.translator.converters import elements_bmad, type_conversion_rules_bmad
from laura.translator.converters.codes.bmad import (
    BmadLatticeImporter,
    BmadTaoInit,
    _native_keyword,
    _switch_dict,
    _taylor_matrices,
)
from laura.translator.converters.converter import translate_elements
from laura.translator.utils.bmad import (
    bmad_floor_angles_from_matrix,
    bmad_floor_angles_to_laura,
    bmad_floor_rotation_matrix,
)
from laura.utils.rotation_matrix import euler_angles_to_rotation_matrix


def _bind_importer_methods(importer):
    for name, member in vars(BmadLatticeImporter).items():
        if inspect.isfunction(member) and not hasattr(importer, name):
            setattr(importer, name, member.__get__(importer))


def _line_importer(names, types, lengths, spos, params, position_mode="s", **extra):
    importer = SimpleNamespace(
        names_numbered={1: {"LINE_1": names}},
        types={1: {"LINE_1": types}},
        lengths={1: {"LINE_1": lengths}},
        spos={1: {"LINE_1": spos}},
        params={1: {"LINE_1": params}},
        laura_elems={1: {"LINE_1": {}}},
        position_mode=position_mode,
        deferred_parameters={},
        functional_definitions={},
        super_lord_children={},
        **extra,
    )
    _bind_importer_methods(importer)
    return importer


def _convert(importer):
    return BmadLatticeImporter.create_laura_element_dictionary(importer, 1)["LINE_1"]


def _parse(source, text):
    source.write_text(text)
    importer = SimpleNamespace(
        lattice_file=str(source), deferred_parameters={}, functional_definitions={}
    )
    BmadLatticeImporter._read_functional_definitions(importer)
    return importer


def test_bmad_conversion_rules_are_loaded():
    assert type_conversion_rules_bmad["Dipole"] == "sbend"
    assert _switch_dict()["rbend"] == "Dipole"
    assert _switch_dict()["match"] == "MatrixTransform"
    assert _native_keyword("RFCavity", "frequency") == "RF_FREQUENCY"
    assert "ks" in elements_bmad["sol_quad"]
    translated = translate_elements([MatrixTransform(name="map", machine_area="test")])[
        "map"
    ]
    assert translated._convert_type_bmad("MatrixTransform") == "taylor"
    assert translated._convert_keyword_bmad("physical_length") == "l"


def test_bmad_parser_retains_only_deferred_assignments(tmp_path):
    importer = _parse(
        tmp_path / "line.bmad",
        "quad_k1l = 0.3\n"
        "fixed_k1 = 0.4\n"
        "q_live: quadrupole, l = 0.5, k1 := quad_k1l / 0.5\n"
        "q_fixed: quadrupole, l = 0.5, k1 = fixed_k1 / 0.5\n",
    )

    assert importer.functional_definitions == {"quad_k1l": pytest.approx(0.3)}
    assert BmadLatticeImporter._symbol(importer, "q_live", "K1", 0.5) == "quad_k1l"
    assert BmadLatticeImporter._symbol(importer, "q_fixed", "K1", 0.5) is None


def test_bmad_parser_retains_deferred_update_after_definition(tmp_path):
    importer = _parse(
        tmp_path / "line.bmad",
        "ky = 0.3\nq: quadrupole, l = 0.5\nln: line = (q)\nuse, ln\nq[k1] := ky\n",
    )

    assert importer.deferred_parameters == {"q": {"K1": "ky"}}
    assert importer.functional_definitions == {"ky": pytest.approx(0.3)}


def test_bmad_bare_per_metre_strength_symbol_is_integrated():
    """``k1 := kx`` is per metre; a symbol two lengths share stays numeric."""
    importer = SimpleNamespace(
        functional_definitions={"kx": 0.4, "kw": 0.2},
        deferred_parameters={"q1": {"K1": "kx"}, "q4": {"K1": "kw"}, "q5": {"K1": "kw"}},
        names_numbered={1: {"b": ["Q1", "Q4", "Q5"]}},
        lengths={1: {"b": [0.5, 0.5, 0.25]}},
    )

    BmadLatticeImporter._rescale_strength_symbols(importer, 1)

    assert importer.functional_definitions == {"kx": pytest.approx(0.2), "kw": 0.2}
    assert BmadLatticeImporter._symbol(importer, "Q1", "K1", 0.5) == "kx"
    assert BmadLatticeImporter._symbol(importer, "Q4", "K1", 0.5) is None


def test_bmad_parser_follows_call_file_statements(tmp_path):
    (tmp_path / "sub_files").mkdir()
    (tmp_path / "sub_files" / "definitions.bmad").write_text("quad_k1l = 0.3\n")
    importer = _parse(
        tmp_path / "line.bmad",
        "call, file = sub_files/definitions.bmad\n"
        "q_live: quadrupole, l = 0.5, k1 := quad_k1l / 0.5\n",
    )

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


def test_create_machine_model_keeps_section_and_layout_metadata(tmp_path):
    """MachineModel rebuilds sections from bare names; Tao metadata is reapplied."""
    init = tmp_path / "ring.init"
    init.write_text('design_lattice(1)%file = "../Lines/ring.bmad"\n')
    importer = SimpleNamespace(
        tao_init=str(init),
        lattice_file=None,
        branches={1: ["RING_1"]},
        functional_definitions={},
    )

    def create_layout(universe, name=None):
        elements = {
            element_name: Marker(
                name=element_name,
                machine_area=name,
                physical={"middle": {"z": index}},
            )
            for index, element_name in enumerate(["e1", "e2", "e3", "e4", "e5"])
        }
        section = SectionLattice(
            name="RING_1",
            order=list(elements),
            elements=ElementList(elements=elements),
            geometry="closed",
            reference_energy=6.0e6,
        )
        return MachineLayout(
            name=name, sections={"RING_1": section}, particle="Electron"
        )

    importer.create_layout = create_layout

    model = BmadLatticeImporter.create_machine_model(importer)

    assert model.sections["RING_1"].geometry == "closed"
    assert model.sections["RING_1"].reference_energy == pytest.approx(6.0e6)
    assert model.lattices["ring"].particle == "Electron"
    assert model.particle == "Electron"


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
    identity_spin = [{"index": 0, "coef": 1.0, **{f"exp{i}": 0.0 for i in range(1, 7)}}]
    elements = _convert(
        _line_importer(
            "h v sep match taylor sol_quad instrument pipe patch".split(),
            [
                "HKicker",
                "VKicker",
                "ELSeparator",
                "Match",
                "Taylor",
                "Sol_Quad",
                "Instrument",
                "Pipe",
                "Patch",
            ],
            [0.1, 0.2, 1.0, 0.0, 0.0, 2.0, 0.3, 0.4, 0.0],
            [0.1, 0.3, 1.3, 1.3, 1.3, 3.3, 3.6, 4.0, 4.0],
            [
                {"KICK": 0.01},
                {"KICK": -0.02},
                {"E_FIELD": 5.0, "HKICK": 3.0, "VKICK": 4.0},
                {"_VEC0": np.arange(6), "_MAT6": np.eye(6)},
                {"_TAYLOR": identity_taylor, "_SPIN_TAYLOR": identity_spin},
                {"K1": 0.3, "KS": 0.4},
                {},
                {},
                {},
            ],
        )
    )

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
    assert elements["pipe"].hardware_type == "Drift"
    assert elements["pipe"].physical.length == pytest.approx(0.4)
    assert "patch" not in elements


def test_bmad_fixers_and_empty_multipoles_are_kept_as_markers():
    """Inactive fixer (no ``_ACTIVE``): its stored Twiss isn't this branch's."""
    importer = _line_importer(
        ["fixer", "bare_multipole", "quad_multipole"],
        ["Fixer", "Multipole", "Multipole"],
        [0.0, 0.0, 0.0],
        [1.5, 2.5, 3.5],
        [
            {"BETA_A_STORED": 1.4, "ALPHA_A_STORED": -2.6},
            {"_MULTIPOLES": {"multipoles_on": True, "data": []}},
            {
                "_MULTIPOLES": {
                    "multipoles_on": True,
                    "data": [{"index": 1, "Bn": 0.25, "An": 0.0}],
                }
            },
        ],
        _declared_poles={},
    )

    with pytest.warns(UserWarning) as record:
        elements = _convert(importer)

    messages = [str(warning.message) for warning in record]
    assert any(
        "Fixer 'fixer' is not the active fixer" in m and "Marker" in m for m in messages
    )
    assert any(
        "'bare_multipole' has no multipole content" in m and "Marker" in m
        for m in messages
    )

    assert elements["fixer"].hardware_type == "Marker"
    assert elements["fixer"].physical.s == pytest.approx(1.5)
    assert elements["bare_multipole"].hardware_type == "Marker"
    assert elements["bare_multipole"].physical.s == pytest.approx(2.5)
    assert elements["quad_multipole"].hardware_type == "Quadrupole"
    assert elements["quad_multipole"].magnetic.KnL(1) == pytest.approx(0.25)


def test_bmad_floor_position_mode_places_elements_at_tao_coordinates():
    """``s`` and ``middle`` are mutually exclusive in the schema."""
    importer = SimpleNamespace(
        lengths={1: {"L": [2.0]}},
        spos={1: {"L": [10.0]}},
        params={1: {"L": [{"_FLOOR": {"Reference": [1.0, 2.0, 3.0, 0.4, 0.5, 0.6]}}]}},
        position_mode="floor",
    )

    physical = BmadLatticeImporter._physical_common(importer, 1, "L", 0)

    assert physical["middle"] == {"x": 1.0, "y": 2.0, "z": 3.0}
    rotation = physical["global_rotation"]
    assert rotation["phi"] == pytest.approx(-0.145078089699)
    assert rotation["psi"] == pytest.approx(0.749558154311)
    assert rotation["theta"] == pytest.approx(-0.614800048321)
    np.testing.assert_allclose(
        euler_angles_to_rotation_matrix(
            rotation["theta"], rotation["phi"], rotation["psi"]
        ),
        bmad_floor_rotation_matrix(0.4, 0.5, 0.6),
        atol=1e-14,
    )
    assert "s" not in physical and "s_point" not in physical

    importer.position_mode = "s"
    physical = BmadLatticeImporter._physical_common(importer, 1, "L", 0)

    assert physical["s"] == 10.0
    assert physical["s_point"] == "end"
    assert "middle" not in physical


def test_bmad_floor_mode_restores_bmad_arc_length():
    """Bmad's s is written back under ``_syncing`` so ``middle`` doesn't move."""
    element = Marker(name="q", machine_area="test", physical={"middle": {"z": 5.0}})
    element.physical._trajectory = SimpleNamespace(
        xyz_at_s=lambda s: {"x": 999.0, "y": 999.0, "z": 999.0},
        s_at_xyz=lambda p: 0.0,
    )
    importer = SimpleNamespace(
        names_numbered={1: {"L": ["q"]}},
        lengths={1: {"L": [2.0]}},
        spos={1: {"L": [10.0]}},
    )

    BmadLatticeImporter._restore_arc_length(importer, 1, "L", {"q": element})

    assert element.physical.s == pytest.approx(9.0)  # Tao s is at the exit
    assert element.physical.s_point == "middle"
    assert element.physical.middle.z == pytest.approx(5.0)


def _patch_importer(position_mode):
    return _line_importer(
        ["inert_patch", "noise_patch", "sliding_patch"],
        ["Patch", "Patch", "Patch"],
        [1.677, 0.0, 0.0],
        [1.677, 1.677, 1.677],
        [
            # Non-zero, but both are drift-equivalent or derived from L.
            {"Z_OFFSET": 1.677, "DELTA_REF_TIME": 5.59e-09},
            # Bmad resolves tilt numerically; this is an untilted patch.
            {"TILT": 1.17879544139e-20},
            {"Y_OFFSET": 0.003, "X_PITCH": 0.0012},
        ],
        position_mode,
    )


@pytest.mark.parametrize("position_mode", ["s", "floor"])
def test_bmad_patch_warns_only_where_the_frame_shift_is_actually_lost(position_mode):
    """Under ``"floor"`` to_bmad() rebuilds the patch from survey frames: lossless."""
    importer = _patch_importer(position_mode)

    with warnings.catch_warnings(record=True) as record:
        warnings.simplefilter("always")
        BmadLatticeImporter.create_laura_element_dictionary(importer, 1)

    messages = [str(warning.message) for warning in record]
    assert not any("inert_patch" in message for message in messages)
    assert not any("noise_patch" in message for message in messages)
    moved = [m for m in messages if "sliding_patch" in m]
    if position_mode == "floor":
        assert moved == []
    else:
        assert len(moved) == 1
        assert "moves the reference frame" in moved[0]
        assert "Y_OFFSET=0.003" in moved[0] and "X_PITCH=0.0012" in moved[0]
        assert "placed as though the patch were absent" in moved[0]
    assert not any("Could not parse" in message for message in messages)


@pytest.mark.parametrize("position_mode", ["s", "floor"])
def test_bmad_patch_reference_energy_jump_warns_in_every_mode(position_mode):
    """Floor coordinates carry no reference momentum, so no mode recovers it."""
    importer = _line_importer(
        ["energy_patch"],
        ["Patch"],
        [0.0],
        [4.2],
        [{"DELTA_E_REF": -1.35e8}],
        position_mode,
    )

    with pytest.warns(UserWarning) as record:
        BmadLatticeImporter.create_laura_element_dictionary(importer, 1)

    messages = [m for m in (str(w.message) for w in record) if "energy_patch" in m]
    assert len(messages) == 1
    assert "changes the reference energy" in messages[0]
    assert "DELTA_E_REF=-135000000.0" in messages[0]
    assert "moves the reference frame" not in messages[0]


def test_bmad_non_positive_n_cell_fills_the_element_with_cells():
    """Bmad: ``n_cell <= 0`` fills the length with half-wavelength cells."""
    elements = _convert(
        _line_importer(
            ["sentinel_cav", "nine_cell_cav"],
            ["Lcavity", "Lcavity"],
            [3.0441, 9.0],
            [3.0441, 12.0441],
            [
                {
                    "N_CELL": -1,
                    "RF_FREQUENCY": 2856000000.0,
                    "VOLTAGE": 5.2e7,
                    "PHI0": 0.0,
                },
                {
                    "N_CELL": 9,
                    "RF_FREQUENCY": 1300000000.0,
                    "VOLTAGE": 1.44e8,
                    "PHI0": 0.0,
                },
            ],
        )
    )

    sentinel = elements["sentinel_cav"]
    assert sentinel.cavity.cell_length == pytest.approx(299792458.0 / (2 * 2.856e9))
    assert sentinel.cavity.n_cells == 57
    assert sentinel.cavity.n_cells * sentinel.cavity.cell_length <= 3.0441
    nine = elements["nine_cell_cav"]
    assert nine.cavity.n_cells == 9
    assert nine.cavity.cell_length == pytest.approx(299792458.0 / (2 * 1.3e9))


@pytest.mark.parametrize(
    "terms, c, r, t, u",
    [
        pytest.param(
            [
                {"coef": 3.0, **{f"exp{i}": 0.0 for i in range(1, 7)}},
                {"coef": 4.0, "exp1": 1.0, **{f"exp{i}": 0.0 for i in range(2, 7)}},
                {"coef": 5.0, "exp1": 2.0, **{f"exp{i}": 0.0 for i in range(2, 7)}},
            ],
            15.0,
            -16.0,
            5.0,
            0.0,
            id="quadratic",
        ),
        pytest.param(
            [{"coef": 7.0, "exp1": 3.0, **{f"exp{i}": 0.0 for i in range(2, 7)}}],
            -56.0,
            84.0,
            -42.0,
            7.0,
            id="cubic",
        ),
    ],
)
def test_bmad_taylor_reference_orbit_feeddown(terms, c, r, t, u):
    sections = [
        {"index": output, "ref": 2.0 if output == 1 else 0.0, "data": []}
        for output in range(1, 7)
    ]
    sections[0]["data"] = terms
    c_matrix, r_matrix, t_matrix, u_matrix = _taylor_matrices({"data": sections})

    assert c_matrix[0] == pytest.approx(c)
    assert r_matrix[0, 0] == pytest.approx(r)
    assert t_matrix[0, 0, 0] == pytest.approx(t)
    assert u_matrix[0, 0, 0, 0] == pytest.approx(u)
    assert np.count_nonzero(u_matrix) == (u != 0)


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

    loaded = read_yaml_element_file(str(path), validate=True)

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

    loaded = read_yaml_element_file(str(path), validate=True)

    assert loaded.simulation.spin_taylor == [term]


def test_bmad_floor_angles_survive_the_trip_into_laura_and_back():
    """Opposite composition order and Ry sign: conversion must go through the matrix."""
    rng = np.random.default_rng(20260901)
    for theta, phi, psi in rng.uniform(-4.0, 4.0, size=(200, 3)):
        phi = float(np.clip(phi, -1.5, 1.5))
        expected = bmad_floor_rotation_matrix(theta, phi, psi)

        laura = bmad_floor_angles_to_laura(theta, phi, psi)
        np.testing.assert_allclose(
            euler_angles_to_rotation_matrix(laura["theta"], laura["phi"], laura["psi"]),
            expected,
            atol=1e-13,
        )
        assert abs(laura["phi"]) <= np.pi / 2 + 1e-12
        assert abs(laura["theta"]) <= np.pi + 1e-12
        assert abs(laura["psi"]) <= np.pi + 1e-12

        back = bmad_floor_angles_from_matrix(expected)
        np.testing.assert_allclose(
            bmad_floor_rotation_matrix(back["theta"], back["phi"], back["psi"]),
            expected,
            atol=1e-13,
        )


def test_bmad_floor_angles_reduce_to_a_sign_flip_for_a_flat_machine():
    flat = bmad_floor_angles_to_laura(0.3, 0.0, 0.0)
    assert flat == pytest.approx({"theta": -0.3, "phi": 0.0, "psi": 0.0})

    roll = bmad_floor_angles_to_laura(0.0, 0.0, 0.3)
    assert roll == pytest.approx({"theta": 0.0, "phi": 0.0, "psi": 0.3})


def test_bmad_collective_and_radiation_settings_reach_the_elements():
    """``bmad_com`` switches have no LAURA global, so they ride on every element."""
    elements = _convert(
        _line_importer(
            ["q", "cav", "mark"],
            ["Quadrupole", "Lcavity", "Marker"],
            [0.5, 3.0441, 0.0],
            [0.5, 3.5441, 3.5441],
            [
                {
                    "K1": 0.5,
                    "CSR_DS_STEP": 0.01,
                    "_METHODS": {
                        "csr_method": "1_Dim",
                        "space_charge_method": "Slice",
                    },
                },
                {
                    "N_CELL": -1,
                    "N_RF_STEPS": 1000,
                    "RF_FREQUENCY": 2856000000.0,
                    "VOLTAGE": 5.2e7,
                    "PHI0": 0.0,
                    "_METHODS": {},
                },
                {"_METHODS": {}},
            ],
            bmad_com={
                "csr_and_space_charge_on": False,
                "radiation_damping_on": False,
                "radiation_fluctuations_on": True,
            },
        )
    )

    quadrupole = elements["q"].simulation
    assert (quadrupole.csr_method, quadrupole.space_charge_method) == (
        "1_Dim",
        "Slice",
    )
    assert quadrupole.csrdz == 0.01
    assert (quadrupole.sr_enable, quadrupole.isr_enable) == (False, True)
    assert (quadrupole.csr_enable, quadrupole.lsc_enable) == (False, False)

    # Off is Bmad's default, so it isn't recorded.
    cavity = elements["cav"].simulation
    assert cavity.csr_method is None and cavity.space_charge_method is None
    assert cavity.n_kicks == 1000

    assert elements["mark"].simulation.csr_enable is False


_BEND = {"ANGLE": 0.01, "E1": 0.0, "E2": 0.0, "HGAP": 0.0, "FINT": 0.0,
         "REF_TILT": 0.0, "_METHODS": {}}


def test_bmad_fringe_model_is_kept_only_when_it_is_not_the_default():
    """Bmad fills ``fringe_type`` everywhere; its per-class defaults are dropped."""
    elements = _convert(
        _line_importer(
            ["b_full", "b_default", "q_default", "cav"],
            ["SBend", "SBend", "Quadrupole", "Lcavity"],
            [0.2, 0.2, 0.5, 3.0441],
            [0.2, 0.4, 0.9, 3.9441],
            [
                {**_BEND, "FRINGE_TYPE": "Full"},
                {**_BEND, "FRINGE_TYPE": "Basic_Bend"},
                {"K1": 0.5, "FRINGE_TYPE": "None", "_METHODS": {}},
                {
                    "N_CELL": 1,
                    "RF_FREQUENCY": 2856000000.0,
                    "VOLTAGE": 5.2e7,
                    "PHI0": 0.0,
                    "FRINGE_TYPE": "Full",
                    "_METHODS": {},
                },
            ],
            bmad_com={},
        )
    )

    assert elements["b_full"].simulation.fringe_model == "full"
    assert elements["b_default"].simulation.fringe_model is None
    assert elements["q_default"].simulation.fringe_model is None

    assert not hasattr(elements["cav"].simulation, "fringe_model")
