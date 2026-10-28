import pytest

from laura.models.element import (
    Quadrupole,
    Marker,
    Dipole,
    BeamPositionMonitor,
)
from laura.models.physical import Position, PhysicalElement
from laura.models.element_list import (
    ElementList,
    SectionLattice,
    MachineLayout,
    MachineModel,
    load_functional_definitions,
    normalise_lattice_type,
)
from laura.models.base_models import IgnoreExtra
from laura.models.exceptions import LatticeError


@pytest.fixture
def elements():
    m1 = Marker(
        name="M1", machine_area="S1", hardware_class="Marker",
        physical={"middle": {"x": 0.0, "y": 0.0, "z": 0.0}},
    )
    q1 = Quadrupole(
        name="Q1", machine_area="S1",
        magnetic={"length": 0.3, "k1l": -1.0},
        physical={"length": 0.3, "middle": {"x": 0.0, "y": 0.0, "z": 1.0}},
    )
    q2 = Quadrupole(
        name="Q2", machine_area="S1",
        magnetic={"length": 0.3, "k1l": 1.0},
        physical={"length": 0.3, "middle": {"x": 0.0, "y": 0.0, "z": 3.0}},
    )
    m2 = Marker(
        name="M2", machine_area="S1", hardware_class="Marker",
        physical={"middle": {"x": 0.0, "y": 0.0, "z": 4.0}},
    )
    return [m1, q1, q2, m2]


@pytest.fixture
def element_list(elements):
    return ElementList(elements={e.name: e for e in elements})


@pytest.fixture
def section_lattice(elements):
    return SectionLattice(
        name="S1",
        order=["M1", "Q1", "Q2", "M2"],
        elements=elements,
    )


@pytest.fixture
def machine_layout(section_lattice):
    return MachineLayout(
        name="beam1",
        sections={"S1": section_lattice},
    )


@pytest.fixture
def machine_model(elements):
    return MachineModel(
        layout={"default_layout": "beam1", "layouts": {"beam1": ["S1"]}},
        section={"sections": {"S1": ["M1", "Q1", "Q2", "M2"]}},
        elements={e.name: e for e in elements},
    )


class TestElementList:
    def test_names(self, element_list):
        assert "M1" in element_list.names
        assert "Q1" in element_list.names
        assert len(element_list.names) == 4

    def test_getitem(self, element_list):
        q1 = element_list["Q1"]
        assert q1.name == "Q1"

    def test_index_by_name(self, element_list):
        idx = element_list.index("Q1")
        assert isinstance(idx, int)

    def test_index_by_element(self, element_list, elements):
        idx = element_list.index(elements[1])
        assert isinstance(idx, int)

    def test_list(self, element_list):
        lst = element_list.list()
        assert len(lst) == 4

    def test_str(self, element_list):
        s = str(element_list)
        assert "M1" in s

    def test_getattr_delegates(self, element_list):
        result = element_list.hardware_type
        assert isinstance(result, dict)
        assert result["Q1"] == "Quadrupole"

    def test_missing_attribute_recorded_as_none(self):
        m1 = Marker(name="M1", machine_area="A")
        el = ElementList(elements={"M1": m1})
        assert el._get_attributes_or_none("no_such_attr") == {"M1": None}

    def test_present_attribute_gathered(self):
        m1 = Marker(name="M1", machine_area="A")
        el = ElementList(elements={"M1": m1})
        assert el._get_attributes_or_none("name") == {"M1": "M1"}

    def test_getattr_wraps_in_elementlist_when_all_none(self):
        m1 = Marker(name="M1", machine_area="A")
        m2 = Marker(name="M2", machine_area="A")
        el = ElementList(elements={"M1": m1, "M2": m2})
        result = el.totally_missing_attr
        assert isinstance(result, ElementList)
        assert result.elements == {"M1": None, "M2": None}


