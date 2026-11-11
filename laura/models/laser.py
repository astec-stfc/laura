from warnings import warn

import numpy as np
from pydantic import computed_field

from ._generated import (
    _LaserElementBase,
    _LaserEnergyMeterElementBase,
    _LaserHalfWavePlateElementBase,
    _LaserMirrorElementBase,
    _LaserMirrorSenseBase,
)
from .base_models import IgnoreExtra
from .constants import c, e, epsilon_0, m_e, pi


class LaserElement(_LaserElementBase):
    """Laser info model."""

    @property
    def pulse_duration_1e_field(self) -> float:
        """
        Pulse duration as the 1/e half-width of the *field* envelope, in seconds.

        Returns
        -------
        float
            Field 1/e half-width [s]
        """
        return self.pulse_duration_fwhm / np.sqrt(2 * np.log(2))

    @computed_field
    @property
    def amplitude(self) -> float:
        """
        Peak normalised vector potential a0.

        :attr:`~a0` if it is set. Otherwise it is derived from the pulse energy
        for a Gaussian pulse, whose peak power is
        ``P = 2*sqrt(ln2/pi) * E / tau_FWHM`` and peak intensity
        ``I = 2*P/(pi*w0**2)``, giving
        ``a0 = (e*lambda0/(pi*m_e*c**2*w0)) * sqrt(P/(pi*epsilon_0*c))``,
        over sqrt(2) for circular polarization, whose a0 is per component.

        Returns
        -------
        float
            Laser amplitude (dimensionless); 0, with a warning, if a0 is not
            set and any of the parameters it is derived from is non-positive.
        """
        if self.a0 is not None:
            return self.a0
        params = [
            self.wavelength,
            self.waist,
            self.pulse_energy,
            self.pulse_duration_fwhm,
        ]
        if any(p is None or p <= 0 for p in params):
            warn(
                "Set a0, or a positive wavelength, waist, pulse energy and pulse "
                "duration, to compute laser amplitude."
            )
            return 0
        peak_power = (
            2 * np.sqrt(np.log(2) / pi) * self.pulse_energy / self.pulse_duration_fwhm
        )
        if str(self.polarization) == "circular":
            peak_power /= 2
        return ((e * self.wavelength) / (pi * m_e * c**2 * self.waist)) * np.sqrt(
            peak_power / (pi * epsilon_0 * c)
        )

    @property
    def angular_frequency(self) -> float:
        """
        Laser angular frequency: 2*pi*c/lambda0

        Returns
        -------
        float
            Laser angular frequency [rad/s]

        Raises
        ------
        ValueError
            If wavelength is not set or non-positive
        """
        if self.wavelength <= 0:
            raise ValueError(
                "Wavelength must be positive to compute laser angular frequency."
            )
        return 2 * pi * c / self.wavelength

    @property
    def _is_few_cycle(self) -> bool:
        """
        Check if the laser is a few-cycle pulse, which is the case if :attr:`~pulse_duration_fwhm` *
        :attr:`~angular_frequency` is not greater than 10.

        Returns
        -------
        bool
            True if laser is a few-cycle pulse, False otherwise

        Raises
        ------
        ValueError
            If wavelength is not set or non-positive
        """
        if self.wavelength <= 0:
            raise ValueError(
                "Wavelength must be positive to compute laser angular frequency."
            )
        return self.angular_frequency * self.pulse_duration_fwhm <= 10


class LaserHalfWavePlateElement(_LaserHalfWavePlateElementBase):
    """
    Laser half-wave plate model.
    """

    pass


class LaserEnergyMeterElement(_LaserEnergyMeterElementBase):
    """
    Laser energy meter model.
    """

    pass


class LaserMirrorSense(_LaserMirrorSenseBase):
    """
    Laser mirror sense model.
    """

    pass


class LaserMirrorElement(_LaserMirrorElementBase, IgnoreExtra):
    """Laser mirror model."""

    pass
