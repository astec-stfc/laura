"""Tests for laura.Exporters.YAML and laura.Importers.YAML_Loader."""

import pytest
import os
import json
import tempfile
import shutil
import yaml

from laura.models.element import (
    Quadrupole,
    Marker,
    PhysicalBaseElement,
    Dipole,
)
from laura.models.physical import Position
from laura.Exporters.YAML import (
    export_as_yaml,
    export_machine,
    export_machine_combined_file,
    export_elements,
)
from laura.Importers.YAML_Loader import (
    interpret_YAML_Element,
    read_YAML_Element_File,
    read_YAML_Combined_File,
    get_all_subclasses,
    filter_top_level,
)
from laura import LAURA


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def sample_quad():
    return Quadrupole(
        name="Q1",
        machine_area="SEC",
        magnetic={"length": 0.3, "k1l": -1.5},
        physical={"length": 0.3, "middle": {"x": 0.0, "y": 0.0, "z": 1.0}},
    )


@pytest.fixture
def sample_marker():
    return Marker(
        name="M1",
        machine_area="SEC",
        hardware_class="Marker",
        physical={"middle": {"x": 0.0, "y": 0.0, "z": 0.0}},
    )


@pytest.fixture
def small_machine(sample_quad, sample_marker):
    sections = {"sections": {"SEC": ["M1", "Q1"]}}
    layouts = {"default_layout": "beam", "layouts": {"beam": ["SEC"]}}
    return LAURA(
        element_list=[sample_marker, sample_quad],
        layout=layouts,
        section=sections,
    )


# ---------------------------------------------------------------------------
# export_as_yaml
# ---------------------------------------------------------------------------

class TestExportAsYaml:
    def test_returns_dict_when_no_filename(self, sample_quad):
        result = export_as_yaml(None, sample_quad)
        assert isinstance(result, dict)
        assert result["name"] == "Q1"
        # When no filename is given, CASCADING_RULES is included in the raw dict
        # (only the file-writing path pops it)
        assert "CASCADING_RULES" in result

    def test_writes_file(self, sample_quad, tmp_path):
        filepath = str(tmp_path / "q1.yaml")
        export_as_yaml(filepath, sample_quad)
        assert os.path.isfile(filepath)
        with open(filepath, "r") as f:
            data = yaml.safe_load(f)
        assert data["name"] == "Q1"

    def test_marker_export(self, sample_marker):
        result = export_as_yaml(None, sample_marker)
        assert result["name"] == "M1"
        assert result["hardware_type"] == "Marker"


# ---------------------------------------------------------------------------
# export_machine / export_machine_combined_file / export_elements
# ---------------------------------------------------------------------------

class TestExportMachine:
    def test_export_machine_creates_files(self, small_machine, tmp_path):
        export_path = str(tmp_path / "lattice")
        export_machine(path=export_path, machine=small_machine, overwrite=True)
        # Check that YAML files were created
        yaml_files = []
        for root, dirs, files in os.walk(export_path):
            for f in files:
                if f.endswith(".yaml"):
                    yaml_files.append(f)
        assert len(yaml_files) >= 2

    def test_export_machine_no_overwrite(self, small_machine, tmp_path):
        export_path = str(tmp_path / "lattice")
        export_machine(path=export_path, machine=small_machine, overwrite=True)
        # Export again without overwrite — files should still exist
        export_machine(path=export_path, machine=small_machine, overwrite=False)
        yaml_files = []
        for root, dirs, files in os.walk(export_path):
            for f in files:
                if f.endswith(".yaml"):
                    yaml_files.append(f)
        assert len(yaml_files) >= 2

    def test_export_machine_combined_file(self, small_machine, tmp_path):
        export_path = str(tmp_path / "combined")
        export_machine_combined_file(path=export_path, machine=small_machine)
        summary_file = os.path.join(export_path, "summary.yaml")
        assert os.path.isfile(summary_file)
        with open(summary_file, "r") as f:
            data = yaml.safe_load(f)
        assert "Q1" in data or "M1" in data

    def test_export_elements(self, sample_quad, sample_marker, tmp_path):
        export_path = str(tmp_path / "elems")
        export_elements(path=export_path, elements=[sample_quad, sample_marker])
        yaml_files = []
        for root, dirs, files in os.walk(export_path):
            for f in files:
                if f.endswith(".yaml"):
                    yaml_files.append(f)
        assert len(yaml_files) == 2


