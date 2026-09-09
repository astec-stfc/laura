from types import SimpleNamespace

import numpy as np
import pytest

from laura.translator.utils.fields import field
from laura.translator.utils.fields import sdds


def test_sdds_reader_maps_all_field_kinds(monkeypatch):
    columns = {
        "position": SimpleNamespace(data=[0.0, 1.0], unit="m"),
        "electricX": SimpleNamespace(data=[2.0, 3.0], unit="V/m"),
        "By": SimpleNamespace(data=[4.0, 5.0], unit="T"),
        "TIME": SimpleNamespace(data=[6.0, 7.0], unit="s"),
        "W": SimpleNamespace(data=[8.0, 9.0], unit="V/C"),
        "gradient": SimpleNamespace(data=[10.0, 11.0], unit="T/m"),
    }

    class FakeSDDSFile:
        def __init__(self, *args, **kwargs):
            self._columns = columns

        def read_file(self, *args, **kwargs):
            pass

    monkeypatch.setattr(sdds, "SDDSFile", FakeSDDSFile)
    result = field()
    sdds.read_SDDS_field_file(
        result,
        "fields.sdds",
        "3DElectroDynamic",
        column_map={"x": "position", "Ex": "electricX", "G": "gradient"},
        t_column="TIME",
        wz_column="W",
    )

    for name, expected in {
        "x": [0.0, 1.0],
        "Ex": [2.0, 3.0],
        "By": [4.0, 5.0],
        "t": [6.0, 7.0],
        "Wz": [8.0, 9.0],
        "G": [10.0, 11.0],
    }.items():
        np.testing.assert_array_equal(getattr(result, name).value.val, expected)

    result.filename = "fields.sdds"
    with pytest.warns(UserWarning):
        restored = field.model_validate(result.model_dump())
    np.testing.assert_array_equal(restored.t.value.val, [6.0, 7.0])
    np.testing.assert_array_equal(restored.Wz.value.val, [8.0, 9.0])
