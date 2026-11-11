"""
On-axis field maps as analytic expressions, for codes that take fields as
functions of position and time rather than as files (WarpX's particle fields).

A 1D map ``f(z)`` becomes a cosine series on its own range (:class:`Profile`),
and the off-axis field follows from the first-order paraxial expansion, as in
ASTRA and GPT's ``map1D`` elements::

    static:  F_z = A f,          F_x = -(x/2) A f',  F_y = -(y/2) A f'
    RF:      E_z = A f cos(wt+p), E_x = -(x/2) A f' cos(wt+p),
             B_x = (y w / 2c^2) A f sin(wt+p),  B_y = -(x w / 2c^2) A f sin(wt+p)

:func:`autophase` finds each cavity's crest by tracking the reference particle
along the axis, cavity by cavity.
"""

from dataclasses import dataclass, field
from typing import Literal, Sequence

import numpy as np
from scipy.constants import c

from ..hipace import number


@dataclass
class Profile:
    """``f(z)`` on ``[z0, z0 + length]`` as ``sum a_n cos(n pi u)``, ``u = (z - z0) / length``; zero outside."""

    z0: float
    length: float
    a: np.ndarray

    @classmethod
    def fit(cls, z: Sequence[float], f: Sequence[float], tol: float = 1e-3, max_terms: int = 4000) -> "Profile":
        """
        The fewest cosine terms that reproduce the samples to ``tol`` of the peak.

        Parameters
        ----------
        z, f : Sequence[float]
            Samples of the profile, ``z`` increasing
        tol : float
            Largest error at the samples, relative to the peak of ``f``
        max_terms : int
            Most terms to keep, whatever the error; never more than the samples,
            past which the series only follows the kinks of their interpolation

        Returns
        -------
        Profile
        """
        from scipy.fft import dct

        z, f = np.asarray(z, dtype=float), np.asarray(f, dtype=float)
        max_terms = min(max_terms, len(z))
        n = max(4 * len(z), 2 * max_terms)
        u = (np.arange(n) + 0.5) / n
        a = dct(np.interp(z[0] + u * (z[-1] - z[0]), z, f), type=2) / (2 * n)
        a[1:] *= 2  # a_0 is the mean
        basis = np.cos(np.pi * np.outer((z - z[0]) / (z[-1] - z[0]), np.arange(max_terms)))
        lo, hi = 1, max_terms  # fewest terms within tol, by bisection
        while lo < hi:
            mid = (lo + hi) // 2
            if np.abs(basis[:, :mid] @ a[:mid] - f).max() <= tol * np.abs(f).max():
                hi = mid
            else:
                lo = mid + 1
        return cls(float(z[0]), float(z[-1] - z[0]), a[:lo])

    def _u(self, z):
        return (np.asarray(z, dtype=float) - self.z0) / self.length

    def __call__(self, z) -> np.ndarray:
        u = self._u(z)
        n = np.arange(len(self.a))
        values = np.cos(np.pi * np.multiply.outer(u, n)) @ self.a
        return np.where((u >= 0) & (u <= 1), values, 0.0)

    def derivative(self, z) -> np.ndarray:
        """``df/dz``"""
        u = self._u(z)
        k = np.pi * np.arange(len(self.a)) / self.length
        values = -np.sin(np.pi * np.multiply.outer(u, np.arange(len(self.a)))) @ (self.a * k)
        return np.where((u >= 0) & (u <= 1), values, 0.0)

    def statements(self, name: str, z: str) -> str:
        """Parser statements setting ``<name>`` to f and ``<name>_d`` to f' at ``z``."""
        u = f"u_{name}"
        cos = "+".join(f"{number(a)}*cos({n}*pi*{u})" for n, a in enumerate(self.a))
        sin = "+".join(f"{number(-a * n * np.pi / self.length)}*sin({n}*pi*{u})"
                       for n, a in enumerate(self.a) if n)
        gate = f"if({u}<0,0,if({u}>1,0,1))"
        return (f"{u} = ({z}-{number(self.z0)})/{number(self.length)}; "
                f"{name} = {gate}*({cos}); {name}_d = {gate}*({sin or 0}); ")


