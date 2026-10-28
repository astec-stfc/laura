"""Section repeats (``fodo_cell: {repeat: 3}``) and nested lines, expanded at load."""

from pathlib import Path

import pytest
import yaml
from pydantic import ValidationError

from laura import LAURA
from laura.Exporters.YAML import export_machine_combined_file
from laura.models.element import Drift
from laura.models.elementList import (
    LatticeError,
    MachineModel,
    expand_section_order,
)
from unit_tests.helpers import quad, quiet

EXAMPLES = Path(__file__).resolve().parents[1] / "examples" / "testing"

CELL = ["drift1", "quad1", "drift2", "quad2", "drift1"]
COMPACT = {"fodo_channel": [{"fodo_cell": {"repeat": 3}}], "fodo_cell": CELL}


def drift(name, length):
    return Drift(
        name=name,
        hardware_class="Drift",
        machine_area="FODO",
        physical={"length": length},
    )


def elements():
    return {
        e.name: e
        for e in (
            drift("drift1", 0.25),
            quad("quad1", 1.0, 1.0, "FODO"),
            drift("drift2", 0.5),
            quad("quad2", 1.0, -1.0, "FODO"),
        )
    }


def machine(sections, layouts=("fodo_channel",)):
    with quiet():
        return MachineModel(
            elements=elements(),
            section={"sections": sections},
            layout={
                "layouts": {"fodo_lattice": list(layouts)},
                "default_layout": "fodo_lattice",
            },
        )


def written_sections(model, path):
    with quiet():
        export_machine_combined_file(str(path), model, position_mode="sequential")
    return yaml.safe_load((path / "_sections.yaml").read_text())["sections"]


def reload(path):
    with quiet():
        return LAURA(
            element_list=str(path / "summary.yaml"),
            section=str(path / "_sections.yaml"),
            layout={
                "layouts": {"fodo_lattice": ["fodo_channel"]},
                "default_layout": "fodo_lattice",
            },
        )


Q123 = ["q1", "q2", "q3"]


class TestExpandSectionOrder:
    @pytest.mark.parametrize(
        "authored, expected",
        [
            pytest.param({"s": CELL}, CELL, id="flat-order-left-alone"),
            pytest.param(
                {"s": [{"q1": {"repeat": 3}}]}, ["q1"] * 3, id="repeat-writes-it-out"
            ),
            pytest.param(
                {"cell": CELL, "s": ["q0", "cell"]}, ["q0"] + CELL, id="line-spliced-in"
            ),
            pytest.param(
                {"cell": CELL, "s": [{"cell": {"repeat": 3}}]},
                CELL * 3,
                id="repeated-line-spliced-in",
            ),
            pytest.param(
                {
                    "inner": ["a", "b"],
                    "middle": [{"inner": {"repeat": 2}}],
                    "s": [{"middle": {"repeat": 2}}, "c"],
                },
                ["a", "b"] * 4 + ["c"],
                id="lines-nest",
            ),
            pytest.param(
                {"cell": Q123, "s": [{"cell": {"repeat": -1}}]},
                Q123[::-1],
                id="negative-repeat-reverses",
            ),
            pytest.param(
                {"cell": Q123, "s": [{"cell": {"repeat": -2}}]},
                Q123[::-1] * 2,
                id="negative-repeat-reverses-then-repeats",
            ),
            # the MAD-X idiom: LINE = (cell, -cell)
            pytest.param(
                {"cell": Q123, "s": ["cell", {"cell": {"repeat": -1}}]},
                Q123 + Q123[::-1],
                id="reversed-line-joins-forward-one",
            ),
            pytest.param(
                {"s": [{"q1": {"repeat": -1}}]},
                ["q1"],
                id="reversing-one-element-no-op",
            ),
            pytest.param(
                {
                    "inner": ["a", "b"],
                    "cell": ["x", {"inner": {"repeat": 2}}, "y"],
                    "s": [{"cell": {"repeat": -1}}],
                },
                ["y", "b", "a", "b", "a", "x"],
                id="reversal-after-nested-expansion",
            ),
        ],
    )
    def test_expansion(self, authored, expected):
        assert expand_section_order("s", authored["s"], authored) == expected

    def test_a_line_may_be_used_before_it_is_defined(self):
        loaded = yaml.safe_load((EXAMPLES / "repeats_sections.yaml").read_text())
        authored = loaded["sections"]
        assert list(authored) == ["fodo_channel", "fodo_cell"]
        assert (
            expand_section_order("fodo_channel", authored["fodo_channel"], authored)
            == CELL * 3
        )


