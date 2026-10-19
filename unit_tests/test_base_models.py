"""laura.models.base_models helpers."""

import pytest
import numpy as np

from pydantic import PrivateAttr

from laura.models.base_models import (
    convert_numpy_types,
    FlowList,
    ModelBase,
    IgnoreExtra,
    NumpyVectorModel,
    DeviceList,
    Aliases,
    functional_annotations,
    functional_references,
)
from laura.models.magnetic import DipoleMagnet
from laura.models._generated import _MagneticElementBase


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
        assert isinstance(result, FlowList)
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
        assert isinstance(result, FlowList)


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


class _Vec3(NumpyVectorModel):
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0


class TestNumpyModel:
    def test_json_serialization_uses_array(self):
        v = _Vec3(x=1.0, y=2.0, z=3.0)
        dumped = v.model_dump(mode="json")
        assert list(dumped) == [1.0, 2.0, 3.0]

    def test_python_serialization_uses_dict(self):
        v = _Vec3(x=1.0, y=2.0, z=3.0)
        assert v.model_dump() == {"x": 1.0, "y": 2.0, "z": 3.0}

    def test_from_list(self):
        v = _Vec3.from_list([1.0, 2.0, 3.0])
        assert (v.x, v.y, v.z) == (1.0, 2.0, 3.0)

    def test_from_list_wrong_length(self):
        with pytest.raises(AssertionError):
            _Vec3.from_list([1.0])

    def test_from_values(self):
        v = _Vec3.from_values(1.0, 2.0, 3.0)
        assert (v.x, v.y, v.z) == (1.0, 2.0, 3.0)

    def test_array_property(self):
        v = _Vec3(x=1.0, y=2.0, z=3.0)
        np.testing.assert_array_equal(v.array, [1.0, 2.0, 3.0])


class TestNumpyVectorModel:
    def test_update(self):
        v = _Vec3(x=1.0, y=2.0, z=3.0)
        v.update(x=9.0)
        assert v.x == 9.0

    def test_iter(self):
        v = _Vec3(x=1.0, y=2.0, z=3.0)
        assert list(v) == [1.0, 2.0, 3.0]

    def test_eq_with_same(self):
        assert _Vec3(x=1, y=2) == _Vec3(x=1, y=2)

    def test_eq_zero(self):
        assert _Vec3() == 0
        assert _Vec3() == 0.0
        assert _Vec3() == None  # noqa: E711

    def test_eq_zero_false_when_nonzero(self):
        assert not (_Vec3(x=1.0) == 0)

    def test_eq_list(self):
        v = _Vec3(x=1.0, y=2.0, z=3.0)
        assert v == [1.0, 2.0, 3.0]

    def test_neq_zero(self):
        assert not (_Vec3() != 0)

    def test_neq_zero_true_when_nonzero(self):
        assert _Vec3(x=1.0) != 0

    def test_neq_list(self):
        v = _Vec3(x=1.0, y=2.0, z=3.0)
        assert v != [9.0, 9.0, 9.0]


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


class TestFunctionalAnnotationsBendAngle:
    def test_flat_functional_marker_short_circuits(self):
        # DipoleMagnet's hand-written json_schema_extra hits the early-return branch.
        field_info = DipoleMagnet.model_fields["entrance_edge_angle"]
        meta = functional_annotations(field_info)
        assert meta == {"functional": True, "reserved_contains": "angle"}

    def test_bend_angle_marker_derived_from_in_subset(self):
        field_info = _MagneticElementBase.model_fields["entrance_edge_angle"]
        meta = functional_annotations(field_info)
        assert meta == {"functional": True, "reserved_contains": "angle"}


class TestFunctionalReferences:
    def test_non_model_returns_empty_set(self):
        assert functional_references(5) == set()
        assert functional_references(None) == set()

    def test_reserved_value_is_skipped(self):
        d = DipoleMagnet(length=1.0, entrance_edge_angle="angle")
        assert functional_references(d) == set()

    def test_non_reserved_string_is_collected(self):
        d = DipoleMagnet(length=1.0, entrance_edge_angle="my_func")
        assert functional_references(d) == {"my_func"}


class TestModelBaseEqFallback:
    class _WithNumpyPrivate(ModelBase):
        x: int = 1
        _arr = PrivateAttr(default_factory=lambda: np.array([1, 2, 3]))

    def test_equal_dumps_are_equal_despite_numpy_private_attr(self):
        a, b = self._WithNumpyPrivate(), self._WithNumpyPrivate()
        assert a == b

    def test_unequal_fields_are_not_equal(self):
        a, b = self._WithNumpyPrivate(), self._WithNumpyPrivate(x=2)
        assert a != b

    def test_hash_is_stable_and_identity_based(self):
        a = self._WithNumpyPrivate()
        assert hash(a) == hash(a)
        assert hash(a) == id(a)


class TestIgnoreExtraFieldHelpers:
    def test_create_field_collects_inputs(self):
        ie = IgnoreExtra()
        fields = {"a": 1, "b": 2}
        ie._create_field(fields, "combined", ["a", "b"])
        assert fields["combined"] == [1, 2]
