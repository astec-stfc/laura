"""
Multi-component (Taylor) wake tables, the format of Zagorodnov's ECHO codes that
ASTRA (``Wk_Type = 'Taylor_Method_F'``) and Ocelot (``WakeTable``) read.

A table is a list of :class:`WakeComponent`. Each component has a sampled wake
``W0`` convolved with the bunch current, a sampled wake ``W1`` convolved with
the derivative of the current, and lumped resistive, inductive and capacitive
terms. Its ``nm`` says how it scales with the transverse offsets of the source
and the witness particle, one digit each: 0 none, 1 source
x, 2 source y, 3 witness x, 4 witness y; so 00 is the longitudinal wake, 13 and
24 the dipole wakes, and 11, 22, 33, ... the quadrupole terms.

The file layout is ``Nt 0``, then per component ``N0 N1`` / ``R L`` /
``Cinv nm`` followed by the ``N0`` rows of ``W0`` and the ``N1`` rows of
``W1``, two columns each (s [m], wake).
"""

import numpy as np
from pydantic import BaseModel, ConfigDict

from laura.models.constants import speed_of_light

HDF5_GROUP = "wake_component_{}"
"""Name of the HDF5 group holding component ``i`` of a ``TaylorWake``."""

DIPOLE_FACTOR = -2 * speed_of_light
"""A ``3DWake`` dipole wake ``Wx`` [V/C/m] is ``DIPOLE_FACTOR * W1`` of component 13
(``Wy``: 24)."""

MAX_POINTS = 10**6
"""Most samples :func:`to_3d_wake` will put on its one uniform grid."""


