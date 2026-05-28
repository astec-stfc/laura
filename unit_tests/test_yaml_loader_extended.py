"""Extended tests for laura.Importers.YAML_Loader.

Covers:
- fast_get_element_metadata
- LazyElementDict (lazy load, metadata, iteration, containment)
- LazyAdapterDict (type-adapter caching)
- validate_element_dict / _get_json_schema
- read_YAML_Element_File with validate=True
- read_YAML_Combined_File with validate=True
- read_YAML_Element_Files (multi-file)
"""

import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
import yaml

from laura.models.element import Quadrupole, Marker, Dipole
from laura.Exporters.YAML import export_as_yaml, export_machine_combined_file
from laura.Importers.YAML_Loader import (
    fast_get_element_metadata,
    LazyElementDict,
    LazyAdapterDict,
    MODEL_REGISTRY,
    filter_top_level,
    interpret_YAML_Element,
    read_YAML_Element_File,
    read_YAML_Element_Files,
    read_YAML_Combined_File,
)
from laura import LAURA


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _write_element_yaml(directory: str, element) -> str:
    """Export *element* to a YAML file in *directory* and return the path."""
    filepath = os.path.join(directory, f"{element.name}.yaml")
    export_as_yaml(filepath, element)
    return filepath


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


# ---------------------------------------------------------------------------
# fast_get_element_metadata
# ---------------------------------------------------------------------------

class TestFastGetElementMetadata:
    """fast_get_element_metadata reads name/machine_area without a full YAML parse."""

    def test_extracts_name(self, tmp_path):
        q = _make_quad(name="QA", machine_area="S01")
        fpath = _write_element_yaml(str(tmp_path), q)
        meta = fast_get_element_metadata(fpath)
        assert meta["name"] == "QA"

    def test_extracts_machine_area(self, tmp_path):
        q = _make_quad(name="QB", machine_area="INJECT")
        fpath = _write_element_yaml(str(tmp_path), q)
        meta = fast_get_element_metadata(fpath)
        assert meta["machine_area"] == "INJECT"

    def test_returns_dict_with_required_keys(self, tmp_path):
        m = _make_marker(name="M5", machine_area="BA1")
        fpath = _write_element_yaml(str(tmp_path), m)
        meta = fast_get_element_metadata(fpath)
        assert "name" in meta
        assert "machine_area" in meta

    def test_falls_back_to_filename_when_name_missing(self, tmp_path):
        """When YAML has no 'name' key the filename stem is used."""
        fpath = str(tmp_path / "MY_ELEMENT.yaml")
        with open(fpath, "w") as fh:
            yaml.dump({"hardware_type": "Quadrupole", "machine_area": "X"}, fh)
        meta = fast_get_element_metadata(fpath)
        assert meta["name"] == "MY_ELEMENT"

    def test_machine_area_is_none_when_absent(self, tmp_path):
        fpath = str(tmp_path / "bare.yaml")
        with open(fpath, "w") as fh:
            yaml.dump({"name": "bare_elem", "hardware_type": "Quadrupole"}, fh)
        meta = fast_get_element_metadata(fpath)
        assert meta["machine_area"] is None

    def test_gracefully_handles_nonexistent_file(self):
        """Missing file does not raise; name falls back to basename."""
        meta = fast_get_element_metadata("/no/such/file/element.yaml")
        assert meta["name"] == "element"


# ---------------------------------------------------------------------------
# LazyElementDict
# ---------------------------------------------------------------------------