class TestRefusesTheAmbiguous:
    @pytest.mark.parametrize(
        "authored",
        [
            pytest.param({"a": ["b"], "b": [{"a": {"repeat": 2}}]}, id="via-another"),
            pytest.param({"a": ["a"]}, id="directly"),
        ],
    )
    def test_a_line_that_includes_itself(self, authored):
        with pytest.raises(LatticeError, match="includes itself"):
            expand_section_order("a", authored["a"], authored)

    def test_a_repeat_of_zero(self):
        with pytest.raises(ValueError, match="not be\\s+zero"):
            expand_section_order("s", [{"q1": {"repeat": 0}}], {})

    @pytest.mark.parametrize("count", ["3", 3.0, True, None])
    def test_a_repeat_that_is_not_an_integer(self, count):
        with pytest.raises(TypeError, match="must be an"):
            expand_section_order("s", [{"q1": {"repeat": count}}], {})

    def test_an_unknown_option(self):
        with pytest.raises(TypeError, match="'repeat' count"):
            expand_section_order("s", [{"q1": {"reverse": True}}], {})

    @pytest.mark.parametrize("entry", [["a", "b"], 3, None, {"a": 1, "b": 2}])
    def test_an_entry_that_is_neither_a_name_nor_a_name_with_options(self, entry):
        with pytest.raises(TypeError):
            expand_section_order("s", [entry], {})


class TestThroughAMachine:
    @pytest.fixture
    def compact(self):
        return machine(COMPACT)

    def test_the_channel_holds_fifteen_placements(self, compact):
        assert len(compact.sections["fodo_channel"].order) == 15

    def test_a_line_no_layout_lists_is_not_a_section(self, compact):
        assert list(compact.sections) == ["fodo_channel"]

    def test_the_authored_order_is_kept(self, compact):
        assert compact.sections["fodo_channel"]._authored_order == [
            {"fodo_cell": {"repeat": 3}}
        ]

    def test_a_flat_section_keeps_no_authored_order(self):
        flat = machine({"fodo_channel": CELL})
        assert flat.sections["fodo_channel"]._authored_order is None

    def test_each_occurrence_became_its_own_element(self, compact):
        assert compact.sections["fodo_channel"].order.count("drift1.1") == 1
        assert "drift1.6" in compact.elements
        assert "drift1" not in compact.elements

    def test_a_line_that_includes_itself_is_rejected_at_load(self):
        with pytest.raises(LatticeError, match="includes itself"):
            machine({"fodo_channel": [{"fodo_channel": {"repeat": 2}}]})

    def test_a_line_that_repeats_nothing_may_also_be_a_section(self):
        both = machine(
            {"fodo_channel": ["fodo_cell"], "fodo_cell": CELL[:4]},
            layouts=("fodo_cell", "fodo_channel"),
        )
        assert both.sections["fodo_channel"].order == CELL[:4]

    def test_a_repeating_line_may_not_also_be_a_section(self):
        # both would want their own placement of the same numbered copies
        with pytest.raises(ValidationError, match="same system"):
            machine(COMPACT, layouts=("fodo_cell", "fodo_channel"))


class TestReversalThroughAMachine:
    """MAD-X's ``(cell, -cell)``: a mirror-symmetric line from one definition."""

    @pytest.fixture
    def mirrored(self):
        return machine(
            {
                "fodo_channel": ["fodo_cell", {"fodo_cell": {"repeat": -1}}],
                "fodo_cell": CELL[:4],
            }
        )

    def test_the_second_half_is_the_first_reversed(self, mirrored):
        order = mirrored.sections["fodo_channel"].order
        first = [n.split(".")[0] for n in order[:4]]
        second = [n.split(".")[0] for n in order[4:]]
        assert second == first[::-1]

    def test_it_places_symmetrically_about_the_centre(self, mirrored):
        order = mirrored.sections["fodo_channel"].order
        physicals = [mirrored.elements[n].physical for n in order]
        centre = physicals[-1].s + physicals[-1].length / 2
        for near, far in zip(physicals, reversed(physicals)):
            assert near.s == pytest.approx(centre - far.s)

    def test_each_half_holds_its_own_copies(self, mirrored):
        assert mirrored.elements["quad1.1"].physical.s != (
            mirrored.elements["quad1.2"].physical.s
        )

    def test_the_reversal_survives_the_round_trip(self, mirrored, tmp_path):
        sections = written_sections(mirrored, tmp_path)
        assert sections["fodo_channel"]["elements"] == [
            "fodo_cell",
            {"fodo_cell": {"repeat": -1}},
        ]
        reloaded = reload(tmp_path)
        for name, element in mirrored.elements.items():
            assert reloaded[name].physical.s == pytest.approx(element.physical.s)


