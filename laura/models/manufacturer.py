from pydantic import field_validator

from ._generated import _ManufacturerElementBase


class ManufacturerElement(_ManufacturerElementBase):
    """Manufacturer info model."""

    # Override Optional[str] fields from generated base with str defaults so
    # callers always get a string (never None).
    manufacturer: str = ""
    """Name of manufacturer."""

    serial_number: str = ""
    """Serial number of element."""

    @field_validator("serial_number", mode="before")
    @classmethod
    def validate_serial_number(cls, v: str | int) -> str:
        if isinstance(v, int):
            return str(v)
        return v

    @field_validator("manufacturer", mode="before")
    @classmethod
    def validate_manufacturer(cls, v: str | int) -> str:
        if isinstance(v, int):
            return str(v)
        return v
