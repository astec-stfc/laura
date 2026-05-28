from pydantic import field_validator
from typing import List, Union

from ._generated import _DegaussableElementBase


def _coerce_csv_numbers(v: Union[str, List]) -> list:
    if isinstance(v, str):
        return list(map(float, v.split(",")))
    if isinstance(v, (list, tuple)):
        return list(v)
    raise ValueError("degauss_values should be a string or a list of floats")


class DegaussableElement(_DegaussableElementBase):
    """
    Model for elements that can be degaussed.
    """

    @field_validator("values", mode="before")
    @classmethod
    def validate_degauss_values(cls, v: Union[str, List]) -> list:
        return _coerce_csv_numbers(v)
