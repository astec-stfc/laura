"""Demonstrate LAURA sequential (drift-based) placement.

A section can leave every position unstated and let the order plus the
lengths do the work::

    sections:
      INJ_LINE: [GUN_CAVITY, INJ_DRIFT_LONG, INJ_QUAD_01, ...]

which is how MAD-X, elegant and PALS define a lattice. LAURA normalises such
a section to ``s`` during assembly, so from that point on a hand-written drift
lattice and an imported MAD-X one take the identical path -- the same bend arc
geometry, the same trajectory, the same exports.

Four things this example is meant to show:

  1. That order and length alone place the line, and that ``s`` is left on the
     elements afterwards as a real, inspectable value.
  2. That hand-written drifts stay elements, and that a drift reused three
     times becomes three separately-placed elements.
  3. That a line can be anchored somewhere other than the origin, and what
     happens when a stated position mid-line disagrees with the drifts.
  4. That the answer matches the same lattice written out with explicit ``s``
     -- including through a bend, where the two could easily disagree.

Run from the repository root::

    python examples/testing/sequential_example.py
"""

from __future__ import annotations

import sys
import warnings
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import numpy as np  # noqa: E402

from laura import LAURA  # noqa: E402
from laura.models.element import Dipole, Drift, Quadrupole  # noqa: E402
from laura.models.elementList import MachineModel  # noqa: E402

# -- file paths ----------------------------------------------------------------

EXAMPLES = ROOT / "examples" / "testing"
ELEMENTS = EXAMPLES / "sequential_elements.yaml"
SECTIONS = EXAMPLES / "sequential_sections.yaml"
LAYOUTS = EXAMPLES / "sequential_layouts.yaml"


# -- helpers -------------------------------------------------------------------


def _sep(title: str) -> None:
    width = 74
    print()
    print("=" * width)
    print(f"  {title}")
    print("=" * width)


def _load() -> tuple[LAURA, list[str]]:
    with warnings.catch_warnings(record=True) as records:
        warnings.simplefilter("always")
        machine = LAURA(
            element_list=str(ELEMENTS),
            section=str(SECTIONS),
            layout=str(LAYOUTS),
        )
    return machine, [str(r.message) for r in records]


def _quad(name, length=0.1, **physical):
    return Quadrupole(
        name=name, hardware_class="Magnet", machine_area="S",
        magnetic={"magnetic_length": length, "k1l": 0.1},
        physical={"length": length, **physical},
    )


def _drift(name, length, **physical):
    return Drift(
        name=name, hardware_class="Drift", machine_area="S",
        physical={"length": length, **physical},
    )


def _bend(name, length=1.0, angle=0.3, **physical):
    return Dipole(
        name=name, hardware_class="Magnet", machine_area="S",
        magnetic={"magnetic_length": length, "k0l": angle},
        physical={"length": length, **physical},
    )


def _machine(elements, order=None):
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", message="No layouts")
        return MachineModel(
            elements={e.name: e for e in elements},
            section={"sections": {"S": {"elements": order or [e.name for e in elements]}}},
        )


# -- section 1: the line places itself ------------------------------------------


def demo_placement(machine: LAURA, order: list[str]) -> None:
    _sep("1. Order and length are enough")
    print("""
  Nothing in sequential_elements.yaml states a position. Each element's s and
  world position below were accumulated from the lengths, in section order.
""")
    print(f"  {'Element':<22} {'len [m]':>8} {'s [m]':>8} {'middle.z [m]':>14}")
    print(f"  {'-' * 22} {'-' * 8} {'-' * 8} {'-' * 14}")
    total = 0.0
    for name in order:
        phys = machine[name].physical
        total += phys.length
        print(
            f"  {name:<22} {phys.length:>8.3f} {phys.s:>8.3f} "
            f"{phys.middle.z:>14.3f}"
        )
    print(f"\n  total length: {total:.3f} m")
    print("""
  Before this existed, a section like that resolved with every element
  sitting on top of the others at the origin -- a valid lattice, silently
  wrong, which is the worst combination.
""")


# -- section 2: drifts, and repeated ones ---------------------------------------


def demo_drifts(machine: LAURA, order: list[str], messages: list[str]) -> None:
    _sep("2. Drifts are elements, and a repeated one is split")
    print("""
  The importers consume drifts: the length goes into s and the element is
  discarded. A hand-written drift is kept instead -- you named it, so
  machine["INJ_DRIFT_LONG"] has to resolve.
""")
    drifts = [n for n in order if "DRIFT" in n]
    print(f"  drifts in the machine: {drifts}")
    print("""
  INJ_DRIFT_SHORT was listed three times. A machine model holds one placement
  per name, so each occurrence became its own element rather than three
  placements fighting over one name:
""")
    for name in drifts:
        if "SHORT" in name:
            print(f"    {name:<24} s = {machine[name].physical.s:.3f} m")
    for message in messages:
        if "Repeated element names" in message:
            print(f"\n  It says so, too:\n    {message}")


