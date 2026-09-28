"""Layout ``settings``: values one beam path runs a shared device at.

Two paths share a section, and one of them runs its quadrupole differently.
The element keeps one value; each path's settings reach its exports and
``element_on_pass``, and never the shared element.
"""

import warnings

import pytest
import yaml

from laura.models.element import Quadrupole, RFCavity
from laura.models.element_list import MachineModel
from laura.translator.converters.layout import MachineLayoutTranslator

SECTIONS = {
    "INJ_A": ["QA"],
    "INJ_B": ["QB"],
    "HALL": ["CAV", "Q5"],
}
LAYOUTS = {"PATH_A": ["INJ_A", "HALL"], "PATH_B": ["INJ_B", "HALL"]}
B_SETTINGS = {"Q5": {"magnetic.k1l": 0.2}, "CAV": {"cavity.phase": 10.0}}


def elements():
    built = {
        name: Quadrupole(
            name=name,
            hardware_class="Magnet",
            machine_area="A",
            magnetic={"magnetic_length": 0.2, "k1l": 0.5},
            physical={"length": 0.2},
        )
        for name in ("QA", "QB", "Q5")
    }
    built["CAV"] = RFCavity(
        name="CAV", machine_area="A", physical={"length": 0.6}, cavity={"phase": 0.0}
    )
    return built


def machine(settings=B_SETTINGS, layouts=LAYOUTS, master_lattice=None):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        return MachineModel(
            elements=elements(),
            section={"sections": SECTIONS},
            layout={
                "layouts": layouts,
                "default_layout": "PATH_A",
                "layout_metadata": {"PATH_B": {"settings": settings}},
            },
            master_lattice=master_lattice,
        )


def exported(layout):
    """``{name: element}`` over every section *layout* exports."""
    translator = MachineLayoutTranslator.from_layout(layout)
    return {
        name: element
        for section in translator.sections.values()
        for name, element in section.elements.elements.items()
    }


def test_settings_arrive_on_their_path_only():
    model = machine()
    assert model.lattices["PATH_B"].settings == B_SETTINGS
    assert model.lattices["PATH_A"].settings == {}


def test_export_carries_each_paths_own_values():
    model = machine()
    b = exported(model.lattices["PATH_B"])
    a = exported(model.lattices["PATH_A"])
    assert b["Q5"].magnetic.k1l == pytest.approx(0.2)
    assert b["CAV"].cavity.phase == 10.0
    assert a["Q5"].magnetic.k1l == pytest.approx(0.5)
    assert a["CAV"].cavity.phase == 0.0


def test_bmad_export_writes_each_paths_values():
    model = machine()
    hall = {
        path: MachineLayoutTranslator.from_layout(model.lattices[path]).to_bmad()[
            "HALL"
        ]
        for path in ("PATH_A", "PATH_B")
    }
    assert "Q5: quadrupole, l = 0.2, tilt = 0.0, k1 = 2.5" in hall["PATH_A"]
    assert "Q5: quadrupole, l = 0.2, tilt = 0.0, k1 = 1.0" in hall["PATH_B"]


def test_the_shared_element_is_untouched():
    model = machine()
    exported(model.lattices["PATH_B"])
    assert model.elements["Q5"].magnetic.k1l == pytest.approx(0.5)
    assert model.sections["HALL"].elements.elements["Q5"].magnetic.k1l == (
        pytest.approx(0.5)
    )


def test_element_on_pass_gives_the_path_value():
    model = machine()
    element = model.lattices["PATH_B"].element_on_pass("Q5")
    assert element.magnetic.k1l == pytest.approx(0.2)
    assert element is not model.elements["Q5"]
    # Nothing set here, or on this path: the caller falls back to the device.
    assert model.lattices["PATH_B"].element_on_pass("QB") is None
    assert model.lattices["PATH_A"].element_on_pass("Q5") is None


def test_settings_apply_under_passes():
    layouts = {
        "PATH_A": ["INJ_A", "HALL"],
        "PATH_B": [
            "INJ_B",
            {"HALL": {"multipass": 1}},
            {"HALL": {"multipass": 2, "overrides": {"CAV": {"cavity.phase": 180}}}},
        ],
    }
    model = machine(layouts=layouts)
    layout = model.lattices["PATH_B"]
    first, second = layout.element_on_pass("Q5#1"), layout.element_on_pass("Q5#2")
    assert first.magnetic.k1l == second.magnetic.k1l == pytest.approx(0.2)
    # A pass's overrides are more particular than the path's settings.
    assert layout.element_on_pass("CAV#1").cavity.phase == 10.0
    assert layout.element_on_pass("CAV#2").cavity.phase == 180
    flat = exported(layout)
    q5s = [e.magnetic.k1l for n, e in flat.items() if n.startswith("Q5")]
    assert q5s == pytest.approx([0.2, 0.2])


def test_settings_can_live_in_a_file(tmp_path):
    (tmp_path / "path_b.yaml").write_text(yaml.safe_dump(B_SETTINGS))
    model = machine(settings="path_b.yaml", master_lattice=str(tmp_path))
    assert model.lattices["PATH_B"].settings == B_SETTINGS


def test_a_settings_file_is_found_beside_the_layouts_file(tmp_path, monkeypatch):
    (tmp_path / "settings").mkdir()
    (tmp_path / "settings" / "path_b.yaml").write_text(yaml.safe_dump(B_SETTINGS))
    (tmp_path / "layouts.yaml").write_text(
        yaml.safe_dump(
            {
                "layouts": LAYOUTS,
                "default_layout": "PATH_A",
                "layout_metadata": {"PATH_B": {"settings": "settings/path_b.yaml"}},
            }
        )
    )
    monkeypatch.chdir(tmp_path.parent)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        model = MachineModel(
            elements=elements(),
            section={"sections": SECTIONS},
            layout=str(tmp_path / "layouts.yaml"),
        )
    assert model.lattices["PATH_B"].settings == B_SETTINGS


def test_an_element_not_on_the_path_is_refused():
    with pytest.raises(ValueError, match="QA"):
        machine(settings={"QA": {"magnetic.k1l": 0.2}})


def test_an_attribute_the_element_lacks_is_refused():
    with pytest.raises(ValueError, match="no such attribute"):
        machine(settings={"Q5": {"magnetic.nonsense": 0.2}})


def test_a_malformed_mapping_is_refused():
    with pytest.raises(TypeError, match="must map an element name"):
        machine(settings={"Q5": 0.2})
