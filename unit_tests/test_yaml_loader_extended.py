import os
from unittest.mock import patch

import pytest
import yaml

from laura.models.element import Quadrupole, Marker, ELEMENT_REGISTRY
from laura.exporters.yaml_exporter import export_as_yaml, export_machine_combined_file
from laura.importers.yaml_loader import (
    fast_get_element_metadata,
    LazyElementDict,
    LazyAdapterDict,
    interpret_yaml_element,
    read_yaml_element_file,
    read_yaml_element_files,
    read_yaml_combined_file,
    validate_element_dict,
    _get_json_schema,
)
from laura import LAURA


def _write_element_yaml(directory: str, element) -> str:
    filepath = os.path.join(directory, f"{element.name}.yaml")
    export_as_yaml(filepath, element)
    return filepath


def _write_raw(path, data) -> str:
    path.write_text(yaml.dump(data))
    return str(path)


def _make_quad(name="Q1", machine_area="SEC", k1l=-1.0) -> Quadrupole:
    return Quadrupole(
        name=name,
        machine_area=machine_area,
        magnetic={"length": 0.3, "k1l": k1l},
        physical={"length": 0.3, "middle": {"x": 0.0, "y": 0.0, "z": 1.0}},
    )


def _make_marker(name="M1", machine_area="SEC") -> Marker:
    return Marker(
        name=name,
        machine_area=machine_area,
        hardware_class="Marker",
        physical={"middle": {"x": 0.0, "y": 0.0, "z": 0.0}},
    )


class TestFastGetElementMetadata:
    @pytest.mark.parametrize(
        "element",
        [_make_quad(name="QA", machine_area="INJECT"), _make_marker(name="M5", machine_area="BA1")],
        ids=["quad", "marker"],
    )
    def test_extracts_name_and_machine_area(self, tmp_path, element):
        meta = fast_get_element_metadata(_write_element_yaml(str(tmp_path), element))
        assert meta["name"] == element.name
        assert meta["machine_area"] == element.machine_area

    def test_falls_back_to_filename_when_name_missing(self, tmp_path):
        fpath = _write_raw(tmp_path / "MY_ELEMENT.yaml", {"hardware_type": "Quadrupole", "machine_area": "X"})
        meta = fast_get_element_metadata(fpath)
        assert meta["name"] == "MY_ELEMENT"

    def test_machine_area_is_none_when_absent(self, tmp_path):
        fpath = _write_raw(tmp_path / "bare.yaml", {"name": "bare_elem", "hardware_type": "Quadrupole"})
        meta = fast_get_element_metadata(fpath)
        assert meta["machine_area"] is None

    def test_gracefully_handles_nonexistent_file(self):
        meta = fast_get_element_metadata("/no/such/file/element.yaml")
        assert meta["name"] == "element"

    def test_keeps_a_hash_inside_a_name(self, tmp_path):
        """``#`` is a comment only after whitespace; Bmad names split pieces ``Q#1``."""
        q = _make_quad(name="QM01#1", machine_area="LI21")
        fpath = _write_element_yaml(str(tmp_path), q)
        meta = fast_get_element_metadata(fpath)
        assert meta["name"] == "QM01#1"

    def test_two_hashed_names_stay_distinct_in_a_lattice(self, tmp_path):
        for name in ("QM01#1", "QM01#2"):
            _write_element_yaml(str(tmp_path), _make_quad(name=name, machine_area="LI21"))
        machine = LAURA(
            element_list=str(tmp_path),
            section={"sections": {"LI21": ["QM01#1", "QM01#2"]}},
            layout={"layouts": {"line": ["LI21"]}, "default_layout": "line"},
        )
        assert set(machine.elements) == {"QM01#1", "QM01#2"}

    def test_strips_a_real_trailing_comment(self, tmp_path):
        fpath = tmp_path / "commented.yaml"
        fpath.write_text("name: QX  # the horizontal one\nmachine_area: S01  # injector\n")
        meta = fast_get_element_metadata(str(fpath))
        assert meta["name"] == "QX"
        assert meta["machine_area"] == "S01"

    def test_unquotes_a_quoted_name(self, tmp_path):
        fpath = tmp_path / "quoted.yaml"
        fpath.write_text('name: "Q#1"\nmachine_area: \'S01\'\n')
        meta = fast_get_element_metadata(str(fpath))
        assert meta["name"] == "Q#1"
        assert meta["machine_area"] == "S01"


