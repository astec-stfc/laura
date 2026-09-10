"""Space-charge mode -> OPAL FSTYPE mapping."""

import pytest

from laura.translator.converters.codes.opal import OpalFieldSolver


@pytest.mark.parametrize(
    "mode,fstype",
    [
        ("False", "NONE"),
        ("None", "NONE"),
        ("off", "NONE"),
        ("0", "NONE"),
        ("no", "NONE"),
        ("3D", "FFT"),
    ],
)
def test_mode_selects_fstype(mode, fstype):
    assert OpalFieldSolver(npart=32768, space_charge_mode=mode).FSTYPE == fstype


def test_2d_falls_back_to_the_3d_solver_with_a_warning():
    with pytest.warns(UserWarning, match="no 2D/cylindrical space-charge solver"):
        fs = OpalFieldSolver(npart=32768, space_charge_mode="2D")
    assert fs.FSTYPE == "FFT"
