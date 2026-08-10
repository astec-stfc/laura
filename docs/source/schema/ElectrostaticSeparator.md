# Class: ElectrostaticSeparator 


_Static electrostatic transverse-deflection element._



<div data-search-exclude markdown="1">



URI: [laura:ElectrostaticSeparator](https://w3id.org/laura/ElectrostaticSeparator)





```mermaid
 classDiagram
    class ElectrostaticSeparator
    click ElectrostaticSeparator href "../ElectrostaticSeparator/"
      PhysicalAcceleratorElement <|-- ElectrostaticSeparator
        click PhysicalAcceleratorElement href "../PhysicalAcceleratorElement/"
      
      ElectrostaticSeparator : alias
        
      ElectrostaticSeparator : aperture
        
          
    
        
        
        ElectrostaticSeparator --> "0..1" ApertureElement : aperture
        click ApertureElement href "../ApertureElement/"
    

        
      ElectrostaticSeparator : controls
        
          
    
        
        
        ElectrostaticSeparator --> "0..1" ControlsInformation : controls
        click ControlsInformation href "../ControlsInformation/"
    

        
      ElectrostaticSeparator : downstream
        
          
    
        
        
        ElectrostaticSeparator --> "*" AcceleratorElement : downstream
        click AcceleratorElement href "../AcceleratorElement/"
    

        
      ElectrostaticSeparator : electrical
        
          
    
        
        
        ElectrostaticSeparator --> "0..1" ElectricalElement : electrical
        click ElectricalElement href "../ElectricalElement/"
    

        
      ElectrostaticSeparator : hardware_class
        
          
    
        
        
        ElectrostaticSeparator --> "1" HardwareClassEnum : hardware_class
        click HardwareClassEnum href "../HardwareClassEnum/"
    

        
      ElectrostaticSeparator : hardware_model
        
      ElectrostaticSeparator : hardware_type
        
      ElectrostaticSeparator : inputs
        
          
    
        
        
        ElectrostaticSeparator --> "*" IOTypeEnum : inputs
        click IOTypeEnum href "../IOTypeEnum/"
    

        
      ElectrostaticSeparator : machine_area
        
      ElectrostaticSeparator : manufacturer
        
          
    
        
        
        ElectrostaticSeparator --> "0..1" ManufacturerElement : manufacturer
        click ManufacturerElement href "../ManufacturerElement/"
    

        
      ElectrostaticSeparator : material
        
      ElectrostaticSeparator : name
        
      ElectrostaticSeparator : outputs
        
          
    
        
        
        ElectrostaticSeparator --> "*" IOTypeEnum : outputs
        click IOTypeEnum href "../IOTypeEnum/"
    

        
      ElectrostaticSeparator : physical
        
          
    
        
        
        ElectrostaticSeparator --> "0..1" PhysicalElement : physical
        click PhysicalElement href "../PhysicalElement/"
    

        
      ElectrostaticSeparator : reference
        
          
    
        
        
        ElectrostaticSeparator --> "0..1" ReferenceElement : reference
        click ReferenceElement href "../ReferenceElement/"
    

        
      ElectrostaticSeparator : simulation
        
          
    
        
        
        ElectrostaticSeparator --> "0..1" ElectrostaticSeparatorSimulationElement : simulation
        click ElectrostaticSeparatorSimulationElement href "../ElectrostaticSeparatorSimulationElement/"
    

        
      ElectrostaticSeparator : subelement
        
      ElectrostaticSeparator : upstream
        
          
    
        
        
        ElectrostaticSeparator --> "*" AcceleratorElement : upstream
        click AcceleratorElement href "../AcceleratorElement/"
    

        
      ElectrostaticSeparator : virtual_name
        
      
```





## Inheritance
* [AcceleratorElement](AcceleratorElement.md)
    * [StandardElement](StandardElement.md)
        * [Element](Element.md)
            * [PhysicalAcceleratorElement](PhysicalAcceleratorElement.md)
                * **ElectrostaticSeparator**


## Class Properties

| Property | Value |
| --- | --- |
| Class URI | [laura:ElectrostaticSeparator](https://w3id.org/laura/ElectrostaticSeparator) |


## Slots

| Name | Cardinality and Range | Description | Inheritance |
| ---  | --- | --- | --- |
| [physical](physical.md) | 0..1 <br/> [PhysicalElement](PhysicalElement.md) | Position, rotation, and length data | [PhysicalAcceleratorElement](PhysicalAcceleratorElement.md) |
| [aperture](aperture.md) | 0..1 <br/> [ApertureElement](ApertureElement.md) | Aperture of the element | [PhysicalAcceleratorElement](PhysicalAcceleratorElement.md) |
| [material](material.md) | 0..1 <br/> [String](String.md) | Element material | [PhysicalAcceleratorElement](PhysicalAcceleratorElement.md) |
| [simulation](simulation.md) | 0..1 <br/> [ElectrostaticSeparatorSimulationElement](ElectrostaticSeparatorSimulationElement.md) | Simulation / tracking attributes | [StandardElement](StandardElement.md) |
| [electrical](electrical.md) | 0..1 <br/> [ElectricalElement](ElectricalElement.md) | Power-supply electrical limits | [StandardElement](StandardElement.md) |
| [manufacturer](manufacturer.md) | 0..1 <br/> [ManufacturerElement](ManufacturerElement.md) | Manufacturer and serial-number data | [StandardElement](StandardElement.md) |
| [controls](controls.md) | 0..1 <br/> [ControlsInformation](ControlsInformation.md) | Control-system process-variable definitions | [StandardElement](StandardElement.md) |
| [reference](reference.md) | 0..1 <br/> [ReferenceElement](ReferenceElement.md) | Links to design drawings and files | [StandardElement](StandardElement.md) |
| [name](name.md) | 1 <br/> [String](String.md) | Unique element name within the machine | [AcceleratorElement](AcceleratorElement.md) |
| [hardware_class](hardware_class.md) | 1 <br/> [HardwareClassEnum](HardwareClassEnum.md) | Functional category (e | [AcceleratorElement](AcceleratorElement.md) |
| [hardware_type](hardware_type.md) | 0..1 <br/> [String](String.md) | Python class name used for ELEMENT_REGISTRY dispatch | [AcceleratorElement](AcceleratorElement.md) |
| [hardware_model](hardware_model.md) | 0..1 <br/> [String](String.md) | Model or variant name within the hardware type (e | [AcceleratorElement](AcceleratorElement.md) |
| [machine_area](machine_area.md) | 0..1 <br/> [String](String.md) | Machine area label grouping related elements (e | [AcceleratorElement](AcceleratorElement.md) |
| [virtual_name](virtual_name.md) | 0..1 <br/> [String](String.md) | Alternative internal name used by the control system when the physical name i... | [AcceleratorElement](AcceleratorElement.md) |
| [alias](alias.md) | * <br/> [String](String.md) | Human-readable aliases for the element | [AcceleratorElement](AcceleratorElement.md) |
| [subelement](subelement.md) | 0..1 <br/> [String](String.md) | If set, this element is a logical sub-component of the named parent element | [AcceleratorElement](AcceleratorElement.md) |
| [inputs](inputs.md) | * <br/> [IOTypeEnum](IOTypeEnum.md) | Signal types this element consumes (e | [AcceleratorElement](AcceleratorElement.md) |
| [outputs](outputs.md) | * <br/> [IOTypeEnum](IOTypeEnum.md) | Signal types this element produces (e | [AcceleratorElement](AcceleratorElement.md) |
| [upstream](upstream.md) | * <br/> [AcceleratorElement](AcceleratorElement.md) | Names of elements feeding this one, whose ``outputs`` supply its ``inputs`` | [AcceleratorElement](AcceleratorElement.md) |
| [downstream](downstream.md) | * <br/> [AcceleratorElement](AcceleratorElement.md) | Names of elements this one feeds; the inverse of ``upstream`` | [AcceleratorElement](AcceleratorElement.md) |















## Identifier and Mapping Information





### Schema Source


* from schema: https://w3id.org/laura/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | laura:ElectrostaticSeparator |
| native | laura:ElectrostaticSeparator |






## LinkML Source

<!-- TODO: investigate https://stackoverflow.com/questions/37606292/how-to-create-tabbed-code-blocks-in-mkdocs-or-sphinx -->

### Direct

<details>
```yaml
name: ElectrostaticSeparator
description: Static electrostatic transverse-deflection element.
from_schema: https://w3id.org/laura/schema
is_a: PhysicalAcceleratorElement
slot_usage:
  hardware_type:
    name: hardware_type
    equals_string: ElectrostaticSeparator
  simulation:
    name: simulation
    range: ElectrostaticSeparatorSimulationElement
class_uri: laura:ElectrostaticSeparator

```
</details>

### Induced

<details>
```yaml
name: ElectrostaticSeparator
description: Static electrostatic transverse-deflection element.
from_schema: https://w3id.org/laura/schema
is_a: PhysicalAcceleratorElement
slot_usage:
  hardware_type:
    name: hardware_type
    equals_string: ElectrostaticSeparator
  simulation:
    name: simulation
    range: ElectrostaticSeparatorSimulationElement
attributes:
  physical:
    name: physical
    description: Position, rotation, and length data.
    in_subset:
    - physical_properties
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    owner: ElectrostaticSeparator
    domain_of:
    - PhysicalAcceleratorElement
    range: PhysicalElement
  aperture:
    name: aperture
    description: Aperture of the element.
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    owner: ElectrostaticSeparator
    domain_of:
    - PhysicalAcceleratorElement
    - Aperture
    range: ApertureElement
  material:
    name: material
    description: 'Element material. '
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    owner: ElectrostaticSeparator
    domain_of:
    - PhysicalAcceleratorElement
    - ApertureElement
    range: string
  simulation:
    name: simulation
    description: Simulation / tracking attributes.
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    owner: ElectrostaticSeparator
    domain_of:
    - StandardElement
    range: ElectrostaticSeparatorSimulationElement
  electrical:
    name: electrical
    description: Power-supply electrical limits.
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    owner: ElectrostaticSeparator
    domain_of:
    - StandardElement
    range: ElectricalElement
  manufacturer:
    name: manufacturer
    description: Manufacturer and serial-number data.
    from_schema: https://w3id.org/laura/schema
    owner: ElectrostaticSeparator
    domain_of:
    - ManufacturerElement
    - StandardElement
    range: ManufacturerElement
  controls:
    name: controls
    description: Control-system process-variable definitions.
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    owner: ElectrostaticSeparator
    domain_of:
    - StandardElement
    range: ControlsInformation
  reference:
    name: reference
    description: Links to design drawings and files.
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    owner: ElectrostaticSeparator
    domain_of:
    - StandardElement
    range: ReferenceElement
  name:
    name: name
    description: Unique element name within the machine.
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    identifier: true
    owner: ElectrostaticSeparator
    domain_of:
    - AcceleratorElement
    - SectionLattice
    - MachineLayout
    range: string
    required: true
  hardware_class:
    name: hardware_class
    description: Functional category (e.g., ``Magnet``, ``Diagnostic``).
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    owner: ElectrostaticSeparator
    domain_of:
    - AcceleratorElement
    range: HardwareClassEnum
    required: true
  hardware_type:
    name: hardware_type
    description: Python class name used for ELEMENT_REGISTRY dispatch.  Identifies
      the concrete subclass to instantiate when loading from YAML.
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    ifabsent: string(Generic)
    owner: ElectrostaticSeparator
    domain_of:
    - AcceleratorElement
    range: string
    equals_string: ElectrostaticSeparator
  hardware_model:
    name: hardware_model
    description: Model or variant name within the hardware type (e.g., ``Generic``,
      ``TESLA``).
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    ifabsent: string(Generic)
    owner: ElectrostaticSeparator
    domain_of:
    - AcceleratorElement
    range: string
  machine_area:
    name: machine_area
    description: Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    owner: ElectrostaticSeparator
    domain_of:
    - AcceleratorElement
    range: string
  virtual_name:
    name: virtual_name
    description: Alternative internal name used by the control system when the physical
      name is inaccessible.
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    ifabsent: string()
    owner: ElectrostaticSeparator
    domain_of:
    - AcceleratorElement
    range: string
  alias:
    name: alias
    description: Human-readable aliases for the element. Populated from ``name_alias``
      in YAML. Accepts a single string or a list of strings.
    from_schema: https://w3id.org/laura/schema
    aliases:
    - name_alias
    rank: 1000
    owner: ElectrostaticSeparator
    domain_of:
    - AcceleratorElement
    range: string
    multivalued: true
  subelement:
    name: subelement
    description: If set, this element is a logical sub-component of the named parent
      element.
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    owner: ElectrostaticSeparator
    domain_of:
    - AcceleratorElement
    range: string
  inputs:
    name: inputs
    description: Signal types this element consumes (e.g. ``[current, voltage]``).
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    owner: ElectrostaticSeparator
    domain_of:
    - AcceleratorElement
    range: IOTypeEnum
    multivalued: true
  outputs:
    name: outputs
    description: Signal types this element produces (e.g. ``[power, phase]``).
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    owner: ElectrostaticSeparator
    domain_of:
    - AcceleratorElement
    range: IOTypeEnum
    multivalued: true
  upstream:
    name: upstream
    description: Names of elements feeding this one, whose ``outputs`` supply its
      ``inputs``.
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    owner: ElectrostaticSeparator
    domain_of:
    - AcceleratorElement
    range: AcceleratorElement
    multivalued: true
  downstream:
    name: downstream
    description: Names of elements this one feeds; the inverse of ``upstream``.
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    owner: ElectrostaticSeparator
    domain_of:
    - AcceleratorElement
    range: AcceleratorElement
    multivalued: true
class_uri: laura:ElectrostaticSeparator

```
</details></div>