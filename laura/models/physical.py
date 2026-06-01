import numpy as np
from pydantic import (
    field_validator,
    model_validator,
    PrivateAttr,
    computed_field,
    model_serializer,
    BaseModel,
    Field,
)
from typing import List, Literal, Optional, Union, Dict, Any

from ._generated import _PositionBase, _RotationBase, _ElementPositionErrorBase, _ElementSurveyBase, _PhysicalElementBase
from ..utils.rotation_matrix import euler_angles_to_rotation_matrix


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

    def __neq__(self, other) -> bool:
        return not self.__eq__(other)

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

    def __neq__(self, other) -> bool:
        return not self.__eq__(other)

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
        if isinstance(v, (list, tuple, np.ndarray)):
            coerced = _coerce_position_vector(v)
            if coerced is not None:
                return coerced
            raise ValueError("position should be a number or a list of floats")
        if isinstance(v, Position):
            return v
        if isinstance(v, dict):
            return _coerce_position_mapping(
                v, error_message="setting position as dictionary must include x, y, z as floats"
            )

        raise ValueError("position should be a number or a list of floats")

    @field_validator("rotation", mode="before")
    @classmethod
    def validate_rotation(cls, v: Union[Rotation, Dict, List, np.ndarray]) -> Rotation:
        if v is None:
            return Rotation(theta=0, phi=0, psi=0)
        if isinstance(v, (list, tuple, np.ndarray)):
            coerced = _coerce_rotation_vector(v)
            if coerced is not None:
                return Rotation(theta=coerced.phi, phi=coerced.psi, psi=coerced.theta)
            raise ValueError("rotation should be a number or a list of floats")
        if isinstance(v, Rotation):
            return v
        if isinstance(v, dict):
            return _coerce_rotation_mapping(
                v, error_message="setting rotation as dictionary must include phi, psi, theta as floats"
            )

        raise ValueError("rotation should be a number or a list of floats")

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
        return self.__class__.__name__ + "(" + self.__str__() + ")"

    def __eq__(self, other):
        cls = self.__class__
        if other == 0:
            return all([getattr(self, k) == 0 for k in cls.model_fields.keys()])
        else:
            return super().__eq__(other)


class ElementSurvey(ElementError):
    pass


class ReferencePlacement(BaseModel):
    """
    Position an element relative to a named reference element's frame.

    The ``offset`` field is expressed in the reference element's local frame at
    the chosen ``point`` (start / middle / end).  Use ``world_offset`` instead
    to supply an offset already in global world coordinates.  Only one of the
    two offset fields may be set at a time.

    YAML examples::

        # At the exit of a dipole, no offset
        reference_placement:
          element: some_dipole

        # 1 m downstream along the dipole exit axis
        reference_placement:
          element: some_dipole
          offset: [0, 0, 1.0]

        # 5 cm horizontal shift in world frame
        reference_placement:
          element: some_dipole
          world_offset: [0.05, 0, 0]
    """

    element: str
    point: Literal["start", "middle", "end"] = "end"
    offset: Optional[Position] = Field(default=None)
    world_offset: Optional[Position] = Field(default=None)

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
    def _check_offset_exclusivity(self) -> "ReferencePlacement":
        if self.offset is not None and self.world_offset is not None:
            raise ValueError(
                "Specify either 'offset' (reference-frame) or 'world_offset' "
                "(world-frame) in reference_placement — not both."
            )
        return self


