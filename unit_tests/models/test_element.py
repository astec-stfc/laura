# python
import pytest
from laura.models.element import baseElement, PhysicalBaseElement, Element
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
