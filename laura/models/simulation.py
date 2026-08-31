from pydantic import SerializeAsAny, Field
from typing import Literal, Any, ClassVar, Union
from .baseModels import IgnoreExtra, FunctionalMixin
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


class SimulationElement(_SimulationElementBase, FunctionalMixin):
    """
    Simulation element model.
    """

    wakefield_enable: bool = True
    """Flag to indicate whether the wakefield defined by
    :attr:`~wakefield_definition` is applied. Set to False to track the element
    without its wakefield, without discarding the definition itself."""


class MagnetSimulationElement(_MagnetSimulationElementBase, FunctionalMixin):
    """
    Magnet simulation element model.
    """

    field_definition: str | field | None = None
    # Schema declares `smooth` as boolean but ASTRA uses an integer smoothing count (Q_smooth / S_smooth).
    smooth: int | None = 2

    field_amplitude: Union[float, str] = Field(
        default=0.0, json_schema_extra={"functional": True}
    )
    """Field amplitude for the magnet simulation. Stored verbatim: a number or a
    string naming a functional definition (resolve via ``resolved("field_amplitude")``)."""


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

    @property
    def p_zmin(self) -> float:
        """Start of the plasma column, defaulting to the box lower edge."""
        if self.plasma_min_longitudinal_position is None:
            return self.min_longitudinal_position
        return self.plasma_min_longitudinal_position

    @property
    def p_zmax(self) -> float:
        """End of the plasma column, defaulting to the box upper edge."""
        if self.plasma_max_longitudinal_position is None:
            return self.max_longitudinal_position
        return self.plasma_max_longitudinal_position

    @property
    def p_rmax(self) -> float:
        """Radial extent of the plasma column, defaulting to the box radius."""
        if self.r_max_plasma is None:
            return self.r_max
        return self.r_max_plasma


class RFCavitySimulationElement(_RFCavitySimulationElementBase, FunctionalMixin):
    """
    RF cavity simulation element model.
    """

    field_definition: str | field | None = None
    wakefield_definition: str | field | None = None

    field_amplitude: Union[float, str] = Field(
        default=0.0, json_schema_extra={"functional": True}
    )
    """Cavity field amplitude. Stored verbatim: a number or a string naming a
    functional definition (resolve via ``resolved("field_amplitude")``)."""


class WakefieldSimulationElement(_WakefieldSimulationElementBase):
    """
    Wakefield simulation element model.
    """

    wakefield_definition: str | field | None = None

    pass


class TwissMatchSimulationElement(_TwissMatchSimulationElementBase):
    pass
