"""
Per-``hardware_type`` builders converting a LAURA element translator into an
RF-Track Python object.

RF-Track constructors take positional arguments with per-type signatures (see
``RFTrack/RFTrack_API_notes.md``), so each entry is a builder function rather
than a bare class. Each builder has a matching ``repr_*`` entry in
``rftrack_repr_rules`` that renders the same call as Python source, for
exporting a standalone script; :func:`_make` derives both from one args helper.

RF-Track is optional (``pip install rf_track``, under a CERN proprietary
licence), so its import is guarded; :func:`get_rftrack` raises only when it is
actually needed.
"""

import math
from warnings import warn

import numpy as np

from laura.models.constants import speed_of_light

try:
    import RF_Track as _rft

    _RFTRACK_AVAILABLE = True
except ImportError:
    _rft = None
    _RFTRACK_AVAILABLE = False


def get_rftrack():
    """
    Return the imported ``RF_Track`` module.

    Raises
    ------
    ImportError
        If RF_Track is not installed (``pip install rf_track``).
    """
    if not _RFTRACK_AVAILABLE:
        raise ImportError(
            "RF_Track is not installed. Install it with `pip install rf_track` "
            "(distributed by CERN under a proprietary licence)."
        )
    return _rft


def space_charge_engine(npart, sample_interval: int = 1, mirror_z=None):
    """
    Build an ``RF_Track.SpaceCharge_PIC_FreeSpace`` engine (manual §5.1.3), with
    an ``Nx=Ny=Nz`` mesh computed exactly as ASTRA sizes its space-charge grid:
    the nearest power of two to the cube root of the (down-sampled) particle
    count, minimum 4 (``laura.translator.utils.classes.get_grid_size``).

    Parameters
    ----------
    npart: int
        Number of macro-particles in the bunch.
    sample_interval: int
        Particle down-sampling factor, as ASTRA's ``&CHARGE`` uses (grid is
        sized from ``npart / sample_interval``).
    mirror_z: float or None
        If not ``None``, activate cathode mirror charges (manual §7.5) with the
        cathode plane at longitudinal position ``mirror_z`` [m] via
        ``SpaceCharge.set_mirror``.

    Returns
    -------
    RF_Track.SpaceCharge_PIC_FreeSpace
    """
    from ...utils.classes import get_grid_size

    rft = get_rftrack()
    n = int(get_grid_size(npart / max(1, sample_interval)))
    sc = rft.SpaceCharge_PIC_FreeSpace(n, n, n)
    if mirror_z is not None:
        sc.set_mirror(mirror_z)
    return sc


def _format_args(args) -> str:
    """Render a tuple of constructor arguments as Python source text (used by
    every ``repr_*`` function below)."""
    parts = []
    for a in args:
        if isinstance(a, float) and math.isnan(a):
            parts.append("float('nan')")
        elif isinstance(a, np.ndarray):
            parts.append(f"np.array({a.tolist()!r})")
        else:
            parts.append(repr(a))
    return ", ".join(parts)


def _make(ctor: str, args_fn, post_fn=None) -> tuple:
    """
    Return the ``(build, repr)`` pair for ``rft.<ctor>(*args_fn(t, P_Q))``;
    ``post_fn(t)`` lists ``(method, value)`` calls made on the new object.
    """

    def build(t, P_Q: float = float("nan"), **kwargs) -> "object":
        obj = getattr(get_rftrack(), ctor)(*args_fn(t, P_Q))
        for method, value in post_fn(t) if post_fn else []:
            getattr(obj, method)(value)
        return obj

    def repr_(t, P_Q: float = float("nan"), **kwargs) -> tuple:
        ctor_expr = f"{ctor}({_format_args(args_fn(t, P_Q))})"
        post = post_fn(t) if post_fn else []
        return ctor_expr, [f"{{var}}.{method}({value!r})" for method, value in post]

    return build, repr_


def _length_args(t, P_Q) -> tuple:
    return (t.physical.length,)


