# python
import pytest
from laura.models.element import (
    baseElement,
    PhysicalBaseElement,
    Element,
    Sextupole,
    Octupole,
    Solenoid,
    Wiggler,
    NonLinearLens,
    Horizontal_Corrector,
    Vertical_Corrector,
    Combined_Corrector,
)
from laura.models._generated import (
    _SextupoleBase,
    _OctupoleBase,
    _SolenoidBase,
    _WigglerBase,
    _NonLinearLensBase,
    _HorizontalCorrectorBase,
    _VerticalCorrectorBase,
    _CombinedCorrectorBase,
)
from laura.models.physical import PhysicalElement
from laura.models.electrical import ElectricalElement
from laura.models.manufacturer import ManufacturerElement
from laura.models.simulation import SimulationElement


@pytest.fixture
def base_element() -> baseElement:
    return baseElement(
        name="Base1",
        hardware_class="Generic",
        hardware_type="HT",
        machine_area="MA",
        subelement=True,
    )


@pytest.fixture
def physical_base_element() -> PhysicalBaseElement:
    return PhysicalBaseElement(
        name="Phys1",
        hardware_class="Generic",
        hardware_type="HT",
        machine_area="MA",
    )


def test_base_element_initialization(base_element):
    assert base_element.name == "Base1"
    assert base_element.hardware_class == "Generic"
    assert base_element.hardware_type == "HT"
    assert base_element.machine_area == "MA"
    assert base_element.is_subelement() is True


def test_base_element_flatten(base_element):
    flat_data = base_element.flat()
    assert "name" in flat_data
    assert flat_data["name"] == "Base1"


def test_physical_base_element_initialization(physical_base_element):
    assert isinstance(physical_base_element.physical, PhysicalElement)
    assert physical_base_element.physical is not None


def test_element_initialization():
    el = Element(
        name="Elem1",
        hardware_class="Generic",
        hardware_type="HT",
        machine_area="MA",
    )
    assert isinstance(el.electrical, ElectricalElement)
    assert isinstance(el.manufacturer, ManufacturerElement)
    assert isinstance(el.simulation, SimulationElement)


@pytest.mark.parametrize(
    "cls,base",
    [
        (Sextupole, _SextupoleBase),
        (Octupole, _OctupoleBase),
        (Solenoid, _SolenoidBase),
        (Wiggler, _WigglerBase),
        (NonLinearLens, _NonLinearLensBase),
        (Horizontal_Corrector, _HorizontalCorrectorBase),
        (Vertical_Corrector, _VerticalCorrectorBase),
        (Combined_Corrector, _CombinedCorrectorBase),
    ],
)
def test_magnet_elements_inherit_generated_base(cls, base):
    """Dipole/Quadrupole already did this (Dipole(Magnet, _DipoleBase)); these
    were the ones added for the new schema classes that hadn't been wired up."""
    assert issubclass(cls, base)


def test_magnet_elements_still_construct_and_round_trip():
    for cls in [Sextupole, Octupole, Solenoid, Wiggler, NonLinearLens]:
        el = cls(name=cls.__name__, machine_area="MA")
        assert el.hardware_type == cls.__name__
        assert el.model_dump()["hardware_type"] == cls.__name__

    combined = Combined_Corrector(
        name="COMBINED1",
        machine_area="MA",
        Horizontal_Corrector="HCORR1",
        Vertical_Corrector="VCORR1",
    )
    assert combined.Horizontal_Corrector == "HCORR1"
    assert combined.Vertical_Corrector == "VCORR1"
