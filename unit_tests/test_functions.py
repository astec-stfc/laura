"""Tests for laura.models._functions — read_yaml, merge_two_dicts, _rotation_matrix."""

import pytest
import os
import tempfile
import numpy as np
import yaml

from laura.models._functions import _rotation_matrix, merge_two_dicts, read_yaml

# ---------------------------------------------------------------------------
# _rotation_matrix
# ---------------------------------------------------------------------------


class TestRotationMatrix:
    def test_identity_at_zero(self):
        R = _rotation_matrix(0)
        np.testing.assert_array_almost_equal(R, np.eye(3))

    def test_pi_rotation(self):
        R = _rotation_matrix(np.pi)
        expected = np.array([[-1, 0, 0], [0, 1, 0], [0, 0, -1]])
        np.testing.assert_array_almost_equal(R, expected, decimal=10)

    def test_half_pi(self):
        R = _rotation_matrix(np.pi / 2)
        expected = np.array([[0, 0, 1], [0, 1, 0], [-1, 0, 0]])
        np.testing.assert_array_almost_equal(R, expected, decimal=10)

    def test_orthogonality(self):
        R = _rotation_matrix(0.7)
        product = R @ R.T
        np.testing.assert_array_almost_equal(product, np.eye(3))

    def test_determinant_is_one(self):
        R = _rotation_matrix(1.3)
        assert np.linalg.det(R) == pytest.approx(1.0)

    def test_returns_ndarray(self):
        R = _rotation_matrix(0.5)
        assert isinstance(R, np.ndarray)
        assert R.shape == (3, 3)


# ---------------------------------------------------------------------------
# merge_two_dicts
# ---------------------------------------------------------------------------


class TestMergeTwoDicts:
    def test_basic_merge(self):
        x = {"a": 1, "b": 2}
        y = {"b": 3, "c": 4}
        result = merge_two_dicts(y, x)
        assert result["a"] == 1
        assert result["b"] == 3  # y overwrites x
        assert result["c"] == 4

    def test_empty_dicts(self):
        result = merge_two_dicts({}, {})
        assert result == {}

    def test_non_dict_x_returns_y(self):
        result = merge_two_dicts({"a": 1}, "not_a_dict")
        assert result == {"a": 1}

    def test_non_dict_y_returns_x(self):
        result = merge_two_dicts("not_a_dict", {"a": 1})
        assert result == {"a": 1}

    def test_both_non_dict(self):
        from collections import OrderedDict

        result = merge_two_dicts("a", "b")
        assert isinstance(result, OrderedDict)
        assert len(result) == 0

    def test_x_not_modified(self):
        x = {"a": 1}
        y = {"b": 2}
        merge_two_dicts(y, x)
        assert x == {"a": 1}  # original not mutated


# ---------------------------------------------------------------------------
# read_yaml
# ---------------------------------------------------------------------------


class TestReadYaml:
    def test_read_simple_yaml(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump({"name": "test", "value": 42}, f)
            fname = f.name
        try:
            model = read_yaml(fname)
            assert model.name == "test"
            assert model.value == 42
        finally:
            os.remove(fname)

    def test_read_yaml_types(self):
        data = {"x": 1.5, "y": "hello", "z": True}
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(data, f)
            fname = f.name
        try:
            model = read_yaml(fname)
            assert model.x == 1.5
            assert model.y == "hello"
            assert model.z is True
        finally:
            os.remove(fname)
