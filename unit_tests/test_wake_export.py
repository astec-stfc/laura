"""Tests for structure-wake export to ASTRA, Elegant and GPT, and the warning from codes without it."""

import re
import warnings

import numpy as np
import pytest

from laura.models.element import Quadrupole, RFCavity, Wakefield
from laura.models.element_list import SectionLattice
from laura.translator.converters.cavity import RFCavityTranslator
from laura.translator.converters.converter import translate_elements
from laura.translator.converters.section import SectionLatticeTranslator
from laura.translator.converters.wake import WakefieldTranslator
from laura.translator.utils.fields import FieldMap
from laura.translator.utils.fields.field_parameter import FieldParameter
from laura.translator.utils.units import UnitValue

CELLS = {"n_cells": 3, "cell_length": 0.1}


def _wake_file(tmp_path):
    wake = FieldMap()
    z = np.linspace(0, 1e-3, 11)
    wake.length = CELLS["cell_length"]  # a per-cell wake: ASTRA places one per cell
    wake.z = FieldParameter(name="z", value=UnitValue(z, "m"))
    wake.Wz = FieldParameter(name="Wz", value=UnitValue(1e12 * np.exp(-z / 1e-4), "V/C"))
    wake.field_type = "LongitudinalWake"
    wake.filename = str(tmp_path / "wk.hdf5")
    wake.read = True
    wake.write_field_file(code="hdf5")
    return wake.filename


def _cavity(name="C", z=2.0, **simulation):
    return RFCavity(
        name=name,
        machine_area="S",
        physical={"length": 0.3, "middle": [0, 0, z]},
        cavity={"structure_type": "StandingWave", "frequency": 2.856e9, "phase": 0.0, **CELLS},
        simulation={"field_amplitude": 1e7, **simulation},
    )


def _wakefield(path, z):
    return Wakefield(name="W", machine_area="S", physical={"length": 0.3, "middle": [0, 0, z]},
                     cavity=CELLS, simulation={"wakefield_definition": path})


def _section(elements, tmp_path):
    section = SectionLatticeTranslator.from_section(
        SectionLattice(name="S", order=[e.name for e in elements], elements=elements)
    )
    section.directory = str(tmp_path)
    return section


class _Header:
    def write_astra(self):
        return ""

    def write_gpt(self):
        return ""


def test_elegant_rfcw_writes_its_wake_without_column_names(tmp_path, monkeypatch):
    """With no column names set, rfcw was written with no wakefile at all; a wake read
    from file then got Wx/Wy columns it doesn't have."""
    monkeypatch.chdir(tmp_path)
    cavity = translate_elements([_cavity()])["C"]
    cavity.directory = str(tmp_path)
    cavity.simulation.wakefield_definition = _wake_file(tmp_path)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        written = cavity.to_elegant()
    assert written.startswith("C: rfcw")
    assert 'zwakefile = "wk.sdds"' in written
    assert 'tcolumn = "t"' in written and 'wzcolumn = "Wz"' in written
    assert "wxcolumn" not in written


def test_elegant_writes_a_wakefield_as_a_zero_voltage_rfcw(tmp_path, monkeypatch):
    """ELEGANT's wake element has no length, so the lattice came out short, and it was
    written without its wake file."""
    monkeypatch.chdir(tmp_path)
    wake = translate_elements([_wakefield(_wake_file(tmp_path), 1.0)], directory=str(tmp_path))["W"]
    assert isinstance(wake, WakefieldTranslator)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        written = wake.to_elegant()
    assert written.startswith("W: rfcw, l = 0.3, volt = 0,")
    # rfcw scales the per-cell wake by l / cell_length, so once per cell
    assert float(re.search(r"cell_length = ([^,]+)", written).group(1)) == pytest.approx(0.1)
    assert 'zwakefile = "wk.sdds", tcolumn = "t", wzcolumn = "Wz"' in written


def test_astra_numbers_and_places_every_wake_once(tmp_path, monkeypatch):
    """A float counter crashed the second wake element, each was placed by its index in
    the deck rather than by its own cells, and a Wakefield mustn't be written twice."""
    monkeypatch.setattr(RFCavityTranslator, "to_astra", lambda self, n=0, **kwargs: "")
    path = _wake_file(tmp_path)
    section = _section(
        [_cavity("C1", 1.0, wakefield_definition=path), _wakefield(path, 1.5),
         _cavity("C2", 2.0, wakefield_definition=path)],
        tmp_path,
    )
    section.astra_headers = {"h": _Header()}
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        written = section.to_astra()
    wakes = re.findall(r"Wk_z\((\d+)\) = ([^,\s]+)", written)
    assert [int(i) for i, _ in wakes] == list(range(1, 10))
    assert [float(z) for _, z in wakes] == pytest.approx([0.9, 1.0, 1.1, 1.4, 1.5, 1.6, 1.9, 2.0, 2.1])


def test_gpt_wakes_sit_on_their_cells_per_metre_and_decelerate(tmp_path):
    """GPT's wakes were half a cell upstream, cell_length times too weak and accelerating,
    and a cavity's were placed in absolute z rather than in the section's frame."""
    path = _wake_file(tmp_path)
    section = _section(
        [_cavity("C", 1.0, field_amplitude=0.0, wakefield_definition=path), _wakefield(path, 2.0),
         Quadrupole(name="Q", machine_area="S", physical={"length": 0.1, "middle": [0, 0, 3.0]})],
        tmp_path,
    )
    section.gpt_headers = {"h": _Header()}
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        written = section.to_gpt(startz=0.0, endz=3.5, Brho=0.02)
    wakes = re.findall(r'wakefield\("wcs", "z", ([^,]+), 0.1, .*"FieldFactorWz", ([^)]+)\);', written)
    # the section's frame starts at C, at 0.85 m
    assert [float(z) for z, _ in wakes] == pytest.approx([0.05, 0.15, 0.25, 1.05, 1.15, 1.25])
    assert [float(f) for _, f in wakes] == pytest.approx([-10.0] * 6)


@pytest.mark.parametrize("off", [None, "section", "element"])
def test_madx_warns_when_it_drops_structure_wakes(tmp_path, off):
    """MAD-X, Cheetah, Xsuite and OPAL tracked without the wakes and said nothing."""
    cavity = _cavity(wakefield_definition=_wake_file(tmp_path), wakefield_enable=off != "element")
    elements = [
        Quadrupole(name="Q", machine_area="S", physical={"length": 0.1, "middle": [0, 0, 0.5]}),
        cavity,
    ]
    section = _section(elements, tmp_path)
    section.wakefield_enable = off != "section"
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        section.to_madx()
    dropped = [str(w.message) for w in caught if "without structure wakefields" in str(w.message)]
    assert dropped == ([] if off else ["MAD-X is written without structure wakefields; dropped on C"])
