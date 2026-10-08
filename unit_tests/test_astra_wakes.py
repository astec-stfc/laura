"""How many `&WAKE` entries a cavity writes, and where they go."""

import re

import pytest

from laura.models.physical import PhysicalElement
from laura.models.rf import WakefieldElement
from laura.models.simulation import WakefieldSimulationElement
from laura.translator.converters.wake import WakefieldTranslator

CELL_LENGTH = 0.0349753333333
N_CELLS = 84
LENGTH = 3.095244


def _translator(tmp_path, wakefile, start_z):
    return WakefieldTranslator(
        name="L0A_wake",
        hardware_class="Wakefield",
        hardware_type="Wakefield",
        machine_area="CU_INJ",
        physical=PhysicalElement(middle=[0, 0, start_z + LENGTH / 2], length=LENGTH),
        cavity=WakefieldElement(cell_length=CELL_LENGTH, n_cells=N_CELLS),
        simulation=WakefieldSimulationElement(wakefield_definition=str(wakefile)),
        directory=str(tmp_path),
    )


def _positions(text):
    return [
        (int(i), float(z)) for i, z in re.findall(r"Wk_z\((\d+)\) = ([0-9.e+-]+)", text)
    ]


def _wake_file(path, length=None):
    h5py = pytest.importorskip("h5py")
    import numpy as np

    with h5py.File(path, "w") as f:
        f.attrs["type"] = "LongitudinalWake"
        if length is not None:
            f.attrs["length"] = length
        for name, units in (("z", "m"), ("Wz", "V/C")):
            f.create_dataset(name, data=np.linspace(0, 0.01, 11))
            f[name].attrs["units"] = units
    return path


@pytest.fixture
def per_cell_wake(tmp_path):
    """A Green's function for one cell, which says nothing about length."""
    return _wake_file(tmp_path / "per_cell_wake.hdf5")


@pytest.fixture
def whole_structure_wake(tmp_path):
    """A wake already integrated over the structure, which records its length."""
    return _wake_file(tmp_path / "structure_wake.hdf5", length=LENGTH)


def test_wake_without_a_length_goes_in_once_per_cell(tmp_path, per_cell_wake):
    w = _translator(tmp_path, per_cell_wake, start_z=1.459)
    positions = _positions(w.to_astra(n=1))
    assert len(positions) == N_CELLS
    assert positions[0][1] == pytest.approx(1.459 + 0.5 * CELL_LENGTH)
    assert positions[-1][1] == pytest.approx(1.459 + (N_CELLS - 0.5) * CELL_LENGTH)


def test_wake_with_a_structure_length_goes_in_once(tmp_path, whole_structure_wake):
    w = _translator(tmp_path, whole_structure_wake, start_z=1.459)
    positions = _positions(w.to_astra(n=1))
    assert positions == [(1, pytest.approx(1.459 + LENGTH / 2))]


def test_later_cavities_keep_their_wakes_inside_themselves(tmp_path, per_cell_wake):
    """`n` indexes the deck's wakes; it is not an offset into this cavity."""
    start_z = 5.3031976
    w = _translator(tmp_path, per_cell_wake, start_z=start_z)
    positions = _positions(w.to_astra(n=85))
    assert [i for i, _ in positions] == list(range(85, 85 + N_CELLS))
    assert positions[0][1] == pytest.approx(start_z + 0.5 * CELL_LENGTH)
    assert positions[-1][1] < start_z + LENGTH


def test_wake_offsets_use_their_own_plane(tmp_path, whole_structure_wake):
    w = _translator(tmp_path, whole_structure_wake, start_z=0)
    w.physical.error.position.x, w.physical.error.position.y = 0.001, 0.002
    text = w.to_astra(n=1)
    assert re.search(r"Wk_x\(1\) = 0\.001\b", text)
    assert re.search(r"Wk_y\(1\) = 0\.002\b", text)
