from pydantic import (
    computed_field,
    field_validator,
    Field
)
from typing import Any, ClassVar, Dict, Union, List
from .baseModels import FunctionalMixin
import numpy as np
import re
from ._generated import (
    _ApertureElementBase,
    _SimulationElementBase,
    _MagnetSimulationElementBase,
    _RFCavitySimulationElementBase,
    _WakefieldSimulationElementBase,
    _DriftSimulationElementBase,
    _DiagnosticSimulationElementBase,
    _PlasmaSimulationElementBase,
    _TwissMatchSimulationElementBase,
    _MatrixTransformSimulationElementBase,
    _ElectrostaticSeparatorSimulationElementBase,
    _ACDipoleSimulationElementBase,
    _WireSimulationElementBase,
    _BeamBeamSimulationElementBase,
    _RFMultipoleSimulationElementBase,
)
from ..translator.utils.fields import field


class ApertureElement(_ApertureElementBase):
    """Physical info model."""

    pass


class SimulationElement(_SimulationElementBase, FunctionalMixin):
    """
    Simulation element model.
    """

    wakefield_enable: bool = True
    """Flag to indicate whether the wakefield defined by
    :attr:`~wakefield_definition` is applied. Set to False to track the element
    without its wakefield, without discarding the definition itself."""


class MagnetSimulationElement(_MagnetSimulationElementBase, FunctionalMixin):
    """
    Magnet simulation element model.
    """

    field_definition: str | field | None = None
    # Schema declares `smooth` as boolean but ASTRA uses an integer smoothing count (Q_smooth / S_smooth).
    smooth: int | None = 2

    field_amplitude: Union[float, str] = Field(
        default=0.0, json_schema_extra={"functional": True}
    )
    """Field amplitude for the magnet simulation. Stored verbatim: a number or a
    string naming a functional definition (resolve via ``resolved("field_amplitude")``)."""


class DriftSimulationElement(_DriftSimulationElementBase):
    """
    Drift simulation element model.
    """

    pass


class DiagnosticSimulationElement(_DiagnosticSimulationElementBase):
    pass


class PlasmaSimulationElement(_PlasmaSimulationElementBase):
    """
    Plasma simulation element model.
    """

    required_attrs: ClassVar[dict[str, list[str]]] = {
        "common": [
            "length",
        ],
        "quasistatic_2d": [
            "density",
            "r_max",
            "n_longitudinal",
            "n_radial",
            "min_longitudinal_position",
            "max_longitudinal_position",
        ],
    }

    pass


class RFCavitySimulationElement(_RFCavitySimulationElementBase, FunctionalMixin):
    """
    RF cavity simulation element model.
    """

    field_definition: str | field | None = None
    wakefield_definition: str | field | None = None

    field_amplitude: Union[float, str] = Field(
        default=0.0, json_schema_extra={"functional": True}
    )
    """Cavity field amplitude. Stored verbatim: a number or a string naming a
    functional definition (resolve via ``resolved("field_amplitude")``)."""


class WakefieldSimulationElement(_WakefieldSimulationElementBase):
    """
    Wakefield simulation element model.
    """

    wakefield_definition: str | field | None = None

    pass


class TwissMatchSimulationElement(_TwissMatchSimulationElementBase):
    @field_validator("beta_x", "beta_y")
    @classmethod
    def validate_beta(cls, value):
        if value <= 0:
            raise ValueError("Twiss beta must be greater than zero")
        return value

    @computed_field
    @property
    def r_matrix(self) -> np.ndarray:
        bx = np.sqrt(self.beta_x)
        by = np.sqrt(self.beta_y)

        R = np.eye(6)

        # x-plane CS transform
        R[0, 0] = bx
        R[0, 5] = self.eta_x

        R[1, 0] = -self.alpha_x / bx
        R[1, 1] = 1.0 / bx
        R[1, 5] = self.eta_xp

        # y-plane CS transform
        R[2, 2] = by
        R[2, 5] = self.eta_y

        R[3, 2] = -self.alpha_y / by
        R[3, 3] = 1.0 / by
        R[3, 5] = self.eta_yp

        # z, δ untouched
        R[4, 4] = 1.0
        R[5, 5] = 1.0

        return R

    @computed_field
    @property
    def r_matrix_7x7(self) -> np.ndarray:
        n = self.r_matrix.shape[0]
        B = np.zeros((n + 1, n + 1))
        B[:n, :n] = self.r_matrix
        B[n, n] = 1
        return B


