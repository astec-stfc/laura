"""
Convert a :class:`~laura.translator.utils.fields.field` object's on-axis 1D
samples into the plain-array form RF-Track's field-map constructors need
(RF_Track_reference_manual.pdf §4.4).

Unlike ASTRA/GPT/OPAL (``astra.py``/``gdf.py``/``opal.py`` in this package),
RF-Track has no field-map *file* format of its own -- ``RF_Track.RF_FieldMap_1d``
/``Static_Magnetic_FieldMap_1d`` are built directly from in-memory numpy arrays
-- so, unlike those modules, this one has no ``write_rftrack_field_file``: it
only hands back a plain constructor-args tuple. The caller
(``laura.translator.conversion_rules.codes.rftrack_conversion``) passes that
straight into the real ``RF_Track`` constructor and also reuses it, via that
module's own ``_format_args``, to render the equivalent Python source line for
exported standalone scripts -- mirroring every other builder in that file
(``_cavity_args``/``build_pillbox_cavity``/``repr_pillbox_cavity``, etc).

Only 1D on-axis field maps are supported -- the only field-map data LAURA's
generic element model actually stores (mirrors ASTRA/GPT's own on-axis
convention; RF-Track itself reconstructs the off-axis field assuming
cylindrical symmetry from just this on-axis data, manual §4.4). Standing-wave
cavities and static-magnetic elements (:func:`rf_fieldmap_1d_args`/
:func:`static_magnetic_fieldmap_1d_args`) use the on-axis samples directly.

Travelling-wave cavities (:func:`rf_fieldmap_1d_travelling_wave_args_list`)
need a genuinely complex on-axis array for the core (manual §4.4.1: "can be
either complex numbers (travelling waves) or real numbers (standing
waves)"), which an ASTRA TWS field file doesn't store directly -- its
``start_cell_z``/``end_cell_z`` window is not one physical cell but one full
*periodic repeat block* (``mode_denominator`` physical cells, since after
that many cells the field's own phase advance, ``mode_denominator *
2*pi*mode_numerator/mode_denominator = 2*pi*mode_numerator``, returns to the
start -- verified against CLARA's real L01/``TWS_S-DL.hdf5``:
``end_cell_z - start_cell_z`` = 3 physical cells worth of length, and the
on-axis data genuinely oscillates in sign across that span). Getting this
wrong is not a cosmetic inaccuracy: an earlier version of this function
replicated that span ``n_cells`` times with an extra ``exp(i*i*dphi)``
rotation between every replica (as if each one were a single physical cell);
those spurious phases summed to *exactly* zero every ``mode_denominator``
replicas -- and ``get_cells()`` always returns a multiple of
``mode_denominator`` cells -- so real CLARA L01 tracking gave *exactly zero*
net acceleration.

:func:`rf_fieldmap_1d_travelling_wave_args_list` tiles the real periodic
block ``n_cells / mode_denominator`` times with NO extra rotation between
tiles, then recovers the complex forward-travelling-wave array via the
conjugated analytic-signal construction, ``np.conj(scipy.signal.hilbert(...)
)`` -- empirically verified against the real package to give the physically
expected gain (the unconjugated form gives near-zero). The samples outside
``[start_cell_z, end_cell_z]`` are the structure's real input/output
couplers and are kept as separate, real ``RF_FieldMap_1d`` args rather than
being folded into the Hilbert-transformed core -- matching manual §4.3.6's
own recommendation to chain a real entrance coupler, the travelling-wave
core, and a real exit coupler for a genuine TW structure. All returned
elements should get the same ``set_phid`` applied (empirically verified;
manual §4.3.6's own +90 degree core-vs-coupler offset is specific to the
analytic ``SW_Structure``/``TW_Structure`` element pair, not
``RF_FieldMap_1d``). ``rftrack_conversion.build_tw_structure`` (RF-Track's
analytic, single-harmonic ``TW_Structure`` model) remains the fallback when a
field map isn't available.
"""
import numpy as np
from scipy.signal import hilbert


def _as_str(value) -> str:
    """h5py string attributes sometimes come back as ``bytes``/``numpy.bytes_``
    rather than ``str`` -- normalise before comparing (same pitfall
    ``astra.generate_astra_field_data`` already guards against)."""
    return value.decode("utf-8") if isinstance(value, bytes) else str(value)


