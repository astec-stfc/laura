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


@pytest.mark.parametrize("npart, grid", [(5000, 16), (32768, 32), (50000, 32), (100, 4)])
def test_automatic_mesh_is_as_fine_as_opal_allows(npart, grid):
    """Eight particles per cell gave the LCLS gun an 8^3 mesh at 5000 particles and
    twice ASTRA's emittance; 16^3 / 32^3 brought it to 1.4x / 1.05x."""
    fs = OpalFieldSolver(npart=npart, space_charge_mode="3D")
    assert fs.grid_size == grid
    assert grid**3 <= npart  # OPAL's limit
