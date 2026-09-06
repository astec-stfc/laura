"""Round-trip tests for the two collapsing halves of the YAML exporter.

``position_mode="sequential"`` and ``collapse_inheritance=True`` are both
inverses: they undo, on the way out, what the loader did on the way in. What
matters for either is not the exact text produced but that reloading it gives
back the machine that was exported, so most of what is below exports, reloads
and compares.
"""

import os
import warnings

import pytest
import yaml

from laura import LAURA
from laura.Exporters.YAML import (
    export_as_yaml,
    export_elements,
    export_machine,
    export_machine_combined_file,
    export_machine_sections,
)
from laura.models.element import Drift, Marker, Quadrupole


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

QUAD_TEMPLATE = {
    "name": "QUAD_TYPE_A",
    "hardware_class": "Magnet",
    "hardware_type": "Quadrupole",
    "machine_area": "INJ",
    "physical": {"length": 0.1},
    "magnetic": {"length": 0.1, "magnet_type": "quadrupole"},
}

SEQUENTIAL_ELEMENTS = {
    "_templates": {"QUAD_TYPE_A": QUAD_TEMPLATE},
    "GUN": {
        "name": "GUN",
        "hardware_class": "RF",
        "hardware_type": "RFCavity",
        "machine_area": "INJ",
        "physical": {"length": 0.2},
    },
    "D1": {
        "name": "D1",
        "hardware_class": "Drift",
        "hardware_type": "Drift",
        "machine_area": "INJ",
        "physical": {"length": 0.3},
    },
    "Q1": {"name": "Q1", "inherits_from": "QUAD_TYPE_A", "magnetic": {"k1l": 0.85}},
    "Q2": {"name": "Q2", "inherits_from": "QUAD_TYPE_A", "magnetic": {"k1l": -0.85}},
}

# D1 appears twice, so placement splits it into D1.1 and D1.2.
SEQUENTIAL_SECTIONS = {"sections": {"INJ": ["GUN", "D1", "Q1", "D1", "Q2"]}}
SEQUENTIAL_LAYOUTS = {"default_layout": "beam", "layouts": {"beam": ["INJ"]}}


def _write(path, data):
    with open(path, "w") as handle:
        yaml.dump(data, handle)
    return str(path)


def _load(element_list, section, layout):
    with warnings.catch_warnings():
        # The repeated-name split warns by design; see test_repeats_are_numbered.
        warnings.simplefilter("ignore")
        return LAURA(element_list=element_list, section=section, layout=layout)


@pytest.fixture
def sequential_source(tmp_path):
    """A loaded sequential machine plus the paths it was loaded from."""
    source = tmp_path / "source"
    source.mkdir()
    elements = _write(source / "elements.yaml", SEQUENTIAL_ELEMENTS)
    sections = _write(source / "sections.yaml", SEQUENTIAL_SECTIONS)
    layouts = _write(source / "layouts.yaml", SEQUENTIAL_LAYOUTS)
    return _load(elements, sections, layouts), elements, layouts


def _placements(machine):
    return {
        name: (elem.physical.s, elem.physical.s_point, elem.physical.length)
        for name, elem in machine.elements.items()
    }


# ---------------------------------------------------------------------------
# position_mode="sequential"
# ---------------------------------------------------------------------------

