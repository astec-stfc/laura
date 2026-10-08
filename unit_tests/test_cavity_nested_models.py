"""Each cavity subclass carries its own ``_cavity_model``, not ``RFCavity``'s."""

import pytest

from laura.models.element import CrabCavity, RFCavity, RFDeflectingCavity, Wakefield
from laura.models.RF import (
    RFCavityElement,
    RFDeflectingCavityElement,
    WakefieldElement,
)

EXPECTED = [
    (RFCavity, RFCavityElement),
    (RFDeflectingCavity, RFDeflectingCavityElement),
    (CrabCavity, RFDeflectingCavityElement),
    (Wakefield, WakefieldElement),
]


def build(cls, **kwargs):
    return cls(name="C", machine_area="S", physical={"length": 0.3}, **kwargs)


@pytest.mark.parametrize("cls,model", EXPECTED, ids=lambda v: getattr(v, "__name__", v))
def test_an_omitted_cavity_defaults_to_the_declared_model(cls, model):
    assert type(build(cls).cavity) is model


@pytest.mark.parametrize("cls,model", EXPECTED, ids=lambda v: getattr(v, "__name__", v))
def test_an_authored_cavity_validates_into_the_same_model(cls, model):
    assert type(build(cls, cavity={"n_cells": 9}).cavity) is model


def test_a_deflector_has_no_accelerating_structure_fields():
    deflector = build(RFDeflectingCavity).cavity
    assert not hasattr(deflector, "structure_type")
    assert not hasattr(deflector, "attenuation_constant")


def test_an_accelerating_cavity_still_has_them():
    assert build(RFCavity).cavity.structure_type == "StandingWave"


def test_authored_values_survive():
    deflector = build(RFDeflectingCavity, cavity={"phase": 45.0, "frequency": 3e9})
    assert deflector.cavity.phase == pytest.approx(45.0)
    assert deflector.cavity.frequency == pytest.approx(3e9)


def test_export_still_reports_a_structure_type_for_a_deflector():
    """``RFCavityTranslator`` branches on this for all three classes."""
    from laura.translator.converters.converter import translate_elements

    for cls in (RFCavity, RFDeflectingCavity, CrabCavity):
        element = build(
            cls,
            cavity={"phase": 10.0, "frequency": 3e9},
            simulation={"field_amplitude": 1e7},
        )
        translator = translate_elements([element])["C"]
        assert translator.structure_type == "StandingWave"