@dataclass
class FieldTerm:
    """One map's contribution: ``amplitude * profile(z - z)``, static or RF."""

    profile: Profile
    amplitude: float
    """Peak field [V/m or T]"""
    kind: Literal["E", "B"]
    z: float
    """Code z of the profile's z = 0 [m]"""
    x: float = 0.0
    y: float = 0.0
    """Transverse position of the axis [m]"""
    frequency: float = 0.0
    """RF frequency [Hz]; RF fields are ``E`` and carry their ``B``"""
    phase: float = 0.0
    """Fixed phase of this term within its cavity [rad], e.g. pi/2 for a travelling wave's second wave"""
    off_crest: float = 0.0
    """The cavity's phase from crest [rad]; RF fields go as ``cos(w t + phase + crest + off_crest)``"""
    group: str | None = None
    """Cavity the term belongs to: its terms share one crest"""
    crest: float = field(default=0.0)
    """Crest phase [rad], set by :func:`autophase`"""

    @property
    def total_phase(self) -> float:
        return self.phase + self.crest + self.off_crest

    def on_axis(self, z, t) -> np.ndarray:
        """``E_z`` on the axis [V/m]; zero for a magnetic term."""
        if self.kind == "B":
            return np.zeros_like(np.asarray(z, dtype=float))
        value = self.amplitude * self.profile(np.asarray(z) - self.z)
        if self.frequency:
            value = value * np.cos(2 * np.pi * self.frequency * t + self.total_phase)
        return value


K_PER_TESLA_METRE = 93.3728962
"""Undulator ``K = e B0 lambda_u / (2 pi m_e c)`` per tesla-metre of ``B0 lambda_u``."""


@dataclass
class UndulatorTerm:
    """
    An ideal undulator of ``length`` from code z ``z``, starting on a cosine so that
    whole periods leave no net kick. Planar: the vacuum
    field ``B_y = B0 cosh(k y) cos(k s)``, ``B_z = -B0 sinh(k y) sin(k s)``, which
    carries the natural vertical focusing. Helical: ``B0 (cos, sin)(k s)`` with the
    first-order ``B_z``.
    """

    peak_field: float
    """Peak field per component [T]"""
    period: float
    length: float
    z: float
    x: float = 0.0
    y: float = 0.0
    helical: bool = False
    kind: Literal["B"] = "B"
    frequency: float = 0.0
    amplitude: float = 0.0  # no E_z on the axis, for track()
    group: str | None = None

    def on_axis(self, z, t) -> np.ndarray:
        return np.zeros_like(np.asarray(z, dtype=float))

    def components(self, name: str) -> tuple[str, dict]:
        """Parser statements and ``{component: expression}`` of this term."""
        k, b = number(2 * np.pi / self.period), number(self.peak_field)
        s, dx, dy = f"s_{name}", f"(x-{number(self.x)})", f"(y-{number(self.y)})"
        head = (f"{s} = z-{number(self.z)}; "
                f"{name} = if({s}<0,0,if({s}>{number(self.length)},0,1)); ")
        if self.helical:
            return head, {
                "Bx": f"{name}*{b}*cos({k}*{s})",
                "By": f"{name}*{b}*sin({k}*{s})",
                "Bz": f"{name}*{b}*{k}*({dy}*cos({k}*{s})-{dx}*sin({k}*{s}))",
            }
        return head, {
            "By": f"{name}*{b}*cosh({k}*{dy})*cos({k}*{s})",
            "Bz": f"-{name}*{b}*sinh({k}*{dy})*sin({k}*{s})",
        }


@dataclass
class CurrentSheetTerm:
    """
    The solenoid of a current sheet of ``length`` and ``radius`` centred on code z ``z``, in
    closed form: ``B_z = B0 g(s) / g(0)``, ``g(s) = (s + L/2)/sqrt((s + L/2)^2 + R^2) - (s - L/2)/sqrt(...)``,
    with the first-order ``B_x, B_y = -(x, y)/2 dB_z/ds``. Exactly the map
    :meth:`~laura.translator.converters.magnet.SolenoidTranslator._field_map` samples, at a few
    operations a particle instead of the hundreds of terms a Fourier series of it needs.
    """

    peak_field: float
    """``B_z`` at the centre [T]"""
    length: float
    radius: float
    z: float
    x: float = 0.0
    y: float = 0.0
    kind: Literal["B"] = "B"
    frequency: float = 0.0
    amplitude: float = 0.0  # no E_z on the axis, for track()
    group: str | None = None

    def on_axis(self, z, t) -> np.ndarray:
        return np.zeros_like(np.asarray(z, dtype=float))

    def components(self, name: str) -> tuple[str, dict]:
        """Parser statements and ``{component: expression}`` of this term."""
        h, r2 = self.length / 2, self.radius**2
        b = number(self.peak_field / (2 * h / np.sqrt(h**2 + r2)))  # B0 / g(0)
        s, p, m = f"s_{name}", f"p_{name}", f"m_{name}"
        head = (f"{s} = z-{number(self.z)}; {p} = {s}+{number(h)}; {m} = {s}-{number(h)}; "
                f"{name} = {b}*({p}/sqrt({p}*{p}+{number(r2)})-{m}/sqrt({m}*{m}+{number(r2)})); "
                f"{name}_d = {b}*{number(r2)}*(1/({p}*{p}+{number(r2)})^1.5-1/({m}*{m}+{number(r2)})^1.5); ")
        dx, dy = f"(x-{number(self.x)})", f"(y-{number(self.y)})"
        return head, {"Bz": name, "Bx": f"-0.5*{dx}*{name}_d", "By": f"-0.5*{dy}*{name}_d"}