class TestNormaliseLatticeType:
    def test_non_string_raises_typeerror(self):
        with pytest.raises(TypeError, match="must be a string"):
            normalise_lattice_type(5, context="section")

    def test_unknown_value_raises_valueerror(self):
        with pytest.raises(ValueError, match="must be one of"):
            normalise_lattice_type("not_a_type", context="section")

    def test_none_returns_default(self):
        assert normalise_lattice_type(None, context="section") == "beam"

    def test_valid_value_normalised(self):
        assert normalise_lattice_type(" RF ", context="section") == "rf"


class TestSectionLattice:
    def test_names(self, section_lattice):
        assert section_lattice.names == ["M1", "Q1", "Q2", "M2"]

    def test_getitem_by_name(self, section_lattice):
        q1 = section_lattice["Q1"]
        assert q1.name == "Q1"

    def test_getitem_by_index(self, section_lattice):
        first = section_lattice[0]
        assert first.name == "M1"

    def test_create_drifts(self, section_lattice):
        drifts = section_lattice.create_drifts()
        assert isinstance(drifts, dict)
        drift_names = [k for k in drifts.keys() if "drift" in k.lower()]
        assert len(drift_names) > 0

    def _thick_diagnostic_section(self):
        return SectionLattice(
            name="S",
            order=["Q1", "BPM", "Q2"],
            elements=[
                Quadrupole(
                    name="Q1",
                    machine_area="S",
                    magnetic={"magnetic_length": 0.5, "k1l": 0.3},
                    physical=PhysicalElement(length=0.5, middle=Position(z=0.25)),
                ),
                BeamPositionMonitor(
                    name="BPM",
                    machine_area="S",
                    physical=PhysicalElement(length=0.3, middle=Position(z=1.15)),
                ),
                Quadrupole(
                    name="Q2",
                    machine_area="S",
                    magnetic={"magnetic_length": 0.5, "k1l": -0.3},
                    physical=PhysicalElement(length=0.5, middle=Position(z=2.05)),
                ),
            ],
            geometry="open",
        )

    def test_create_drifts_collapses_a_diagnostic_by_default(self):
        """Not every code has a thick marker, so the drifts absorb the length."""
        section = self._thick_diagnostic_section()
        drifts = section.createDrifts()

        assert drifts["BPM"].physical.length == 0.0
        total = sum(e.physical.length for e in drifts.values())
        assert total == pytest.approx(2.3)

    def test_create_drifts_can_keep_a_diagnostic_thick(self):
        """For codes with thick diagnostics, e.g. Bmad monitor/instrument."""
        section = self._thick_diagnostic_section()
        drifts = section.createDrifts(keep_diagnostic_length=True)

        assert drifts["BPM"].physical.length == pytest.approx(0.3)
        total = sum(e.physical.length for e in drifts.values())
        assert total == pytest.approx(2.3)

    def test_create_drifts_does_not_touch_the_section_it_was_given(self):
        section = self._thick_diagnostic_section()
        section.createDrifts()
        section.createDrifts()

        assert section.elements["BPM"].physical.length == pytest.approx(0.3)

    def test_get_s_values_list(self, section_lattice):
        s_vals = section_lattice.get_s_values()
        assert isinstance(s_vals, list)
        assert len(s_vals) > 0

    def test_get_s_values_dict(self, section_lattice):
        s_dict = section_lattice.get_s_values(as_dict=True)
        assert isinstance(s_dict, dict)

    def test_get_s_values_at_entrance(self, section_lattice):
        s_entrance = section_lattice.get_s_values(at_entrance=True)
        s_exit = section_lattice.get_s_values(at_entrance=False)
        assert s_entrance[0] <= s_exit[0]

    def test_str(self, section_lattice):
        s = str(section_lattice)
        assert "M1" in s

    def test_section_type_default(self, section_lattice):
        assert section_lattice.section_type == "beam"