def _set_phid(t) -> list:
    return [("set_phid", _phid(t))]


def _phid(t) -> float:
    # Off crest after autophase, with ASTRA's sign (Phi = crest - phase): a
    # positive LAURA phase is behind crest, as in Bmad and Xsuite.
    return -t.cavity.phase


def _field_types(t) -> tuple:
    """``(field_type, cavity_type)`` of the field map ``start_write()``
    resolved into ``simulation.field_definition``, or ``(None, None)``."""
    field_def = getattr(t.simulation, "field_definition", None)
    if not getattr(field_def, "read", False):
        return None, None
    types = (getattr(field_def, a, None) for a in ("field_type", "cavity_type"))
    return tuple(v.decode("utf-8") if isinstance(v, bytes) else v for v in types)


build_drift, repr_drift = _make("Drift", _length_args)

# P_Q is always NaN so RF-Track computes the gradient from LAURA's normalized
# k1 at autophase() time (API notes §4.1, §10); unlike SBend, no beam momentum
# is needed at conversion time.
build_quadrupole, _repr_quadrupole = _make(
    "Quadrupole", lambda t, P_Q: (t.physical.length, float("nan"), t.k1)
)


def repr_quadrupole(t, P_Q: float = float("nan"), **kwargs) -> tuple:
    """Render the caller's ``P_Q`` as a trailing debugging comment; the
    constructor still uses ``float('nan')`` (see :func:`build_quadrupole`)."""
    ctor_expr, _ = _repr_quadrupole(t)
    return (
        ctor_expr,
        [
            f"# P_Q (beam rigidity) at this element = {P_Q!r} MV/c "
            f"-- unused here, Quadrupole defers to autophase()"
        ],
    )


def _sbend_args(t, P_Q: float) -> tuple:
    # `t.angle` (DipoleTranslator's `magnetic.KnL(0)` property), not the raw
    # `t.magnetic.angle` field, which is not reliably populated.
    return (t.physical.length, t.angle, P_Q, t.e1, t.e2)


# SBend(L, angle, P_Q, E1, E2) (manual §4.2.3). A NaN P_Q takes the bunch's own
# P/Q, set by autophase() at each bend after acceleration (RF-Track 2.7.4); a
# fixed P_Q [MV/c] is kept as given. K1 [1/m^2, MAD-X convention] is not a
# constructor argument, so it is applied via `set_K1` when nonzero.
def _sbend_setters(t) -> list:
    setters = [("set_K1", t.k1)] if t.k1 else []
    # Fringe-field part of the edge focusing, MAD-X style: one half gap, and
    # (ponytail: RF-Track has a single fint) the entrance fint for both faces.
    fringe = t._madx_fringe("sbend")
    if fringe.get("fint") and fringe.get("hgap"):
        setters += [("set_fint", fringe["fint"]), ("set_hgap", fringe["hgap"])]
    return setters


build_sbend, repr_sbend = _make("SBend", _sbend_args, _sbend_setters)

# Kick strengths are left at 0, to be set at run time (as for ASTRA/GPT).
build_corrector, repr_corrector = _make("Corrector", _length_args)


def _magnetic_fieldmap_available(t) -> bool:
    """
    True if ``simulation.field_definition`` has resolved (via
    ``start_write()``, run before any builder) to an on-axis static magnetic
    field map for ``Static_Magnetic_FieldMap_1d`` (manual §4.4.4); otherwise
    the analytic ``Solenoid`` is used.
    """
    return _field_types(t)[0] == "1DMagnetoStatic"


def _solenoid_fieldmap_args(t, P_Q) -> tuple:
    from ...utils.fields import rftrack as fields_rftrack

    return fields_rftrack.static_magnetic_fieldmap_1d_args(
        t.simulation.field_definition, amplitude=t.magnetic.field_amplitude
    )


