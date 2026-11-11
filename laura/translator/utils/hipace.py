"""HiPACE++ input-file helpers, dependency-free so simba can write inputs without HiPACE++."""

from math import atan, comb, factorial, pi, sqrt
from numbers import Integral, Real
from typing import Sequence

from scipy.constants import c


def number(value: float) -> str:
    """A float as the AMReX parser reads it; ``repr`` of a numpy scalar is not a number."""
    return repr(float(value))


def piecewise_linear(x: str, xs: Sequence[float], ys: Sequence[float]) -> str:
    """
    AMReX parser expression interpolating ``ys`` against ``xs`` linearly in the
    variable or expression ``x``, holding the end values outside -- as ``np.interp``.

    Parameters
    ----------
    x : str
        Expression to interpolate in, e.g. ``"(z-0.001)"``
    xs, ys : Sequence[float]
        Knots, with ``xs`` ascending; repeated ``xs`` give a step

    Returns
    -------
    str
        Nested ``if()`` expression
    """
    expr = number(ys[-1])
    for i in range(len(xs) - 1, 0, -1):
        x0, x1, y0, y1 = xs[i - 1], xs[i], ys[i - 1], ys[i]
        if x1 == x0:
            continue
        segment = f"{number(y0)}+{number(y1 - y0)}*({x}-{number(x0)})/{number(x1 - x0)}"
        expr = f"if({x}<{number(x1)},{segment},{expr})"
    return f"if({x}<{number(xs[0])},{number(ys[0])},{expr})"


def _laguerre(n: int, alpha: int, u: str) -> str:
    """Generalised Laguerre polynomial ``L_n^alpha(u)`` in Horner form."""
    coeffs = [(-1) ** k * comb(n + alpha, n - k) / factorial(k) for k in range(n + 1)]
    expr = number(coeffs[-1])
    for coeff in reversed(coeffs[:-1]):
        expr = f"{number(coeff)}+{u}*({expr})"
    return f"({expr})"


def laser_envelope(
    profile: str,
    a0: float,
    wavelength: float,
    waist: float,
    tau: float,
    center: float,
    focus: float,
    phi2: float = 0.0,
    p: int = 0,
    m: int = 0,
    flatness: int = 6,
) -> tuple[str, str]:
    """
    Real and imaginary parts of a laser envelope at t = 0 as HiPACE++'s
    ``laser_real(x,y,z)`` and ``laser_imag(x,y,z)``: FBPIC's
    ``LaguerreGaussLaser``, ``DonutLikeLaguerreGaussLaser`` and
    ``FlattenedGaussianLaser``, diffraction, Gouy phase and ``phi2`` chirp
    included, less the carrier ``exp(i k0 z)``. Quoted, as the local
    variables' ``=`` would otherwise end the ParmParse value.

    Parameters
    ----------
    profile : str
        ``laguerre-gaussian``, ``laguerre-gaussian-donut`` or ``flattened-gaussian``
    a0 : float
        Peak normalised vector potential, as FBPIC's ``a0``
    wavelength, waist : float
        [m]
    tau : float
        Fourier-limited 1/e field half-width [s]
    center, focus : float
        Pulse centre and focal plane at t = 0, box z [m]
    phi2 : float
        Temporal chirp at focus [s^2]
    p, m : int
        Laguerre-Gauss radial and azimuthal orders
    flatness : int
        Flattened-Gaussian order N

    Returns
    -------
    tuple[str, str]
        Real and imaginary expressions in ``x``, ``y`` and ``z``
    """
    w = waist * sqrt(flatness + 1) if profile == "flattened-gaussian" else waist
    w2 = number(w**2)
    s = 2 * phi2 / tau**2  # FBPIC's stretch factor is 1 - i*s
    head = (
        f"r2 = x^2+y^2; zeta = (z-{number(focus)})/{number(pi * w**2 / wavelength)}; "
        f"d = 1+zeta^2; psi = atan(zeta); u = 2*r2/({w2}*d); "
        f"zl2 = (z-{number(center)})^2/{number((c * tau) ** 2 * (1 + s**2))}; "
    )
    phase = f"r2*zeta/({w2}*d)-zl2*({number(s)})+{number(atan(s) / 2)}"
    qr, qi = "1", "0"
    if profile == "flattened-gaussian":
        scale, gouy = 1.0, 1
        terms = []
        for n in range(flatness + 1):
            cn = sum(0.5**k * comb(k, n) for k in range(n, flatness + 1)) / (flatness + 1)
            terms.append((number(cn), _laguerre(n, 0, "u"), n))
        qr = "+".join(f"{cn}*{lag}*cos({2 * n}*psi)" for cn, lag, n in terms)
        qi = "-(" + "+".join(f"{cn}*{lag}*sin({2 * n}*psi)" for cn, lag, n in terms) + ")"
    elif profile in ("laguerre-gaussian", "laguerre-gaussian-donut"):
        gouy = 1 + 2 * p + m
        qr = f"u^{number(m / 2)}*{_laguerre(p, m, 'u')}" if m else _laguerre(p, 0, "u")
        if profile == "laguerre-gaussian-donut":
            scale = sqrt(factorial(p) / factorial(m + p))
            phase += f"-{m}*atan2(y,x)"
        elif m:
            scale = sqrt(2 * factorial(p) / factorial(m + p))
            qr += f"*cos({m}*atan2(y,x))"
        else:
            scale = 1.0
    else:
        raise ValueError(f"No HiPACE++ parser envelope for laser profile {profile!r}.")
    amplitude = a0 * scale * (1 + s**2) ** -0.25
    head += (
        f"amp = {number(amplitude)}*exp(-r2/({w2}*d)-zl2)/sqrt(d); "
        f"ph = {phase}-{gouy}*psi; qr = {qr}; qi = {qi}; "
    )
    return f'"{head}amp*(qr*cos(ph)-qi*sin(ph))"', f'"{head}amp*(qr*sin(ph)+qi*cos(ph))"'


