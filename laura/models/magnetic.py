from typing import Any, ClassVar, Dict, List, Union

import numpy as np
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    NonNegativeFloat,
    NonNegativeInt,
    computed_field,
    create_model,
    field_validator,
    model_serializer,
    model_validator,
)
from laura._compat import DeprecatedMethodAliases
from ._generated import (
    _CombinedCorrectorMagnetBase,
    _CombinedSolenoidQuadrupoleMagnetBase,
    _CorrectorMagnetBase,
    _FieldIntegralBase,
    _LinearSaturationFitBase,
    _MagneticElementBase,
    _MultipoleBase,
    _NonLinearLensMagnetBase,
    _SolenoidFieldsBase,
    _SolenoidMagnetBase,
    _WigglerMagnetBase,
)
from .base_models import FunctionalMixin, IgnoreExtra, T, resolve_functional_parameter
from .constants import pi, speed_of_light


def power(a, b):
    return a**b


def sqrt(a):
    return power(a, 0.5)


def _coerce_field_integral(v: Union[str, List, dict, Any, None]) -> Any:
    if isinstance(v, str):
        return FieldIntegral(coefficients=list(map(float, v.split(","))))
    if isinstance(v, (list, tuple)):
        return FieldIntegral(coefficients=list(v))
    if isinstance(v, dict):
        return FieldIntegral(**v)
    if isinstance(v, FieldIntegral):
        return v
    if v is None:
        return None
    raise ValueError(
        "field_integral_coefficients should be a string or a list of floats"
    )


Pi = pi
Degree = pi / 180.0


def _is_set(value: Any) -> bool:
    """True if a (possibly functional) strength value is non-trivial: any string
    functional definition counts as set; numbers count if non-zero."""
    if isinstance(value, str):
        return True
    return abs(value) > 0


def brho(momentum: float) -> float:
    """Magnetic rigidity ``B*rho`` [T.m] for a beam momentum in **eV/c**.

    Anything converting between a stored strength and a real field goes
    through here.
    """
    return 3.3356 * momentum / 1e9


class Multipole(_MultipoleBase, FunctionalMixin):
    """
    Single order magnetic multipole model.

    ``normal``/``skew`` accept the name of a functional definition as well as a
    number; that widening and the ``functional`` marker both come from the
    schema slot, so nothing needs restating here.
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
    def validate_multipole(cls, v: Union[List, dict]) -> Multipole:
        if v is None:
            return Multipole()
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
                if _is_set(getattr(self, "K" + str(i) + "L").normal)
                or _is_set(getattr(self, "K" + str(i) + "L").skew)
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
            Union[int, float, str]: The normal component of the multipole strength,
            as stored (a number, or the name of a functional definition).
        """
        return getattr(self, "K" + str(order) + "L").normal

    def skew(self, order: int) -> Union[int, float]:
        """
        Get the skew component of the multipole strength for a given order.

        Args:
            order (int): The order of the multipole (0=dipole, 1=quadrupole, etc.).

        Returns:
            Union[int, float, str]: The skew component of the multipole strength,
            as stored (a number, or the name of a functional definition).
        """
        return getattr(self, "K" + str(order) + "L").skew

    def __eq__(self, other) -> bool:
        return self.ser_model() == other


class FieldIntegral(DeprecatedMethodAliases, _FieldIntegralBase):
    """
    Field integral coefficients model.
    """

    _DEPRECATED_METHOD_ALIASES = {
        "currentToK": "current_to_k",
    }

    def current_to_k(self, current: float, energy: float) -> float:
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


