from laura.models.constants import elementary_charge
from laura.models.simulation import BeamBeamSimulationElement

from ..utils.functions import sanitize_string
from .base import BaseElementTranslator


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
        etype = self._convert_type_madx(self.hardware_type)
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
        etype = self._convert_type_elegant(self.hardware_type)
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
        Generates an Xsuite/``xfields`` ``BeamBeamBiGaussian2D`` object: the thin,
        single-slice weak-strong model. ``BeamBeamBiGaussian3D`` is not used, even
        when ``simulation.width`` is set, as it needs per-slice configuration this
        element does not model.

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

    def to_warpx(
        self, p0c: float, rest_energy: float, z_centre: float, sigma_z: float, macroparticles: int = 10000
    ) -> dict:
        """
        The opposing bunch as a WarpX species ``opposing`` for a strong-strong
        collision: a Gaussian of ``n_particles`` particles of ``charge`` e,
        rms sizes ``horizontal/vertical_sigma`` and ``width``, offset by
        ``horizontal/vertical_offset``, moving towards -z. Its momentum and mass
        are not in the element so the caller gives them (simba: the incoming beam's,
        unless overridden).

        Parameters
        ----------
        p0c, rest_energy : float
            Opposing particles' momentum and rest energy [eV]
        z_centre : float
            Code z of the bunch centre at t = 0 [m]
        sigma_z : float
            Rms length to use when ``width`` is 0 [m]
        macroparticles : int
            Macroparticles in the bunch

        Returns
        -------
        dict
            ``{input key: value}``, in SI units

        Raises
        ------
        ValueError
            Without a size, a particle count or a charge
        """
        from scipy.constants import c, e

        sim = self.simulation
        if not (sim.horizontal_sigma and sim.vertical_sigma and sim.n_particles and sim.charge):
            raise ValueError(
                f"{self.name}: a WarpX opposing bunch needs horizontal_sigma, vertical_sigma, "
                "n_particles and charge."
            )
        return {
            "opposing.charge": sim.charge * e,
            "opposing.mass": rest_energy * e / c**2,
            "opposing.injection_style": "gaussian_beam",
            "opposing.npart": macroparticles,
            "opposing.q_tot": sim.charge * e * sim.n_particles,
            "opposing.x_rms": sim.horizontal_sigma,
            "opposing.y_rms": sim.vertical_sigma,
            "opposing.z_rms": sim.width or sigma_z,
            "opposing.x_m": sim.horizontal_offset,
            "opposing.y_m": sim.vertical_offset,
            "opposing.z_m": z_centre,
            "opposing.momentum_distribution_type": "constant",
            "opposing.uz": -p0c / rest_energy,  # gamma*beta
        }