class TestSequentialDump:
    def _abutting_pair(self):
        first = Drift(
            name="D1", machine_area="SEC", hardware_class="Drift",
            physical={"length": 0.4, "s": 0.2, "s_point": "middle"},
        )
        second = Drift(
            name="D2", machine_area="SEC", hardware_class="Drift",
            physical={"length": 0.4, "s": 0.6, "s_point": "middle"},
        )
        return first, second

    def test_abutting_elements_carry_no_position(self):
        first, second = self._abutting_pair()
        dump = export_as_yaml(None, second, "sequential", prev_name="D1", prev_ele=first)
        for key in ("s", "s_point", "middle", "reference_placement"):
            assert key not in dump["physical"]

    def test_first_element_at_origin_carries_no_position(self):
        first, _ = self._abutting_pair()
        dump = export_as_yaml(None, first, "sequential")
        for key in ("s", "s_point", "middle", "reference_placement"):
            assert key not in dump["physical"]

    def test_first_element_off_origin_anchors(self):
        anchored = Drift(
            name="D1", machine_area="SEC", hardware_class="Drift",
            physical={"length": 0.4, "s": 12.2, "s_point": "middle"},
        )
        with pytest.warns(UserWarning, match="does not abut"):
            dump = export_as_yaml(None, anchored, "sequential")
        assert dump["physical"]["s"] == pytest.approx(12.0)
        assert dump["physical"]["s_point"] == "start"
        assert "middle" not in dump["physical"]

    def test_gap_anchors_and_warns(self):
        first, second = self._abutting_pair()
        second.physical.s = 1.6  # a metre of nothing in between
        with pytest.warns(UserWarning, match="does not abut"):
            dump = export_as_yaml(None, second, "sequential", prev_name="D1", prev_ele=first)
        assert dump["physical"]["s"] == pytest.approx(1.4)
        assert dump["physical"]["s_point"] == "start"

    def test_unplaced_element_is_left_alone(self):
        """Nothing to invert: an element with no ``s`` keeps whatever it has."""
        quad = Quadrupole(
            name="Q1", machine_area="SEC",
            magnetic={"length": 0.3, "k1l": 1.0},
            physical={"length": 0.3, "middle": {"x": 0.0, "y": 0.0, "z": 1.0}},
        )
        dump = export_as_yaml(None, quad, "sequential")
        assert dump["physical"]["middle"]["z"] == 1.0


class TestSequentialRoundTrip:
    def test_combined_file_reloads_to_the_same_placement(self, sequential_source, tmp_path):
        machine, _, layouts = sequential_source
        dest = tmp_path / "combined"
        export_machine_combined_file(str(dest), machine, position_mode="sequential")

        reloaded = _load(str(dest / "summary.yaml"), str(dest / "_sections.yaml"), layouts)
        assert _placements(reloaded) == _placements(machine)

    def test_directory_export_reloads_to_the_same_placement(self, sequential_source, tmp_path):
        machine, _, layouts = sequential_source
        dest = tmp_path / "tree"
        export_machine(str(dest), machine, overwrite=True, position_mode="sequential")

        reloaded = _load(str(dest), str(dest / "_sections.yaml"), layouts)
        assert _placements(reloaded) == _placements(machine)

    def test_no_positions_are_written_at_all(self, sequential_source, tmp_path):
        machine, _, _ = sequential_source
        dest = tmp_path / "combined"
        export_machine_combined_file(str(dest), machine, position_mode="sequential")

        with open(dest / "summary.yaml") as handle:
            written = yaml.safe_load(handle)
        for name, dump in written.items():
            if name.startswith("_"):
                continue
            physical = dump.get("physical", {})
            assert "s" not in physical, name
            assert "middle" not in physical, name

    def test_repeats_are_numbered_in_the_exported_sections(self, sequential_source, tmp_path):
        machine, _, _ = sequential_source
        dest = tmp_path / "combined"
        export_machine_combined_file(str(dest), machine, position_mode="sequential")

        with open(dest / "_sections.yaml") as handle:
            sections = yaml.safe_load(handle)
        assert sections["sections"]["INJ"]["elements"] == [
            "GUN", "D1.1", "Q1", "D1.2", "Q2",
        ]

    def test_sections_are_not_written_in_other_modes(self, sequential_source, tmp_path):
        machine, _, _ = sequential_source
        dest = tmp_path / "combined"
        export_machine_combined_file(str(dest), machine, position_mode="s")
        assert not (dest / "_sections.yaml").exists()

    def test_write_sections_can_be_turned_off(self, sequential_source, tmp_path):
        machine, _, _ = sequential_source
        dest = tmp_path / "combined"
        export_machine_combined_file(
            str(dest), machine, position_mode="sequential", write_sections=False
        )
        assert not (dest / "_sections.yaml").exists()

    def test_exported_sections_alone_are_loadable(self, sequential_source, tmp_path):
        machine, elements, layouts = sequential_source
        dest = tmp_path / "sections_only"
        export_machine_sections(str(dest), machine)
        assert (dest / "_sections.yaml").exists()