class TestAgreesWithTheExpandedForm:
    @pytest.fixture
    def pair(self):
        return machine(COMPACT), machine({"fodo_channel": CELL * 3})

    def test_the_same_order(self, pair):
        compact, expanded = pair
        assert compact.sections["fodo_channel"].order == (
            expanded.sections["fodo_channel"].order
        )

    def test_the_same_positions(self, pair):
        compact, expanded = pair
        for name in compact.sections["fodo_channel"].order:
            assert compact.elements[name].physical.s == pytest.approx(
                expanded.elements[name].physical.s
            )

    def test_the_channel_is_three_cells_long(self, pair):
        compact, _ = pair
        last = compact.elements[compact.sections["fodo_channel"].order[-1]].physical
        assert last.s + last.length / 2 == pytest.approx(3 * 3.0)


class TestOutsideASequentialSection:
    def test_it_expands_but_does_not_number(self):
        positioned = {
            "drift1": Drift(
                name="drift1",
                hardware_class="Drift",
                machine_area="FODO",
                physical={"length": 0.25, "s": 0.25, "s_point": "end"},
            ),
            "quad1": quad("quad1", 1.0, 1.0, "FODO", s=1.25, s_point="end"),
        }
        with quiet():
            model = MachineModel(
                elements=positioned,
                section={
                    "sections": {"S": [{"pair": {"repeat": 2}}], "pair": CELL[:2]}
                },
                layout={"layouts": {"L": ["S"]}, "default_layout": "L"},
            )
        assert model.sections["S"].order == ["drift1", "quad1"] * 2
        assert model.sections["S"]._repeat_origins == {}


class TestWritesTheCompactFormBackOut:
    @pytest.fixture
    def written(self, tmp_path):
        model = machine(COMPACT)
        return model, tmp_path, written_sections(model, tmp_path)

    def test_the_repeat_survives(self, written):
        _, _, sections = written
        assert sections["fodo_channel"]["elements"] == [{"fodo_cell": {"repeat": 3}}]

    def test_the_nested_line_is_written_too(self, written):
        _, _, sections = written
        assert sections["fodo_cell"]["elements"] == CELL

    def test_it_reloads_to_the_same_machine(self, written):
        model, path, _ = written
        reloaded = reload(path)
        assert len(reloaded.elements) == len(model.elements)
        for name, element in model.elements.items():
            assert reloaded[name].physical.s == pytest.approx(element.physical.s)

    def test_a_copy_edited_since_load_is_written_out_flat(self, tmp_path):
        model = machine(COMPACT)
        model.elements["drift1.4"].physical.length = 0.4
        with pytest.warns(UserWarning, match="fully expanded"):
            export_machine_combined_file(
                str(tmp_path), model, position_mode="sequential"
            )
        sections = yaml.safe_load((tmp_path / "_sections.yaml").read_text())["sections"]
        assert len(sections["fodo_channel"]["elements"]) == 15
        assert "fodo_cell" not in sections

    def test_a_flat_section_is_unaffected(self, tmp_path):
        sections = written_sections(machine({"fodo_channel": CELL * 3}), tmp_path)
        assert sections["fodo_channel"]["elements"] == CELL * 3


class TestTheExampleFiles:
    @pytest.fixture
    def example(self):
        with quiet():
            return LAURA(
                element_list=str(EXAMPLES / "repeats_elements.yaml"),
                section=str(EXAMPLES / "repeats_sections.yaml"),
                layout=str(EXAMPLES / "repeats_layouts.yaml"),
            )

    def test_four_definitions_become_fifteen_placements(self, example):
        assert len(example.sections["fodo_channel"].order) == 15
        assert len(example.elements) == 15

    def test_the_cell_is_three_metres(self, example):
        order = example.sections["fodo_channel"].order
        cell = example.elements[order[4]].physical
        assert cell.s + cell.length / 2 == pytest.approx(3.0)

    def test_the_inherited_quadrupole_flipped_sign(self, example):
        assert example["quad1.1"].magnetic.k1l == pytest.approx(1.0)
        assert example["quad2.1"].magnetic.k1l == pytest.approx(-1.0)
        assert example["quad2.1"].physical.length == pytest.approx(1.0)
