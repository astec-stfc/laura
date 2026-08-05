"""Demonstrate LAURA element positioning modes.

Three positioning modes are available for physical elements:

  1. Global Cartesian (``middle: {x, y, z}``) -- explicit world coordinates.
  2. s-coordinate (``s: <float>``) -- arc-length along the design trajectory;
     LAURA integrates the orbit to resolve global xyz.
  3. reference_placement -- position relative to another element's frame,
     with three offset styles:
       * ``s_offset``    -- scalar along local beam direction.
       * ``offset``      -- 3-D vector in the reference element's local frame.
       * ``world_offset``-- 3-D vector in the global frame.

After lattice assembly LAURA always exposes:
  * ``element.physical.middle``  -- resolved global position (Position object)
  * ``element.physical.s``       -- arc-length along the design trajectory [m]

The ``s`` attribute is writable; assigning a new value automatically updates
``middle`` (and vice versa) once the trajectory is attached.

Run from the repository root::

    python examples/testing/positioning_example.py
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from laura import LAURA  # noqa: E402

# -- file paths ----------------------------------------------------------------

EXAMPLES = ROOT / "examples" / "testing"
SECTIONS = EXAMPLES / "positioning_sections.yaml"
LAYOUTS  = EXAMPLES / "positioning_layouts.yaml"

GLOBAL_ELEMENTS    = EXAMPLES / "positioning_global_elements.yaml"
S_COORD_ELEMENTS   = EXAMPLES / "positioning_s_elements.yaml"
REFERENCE_ELEMENTS = EXAMPLES / "positioning_reference_elements.yaml"

ORDERED = ["GUN_CAVITY", "INJ_SOL_01", "INJ_QUAD_01",
           "INJ_QUAD_02", "INJ_QUAD_03", "INJ_BPM_01"]


# -- helpers -------------------------------------------------------------------

def _sep(title: str) -> None:
    width = 70
    print()
    print("=" * width)
    print(f"  {title}")
    print("=" * width)


def _print_positions(machine: LAURA) -> None:
    """Print resolved middle and s for every physical element in order."""
    print(f"  {'Element':<18} {'z (middle) [m]':>16}  {'s [m]':>10}  {'start z':>10}  {'end z':>8}")
    print(f"  {'-'*18} {'-'*16}  {'-'*10}  {'-'*10}  {'-'*8}")
    for name in ORDERED:
        elem = machine[name]
        phys = elem.physical
        if phys is None or phys.middle is None:
            print(f"  {name:<18} {'<unresolved>':>16}")
            continue
        z   = phys.middle.z
        s   = phys.s if phys.s is not None else float("nan")
        sz  = phys.start.z
        ez  = phys.end.z
        print(f"  {name:<18} {z:>16.4f}  {s:>10.4f}  {sz:>10.4f}  {ez:>8.4f}")


def _load(elements_file: Path) -> LAURA:
    return LAURA(
        element_list=str(elements_file),
        section=str(SECTIONS),
        layout=str(LAYOUTS),
    )


# -- section 1: global xyz -----------------------------------------------------

def demo_global() -> LAURA:
    _sep("1. Global Cartesian coordinates  (positioning_global_elements.yaml)")
    print("""
  Elements defined with explicit ``middle: {{x, y, z}}`` in metres.
  LAURA reads these directly -- no conversion needed.
""")
    machine = _load(GLOBAL_ELEMENTS)
    _print_positions(machine)
    return machine


# -- section 2: s-coordinates --------------------------------------------------

def demo_s_coords() -> LAURA:
    _sep("2. s-coordinates  (positioning_s_elements.yaml)")
    print("""
  Elements defined with ``s: <float>`` (arc-length in metres from the origin).
  LAURA integrates the design orbit element-by-element and resolves each
  s value to global {x, y, z}.  For a straight lattice: z = s.
""")
    machine = _load(S_COORD_ELEMENTS)
    _print_positions(machine)
    return machine


# -- section 3: compare global vs s-coord -------------------------------------

def demo_compare(global_machine: LAURA, s_machine: LAURA) -> None:
    _sep("3. Comparison -- global xyz vs s-coordinate lattices")
    print("""
  Both lattices define the same physical layout; the resolved middle
  positions should be numerically identical.