class LinearSaturationFit(DeprecatedMethodAliases, _LinearSaturationFitBase):
    """
    Linear + saturation fit coefficients model.
    """

    _DEPRECATED_METHOD_ALIASES = {
        "KLToCurrent": "kl_to_current",
        "KToCurrent": "k_to_current",
        "currentToK": "current_to_k",
    }

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

    def current_to_k(self, current: float, momentum: float | None = None) -> Dict:
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
        abs_i = abs(current)
        m, i_max, f, a, i0, d, l = list(self.coefficients)
        l = 1e-3 * l
        int_strength = (
            m * current
            if i_max == 0 or abs_i < i_max
            else np.copysign((f * abs_i**3 + a * (abs_i - i0) ** 2 + d), current)
        )
        gradient = int_strength / l if l != 0 else 0.0
        if momentum is not None:
            # order-0 (dipoles/correctors): m in mT·m/A → scale c/1e9
            # order-1+ (quadrupoles etc.): m in T/A      → scale c/1e6
            scale = 1e9 if self.order == 0 else 1e6
            kl = (speed_of_light / scale) * int_strength / momentum
            return {
                "K": kl / l if l != 0 else 0.0,
                "KL": kl,
                "gradient": gradient,
                "int_strength": int_strength,
            }
        else:
            return {"gradient": gradient, "int_strength": int_strength}

    def kl_to_current(self, KL: float | dict, momentum: float) -> float: # noqa N806
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
        m, i_max, f, a, i0, d, l = list(self.coefficients)
        if isinstance(KL, dict):
            if "KL" in KL:
                KL = KL["KL"] # noqa N806
            elif "K" in KL:
                KL = KL["K"] * l / 1000  # noqa N806
        k = KL / (l / 1000) if l != 0 else 0.0
        return self.k_to_current(k, momentum)

    def k_to_current(self, K: float | dict, momentum: float) -> float: # noqa N806
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
        m, i_max, f, a, i0, d, l = list(self.coefficients)
        if isinstance(K, dict):
            if "K" in K:
                K = K["K"]  # noqa N806
            elif "KL" in K:
                K = K["KL"] / (l / 1000) if l != 0 else 0.0  # noqa N806
            else:
                raise ValueError(f"K value not found in the dictionary {K}")
        # Inverse of currentToK scale: order-0 uses 1e9, order-1+ uses 1e6
        scale = 1e9 if self.order == 0 else 1e6
        int_strength = scale * K * l * momentum / speed_of_light
        int_strength *= 1e-3  # L is in mm, convert K·L_m back to int_strength units
        abs_str = abs(int_strength)
        linear_current = int_strength / m
        if i_max == 0 or abs(linear_current) < i_max:
            return linear_current
        elif f == 0:
            abs_current = i0 - sqrt((abs_str - d) / a)
            return np.sign(K) * abs_current
        else:
            p = (-6 * f * a * i0 - a**2) / (3 * f**2)
            q = (
                (2 * a**3)
                + (18 * f * a**2 * i0)
                + (27 * f**2 * (a * i0**2 + d - abs_str))
            ) / (27 * f**3)
            r = sqrt((p / 3) ** 3)
            theta = np.arccos(-q / (2 * r))
            r_cbrt = -(r ** (1 / 3))
            t3 = 2 * r_cbrt * np.cos((theta / 3) + 4 * Pi / 3)
            return t3 - a / (3 * f)

    def __iter__(self) -> iter:
        return iter([getattr(self, k) for k in self._COEFF_KEYS])