class TestCombinedFileHonoursPositionMode:
    """The combined exporter used to build each dump twice, the second time in
    ``"global"`` mode, so every mode but the default was silently discarded."""

    def test_s_mode_reaches_the_file(self, sequential_source, tmp_path):
        machine, _, _ = sequential_source
        dest = tmp_path / "combined"
        export_machine_combined_file(str(dest), machine, position_mode="s")

        with open(dest / "summary.yaml") as handle:
            written = yaml.safe_load(handle)
        assert written["Q1"]["physical"]["s"] == pytest.approx(machine["Q1"].physical.s)
        assert "middle" not in written["Q1"]["physical"]

    def test_reference_mode_reaches_the_file(self, sequential_source, tmp_path):
        machine, _, _ = sequential_source
        dest = tmp_path / "combined"
        export_machine_combined_file(str(dest), machine, position_mode="reference")

        with open(dest / "summary.yaml") as handle:
            written = yaml.safe_load(handle)
        assert written["Q1"]["physical"]["reference_placement"]["element"] == "D1.1"


# ---------------------------------------------------------------------------
# Pruning empty containers
# ---------------------------------------------------------------------------

class TestPruneEmpty:
    """`exclude_defaults=True` drops a field equal to its default, but a
    sub-model whose own fields are all defaults dumps as `{}` -- so every
    element used to carry a dozen lines of empty containers around the two that
    said what it was."""

    def test_empty_submodels_are_dropped(self, sequential_source):
        machine, _, _ = sequential_source
        dump = export_as_yaml(None, machine["Q1"])
        for key in ("manufacturer", "simulation", "electrical"):
            assert key not in dump
        assert "error" not in dump["physical"]
        assert "survey" not in dump["physical"]

    def test_unset_multipole_slots_are_dropped(self, sequential_source):
        machine, _, _ = sequential_source
        dump = export_as_yaml(None, machine["Q1"])
        multipoles = dump["magnetic"]["multipoles"]
        assert set(multipoles) == {"K1L"}
        # ...but the slot that carries a strength keeps its order, which a
        # supplied entry does not get back from the container.
        assert multipoles["K1L"]["order"] == 1
        assert multipoles["K1L"]["normal"] == pytest.approx(0.85)

    def test_zero_is_not_empty(self):
        """0, 0.0 and False are values someone may have written."""
        quad = Quadrupole(
            name="Q1", machine_area="SEC",
            magnetic={"length": 0.3, "k1l": 0.0},
            physical={"length": 0.3, "middle": {"x": 0.0, "y": 0.0, "z": 4.0}},
        )
        dump = export_as_yaml(None, quad)
        assert dump["physical"]["middle"]["z"] == 4.0
        assert dump["physical"]["length"] == pytest.approx(0.3)

    def _origin_machine(self):
        """A globally-positioned section whose first element sits at s = 0."""
        marker = Marker(
            name="M1", machine_area="SEC", hardware_class="Marker",
            physical={"middle": {"x": 0.0, "y": 0.0, "z": 0.0}},
        )
        quad = Quadrupole(
            name="Q1", machine_area="SEC",
            magnetic={"length": 0.3, "k1l": -1.5},
            physical={"length": 0.3, "middle": {"x": 0.0, "y": 0.0, "z": 1.0}},
        )
        return _load(
            [marker, quad],
            {"sections": {"SEC": ["M1", "Q1"]}},
            {"default_layout": "beam", "layouts": {"beam": ["SEC"]}},
        )

    def test_an_element_at_the_origin_keeps_its_position(self):
        """The trap. `Position(0, 0, 0)` equals its own default, so a resolved
        element at the origin dumps as `middle: {}` -- and if pruning takes
        that, the element reloads *unpositioned*, which turns a globally
        positioned section into a sequential one and raises on the mix."""
        machine = self._origin_machine()
        dump = export_as_yaml(None, machine["M1"])
        assert dump["physical"]["middle"] == {}

    def test_origin_element_survives_a_round_trip(self, tmp_path):
        machine = self._origin_machine()
        sections = {"sections": {"SEC": ["M1", "Q1"]}}
        layouts = {"default_layout": "beam", "layouts": {"beam": ["SEC"]}}

        dest = tmp_path / "tree"
        export_machine(str(dest), machine, overwrite=True)
        reloaded = _load(str(dest), sections, layouts)
        assert reloaded["M1"].physical.middle.array == pytest.approx([0.0, 0.0, 0.0])
        assert reloaded["Q1"].physical.middle.array == pytest.approx([0.0, 0.0, 1.0])

    @pytest.mark.parametrize("element_name", ["GUN", "D1.1", "Q1", "Q2"])
    def test_pruning_is_lossless(self, sequential_source, tmp_path, element_name):
        """Every key pruned is one the loader rebuilds from the same default the
        empty container was standing in for. Compared on the full model dump,
        not on the keys the exporter happens to write."""
        machine, _, layouts = sequential_source
        dest = tmp_path / "combined"
        export_machine_combined_file(
            str(dest), machine, position_mode="sequential", collapse_inheritance=True
        )
        reloaded = _load(str(dest / "summary.yaml"), str(dest / "_sections.yaml"), layouts)
        assert reloaded[element_name].model_dump() == machine[element_name].model_dump()


