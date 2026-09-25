"""Tier-2 Bmad export: a multipass section as a real Bmad multipass lord.

:meth:`~laura.translator.converters.layout.MachineLayoutTranslator.to_bmad`
flattens -- one standalone file per occurrence, which every backend can read
and which is the honest answer for codes with nowhere to put per-pass state.
Bmad is the one backend that can hold the *identity* instead, so
``to_bmad_multipass`` writes the hardware once and lets ``NAME\\1``, ``NAME\\2``
be the beam's visits to it.

What Bmad will and will not take per slave is not guessable and was measured
against Tao 2026-09-09: ``phi0_multipass`` yes, ``k1`` and ``e_tot`` no --
those are lord attributes, and a lattice file setting them per slave parses
without complaint and has no effect.
"""

import os
import warnings
from pathlib import Path

import pytest

from laura.models.element import Quadrupole, RFCavity
from laura.models.elementList import MachineModel
from laura.translator.converters.layout import MachineLayoutTranslator

SECTIONS = {
    "INJECTOR": ["INJ_Q"],
    "LINAC": ["CAV_01", "LIN_Q"],
    "ARC": ["ARC_B"],
    "DUMP": ["DMP_Q"],
}

# The decelerating return leg of an ERL: same cavity, 180 degrees apart.
ERL = [
    "INJECTOR",
    {"LINAC": {"multipass": 1}},
    "ARC",
    {"LINAC": {"multipass": 2, "overrides": {"CAV_01": {"cavity.phase": 180}}}},
    "DUMP",
]


def elements():
    built = {
        name: Quadrupole(
            name=name,
            hardware_class="Magnet",
            machine_area="A",
            magnetic={"magnetic_length": length, "k1l": 1.0},
            physical={"length": length},
        )
        for name, length in (
            ("INJ_Q", 0.2),
            ("LIN_Q", 0.3),
            ("ARC_B", 0.4),
            ("DMP_Q", 0.2),
        )
    }
    built["CAV_01"] = RFCavity(
        name="CAV_01",
        machine_area="A",
        physical={"length": 0.6},
        cavity={"phase": 0.0, "field_amplitude": 1e7},
    )
    return built


def translator(layout, *, multipass=True):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        model = MachineModel(
            elements=elements(),
            section={"sections": SECTIONS},
            layout={"layouts": {"ERL": layout}, "default_layout": "ERL"},
        )
    return MachineLayoutTranslator.from_layout(
        model.lattices["ERL"], multipass=multipass
    )


@pytest.fixture
def erl():
    return translator(ERL)


@pytest.fixture
def lattice(erl):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        return erl.to_bmad_multipass("electron")


# --- the structure -------------------------------------------------------


def test_the_multipass_section_is_a_multipass_line(lattice):
    assert "LINAC: line[multipass] = (CAV_01, LIN_Q)\n" in lattice


def test_a_single_pass_section_is_an_ordinary_line(lattice):
    assert "ARC: line = (ARC_B)\n" in lattice


def test_the_beam_path_lists_the_multipass_line_once_per_pass(lattice):
    assert "ERL: line = (INJECTOR, LINAC, ARC, LINAC, DUMP)\n" in lattice
    assert "use, ERL\n" in lattice


def test_the_shared_hardware_is_defined_exactly_once(lattice):
    assert lattice.count("CAV_01: lcavity") == 1
    assert lattice.count("LIN_Q: quadrupole") == 1


def test_one_file_holds_every_section(lattice):
    for name in SECTIONS:
        assert f"{name}: line" in lattice


def test_the_header_is_written_once(lattice):
    assert lattice.count("parameter[geometry]") == 1
    assert lattice.count("parameter[particle] = electron") == 1


# --- per-pass state ------------------------------------------------------


def test_a_per_pass_phase_becomes_phi0_multipass(lattice):
    # -0.5, not 180: Bmad phases are turns, and LAURA's sign convention is
    # `-phase / 360`, which is what the element definition already writes.
    assert "CAV_01\\2[phi0_multipass] = -0.5\n" in lattice


def test_pass_one_carries_no_settings_of_its_own(lattice):
    assert "CAV_01\\1[" not in lattice


def test_settings_come_after_the_lattice_is_expanded(lattice):
    # Slaves do not exist until `use` has been expanded, so Bmad cannot resolve
    # `CAV_01\2` before this line.
    assert lattice.index("expand_lattice") < lattice.index("CAV_01\\2[")
    assert lattice.index("use, ERL") < lattice.index("expand_lattice")


def test_a_layout_with_nothing_per_pass_does_not_expand(erl):
    plain = translator(["INJECTOR", "LINAC", "ARC", "DUMP"])
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        assert "expand_lattice" not in plain.to_bmad_multipass("electron")


def test_a_lord_only_attribute_is_dropped_with_a_warning():
    # Strength is the case that matters: an ERL's shared magnet holds its field,
    # so `k` differs per pass -- but Bmad keeps `k1` on the lord, and resolving
    # this needs `field_master`, which v1 leaves as a slot.
    changed = [
        "INJECTOR",
        {"LINAC": {"multipass": 1}},
        "ARC",
        {"LINAC": {"multipass": 2, "overrides": {"LIN_Q": {"magnetic.k1l": 2.0}}}},
        "DUMP",
    ]
    with pytest.warns(UserWarning, match="k1.*multipass lord"):
        lattice = translator(changed).to_bmad_multipass("electron")
    assert "LIN_Q\\2[" not in lattice


