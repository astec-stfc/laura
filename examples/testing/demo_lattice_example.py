"""Example: load and inspect the DEMO lattice files.

Run from repository root:
    python examples/testing/demo_lattice_example.py
"""

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


def main() -> None:
    machine = LAURA(
        element_list=str(ELEMENTS),
        section=str(SECTIONS),
        layout=str(LAYOUTS),
    )

    print(f"Loaded elements: {len(machine.elements)}")
    print(f"Available layouts: {list(machine.lattices.keys())}")
    print(f"Default layout: {machine.default_path}")

    # Confirm the new typed PSU elements are present.
    psus = [
        name
        for name, elem in machine.elements.items()
        if getattr(elem, "hardware_type", "") == "PowerSupply"
    ]
    print(f"Power supplies ({len(psus)}): {sorted(psus)}")

    # Show direct signal connections in the RF chain.
    gun_psu = machine["GUN_RF_POWER_SUPPLY"]
    gun_mod = machine["GUN_KLYSTRON_MODULATOR"]
    print(f"{gun_psu.name} downstream -> {gun_psu.downstream}")
    print(f"{gun_mod.name} upstream -> {gun_mod.upstream}")


if __name__ == "__main__":
    main()
