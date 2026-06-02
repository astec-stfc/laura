from .base import BaseElementTranslator
from laura.models.simulation import MatrixTransformSimulationElement
from torch import tensor, float64
import numpy as np
from warnings import warn


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

        def split_lines(fullstr: str, linestr: str) -> str:
            if len(fullstr + linestr) > 76:
                fullstr += fullstr + ",&\n"
                fullstr = ""
                fullstr += linestr[2::]
            else:
                fullstr += linestr
            return fullstr

        if not np.array_equal(self.simulation.c_matrix, np.zeros(6)):
            for i, row in enumerate(self.simulation.c_matrix):
                wholestring = split_lines(wholestring, f", C{i + 1} = {row}")
        if not np.array_equal(self.simulation.r_matrix, np.eye(6)):
            for i, row in enumerate(self.simulation.r_matrix):
                for j, col in enumerate(row):
                    wholestring = split_lines(wholestring, f", R{i + 1}{j + 1} = {row[j]}")
        if not np.array_equal(self.simulation.t_matrix, np.zeros((6, 6, 6))):
            for i, row in enumerate(self.simulation.t_matrix):
                for j, col in enumerate(row):
                    for k, val in enumerate(col):
                        wholestring = split_lines(wholestring, f", T{i + 1}{j + 1}{k + 1} = {val[k]}")
        wholestring += string + ";\n"
        return wholestring

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

        type_conversion_rules_Cheetah = cheetah_conversion.cheetah_conversion_rules
        self.start_write()
        warn(f"WARNING! Only 1st-order transfer maps implemented for cheetah, {self.name}")
        obj = type_conversion_rules_Cheetah[self.hardware_type](
            name=self.name,
            length=tensor(self.physical.length, dtype=float64),
            predefined_transfer_map=tensor(self.simulation.r_matrix_7x7, dtype=float64),
            sanitize_name=True,
        )
        return obj