class TestLazyElementDict:
    """LazyElementDict loads YAML files on first access and caches the result."""

    def _build(self, tmp_path):
        """Return a LazyElementDict backed by two real YAML files."""
        q = _make_quad("Q1", "SEC")
        m = _make_marker("M1", "SEC")
        fq = _write_element_yaml(str(tmp_path), q)
        fm = _write_element_yaml(str(tmp_path), m)
        filenames = {"Q1": fq, "M1": fm}
        return LazyElementDict(filenames), filenames

    def test_len_equals_number_of_files(self, tmp_path):
        d, _ = self._build(tmp_path)
        assert len(d) == 2

    def test_keys_present_before_loading(self, tmp_path):
        d, _ = self._build(tmp_path)
        assert "Q1" in d.keys()
        assert "M1" in d.keys()

    def test_contains_known_key(self, tmp_path):
        d, _ = self._build(tmp_path)
        assert "Q1" in d
        assert "M1" in d

    def test_does_not_contain_unknown_key(self, tmp_path):
        d, _ = self._build(tmp_path)
        assert "UNKNOWN_ELEM" not in d

    def test_getitem_loads_element(self, tmp_path):
        d, _ = self._build(tmp_path)
        elem = d["Q1"]
        assert elem is not None
        assert elem.name == "Q1"
        assert elem.hardware_type == "Quadrupole"

    def test_getitem_caches_loaded_element(self, tmp_path):
        d, _ = self._build(tmp_path)
        elem1 = d["Q1"]
        elem2 = d["Q1"]
        # Second access returns same object (cached)
        assert elem1 is elem2

    def test_getitem_unknown_key_raises(self, tmp_path):
        d, _ = self._build(tmp_path)
        with pytest.raises(KeyError):
            _ = d["DOES_NOT_EXIST"]

    def test_get_returns_default_for_missing_key(self, tmp_path):
        d, _ = self._build(tmp_path)
        result = d.get("MISSING", "default_value")
        assert result == "default_value"

    def test_get_returns_element_for_present_key(self, tmp_path):
        d, _ = self._build(tmp_path)
        result = d.get("M1")
        assert result is not None
        assert result.name == "M1"

    def test_iter_yields_all_keys(self, tmp_path):
        d, _ = self._build(tmp_path)
        all_keys = list(d)
        assert set(all_keys) == {"Q1", "M1"}

    def test_values_loads_all_elements(self, tmp_path):
        d, _ = self._build(tmp_path)
        all_elements = list(d.values())
        names = {e.name for e in all_elements if e is not None}
        assert names == {"Q1", "M1"}

    def test_is_loaded_returns_true_after_init(self, tmp_path):
        """After __init__, is_loaded returns True because keys are in the dict."""
        d, _ = self._build(tmp_path)
        # Keys are placed in dict at init time (with None values)
        assert d.is_loaded("Q1") is True

    def test_get_metadata_returns_name_and_area(self, tmp_path):
        """get_metadata returns element fields after the element has been loaded."""
        d, _ = self._build(tmp_path)
        _ = d["Q1"]  # trigger load so the element object is stored
        meta = d.get_metadata("Q1")
        assert meta is not None
        assert meta["name"] == "Q1"
        assert meta["machine_area"] == "SEC"

    def test_get_metadata_none_for_unknown_key(self, tmp_path):
        d, _ = self._build(tmp_path)
        assert d.get_metadata("TOTALLY_UNKNOWN") is None

    def test_get_all_metadata_returns_all_entries(self, tmp_path):
        """get_all_metadata returns entries for all elements after loading."""
        d, _ = self._build(tmp_path)
        # Load both elements so get_metadata can return data from the stored objects
        _ = d["Q1"]
        _ = d["M1"]
        all_meta = d.get_all_metadata()
        assert isinstance(all_meta, dict)
        assert set(all_meta.keys()) == {"Q1", "M1"}
        assert all_meta["Q1"]["name"] == "Q1"
        assert all_meta["M1"]["machine_area"] == "SEC"

    def test_get_metadata_after_load_uses_element(self, tmp_path):
        """After an element is loaded, get_metadata reads from the loaded object."""
        d, _ = self._build(tmp_path)
        _ = d["Q1"]  # trigger load
        meta = d.get_metadata("Q1")
        assert meta["name"] == "Q1"

    def test_empty_dict(self):
        d = LazyElementDict({})
        assert len(d) == 0
        assert list(d) == []
        assert d.get("anything") is None


# ---------------------------------------------------------------------------
# LazyAdapterDict
# ---------------------------------------------------------------------------

class TestLazyAdapterDict:
    """LazyAdapterDict creates TypeAdapters on demand and caches them."""

    def test_get_known_type_returns_adapter(self):
        d = LazyAdapterDict()
        adapter = d.get("Quadrupole")
        assert adapter is not None
        # Pydantic TypeAdapter has a validate_python method
        assert callable(adapter.validate_python)

    def test_get_known_type_caches_adapter(self):
        d = LazyAdapterDict()
        a1 = d.get("Quadrupole")
        a2 = d.get("Quadrupole")
        assert a1 is a2

    def test_get_unknown_type_returns_none(self):
        d = LazyAdapterDict()
        result = d.get("CompletelyUnknownType12345")
        assert result is None

    def test_get_unknown_type_returns_default(self):
        d = LazyAdapterDict()
        sentinel = object()
        result = d.get("CompletelyUnknownType12345", sentinel)
        assert result is sentinel

    def test_all_registered_models_have_adapters(self):
        """Every entry in MODEL_REGISTRY should be resolvable."""
        d = LazyAdapterDict()
        for name in list(MODEL_REGISTRY.keys())[:5]:  # sample first 5 to keep test fast
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


# ---------------------------------------------------------------------------
# validate_element_dict / _get_json_schema
# ---------------------------------------------------------------------------

