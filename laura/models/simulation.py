from pydantic import SerializeAsAny, Field
from typing import Literal, Any, ClassVar, Union
from .base_models import IgnoreExtra, FunctionalMixin
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
from ..translator.utils.fields import FieldMap


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

    field_definition: str | FieldMap | None = None

    smooth: int | None = 2

    field_amplitude: Union[float, str] = Field(
        default=0.0, json_schema_extra={"functional": True}
    )
    """Field amplitude for the magnet simulation. Stored verbatim: a number or a
    string naming a functional definition (resolve via ``resolved("field_amplitude")``)."""

    # n_kicks, n_slices, edge_*, sr_enable, integration_order, nonlinear,
    # smoothing_half_width, csr_*, isr_enable and deltaL were declared inline by
    # PR #4; they now come from _MagnetSimulationElementBase.


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


class RFCavitySimulationElement(_RFCavitySimulationElementBase, FunctionalMixin):
    """
    RF cavity simulation element model.
    """

    field_definition: str | FieldMap | None = None
    wakefield_definition: str | FieldMap | None = None

    field_amplitude: Union[float, str] = Field(
        default=0.0, json_schema_extra={"functional": True}
    )
    """Cavity field amplitude. Stored verbatim: a number or a string naming a
    functional definition (resolve via ``resolved("field_amplitude")``)."""


class WakefieldSimulationElement(_WakefieldSimulationElementBase):
    """
    Wakefield simulation element model.
    """

    wakefield_definition: str | FieldMap | None = None

    pass


class TwissMatchSimulationElement(_TwissMatchSimulationElementBase):
    pass
