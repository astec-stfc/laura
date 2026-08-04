"""Tests for laura.models._functions — read_yaml."""

import os
import tempfile
import yaml

from laura.models._functions import read_yaml


# ---------------------------------------------------------------------------
# read_yaml
# ---------------------------------------------------------------------------

class TestReadYaml:
    def test_read_simple_yaml(self):
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".yaml", delete=False
        ) as f:
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
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".yaml", delete=False
        ) as f:
            yaml.dump(data, f)
            fname = f.name
        try:
            model = read_yaml(fname)
            assert model.x == 1.5
            assert model.y == "hello"
            assert model.z is True
        finally:
            os.remove(fname)
