from pydantic import Field, AliasChoices

from ._generated import _ElectricalElementBase


class ElectricalElement(_ElectricalElementBase):
    """
    Electrical info model.
    """

    min_i: float = Field(
        default=0, validation_alias=AliasChoices("min_i", "minI")
    )
    """Minimum current that can be set [A]."""

    max_i: float = Field(
        default=0, validation_alias=AliasChoices("max_i", "maxI")
    )
    """Maximum current that can be set [A]."""

    read_tolerance: float = Field(
        default=0.1, validation_alias=AliasChoices("read_tolerance", "ri_tolerance")
    )
    """Tolerance on read current [A]."""
