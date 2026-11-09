"""Export failures found by running every machine in laura_lattices through every code."""

import re

import numpy as np
import pytest

from laura.models.element import (
    Dipole,
    MatrixTransform,
    Quadrupole,
    RFCavity,
    TwissMatch,
    Valve,
    Wiggler,
)
from laura.translator.converters.converter import translate_elements
from laura.translator.utils.fields import FieldMap
from laura.translator.utils.fields.field_parameter import FieldParameter
from laura.translator.utils.fields.opal import opal_tw_window
from laura.translator.utils.functions import cavity_energy_gain, tw_cavity_energy_gain
from laura.translator.utils.units import UnitValue


def translate(element):
    return translate_elements([element])[element.name]


def test_tw_energy_gain_reads_a_real_cavity():
    """``mode_numerator`` is also on the field and wake definitions, so an unqualified
    lookup is ambiguous.
    """
    cavity = translate(
        RFCavity(
            name="C", machine_area="S", physical={"length": 1.0},
            cavity={"structure_type": "TravellingWave", "n_cells": 30.0, "cell_length": 0.0333,
                    "mode_numerator": 2, "mode_denominator": 3, "phase": 0.0},
            simulation={"field_amplitude": 20.0},
        )
    )
    assert tw_cavity_energy_gain(cavity) > 0


def test_astra_cavity_without_a_field_map_says_so():
    cavity = translate(
        RFCavity(name="C", machine_area="S", physical={"length": 1.0}, simulation={"field_amplitude": 1e7})
    )
    with pytest.raises(ValueError, match="field map"):
        cavity.to_astra(n=1)


@pytest.mark.parametrize("cls", [Wiggler, Valve])
def test_opal_writes_unmapped_types_as_drift(cls):
    element = translate(cls(name="W", machine_area="S", physical={"length": 1.0}))
    assert element.to_opal(sval=0.0) == ""


def test_cheetah_dipole_without_fringe_integrals():
    pytest.importorskip("cheetah")
    dipole = translate(Dipole(name="D", machine_area="S", physical={"length": 0.2}, magnetic={"angle": 0.1, "length": 0.2}))
    obj = dipole.to_cheetah()
    assert float(obj.fringe_integral_exit) == float(obj.fringe_integral)


@pytest.mark.parametrize(
    "element",
    [
        MatrixTransform(name="M", machine_area="S", simulation={"r_matrix": {"r21": 0.5}}),
        TwissMatch(name="T", machine_area="S"),
    ],
    ids=["MatrixTransform", "TwissMatch"],
)
def test_xsuite_taylor_maps_build(element):
    """xtrack rejects ``name`` as a constructor keyword."""
    pytest.importorskip("xtrack")
    _, component, properties = translate(element).to_xsuite(beam_length=1)
    assert component(**properties) is not None


FREQUENCY = 2.856e9
WAVELENGTH = 299792458.0 / FREQUENCY


def _rf_map(z, ez, start_cell_z=None):
    field = FieldMap()
    field.length = len(z)
    field.z = FieldParameter(name="z", value=UnitValue(z, "m"))
    field.Ez = FieldParameter(name="Ez", value=UnitValue(ez, "V/m"))
    field.field_type = "1DElectroDynamic"
    field.frequency = FREQUENCY
    field.read = True
    if start_cell_z is not None:
        field.start_cell_z, field.end_cell_z = start_cell_z, start_cell_z + WAVELENGTH
        field.mode_numerator, field.mode_denominator = 1, 3
    return field


def _cavity(field, structure_type, n_cells=30):
    cavity = translate(
        RFCavity(
            name="C", machine_area="S", physical={"length": 1.0},
            cavity={"structure_type": structure_type, "frequency": FREQUENCY, "n_cells": n_cells,
                    "phase": 0.0, "mode_numerator": 1, "mode_denominator": 3},
            simulation={"field_amplitude": 1e7},
        )
    )
    cavity.simulation.field_definition = field
    return cavity


def test_sw_energy_gain_is_the_transit_time_integral_of_the_map():
    """The section's OPAL design energy once took a gun's peak field as its gain."""
    z = np.linspace(0, 2 * WAVELENGTH, 2001)
    cavity = _cavity(_rf_map(z, np.cos(2 * np.pi * z / WAVELENGTH)), "StandingWave")
    # |int cos(kz) exp(ikz)| over two wavelengths is one wavelength
    assert cavity_energy_gain(cavity) == pytest.approx(10 * WAVELENGTH, rel=1e-4)


def test_tw_energy_gain_is_amplitude_times_length_for_an_ideal_map():
    z = np.linspace(0, 0.3, 3001)
    field = _rf_map(z, np.cos(2 * np.pi * z / WAVELENGTH), start_cell_z=0.08)
    # 30 cells at 2pi/3 are 10 periods
    assert cavity_energy_gain(_cavity(field, "TravellingWave")) == pytest.approx(
        10 * 10 * WAVELENGTH, rel=1e-3
    )