class TestLazyElementDict:
    def _build(self, tmp_path):
        q = _make_quad("Q1", "SEC")
        m = _make_marker("M1", "SEC")
        fq = _write_element_yaml(str(tmp_path), q)
        fm = _write_element_yaml(str(tmp_path), m)
        filenames = {"Q1": fq, "M1": fm}
        return LazyElementDict(filenames), filenames

    def test_keys_known_before_loading(self, tmp_path):
        d, _ = self._build(tmp_path)
        assert len(d) == 2
        assert "Q1" in d.keys()
        assert "M1" in d.keys()
        assert "Q1" in d
        assert "M1" in d
        assert "UNKNOWN_ELEM" not in d
        assert set(d) == {"Q1", "M1"}

    def test_getitem_loads_and_caches_element(self, tmp_path):
        d, _ = self._build(tmp_path)
        elem = d["Q1"]
        assert elem is not None
        assert elem.name == "Q1"
        assert elem.hardware_type == "Quadrupole"
        assert d["Q1"] is elem

    def test_getitem_unknown_key_raises(self, tmp_path):
        d, _ = self._build(tmp_path)
        with pytest.raises(KeyError):
            _ = d["DOES_NOT_EXIST"]

    def test_get(self, tmp_path):
        d, _ = self._build(tmp_path)
        assert d.get("MISSING", "default_value") == "default_value"
        result = d.get("M1")
        assert result is not None
        assert result.name == "M1"

    def test_values_loads_all_elements(self, tmp_path):
        d, _ = self._build(tmp_path)
        all_elements = list(d.values())
        names = {e.name for e in all_elements if e is not None}
        assert names == {"Q1", "M1"}

    def test_is_loaded_returns_true_after_init(self, tmp_path):
        """Keys are placed in the dict at init time, with None values."""
        d, _ = self._build(tmp_path)
        assert d.is_loaded("Q1") is True

    def test_get_metadata_returns_name_and_area(self, tmp_path):
        d, _ = self._build(tmp_path)
        _ = d["Q1"]
        meta = d.get_metadata("Q1")
        assert meta is not None
        assert meta["name"] == "Q1"
        assert meta["machine_area"] == "SEC"

    def test_get_metadata_none_for_unknown_key(self, tmp_path):
        d, _ = self._build(tmp_path)
        assert d.get_metadata("TOTALLY_UNKNOWN") is None

    def test_get_all_metadata_returns_all_entries(self, tmp_path):
        d, _ = self._build(tmp_path)
        _ = d["Q1"]
        _ = d["M1"]
        all_meta = d.get_all_metadata()
        assert isinstance(all_meta, dict)
        assert set(all_meta.keys()) == {"Q1", "M1"}
        assert all_meta["Q1"]["name"] == "Q1"
        assert all_meta["M1"]["machine_area"] == "SEC"

    def test_empty_dict(self):
        d = LazyElementDict({})
        assert len(d) == 0
        assert list(d) == []
        assert d.get("anything") is None


class TestLazyAdapterDict:
    def test_get_known_type_returns_cached_adapter(self):
        d = LazyAdapterDict()
        adapter = d.get("Quadrupole")
        assert adapter is not None
        assert callable(adapter.validate_python)
        assert d.get("Quadrupole") is adapter

    def test_get_unknown_type_returns_default(self):
        d = LazyAdapterDict()
        assert d.get("CompletelyUnknownType12345") is None
        sentinel = object()
        assert d.get("CompletelyUnknownType12345", sentinel) is sentinel

    def test_all_registered_models_have_adapters(self):
        d = LazyAdapterDict()
        for name in list(ELEMENT_REGISTRY.keys())[:5]:  # sample first 5 to keep test fast
            adapter = d.get(name)
            assert adapter is not None, f"Missing adapter for {name}"

    def test_adapter_validates_correct_data(self):
        d = LazyAdapterDict()
        adapter = d.get("Marker")
        assert adapter is not None
        elem = adapter.validate_python({
            "name": "T1",
            "hardware_type": "Marker",
            "hardware_class": "Marker",
            "machine_area": "X",
            "physical": {"middle": {"x": 0.0, "y": 0.0, "z": 0.0}},
        })
        assert elem.name == "T1"


