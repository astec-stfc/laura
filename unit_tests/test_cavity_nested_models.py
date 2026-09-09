"""Each cavity element carries the cavity model it declares.

``RFDeflectingCavity`` and ``CrabCavity`` subclass ``RFCavity``, so
``RFCavity.model_post_init`` runs first through ``super()``. It used to fill
``cavity`` with a hardcoded ``RFCavityElement``, and the subclass's own
``_ensure_nested_default`` then found the slot occupied and did nothing. That
broke both subclasses, differently:

* ``RFDeflectingCavity`` silently carried an ``RFCavityElement`` -- including a
  ``structure_type`` and ``attenuation_constant`` that mean nothing for a
  deflector -- because it did not redeclare the field, so ``RFCavity``'s
  annotation won on the MRO.
* ``CrabCavity`` *did* redeclare it, so the parent's assignment failed
  validation outright and **the class could not be constructed at all**.

The parent now takes the model from a ``_cavity_model`` class attribute that
each subclass overrides, and every one of them declares the concrete model
rather than the generated ``_...Base``, so an authored mapping and an omitted
one land in the same class.
"""

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
    """The two disagreed: a dict landed in the generated base class instead."""
    assert type(build(cls, cavity={"n_cells": 9}).cavity) is model


def test_a_crab_cavity_can_be_constructed():
    """It raised ValidationError on every construction before."""
    assert build(CrabCavity).cavity is not None


def test_a_deflector_has_no_accelerating_structure_fields():
    """The point of giving it its own model: these mean nothing for a kicker."""
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
    """`RFCavityTranslator` serves all three, and branches on this. A deflector
    has no such field, and reported ``StandingWave`` before it was given the
    right cavity model -- so backends see no change."""
    from laura.translator.converters.converter import translate_elements

    for cls in (RFCavity, RFDeflectingCavity, CrabCavity):
        element = build(
            cls,
            cavity={"phase": 10.0, "frequency": 3e9},
            simulation={"field_amplitude": 1e7},
        )
        translator = translate_elements([element])["C"]
        assert translator.structure_type == "StandingWave"