def test_opal_tw_map_is_the_two_periods_opal_reads(tmp_path, monkeypatch):
    """OPAL takes the period as half the map, so ASTRA's longer couplers gave the wrong cells."""
    monkeypatch.chdir(tmp_path)
    field = _rf_map(np.linspace(0, 0.3, 3001), np.ones(3001), start_cell_z=0.08)
    field.filename = "tw.hdf5"
    lines = open(field.write_field_file(code="opal")).read().split("\n")
    z = [float(line.split()[0]) for line in lines[2:] if line.strip()]
    assert z[0] == 0.0  # OPAL refuses anything else
    assert z[-1] == pytest.approx(2 * WAVELENGTH)
    assert opal_tw_window(field, FREQUENCY)[0] == pytest.approx(0.08 - WAVELENGTH / 2)


def test_gpt_tw_maps_of_different_cell_counts_get_their_own_file(tmp_path, monkeypatch):
    """LCLS's L0A/L0B (84 cells) and a 12-cell structure share one map, and the
    12-cell mock-up overwrote theirs, so GPT's L0 gained 7 times too little."""
    easygdf = pytest.importorskip("easygdf")
    monkeypatch.chdir(tmp_path)
    lengths = {}
    z = np.linspace(0, 0.3, 3001)
    for n_cells in (84, 12):
        field = _rf_map(z, np.ones(3001), start_cell_z=z[800])  # the writer needs it on the grid
        field.filename, field.cavity_type, field.n_cells = "tw.hdf5", "TravellingWave", n_cells
        path = field.write_field_file(code="gpt")
        written = next(b["value"] for b in easygdf.load(path)["blocks"] if b["name"] == "z")
        lengths[path] = written[-1] - written[0]
    assert len(lengths) == 2
    assert max(lengths.values()) - min(lengths.values()) == pytest.approx(72 / 3 * WAVELENGTH, rel=1e-3)


def test_gpt_screen_after_a_dipole_is_placed_in_its_ccs(tmp_path):
    """Screens past a bend were written at survey z in the bend's ccs, so GPT saw
    those after the LCLS laser heater 10.6 m downstream, and those inside it never."""
    from laura.models.element import Marker, Screen
    from laura.models.element_list import SectionLattice
    from laura.translator.converters.section import SectionLatticeTranslator

    elements = [
        Marker(name="M0", machine_area="S", physical={"length": 0.0, "middle": [0, 0, 0]}),
        Dipole(name="D", machine_area="S", physical={"length": 0.2, "middle": [0, 0, 10.1]},
               magnetic={"angle": 0.2, "length": 0.2}),
        # 5 m along the exit direction
        Screen(name="SCR", machine_area="S",
               physical={"length": 0.0, "middle": [1.00828424, 0, 15.0991688],
                         "global_rotation": {"theta": 0.2}}),
    ]
    section = SectionLatticeTranslator.from_section(
        SectionLattice(name="S", order=[e.name for e in elements], elements=elements)
    )
    section.directory = str(tmp_path)
    written = section.to_gpt(startz=0, endz=15.1, Brho=1.0)
    z = section.gpt_screen_positions["SCR"]
    assert f'screen("ccs_1", "I", {z}, "ccs_1")' in written
    assert z == pytest.approx(5.1, abs=0.01)


def test_hdf5_wake_keeps_its_reference_length_not_its_sample_count(tmp_path, monkeypatch):
    """The sample count went into ``length``, which the reader takes as metres, so
    ASTRA placed one wake 2 km downstream."""
    monkeypatch.chdir(tmp_path)
    wake = FieldMap(field_type="LongitudinalWake", length=101, reference_length=0.035, read=True)
    wake.filename = "w.hdf5"
    wake.z = FieldParameter(name="z", value=UnitValue(np.linspace(0, 0.01, 101), "m"))
    wake.Wz = FieldParameter(name="Wz", value=UnitValue(np.ones(101), "V/C"))
    back = FieldMap()
    back.read_field_file(wake.write_field_file(code="hdf5"))
    assert back.reference_length == pytest.approx(0.035)
    assert back.length == 101


def test_astra_monopole_wake_is_one_sub_table(tmp_path, monkeypatch):
    """ASTRA 3.2 read a leading "1 0" as Nq Np, so took the sample count as a
    resistive term and lost 350 times the LCLS wake per kick."""
    monkeypatch.chdir(tmp_path)
    wake = FieldMap(field_type="LongitudinalWake", length=101, read=True)
    wake.filename = "w.hdf5"
    wake.z = FieldParameter(name="z", value=UnitValue(np.linspace(0, 0.01, 101), "m"))
    wake.Wz = FieldParameter(name="Wz", value=UnitValue(np.linspace(2, 1, 101), "V/C"))
    path = wake.write_field_file(code="astra")
    lines = open(path).read().split()
    assert lines[:6] == ["101", "0", "0", "0", "0", "0"]
    old = tmp_path / "old.astra"
    old.write_text("1 0\n" + open(path).read())
    for name in (path, str(old)):
        back = FieldMap()
        back.read_field_file(name, field_type="LongitudinalWake")
        assert back.Wz.value.val == pytest.approx(np.linspace(2, 1, 101))


def test_opal_quadrupole_k1_is_a_gradient():
    quad = translate(
        Quadrupole(name="Q", machine_area="S", physical={"length": 0.1},
                   magnetic={"length": 0.1, "k1l": 0.5})
    )
    # 599.584916 MeV is B*rho = 2 T m; the field gradient flips sign for electrons
    written = quad.to_opal(sval=0.0, designenergy=599.584916)
    assert float(re.search(r"k1 = ([^,]+)", written).group(1)) == pytest.approx(-10.0)