# ---------------------------------------------------------------------------
# Importers: interpret_YAML_Element
# ---------------------------------------------------------------------------

class TestInterpretYAMLElement:
    def test_interpret_quadrupole(self):
        data = {
            "name": "Q1",
            "hardware_class": "Magnet",
            "hardware_type": "Quadrupole",
            "machine_area": "SEC",
            "magnetic": {"length": 0.3, "k1l": -1.5},
            "physical": {"length": 0.3, "middle": {"x": 0.0, "y": 0.0, "z": 1.0}},
        }
        elem = interpret_YAML_Element(data)
        assert elem is not None
        assert elem.name == "Q1"
        assert elem.hardware_type == "Quadrupole"

    def test_interpret_marker(self):
        data = {
            "name": "M1",
            "hardware_class": "Marker",
            "hardware_type": "Marker",
            "machine_area": "SEC",
            "physical": {"middle": {"x": 0.0, "y": 0.0, "z": 0.0}},
        }
        elem = interpret_YAML_Element(data)
        assert elem is not None
        assert elem.hardware_type == "Marker"

    def test_interpret_no_hardware_type_returns_none(self):
        data = {"name": "X", "machine_area": "SEC"}
        assert interpret_YAML_Element(data) is None

    def test_interpret_unknown_type_returns_none(self):
        data = {"name": "X", "hardware_type": "UnknownWidgetFoo", "machine_area": "SEC"}
        assert interpret_YAML_Element(data) is None

    def test_interpret_with_exclude_set(self):
        data = {
            "name": "Q1",
            "hardware_class": "Magnet",
            "hardware_type": "Quadrupole",
            "machine_area": "SEC",
            "magnetic": {"length": 0.3},
            "physical": {"length": 0.3, "middle": {"x": 0.0, "y": 0.0, "z": 1.0}},
            "custom_field": "should_be_excluded",
        }
        elem = interpret_YAML_Element(data, exclude_set={"custom_field"})
        assert elem is not None


# ---------------------------------------------------------------------------
# Importers: read_YAML_Element_File / read_YAML_Combined_File
# ---------------------------------------------------------------------------

class TestReadYAMLFiles:
    def test_read_single_element_file(self, sample_quad, tmp_path):
        filepath = str(tmp_path / "q1.yaml")
        export_as_yaml(filepath, sample_quad)
        elem = read_YAML_Element_File(filepath)
        assert elem is not None
        assert elem.name == "Q1"

    def test_read_combined_yaml_file(self, small_machine, tmp_path):
        export_path = str(tmp_path / "combined")
        export_machine_combined_file(path=export_path, machine=small_machine)
        summary_file = os.path.join(export_path, "summary.yaml")
        elements = read_YAML_Combined_File(summary_file)
        names = [e.name for e in elements if e is not None]
        assert "Q1" in names or "M1" in names

    def test_read_combined_json_file(self, sample_quad, sample_marker, tmp_path):
        """Test reading a JSON combined file."""
        q_dict = export_as_yaml(None, sample_quad)
        m_dict = export_as_yaml(None, sample_marker)
        combined = {"Q1": q_dict, "M1": m_dict}
        filepath = str(tmp_path / "elements.json")
        with open(filepath, "w") as f:
            json.dump(combined, f)
        elements = read_YAML_Combined_File(filepath)
        names = [e.name for e in elements if e is not None]
        assert "Q1" in names

    def test_read_with_exclude_keys(self, sample_quad, tmp_path):
        filepath = str(tmp_path / "q1.yaml")
        export_as_yaml(filepath, sample_quad)
        elem = read_YAML_Element_File(filepath, exclude_keys=["controls"])
        assert elem is not None


# ---------------------------------------------------------------------------
# Utility: get_all_subclasses / filter_top_level
# ---------------------------------------------------------------------------

class TestImporterUtils:
    def test_get_all_subclasses(self):
        from pydantic import BaseModel

        subs = get_all_subclasses(BaseModel)
        assert len(subs) > 0
        # Should include our models
        class_names = {cls.__name__ for cls in subs}
        assert "Quadrupole" in class_names

    def test_filter_top_level_with_exclude(self):
        data = {"a": 1, "b": 2, "c": 3}
        result = filter_top_level(data, exclude_keys=["b"])
        assert "a" in result
        assert "b" not in result
        assert "c" in result

    def test_filter_top_level_no_exclude(self):
        data = {"a": 1, "b": 2}
        result = filter_top_level(data)
        assert result == data
