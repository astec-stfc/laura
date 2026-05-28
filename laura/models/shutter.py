from pydantic import field_validator
from typing import List, Union

from ._generated import _ShutterElementBase, _ValveElementBase


def _coerce_csv_strings(v: Union[str, List]) -> List[str]:
    if isinstance(v, str):
        return list(map(str.strip, v.split(",")))
    if isinstance(v, (list, tuple)):
        return list(v)
    raise ValueError("interlocks should be a string or a list of strings")


class ShutterElement(_ShutterElementBase):
    """Laser info model."""

    @field_validator("interlocks", mode="before")
    @classmethod
    def validate_interlocks(cls, v: Union[str, List]) -> List[str]:
        return _coerce_csv_strings(v)


class ValveElement(_ValveElementBase):
    """Valve info model."""

    pass