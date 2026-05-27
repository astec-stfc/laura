import numpy as np
from .constants import speed_of_light, pi
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
from typing import ClassVar, Dict, Any, List, Union
from .baseModels import IgnoreExtra, T
from ._generated import _MultipoleBase, _FieldIntegralBase, _LinearSaturationFitBase, _MagneticElementBase


def Power(a, b):
    return a**b


def Sqrt(a):
    return Power(a, 0.5)


Pi = pi
Degree = pi / 180.0


class Multipole(_MultipoleBase):
    """
    Single order magnetic multipole model.
    """

    pass


multipoles = {
    "K" + str(no) + "L": (Multipole, Field(default=Multipole(order=no), repr=False))
    for no in range(0, 5)
}
MultipolesData = create_model("Multipoles", **multipoles)


class Multipoles(MultipolesData):
    """
    Magnetic multipoles model.
    """

    @field_validator("*", mode="before")
    def validate_Multipole(cls, v: Union[List, dict]) -> Multipole:
        if isinstance(v, (list, tuple)):
            if len(v) == 2:
                return Multipole(order=v[0], normal=v[1])
            elif len(v) == 4:
                return Multipole(order=v[0], normal=v[1], skew=v[2], radius=v[3])
        elif isinstance(v, dict):
            return Multipole(**v)
        elif isinstance(v, Multipole):
            return v
        else:
            raise ValueError("Multipole should be a dict or a list of floats")

    def __str__(self):
        return " ".join(
            [
                "K"
                + str(i)
                + "L=Multipole("
                + getattr(self, "K" + str(i) + "L").__str__()
                + ")"
                for i in range(0, 5)
                if abs(getattr(self, "K" + str(i) + "L").normal) > 0
                or abs(getattr(self, "K" + str(i) + "L").skew) > 0
            ]
        )

    def __repr__(self):
        return "Multipoles(" + self.__str__() + ")"

    @model_serializer
    def ser_model(self) -> Dict[str, Any]:
        cls = self.__class__
        return {
            k: getattr(self, k)
            for k in cls.model_fields.keys()
            # if abs(getattr(self, k).normal) > 0 or abs(getattr(self, k).skew) > 0
        }

    def normal(self, order: int) -> Union[int, float]:
        """
        Get the normal component of the multipole strength for a given order.

        Args:
            order (int): The order of the multipole (0=dipole, 1=quadrupole, etc.).

        Returns:
            Union[int, float]: The normal component of the multipole strength.
        """
        return getattr(self, "K" + str(order) + "L").normal

    def skew(self, order: int) -> Union[int, float]:
        """
        Get the skew component of the multipole strength for a given order.

        Args:
            order (int): The order of the multipole (0=dipole, 1=quadrupole, etc.).

        Returns:
            Union[int, float]: The skew component of the multipole strength.
        """
        return getattr(self, "K" + str(order) + "L").skew

    def __eq__(self, other) -> bool:
        return self.ser_model() == other

    def __neq__(self, other) -> bool:
        return not self.__eq__(other)


class FieldIntegral(_FieldIntegralBase):
    """
    Field integral coefficients model.
    """

    def currentToK(self, current: float, energy: float) -> float:
        """
        Convert the current in the magnet to the normalized strength (K value).
        The method calculates the normalized strength (K value) of the magnetic field
        based on the provided current and energy. It uses the field integral coefficients
        to compute the integrated field strength and applies a scaling factor based on
        the speed of light and the beam energy.

        Args:
            current (float): The current flowing through the magnet (in amperes).
            energy (float): The energy of the particle beam (in MeV).

        Returns:
            float: The normalized strength (K value) of the magnetic field.
        """
        sign = np.copysign(1, current)
        ficmod = [i * int(sign) for i in self.coefficients[:-1]]
        coeffs = np.append(ficmod, self.coefficients[-1])
        int_strength = np.polyval(coeffs, abs(current))
        effect = (speed_of_light / 1e6) * int_strength / energy
        return effect

    def __iter__(self) -> iter:
        return iter(self.coefficients)


