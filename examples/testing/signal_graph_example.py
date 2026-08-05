"""Example: walk the control/signal graph via ``upstream`` / ``downstream``.

Answers "how do I get from LINAC_KLYSTRON_MODULATOR to LINAC_RF_CAVITY, and
what actually flows between them?"

``inputs`` / ``outputs`` say *what kind* of signal an element consumes and
produces (IOTypeEnum values); ``upstream`` / ``downstream`` say *which*
elements are on either side, by name. A link carries meaning when the source's
``outputs`` intersect the destination's ``inputs``.

Two things the traversal has to cope with, both exercised below:

* The graph has cycles -- a PID is downstream of the cavity it measures and
  upstream of the modulator it trims. Hence the ``seen`` set.
* ``upstream`` / ``downstream`` are stored on both elements by convention but
  symmetry is not enforced, so we follow one direction only.

There is deliberately no graph API on ``LAURA`` for this: the links are plain
lists of names, so a few lines of ``collections.deque`` covers it.

Run from repository root:
    python examples/testing/signal_graph_example.py
"""

from collections import deque
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

try:
    from laura import LAURA
except ImportError:
    from laura.laura import LAURA


ELEMENTS = ROOT / "examples" / "testing" / "sample_rf_control_elements.yaml"
SECTIONS = ROOT / "examples" / "testing" / "sample_rf_control_sections.yaml"
LAYOUTS = ROOT / "examples" / "testing" / "sample_rf_control_layouts.yaml"


def signals_between(machine, source: str, dest: str) -> list[str]:
    """Signal types flowing from *source* to *dest*: its outputs ∩ dest's inputs."""
    out = set(machine[source].outputs)
    return sorted(out & set(machine[dest].inputs))


def find_path(machine, start: str, goal: str) -> list[str] | None:
    """Shortest ``downstream`` path from *start* to *goal*, or None.

    Breadth-first, so the first route found is the shortest. ``seen`` is what
    keeps the RF feedback loops from spinning forever.
    """
    queue = deque([[start]])
    seen = {start}
    while queue:
        path = queue.popleft()
        if path[-1] == goal:
            return path
        for nxt in machine[path[-1]].downstream:
            if nxt in seen or nxt not in machine.elements:
                continue
            seen.add(nxt)
            queue.append(path + [nxt])
    return None


def walk(machine, start: str, direction: str = "downstream") -> list[str]:
    """Every element reachable from *start* along *direction*, breadth-first."""
    queue, seen, order = deque([start]), {start}, []
    while queue:
        name = queue.popleft()
        order.append(name)
        for nxt in getattr(machine[name], direction):
            if nxt in seen or nxt not in machine.elements:
                continue
            seen.add(nxt)
            queue.append(nxt)
    return order


def main() -> None:
    machine = LAURA(
        element_list=str(ELEMENTS),
        section=str(SECTIONS),
        layout=str(LAYOUTS),
    )

    # 1. The case from the review: modulator -> cavity, and what flows.
    path = find_path(machine, "LINAC_KLYSTRON_MODULATOR", "LINAC_RF_CAVITY")
    print("1. LINAC_KLYSTRON_MODULATOR -> LINAC_RF_CAVITY")
    print(f"   path: {' -> '.join(path)}")
    for src, dst in zip(path, path[1:]):
        print(f"   {src} --{','.join(signals_between(machine, src, dst))}--> {dst}")

    # 2. Trace a set-point all the way to the beam: PSU -> modulator -> cavity.
    print("\n2. Full drive chain from the LINAC power supply")
    chain = find_path(machine, "LINAC_RF_POWER_SUPPLY", "LINAC_RF_CAVITY")
    for src, dst in zip(chain, chain[1:]):
        print(f"   {src} --{','.join(signals_between(machine, src, dst))}--> {dst}")

    # 3. Answer the practical question: what feeds this cavity, and with what?
    cavity = machine["LINAC_RF_CAVITY"]
    print(f"\n3. What drives {cavity.name}? (inputs: {list(cavity.inputs)})")
    for name in cavity.upstream:
        if name not in machine.elements:
            print(f"   {name}: not loaded in this element file")
            continue
        shared = signals_between(machine, name, cavity.name)
        supplies = ",".join(shared) if shared else "nothing it declares as an input"
        print(f"   {name} ({machine[name].hardware_type}) supplies {supplies}")

    # 4. The reverse question, and proof the cycle terminates.
    print("\n4. Everything reachable downstream of the LINAC power supply")
    print(f"   {walk(machine, 'LINAC_RF_POWER_SUPPLY')}")

    # 5. Which magnet does a given PSU actually drive?
    print("\n5. Magnet power supplies")
    for name, elem in sorted(machine.elements.items()):
        if elem.hardware_type != "PowerSupply" or not name.endswith("_PSU"):
            continue
        for driven in elem.downstream:
            print(
                f"   {name} --{','.join(signals_between(machine, name, driven))}--> "
                f"{driven} (outputs {list(machine[driven].outputs)})"
            )


if __name__ == "__main__":
    main()
