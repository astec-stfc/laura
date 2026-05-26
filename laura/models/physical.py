import numpy as np
from pydantic import (
    field_validator,
    confloat,
    Field,
    AliasChoices,
    PrivateAttr,
    computed_field,
    model_serializer,
)
from typing import List, Union, Dict, Any

from .baseModels import IgnoreExtra
from ._generated import _PositionBase, _RotationBase, _ElementPositionErrorBase, _ElementSurveyBase, _PhysicalElementBase


class Position(_PositionBase):
    """
    Position model. Cartesian co-ordinates are used.
    """

    x: float = 0.0
    """Horizontal position [m]."""

    y: float = 0.0
    """Vertical position [m]."""

    z: float = 0.0
    """Longitudinal position [m]."""

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

    phi: confloat(ge=-np.pi, le=np.pi) = 0.0  # type: ignore
    """Rotation about the horizontal axis [rad]."""

    psi: confloat(ge=-np.pi, le=np.pi) = 0.0  # type: ignore
    """Rotation about the vertical axis [rad]."""

    theta: confloat(ge=-np.pi, le=np.pi) = 0.0  # type: ignore
    """Rotation about the longitudinal axis [rad]."""

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

    position: Union[Position, List[Union[float, int]]] = Position(x=0, y=0, z=0)
    """Errors in position."""

    rotation: Union[Rotation, List[Union[float, int]]] = Rotation(theta=0, phi=0, psi=0)
    """Errors in rotation."""

    @field_validator("position", mode="before")
    @classmethod
    def validate_position(cls, v: Union[Position, Dict, List, np.ndarray]) -> Position:
        if isinstance(v, (list, tuple, np.ndarray)) and len(v) == 3:
            return Position(x=v[0], y=v[1], z=v[2])
        elif isinstance(v, Position):
            return v
        elif isinstance(v, dict):
            if all(k in ("x", "y", "z") for k in v):
                return Position(
                    x=float(v.get("x", 0.0)),
                    y=float(v.get("y", 0.0)),
                    z=float(v.get("z", 0.0)),
                )
            else:
                raise ValueError(
                    "setting position as dictionary must include x, y, z as floats"
                )

        else:
            raise ValueError("position should be a number or a list of floats")

    @field_validator("rotation", mode="before")
    @classmethod
    def validate_rotation(cls, v: Union[Rotation, Dict, List, np.ndarray]) -> Rotation:
        if isinstance(v, (list, tuple, np.ndarray)) and len(v) == 3:
            return Rotation(theta=v[0], phi=v[1], psi=v[2])
        elif isinstance(v, Rotation):
            return v
        elif isinstance(v, dict):
            if all(k in ("phi", "psi", "theta") for k in v):
                return Rotation(
                    phi=float(v.get("phi", 0.0)),
                    psi=float(v.get("psi", 0.0)),
                    theta=float(v.get("theta", 0.0)),
                )
            else:
                raise ValueError(
                    "setting rotation as dictionary must include phi, psi, theta as floats"
                )

        else:
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


class PhysicalElement(_PhysicalElementBase):
    """
    Physical info model.
    """

    middle: Position = Field(
        default=Position(), alias=AliasChoices("position", "centre")
    )
    """Middle position of the element."""

    datum: Position = Field(default_factory=Position)
    """Datum."""

    rotation: Rotation = Rotation(theta=0, phi=0, psi=0)
    """Local rotation of the element."""

    global_rotation: Rotation = Rotation(theta=0, phi=0, psi=0)
    """Global rotation of the element."""

    error: ElementError = ElementError()
    """Position errors in the element."""

    survey: ElementSurvey = ElementSurvey()
    """Survey positions of the element."""

    length: float = 0.0
    """Length of the element."""

    maximum_position: float | None = None
    """Maximum position of the element"""

    minimum_position: float | None = None
    """Minimum position of the element"""

    _parent: Any = PrivateAttr(default=None)

    physical_angle: float = 0.0

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

    @field_validator("middle", "datum", mode="before")
    @classmethod
    def validate_middle(cls, v: Union[float, int, Dict, List, np.ndarray]) -> Position:
        if isinstance(v, (float, int)):
            return Position(z=v)
        elif isinstance(v, (list, tuple, np.ndarray)):
            if len(v) == 3:
                return Position(x=v[0], y=v[1], z=v[2])
            elif len(v) == 2:
                return Position(x=v[0], y=0, z=v[1])
        elif isinstance(v, Position):
            return v
        elif isinstance(v, dict):
            if all(k in ("x", "y", "z") for k in v):
                return Position(
                    x=float(v.get("x", 0.0)),
                    y=float(v.get("y", 0.0)),
                    z=float(v.get("z", 0.0)),
                )
            else:
                raise ValueError(
                    "setting middle as dictionary must include x, y, z as floats"
                )

        else:
            raise ValueError("middle should be a number or a list of floats")

    @field_validator("rotation", "global_rotation", mode="before")
    @classmethod
    def validate_rotation(cls, v: Union[float, int, List, np.ndarray]) -> Rotation:
        if isinstance(v, (float, int)):
            return Rotation(theta=v)
        elif isinstance(v, (list, tuple, np.ndarray)):
            if len(v) == 3:
                return Rotation(phi=v[0], psi=v[1], theta=v[2])
        elif isinstance(v, Rotation):
            return v
        elif isinstance(v, dict):
            if all(k in ("phi", "psi", "theta") for k in v):
                return Rotation(
                    phi=float(v.get("phi", 0.0)),
                    psi=float(v.get("psi", 0.0)),
                    theta=float(v.get("theta", 0.0)),
                )
            else:
                raise ValueError(
                    "setting rotation as dictionary must include phi, psi, theta as floats"
                )

        else:
            raise ValueError("rotation should be a number or a list of floats")

    _rotation_matrix_cache = None

    @property
    def rotation_matrix(self) -> np.ndarray:
        if self._rotation_matrix_cache is not None:
            return self._rotation_matrix_cache
            
        # Combined rotations. We apply (column-vector convention):
        #   1) yaw (Y)  -> Ry  (rightmost)
        #   2) pitch (X)-> Rx
        #   3) roll (Z) -> Rz  (leftmost)
        yaw = self.rotation.theta + self.global_rotation.theta
        pitch = self.rotation.phi + self.global_rotation.phi
        roll = self.rotation.psi + self.global_rotation.psi

        Rx = np.array(
            [
                [1, 0, 0],
                [0, np.cos(pitch), -np.sin(pitch)],
                [0, np.sin(pitch), np.cos(pitch)],
            ]
        )

        Rz = np.array(
            [
                [np.cos(roll), -np.sin(roll), 0],
                [np.sin(roll), np.cos(roll), 0],
                [0, 0, 1],
            ]
        )

        Ry = np.array(
            [[np.cos(yaw), 0, -np.sin(yaw)], [0, 1, 0], [np.sin(yaw), 0, np.cos(yaw)]]
        )
        self._rotation_matrix_cache = np.dot(Rz, np.dot(Rx, Ry))
        return self._rotation_matrix_cache

        return Rz @ Rx @ Ry

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
    def start(self) -> Position:
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
