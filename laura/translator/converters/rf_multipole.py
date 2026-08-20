from warnings import warn

from .base import BaseElementTranslator
from laura.models.simulation import RFMultipoleSimulationElement
from ..utils.functions import sanitize_string


class RFMultipoleTranslator(BaseElementTranslator):
    """
    Translator class for converting a :class:`~laura.models.element.RFMultipole`
    element instance into a string or object that can be understood by
    various simulation codes.
    """

    simulation: RFMultipoleSimulationElement
    """RF multipole simulation element."""

    def to_madx(self, at: float = None) -> str:
        """
        Generates a string representation of the object's properties in the
        MAD-X format, as a MAD-X ``RFMULTIPOLE`` element. MAD-X ``VOLT`` is in
        MV and ``FREQ`` in MHz (LAURA stores V and Hz), and ``LAG`` is the
        phase lag in fractions of a full RF cycle, following the same
        convention as :meth:`RFCavityTranslator.to_madx
        <laura.translator.converters.cavity.RFCavityTranslator.to_madx>`.

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
            string += f", lag := (90 - ({lag})) / 360"
        else:
            resolved = self.resolve(lag)
            string += f", lag = {(90 - resolved) / 360.0}"
        if any(self.simulation.knl):
            string += f", knl = {{{', '.join(str(v) for v in self.simulation.knl)}}}"
        if any(self.simulation.ksl):
            string += f", ksl = {{{', '.join(str(v) for v in self.simulation.ksl)}}}"
        if any(self.simulation.pnl):
            string += f", pnl = {{{', '.join(str(v) for v in self.simulation.pnl)}}}"
        if any(self.simulation.psl):
            string += f", psl = {{{', '.join(str(v) for v in self.simulation.psl)}}}"
        if at is not None:
            string += f", at = {at}"
        return string + ";\n"

    def to_xsuite(self, beam_length: int) -> tuple:
        """
        Generates an Xsuite ``RFMultipole`` object based on the element's
        properties.

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
        from xtrack import RFMultipole as RFMultipole_xs

        self.start_write()
        properties = {
            "voltage": self.resolve(self.simulation.field_amplitude),
            "frequency": self.simulation.frequency,
            "lag": self.resolve(self.simulation.phase),
            "knl": list(self.simulation.knl),
            "ksl": list(self.simulation.ksl),
            "pn": list(self.simulation.pnl),
            "ps": list(self.simulation.psl),
        }
        return self.name, RFMultipole_xs, properties

    def to_bdsim(
        self, section_aperture: dict | None = None, charge_sign: int | float = 1
    ) -> object:
        """
        Generates a BDSIM object based on the element's properties and type.

        BDSIM has no RF multipole, so the integrated strengths are exported as a
        static ``multipole`` (or ``thinmultipole`` at zero length) and the RF
        modulation -- frequency, phase and the per-order phases ``pnl``/``psl``
        -- is dropped. A warning names what was discarded.

        Parameters
        ----------
        section_aperture: dict, optional
                Dictionary containing aperture information for the section,
                which may be used to set the aperture of the BDSIM element.
        charge_sign: int or float, optional
                Beam particle charge sign; see
                :meth:`~laura.translator.converters.base.BaseElementTranslator.to_bdsim`.

        Returns
        -------
        object
            BDSIM object
        """
        from ..conversion_rules.codes import bdsim_conversion

        thin = not self.physical.length
        if thin:
            from pybdsim.Builder import ThinMultipole

            obj = ThinMultipole
        else:
            obj = bdsim_conversion.bdsim_conversion_rules[self.hardware_type]
        keywords = self._bdsim_keywords(obj, section_aperture)
        keywords["knl"] = tuple(self.simulation.knl or ())
        keywords["ksl"] = tuple(self.simulation.ksl or ())
        if self.verbose:
            warn(
                f"WARNING! BDSIM has no RF multipole; {self.name} exported as a static "
                f"{'thinmultipole' if thin else 'multipole'} -- frequency, phase, pnl "
                "and psl are not carried."
            )
        return obj(**self._bdsim_charge_sign(keywords, charge_sign))
