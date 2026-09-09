# Class: Stage 


_Motorised positioning stage._



<div data-search-exclude markdown="1">



URI: [laura:Stage](https://w3id.org/laura/Stage)





```mermaid
 classDiagram
    class Stage
    click Stage href "../Stage/"
      PhysicalAcceleratorElement <|-- Stage
        click PhysicalAcceleratorElement href "../PhysicalAcceleratorElement/"
      
      Stage : alias
        
      Stage : aperture
        
          
    
        
        
        Stage --> "0..1" ApertureElement : aperture
        click ApertureElement href "../ApertureElement/"
    

        
      Stage : controls
        
          
    
        
        
        Stage --> "0..1" ControlsInformation : controls
        click ControlsInformation href "../ControlsInformation/"
    

        
      Stage : downstream
        
          
    
        
        
        Stage --> "*" AcceleratorElement : downstream
        click AcceleratorElement href "../AcceleratorElement/"
    

        
      Stage : electrical
        
          
    
        
        
        Stage --> "0..1" ElectricalElement : electrical
        click ElectricalElement href "../ElectricalElement/"
    

        
      Stage : hardware_class
        
          
    
        
        
        Stage --> "1" HardwareClassEnum : hardware_class
        click HardwareClassEnum href "../HardwareClassEnum/"
    

        
      Stage : hardware_model
        
      Stage : hardware_type
        
      Stage : inputs
        
          
    
        
        
        Stage --> "*" IOTypeEnum : inputs
        click IOTypeEnum href "../IOTypeEnum/"
    

        
      Stage : machine_area
        
      Stage : manufacturer
        
          
    
        
        
        Stage --> "0..1" ManufacturerElement : manufacturer
        click ManufacturerElement href "../ManufacturerElement/"
    

        
      Stage : name
        
      Stage : outputs
        
          
    
        
        
        Stage --> "*" IOTypeEnum : outputs
        click IOTypeEnum href "../IOTypeEnum/"
    

        
      Stage : physical
        
          
    
        
        
        Stage --> "0..1" PhysicalElement : physical
        click PhysicalElement href "../PhysicalElement/"
    

        
      Stage : reference
        
          
    
        
        
        Stage --> "0..1" ReferenceElement : reference
        click ReferenceElement href "../ReferenceElement/"
    

        
      Stage : simulation
        
          
    
        
        
        Stage --> "0..1" SimulationElement : simulation
        click SimulationElement href "../SimulationElement/"
    

        
      Stage : subelement
        
      Stage : upstream
        
          
    
        
        
        Stage --> "*" AcceleratorElement : upstream
        click AcceleratorElement href "../AcceleratorElement/"
    

        
      Stage : virtual_name
        
      
```





## Inheritance
* [AcceleratorElement](AcceleratorElement.md)
    * [StandardElement](StandardElement.md)
        * [Element](Element.md)
            * [PhysicalAcceleratorElement](PhysicalAcceleratorElement.md)
                * **Stage**


## Class Properties

| Property | Value |
| --- | --- |
| Class URI | [laura:Stage](https://w3id.org/laura/Stage) |


## Slots

| Name | Cardinality and Range | Description | Inheritance |
| ---  | --- | --- | --- |
| [physical](physical.md) | 0..1 <br/> [PhysicalElement](PhysicalElement.md) | Position, rotation, and length data | [PhysicalAcceleratorElement](PhysicalAcceleratorElement.md) |
| [aperture](aperture.md) | 0..1 <br/> [ApertureElement](ApertureElement.md) | Aperture of the element | [PhysicalAcceleratorElement](PhysicalAcceleratorElement.md) |
| [simulation](simulation.md) | 0..1 <br/> [SimulationElement](SimulationElement.md) | Simulation / tracking attributes | [StandardElement](StandardElement.md) |
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
| self | laura:Stage |
| native | laura:Stage |






## LinkML Source

<!-- TODO: investigate https://stackoverflow.com/questions/37606292/how-to-create-tabbed-code-blocks-in-mkdocs-or-sphinx -->

### Direct

<details>
```yaml
name: Stage
description: Motorised positioning stage.
from_schema: https://w3id.org/laura/schema
is_a: PhysicalAcceleratorElement
slot_usage:
  hardware_type:
    name: hardware_type
    equals_string: Stage
class_uri: laura:Stage

```
</details>

### Induced

<details>
```yaml
name: Stage
description: Motorised positioning stage.
from_schema: https://w3id.org/laura/schema
is_a: PhysicalAcceleratorElement
slot_usage:
  hardware_type:
    name: hardware_type
    equals_string: Stage
attributes:
  physical:
    name: physical
    description: Position, rotation, and length data.
    in_subset:
    - physical_properties
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    owner: Stage
    domain_of:
    - PhysicalAcceleratorElement
    range: PhysicalElement
  aperture:
    name: aperture
    description: Aperture of the element.
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    owner: Stage
    domain_of:
    - PhysicalAcceleratorElement
    - Aperture
    range: ApertureElement
    required: false
  simulation:
    name: simulation
    description: Simulation / tracking attributes.
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    owner: Stage
    domain_of:
    - StandardElement
    range: SimulationElement
  electrical:
    name: electrical
    description: Power-supply electrical limits.
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    owner: Stage
    domain_of:
    - StandardElement
    range: ElectricalElement
  manufacturer:
    name: manufacturer
    description: Manufacturer and serial-number data.
    from_schema: https://w3id.org/laura/schema
    owner: Stage
    domain_of:
    - ManufacturerElement
    - StandardElement
    range: ManufacturerElement
  controls:
    name: controls
    description: Control-system process-variable definitions.
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    owner: Stage
    domain_of:
    - StandardElement
    range: ControlsInformation
  reference:
    name: reference
    description: Links to design drawings and files.
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    owner: Stage
    domain_of:
    - StandardElement
    range: ReferenceElement
  name:
    name: name
    description: Unique element name within the machine.
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    identifier: true
    owner: Stage
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
    owner: Stage
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
    owner: Stage
    domain_of:
    - AcceleratorElement
    range: string
    equals_string: Stage
  hardware_model:
    name: hardware_model
    description: Model or variant name within the hardware type (e.g., ``Generic``,
      ``TESLA``).
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    ifabsent: string(Generic)
    owner: Stage
    domain_of:
    - AcceleratorElement
    range: string
  machine_area:
    name: machine_area
    description: Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    owner: Stage
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
    owner: Stage
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
    owner: Stage
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
    owner: Stage
    domain_of:
    - AcceleratorElement
    range: string
  inputs:
    name: inputs
    description: Signal types this element consumes (e.g. ``[current, voltage]``).
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    owner: Stage
    domain_of:
    - AcceleratorElement
    range: IOTypeEnum
    multivalued: true
  outputs:
    name: outputs
    description: Signal types this element produces (e.g. ``[power, phase]``).
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    owner: Stage
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
    owner: Stage
    domain_of:
    - AcceleratorElement
    range: AcceleratorElement
    multivalued: true
  downstream:
    name: downstream
    description: Names of elements this one feeds; the inverse of ``upstream``.
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    owner: Stage
    domain_of:
    - AcceleratorElement
    range: AcceleratorElement
    multivalued: true
class_uri: laura:Stage

```
</details></div>