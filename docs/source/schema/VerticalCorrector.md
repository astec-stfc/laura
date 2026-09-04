# Class: VerticalCorrector 


_Vertical steering corrector._



<div data-search-exclude markdown="1">



URI: [laura:VerticalCorrector](https://w3id.org/laura/VerticalCorrector)





```mermaid
 classDiagram
    class VerticalCorrector
    click VerticalCorrector href "../VerticalCorrector/"
      Dipole <|-- VerticalCorrector
        click Dipole href "../Dipole/"
      
      VerticalCorrector : alias
        
      VerticalCorrector : controls
        
          
    
        
        
        VerticalCorrector --> "0..1" ControlsInformation : controls
        click ControlsInformation href "../ControlsInformation/"
    

        
      VerticalCorrector : degauss
        
          
    
        
        
        VerticalCorrector --> "0..1" DegaussableElement : degauss
        click DegaussableElement href "../DegaussableElement/"
    

        
      VerticalCorrector : downstream
        
          
    
        
        
        VerticalCorrector --> "*" AcceleratorElement : downstream
        click AcceleratorElement href "../AcceleratorElement/"
    

        
      VerticalCorrector : electrical
        
          
    
        
        
        VerticalCorrector --> "0..1" ElectricalElement : electrical
        click ElectricalElement href "../ElectricalElement/"
    

        
      VerticalCorrector : hardware_class
        
          
    
        
        
        VerticalCorrector --> "1" HardwareClassEnum : hardware_class
        click HardwareClassEnum href "../HardwareClassEnum/"
    

        
      VerticalCorrector : hardware_model
        
      VerticalCorrector : hardware_type
        
      VerticalCorrector : inputs
        
          
    
        
        
        VerticalCorrector --> "*" IOTypeEnum : inputs
        click IOTypeEnum href "../IOTypeEnum/"
    

        
      VerticalCorrector : machine_area
        
      VerticalCorrector : magnetic
        
          
    
        
        
        VerticalCorrector --> "0..1" CorrectorMagnet : magnetic
        click CorrectorMagnet href "../CorrectorMagnet/"
    

        
      VerticalCorrector : manufacturer
        
          
    
        
        
        VerticalCorrector --> "0..1" ManufacturerElement : manufacturer
        click ManufacturerElement href "../ManufacturerElement/"
    

        
      VerticalCorrector : name
        
      VerticalCorrector : outputs
        
          
    
        
        
        VerticalCorrector --> "*" IOTypeEnum : outputs
        click IOTypeEnum href "../IOTypeEnum/"
    

        
      VerticalCorrector : physical
        
          
    
        
        
        VerticalCorrector --> "0..1" PhysicalElement : physical
        click PhysicalElement href "../PhysicalElement/"
    

        
      VerticalCorrector : reference
        
          
    
        
        
        VerticalCorrector --> "0..1" ReferenceElement : reference
        click ReferenceElement href "../ReferenceElement/"
    

        
      VerticalCorrector : simulation
        
          
    
        
        
        VerticalCorrector --> "0..1" MagnetSimulationElement : simulation
        click MagnetSimulationElement href "../MagnetSimulationElement/"
    

        
      VerticalCorrector : subelement
        
      VerticalCorrector : upstream
        
          
    
        
        
        VerticalCorrector --> "*" AcceleratorElement : upstream
        click AcceleratorElement href "../AcceleratorElement/"
    

        
      VerticalCorrector : virtual_name
        
      
```





## Inheritance
* [AcceleratorElement](AcceleratorElement.md)
    * [StandardElement](StandardElement.md)
        * [Element](Element.md)
            * [PhysicalAcceleratorElement](PhysicalAcceleratorElement.md)
                * [Magnet](Magnet.md)
                    * [Dipole](Dipole.md)
                        * **VerticalCorrector**


## Class Properties

| Property | Value |
| --- | --- |
| Class URI | [laura:VerticalCorrector](https://w3id.org/laura/VerticalCorrector) |


## Slots

| Name | Cardinality and Range | Description | Inheritance |
| ---  | --- | --- | --- |
| [magnetic](magnetic.md) | 0..1 <br/> [CorrectorMagnet](CorrectorMagnet.md) | Magnetic field parameters | [Magnet](Magnet.md) |
| [degauss](degauss.md) | 0..1 <br/> [DegaussableElement](DegaussableElement.md) | Degaussing-cycle parameters | [Magnet](Magnet.md) |
| [physical](physical.md) | 0..1 <br/> [PhysicalElement](PhysicalElement.md) | Position, rotation, and length data | [PhysicalAcceleratorElement](PhysicalAcceleratorElement.md) |
| [simulation](simulation.md) | 0..1 <br/> [MagnetSimulationElement](MagnetSimulationElement.md) | Simulation / tracking attributes | [StandardElement](StandardElement.md) |
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
| self | laura:VerticalCorrector |
| native | laura:VerticalCorrector |






## LinkML Source

<!-- TODO: investigate https://stackoverflow.com/questions/37606292/how-to-create-tabbed-code-blocks-in-mkdocs-or-sphinx -->

### Direct

<details>
```yaml
name: VerticalCorrector
description: Vertical steering corrector.
from_schema: https://w3id.org/laura/schema
is_a: Dipole
slot_usage:
  magnetic:
    name: magnetic
    range: Corrector_Magnet
  hardware_type:
    name: hardware_type
    ifabsent: Vertical_Corrector
    equals_string: Vertical_Corrector
class_uri: laura:VerticalCorrector

```
</details>

### Induced

<details>
```yaml
name: VerticalCorrector
description: Vertical steering corrector.
from_schema: https://w3id.org/laura/schema
is_a: Dipole
slot_usage:
  magnetic:
    name: magnetic
    range: Corrector_Magnet
  hardware_type:
    name: hardware_type
    ifabsent: Vertical_Corrector
    equals_string: Vertical_Corrector
attributes:
  magnetic:
    name: magnetic
    description: Magnetic field parameters.
    in_subset:
    - magnetic_properties
    from_schema: https://w3id.org/laura/schema/magnetic
    rank: 1000
    owner: VerticalCorrector
    domain_of:
    - Magnet
    range: Corrector_Magnet
  degauss:
    name: degauss
    description: Degaussing-cycle parameters.
    from_schema: https://w3id.org/laura/schema/magnetic
    rank: 1000
    owner: VerticalCorrector
    domain_of:
    - Magnet
    range: DegaussableElement
  physical:
    name: physical
    description: Position, rotation, and length data.
    in_subset:
    - physical_properties
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    owner: VerticalCorrector
    domain_of:
    - PhysicalAcceleratorElement
    range: PhysicalElement
  simulation:
    name: simulation
    description: Simulation / tracking attributes.
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    owner: VerticalCorrector
    domain_of:
    - StandardElement
    range: MagnetSimulationElement
  electrical:
    name: electrical
    description: Power-supply electrical limits.
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    owner: VerticalCorrector
    domain_of:
    - StandardElement
    range: ElectricalElement
  manufacturer:
    name: manufacturer
    description: Manufacturer and serial-number data.
    from_schema: https://w3id.org/laura/schema
    owner: VerticalCorrector
    domain_of:
    - ManufacturerElement
    - StandardElement
    range: ManufacturerElement
  controls:
    name: controls
    description: Control-system process-variable definitions.
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    owner: VerticalCorrector
    domain_of:
    - StandardElement
    range: ControlsInformation
  reference:
    name: reference
    description: Links to design drawings and files.
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    owner: VerticalCorrector
    domain_of:
    - StandardElement
    range: ReferenceElement
  name:
    name: name
    description: Unique element name within the machine.
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    identifier: true
    owner: VerticalCorrector
    domain_of:
    - AcceleratorElement
    - ControlVariable
    - FunctionalDefinition
    - SectionLattice
    - MachineLayout
    range: string
    required: true
  hardware_class:
    name: hardware_class
    description: Functional category (e.g., ``Magnet``, ``Diagnostic``).
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    owner: VerticalCorrector
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
    ifabsent: Vertical_Corrector
    owner: VerticalCorrector
    domain_of:
    - AcceleratorElement
    range: string
    equals_string: Vertical_Corrector
  hardware_model:
    name: hardware_model
    description: Model or variant name within the hardware type (e.g., ``Generic``,
      ``TESLA``).
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    ifabsent: string(Generic)
    owner: VerticalCorrector
    domain_of:
    - AcceleratorElement
    range: string
  machine_area:
    name: machine_area
    description: Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    owner: VerticalCorrector
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
    owner: VerticalCorrector
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
    owner: VerticalCorrector
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
    owner: VerticalCorrector
    domain_of:
    - AcceleratorElement
    range: string
  inputs:
    name: inputs
    description: Signal types this element consumes (e.g. ``[current, voltage]``).
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    owner: VerticalCorrector
    domain_of:
    - AcceleratorElement
    range: IOTypeEnum
    multivalued: true
  outputs:
    name: outputs
    description: Signal types this element produces (e.g. ``[power, phase]``).
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    owner: VerticalCorrector
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
    owner: VerticalCorrector
    domain_of:
    - AcceleratorElement
    range: AcceleratorElement
    multivalued: true
  downstream:
    name: downstream
    description: Names of elements this one feeds; the inverse of ``upstream``.
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    owner: VerticalCorrector
    domain_of:
    - AcceleratorElement
    range: AcceleratorElement
    multivalued: true
class_uri: laura:VerticalCorrector

```
</details></div>