@dataclass
class MultipoleTerm:
    """
    A hard-edged normal multipole of ``order`` n over ``length`` from code z ``z``:
    ``B_y + i B_x = coefficient (x + i y)^n``, so that ``coefficient = Brho K_n / n!`` gives
    MAD-X's kick of ``(x' - i y')`` by ``-K_n L (x + i y)^n / n!`` (n = 1 is a quadrupole of gradient
    ``coefficient``). No fringe field.
    """

    order: int
    coefficient: float
    """[T / m^n]"""
    length: float
    z: float
    x: float = 0.0
    y: float = 0.0
    kind: Literal["B"] = "B"
    frequency: float = 0.0
    amplitude: float = 0.0  # no E_z on the axis, for track()
    group: str | None = None

    def on_axis(self, z, t) -> np.ndarray:
        return np.zeros_like(np.asarray(z, dtype=float))

    def components(self, name: str) -> tuple[str, dict]:
        """Parser statements and ``{component: expression}`` of this term."""
        from math import comb

        n, s, u, v = self.order, f"s_{name}", f"u_{name}", f"v_{name}"
        head = (f"{s} = z-{number(self.z)}; {u} = x-{number(self.x)}; {v} = y-{number(self.y)}; "
                f"{name} = {number(self.coefficient)}*if({s}<0,0,if({s}>{number(self.length)},0,1)); ")
        # (u + i v)^n = sum_k C(n, k) u^(n-k) (i v)^k: even k real, odd k imaginary, i^k giving the sign
        terms = {0: [], 1: []}
        for k in range(n + 1):
            sign = -1 if (k // 2) % 2 else 1
            terms[k % 2].append(f"{sign * comb(n, k)}*{u}^{n - k}*{v}^{k}")
        return head, {"By": f"{name}*({'+'.join(terms[0])})", "Bx": f"{name}*({'+'.join(terms[1])})"}


def render(terms: Sequence[FieldTerm | UndulatorTerm | CurrentSheetTerm | MultipoleTerm]) -> dict:
    """
    WarpX ``particles.*_external_particle_function(x,y,z,t)`` inputs for ``terms``,
    each quoted so its local variables survive ParmParse.

    Returns
    -------
    dict
        ``{input key: value}``; empty without terms
    """
    parts = {k: [] for k in ("Ex", "Ey", "Ez", "Bx", "By", "Bz")}
    head = ""
    for i, term in enumerate(terms):
        name = f"f{i}"
        if hasattr(term, "components"):  # a closed-form term writes its own components
            statements, components = term.components(name)
            head += statements
            for key, expr in components.items():
                parts[key].append(expr)
            continue
        head += term.profile.statements(name, f"(z-{number(term.z)})")
        a = number(term.amplitude)
        dx, dy = f"(x-{number(term.x)})", f"(y-{number(term.y)})"
        if term.frequency:
            w = 2 * np.pi * term.frequency
            arg = f"({number(w)}*t+{number(term.total_phase)})"
            parts["Ez"].append(f"{a}*{name}*cos{arg}")
            parts["Ex"].append(f"-0.5*{dx}*{a}*{name}_d*cos{arg}")
            parts["Ey"].append(f"-0.5*{dy}*{a}*{name}_d*cos{arg}")
            b = number(term.amplitude * w / (2 * c**2))
            parts["Bx"].append(f"{dy}*{b}*{name}*sin{arg}")
            parts["By"].append(f"-{dx}*{b}*{name}*sin{arg}")
        else:
            k = term.kind
            parts[f"{k}z"].append(f"{a}*{name}")
            parts[f"{k}x"].append(f"-0.5*{dx}*{a}*{name}_d")
            parts[f"{k}y"].append(f"-0.5*{dy}*{a}*{name}_d")
    params = {}
    for k in "EB":
        if any(parts[f"{k}{d}"] for d in "xyz"):
            params[f"particles.{k}_ext_particle_init_style"] = f"parse_{k}_ext_particle_function"
            for d in "xyz":
                params[f"particles.{k}{d}_external_particle_function(x,y,z,t)"] = (
                    f'"{head}{"+".join(parts[f"{k}{d}"]) or 0}"'
                )
    return params


def track(terms: Sequence[FieldTerm], z0: float, p0c: float, rest_energy: float,
          charge_sign: int, z_end: float) -> tuple[float, float]:
    """
    The reference particle along the axis from ``z0`` at t = 0 to ``z_end``,
    through the electric terms' ``E_z`` only (nothing else acts on the axis).

    Parameters
    ----------
    z0, z_end : float
        Start and end [m]
    p0c, rest_energy : float
        Momentum and rest energy [eV]
    charge_sign : int
        Sign of the particle's charge

    Returns
    -------
    tuple[float, float]
        Arrival time [s] and kinetic energy [eV] at ``z_end``; the energy is
        ``-inf`` if the particle stops first
    """
    from scipy.integrate import solve_ivp

    if z_end <= z0:
        raise ValueError(f"The reference particle starts at z = {z0} m, past the end z = {z_end} m.")
    active = [t for t in terms if t.kind == "E" and t.amplitude]

    def rhs(t, y):  # y = (z, pc [eV])
        energy = np.hypot(y[1], rest_energy)
        return [c * y[1] / energy, charge_sign * c * sum(term.on_axis(y[0], t) for term in active)]

    def arrived(t, y):
        return y[0] - z_end
    arrived.terminal, arrived.direction = True, 1

    def stopped(t, y):
        return y[1]
    stopped.terminal = True

    beta0 = p0c / np.hypot(p0c, rest_energy)
    t_max = 100 * (z_end - z0) / (beta0 * c) + 1e-9
    out = solve_ivp(rhs, (0.0, t_max), [z0, p0c], events=(arrived, stopped),
                    rtol=1e-10, atol=[1e-12, 1e-6], max_step=(z_end - z0) / (beta0 * c) / 200)
    if not len(out.t_events[0]):
        return float(out.t[-1]), -np.inf
    return float(out.t_events[0][0]), float(np.hypot(out.y_events[0][0][1], rest_energy) - rest_energy)


def autophase(terms: Sequence[FieldTerm], z0: float, p0c: float, rest_energy: float,
              charge_sign: int) -> dict[str, float]:
    """
    Set each cavity's crest, in beamline order, to the phase of most energy gain
    by the reference particle at its exit, the cavities before it at their own
    phase and those after it off.

    Returns
    -------
    dict[str, float]
        ``{cavity: crest [rad]}``
    """
    from scipy.optimize import minimize_scalar

    terms = [t for t in terms if isinstance(t, FieldTerm)]
    groups = []
    for term in terms:
        if term.frequency and term.group not in groups:
            groups.append(term.group)
    exit_z = {g: max(t.z + t.profile.z0 + t.profile.length for t in terms if t.group == g) for g in groups}
    groups.sort(key=exit_z.get)
    crests = {}
    for i, group in enumerate(groups):
        mine = [t for t in terms if t.group == group]
        before = [t for t in terms if t.group in groups[:i]]
        off_crest = [t.off_crest for t in mine]
        for t in mine:
            t.off_crest = 0.0  # the crest is the phase of most gain on crest

        def gain(crest):
            for t in mine:
                t.crest = crest
            return track(before + mine, z0, p0c, rest_energy, charge_sign, exit_z[group])[1]

        scan = np.linspace(-np.pi, np.pi, 24, endpoint=False)
        best = scan[int(np.argmax([gain(p) for p in scan]))]
        step = scan[1] - scan[0]
        found = minimize_scalar(lambda p: -gain(p), bounds=(best - step, best + step),
                                method="bounded", options={"xatol": 1e-6})
        crests[group] = float(found.x)
        for t, phase in zip(mine, off_crest):
            t.crest, t.off_crest = crests[group], phase
    return crests
