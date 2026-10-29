from typing import Any, Dict, List, Literal, Optional, Union

import numpy as np
from pydantic import (
    Field,
    PrivateAttr,
    computed_field,
    field_validator,
    model_serializer,
    model_validator,
)

from ..utils.rotation_matrix import euler_angles_to_rotation_matrix
from ._generated import (
    _ElementPositionErrorBase,
    _PhysicalElementBase,
    _PositionBase,
    _ReferencePlacementBase,
    _RotationBase,
)
from .trajectory import Trajectory


def _coerce_position_vector(v: Union[List, tuple, np.ndarray]) -> "Position | None":
    if len(v) == 3:
        return Position(x=v[0], y=v[1], z=v[2])
    if len(v) == 2:
        return Position(x=v[0], y=0, z=v[1])
    return None


def _coerce_rotation_vector(v: Union[List, tuple, np.ndarray]) -> "Rotation | None":
    if len(v) == 3:
        return Rotation(phi=v[0], psi=v[1], theta=v[2])
    return None


def _coerce_position_mapping(v: dict, *, error_message: str) -> "Position":
    if all(k in ("x", "y", "z") for k in v):
        return Position(
            x=float(v.get("x", 0.0)),
            y=float(v.get("y", 0.0)),
            z=float(v.get("z", 0.0)),
        )
    raise ValueError(error_message)


def _coerce_rotation_mapping(v: dict, *, error_message: str) -> "Rotation":
    if all(k in ("phi", "psi", "theta") for k in v):
        return Rotation(
            phi=float(v.get("phi", 0.0)),
            psi=float(v.get("psi", 0.0)),
            theta=float(v.get("theta", 0.0)),
        )
    raise ValueError(error_message)


def _coerce_position(v: Any, name: str) -> "Position":
    if isinstance(v, (list, tuple, np.ndarray)):
        coerced = _coerce_position_vector(v)
        if coerced is not None:
            return coerced
    elif isinstance(v, Position):
        return v
    elif isinstance(v, dict):
        return _coerce_position_mapping(
            v,
            error_message=f"setting {name} as dictionary must include x, y, z as floats",
        )
    raise ValueError(f"{name} should be a number or a list of floats")


def _coerce_rotation(v: Any) -> "Rotation":
    if isinstance(v, (list, tuple, np.ndarray)):
        coerced = _coerce_rotation_vector(v)
        if coerced is not None:
            return coerced
    elif isinstance(v, Rotation):
        return v
    elif isinstance(v, dict):
        return _coerce_rotation_mapping(
            v,
            error_message="setting rotation as dictionary must include phi, psi, theta as floats",
        )
    raise ValueError("rotation should be a number or a list of floats")


class Position(_PositionBase):
    """
    Position model. Cartesian co-ordinates are used.
    """

    @model_serializer(mode="wrap")
    def ser_model(self, handler, info) -> list | dict:
        if info.mode == "json":
            return [self.x, self.y, self.z]
        return handler(self)

    @property
    def array(self) -> np.ndarray:
        return np.array([self.x, self.y, self.z])

    @classmethod
    def from_list(cls, vec: List[Union[float, int]]) -> "Position":
        assert len(vec) == 3
        return cls(x=vec[0], y=vec[1], z=vec[2])

    @classmethod
    def from_values(cls, *values: Union[float, int]) -> "Position":
        assert len(values) == 3
        return cls(x=values[0], y=values[1], z=values[2])

    def __iter__(self) -> iter:
        return iter([self.x, self.y, self.z])

    def __eq__(self, other) -> bool:
        if other == 0 or other == 0.0 or other is None:
            return all([self.x == 0, self.y == 0, self.z == 0])
        return list(self) == list(other)

    def __add__(self, other: "Position") -> "Position":
        return Position(
            x=(self.x + other.x), y=(self.y + other.y), z=(self.z + other.z)
        )

    def __radd__(self, other: "Position") -> "Position":
        return self.__add__(other)

    def __sub__(self, other: "Position") -> "Position":
        return Position(
            x=(self.x - other.x), y=(self.y - other.y), z=(self.z - other.z)
        )

    def __rsub__(self, other: "Position") -> "Position":
        return Position(
            x=(other.x - self.x), y=(other.y - self.y), z=(other.z - self.z)
        )

    def dot(self, other: Union[List, "Position"]) -> float:
        if isinstance(other, (set, tuple, list)):
            other = Position.from_list(other)
        return self.x * other.x + self.y * other.y + self.z * other.z

    def vector_angle(self, other: Union[List, "Position"], direction: List) -> float:
        if isinstance(other, (set, tuple, list)):
            other = Position.from_list(other)
        return (self - other).dot(direction)

    def length(self) -> float:
        return np.sqrt([self.x * self.x + self.y * self.y + self.z * self.z])


