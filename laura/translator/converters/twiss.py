from .base import BaseElementTranslator
from laura.models.simulation import TwissMatchSimulationElement
from typing import Dict
import numpy as np


class TwissMatchTranslator(BaseElementTranslator):
    """
    Translator class for converting a :class:`~laura.models.element.TwissMatch` element instance into a string or
    object that can be understood by various simulation codes.
    """

    simulation: TwissMatchSimulationElement
    """Twiss match simulation element"""


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

        type_conversion_rules_Xsuite = xsuite_conversion.xsuite_conversion_rules
        self.start_write()
        obj = type_conversion_rules_Xsuite["MatrixTransform"]
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

        type_conversion_rules_Ocelot = ocelot_conversion.ocelot_conversion_rules
        self.start_write()
        obj = type_conversion_rules_Ocelot["MatrixTransform"](eid=self.name)
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
        from torch import tensor, float64

        type_conversion_rules_Cheetah = cheetah_conversion.cheetah_conversion_rules
        self.start_write()
        obj = type_conversion_rules_Cheetah["MatrixTransform"](
            name=self.name,
            length=tensor(self.physical.length, dtype=float64),
            predefined_transfer_map=tensor(self.simulation.r_matrix_7x7, dtype=float64),
            sanitize_name=True,
        )
        return obj

    def to_bdsim(self, section_aperture: Dict | None = None) -> object:
        """
        Generates a BDSIM object based on the element's properties and type.

        Parameters
        ----------
        section_aperture: dict, optional
                Dictionary containing aperture information for the section,
                which may be used to set the aperture of the BDSIM element.

        Returns
        -------
        object
            BDSIM object
        """
        from ..conversion_rules.codes import bdsim_conversion
        from .matrix import _bdsim_rmatrix

        if not self.physical.length:
            from pybdsim.Builder import ThinRmat

            obj = ThinRmat
        else:
            obj = bdsim_conversion.bdsim_conversion_rules["MatrixTransform"]
        keywords = self._bdsim_keywords(obj, section_aperture)
        keywords.update(_bdsim_rmatrix(self.simulation.r_matrix))
        return obj(**keywords)