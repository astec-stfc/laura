"""Tests for laura.exporters.yaml_exporter and laura.importers.yaml_loader."""

import pytest
import os
import json
import yaml

from laura.models.element import (
    Quadrupole,
    Marker,
)
from laura.exporters.yaml_exporter import (
    export_as_yaml,
    export_machine,
    export_machine_combined_file,
    export_elements,
)
from laura.importers.yaml_loader import (
    interpret_yaml_element,
    read_yaml_element_file,
    read_yaml_combined_file,
    get_all_subclasses,
    resolve_controls_schema,
)
from laura import LAURA


def _yaml_files(path):
    return [f for _, _, files in os.walk(path) for f in files if f.endswith(".yaml")]


def _quad_data(**extra):
    return {
        "name": "Q1",
        "hardware_class": "Magnet",
        "hardware_type": "Quadrupole",
        "machine_area": "SEC",
        "magnetic": {"length": 0.3, "k1l": -1.5},
        "physical": {"length": 0.3, "middle": {"x": 0.0, "y": 0.0, "z": 1.0}},
        **extra,
    }


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


class TestExportAsYaml:
    def test_returns_dict_when_no_filename(self, sample_quad):
        result = export_as_yaml(None, sample_quad)
        assert isinstance(result, dict)
        assert result["name"] == "Q1"
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


class TestExportMachine:
    def test_export_machine_creates_files(self, small_machine, tmp_path):
        export_path = str(tmp_path / "lattice")
        export_machine(path=export_path, machine=small_machine, overwrite=True)
        assert len(_yaml_files(export_path)) >= 2
        export_machine(path=export_path, machine=small_machine, overwrite=False)
        assert len(_yaml_files(export_path)) >= 2

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
        assert len(_yaml_files(export_path)) == 2


class TestInterpretYAMLElement:
    def test_interpret_quadrupole(self):
        elem = interpret_yaml_element(_quad_data())
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
        elem = interpret_yaml_element(data)
        assert elem is not None
        assert elem.hardware_type == "Marker"

    def test_interpret_no_hardware_type_returns_none(self):
        data = {"name": "X", "machine_area": "SEC"}
        assert interpret_yaml_element(data) is None

    def test_interpret_unknown_type_returns_none(self):
        data = {"name": "X", "hardware_type": "UnknownWidgetFoo", "machine_area": "SEC"}
        assert interpret_yaml_element(data) is None

    def test_interpret_with_exclude_set(self):
        data = _quad_data(custom_field="should_be_excluded")
        elem = interpret_yaml_element(data, exclude_set={"custom_field"})
        assert elem is not None