# --- what it refuses -----------------------------------------------------


def test_a_flattened_translator_is_refused(erl):
    plain = translator(ERL, multipass=False)
    with pytest.raises(ValueError, match="multipass=True"):
        plain.to_bmad_multipass("electron")


def test_a_reversed_pass_is_refused():
    reversed_leg = [
        "INJECTOR",
        {"LINAC": {"multipass": 1}},
        "ARC",
        {"LINAC": {"multipass": 2, "direction": -1}},
        "DUMP",
    ]
    with pytest.raises(NotImplementedError, match="reflection patch"):
        translator(reversed_leg).to_bmad_multipass("electron")


# --- against Tao ---------------------------------------------------------

LIBTAO = Path(
    os.environ.get(
        "LAURA_LIBTAO",
        Path.home() / "Documents" / "bmad-ecosystem" / "production" / "lib" / "libtao.so",
    )
).expanduser()


@pytest.mark.skipif(not LIBTAO.exists(), reason="libtao is not installed")
def test_tao_reads_the_export_as_a_multipass_lord(lattice, tmp_path):
    pytest.importorskip("pytao")
    os.environ.setdefault("ACC_ROOT_DIR", str(LIBTAO.parent.parent.parent))
    from pytao import Tao

    path = tmp_path / "erl.bmad"
    path.write_text(f"beginning[e_tot] = 10e6\n{lattice}")
    tao = Tao(f"-lat {path} -noplot")

    names = list(tao.lat_list("*", "ele.name", flags=""))
    assert "CAV_01" in names and "CAV_01\\1" in names and "CAV_01\\2" in names

    assert tao.ele_gen_attribs("CAV_01")["lord_status"] == "Multipass_Lord"
    assert tao.ele_gen_attribs("CAV_01\\1")["slave_status"] == "Multipass_Slave"
    # The point of the whole exercise: one cavity, and the return pass is 180
    # degrees off it.
    assert tao.ele_gen_attribs("CAV_01\\1")["PHI0_MULTIPASS"] == 0.0
    assert tao.ele_gen_attribs("CAV_01\\2")["PHI0_MULTIPASS"] == -0.5


# --- back again ----------------------------------------------------------


@pytest.fixture
def imported(lattice, tmp_path):
    """The exported lattice read back through Tao."""
    pytest.importorskip("pytao")
    if not LIBTAO.exists():
        pytest.skip("libtao is not installed")
    os.environ.setdefault("ACC_ROOT_DIR", str(LIBTAO.parent.parent.parent))
    from laura.translator.converters.codes.bmad import BmadLatticeImporter

    path = tmp_path / "erl.bmad"
    path.write_text(f"beginning[e_tot] = 10e6\n{lattice}")
    importer = BmadLatticeImporter(lattice_file=str(path), libtao=str(LIBTAO))
    return importer.create_layout(1, name="ERL")


def traversal(layout):
    return [(entry.section, entry.number) for entry in layout.passes]


def test_the_shared_section_comes_back_once(imported):
    sections = [entry.section for entry in imported.passes]
    repeated = {name for name in sections if sections.count(name) > 1}
    assert len(repeated) == 1
    assert imported.sections[repeated.pop()].order == ["CAV_01", "LIN_Q"]


def test_the_shared_section_is_entered_twice(imported):
    numbers = [entry.number for entry in imported.passes]
    assert numbers == [None, 1, None, 2, None]


def test_the_hardware_loses_the_slave_numbering(imported):
    for section in imported.sections.values():
        assert not any("\\" in name for name in section.order)


def test_the_per_pass_phase_comes_back_as_an_override(imported):
    second = next(entry for entry in imported.passes if entry.number == 2)
    assert second.overrides == {"CAV_01": {"cavity.phase": 180.0}}


def test_pass_one_carries_no_overrides(imported):
    first = next(entry for entry in imported.passes if entry.number == 1)
    assert first.overrides == {}


def test_reference_energy_is_not_read_back_as_momentum(imported):
    # Bmad keeps strength on the multipass lord, so both passes really do share
    # one `k1`. A per-pass momentum would make LAURA rescale it on the way out.
    assert all(entry.momentum is None for entry in imported.passes)


def test_a_lattice_with_no_multipass_still_imports_as_one_section(tmp_path):
    pytest.importorskip("pytao")
    if not LIBTAO.exists():
        pytest.skip("libtao is not installed")
    os.environ.setdefault("ACC_ROOT_DIR", str(LIBTAO.parent.parent.parent))
    from laura.translator.converters.codes.bmad import BmadLatticeImporter

    path = tmp_path / "plain.bmad"
    path.write_text(
        "parameter[geometry] = open\nbeginning[e_tot] = 10e6\n"
        "Q1: quadrupole, l = 0.1, k1 = 0.3\nD1: drift, l = 0.2\n"
        "LIN: line = (Q1, D1, Q1)\nuse, LIN\n"
    )
    layout = BmadLatticeImporter(
        lattice_file=str(path), libtao=str(LIBTAO)
    ).create_layout(1, name="LIN")
    assert len(layout.sections) == 1
    assert traversal(layout) == [(next(iter(layout.sections)), None)]