build_solenoid_fieldmap, repr_solenoid_fieldmap = _make(
    "Static_Magnetic_FieldMap_1d", _solenoid_fieldmap_args
)
# The third argument is the aperture radius [m], and RF-Track loses every particle
# outside it (its default, 0, loses them all). It does not change the field, so it
# is left wide; the element's own aperture is applied afterwards via set_aperture.
_build_solenoid, _repr_solenoid = _make(
    "Solenoid", lambda t, P_Q: (t.physical.length, t.magnetic.field_amplitude, 1.0)
)


def build_solenoid(t, **kwargs) -> "object":
    """Build an ``RF_Track.Solenoid`` from length [m] and peak on-axis field
    [T], or a real ``Static_Magnetic_FieldMap_1d`` (manual §4.4.4) when this
    solenoid carries a resolved on-axis field map -- see
    :func:`_magnetic_fieldmap_available`."""
    if _magnetic_fieldmap_available(t):
        return build_solenoid_fieldmap(t, **kwargs)
    return _build_solenoid(t, **kwargs)


def repr_solenoid(t, **kwargs) -> tuple:
    if _magnetic_fieldmap_available(t):
        return repr_solenoid_fieldmap(t, **kwargs)
    return _repr_solenoid(t, **kwargs)


def _undulator_args(t, P_Q) -> tuple:
    m = t.magnetic
    nperiods = m.num_periods if m.num_periods else 1
    period = m.period if m.period else (m.length / nperiods if nperiods else m.length)
    return (period, m.normalized_strength, nperiods)


build_undulator, repr_undulator = _make("Undulator", _undulator_args)


def _multipole_args(t, order: int) -> tuple:
    knl = [0.0] * (order + 1)
    knl[order] = t.magnetic.KnL(order)
    return (t.physical.length, float("nan"), np.array(knl))


# RF-Track has no Sextupole/Octupole class: a Multipole carrying only K2L/K3L
# (MAD-X convention, same as LAURA's own multipole model).
build_sextupole, repr_sextupole = _make(
    "Multipole", lambda t, P_Q: _multipole_args(t, 2)
)
build_octupole, repr_octupole = _make("Multipole", lambda t, P_Q: _multipole_args(t, 3))


def _bpm_args(t, P_Q) -> tuple:
    resolution = getattr(getattr(t, "diagnostic", None), "resolution", None) or 0.0
    return (t.physical.length, resolution)  # [m], [mm]


build_bpm, repr_bpm = _make("Bpm", _bpm_args)

# Infinite extent, unbounded time window: LAURA's width/height/time window are
# not carried over yet.
build_screen, repr_screen = _make("Screen", lambda t, P_Q: ())


def _cavity_args(t, P_Q) -> tuple:
    cav = t.cavity
    length = t.physical.length if t.physical.length > 0 else (cav.cell_length or 1.0)
    # Without a field map, `field_amplitude` is the cavity's voltage, as Elegant,
    # Ocelot and Xsuite read it. A uniform field E over the cell gains E * L * T,
    # T being the transit-time factor at beta = 1.
    x = np.pi * float(cav.frequency) * length / speed_of_light
    transit = np.sinc(x / np.pi)
    if abs(transit) < 1e-3:
        raise ValueError(
            f"RF cavity {t.name}: a {length} m pillbox at {cav.frequency} Hz gains "
            f"nothing at beta = 1 (transit-time factor {transit:.1e}), so it cannot "
            f"give a voltage of {t.simulation.field_amplitude} V."
        )
    amplitude = t.simulation.field_amplitude / (length * transit)
    return (np.array([amplitude]), float(cav.frequency), length, 1)


# Pillbox_Cavity: a standing-wave cavity as one effective cell with a uniform
# (0th Fourier coefficient) on-axis field.
# ponytail: single cell/harmonic, because Pillbox_Cavity construction blows up
# beyond ~25 cells; upgrade to SW_Structure (manual §4.3.6) once LAURA stores
# per-cell Fourier coefficients.
build_pillbox_cavity, repr_pillbox_cavity = _make(
    "Pillbox_Cavity", _cavity_args, _set_phid
)