class Rotation(_RotationBase):
    """
    Rotation model.
    """

    @model_serializer(mode="wrap")
    def ser_model(self, handler, info) -> list | dict:
        if info.mode == "json":
            return [self.phi, self.psi, self.theta]
        return handler(self)

    @property
    def array(self) -> np.ndarray:
        return np.array([self.phi, self.psi, self.theta])

    @classmethod
    def from_list(cls, vec: List[Union[float, int]]) -> "Rotation":
        assert len(vec) == 3
        return cls(phi=vec[0], psi=vec[1], theta=vec[2])

    @classmethod
    def from_values(cls, *values: Union[float, int]) -> "Rotation":
        assert len(values) == 3
        return cls(phi=values[0], psi=values[1], theta=values[2])

    def __iter__(self) -> iter:
        return iter([self.phi, self.psi, self.theta])

    def __eq__(self, other) -> bool:
        if other == 0 or other == 0.0 or other is None:
            return all([self.phi == 0, self.psi == 0, self.theta == 0])
        return list(self) == list(other)

    def __add__(self, other: "Rotation") -> "Rotation":
        return Rotation(
            phi=(self.phi + other.phi),
            psi=(self.psi + other.psi),
            theta=(self.theta + other.theta),
        )

    def __radd__(self, other: "Rotation") -> "Rotation":
        return self.__add__(other)

    def __sub__(self, other: "Rotation") -> "Rotation":
        return Rotation(
            phi=(self.phi - other.phi),
            psi=(self.psi - other.psi),
            theta=(self.theta - other.theta),
        )

    def __rsub__(self, other: "Rotation") -> "Rotation":
        return Rotation(
            phi=(other.phi - self.phi),
            psi=(other.psi - self.psi),
            theta=(other.theta - self.theta),
        )

    def __abs__(self):
        return Rotation(phi=abs(self.phi), psi=abs(self.psi), theta=abs(self.theta))

    def __gt__(self, value: Union[int, float, List, "Rotation"]):
        if isinstance(value, (int, float)):
            return any([self.phi > value, self.psi > value, self.theta > value])
        elif isinstance(value, (list, set, tuple)):
            return [self.phi, self.psi, self.theta] > value
        elif isinstance(value, Rotation):
            return any(
                [self.phi > value.phi, self.psi > value.psi, self.theta > value.theta]
            )


