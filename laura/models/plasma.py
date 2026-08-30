import numpy as np
from scipy.constants import e, m_e, m_p, epsilon_0, pi, c
from pydantic import (
    BaseModel,
    model_serializer,
    Field,
    field_validator,
    NonNegativeInt,
    create_model,
    NonNegativeFloat,
    computed_field,
)
from .baseModels import IgnoreExtra, T
from ._generated import _PlasmaElementBase


class PlasmaElement(_PlasmaElementBase):
    """Plasma model."""

    pass

    def plasma_wavelength(self) -> float:
        """
        Plasma wavelength in metres: 2*pi*c*sqrt(epsilon_0*mass/(density*e^2))

        Returns
        -------
        float
            Plasma wavelength in metres

        Raises
        ------
        ValueError
            If density is not positive
        """
        if self.density <= 0:
            raise ValueError("Density must be positive to compute plasma wavelength.")
        return 2 * pi * c * np.sqrt((epsilon_0 * self.mass(self.species)) / (self.density * e ** 2))

    def plasma_frequency(self) -> float:
        """
        Plasma frequency: sqrt(density*e^2)/epsilon_0/mass)

        Returns
        -------
        float
            Plasma frequency

        Raises
        ------
        ValueError
            If density is not positive
        """
        if self.density <= 0:
            raise ValueError("Density must be positive to compute plasma frequency.")
        return np.sqrt((self.density * e ** 2) / (epsilon_0 * self.mass(self.species)))

    @staticmethod
    def critical_density(omega0: float) -> float:
        """
        Critical plasma density (electrons.meters^-3),
        omega0**2*epsilon_0*m_e/e**2

        Parameters
        ----------
        omega0: float
            Laser angular frequency

        Returns
        -------
        float
            Critical plasma density
        """
        return omega0 ** 2 * epsilon_0 * m_e / e ** 2

    def _density_profile(self, z: float, r: float) -> np.ndarray:
        """
        Define plasma density as a function of length.
        This takes the :attr:`~length` of the plasma element and calculates the density profile based
        on the :attr:`~ramp_up`, :attr:`~plateau`, :attr:`~ramp_down` and :attr:`~ramp_decay_length` attributes.

        Parameters
        ----------
        z : float
            Longitudinal position along the plasma element in metres
        r : float
            Radial position from the axis in metres (not yet implemented)

        Returns
        -------
        np.ndarray
            Array of length `n_steps` containing the density profile in m^-3
        """
        # Allocate relative density array.
        if self.plateau <= 0:
            raise ValueError("Plateau length must be positive for density profile.")
        if self.ramp_up < 0 or self.ramp_down < 0 or self.ramp_decay_length <= 0:
            raise ValueError(
                "Ramp lengths must be non-negative and ramp decay length must be positive for density profile."
            )
        n = np.ones_like(z)
        # Add upramp.
        n = np.where(z < self.ramp_up, 1 / (1 + (self.ramp_up - z) / self.ramp_decay_length) ** 2, n)
        # Add downramp.
        try:
            n = np.where(
                (z > self.ramp_up + self.plateau) & (z <= self.ramp_up + self.plateau + self.ramp_down),
                1 / (1 + (z - self.ramp_up - self.plateau) / self.ramp_decay_length) ** 2,
                n,
            )
        except ZeroDivisionError:
            n = np.where(
                (z > self.ramp_up + self.plateau) & (z <= self.ramp_up + self.plateau + self.ramp_down),
                1,
                n,
            )
        # Make zero after downramp.
        n = np.where(z > self.ramp_up + self.plateau + self.ramp_down, 1e-6, n)
        # Return absolute density.
        return n * self.density

    @staticmethod
    def mass(species: Literal["electron", "positron", "hydrogen"]) -> float:
        """
        Mass of plasma species in kg.

        Parameters
        ----------
        species: str
            Species of plasma -- supported values are "electron", "positron" and "hydrogen"

        Returns
        -------
        float
            Mass of plasma species in kg

        Raises
        ------
        ValueError
            If species is not supported
        """
        if species == "electron":
            return m_e
        elif species == "positron":
            return m_e
        elif species == "hydrogen":
            return m_p
        else:
            raise ValueError(f"Species {species} not supported.")

    @staticmethod
    def charge(species: Literal["electron", "positron", "hydrogen"]) -> float:
        """
        Charge of plasma species in C.

        Parameters
        ----------
        species: str
            Species of plasma -- supported values are "electron", "positron" and "hydrogen"

        Returns
        -------
        float
            Charge of plasma species in C

        Raises
        ------
        ValueError
            If species is not supported
        """
        if species == "electron":
            return -e
        elif species == "positron":
            return e
        elif species == "hydrogen":
            return e
        else:
            raise ValueError(f"Species {species} not supported.")