class LinearSaturationFit(_LinearSaturationFitBase):
    """
    Linear + saturation fit coefficients model.
    """

    # Ordered list of calibration coefficient field names — used by
    # from_string / update_from_string so that the non-calibration `order`
    # field is never interpreted as a coefficient.
    _COEFF_KEYS: ClassVar[list] = ["m", "I_max", "f", "a", "I0", "d", "L"]

    # Magnet order (0 = dipole/corrector, 1 = quadrupole, …).
    # Set by MagneticElement after construction; excluded from serialisation.
    order: int = Field(default=1, exclude=True)

    @property
    def coefficients(self) -> List[Union[int, float]]:
        return [getattr(self, k) for k in self._COEFF_KEYS]

    @classmethod
    def from_string(cls, v: Union[str, List]) -> T:
        if isinstance(v, str):
            coeff_list = list(map(float, v.strip().split(",")))
            assert len(coeff_list) == len(cls._COEFF_KEYS)
            return cls(**{k: v for k, v in zip(cls._COEFF_KEYS, coeff_list)})
        elif isinstance(v, (list, tuple)):
            assert len(v) == len(cls.model_fields.keys())
            return cls(**{k: v for k, v in zip(cls.model_fields.keys(), v)})
        else:
            raise ValueError(
                "LinearSaturationFit should be a string or a list of floats"
            )

    def update_from_string(self, v: Union[str, List]) -> None:
        if isinstance(v, str):
            coeff_list = list(map(float, v.strip().split(",")))
            assert len(coeff_list) == len(self._COEFF_KEYS)
            [setattr(self, k, v) for k, v in zip(self._COEFF_KEYS, coeff_list)]
        elif isinstance(v, (list, tuple)):
            assert len(v) == len(self._COEFF_KEYS)
            [setattr(self, k, v) for k, v in zip(self._COEFF_KEYS, v)]

    def currentToK(self, current: float, momentum: float | None = None) -> Dict:
        """
        Convert the current in the magnet to the normalized strength (K value).

        The method calculates the normalized strength (K value) of the magnetic field
        based on the provided current and momentum. It uses the field integral coefficients
        to compute the integrated field strength and applies a scaling factor based on
        the speed of light and the beam momentum.

        Args:
            current (float): The current flowing through the magnet (in amperes).
            momentum (float): The momentum of the particle beam (in MeV/c).

        Returns:
            dict: A dictionary containing the K value, KL value, gradient, and integrated strength.
                The K value is the normalized strength of the magnetic field, KL is the K value multiplied by the
                length of the magnet, gradient is the magnetic field gradient, and integrated strength is the
                integrated field strength.
        """
        abs_I = abs(current)
        m, I_max, f, a, I0, d, L = list(self.coefficients)
        L = 1e-3 * L
        int_strength = (
            m * current
            if I_max == 0 or abs_I < I_max
            else np.copysign((f * abs_I**3 + a * (abs_I - I0) ** 2 + d), current)
        )
        gradient = int_strength / L if L != 0 else 0.0
        if momentum is not None:
            # order-0 (dipoles/correctors): m in mT·m/A → scale c/1e9
            # order-1+ (quadrupoles etc.): m in T/A      → scale c/1e6
            scale = 1e9 if self.order == 0 else 1e6
            KL = (speed_of_light / scale) * int_strength / momentum
            return {
                "K": KL / L if L != 0 else 0.0,
                "KL": KL,
                "gradient": gradient,
                "int_strength": int_strength,
            }
        else:
            return {"gradient": gradient, "int_strength": int_strength}

    def KLToCurrent(self, KL: float | dict, momentum: float) -> float:
        """
        Convert the normalized strength (K value) of the magnetic field to the corresponding current.

        This method calculates the current required to produce a given normalized strength (K value)
        of the magnetic field, based on the magnet's linear and saturation fit coefficients. It accounts
        for both linear and nonlinear (saturation) behavior of the magnet.

        Args:
            KL (float): The normalized strength (K value) of the magnetic field.
                OR
            dict: A dictionary containing the K value and its gradient.
            momentum (float): The momentum of the particle beam (in MeV/c).

        Returns:
            float: The current (in amperes) required to produce the given K value.
        """
        m, I_max, f, a, I0, d, L = list(self.coefficients)
        if isinstance(KL, dict):
            if "KL" in KL:
                KL = KL["KL"]
            elif "K" in KL:
                KL = KL["K"] * L / 1000
        K = KL / (L / 1000) if L != 0 else 0.0
        return self.KToCurrent(K, momentum)

    def KToCurrent(self, K: float | dict, momentum: float) -> float:
        """
        Convert the normalized strength (K value) of the magnetic field to the corresponding current.
        This method calculates the current required to produce a given normalized strength (K value)
        of the magnetic field, based on the magnet's linear and saturation fit coefficients. It accounts
        for both linear and nonlinear (saturation) behavior of the magnet.

        Args:
            K (float): The normalized strength (K value) of the magnetic field.
                OR
            dict: A dictionary containing the K value and its gradient.
            momentum (float): The momentum of the particle beam (in MeV/c).

        Returns:
            float: The current (in amperes) required to produce the given K value.
        """
        m, I_max, f, a, I0, d, L = list(self.coefficients)
        if isinstance(K, dict):
            if "K" in K:
                K = K["K"]
            elif "KL" in K:
                K = K["KL"] / (L / 1000) if L != 0 else 0.0
            else:
                raise ValueError(f"K value not found in the dictionary {K}")
        # Inverse of currentToK scale: order-0 uses 1e9, order-1+ uses 1e6
        scale = 1e9 if self.order == 0 else 1e6
        int_strength = scale * K * L * momentum / (speed_of_light)
        int_strength *= 1e-3  # L is in mm, convert K·L_m back to int_strength units
        abs_str = abs(int_strength)
        linear_current = int_strength / m
        if I_max == 0 or abs(linear_current) < I_max:
            return linear_current
        elif f == 0:
            abs_current = I0 - Sqrt((abs_str - d) / a)
            return np.sign(K) * abs_current
        else:
            p = (-6 * f * a * I0 - a**2) / (3 * f**2)
            q = (
                (2 * a**3)
                + (18 * f * a**2 * I0)
                + (27 * f**2 * (a * I0**2 + d - abs_str))
            ) / (27 * f**3)
            r = Sqrt((p / 3) ** 3)
            theta = np.arccos(-q / (2 * r))
            r_cbrt = -(r ** (1 / 3))
            t3 = 2 * r_cbrt * np.cos((theta / 3) + 4 * Pi / 3)
            return t3 - a / (3 * f)

    def __iter__(self) -> iter:
        return iter(
            [getattr(self, k) for k in self._COEFF_KEYS]
        )


