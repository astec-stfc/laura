"""
Per-``hardware_type`` builders converting a LAURA element translator into
ImpactX elements, as the plain dicts ``element.to_dict()`` writes and
``KnownElementsList.from_dicts`` reads.

``model`` picks the fidelity tier, ``"linear"``, ``"paraxial"`` or ``"exact"``.
"""

from math import ceil, degrees, sqrt
from warnings import warn

import numpy as np

TIERS = ("linear", "paraxial", "exact")

_DRIFTS = {"linear": "Drift", "paraxial": "ChrDrift", "exact": "ExactDrift"}
_QUADS = {"linear": "Quad", "paraxial": "ChrQuad", "exact": "ExactQuad"}
_EDGES = {"linear": "linear_slac75", "exact": "nonlinear_hwang_lee"}
_HWANG_LEE = ("k0", "k1", "k3", "k4", "k5", "k6")
_INT_ORDER = 4


def tier(available, model: str) -> str:
    """
    The cheapest of ``available`` tiers at least as faithful as ``model``,
    else the most faithful one.
    """
    if model not in TIERS:
        raise ValueError(f"model must be one of {TIERS}, got {model!r}")
    ranked = sorted(available, key=TIERS.index)
    return next((t for t in ranked if TIERS.index(t) >= TIERS.index(model)), ranked[-1])


def reference(energy: float | None, particle: str) -> dict:
    """
    ``mass`` [eV] and ``charge`` [e] of ``particle``; with ``energy``, the
    total energy [eV], also ``beta_gamma`` and the signed rigidity ``brho`` [T m].
    """
    from beamphysics.species import charge_of, mass_of

    mass, charge = mass_of(particle), charge_of(particle) / 1.602176634e-19
    ref = {"mass": mass, "charge": charge}
    if energy:
        momentum = sqrt(energy**2 - mass**2)
        ref.update(beta_gamma=momentum / mass, brho=momentum / (299792458.0 * charge))
    return ref


def drift(name: str, length: float, model: str) -> dict:
    return {"type": _DRIFTS[tier(_DRIFTS, model)], "name": name, "ds": length}


def _passive(t, model, ref) -> list:
    """A drift over the element's length, or a ``Marker`` if it has none."""
    if t.physical.length:
        return [drift(t.name, t.physical.length, model)]
    return [{"type": "Marker", "name": t.name}]


def _thin(t, kick: dict, model) -> list:
    """``kick`` between two half-length drifts, as MAD-X places a thin element."""
    half = t.physical.length / 2
    if not half:
        return [kick]
    return [
        drift(f"{t.name}_in", half, model),
        kick,
        drift(f"{t.name}_out", half, model),
    ]


def _strengths(t) -> tuple:
    """Integrated normal and skew strengths, indexed by order, MAD-X's knl/ksl."""
    multipoles = t.magnetic.multipoles
    orders = (
        sorted(int(k[1:-1]) for k in type(multipoles).model_fields)
        if multipoles
        else []
    )
    normal = [float(t.resolve(multipoles.normal(n)) or 0.0) for n in orders]
    skew = [float(t.resolve(multipoles.skew(n)) or 0.0) for n in orders]
    while normal and not (normal[-1] or skew[-1]):
        normal.pop(), skew.pop()
    return normal, skew


def build_magnet(t, model, ref) -> list:
    """A quadrupole, ``ExactMultipole`` or drift; thin, one ``Multipole`` per order."""
    length = t.physical.length
    normal, skew = _strengths(t)
    if not length:
        kicks = [
            {
                "type": "Multipole",
                "name": f"{t.name}_m{n + 1}",
                "multipole": n + 1,
                "K_normal": kn,
                "K_skew": ks,
            }
            for n, (kn, ks) in enumerate(zip(normal, skew))
            if kn or ks
        ]
        return kicks or [{"type": "Marker", "name": t.name}]
    if not any(normal + skew):
        return [drift(t.name, length, model)]
    if len(normal) == 2 and not (normal[0] or any(skew)):
        body = {
            "type": _QUADS[tier(_QUADS, model)],
            "name": t.name,
            "ds": length,
            "k": normal[1] / length,
        }
        if body["type"] != "Quad":
            body["unit"] = 0
        if body["type"] == "ExactQuad":
            body["int_order"] = _INT_ORDER
        return [body]
    return [
        {
            "type": "ExactMultipole",
            "name": t.name,
            "ds": length,
            "unit": 0,
            "int_order": _INT_ORDER,
            "k_normal": [k / length for k in normal],
            "k_skew": [k / length for k in skew],
        }
    ]


