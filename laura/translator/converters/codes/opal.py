from typing import Any, Dict, List, Literal
from warnings import warn

from pydantic import BaseModel, ConfigDict, Field

from laura._compat import DeprecatedMethodAliases

from ...utils.classes import get_grid_size

opal_unsupported = [
    "Laser",
    "Plasma",
    "Decapole",
    "RFDeflectingCavity",
    "Plasma",
    "TwissMatch",
    "MatrixTransform",
    "ActivePlasmaLens",
    "CrabCavity",
    "Wiggler",
]


class OpalHeader(DeprecatedMethodAliases, BaseModel):
    """
    Generic class for generating OPAL namelists

    See `OPAL manual`_ for more details.

    .. _OPAL manual: https://amas.web.psi.ch/opal/Documentation/master/OPAL_Manual.html
    """

    _DEPRECATED_METHOD_ALIASES = {
        "write_Opal": "write_opal",
    }

    model_config = ConfigDict(
        extra="allow",
        arbitrary_types_allowed=True,
        validate_assignment=True,
        populate_by_name=True,
    )

    objectname: str = Field(alias="name")
    """Name of the object, used as a unique identifier in the simulation."""

    objecttype: str = Field(alias="type")
    """Type of the object, which determines its behavior and properties in the simulation."""

    header: str
    """Name of OPAL header"""

    exclude: List[str] = [
        "objectname",
        "objecttype",
        "opaldict",
        "header",
        "exclude",
        "breakstr",
    ]

    opaldict: Dict = {}
    """Dictionary containing values to be written to the header"""

    breakstr: str = (
        "//----------------------------------------------------------------------------"
    )
    """String used for separating headers in the input file"""

    def write_opal(self) -> str:
        """
        Write the text for the Opal namelist based on its attributes.

        Returns
        -------
        str
            Opal-compatible string representing the namelist
        """
        output = f"{self.breakstr}\n// {self.header}\n"
        if self.objecttype != "":
            output += f"{self.header}: {self.objecttype}, \n"
        else:
            output += f"{self.header}, \n"
        for key, val in self.model_dump().items():
            if key not in self.exclude and val is not None:
                if key in self.opaldict:
                    output += f"\t{self.opaldict[key]} = {val},\n"
                elif key == "METHOD":
                    output += 'METHOD = "PARALLEL-T",\n'
                else:
                    output += f"\t{key} = {val},\n"
        output = output[:-2] + ";\n"
        return output