class ElementError(_ElementPositionErrorBase):
    """
    Position/Rotation error model.
    """

    def model_post_init(self, __context) -> None:
        # Preserve historical defaults while keeping schema fields authoritative.
        if self.position is None:
            self.position = Position(x=0, y=0, z=0)
        if self.rotation is None:
            self.rotation = Rotation(theta=0, phi=0, psi=0)

    @field_validator("position", mode="before")
    @classmethod
    def validate_position(cls, v: Union[Position, Dict, List, np.ndarray]) -> Position:
        if v is None:
            return Position(x=0, y=0, z=0)
        return _coerce_position(v, "position")

    @field_validator("rotation", mode="before")
    @classmethod
    def validate_rotation(cls, v: Union[Rotation, Dict, List, np.ndarray]) -> Rotation:
        if v is None:
            return Rotation(theta=0, phi=0, psi=0)
        coerced = _coerce_rotation(v)
        if isinstance(v, (list, tuple, np.ndarray)):
            # Error lists are ordered theta, phi, psi.
            return Rotation(theta=coerced.phi, phi=coerced.psi, psi=coerced.theta)
        return coerced

    def __str__(self):
        cls = self.__class__
        if any([getattr(self, k) != 0 for k in cls.model_fields]):
            return " ".join(
                [
                    getattr(self, k).__repr__()
                    for k in cls.model_fields
                    if getattr(self, k) != 0
                ]
            )
        else:
            return str(None)

    def __repr__(self):
        return f"{self.__class__.__name__}({self.__str__()})"

    def __eq__(self, other):
        cls = self.__class__
        if other == 0:
            return all([getattr(self, k) == 0 for k in cls.model_fields.keys()])
        else:
            return super().__eq__(other)


class ElementSurvey(ElementError):  # noqa: N818
    pass


class ReferencePlacement(_ReferencePlacementBase):
    """
    Position an element relative to a named reference element's frame.

    Exactly one offset field may be set (or none for zero offset):

    * ``offset`` — full 3-D offset **in the reference element's local frame**
      at the chosen ``point``.
    * ``world_offset`` — full 3-D offset already in **global world coordinates**.
    * ``s_offset`` — scalar offset **along the local beam direction** (s-axis)
      from the reference point; equivalent to ``offset: [0, 0, s_offset]``.

    YAML examples::

        # At the exit of a dipole, no offset
        reference_placement:
          element: some_dipole

        # 1 m downstream along the dipole exit axis (local frame)
        reference_placement:
          element: some_dipole
          offset: [0, 0, 1.0]

        # Same thing, more concisely
        reference_placement:
          element: some_dipole
          s_offset: 1.0

        # 5 cm horizontal shift in world frame
        reference_placement:
          element: some_dipole
          world_offset: [0.05, 0, 0]
    """

    point: Literal["start", "middle", "end"] = "end"

    @field_validator("offset", "world_offset", mode="before")
    @classmethod
    def _coerce_offset(cls, v):
        if v is None:
            return None
        if isinstance(v, Position):
            return v
        if isinstance(v, (list, tuple, np.ndarray)):
            coerced = _coerce_position_vector(v)
            if coerced is not None:
                return coerced
            raise ValueError("offset must be a list of 3 floats")
        if isinstance(v, dict):
            return _coerce_position_mapping(
                v, error_message="offset dict must contain x, y, z"
            )
        raise ValueError("offset must be a list of 3 floats or {x, y, z} dict")

    @model_validator(mode="after")
    def _check_offset_exclusivity(
        self,  # noqa: N804 (pydantic after-validator takes self)
    ) -> "ReferencePlacement":
        n = sum(
            [
                self.offset is not None,
                self.world_offset is not None,
                self.s_offset is not None,
            ]
        )
        if n > 1:
            raise ValueError(
                "Specify at most one offset in reference_placement: "
                "'offset' (local frame), 'world_offset' (global frame), "
                "or 's_offset' (beam-direction scalar)."
            )
        return self


