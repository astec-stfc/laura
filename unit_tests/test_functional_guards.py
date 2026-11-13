"""Guards on functional definitions: names are checked when set, each machine
keeps its own definitions and resolution mode, an empty
``functional_definitions`` is allowed, and a YAML export carries the values its
elements name."""

import warnings

import pytest

from laura import LAURA
from laura.exporters.yaml_exporter import export_machine, export_machine_combined_file
from laura.models.element import Quadrupole
from laura.translator.converters.section import SectionLatticeTranslator


def build(k1l, definitions, resolve=False):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        return LAURA(
            element_list=[
                Quadrupole(
                    name="Q",
                    machine_area="A",
                    hardware_class="Magnet",
                    magnetic={"magnetic_length": 0.1, "k1l": k1l},
                    physical={"length": 0.1},
                )
            ],
            section={"sections": {"A": ["Q"]}},
            layout={"default_layout": "l", "layouts": {"l": ["A"]}},
            functional_definitions=definitions,
            resolve_functional=resolve,
        )


def test_a_misspelt_name_is_refused_when_set():
    magnet = build(0.5, {"quad_k1l": -2.0})["Q"].magnetic
    with pytest.raises(ValueError, match="'quad_k1'.*quad_k1l"):
        magnet.k1l = "quad_k1"
    magnet.k1l = "quad_k1l"
    assert magnet.KnL(1) == -2.0


def test_a_misspelt_name_is_refused_when_appended():
    machine = build("quad_k1l", {"quad_k1l": -2.0})
    typo = Quadrupole(
        name="Q2",
        machine_area="A",
        hardware_class="Magnet",
        magnetic={"magnetic_length": 0.1, "k1l": "quad_k1"},
        physical={"length": 0.1},
    )
    with pytest.raises(ValueError, match="'quad_k1'.*Q2"):
        machine.append({"Q2": typo})


def test_each_machine_keeps_its_own_definitions():
    first = build("quad_k1l", {"quad_k1l": -2.0})["Q"].magnetic
    second = build("quad_k1l", {"quad_k1l": 3.0, "other": 1.0})["Q"].magnetic
    assert (first.KnL(1), second.KnL(1)) == (-2.0, 3.0)
    with pytest.raises(ValueError, match="'other'"):
        first.k1l = "other"  # defined only by the second machine
    second.k1l = "other"
    assert second.KnL(1) == 1.0


def test_each_machine_keeps_its_own_resolution_mode():
    symbolic = build("quad_k1l", {"quad_k1l": -2.0})
    resolved = build("quad_k1l", {"quad_k1l": 3.0}, resolve=True)
    assert symbolic["Q"].magnetic.kl == "quad_k1l"
    assert resolved["Q"].magnetic.kl == 3.0

    def madx(machine):
        return SectionLatticeTranslator.from_section(machine.sections["A"]).to_madx()

    assert "quad_k1l = -2.0;" in madx(symbolic)
    assert "quad_k1l" not in madx(resolved)


def test_empty_functional_definitions_are_allowed():
    assert build(0.5, None)["Q"].magnetic.k1l == 0.5


@pytest.mark.parametrize("combined", [True, False])
def test_an_export_carries_the_definitions_it_names(tmp_path, combined):
    machine = build("quad_k1l", {"quad_k1l": -2.0})
    if combined:
        export_machine_combined_file(str(tmp_path), machine)
        elements = str(tmp_path / "summary.yaml")
    else:
        export_machine(str(tmp_path), machine)
        elements = str(tmp_path)

    reloaded = LAURA(
        element_list=elements,
        section={"sections": {"A": ["Q"]}},
        layout={"default_layout": "l", "layouts": {"l": ["A"]}},
        functional_definitions=str(tmp_path / "_functional_definitions.yaml"),
    )
    assert reloaded["Q"].magnetic.KnL(1) == -2.0