def write_density_rz(path: str, z, r, density) -> None:
    """
    Write ``density[z, r]`` as the openPMD ``density`` mesh HiPACE++'s
    ``read_density_from_path`` reads. Written with h5py in openPMD-api's own
    layout: ``openpmd_api`` crashes in a process that has imported ROOT.

    Parameters
    ----------
    path : str
        File to write, e.g. ``"stage_density.h5"``
    z, r : np.ndarray
        Evenly spaced grid [m]; HiPACE++ holds the edge values outside it
    density : np.ndarray
        Density [m^-3], shape ``(len(z), len(r))``
    """
    import h5py
    import numpy as np

    with h5py.File(path, "w") as f:
        f.attrs.update({
            "openPMD": np.bytes_("1.1.0"), "openPMDextension": np.uint32(0),
            "basePath": np.bytes_("/data/%T/"), "meshesPath": np.bytes_("meshes/"),
            "iterationEncoding": np.bytes_("groupBased"),
            "iterationFormat": np.bytes_("/data/%T/"), "software": np.bytes_("LAURA"),
        })
        iteration = f.create_group("data/0")
        iteration.attrs.update({"dt": 1.0, "time": 0.0, "timeUnitSI": 1.0})
        mesh = iteration.create_dataset(
            "meshes/density", data=np.ascontiguousarray(density, dtype=float)
        )
        mesh.attrs.update({
            "geometry": np.bytes_("thetaMode"), "axisLabels": np.array([b"z", b"r"]),
            "dataOrder": np.bytes_("C"),
            "gridSpacing": np.array([z[1] - z[0], r[1] - r[0]], dtype=float),
            "gridGlobalOffset": np.array([z[0], r[0]], dtype=float), "gridUnitSI": 1.0,
            "position": np.zeros(2), "timeOffset": np.float32(0.0),
            "unitDimension": np.array([-3.0, 0, 0, 0, 0, 0, 0]), "unitSI": 1.0,
        })


def hipace_inputs(params: dict) -> str:
    """
    Render ``{key: value}`` as a HiPACE++ inputs file: lists space-separated,
    booleans as 0/1, strings (parser expressions included) verbatim.

    Parameters
    ----------
    params : dict
        Input parameters, e.g. from :func:`~laura.translator.converters.plasma.PlasmaTranslator.to_hipace`

    Returns
    -------
    str
        Inputs-file text
    """

    def fmt(value) -> str:
        if isinstance(value, (list, tuple)):
            return " ".join(fmt(v) for v in value)
        if isinstance(value, Integral):  # bool included
            return str(int(value))
        if isinstance(value, Real):
            return number(value)
        return str(value)

    return "".join(f"{key} = {fmt(value)}\n" for key, value in params.items())
