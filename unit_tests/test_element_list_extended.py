"""Tests for laura.models.elementList — SectionLattice, MachineLayout, MachineModel, ElementList."""

import pytest
import numpy as np

from laura.models.element import (
    Quadrupole,
    Marker,
    PhysicalBaseElement,
    Dipole,
    Drift,
    Beam_Position_Monitor,
)
from laura.models.physical import Position, PhysicalElement
from laura.models.elementList import (
    ElementList,
    SectionLattice,
    MachineLayout,
    MachineModel,
    load_functional_definitions,
)
from laura.models.baseModels import (
    IgnoreExtra,
    set_functional_definitions,
    set_resolve_functional,
)
from laura.models.exceptions import LatticeError


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# ElementList
# ---------------------------------------------------------------------------

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
        """Test that ElementList.__getattr__ delegates to element attributes."""
        result = element_list.hardware_type
        assert isinstance(result, dict)
        assert result["Q1"] == "Quadrupole"


# ---------------------------------------------------------------------------
# SectionLattice
# ---------------------------------------------------------------------------

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
        drifts = section_lattice.createDrifts()
        assert isinstance(drifts, dict)
        # Count drift elements
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
                Beam_Position_Monitor(
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
        """Not every code can express a marker that occupies space, so the
        default is to shrink a Diagnostic to a point and let the drifts either
        side take up the slack.
        """
        section = self._thick_diagnostic_section()
        drifts = section.createDrifts()

        assert drifts["BPM"].physical.length == 0.0
        total = sum(e.physical.length for e in drifts.values())
        assert total == pytest.approx(2.3)

    def test_create_drifts_can_keep_a_diagnostic_thick(self):
        """Codes whose diagnostics do take a length -- Bmad's monitor and
        instrument both do -- ask for the length to survive, or the element's
        recorded position moves half an element-length upstream.
        """
        section = self._thick_diagnostic_section()
        drifts = section.createDrifts(keep_diagnostic_length=True)

        assert drifts["BPM"].physical.length == pytest.approx(0.3)
        total = sum(e.physical.length for e in drifts.values())
        assert total == pytest.approx(2.3)

    def test_create_drifts_does_not_touch_the_section_it_was_given(self):
        """This used to assign straight into the caller's model, so one call
        permanently zeroed every diagnostic length in it and every later
        export -- to any code, or back to YAML -- inherited the loss.
        """
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
        # Entrance s-values should be <= exit s-values
        assert s_entrance[0] <= s_exit[0]

    def test_str(self, section_lattice):
        s = str(section_lattice)
        assert "M1" in s

    def test_section_type_default(self, section_lattice):
        assert section_lattice.section_type == "beam"


# ---------------------------------------------------------------------------
# MachineLayout
# ---------------------------------------------------------------------------

class TestMachineLayout:
    def test_names(self, machine_layout):
        assert "S1" in machine_layout.names

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


# ---------------------------------------------------------------------------
# MachineModel
# ---------------------------------------------------------------------------

class TestMachineModel:
    def test_empty_model(self):
        mm = MachineModel()
        assert len(mm.elements) == 0

    def test_from_elements_and_sections(self, elements):
        sections = {"sections": {"S1": ["M1", "Q1", "Q2", "M2"]}}
        layouts = {"default_layout": "beam1", "layouts": {"beam1": ["S1"]}}
        mm = MachineModel(
            layout=layouts,
            section=sections,
            elements={e.name: e for e in elements},
        )
        assert "S1" in mm.sections
        assert "beam1" in mm.lattices
        assert mm.default_path == "beam1"

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

    def test_getitem(self, elements):
        sections = {"sections": {"S1": ["M1", "Q1", "Q2", "M2"]}}
        layouts = {"default_layout": "beam1", "layouts": {"beam1": ["S1"]}}
        mm = MachineModel(
            layout=layouts, section=sections,
            elements={e.name: e for e in elements},
        )
        q1 = mm["Q1"]
        assert q1.name == "Q1"

    def test_setitem(self, elements):
        sections = {"sections": {"S1": ["M1", "Q1", "Q2", "M2"]}}
        layouts = {"default_layout": "beam1", "layouts": {"beam1": ["S1"]}}
        mm = MachineModel(
            layout=layouts, section=sections,
            elements={e.name: e for e in elements},
        )
        new_marker = Marker(
            name="M3", machine_area="S1", hardware_class="Marker",
            physical={"middle": {"x": 0.0, "y": 0.0, "z": 5.0}},
        )
        mm["M3"] = new_marker
        assert "M3" in mm.elements

    def test_get_element(self, elements):
        sections = {"sections": {"S1": ["M1", "Q1", "Q2", "M2"]}}
        layouts = {"default_layout": "beam1", "layouts": {"beam1": ["S1"]}}
        mm = MachineModel(
            layout=layouts, section=sections,
            elements={e.name: e for e in elements},
        )
        q1 = mm.get_element("Q1")
        assert q1.name == "Q1"

    def test_get_element_not_found(self, elements):
        mm = MachineModel(
            layout={"default_layout": "beam1", "layouts": {"beam1": ["S1"]}},
            section={"sections": {"S1": ["M1", "Q1", "Q2", "M2"]}},
            elements={e.name: e for e in elements},
        )
        with pytest.raises(LatticeError):
            mm.get_element("NONEXISTENT")

    def test_add(self, elements):
        mm = MachineModel(
            layout={"default_layout": "beam1", "layouts": {"beam1": ["S1"]}},
            section={"sections": {"S1": ["M1", "Q1", "Q2", "M2"]}},
            elements={e.name: e for e in elements},
        )
        new_elem = Marker(
            name="M3", machine_area="S1", hardware_class="Marker",
            physical={"middle": {"x": 0.0, "y": 0.0, "z": 5.0}},
        )
        result = mm + {"M3": new_elem}
        assert "M3" in result

    def test_elements_between(self, elements):
        mm = MachineModel(
            layout={"default_layout": "beam1", "layouts": {"beam1": ["S1"]}},
            section={"sections": {"S1": ["M1", "Q1", "Q2", "M2"]}},
            elements={e.name: e for e in elements},
        )
        result = mm.elements_between(start="Q1", end="Q2", path="beam1")
        assert "Q1" in result
        assert "Q2" in result

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

    def test_iter(self, elements):
        mm = MachineModel(
            layout={"default_layout": "beam1", "layouts": {"beam1": ["S1"]}},
            section={"sections": {"S1": ["M1", "Q1", "Q2", "M2"]}},
            elements={e.name: e for e in elements},
        )
        names = list(mm)
        assert "Q1" in names

    def test_str(self, elements):
        mm = MachineModel(
            layout={"default_layout": "beam1", "layouts": {"beam1": ["S1"]}},
            section={"sections": {"S1": ["M1", "Q1", "Q2", "M2"]}},
            elements={e.name: e for e in elements},
        )
        s = str(mm)
        assert "Q1" in s or "M1" in s


# ---------------------------------------------------------------------------
# Functional definitions (dict or YAML)
# ---------------------------------------------------------------------------

class TestFunctionalDefinitionsLoading:
    @pytest.fixture(autouse=True)
    def _reset(self):
        set_functional_definitions({}, merge=False)
        set_resolve_functional(False)
        yield
        set_functional_definitions({}, merge=False)
        set_resolve_functional(False)

    def test_resolve_functional_flag_set_and_cascaded(self, elements):
        mm = MachineModel(
            layout={"default_layout": "beam1", "layouts": {"beam1": ["S1"]}},
            section={"sections": {"S1": ["M1", "Q1", "Q2", "M2"]}},
            elements={e.name: e for e in elements},
            functional_definitions={"quad1_k1l": -2.0},
            resolve_functional=True,
        )
        # the flag is set globally and cascaded into the child section
        assert IgnoreExtra.resolve_functional is True
        assert mm.sections["S1"].resolve_functional is True

    def test_load_dict_passthrough(self):
        assert load_functional_definitions({"a": 1}) == {"a": 1}

    def test_load_none(self):
        assert load_functional_definitions(None) == {}

    def test_load_flat_yaml(self, tmp_path):
        f = tmp_path / "defs.yaml"
        f.write_text("quad1_k1l: -2.0\ncav1_phase: 90\n")
        assert load_functional_definitions(str(f)) == {"quad1_k1l": -2.0, "cav1_phase": 90}

    def test_load_nested_yaml(self, tmp_path):
        f = tmp_path / "defs.yaml"
        f.write_text("functional_definitions:\n  quad1_k1l: -3.3\n")
        assert load_functional_definitions(str(f)) == {"quad1_k1l": -3.3}

    def test_missing_file_raises(self):
        with pytest.raises(ValueError):
            load_functional_definitions("/no/such/file.yaml")

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
        # the loaded definitions cascade into the child section and layout
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
        assert str(f) in msg  # error points at the source file

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
        from laura.models.element import Dipole
        # undefined bend angle and edge angle are both caught; the reserved
        # "angle/2" edge expression is not treated as a functional reference.
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
        from laura.models.element import Dipole
        d = Dipole(
            name="D", machine_area="ARC",
            magnetic={"magnetic_length": 0.5, "k0l": "bend1",
                      "entrance_edge_angle": "angle", "exit_edge_angle": "angle/2"},
        )
        # only bend1 needs defining; the "angle"/"angle/2" edges are reserved
        sl = SectionLattice(
            name="ARC", order=["D"], elements=[d],
            functional_definitions={"bend1": 0.1},
        )
        assert sl.functional_definitions == {"bend1": 0.1}

    def test_magnet_simulation_field_amplitude_is_validated(self):
        # The magnet-simulation field_amplitude is functional too, so an
        # undefined reference there is caught by validation.
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
        # no error: the reference is defined
        sl = SectionLattice(
            name="S1", order=["Q1"], elements=[q],
            functional_definitions=str(f),
        )
        assert sl.functional_definitions == {"quad1_k1l": -2.0}
