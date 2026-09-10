"""Tier-2 PALS export: a multipass section as a nested ``multipass`` BeamLine.

``to_pals`` flattens -- one branch per traversal, each with its own copy of the
hardware. PALS can hold the identity instead: a ``BeamLine`` marked
``multipass`` and named twice is one piece of hardware the beam visits twice,
and the parser stamps a ``multipass_index`` on each visit. Both directions are
checked here, the export through the reference parser rather than through
LAURA's own reading of what it wrote.

The ERL is the one ``test_bmad_multipass`` builds: the same machine written for
the other backend that can hold a multipass line.
"""

import warnings

import pytest
import yaml

from laura.models.elementList import MachineModel
from laura.translator.converters.codes.pals import PalsLatticeImporter
from laura.translator.converters.layout import MachineLayoutTranslator
from laura.translator.utils.pals import parse_pals_file, parser_available

from .test_bmad_multipass import ERL, SECTIONS, elements

pytestmark = pytest.mark.skipif(
    not parser_available(), reason="palsparserpy is not installed"
)


def translator(layout, *, multipass=True):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        model = MachineModel(
            elements=elements(),
            section={"sections": SECTIONS},
            layout={"layouts": {"ERL": layout}, "default_layout": "ERL"},
        )
    built = model.lattices["ERL"]
    for section in built.sections.values():
        # A branch with no reference energy is not a document the parser will
        # take, and the fixture is built for Bmad, which states it separately.
        section.reference_energy = 1.0e8
    return MachineLayoutTranslator.from_layout(built, multipass=multipass)


@pytest.fixture(scope="module")
def document():
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        return translator(ERL).to_pals_multipass("electron")


@pytest.fixture(scope="module")
def facility(document):
    entries = yaml.safe_load(document)["PALS"]["facility"]
    return {name: body for entry in entries for name, body in entry.items()}


# --- the structure -------------------------------------------------------


def test_the_multipass_section_is_a_multipass_beamline(facility):
    assert facility["LINAC"] == {
        "kind": "BeamLine",
        "multipass": True,
        "line": ["CAV_01", "LIN_Q"],
    }


def test_a_single_pass_section_is_an_ordinary_beamline(facility):
    assert facility["ARC"] == {"kind": "BeamLine", "line": ["ARC_B"]}


def test_the_beam_path_names_the_multipass_line_once_per_pass(facility):
    assert [name for name in facility["ERL"]["line"] if isinstance(name, str)] == [
        "INJECTOR",
        "LINAC",
        "ARC",
        "LINAC",
        "DUMP_element",
    ]


def test_the_sections_are_sub_lines_rather_than_branches(facility):
    # One branch: the beam path. A section listed as a branch would be a
    # machine of its own, tracked separately from the path through it.
    assert facility["ERL_lattice"] == {"kind": "Lattice", "branches": ["ERL"]}


def test_the_shared_hardware_is_defined_exactly_once(document):
    assert document.count("CAV_01:") == 1
    assert document.count("LIN_Q:") == 1


def test_a_section_named_like_a_parameter_group_is_renamed():
    # DUMP is two or more letters, capitalised, ending in P, which is how PALS
    # tells a parameter group from a name.
    with pytest.warns(UserWarning, match="DUMP -> DUMP_element"):
        translator(ERL).to_pals_multipass("electron")


def test_per_pass_settings_are_dropped_with_a_warning():
    # The ERL's return pass is 180 degrees off. PALS defines the cavity once,
    # and RFP's multipass_phase does not say which pass it belongs to.
    with pytest.warns(UserWarning, match="per-pass settings on LINAC pass 2"):
        translator(ERL).to_pals_multipass("electron")


# --- what it refuses -----------------------------------------------------


def test_a_flattened_translator_is_refused():
    with pytest.raises(ValueError, match="multipass=True"):
        translator(ERL, multipass=False).to_pals_multipass("electron")


def test_a_reversed_pass_is_refused():
    # PALS takes `direction: -1` on a line item, but the reference parser
    # leaves the item unexpanded, so the sub-line would go missing.
    reversed_leg = [
        "INJECTOR",
        {"LINAC": {"multipass": 1}},
        "ARC",
        {"LINAC": {"multipass": 2, "direction": -1}},
        "DUMP",
    ]
    with pytest.raises(NotImplementedError, match="use to_pals..."):
        translator(reversed_leg).to_pals_multipass("electron")


# --- against the reference parser ----------------------------------------


@pytest.fixture(scope="module")
def written(document, tmp_path_factory):
    path = tmp_path_factory.mktemp("pals") / "erl.pals.yaml"
    path.write_text(document)
    return path


@pytest.fixture(scope="module")
def branch(written):
    parsed = parse_pals_file(str(written))
    assert parsed.errors == []
    return parsed.branch("ERL")


def test_the_parser_expands_the_line_twice(branch):
    assert [element.name for element in branch.elements if element.length] == [
        "INJ_Q",
        "CAV_01",
        "LIN_Q",
        "ARC_B",
        "CAV_01",
        "LIN_Q",
        "DMP_Q",
    ]


def test_the_parser_numbers_the_visits(branch):
    passes = {
        (element.name, element.parameters.get("multipass_index"))
        for element in branch.elements
        if element.parameters.get("multipass_index")
    }
    assert passes == {("CAV_01", 1), ("LIN_Q", 1), ("CAV_01", 2), ("LIN_Q", 2)}


# --- back again ----------------------------------------------------------


@pytest.fixture(scope="module")
def imported(written):
    return PalsLatticeImporter(source_file=str(written)).create_layout()


def test_the_shared_section_comes_back_once(imported):
    orders = [section.order for section in imported.sections.values()]
    assert orders.count(["CAV_01", "LIN_Q"]) == 1


def test_the_beam_path_comes_back_pass_by_pass(imported):
    numbers = [entry.number for entry in imported.passes]
    sections = [entry.section for entry in imported.passes]
    assert numbers == [None, 1, None, 2, None]
    assert sections[1] == sections[3]


def test_the_hardware_keeps_its_own_name(imported):
    # The branch numbers repeated names apart; a multipass import drops the
    # later passes, so the copies the numbering told apart are gone.
    for section in imported.sections.values():
        assert not any("." in name for name in section.order)