def _resolve_ph_advance(t) -> float:
    """
    Phase advance per cell [rad].

    Read from the field map's ``mode_numerator``/``mode_denominator`` (the
    source the Elegant export uses), not ``t.cavity``'s, which can disagree
    with the referenced field map; RF-Track and ASTRA/Elegant must use the
    same mode. Falls back to ``t.cavity`` if the field definition has none.
    """
    cav = t.cavity
    field_def = getattr(t.simulation, "field_definition", None)
    numerator = getattr(field_def, "mode_numerator", None)
    denominator = getattr(field_def, "mode_denominator", None)
    if numerator is None or denominator is None:
        numerator, denominator = cav.mode_numerator, cav.mode_denominator
    if numerator and denominator:
        return float(2 * np.pi * numerator / denominator)
    warn(
        f"No mode_numerator/mode_denominator supplied for travelling-wave "
        f"cavity {t.name} (checked both its field_definition and its own "
        f"cavity data); defaulting to a 2*pi/3 phase advance per cell (the "
        f"common S-band travelling-wave convention)."
    )
    return 2 * np.pi / 3


def _tw_structure_args(t, P_Q) -> tuple:
    cav = t.cavity
    frequency = float(cav.frequency)
    ph_adv = _resolve_ph_advance(t)
    # The structure spans the element (RF-Track takes a fractional cell count,
    # each cell ph_adv*c/(2*pi*f) long) and gains coefficient * length: the
    # voltage Elegant and Bmad give a travelling-wave field_amplitude.
    cells = t.physical.length * 2 * np.pi * frequency / (ph_adv * speed_of_light)
    voltage = t.simulation.field_amplitude / np.sqrt(2) * (t.get_cells() + 3.8) * cav.cell_length
    return (np.array([voltage / t.physical.length]), 0, frequency, ph_adv, cells)


# TW_Structure (analytic Fourier-series travelling-wave model, manual §4.3.5)
# takes the real cell count without Pillbox_Cavity's construction blow-up.
# ponytail: single harmonic (n=0), as in the manual's ideal TW example; pass
# the full coefficient array once LAURA stores per-cell Fourier coefficients.
build_tw_structure, repr_tw_structure = _make(
    "TW_Structure", _tw_structure_args, _set_phid
)


def _cavity_fieldmap_available(t) -> bool:
    """
    True if ``simulation.field_definition`` has resolved to an on-axis
    standing-wave field map for ``RF_FieldMap_1d`` (manual §4.4.1); otherwise
    :func:`build_tw_structure`/:func:`build_pillbox_cavity` is used.
    """
    return _field_types(t) == ("1DElectroDynamic", "StandingWave")


def _cavity_fieldmap_args(t, P_Q) -> tuple:
    from ...utils.fields import rftrack as fields_rftrack

    # `field_amplitude` is the peak on-axis field, as ASTRA's MaxE; the map
    # already holds every cell.
    return fields_rftrack.rf_fieldmap_1d_args(
        t.simulation.field_definition,
        amplitude=t.simulation.field_amplitude,
        frequency=float(t.cavity.frequency),
    )


# RF_FieldMap_1d (manual §4.4.1) reconstructs the off-axis field from the
# on-axis samples, like ASTRA's FILE_EFieLD; preferred over Pillbox_Cavity.
build_cavity_fieldmap, repr_cavity_fieldmap = _make(
    "RF_FieldMap_1d", _cavity_fieldmap_args, _set_phid
)


def _tw_fieldmap_available(t) -> bool:
    """
    True if ``simulation.field_definition`` has resolved to an ASTRA-TWS-style
    travelling-wave field map with ``start_cell_z``, ``end_cell_z``,
    ``mode_numerator`` and ``mode_denominator`` all set; otherwise
    :func:`build_tw_structure` is used.
    """
    if _field_types(t) != ("1DElectroDynamic", "TravellingWave"):
        return False
    return all(
        getattr(t.simulation.field_definition, attr, None) is not None
        for attr in ("start_cell_z", "end_cell_z", "mode_numerator", "mode_denominator")
    )


