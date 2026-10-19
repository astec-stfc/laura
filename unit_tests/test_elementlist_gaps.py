"""Additional tests for laura.models.elementList helpers not exercised by
test_element_list_extended.py / models/test_elementList.py / test_laura_class.py:
normalise_lattice_type's type guard, load_functional_definitions' file-resolution
branches, and ElementList's dict-attribute-gathering fallback in __getattr__."""

import pytest

from laura.models.element_list import (
    normalise_lattice_type,
    load_functional_definitions,
    ElementList,
)
from laura.models.element import Marker


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


class TestLoadFunctionalDefinitions:
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


class TestElementListAttributeGathering:
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

    def test_getattr_returns_plain_dict_for_non_element_values(self):
        m1 = Marker(name="M1", machine_area="A")
        el = ElementList(elements={"M1": m1})
        result = el.name
        assert result == {"M1": "M1"}
