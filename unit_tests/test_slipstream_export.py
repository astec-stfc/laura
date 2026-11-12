"""``to_slipstream`` gives slipstream one plain record per element, in section order."""

import numpy as np
import pytest

from laura.models.element import Aperture, Dipole, Marker, RFCavity
from laura.models.element_list import ElementList, SectionLattice
from laura.translator.converters.codes.slipstream import SlipstreamElement
from laura.translator.converters.converter import translate_elements
from laura.translator.converters.section import SectionLatticeTranslator
from unit_tests.helpers import quad, quiet


def travelling_wave(length=1.2, cells=3, cell_length=0.3, amplitude=2e7, phase=10.0):
    return RFCavity(
        name="C1",
        machine_area="S",
        physical={"length": length},
        cavity={
            "phase": phase,
            "frequency": 3e9,
            "n_cells": cells,
            "cell_length": cell_length,
            "structure_Type": "TravellingWave",
            "mode_numerator": 2,
            "mode_denominator": 3,
        },
        simulation={"field_amplitude": amplitude},
    )


def records(*elements):
    registry = {e.name: e for e in elements}
    lattice = SectionLattice(
        name="line", order=list(registry), elements=ElementList(elements=registry)
    )
    lattice.resolve_positions(lattice.elements.elements)
    with quiet():
        return SectionLatticeTranslator.from_section(lattice).to_slipstream()


def test_section_gives_a_record_for_every_element_and_drift_between_them():
    out = records(
        quad("Q1", length=0.1, k1l=0.5, s=0.5),
        Marker(name="M1", machine_area="S", physical={"s": 1.0}),
        quad("Q2", length=0.1, k1l=-0.5, s=1.5),
    )
    assert all(isinstance(r, SlipstreamElement) for r in out)
    assert [r.name for r in out] == ["Q1", "line_drift_1", "M1", "line_drift_2", "Q2"]
    # from the first quadrupole's entrance (0.45) to the last one's exit (1.55)
    assert sum(r.length for r in out) == pytest.approx(1.1)
    assert [r.k1 for r in out if r.name.startswith("Q")] == pytest.approx([5.0, -5.0])


def test_dipole_carries_angle_and_edge_angles():
    bend = Dipole(
        name="B1", machine_area="S", physical={"length": 1.0},
        magnetic={"length": 1.0, "k0l": 0.2, "entrance_edge_angle": 0.05, "exit_edge_angle": -0.05},
    )
    (record,) = [r for r in records(bend) if r.name == "B1"]
    assert (record.angle, record.e1, record.e2) == pytest.approx((0.2, 0.05, -0.05))


def test_travelling_wave_voltage_is_the_one_elegant_writes():
    cavity = travelling_wave()
    (record,) = [r for r in records(cavity) if r.name == "C1"]
    with quiet():
        elegant = translate_elements([cavity])["C1"].to_elegant()
    volt = float(elegant.split("volt = ")[1].split(",")[0])
    assert record.voltage_v == pytest.approx(volt, rel=1e-6)
    expected = abs((3 + 3.8) * 0.3 / np.sqrt(2)) * 2e7
    assert record.voltage_v == pytest.approx(expected, rel=1e-6)
    # elegant's phase convention: 90 degrees minus LAURA's off-crest phase
    assert record.phase_deg == pytest.approx(80.0)
    assert record.frequency_hz == 3e9
    assert record.body_focus_model == "TW1"


def test_aperture_keeps_its_shape_and_half_sizes():
    aperture = Aperture(
        name="A1", machine_area="S", physical={"length": 0.0},
        aperture={"shape": "rectangular", "horizontal_size": 0.01, "vertical_size": 0.02},
    )
    (record,) = [r for r in records(aperture) if r.name == "A1"]
    assert record.aperture_shape == "rectangular"
    assert (record.aperture_horizontal_m, record.aperture_vertical_m) == (0.01, 0.02)


def test_other_elements_are_plain_drifts():
    (record,) = [r for r in records(Marker(name="M1", machine_area="S", physical={"s": 0.0}))
                 if r.name == "M1"]
    assert record.length == 0.0
    assert record.k1 == record.angle == record.voltage_v == 0.0
