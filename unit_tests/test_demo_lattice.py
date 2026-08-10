"""Unit tests for the DEMO lattice sample files."""

from pathlib import Path

from laura import LAURA


ROOT = Path(__file__).resolve().parents[1]
ELEMENTS = ROOT / "examples" / "testing" / "sample_rf_control_elements.yaml"
SECTIONS = ROOT / "examples" / "testing" / "sample_rf_control_sections.yaml"
LAYOUTS = ROOT / "examples" / "testing" / "sample_rf_control_layouts.yaml"


def _load_demo_machine() -> LAURA:
    return LAURA(
        element_list=str(ELEMENTS),
        section=str(SECTIONS),
        layout=str(LAYOUTS),
    )


class TestDemoLattice:
    def test_demo_lattice_loads(self):
        machine = _load_demo_machine()

        assert "DEMO" in machine.sections
        assert "DEMO_LAYOUT" in machine.lattices
        assert machine.default_path == "DEMO_LAYOUT"
        assert "GUN_RF_CAVITY" in machine.elements
        assert "LINAC_RF_CAVITY" in machine.elements

    def test_power_supply_elements_are_typed(self):
        machine = _load_demo_machine()
        psu_names = [
            "GUN_RF_POWER_SUPPLY",
            "LINAC_RF_POWER_SUPPLY",
            "INJ_SOL_01_PSU",
            "INJ_QUAD_01_PSU",
            "INJ_QUAD_02_PSU",
            "INJ_QUAD_03_PSU",
            "INJ_QUAD_04_PSU",
        ]

        for name in psu_names:
            elem = machine[name]
            assert elem.hardware_type == "PowerSupply"
            assert "current" in elem.outputs

    def test_rf_chain_is_directly_connected(self):
        machine = _load_demo_machine()

        assert machine["GUN_RF_POWER_SUPPLY"].downstream == ["GUN_KLYSTRON_MODULATOR"]
        assert "GUN_RF_POWER_SUPPLY" in machine["GUN_KLYSTRON_MODULATOR"].upstream
        assert "GUN_KLYSTRON_MODULATOR" in machine["GUN_RF_CAVITY"].upstream

    def test_magnets_connect_to_psu_not_each_other(self):
        machine = _load_demo_machine()

        magnets = ["INJ_SOL_01", "INJ_QUAD_01", "INJ_QUAD_02", "INJ_QUAD_03", "INJ_QUAD_04"]
        for magnet_name in magnets:
            magnet = machine[magnet_name]
            assert magnet.upstream == [f"{magnet_name}_PSU"]
            assert magnet.downstream == []