class TestReadYAMLFiles:
    def test_read_single_element_file(self, sample_quad, tmp_path):
        filepath = str(tmp_path / "q1.yaml")
        export_as_yaml(filepath, sample_quad)
        elem = read_yaml_element_file(filepath)
        assert elem is not None
        assert elem.name == "Q1"

    def test_read_combined_yaml_file(self, small_machine, tmp_path):
        export_path = str(tmp_path / "combined")
        export_machine_combined_file(path=export_path, machine=small_machine)
        summary_file = os.path.join(export_path, "summary.yaml")
        elements = read_yaml_combined_file(summary_file)
        names = [e.name for e in elements if e is not None]
        assert "Q1" in names or "M1" in names

    def test_read_combined_json_file(self, sample_quad, sample_marker, tmp_path):
        q_dict = export_as_yaml(None, sample_quad)
        m_dict = export_as_yaml(None, sample_marker)
        combined = {"Q1": q_dict, "M1": m_dict}
        filepath = str(tmp_path / "elements.json")
        with open(filepath, "w") as f:
            json.dump(combined, f)
        elements = read_yaml_combined_file(filepath)
        names = [e.name for e in elements if e is not None]
        assert "Q1" in names

    def test_read_with_exclude_keys(self, sample_quad, tmp_path):
        filepath = str(tmp_path / "q1.yaml")
        export_as_yaml(filepath, sample_quad)
        elem = read_yaml_element_file(filepath, exclude_keys=["controls"])
        assert elem is not None


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
        (tmp_path / "quad_schema.yaml").write_text(QUAD_SCHEMA_YAML)
        controls = {"schema": "quad_schema.yaml"}
        resolved = resolve_controls_schema(controls, "Q1", base_dir=str(tmp_path))
        assert resolved["variables"]["READI"]["identifier"] == "Q1:READI"
        assert resolved["variables"]["SETI"]["identifier"] == "Q1:SETI"
        assert resolved["variables"]["SETI"]["readback"] == "READI"

    def test_resolve_controls_schema_field_override(self, tmp_path):
        (tmp_path / "quad_schema.yaml").write_text(QUAD_SCHEMA_YAML)
        controls = {
            "schema": "quad_schema.yaml",
            "variables": {"SETI": {"description": "Custom override"}},
        }
        resolved = resolve_controls_schema(controls, "Q1", base_dir=str(tmp_path))
        assert resolved["variables"]["SETI"]["description"] == "Custom override"
        assert resolved["variables"]["SETI"]["identifier"] == "Q1:SETI"
        assert resolved["variables"]["SETI"]["readback"] == "READI"

    def test_resolve_controls_schema_new_variable(self, tmp_path):
        (tmp_path / "quad_schema.yaml").write_text(QUAD_SCHEMA_YAML)
        controls = {
            "schema": "quad_schema.yaml",
            "variables": {"EXTRA": {"identifier": "Q1:EXTRA", "protocol": "CA"}},
        }
        resolved = resolve_controls_schema(controls, "Q1", base_dir=str(tmp_path))
        assert resolved["variables"]["EXTRA"]["identifier"] == "Q1:EXTRA"
        assert "READI" in resolved["variables"]

    def test_resolve_controls_schema_identifier_pattern_override(self, tmp_path):
        (tmp_path / "quad_schema.yaml").write_text(QUAD_SCHEMA_YAML)
        controls = {"schema": "quad_schema.yaml", "identifier_pattern": "Q_SHARED"}
        resolved = resolve_controls_schema(controls, "Q1", base_dir=str(tmp_path))
        assert resolved["variables"]["READI"]["identifier"] == "Q_SHARED:READI"
        assert resolved["variables"]["SETI"]["identifier"] == "Q_SHARED:SETI"
        assert resolved["identifier_pattern"] == "Q_SHARED"

    def test_interpret_yaml_element_identifier_pattern(self, tmp_path):
        (tmp_path / "quad_schema.yaml").write_text(QUAD_SCHEMA_YAML)
        data = _quad_data(
            name="Q5", controls={"schema": "quad_schema.yaml", "identifier_pattern": "Q1"}
        )
        elem = interpret_yaml_element(data, base_dir=str(tmp_path))
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
        (tmp_path / "quad_schema.yaml").write_text(QUAD_SCHEMA_YAML)
        data = _quad_data(controls={"schema": "quad_schema.yaml"})
        elem = interpret_yaml_element(data, base_dir=str(tmp_path))
        assert elem is not None
        assert elem.controls.variables["SETI"].identifier == "Q1:SETI"
        assert elem.controls.variables["READI"].identifier == "Q1:READI"
        assert elem.controls.schema_ == "quad_schema.yaml"

    def test_read_yaml_element_file_resolves_schema_relative_to_file(self, tmp_path):
        (tmp_path / "quad_schema.yaml").write_text(QUAD_SCHEMA_YAML)
        element_file = tmp_path / "Q1.yaml"
        element_file.write_text(yaml.dump(_quad_data(controls={"schema": "quad_schema.yaml"})))
        elem = read_yaml_element_file(str(element_file))
        assert elem.controls.variables["SETI"].identifier == "Q1:SETI"


