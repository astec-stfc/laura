from pydantic import computed_field
from typing import Type
from warnings import warn
from .constants import pi, c, e, m_e, epsilon_0
import numpy as np

from .baseModels import IgnoreExtra, T
from ._generated import (
    _LaserElementBase,
    _LaserHalfWavePlateElementBase,
    _LaserEnergyMeterElementBase,
    _LaserMirrorSenseBase,
    _LaserMirrorElementBase,
)


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
        Laser amplitude: ((e*lambda0)/(pi*m_e*c**2*w0)) * np.sqrt( E/(pi*epsilon_0*c*tau_FWHM) )

        Returns
        -------
        float
            Laser amplitude (dimensionless)

        Raises
        ------
        ValueError
            If any of the required parameters are not set or non-positive
        """
        params = [
            self.wavelength,
            self.waist,
            self.pulse_energy,
            self.pulse_duration_fwhm,
        ]
        if any(p is None or p <= 0 for p in params):
            warn(
                "Wavelength, waist, pulse energy and pulse duration must be positive "
                "to compute laser amplitude."
            )
            return 0
        return ((e * self.wavelength) / (pi * m_e * c**2 * self.waist)) * np.sqrt(
            self.pulse_energy / (pi * epsilon_0 * c * self.pulse_duration_fwhm)
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
            raise ValueError("Wavelength must be positive to compute laser angular frequency.")
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
    """Laser info model."""

    pass