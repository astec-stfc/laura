"""Authored repetition and nested lines in a section order.

A section may be written as ``fodo_cell: {repeat: 3}`` over a line defined
once, the way PALS, MAD-X and elegant all let you.  Expansion happens at load,
so everything downstream keeps seeing the flat name list it already handled --
including the per-occurrence numbering sequential placement does for a name
written out twice by hand.

The oracle here is :class:`TestAgreesWithTheExpandedForm`: the compact channel
and the same channel typed out in full must give the same fifteen placements.
"""

import warnings
from pathlib import Path

import pytest
import yaml
from pydantic import ValidationError

from laura import LAURA
from laura.Exporters.YAML import export_machine_combined_file
from laura.models.element import Drift, Quadrupole
from laura.models.elementList import (
    LatticeError,
    MachineModel,
    expand_section_order,
)

EXAMPLES = Path(__file__).resolve().parents[1] / "examples" / "testing"

CELL = ["drift1", "quad1", "drift2", "quad2", "drift1"]


def drift(name, length):
    return Drift(
        name=name,
        hardware_class="Drift",
        machine_area="FODO",
        physical={"length": length},
    )


def quad(name, length, k1l):
    return Quadrupole(
        name=name,
        hardware_class="Magnet",
        machine_area="FODO",
        magnetic={"magnetic_length": length, "k1l": k1l},
        physical={"length": length},
    )


def elements():
    """The four FODO element definitions of the PALS example."""
    return {
        e.name: e
        for e in (
            drift("drift1", 0.25),
            quad("quad1", 1.0, 1.0),
            drift("drift2", 0.5),
            quad("quad2", 1.0, -1.0),
        )
    }


def machine(sections, layouts=("fodo_channel",)):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        return MachineModel(
            elements=elements(),
            section={"sections": sections},
            layout={
                "layouts": {"fodo_lattice": list(layouts)},
                "default_layout": "fodo_lattice",
            },
        )


# ---------------------------------------------------------------------------
# the expansion itself
# ---------------------------------------------------------------------------


class TestExpandSectionOrder:
    def test_a_flat_order_is_left_alone(self):
        assert expand_section_order("cell", CELL, {"cell": CELL}) == CELL

    def test_a_repeat_writes_the_entry_out_that_many_times(self):
        assert expand_section_order("s", [{"q1": {"repeat": 3}}], {}) == ["q1"] * 3

    def test_a_named_line_is_spliced_in(self):
        authored = {"cell": CELL, "channel": ["q0", "cell"]}
        assert (
            expand_section_order("channel", authored["channel"], authored)
            == ["q0"] + CELL
        )

    def test_a_repeated_line_is_spliced_in_that_many_times(self):
        authored = {"cell": CELL, "channel": [{"cell": {"repeat": 3}}]}
        assert (
            expand_section_order("channel", authored["channel"], authored) == CELL * 3
        )

    def test_lines_nest(self):
        authored = {
            "inner": ["a", "b"],
            "middle": [{"inner": {"repeat": 2}}],
            "outer": [{"middle": {"repeat": 2}}, "c"],
        }
        assert expand_section_order("outer", authored["outer"], authored) == [
            "a",
            "b",
        ] * 4 + ["c"]

    def test_a_negative_repeat_reverses_the_entry(self):
        authored = {"cell": ["q1", "q2", "q3"]}
        assert expand_section_order("s", [{"cell": {"repeat": -1}}], authored) == [
            "q3",
            "q2",
            "q1",
        ]

    def test_a_negative_repeat_reverses_then_repeats(self):
        authored = {"cell": ["q1", "q2", "q3"]}
        assert (
            expand_section_order("s", [{"cell": {"repeat": -2}}], authored)
            == ["q3", "q2", "q1"] * 2
        )

    def test_a_reversed_line_joins_onto_a_forward_one(self):
        # the MAD-X idiom: LINE = (cell, -cell)
        authored = {"cell": ["q1", "q2", "q3"]}
        assert expand_section_order(
            "s", ["cell", {"cell": {"repeat": -1}}], authored
        ) == ["q1", "q2", "q3", "q3", "q2", "q1"]

    def test_reversing_a_single_element_is_a_no_op(self):
        assert expand_section_order("s", [{"q1": {"repeat": -1}}], {}) == ["q1"]

    def test_reversal_applies_after_the_nested_line_is_expanded(self):
        authored = {
            "inner": ["a", "b"],
            "cell": ["x", {"inner": {"repeat": 2}}, "y"],
        }
        assert expand_section_order("s", [{"cell": {"repeat": -1}}], authored) == [
            "y",
            "b",
            "a",
            "b",
            "a",
            "x",
        ]

    def test_a_line_may_be_used_before_it_is_defined(self):
        # the example file writes fodo_channel above fodo_cell
        loaded = yaml.safe_load((EXAMPLES / "repeats_sections.yaml").read_text())
        authored = loaded["sections"]
        assert list(authored) == ["fodo_channel", "fodo_cell"]
        assert (
            expand_section_order("fodo_channel", authored["fodo_channel"], authored)
            == CELL * 3
        )


class TestRefusesTheAmbiguous:
    def test_a_line_that_includes_itself(self):
        authored = {"a": ["b"], "b": [{"a": {"repeat": 2}}]}
        with pytest.raises(LatticeError, match="includes itself"):
            expand_section_order("a", authored["a"], authored)

    def test_a_line_that_includes_itself_directly(self):
        with pytest.raises(LatticeError, match="includes itself"):
            expand_section_order("a", ["a"], {"a": ["a"]})

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


