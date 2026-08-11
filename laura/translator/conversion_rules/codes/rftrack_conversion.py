"""
Per-``hardware_type`` builder functions converting a LAURA element translator
instance into an RF-Track Python object.

Unlike Ocelot/Cheetah/Xsuite (``ocelot_conversion.py`` and siblings), RF-Track
element constructors take strictly *positional* arguments with heterogeneous
signatures per element type (see ``RFTrack/RFTrack_API_notes.md`` in the repo
root), so a flat ``hardware_type -> class`` dict is not enough — each entry
here is a small builder function instead of a bare class.

Each builder has a matching entry in ``rftrack_repr_rules`` (see bottom of
this file) that renders the *same* constructor call as Python source text
(``BaseElementTranslator.to_rftrack_repr`` / ``SectionLatticeTranslator.
to_rftrack(save=True)``), for exporting a lattice to a standalone script —
mirrors Ocelot's ``MagneticLattice.save_as_py_file()``, which RF-Track has no
built-in equivalent of. Every builder therefore isolates its constructor
arguments into a small ``_..._args()`` helper so the object-building and
text-rendering paths share one source of truth for the numeric formulas.

RF-Track is not distributed on PyPI; it must be installed manually from the
RF-Track CERN page. Import is therefore guarded so the rest of LAURA keeps
working without it installed — call :func:`get_rftrack` to fail with a clear
message only at the point RF-Track is actually needed.
"""
import math
from warnings import warn