class TestMachineLayout:
    def test_names(self, machine_layout):
        assert machine_layout.names == ["S1"]

    def test_getitem(self, machine_layout):
        s1 = machine_layout["S1"]
        assert s1.name == "S1"

    def test_elements(self, machine_layout):
        elem_names = machine_layout.elements
        assert "Q1" in elem_names

    def test_get_element(self, machine_layout):
        q1 = machine_layout.get_element("Q1")
        assert q1.name == "Q1"

    def test_get_element_not_found(self, machine_layout):
        with pytest.raises(LatticeError):
            machine_layout.get_element("NONEXISTENT")

    def test_elements_between(self, machine_layout):
        result = machine_layout.elements_between(start="Q1", end="Q2")
        assert "Q1" in result
        assert "Q2" in result

    def test_elements_between_all(self, machine_layout):
        result = machine_layout.elements_between()
        assert isinstance(result, list)
        assert len(result) == 4

    def test_elements_between_filter_type(self, machine_layout):
        result = machine_layout.elements_between(element_type="Quadrupole")
        assert "Q1" in result
        assert "Q2" in result
        assert "M1" not in result

    def test_elements_between_filter_class(self, machine_layout):
        result = machine_layout.elements_between(element_class="Magnet")
        assert "Q1" in result
        assert "M1" not in result

    def test_elements_between_filter_section_type(self, machine_layout):
        machine_layout.sections["S1"].section_type = "beam"
        result = machine_layout.elements_between(section_type="beam")
        assert len(result) == 4

    def test_elements_between_filter_section_type_invalid(self, machine_layout):
        with pytest.raises(ValueError):
            machine_layout.elements_between(section_type="invalid")

    def test_get_all_elements(self, machine_layout):
        result = machine_layout.get_all_elements()
        assert len(result) == 4

    def test_get_all_elements_filtered(self, machine_layout):
        result = machine_layout.get_all_elements(element_type="Marker")
        assert "M1" in result
        assert "M2" in result
        assert len(result) == 2

    def test_str(self, machine_layout):
        s = str(machine_layout)
        assert "S1" in s