def _uniform_mesh(z: np.ndarray, values: np.ndarray) -> tuple:
    """
    Return ``(hz, values)`` for RF-Track's fixed-spacing 1D mesh convention
    (manual §4.4: "All field maps accept 3D Cartesian mesh grids with regular
    spacing"). Resamples onto a uniform grid via linear interpolation if the
    source samples are not already evenly spaced -- real field-map files are
    not guaranteed to be, unlike RF-Track's own requirement.
    """
    z = np.asarray(z, dtype=float)
    dz = np.diff(z)
    hz = float(dz[0])
    if not np.allclose(dz, hz, rtol=1e-6):
        z_uniform = np.linspace(z[0], z[-1], len(z))
        values = np.interp(z_uniform, z, values)
        hz = float(z_uniform[1] - z_uniform[0])
    return hz, np.asarray(values, dtype=float)


def rf_fieldmap_1d_args(self, amplitude: float, frequency: float, direction: int = 1) -> tuple:
    """
    Return the ``(Ez, hz, length, frequency, direction, P_map, P_actual)``
    positional arguments for ``RF_Track.RF_FieldMap_1d`` (manual §4.4.1), built
    from this field's on-axis ``z``/``Ez`` samples.

    Parameters
    ----------
    amplitude: float
        Real peak on-axis field [V/m]. This field's own ``Ez`` samples are
        stored normalized to a peak of 1.0 (SIMBA/LAURA's own field-file
        convention -- see ``astra.read_astra_field_file``), so the caller must
        supply the true scale (e.g. the owning element's
        ``simulation.field_amplitude``); the field object itself has no
        concept of the element that references it.
    frequency: float
        RF frequency [Hz].
    direction: int
        0 static, +1/-1 forward/backward travelling; standing-wave fields give
        identical results for either sign (manual §4.4.1 note). Default +1.

    Returns
    -------
    tuple
        Ready to splat into ``RF_Track.RF_FieldMap_1d(*args)``.
    """
    field_type = _as_str(self.field_type)
    cavity_type = _as_str(self.cavity_type)
    if field_type != "1DElectroDynamic" or cavity_type != "StandingWave":
        raise ValueError(
            f"rf_fieldmap_1d_args requires a 1DElectroDynamic/StandingWave "
            f"field (got field_type={field_type!r}, cavity_type={cavity_type!r})"
        )
    hz, ez = _uniform_mesh(self.z_values, self.Ez.value.val)
    # length=-1 -> RF-Track takes the field map's own length (manual §4.4.1),
    # self-consistent with `hz` by construction; avoids a separate rounding-
    # prone z[-1]-z[0] computation.
    return ez * amplitude, hz, -1, float(frequency), direction, 1.0, 1.0


def static_magnetic_fieldmap_1d_args(self, amplitude: float) -> tuple:
    """
    Return the ``(Bz, hz, length)`` positional arguments for
    ``RF_Track.Static_Magnetic_FieldMap_1d`` (manual §4.4.4), built from this
    field's on-axis ``z``/``Bz`` samples.

    Parameters
    ----------
    amplitude: float
        Real peak on-axis field [T] -- see :func:`rf_fieldmap_1d_args` for why
        this can't be read from the field object itself.

    Returns
    -------
    tuple
        Ready to splat into ``RF_Track.Static_Magnetic_FieldMap_1d(*args)``.
    """
    field_type = _as_str(self.field_type)
    if field_type != "1DMagnetoStatic":
        raise ValueError(
            f"static_magnetic_fieldmap_1d_args requires a 1DMagnetoStatic "
            f"field (got field_type={field_type!r})"
        )
    hz, bz = _uniform_mesh(self.z_values, self.Bz.value.val)
    return bz * amplitude, hz, -1