class TestValidateElementDict:
    def _valid_quad_dict(self):
        return {
            "name": "QV",
            "hardware_type": "Quadrupole",
            "hardware_class": "Magnet",
            "machine_area": "SEC",
            "magnetic": {"length": 0.3, "k1l": -1.5},
            "physical": {"length": 0.3, "middle": {"x": 0.0, "y": 0.0, "z": 1.0}},
        }

    def test_base_class_element_passes(self):
        """The root schema requires only name and hardware_class."""
        pytest.importorskip("jsonschema")
        base_elem = {"name": "BASE_ELEM", "hardware_class": "Generic", "hardware_type": "AcceleratorElement"}
        validate_element_dict(base_elem)

    def test_concrete_hardware_type_with_hardware_class_passes(self):
        pytest.importorskip("jsonschema")
        validate_element_dict(self._valid_quad_dict())

    def test_missing_hardware_class_raises_validation_error(self):
        jsonschema = pytest.importorskip("jsonschema")
        bad = {"name": "QV", "hardware_type": "Quadrupole"}
        with pytest.raises(jsonschema.ValidationError):
            validate_element_dict(bad)

    def test_missing_required_name_raises_validation_error(self):
        jsonschema = pytest.importorskip("jsonschema")
        bad = {"hardware_type": "AcceleratorElement"}
        with pytest.raises(jsonschema.ValidationError):
            validate_element_dict(bad)

    def test_missing_jsonschema_raises_import_error(self):
        with patch.dict("sys.modules", {"jsonschema": None}):
            with pytest.raises(ImportError, match="jsonschema"):
                validate_element_dict(self._valid_quad_dict())

    def test_missing_schema_file_raises_file_not_found(self, tmp_path):
        from laura.importers import yaml_loader as loader_mod
        original_path = loader_mod._SCHEMA_PATH
        loader_mod._get_json_schema.cache_clear()
        try:
            loader_mod._SCHEMA_PATH = tmp_path / "does_not_exist.json"
            with pytest.raises(FileNotFoundError, match="LAURA JSON Schema"):
                loader_mod._get_json_schema()
        finally:
            loader_mod._SCHEMA_PATH = original_path
            loader_mod._get_json_schema.cache_clear()

    def test_schema_is_cached_after_first_load(self):
        schema1 = _get_json_schema()
        schema2 = _get_json_schema()
        assert schema1 is schema2


class TestReadYAMLElementFileWithValidation:
    def test_real_element_file_passes_with_validate_true(self, tmp_path):
        q = _make_quad("QV", "SEC")
        fpath = _write_element_yaml(str(tmp_path), q)
        pytest.importorskip("jsonschema")
        elem = read_yaml_element_file(fpath, validate=True)
        assert elem is not None

    def test_validate_false_reads_element_successfully(self, tmp_path):
        q = _make_quad("QV2", "SEC")
        fpath = _write_element_yaml(str(tmp_path), q)
        elem = read_yaml_element_file(fpath, validate=False)
        assert elem is not None
        assert elem.name == "QV2"

    def test_validate_false_does_not_raise_on_unknown_type(self, tmp_path):
        bad_path = _write_raw(tmp_path / "bad.yaml", {"name": "BAD", "hardware_type": "NONESUCH_XYZ123"})
        result = read_yaml_element_file(bad_path, validate=False)
        assert result is None


