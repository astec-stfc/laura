from pydantic import field_validator
from typing import List, Union

from ._generated import _DegaussableElementBase


class DegaussableElement(_DegaussableElementBase):
    """
    Model for elements that can be degaussed.
    """

    @field_validator("values", mode="before")
    @classmethod
    def validate_degauss_values(cls, v: Union[str, List]) -> list:
        if isinstance(v, str):
            return list(map(float, v.split(",")))
        elif isinstance(v, (list, tuple)):
            return list(v)
        else:
            raise ValueError("degauss_values should be a string or a list of floats")
