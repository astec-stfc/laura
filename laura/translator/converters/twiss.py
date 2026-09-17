from typing import Any, Dict
from warnings import warn

from torch import float64, tensor

from laura.models.simulation import TwissMatchSimulationElement

from .base import BaseElementTranslator

_BMAD_FIXER_COMMON = frozenset(
    {
        "tracking_method",
        "mat6_calc_method",
        "spin_tracking_method",
        "integrator_order",
        "ds_step",
    }
)
"""The common Bmad attributes a ``fixer`` accepts."""


class TwissMatchTranslator(BaseElementTranslator):
    """
    Translator class for converting a :class:`~laura.models.element.TwissMatch` element instance into a string or
    object that can be understood by various simulation codes.
    """

    simulation: TwissMatchSimulationElement
    """Twiss match simulation element"""

    bmad_active_fixer: bool = True
    """
    Whether Bmad should take this element's Twiss as the branch's own. A branch
    has room for exactly one, so the section sets this to ``False`` on every
    `TwissMatch` after the first.
    """

    def _bmad_common_parameters(self) -> Dict[str, Any]:
        """Drop the common attributes a ``fixer`` will not take."""
        return {
            key: value
            for key, value in super()._bmad_common_parameters().items()
            if key in _BMAD_FIXER_COMMON
        }

    def to_bmad(self) -> str:
        """
        Generate a Bmad fixer, the element that states the Twiss at a point.

        A `TwissMatch` is where the design Twiss is declared, and Bmad has two
        elements that do that and no third: ``beginning_ele``, which a leading
        `TwissMatch` becomes as the section's ``beginning[...]`` header, and
        ``fixer`` for one anywhere else.

        Returns
        -------
        str
            String representation of the element for Bmad
        """
        if self.length:
            warn(
                f"TwissMatch {self.name!r} is {self.length} m long, but a Bmad "
                "fixer is a point and has no length attribute; the length is "
                f"dropped and everything downstream of it moves {self.length} "
                "m upstream."
            )
        if not self.bmad_active_fixer:
            warn(
                f"TwissMatch {self.name!r} is not the first in its line, and a "
                "Bmad branch honours one fixer -- given two it takes the last "
                "without saying so. It is written with is_on = F, so it carries "
                "its Twiss but no longer declares it."
            )
        return self._format_bmad(
            "fixer",
            {
                "beta_a_stored": self.simulation.beta_x,
                "beta_b_stored": self.simulation.beta_y,
                "alpha_a_stored": self.simulation.alpha_x,
                "alpha_b_stored": self.simulation.alpha_y,
                "eta_x_stored": self.simulation.eta_x,
                "eta_y_stored": self.simulation.eta_y,
                "etap_x_stored": self.simulation.eta_xp,
                "etap_y_stored": self.simulation.eta_yp,
                "is_on": self.bmad_active_fixer,
            },
        )

    def to_xsuite(self, beam_length: int) -> tuple:
        """
        Generates an Xsuite object based on the element's properties and type.

        Parameters
        ----------
        beam_length: int
            Number of macroparticles in the beam

        Returns
        -------
        tuple
            (objectname, Xsuite object, properties[dict])
        """
        from ..conversion_rules.codes import xsuite_conversion

        type_conversion_rules_xsuite = xsuite_conversion.xsuite_conversion_rules
        self.start_write()
        obj = type_conversion_rules_xsuite["MatrixTransform"]
        properties = {
            "name": self.name,
            "length": self.length,
            "R": self.simulation.r_matrix,
        }
        return self.name, obj, properties

    def to_ocelot(self) -> object:
        """
        Generates an Ocelot object based on the element's properties and type.

        Returns
        -------
        object
            An Ocelot object representing the element, initialized with its properties.
        """
        from ..conversion_rules.codes import ocelot_conversion

        type_conversion_rules_ocelot = ocelot_conversion.ocelot_conversion_rules
        self.start_write()
        obj = type_conversion_rules_ocelot["MatrixTransform"](eid=self.name)
        setattr(obj, "l", self.length)
        setattr(obj, "r", self.simulation.r_matrix)
        return obj

    def to_cheetah(self) -> object:
        """
        Generates a Cheetah object based on the element's properties and type.

        Returns
        -------
        object
            An Cheetah object representing the element, initialized with its properties.
        """
        from ..conversion_rules.codes import cheetah_conversion

        type_conversion_rules_cheetah = cheetah_conversion.cheetah_conversion_rules
        self.start_write()
        obj = type_conversion_rules_cheetah["MatrixTransform"](
            name=self.name,
            length=tensor(self.physical.length, dtype=float64),
            predefined_transfer_map=tensor(self.simulation.r_matrix_7x7, dtype=float64),
            sanitize_name=True,
        )
        return obj
