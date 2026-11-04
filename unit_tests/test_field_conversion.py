"""Field maps written for each code and read back, ported from simba's test_field.py."""

import contextlib

import numpy as np
import pytest

from laura.translator.utils.fields import FieldMap, allowed_fields
from laura.translator.utils.fields.field_parameter import FieldParameter
from laura.translator.utils.units import UnitValue

UNITS = {
    "m": ("x", "y", "z", "r"),
    "V/m": ("Ex", "Ey", "Ez", "Er"),
    "T": ("Bx", "By", "Bz", "Br"),
    "V/C/m": ("Wx", "Wy", "Wr"),
    "V/C": ("Wz",),
    "T/m": ("G",),
}
WAKES = {
    "LongitudinalWake": ["z", "Wz"],
    "TransverseWake": ["z", "Wx", "Wy"],
    "3DWake": ["z", "Wx", "Wy", "Wz"],
}
ROUND_TRIPS = {
    "astra": {
        "LongitudinalWake": ["z", "Wz"],
        "3DWake": ["z", "Wx", "Wy", "Wz"],
        "1DMagnetoStatic": ["z", "Bz"],
        "1DElectroDynamic": ["z", "Ez"],
        "1DQuadrupole": ["z", "G"],
    },
    "gdf": WAKES | {
        "1DMagnetoStatic": ["z", "Bz"],
        "3DMagnetoStatic": ["x", "y", "z", "Bx", "By", "Bz"],
        "1DElectroDynamic": ["z", "Ez"],
    },
    "sdds": WAKES,
    "opal": WAKES | {"1DMagnetoStatic": ["z", "Bz"], "1DElectroDynamic": ["z", "Ez"]},
}


@pytest.fixture
def simple_field(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    field = FieldMap()
    field.length = 1000
    for units, names in UNITS.items():
        for name in names:
            value = UnitValue(np.linspace(0, 1, field.length), units)
            setattr(field, name, FieldParameter(name=name, value=value))
    field.read = True
    field.frequency = 3e9
    field.cavity_type = "StandingWave"
    return field


def _read_back(field, code, **kwargs):
    return FieldMap(
        field.write_field_file(code=code),
        field_type=field.field_type,
        frequency=field.frequency,
        cavity_type=field.cavity_type,
        **kwargs,
    )


@pytest.mark.parametrize(
    "code, field_type",
    [(code, field_type) for code, types in ROUND_TRIPS.items() for field_type in types],
)
def test_round_trip(simple_field, code, field_type):
    params = ROUND_TRIPS[code][field_type]
    simple_field.filename = f"test_{field_type}.{'hdf5' if code in ('astra', 'gdf') else code}"
    simple_field.field_type = field_type
    # OPAL has no format for wakes or 1D magnetostatic maps, and says so
    warns = code == "opal" and ("Wake" in field_type or field_type == "1DMagnetoStatic")
    with pytest.warns(UserWarning) if warns else contextlib.nullcontext():
        # GDF otherwise normalises B to its on-axis peak
        new = _read_back(simple_field, code, **({"normalize_b": False} if code == "gdf" else {}))
    for param in params:
        assert all(getattr(new, param).value == getattr(simple_field, param).value)
    for name in simple_field.model_fields_set - set(params):
        if isinstance(getattr(simple_field, name), FieldParameter):
            assert getattr(new, name).value is None


@pytest.mark.parametrize("field_type", allowed_fields)
def test_hdf5_round_trip(simple_field, field_type):
    simple_field.filename = f"test_{field_type}.hdf5"
    simple_field.field_type = field_type
    new = _read_back(simple_field, "hdf5")
    for name in simple_field.model_fields_set:
        value = getattr(simple_field, name)
        if isinstance(value, FieldParameter):
            assert all(getattr(new, name).value == value.value)
        elif type(value) in (str, float, int):
            assert getattr(new, name) == value