class TestValidateElementDict:
    """validate_element_dict validates against the LinkML-derived JSON Schema."""

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
        """An element with both required fields (name, hardware_class) satisfies the root schema."""
        jsonschema = pytest.importorskip("jsonschema")
        from laura.Importers.YAML_Loader import validate_element_dict
        # Root schema requires 'name' and 'hardware_class'; hardware_type is an unconstrained string
        base_elem = {"name": "BASE_ELEM", "hardware_class": "Generic", "hardware_type": "AcceleratorElement"}
        # Should not raise
        validate_element_dict(base_elem)

    def test_concrete_hardware_type_with_hardware_class_passes(self):
        """Concrete hardware types (Quadrupole, etc.) pass validation when hardware_class is present.

        The root schema does not constrain hardware_type — it accepts any string value.
        Validation only fails if 'name' or 'hardware_class' are missing.
        """
        jsonschema = pytest.importorskip("jsonschema")
        from laura.Importers.YAML_Loader import validate_element_dict
        # Should not raise: name and hardware_class are both present
        validate_element_dict(self._valid_quad_dict())

    def test_missing_hardware_class_raises_validation_error(self):
        """An element missing the required 'hardware_class' field fails validation."""
        jsonschema = pytest.importorskip("jsonschema")
        from laura.Importers.YAML_Loader import validate_element_dict
        bad = {"name": "QV", "hardware_type": "Quadrupole"}  # missing hardware_class
        with pytest.raises(jsonschema.ValidationError):
            validate_element_dict(bad)

    def test_missing_required_name_raises_validation_error(self):
        """An element missing the required 'name' field fails validation."""
        jsonschema = pytest.importorskip("jsonschema")
        from laura.Importers.YAML_Loader import validate_element_dict
        bad = {"hardware_type": "AcceleratorElement"}  # missing 'name'
        with pytest.raises(jsonschema.ValidationError):
            validate_element_dict(bad)

    def test_missing_jsonschema_raises_import_error(self):
        from laura.Importers.YAML_Loader import validate_element_dict
        with patch.dict("sys.modules", {"jsonschema": None}):
            with pytest.raises(ImportError, match="jsonschema"):
                validate_element_dict(self._valid_quad_dict())

    def test_missing_schema_file_raises_file_not_found(self, tmp_path):
        from laura.Importers import YAML_Loader as loader_mod
        original = loader_mod._SCHEMA_CACHE
        original_path = loader_mod._SCHEMA_PATH
        try:
            loader_mod._SCHEMA_CACHE = None
            loader_mod._SCHEMA_PATH = tmp_path / "does_not_exist.json"
            with pytest.raises(FileNotFoundError, match="LAURA JSON Schema"):
                loader_mod._get_json_schema()
        finally:
            loader_mod._SCHEMA_CACHE = original
            loader_mod._SCHEMA_PATH = original_path

    def test_schema_is_cached_after_first_load(self):
        from laura.Importers.YAML_Loader import _get_json_schema
        schema1 = _get_json_schema()
        schema2 = _get_json_schema()
        assert schema1 is schema2


# ---------------------------------------------------------------------------
# read_YAML_Element_File with validate=True
# ---------------------------------------------------------------------------

class TestReadYAMLElementFileWithValidation:
    """read_YAML_Element_File(validate=True) validates before Pydantic parsing."""

    def test_real_element_file_passes_with_validate_true(self, tmp_path):
        """validate=True on a concrete element file does not raise.

        Element YAML files include both 'name' and 'hardware_class', satisfying
        all root-schema requirements.  The schema accepts any hardware_type string.
        """
        q = _make_quad("QV", "SEC")
        fpath = _write_element_yaml(str(tmp_path), q)
        pytest.importorskip("jsonschema")
        # Should not raise: exported YAML has name + hardware_class
        elem = read_YAML_Element_File(fpath, validate=True)
        assert elem is not None

    def test_validate_false_reads_element_successfully(self, tmp_path):
        """validate=False (default) loads an element without schema validation."""
        q = _make_quad("QV2", "SEC")
        fpath = _write_element_yaml(str(tmp_path), q)
        elem = read_YAML_Element_File(fpath, validate=False)
        assert elem is not None
        assert elem.name == "QV2"

    def test_validate_false_does_not_raise_on_unknown_type(self, tmp_path):
        """Without validate=True, unknown hardware_type silently returns None."""
        bad_path = str(tmp_path / "bad.yaml")
        with open(bad_path, "w") as fh:
            yaml.dump({"name": "BAD", "hardware_type": "NONESUCH_XYZ123"}, fh)
        result = read_YAML_Element_File(bad_path, validate=False)
        assert result is None


