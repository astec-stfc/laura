"""
Per-``hardware_type`` builders converting a LAURA element translator into a
pyAT (Accelerator Toolbox) element.

AT keeps every magnet's strengths in ``PolynomA``/``PolynomB`` arrays rather
than in flat keywords, so each entry is a builder function, as for RF-Track;
the conventions shared with the importer live in :mod:`laura.translator.utils.at`.
"""

from math import ceil, pi, radians
from warnings import warn

import numpy as np

try:
    import at
except ImportError as _err:
    raise ImportError(
        "accelerator-toolbox is not installed. "
        'Install with: pip install "laura-accelerator[at]"'
    ) from _err

from ...utils.alignment import to_frame
from ...utils.at import FRINGE_BEND_MODEL, at_pivot, polynoms, time_lag

AT_STEP_LENGTH = 0.005
"""Longest integration step [m]."""

_MAGNET_CLASSES = {
    "Quadrupole": at.Quadrupole,
    "Sextupole": at.Sextupole,
}


_AT_PLANES = [0, 1, 2, 3, 5, 4]
"""LAURA writes its matrices raw to every code, whose last two planes are
(z-like, delta); AT's are (delta, ct)."""


def _strengths(t, skip_bend: bool = False) -> tuple:
    """``(PolynomA, PolynomB)`` from every multipole the element carries."""
    multipoles = t.magnetic.multipoles
    normal, skew = {}, {}
    for key in type(multipoles).model_fields if multipoles is not None else ():
        order = int(key[1:-1])
        normal[order] = float(t.resolve(multipoles.normal(order)) or 0.0)
        skew[order] = float(t.resolve(multipoles.skew(order)) or 0.0)
    if skip_bend:
        normal[0] = 0.0  # the bend field is BendingAngle; PolynomB[0] is an error on it
    normal = {n: v for n, v in normal.items() if v}
    skew = {n: v for n, v in skew.items() if v}
    return polynoms(normal, skew, t.physical.length)


def misalign(obj: "at.Element", t) -> None:
    """
    Apply ``t``'s tilt and alignment errors to ``obj``. A bend's design tilt
    rolls its frame, and its errors move it inside that roll, the roll is wrapped round
    them here.
    """
    curved = t._curved
    errors = t._misalignment()
    if not curved:
        errors["dz_rot"] = t.roll
    frame = t.roll - t.dz_rot if curved else 0.0
    if not (frame or any(errors.values())):
        return
    angle = obj.BendingAngle if curved else 0.0
    offset, rotation = to_frame(
        errors, tilt=frame, **at_pivot(t.physical.length, angle)
    )
    at.transform_elem(
        obj,
        dx=offset[0],
        dy=offset[1],
        dz=offset[2],
        pitch=rotation[0],
        yaw=rotation[1],
        tilt=rotation[2],
        reference=at.ReferencePoint.CENTRE,
    )
    if frame:
        c, s = np.cos(frame), np.sin(frame)
        rm = np.diag([c, c, c, c, 1.0, 1.0])
        rm[0, 2] = rm[1, 3] = s
        rm[2, 0] = rm[3, 1] = -s
        obj.R1, obj.T1 = obj.R1 @ rm, rm.T @ obj.T1
        obj.R2, obj.T2 = rm.T @ obj.R2, rm.T @ obj.T2
        obj._tilt_frame = frame  # what pyAT's ``tilt_frame`` getter reads


def _steps(t) -> dict:
    """``NumIntSteps``: at least AT's default and one step per
    :data:`AT_STEP_LENGTH`; a lattice's ``n_kicks`` may only raise it, since
    elegant's ``N_KICKS = 4`` is far coarser in AT."""
    explicit = t.simulation.n_kicks if "n_kicks" in t.simulation.model_fields_set else 0
    steps = ceil(t.physical.length / AT_STEP_LENGTH - 1e-9)
    return {"NumIntSteps": max(10, steps, explicit or 0)}


def build_passive(t) -> "at.Element":
    """A ``Drift`` over the element's length, or a ``Marker`` if it has none."""
    if t.physical.length > 0:
        return at.Drift(t.name, t.physical.length)
    return at.Marker(t.name)


