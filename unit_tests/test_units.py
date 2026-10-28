import pytest

from laura.translator.utils.units import UnitValue


@pytest.mark.parametrize("prefix", ["m", "milli", "milli-"])
def test_in_units_of_scales(prefix):
    assert UnitValue(0.002, units="m").in_units_of(prefix) == pytest.approx(2.0)
