"""Guards on functional definitions: names are checked when set, a clash
between machines warns, an empty ``functional_definitions`` is allowed, and a
YAML export carries the values its elements name."""

import warnings

import pytest

from laura import LAURA
from laura.exporters.yaml_exporter import export_machine, export_machine_combined_file
from laura.models.base_models import set_functional_definitions
from laura.models.element import Quadrupole


@pytest.fixture(autouse=True)
def empty_registry():
    set_functional_definitions({}, merge=False)
    yield
    set_functional_definitions({}, merge=False)


def build(k1l, definitions):
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", message="(?!.*functional definition)")
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


def test_redefining_a_name_with_another_value_warns():
    build("quad_k1l", {"quad_k1l": -2.0})
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        build("quad_k1l", {"quad_k1l": -2.0})  # the same value again is fine
    with pytest.warns(UserWarning, match="quad_k1l.*-2.0.*3.0"):
        build("quad_k1l", {"quad_k1l": 3.0})


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
    set_functional_definitions({}, merge=False)  # as in a fresh session

    reloaded = LAURA(
        element_list=elements,
        section={"sections": {"A": ["Q"]}},
        layout={"default_layout": "l", "layouts": {"l": ["A"]}},
        functional_definitions=str(tmp_path / "_functional_definitions.yaml"),
    )
    assert reloaded["Q"].magnetic.KnL(1) == -2.0