def build_monitor(t) -> "at.Element":
    """A thin ``Monitor``; the section pads any length with a drift."""
    return at.Monitor(t.name)


def build_magnet(t) -> "at.Element":
    """A thick ``Quadrupole``/``Sextupole``/``Multipole``, or a
    ``ThinMultipole`` for a zero-length magnet."""
    poly_a, poly_b = _strengths(t)
    length = t.physical.length
    if length == 0:
        return at.ThinMultipole(t.name, poly_a, poly_b)
    cls = _MAGNET_CLASSES.get(t.hardware_type)
    if cls is None:
        return at.Multipole(t.name, length, poly_a, poly_b, **_steps(t))
    return cls(t.name, length, PolynomA=poly_a, PolynomB=poly_b, **_steps(t))


def _fringe_model(t, effects: bool | None) -> int:
    return 0 if effects is False else FRINGE_BEND_MODEL[t.fringe_order]


def build_dipole(t) -> "at.Element":
    """A sector ``Dipole``; any gradient and higher terms ride in the polynoms.

    ``BndMPoleSymplectic4E2Pass`` is the only bend pass matching elegant's
    combined-function chromaticity (br14); it ignores ``FringeBend*`` and always
    applies both edges, so a lattice that switches an edge off falls back to
    ``BndMPoleSymplectic4Pass``."""
    poly_a, poly_b = _strengths(t, skip_bend=True)
    magnetic, simulation = t.magnetic, t.simulation
    edges = (simulation.edge1_effects, simulation.edge2_effects)
    if magnetic.exit_half_gap != magnetic.half_gap:
        warn(
            f"{t.name}: AT has one FullGap for both faces; using the entrance "
            f"half gap {magnetic.half_gap} m, not the exit's {magnetic.exit_half_gap} m."
        )
    return at.Dipole(
        t.name,
        t.physical.length,
        float(t.resolve(t.angle)),
        PolynomA=poly_a,
        PolynomB=poly_b,
        EntranceAngle=float(t.e1),
        ExitAngle=float(t.e2),
        FullGap=2 * magnetic.half_gap,
        FringeInt1=magnetic.edge_field_integral_entrance or 0.0,
        FringeInt2=magnetic.edge_field_integral_exit or 0.0,
        FringeBendEntrance=_fringe_model(t, edges[0]),
        FringeBendExit=_fringe_model(t, edges[1]),
        PassMethod=(
            "BndMPoleSymplectic4Pass" if False in edges else "BndMPoleSymplectic4E2Pass"
        ),
        **_steps(t),
    )


def build_corrector(t) -> "at.Element":
    """A ``Corrector``; ``KickAngle`` has LAURA's sign, positive toward +x/+y."""
    kicks = [
        float(t.resolve(t.magnetic.horizontal_kick) or 0.0),
        float(t.resolve(t.magnetic.vertical_kick) or 0.0),
    ]
    return at.Corrector(t.name, t.physical.length, kicks)


def build_cavity(t) -> "at.Element":
    """An ``RFCavity``. ``Energy`` and ``HarmNumber`` need the ring, so the
    section fills them in."""
    frequency = float(t.cavity.frequency)
    return at.RFCavity(
        t.name,
        t.physical.length,
        float(t.voltage),
        frequency,
        0,
        0.0,
        TimeLag=time_lag(float(t.phase), frequency),
    )


def build_crab_cavity(t) -> "at.Element":
    """A horizontal ``CrabCavity``; a roll turns its plane. Phase 0 is full
    deflection; ``CrabCavityPass`` gives no energy kick."""
    frequency = float(t.cavity.frequency)
    return at.CrabCavity(
        t.name,
        t.physical.length,
        [float(t.voltage), 0.0],
        frequency,
        0,
        TimeLag=time_lag(float(t.phase), frequency, crest=-90.0),
    )


