"""
Convert a :class:`~laura.translator.utils.fields.FieldMap`'s on-axis 1D samples
into the constructor arguments of RF-Track's field-map elements.

RF-Track has no field-map file format: ``RF_FieldMap_1d`` and
``Static_Magnetic_FieldMap_1d`` take in-memory arrays, so these functions return
argument tuples for ``rftrack_conversion`` rather than writing files. Only 1D
on-axis maps are supported; RF-Track reconstructs the off-axis field assuming
cylindrical symmetry.
"""

import numpy as np
from scipy.signal import hilbert


def _as_str(value) -> str:
    """Normalise h5py ``bytes``/``numpy.bytes_`` string attributes to ``str``."""
    return value.decode("utf-8") if isinstance(value, bytes) else str(value)


def _uniform_mesh(z: np.ndarray, values: np.ndarray) -> tuple:
    """
    Return ``(hz, values)`` on the regular 1D mesh RF-Track requires,
    linearly resampling if the source samples are unevenly spaced.
    """
    z = np.asarray(z, dtype=float)
    dz = np.diff(z)
    hz = float(dz[0])
    if not np.allclose(dz, hz, rtol=1e-6):
        z_uniform = np.linspace(z[0], z[-1], len(z))
        values = np.interp(z_uniform, z, values)
        hz = float(z_uniform[1] - z_uniform[0])
    return hz, np.asarray(values, dtype=float)


def rf_fieldmap_1d_args(
    self, amplitude: float, frequency: float, direction: int = 1
) -> tuple:
    """
    Return the ``(Ez, hz, length, frequency, direction, P_map, P_actual)``
    positional arguments for ``RF_Track.RF_FieldMap_1d`` (manual §4.4.1), built
    from this field's on-axis ``z``/``Ez`` samples.

    Parameters
    ----------
    amplitude: float
        Real peak on-axis field [V/m]. ``Ez`` samples are stored normalized
        to a peak of 1.0, so the caller supplies the scale (e.g. the
        element's ``simulation.field_amplitude``).
    frequency: float
        RF frequency [Hz].
    direction: int
        0 static, +1/-1 forward/backward travelling. Default +1.

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
    return ez * amplitude, hz, -1, float(frequency), direction, 1.0, 1.0


def static_magnetic_fieldmap_1d_args(self, amplitude: float) -> tuple:
    """
    Return the ``(Bz, hz, length)`` positional arguments for
    ``RF_Track.Static_Magnetic_FieldMap_1d`` (manual §4.4.4), built from this
    field's on-axis ``z``/``Bz`` samples.

    Parameters
    ----------
    amplitude: float
        Real peak on-axis field [T]; see :func:`rf_fieldmap_1d_args`.

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


def wakefield_1d_args(self, factor: float, nbins: int = 501) -> tuple:
    """
    Return the ``(W_transv, W_long, hz, nbins)`` arguments for
    ``RF_Track.Wakefield_1d``, built from this wake's ``z``/``Wz``/``Wx`` (or
    ``Wy``) samples.

    RF-Track 2.7.4 takes V/pC/m and V/pC/m/mm, applied per metre of the wake element,
    with the transverse kick of the opposite sign to LAURA's tables.

    Parameters
    ----------
    factor: float
        Cells per metre of the host element, e.g. ``n_cells / length``.
    nbins: int
        Longitudinal bins over the bunch; 501 matches the analytic value.

    Returns
    -------
    tuple
        Ready to splat into ``RF_Track.Wakefield_1d(*args)``.
    """
    z = np.asarray(self.z_values, dtype=float)
    if abs(z[0]) > 1e-12:
        raise ValueError(f"RF-Track wakes start at z = 0, not {z[0]} m")

    def samples(name):
        param = getattr(self, name, None)
        value = getattr(param, "value", None)
        return None if value is None else np.asarray(value.val, dtype=float)

    w_long = samples("Wz")
    # ponytail: one transverse table, Wx else Wy; RF-Track's Wakefield_1d takes one
    w_transv = samples("Wx")
    if w_transv is None:
        w_transv = samples("Wy")
    zeros = np.zeros_like(z)
    hz, w_long = _uniform_mesh(z, zeros if w_long is None else w_long)
    _, w_transv = _uniform_mesh(z, zeros if w_transv is None else w_transv)
    return -w_transv * 1e-15 * factor, w_long * 1e-12 * factor, hz, int(nbins)


def rf_fieldmap_1d_travelling_wave_args_list(
    self, amplitude: float, frequency: float, n_cells: int, direction: int = 1
) -> list:
    """
    Return the ``RF_Track.RF_FieldMap_1d`` constructor arguments, as a
    one-tuple list, for a travelling-wave cavity from an ASTRA-style TWS
    field: the input coupler (``z < start_cell_z``), the periodic core
    (``start_cell_z <= z <= end_cell_z``, tiled) and the output coupler
    (``z > end_cell_z``) on one mesh, made complex as a whole.

    The ``[start_cell_z, end_cell_z]`` window is one periodic block of
    ``mode_denominator`` physical cells (the phase advance returns to
    ``2*pi*mode_numerator`` after that many), so it is tiled
    ``n_cells / mode_denominator`` times with no phase rotation between tiles;
    rotating each tile cancels the net acceleration. The whole map is made
    complex with ``np.conj(scipy.signal.hilbert(...))``:
    separate real couplers would make
    the quadrature field jump at their ends, which grows the emittance.

    Parameters
    ----------
    amplitude: float
        Real peak on-axis field [V/m]; see :func:`rf_fieldmap_1d_args`.
    frequency: float
        RF frequency [Hz].
    n_cells: int
        Total number of physical travelling-wave cells (ASTRA's ``C_numb``/
        LAURA's ``BaseElementTranslator.get_cells()``). Must be a whole
        multiple of ``mode_denominator`` -- ``get_cells()`` already
        guarantees this (rounds down to a multiple of 3).
    direction: int
        Forward (+1, default) or backward (-1) travelling wave.

    Returns
    -------
    list of tuple
        One tuple, ready to splat into ``RF_Track.RF_FieldMap_1d(*args)``.
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
                f"to be set on the field"
            )
    z1, z2 = float(self.start_cell_z), float(self.end_cell_z)
    block_length = z2 - z1
    mode_denominator = float(self.mode_denominator)
    n_cells = int(n_cells)
    n_periods, remainder = divmod(n_cells, int(round(mode_denominator)))
    if remainder:
        raise ValueError(
            f"n_cells={n_cells} is not a whole multiple of "
            f"mode_denominator={mode_denominator!r}"
        )

    z = np.asarray(self.z_values, dtype=float)
    ez = np.asarray(self.Ez.value.val, dtype=float) * amplitude
    core = (z >= z1) & (z <= z2)
    # tiles share their end points: keep each block's last sample only on the last tile
    z_block, ez_block = z[core][:-1], ez[core][:-1]
    shift = (n_periods - 1) * block_length
    z_all = np.concatenate(
        [z[z < z1]]
        + [z_block + i * block_length for i in range(n_periods)]
        + [z[z >= z2] + shift]
    )
    ez_all = np.concatenate([ez[z < z1], np.tile(ez_block, n_periods), ez[z >= z2]])
    # on the core's own spacing, which the couplers are resampled to
    hz = float(np.diff(z[core]).min())
    z_uniform = np.arange(z_all[0], z_all[-1] + hz / 2, hz)
    ez_uniform = np.interp(z_uniform, z_all, ez_all)
    return [
        (np.conj(hilbert(ez_uniform)), hz, -1, float(frequency), direction, 1.0, 1.0)
    ]