class TestMachineModel:
    def test_empty_model(self):
        mm = MachineModel()
        assert len(mm.elements) == 0

    def test_from_elements_and_sections(self, machine_model):
        assert "S1" in machine_model.sections
        assert "beam1" in machine_model.lattices
        assert machine_model.default_path == "beam1"

    def test_from_elements_and_inline_typed_sections(self, elements):
        sections = {
            "sections": {
                "S1": {
                    "type": "rf",
                    "elements": ["M1", "Q1", "Q2", "M2"],
                }
            }
        }
        layouts = {"default_layout": "beam1", "layouts": {"beam1": ["S1"]}}
        mm = MachineModel(
            layout=layouts,
            section=sections,
            elements={e.name: e for e in elements},
        )
        assert mm.sections["S1"].section_type == "rf"

    def test_layout_metadata_defaults_and_types(self, elements):
        sections = {"sections": {"S1": ["M1", "Q1", "Q2", "M2"]}}
        layouts = {
            "default_layout": "beam1",
            "layouts": {"beam1": ["S1"], "rf1": ["S1"]},
            "layout_metadata": {"rf1": {"type": "rf"}},
        }
        mm = MachineModel(
            layout=layouts,
            section=sections,
            elements={e.name: e for e in elements},
        )
        assert mm.lattices["beam1"].layout_type == "beam"
        assert mm.lattices["rf1"].layout_type == "rf"

    def test_get_sections_by_type(self, elements):
        sections = {
            "sections": {
                "S1": {"type": "beam", "elements": ["M1", "Q1"]},
                "S2": {"type": "laser", "elements": ["Q2", "M2"]},
            }
        }
        layouts = {"default_layout": "beam1", "layouts": {"beam1": ["S1", "S2"]}}
        mm = MachineModel(
            layout=layouts,
            section=sections,
            elements={e.name: e for e in elements},
        )
        assert list(mm.get_sections_by_type("laser").keys()) == ["S2"]

    def test_get_layouts_by_type(self, elements):
        sections = {"sections": {"S1": ["M1", "Q1", "Q2", "M2"]}}
        layouts = {
            "default_layout": "beam1",
            "layouts": {"beam1": ["S1"], "laser1": ["S1"]},
            "layout_metadata": {"laser1": {"type": "laser"}},
        }
        mm = MachineModel(
            layout=layouts,
            section=sections,
            elements={e.name: e for e in elements},
        )
        assert list(mm.get_layouts_by_type("laser").keys()) == ["laser1"]

    def test_elements_between_section_type(self, elements):
        sections = {
            "sections": {
                "S1": {"type": "beam", "elements": ["M1", "Q1"]},
                "S2": {"type": "rf", "elements": ["Q2", "M2"]},
            }
        }
        layouts = {"default_layout": "beam1", "layouts": {"beam1": ["S1", "S2"]}}
        mm = MachineModel(
            layout=layouts,
            section=sections,
            elements={e.name: e for e in elements},
        )
        result = mm.elements_between(path="beam1", section_type="rf")
        assert result == ["Q2", "M2"]

    def test_getitem(self, machine_model):
        q1 = machine_model["Q1"]
        assert q1.name == "Q1"

    def test_setitem(self, machine_model):
        new_marker = Marker(
            name="M3", machine_area="S1", hardware_class="Marker",
            physical={"middle": {"x": 0.0, "y": 0.0, "z": 5.0}},
        )
        machine_model["M3"] = new_marker
        assert "M3" in machine_model.elements

    def test_get_element(self, machine_model):
        q1 = machine_model.get_element("Q1")
        assert q1.name == "Q1"

    def test_get_element_not_found(self, machine_model):
        with pytest.raises(LatticeError):
            machine_model.get_element("NONEXISTENT")

    def test_add(self, machine_model):
        new_elem = Marker(
            name="M3", machine_area="S1", hardware_class="Marker",
            physical={"middle": {"x": 0.0, "y": 0.0, "z": 5.0}},
        )
        result = machine_model + {"M3": new_elem}
        assert "M3" in result

    def test_elements_between(self, machine_model):
        result = machine_model.elements_between(start="Q1", end="Q2", path="beam1")
        assert "Q1" in result
        assert "Q2" in result
        assert isinstance(machine_model.elements_between(), list)

    def test_space_charge_is_authored_on_the_section_definition(self, elements):
        # Settings applied only to the built SectionLattice are lost on rebuild.
        definitions = {
            "sections": {
                "S1": {
                    "elements": ["M1", "Q1", "Q2", "M2"],
                    "space_charge": {"number_of_bins": 40, "step_size": 0.01},
                }
            }
        }
        layout = {"default_layout": "beam1", "layouts": {"beam1": ["S1"]}}
        mm = MachineModel(
            layout=layout,
            section=definitions,
            elements={e.name: e for e in elements},
        )
        assert mm.sections["S1"].space_charge.number_of_bins == 40
        assert mm.sections["S1"].space_charge.step_size == 0.01
        assert mm.sections["S1"].space_charge.chamber_height is None

        rebuilt = MachineModel(
            layout=layout,
            section=mm.section,
            elements={e.name: e for e in elements},
        )
        assert rebuilt.sections["S1"].space_charge.number_of_bins == 40

    def test_section_written_as_a_bare_list_has_no_space_charge(self, machine_model):
        assert machine_model.sections["S1"].space_charge is None

    def test_layout_validation_missing_layouts_key(self):
        with pytest.raises(KeyError):
            MachineModel(
                layout={"not_layouts": {}},
                section={"sections": {}},
            )

    def test_section_validation_missing_sections_key(self):
        with pytest.raises(KeyError):
            MachineModel(
                layout={"default_layout": "a", "layouts": {"a": ["SEC"]}},
                section={"not_sections": {}},
            )

    def test_iter(self, machine_model):
        names = list(machine_model)
        assert "Q1" in names

    def test_str(self, machine_model):
        s = str(machine_model)
        assert "Q1" in s or "M1" in s


