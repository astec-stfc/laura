---
search:
  boost: 10.0
---

# Class: RFDeflectingCavity 


_Transverse-deflecting (streak) RF cavity._



<div data-search-exclude markdown="1">



URI: [laura:RFDeflectingCavity](https://w3id.org/laura/RFDeflectingCavity)





```mermaid
 classDiagram
    class RFDeflectingCavity
    click RFDeflectingCavity href "../RFDeflectingCavity/"
      RFCavity <|-- RFDeflectingCavity
        click RFCavity href "../RFCavity/"
      
      RFDeflectingCavity : alias
        
      RFDeflectingCavity : cavity
        
          
    
        
        
        RFDeflectingCavity --> "0..1" RFDeflectingCavityElement : cavity
        click RFDeflectingCavityElement href "../RFDeflectingCavityElement/"
    

        
      RFDeflectingCavity : controls
        
          
    
        
        
        RFDeflectingCavity --> "0..1" ControlsInformation : controls
        click ControlsInformation href "../ControlsInformation/"
    

        
      RFDeflectingCavity : electrical
        
          
    
        
        
        RFDeflectingCavity --> "0..1" ElectricalElement : electrical
        click ElectricalElement href "../ElectricalElement/"
    

        
      RFDeflectingCavity : hardware_class
        
          
    
        
        
        RFDeflectingCavity --> "1" HardwareClassEnum : hardware_class
        click HardwareClassEnum href "../HardwareClassEnum/"
    

        
      RFDeflectingCavity : hardware_model
        
      RFDeflectingCavity : hardware_type
        
      RFDeflectingCavity : machine_area
        
      RFDeflectingCavity : manufacturer
        
          
    
        
        
        RFDeflectingCavity --> "0..1" ManufacturerElement : manufacturer
        click ManufacturerElement href "../ManufacturerElement/"
    

        
      RFDeflectingCavity : name
        
      RFDeflectingCavity : physical
        
          
    
        
        
        RFDeflectingCavity --> "0..1" PhysicalElement : physical
        click PhysicalElement href "../PhysicalElement/"
    

        
      RFDeflectingCavity : reference
        
          
    
        
        
        RFDeflectingCavity --> "0..1" ReferenceElement : reference
        click ReferenceElement href "../ReferenceElement/"
    

        
      RFDeflectingCavity : simulation
        
          
    
        
        
        RFDeflectingCavity --> "0..1" RFCavitySimulationElement : simulation
        click RFCavitySimulationElement href "../RFCavitySimulationElement/"
    

        
      RFDeflectingCavity : subelement
        
      RFDeflectingCavity : virtual_name
        
      
```





## Inheritance
* [AcceleratorElement](AcceleratorElement.md)
    * [StandardElement](StandardElement.md)
        * [Element](Element.md)
            * [PhysicalAcceleratorElement](PhysicalAcceleratorElement.md)
                * [RFCavity](RFCavity.md)
                    * **RFDeflectingCavity**


## Class Properties

| Property | Value |
| --- | --- |
| Class URI | [laura:RFDeflectingCavity](https://w3id.org/laura/RFDeflectingCavity) |


## Slots

| Name | Cardinality and Range | Description | Inheritance |
| ---  | --- | --- | --- |
| [cavity](cavity.md) | 0..1 <br/> [RFDeflectingCavityElement](RFDeflectingCavityElement.md) | RF structure parameters | direct |
| [physical](physical.md) | 0..1 <br/> [PhysicalElement](PhysicalElement.md) | Position, rotation, and length data | [PhysicalAcceleratorElement](PhysicalAcceleratorElement.md) |
| [simulation](simulation.md) | 0..1 <br/> [RFCavitySimulationElement](RFCavitySimulationElement.md) | Simulation / tracking attributes | [StandardElement](StandardElement.md) |
| [electrical](electrical.md) | 0..1 <br/> [ElectricalElement](ElectricalElement.md) | Power-supply electrical limits | [StandardElement](StandardElement.md) |
| [manufacturer](manufacturer.md) | 0..1 <br/> [ManufacturerElement](ManufacturerElement.md) | Manufacturer and serial-number data | [StandardElement](StandardElement.md) |
| [controls](controls.md) | 0..1 <br/> [ControlsInformation](ControlsInformation.md) | Control-system process-variable definitions | [StandardElement](StandardElement.md) |
| [reference](reference.md) | 0..1 <br/> [ReferenceElement](ReferenceElement.md) | Links to design drawings and files | [StandardElement](StandardElement.md) |
| [name](name.md) | 1 <br/> [String](String.md) | Unique element name within the machine | [AcceleratorElement](AcceleratorElement.md) |
| [hardware_class](hardware_class.md) | 1 <br/> [HardwareClassEnum](HardwareClassEnum.md) | Functional category (e | [AcceleratorElement](AcceleratorElement.md) |
| [hardware_type](hardware_type.md) | 0..1 <br/> [String](String.md) | Python class name used for MODEL_REGISTRY dispatch | [AcceleratorElement](AcceleratorElement.md) |
| [hardware_model](hardware_model.md) | 0..1 <br/> [String](String.md) | Model or variant name within the hardware type (e | [AcceleratorElement](AcceleratorElement.md) |
| [machine_area](machine_area.md) | 0..1 <br/> [String](String.md) | Machine area label grouping related elements (e | [AcceleratorElement](AcceleratorElement.md) |
| [virtual_name](virtual_name.md) | 0..1 <br/> [String](String.md) | Alternative internal name used by the control system when the physical name i... | [AcceleratorElement](AcceleratorElement.md) |
| [alias](alias.md) | * <br/> [String](String.md) | Human-readable aliases for the element | [AcceleratorElement](AcceleratorElement.md) |
| [subelement](subelement.md) | 0..1 <br/> [String](String.md) | If set, this element is a logical sub-component of the named parent element | [AcceleratorElement](AcceleratorElement.md) |















## Identifier and Mapping Information





### Schema Source


* from schema: https://w3id.org/laura/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | laura:RFDeflectingCavity |
| native | laura:RFDeflectingCavity |






## LinkML Source

<!-- TODO: investigate https://stackoverflow.com/questions/37606292/how-to-create-tabbed-code-blocks-in-mkdocs-or-sphinx -->

### Direct

<details>
```yaml
name: RFDeflectingCavity
description: Transverse-deflecting (streak) RF cavity.
from_schema: https://w3id.org/laura/schema
is_a: RFCavity
slot_usage:
  hardware_type:
    name: hardware_type
    equals_string: RFDeflectingCavity
attributes:
  cavity:
    name: cavity
    description: RF structure parameters.
    in_subset:
    - rf_properties
    from_schema: https://w3id.org/laura/schema
    domain_of:
    - RFCavity
    - RFDeflectingCavity
    - Wakefield
    range: RFDeflectingCavityElement
class_uri: laura:RFDeflectingCavity

```
</details>

### Induced

<details>
```yaml
name: RFDeflectingCavity
description: Transverse-deflecting (streak) RF cavity.
from_schema: https://w3id.org/laura/schema
is_a: RFCavity
slot_usage:
  hardware_type:
    name: hardware_type
    equals_string: RFDeflectingCavity
attributes:
  cavity:
    name: cavity
    description: RF structure parameters.
    in_subset:
    - rf_properties
    from_schema: https://w3id.org/laura/schema
    owner: RFDeflectingCavity
    domain_of:
    - RFCavity
    - RFDeflectingCavity
    - Wakefield
    range: RFDeflectingCavityElement
  physical:
    name: physical
    description: Position, rotation, and length data.
    in_subset:
    - physical_properties
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    owner: RFDeflectingCavity
    domain_of:
    - PhysicalAcceleratorElement
    range: PhysicalElement
  simulation:
    name: simulation
    description: Simulation / tracking attributes.
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    owner: RFDeflectingCavity
    domain_of:
    - StandardElement
    range: RFCavitySimulationElement
  electrical:
    name: electrical
    description: Power-supply electrical limits.
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    owner: RFDeflectingCavity
    domain_of:
    - StandardElement
    range: ElectricalElement
  manufacturer:
    name: manufacturer
    description: Manufacturer and serial-number data.
    from_schema: https://w3id.org/laura/schema
    owner: RFDeflectingCavity
    domain_of:
    - ManufacturerElement
    - StandardElement
    range: ManufacturerElement
  controls:
    name: controls
    description: Control-system process-variable definitions.
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    owner: RFDeflectingCavity
    domain_of:
    - StandardElement
    range: ControlsInformation
  reference:
    name: reference
    description: Links to design drawings and files.
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    owner: RFDeflectingCavity
    domain_of:
    - StandardElement
    range: ReferenceElement
  name:
    name: name
    description: Unique element name within the machine.
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    identifier: true
    owner: RFDeflectingCavity
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
    owner: RFDeflectingCavity
    domain_of:
    - AcceleratorElement
    range: HardwareClassEnum
    required: true
  hardware_type:
    name: hardware_type
    description: Python class name used for MODEL_REGISTRY dispatch.  Identifies the
      concrete subclass to instantiate when loading from YAML.
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    ifabsent: string(Generic)
    owner: RFDeflectingCavity
    domain_of:
    - AcceleratorElement
    range: string
    equals_string: RFDeflectingCavity
  hardware_model:
    name: hardware_model
    description: Model or variant name within the hardware type (e.g., ``Generic``,
      ``TESLA``).
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    ifabsent: string(Generic)
    owner: RFDeflectingCavity
    domain_of:
    - AcceleratorElement
    range: string
  machine_area:
    name: machine_area
    description: Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    owner: RFDeflectingCavity
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
    owner: RFDeflectingCavity
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
    owner: RFDeflectingCavity
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
    owner: RFDeflectingCavity
    domain_of:
    - AcceleratorElement
    range: string
class_uri: laura:RFDeflectingCavity

```
</details></div>