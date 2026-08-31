import numpy as np
from laura.models.constants import pi, c, e, m_e, epsilon_0
from typing import Any
from warnings import warn
from .base import BaseElementTranslator
from laura.models.plasma import PlasmaElement
from laura.models.simulation import PlasmaSimulationElement
from laura.models.laser import LaserElement
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

        type_conversion_rules_Wake_T = wake_t_conversion.wake_t_conversion_rules
        if self.simulation.wakefield_model is None:
            warn(
                "No wakefield model defined; no plasma wakefields will be computed."
                f"Supported models are {list(self.simulation.required_attrs.keys())[1:]}."
            )
        elif (
            self.simulation.wakefield_model not in self.simulation.required_attrs.keys()
        ):
            raise ValueError(
                f"Invalid wakefield model {self.wakefield_model}. "
                f"Supported models are {list(self.simulation.required_attrs.keys())[1:]}."
            )
        commondict = {
            self._convertKeyword_WakeT(param): getattr(self, param)
            for param in self.simulation.required_attrs["common"]
        }
        modeldict = {
            self._convertKeyword_WakeT(param): getattr(self, param)
            for param in self.simulation.required_attrs[self.simulation.wakefield_model]
        }
        if self.plasma.density_profile:
            modeldict["density"] = self._wake_t_density_profile
        else:
            modeldict["density"] = float(self.plasma.density)
        elemdict = modeldict | commondict
        lasers = []
        if isinstance(self.laser, LaserElement):
            laser_translator = LaserTranslator.model_validate(self.model_dump())
            lasers.append(laser_translator.to_wake_t())
        if len(lasers) == 1:
            elemdict.update({"laser": lasers[0]})
        elif len(lasers) == 2:
            elemdict.update({"laser": SummedPulse(lasers[0], lasers[1])})
        elif len(lasers) > 2:
            warn(
                "More than two laser sub-elements found; only the first two will be used."
            )
            elemdict.update({"laser": SummedPulse(lasers[0], lasers[1])})
        obj = type_conversion_rules_Wake_T[self.hardware_type](
            wakefield_model=self.simulation.wakefield_model, **elemdict
        )
        return obj

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
