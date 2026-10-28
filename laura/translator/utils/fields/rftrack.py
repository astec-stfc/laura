"""
Convert a :class:`~laura.translator.utils.fields.FieldMap`'s on-axis 1D samples
into the constructor arguments of RF-Track's field-map elements
(RF_Track_reference_manual.pdf §4.4).

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
    Return ``(hz, values)`` on the regular 1D mesh RF-Track requires (manual
    §4.4), linearly resampling if the source samples are unevenly spaced.
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


def rf_fieldmap_1d_travelling_wave_args_list(
    self, amplitude: float, frequency: float, n_cells: int, direction: int = 1
) -> list:
    """
    Return 1-3 ``RF_Track.RF_FieldMap_1d`` constructor-argument tuples for a
    travelling-wave cavity from an ASTRA-style TWS field: a real input coupler
    (``z < start_cell_z``), a complex travelling-wave core
    (``start_cell_z <= z <= end_cell_z``, tiled) and a real output coupler
    (``z > end_cell_z``), omitting empty couplers (manual §4.3.6). The caller
    applies the same ``set_phid`` to every element; the manual's +90 degree
    core offset applies only to ``SW_Structure``/``TW_Structure``.

    The ``[start_cell_z, end_cell_z]`` window is one periodic block of
    ``mode_denominator`` physical cells (the phase advance returns to
    ``2*pi*mode_numerator`` after that many), so it is tiled
    ``n_cells / mode_denominator`` times with no phase rotation between tiles;
    rotating each tile cancels the net acceleration. The tiled core is made
    complex with ``np.conj(scipy.signal.hilbert(...))``; the unconjugated
    analytic signal gives near-zero gain.

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
    args_list.append(
        (ez_core_complex, hz_core, -1, float(frequency), direction, 1.0, 1.0)
    )

    if len(z_out) > 1:
        hz_out, ez_out_u = _uniform_mesh(z_out, ez_out)
        args_list.append((ez_out_u, hz_out, -1, float(frequency), direction, 1.0, 1.0))

    return args_list
