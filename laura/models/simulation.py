from pydantic import SerializeAsAny
from typing import Literal, Any, ClassVar
from .baseModels import IgnoreExtra
from ._generated import (
    _ApertureElementBase,
    _SimulationElementBase,
    _MagnetSimulationElementBase,
    _RFCavitySimulationElementBase,
    _WakefieldSimulationElementBase,
    _DriftSimulationElementBase,
    _DiagnosticSimulationElementBase,
    _PlasmaSimulationElementBase,
    _TwissMatchSimulationElementBase,
)
from ..translator.utils.fields import field


class ApertureElement(_ApertureElementBase):
    """Physical info model."""

    pass


class SimulationElement(_SimulationElementBase):
    """
    Simulation element model.
    """

    pass


class MagnetSimulationElement(_MagnetSimulationElementBase):
    """
    Magnet simulation element model.
    """

    field_definition: str | field | None = None
    # Schema declares `smooth` as boolean but ASTRA uses an integer smoothing count (Q_smooth / S_smooth).
    smooth: int | None = 2


class DriftSimulationElement(_DriftSimulationElementBase):
    """
    Drift simulation element model.
    """

    pass


class DiagnosticSimulationElement(_DiagnosticSimulationElementBase):
    pass


class PlasmaSimulationElement(_PlasmaSimulationElementBase):
    """
    Plasma simulation element model.
    """

    required_attrs: ClassVar[dict[str, list[str]]] = {
        "common": [
            "length",
        ],
        "quasistatic_2d": [
            "density",
            "r_max",
            "n_longitudinal",
            "n_radial",
            "min_longitudinal_position",
            "max_longitudinal_position",
        ],
    }

    pass


class RFCavitySimulationElement(_RFCavitySimulationElementBase):
    """
    RF cavity simulation element model.
    """

    field_definition: str | field | None = None
    wakefield_definition: str | field | None = None

    pass


class WakefieldSimulationElement(_WakefieldSimulationElementBase):
    """
    Wakefield simulation element model.
    """

    wakefield_definition: str | field | None = None

    pass


class TwissMatchSimulationElement(_TwissMatchSimulationElementBase):
    pass