class MagneticElement(_MagneticElementBase):
    """
    Magnetic info model.
    """

    multipoles: Multipoles | None = Multipoles()
    """Magnetic multipoles."""

    systematic_multipoles: Multipoles | None = Multipoles()
    """Systematic magnetic multipoles."""

    random_multipoles: Multipoles | None = Multipoles()
    """Random magnetic multipoles."""

    def __init__(self, /, **data: Any) -> None:
        super().__init__(**data)
        # Propagate the magnet order into the calibration fit so that
        # currentToK / KToCurrent can apply the correct unit convention.
        if self.linear_saturation_coefficients is not None:
            self.linear_saturation_coefficients.order = self.order
        # Auto-create multipoles if strength data is provided but multipoles is None
        needs_multipoles = any(
            k in data for k in ["kl", "angle", "k0l", "k1l", "k2l", "k3l"]
        )
        if self.multipoles is None and needs_multipoles:
            object.__setattr__(self, "multipoles", Multipoles())
        if "kl" in data:
            self.kl = data["kl"]
        if "angle" in data and self.order == 0:
            self.kl = data["angle"]
        if self.multipoles is not None:
            if "kl" in data or "angle" in data:
                if self.skew:
                    setattr(
                        self.multipoles,
                        "K" + str(self.order) + "L",
                        Multipole(skew=self.kl, order=self.order),
                    )
                else:
                    setattr(
                        self.multipoles,
                        "K" + str(self.order) + "L",
                        Multipole(normal=self.kl, order=self.order),
                    )
            for i in range(0, 5):
                if f"k{i}l" in data:
                    setattr(
                        self.multipoles,
                        f"K{i}L",
                        Multipole(normal=data[f"k{i}l"], order=i),
                    )

    @field_validator("field_integral_coefficients", mode="before")
    @classmethod
    def validate_field_integral_coefficients(
            cls, v: Union[str, List, dict | None]
    ) -> FieldIntegral | None:
        if isinstance(v, str):
            return FieldIntegral(coefficients=list(map(float, v.split(","))))
        elif isinstance(v, (list, tuple)):
            return FieldIntegral(coefficients=list(v))
        elif isinstance(v, dict):
            return FieldIntegral(**v)
        elif isinstance(v, FieldIntegral):
            return v
        elif v is None:
            return None
        else:
            raise ValueError(
                "field_integral_coefficients should be a string or a list of floats"
            )

    # @debug
    def KnL(self, order: int = None) -> Union[int, float]:
        """
        Get the integrated strength (KnL) of the multipole for a given order.

        Args:
            order (int, optional): The order of the multipole. Defaults to None, which uses self.order.

        Returns:
            Union[int, float]: The integrated strength (KnL) of the multipole.
        """
        if self.multipoles is None:
            return 0
        f = self.multipoles.skew if self.skew else self.multipoles.normal
        order = self.order if order is None else order
        return f(order) if order >= 0 else 0

    def Kn(self, order: int = None) -> Union[int, float]:
        """
        Get the normalized strength (Kn) of the multipole for a given order.

        Args:
            order (int, optional): The order of the multipole. Defaults to None, which uses self.order.

        Returns:
            Union[int, float]: The normalized strength (Kn) of the multipole.
        """
        return self.knl(order) / self.length

    @property
    def kl(self) -> Union[int, float]:
        return self.KnL(self.order)

    @kl.setter
    def kl(self, kl: float = 0) -> None:
        if self.multipoles is None:
            object.__setattr__(self, "multipoles", Multipoles())
        setattr(getattr(self.multipoles, "K" + str(self.order) + "L"), "normal", kl)
        setattr(
            getattr(self.multipoles, "K" + str(self.order) + "L"), "order", self.order
        )

    @computed_field
    @property
    def half_gap(self) -> float:
        return self.gap / 2

    def get_gradient(self, momentum: float) -> float:
        """
        Get the magnetic field gradient for the multipole.

        Args:
            momentum (float): The momentum of the particle beam (in MeV/c).

        Returns:
            float: The magnetic field gradient.
        """
        if self.gradient is not None:
            return self.gradient
        Brho = 3.3356 * momentum / (1e9)
        return self.kl * Brho / self.length

    def currentToK(self, *args, **kwargs):
        return self.linear_saturation_coefficients.currentToK(*args, **kwargs)

    def KToCurrent(self, *args, **kwargs):
        return self.linear_saturation_coefficients.KToCurrent(*args, **kwargs)

    def KLToCurrent(self, *args, **kwargs):
        return self.linear_saturation_coefficients.KLToCurrent(*args, **kwargs)


