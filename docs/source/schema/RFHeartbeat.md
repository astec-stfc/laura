---
search:
  boost: 10.0
---

# Class: RFHeartbeat 


_RF timing heartbeat / signal-monitor element._



<div data-search-exclude markdown="1">



URI: [laura:RFHeartbeat](https://w3id.org/laura/RFHeartbeat)





```mermaid
 classDiagram
    class RFHeartbeat
    click RFHeartbeat href "../RFHeartbeat/"
      StandardElement <|-- RFHeartbeat
        click StandardElement href "../StandardElement/"
      
      RFHeartbeat : alias
        
      RFHeartbeat : controls
        
          
    
        
        
        RFHeartbeat --> "0..1" ControlsInformation : controls
        click ControlsInformation href "../ControlsInformation/"
    

        
      RFHeartbeat : electrical
        
          
    
        
        
        RFHeartbeat --> "0..1" ElectricalElement : electrical
        click ElectricalElement href "../ElectricalElement/"
    

        
      RFHeartbeat : hardware_class
        
          
    
        
        
        RFHeartbeat --> "0..1" HardwareClassEnum : hardware_class
        click HardwareClassEnum href "../HardwareClassEnum/"
    

        
      RFHeartbeat : hardware_model
        
      RFHeartbeat : hardware_type
        
      RFHeartbeat : heartbeat
        
          
    
        
        
        RFHeartbeat --> "0..1" RFHeartbeatElement : heartbeat
        click RFHeartbeatElement href "../RFHeartbeatElement/"
    

        
      RFHeartbeat : machine_area
        
      RFHeartbeat : manufacturer
        
          
    
        
        
        RFHeartbeat --> "0..1" ManufacturerElement : manufacturer
        click ManufacturerElement href "../ManufacturerElement/"
    

        
      RFHeartbeat : name
        
      RFHeartbeat : reference
        
          
    
        
        
        RFHeartbeat --> "0..1" ReferenceElement : reference
        click ReferenceElement href "../ReferenceElement/"
    

        
      RFHeartbeat : simulation
        
          
    
        
        
        RFHeartbeat --> "0..1" SimulationElement : simulation
        click SimulationElement href "../SimulationElement/"
    

        
      RFHeartbeat : subelement
        
      RFHeartbeat : virtual_name
        
      
```





## Inheritance
* [AcceleratorElement](AcceleratorElement.md)
    * [StandardElement](StandardElement.md)
        * **RFHeartbeat**


## Class Properties

| Property | Value |
| --- | --- |
| Class URI | [laura:RFHeartbeat](https://w3id.org/laura/RFHeartbeat) |


## Slots

| Name | Cardinality and Range | Description | Inheritance |
| ---  | --- | --- | --- |
| [heartbeat](heartbeat.md) | 0..1 <br/> [RFHeartbeatElement](RFHeartbeatElement.md) | RF heartbeat parameters | direct |
| [simulation](simulation.md) | 0..1 <br/> [SimulationElement](SimulationElement.md) | Simulation / tracking attributes | [StandardElement](StandardElement.md) |
| [electrical](electrical.md) | 0..1 <br/> [ElectricalElement](ElectricalElement.md) | Power-supply electrical limits | [StandardElement](StandardElement.md) |
| [manufacturer](manufacturer.md) | 0..1 <br/> [ManufacturerElement](ManufacturerElement.md) | Manufacturer and serial-number data | [StandardElement](StandardElement.md) |
| [controls](controls.md) | 0..1 <br/> [ControlsInformation](ControlsInformation.md) | Control-system process-variable definitions | [StandardElement](StandardElement.md) |
| [reference](reference.md) | 0..1 <br/> [ReferenceElement](ReferenceElement.md) | Links to design drawings and files | [StandardElement](StandardElement.md) |
| [name](name.md) | 1 <br/> [String](String.md) | Unique element name within the machine | [AcceleratorElement](AcceleratorElement.md) |
| [hardware_class](hardware_class.md) | 0..1 <br/> [HardwareClassEnum](HardwareClassEnum.md) | Functional category (e | [AcceleratorElement](AcceleratorElement.md) |
| [hardware_type](hardware_type.md) | 0..1 <br/> [String](String.md) | Python class name used for MODEL_REGISTRY dispatch | [AcceleratorElement](AcceleratorElement.md) |
| [hardware_model](hardware_model.md) | 0..1 <br/> [String](String.md) | Model or variant name within the hardware type (e | [AcceleratorElement](AcceleratorElement.md) |
| [machine_area](machine_area.md) | 0..1 <br/> [String](String.md) | Machine area label grouping related elements (e | [AcceleratorElement](AcceleratorElement.md) |
| [virtual_name](virtual_name.md) | 0..1 <br/> [String](String.md) | Alternative internal name used by the control system when the physical name i... | [AcceleratorElement](AcceleratorElement.md) |
| [alias](alias.md) | 0..1 <br/> [String](String.md) | Short human-readable alias | [AcceleratorElement](AcceleratorElement.md) |
| [subelement](subelement.md) | 0..1 <br/> [String](String.md) | If set, this element is a logical sub-component of the named parent element | [AcceleratorElement](AcceleratorElement.md) |















## Identifier and Mapping Information





### Schema Source


* from schema: https://w3id.org/laura/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | laura:RFHeartbeat |
| native | laura:RFHeartbeat |






## LinkML Source

<!-- TODO: investigate https://stackoverflow.com/questions/37606292/how-to-create-tabbed-code-blocks-in-mkdocs-or-sphinx -->

### Direct

<details>
```yaml
name: RFHeartbeat
description: RF timing heartbeat / signal-monitor element.
from_schema: https://w3id.org/laura/schema
is_a: StandardElement
slot_usage:
  hardware_type:
    name: hardware_type
    equals_string: RFHeartbeat
attributes:
  heartbeat:
    name: heartbeat
    description: RF heartbeat parameters.
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    domain_of:
    - RFHeartbeat
    range: RFHeartbeatElement
class_uri: laura:RFHeartbeat

```
</details>

### Induced

<details>
```yaml
name: RFHeartbeat
description: RF timing heartbeat / signal-monitor element.
from_schema: https://w3id.org/laura/schema
is_a: StandardElement
slot_usage:
  hardware_type:
    name: hardware_type
    equals_string: RFHeartbeat
attributes:
  heartbeat:
    name: heartbeat
    description: RF heartbeat parameters.
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    owner: RFHeartbeat
    domain_of:
    - RFHeartbeat
    range: RFHeartbeatElement
  simulation:
    name: simulation
    description: Simulation / tracking attributes.
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    owner: RFHeartbeat
    domain_of:
    - StandardElement
    range: SimulationElement
  electrical:
    name: electrical
    description: Power-supply electrical limits.
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    owner: RFHeartbeat
    domain_of:
    - StandardElement
    range: ElectricalElement
  manufacturer:
    name: manufacturer
    description: Manufacturer and serial-number data.
    from_schema: https://w3id.org/laura/schema
    owner: RFHeartbeat
    domain_of:
    - ManufacturerElement
    - StandardElement
    range: ManufacturerElement
  controls:
    name: controls
    description: Control-system process-variable definitions.
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    owner: RFHeartbeat
    domain_of:
    - StandardElement
    range: ControlsInformation
  reference:
    name: reference
    description: Links to design drawings and files.
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    owner: RFHeartbeat
    domain_of:
    - StandardElement
    range: ReferenceElement
  name:
    name: name
    description: Unique element name within the machine.
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    identifier: true
    owner: RFHeartbeat
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
    owner: RFHeartbeat
    domain_of:
    - AcceleratorElement
    range: HardwareClassEnum
  hardware_type:
    name: hardware_type
    description: Python class name used for MODEL_REGISTRY dispatch.  Identifies the
      concrete subclass to instantiate when loading from YAML.
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    designates_type: true
    owner: RFHeartbeat
    domain_of:
    - AcceleratorElement
    range: string
    equals_string: RFHeartbeat
  hardware_model:
    name: hardware_model
    description: Model or variant name within the hardware type (e.g., ``Generic``,
      ``TESLA``).
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    owner: RFHeartbeat
    domain_of:
    - AcceleratorElement
    range: string
  machine_area:
    name: machine_area
    description: Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    owner: RFHeartbeat
    domain_of:
    - AcceleratorElement
    range: string
  virtual_name:
    name: virtual_name
    description: Alternative internal name used by the control system when the physical
      name is inaccessible.
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    owner: RFHeartbeat
    domain_of:
    - AcceleratorElement
    range: string
  alias:
    name: alias
    description: Short human-readable alias. Populated from ``name_alias`` in YAML.
    from_schema: https://w3id.org/laura/schema
    aliases:
    - name_alias
    rank: 1000
    owner: RFHeartbeat
    domain_of:
    - AcceleratorElement
    range: string
  subelement:
    name: subelement
    description: If set, this element is a logical sub-component of the named parent
      element.
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    owner: RFHeartbeat
    domain_of:
    - AcceleratorElement
    range: string
class_uri: laura:RFHeartbeat

```
</details></div>