def build_ac_dipole(t) -> "at.Element":
    """A thin sine-mode ``VariableThinMultipole``. Its amplitude is a kick, so
    this leaves it as the integrated field [T m] for the section to divide by
    the rigidity. ``PolynomB`` kicks toward -x, hence the horizontal sign.
    All-zero ``ramp`` turns leave it off."""
    if t.simulation.waveform:
        warn(
            f"{t.name}: AT's AC dipole drives a sinusoid; the waveform was not applied."
        )
    vertical = t.hardware_type == "Vertical_AC_Dipole"
    plane = "A" if vertical else "B"
    return at.VariableThinMultipole(
        t.name,
        at.ACMode.SINE,
        **{
            f"Amplitude{plane}": [t._integrated_field * (1 if vertical else -1)],
            f"Frequency{plane}": float(t.simulation.frequency),
            f"Phase{plane}": radians(float(t.resolve(t.simulation.phase) or 0.0)),
        },
        Ramps=list(t.simulation.ramp),
    )


def build_matrix(t) -> "at.Element":
    """``Matrix66Pass``, or ``MatrixTijkPass`` given a second-order map;
    ``c_matrix`` is the exit offset ``T2``."""
    simulation, planes = t.simulation, _AT_PLANES
    kwargs = {"Length": t.physical.length}
    if simulation.c_matrix.any():
        kwargs["T2"] = simulation.c_matrix[planes]
    if simulation.u_matrix.any():
        warn(f"{t.name}: AT has no third-order map; the U matrix was dropped.")
    m66 = simulation.r_matrix[np.ix_(planes, planes)]
    if not simulation.t_matrix.any():
        return at.M66(t.name, m66, **kwargs)
    return at.Element(
        t.name,
        M66=np.asfortranarray(m66),
        Tijk=np.asfortranarray(simulation.t_matrix[np.ix_(planes, planes, planes)]),
        PassMethod="MatrixTijkPass",
        **kwargs,
    )


def build_wiggler(t) -> "at.Element":
    """A ``Wiggler`` (``GWigSymplecticPass``) with one field harmonic per plane;
    a helical wiggler's horizontal harmonic is a quarter period out of phase."""
    magnetic, length = t.magnetic, t.physical.length
    period = magnetic.period or length / magnetic.num_periods
    b_max = magnetic.peak_magnetic_field or magnetic.resolved("strength") / (
        93.3728962 * period
    )
    helical = {"Bx": (1, 1, 1, 0, 1, pi / 2)} if magnetic.helical else {}
    return at.Wiggler(t.name, length, period, b_max, **helical)


def build_solenoid(t) -> "at.Element":
    """A ``SolenoidLinearPass`` element; its ``K`` is MAD-X's per-metre ``KS``
    and LAURA's ``ks`` is integrated, as the importers and Bmad exporter read it."""
    if not t.physical.length:
        return build_passive(t)
    return at.Element(
        t.name,
        Length=t.physical.length,
        K=float(t.resolve(t.magnetic.ks) or 0.0)
        / (t.magnetic.length or t.physical.length),
        PassMethod="SolenoidLinearPass",
    )


_PASSIVE = (
    "Drift Marker Screen WireScanner Monitor Beam_Arrival_Monitor "
    "Bunch_Length_Monitor Wall_Current_Monitor Integrated_Current_Transformer "
    "Faraday_Cup_Monitor Photon_Monitor Watch_Point Diagnostic Center APContour "
    "Aperture Collimator RCollimator Rcollimator Shutter Valve Bellows Cleaner "
    "lscdrift csrdrift edrift"
).split()

at_conversion_rules = {
    **dict.fromkeys(_PASSIVE, build_passive),
    "Beam_Position_Monitor": build_monitor,
    "Dipole": build_dipole,
    "Quadrupole": build_magnet,
    "Sextupole": build_magnet,
    "Octupole": build_magnet,
    "Decapole": build_magnet,
    "Horizontal_Corrector": build_corrector,
    "Vertical_Corrector": build_corrector,
    "Combined_Corrector": build_corrector,
    "RFCavity": build_cavity,
    "CrabCavity": build_crab_cavity,
    "RFDeflectingCavity": build_crab_cavity,
    "Wiggler": build_wiggler,
    "Solenoid": build_solenoid,
    "MatrixTransform": build_matrix,
    "Horizontal_AC_Dipole": build_ac_dipole,
    "Vertical_AC_Dipole": build_ac_dipole,
}
"""LAURA ``hardware_type`` -> builder taking the element translator."""