# ---------------------------------------------------------------------------
# collapse_inheritance=True
# ---------------------------------------------------------------------------

class TestCollapseInheritanceDump:
    def test_shared_keys_are_dropped_and_overrides_kept(self, sequential_source):
        machine, elements, _ = sequential_source
        dump = export_as_yaml(
            None, machine["Q1"], collapse_inheritance=True, template_root=elements
        )
        assert dump["inherits_from"] == "QUAD_TYPE_A"
        # Supplied identically by the template.
        assert "hardware_type" not in dump
        assert "machine_area" not in dump
        assert "length" not in dump.get("physical", {})
        # The override is the whole point of the child.
        assert dump["magnetic"]["multipoles"]["K1L"]["normal"] == 0.85

    def test_name_survives_collapse(self, sequential_source):
        """``name`` is in NON_INHERITED_FIELDS, so it is kept even though the
        template carries one: dropping it would leave the child anonymous."""
        machine, elements, _ = sequential_source
        dump = export_as_yaml(
            None, machine["Q1"], collapse_inheritance=True, template_root=elements
        )
        assert dump["name"] == "Q1"

    def test_position_survives_collapse(self, tmp_path):
        """``physical.middle`` is never inherited either, so an element sitting
        exactly where its template says must still say so itself."""
        source = tmp_path / "src"
        source.mkdir()
        template = dict(QUAD_TEMPLATE)
        template["physical"] = {"length": 0.1, "middle": {"x": 0.0, "y": 0.0, "z": 1.0}}
        raw = {
            "_templates": {"QUAD_TYPE_A": template},
            "Q1": {
                "name": "Q1",
                "inherits_from": "QUAD_TYPE_A",
                "physical": {"middle": {"x": 0.0, "y": 0.0, "z": 1.0}},
                "magnetic": {"k1l": 0.85},
            },
        }
        elements = _write(source / "elements.yaml", raw)
        machine = _load(elements, None, SEQUENTIAL_LAYOUTS)
        dump = export_as_yaml(
            None, machine["Q1"], collapse_inheritance=True, template_root=elements
        )
        assert dump["physical"]["middle"]["z"] == 1.0

    def test_missing_parent_leaves_the_dump_expanded(self, sequential_source, tmp_path):
        machine, _, _ = sequential_source
        with pytest.warns(UserWarning, match="Cannot collapse inheritance"):
            dump = export_as_yaml(
                None,
                machine["Q1"],
                collapse_inheritance=True,
                template_root=str(tmp_path / "nowhere"),
            )
        # No dangling reference, and everything the reload needs is present.
        assert "inherits_from" not in dump
        assert dump["hardware_type"] == "Quadrupole"
        assert dump["physical"]["length"] == pytest.approx(0.1)

    def test_without_the_flag_the_dump_is_fully_expanded(self, sequential_source):
        machine, _, _ = sequential_source
        dump = export_as_yaml(None, machine["Q1"])
        assert dump["hardware_type"] == "Quadrupole"
        assert dump["physical"]["length"] == pytest.approx(0.1)