class OpalOption(OpalHeader):
    """
    Class for generating the OPTION namelist for OPAL. See `OPAL manual`_ for more details.
    """

    objectname: str = "option"
    """Name of object"""

    objecttype: str = "OPTION"
    """Type of object"""

    header: str = "OPTION"
    """Name of header"""

    VERSION: str = "202210"
    """OPAL version the input targets, as ``Mmmpp`` (major, minor, patch); mandatory since 1.6.0."""

    AMR: bool = None
    """Enable adaptive mesh refinement (default false)."""

    AMR_REGRID_FREQ: int = None
    """Defines after how many steps an AMR regrid is performed."""

    AMR_YT_DUMP_FREQ: int = None
    """The frequency to dump grid and particle data for AMR."""

    ASCIIDUMP: bool = False
    """Write ASCII instead of HDF5 for collimators, monitors, probes, etc. and global losses."""

    AUTOPHASE: int = 6
    """Auto-phasing accuracy; higher is more accurate, 0 disables auto-phasing."""

    BEAMHALOBOUNDARY: float = None
    """Halo boundary in units of sigma (OPAL-cycl only)."""

    BOUNDPDESTROYFQ: int = None
    """Frequency of deleting particles far from the beam centre (OPAL-cycl only)."""

    CLOTUNEONLY: bool = False
    """Stop after the closed-orbit finder and tune calculation (OPAL-cycl only)."""

    COMPUTEPERCENTILES: bool = False
    """Compute 1-4 sigma percentiles of bunch size and emittance (when over 100 particles)."""

    CSRDUMP: bool = False
    """Dump the CSR field Ez and line density per bend and time step to the data directory."""

    CZERO: bool = False
    """Generate distributions with a centroid of exactly zero."""

    DELPARTFREQ: int = None
    """The frequency to delete particles in OPAL-cycl."""

    DUMPBEAMMATRIX: bool = None
    """If true, the 6-dimensional beam matrix (upper triangle only) is stored in the statistics output file (.stat)."""

    EBDUMP: bool = None
    """Save E and B fields on the particles with each phase-space dump."""

    ENABLEHDF5: bool = None
    """Enable HDF5 read/write (default true)."""

    ENABLEVTK: bool = None
    """Enable VTK output of the geometry voxel mesh (default true)."""

    HALOSHIFT: float = None
    """Constant shift of the halo value (default 0.0)."""

    IDEALIZED: bool = None
    """Use the hard-edge model for path length in OPAL-t."""

    LOGBENDTRAJECTORY: bool = None
    """Save the reference trajectory in each dipole to an ASCII file in data/."""

    MEMORYDUMP: bool = None
    """Write per-core memory use to a .mem file every STATDUMPFREQ steps."""

    MINBINEMITTED: int = None
    """Bins that must be emitted before they are merged into one."""

    MINSTEPFORREBIN: int = None
    """Steps before the bins are merged into one (default 200)."""

    MTSSUBSTEPS: int = None
    """External-field substeps per step for the MTS integrator (OPAL-cycl, default 1)."""

    NLHS: int = None
    """Stored old solutions used to extrapolate the solver start vector (default 1)."""

    NUMBLOCKS: int = None
    """Maximum Krylov-space vectors for ITSOLVER CG/GMRES (default 0)."""

    PSDUMPFREQ: int = None
    """Time steps between phase-space dumps to .h5 (default 10)."""

    PSDUMPEACHTURN: bool = None
    """Dump phase space after each turn (multi-bunch OPAL-cycl, default false)."""

    PSDUMPFRAME: str = None
    """Frame for .h5/.stat phase-space data: GLOBAL, BUNCH_MEAN or REFERENCE (OPAL-cycl only)."""

    REBINFREQ: int = None
    """Time steps between energy-bin updates (multi-bunch OPAL-cycl, default 100)."""

    RECYCLEBLOCKS: int = None
    """Recycle-space vectors for ITSOLVER CG/GMRES (default 0)."""

    REMOTEPARTDEL: float = None
    """Delete particles beyond this many rms sizes from the centroid (default 0.0, none deleted)."""

    REPARTFREQ: int = None
    """Time steps between particle load-balancing repartitions (default 10)."""

    RHODUMP: bool = None
    """Save the scalar charge-density field with each phase-space dump (default false)."""

    RNGTYPE: str = None
    """Random generator: RANDOM (default), HALTON, SOBOL or NIEDERREITER."""

    SCSOLVEFREQ: int = None
    """Steps between space-charge solves for OPAL-cycl LF2/RK4 (default 1; prefer MTS)."""

    SEED: int = None
    """Random seed in [0, 999999999] (default 123456789); -1 seeds from the time."""

    SPTDUMPFREQ: int = None
    """Time steps between single-particle dumps in OPAL-cycl (default 1)."""

    STATDUMPFREQ: int = None
    """Time steps between statistics dumps to .stat (default 10)."""

    def write_opal(self) -> str:
        """
        Write the text for the Opal namelist based on its attributes.

        Returns
        -------
        str
            Opal-compatible string representing the namelist
        """
        output = f"{self.breakstr}\n// {self.header}\n"
        for key, val in self.model_dump().items():
            if key not in self.exclude and val is not None:
                output += f"{self.header}, {key} = {val};\n"
        return output


