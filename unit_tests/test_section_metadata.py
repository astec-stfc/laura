"""Section ``geometry``/``reference_energy`` and layout/machine ``particle``.

Each is set in the sections and layouts files, and written back out by
`export_machine_sections`, so a machine saved as YAML keeps what a tracking
code needs to know about its beam.
"""

import warnings

import yaml

from laura import LAURA
from laura.exporters.yaml_exporter import export_as_yaml, export_machine_sections
from laura.models.element import Quadrupole


def _quad(name, z):
    return Quadrupole(
        name=name,
        machine_area="L1",
        physical={"length": 0.1, "middle": {"z": z}},
        magnetic={"length": 0.1, "k1l": 0.5},
    )


def _write_tree(root, sections, layouts):
    elements = [_quad("Q1", 1.0), _quad("Q2", 2.0)]
    root.mkdir()
    with open(root / "elements.yaml", "w") as handle:
        yaml.dump({e.name: export_as_yaml(None, e, "global") for e in elements}, handle)
    with open(root / "sections.yaml", "w") as handle:
        yaml.dump({"sections": sections}, handle)
    with open(root / "layouts.yaml", "w") as handle:
        yaml.dump(layouts, handle)


def _load(root):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        return LAURA(
            element_list=str(root / "elements.yaml"),
            section=str(root / "sections.yaml"),
            layout=str(root / "layouts.yaml"),
            master_lattice=str(root),
        )


SECTIONS = {
    "L1": {
        "elements": ["Q1", "Q2"],
        "geometry": "open",
        "reference_energy": 135e6,
    }
}


def test_metadata_is_read_from_the_files(tmp_path):
    _write_tree(
        tmp_path / "tree",
        SECTIONS,
        {
            "default_layout": "beam",
            "layouts": {"beam": ["L1"]},
            "layout_metadata": {"beam": {"particle": "Positron"}},
            "particle": "Electron",
        },
    )
    machine = _load(tmp_path / "tree")
    section = machine.sections["L1"]
    assert section.reference_energy == 135e6
    assert getattr(section.geometry, "value", section.geometry) == "open"
    assert machine.particle == "Electron"
    assert machine.lattices["beam"].particle == "Positron"


def test_metadata_is_optional(tmp_path):
    _write_tree(
        tmp_path / "tree",
        {"L1": ["Q1", "Q2"]},
        {"default_layout": "beam", "layouts": {"beam": ["L1"]}},
    )
    machine = _load(tmp_path / "tree")
    assert machine.sections["L1"].reference_energy is None
    assert machine.sections["L1"].geometry is None
    assert machine.particle is None
    assert machine.lattices["beam"].particle is None


def test_section_metadata_survives_export(tmp_path):
    layouts = {"default_layout": "beam", "layouts": {"beam": ["L1"]}}
    _write_tree(tmp_path / "tree", SECTIONS, layouts)
    export_machine_sections(str(tmp_path), _load(tmp_path / "tree"), "written.yaml")
    written = yaml.safe_load((tmp_path / "written.yaml").read_text())["sections"]
    assert written["L1"]["geometry"] == "open"
    assert written["L1"]["reference_energy"] == 135e6

    _write_tree(tmp_path / "again", written, layouts)
    assert _load(tmp_path / "again").sections["L1"].reference_energy == 135e6
