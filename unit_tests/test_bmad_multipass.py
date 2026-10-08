"""Bmad multipass export: hardware written once, ``NAME\\1``, ``NAME\\2`` its passes.

Tao takes ``phi0_multipass`` per slave, but ``k1``/``e_tot`` are lord-only and silently ignored.
"""

import os
from pathlib import Path

import pytest

from laura.models.element import RFCavity, TwissMatch
from laura.models.elementList import MachineModel
from laura.translator.converters.layout import MachineLayoutTranslator
from unit_tests.helpers import quad, quiet

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
        name: quad(name, length, 1.0, machine_area="A")
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
    with quiet():
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
    with quiet():
        return erl.to_bmad_multipass("electron")


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


def test_a_per_pass_phase_becomes_phi0_multipass(lattice):
    # Bmad phases are turns, and LAURA writes `-phase / 360`.
    assert "CAV_01\\2[phi0_multipass] = -0.5\n" in lattice


def test_pass_one_carries_no_settings_of_its_own(lattice):
    assert "CAV_01\\1[" not in lattice


def test_settings_come_after_the_lattice_is_expanded(lattice):
    # Slaves exist only once `use` has been expanded.
    assert lattice.index("expand_lattice") < lattice.index("CAV_01\\2[")
    assert lattice.index("use, ERL") < lattice.index("expand_lattice")


def test_a_layout_with_nothing_per_pass_does_not_expand(erl):
    plain = translator(["INJECTOR", "LINAC", "ARC", "DUMP"])
    with quiet():
        assert "expand_lattice" not in plain.to_bmad_multipass("electron")


def test_a_lord_only_attribute_is_dropped_with_a_warning():
    # Bmad keeps `k1` on the lord; per-pass strength would need `field_master`.
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


def test_a_fixer_that_starts_a_later_section_stays_in_the_line():
    # Only the first section gives the beginning Twiss; a later fixer declares design optics.
    with quiet():
        model = MachineModel(
            elements=elements()
            | {
                "FIX": TwissMatch(
                    name="FIX", machine_area="A", simulation={"beta_x": 2, "beta_y": 3}
                )
            },
            section={"sections": SECTIONS | {"OPTICS": ["FIX"]}},
            layout={
                "layouts": {"P": ["INJECTOR", "OPTICS", "ARC"]},
                "default_layout": "P",
            },
        )
        lattice = MachineLayoutTranslator.from_layout(
            model.lattices["P"], multipass=True
        ).to_bmad_multipass("electron")
    assert "OPTICS: line = (FIX)\n" in lattice
    assert "FIX: fixer, beta_a_stored = 2.0, beta_b_stored = 3.0" in lattice
    assert "beginning[beta_a]" not in lattice


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
    assert tao.ele_gen_attribs("CAV_01\\1")["PHI0_MULTIPASS"] == 0.0
    assert tao.ele_gen_attribs("CAV_01\\2")["PHI0_MULTIPASS"] == -0.5


@pytest.fixture
def imported(lattice, tmp_path):
    return _import_layout(tmp_path, f"beginning[e_tot] = 10e6\n{lattice}", "ERL")


def _import_layout(tmp_path, text, name):
    pytest.importorskip("pytao")
    if not LIBTAO.exists():
        pytest.skip("libtao is not installed")
    os.environ.setdefault("ACC_ROOT_DIR", str(LIBTAO.parent.parent.parent))
    from laura.translator.converters.codes.bmad import BmadLatticeImporter

    path = tmp_path / f"{name}.bmad"
    path.write_text(text)
    importer = BmadLatticeImporter(lattice_file=str(path), libtao=str(LIBTAO))
    return importer.create_layout(1, name=name)


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
    # Bmad keeps strength on the lord; a per-pass momentum would make LAURA rescale `k1`.
    assert all(entry.momentum is None for entry in imported.passes)


def test_a_lattice_with_no_multipass_still_imports_as_one_section(tmp_path):
    layout = _import_layout(
        tmp_path,
        "parameter[geometry] = open\nbeginning[e_tot] = 10e6\n"
        "Q1: quadrupole, l = 0.1, k1 = 0.3\nD1: drift, l = 0.2\n"
        "LIN: line = (Q1, D1, Q1)\nuse, LIN\n",
        "LIN",
    )
    assert len(layout.sections) == 1
    assert traversal(layout) == [(next(iter(layout.sections)), None)]