class PhysicalElement(_PhysicalElementBase):
    """
    Physical info model.
    """

    # Override generated base-class types so list inputs are coerced correctly.
    # The bare generated bases (_ElementPositionErrorBase etc.) only accept dicts
    # or model instances; the concrete subclasses add the list/array coercers.
    error: Optional[ElementError] = Field(default=None)
    survey: Optional[ElementSurvey] = Field(default=None)
    reference_placement: Optional[ReferencePlacement] = Field(default=None)

    # s is included in default serialisation (once resolved) as an
    # informational reference value alongside the authoritative 'middle'
    # (Z), for backwards-compatible file output. s_point stays excluded by
    # default — it only matters for the explicit s-coordinate export modes
    # (model_dump_s() / position_mode="s"/"reference"), which set it directly.
    s: Optional[float] = Field(default=None)
    s_point: Literal["start", "middle", "end"] = Field(default="middle", exclude=True)

    _parent: Any = PrivateAttr(default=None)
    _trajectory: Optional[Trajectory] = PrivateAttr(default=None)
    # Whether ``physical_angle`` was supplied explicitly at construction, as
    # opposed to being left to derive from the magnetic model.
    _explicit_angle: bool = PrivateAttr(default=False)

    @model_validator(mode="after")
    def _check_placement_exclusivity(
        self,  # noqa: N804 (pydantic after-validator takes self)
    ) -> "PhysicalElement":
        # Pydantic v2 re-runs model validators on every field assignment when
        # validate_assignment=True.  After construction the lattice assembly
        # legitimately sets both middle AND s on the same element, so we only
        # enforce mutual-exclusion during initial construction.
        if getattr(self, "_constructed", False):
            return self
        # 'middle' + 's' together is allowed: 'middle' remains authoritative
        # and 's' is treated as an informational/redundant reference value
        # (e.g. round-tripped from a default YAML export that now records
        # both for backwards compatibility). Only reject an ambiguous mix
        # involving 'reference_placement'.
        has_middle = "middle" in self.model_fields_set
        has_reference = self.reference_placement is not None
        has_s = "s" in self.model_fields_set
        if has_reference and (has_middle or has_s):
            raise ValueError(
                "Cannot specify both a world position ('middle'/'position'/'centre'/'s') "
                "and 'reference_placement' — use only one."
            )
        return self

    def model_post_init(self, __context) -> None:
        object.__setattr__(
            self,
            "_position_stated",
            self.reference_placement is not None
            or self.middle is not None
            or self.s is not None,
        )
        object.__setattr__(
            self, "_explicit_angle", "physical_angle" in self.model_fields_set
        )
        # Skip the middle default when another positioning mode handles placement.
        if self.reference_placement is None and self.middle is None and self.s is None:
            self.middle = Position()
        if self.datum is None:
            self.datum = Position()
        if self.rotation is None:
            self.rotation = Rotation(theta=0, phi=0, psi=0)
        if self.global_rotation is None:
            self.global_rotation = Rotation(theta=0, phi=0, psi=0)
        if self.error is None:
            self.error = ElementError()
        if self.survey is None:
            self.survey = ElementSurvey()
        # Mark construction complete so the exclusivity validator is not
        # re-triggered by lattice-assembly code that sets both s and middle.
        object.__setattr__(self, "_constructed", True)

    def __setattr__(self, name: str, value: Any) -> None:
        # Guard flag stored directly on the instance (not a Pydantic field).
        if name == "_syncing":
            object.__setattr__(self, "_syncing", value)
            return
        super().__setattr__(name, value)
        if getattr(self, "_syncing", False):
            return
        # Bidirectional s ↔ middle sync when trajectory is available.
        traj: Optional[Trajectory] = None
        try:
            traj = self.__pydantic_private__.get("_trajectory")
        except (AttributeError, TypeError):
            pass
        if traj is None:
            return
        object.__setattr__(self, "_syncing", True)
        try:
            if name == "s" and value is not None:
                self.middle = traj.xyz_at_s(value)
            elif name == "middle" and value is not None:
                self.s = traj.s_at_xyz(value)
        finally:
            object.__setattr__(self, "_syncing", False)

    def model_dump_s(self, **kwargs) -> dict:
        """Serialise using ``s`` instead of global ``middle`` coordinates.

        If ``s`` has been set (either as input or by lattice assembly), the
        returned dict contains ``s`` (and ``s_point`` when not ``'middle'``)
        in place of ``middle``.  Falls back to the standard ``model_dump``
        output when ``s`` is not available.
        """
        d = self.model_dump(**kwargs)
        if self.s is not None:
            d.pop("middle", None)
            d["s"] = round(self.s, 6)
            if self.s_point != "middle":
                d["s_point"] = self.s_point
        return d

    def __str__(self):
        cls = self.__class__
        if any([getattr(self, k) != 0 for k in cls.model_fields.keys()]):
            return " ".join(
                [
                    f"{k!s}={getattr(self, k).__repr__()}"
                    for k in cls.model_fields.keys()
                    if getattr(self, k) != 0
                ]
            )
        else:
            return str()

    def __repr__(self):
        return f"{self.__class__.__name__}({self.__str__()})"

    def set_physical_angle(self, angle: float | None) -> None:
        """
        Pin the angle used to lay out :func:`start` and :func:`end`, overriding the
        bend angle taken from the magnet. Pass ``None`` to go back to tracking it.

        Needed where the transverse displacement through a magnet does not run the same
        way as its bend: the second and third dipoles of a chicane bend back towards the
        axis while the beam continues to move away from it, so their start/end offsets
        take the sign of the displacement rather than of the field.
        """
        self._physical_angle_override = angle

    @property
    def magnet_angle(self) -> Optional[float]:
        """The bend angle the magnetic model asks for [rad].

        ``None`` where the element has no magnet that can bend, which is not the
        same as a magnet set to bend by zero.
        """
        magnetic = getattr(self._parent, "magnetic", None)
        if magnetic is None or not hasattr(type(magnetic), "angle"):
            return None
        try:
            return float(magnetic.KnL(0))
        except KeyError:
            return 0.0

    @computed_field
    @property
    def _physical_angle(self) -> float:
        if self._physical_angle_override is not None:
            self.physical_angle = self._physical_angle_override
            return self._physical_angle_override
        if self._explicit_angle:
            return float(self.physical_angle)
        angle = self.magnet_angle
        self.physical_angle = 0.0 if angle is None else angle
        return self.physical_angle

    @field_validator("middle", "datum", mode="before")
    @classmethod
    def validate_middle_and_datum(
        cls, v: Union[float, int, Dict, List, np.ndarray], info
    ) -> Optional[Position]:
        if v is None:
            # middle is deferred to model_post_init to respect reference_placement
            return None if info.field_name == "middle" else Position()
        if isinstance(v, (float, int)):
            return Position(z=v)
        return _coerce_position(v, info.field_name)

    @field_validator("rotation", "global_rotation", mode="before")
    @classmethod
    def validate_rotation(cls, v: Union[float, int, List, np.ndarray]) -> Rotation:
        if v is None:
            return Rotation(theta=0, phi=0, psi=0)
        if isinstance(v, (float, int)):
            return Rotation(theta=v)
        return _coerce_rotation(v)

    _rotation_matrix_cache = None
    _rotation_matrix_key = None

    _physical_angle_override = None
    """Set via :func:`set_physical_angle` to pin the layout angle; ``None`` tracks the
    magnet's bend angle."""

    @property
    def rotation_matrix(self) -> np.ndarray:
        """The element's orientation as a 3x3 matrix."""
        # Apply yaw (Y), pitch (X), roll (Z) in that order
        key = (
            self.rotation.theta + self.global_rotation.theta,
            self.rotation.phi + self.global_rotation.phi,
            self.rotation.psi + self.global_rotation.psi,
        )
        if self._rotation_matrix_cache is None or self._rotation_matrix_key != key:
            self._rotation_matrix_cache = euler_angles_to_rotation_matrix(*key)
            self._rotation_matrix_key = key
        return self._rotation_matrix_cache

    def rotated_position(self, vec: List[Union[int, float]] = [0, 0, 0]) -> np.ndarray:
        """
        Rotate a vector by :attr:`rotation_matrix`.

        Parameters
        ----------
        vec: List[float]
            Vector to rotate.

        Returns
        -------
        np.ndarray
            Rotated vector.
        """
        return self.rotation_matrix @ np.array(vec)

    @property
    def _physical_tilt(self) -> float:
        """Roll of the layout plane about the beam axis [rad].

        :attr:`start`, :attr:`end` and :attr:`end_rotation_matrix` all lay the
        bend out in the ``y = 0`` plane of :attr:`rotation_matrix`.  A magnet
        rolled about the beam axis bends in a different plane,
        so the layout has to be rolled with it.
        Read off the magnet rather than folded into :attr:`rotation`.
        """
        magnetic = getattr(self._parent, "magnetic", None)
        tilt = getattr(magnetic, "tilt", None) if magnetic is not None else None
        if not isinstance(tilt, (int, float)) or not tilt:
            return 0.0
        placed = getattr(self.global_rotation, "psi", 0.0) or 0.0
        return 0.0 if abs(placed) > 1e-12 else float(tilt)

    @property
    def _layout_matrix(self) -> np.ndarray:
        """:attr:`rotation_matrix`, rolled into the plane the magnet bends in."""
        tilt = self._physical_tilt
        if not tilt:
            return self.rotation_matrix
        cz, sz = np.cos(tilt), np.sin(tilt)
        return self.rotation_matrix @ np.array(
            [[cz, -sz, 0.0], [sz, cz, 0.0], [0.0, 0.0, 1.0]]
        )

    @property
    def end_rotation_matrix(self) -> np.ndarray:
        """Rotation matrix at the element exit, accounting for bending angle.

        For a straight element this is identical to :attr:`rotation_matrix`.
        For a bent element (dipole) the exit frame is rotated by the full bend
        angle relative to the entrance frame.

        Derivation: in the canonical orientation (rotation = 0) the exit beam
        direction is ``[sin θ, 0, cos θ]`` in global coords.  Rotating by
        ``rotation_matrix`` gives the actual exit direction, which equals
        ``rotation_matrix @ Ry(-θ)`` where Ry uses LAURA's convention
        ``Ry(α) = [[cos α, 0, −sin α], [0,1,0], [sin α, 0, cos α]]``.

        """
        theta = self._physical_angle
        if abs(theta) < 1e-9:
            return self.rotation_matrix
        ct, st = np.cos(theta), np.sin(theta)
        # Ry(-theta) in LAURA's convention
        ry_neg = np.array([[ct, 0, st], [0, 1, 0], [-st, 0, ct]])
        tilt = self._physical_tilt
        if not tilt:
            return self.rotation_matrix @ ry_neg
        cz, sz = np.cos(tilt), np.sin(tilt)
        rz = np.array([[cz, -sz, 0.0], [sz, cz, 0.0], [0.0, 0.0, 1.0]])
        return self.rotation_matrix @ rz @ ry_neg @ rz.T

    def offset_from_middle(self, face: Literal["start", "end"]) -> np.ndarray:
        """The vector from :attr:`middle` to one face of the element [m].

        The one home for the layout geometry: :attr:`start` and :attr:`end` are
        this offset applied to :attr:`middle`.

        The faces sit on the arc, half the bend either side of the middle, in the
        plane the magnet bends in (:attr:`_layout_matrix`).
        """
        theta = self._physical_angle
        if abs(theta) > 1e-9:
            half = theta / 2.0
            rho = self.length / theta
            if face == "end":
                local = [
                    rho * (np.cos(half) - np.cos(theta)),
                    0,
                    rho * (np.sin(theta) - np.sin(half)),
                ]
            else:
                local = [-rho * (1 - np.cos(half)), 0, -rho * np.sin(half)]
        else:
            # Straight element
            local = [0, 0, (self.length / 2.0) * (1 if face == "end" else -1)]
        return self._layout_matrix @ np.array(local)

    def _face(self, face: Literal["start", "end"]) -> Position:
        if self.middle is None:
            raise RuntimeError(
                f"Cannot compute '{face}': element has an unresolved position "
                "(reference_placement or s-coordinate pending). "
                "Call resolve_positions() on the containing lattice first."
            )
        return Position.from_list(
            np.array(self.middle.array) + self.offset_from_middle(face)
        )

    @property
    def start(self) -> Position:
        return self._face("start")

    @property
    def end(self) -> Position:
        return self._face("end")
