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

    pass


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

    pass


class WakefieldSimulationElement(_WakefieldSimulationElementBase):
    """
    Wakefield simulation element model.
    """

    pass


class TwissMatchSimulationElement(_TwissMatchSimulationElementBase):
    pass
