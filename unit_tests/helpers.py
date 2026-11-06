"""Builders shared across test modules: ``from unit_tests.helpers import quad, quiet``."""

import contextlib
import warnings

from laura.models.element import Quadrupole


def quad(name="Q", length=0.1, k1l=0.5, machine_area="S", **physical):
    """A quadrupole whose magnetic and physical lengths agree."""
    return Quadrupole(
        name=name,
        hardware_class="Magnet",
        machine_area=machine_area,
        magnetic={"magnetic_length": length, "k1l": k1l},
        physical={"length": length, **physical},
    )


@contextlib.contextmanager
def quiet():
    """Suppress warnings (``catch_warnings(action=...)`` needs Python 3.11)."""
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        yield
