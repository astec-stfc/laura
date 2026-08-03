from pydantic import (
    PositiveInt,
    PositiveFloat,
    SerializeAsAny,
    computed_field,
    field_validator,
    Field
)
from typing import Literal, Any, Dict, List, Union
from .baseModels import IgnoreExtra
import numpy as np
import re


class ApertureElement(IgnoreExtra):
    """Physical info model."""

    number_of_elements: int | None = None
    """Number of aperture elements"""

    horizontal_size: float = 0.0
    """Horizontal aperture size [m]"""

    vertical_size: float = 0.0
    """Vertical aperture size [m]"""

    shape: (
        Literal["elliptical", "planar", "circular", "rectangular", "scraper"] | None
    ) = None
    """Aperture shape"""

    radius: float | None = None
    """Radius of aperture"""

    negative_extent: float | None = None
    """Longitudinal start position of an aperture"""

    positive_extent: float | None = None
    """Longitudinal end position of an aperture"""


class SimulationElement(IgnoreExtra):
    """
    Simulation element model.
    """

    field_definition: SerializeAsAny[Any] = None
    """String pointing to field definition"""

    wakefield_definition: SerializeAsAny[Any] = None
    """String pointing to wakefield definition"""

    field_reference_position: Literal["start", "middle", "end"] | None = None
    """Reference position for field file"""

    scale_field: int | float | bool = False
    """Flag indicating whether to scale the field from the field file"""


class MagnetSimulationElement(SimulationElement):
    """
    Magnet simulation element model.
    """

    n_kicks: int = 4
    """Number of kicks for tracking through the quad"""

    n_slices: int = 4
    """Number of kicks for tracking through the quad"""

    smooth: int | float | None = 2
    """Number of points to smooth the field map [ASTRA only]"""

    edge_field_integral: float = 0.5
    """Edge field integral for fringes"""

    edge1_effects: int = 1
    """Flag to indicate whether entrance edge effects are included"""

    edge2_effects: int = 1
    """Flag to indicate whether exit edge effects are included"""

    sr_enable: bool = True
    """Flag to enable SR calculations"""

    integration_order: int = 4
    """Runge-Kutta integration order"""

    nonlinear: int = 1
    """Flag to indicate whether to perform nonlinear calculations"""

    smoothing_half_width: int = 1
    """Half-width for smoothing"""

    edge_order: int = 2
    """Matrix order for edges"""

    csr_bins: int = 100
    """Number of CSR bins"""

    deltaL: float = 0.0
    """Delta length"""

    csr_enable: bool = True
    """Flag to indicate whether CSR is enabled"""

    isr_enable: bool = True
    """Flag to indicate whether ISR is enabled"""

    field_amplitude: Union[float, str] = Field(
        default=0.0, json_schema_extra={"functional": True}
    )
    """Field amplitude for the magnet simulation. Stored verbatim: a number or a
    string naming a functional definition (resolve via ``resolved("field_amplitude")``)."""


class DriftSimulationElement(SimulationElement):
    """
    Drift simulation element model.
    """

    lsc_interpolate: int = 1
    """Flag to allow for interpolation of computed longitudinal space charge wake.
    See `Elegant manual LSC drift`_
    
    .. _Elegant manual LSC drift: https://ops.aps.anl.gov/manuals/elegant_latest/elegantsu168.html#x179-18000010.58
    """

    csr_enable: bool = True
    """Enable CSR drift calculations"""

    lsc_enable: bool = True
    """Enable LSC drift calculations"""

    use_stupakov: int = 1
    """Use Stupakov formula; see `Elegant manual LSC drift`_"""

    csrdz: PositiveFloat = 0.01
    """Step size for CSR calculations"""

    lsc_bins: PositiveInt = 20
    """Number of bins for LSC calculations"""

    lsc_high_frequency_cutoff_start: float | None = None
    """Spatial frequency at which smoothing filter begins. If not positive, no frequency filter smoothing is done. 
    See `Elegant manual LSC drift`_
    """

    lsc_high_frequency_cutoff_end: float | None = None
    """Spatial frequency at which smoothing filter is 0. See `Elegant manual LSC drift`_"""

    lsc_low_frequency_cutoff_start: float | None = None
    """Highest spatial frequency at which low-frequency cutoff filter is zero. See `Elegant manual LSC drift`_"""

    lsc_low_frequency_cutoff_end: float | None = None
    """Lowest spatial frequency at which low-frequency cutoff filter is 1. See `Elegant manual LSC drift`_"""