class MatrixTransformSimulationElement(_MatrixTransformSimulationElementBase):
    c_matrix: np.ndarray = Field(default_factory=lambda: np.zeros(6))
    """C-matrix for the element (0th order transformation matrix)."""

    r_matrix: np.ndarray = Field(default_factory=lambda: np.eye(6))
    """R-matrix for the element (1st order transformation matrix)."""

    t_matrix: np.ndarray = Field(default_factory=lambda: np.zeros((6, 6, 6)))
    """T-matrix for the element (2nd order transformation matrix)."""

    u_matrix: np.ndarray = Field(default_factory=lambda: np.zeros((6, 6, 6, 6)))
    """U-matrix for the element (3rd order transformation matrix)."""

    spin_taylor: List[Dict[str, Any]] = Field(default_factory=list)
    """Sparse quaternion Taylor terms indexed as S1, Sx, Sy, and Sz (0--3)."""

    @field_validator("c_matrix", mode="before")
    @classmethod
    def validate_c_matrix(cls, v):
        if isinstance(v, dict):
            vector = np.zeros(6)

            for key, value in v.items():
                m = re.fullmatch(r"c(\d)", key.lower())
                if not m:
                    raise ValueError(
                        f"Invalid C-matrix element '{key}'. Expected e.g. c1."
                    )

                idx = int(m.group(1)) - 1

                if not (0 <= idx < 6):
                    raise ValueError(
                        f"C-matrix index out of range: {key}"
                    )

                vector[idx] = float(value)

            return vector

        arr = np.asarray(v, dtype=float)

        if arr.shape != (6,):
            raise ValueError(
                f"c_matrix must have shape (6,), got {arr.shape}"
            )

        return arr

    @field_validator("r_matrix", mode="before")
    @classmethod
    def validate_r_matrix(cls, v):
        if isinstance(v, dict):
            matrix = np.eye(6)

            for key, value in v.items():
                m = re.fullmatch(r"r(\d)(\d)", key.lower())
                if not m:
                    raise ValueError(
                        f"Invalid R-matrix element '{key}'. Expected e.g. r21."
                    )

                row = int(m.group(1)) - 1
                col = int(m.group(2)) - 1

                if not (0 <= row < 6 and 0 <= col < 6):
                    raise ValueError(
                        f"R-matrix index out of range: {key}"
                    )

                matrix[row, col] = float(value)

            return matrix

        arr = np.asarray(v, dtype=float)

        if arr.shape != (6, 6):
            raise ValueError(
                f"r_matrix must have shape (6,6), got {arr.shape}"
            )

        return arr

    @field_validator("t_matrix", mode="before")
    @classmethod
    def validate_t_matrix(cls, v):
        if isinstance(v, dict):
            tensor = np.zeros((6, 6, 6))

            for key, value in v.items():
                m = re.fullmatch(r"t(\d)(\d)(\d)", key.lower())
                if not m:
                    raise ValueError(
                        f"Invalid T-matrix element '{key}'. Expected e.g. t513."
                    )

                i = int(m.group(1)) - 1
                j = int(m.group(2)) - 1
                k = int(m.group(3)) - 1

                if not all(0 <= idx < 6 for idx in (i, j, k)):
                    raise ValueError(
                        f"T-matrix index out of range: {key}"
                    )

                tensor[i, j, k] = float(value)

            return tensor

        arr = np.asarray(v, dtype=float)

        if arr.shape != (6, 6, 6):
            raise ValueError(
                f"t_matrix must have shape (6,6,6), got {arr.shape}"
            )

        return arr

    @field_validator("u_matrix", mode="before")
    @classmethod
    def validate_u_matrix(cls, v):
        if isinstance(v, dict):
            tensor = np.zeros((6, 6, 6, 6))

            for key, value in v.items():
                m = re.fullmatch(r"u(\d)(\d)(\d)(\d)", key.lower())
                if not m:
                    raise ValueError(
                        f"Invalid U-matrix element '{key}'. Expected e.g. u5132."
                    )

                indices = tuple(int(index) - 1 for index in m.groups())
                if not all(0 <= index < 6 for index in indices):
                    raise ValueError(f"U-matrix index out of range: {key}")

                tensor[indices] = float(value)

            return tensor

        arr = np.asarray(v, dtype=float)
        if arr.shape != (6, 6, 6, 6):
            raise ValueError(
                f"u_matrix must have shape (6,6,6,6), got {arr.shape}"
            )
        return arr

    @field_validator("spin_taylor", mode="before")
    @classmethod
    def validate_spin_taylor(cls, terms):
        if terms is None:
            return []
        if not isinstance(terms, (list, tuple)):
            raise ValueError("spin_taylor must be a list of terms")
        required = {"index", "coef", *(f"exp{i}" for i in range(1, 7))}
        for term in terms:
            if not isinstance(term, dict):
                raise ValueError("Each spin Taylor term must be a mapping")
            missing = required - term.keys()
            if missing:
                raise ValueError(
                    f"Spin Taylor term is missing: {', '.join(sorted(missing))}"
                )
            if term["index"] not in range(4):
                raise ValueError("Spin Taylor component index must be between 0 and 3")
        return terms

    @computed_field
    @property
    def r_matrix_7x7(self) -> np.ndarray:
        n = self.r_matrix.shape[0]
        B = np.zeros((n + 1, n + 1))
        B[:n, :n] = self.r_matrix
        B[n, n] = 1
        return B


