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
        # Arguments of the stage itself, passed whatever the wakefield model.
        "common": [
            "length",
            # These three were already fields on this model but reached no
            # code, so setting them in a lattice did nothing. Wake-T's defaults
            # for all three are identical to LAURA's ("boris", "auto", 1), so
            # wiring them up changes no existing result.
            "bunch_pusher",
            "dt_bunch",
            "n_out",
        ],
        "quasistatic_2d": [
            "density",
            "r_max",
            "r_max_plasma",
            "n_longitudinal",
            "n_radial",
            "min_longitudinal_position",
            "max_longitudinal_position",
            "particles_per_radial_cell",
            "laser_evolution",
            "laser_envelope_substeps",
            "laser_envelope_n_longitudinal",
            "laser_envelope_n_radial",
            "laser_envelope_use_phase",
            # Also inert until now, and also default-compatible with Wake-T.
            "dz_fields",
            "parabolic_coefficient",
            # NOT `plasma_pusher`. It is a field on this model, but the
            # quasi-static solver dispatches on 'ab5' or 'rk4' and has no else
            # branch, so LAURA's default of 'boris' would leave the plasma
            # unpushed rather than raise. Wake-T's own default ('rk4') is what
            # runs while this stays unpassed, which is the safe behaviour; the
            # field is really an FBPIC/general-tracking notion and would need a
            # per-model validity check before it could be forwarded here.
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

    @property
    def p_rmin(self) -> float:
        """Inner radius of the plasma column, zero (a filled column) unless a
        hollow channel is asked for."""
        if self.r_min_plasma is None:
            return 0.0
        return self.r_min_plasma


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
