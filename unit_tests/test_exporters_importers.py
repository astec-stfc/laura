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
    resolve_controls_schema,
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
        # CASCADING_RULES is stripped from exported data
        assert "CASCADING_RULES" not in result

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
# Importers: controls schema expansion
# ---------------------------------------------------------------------------

QUAD_SCHEMA_YAML = """
variables:
  READI:
    description: Gets the readback current of a magnet power supply.
    dtype: float
    identifier: "{name}:READI"
    protocol: CA
    type: statistical
    units: A
  SETI:
    description: Sets the target current for a magnet power supply.
    dtype: float
    identifier: "{name}:SETI"
    protocol: CA
    read_only: false
    readback: READI
    type: scalar
    units: A
"""


class TestControlsSchema:
    def test_resolve_controls_schema_fills_in_identifier(self, tmp_path):
        schema_file = tmp_path / "quad_schema.yaml"
        schema_file.write_text(QUAD_SCHEMA_YAML)
        controls = {"schema": "quad_schema.yaml"}
        resolved = resolve_controls_schema(controls, "Q1", base_dir=str(tmp_path))
        assert resolved["variables"]["READI"]["identifier"] == "Q1:READI"
        assert resolved["variables"]["SETI"]["identifier"] == "Q1:SETI"
        assert resolved["variables"]["SETI"]["readback"] == "READI"

    def test_resolve_controls_schema_field_override(self, tmp_path):
        schema_file = tmp_path / "quad_schema.yaml"
        schema_file.write_text(QUAD_SCHEMA_YAML)
        controls = {
            "schema": "quad_schema.yaml",
            "variables": {"SETI": {"description": "Custom override"}},
        }
        resolved = resolve_controls_schema(controls, "Q1", base_dir=str(tmp_path))
        # Overridden field changes...
        assert resolved["variables"]["SETI"]["description"] == "Custom override"
        # ...but the rest of the templated entry survives.
        assert resolved["variables"]["SETI"]["identifier"] == "Q1:SETI"
        assert resolved["variables"]["SETI"]["readback"] == "READI"

    def test_resolve_controls_schema_new_variable(self, tmp_path):
        schema_file = tmp_path / "quad_schema.yaml"
        schema_file.write_text(QUAD_SCHEMA_YAML)
        controls = {
            "schema": "quad_schema.yaml",
            "variables": {"EXTRA": {"identifier": "Q1:EXTRA", "protocol": "CA"}},
        }
        resolved = resolve_controls_schema(controls, "Q1", base_dir=str(tmp_path))
        assert resolved["variables"]["EXTRA"]["identifier"] == "Q1:EXTRA"
        assert "READI" in resolved["variables"]

    def test_resolve_controls_schema_identifier_pattern_override(self, tmp_path):
        schema_file = tmp_path / "quad_schema.yaml"
        schema_file.write_text(QUAD_SCHEMA_YAML)
        controls = {"schema": "quad_schema.yaml", "identifier_pattern": "Q_SHARED"}
        resolved = resolve_controls_schema(controls, "Q1", base_dir=str(tmp_path))
        # Substitution uses identifier_pattern, not the element's own name.
        assert resolved["variables"]["READI"]["identifier"] == "Q_SHARED:READI"
        assert resolved["variables"]["SETI"]["identifier"] == "Q_SHARED:SETI"
        assert resolved["identifier_pattern"] == "Q_SHARED"

    def test_interpret_yaml_element_identifier_pattern(self, tmp_path):
        schema_file = tmp_path / "quad_schema.yaml"
        schema_file.write_text(QUAD_SCHEMA_YAML)
        data = {
            "name": "Q5",
            "hardware_class": "Magnet",
            "hardware_type": "Quadrupole",
            "machine_area": "SEC",
            "magnetic": {"length": 0.3, "k1l": -1.5},
            "physical": {"length": 0.3, "middle": {"x": 0.0, "y": 0.0, "z": 1.0}},
            "controls": {"schema": "quad_schema.yaml", "identifier_pattern": "Q1"},
        }
        elem = interpret_YAML_Element(data, base_dir=str(tmp_path))
        assert elem.controls.variables["READI"].identifier == "Q1:READI"
        assert elem.controls.identifier_pattern == "Q1"

    def test_resolve_controls_schema_missing_file_raises(self, tmp_path):
        controls = {"schema": "does_not_exist.yaml"}
        with pytest.raises(FileNotFoundError):
            resolve_controls_schema(controls, "Q1", base_dir=str(tmp_path))

    def test_resolve_controls_schema_noop_without_schema_key(self):
        controls = {"variables": {"X": {"identifier": "foo", "protocol": "CA"}}}
        assert resolve_controls_schema(controls, "Q1") == controls

    def test_interpret_yaml_element_expands_schema(self, tmp_path):
        schema_file = tmp_path / "quad_schema.yaml"
        schema_file.write_text(QUAD_SCHEMA_YAML)
        data = {
            "name": "Q1",
            "hardware_class": "Magnet",
            "hardware_type": "Quadrupole",
            "machine_area": "SEC",
            "magnetic": {"length": 0.3, "k1l": -1.5},
            "physical": {"length": 0.3, "middle": {"x": 0.0, "y": 0.0, "z": 1.0}},
            "controls": {"schema": "quad_schema.yaml"},
        }
        elem = interpret_YAML_Element(data, base_dir=str(tmp_path))
        assert elem is not None
        assert elem.controls.variables["SETI"].identifier == "Q1:SETI"
        assert elem.controls.variables["READI"].identifier == "Q1:READI"
        assert elem.controls.schema_ == "quad_schema.yaml"

    def test_read_yaml_element_file_resolves_schema_relative_to_file(self, tmp_path):
        schema_file = tmp_path / "quad_schema.yaml"
        schema_file.write_text(QUAD_SCHEMA_YAML)
        element_file = tmp_path / "Q1.yaml"
        yaml.dump(
            {
                "name": "Q1",
                "hardware_class": "Magnet",
                "hardware_type": "Quadrupole",
                "machine_area": "SEC",
                "magnetic": {"length": 0.3, "k1l": -1.5},
                "physical": {"length": 0.3, "middle": {"x": 0.0, "y": 0.0, "z": 1.0}},
                "controls": {"schema": "quad_schema.yaml"},
            },
            element_file.open("w"),
        )
        elem = read_YAML_Element_File(str(element_file))
        assert elem.controls.variables["SETI"].identifier == "Q1:SETI"


