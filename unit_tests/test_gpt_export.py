"""Tests for GPT export: field maps, design energies and screen placement."""

import numpy as np
import pytest

from laura.models.element import Dipole, Marker, Quadrupole, RFCavity, Screen
from laura.models.element_list import SectionLattice
from laura.translator.converters.converter import translate_elements
from laura.translator.converters.magnet import MagnetTranslator
from laura.translator.converters.section import SectionLatticeTranslator
from laura.translator.utils.fields import FieldMap
from laura.translator.utils.fields.field_parameter import FieldParameter
from laura.translator.utils.fields.gdf import gpt_tw_mockup
from laura.translator.utils.functions import cavity_energy_gain, transit_time_integral
from laura.translator.utils.units import UnitValue

FREQUENCY = 2.856e9
WAVELENGTH = 299792458.0 / FREQUENCY


def _rf_map(z, ez, start_cell_z=None):
    field = FieldMap()
    field.length = len(z)
    field.z = FieldParameter(name="z", value=UnitValue(z, "m"))
    field.Ez = FieldParameter(name="Ez", value=UnitValue(ez, "V/m"))
    field.field_type = "1DElectroDynamic"
    field.frequency = FREQUENCY
    field.filename = "rf.hdf5"
    field.read = True
    if start_cell_z is not None:
        field.start_cell_z, field.end_cell_z = start_cell_z, start_cell_z + WAVELENGTH
        field.mode_numerator, field.mode_denominator = 1, 3
        field.cavity_type = "TravellingWave"
    return field


def _cavity_element(structure_type, n_cells=30, **physical):
    return RFCavity(
        name="C",
        machine_area="S",
        physical={"length": 1.0, **physical},
        cavity={
            "structure_type": structure_type,
            "frequency": FREQUENCY,
            "n_cells": n_cells,
            "phase": 0.0,
            "mode_numerator": 1,
            "mode_denominator": 3,
        },
        simulation={"field_amplitude": 1e7},
    )


def _cavity(field, structure_type, n_cells=30):
    cavity = translate_elements([_cavity_element(structure_type, n_cells)])["C"]
    cavity.simulation.field_definition = field
    return cavity


def test_translation_keeps_an_in_memory_field_map():
    """Translation re-validated the element's dump, and a FieldMap doesn't survive
    that: its None fields fail validation, and its file is read again."""
    element = _cavity_element("StandingWave")
    field = _rf_map(np.linspace(0, 0.1, 11), np.ones(11))
    element.simulation.field_definition = field
    translated = translate_elements([element])["C"].simulation.field_definition
    assert translated is not field
    assert translated.Ez.value.val == pytest.approx(np.ones(11))


def test_sw_energy_gain_is_the_transit_time_integral_of_the_map():
    z = np.linspace(0, 2 * WAVELENGTH, 2001)
    cavity = _cavity(_rf_map(z, np.cos(2 * np.pi * z / WAVELENGTH)), "StandingWave")
    # |int cos(kz) exp(ikz)| over two wavelengths is one wavelength
    assert cavity_energy_gain(cavity) == pytest.approx(10 * WAVELENGTH, rel=1e-4)
    assert cavity_energy_gain(cavity, phase=60) == pytest.approx(5 * WAVELENGTH, rel=1e-4)


def test_tw_energy_gain_is_amplitude_times_length_for_an_ideal_map():
    z = np.linspace(0, 0.3, 3001)
    field = _rf_map(z, np.cos(2 * np.pi * z / WAVELENGTH), start_cell_z=0.08)
    # 30 cells at 2pi/3 are 10 periods
    assert cavity_energy_gain(_cavity(field, "TravellingWave")) == pytest.approx(
        10 * 10 * WAVELENGTH, rel=1e-3
    )


def test_gpt_tw_field_factor_gives_the_maps_energy_gain():
    """The hard-coded 1.007 * 9/(2 pi) was tuned on CLARA's maps; on LCLS's it
    gained ~5% too little."""
    z = np.linspace(0, 0.3, 3001)
    field = _rf_map(z, np.cos(2 * np.pi * z / WAVELENGTH), start_cell_z=z[800])
    field.n_cells = 30
    cavity = _cavity(field, "TravellingWave")
    gain = cavity._gpt_tw_ffac() * transit_time_integral(*gpt_tw_mockup(field), FREQUENCY)
    assert gain == pytest.approx(cavity_energy_gain(cavity) * 1e6, rel=1e-9)


