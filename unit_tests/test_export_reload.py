"""An exported machine loads back from what the export wrote: elements,
section orders and layouts."""

import warnings

import pytest

from laura import LAURA
from laura.exporters.yaml_exporter import export_machine, export_machine_combined_file
from unit_tests.helpers import quad, quiet

LAYOUT = {
    "default_layout": "short",
    "layouts": {
        "line": ["A", {"B": {"direction": -1}}],
        "short": ["A"],
    },
    "layout_metadata": {"line": {"type": "beam", "particle": "electron"}},
}


def built():
    with quiet():
        return LAURA(
            element_list=[quad("QA1", machine_area="A"), quad("QA2", machine_area="A"),
                          quad("QB1", machine_area="B")],
            section={"sections": {"A": ["QA1", "QA2"], "B": ["QB1"]}},
            layout=LAYOUT,
        )


@pytest.mark.parametrize("position_mode", ["global", "sequential"])
@pytest.mark.parametrize("combined", [False, True], ids=["files", "combined"])
def test_an_exported_machine_loads_back(tmp_path, position_mode, combined):
    machine = built()
    with quiet():
        if combined:
            export_machine_combined_file(str(tmp_path), machine, position_mode=position_mode)
            element_list = str(tmp_path / "summary.yaml")
        else:
            export_machine(str(tmp_path), machine, position_mode=position_mode)
            element_list = str(tmp_path)
        reloaded = LAURA(
            layout=str(tmp_path / "_layouts.yaml"),
            section=str(tmp_path / "_sections.yaml"),
            element_list=element_list,
        )
    assert reloaded.default_path == "short"
    assert reloaded._layout_entries == machine._layout_entries
    assert reloaded._layout_metadata == machine._layout_metadata
    assert {n: s.order for n, s in reloaded.sections.items()} == {
        "A": ["QA1", "QA2"],
        "B": ["QB1"],
    }


def test_a_repeat_exported_with_positions_loads_back_without_a_warning(tmp_path):
    with quiet():
        machine = LAURA(
            element_list=[quad("Q1"), quad("D")],
            section={"sections": {"S": ["Q1", {"D": {"repeat": 2}}]}},
        )
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        export_machine(str(tmp_path), machine, position_mode="global")
    with quiet():
        reloaded = LAURA(section=str(tmp_path / "_sections.yaml"), element_list=str(tmp_path))
    assert reloaded.sections["S"].order == ["Q1", "D.1", "D.2"]
    assert not (tmp_path / "_layouts.yaml").exists()  # the machine has no layouts
