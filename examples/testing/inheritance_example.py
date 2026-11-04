"""Demonstrate LAURA element inheritance.

An element may name another element's definition and override only what
differs::

    INJ_QUAD_01:
      inherits_from: QUAD_TYPE_A
      physical: {s: 0.50}
      magnetic: {k1l: 0.85}

The merge runs on the raw dict before Pydantic parsing -- which is what makes
it possible to tell "the parent set this" from "the parent never mentioned
it", since a parsed parent has every default filled in already.

Three things this example is meant to show:

  1. What crosses over (length, magnet type, controls, machine area) and what
     does not (position, identity, topology).
  2. That a template under ``_templates`` defines without becoming a machine
     element of its own.
  3. That failures -- a parent that does not exist, or a cycle -- are
     itemised on ``machine.load_errors`` rather than silently dropping the
     element, and are raised outright under ``strict=True``.

Run from the repository root::

    python examples/testing/inheritance_example.py
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from laura import LAURA  # noqa: E402
from laura.Importers.YAML_Loader import ElementLoadError  # noqa: E402

# -- file paths ----------------------------------------------------------------

EXAMPLES = ROOT / "examples" / "testing"
ELEMENTS = EXAMPLES / "inheritance_elements.yaml"
SECTIONS = EXAMPLES / "inheritance_sections.yaml"
LAYOUTS = EXAMPLES / "inheritance_layouts.yaml"

QUADS = ["INJ_QUAD_01", "INJ_QUAD_02", "INJ_QUAD_03", "INJ_QUAD_04"]


# -- helpers -------------------------------------------------------------------


def _sep(title: str) -> None:
    width = 74
    print()
    print("=" * width)
    print(f"  {title}")
    print("=" * width)


def _load() -> LAURA:
    return LAURA(
        element_list=str(ELEMENTS),
        section=str(SECTIONS),
        layout=str(LAYOUTS),
    )


# -- section 1: what the children inherited ------------------------------------


def demo_merge(machine: LAURA) -> None:
    _sep("1. What crossed over from the template")
    print("""
  Each quadrupole's YAML states only its name, its parent, its position and
  its strength. Everything else below was inherited.
""")
    header = f"  {'Element':<14} {'type':<12} {'area':<6} {'len [m]':>8} {'k1l':>7}"
    print(header)
    print(f"  {'-' * 14} {'-' * 12} {'-' * 6} {'-' * 8} {'-' * 7}")
    for name in QUADS:
        elem = machine[name]
        print(
            f"  {name:<14} {elem.hardware_type:<12} {elem.machine_area:<6} "
            f"{elem.physical.length:>8.3f} {elem.magnetic.k1l:>7.2f}"
        )
    print("""
  INJ_QUAD_04 used the PALS ``inherit:`` spelling and overrode the length;
  the other three took the template's 0.1 m.
""")


# -- section 2: position is never inherited ------------------------------------


def demo_position(machine: LAURA) -> None:
    _sep("2. Position is never inherited")
    print("""
  The template carries no position, but even if it did, none of it would
  cross over. This is the rule that keeps inheritance safe: a child that
  states no position of its own would otherwise land exactly on top of its
  parent, and every downstream export would then work from a lattice that
  is wrong but perfectly valid.
""")
    print(f"  {'Element':<14} {'s [m]':>8} {'middle.z [m]':>14}")
    print(f"  {'-' * 14} {'-' * 8} {'-' * 14}")
    for name in QUADS:
        phys = machine[name].physical
        print(f"  {name:<14} {phys.s:>8.3f} {phys.middle.z:>14.3f}")
    print("""
  Each s value came from the element's own file. Identity and topology are
  excluded on the same grounds -- name, alias, virtual_name, subelement,
  upstream, downstream.
""")


# -- section 3: templates are not elements -------------------------------------


def demo_templates(machine: LAURA) -> None:
    _sep("3. A template defines, but is not a machine element")
    print("""
  ``QUAD_TYPE_A`` and ``BPM_TYPE_A`` live under the ``_templates`` key.
  Without that, every template would also be a real element -- in the
  machine, in the lattice, and in every export.
""")
    print(f"  machine.elements: {sorted(machine.elements)}")
    for template in ("QUAD_TYPE_A", "BPM_TYPE_A"):
        print(f"    {template!r} in machine.elements: {template in machine.elements}")
    print("""
  In a directory of one-element files an ``_``-prefixed filename does the
  same job: ``_quad_type_a.yaml`` is loadable as a parent but never becomes
  an element.
""")


# -- section 4: the link survives ----------------------------------------------


def demo_link(machine: LAURA) -> None:
    _sep("4. The declared parent is kept on the element")
    print("""
  Merging does not erase the relationship -- ``inherits_from`` stays on the
  parsed model, so an exporter can one day write the compact form back out
  instead of the fully expanded one.
""")
    for name in QUADS + ["GUN_CAVITY"]:
        print(f"  {name:<14} inherits_from = {machine[name].inherits_from!r}")


# -- section 5: failures are visible -------------------------------------------


def _machine_from(document: dict, **kwargs) -> LAURA:
    """Write a throwaway combined file and load it."""
    directory = Path(tempfile.mkdtemp())
    path = directory / "elements.yaml"
    path.write_text(yaml.safe_dump(document))
    return LAURA(element_list=str(path), **kwargs)


def demo_failures() -> None:
    _sep("5. A parent that is not there, and a cycle")
    print("""
  LAURA's loader skips an element it cannot build and returns None, so a
  machine can load "successfully" while quietly missing elements. An
  unresolvable parent is exactly that kind of loss -- the element would
  parse, just without its strength, its length or its controls. So both
  inheritance failures are itemised instead.
""")
    orphan = {
        "Q9": {
            "name": "Q9",
            "hardware_class": "Magnet",
            "hardware_type": "Quadrupole",
            "inherits_from": "NO_SUCH_TEMPLATE",
            "physical": {"length": 0.1, "s": 1.0},
        }
    }
    cycle = {
        "A": {"name": "A", "hardware_type": "Quadrupole", "inherits_from": "B"},
        "B": {"name": "B", "hardware_type": "Quadrupole", "inherits_from": "A"},
    }

    for label, document in (("missing parent", orphan), ("cycle", cycle)):
        machine = _machine_from(document)
        print(f"  {label}:")
        for error in machine.load_errors:
            print(f"    reason = {error.reason!r}")
            print(f"    {error.detail}")

    print("""
  Under ``strict=True`` the same conditions abort the load instead:
""")
    try:
        _machine_from(orphan, strict=True)
    except ElementLoadError as exc:
        print(f"    raised: {exc}")


# -- main ----------------------------------------------------------------------


def main() -> None:
    machine = _load()
    demo_merge(machine)
    demo_position(machine)
    demo_templates(machine)
    demo_link(machine)
    demo_failures()
    print()


if __name__ == "__main__":
    main()