""")
    all_match = True
    print(f"  {'Element':<18}  {'dz [mm]':>10}  {'Match?':>8}")
    print(f"  {'-'*18}  {'-'*10}  {'-'*8}")
    for name in ORDERED:
        g = global_machine[name].physical.middle.z
        s = s_machine[name].physical.middle.z
        delta_mm = abs(g - s) * 1000
        ok = delta_mm < 0.001
        all_match = all_match and ok
        print(f"  {name:<18}  {delta_mm:>10.4f}  {'OK' if ok else 'FAIL  MISMATCH':>8}")
    print()
    print(f"  All positions match: {all_match}")


# -- section 4: querying s for all elements ------------------------------------

def demo_query_s(machine: LAURA) -> None:
    _sep("4. Querying .s after lattice assembly")
    print("""
  After assembly every physical element exposes ``element.physical.s``
  regardless of which positioning mode was used to define it.
  The trajectory is built from the resolved element positions.
""")
    for name in ORDERED:
        phys = machine[name].physical
        print(f"  {name:<18}  middle.z = {phys.middle.z:.4f} m   "
              f"s = {phys.s:.4f} m")


# -- section 5: dynamic s <-> middle sync ----------------------------------------

def demo_dynamic_sync(machine: LAURA) -> None:
    _sep("5. Dynamic s <-> middle synchronisation")
    print("""
  Once the trajectory is attached to an element, writing to ``physical.s``
  immediately updates ``physical.middle``, and writing to ``physical.middle``
  immediately updates ``physical.s``.
""")
    quad = machine["INJ_QUAD_01"]
    phys = quad.physical

    orig_s      = phys.s
    orig_middle = phys.middle.z
    print(f"  INJ_QUAD_01 before: s = {orig_s:.4f} m,  middle.z = {orig_middle:.4f} m")

    # Move the quadrupole 5 cm downstream by changing s.
    new_s = orig_s + 0.05
    phys.s = new_s
    print(f"  After phys.s = {new_s:.4f}:   middle.z = {phys.middle.z:.4f} m  "
          f"(dz = {(phys.middle.z - orig_middle)*1000:.1f} mm)")

    # Restore via middle assignment -- s should update automatically.
    from laura.models.physical import Position
    phys.middle = Position(x=0.0, y=0.0, z=orig_middle)
    print(f"  After restoring middle.z = {orig_middle:.4f}:  s = {phys.s:.4f} m  "
          f"(back to original: {abs(phys.s - orig_s) < 1e-6})")


# -- section 6: s-coordinate serialisation ------------------------------------

def demo_dump_s(machine: LAURA) -> None:
    _sep("6. Exporting in s-coordinate form  (.model_dump_s())")
    print("""
  The default ``model_dump()`` (and YAML export) always writes global
  Cartesian coordinates so round-tripped files stay self-contained.
  Call ``physical.model_dump_s()`` to get the s-coordinate representation.
""")
    import json
    for name in ORDERED:
        phys = machine[name].physical
        normal = phys.model_dump()
        s_form = phys.model_dump_s()
        print(f"  {name}")
        print(f"    model_dump()   -> middle = {json.dumps(normal.get('middle'))}")
        print(f"    model_dump_s() -> s = {s_form.get('s')}, "
              f"s_point = '{s_form.get('s_point', 'middle')}'")
        print()


# -- section 7: reference_placement -------------------------------------------

def demo_reference() -> None:
    _sep("7. reference_placement  (positioning_reference_elements.yaml)")
    print("""
  Elements placed relative to a named reference element.
  Three offset flavours are shown in the YAML file:

    s_offset     -- most elements: scalar along local beam axis.
    offset       -- INJ_QUAD_02: [x, y, z] in the local reference frame.
    world_offset -- INJ_QUAD_03: [x, y, z] in the global frame.

  All resolve to the same positions as the other two files.
""")
    machine = _load(REFERENCE_ELEMENTS)
    _print_positions(machine)


# -- main ----------------------------------------------------------------------

def main() -> None:
    print("\nLAURA positioning modes -- worked example")
    print("(straight injector line, all positions in z only)\n")

    global_machine  = demo_global()
    s_machine       = demo_s_coords()
    demo_compare(global_machine, s_machine)
    demo_query_s(global_machine)
    demo_dynamic_sync(global_machine)
    demo_dump_s(s_machine)
    demo_reference()

    print()
    print("Done.")


if __name__ == "__main__":
    main()





