from pydantic import BaseModel, ConfigDict
from ..units import UnitValue
import numpy as np


class FieldParameter(BaseModel):
    """Field parameter with a name and an optional value."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    name: str
    """Name of the field parameter."""
    value: UnitValue | np.ndarray | list | None = None
    """Value of the field parameter."""


FIELD_NAMES = (
    "x",
    "y",
    "z",
    "r",
    "t",
    "Ex",
    "Ey",
    "Ez",
    "Er",
    "Bx",
    "By",
    "Bz",
    "Br",
    "Wx",
    "Wy",
    "Wz",
    "Wr",
    "G",
)
"""Names of every :class:`FieldParameter` attribute of a field map."""


def set_field(self, name: str, value, units: str) -> None:
    """Set ``self.<name>`` to a :class:`FieldParameter` holding `value` in `units`."""
    setattr(self, name, FieldParameter(name=name, value=UnitValue(value, units=units)))


def require_rf(self, field_type: str, cavity_type, frequency) -> None:
    """Set `cavity_type` and `frequency`, raising ValueError if an Electro field lacks either."""
    if "Electro" in field_type:
        if cavity_type is None:
            raise ValueError(f"cavity_type must be provided for {field_type}")
        else:
            setattr(self, "cavity_type", cavity_type)
        if frequency is None:
            raise ValueError(f"frequency must be provided for {field_type}")
        else:
            setattr(self, "frequency", frequency)