class TestCollapseInheritanceRoundTrip:
    def _assert_merged(self, machine):
        quad = machine["Q1"]
        assert quad.hardware_type == "Quadrupole"
        assert quad.machine_area == "INJ"
        assert quad.physical.length == pytest.approx(0.1)
        assert quad.magnetic.k1l == pytest.approx(0.85)
        assert machine["Q2"].magnetic.k1l == pytest.approx(-0.85)

    def test_combined_file_is_standalone(self, sequential_source, tmp_path):
        machine, _, layouts = sequential_source
        dest = tmp_path / "combined"
        export_machine_combined_file(str(dest), machine, collapse_inheritance=True)

        with open(dest / "summary.yaml") as handle:
            written = yaml.safe_load(handle)
        assert written["Q1"]["inherits_from"] == "QUAD_TYPE_A"
        assert "QUAD_TYPE_A" in written["_templates"]
        # A template is a definition, not an element.
        assert "QUAD_TYPE_A" not in [k for k in written if not k.startswith("_")]

        reloaded = _load(str(dest / "summary.yaml"), None, layouts)
        assert "QUAD_TYPE_A" not in reloaded.elements
        self._assert_merged(reloaded)

    def test_directory_export_is_standalone(self, sequential_source, tmp_path):
        machine, _, layouts = sequential_source
        dest = tmp_path / "tree"
        export_machine(str(dest), machine, overwrite=True, collapse_inheritance=True)

        assert (dest / "_QUAD_TYPE_A.yaml").exists()
        reloaded = _load(str(dest), None, layouts)
        assert "QUAD_TYPE_A" not in reloaded.elements
        self._assert_merged(reloaded)

    def test_export_elements_is_standalone(self, sequential_source, tmp_path):
        machine, elements, layouts = sequential_source
        dest = tmp_path / "list"
        export_elements(
            str(dest),
            [machine["Q1"], machine["Q2"]],
            collapse_inheritance=True,
            template_root=elements,
        )
        assert (dest / "_QUAD_TYPE_A.yaml").exists()
        reloaded = _load(str(dest), None, layouts)
        self._assert_merged(reloaded)

    def test_templates_are_not_copied_when_asked_not_to(self, sequential_source, tmp_path):
        machine, _, _ = sequential_source
        dest = tmp_path / "tree"
        export_machine(
            str(dest), machine, overwrite=True,
            collapse_inheritance=True, copy_templates=False,
        )
        assert not (dest / "_QUAD_TYPE_A.yaml").exists()

    def test_a_parent_that_is_an_element_is_not_duplicated(self, tmp_path):
        """Inheriting from an ordinary element rather than a template: it is
        already exported in its own right, so carrying a copy would define it
        twice."""
        source = tmp_path / "src"
        source.mkdir()
        raw = {
            "PARENT": dict(QUAD_TEMPLATE, name="PARENT"),
            "CHILD": {"name": "CHILD", "inherits_from": "PARENT", "magnetic": {"k1l": 2.0}},
        }
        elements = _write(source / "elements.yaml", raw)
        machine = _load(elements, None, {"default_layout": "b", "layouts": {"b": []}})

        dest = tmp_path / "combined"
        export_machine_combined_file(str(dest), machine, collapse_inheritance=True)
        with open(dest / "summary.yaml") as handle:
            written = yaml.safe_load(handle)
        assert "_templates" not in written
        assert written["CHILD"]["inherits_from"] == "PARENT"

        reloaded = _load(str(dest / "summary.yaml"), None, {"default_layout": "b", "layouts": {"b": []}})
        assert reloaded["CHILD"].magnetic.k1l == pytest.approx(2.0)
        assert reloaded["CHILD"].physical.length == pytest.approx(0.1)

    def test_whole_inheritance_chain_is_carried(self, tmp_path):
        source = tmp_path / "src"
        source.mkdir()
        raw = {
            "_templates": {
                "BASE": QUAD_TEMPLATE,
                "MIDDLE": {
                    "name": "MIDDLE",
                    "inherits_from": "BASE",
                    "magnetic": {"k1l": 1.0},
                },
            },
            "Q1": {"name": "Q1", "inherits_from": "MIDDLE", "machine_area": "BA1"},
        }
        elements = _write(source / "elements.yaml", raw)
        machine = _load(elements, None, {"default_layout": "b", "layouts": {"b": []}})

        dest = tmp_path / "combined"
        export_machine_combined_file(str(dest), machine, collapse_inheritance=True)
        with open(dest / "summary.yaml") as handle:
            written = yaml.safe_load(handle)
        assert set(written["_templates"]) == {"MIDDLE", "BASE"}

        reloaded = _load(
            str(dest / "summary.yaml"), None, {"default_layout": "b", "layouts": {"b": []}}
        )
        quad = reloaded["Q1"]
        assert quad.machine_area == "BA1"
        assert quad.magnetic.k1l == pytest.approx(1.0)   # from MIDDLE
        assert quad.hardware_type == "Quadrupole"        # from BASE


