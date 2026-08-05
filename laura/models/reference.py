from pydantic import ConfigDict

from ._generated import _ReferenceElementBase


class ReferenceElement(_ReferenceElementBase):
    """Reference information model."""

    # Override model_config so that extra fields are allowed (not silently
    # dropped) and legacy populate_by_name behaviour is preserved.  The
    # generated ConfiguredBaseModel uses extra="ignore"; we need extra="allow"
    # here to be compatible with existing YAML files.
    model_config = ConfigDict(
        extra="allow",
        arbitrary_types_allowed=True,
        populate_by_name=True,
        validate_by_name=True,
    )