# ---------------------------------------------------------------------------
# through a machine
# ---------------------------------------------------------------------------


class TestThroughAMachine:
    @pytest.fixture
    def compact(self):
        return machine(
            {"fodo_channel": [{"fodo_cell": {"repeat": 3}}], "fodo_cell": CELL}
        )

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
        # Both sections would want their own placement of the same numbered
        # copies. Refused at load rather than one of them silently winning.
        with pytest.raises(ValidationError, match="same system"):
            machine(
                {"fodo_channel": [{"fodo_cell": {"repeat": 3}}], "fodo_cell": CELL},
                layouts=("fodo_cell", "fodo_channel"),
            )


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
        # the same definition placed twice is two devices at two positions
        assert mirrored.elements["quad1.1"].physical.s != (
            mirrored.elements["quad1.2"].physical.s
        )

    def test_the_reversal_survives_the_round_trip(self, mirrored, tmp_path):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            export_machine_combined_file(
                str(tmp_path), mirrored, position_mode="sequential"
            )
        sections = yaml.safe_load((tmp_path / "_sections.yaml").read_text())["sections"]
        assert sections["fodo_channel"]["elements"] == [
            "fodo_cell",
            {"fodo_cell": {"repeat": -1}},
        ]
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            reloaded = LAURA(
                element_list=str(tmp_path / "summary.yaml"),
                section=str(tmp_path / "_sections.yaml"),
                layout={
                    "layouts": {"fodo_lattice": ["fodo_channel"]},
                    "default_layout": "fodo_lattice",
                },
            )
        for name, element in mirrored.elements.items():
            assert reloaded[name].physical.s == pytest.approx(element.physical.s)


class TestAgreesWithTheExpandedForm:
    """The compact channel and the hand-typed one must land in the same place."""

    @pytest.fixture
    def pair(self):
        compact = machine(
            {"fodo_channel": [{"fodo_cell": {"repeat": 3}}], "fodo_cell": CELL}
        )
        return compact, machine({"fodo_channel": CELL * 3})

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
    """Repetition is an authoring feature; it expands whatever the mode."""

    def test_it_expands_but_does_not_number(self):
        positioned = {
            "drift1": Drift(
                name="drift1",
                hardware_class="Drift",
                machine_area="FODO",
                physical={"length": 0.25, "s": 0.25, "s_point": "end"},
            ),
            "quad1": quad("quad1", 1.0, 1.0),
        }
        positioned["quad1"] = Quadrupole(
            name="quad1",
            hardware_class="Magnet",
            machine_area="FODO",
            magnetic={"magnetic_length": 1.0, "k1l": 1.0},
            physical={"length": 1.0, "s": 1.25, "s_point": "end"},
        )
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            model = MachineModel(
                elements=positioned,
                section={
                    "sections": {"S": [{"pair": {"repeat": 2}}], "pair": CELL[:2]}
                },
                layout={"layouts": {"L": ["S"]}, "default_layout": "L"},
            )
        assert model.sections["S"].order == ["drift1", "quad1"] * 2
        assert model.sections["S"]._repeat_origins == {}


# ---------------------------------------------------------------------------
# round trip
# ---------------------------------------------------------------------------


class TestWritesTheCompactFormBackOut:
    @pytest.fixture
    def written(self, tmp_path):
        model = machine(
            {"fodo_channel": [{"fodo_cell": {"repeat": 3}}], "fodo_cell": CELL}
        )
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            export_machine_combined_file(
                str(tmp_path), model, position_mode="sequential"
            )
        sections = yaml.safe_load((tmp_path / "_sections.yaml").read_text())["sections"]
        return model, tmp_path, sections

    def test_the_repeat_survives(self, written):
        _, _, sections = written
        assert sections["fodo_channel"]["elements"] == [{"fodo_cell": {"repeat": 3}}]

    def test_the_nested_line_is_written_too(self, written):
        _, _, sections = written
        assert sections["fodo_cell"]["elements"] == CELL

    def test_it_reloads_to_the_same_machine(self, written):
        model, path, _ = written
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            reloaded = LAURA(
                element_list=str(path / "summary.yaml"),
                section=str(path / "_sections.yaml"),
                layout={
                    "layouts": {"fodo_lattice": ["fodo_channel"]},
                    "default_layout": "fodo_lattice",
                },
            )
        assert len(reloaded.elements) == len(model.elements)
        for name, element in model.elements.items():
            assert reloaded[name].physical.s == pytest.approx(element.physical.s)

    def test_a_copy_edited_since_load_is_written_out_flat(self, tmp_path):
        model = machine(
            {"fodo_channel": [{"fodo_cell": {"repeat": 3}}], "fodo_cell": CELL}
        )
        model.elements["drift1.4"].physical.length = 0.4
        with pytest.warns(UserWarning, match="fully expanded"):
            export_machine_combined_file(
                str(tmp_path), model, position_mode="sequential"
            )
        sections = yaml.safe_load((tmp_path / "_sections.yaml").read_text())["sections"]
        assert len(sections["fodo_channel"]["elements"]) == 15
        assert "fodo_cell" not in sections

    def test_a_flat_section_is_unaffected(self, tmp_path):
        model = machine({"fodo_channel": CELL * 3})
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            export_machine_combined_file(
                str(tmp_path), model, position_mode="sequential"
            )
        sections = yaml.safe_load((tmp_path / "_sections.yaml").read_text())["sections"]
        assert sections["fodo_channel"]["elements"] == CELL * 3


# ---------------------------------------------------------------------------
# the shipped example
# ---------------------------------------------------------------------------


class TestTheExampleFiles:
    @pytest.fixture
    def example(self):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
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
