from typing import Any
from warnings import warn

import numpy as np

from laura.models.laser import LaserElement
from laura.models.plasma import PlasmaElement
from laura.models.simulation import PlasmaSimulationElement

from .base import BaseElementTranslator
from .laser import LaserTranslator


class PlasmaTranslator(BaseElementTranslator):
    """
    Translator class for converting a :class:`~laura.models.element.Plasma` instance into a string or
    object that can be understood by various simulation codes.
    """

    plasma: PlasmaElement
    """Plasma element."""

    simulation: PlasmaSimulationElement
    """Plasma simulation element."""

    laser: LaserElement | None
    """Laser element."""

    def to_wake_t(self) -> Any:
        """
        Create a Wake-T plasma element object based on the attributes of this element.

        If a `laser` sub-element is defined, it is also converted to a Wake-T laser object and
        added to the plasma element; if two laser sub-elements are defined, they are summed together
        using the :class:`~wake_t.physics_models.laser.laser_pulse.SummedPulse` class.

        Returns
        -------
        wake_t.PlasmaStage
            Wake-T plasma element object

        Raises
        ------
        ValueError
            If the wakefield model is not supported; note that not all models are implemented yet
        """
        from wake_t.physics_models.laser.laser_pulse import (
            SummedPulse,
        )
        from ..conversion_rules.codes import wake_t_conversion

        type_conversion_rules_wake_t = wake_t_conversion.wake_t_conversion_rules
        if self.simulation.wakefield_model is None and self.verbose:
            warn(
                "No wakefield model defined; no plasma wakefields will be computed."
                f"Supported models are {list(self.simulation.required_attrs.keys())[1:]}."
            )
        elif (
            self.simulation.wakefield_model not in self.simulation.required_attrs.keys()
        ):
            raise ValueError(
                f"Invalid wakefield model {self.simulation.wakefield_model}. "
                f"Supported models are {list(self.simulation.required_attrs.keys())[1:]}."
            )
        commondict = {
            self._convert_keyword_wake_t(param): getattr(self, param)
            for param in self.simulation.required_attrs["common"]
        }
        modeldict = {
            self._convert_keyword_wake_t(param): getattr(self, param)
            for param in self.simulation.required_attrs.get(
                self.simulation.wakefield_model, []
            )
        }
        elemdict = modeldict | commondict | {"density": self._wake_t_density()}
        if self.plasma.ionizable:
            warn(
                f"{self.name} has an ionizable species, which Wake-T does not model; "
                "it is tracked as the pre-ionized plasma alone, with no ionization "
                "injection. Use a PIC code such as FBPIC for that."
            )
        if self.laser is not None and self.driver_laser is None:
            warn(
                f"The laser of {self.name} is an injector, not a wake driver; Wake-T "
                "cannot model the ionization it is there for, so it is left out."
            )
        lasers = []
        if self.driver_laser is not None:
            laser_translator = LaserTranslator.model_validate(self.model_dump())
            lasers.append(laser_translator.to_wake_t())
        if len(lasers) == 1:
            elemdict.update({"laser": lasers[0]})
        elif len(lasers) == 2:
            elemdict.update({"laser": SummedPulse(lasers[0], lasers[1])})
        elif len(lasers) > 2:
            if self.verbose:
                warn(
                    "More than two laser sub-elements found; only the first two will be used."
                )
            elemdict.update({"laser": SummedPulse(lasers[0], lasers[1])})
        obj = type_conversion_rules_wake_t[self.hardware_type](
            wakefield_model=self.simulation.wakefield_model, **elemdict
        )
        return obj

    @property
    def driver_laser(self) -> LaserElement | None:
        """
        The laser driving the wake, or None for a beam-driven stage -- which
        includes one whose only laser is an injector (``role: injector``).
        """
        if isinstance(self.laser, LaserElement) and str(self.laser.role) == "driver":
            return self.laser
        return None

    def _wake_t_density(self) -> float | Any:
        """
        The plasma density in the form Wake-T takes it: a number for a uniform
        plasma, otherwise :func:`~_wake_t_density_profile`, which carries the
        longitudinal profile and any parabolic channel together.

        Returns
        -------
        float or Callable
            Density in m^-3, or a function ``f(z, r)`` returning it
        """
        if self.plasma.is_uniform:
            return float(self.plasma.density)
        return self._wake_t_density_profile

    def _wake_t_density_profile(self, z, r=0.0) -> np.ndarray:
        """
        :func:`~_density_profile`, floored just above zero for Wake-T.

        Wake-T normalises its grid by the local plasma skin depth, which is
        infinite where the density is exactly zero. The floor is the same
        1e-6 of nominal density that the ``decaying`` profile already
        returns past its down-ramp.

        Parameters
        ----------
        z : float or np.ndarray
            Longitudinal position in metres
        r : float or np.ndarray
            Radial position from the axis in metres

        Returns
        -------
        np.ndarray
            Density in m^-3, never less than 1e-6 of :attr:`~plasma.density`
        """
        return np.maximum(
            self._density_profile(z, r), 1e-6 * float(self.plasma.density)
        )

    def laser_to_fbpic(self) -> Any | None:
        """
        Create the FBPIC laser profile for the laser attached to this plasma stage
        via `fbpic.lpa_utils.laser.add_laser_pulse`.

        Returns
        -------
        fbpic.lpa_utils.laser.laser_profiles.LaserProfile or None
            The laser profile, or None if no laser is attached to this stage.
        """
        if not isinstance(self.laser, LaserElement):
            return None
        data = self.model_dump()
        data["hardware_type"] = "Laser"
        data["hardware_class"] = "Laser"
        return LaserTranslator.model_validate(data).to_fbpic()

    def _density_profile(self, z, r=0.0) -> np.ndarray:
        """
        Absolute plasma density as a function of position, in m^-3.

        This is the form Wake-T expects. PIC codes such as FBPIC instead want the
        density *relative* to the nominal density; use
        :func:`~_relative_density_profile` for those.

        Parameters
        ----------
        z : float or np.ndarray
            Longitudinal position along the plasma element in metres
        r : float or np.ndarray
            Radial position from the axis in metres

        Returns
        -------
        np.ndarray
            Density in m^-3
        """
        return self.plasma._density_profile(z, r)

    def _relative_density_profile(self, z, r=0.0) -> np.ndarray:
        """
        Plasma density profile relative to :attr:`~plasma.density`.

        Parameters
        ----------
        z : float or np.ndarray
            Longitudinal position along the plasma element in metres
        r : float or np.ndarray
            Radial position from the axis in metres

        Returns
        -------
        np.ndarray
            Relative density
        """
        return self.plasma.relative_density_profile(z, r)