class PhysicalElement(_PhysicalElementBase):
    """
    Physical info model.
    """

    reference_placement: Optional[ReferencePlacement] = Field(default=None)
    """Place this element relative to another element's frame instead of using
    absolute world coordinates.  Mutually exclusive with ``middle``/``position``/``centre``."""

    @model_validator(mode="after")
    def _check_placement_exclusivity(self) -> "PhysicalElement":
        # Check model_fields_set so that an un-provided middle (defaulting to None)
        # doesn't trigger the error — only an explicitly supplied position does.
        if self.reference_placement is not None and "middle" in self.model_fields_set:
            raise ValueError(
                "Cannot specify both a world position ('middle'/'position'/'centre') "
                "and 'reference_placement' in a physical element — use one or the other."
            )
        return self

    def model_post_init(self, __context) -> None:
        # Preserve legacy defaults expected by existing code/tests.
        # Skip the middle default when reference_placement is in use; it will be
        # resolved to world coordinates later by the lattice assembly.
        if self.reference_placement is None and self.middle is None:
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
            self.survey = _ElementSurveyBase(
                position=Position(x=0, y=0, z=0),
                rotation=Rotation(theta=0, phi=0, psi=0),
            )

    _parent: Any = PrivateAttr(default=None)

    def __str__(self):
        cls = self.__class__
        if any([getattr(self, k) != 0 for k in cls.model_fields.keys()]):
            return " ".join(
                [
                    str(k) + "=" + getattr(self, k).__repr__()
                    for k in cls.model_fields.keys()
                    if getattr(self, k) != 0
                ]
            )
        else:
            return str()

    def __repr__(self):
        return self.__class__.__name__ + "(" + self.__str__() + ")"

    @computed_field
    @property
    def _physical_angle(self) -> float:
        if self._parent is not None:
            magnetic = getattr(self._parent, "magnetic", None)
            if magnetic is not None and getattr(magnetic, "angle", None) is not None:
                self.physical_angle = magnetic.angle
                return magnetic.angle
        self.physical_angle = 0.0
        return 0.0

    @field_validator("middle", mode="before")
    @classmethod
    def validate_middle(cls, v: Union[float, int, Dict, List, np.ndarray]) -> Optional[Position]:
        if v is None:
            return None  # Deferred to model_post_init to respect reference_placement
        if isinstance(v, (float, int)):
            return Position(z=v)
        if isinstance(v, (list, tuple, np.ndarray)):
            coerced = _coerce_position_vector(v)
            if coerced is not None:
                return coerced
            raise ValueError("middle should be a number or a list of floats")
        if isinstance(v, Position):
            return v
        if isinstance(v, dict):
            return _coerce_position_mapping(
                v, error_message="setting middle as dictionary must include x, y, z as floats"
            )
        raise ValueError("middle should be a number or a list of floats")

    @field_validator("datum", mode="before")
    @classmethod
    def validate_datum(cls, v: Union[float, int, Dict, List, np.ndarray]) -> Position:
        if v is None:
            return Position()
        if isinstance(v, (float, int)):
            return Position(z=v)
        if isinstance(v, (list, tuple, np.ndarray)):
            coerced = _coerce_position_vector(v)
            if coerced is not None:
                return coerced
            raise ValueError("datum should be a number or a list of floats")
        if isinstance(v, Position):
            return v
        if isinstance(v, dict):
            return _coerce_position_mapping(
                v, error_message="setting datum as dictionary must include x, y, z as floats"
            )
        raise ValueError("datum should be a number or a list of floats")

    @field_validator("rotation", "global_rotation", mode="before")
    @classmethod
    def validate_rotation(cls, v: Union[float, int, List, np.ndarray]) -> Rotation:
        if v is None:
            return Rotation(theta=0, phi=0, psi=0)
        if isinstance(v, (float, int)):
            return Rotation(theta=v)
        if isinstance(v, (list, tuple, np.ndarray)):
            coerced = _coerce_rotation_vector(v)
            if coerced is not None:
                return coerced
            raise ValueError("rotation should be a number or a list of floats")
        if isinstance(v, Rotation):
            return v
        if isinstance(v, dict):
            return _coerce_rotation_mapping(
                v, error_message="setting rotation as dictionary must include phi, psi, theta as floats"
            )

        raise ValueError("rotation should be a number or a list of floats")

    _rotation_matrix_cache = None

    @property
    def rotation_matrix(self) -> np.ndarray:
        if self._rotation_matrix_cache is not None:
            return self._rotation_matrix_cache
        
        # Combined rotations using utility function
        # Apply yaw (Y), pitch (X), roll (Z) in that order
        yaw = self.rotation.theta + self.global_rotation.theta
        pitch = self.rotation.phi + self.global_rotation.phi
        roll = self.rotation.psi + self.global_rotation.psi

        self._rotation_matrix_cache = euler_angles_to_rotation_matrix(yaw, pitch, roll)
        return self._rotation_matrix_cache

    def rotated_position(self, vec: List[Union[int, float]] = [0, 0, 0]) -> np.ndarray:
        """
        Get the rotated position of the element based on matrix multiplication with rotation_matrix.

        Parameters
        ----------
        vec: List[float]
            Vector by which to rotate the element

        Returns
        -------
        np.ndarray
            Rotated vector.
        """
        return self.rotation_matrix @ np.array(vec)

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
        return self.rotation_matrix @ ry_neg

    @property
    def start(self) -> Position:
        if self.middle is None:
            raise RuntimeError(
                "Cannot compute 'start': element has an unresolved "
                "'reference_placement'. Call resolve_reference_placements() "
                "on the containing lattice first."
            )
        middle = np.array(self.middle.array)

        if abs(self._physical_angle) > 1e-9:
            # Bent element
            sx = (
                -self.length
                * (1 - np.cos(self._physical_angle))
                / (2 * self._physical_angle)
            )
            sy = 0
            sz = (
                -self.length * np.sin(self._physical_angle) / (2 * self._physical_angle)
            )
        else:
            # Straight element
            sx, sy, sz = 0, 0, -self.length / 2.0

        vec = [sx, sy, sz]
        start = middle + self.rotated_position(vec)
        return Position.from_list(start)

    @property
    def end(self) -> Position:
        if self.middle is None:
            raise RuntimeError(
                "Cannot compute 'end': element has an unresolved "
                "'reference_placement'. Call resolve_reference_placements() "
                "on the containing lattice first."
            )
        middle = np.array(self.middle.array)

        if abs(self._physical_angle) > 1e-9:
            ex = (
                self.length
                * (1 - np.cos(self._physical_angle))
                / (2 * self._physical_angle)
            )
            ey = 0
            ez = self.length * np.sin(self._physical_angle) / (2 * self._physical_angle)
        else:
            ex, ey, ez = 0, 0, self.length / 2.0

        vec = [ex, ey, ez]
        end = middle + self.rotated_position(vec)
        return Position.from_list(end)