class MagneticElement(DeprecatedMethodAliases, _MagneticElementBase, FunctionalMixin):
    """
    Magnetic info model.
    """

    _DEPRECATED_METHOD_ALIASES = {
        "KLToCurrent": "kl_to_current",
        "KToCurrent": "k_to_current",
        "currentToAngle": "current_to_angle",
        "currentToK": "current_to_k",
    }

    entrance_edge_angle: float | str | None = 0.0
    """Entrance edge angle"""

    exit_edge_angle: float | str | None = 0.0
    """Exit edge angle"""

    multipoles: Multipoles | None = Multipoles()
    """Magnetic multipoles."""

    systematic_multipoles: Multipoles | None = Multipoles()
    """Systematic magnetic multipoles."""

    random_multipoles: Multipoles | None = Multipoles()
    """Random magnetic multipoles."""

    linear_saturation_coefficients: LinearSaturationFit | None = None
    """Linear saturation fit coefficients (typed to allow order assignment)."""

    entrance_edge_angle: float | str = Field(
        default=0.0,
        json_schema_extra={"functional": True, "reserved_contains": "angle"},
    )
    """Entrance edge angle in degrees. May be a number, an expression referencing
    the bend angle (any string containing the reserved token ``angle``, e.g.
    ``"angle"`` or ``"angle/2"``), or the name of a functional definition (see
    :ref:`functional-parameters`)."""

    exit_edge_angle: float | str = Field(
        default=0.0,
        json_schema_extra={"functional": True, "reserved_contains": "angle"},
    )
    """Exit edge angle in degrees. May be a number, an expression referencing the
    bend angle (any string containing the reserved token ``angle``, e.g.
    ``"angle"`` or ``"angle/2"``), or the name of a functional definition (see
    :ref:`functional-parameters`)."""

    def __init__(self, /, **data: Any) -> None:
        super().__init__(**data)
        if self.linear_saturation_coefficients is not None:
            self.linear_saturation_coefficients.order = self.order
        needs_multipoles = any(
            k in data for k in ["kl", "angle", "k0l", "k1l", "k2l", "k3l"]
        )
        if self.multipoles is None and needs_multipoles:
            object.__setattr__(self, "multipoles", Multipoles())
        if data.get("kl") is not None:
            self.kl = data["kl"]
        if data.get("angle") is not None and self.order == 0:
            self.kl = data["angle"]
        if self.multipoles is not None:
            if data.get("kl") is not None or data.get("angle") is not None:
                raw_kl = data["kl"] if data.get("kl") is not None else data["angle"]
                if self.skew:
                    setattr(
                        self.multipoles,
                        "K" + str(self.order) + "L",
                        Multipole(skew=raw_kl, order=self.order),
                    )
                else:
                    setattr(
                        self.multipoles,
                        "K" + str(self.order) + "L",
                        Multipole(normal=raw_kl, order=self.order),
                    )
            for i in range(0, 5):
                if data.get(f"k{i}l") is not None:
                    setattr(
                        self.multipoles,
                        f"K{i}L",
                        Multipole(normal=data[f"k{i}l"], order=i),
                    )
        if self.order == 0:
            pass  # angle is derived from K0L; nothing to mirror.

    @field_validator("plane", mode="before")
    @classmethod
    def validate_plane(cls, v) -> str:
        if isinstance(v, str):
            return v.capitalize()
        return v

    @model_validator(mode="after")
    def resolve_edge_field_integrals(self) -> "MagneticElement":  # noqa: N804
        """
        Reconciles ``edge_field_integral`` (the single combined value read by
        codes that only expose one edge-focussing keyword, e.g. ELEGANT/OPAL's
        ``fint``) against ``edge_field_integral_entrance``/``_exit`` (read by
        codes with separate entrance/exit keywords, e.g. MAD-X's ``fint``/
        ``fintx``). All three are ``None`` unless given -- an unset value is
        simply omitted from the written output (every ``to_*`` writer skips
        ``None``), so the target code's own built-in default applies rather
        than laura silently forcing a number in.

        * edge_field_integral_entrance/_exit, when explicitly given, are
          always used as given -- edge_field_integral never overrides them.
        * edge_field_integral, when given, becomes the *default* for whichever
          of entrance/exit was not itself given.
        * edge_field_integral itself is never inferred from entrance/exit --
          if only entrance and/or exit are given, edge_field_integral stays
          None (so single-value codes get nothing written for this magnet).

        Uses ``object.__setattr__`` rather than plain attribute assignment:
        this model has ``validate_assignment = True``, so a normal
        ``self.x = y`` here would re-run this very validator re-entrantly.
        """
        if self.edge_field_integral is not None:
            if self.edge_field_integral_entrance is None:
                object.__setattr__(self, "edge_field_integral_entrance", self.edge_field_integral)
            if self.edge_field_integral_exit is None:
                object.__setattr__(self, "edge_field_integral_exit", self.edge_field_integral)
        return self

    @field_validator("field_integral_coefficients", mode="before")
    @classmethod
    def validate_field_integral_coefficients(
        cls, v: Union[str, List, dict | None]
    ) -> FieldIntegral | None:
        return _coerce_field_integral(v)

    # @debug
    def KnL(self, order: int = None) -> Union[int, float]:
        """
        Get the integrated strength (KnL) of the multipole for a given order,
        resolved to a number. This is the value to use for computation; a
        functional definition (stored as a string on the multipole) is resolved
        here, while the raw configured value remains available via
        :attr:`kl` / :meth:`Multipoles.normal`.

        Args:
            order (int, optional): The order of the multipole. Defaults to None, which uses self.order.

        Returns:
            Union[int, float]: The integrated strength (KnL) of the multipole.
        """
        return resolve_functional_parameter(self.kl_raw(order), force=True)

    def kl_raw(self, order: int = None) -> Union[int, float, str]:
        """
        Get the integrated strength as stored — a number, or the name of a
        functional definition — without resolving it.
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
        return self.KnL(order) / self.length

    @property
    def kl(self) -> Union[int, float, str]:
        """Integrated strength as configured. By default (global resolution mode
        off) this is the value as stored — a number, or the name of a functional
        definition; with resolution mode on it is the resolved number. Use
        :meth:`KnL` for the resolved number regardless of mode."""
        return resolve_functional_parameter(self.kl_raw(self.order))

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

    @property
    def exit_half_gap(self) -> float:
        """Half gap at the exit face. Falls back to :attr:`half_gap`."""
        if self.exit_gap is None:
            return self.half_gap
        return self.exit_gap / 2

    @property
    def exit_fringe_integral(self) -> float | None:
        """Fringe-field integral at the exit face.
        Falls back to :attr:`edge_field_integral`."""
        if self.edge_field_integral_exit is None:
            return self.edge_field_integral
        return self.edge_field_integral_exit

    def get_gradient(self, momentum: float) -> float:
        """
        Get the magnetic field gradient for the multipole.

        Args:
            momentum (float): The momentum of the particle beam (in eV/c).

        Returns:
            float: The magnetic field gradient.
        """
        if self.gradient is not None:
            return self.gradient
        return self.KnL(self.order) * brho(momentum) / self.length

    def current_to_k(self, *args, **kwargs):
        return self.linear_saturation_coefficients.current_to_k(*args, **kwargs)

    def k_to_current(self, *args, **kwargs):
        return self.linear_saturation_coefficients.k_to_current(*args, **kwargs)

    def kl_to_current(self, *args, **kwargs):
        return self.linear_saturation_coefficients.kl_to_current(*args, **kwargs)

    def current_to_angle(self, current: float, momentum: float) -> float:
        """Convert current to bend angle in degrees."""
        output_dict = self.linear_saturation_coefficients.current_to_k(
            current=current, momentum=momentum
        )
        return output_dict["KL"] * 360 / (2.0 * np.pi)


class DipoleMagnet(MagneticElement):
    """
    Dipole magnet with magnetic order 0.
    """

    order: int = Field(repr=False, default=0)
    """Magnetic order of the dipole."""

    # `angle` is deliberately not a schema slot (see magnetic.yaml): it is
    # derived from multipoles.K0L here, so a symbolic bend angle survives
    # round-tripping and reads follow the global resolution mode.
    @property
    def angle(self) -> Union[int, float, str]:
        """Bend angle as configured. By default (global resolution mode off) this
        is the value as stored -- a number, or the name of a functional
        definition; with resolution mode on it is the resolved number. Use
        ``KnL(0)`` for the resolved number regardless of mode."""
        return resolve_functional_parameter(self.kl_raw(0))

    @angle.setter
    def angle(self, value: float) -> None:
        if self.multipoles is None:
            object.__setattr__(self, "multipoles", Multipoles())
        self.multipoles.K0L.normal = value

    def current_to_angle(self, current: float, momentum: float) -> float:
        """
        Convert current to bend angle in degrees.

        Args:
            current (float): Magnet current [A].
            momentum (float): Beam momentum [MeV/c].

        Returns:
            float: The bend angle [degrees].
        """
        return self.current_to_k(current=current, momentum=momentum)["degrees"]

    def current_to_k(self, *args, **kwargs):
        """
        Current -> K/KL, plus the bend angle in degrees.

        ``LinearSaturationFit.current_to_k`` already applies an order-aware
        ``c/1e9`` for order 0, which makes ``KL`` the bend angle in **radians**.
        """
        output_dict = dict(
            self.linear_saturation_coefficients.current_to_k(*args, **kwargs)
        )
        if "KL" in output_dict:
            output_dict["degrees"] = output_dict["KL"] * 360 / (2.0 * np.pi)
        return output_dict

    # No k_to_current/kl_to_current override: current_to_k above no longer
    # divides by 1000, so there is nothing to undo and MagneticElement's
    # inverses round-trip exactly.

    @computed_field
    @property
    def rho(self) -> float:
        """
        Get the dipole bend radius -- l / theta.

        Returns
            float: The dipole bend radius
        """

        try:
            angle = self.KnL(0)
        except KeyError:
            return 0
        return (
            self.length / angle if self.length is not None and abs(angle) > 1e-9 else 0
        )

    def field_strength(self, momentum: float) -> float:
        """
        Get the dipole magnetic field strength, ``B = Brho / rho`` [T].

        This is the dipole's counterpart to
        :meth:`MagneticElement.get_gradient`, and reads the same way: with
        ``rho = length / angle`` and ``K0L = angle``, ``Brho / rho`` is
        ``K0L * Brho / length`` -- one relation, whatever the order.

        Args:
            momentum (float): The momentum of the particle beam (in eV/c).

        Returns:
            float: The dipole magnetic field strength.
        """
        if self.gradient is not None:
            return self.gradient
        return brho(momentum) / self.rho if self.rho else 0.0


class QuadrupoleMagnet(MagneticElement):
    """
    Quadrupole with magnetic order 1.
    """

    order: int = Field(repr=False, default=1)
    """Magnetic order of the quadrupole."""

    @property
    def k1l(self) -> float:
        return self.kl

    @k1l.setter
    def k1l(self, value: float) -> None:
        self.kl = value


class SextupoleMagnet(MagneticElement):
    """
    Sextupole magnet with magnetic order 2.
    """

    order: int = Field(repr=False, default=2)
    """Magnetic order of the sextupole."""

    @property
    def k2l(self) -> float:
        return self.kl

    @k2l.setter
    def k2l(self, value: float) -> None:
        self.kl = value


class OctupoleMagnet(MagneticElement):
    """
    Octupole magnet with magnetic order 3.
    """

    order: int = Field(repr=False, default=3)
    """Magnetic order of the octupole."""

    @property
    def k3l(self) -> float:
        return self.kl

    @k3l.setter
    def k3l(self, value: float) -> None:
        self.kl = value


solenoid_fields = {
    "S" + str(no) + "L": (
        Union[float, str],
        Field(default=0, repr=False, json_schema_extra={"functional": True}),
    )
    for no in range(0, 13)
}
solenoid_fields_data = create_model("solenoidFieldsData", **solenoid_fields)


class SolenoidFields(solenoid_fields_data, _SolenoidFieldsBase):
    """Magnetic multipoles model."""

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

    def normal(self, order: int) -> Union[int, float, str]:
        """The solenoid field of a given order as stored (a number, or the name
        of a functional definition); resolved on demand via
        :attr:`Solenoid_Magnet.field_amplitude`."""
        return getattr(self, "S" + str(order) + "L")

    def __eq__(self, other: Any) -> bool:
        return self.ser_model() == other


class CombinedSolenoidQuadrupoleMagnet(
    MagneticElement, _CombinedSolenoidQuadrupoleMagnetBase
):
    """Coaxial quadrupole and solenoid field components."""

    order: int = Field(repr=False, default=1, frozen=True)
    """Sol-quad multipole order."""

    solenoid_fields: SolenoidFields = Field(default_factory=SolenoidFields)
    """Solenoid fields."""

    def __init__(self, /, **data: Any) -> None:
        super().__init__(**data)
        if "ks" in data:
            self.ks = data["ks"]

    @property
    def ks(self) -> Union[int, float, str]:
        return self.solenoid_fields.S0L

    @ks.setter
    def ks(self, value: Union[int, float, str]) -> None:
        self.solenoid_fields.S0L = value


class SolenoidMagnet(_SolenoidMagnetBase, IgnoreExtra):
    """
    Solenoid magnet including higher order fields.
    """

    # _SolenoidMagnetBase pulls in ConfiguredBaseModel's serialize_by_alias=True.
    # Fields below use `alias=` (bidirectional) rather than the generated
    # classes' input-only `validation_alias=`, so with serialize_by_alias on,
    # model_dump() would emit YAML aliases (e.g. "mag_set_max_wait_time")
    # instead of field names -- breaking flatten_dict()-based full_dump() and
    # every export path that reads dumps by field name. Pin it back off.
    model_config = ConfigDict(serialize_by_alias=False)

    length: NonNegativeFloat = Field(default=0.0, alias="magnetic_length")
    """Magnetic length [m]."""

    order: int = Field(repr=False, default=0)
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

    @field_validator("field_integral_coefficients", mode="before")
    @classmethod
    def validate_field_integral_coefficients(cls, v: Union[str, List]) -> FieldIntegral:
        result = _coerce_field_integral(v)
        if result is None:
            raise ValueError(
                "field_integral_coefficients should be a string or a list of floats"
            )
        return result

    @property
    def field_amplitude(self) -> Union[int, float]:
        """Solenoid field amplitude (ks / length), resolved to a number."""
        return resolve_functional_parameter(self.ks, force=True) / self.length

    @field_amplitude.setter
    def field_amplitude(self, fa: float = 0) -> None:
        self.ks = fa * self.length

    @property
    def ks(self) -> Union[int, float, str]:
        """Solenoid strength as configured. By default (global resolution mode
        off) this is the value as stored — a number, or the name of a functional
        definition; with resolution mode on it is the resolved number. Use
        :attr:`field_amplitude` for the resolved number regardless of mode."""
        return resolve_functional_parameter(
            getattr(self.fields, "S" + str(self.order) + "L")
        )

    @ks.setter
    def ks(self, ks: float = 0) -> None:
        setattr(self.fields, "S" + str(self.order) + "L", ks)


class NonLinearLensMagnet(_NonLinearLensMagnetBase, IgnoreExtra):
    """
    Non-linear lens magnet. See `MAD-X manual`_ and `PAC2011 article`_

    .. _MAD-X manual: https://cern.ch/madx
    .. _PAC2011 article: https://proceedings.jacow.org/PAC2011/papers/wep070.pdf
    """

    # See the comment on Solenoid_Magnet.model_config -- same reasoning.
    model_config = ConfigDict(serialize_by_alias=False)

    length: NonNegativeFloat = Field(default=0.0, alias="magnetic_length")
    """Magnetic length of NLL [m]."""

    integrated_strength: Union[NonNegativeFloat, str] = Field(
        default=0.0, alias="knll", json_schema_extra={"functional": True}
    )
    """Integrated strength of NLL. Stored verbatim: a number or a string naming a
    functional definition (resolve via ``resolved("integrated_strength")``)."""

    dimensional_parameter: Union[float, str] = Field(
        default=0.0, alias="cnll", json_schema_extra={"functional": True}
    )
    """Dimensional parameter of NLL. Stored verbatim: a number or a string naming
    a functional definition (resolve via ``resolved("dimensional_parameter")``)."""

    def __init__(self, /, **data: Any) -> None:
        super().__init__(**data)


class CorrectorMagnet(DipoleMagnet, _CorrectorMagnetBase):
    """
    Corrector (steering) magnet.

    The two kick angles are the two components of the *same* order-0 multipole,
    addressed by beam plane: `horizontal_kick` goes to `multipoles.K0L.normal`
    and `vertical_kick` goes to `multipoles.K0L.vertical`.

    Use :meth:`resolved_kicks` for the resolved numbers regardless of mode.
    """

    def __init__(self, /, **data: Any) -> None:
        super().__init__(**data)
        if data.get("horizontal_kick") is not None:
            self.horizontal_kick = data["horizontal_kick"]
        if data.get("vertical_kick") is not None:
            self.vertical_kick = data["vertical_kick"]

    def _k0l(self) -> Multipole:
        """The order-0 multipole, creating ``multipoles`` if it is unset."""
        if self.multipoles is None:
            object.__setattr__(self, "multipoles", Multipoles())
        return self.multipoles.K0L

    @computed_field
    @property
    def horizontal_kick(self) -> Union[int, float, str]:
        """Horizontal kick angle [rad] -- the normal component of ``K0L``."""
        return resolve_functional_parameter(self._k0l().normal)

    @horizontal_kick.setter
    def horizontal_kick(self, value: Union[int, float, str]) -> None:
        k0l = self._k0l()
        k0l.normal = value
        k0l.order = 0

    @computed_field
    @property
    def vertical_kick(self) -> Union[int, float, str]:
        """Vertical kick angle [rad] -- the skew component of ``K0L``."""
        return resolve_functional_parameter(self._k0l().skew)

    @vertical_kick.setter
    def vertical_kick(self, value: Union[int, float, str]) -> None:
        k0l = self._k0l()
        k0l.skew = value
        k0l.order = 0

    def resolved_kicks(self) -> tuple[float, float]:
        """
        Both kick angles as numbers, the kick counterpart of
        :meth:`~MagneticElement.KnL`.

        Returns:
            tuple[float, float]: ``(horizontal_kick, vertical_kick)`` [rad].
        """
        k0l = self._k0l()
        return (
            resolve_functional_parameter(k0l.normal, force=True),
            resolve_functional_parameter(k0l.skew, force=True),
        )

    def kick_from_angle(self, skew: bool = None) -> Union[int, float, str]:
        """
        Transfer this magnet's bend angle (equivalently ``k0l`` / ``kl``) onto
        the kick of the plane implied by *skew*, and return it.

        Args:
            skew (bool, optional): Put the angle in the vertical (skew) plane
                rather than the horizontal (normal) one. Defaults to this
                magnet's :attr:`skew` flag.

        Returns:
            Union[int, float, str]: The kick now held by the selected plane,
            as stored.
        """
        skew = self.skew if skew is None else skew
        k0l = self._k0l()
        source = "skew" if skew else "normal"
        other = "normal" if skew else "skew"
        value = getattr(k0l, source)
        if not _is_set(value) and _is_set(getattr(k0l, other)):
            value = getattr(k0l, other)
            setattr(k0l, source, value)
            setattr(k0l, other, 0.0)
        return value

    def current_to_angle(self, current: float, momentum: float) -> float:
        """
        Convert a magnet current to a kick angle.

        Args:
            current (float): Magnet current [A].
            momentum (float): Beam momentum [MeV/c].

        Returns:
            float: The kick angle [rad]. Note this is radians, unlike
            :meth:`DipoleMagnet.current_to_angle`, which returns degrees.
        """
        return self.linear_saturation_coefficients.current_to_k(
            current=current, momentum=momentum
        )["KL"]

    def angle_to_current(self, angle: float, momentum: float) -> float:
        """
        Inverse of :meth:`current_to_angle`.

        Args:
            angle (float): Kick angle [rad].
            momentum (float): Beam momentum [MeV/c].

        Returns:
            float: The magnet current [A].
        """
        return self.linear_saturation_coefficients.kl_to_current(angle, momentum)


class CombinedCorrectorMagnet(_CombinedCorrectorMagnetBase, IgnoreExtra):
    """
    The two corrector fields inside one combined corrector.

    The horizontal and vertical planes are separate magnets with separate
    windings.

    The kick accessors are proxied to the plane that owns them, so
    ``magnetic.horizontal_kick`` / ``magnetic.vertical_kick`` read and write the
    same way they do on a single-plane corrector -- only the *calibration* is
    per-plane.
    """

    horizontal: CorrectorMagnet = Field(default_factory=CorrectorMagnet)
    """Horizontal-plane corrector field, with its own calibration."""

    vertical: CorrectorMagnet = Field(default_factory=CorrectorMagnet)
    """Vertical-plane corrector field, with its own calibration."""

    @model_validator(mode="before")
    @classmethod
    def _accept_single_magnet(cls, data: Any) -> Any:
        """Build the two planes, merging any shared top-level magnetic keys into
        each. Could be a single flat corrector mapping, a flat mapping plus
        ``horizontal`` and ``vertical`` keys, or two fully specified planes.

        Each plane keeps only its own kick, so a combined corrector never
        deflects in both planes off one value.
        """
        if not isinstance(data, dict):
            return data
        per_plane = ("horizontal", "vertical")
        kicks = ("horizontal_kick", "vertical_kick")
        shared = {k: v for k, v in data.items() if k not in per_plane + kicks}
        out = {}
        for plane, kick in zip(per_plane, kicks):
            own = data.get(plane) or {}
            merged = {**shared, **own}
            merged[kick] = own.get(kick, data.get(kick, 0.0))
            merged.pop(kicks[1] if plane == "horizontal" else kicks[0], None)
            out[plane] = merged
        return out

    # -- Proxies to the plane that owns the quantity ------------------------
    @computed_field
    @property
    def horizontal_kick(self) -> Union[int, float, str]:
        """Horizontal kick angle [rad], held by :attr:`horizontal`."""
        return self.horizontal.horizontal_kick

    @horizontal_kick.setter
    def horizontal_kick(self, value: Union[int, float, str]) -> None:
        self.horizontal.horizontal_kick = value

    @computed_field
    @property
    def vertical_kick(self) -> Union[int, float, str]:
        """Vertical kick angle [rad], held by :attr:`vertical`."""
        return self.vertical.vertical_kick

    @vertical_kick.setter
    def vertical_kick(self, value: Union[int, float, str]) -> None:
        self.vertical.vertical_kick = value

    @computed_field
    @property
    def length(self) -> float:
        """Magnetic length [m] of the horizontal magnet."""
        return self.horizontal.length

    @length.setter
    def length(self, value: float) -> None:
        self.horizontal.length = value
        self.vertical.length = value

    @computed_field
    @property
    def order(self) -> int:
        """Multipole order (0, a dipole-like kick)."""
        return self.horizontal.order

    @computed_field
    @property
    def tilt(self) -> float:
        """Roll of the horizontal magnet about the beam axis [rad]."""
        return self.horizontal.tilt

    @tilt.setter
    def tilt(self, value: float) -> None:
        self.horizontal.tilt = value
        self.vertical.tilt = value

    def __getattr__(self, name: str) -> Any:
        """Fall back to the horizontal plane for the rest of the magnetic
        surface (``tilt``, ``multipoles``, ``current_to_k``, ...), so a combined
        corrector still reads like a magnet."""
        if name.startswith("_") or name in ("horizontal", "vertical"):
            raise AttributeError(name)
        return getattr(self.horizontal, name)

    def __setattr__(self, name: str, value: Any) -> None:
        """Mirror of :meth:`__getattr__`. Anything proxied is geometry the two
        planes share, so it is written to both -- without this, a write of a
        proxied name (``reverse_element`` swapping the edge angles) would land
        on the pair as an extra field and the plane would keep the old value."""
        if (
            name.startswith("_")
            or name in type(self).model_fields
            or hasattr(type(self), name)
        ):
            super().__setattr__(name, value)
            return
        setattr(self.horizontal, name, value)
        setattr(self.vertical, name, value)

    def resolved_kicks(self) -> tuple[float, float]:
        """``(horizontal_kick, vertical_kick)`` [rad] as numbers, resolving
        functional definitions regardless of the global resolution mode."""
        return (
            self.horizontal.resolved_kicks()[0],
            self.vertical.resolved_kicks()[1],
        )

    def current_to_angle(self, current: float, momentum: float, skew: bool = False) -> float:
        """
        Convert a magnet current to a kick angle using the calibration of the
        requested plane.

        Args:
            current (float): Magnet current [A].
            momentum (float): Beam momentum [MeV/c].
            skew (bool): Use the vertical plane's calibration instead of the
                horizontal one.

        Returns:
            float: The kick angle [rad].
        """
        plane = self.vertical if skew else self.horizontal
        return plane.current_to_angle(current, momentum)

    def angle_to_current(self, angle: float, momentum: float, skew: bool = False) -> float:
        """Inverse of :meth:`current_to_angle`, using the same plane selection."""
        plane = self.vertical if skew else self.horizontal
        return plane.angle_to_current(angle, momentum)


class WigglerMagnet(_WigglerMagnetBase, IgnoreExtra):
    """
    Undulator magnet.
    """

    # See the comment on Solenoid_Magnet.model_config -- same reasoning.
    model_config = ConfigDict(serialize_by_alias=False)

    length: NonNegativeFloat = Field(default=0.0, alias="magnetic_length")
    """Magnetic length of wiggler [m].
    #TODO validate / check that length == period*num_periods.
    """

    strength: Union[NonNegativeFloat, str] = Field(
        default=0.0, alias="K", json_schema_extra={"functional": True}
    )
    """Wiggler strength (K) parameter. Stored verbatim: a number or a string
    naming a functional definition (resolved via :attr:`normalized_strength` /
    ``resolved("strength")``)."""

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

    @property
    def normalized_strength(self) -> float:
        """
        Getter for the normalised undulator strength :math:`a_w`

        Returns
        -------
        float:
            :attr:`~strength` / :math:`\\sqrt{2}`
        """

        strength = self.resolved("strength")
        if not self.helical:
            return strength / np.sqrt(2)
        else:
            return strength

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


from laura._compat import deprecated_aliases  # noqa: E402

__getattr__ = deprecated_aliases(
    __name__,
    globals(),
    {
        "Corrector_Magnet": "CorrectorMagnet",
        "Dipole_Magnet": "DipoleMagnet",
        "NonLinearLens_Magnet": "NonLinearLensMagnet",
        "Octupole_Magnet": "OctupoleMagnet",
        "Power": "power",
        "Quadrupole_Magnet": "QuadrupoleMagnet",
        "Sextupole_Magnet": "SextupoleMagnet",
        "Solenoid_Magnet": "SolenoidMagnet",
        "Sqrt": "sqrt",
        "Wiggler_Magnet": "WigglerMagnet",
        "solenoidFields": "solenoid_fields",
        "solenoidFieldsData": "solenoid_fields_data",
    },
)
