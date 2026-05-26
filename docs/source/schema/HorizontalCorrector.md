---
search:
  boost: 10.0
---

# Class: HorizontalCorrector 


_Horizontal orbit-corrector dipole._



<div data-search-exclude markdown="1">



URI: [laura:HorizontalCorrector](https://w3id.org/laura/HorizontalCorrector)





```mermaid
 classDiagram
    class HorizontalCorrector
    click HorizontalCorrector href "../HorizontalCorrector/"
      Dipole <|-- HorizontalCorrector
        click Dipole href "../Dipole/"
      
      HorizontalCorrector : alias
        
      HorizontalCorrector : controls
        
          
    
        
        
        HorizontalCorrector --> "0..1" ControlsInformation : controls
        click ControlsInformation href "../ControlsInformation/"
    

        
      HorizontalCorrector : degauss
        
          
    
        
        
        HorizontalCorrector --> "0..1" DegaussableElement : degauss
        click DegaussableElement href "../DegaussableElement/"
    

        
      HorizontalCorrector : electrical
        
          
    
        
        
        HorizontalCorrector --> "0..1" ElectricalElement : electrical
        click ElectricalElement href "../ElectricalElement/"
    

        
      HorizontalCorrector : hardware_class
        
          
    
        
        
        HorizontalCorrector --> "0..1" HardwareClassEnum : hardware_class
        click HardwareClassEnum href "../HardwareClassEnum/"
    

        
      HorizontalCorrector : hardware_model
        
      HorizontalCorrector : hardware_type
        
      HorizontalCorrector : machine_area
        
      HorizontalCorrector : magnetic
        
          
    
        
        
        HorizontalCorrector --> "0..1" MagneticElement : magnetic
        click MagneticElement href "../MagneticElement/"
    

        
      HorizontalCorrector : manufacturer
        
          
    
        
        
        HorizontalCorrector --> "0..1" ManufacturerElement : manufacturer
        click ManufacturerElement href "../ManufacturerElement/"
    

        
      HorizontalCorrector : name
        
      HorizontalCorrector : physical
        
          
    
        
        
        HorizontalCorrector --> "0..1" PhysicalElement : physical
        click PhysicalElement href "../PhysicalElement/"
    

        
      HorizontalCorrector : reference
        
          
    
        
        
        HorizontalCorrector --> "0..1" ReferenceElement : reference
        click ReferenceElement href "../ReferenceElement/"
    

        
      HorizontalCorrector : simulation
        
          
    
        
        
        HorizontalCorrector --> "0..1" MagnetSimulationElement : simulation
        click MagnetSimulationElement href "../MagnetSimulationElement/"
    

        
      HorizontalCorrector : subelement
        
      HorizontalCorrector : virtual_name
        
      
```





## Inheritance
* [AcceleratorElement](AcceleratorElement.md)
    * [StandardElement](StandardElement.md)
        * [PhysicalAcceleratorElement](PhysicalAcceleratorElement.md)
            * [MagnetBaseElement](MagnetBaseElement.md)
                * [Dipole](Dipole.md)
                    * **HorizontalCorrector**


## Class Properties

| Property | Value |
| --- | --- |
| Class URI | [laura:HorizontalCorrector](https://w3id.org/laura/HorizontalCorrector) |


## Slots

| Name | Cardinality and Range | Description | Inheritance |
| ---  | --- | --- | --- |
| [magnetic](magnetic.md) | 0..1 <br/> [MagneticElement](MagneticElement.md) | Magnetic field parameters | [MagnetBaseElement](MagnetBaseElement.md) |
| [degauss](degauss.md) | 0..1 <br/> [DegaussableElement](DegaussableElement.md) | Degaussing-cycle parameters | [MagnetBaseElement](MagnetBaseElement.md) |
| [physical](physical.md) | 0..1 <br/> [PhysicalElement](PhysicalElement.md) | Position, rotation, and length data | [PhysicalAcceleratorElement](PhysicalAcceleratorElement.md) |
| [simulation](simulation.md) | 0..1 <br/> [MagnetSimulationElement](MagnetSimulationElement.md) | Simulation / tracking attributes | [StandardElement](StandardElement.md) |
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
| self | laura:HorizontalCorrector |
| native | laura:HorizontalCorrector |






## LinkML Source

<!-- TODO: investigate https://stackoverflow.com/questions/37606292/how-to-create-tabbed-code-blocks-in-mkdocs-or-sphinx -->

### Direct

<details>
```yaml
name: HorizontalCorrector
description: Horizontal orbit-corrector dipole.
from_schema: https://w3id.org/laura/schema
is_a: Dipole
slot_usage:
  hardware_type:
    name: hardware_type
    equals_string: Horizontal_Corrector
class_uri: laura:HorizontalCorrector

```
</details>

### Induced

<details>
```yaml
name: HorizontalCorrector
description: Horizontal orbit-corrector dipole.
from_schema: https://w3id.org/laura/schema
is_a: Dipole
slot_usage:
  hardware_type:
    name: hardware_type
    equals_string: Horizontal_Corrector
attributes:
  magnetic:
    name: magnetic
    description: Magnetic field parameters.
    in_subset:
    - magnetic_properties
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    owner: HorizontalCorrector
    domain_of:
    - MagnetBaseElement
    range: MagneticElement
  degauss:
    name: degauss
    description: Degaussing-cycle parameters.
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    owner: HorizontalCorrector
    domain_of:
    - MagnetBaseElement
    range: DegaussableElement
  physical:
    name: physical
    description: Position, rotation, and length data.
    in_subset:
    - physical_properties
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    owner: HorizontalCorrector
    domain_of:
    - PhysicalAcceleratorElement
    range: PhysicalElement
  simulation:
    name: simulation
    description: Simulation / tracking attributes.
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    owner: HorizontalCorrector
    domain_of:
    - StandardElement
    range: MagnetSimulationElement
  electrical:
    name: electrical
    description: Power-supply electrical limits.
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    owner: HorizontalCorrector
    domain_of:
    - StandardElement
    range: ElectricalElement
  manufacturer:
    name: manufacturer
    description: Manufacturer and serial-number data.
    from_schema: https://w3id.org/laura/schema
    owner: HorizontalCorrector
    domain_of:
    - ManufacturerElement
    - StandardElement
    range: ManufacturerElement
  controls:
    name: controls
    description: Control-system process-variable definitions.
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    owner: HorizontalCorrector
    domain_of:
    - StandardElement
    range: ControlsInformation
  reference:
    name: reference
    description: Links to design drawings and files.
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    owner: HorizontalCorrector
    domain_of:
    - StandardElement
    range: ReferenceElement
  name:
    name: name
    description: Unique element name within the machine.
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    identifier: true
    owner: HorizontalCorrector
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
    owner: HorizontalCorrector
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
    owner: HorizontalCorrector
    domain_of:
    - AcceleratorElement
    range: string
    equals_string: Horizontal_Corrector
  hardware_model:
    name: hardware_model
    description: Model or variant name within the hardware type (e.g., ``Generic``,
      ``TESLA``).
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    owner: HorizontalCorrector
    domain_of:
    - AcceleratorElement
    range: string
  machine_area:
    name: machine_area
    description: Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    owner: HorizontalCorrector
    domain_of:
    - AcceleratorElement
    range: string
  virtual_name:
    name: virtual_name
    description: Alternative internal name used by the control system when the physical
      name is inaccessible.
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    owner: HorizontalCorrector
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
    owner: HorizontalCorrector
    domain_of:
    - AcceleratorElement
    range: string
  subelement:
    name: subelement
    description: If set, this element is a logical sub-component of the named parent
      element.
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    owner: HorizontalCorrector
    domain_of:
    - AcceleratorElement
    range: string
class_uri: laura:HorizontalCorrector

```
</details></div>