"""Tests for laura.models._functions — read_yaml."""

import yaml

from laura.models._functions import read_yaml


def test_read_yaml_builds_a_model_from_the_files_keys(tmp_path):
    """The returned model is shaped by the file, not by a schema, so the types
    have to survive as written."""
    path = tmp_path / "probe.yaml"
    path.write_text(yaml.dump({"name": "test", "x": 1.5, "n": 42, "flag": True}))

    model = read_yaml(str(path))

    assert (model.name, model.x, model.n) == ("test", 1.5, 42)
    assert model.flag is True