class OpalDistribution(OpalHeader):
    """
    Class for generating the DISTRIBUTION namelist for OPAL. See `OPAL manual`_ for more details.

    Note that only FROMFILE distributions are currently supported.
    """

    header: str = "DIST"
    """Name of header"""

    objectname: str = "distribution"
    """Name of object"""

    objecttype: str = "DISTRIBUTION"
    """Type of object"""

    TYPE: Literal["FROMFILE"] = "FROMFILE"

    input_particle_definition: str

    emitted: bool = None
    """If True, the bunch is emitted from a cathode and the input's longitudinal
    column is read as emission time. Must match the beam file, or OPAL reads
    times as metres and the bunch collapses to a point."""

    emission_model: str = None
    """Emission model used at the cathode (e.g. ``ASTRA``, ``NONE``,
    ``NONEQUIL``). Only meaningful when :attr:`~emitted` is True."""

    emission_steps: int = None
    """Number of steps used to emit the bunch from the cathode."""

    n_bins: int = None
    """Number of energy bins used while the bunch is being emitted."""

    emission_time: float = None
    """Length of the emission window in seconds. Only meaningful when
    :attr:`~emitted` is True."""

    def model_post_init(self, context: Any, /) -> None:
        self.opaldict = {
            "input_particle_definition": "FNAME",
            "emitted": "EMITTED",
            "emission_model": "EMISSIONMODEL",
            "emission_steps": "EMISSIONSTEPS",
            "n_bins": "NBIN",
            "emission_time": "TEMISSION",
        }

    raw_block: str | None = None
    """Pre-rendered ``DISTRIBUTION`` block written verbatim instead of the
    ``FROMFILE`` form, for bunches OPAL generates natively at the cathode."""

    def write_opal(self) -> str:
        if self.raw_block:
            return f"{self.breakstr}\n{self.raw_block}"
        if not self.input_particle_definition:
            raise ValueError(
                "input_particle_definition must be defined for opal_distribution"
            )
        return super().write_opal()


