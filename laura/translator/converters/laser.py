from inspect import signature
from typing import Any, List
from .base import BaseElementTranslator
from laura.models.laser import LaserElement
from warnings import warn


class LaserTranslator(BaseElementTranslator):
    """
    Translator class for converting a :class:`~laura.models.element.Laser` element instance into a string or
    object that can be understood by various simulation codes.
    """

    laser: LaserElement
    """Laser element class."""

    supported_pulses: List = [
        "gaussian",
        "laguerre-gaussian",
        "flattened-gaussian",
        # 'file'
    ]
    """Types of laser pulses that can be supported."""

    supported_pulses_fbpic: List = [
        "gaussian",
        "laguerre-gaussian",
        "laguerre-gaussian-donut",
        "flattened-gaussian",
    ]
    """Types of laser pulses that FBPIC can be given."""

    additional_attrs: List = [
        "focal_position",
        "wavelength",
        "cep_phase",
        "polarization",
    ]
    """Additional laser attributes."""

    fbpic_additional_attrs: List = [
        "focal_position",
        "wavelength",
        "cep_phase",
        "polarization_angle",
        "temporal_chirp_2nd_order",
        "propagation_direction",
    ]
    """Additional laser attributes offered to the FBPIC laser profiles."""

    def to_wake_t(self) -> Any:
        """
        Create a Wake-T laser element object based on the attributes of this element.

        Returns
        -------
        wake_t.LaserPulse
            Wake-T laser element object

        Raises
        ------
        ValueError
            If the laser model is not supported; note that not all models are implemented yet
        """
        from wake_t.physics_models.laser.laser_pulse import (
            GaussianPulse,
            LaguerreGaussPulse,
            FlattenedGaussianPulse,
            # SummedPulse,
            # OpenPMDPulse,
        )

        additional_dict = {
            self._convertKeyword_WakeT(param): getattr(self.laser, param)
            for param in self.additional_attrs
        }
        if self.profile_type == "gaussian":
            obj = GaussianPulse(
                self.laser.initial_position,
                self.laser.amplitude,
                self.laser.waist,
                self.laser.pulse_duration_fwhm,
                **additional_dict,
            )
        elif self.profile_type == "laguerre-gaussian":
            obj = LaguerreGaussPulse(
                self.laser.initial_position,
                self.laser.laguerre_polynomial_order_p,
                self.laser.amplitude,
                self.laser.waist,
                self.laser.pulse_duration_fwhm,
                **additional_dict,
            )
        elif self.profile_type == "flattened-gaussian":
            obj = FlattenedGaussianPulse(
                self.laser.initial_position,
                self.laser.amplitude,
                self.laser.waist,
                self.laser.pulse_duration_fwhm,
                N=self.laser.flatness,
                **additional_dict,
            )
        else:
            raise ValueError(
                f"Invalid laser profile type {self.laser.profile_type}. "
                f"Supported models are {self.supported_pulses}."
            )
        return obj

    def to_fbpic(self) -> Any:
        """
        Create an FBPIC laser element object based on the attributes of this element.

        Returns
        -------
        fbpic.lpa_utils.laser.laser_profiles.LaserProfile
            FBPIC laser element object

        Raises
        ------
        ValueError
            If the laser model is not supported; note that not all models are implemented yet
        """
        from fbpic.lpa_utils.laser.laser_profiles import (
            GaussianLaser,
            LaguerreGaussLaser,
            DonutLikeLaguerreGaussLaser,
            FlattenedGaussianLaser,
            FewCycleLaser,
        )
        a0 = self.laser.amplitude
        waist = self.laser.waist
        z0 = self.laser.initial_position
        tau = self.laser.pulse_duration_1e_field
        profile_type = str(self.laser.profile_type).lower()
        if profile_type == "gaussian":
            if self.laser._is_few_cycle:
                warn(f"The laser defined in element {self.name} is a few-cycle pulse. "
                     "Using the FewCycleLaser model.")
                cls, args = FewCycleLaser, (a0, waist, self.laser.pulse_duration_fwhm, z0)
            else:
                cls, args = GaussianLaser, (a0, waist, tau, z0)
            kwargs = {}
        elif profile_type in ("laguerre-gaussian", "laguerre-gaussian-donut"):
            cls = (
                LaguerreGaussLaser
                if profile_type == "laguerre-gaussian"
                else DonutLikeLaguerreGaussLaser
            )
            args = (
                self.laser.laguerre_polynomial_order_p,
                self.laser.laguerre_polynomial_order_m,
                a0,
                waist,
                tau,
                z0,
            )
            kwargs = {}
        elif profile_type == "flattened-gaussian":
            cls, args = FlattenedGaussianLaser, (a0, waist, tau, z0)
            kwargs = {"N": self.laser.flatness}
        else:
            raise ValueError(
                f"Invalid laser profile type {self.laser.profile_type} for FBPIC. "
                f"Supported models are {self.supported_pulses_fbpic}."
            )
        kwargs.update(self._fbpic_optional_kwargs(cls))
        return cls(*args, **kwargs)

    def _fbpic_optional_kwargs(self, cls: type) -> dict:
        """
        Optional keyword arguments for the FBPIC laser profile class *cls*.

        The profiles do not all take the same keywords, so
        :attr:`~fbpic_additional_attrs` is filtered against the
        constructor signature, raising warnings if there is a conflict.

        Parameters
        ----------
        cls : type
            The FBPIC laser profile class about to be constructed

        Returns
        -------
        dict
            Keyword arguments accepted by *cls*
        """
        accepted = signature(cls.__init__).parameters
        model_fields = type(self.laser).model_fields
        kwargs = {}
        for param in self.fbpic_additional_attrs:
            value = getattr(self.laser, param)
            if value is None:
                continue
            keyword = self._convertKeyword_FBPIC(param)
            if keyword in accepted:
                kwargs[keyword] = value
            elif param in model_fields and value != model_fields[param].default:
                warn(
                    f"{cls.__name__} does not accept {keyword}; the value "
                    f"{value} set for {param} on element {self.name} is ignored."
                )
        return kwargs