class Dipole_Magnet(MagneticElement):
    """
    Dipole magnet with magnetic order 0.
    """

    order: int = Field(repr=False, default=0, frozen=True)
    """Magnetic order of the dipole."""

    @property
    def angle(self) -> float:
        return self.KnL(order=0)

    @angle.setter
    def angle(self, value: float) -> None:
        if self.multipoles is None:
            object.__setattr__(self, "multipoles", Multipoles())
        self.multipoles.K0L.normal = value

    def currentToAngle(self, current: float, momentum: float) -> float:
        """Convert current to bend angle in degrees."""
        output_dict = self.linear_saturation_coefficients.currentToK(
            current=current, momentum=momentum
        )
        return output_dict["KL"] * 360 / (2.0 * np.pi) / 1000

    def currentToK(self, *args, **kwargs):
        output_dict = {
            k: v / 1000
            for k, v in self.linear_saturation_coefficients.currentToK(
                *args, **kwargs
            ).items()
        }
        output_dict.update({"degrees": output_dict["KL"] * 360 / (2.0 * np.pi)})
        return output_dict

    def KToCurrent(self, K, momentum):
        """Reverse the /1000 scaling applied by currentToK."""
        if isinstance(K, dict):
            K = {k: v * 1000 for k, v in K.items() if isinstance(v, (int, float))}
        else:
            K = K * 1000
        return self.linear_saturation_coefficients.KToCurrent(K, momentum)

    def KLToCurrent(self, KL, momentum):
        """Reverse the /1000 scaling applied by currentToK."""
        if isinstance(KL, dict):
            KL = {k: v * 1000 for k, v in KL.items() if isinstance(v, (int, float))}
        else:
            KL = KL * 1000
        return self.linear_saturation_coefficients.KLToCurrent(KL, momentum)

    @computed_field
    @property
    def rho(self) -> float:
        """
        Get the dipole bend radius -- l / theta.

        Returns
            float: The dipole bend radius
        """
        return (
            self.length / self.angle
            if self.length is not None and abs(self.angle) > 1e-9
            else 0
        )

    def field_strength(self, momentum: float) -> float:
        """
        Get the dipole magnetic field strength.

        Args:
            momentum (float): The momentum of the particle beam (in eV/c).

        Returns:
            float: The dipole magnetic field strength.
        """
        Brho = 3.3356 * momentum / (1e9)
        return self.rho * Brho / self.length