class OpalFieldSolver(OpalHeader):
    """
    Class for generating the FIELDSOLVER namelist for OPAL. See `OPAL manual`_ for more details.

    Note that the AMR solve is not currently supported; only FFT has really been tested.
    """

    objectname: str = "fieldsolver"
    """Name of object"""

    objecttype: str = "FIELDSOLVER"
    """Type of object"""

    header: str = "FS"
    """Name of header"""

    npart: int
    """Number of particles in the bunch"""

    space_charge_mode: str = "False"
    """Space charge mode"""

    sample_interval: int = 1
    """Divides ``npart`` when sizing the space-charge grid. """

    MIN_PARTICLES_PER_CELL: int = 8
    """Fewest particles per space-charge cell the automatic mesh may produce.
    Eight matches the mesh at which the CLARA benchmark stopped improving (16^3
    at 32768 particles gave 2.07x ASTRA against 2.05x at 32^3, for an eighth of
    the cells) and keeps ``grid**3`` safely below the particle count."""

    grid_size_override: int | tuple[int, int, int] | list | None = None
    """Explicit space-charge mesh size, replacing the heuristic in
    :attr:`~grid_size`. A single value sets all three dimensions; a
    ``(MX, MY, MT)`` triple suits high-aspect bunches such as near the cathode."""

    FSTYPE: Literal["FFT", "FFTPERIODIC", "SAAMG", "P3M", "NONE"] = "FFT"
    """Field solver type: FFT, FFTPERIODIC, SAAMG, P3M or NONE."""

    PARFFTX: bool = True
    """If TRUE, the dimension x is distributed among the processors"""

    PARFFTY: bool = True
    """If TRUE, the dimension y is distributed among the processors"""

    PARFFTT: bool = True
    """If TRUE, the dimension t is distributed among the processors"""

    MX: int | None = None
    """Number of grid points in x specifying rectangular grid"""

    MY: int | None = None
    """Number of grid points in y specifying rectangular grid"""

    MT: int | None = None
    """Number of grid points in t specifying rectangular grid"""

    BCFFTX: str = "open"
    """Boundary condition in x [OPEN] (FFT + AMR_MG only)."""

    BCFFTY: str = "open"
    """Boundary condition in y [OPEN] (FFT + AMR_MG only)."""

    BCFFTZ: str = "open"
    """Boundary condition in z [OPEN,PERIODIC] (FFT + AMR_MG only)."""

    GREENSF: str = "Integrated"
    """Defines the Greens function for the FFT-based solvers (FFT + P3M only)."""

    BBOXINCR: float | None = None
    """Enlargement of the bounding box in %."""

    ITSOLVER: str | None = None
    """Type of iterative solver (SAAMG + AMR_MG only)."""

    RC: float | None = None
    """Defines the cut-off radius in the boosted frame for the P3M solver (P3M only)."""

    ALPHA: float | None = None
    """Interaction splitting parameter for P3M with GREENSF=STANDARD."""

    def model_post_init(self, context: Any, /) -> None:
        self.exclude.extend(
            [
                "npart",
                "space_charge_mode",
                "grids",
                "sample_interval",
                "grid_size_override",
                "MIN_PARTICLES_PER_CELL",
            ]
        )
        if isinstance(self.grid_size_override, (tuple, list)):
            self.MX, self.MY, self.MT = (int(v) for v in self.grid_size_override)
        else:
            self.MX = self.MY = self.MT = self.grid_size
        self.apply_space_charge_mode()

    def apply_space_charge_mode(self) -> None:
        """
        Translate the requested space-charge mode into an OPAL ``FSTYPE``.

        OPAL has no 2D solver, so a ``2D`` request runs the 3D FFT solver with
        a warning. A disabled mode selects ``FSTYPE = NONE``.
        """
        mode = str(self.space_charge_mode or "").strip().lower()
        if not self.space_charge or mode in ("false", "off", "0", "no", "none_"):
            self.FSTYPE = "NONE"
            return
        if mode == "2d":
            warn(
                "OPAL has no 2D/cylindrical space-charge solver; the 2D request "
                "is being run with the 3D FFT solver, which will not reproduce "
                "a 2D code (e.g. ASTRA) exactly."
            )
        self.FSTYPE = "FFT"

    def write_opal(self) -> str:
        if not self.npart:
            raise ValueError("npart must be defined for opal_fieldsolver")
        return super().write_opal()

    @property
    def space_charge(self) -> bool:
        """
        Flag to indicate whether space charge is enabled.

        Returns
        -------
        bool
            True if enabled
        """
        return not (
            self.space_charge_mode == "False"
            or self.space_charge_mode is False
            or self.space_charge_mode is None
            or self.space_charge_mode == "None"
        )

    @property
    def grid_size(self) -> int:
        """
        Get the space-charge mesh size for one dimension.

        Uses :attr:`~grid_size_override` when set; otherwise starts near the cube
        root of the particle count and halves until each cell holds at least
        :attr:`~MIN_PARTICLES_PER_CELL` (OPAL rejects ``npart < grid**3``).

        Returns
        -------
        int
            The number of mesh points per dimension
        """
        if self.grid_size_override:
            return int(self.grid_size_override)
        npart = self.npart / self.sample_interval
        grid = get_grid_size(npart)
        while grid > 4 and grid**3 > npart / self.MIN_PARTICLES_PER_CELL:
            grid //= 2
        return grid


class OpalBeam(OpalHeader):
    """
    Class for generating the BEAM namelist for OPAL. See `OPAL manual`_ for more details.

    Note that only electrons, positrons and protons are currently supported.
    """

    objectname: str = "beam"
    """Name of object"""

    objecttype: str = "BEAM"
    """Type of object"""

    header: str = "BEAM1"
    """Name of header"""

    PARTICLE: Literal["ELECTRON", "POSITRON", "PROTON"]
    """The name of particles in the machine."""

    PC: float
    """Particle momentum in GeV/c."""

    NPART: int
    """Number of particles."""

    CHARGE: int
    """The particle charge expressed in elementary charges."""

    BFREQ: int = 1
    """The bunch frequency in MHz."""

    BCURRENT: float
    """Bunch current [A], ``Q * BFREQ``; with BFREQ = 1 MHz this is the bunch charge in uC."""


