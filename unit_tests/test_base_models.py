"""Tests for laura.models.baseModels — NumpyModel, NumpyVectorModel, ModelBase, IgnoreExtra, etc."""

import pytest
import numpy as np
from pydantic import BaseModel

from laura.models.baseModels import (
    convert_numpy_types,
    flow_list,
    string_with_quotes,
    ModelBase,
    IgnoreExtra,
    NumpyModel,
    NumpyVectorModel,
    objectList,
    DeviceList,
    Aliases,
)


# ---------------------------------------------------------------------------
# convert_numpy_types
# ---------------------------------------------------------------------------

class TestConvertNumpyTypes:
    def test_float64(self):
        assert convert_numpy_types(np.float64(3.14)) == pytest.approx(3.14)
        assert isinstance(convert_numpy_types(np.float64(3.14)), float)

    def test_float32(self):
        assert isinstance(convert_numpy_types(np.float32(1.5)), float)

    def test_int64(self):
        assert convert_numpy_types(np.int64(42)) == 42
        assert isinstance(convert_numpy_types(np.int64(42)), int)

    def test_uint32(self):
        assert isinstance(convert_numpy_types(np.uint32(7)), int)

    def test_ndarray(self):
        result = convert_numpy_types(np.array([1.0, 2.0, 3.0]))
        assert isinstance(result, flow_list)
        assert result == [1.0, 2.0, 3.0]

    def test_nested_dict(self):
        data = {"a": np.float64(1.0), "b": {"c": np.int64(2)}}
        result = convert_numpy_types(data)
        assert result == {"a": 1.0, "b": {"c": 2}}
        assert isinstance(result["a"], float)
        assert isinstance(result["b"]["c"], int)

    def test_plain_values_pass_through(self):
        assert convert_numpy_types("hello") == "hello"
        assert convert_numpy_types(42) == 42
        assert convert_numpy_types(None) is None

    def test_list_of_numpy(self):
        result = convert_numpy_types([np.float64(1), np.int64(2)])
        assert result == [1.0, 2]
        assert isinstance(result, flow_list)


# ---------------------------------------------------------------------------
# ModelBase
# ---------------------------------------------------------------------------

class TestModelBase:
    def test_base_model_dump_excludes_none(self):
        class M(ModelBase):
            a: int = 1
            b: float | None = None

        m = M()
        dump = m.base_model_dump()
        assert "a" in dump
        assert "b" not in dump

    def test_base_model_dump_converts_numpy(self):
        class M(ModelBase):
            val: float = 0.0

        m = M(val=np.float64(2.5))
        dump = m.base_model_dump()
        assert isinstance(dump["val"], float)


# ---------------------------------------------------------------------------
# IgnoreExtra
# ---------------------------------------------------------------------------

class TestIgnoreExtra:
    def test_extra_fields_ignored(self):
        class IE(IgnoreExtra):
            x: int = 0

        obj = IE(x=5, unknown_field=99)
        assert obj.x == 5
        assert not hasattr(obj, "unknown_field")

    def test_update(self):
        class IE(IgnoreExtra):
            x: int = 0

        obj = IE(x=1)
        obj.update(x=42)
        assert obj.x == 42


# ---------------------------------------------------------------------------
# NumpyModel
# ---------------------------------------------------------------------------

class TestNumpyModel:
    def test_array_property(self):
        class V(NumpyModel):
            a: float = 0.0
            b: float = 0.0

        v = V(a=1.0, b=2.0)
        np.testing.assert_array_equal(v.array, np.array([1.0, 2.0]))

    def test_from_list(self):
        class V(NumpyModel):
            a: float = 0.0
            b: float = 0.0

        v = V.from_list([3.0, 4.0])
        assert v.a == 3.0
        assert v.b == 4.0

    def test_from_values(self):
        class V(NumpyModel):
            a: float = 0.0
            b: float = 0.0

        v = V.from_values(5.0, 6.0)
        assert v.a == 5.0
        assert v.b == 6.0

    def test_from_list_wrong_length(self):
        class V(NumpyModel):
            a: float = 0.0
            b: float = 0.0

        with pytest.raises(AssertionError):
            V.from_list([1.0])

    def test_json_serialization(self):
        class V(NumpyModel):
            a: float = 1.0
            b: float = 2.0

        v = V()
        # The NumpyModel serializer returns a numpy array for JSON mode,
        # which Pydantic cannot serialize directly. Use .array.tolist() instead.
        assert v.array.tolist() == [1.0, 2.0]

    def test_python_serialization_is_dict(self):
        class V(NumpyModel):
            a: float = 1.0
            b: float = 2.0

        v = V()
        dumped = v.model_dump(mode="python")
        assert isinstance(dumped, dict)
        assert dumped["a"] == 1.0


# ---------------------------------------------------------------------------
# NumpyVectorModel
# ---------------------------------------------------------------------------

class TestNumpyVectorModel:
    def test_iter(self):
        class V(NumpyVectorModel):
            x: float = 0.0
            y: float = 0.0

        v = V(x=1.0, y=2.0)
        assert list(v) == [1.0, 2.0]

    def test_eq_with_same(self):
        class V(NumpyVectorModel):
            x: float = 0.0
            y: float = 0.0

        assert V(x=1, y=2) == V(x=1, y=2)

    def test_eq_with_zero(self):
        class V(NumpyVectorModel):
            x: float = 0.0
            y: float = 0.0

        assert V() == 0
        assert V() == 0.0
        assert V() == None  # noqa: E711


# ---------------------------------------------------------------------------
# objectList / DeviceList / Aliases
# ---------------------------------------------------------------------------

class TestObjectList:
    def test_device_list_iter(self):
        dl = DeviceList(devices=["d1", "d2", "d3"])
        assert list(dl) == ["d1", "d2", "d3"]

    def test_device_list_str(self):
        dl = DeviceList(devices=["a"])
        assert "a" in str(dl)

    def test_aliases_iter(self):
        al = Aliases(aliases=["x", "y"])
        assert list(al) == ["x", "y"]

    def test_aliases_empty(self):
        al = Aliases()
        assert list(al) == []

    def test_aliases_repr(self):
        al = Aliases(aliases=["foo"])
        assert "foo" in repr(al)