class Quadrupole_Magnet(MagneticElement):
    """
    Quadrupole with magnetic order 1.
    """

    order: int = Field(repr=False, default=1, frozen=True)
    """Magnetic order of the quadrupole."""

    @property
    def k1l(self) -> float:
        return self.kl

    @k1l.setter
    def k1l(self, value: float) -> None:
        self.kl = value


class Sextupole_Magnet(MagneticElement):
    """
    Sextupole magnet with magnetic order 2.
    """

    order: int = Field(repr=False, default=2, frozen=True)
    """Magnetic order of the sextupole."""

    @property
    def k2l(self) -> float:
        return self.kl

    @k2l.setter
    def k2l(self, value: float) -> None:
        self.kl = value


class Octupole_Magnet(MagneticElement):
    """
    Octupole magnet with magnetic order 3.
    """

    order: int = Field(repr=False, default=3, frozen=True)
    """Magnetic order of the octupole."""

    @property
    def k3l(self) -> float:
        return self.kl

    @k3l.setter
    def k3l(self, value: float) -> None:
        self.kl = value


solenoidFields = {
    "S" + str(no) + "L": (float, Field(default=0, repr=False)) for no in range(0, 13)
}
solenoidFieldsData = create_model("solenoidFieldsData", **solenoidFields)


class SolenoidFields(solenoidFieldsData):
    """Magnetic multipoles model."""

    # def __str__(self):
    #     return " ".join(
    #         [
    #             "S" + str(i) + "L=" + getattr(self, "S" + str(i) + "L").__str__() + ""
    #             for i in range(13)
    #             if abs(getattr(self, "S" + str(i) + "L")) > 0
    #         ]
    #     )

    def __repr__(self):
        return "SolenoidFields(" + self.__str__() + ")"

    @model_serializer
    def ser_model(self) -> Dict[str, Any]:
        cls = self.__class__
        return {
            k: getattr(self, k)
            for k in cls.model_fields.keys()
            # if abs(getattr(self, k)) > 0
        }

    def normal(self, order: int) -> Union[int, float]:
        return getattr(self, "S" + str(order) + "L")

    def __eq__(self, other: Any) -> bool:
        return self.ser_model() == other

    def __neq__(self, other: Any) -> bool:
        return not self.__eq__(other)


class Solenoid_Magnet(IgnoreExtra):
    """
    Solenoid magnet including higher order fields.
    """

    length: NonNegativeFloat = Field(default=0.0, alias="magnetic_length")
    """Magnetic length [m]."""

    order: int = Field(repr=False, default=0, frozen=True)
    """Solenoid multipole order."""

    fields: SolenoidFields = SolenoidFields()
    """Solenoid fields."""

    systematic_fields: SolenoidFields = SolenoidFields()
    """Systematic solenoid fields."""

    random_fields: SolenoidFields = SolenoidFields()
    """Random solenoid fields."""

    field_integral_coefficients: FieldIntegral = FieldIntegral()
    """Field integral coefficients."""

    linear_saturation_coefficients: LinearSaturationFit = LinearSaturationFit()
    """Linear saturation coefficients."""

    settle_time: float = Field(alias="mag_set_max_wait_time", default=45.0)
    """Time for solenoid to settle.
    #TODO move to electrical?
    """

    def __init__(self, /, **data: Any) -> None:
        super().__init__(**data)
        if "ks" in data:
            self.ks = data["ks"]
        elif "field_amplitude" in data:
            self.ks = data["field_amplitude"] / self.length
        # else:
        #     self.ks = 0
        # setattr(self.fields, 'S'+str(self.order)+'L', self.ks)

    @field_validator("field_integral_coefficients", mode="before")
    @classmethod
    def validate_field_integral_coefficients(cls, v: Union[str, List]) -> FieldIntegral:
        if isinstance(v, str):
            return FieldIntegral(coefficients=list(map(float, v.split(","))))
        elif isinstance(v, (list, tuple)):
            return FieldIntegral(coefficients=list(v))
        elif isinstance(v, dict):
            return FieldIntegral(**v)
        elif isinstance(v, FieldIntegral):
            return v
        else:
            raise ValueError(
                "field_integral_coefficients should be a string or a list of floats"
            )

    @property
    def field_amplitude(self) -> Union[int, float]:
        return self.ks / self.length

    @field_amplitude.setter
    def field_amplitude(self, fa: float = 0) -> None:
        self.ks = fa * self.length

    @property
    def ks(self) -> Union[int, float]:
        return getattr(self.fields, "S" + str(self.order) + "L")

    @ks.setter
    def ks(self, ks: float = 0) -> None:
        setattr(self.fields, "S" + str(self.order) + "L", ks)


