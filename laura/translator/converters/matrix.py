from .base import BaseElementTranslator
from laura.models.simulation import MatrixTransformSimulationElement
import numpy as np
from warnings import warn
from ..utils.functions import sanitize_string
from typing import Dict


def _bdsim_rmatrix(r_matrix) -> Dict:
    """
    Build the ``r11``..``r44`` keywords for ``pybdsim.Builder.Rmat``.
    """
    return {
        f"r{i + 1}{j + 1}": float(r_matrix[i][j]) for i in range(4) for j in range(4)
    }


class MatrixTransformTranslator(BaseElementTranslator):
    """
    Translator class for converting a :class:`~laura.models.element.MatrixTransform` element instance into a string or
    object that can be understood by various simulation codes.
    """

    simulation: MatrixTransformSimulationElement
    """Matrix transform simulation element"""

    def to_elegant(self) -> str:
        """
        Generates a string representation of the object's properties in the Elegant format.

        Returns
        -------
        str
            A formatted string representing the object's properties in Elegant format.
        """
        self.start_write()
        wholestring = ""
        etype = self._convertType_Elegant(self.hardware_type)
        string = self.name + ": " + etype

        def split_lines(fullstr: str, string: str, linestr: str) -> tuple:
            if len(string + linestr) > 76:
                fullstr += string + ",&\n"
                string = linestr[2::]
            else:
                string += linestr
            return fullstr, string

        if self.length:
            wholestring, string = split_lines(
                wholestring, string, f", L = {self.length}"
            )
        if not np.array_equal(self.simulation.c_matrix, np.zeros(6)):
            for i, val in enumerate(self.simulation.c_matrix):
                if val != 0:
                    wholestring, string = split_lines(wholestring, string, f", C{i + 1} = {val}")
        if not np.array_equal(self.simulation.r_matrix, np.eye(6)):
            for i, row in enumerate(self.simulation.r_matrix):
                for j, val in enumerate(row):
                    if val != (1.0 if i == j else 0.0):
                        wholestring, string = split_lines(wholestring, string, f", R{i + 1}{j + 1} = {val}")
        if not np.array_equal(self.simulation.t_matrix, np.zeros((6, 6, 6))):
            for i, plane in enumerate(self.simulation.t_matrix):
                for j, row in enumerate(plane):
                    for k, val in enumerate(row):
                        if val != 0:
                            wholestring, string = split_lines(
                                wholestring, string, f", T{i + 1}{j + 1}{k + 1} = {val}"
                            )
        wholestring += string + ";\n"
        return wholestring

    def to_madx(self, at: float = None) -> str:
        """
        Generates a string representation of the object's properties in the MAD-X
        format, as a MAD-X ``MATRIX`` element (an explicit, arbitrary transfer
        matrix). Only the entries that differ from the identity/zero default are
        written (MAD-X's ``matrix`` element has hundreds of individual
        ``kick{i}``/``rm{i}{j}``/``tm{i}{j}{k}`` attributes).

        Parameters
        ----------
        at: float, optional
            S-position at which to place the element inside a MAD-X ``SEQUENCE``;
            see :meth:`~laura.translator.converters.base.BaseElementTranslator.to_madx`.

        Returns
        -------
        str
            String representation of the element for MAD-X
        """
        self.start_write()
        etype = self._convertType_Madx(self.hardware_type)
        string = sanitize_string(self.name) + ": " + etype + f", l = {self.length}"
        if not np.array_equal(self.simulation.c_matrix, np.zeros(6)):
            for i, val in enumerate(self.simulation.c_matrix):
                if val != 0:
                    string += f", kick{i + 1} = {val}"
        if not np.array_equal(self.simulation.r_matrix, np.eye(6)):
            for i, row in enumerate(self.simulation.r_matrix):
                for j, val in enumerate(row):
                    if val != (1.0 if i == j else 0.0):
                        string += f", rm{i + 1}{j + 1} = {val}"
        if not np.array_equal(self.simulation.t_matrix, np.zeros((6, 6, 6))):
            for i, plane in enumerate(self.simulation.t_matrix):
                for j, row in enumerate(plane):
                    for k, val in enumerate(row):
                        if val != 0:
                            string += f", tm{i + 1}{j + 1}{k + 1} = {val}"
        if at is not None:
            string += f", at = {at}"
        return string + ";\n"

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
        obj = type_conversion_rules_Xsuite[self.hardware_type]
        properties = {
            "name": self.name,
            "length": self.length,
            "k": self.simulation.c_matrix,
            "R": self.simulation.r_matrix,
            "T": self.simulation.t_matrix,
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
        obj = type_conversion_rules_Ocelot[self.hardware_type](eid=self.name)
        setattr(obj, "l", self.length)
        setattr(obj, "b", self.simulation.c_matrix)
        setattr(obj, "r", self.simulation.r_matrix)
        setattr(obj, "t", self.simulation.t_matrix)
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
        if self.verbose:
            warn(f"WARNING! Only 1st-order transfer maps implemented for cheetah, {self.name}")
        obj = type_conversion_rules_Cheetah[self.hardware_type](
            name=self.name,
            length=tensor(self.physical.length, dtype=float64),
            predefined_transfer_map=tensor(self.simulation.r_matrix_7x7, dtype=float64),
            sanitize_name=True,
        )
        return obj

    def to_bdsim(
        self, section_aperture: Dict | None = None, charge_sign: int | float = 1
    ) -> object:
        """
        Generates a BDSIM object based on the element's properties and type.

        Parameters
        ----------
        section_aperture: dict, optional
                Dictionary containing aperture information for the section,
                which may be used to set the aperture of the BDSIM element.
        charge_sign: int or float, optional
                Beam particle charge sign; unused here.

        Returns
        -------
        object
            BDSIM object
        """
        from ..conversion_rules.codes import bdsim_conversion

        if not self.physical.length:
            from pybdsim.Builder import ThinRmat

            obj = ThinRmat
        else:
            obj = bdsim_conversion.bdsim_conversion_rules[self.hardware_type]
        keywords = self._bdsim_keywords(obj, section_aperture)
        keywords.update(_bdsim_rmatrix(self.simulation.r_matrix))
        if self.verbose:
            warn(
                f"WARNING! Only 1st-order transfer maps implemented for BDSIM, {self.name}"
            )
        return obj(**self._bdsim_charge_sign(keywords, charge_sign))