class TestBothTogether:
    """The two halves are meant to be usable at once -- that is how a lattice
    written by hand in the compact form comes back out in the compact form."""

    def test_combined_round_trip(self, sequential_source, tmp_path):
        machine, _, layouts = sequential_source
        dest = tmp_path / "combined"
        export_machine_combined_file(
            str(dest), machine, position_mode="sequential", collapse_inheritance=True
        )

        with open(dest / "summary.yaml") as handle:
            written = yaml.safe_load(handle)
        assert written["Q1"]["inherits_from"] == "QUAD_TYPE_A"
        assert "s" not in written["Q1"].get("physical", {})

        reloaded = _load(str(dest / "summary.yaml"), str(dest / "_sections.yaml"), layouts)
        assert _placements(reloaded) == _placements(machine)
        assert reloaded["Q1"].magnetic.k1l == pytest.approx(0.85)

    def test_directory_round_trip(self, sequential_source, tmp_path):
        machine, _, layouts = sequential_source
        dest = tmp_path / "tree"
        export_machine(
            str(dest), machine, overwrite=True,
            position_mode="sequential", collapse_inheritance=True,
        )

        reloaded = _load(str(dest), str(dest / "_sections.yaml"), layouts)
        assert _placements(reloaded) == _placements(machine)
        assert reloaded["Q1"].magnetic.k1l == pytest.approx(0.85)

    def test_export_of_an_export_is_stable(self, sequential_source, tmp_path):
        """Exporting twice must not drift: the second file is the first."""
        machine, _, layouts = sequential_source
        first = tmp_path / "first"
        export_machine_combined_file(
            str(first), machine, position_mode="sequential", collapse_inheritance=True
        )
        reloaded = _load(str(first / "summary.yaml"), str(first / "_sections.yaml"), layouts)

        second = tmp_path / "second"
        export_machine_combined_file(
            str(second), reloaded, position_mode="sequential", collapse_inheritance=True
        )
        assert (
            open(second / "summary.yaml").read() == open(first / "summary.yaml").read()
        )
        assert (
            open(second / "_sections.yaml").read() == open(first / "_sections.yaml").read()
        )