class ElectrostaticSeparatorSimulationElement(_ElectrostaticSeparatorSimulationElementBase):
    """
    Electrostatic separator simulation element model.
    """

    horizontal_field: Union[float, str] = Field(
        default=0.0, json_schema_extra={"functional": True}
    )
    """Horizontal deflecting electric field [V/m]. Stored verbatim: a number, or
    the name of a functional definition."""

    vertical_field: Union[float, str] = Field(
        default=0.0, json_schema_extra={"functional": True}
    )
    """Vertical deflecting electric field [V/m]. Stored verbatim: a number, or
    the name of a functional definition."""

    tilt: float = 0.0
    """Rotation of the separator about the beam axis [rad]."""


class ACDipoleSimulationElement(_ACDipoleSimulationElementBase):
    """
    AC dipole / tune-exciter simulation element model.
    """

    field_amplitude: Union[float, str] = Field(
        default=0.0, json_schema_extra={"functional": True}
    )
    """Peak kick voltage/amplitude of the exciter. Stored verbatim: a number, or
    the name of a functional definition."""

    frequency: float = 0.0
    """Drive frequency [Hz]."""

    phase: Union[float, str] = Field(
        default=0.0, json_schema_extra={"functional": True}
    )
    """Phase lag [deg]. Stored verbatim: a number, or the name of a functional
    definition."""

    ramp: List[int] = Field(default_factory=lambda: [0, 0, 0, 0])
    """Turn numbers ``[ramp1, ramp2, ramp3, ramp4]`` defining the ramp-up start,
    flat-top start, flat-top end and ramp-down end."""


class WireSimulationElement(_WireSimulationElementBase):
    """
    Compensating wire simulation element model.
    """

    current: float = 0.0
    """Current carried by the wire [A]."""

    interaction_length: float = 0.0
    """Interaction (effective) length of the wire [m]."""

    horizontal_offset: float = 0.0
    """Horizontal offset of the wire from the reference orbit [m]."""

    vertical_offset: float = 0.0
    """Vertical offset of the wire from the reference orbit [m]."""


class BeamBeamSimulationElement(_BeamBeamSimulationElementBase):
    """
    Beam-beam interaction simulation element model.
    """

    charge: float = 1.0
    """Charge of a single particle in the opposing beam, in units of the
    elementary charge (e.g. ``+1`` for protons/positrons, ``-1`` for
    electrons)."""

    n_particles: float = 0.0
    """Number of particles in the opposing (strong) bunch."""

    horizontal_offset: float = 0.0
    """Horizontal offset of the opposing bunch centroid [m]."""

    vertical_offset: float = 0.0
    """Vertical offset of the opposing bunch centroid [m]."""

    horizontal_sigma: float = 0.0
    """Horizontal RMS beam size of the opposing bunch [m]."""

    vertical_sigma: float = 0.0
    """Vertical RMS beam size of the opposing bunch [m]."""

    width: float = 0.0
    """Bunch length of the opposing bunch [m], for the 3D weak-strong model."""


class RFMultipoleSimulationElement(_RFMultipoleSimulationElementBase, FunctionalMixin):
    """
    Thin RF multipole simulation element model.
    """

    frequency: float = 0.0
    """RF frequency [Hz]."""

    phase: Union[float, str] = Field(
        default=0.0, json_schema_extra={"functional": True}
    )
    """Overall phase lag [deg]. Stored verbatim: a number, or the name of a
    functional definition."""

    field_amplitude: Union[float, str] = Field(
        default=0.0, json_schema_extra={"functional": True}
    )
    """Longitudinal voltage [V]. Stored verbatim: a number, or
    the name of a functional definition."""

    knl: List[float] = Field(default_factory=lambda: [0.0] * 5)
    """Integrated normal multipole strengths, order 0 (dipole) to 4 (decapole)."""

    ksl: List[float] = Field(default_factory=lambda: [0.0] * 5)
    """Integrated skew multipole strengths, order 0 (dipole) to 4 (decapole)."""

    pnl: List[float] = Field(default_factory=lambda: [0.0] * 5)
    """Phase of the normal multipole components [deg], order 0 to 4."""

    psl: List[float] = Field(default_factory=lambda: [0.0] * 5)
    """Phase of the skew multipole components [deg], order 0 to 4."""