def _edge(t, location: str, psi: float, rc: float, fint, gap: float, model) -> dict:
    """A ``DipEdge``. With no fringe integral, a hard edge: ``g = 0``, else the
    nonlinear model's tanh-profile defaults would bend a bare face."""
    magnetic = t.magnetic
    edge = {
        "type": "DipEdge",
        "name": f"{t.name}_{location}",
        "psi": psi,
        "rc": rc,
        "g": 0.0 if fint is None else gap,
        "K2": fint or 0.0,
        "location": location,
        "model": _EDGES["linear" if t.fringe_order == 1 else tier(_EDGES, model)],
    }
    for k in _HWANG_LEE:
        value = getattr(magnetic, f"fringe_{k}")
        if value is not None:
            edge[k.upper()] = value
    return edge


def build_dipole(t, model, ref) -> list:
    """Entry ``DipEdge``, sector body, exit ``DipEdge``. The body is ``Sbend``,
    ``CFbend`` with a gradient, or ``ExactCFbend`` with skew or higher terms."""
    length, angle = t.physical.length, float(t.resolve(t.angle))
    if not (length and angle):
        return build_magnet(t, model, ref)
    rc = length / angle
    normal, skew = _strengths(t)
    k_normal = [1 / rc] + [k / length for k in normal[1:]]
    k_skew = [k / length for k in skew]
    exact = {
        "type": "ExactCFbend",
        "name": t.name,
        "ds": length,
        "unit": 0,
        "int_order": _INT_ORDER,
        "k_normal": k_normal,
        "k_skew": k_skew,
    }
    if any(skew) or any(normal[2:]):
        bodies = {"exact": exact}
    elif len(normal) > 1 and normal[1]:
        bodies = {
            "linear": {
                "type": "CFbend",
                "name": t.name,
                "ds": length,
                "rc": rc,
                "k": k_normal[1],
            },
            "exact": exact,
        }
    else:
        bodies = {
            "linear": {"type": "Sbend", "name": t.name, "ds": length, "rc": rc},
            "exact": {
                "type": "ExactSbend",
                "name": t.name,
                "ds": length,
                "phi": degrees(angle),
            },
        }
    magnetic, simulation = t.magnetic, t.simulation
    parts = [bodies[tier(bodies, model)]]
    if simulation.edge1_effects is not False:
        fint = magnetic.edge_field_integral_entrance
        parts.insert(0, _edge(t, "entry", float(t.e1), rc, fint, magnetic.gap, model))
    if simulation.edge2_effects is not False:
        gap = magnetic.gap if magnetic.exit_gap is None else magnetic.exit_gap
        parts.append(
            _edge(t, "exit", float(t.e2), rc, magnetic.exit_fringe_integral, gap, model)
        )
    return parts


def build_corrector(t, model, ref) -> list:
    """A thin ``Kicker``; ``hangle``/``vangle`` are MAD-X's ``hkick``/``vkick``."""
    kick = {
        "type": "Kicker",
        "name": t.name,
        "unit": "dimensionless",
        "xkick": float(t.resolve(t.hangle) or 0.0),
        "ykick": float(t.resolve(t.vangle) or 0.0),
    }
    return _thin(t, kick, model)


def build_solenoid(t, model, ref) -> list:
    """``Sol``, or for a paraxial or exact tier ``ChrAcc`` with no electric
    field, whose ``bz = ks * beta_gamma`` fixes it to the reference energy."""
    length = t.physical.length
    t.Brho = ref.get("brho", 0.0)
    t._check_rigidity("ImpactX")
    ks = float(t.ks or 0.0)
    if not length:
        if ks:
            warn(f"{t.name}: ImpactX has no thin solenoid; written as a marker.")
        return [{"type": "Marker", "name": t.name}]
    if tier(("linear", "paraxial"), model) == "linear" or not ks:
        return [{"type": "Sol", "name": t.name, "ds": length, "ks": ks}]
    return [
        {
            "type": "ChrAcc",
            "name": t.name,
            "ds": length,
            "ez": 0.0,
            "bz": ks * ref["beta_gamma"],
        }
    ]


def _standing_wave_map(t):
    """The on-axis standing-wave field map ``start_write()`` resolved, or None."""
    field = getattr(t.simulation, "field_definition", None)
    if not getattr(field, "read", False):
        return None
    types = [getattr(field, key) for key in ("field_type", "cavity_type")]
    types = [v.decode() if isinstance(v, bytes) else v for v in types]
    return field if types == ["1DElectroDynamic", "StandingWave"] else None