class WakeComponent(BaseModel):
    """One component of a Taylor wake table, in the units of the table itself."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    nm: int
    """Offset dependence: one digit per offset (0 none, 1/2 source x/y, 3/4 witness x/y)."""

    R: float = 0.0
    """Resistive term, applied as ``-R * I``."""

    L: float = 0.0
    """Inductive term, applied as ``L * c * dI/ds``."""

    Cinv: float = 0.0
    """Capacitive term (inverse capacitance), applied as ``-Cinv * integral(I) / c``."""

    W0: np.ndarray | None = None
    """``(N0, 2)`` array of s [m] and the wake convolved with the current, or None."""

    W1: np.ndarray | None = None
    """``(N1, 2)`` array of s [m] and the wake convolved with ``dI/ds``, or None."""

    def __eq__(self, other) -> bool:
        if not isinstance(other, WakeComponent):
            return NotImplemented

        def same(a, b):
            return (a is None and b is None) or (
                a is not None and b is not None and np.array_equal(a, b)
            )

        return (
            (self.nm, self.R, self.L, self.Cinv)
            == (other.nm, other.R, other.L, other.Cinv)
            and same(self.W0, other.W0)
            and same(self.W1, other.W1)
        )


def _rows(table) -> int:
    return 0 if table is None else len(table)


def from_table(data: np.ndarray) -> list[WakeComponent]:
    """
    The components of a Taylor wake table, as read by ``np.loadtxt``.

    Raises
    ------
    ValueError
        if the table is shorter or longer than its headers say
    """
    data = np.atleast_2d(np.asarray(data, dtype=float))
    components, row = [], 1
    for _ in range(int(data[0, 0])):
        if row + 3 > len(data):
            raise ValueError("Taylor wake table ends inside a component header")
        (n0, n1), (r, ell), (cinv, nm) = data[row : row + 3]
        n0, n1, row = int(n0), int(n1), row + 3
        if row + n0 + n1 > len(data):
            raise ValueError(
                f"Taylor wake component {int(nm)} has fewer rows than {n0} + {n1}"
            )
        w0 = data[row : row + n0].copy() if n0 else None
        w1 = data[row + n0 : row + n0 + n1].copy() if n1 else None
        components.append(
            WakeComponent(nm=int(nm), R=r, L=ell, Cinv=cinv, W0=w0, W1=w1)
        )
        row += n0 + n1
    if row != len(data):
        raise ValueError(
            f"Taylor wake table has {len(data) - row} rows after its last component"
        )
    return components


def to_table(components: list[WakeComponent]) -> np.ndarray:
    """The two-column table of `components`, the inverse of :func:`from_table`."""
    blocks = [np.array([[len(components), 0]], dtype=float)]
    for c in components:
        blocks.append(
            np.array(
                [[_rows(c.W0), _rows(c.W1)], [c.R, c.L], [c.Cinv, c.nm]], dtype=float
            )
        )
        blocks += [np.asarray(w, dtype=float) for w in (c.W0, c.W1) if w is not None]
    return np.concatenate(blocks)


def from_3d_wake(z, wz, wx, wy) -> list[WakeComponent]:
    """The components of a LAURA ``3DWake`` (see :func:`to_3d_wake`): 00 from ``Wz``, 13/24 from ``Wx``/``Wy``."""
    z = np.asarray(z, dtype=float)

    def table(w, factor=1.0):
        return np.column_stack([z, np.asarray(w, dtype=float) / factor])

    return [
        WakeComponent(nm=0, W0=table(wz)),
        WakeComponent(nm=13, W1=table(wx, DIPOLE_FACTOR)),
        WakeComponent(nm=24, W1=table(wy, DIPOLE_FACTOR)),
    ]


def _at_zero(table) -> float:
    return (
        0.0
        if table is None
        else float(np.interp(0.0, table[:, 0], table[:, 1], 0.0, 0.0))
    )


def to_3d_wake(
    components: list[WakeComponent],
) -> tuple[np.ndarray, dict[str, np.ndarray]]:
    """
    The wake of `components` as a LAURA ``3DWake`` holds it: Green functions on one
    uniform grid from s = 0, ``Wz`` [V/C] positive for an energy loss, and the dipole
    wakes ``Wx``/``Wy`` [V/C/m] positive for a kick towards the source's offset.

    Returns
    -------
    tuple[np.ndarray, dict[str, np.ndarray]]
        s [m], and ``Wz`` with ``Wx`` and ``Wy`` too if either dipole is present.

    Raises
    ------
    ValueError
        if the finest table spacing would need more than :data:`MAX_POINTS` samples
    """
    tables = [
        w[:, 0]
        for c in components
        for w in (c.W0, c.W1)
        if w is not None and len(w) > 1
    ]
    step = min(np.diff(s)[np.diff(s) > 0].min() for s in tables)
    end = max(s[-1] for s in tables)
    n = int(round(end / step)) + 1
    if n > MAX_POINTS:
        raise ValueError(
            f"A uniform wake grid down to {step} m over {end} m needs {n} points"
        )
    z = np.linspace(0.0, end, n)

    def on_grid(table):
        return (
            np.zeros(n)
            if table is None
            else np.interp(z, table[:, 0], table[:, 1], 0.0, 0.0)
        )

    def integral(w):
        return np.concatenate([[0.0], np.cumsum(0.5 * (w[1:] + w[:-1]) * np.diff(z))])

    wakes = {}
    for c in components:
        w0, w1 = on_grid(c.W0), on_grid(c.W1)
        if c.nm == 0:
            # by parts, W1 * dI/ds is the slope of W1 times I, plus a point term at s = 0
            wakes["Wz"] = w0 - speed_of_light * np.gradient(w1, z) + c.Cinv
        elif c.nm in (13, 24):
            # the kick integrates the longitudinal term, so W1 and R come out unchanged
            wakes["Wx" if c.nm == 13 else "Wy"] = (
                DIPOLE_FACTOR * (w1 - c.R) + 2 * integral(w0) + 2 * c.Cinv * z
            )
    wakes.setdefault("Wz", np.zeros(n))
    if "Wx" in wakes or "Wy" in wakes:
        wakes.setdefault("Wx", np.zeros(n))
        wakes.setdefault("Wy", np.zeros(n))
    return z, wakes


def dropped_parts(components: list[WakeComponent]) -> list[str]:
    """What :func:`to_3d_wake` cannot hold: point terms at s = 0, and every component but 00, 13 and 24."""
    dropped = []
    for c in components:
        if c.nm not in (0, 13, 24):
            dropped.append(f"component {c.nm:02d}")
            continue
        point = speed_of_light * (c.R - _at_zero(c.W1))
        if c.nm == 0 and point:
            dropped.append(f"00: a point wake of {point:.3g} V m/C at s = 0")
        if c.L:
            dropped.append(f"{c.nm:02d}: the inductive term L = {c.L:.3g}")
    return dropped


def write_hdf5(h5file, components: list[WakeComponent]) -> None:
    """Write `components` to `h5file`, one group each, with ``nm, R, L, Cinv`` as attributes."""
    for i, c in enumerate(components):
        group = h5file.create_group(HDF5_GROUP.format(i))
        for key in ("nm", "R", "L", "Cinv"):
            group.attrs[key] = getattr(c, key)
        for key in ("W0", "W1"):
            if getattr(c, key) is not None:
                group.create_dataset(key, data=getattr(c, key))


def read_hdf5(h5file) -> list[WakeComponent] | None:
    """The components :func:`write_hdf5` wrote to `h5file`, or None if there are none."""
    components, i = [], 0
    while HDF5_GROUP.format(i) in h5file:
        group = h5file[HDF5_GROUP.format(i)]
        components.append(
            WakeComponent(
                nm=int(group.attrs["nm"]),
                **{k: float(group.attrs[k]) for k in ("R", "L", "Cinv")},
                **{k: group[k][()] for k in ("W0", "W1") if k in group},
            )
        )
        i += 1
    return components or None
