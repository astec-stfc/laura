import numpy as np
from .constants import speed_of_light, pi
from pydantic import (
    BaseModel,
    model_serializer,
    Field,
    field_validator,
    NonNegativeInt,
    create_model,
    NonNegativeFloat,
    computed_field,
)
from .baseModels import IgnoreExtra, T
from ._generated import _PlasmaElementBase


class PlasmaElement(_PlasmaElementBase):
    """Plasma model."""

    pass
