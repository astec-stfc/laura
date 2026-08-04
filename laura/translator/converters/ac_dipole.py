from .base import BaseElementTranslator
from laura.models.simulation import ACDipoleSimulationElement
from ..utils.functions import sanitize_string


class ACDipoleTranslator(BaseElementTranslator):
    """
    Translator class for converting a :class:`~laura.models.element.Horizontal_AC_Dipole`
    or :class:`~laura.models.element.Vertical_AC_Dipole` element instance into a
    string or object that can be understood by various simulation codes.
    """

    simulation: ACDipoleSimulationElement
    """AC dipole simulation element."""

    def to_madx(self, at: float = None) -> str:
        """
        Generates a string representation of the object's properties in the
        MAD-X format, as a MAD-X ``HACDIPOLE``/``VACDIPOLE`` element. MAD-X
        ``VOLT`` is in MV and ``FREQ`` in MHz (LAURA stores V and Hz).

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

        volt = self.simulation.field_amplitude
        functional = not self._resolve_functional and self.is_functional(volt)
        if functional:
            string += f", volt := ({volt}) / 1e6"
        else:
            resolved = self.resolve(volt)
            if resolved:
                string += f", volt = {resolved / 1e6}"
        if self.simulation.frequency:
            string += f", freq = {self.simulation.frequency / 1e6}"
        lag = self.simulation.phase
        functional = not self._resolve_functional and self.is_functional(lag)
        if functional:
            string += f", lag := ({lag}) / 360"
        else:
            resolved = self.resolve(lag)
            if resolved:
                string += f", lag = {resolved / 360.0}"
        for i, val in enumerate(self.simulation.ramp):
            if val:
                string += f", ramp{i + 1} = {val}"
        if at is not None:
            string += f", at = {at}"
        return string + ";\n"

    def to_xsuite(self, beam_length: int, revolution_frequency: float | None = None) -> tuple:
        """
        Generates an Xsuite ``ACDipole`` object based on the element's properties.

        Xsuite's ``ACDipole.freq`` is expressed in units of :math:`2\\pi` per
        turn (a tune-like, machine-revolution-relative quantity), not an
        absolute frequency, whereas this element's ``simulation.frequency`` is
        stored in Hz. Converting between the two requires the ring's
        revolution frequency, which an individual element translator has no
        access to by default -- pass it explicitly via ``revolution_frequency``
        [Hz] (e.g. ``beta0 * c / circumference``) when calling this method
        directly to have it done automatically; if omitted,
        ``simulation.frequency`` is passed through as-is (rescale it yourself
        before use).

        Parameters
        ----------
        beam_length: int
            Number of macroparticles in the beam (unused; kept for interface
            consistency with other :meth:`to_xsuite` implementations).
        revolution_frequency: float, optional
            The ring's revolution frequency [Hz]. If given,
            ``simulation.frequency`` [Hz] is converted to Xsuite's per-turn
            convention via ``freq / revolution_frequency``; if omitted, the
            raw (Hz) value is passed through unconverted.

        Returns
        -------
        tuple
            (objectname, Xsuite object, properties[dict])
        """
        from xtrack import ACDipole as ACDipole_xs

        self.start_write()
        plane = "h" if self.hardware_type == "Horizontal_AC_Dipole" else "v"
        freq = self.simulation.frequency
        if revolution_frequency:
            freq = freq / revolution_frequency
        properties = {
            "volt": self.resolve(self.simulation.field_amplitude),
            "freq": freq,
            "lag": self.resolve(self.simulation.phase),
            "ramp": list(self.simulation.ramp),
            "plane": plane,
        }
        return self.name, ACDipole_xs, properties
