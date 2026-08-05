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
            If any of the requires parameters are not set or non-positive
        """
        if (
            any(
                [
                    self.wavelength,
                    self.waist,
                    self.pulse_energy,
                    self.pulse_duration_fwhm,
                ]
            )
            <= 0
        ):
            warn(
                "Wavelength, waist, pulse enegy and pulse duration must be positive "
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