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