def fourier_coefficients(z, field, ncoef: int = 100) -> tuple:
    """
    ``impactx.fourier_coefficients``: the cosine and sine coefficients of
    ``field`` about the middle of ``z``, by the trapezoidal rule on a uniform
    resampling.
    """
    z = np.asarray(z, dtype=float)
    length = z[-1] - z[0]
    h = length / (len(z) - 1)
    uniform = z[0] + h * np.arange(len(z))
    weights = np.full(len(z), h / (length / 2))
    weights[[0, -1]] /= 2
    angles = np.outer(
        uniform - (z[0] + z[-1]) / 2, 2 * np.pi * np.arange(ncoef) / length
    )
    sampled = np.interp(uniform, z, field) * weights
    return sampled @ np.cos(angles), sampled @ np.sin(angles)


def field_map_cavity(t, ref) -> list | None:
    """
    A thick ``RFCavity`` from a standing-wave field map, or None without one.

    ImpactX pushes the beam through it with a linear map about the reference
    particle: RF focusing, but no RF curvature. The crest must come from
    tracking the reference particle in ImpactX.
    """
    length = t.physical.length
    field = _standing_wave_map(t)
    if field is None:
        return None
    z = np.asarray(field.z_values, dtype=float)
    if abs(z[-1] - z[0] - length) > 1e-3 * length:
        warn(
            f"{t.name}: its field map spans {z[-1] - z[0]:.4g} m of its "
            f"{length:.4g} m; written as a thin ShortRF."
        )
        return None
    cos, sin = fourier_coefficients(z, field.Ez.value.val)
    frequency = float(t.resolve(t.cavity.frequency))
    return [
        {
            "type": "RFCavity",
            "name": t.name,
            "ds": length,
            "escale": float(t.field_amplitude) * abs(ref["charge"]) / ref["mass"],
            "freq": frequency,
            "phase": float(t.cavity.crest) - float(t.phase),
            "cos_coefficients": cos.tolist(),
            "sin_coefficients": sin.tolist(),
            # ImpactX's default of 10 steps gives a third of a TESLA cavity's gain
            "mapsteps": ceil(200 * length * frequency / 299792458.0),
        }
    ]


def build_cavity(t, model, ref) -> list:
    """A thin ``ShortRF`` between half drifts, as MAD-X's ``rfcavity``. ``V``
    is the energy gain over ``m c^2``; crest is phase 0, LAURA's phase negated."""
    kick = {
        "type": "ShortRF",
        "name": t.name,
        "freq": float(t.resolve(t.cavity.frequency)),
        "V": float(t.voltage) * abs(ref["charge"]) / ref["mass"],
        "phase": -float(t.phase),
    }
    return _thin(t, kick, model)


def build_nonlinear_lens(t, model, ref) -> list:
    """A thin IOTA ``NonlinearLens``, MAD-X's ``nllens``."""
    magnetic = t.magnetic
    kick = {
        "type": "NonlinearLens",
        "name": t.name,
        "knll": float(t.resolve(magnetic.integrated_strength)),
        "cnll": float(t.resolve(magnetic.dimensional_parameter)),
    }
    return _thin(t, kick, model)


def build_aperture(t, model, ref) -> list:
    """An ``Aperture``, or a drift between two for a thick element. ImpactX's
    ``dx``/``dy`` place its centre, so they carry the offset; 0 is open."""
    horizontal, vertical = t._half_sizes()
    ox, oy = t._offsets()

    def aperture(name):
        return {
            "type": "Aperture",
            "name": name,
            "aperture_x": horizontal,
            "aperture_y": vertical,
            "shape": "elliptical" if t._elliptical else "rectangular",
            "dx": ox,
            "dy": oy,
        }

    if not t.physical.length:
        return [aperture(t.name)]
    return [
        aperture(f"{t.name}_entry"),
        drift(t.name, t.physical.length, model),
        aperture(f"{t.name}_exit"),
    ]