# -- section 3: anchoring -------------------------------------------------------


def demo_anchoring() -> None:
    _sep("3. Anchoring the line somewhere other than the origin")
    print("""
  The first element to state an s anchors the line; the rest accumulate from
  its exit.
""")
    anchored = _machine([
        _quad("Q1", 0.1, s=12.0, s_point="start"),
        _drift("D1", 0.5),
        _quad("Q2"),
    ])
    for name in ("Q1", "D1", "Q2"):
        print(f"    {name:<4} s = {anchored.elements[name].physical.s:7.3f} m")

    print("""
  An s stated mid-line re-anchors everything after it. When it disagrees with
  what the drifts before it add up to, the stated value wins and LAURA says
  so, because the drift lengths and the stated position are then telling two
  different stories:
""")
    with warnings.catch_warnings(record=True) as records:
        warnings.simplefilter("always")
        disagreeing = _machine([
            _quad("Q1"), _drift("D1", 0.5),
            _quad("Q2", 0.1, s=5.0, s_point="start"), _quad("Q3"),
        ])
    for record in records:
        if "accumulate" in str(record.message):
            print(f"    {record.message}")
    print()
    for name in ("Q1", "D1", "Q2", "Q3"):
        print(f"    {name:<4} s = {disagreeing.elements[name].physical.s:7.3f} m")

    print("""
  The anchor must use s, not xyz: converting a stated world position back
  into an arc length needs the design trajectory, which does not exist until
  placement has run. Anchoring with 'middle' is refused rather than guessed:
""")
    try:
        _machine([_quad("Q1", 0.1, middle=[0, 0, 12.0]), _drift("D1", 0.5),
                  _quad("Q2")])
    except ValueError as error:
        print(f"    ValueError: {error}")


# -- section 4: it agrees with the explicit form --------------------------------


def demo_oracle() -> None:
    _sep("4. The same lattice written with explicit s lands in the same place")
    print("""
  This is the check that matters, and it holds through a bend, where an
  approximate chord would show up immediately. Both forms are resolved by the
  same integrator -- that is the reason a sequential section is normalised to
  s rather than given a coordinate system of its own.
""")
    line = [("quad", "Q1", 0.1), ("drift", "D1", 0.5), ("bend", "B1", 1.0),
            ("drift", "D2", 0.5), ("quad", "Q2", 0.1)]
    makers = {"quad": _quad, "drift": _drift, "bend": _bend}

    def build(explicit: bool):
        elements, cumulative = [], 0.0
        for kind, name, length in line:
            cumulative += length
            extra = {"s": cumulative, "s_point": "end"} if explicit else {}
            elements.append(makers[kind](name, length, **extra))
        return _machine(elements)

    sequential, explicit = build(False), build(True)
    print(f"  {'Element':<10} {'s [m]':>8} {'x [m]':>10} {'z [m]':>10} {'|diff| [m]':>12}")
    print(f"  {'-' * 10} {'-' * 8} {'-' * 10} {'-' * 10} {'-' * 12}")
    for _, name, _ in line:
        a = sequential.elements[name].physical
        b = explicit.elements[name].physical
        diff = float(np.linalg.norm(np.array(a.middle.array) - np.array(b.middle.array)))
        print(
            f"  {name:<10} {a.s:>8.3f} {a.middle.x:>10.6f} {a.middle.z:>10.6f} "
            f"{diff:>12.1e}"
        )
    print("""
  The bend curves the line: Q2 ends up off-axis in x and short of its arc
  length in z. Both forms agree exactly.
""")


# -- main ----------------------------------------------------------------------


def main() -> None:
    machine, messages = _load()
    order = machine.sections["INJ_LINE"].order

    demo_placement(machine, order)
    demo_drifts(machine, order, messages)
    demo_anchoring()
    demo_oracle()

    _sep("Summary")
    print("""
  * A section with no stated positions is placed from its order and lengths.
  * Hand-written drifts stay elements; a repeated one is split per occurrence.
  * The first stated s anchors the line; a later one re-anchors and warns on
    disagreement; an xyz anchor is refused rather than guessed.
  * The result is identical to the same lattice written with explicit s.
""")


if __name__ == "__main__":
    main()
