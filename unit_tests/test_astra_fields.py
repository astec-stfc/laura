"""Tests for ASTRA field-file export and import."""

import numpy as np
import pytest

from laura.translator.utils.fields import FieldMap
from laura.translator.utils.fields.field_parameter import FieldParameter
from laura.translator.utils.units import UnitValue


def test_astra_monopole_wake_is_one_sub_table(tmp_path, monkeypatch):
    """ASTRA 3.2 read a leading "1 0" as Nq Np, so took the sample count as a
    resistive term and lost 350 times the LCLS wake per kick."""
    monkeypatch.chdir(tmp_path)
    wake = FieldMap(field_type="LongitudinalWake", length=101, read=True)
    wake.filename = "w.hdf5"
    wake.z = FieldParameter(name="z", value=UnitValue(np.linspace(0, 0.01, 101), "m"))
    wake.Wz = FieldParameter(name="Wz", value=UnitValue(np.linspace(2, 1, 101), "V/C"))
    path = wake.write_field_file(code="astra")
    lines = open(path).read().split()
    assert lines[:6] == ["101", "0", "0", "0", "0", "0"]
    old = tmp_path / "old.astra"
    old.write_text("1 0\n" + open(path).read())
    for name in (path, str(old)):
        back = FieldMap()
        back.read_field_file(name, field_type="LongitudinalWake")
        assert back.Wz.value.val == pytest.approx(np.linspace(2, 1, 101))
