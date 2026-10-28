"""Export failures found by running every machine in laura_lattices through every code."""

import pytest

from laura.models.element import Dipole, MatrixTransform, RFCavity, TwissMatch, Valve, Wiggler
from laura.translator.converters.converter import translate_elements
from laura.translator.utils.functions import tw_cavity_energy_gain


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
