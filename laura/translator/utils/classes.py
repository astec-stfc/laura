import numpy as np
from pydantic import PositiveInt

_powers_of_8 = np.asarray([2**j for j in range(1, 20)])


def get_grid_size(x: PositiveInt) -> int:
    """
    Calculate the 3D space charge grid size given the number of particles: the
    power of 2 closest to the cube root of the number of particles, minimum 4.

    Parameters
    ----------
    x: PositiveInt
        Number of particles

    Returns
    -------
    int
        Grid points per dimension
    """
    cuberoot = int(round(abs(x) ** (1.0 / 3)))
    nearest = _powers_of_8[(np.abs(_powers_of_8 - cuberoot)).argmin()]
    return max(4, nearest)