def build_matrix(t, model, ref) -> list:
    """A ``LinearMap``. LAURA's matrix is in Bmad's (x, px, y, py, z, pz);
    ImpactX's t = -z / beta and pt = -beta pz. ``R`` is a nested list, which
    :func:`lattice` converts for ``from_dicts``."""
    simulation = t.simulation
    dropped = [n for n in "ctu" if np.any(getattr(simulation, f"{n}_matrix"))]
    if dropped:
        warn(
            f"{t.name}: ImpactX's LinearMap is first order; "
            f"the {'/'.join(n.upper() for n in dropped)} matrix was dropped."
        )
    r = np.asarray(simulation.r_matrix, dtype=float)
    off_diagonal = r - np.diag(np.diag(r))
    beta = 1.0
    if "beta_gamma" in ref:
        beta = ref["beta_gamma"] / sqrt(1 + ref["beta_gamma"] ** 2)
    elif off_diagonal[4:].any() or off_diagonal[:, 4:].any():
        warn(f"{t.name}: no energy given; the longitudinal terms assume beta = 1.")
    d = np.array([1, 1, 1, 1, -1 / beta, -beta])
    return [
        {
            "type": "LinearMap",
            "name": t.name,
            "ds": t.physical.length,
            "R": (d[:, None] * r / d).tolist(),
        }
    ]


_PASSIVE = (
    "Drift Marker Screen WireScanner Camera Diagnostic ChargeDiagnostic "
    "Beam_Position_Monitor Beam_Arrival_Monitor Bunch_Length_Monitor "
    "Wall_Current_Monitor Integrated_Current_Transformer Faraday_Cup_Monitor "
    "Photon_Monitor Shutter Valve"
).split()

impactx_conversion_rules = {
    **dict.fromkeys(_PASSIVE, _passive),
    "Dipole": build_dipole,
    "Quadrupole": build_magnet,
    "Sextupole": build_magnet,
    "Octupole": build_magnet,
    "Horizontal_Corrector": build_corrector,
    "Vertical_Corrector": build_corrector,
    "Combined_Corrector": build_corrector,
    "Solenoid": build_solenoid,
    "RFCavity": build_cavity,
    "NonLinearLens": build_nonlinear_lens,
    "Aperture": build_aperture,
    "Collimator": build_aperture,
    "MatrixTransform": build_matrix,
}
"""LAURA ``hardware_type`` -> builder taking the element translator, the
model tier and the :func:`reference` particle."""


def to_dicts(t, model: str, ref: dict, field_maps: bool = False) -> list:
    """``t`` as ImpactX element dicts: its builder's output, with the element's
    alignment and an elliptical bore aperture on every part but drifts. With
    ``field_maps``, a cavity with a standing-wave field map is a
    :func:`field_map_cavity`."""
    builder = impactx_conversion_rules.get(t.hardware_type)
    if builder is None:
        warn(
            f"Element type {t.hardware_type} of {t.name} not supported by ImpactX; using a drift"
        )
        builder = _passive
    parts = field_map_cavity(t, ref) if field_maps and builder is build_cavity else None
    parts = parts or builder(t, model, ref)
    # a bend's rotation rolls its frame, as MAD-X's tilt; a roll error has nowhere to go
    curved = t._curved
    tilt = float(t.resolve(getattr(getattr(t, "magnetic", None), "tilt", 0.0) or 0.0))
    t._warn_dropped_misalignment(
        "ImpactX", {"dx", "dy"} | (set() if curved else {"dz_rot"})
    )
    alignment = {
        "dx": t.dx,
        "dy": t.dy,
        "rotation": degrees(tilt if curved else t.roll),
    }
    bore = None if builder is build_aperture else t._rftrack_aperture_params("ImpactX")
    if bore is not None and bore[2] != "circular":
        warn(
            f"{t.name}: ImpactX element apertures are elliptical; the rectangular bore was dropped."
        )
        bore = None
    for part in parts:
        if part["type"] in ("Marker", *_DRIFTS.values()):
            continue
        for key, value in alignment.items():
            if value:
                part[key] = part.get(key, 0.0) + value
        if bore is not None and part["type"] != "Aperture":
            part["aperture_x"], part["aperture_y"] = bore[:2]
    return parts


def lattice(dicts: list):
    """``dicts`` as an ImpactX ``KnownElementsList``. ``from_dicts`` takes a
    ``LinearMap``'s ``R`` only as an AMReX matrix, which JSON cannot hold."""
    from impactx import Map6x6, elements

    loaded = elements.KnownElementsList()
    loaded.from_dicts(
        [
            # Map6x6 reads a nested list column by column
            (
                {**d, "R": Map6x6(np.transpose(d["R"]).tolist())}
                if d["type"] == "LinearMap"
                else d
            )
            for d in dicts
        ]
    )
    return loaded