class TestFunctionalDefinitionsLoading:
    def test_resolve_functional_flag_set_and_cascaded(self, elements):
        mm = MachineModel(
            layout={"default_layout": "beam1", "layouts": {"beam1": ["S1"]}},
            section={"sections": {"S1": ["M1", "Q1", "Q2", "M2"]}},
            elements={e.name: e for e in elements},
            functional_definitions={"quad1_k1l": -2.0},
            resolve_functional=True,
        )
        assert IgnoreExtra.resolve_functional is True
        assert mm.sections["S1"].resolve_functional is True

    def test_load_flat_yaml(self, tmp_path):
        f = tmp_path / "defs.yaml"
        f.write_text("quad1_k1l: -2.0\ncav1_phase: 90\n")
        assert load_functional_definitions(str(f)) == {"quad1_k1l": -2.0, "cav1_phase": 90}

    def test_none_returns_empty_dict(self):
        assert load_functional_definitions(None) == {}

    def test_dict_passthrough(self):
        assert load_functional_definitions({"a": 1}) == {"a": 1}

    def test_missing_file_raises(self):
        with pytest.raises(ValueError, match="does not exist"):
            load_functional_definitions("no_such_functional_definitions.yaml")

    def test_invalid_type_raises(self):
        with pytest.raises(ValueError, match="path, dict, or None"):
            load_functional_definitions(5)

    def test_resolved_relative_to_master_lattice(self, tmp_path):
        f = tmp_path / "func_defs.yaml"
        f.write_text("quad1_k1l: -2.0\ncav1_phase: 90\n")
        result = load_functional_definitions("func_defs.yaml", master_lattice=str(tmp_path))
        assert result == {"quad1_k1l": -2.0, "cav1_phase": 90}

    def test_nested_functional_definitions_key(self, tmp_path):
        f = tmp_path / "nested.yaml"
        f.write_text("functional_definitions:\n  a: 1\n  b: 2\n")
        result = load_functional_definitions(str(f))
        assert result == {"a": 1, "b": 2}

    def test_empty_file_returns_empty_dict(self, tmp_path):
        f = tmp_path / "empty.yaml"
        f.write_text("")
        assert load_functional_definitions(str(f)) == {}

    def test_machine_model_registers_from_yaml(self, tmp_path):
        f = tmp_path / "defs.yaml"
        f.write_text("quad1_k1l: -2.0\n")
        MachineModel(functional_definitions=str(f))
        assert IgnoreExtra.functional_definitions == {"quad1_k1l": -2.0}

    def test_section_lattice_registers_from_dict(self):
        SectionLattice(
            name="S1", order=[], elements=[], functional_definitions={"x": 5}
        )
        assert IgnoreExtra.functional_definitions == {"x": 5}

    def test_machine_model_cascades_to_children(self, elements, tmp_path):
        f = tmp_path / "defs.yaml"
        f.write_text("quad1_k1l: -2.0\n")
        mm = MachineModel(
            layout={"default_layout": "beam1", "layouts": {"beam1": ["S1"]}},
            section={"sections": {"S1": ["M1", "Q1", "Q2", "M2"]}},
            elements={e.name: e for e in elements},
            functional_definitions=str(f),
        )
        assert mm.sections["S1"].functional_definitions == {"quad1_k1l": -2.0}
        assert mm.lattices["beam1"].functional_definitions == {"quad1_k1l": -2.0}

    def test_undefined_reference_raises_with_file_source(self, tmp_path):
        f = tmp_path / "defs.yaml"
        f.write_text("some_other: 1.0\n")
        qbad = Quadrupole(
            name="QBAD", machine_area="S1",
            magnetic={"length": 0.3, "k1l": "missing_k1l"},
        )
        with pytest.raises(ValueError) as exc:
            MachineModel(
                layout={"default_layout": "b", "layouts": {"b": ["S1"]}},
                section={"sections": {"S1": ["QBAD"]}},
                elements={"QBAD": qbad},
                functional_definitions=str(f),
            )
        msg = str(exc.value)
        assert "missing_k1l" in msg
        assert "QBAD" in msg
        assert str(f) in msg

    def test_undefined_reference_raises_with_dict_source(self):
        qbad = Quadrupole(
            name="QBAD", machine_area="S1",
            magnetic={"length": 0.3, "k1l": "missing_k1l"},
        )
        with pytest.raises(ValueError) as exc:
            SectionLattice(
                name="S1", order=["QBAD"], elements=[qbad],
                functional_definitions={"x": 1},
            )
        assert "missing_k1l" in str(exc.value)

    def test_dipole_angle_and_edge_validation(self):
        dbad = Dipole(
            name="DBAD", machine_area="ARC",
            magnetic={"magnetic_length": 0.5, "k0l": "missing_bend",
                      "entrance_edge_angle": "missing_e1", "exit_edge_angle": "angle/2"},
        )
        with pytest.raises(ValueError) as exc:
            SectionLattice(
                name="ARC", order=["DBAD"], elements=[dbad],
                functional_definitions={"other": 1},
            )
        msg = str(exc.value)
        assert "missing_bend" in msg and "missing_e1" in msg
        assert "angle/2" not in msg  # reserved token, not a functional reference

    def test_reserved_edge_expression_passes_validation(self):
        d = Dipole(
            name="D", machine_area="ARC",
            magnetic={"magnetic_length": 0.5, "k0l": "bend1",
                      "entrance_edge_angle": "angle", "exit_edge_angle": "angle/2"},
        )
        # "angle"/"angle/2" edges are reserved tokens
        sl = SectionLattice(
            name="ARC", order=["D"], elements=[d],
            functional_definitions={"bend1": 0.1},
        )
        assert sl.functional_definitions == {"bend1": 0.1}

    def test_magnet_simulation_field_amplitude_is_validated(self):
        qbad = Quadrupole(
            name="QBAD", machine_area="S1",
            simulation={"field_amplitude": "missing_fa"},
        )
        with pytest.raises(ValueError) as exc:
            SectionLattice(
                name="S1", order=["QBAD"], elements=[qbad],
                functional_definitions={"x": 1},
            )
        assert "missing_fa" in str(exc.value)

    def test_defined_reference_passes_validation(self, tmp_path):
        f = tmp_path / "defs.yaml"
        f.write_text("quad1_k1l: -2.0\n")
        q = Quadrupole(
            name="Q1", machine_area="S1",
            magnetic={"length": 0.3, "k1l": "quad1_k1l"},
        )
        sl = SectionLattice(
            name="S1", order=["Q1"], elements=[q],
            functional_definitions=str(f),
        )
        assert sl.functional_definitions == {"quad1_k1l": -2.0}

    def test_sections_validate_again_after_a_machine_build(self, elements):
        MachineModel(elements={e.name: e for e in elements})
        qbad = Quadrupole(
            name="QBAD", machine_area="S1",
            magnetic={"length": 0.3, "k1l": "missing_k1l"},
        )
        with pytest.raises(ValueError, match="missing_k1l"):
            SectionLattice(name="S1", order=["QBAD"], elements=[qbad])


def test_section_members_adds_subelements_by_generation_in_list_order():
    by_name = {
        "GRANDCHILD": {"subelement": "CHILD_B"},
        "CHILD_A": {"subelement": "A"},
        "A": {"name": "A"},
        "OTHER": {"subelement": "ELSEWHERE"},
        "CHILD_B": {"subelement": "B"},
        "B": {"name": "B"},
    }
    children = MachineModel._subelement_index(by_name)
    members = MachineModel._section_members(["B", "A", "MISSING"], by_name, children)
    assert members == [by_name[n] for n in ["B", "A", "CHILD_A", "CHILD_B", "GRANDCHILD"]]