class PlasmaLensTranslator(PlasmaTranslator):
    """
    Translator for a :class:`~laura.models.element.PlasmaLens` (active plasma lens).

    Only Wake-T models the lens directly. Codes without an equivalent element
    see it as a drift of the same length, with a warning.
    """

    focusing_strength: float = 0.0
    """Focusing gradient [T/m]."""

    wakefields: bool = False
    """Whether the beam-driven plasma wakefields in the lens are modelled."""

    laser: LaserElement | None = None
    """Unused; a plasma lens has no laser driver."""

    def to_wake_t(self) -> Any:
        """
        Create a Wake-T ``ActivePlasmaLens``.

        With :attr:`~wakefields` set, the plasma density and the grid
        settings of the ``simulation`` sub-element are passed on, as for a
        :class:`~PlasmaTranslator` stage.

        Returns
        -------
        wake_t.ActivePlasmaLens
            Wake-T plasma-lens object
        """
        from ..conversion_rules.codes import wake_t_conversion

        kwargs = {
            self._convert_keyword_wake_t(param): getattr(self, param)
            for param in self.simulation.required_attrs["common"]
        }
        if self.wakefields:
            model = self.simulation.wakefield_model or "quasistatic_2d"
            kwargs.update(
                {
                    self._convert_keyword_wake_t(param): getattr(self, param)
                    for param in self.simulation.required_attrs.get(model, [])
                    if not param.startswith("laser_")
                }
            )
            kwargs.update(wakefield_model=model, density=self._wake_t_density())
        return wake_t_conversion.wake_t_conversion_rules["PlasmaLens"](
            foc_strength=self.focusing_strength,
            wakefields=self.wakefields,
            **kwargs,
        )