# ---------------------------------------------------------------------------
# Exporters: collapse_schema
# ---------------------------------------------------------------------------

class TestControlsSchemaExport:
    def _make_quad(self, schema_dir, tmp_path, extra_controls=None):
        schema_dir.mkdir(parents=True, exist_ok=True)
        (schema_dir / "_schema.yaml").write_text(QUAD_SCHEMA_YAML)
        controls = {"schema": "_schema.yaml"}
        if extra_controls:
            controls.update(extra_controls)
        data = {
            "name": "Q1",
            "hardware_class": "Magnet",
            "hardware_type": "Quadrupole",
            "machine_area": "SEC",
            "magnetic": {"length": 0.3, "k1l": -1.5},
            "physical": {"length": 0.3, "middle": {"x": 0.0, "y": 0.0, "z": 1.0}},
            "controls": controls,
        }
        return interpret_YAML_Element(data, base_dir=str(schema_dir))

    def test_export_as_yaml_collapses_to_schema(self, tmp_path):
        schema_root = tmp_path / "root"
        schema_dir = schema_root / "Magnet" / "Quadrupole"
        elem = self._make_quad(
            schema_dir, tmp_path,
            extra_controls={"variables": {"SETI": {"description": "Custom override"}}},
        )
        dump = export_as_yaml(None, elem, collapse_schema=True, schema_root=str(schema_root))
        assert dump["controls"]["schema"] == "_schema.yaml"
        assert dump["controls"]["variables"] == {"SETI": {"description": "Custom override"}}

    def test_export_as_yaml_without_collapse_is_fully_expanded(self, tmp_path):
        schema_root = tmp_path / "root"
        schema_dir = schema_root / "Magnet" / "Quadrupole"
        elem = self._make_quad(schema_dir, tmp_path)
        dump = export_as_yaml(None, elem, collapse_schema=False)
        assert "READI" in dump["controls"]["variables"]
        assert "SETI" in dump["controls"]["variables"]

    def test_export_as_yaml_falls_back_when_schema_missing(self, tmp_path):
        schema_root = tmp_path / "root"
        schema_dir = schema_root / "Magnet" / "Quadrupole"
        elem = self._make_quad(schema_dir, tmp_path)
        # Point schema_root somewhere that has no matching schema file.
        dump = export_as_yaml(None, elem, collapse_schema=True, schema_root=str(tmp_path / "nowhere"))
        assert "schema" not in dump["controls"]
        assert "READI" in dump["controls"]["variables"]

    def test_export_elements_collapses_and_copies_schema(self, tmp_path):
        schema_root = tmp_path / "root"
        schema_dir = schema_root / "Magnet" / "Quadrupole"
        elem = self._make_quad(
            schema_dir, tmp_path,
            extra_controls={"variables": {"SETI": {"description": "Custom override"}}},
        )
        dest = tmp_path / "dest"
        export_elements(str(dest), [elem], collapse_schema=True, schema_root=str(schema_root))
        assert (dest / "Magnet" / "Quadrupole" / "_schema.yaml").exists()
        reloaded = read_YAML_Element_File(str(dest / "Magnet" / "Quadrupole" / "Q1.yaml"))
        assert reloaded.controls.variables["SETI"].description == "Custom override"
        assert reloaded.controls.variables["READI"].identifier == "Q1:READI"

    def test_combined_export_embeds_schema_and_is_standalone(self, tmp_path):
        schema_root = tmp_path / "root"
        schema_dir = schema_root / "Magnet" / "Quadrupole"
        elem = self._make_quad(
            schema_dir, tmp_path,
            extra_controls={"variables": {"SETI": {"description": "Custom override"}}},
        )
        sections = {"sections": {"SEC": ["Q1"]}}
        layouts = {"default_layout": "beam", "layouts": {"beam": ["SEC"]}}
        machine = LAURA(element_list=[elem], layout=layouts, section=sections)

        combined_dir = tmp_path / "combined"
        export_machine_combined_file(
            str(combined_dir), machine, collapse_schema=True, schema_root=str(schema_root)
        )
        combined_file = combined_dir / "summary.yaml"
        with open(combined_file) as f:
            raw = yaml.safe_load(f)
        assert "_schemas" in raw
        assert raw["Q1"]["controls"]["variables"] == {"SETI": {"description": "Custom override"}}

        # No companion schema file present -- must resolve purely from the
        # embedded `_schemas` section.
        elems = read_YAML_Combined_File(str(combined_file))
        reloaded = next(e for e in elems if e is not None)
        assert reloaded.controls.variables["SETI"].description == "Custom override"
        assert reloaded.controls.variables["READI"].identifier == "Q1:READI"


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
