"""Tests for laura.models.baseModels helpers and base classes not already
exercised by unit_tests/test_base_models.py: functional_annotations'
bend-angle marker, functional_references, ModelBase's numpy-safe __eq__
fallback, IgnoreExtra field helpers, and NumpyModel/NumpyVectorModel."""

import numpy as np
from pydantic import PrivateAttr

from laura.models.baseModels import (
    ModelBase,
    IgnoreExtra,
    NumpyVectorModel,
    functional_annotations,
    functional_references,
)
from laura.models.magnetic import Dipole_Magnet
from laura.models._generated import _MagneticElementBase


class TestFunctionalAnnotationsBendAngle:
    def test_flat_functional_marker_short_circuits(self):
        field_info = Dipole_Magnet.model_fields["entrance_edge_angle"]
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
        d = Dipole_Magnet(length=1.0, entrance_edge_angle="angle")
        assert functional_references(d) == set()

    def test_non_reserved_string_is_collected(self):
        d = Dipole_Magnet(length=1.0, entrance_edge_angle="my_func")
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
    def test_create_field_class_calls_from_catap(self):
        class FakeFieldClass:
            @classmethod
            def from_CATAP(cls, fields):
                return "built"

        ie = IgnoreExtra()
        fields = {}
        ie._create_field_class(fields, "myfield", FakeFieldClass)
        assert fields["myfield"] == "built"

    def test_create_field_collects_inputs(self):
        ie = IgnoreExtra()
        fields = {"a": 1, "b": 2}
        ie._create_field(fields, "combined", ["a", "b"])
        assert fields["combined"] == [1, 2]


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

    def test_eq_zero(self):
        assert _Vec3() == 0

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
