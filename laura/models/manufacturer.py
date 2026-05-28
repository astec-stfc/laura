from pydantic import field_validator

from ._generated import _ManufacturerElementBase


def _coerce_string_or_int(v: str | int) -> str:
    return str(v) if isinstance(v, int) else v


class ManufacturerElement(_ManufacturerElementBase):
    """Manufacturer info model."""

    @field_validator("serial_number", mode="before")
    @classmethod
    def validate_serial_number(cls, v: str | int) -> str:
        return _coerce_string_or_int(v)

    @field_validator("manufacturer", mode="before")
    @classmethod
    def validate_manufacturer(cls, v: str | int) -> str:
        return _coerce_string_or_int(v)