class OpalTrack(OpalHeader):
    """
    Class for generating the TRACK namelist for OPAL. See `OPAL manual`_ for more details.
    """

    objectname: str = "track"
    """Name of object"""

    objecttype: str = ""
    """Type of object"""

    header: str = "TRACK"
    """Name of header"""

    LINE: str
    """The label of a preceding LINE (no default)."""

    BEAM: str = "BEAM1"
    """The named BEAM command defines the particle mass, charge and reference momentum.
    This should be the same as the name provided by opal_beam."""

    T0: float = None
    """The initial time [s] of the simulation, its default value is 0."""

    DT: float | str | list | tuple = 1e-12
    """Time step [s] per stage (default 1 ps), paired elementwise with
    :attr:`~ZSTOP` so a run can step finely near the cathode and coarsely after."""

    MAXSTEPS: int = None
    """Maximum time steps per stage (default one stage of 10)."""

    ZSTART: float = None
    """Initial reference-particle position along the trajectory [m] (default 0.0)."""

    ZSTOP: float | str | list | tuple
    """Stage end positions [m]; tracking moves to the next DT/MAXSTEPS/ZSTOP set when one is reached, and stops after the last."""

    TIMEINTEGRATOR: Literal["RK4", "LF2", "MTS"] = None
    """Time integrator: RK4, LF2 or MTS (OPAL-cycl only)."""

    ZSTOP_STAGES: list | tuple | None = None
    """Intermediate z-positions [m] at which :attr:`~DT` moves to its next value.
    Kept apart from :attr:`~ZSTOP`, which the section translator resets to the
    line end, and folded into the ``ZSTOP`` array on write."""

    def model_post_init(self, context: Any, /) -> None:
        self.exclude.append("ZSTOP_STAGES")

    def write_opal(self) -> str:
        # OPAL takes DT/ZSTOP as arrays; a scalar is just the one-stage case. The
        # final ZSTOP is nudged past the end of the line so the last element is
        # tracked through rather than stopped on.
        if isinstance(self.DT, (list, tuple)):
            self.DT = "{" + ", ".join(str(dt) for dt in self.DT) + "}"
        else:
            self.DT = str(self.DT)
        stops = list(self.ZSTOP_STAGES or []) + [self.ZSTOP + 1e-1]
        self.ZSTOP = "{" + ", ".join(str(z) for z in stops) + "}"
        return super().write_opal()


class OpalRun(OpalHeader):
    """
    Class for generating the RUN namelist for OPAL. See `OPAL manual`_ for more details.

    Note that only OPAL-t is currently supported.
    """

    objectname: str = "run"
    """Name of object"""

    objecttype: str = ""
    """Type of object"""

    header: str = "RUN"
    """Name of header"""

    METHOD: str = "PARALLEL-T"
    """Tracking method: ``PARALLEL-T`` (OPAL-t) or ``CYCLOTRON-T`` (OPAL-cycl)."""

    FIELDSOLVER: str = "FS"
    """The field solver to be used. This should be the same as the name provided by opal_fieldsolver"""

    DISTRIBUTION: str = "DIST"
    """The particle distribution to be used. This should be the same as the name provided by opal_distribution"""

    BEAM: str = "BEAM1"
    """The particle beam to be used. This should be the same as the name provided by opal_beam"""

    TURNS: int = 1
    """Turns to track (default 1); in OPAL-cycl, the number of bunches injected."""

    MBMODE: Literal["AUTO", "FORCE"] = None
    """Multi-bunch mode, AUTO or FORCE (OPAL-cycl only)."""

    PARAMB: float = None
    """When AUTO multi-bunch mode switches from single to multiple bunches (default 5.0, OPAL-cycl)."""

    MB_BINNING: Literal["GAMMA_BINNING", "BUNCH_BINNING"] = None
    """Multi-bunch energy binning: GAMMA_BINNING (default) or BUNCH_BINNING (OPAL-cycl)."""

    MB_ETA: float = None
    """Binning scale for GAMMA_BINNING (default 0.01, OPAL-cycl)."""

    TRACKBACK: bool = None
    """Track backward in time from ZSTART through the ZSTOP thresholds (OPAL-t, default false)."""


from laura._compat import deprecated_aliases  # noqa: E402

__getattr__ = deprecated_aliases(
    __name__,
    globals(),
    {
        "opal_beam": "OpalBeam",
        "opal_distribution": "OpalDistribution",
        "opal_fieldsolver": "OpalFieldSolver",
        "opal_header": "OpalHeader",
        "opal_option": "OpalOption",
        "opal_run": "OpalRun",
        "opal_track": "OpalTrack",
    },
)