class TestReadYAMLCombinedFileWithValidation:
    @staticmethod
    def _summary(tmp_path):
        sections = {"sections": {"SEC": ["MC", "QC"]}}
        layouts = {"default_layout": "beam", "layouts": {"beam": ["SEC"]}}
        machine = LAURA(element_list=[_make_marker("MC", "SEC"), _make_quad("QC", "SEC")], layout=layouts, section=sections)
        export_path = str(tmp_path / "combined")
        export_machine_combined_file(path=export_path, machine=machine)
        return os.path.join(export_path, "summary.yaml")

    def test_real_combined_file_passes_with_validate_true(self, tmp_path):
        pytest.importorskip("jsonschema")
        summary = self._summary(tmp_path)
        elements = read_yaml_combined_file(summary, validate=True)
        assert len(elements) > 0

    def test_combined_file_loads_without_validation(self, tmp_path):
        elements = read_yaml_combined_file(self._summary(tmp_path), validate=False)
        names = [e.name for e in elements if e is not None]
        assert "QC" in names or "MC" in names

    def test_missing_name_raises_in_combined_file_validate(self, tmp_path):
        jsonschema = pytest.importorskip("jsonschema")
        bad_path = _write_raw(tmp_path / "bad.yaml", {"elem1": {"hardware_type": "AcceleratorElement"}})
        with pytest.raises(jsonschema.ValidationError):
            read_yaml_combined_file(bad_path, validate=True)


class TestReadYAMLElementFiles:
    def test_returns_raw_dicts_and_filenames(self, tmp_path):
        elements = [_make_quad(f"Q{i}", "S01") for i in range(3)] + [_make_marker("MF", "SEC")]
        fpaths = [_write_element_yaml(str(tmp_path), e) for e in elements]
        dicts, filenames = read_yaml_element_files(fpaths)
        assert isinstance(dicts, list)
        assert isinstance(filenames, list)
        assert len(filenames) == 4
        # the first document of a '---'-split YAML may be empty
        non_none = [d for d in dicts if d is not None]
        assert all(isinstance(d, dict) for d in non_none)
        names = {d.get("name") for d in non_none}
        assert {e.name for e in elements} <= names


class TestElementListDirectoryScan:
    """Aggregate files beside per-element files must not load as elements."""

    @staticmethod
    def _machine(directory):
        return LAURA(
            element_list=str(directory),
            layout={"default_layout": "line1", "layouts": {"line1": ["SEC"]}},
            section={"sections": {"SEC": ["Q1"]}},
        )

    def test_summary_file_is_not_loaded_as_an_element(self, tmp_path):
        _write_element_yaml(str(tmp_path), _make_quad(name="Q1"))
        _write_raw(tmp_path / "summary.yaml", {"Q1": {"name": "Q1", "hardware_type": "Quadrupole"}})

        machine = self._machine(tmp_path)

        assert "Q1" in machine.elements
        # no top-level name, so it would be keyed by its basename
        assert "summary" not in machine.elements

    def test_real_elements_are_still_found_beside_a_summary(self, tmp_path):
        for name in ["Q1", "Q2", "Q3"]:
            _write_element_yaml(str(tmp_path), _make_quad(name=name))
        _write_raw(tmp_path / "summary.yaml", {"anything": 1})

        machine = self._machine(tmp_path)

        assert {"Q1", "Q2", "Q3"}.issubset(set(machine.elements))
        assert len([k for k in machine.elements if k.startswith("summary")]) == 0


class TestControlsSchemaDirectory:
    """Schemas sit beside the elements, in ``<hardware_class>/<hardware_type>/``."""

    @staticmethod
    def _raw_quad():
        return {
            "name": "Q1",
            "hardware_class": "Magnet",
            "hardware_type": "Quadrupole",
            "machine_area": "SEC",
            "controls": {"identifier_pattern": "QUAD:SEC:1", "schema": "Quadrupole_schema.yaml"},
        }

    @staticmethod
    def _write_schema(directory):
        directory.mkdir(parents=True, exist_ok=True)
        schema = {"variables": {"bact": {"identifier": "{name}:BACT", "dtype": "float",
                                         "protocol": "CA", "type": "scalar"}}}
        (directory / "Quadrupole_schema.yaml").write_text(yaml.safe_dump(schema))

    def test_schema_in_the_type_directory_is_found(self, tmp_path):
        self._write_schema(tmp_path / "Magnet" / "Quadrupole")
        elem = interpret_yaml_element(self._raw_quad(), base_dir=str(tmp_path), strict=True)
        assert "bact" in elem.controls.variables

    def test_schema_beside_the_file_takes_precedence(self, tmp_path):
        self._write_schema(tmp_path)
        (tmp_path / "Magnet" / "Quadrupole").mkdir(parents=True)
        elem = interpret_yaml_element(self._raw_quad(), base_dir=str(tmp_path), strict=True)
        assert "bact" in elem.controls.variables