def rf_fieldmap_1d_travelling_wave_args_list(
    self, amplitude: float, frequency: float, n_cells: int, direction: int = 1
) -> list:
    """
    Return a list of 1-3 ``RF_Track.RF_FieldMap_1d`` constructor-arg tuples
    for a travelling-wave cavity built from an ASTRA-style TWS field: a real
    (standing-wave-style) input coupler (``z < start_cell_z``), a complex
    travelling-wave periodic core (``start_cell_z <= z <= end_cell_z``,
    tiled), and a real output coupler (``z > end_cell_z``) -- in that order,
    omitting an empty coupler region. Mirrors manual §4.3.6's own
    recommendation to chain a real entrance coupler, a travelling-wave core,
    and a real exit coupler for a genuine TW structure
    (``SW_Structure``+``TW_Structure``+``SW_Structure``); the caller
    (``rftrack_conversion.build_tw_fieldmap``) appends these into one
    sub-``Lattice``, applying the same ``set_phid`` to every element --
    empirically verified against real CLARA L01 data that this (not the
    manual's own +90 degree core offset, which is specific to the analytic
    ``SW_Structure``/``TW_Structure`` element pair) gives the physically
    correct ~30 MeV/c gain for RF_FieldMap_1d.

    The core spans ``mode_denominator`` physical cells (after which the
    field's own phase advance, ``mode_denominator *
    2*pi*mode_numerator/mode_denominator = 2*pi*mode_numerator``, returns to
    its start -- verified against real ASTRA/CLARA field-map files, whose
    on-axis data genuinely oscillates in sign across that span), so it's
    tiled ``n_cells / mode_denominator`` times with every tile identical (no
    extra phase rotation between tiles -- an earlier version that rotated by
    ``exp(i*i*dphi)`` per tile summed to exactly zero net acceleration every
    ``mode_denominator`` replicas, and ``get_cells()`` always returns a
    multiple of ``mode_denominator``).

    The tiled core is converted from a real, physically-oscillating array to
    the complex forward-travelling-wave field RF-Track needs via the
    conjugated analytic-signal (Hilbert transform) construction --
    ``np.conj(scipy.signal.hilbert(...))`` -- empirically verified against
    the real package (with ``direction=1``) to give the expected ~42 MeV/c
    gain for a clean synthetic case and ~30 MeV/c for real CLARA L01 data at
    its actual operating phase (the unconjugated version gives near-zero
    gain).

    Parameters
    ----------
    amplitude: float
        Real peak on-axis field [V/m] -- see :func:`rf_fieldmap_1d_args` for
        why this can't come from the field object itself.
    frequency: float
        RF frequency [Hz].
    n_cells: int
        Total number of physical travelling-wave cells (ASTRA's ``C_numb``/
        LAURA's ``BaseElementTranslator.get_cells()``). Must be a whole
        multiple of ``mode_denominator`` -- ``get_cells()`` already
        guarantees this (rounds down to a multiple of 3).
    direction: int
        Forward (+1, default) or backward (-1) travelling wave for the core
        only; the couplers are real and give identical results for either
        sign (manual §4.4.1 note).

    Returns
    -------
    list of tuple
        Each ready to splat into ``RF_Track.RF_FieldMap_1d(*args)``, in
        element order (input coupler, core, output coupler).
    """
    field_type = _as_str(self.field_type)
    cavity_type = _as_str(self.cavity_type)
    if field_type != "1DElectroDynamic" or cavity_type != "TravellingWave":
        raise ValueError(
            f"rf_fieldmap_1d_travelling_wave_args_list requires a "
            f"1DElectroDynamic/TravellingWave field (got "
            f"field_type={field_type!r}, cavity_type={cavity_type!r})"
        )
    for attr in ("start_cell_z", "end_cell_z", "mode_numerator", "mode_denominator"):
        if getattr(self, attr, None) is None:
            raise ValueError(
                f"rf_fieldmap_1d_travelling_wave_args_list requires {attr!r} "
                f"to be set on the field (from the ASTRA TWS file's own "
                f"header line)"
            )
    z1, z2 = float(self.start_cell_z), float(self.end_cell_z)
    block_length = z2 - z1
    mode_denominator = float(self.mode_denominator)
    n_cells = int(n_cells)
    n_periods, remainder = divmod(n_cells, int(round(mode_denominator)))
    if remainder:
        raise ValueError(
            f"n_cells={n_cells} is not a whole multiple of "
            f"mode_denominator={mode_denominator!r} (the field's periodic "
            f"repeat block spans mode_denominator physical cells, so n_cells "
            f"must divide evenly by it)"
        )

    z = np.asarray(self.z_values, dtype=float)
    ez = np.asarray(self.Ez.value.val, dtype=float) * amplitude
    z_in, ez_in = z[z < z1], ez[z < z1]
    z_core, ez_core = z[(z >= z1) & (z <= z2)], ez[(z >= z1) & (z <= z2)]
    z_out, ez_out = z[z > z2], ez[z > z2]

    args_list = []
    if len(z_in) > 1:
        hz_in, ez_in_u = _uniform_mesh(z_in, ez_in)
        args_list.append((ez_in_u, hz_in, -1, float(frequency), direction, 1.0, 1.0))

    z_core_tiled = np.concatenate([z_core + i * block_length for i in range(n_periods)])
    ez_core_tiled = np.tile(ez_core, n_periods)
    hz_core, ez_core_u = _uniform_mesh(z_core_tiled, ez_core_tiled)
    ez_core_complex = np.conj(hilbert(ez_core_u))
    args_list.append((ez_core_complex, hz_core, -1, float(frequency), direction, 1.0, 1.0))

    if len(z_out) > 1:
        hz_out, ez_out_u = _uniform_mesh(z_out, ez_out)
        args_list.append((ez_out_u, hz_out, -1, float(frequency), direction, 1.0, 1.0))

    return args_list