class DiagnosticSimulationElement(SimulationElement):
    output_filename: str | None = None
    """Output filename for the diagnostic"""


class PlasmaSimulationElement(SimulationElement):
    """
    Plasma simulation element model.
    """

    wakefield_model: Literal["quasistatic_2d"] | None = None
    """Wakefield model (Wake-T); possible values: 
    'blowout', 'custom_blowout', 'focusing_blowout', 'cold_fluid_1d' and 'quasistatic_2d'; if None, no
    wakefields are computed.
    # TODO add more of these and check which we support
    """

    required_attrs: Dict = {
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

    bunch_pusher: Literal["rk4", "boris"] = "boris"
    """Pusher used to evolve particles in time in the plasma [Wake-T]; possible values:
    'rk4', 'boris'; see `Wake-T pusher`_

    .. _Wake-T pusher: https://github.com/AngelFP/Wake-T/tree/dev/wake_t/particles/push
    """

    dt_bunch: float | Literal["auto"] = "auto"
    """The time step for evolving the particle bunches. If 'auto', set to dt=T/(10*2*pi) with T
    the plasma period.
    """

    n_out: int = 1
    """Number of times to dump the particle distribution during the plasma stage."""

    min_longitudinal_position: float = 0
    """Minimum longitudinal position [metres] up to which
    plasma wakefield will be calculated. Converted to boosted co-ordinates for Wake-T during 
    simulation setup."""

    max_longitudinal_position: float = 0
    """Maximum longitudinal position [metres] up to which
        plasma wakefield will be calculated. Converted to boosted co-ordinates for Wake-T during
        simulation setup."""

    n_longitudinal: int = 0
    """Number of grid points in the longitudinal direction"""

    n_radial: int = 0
    """Number of grid points in the radial direction"""

    plasma_particles_per_cell: int = 2
    """Number of plasma particles per cell; 2 by default"""

    r_max: float = 0
    """Radial extent of the simulation box [meters]"""

    r_max_plasma: float | None = None
    """Maximum radial extension of the plasma column; set to `r_max` if None"""

    dz_fields: float | None = None
    """Determines how often the plasma wakefields should be updated; 
        `max_longitudinal_position`-`min_longitudinal_position` by default"""

    plasma_pusher: Literal["rk4", "boris"] = "boris"
    """Pusher used to evolve the plasma in time [Wake-T]; possible values:
    'rk4', 'boris'; see `Wake-T pusher`_

    .. _Wake-T pusher: https://github.com/AngelFP/Wake-T/tree/dev/wake_t/particles/push
    """


class RFCavitySimulationElement(SimulationElement):
    """
    RF cavity simulation element model.
    """

    field_amplitude: Union[float, str] = Field(
        default=0.0, json_schema_extra={"functional": True}
    )
    """Cavity field amplitude. Stored verbatim: a number or a string naming a
    functional definition (resolve via ``resolved("field_amplitude")``)."""

    t_column: str | None = None
    """t column in wake file"""

    z_column: str | None = None
    """z column in wake file"""

    wx_column: str | None = None
    """Wx column in wake file"""

    wy_column: str | None = None
    """Wy column in wake file"""

    wz_column: str | None = None
    """Wz column in wake file"""

    change_p0: int = 1
    """Flag to indicate whether cavity is changing momentum"""

    n_kicks: int = 0
    """Number of cavity kicks to apply"""

    end1_focus: int = 1
    """Apply entrance focusing"""

    end2_focus: int = 1
    """Apply exit focusing"""

    body_focus_model: str = "SRS"
    """Cavity focusing model"""

    lsc_bins: int = 100
    """Number of longitudinal space charge bins"""

    current_bins: int = 0
    """Number of current bins"""

    interpolate_current_bins: int = 1
    """Flag to indicate whether to interpolate during current histogram"""

    smooth_current_bins: int = 1
    """Flag to indicate whether to smooth the current histogram"""

    smooth: int | None = None
    """Smoothing parameter"""

    ez_peak: float | None = None
    """Peak longitudinal electric field"""

    field_file_name: str | None = None
    """Cavity field file name"""

    wakefile: str | None = None
    """Name of wake file"""

    zwakefile: str | None = None
    """Name of longitudinal wake file"""

    trwakefile: str | None = None
    """Name of transverse wake file"""


class WakefieldSimulationElement(SimulationElement):
    """
    Wakefield simulation element model.
    """

    allow_long_beam: bool = True
    """Flag to indicate whether beams longer than the wakefield are allowed."""

    bunched_beam: bool = False
    """Flag to indicate whether a bunched beam is to be used."""

    change_momentum: bool = True
    """Flag to indicate whether the wakefield can change the central momentum of the bunch."""

    factor: float = 1
    """
    Wake scaling factor.
    #TODO check if redundant based on scale_kick?
    """

    interpolate: bool = True
    """Flag to indicate whether to interpolate points in wake file."""

    scale_kick: float = 1
    """Factor by which to scale wake kicks."""

    t_column: str | None = None
    """t column in wake file"""

    z_column: str | None = None
    """z column in wake file"""

    wx_column: str | None = None
    """Wx column in wake file"""

    wy_column: str | None = None
    """Wy column in wake file"""

    wz_column: str | None = None
    """Wz column in wake file"""

    scale_field_ex: float = 0.0
    """x-component of the longitudinal direction vector."""

    scale_field_ey: float = 0.0
    """y-component of the longitudinal direction vector."""

    scale_field_ez: float = 1.0
    """z-component of the longitudinal direction vector."""

    scale_field_hx: float = 1.0
    """x-component of the horizontal direction vector."""

    scale_field_hy: float = 0.0
    """y-component of the horizontal direction vector."""

    scale_field_hz: float = 0.0
    """z-component of the horizontal direction vector."""

    equal_grid: float = 0.66
    """If 1.0 an equidistant grid is set up, if 0.0 a grid with equal charge per grid cell is
    employed. Values between 1.0 and 0.0 result in intermediate binning based on
    a linear combination of the two methods."""

    interpolation_method: int = 2
    """Interpolation method for ASTRA: 0 = rectangular, 1 = triangular, 2 = Gaussian."""
    smooth: float = 0.25
    """Smoothing parameter for Gaussian interpolation."""

    subbins: int = 10
    """Sub binning parameter."""


class TwissMatchSimulationElement(IgnoreExtra):
    beta_x: float
    """Horizontal beta"""

    beta_y: float
    """Vertical beta"""

    alpha_x: float
    """Horizontal alpha"""

    alpha_y: float
    """Vertical alpha"""

    eta_x: float = 0.0
    """Horizontal dispersion"""

    eta_y: float = 0.0
    """Vertical dispersion"""

    eta_xp: float = 0.0
    """Horizontal dispersion derivative"""

    eta_yp: float = 0.0
    """Vertical dispersion derivative"""

    from_beam: bool = True
    """If `True`, compute transformation from tracked beam properties instead of Twiss parameters"""

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


class MatrixTransformSimulationElement(IgnoreExtra):
    c_matrix: np.ndarray = Field(default_factory=lambda: np.zeros(6))
    """C-matrix for the element (0th order transformation matrix)."""

    r_matrix: np.ndarray = Field(default_factory=lambda: np.eye(6))
    """R-matrix for the element (1st order transformation matrix)."""

    t_matrix: np.ndarray = Field(default_factory=lambda: np.zeros((6, 6, 6)))
    """T-matrix for the element (2nd order transformation matrix)."""

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

    @computed_field
    @property
    def r_matrix_7x7(self) -> np.ndarray:
        n = self.r_matrix.shape[0]
        B = np.zeros((n + 1, n + 1))
        B[:n, :n] = self.r_matrix
        B[n, n] = 1
        return B


class ElectrostaticSeparatorSimulationElement(IgnoreExtra):
    """
    Electrostatic separator simulation element model.

    See the MAD-X ``ELSEPARATOR`` element (no equivalent element exists in
    ELEGANT or Xsuite).
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


class ACDipoleSimulationElement(IgnoreExtra):
    """
    AC dipole / tune-exciter simulation element model.

    See the MAD-X ``HACDIPOLE``/``VACDIPOLE`` elements and the Xsuite
    ``ACDipole`` element.
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
    flat-top start, flat-top end and ramp-down end (see the MAD-X ``RAMP1..4``
    parameters and the Xsuite ``ACDipole.ramp``)."""


class WireSimulationElement(IgnoreExtra):
    """
    Compensating wire simulation element model.

    See the MAD-X ``WIRE`` element and the Xsuite ``Wire`` element. The
    physical length of the wire is the element's own ``physical.length``
    (MAD-X ``L``/Xsuite ``L_phy``).
    """

    current: float = 0.0
    """Current carried by the wire [A]."""

    interaction_length: float = 0.0
    """Interaction (effective) length of the wire [m] (MAD-X ``L_INT``, Xsuite
    ``L_int``)."""

    horizontal_offset: float = 0.0
    """Horizontal offset of the wire from the reference orbit [m] (``XMA``)."""

    vertical_offset: float = 0.0
    """Vertical offset of the wire from the reference orbit [m] (``YMA``)."""


class BeamBeamSimulationElement(IgnoreExtra):
    """
    Beam-beam interaction simulation element model.

    See the MAD-X ``BEAMBEAM`` element (weak-strong kick from an opposing
    bunch).
    """

    charge: float = 1.0
    """Charge of a single particle in the opposing beam, in units of the
    elementary charge (e.g. ``+1`` for protons/positrons, ``-1`` for
    electrons) -- matches Xsuite's ``other_beam_q0``. MAD-X's ``CHARGE`` and
    ELEGANT's ``CHARGE`` (in Coulombs, ``= n_particles * charge * e``) are
    both derived from this."""

    n_particles: float = 0.0
    """Number of particles in the opposing (strong) bunch (MAD-X ``NPART``)."""

    horizontal_offset: float = 0.0
    """Horizontal offset of the opposing bunch centroid [m] (``XMA``)."""

    vertical_offset: float = 0.0
    """Vertical offset of the opposing bunch centroid [m] (``YMA``)."""

    horizontal_sigma: float = 0.0
    """Horizontal RMS beam size of the opposing bunch [m] (``SIGX``)."""

    vertical_sigma: float = 0.0
    """Vertical RMS beam size of the opposing bunch [m] (``SIGY``)."""

    width: float = 0.0
    """Bunch length of the opposing bunch [m], for the 3D weak-strong model
    (``WIDTH``)."""


class RFMultipoleSimulationElement(IgnoreExtra):
    """
    Thin RF multipole simulation element model.

    See the MAD-X ``RFMULTIPOLE`` element and the Xsuite ``RFMultipole``
    element -- a zero-length multipole kick whose strength oscillates at an RF
    frequency, up to 5th order (dipole through decapole).
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
    """Longitudinal voltage [V] (MAD-X ``VOLT``). Stored verbatim: a number, or
    the name of a functional definition."""

    knl: List[float] = Field(default_factory=lambda: [0.0] * 5)
    """Integrated normal multipole strengths, order 0 (dipole) to 4 (decapole)."""

    ksl: List[float] = Field(default_factory=lambda: [0.0] * 5)
    """Integrated skew multipole strengths, order 0 (dipole) to 4 (decapole)."""

    pnl: List[float] = Field(default_factory=lambda: [0.0] * 5)
    """Phase of the normal multipole components [deg], order 0 to 4."""

    psl: List[float] = Field(default_factory=lambda: [0.0] * 5)
    """Phase of the skew multipole components [deg], order 0 to 4."""
