"""Tests for OPAL export: magnet strengths, correctors, field maps and design energy."""

import re
import warnings

import numpy as np
import pytest

from laura.models.element import (
    Dipole,
    HorizontalCorrector,
    Quadrupole,
    RFCavity,
    Solenoid,
)
from laura.models.element_list import SectionLattice
from laura.translator.converters.converter import translate_elements
from laura.translator.converters.magnet import MagnetTranslator
from laura.translator.converters.section import SectionLatticeTranslator
from laura.translator.utils.fields import FieldMap
from laura.translator.utils.fields.field_parameter import FieldParameter
from laura.translator.utils.fields.opal import opal_tw_window
from laura.translator.utils.units import UnitValue

FREQUENCY = 2.856e9
WAVELENGTH = 299792458.0 / FREQUENCY


def translate(element):
    return translate_elements([element])[element.name]


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


def _cavity(amplitude=1e7, **physical):
    return RFCavity(
        name="C",
        machine_area="S",
        physical={"length": 1.0, **physical},
        cavity={"structure_type": "StandingWave", "frequency": FREQUENCY, "phase": 0.0},
        simulation={"field_amplitude": amplitude},
    )


def test_opal_quadrupole_k1_is_a_gradient():
    """OPAL took LAURA's normalised k1 as a gradient: quads ~5x weak, wrong plane for electrons."""
    quad = translate(
        Quadrupole(name="Q", machine_area="S", physical={"length": 0.1},
                   magnetic={"length": 0.1, "k1l": 0.5})
    )
    # 599.584916 MeV is B*rho = 2 T m; the field gradient flips sign for electrons
    written = quad.to_opal(sval=0.0, designenergy=599.584916)
    assert float(re.search(r"k1 = ([^,]+)", written).group(1)) == pytest.approx(-10.0)


@pytest.mark.parametrize("e1", [0.0, 0.13])
def test_opal_rbend_length_is_the_straight_length_of_its_arc(e1):
    """OPAL's rbend `l` is straight; LAURA's arc was 0.57 mm a JFEL VBC dipole longer in OPAL, 7.6 ps over the chicane."""
    bend = translate(
        Dipole(name="B", hardware_class="Magnet", machine_area="S", physical={"length": 0.2},
               magnetic={"length": 0.2, "k0l": 0.13, "entrance_edge_angle": e1, "exit_edge_angle": 0.13 - e1})
    )
    written = bend.to_opal(sval=0.0, designenergy=180.0)
    assert written.split(":")[1].split(",")[0].strip() == "rbend"
    assert float(re.search(r"\bl = ([^,]+)", written).group(1)) == pytest.approx(0.2 * np.sin(0.13) / 0.13)


def test_opal_correctors_are_kickers_and_thin_ones_last_ten_time_steps():
    """OPAL's hkicker/vkicker don't take hkick/vkick, and it rejects an element
    shorter than ten time steps of drift; both aborted the run."""
    def corrector(length):
        return translate(
            HorizontalCorrector(name="X", machine_area="S", physical={"length": length},
                                magnetic={"magnetic_length": length, "horizontal_kick": 1e-3})
        )
    assert corrector(0.1).to_opal(sval=0.0).startswith("X: kicker")
    thin = corrector(0.0)
    thin.opal_time_step = 2e-12
    written = thin.to_opal(sval=1.0)
    step = 10 * 299792458.0 * 2e-12
    assert float(re.search(r"\bl = ([^,]+)", written).group(1)) == pytest.approx(step)
    assert float(re.search(r"ELEMEDGE = ([^;]+)", written).group(1)) == pytest.approx(1.0 - step / 2)
    assert "hkick = 0.001" in written
    assert thin.physical.length == 0.0  # the lattice's own element is untouched


def test_opal_solenoid_map_starts_at_its_field_reference(tmp_path, monkeypatch):
    """OPAL puts a map's origin at ELEMEDGE, ASTRA and GPT at the field reference."""
    monkeypatch.chdir(tmp_path)
    field = FieldMap()
    z = np.linspace(-0.1, 0.1, 201)
    field.length = len(z)
    field.z = FieldParameter(name="z", value=UnitValue(z, "m"))
    field.Bz = FieldParameter(name="Bz", value=UnitValue(np.cos(z * 10), "T"))
    field.field_type = "1DMagnetoStatic"
    field.filename = "sol.hdf5"
    field.read = True
    element = Solenoid(name="SOL", machine_area="S", physical={"length": 0.2},
                       magnetic={"length": 0.2, "ks": 0.06},
                       simulation={"field_reference_position": "middle"})
    element.simulation.field_definition = field
    solenoid = translate(element)
    solenoid.directory = str(tmp_path)
    written = solenoid.to_opal(sval=1.0, designenergy=6.0)
    assert float(re.search(r"ELEMEDGE = ([^;]+)", written).group(1)) == pytest.approx(1.1)