def test_gpt_tw_maps_of_different_cell_counts_get_their_own_file(tmp_path, monkeypatch):
    """LCLS's L0A/L0B (84 cells) and a 12-cell structure share one map, and the
    12-cell mock-up overwrote theirs, so GPT's L0 gained 7 times too little."""
    easygdf = pytest.importorskip("easygdf")
    monkeypatch.chdir(tmp_path)
    lengths = {}
    z = np.linspace(0, 0.3, 3001)
    for n_cells in (84, 12):
        field = _rf_map(z, np.ones(3001), start_cell_z=z[800])  # must lie on the grid
        field.n_cells = n_cells
        path = field.write_field_file(code="gpt")
        written = next(b["value"] for b in easygdf.load(path)["blocks"] if b["name"] == "z")
        lengths[path] = written[-1] - written[0]
    assert len(lengths) == 2
    assert max(lengths.values()) - min(lengths.values()) == pytest.approx(
        72 / 3 * WAVELENGTH, rel=1e-3
    )


def _section(elements, tmp_path):
    section = SectionLatticeTranslator.from_section(
        SectionLattice(name="S", order=[e.name for e in elements], elements=elements)
    )
    section.directory = str(tmp_path)
    return section


def test_gpt_screen_after_a_dipole_is_placed_in_its_ccs(tmp_path):
    """Screens past a bend were written at survey z in the bend's ccs, so GPT saw
    those after the LCLS laser heater 10.6 m downstream, and those inside it never."""
    elements = [
        Marker(name="M0", machine_area="S", physical={"length": 0.0, "middle": [0, 0, 0]}),
        Dipole(
            name="D",
            machine_area="S",
            physical={"length": 0.2, "middle": [0, 0, 10.1]},
            magnetic={"angle": 0.2, "length": 0.2},
        ),
        # 5 m along the exit direction
        Screen(
            name="SCR",
            machine_area="S",
            physical={
                "length": 0.0,
                "middle": [1.00828424, 0, 15.0991688],
                "global_rotation": {"theta": 0.2},
            },
        ),
    ]
    section = _section(elements, tmp_path)
    written = section.to_gpt(startz=0, endz=15.1, Brho=1.0)
    z = section.gpt_screen_positions["SCR"]
    assert f'screen("ccs_1", "I", {z}, "ccs_1")' in written
    assert z == pytest.approx(5.1, abs=0.01)


def test_gpt_magnets_after_a_cavity_see_the_raised_brho(tmp_path, monkeypatch):
    """Every magnet was scaled to the section's entrance Brho, so at the cathode
    (Brho ~ 1e-6 T m) GPT's linac quads came out at ~1e-5 T/m."""
    seen = {}

    def spy(self, Brho=0.0, *args, **kwargs):
        seen[self.name] = Brho
        return ""

    monkeypatch.setattr(MagnetTranslator, "to_gpt", spy)
    z = np.linspace(0, 2 * WAVELENGTH, 2001)
    cavity = _cavity_element("StandingWave", middle=[0, 0, 1.0])
    cavity.simulation.field_definition = _rf_map(z, np.cos(2 * np.pi * z / WAVELENGTH))
    elements = [
        Quadrupole(name="Q1", machine_area="S", physical={"length": 0.1, "middle": [0, 0, 0.2]}),
        cavity,
        Quadrupole(name="Q2", machine_area="S", physical={"length": 0.1, "middle": [0, 0, 2.0]}),
    ]
    _section(elements, tmp_path).to_gpt(startz=0, endz=2.1, Brho=0.1)
    mc2 = 0.51099895e6
    kinetic = np.hypot(0.1 * 299792458.0, mc2) - mc2 + 10 * WAVELENGTH * 1e6
    assert seen["Q1"] == pytest.approx(0.1)
    assert seen["Q2"] == pytest.approx(
        np.sqrt(kinetic * (kinetic + 2 * mc2)) / 299792458.0, rel=1e-6
    )
