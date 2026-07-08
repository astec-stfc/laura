from .base import BaseElementTranslator
from laura.models.simulation import BeamBeamSimulationElement
from laura.models.constants import elementary_charge
from ..utils.functions import sanitize_string


class BeamBeamTranslator(BaseElementTranslator):
    """
    Translator class for converting a :class:`~laura.models.element.BeamBeam`
    element instance into a string or object that can be understood by
    various simulation codes.
    """

    simulation: BeamBeamSimulationElement
    """Beam-beam simulation element."""

    def to_madx(self, at: float = None) -> str:
        """
        Generates a string representation of the object's properties in the
        MAD-X format, as a MAD-X ``BEAMBEAM`` element.

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
        string = sanitize_string(self.name) + ": " + etype
        if self.simulation.charge:
            string += f", charge = {self.simulation.charge}"
        if self.simulation.n_particles:
            string += f", npart = {self.simulation.n_particles}"
        string += f", xma = {self.simulation.horizontal_offset}"
        string += f", yma = {self.simulation.vertical_offset}"
        if self.simulation.horizontal_sigma:
            string += f", sigx = {self.simulation.horizontal_sigma}"
        if self.simulation.vertical_sigma:
            string += f", sigy = {self.simulation.vertical_sigma}"
        if self.simulation.width:
            string += f", width = {self.simulation.width}"
        if at is not None:
            string += f", at = {at}"
        return string + ";\n"

    def to_elegant(self) -> str:
        """
        Generates a string representation of the object's properties in the
        ELEGANT format, as an ELEGANT ``BEAMBEAM`` element. ELEGANT's
        ``CHARGE`` is the *total* charge of the opposing bunch in Coulombs
        (``n_particles * charge * e``), unlike MAD-X/Xsuite which take the
        constituent-particle charge and particle count separately.

        Returns
        -------
        str
            A formatted string representing the object's properties in
            ELEGANT format.
        """
        self.start_write()
        etype = self._convertType_Elegant(self.hardware_type)
        string = self.name + ": " + etype
        total_charge = self.simulation.n_particles * self.simulation.charge * elementary_charge
        if total_charge:
            string += f", charge = {total_charge}"
        string += f", xcenter = {self.simulation.horizontal_offset}"
        string += f", ycenter = {self.simulation.vertical_offset}"
        if self.simulation.horizontal_sigma:
            string += f", xsize = {self.simulation.horizontal_sigma}"
        if self.simulation.vertical_sigma:
            string += f", ysize = {self.simulation.vertical_sigma}"
        return string + ";\n"

    def to_xsuite(self, beam_length: int) -> tuple:
        """
        Generates an Xsuite/``xfields`` ``BeamBeamBiGaussian2D`` object based
        on the element's properties -- the thin, single-slice weak-strong
        model. ``xfields`` also provides ``BeamBeamBiGaussian3D`` for finite
        bunch-length (hourglass) effects, which needs per-slice longitudinal
        configuration this element does not currently model, so it is not
        used here even when ``simulation.width`` is set.

        Both beams are assumed ultra-relativistic (``other_beam_beta0 = 1``).

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
        from xfields import BeamBeamBiGaussian2D

        self.start_write()
        properties = {
            "other_beam_q0": self.simulation.charge,
            "other_beam_beta0": 1.0,
            "other_beam_num_particles": self.simulation.n_particles,
            "other_beam_shift_x": self.simulation.horizontal_offset,
            "other_beam_shift_y": self.simulation.vertical_offset,
            "other_beam_Sigma_11": self.simulation.horizontal_sigma ** 2,
            "other_beam_Sigma_33": self.simulation.vertical_sigma ** 2,
        }
        return self.name, BeamBeamBiGaussian2D, properties