@pytest.mark.parametrize("reference", [None, "middle", "end"])
def test_a_solenoid_without_a_map_gets_a_current_sheet(tmp_path, monkeypatch, reference):
    """OPAL stopped on a solenoid without FMAPFN ("No field map file specified", laura#53)
    and ASTRA's writer raised; both now get the map of a thin current sheet, which
    tracked a hard-edge solenoid to 0.2% of the beam size in ASTRA and OPAL."""
    monkeypatch.chdir(tmp_path)
    element = Solenoid(name="SOL", machine_area="S", physical={"length": 0.2, "middle": [0, 0, 1.0]},
                       magnetic={"length": 0.2, "fields": {"S0L": 0.15}},
                       simulation={"field_reference_position": reference})
    solenoid = translate(element)
    solenoid.directory = str(tmp_path)
    offset = 1.0 - solenoid.get_field_reference_position()[2]
    for code in ("astra", "opal"):
        with pytest.warns(UserWarning, match=f"{code.upper()} needs a field map and 'SOL' has none"):
            field = solenoid._field_map(code)
        z, bz = field.z.value.val, field.Bz.value.val
        assert z[np.argmax(bz)] == pytest.approx(offset, abs=1e-3)  # centred on the middle
        # scaled to the sheet's peak, the field integral is S0L
        assert np.trapezoid(bz, z) * solenoid._map_amplitude(code) == pytest.approx(0.15, rel=1e-4)
    assert 'fmapfn = "SOL_solenoid.opal"' in solenoid.to_opal(sval=0.9, designenergy=100.0)
    assert "FILE_BFieLD(1) = 'SOL_solenoid.astra'" in solenoid.to_astra(n=1)
    assert (tmp_path / "SOL_solenoid.opal").exists() and (tmp_path / "SOL_solenoid.astra").exists()


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


@pytest.mark.parametrize("short, accepted", [(0.0005, True), (0.02, False)])
def test_opal_tw_map_short_of_the_window_by_under_a_step_is_held_not_refused(tmp_path, monkeypatch, short, accepted):
    """JFEL's TW map is 0.5 mm short of the window at each end, under its 2 mm sample step: the exporter refused it."""
    monkeypatch.chdir(tmp_path)
    lo, hi = opal_tw_window(_rf_map(np.linspace(0, 0.3, 3001), np.ones(3001), start_cell_z=0.08), FREQUENCY)
    z = np.arange(lo + short, hi - short, 0.002)
    field = _rf_map(z, np.ones(len(z)), start_cell_z=0.08)
    field.filename = "tw.hdf5"
    if accepted:
        lines = open(field.write_field_file(code="opal")).read().split("\n")
        zs = [float(line.split()[0]) for line in lines[2:] if line.strip()]
        assert zs[0] == 0.0 and zs[-1] == pytest.approx(2 * WAVELENGTH, abs=0.002)
    else:
        with pytest.raises(ValueError, match="TW map spans"):
            field.write_field_file(code="opal")


def test_opal_drops_a_cavity_with_no_field(tmp_path, monkeypatch):
    """OPAL's autophaser rejects a cavity with zero amplitude."""
    monkeypatch.chdir(tmp_path)
    element = _cavity(amplitude=0.0)
    element.simulation.field_definition = _rf_map(np.linspace(0, 0.1, 11), np.ones(11))
    assert translate(element).to_opal(sval=0.0, designenergy=6.0) == ""


class _Header:
    DT = 1e-12

    def write_opal(self):
        return ""


def test_opal_design_energy_after_a_cavity_is_its_gain(tmp_path, monkeypatch):
    """The design energy took a standing-wave cavity's peak field [V/m] as its gain [MeV]."""
    seen = {}

    steps = set()

    def spy(self, sval, designenergy=None):
        seen[self.name] = designenergy
        steps.add(self.opal_time_step)
        return ""

    monkeypatch.setattr(MagnetTranslator, "to_opal", spy)
    z = np.linspace(0, 2 * WAVELENGTH, 2001)
    cavity = _cavity(middle=[0, 0, 1.0])
    cavity.simulation.field_definition = _rf_map(z, np.cos(2 * np.pi * z / WAVELENGTH))
    elements = [
        Quadrupole(name="Q1", machine_area="S", physical={"length": 0.1, "middle": [0, 0, 0.2]}),
        cavity,
        Quadrupole(name="Q2", machine_area="S", physical={"length": 0.1, "middle": [0, 0, 2.0]}),
    ]
    section = SectionLatticeTranslator.from_section(
        SectionLattice(name="S", order=[e.name for e in elements], elements=elements)
    )
    section.directory = str(tmp_path)
    section.opal_headers = {
        k: _Header() for k in ("option", "distribution", "fieldsolver", "beam", "track", "run")
    }
    section.opal_headers["track"].DT = [1e-13, 2e-12]
    monkeypatch.chdir(tmp_path)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        section.to_opal(energy=5.0)
    assert seen["Q1"] == pytest.approx(5.0)
    # |int cos(kz) exp(ikz)| over two wavelengths is one wavelength, at 10 MV/m
    assert seen["Q2"] == pytest.approx(5.0 + 10 * WAVELENGTH, rel=1e-4)
    assert steps == {2e-12}  # the longest stage step


def test_opal_design_energy_is_kinetic():
    """The section's energy is the momentum [MeV/c]; OPAL's DESIGNENERGY is kinetic, so a 5 MeV/c
    bunch was bent 10% too far, 4 ps more path through a 0.1 rad chicane."""
    bend = translate(
        Dipole(name="B", hardware_class="Magnet", machine_area="S", physical={"length": 0.2},
               magnetic={"length": 0.2, "k0l": 0.1, "entrance_edge_angle": 0.0, "exit_edge_angle": 0.1})
    )
    written = bend.to_opal(sval=0.0, designenergy=5.0)
    assert float(re.search(r"DESIGNENERGY = ([^,]+)", written).group(1)) == pytest.approx(np.hypot(5.0, 0.51099895) - 0.51099895)