class NonLinearLens_Magnet(IgnoreExtra):
    """
    Non-linear lens magnet. See `MAD-X manual`_ and `PAC2011 article`_

    .. _MAD-X manual: https://cern.ch/madx
    .. _PAC2011 article: https://proceedings.jacow.org/PAC2011/papers/wep070.pdf
    """

    length: NonNegativeFloat = Field(default=0.0, alias="magnetic_length")
    """Magnetic length of NLL [m]."""

    integrated_strength: NonNegativeFloat = Field(default=0.0, alias="knll")
    """Integrated strength of NLL."""

    dimensional_parameter: float = Field(default=0.0, alias="cnll")
    """Dimensional parameter of NLL."""

    def __init__(self, /, **data: Any) -> None:
        super().__init__(**data)


class Wiggler_Magnet(IgnoreExtra):
    """
    Undulator magnet.
    """

    length: NonNegativeFloat = Field(default=0.0, alias="magnetic_length")
    """Magnetic length of wiggler [m].
    #TODO validate / check that length == period*num_periods.
    """

    strength: NonNegativeFloat = Field(default=0.0, alias="K")
    """Wiggler strength (K) parameter."""

    peak_magnetic_field: float = Field(default=0.0, alias="B")
    """Peak wiggler magnetic field [B]."""

    period: NonNegativeFloat = Field(default=0.0, alias="lambdau")
    """Wiggler period [m]."""

    num_periods: NonNegativeInt = Field(default=0, alias="nwig")
    """Number of periods in the wiggler [m]."""

    helical: bool = False
    """Flag to indicate if the wiggler is helical; False implies planar."""

    quadratic_roll_off_x: float = Field(default=0.0, alias="kx")
    """Horizontal quadratic roll-off parameter."""

    quadratic_roll_off_y: float = Field(default=0.0, alias="ky")
    """Vertical quadratic roll-off parameter."""

    transverse_gradient_x: float = Field(default=0.0, alias="gradx")
    """Horizontal transverse gradient."""

    transverse_gradient_y: float = Field(default=0.0, alias="grady")
    """Vertical transverse gradient."""

    def __init__(self, /, **data: Any) -> None:
        super().__init__(**data)
        # setattr(self.fields, 'S'+str(self.order)+'L', self.ks)

    @property
    def normalized_strength(self) -> float:
        """
        Getter for the normalised undulator strength :math:`a_w`

        Returns
        -------
        float:
            :attr:`~strength` / :math:`\\sqrt{2}`
        """

        if not self.helical:
            return self.strength / np.sqrt(2)
        else:
            return self.strength

    @normalized_strength.setter
    def normalized_strength(self, aw: float) -> None:
        """
        Setter for the normalised undulator strength :math:`a_w`

        Parameters
        ----------
        aw: float
            :attr:`~strength` = :math:`a_w \\times \\sqrt{2}`
        """
        if not self.helical:
            self.strength = aw * np.sqrt(2)
        else:
            self.strength = aw

    @property
    def poles(self) -> int:
        """
        Number of poles, twice :attr:`~num_periods`.

        Returns
        -------
        int
            Number of poles
        """
        return int(self.num_periods * 2)

    @poles.setter
    def poles(self, value: int) -> None:
        self.num_periods = int(value / 2)
