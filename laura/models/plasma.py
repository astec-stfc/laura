import numpy as np
from typing import Literal
from scipy.constants import e, m_e, m_p, epsilon_0, pi, c
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

    def relative_density_profile(self, z, r=0.0) -> np.ndarray:
        """
        Plasma density as a function of position, relative to :attr:`~density`.

        The longitudinal shape is chosen by :attr:`~density_profile_type`:

        ``decaying``
            ``1/(1 + dz/ramp_decay_length)**2`` ramps either side of the plateau.
        ``linear``
            Ramps linearly from zero to full density over :attr:`~ramp_up`, and
            back to zero over :attr:`~ramp_down`.
        ``tabulated``
            Linear interpolation of :attr:`~density_profile_values` against
            :attr:`~density_profile_positions`.
        ``custom``
            Whatever :attr:`~density_profile_function` names.

        All of them except ``custom`` are measured from
        :attr:`~density_profile_start` and are then multiplied by the transverse
        channel ``1 + parabolic_coefficient * r**2``.

        Parameters
        ----------
        z : float or np.ndarray
            Longitudinal position in metres
        r : float or np.ndarray
            Radial position from the axis in metres

        Returns
        -------
        np.ndarray
            Density relative to :attr:`~density`

        Raises
        ------
        ValueError
            If the profile type is not recognised, or the parameters the chosen
            profile needs are not set consistently
        """
        profile_type = str(self.density_profile_type).lower()
        if profile_type == "custom":
            return np.asarray(self.density_profile_callable(z, r), dtype=float)
        dz = np.asarray(z, dtype=float) - self.density_profile_start
        if profile_type == "decaying":
            n = self._decaying_ramp_profile(dz)
        elif profile_type == "linear":
            n = self._linear_ramp_profile(dz)
        elif profile_type == "tabulated":
            n = self._tabulated_profile(dz)
        else:
            raise ValueError(
                f"Invalid density profile type {self.density_profile_type}. "
                "Supported types are 'decaying', 'linear', 'tabulated' and 'custom'."
            )
        if self.parabolic_coefficient:
            n = n * (1 + self.parabolic_coefficient * np.asarray(r, dtype=float) ** 2)
        return n

    def _density_profile(self, z, r=0.0) -> np.ndarray:
        """
        Absolute plasma density as a function of position, in m^-3.

        This is :func:`~relative_density_profile` scaled by :attr:`~density`, and
        is the form codes such as Wake-T expect. PIC codes such as FBPIC want the
        relative profile instead.

        Parameters
        ----------
        z : float or np.ndarray
            Longitudinal position in metres
        r : float or np.ndarray
            Radial position from the axis in metres

        Returns
        -------
        np.ndarray
            Density in m^-3
        """
        return self.relative_density_profile(z, r) * self.density

    @property
    def density_profile_callable(self):
        """
        The callable named by :attr:`~density_profile_function`.

        The name is a dotted path, written either as ``package.module:function``
        or as ``package.module.function``, and must resolve to something with the
        signature ``f(z, r)`` returning the density relative to :attr:`~density`.

        Returns
        -------
        Callable
            The resolved density function

        Raises
        ------
        ValueError
            If no function is named, or the name does not resolve to a callable
        """
        import importlib

        path = self.density_profile_function
        if not path:
            raise ValueError(
                "density_profile_type is 'custom' but density_profile_function "
                "does not name a function."
            )
        module_name, _, attr = path.partition(":")
        if not attr:
            module_name, _, attr = path.rpartition(".")
        try:
            func = getattr(importlib.import_module(module_name), attr)
        except (ImportError, AttributeError, ValueError) as exc:
            raise ValueError(
                f"Could not resolve density_profile_function {path!r}: {exc}"
            ) from exc
        if not callable(func):
            raise ValueError(f"density_profile_function {path!r} is not callable.")
        return func

    def _check_ramp_lengths(self, decay: bool = False) -> None:
        """
        Validate the ramp/plateau lengths the built-in profiles rely on.

        Parameters
        ----------
        decay : bool
            Also require :attr:`~ramp_decay_length` to be positive

        Raises
        ------
        ValueError
            If the plateau is not positive, or a ramp length is negative
        """
        if self.plateau <= 0:
            raise ValueError("Plateau length must be positive for density profile.")
        if self.ramp_up < 0 or self.ramp_down < 0:
            raise ValueError("Ramp lengths must be non-negative for density profile.")
        if decay and self.ramp_decay_length <= 0:
            raise ValueError(
                "Ramp decay length must be positive for a 'decaying' density profile."
            )

    def _decaying_ramp_profile(self, dz: np.ndarray) -> np.ndarray:
        """
        ``1/(1 + dz/ramp_decay_length)**2`` ramps either side of the plateau.

        Parameters
        ----------
        dz : np.ndarray
            Longitudinal position relative to :attr:`~density_profile_start`

        Returns
        -------
        np.ndarray
            Relative density
        """
        self._check_ramp_lengths(decay=True)
        n = np.ones_like(dz)
        # Add upramp.
        n = np.where(
            dz < self.ramp_up,
            1 / (1 + (self.ramp_up - dz) / self.ramp_decay_length) ** 2,
            n,
        )
        # Add downramp.
        plateau_end = self.ramp_up + self.plateau
        n = np.where(
            (dz > plateau_end) & (dz <= plateau_end + self.ramp_down),
            1 / (1 + (dz - plateau_end) / self.ramp_decay_length) ** 2,
            n,
        )
        # Make (almost) zero after downramp.
        return np.where(dz > plateau_end + self.ramp_down, 1e-6, n)

    def _linear_ramp_profile(self, dz: np.ndarray) -> np.ndarray:
        """
        Linear ramps either side of the plateau, zero outside the column.

        Parameters
        ----------
        dz : np.ndarray
            Longitudinal position relative to :attr:`~density_profile_start`

        Returns
        -------
        np.ndarray
            Relative density
        """
        self._check_ramp_lengths()
        n = np.ones_like(dz)
        if self.ramp_up > 0:
            n = np.where(dz < self.ramp_up, dz / self.ramp_up, n)
        plateau_end = self.ramp_up + self.plateau
        if self.ramp_down > 0:
            n = np.where(
                (dz > plateau_end) & (dz <= plateau_end + self.ramp_down),
                1 - (dz - plateau_end) / self.ramp_down,
                n,
            )
        n = np.where(dz < 0, 0.0, n)
        return np.where(dz > plateau_end + self.ramp_down, 0.0, n)

    def _tabulated_profile(self, dz: np.ndarray) -> np.ndarray:
        """
        Linear interpolation of a tabulated profile.

        Parameters
        ----------
        dz : np.ndarray
            Longitudinal position relative to :attr:`~density_profile_start`

        Returns
        -------
        np.ndarray
            Relative density

        Raises
        ------
        ValueError
            If the two tables are empty or of different lengths
        """
        positions = np.asarray(self.density_profile_positions, dtype=float)
        values = np.asarray(self.density_profile_values, dtype=float)
        if positions.size == 0 or positions.size != values.size:
            raise ValueError(
                "A 'tabulated' density profile needs density_profile_positions "
                "and density_profile_values to be non-empty and the same length; "
                f"got {positions.size} and {values.size}."
            )
        order = np.argsort(positions)
        return np.interp(dz, positions[order], values[order])

    def thermal_momentum(
        self, species: str | None = None, mass: float | None = None
    ) -> float:
        """
        Normalised thermal momentum spread, sqrt(k*T/(m*c^2)), from
        :attr:`~temperature`.

        This is the spread of ``u = gamma*v/c``. It assumes a
        non-relativistic plasma, which any temperature small
        against the species rest energy satisfies.

        Parameters
        ----------
        species: str, optional
            Species to take the mass of, defaulting to :attr:`~species`
        mass: float, optional
            Mass in kg to use, for a species outside the handful
            :func:`~mass` knows -- i.e. an ionizable gas.

        Returns
        -------
        float
            Normalised momentum spread, zero for a cold plasma
        """
        if not self.temperature:
            return 0.0
        if mass is None:
            mass = self.mass(species or self.species)
        return float(np.sqrt(self.temperature * e / (mass * c ** 2)))

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

