import numpy as np
from pydantic import PositiveInt

_powers_of_8 = np.asarray([2**j for j in range(1, 20)])


def get_grid_size(x: PositiveInt) -> int:
    """
    Calculate the 3D space charge grid size given the number of particles, minimum of 4:
    the closest power of 8 to the cube root of the number of particles.

    Parameters
    ----------
    x: PositiveInt
        Number of particles

    Returns
    -------
    int
        The number of space charge grids
    """
    cuberoot = int(round(abs(x) ** (1.0 / 3)))
    nearest = _powers_of_8[(np.abs(_powers_of_8 - cuberoot)).argmin()]
    return max(4, nearest)