class TestControlsSchemaExport:
    OVERRIDE = {"variables": {"SETI": {"description": "Custom override"}}}

    def _make_quad(self, schema_dir, extra_controls=None):
        schema_dir.mkdir(parents=True, exist_ok=True)
        (schema_dir / "_schema.yaml").write_text(QUAD_SCHEMA_YAML)
        controls = {"schema": "_schema.yaml", **(extra_controls or {})}
        return interpret_yaml_element(_quad_data(controls=controls), base_dir=str(schema_dir))

    def test_export_as_yaml_collapses_to_schema(self, tmp_path):
        schema_root = tmp_path / "root"
        elem = self._make_quad(schema_root / "Magnet" / "Quadrupole", self.OVERRIDE)
        dump = export_as_yaml(None, elem, collapse_schema=True, schema_root=str(schema_root))
        assert dump["controls"]["schema"] == "_schema.yaml"
        assert dump["controls"]["variables"] == self.OVERRIDE["variables"]

    def test_export_as_yaml_without_collapse_is_fully_expanded(self, tmp_path):
        elem = self._make_quad(tmp_path / "root" / "Magnet" / "Quadrupole")
        dump = export_as_yaml(None, elem, collapse_schema=False)
        assert "READI" in dump["controls"]["variables"]
        assert "SETI" in dump["controls"]["variables"]

    def test_export_as_yaml_falls_back_when_schema_missing(self, tmp_path):
        elem = self._make_quad(tmp_path / "root" / "Magnet" / "Quadrupole")
        dump = export_as_yaml(None, elem, collapse_schema=True, schema_root=str(tmp_path / "nowhere"))
        assert "schema" not in dump["controls"]
        assert "READI" in dump["controls"]["variables"]

    def test_export_elements_collapses_and_copies_schema(self, tmp_path):
        schema_root = tmp_path / "root"
        elem = self._make_quad(schema_root / "Magnet" / "Quadrupole", self.OVERRIDE)
        dest = tmp_path / "dest"
        export_elements(str(dest), [elem], collapse_schema=True, schema_root=str(schema_root))
        assert (dest / "Magnet" / "Quadrupole" / "_schema.yaml").exists()
        reloaded = read_yaml_element_file(str(dest / "Magnet" / "Quadrupole" / "Q1.yaml"))
        assert reloaded.controls.variables["SETI"].description == "Custom override"
        assert reloaded.controls.variables["READI"].identifier == "Q1:READI"

    def test_export_elements_accepts_flat_schema_root(self, tmp_path):
        elem = self._make_quad(tmp_path)
        dest = tmp_path / "dest"

        export_elements(str(dest), [elem], collapse_schema=True, schema_root=str(tmp_path))

        output_dir = dest / "Magnet" / "Quadrupole"
        assert (output_dir / "_schema.yaml").exists()
        assert "schema" in yaml.safe_load((output_dir / "Q1.yaml").read_text())["controls"]

    def test_combined_export_embeds_schema_and_is_standalone(self, tmp_path):
        schema_root = tmp_path / "root"
        elem = self._make_quad(schema_root / "Magnet" / "Quadrupole", self.OVERRIDE)
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
        assert raw["Q1"]["controls"]["variables"] == self.OVERRIDE["variables"]

        # No companion schema file: must resolve from the embedded `_schemas`.
        elems = read_yaml_combined_file(str(combined_file))
        reloaded = next(e for e in elems if e is not None)
        assert reloaded.controls.variables["SETI"].description == "Custom override"
        assert reloaded.controls.variables["READI"].identifier == "Q1:READI"


class TestImporterUtils:
    def test_get_all_subclasses(self):
        from pydantic import BaseModel

        subs = get_all_subclasses(BaseModel)
        assert len(subs) > 0
        class_names = {cls.__name__ for cls in subs}
        assert "Quadrupole" in class_names