def _tw_fieldmap_args(t, P_Q) -> tuple:
    from ...utils.fields import rftrack as fields_rftrack

    # The map replicates every cell, so the amplitude is the real per-cell
    # field, not scaled by n_cells; `get_cells()` is ASTRA's `C_numb`, so
    # RF-Track tracks the same physical structure length.
    (args,) = fields_rftrack.rf_fieldmap_1d_travelling_wave_args_list(
        t.simulation.field_definition,
        amplitude=t.simulation.field_amplitude,
        frequency=float(t.cavity.frequency),
        n_cells=t.get_cells(),
    )
    return args


# One RF_FieldMap_1d (manual §4.4.1) over couplers and tiled core, from the
# cavity's ASTRA-TWS-style field map; preferred over TW_Structure.
build_tw_fieldmap, repr_tw_fieldmap = _make(
    "RF_FieldMap_1d", _tw_fieldmap_args, _set_phid
)


def build_rf_cavity(t, **kwargs) -> "object":
    """Dispatch, in priority order: a ``Drift`` for a cavity with no field (RF-Track
    loses every particle in a zero-field RF element); :func:`build_tw_fieldmap`
    (real on-axis field map) for a travelling-wave cavity with a
    resolved ASTRA-TWS field map, else :func:`build_tw_structure`
    (single-harmonic analytic approximation) for travelling-wave;
    :func:`build_cavity_fieldmap` (real on-axis field map) for a standing-wave
    cavity with one resolved, else :func:`build_pillbox_cavity` (uniform field
    giving ``field_amplitude`` as the voltage)."""
    if not t.simulation.field_amplitude:
        return build_drift(t, **kwargs)
    # The translator's structure_type also accepts Bmad's "TravelingWave"
    if t.structure_type == "TravellingWave":
        if _tw_fieldmap_available(t):
            return build_tw_fieldmap(t, **kwargs)
        return build_tw_structure(t, **kwargs)
    if _cavity_fieldmap_available(t):
        return build_cavity_fieldmap(t, **kwargs)
    return build_pillbox_cavity(t, **kwargs)


def repr_rf_cavity(t, **kwargs) -> tuple:
    if not t.simulation.field_amplitude:
        return repr_drift(t, **kwargs)
    if t.structure_type == "TravellingWave":
        if _tw_fieldmap_available(t):
            return repr_tw_fieldmap(t, **kwargs)
        return repr_tw_structure(t, **kwargs)
    if _cavity_fieldmap_available(t):
        return repr_cavity_fieldmap(t, **kwargs)
    return repr_pillbox_cavity(t, **kwargs)


# hardware_type -> (build, repr)
_RULES = {
    "Drift": (build_drift, repr_drift),
    "Quadrupole": (build_quadrupole, repr_quadrupole),
    "Dipole": (build_sbend, repr_sbend),
    "Sextupole": (build_sextupole, repr_sextupole),
    "Octupole": (build_octupole, repr_octupole),
    "Solenoid": (build_solenoid, repr_solenoid),
    "Undulator": (build_undulator, repr_undulator),
    "Horizontal_Corrector": (build_corrector, repr_corrector),
    "Vertical_Corrector": (build_corrector, repr_corrector),
    "Combined_Corrector": (build_corrector, repr_corrector),
    "RFCavity": (build_rf_cavity, repr_rf_cavity),
    "Beam_Position_Monitor": (build_bpm, repr_bpm),
    "Screen": (build_screen, repr_screen),
    "Aperture": (build_drift, repr_drift),
    "Collimator": (build_drift, repr_drift),
    # A zero-length Screen, so the beam can be read back at every marker
    "Marker": (build_screen, repr_screen),
}
rftrack_conversion_rules = {k: b for k, (b, _) in _RULES.items()}
rftrack_repr_rules = {k: r for k, (_, r) in _RULES.items()}
