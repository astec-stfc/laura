from math import atan2, hypot
from .base import BaseElementTranslator
from laura.models.simulation import ElectrostaticSeparatorSimulationElement
from ..utils.functions import sanitize_string


class ElectrostaticSeparatorTranslator(BaseElementTranslator):
    """
    Translator class for converting a :class:`~laura.models.element.ElectrostaticSeparator`
    element instance into a string or object that can be understood by various
    simulation codes.

    No equivalent element exists in ELEGANT or Xsuite, so only :meth:`to_madx`
    is implemented here (MAD-X ``ELSEPARATOR``).
    """

    simulation: ElectrostaticSeparatorSimulationElement
    """Electrostatic separator simulation element."""

    def to_bmad(self) -> str:
        """
        Generate a Bmad electrostatic separator.

        Returns
        -------
        str
            String representation of the element for Bmad
        """
        horizontal = self.resolve(self.simulation.horizontal_field)
        vertical = self.resolve(self.simulation.vertical_field)
        parameters = {"l": self.length, "e_field": hypot(horizontal, vertical)}
        if horizontal or vertical:
            parameters["tilt"] = atan2(horizontal, vertical)
        elif self.simulation.tilt:
            parameters["tilt"] = self.simulation.tilt
        return self._format_bmad("elseparator", parameters)

    def to_madx(self, at: float = None) -> str:
        """
        Generates a string representation of the object's properties in the
        MAD-X format.

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

        def _term(name: str, value) -> str:
            functional = not self._resolve_functional and self.is_functional(value)
            if functional:
                return f", {name} := ({value}) / 1e6"
            resolved = self.resolve(value)
            return f", {name} = {resolved / 1e6}" if resolved != 0 else ""

        string += _term("ex", self.simulation.horizontal_field)
        string += _term("ey", self.simulation.vertical_field)
        if self.simulation.tilt:
            string += f", tilt = {self.simulation.tilt}"
        if at is not None:
            string += f", at = {at}"
        return string + ";\n"
