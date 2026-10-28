import os
from math import pi
from warnings import warn

from laura.models.simulation import ACDipoleSimulationElement

from ..utils.ac_dipole import MV_PER_VOLT, SINE_TO_COSINE_TURNS
from ..utils.functions import sanitize_string
from ..utils.sdds_file import SDDSFile, SddsTypes
from .base import BaseElementTranslator, elegant_line


class ACDipoleTranslator(BaseElementTranslator):
    """
    Translator class for converting a :class:`~laura.models.element.HorizontalACDipole`
    or :class:`~laura.models.element.VerticalACDipole` element instance into a
    string or object that can be understood by various simulation codes.
    """

    simulation: ACDipoleSimulationElement
    """AC dipole simulation element."""

    @property
    def _vertical(self) -> bool:
        return self.hardware_type == "Vertical_AC_Dipole"

    @property
    def _integrated_field(self) -> float:
        """Peak integrated field [T*m] -- see :data:`MV_PER_VOLT`."""
        return self.resolve(self.simulation.field_amplitude) * MV_PER_VOLT

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
        etype = self._convert_type_madx(self.hardware_type)
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
        if self.simulation.waveform:
            warn(
                f"AC dipole {self.name!r} carries a sampled waveform; MAD-X's "
                "HACDIPOLE/VACDIPOLE drives a sinusoid with a four-point "
                "ramp1-ramp4 envelope and has no sampled form, so the "
                "waveform was not written."
            )
        if at is not None:
            string += f", at = {at}"
        return string + ";\n"

    def to_bmad(self) -> str:
        """
        Generates a string representation of the object's properties in the
        Bmad format, as a Bmad ``AC_KICKER`` element.

        A waveform becomes ``amp_vs_time``, a sinusoid becomes a single-entry
        ``frequencies``; Bmad takes one or the other, never both.

        Returns
        -------
        str
            String representation of the element for Bmad
        """
        parameters = {"l": self.length}
        parameters["bl_vkick" if self._vertical else "bl_hkick"] = (
            self._integrated_field
        )
        waveform = self.simulation.waveform
        if waveform:
            knots = ", ".join(
                f"({time}, {factor})"
                for time, factor in zip(waveform.time, waveform.factor)
            )
            parameters["amp_vs_time"] = "{" + knots + "}"
            if waveform.interpolation == "hold":
                warn(
                    f"AC dipole {self.name!r} holds each waveform knot until "
                    "the next; Bmad interpolates its knots and offers only "
                    "cubic or linear, so the staircase was written as linear "
                    "slews between the same knots."
                )
            parameters["interpolation"] = (
                "cubic" if waveform.interpolation == "spline" else "linear"
            )
            if self.simulation.frequency:
                warn(
                    f"AC dipole {self.name!r} carries both a waveform and a "
                    f"frequency ({self.simulation.frequency} Hz); a Bmad "
                    "AC_Kicker takes amp_vs_time or frequencies but not both, "
                    "so only the waveform was written."
                )
        elif self.simulation.frequency:
            phase = self.resolve(self.simulation.phase) or 0.0
            phi = phase / 360.0 + SINE_TO_COSINE_TURNS
            parameters["frequencies"] = (
                "{(" + f"{self.simulation.frequency}, 1.0, {phi}" + ")}"
            )
        if any(self.simulation.ramp):
            warn(
                f"AC dipole {self.name!r} has a ramp1-ramp4 envelope; that is "
                "MAD-X's turn-indexed way of switching a driven oscillation on "
                "and off, and Bmad's AC_Kicker has no equivalent, so the "
                "envelope was not written."
            )
        return self._format_bmad("ac_kicker", parameters)

    def to_elegant(self, Brho: float | None = None) -> str:
        """
        Generates a string representation of the object's properties in the
        ELEGANT format, as an ELEGANT ``BUMPER`` element.

        ELEGANT states a bumper's strength as ``ANGLE``, a deflection in
        radians, so turning LAURA's ``field_amplitude`` into one needs the
        magnetic rigidity: ``angle = B*L / Brho``.

        ``FIRE_ON_PASS`` is deliberately *not*
        written: when the device fires is a property of the study, not of the
        machine, and belongs in the tracking settings.

        Parameters
        ----------
        Brho: float, optional
            Magnetic rigidity [T*m]. If omitted, ``ANGLE`` is not written and
            a warning is raised.

        Returns
        -------
        str
            A formatted string representing the object's properties in
            ELEGANT format.
        """
        self.start_write()
        etype = self._convert_type_elegant(self.hardware_type)
        terms = [f"l = {self.length}"]
        field = self._integrated_field
        if Brho:
            terms.append(f"angle = {field / Brho}")
        elif field:
            warn(
                f"AC dipole {self.name!r} has an integrated field of {field} "
                "T*m, but ELEGANT's BUMPER states its strength as ANGLE in "
                "radians; converting needs the magnetic rigidity. Pass "
                f"to_elegant(Brho=...) to have {self.name!r} deflect at all."
            )
        if self._vertical:
            terms.append(f"tilt = {pi / 2}")
        waveform = self.simulation.waveform
        if waveform:
            terms.append(f'waveform = "{self._write_elegant_waveform()}=t+factor"')
            if waveform.interpolation != "linear":
                warn(
                    f"AC dipole {self.name!r} interpolates its waveform knots "
                    f"as {waveform.interpolation!r}; ELEGANT reads a WAVEFORM "
                    "file by linear interpolation only, so the pulse was "
                    "written as straight lines between the same knots."
                )
        elif self.simulation.frequency:
            warn(
                f"AC dipole {self.name!r} is a sinusoid at "
                f"{self.simulation.frequency} Hz, and an ELEGANT BUMPER is "
                "driven by a sampled WAVEFORM with no frequency of its own, so "
                f"{self.name!r} was written as a static kick. ELEGANT's RFDF "
                "models a driven transverse oscillation, but is a deflecting "
                "cavity rather than a dipole; choosing it is a modelling "
                "decision, not a translation."
            )
        return elegant_line(self.name + ": " + etype, terms)

    def _write_elegant_waveform(self) -> str:
        """
        Write the waveform out as the two-column SDDS file an ELEGANT
        ``WAVEFORM`` reads, and return its basename.
        """
        self.make_directory()
        basename = f"{sanitize_string(self.name)}_waveform.sdds"
        sdds = SDDSFile(index=1, ascii=True)
        sdds.add_columns(
            ["t", "factor"],
            [
                list(self.simulation.waveform.time),
                list(self.simulation.waveform.factor),
            ],
            [SddsTypes.SDDS_DOUBLE, SddsTypes.SDDS_DOUBLE],
            ["s", ""],
            ["", ""],
        )
        sdds.write_file(os.path.join(self.directory, basename))
        return basename

    def to_xsuite(
        self, beam_length: int, revolution_frequency: float | None = None
    ) -> tuple:
        """
        Generates an Xsuite ``ACDipole`` object based on the element's properties.

        Xsuite's ``ACDipole.freq`` is in units of :math:`2\\pi` per turn (a
        tune-like quantity), whereas ``simulation.frequency`` is in Hz, so
        converting needs the ring's ``revolution_frequency``.

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
        if self.simulation.waveform:
            warn(
                f"AC dipole {self.name!r} carries a sampled waveform; "
                "xtrack.ACDipole drives a sinusoid, and Xsuite expresses a "
                "sampled pulse as a FunctionPieceWiseLinear bound to the "
                "element's volt through line.functions, which an element "
                "translator cannot build. The waveform was not applied."
            )
        properties = {
            # Xtrack's volt is in MV and its lag in units of 2*pi, the same two
            # conventions MAD-X uses; LAURA stores V and degrees.
            "volt": self._integrated_field,
            "freq": freq,
            "lag": (self.resolve(self.simulation.phase) or 0.0) / 360.0,
            "ramp": list(self.simulation.ramp),
            "plane": plane,
        }
        return self.name, ACDipole_xs, properties