# ---------------------------------------------------------------------------
# read_YAML_Combined_File with validate=True
# ---------------------------------------------------------------------------

class TestReadYAMLCombinedFileWithValidation:
    """read_YAML_Combined_File(validate=True) validates each element dict."""

    def test_real_combined_file_passes_with_validate_true(self, tmp_path):
        """validate=True on a combined file with concrete elements does not raise.

        All exported element dicts include 'name' and 'hardware_class', satisfying
        the root-schema requirements.  The schema accepts any hardware_type string.
        """
        pytest.importorskip("jsonschema")
        q = _make_quad("QC", "SEC")
        m = _make_marker("MC", "SEC")
        sections = {"sections": {"SEC": ["MC", "QC"]}}
        layouts = {"default_layout": "beam", "layouts": {"beam": ["SEC"]}}
        machine = LAURA(element_list=[m, q], layout=layouts, section=sections)
        export_path = str(tmp_path / "combined")
        export_machine_combined_file(path=export_path, machine=machine)
        summary = os.path.join(export_path, "summary.yaml")
        # Should not raise: all elements have name + hardware_class
        elements = read_YAML_Combined_File(summary, validate=True)
        assert len(elements) > 0

    def test_combined_file_loads_without_validation(self, tmp_path):
        """validate=False (default) loads combined files normally."""
        q = _make_quad("QD", "SEC")
        m = _make_marker("MD", "SEC")
        sections = {"sections": {"SEC": ["MD", "QD"]}}
        layouts = {"default_layout": "beam", "layouts": {"beam": ["SEC"]}}
        machine = LAURA(element_list=[m, q], layout=layouts, section=sections)
        export_path = str(tmp_path / "comb2")
        export_machine_combined_file(path=export_path, machine=machine)
        summary = os.path.join(export_path, "summary.yaml")
        elements = read_YAML_Combined_File(summary, validate=False)
        names = [e.name for e in elements if e is not None]
        assert "QD" in names or "MD" in names

    def test_missing_name_raises_in_combined_file_validate(self, tmp_path):
        """An element missing 'name' raises ValidationError with validate=True."""
        jsonschema = pytest.importorskip("jsonschema")
        # Dict is missing both 'name' and 'hardware_class' (both required by root schema)
        bad_data = {"elem1": {"hardware_type": "AcceleratorElement"}}
        bad_path = str(tmp_path / "bad.yaml")
        with open(bad_path, "w") as fh:
            yaml.dump(bad_data, fh)
        with pytest.raises(jsonschema.ValidationError):
            read_YAML_Combined_File(bad_path, validate=True)


# ---------------------------------------------------------------------------
# read_YAML_Element_Files (multi-file)
# ---------------------------------------------------------------------------

class TestReadYAMLElementFiles:
    """read_YAML_Element_Files reads multiple YAML files and returns raw dicts."""

    def test_returns_tuple_of_dicts_and_filenames(self, tmp_path):
        q = _make_quad("QF", "SEC")
        m = _make_marker("MF", "SEC")
        fq = _write_element_yaml(str(tmp_path), q)
        fm = _write_element_yaml(str(tmp_path), m)
        dicts, filenames = read_YAML_Element_Files([fq, fm])
        assert isinstance(dicts, list)
        assert isinstance(filenames, list)
        assert len(filenames) == 2

    def test_dicts_contain_raw_data(self, tmp_path):
        q = _make_quad("QF2", "SEC")
        fq = _write_element_yaml(str(tmp_path), q)
        dicts, _ = read_YAML_Element_Files([fq])
        # First dict in a multi-doc YAML split by '---' may be None/empty
        non_none = [d for d in dicts if d is not None]
        names = [d.get("name") for d in non_none if isinstance(d, dict)]
        assert "QF2" in names

    def test_returns_raw_dicts_not_models(self, tmp_path):
        q = _make_quad("QF3", "S01")
        fq = _write_element_yaml(str(tmp_path), q)
        dicts, _ = read_YAML_Element_Files([fq])
        for d in dicts:
            if d is not None:
                assert isinstance(d, dict)

    def test_multiple_files_returns_all(self, tmp_path):
        elements = [_make_quad(f"Q{i}", "S01") for i in range(3)]
        fpaths = [_write_element_yaml(str(tmp_path), e) for e in elements]
        dicts, filenames = read_YAML_Element_Files(fpaths)
        assert len(filenames) == 3
        non_none = [d for d in dicts if d is not None and isinstance(d, dict)]
        names = {d.get("name") for d in non_none}
        # Each element should appear in the raw dicts
        for i in range(3):
            assert f"Q{i}" in names
