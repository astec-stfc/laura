from .base import BaseElementTranslator
from laura.models.simulation import WireSimulationElement
from ..utils.functions import sanitize_string


class WireTranslator(BaseElementTranslator):
    """
    Translator class for converting a :class:`~laura.models.element.Wire`
    element instance into a string or object that can be understood by
    various simulation codes.
    """

    simulation: WireSimulationElement
    """Wire simulation element."""

    def to_madx(self, at: float = None) -> str:
        """
        Generates a string representation of the object's properties in the
        MAD-X format, as a MAD-X ``WIRE`` element. MAD-X's ``WIRE`` attributes
        are array-valued (supporting multiple wires per element); this
        translator always emits a single-element array.

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
        if self.simulation.current:
            string += f", current = {{{self.simulation.current}}}"
        if self.simulation.interaction_length:
            string += f", l_int = {{{self.simulation.interaction_length}}}"
        string += f", xma = {{{self.simulation.horizontal_offset}}}"
        string += f", yma = {{{self.simulation.vertical_offset}}}"
        if at is not None:
            string += f", at = {at}"
        return string + ";\n"

    def to_xsuite(self, beam_length: int) -> tuple:
        """
        Generates an Xsuite ``Wire`` object based on the element's properties.

        Parameters
        ----------
        beam_length: int
            Number of macroparticles in the beam (unused; kept for interface
            consistency with other :meth:`to_xsuite` implementations).

        Returns
        -------
        tuple
            (objectname, Xsuite object, properties[dict])
        """
        from xtrack import Wire as Wire_xs

        self.start_write()
        properties = {
            "L_phy": self.length,
            "L_int": self.simulation.interaction_length,
            "current": self.simulation.current,
            "xma": self.simulation.horizontal_offset,
            "yma": self.simulation.vertical_offset,
        }
        return self.name, Wire_xs, properties