import numpy as np

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
        If RF_Track is not installed (it is not on PyPI; download it from the
        RF-Track page at CERN and install the wheel into this environment).
    """
    if not _RFTRACK_AVAILABLE:
        raise ImportError(
            "RF_Track is not installed. It is not distributed on PyPI; download "
            "the Python wheel from the RF-Track page (CERN, A. Latina) and "
            "install it into this environment, e.g. `pip install RF_Track-*.whl`."
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


def _drift_args(t) -> tuple:
    return (t.physical.length,)


def build_drift(t, **kwargs) -> "object":
    """Build an ``RF_Track.Drift`` from ``t.physical.length`` [m]."""
    rft = get_rftrack()
    return rft.Drift(*_drift_args(t))


def repr_drift(t, **kwargs) -> tuple:
    return f"Drift({_format_args(_drift_args(t))})", []


def _quadrupole_args(t) -> tuple:
    return (t.physical.length, float("nan"), t.k1)


def build_quadrupole(t, **kwargs) -> "object":
    """
    Build an ``RF_Track.Quadrupole``.

    ``P_Q`` (beam rigidity) is always left as ``NaN`` here — regardless of any
    ``P_Q`` passed in by the caller — so RF-Track defers the gradient
    calculation to ``autophase()`` time, matching LAURA's normalized ``k1``
    definition (see API notes §4.1, §10 "P_Q = NaN convention"). This is
    RF-Track's own documented/recommended approach for Quadrupole/Multipole
    specifically (verified working against the real package: transmission is
    preserved) — unlike ``SBend`` (see :func:`build_sbend`), it does not need
    the beam momentum known at conversion time.
    """
    rft = get_rftrack()
    return rft.Quadrupole(*_quadrupole_args(t))


def repr_quadrupole(t, P_Q: float = float("nan"), **kwargs) -> tuple:
    """
    Renders the actual ``P_Q`` (beam rigidity) the caller passed in as a
    trailing comment -- the constructor call itself still always uses
    ``float('nan')`` (see :func:`build_quadrupole`), so this is purely a
    debugging aid for confirming ``P_Q`` was computed correctly (e.g. not
    NaN/zero/garbage) when inspecting the exported lattice script, without
    changing the actual (correct) RF-Track behaviour.
    """
    return (
        f"Quadrupole({_format_args(_quadrupole_args(t))})",
        [f"# P_Q (beam rigidity) at this element = {P_Q!r} MV/c "
         f"-- unused here, Quadrupole defers to autophase()"],
    )


def _resolve_sbend_p_q(t, P_Q: float) -> float:
    if P_Q != P_Q:  # NaN check without importing math/numpy just for this
        warn(
            f"No P_Q (reference momentum/charge) supplied for dipole {t.name}; "
            f"RF-Track SBend requires a real value or the bend physics will be "
            f"wrong (verified: NaN causes total particle loss). Using a "
            f"placeholder of 1.0 MV/c — pass the real beam P_Q via to_rftrack()."
        )
        return 1.0
    return P_Q


def _sbend_args(t, P_Q: float) -> tuple:
    P_Q = _resolve_sbend_p_q(t, P_Q)
    # `t.angle` (the DipoleTranslator's own computed property, `magnetic.KnL(0)`)
    # -- not `t.magnetic.angle`, the raw underlying model field, which defaults
    # to `None`/is not reliably populated (its own docstring says it's meant to
    # be read via a Python property, not read directly).
    return (t.physical.length, t.angle, P_Q, t.e1, t.e2)


def build_sbend(t, P_Q: float = float("nan"), **kwargs) -> "object":
    """
    Build an ``RF_Track.SBend``.

    LAURA already stores explicit entrance/exit edge angles (``t.e1``/``t.e2``)
    per dipole, matching ``SBend``'s own constructor signature directly — no
    rectangular/sector geometry re-derivation needed (resolves PLAN.md open
    question 1: SBend, not RBend). Constructor argument order is
    ``(L, angle, P_Q, E1, E2)`` -- verified against the real
    RF_Track_reference_manual.pdf §4.2.3 (``angle`` before ``P_Q``).

    Unlike ``Quadrupole``/``Multipole``, ``SBend`` does **not** support a
    ``P_Q=NaN`` deferred-autophase convention — verified against the real
    RF_Track package (v2.6.3): ``NaN`` silently produces zero transmission
    (the whole bunch is lost), and the *correct* ``P_Q`` value materially
    changes the bend trajectory (it is not merely cosmetic/reporting-only).
    ``P_Q`` must therefore be supplied by the caller as the beam's actual
    reference momentum-over-charge [MV/c] at this point in the lattice —
    mirrors how ``to_gpt(Brho=...)`` threads the equivalent rigidity value
    down from ``SectionLatticeTranslator.to_gpt(Brho=...)``.

    ``K1`` (combined-function-dipole quadrupolar gradient, 1/m^2, same MAD-X
    convention ``build_quadrupole`` uses for ``t.k1``) is not a constructor
    argument -- the manual only documents it as a settable property
    (``get_K1()``/``set_K1()``) -- so it's applied via ``set_K1`` after
    construction, only when nonzero (most dipoles are pure sector bends).
    """
    rft = get_rftrack()
    obj = rft.SBend(*_sbend_args(t, P_Q))
    if t.k1:
        obj.set_K1(t.k1)
    return obj


def repr_sbend(t, P_Q: float = float("nan"), **kwargs) -> tuple:
    post_stmts = [f"{{var}}.set_K1({t.k1!r})"] if t.k1 else []
    return f"SBend({_format_args(_sbend_args(t, P_Q))})", post_stmts


def _corrector_args(t) -> tuple:
    return (t.physical.length,)


def build_corrector(t, **kwargs) -> "object":
    """Build an ``RF_Track.Corrector`` (steerer). Kick strengths are left at 0;
    a converted corrector is intended to be set via ``set_strength``-style
    calls at run time, mirroring how ASTRA/GPT correctors are handled."""
    rft = get_rftrack()
    return rft.Corrector(*_corrector_args(t))


def repr_corrector(t, **kwargs) -> tuple:
    return f"Corrector({_format_args(_corrector_args(t))})", []


def _solenoid_args(t) -> tuple:
    return (t.physical.length, t.magnetic.field_amplitude, 0.0)


def _magnetic_fieldmap_available(t) -> bool:
    """
    True if this element's ``simulation.field_definition`` has already
    resolved (via ``start_write()`` -> ``update_field_definition()``, always
    run before any builder here) to a real on-axis static-magnetic field map
    that :func:`_solenoid_fieldmap_args` can hand straight to RF-Track's
    ``Static_Magnetic_FieldMap_1d`` (manual §4.4.4) -- see
    ``utils.fields.rftrack.static_magnetic_fieldmap_1d_args``. Elements
    without a configured/resolved field map fall back to the idealized
    analytic ``Solenoid`` model.
    """
    field_def = getattr(t.simulation, "field_definition", None)
    if not getattr(field_def, "read", False):
        return False
    field_type = getattr(field_def, "field_type", None)
    if isinstance(field_type, bytes):
        field_type = field_type.decode("utf-8")
    return field_type == "1DMagnetoStatic"


def _solenoid_fieldmap_args(t) -> tuple:
    from ...utils.fields import rftrack as fields_rftrack

    return fields_rftrack.static_magnetic_fieldmap_1d_args(
        t.simulation.field_definition, amplitude=t.magnetic.field_amplitude
    )


def build_solenoid_fieldmap(t, **kwargs) -> "object":
    """Build a real ``RF_Track.Static_Magnetic_FieldMap_1d`` (manual §4.4.4)
    from this solenoid's own on-axis field map -- e.g. a measured or
    FEM-simulated profile with realistic fringe fields -- in preference to the
    idealized analytic :func:`build_solenoid` model."""
    rft = get_rftrack()
    return rft.Static_Magnetic_FieldMap_1d(*_solenoid_fieldmap_args(t))


def repr_solenoid_fieldmap(t, **kwargs) -> tuple:
    return (
        f"Static_Magnetic_FieldMap_1d({_format_args(_solenoid_fieldmap_args(t))})",
        [],
    )


def build_solenoid(t, **kwargs) -> "object":
    """Build an ``RF_Track.Solenoid`` from length [m] and peak on-axis field
    [T], or a real ``Static_Magnetic_FieldMap_1d`` (manual §4.4.4) when this
    solenoid carries a resolved on-axis field map -- see
    :func:`_magnetic_fieldmap_available`."""
    if _magnetic_fieldmap_available(t):
        return build_solenoid_fieldmap(t, **kwargs)
    rft = get_rftrack()
    return rft.Solenoid(*_solenoid_args(t))


def repr_solenoid(t, **kwargs) -> tuple:
    if _magnetic_fieldmap_available(t):
        return repr_solenoid_fieldmap(t, **kwargs)
    return f"Solenoid({_format_args(_solenoid_args(t))})", []


def _undulator_args(t) -> tuple:
    m = t.magnetic
    nperiods = m.num_periods if m.num_periods else 1
    period = m.period if m.period else (m.length / nperiods if nperiods else m.length)
    return (period, m.normalized_strength, nperiods)


def build_undulator(t, **kwargs) -> "object":
    """Build an ``RF_Track.Undulator`` from period/strength/periods."""
    rft = get_rftrack()
    return rft.Undulator(*_undulator_args(t))


def repr_undulator(t, **kwargs) -> tuple:
    return f"Undulator({_format_args(_undulator_args(t))})", []


def _multipole_args(t, order: int) -> tuple:
    knl = [0.0] * (order + 1)
    knl[order] = t.magnetic.KnL(order)
    return (t.physical.length, float("nan"), np.array(knl))


def _build_multipole(t, order: int) -> "object":
    rft = get_rftrack()
    return rft.Multipole(*_multipole_args(t, order))


def _repr_multipole(t, order: int) -> tuple:
    return f"Multipole({_format_args(_multipole_args(t, order))})", []


def build_sextupole(t, **kwargs) -> "object":
    """Build an ``RF_Track.Multipole`` carrying only the K2L coefficient (RF-Track
    has no dedicated Sextupole class; normal/skew multipole coefficients follow
    the MAD-X convention, same as LAURA's own multipole model)."""
    return _build_multipole(t, 2)


def repr_sextupole(t, **kwargs) -> tuple:
    return _repr_multipole(t, 2)


def build_octupole(t, **kwargs) -> "object":
    """Build an ``RF_Track.Multipole`` carrying only the K3L coefficient."""
    return _build_multipole(t, 3)


def repr_octupole(t, **kwargs) -> tuple:
    return _repr_multipole(t, 3)


def _bpm_args(t) -> tuple:
    resolution = getattr(getattr(t, "diagnostic", None), "resolution", None) or 0.0
    return (t.physical.length, resolution)


def build_bpm(t, **kwargs) -> "object":
    """Build an ``RF_Track.Bpm`` from length [m] and resolution [mm]."""
    rft = get_rftrack()
    return rft.Bpm(*_bpm_args(t))


def repr_bpm(t, **kwargs) -> tuple:
    return f"Bpm({_format_args(_bpm_args(t))})", []


def build_screen(t, **kwargs) -> "object":
    """Build an ``RF_Track.Screen`` (infinite extent, unbounded time window by
    default; width/height/time-window are not carried over from LAURA yet)."""
    rft = get_rftrack()
    return rft.Screen()


def repr_screen(t, **kwargs) -> tuple:
    return "Screen()", []


def _cavity_args(t) -> tuple:
    cav = t.cavity
    length = t.physical.length if t.physical.length > 0 else (cav.cell_length or 1.0)
    # Collapsing the cavity's real `n_cells` cells into RF-Track's single
    # effective cell means the field amplitude has to be scaled up by
    # `n_cells` too, or the energy gain over the cavity's full physical
    # length comes out ~n_cells times too small. Verified against a real
    # end-to-end simba.Framework().track() run: CLARA's L02 should take the
    # beam ~35 -> ~115 MeV; without this scaling RF-Track only added <1 MeV.
    amplitude = t.simulation.field_amplitude * (cav.n_cells or 1)
    return (np.array([amplitude]), float(cav.frequency), length, 1), cav.phase


def build_pillbox_cavity(t, **kwargs) -> "object":
    """
    Build an ``RF_Track.Pillbox_Cavity`` approximating the whole cavity as a
    single effective cell with a uniform (0th-order Fourier coefficient)
    on-axis field. Used for standing-wave cavities (``t.cavity.structure_type
    != "TravellingWave"``) -- travelling-wave cavities use
    :func:`build_tw_structure` instead (see :func:`build_rf_cavity`).

    ponytail: this is a simplified single-cell/single-harmonic approximation,
    not a faithful multi-cell SW structure reproduction (RF-Track's real
    ``SW_Structure`` needs per-cell Fourier coefficients fitted from a real
    1D field map, which LAURA does not currently store) — see PLAN.md open
    question 2. Deliberately always uses ``n_cells=1`` rather than the
    cavity's real cell count: measured against the real RF_Track package
    (v2.6.3), ``Pillbox_Cavity`` construction time grows very steeply with
    ``n_cells`` (fine up to ~25 cells, ~10s+ by 28, and a realistic 30-cell
    S-band value was killed for excessive memory use) -- collapsing to one
    effective cell (with amplitude scaled by ``n_cells``, see
    :func:`_cavity_args`) keeps this fast and avoids that cliff entirely.
    Standing-wave structures are typically few-cell (e.g. buncher cavities),
    so this is a reasonable fallback until ``SW_Structure`` support lands.
    Upgrade path: once LAURA stores per-cell field-map Fourier coefficients
    for a cavity, build a real ``SW_Structure`` instead (its input/output
    coupler + TW-body construction is a bigger, separate piece of work; see
    RF_Track_reference_manual.pdf §4.3.6).
    """
    rft = get_rftrack()
    args, phase = _cavity_args(t)
    obj = rft.Pillbox_Cavity(*args)
    obj.set_phid(phase)
    return obj


def repr_pillbox_cavity(t, **kwargs) -> tuple:
    args, phase = _cavity_args(t)
    return f"Pillbox_Cavity({_format_args(args)})", [f"{{var}}.set_phid({phase!r})"]


def _resolve_ph_advance(t) -> float:
    """
    Phase advance per cell [rad].

    Reads ``t.simulation.field_definition.mode_numerator``/``mode_denominator``
    -- the field-map file's own baked-in values (populated by
    ``BaseElementTranslator.update_field_definition()``/``start_write()``,
    which always runs before this) -- the SAME source
    ``laura.translator.converters.cavity.py``'s Elegant export reads
    (``self.simulation.field_definition.mode_numerator/mode_denominator``).

    Deliberately *not* ``t.cavity.mode_numerator``/``mode_denominator`` (the
    cavity element's own recorded value): verified these can silently
    disagree with the field map the element actually references -- e.g.
    CLARA's L04 cavity element records ``mode_numerator=2``, but its
    ``field_definition`` file (``TWS_S-DL.hdf5``, shared with L02/L03, whose
    cavity elements correctly record ``mode_numerator=1``) says 1. RF-Track
    and ASTRA/Elegant must use the same mode for the same physical structure.
    Falls back to the cavity element's own value only if the field
    definition hasn't resolved to a loaded ``field`` object (e.g. no
    ``field_definition`` file set at all).
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


def _tw_structure_args(t) -> tuple:
    cav = t.cavity
    amplitude = t.simulation.field_amplitude
    ph_adv = _resolve_ph_advance(t)
    return (
        np.array([1. / np.sqrt(2) * amplitude]), 0, float(cav.frequency), ph_adv, int(3 + cav.n_cells),
    ), cav.phase


def build_tw_structure(t, **kwargs) -> "object":
    """
    Build an ``RF_Track.TW_Structure`` -- RF-Track's proper analytic
    travelling-wave model (a closed-form Fourier-series field expansion,
    RF_Track_reference_manual.pdf §4.3.5), used for
    ``t.cavity.structure_type == "TravellingWave"`` cavities instead of
    :func:`build_pillbox_cavity`. Unlike ``Pillbox_Cavity``, whose per-cell
    construction time explodes for realistic cell counts (measured: fine to
    ~25 cells, 10s+ by 28, OOM by 30), ``TW_Structure`` takes the real cell
    count directly with no such blow-up -- it's a parametric analytic model,
    not built from discretized per-cell sub-objects.

    ponytail: single-harmonic (``n=0``) approximation of the on-axis field --
    the manual's own "ideal travelling-wave structure" example (§4.3.5) uses
    exactly this one-coefficient form; a fully faithful multi-harmonic
    expansion (as its "full realistic structure" example uses, §4.3.6) needs
    per-cell Fourier coefficients fitted from a real 1D field map, which
    LAURA does not currently store (same gap noted in
    ``build_pillbox_cavity``). Upgrade path: once LAURA stores those
    coefficients, pass the full array here instead of a single ``a0``.
    """
    rft = get_rftrack()
    args, phase = _tw_structure_args(t)
    obj = rft.TW_Structure(*args)
    obj.set_phid(phase)
    return obj


def repr_tw_structure(t, **kwargs) -> tuple:
    args, phase = _tw_structure_args(t)
    return f"TW_Structure({_format_args(args)})", [f"{{var}}.set_phid({phase!r})"]


def _cavity_fieldmap_available(t) -> bool:
    """
    True if this cavity's ``simulation.field_definition`` has already resolved
    (via ``start_write()`` -> ``update_field_definition()``, always run before
    any builder here) to a real on-axis standing-wave field map that
    :func:`_cavity_fieldmap_args` can hand straight to RF-Track's
    ``RF_FieldMap_1d`` (manual §4.4.1) -- see
    ``utils.fields.rftrack.rf_fieldmap_1d_args``. Travelling-wave and
    unresolved/missing field definitions fall back to
    :func:`build_tw_structure`/:func:`build_pillbox_cavity`.
    """
    field_def = getattr(t.simulation, "field_definition", None)
    if not getattr(field_def, "read", False):
        return False
    field_type = getattr(field_def, "field_type", None)
    cavity_type = getattr(field_def, "cavity_type", None)
    if isinstance(field_type, bytes):
        field_type = field_type.decode("utf-8")
    if isinstance(cavity_type, bytes):
        cavity_type = cavity_type.decode("utf-8")
    return field_type == "1DElectroDynamic" and cavity_type == "StandingWave"


def _cavity_fieldmap_args(t) -> tuple:
    from ...utils.fields import rftrack as fields_rftrack

    cav = t.cavity
    # Same "collapse n_cells into one effective object, scale amplitude up by
    # n_cells" convention as `_cavity_args`/`build_pillbox_cavity` -- except
    # here the field map already carries the real per-cell on-axis shape, so
    # this only needs to make the *total* peak amplitude match the cavity's
    # real physical length, not approximate a multi-cell structure.
    amplitude = t.simulation.field_amplitude * (cav.n_cells or 1)
    args = fields_rftrack.rf_fieldmap_1d_args(
        t.simulation.field_definition, amplitude=amplitude, frequency=float(cav.frequency)
    )
    return args, cav.phase


def build_cavity_fieldmap(t, **kwargs) -> "object":
    """
    Build a real ``RF_Track.RF_FieldMap_1d`` (manual §4.4.1) from this
    cavity's own on-axis field map, in preference to the single-Fourier-
    coefficient :func:`build_pillbox_cavity` approximation -- resolves the
    ``ponytail`` gap flagged there and in PLAN.md ("RF-Track's real
    ``SW_Structure`` needs per-cell Fourier coefficients fitted from a real 1D
    field map, which LAURA does not currently store"): LAURA does store it
    (``simulation.field_definition``), and RF-Track's field-map element
    doesn't need it fitted to Fourier coefficients at all --
    ``RF_FieldMap_1d`` takes the on-axis samples directly and reconstructs the
    off-axis field itself, exactly like ASTRA's own on-axis ``FILE_EFieLD``
    convention. See :func:`_cavity_fieldmap_available` for when this applies.
    """
    rft = get_rftrack()
    args, phase = _cavity_fieldmap_args(t)
    obj = rft.RF_FieldMap_1d(*args)
    obj.set_phid(phase)
    return obj


def repr_cavity_fieldmap(t, **kwargs) -> tuple:
    args, phase = _cavity_fieldmap_args(t)
    return f"RF_FieldMap_1d({_format_args(args)})", [f"{{var}}.set_phid({phase!r})"]


def _tw_fieldmap_available(t) -> bool:
    """
    True if this travelling-wave cavity's ``simulation.field_definition`` has
    already resolved to a real ASTRA-TWS-style on-axis field map with all four
    header values (``start_cell_z``/``end_cell_z``/``mode_numerator``/
    ``mode_denominator``) present -- everything
    :func:`_tw_fieldmap_args`/``utils.fields.rftrack.
    rf_fieldmap_1d_travelling_wave_args_list`` needs to build the coupler +
    core + coupler field maps. Missing any of these (or no field map at all) falls
    back to :func:`build_tw_structure`'s analytic model, which has its own,
    more lenient fallback (``_resolve_ph_advance``, defaults with a warning).
    """
    field_def = getattr(t.simulation, "field_definition", None)
    if not getattr(field_def, "read", False):
        return False
    field_type = getattr(field_def, "field_type", None)
    cavity_type = getattr(field_def, "cavity_type", None)
    if isinstance(field_type, bytes):
        field_type = field_type.decode("utf-8")
    if isinstance(cavity_type, bytes):
        cavity_type = cavity_type.decode("utf-8")
    if field_type != "1DElectroDynamic" or cavity_type != "TravellingWave":
        return False
    return all(
        getattr(field_def, attr, None) is not None
        for attr in ("start_cell_z", "end_cell_z", "mode_numerator", "mode_denominator")
    )


def _tw_fieldmap_args(t) -> tuple:
    from ...utils.fields import rftrack as fields_rftrack

    cav = t.cavity
    # Unlike `_cavity_args`'s Pillbox_Cavity collapse-to-one-cell convention,
    # the stitched field map genuinely replicates every cell, so the
    # amplitude is the real per-cell field -- same convention
    # `_tw_structure_args` already uses for the analytic TW_Structure model.
    amplitude = t.simulation.field_amplitude
    args_list = fields_rftrack.rf_fieldmap_1d_travelling_wave_args_list(
        t.simulation.field_definition,
        amplitude=amplitude,
        frequency=float(cav.frequency),
        # Same cell count ASTRA's own `C_numb` gets (`to_astra()`'s
        # `self.get_cells()`), so a field-map RF-Track cavity tracks the same
        # physical structure length as its ASTRA equivalent.
        n_cells=t.get_cells(),
    )
    return args_list, cav.phase


def build_tw_fieldmap(t, **kwargs) -> "object":
    """
    Build a real input coupler, a complex travelling-wave core, and a real
    output coupler -- all ``RF_Track.RF_FieldMap_1d`` (manual §4.4.1) built
    from this cavity's own ASTRA-TWS-style on-axis field map via
    ``utils.fields.rftrack.rf_fieldmap_1d_travelling_wave_args_list`` -- in
    preference to the single-harmonic analytic :func:`build_tw_structure`
    approximation. See :func:`_tw_fieldmap_available` for when this applies.

    Returns a **list** of RF-Track objects rather than wrapping them in their
    own sub-``Lattice``. ``BaseElementTranslator.to_rftrack()``/
    ``SectionLatticeTranslator.to_rftrack()`` flatten a list return directly
    into the section's own top-level ``Lattice`` as siblings. This avoids
    nesting a ``Lattice`` inside a ``Lattice`` inside a ``Volume`` -- verified
    against real RF_Track 2.6.3 that ``Volume.autophase()`` does not descend
    two ``Lattice`` levels deep (it silently fails to set ``t0`` for anything
    nested inside an appended sub-``Lattice``'s own sub-``Lattice``), so a
    cathode/``Volume``-tracked section containing a TW field-map cavity kept
    printing "reference time t0 not set" warnings on every ``track()`` call
    even after an explicit ``autophase()`` (harmless -- the tracked energy
    gain is verified identical either way, since RF-Track's own per-element
    auto-set-t0 fallback still runs during ``track()`` -- but noisy). Flat
    siblings of the same top-level ``Lattice`` are reached correctly by
    ``Volume.autophase()`` instead.

    Every element gets the same ``set_phid`` (empirically verified against
    real CLARA L01 data -- not the manual's own +90 degree core-vs-coupler
    offset, which is specific to the analytic ``SW_Structure``/
    ``TW_Structure`` element pair).
    """
    rft = get_rftrack()
    args_list, phase = _tw_fieldmap_args(t)
    elems = []
    for args in args_list:
        elem = rft.RF_FieldMap_1d(*args)
        elem.set_phid(phase)
        elems.append(elem)
    return elems


def repr_tw_fieldmap(t, **kwargs) -> list:
    """
    Returns a **list** of ``(ctor_expr, post_stmts)`` tuples, one per element
    -- see :func:`build_tw_fieldmap`. ``BaseElementTranslator.to_rftrack_repr``
    renders each list entry as its own uniquely-suffixed
    ``{varname}_N = rft.RF_FieldMap_1d(...)`` block (instead of the single
    ``{varname} = rft.Ctor(...)`` every other, single-object builder here
    produces), and reports every resulting variable name back to
    ``SectionLatticeTranslator._save_rftrack_py_file`` so each is appended to
    the exported script's ``lattice`` individually, matching :func:`build_tw_fieldmap`.
    """
    args_list, phase = _tw_fieldmap_args(t)
    return [
        (f"RF_FieldMap_1d({_format_args(args)})", [f"{{var}}.set_phid({phase!r})"])
        for args in args_list
    ]


def build_rf_cavity(t, **kwargs) -> "object":
    """Dispatch, in priority order: :func:`build_tw_fieldmap` (real stitched
    on-axis field map) for a travelling-wave cavity with a resolved ASTRA-TWS
    field map, else :func:`build_tw_structure` (single-harmonic analytic
    approximation) for travelling-wave; :func:`build_cavity_fieldmap` (real
    on-axis field map) for a standing-wave cavity with one resolved, else
    :func:`build_pillbox_cavity` (single-coefficient approximation)."""
    if t.cavity.structure_type == "TravellingWave":
        if _tw_fieldmap_available(t):
            return build_tw_fieldmap(t, **kwargs)
        return build_tw_structure(t, **kwargs)
    if _cavity_fieldmap_available(t):
        return build_cavity_fieldmap(t, **kwargs)
    return build_pillbox_cavity(t, **kwargs)


def repr_rf_cavity(t, **kwargs) -> tuple:
    if t.cavity.structure_type == "TravellingWave":
        if _tw_fieldmap_available(t):
            return repr_tw_fieldmap(t, **kwargs)
        return repr_tw_structure(t, **kwargs)
    if _cavity_fieldmap_available(t):
        return repr_cavity_fieldmap(t, **kwargs)
    return repr_pillbox_cavity(t, **kwargs)


rftrack_conversion_rules = {
    "Drift": build_drift,
    "Quadrupole": build_quadrupole,
    "Dipole": build_sbend,
    "Sextupole": build_sextupole,
    "Octupole": build_octupole,
    "Solenoid": build_solenoid,
    "Undulator": build_undulator,
    "Horizontal_Corrector": build_corrector,
    "Vertical_Corrector": build_corrector,
    "Combined_Corrector": build_corrector,
    "RFCavity": build_rf_cavity,
    "Beam_Position_Monitor": build_bpm,
    "Screen": build_screen,
    "Aperture": build_drift,
    "Collimator": build_drift,
    "Marker": build_drift,
}

rftrack_repr_rules = {
    "Drift": repr_drift,
    "Quadrupole": repr_quadrupole,
    "Dipole": repr_sbend,
    "Sextupole": repr_sextupole,
    "Octupole": repr_octupole,
    "Solenoid": repr_solenoid,
    "Undulator": repr_undulator,
    "Horizontal_Corrector": repr_corrector,
    "Vertical_Corrector": repr_corrector,
    "Combined_Corrector": repr_corrector,
    "RFCavity": repr_rf_cavity,
    "Beam_Position_Monitor": repr_bpm,
    "Screen": repr_screen,
    "Aperture": repr_drift,
    "Collimator": repr_drift,
    "Marker": repr_drift,
}

# ---------------------------------------------------------------------------
# Backwards compatibility: names renamed for PEP 8. Served lazily with a
# FutureWarning so downstream consumers (astec-stfc/simba) keep working.
# ---------------------------------------------------------------------------
from laura._compat import deprecated_aliases  # noqa: E402

__getattr__ = deprecated_aliases(
    __name__,
    globals(),
    {
        "_resolve_sbend_P_Q": "_resolve_sbend_p_q",
    },
)
