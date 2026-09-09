# Class: CombinedCorrector 


_Combined horizontal/vertical steering corrector, naming the two single-plane correctors it stands in for._



<div data-search-exclude markdown="1">



URI: [laura:CombinedCorrector](https://w3id.org/laura/CombinedCorrector)





```mermaid
 classDiagram
    class CombinedCorrector
    click CombinedCorrector href "../CombinedCorrector/"
      Dipole <|-- CombinedCorrector
        click Dipole href "../Dipole/"
      
      CombinedCorrector : alias
        
      CombinedCorrector : aperture
        
          
    
        
        
        CombinedCorrector --> "0..1" ApertureElement : aperture
        click ApertureElement href "../ApertureElement/"
    

        
      CombinedCorrector : controls
        
          
    
        
        
        CombinedCorrector --> "0..1" ControlsInformation : controls
        click ControlsInformation href "../ControlsInformation/"
    

        
      CombinedCorrector : degauss
        
          
    
        
        
        CombinedCorrector --> "0..1" DegaussableElement : degauss
        click DegaussableElement href "../DegaussableElement/"
    

        
      CombinedCorrector : downstream
        
          
    
        
        
        CombinedCorrector --> "*" AcceleratorElement : downstream
        click AcceleratorElement href "../AcceleratorElement/"
    

        
      CombinedCorrector : electrical
        
          
    
        
        
        CombinedCorrector --> "0..1" ElectricalElement : electrical
        click ElectricalElement href "../ElectricalElement/"
    

        
      CombinedCorrector : hardware_class
        
          
    
        
        
        CombinedCorrector --> "1" HardwareClassEnum : hardware_class
        click HardwareClassEnum href "../HardwareClassEnum/"
    

        
      CombinedCorrector : hardware_model
        
      CombinedCorrector : hardware_type
        
      CombinedCorrector : Horizontal_Corrector
        
      CombinedCorrector : inputs
        
          
    
        
        
        CombinedCorrector --> "*" IOTypeEnum : inputs
        click IOTypeEnum href "../IOTypeEnum/"
    

        
      CombinedCorrector : machine_area
        
      CombinedCorrector : magnetic
        
          
    
        
        
        CombinedCorrector --> "0..1" CorrectorMagnet : magnetic
        click CorrectorMagnet href "../CorrectorMagnet/"
    

        
      CombinedCorrector : manufacturer
        
          
    
        
        
        CombinedCorrector --> "0..1" ManufacturerElement : manufacturer
        click ManufacturerElement href "../ManufacturerElement/"
    

        
      CombinedCorrector : name
        
      CombinedCorrector : outputs
        
          
    
        
        
        CombinedCorrector --> "*" IOTypeEnum : outputs
        click IOTypeEnum href "../IOTypeEnum/"
    

        
      CombinedCorrector : physical
        
          
    
        
        
        CombinedCorrector --> "0..1" PhysicalElement : physical
        click PhysicalElement href "../PhysicalElement/"
    

        
      CombinedCorrector : reference
        
          
    
        
        
        CombinedCorrector --> "0..1" ReferenceElement : reference
        click ReferenceElement href "../ReferenceElement/"
    

        
      CombinedCorrector : simulation
        
          
    
        
        
        CombinedCorrector --> "0..1" MagnetSimulationElement : simulation
        click MagnetSimulationElement href "../MagnetSimulationElement/"
    

        
      CombinedCorrector : subelement
        
      CombinedCorrector : upstream
        
          
    
        
        
        CombinedCorrector --> "*" AcceleratorElement : upstream
        click AcceleratorElement href "../AcceleratorElement/"
    

        
      CombinedCorrector : Vertical_Corrector
        
      CombinedCorrector : virtual_name
        
      
```





## Inheritance
* [AcceleratorElement](AcceleratorElement.md)
    * [StandardElement](StandardElement.md)
        * [Element](Element.md)
            * [PhysicalAcceleratorElement](PhysicalAcceleratorElement.md)
                * [Magnet](Magnet.md)
                    * [Dipole](Dipole.md)
                        * **CombinedCorrector**


## Class Properties

| Property | Value |
| --- | --- |
| Class URI | [laura:CombinedCorrector](https://w3id.org/laura/CombinedCorrector) |


## Slots

| Name | Cardinality and Range | Description | Inheritance |
| ---  | --- | --- | --- |
| [Horizontal_Corrector](Horizontal_Corrector.md) | 0..1 <br/> [String](String.md) | Name of the horizontal-plane corrector element | direct |
| [Vertical_Corrector](Vertical_Corrector.md) | 0..1 <br/> [String](String.md) | Name of the vertical-plane corrector element | direct |
| [magnetic](magnetic.md) | 0..1 <br/> [CorrectorMagnet](CorrectorMagnet.md) | Magnetic field parameters | [Magnet](Magnet.md) |
| [degauss](degauss.md) | 0..1 <br/> [DegaussableElement](DegaussableElement.md) | Degaussing-cycle parameters | [Magnet](Magnet.md) |
| [physical](physical.md) | 0..1 <br/> [PhysicalElement](PhysicalElement.md) | Position, rotation, and length data | [PhysicalAcceleratorElement](PhysicalAcceleratorElement.md) |
| [aperture](aperture.md) | 0..1 <br/> [ApertureElement](ApertureElement.md) | Aperture of the element | [PhysicalAcceleratorElement](PhysicalAcceleratorElement.md) |
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
| self | laura:CombinedCorrector |
| native | laura:CombinedCorrector |






## LinkML Source

<!-- TODO: investigate https://stackoverflow.com/questions/37606292/how-to-create-tabbed-code-blocks-in-mkdocs-or-sphinx -->

### Direct

<details>
```yaml
name: CombinedCorrector
description: Combined horizontal/vertical steering corrector, naming the two single-plane
  correctors it stands in for.
from_schema: https://w3id.org/laura/schema
is_a: Dipole
slot_usage:
  magnetic:
    name: magnetic
    range: Corrector_Magnet
  hardware_type:
    name: hardware_type
    ifabsent: Combined_Corrector
    equals_string: Combined_Corrector
attributes:
  Horizontal_Corrector:
    name: Horizontal_Corrector
    description: Name of the horizontal-plane corrector element.
    from_schema: https://w3id.org/laura/schema/magnetic
    rank: 1000
    domain_of:
    - CombinedCorrector
    range: string
  Vertical_Corrector:
    name: Vertical_Corrector
    description: Name of the vertical-plane corrector element.
    from_schema: https://w3id.org/laura/schema/magnetic
    rank: 1000
    domain_of:
    - CombinedCorrector
    range: string
class_uri: laura:CombinedCorrector

```
</details>

### Induced

<details>
```yaml
name: CombinedCorrector
description: Combined horizontal/vertical steering corrector, naming the two single-plane
  correctors it stands in for.
from_schema: https://w3id.org/laura/schema
is_a: Dipole
slot_usage:
  magnetic:
    name: magnetic
    range: Corrector_Magnet
  hardware_type:
    name: hardware_type
    ifabsent: Combined_Corrector
    equals_string: Combined_Corrector
attributes:
  Horizontal_Corrector:
    name: Horizontal_Corrector
    description: Name of the horizontal-plane corrector element.
    from_schema: https://w3id.org/laura/schema/magnetic
    rank: 1000
    owner: CombinedCorrector
    domain_of:
    - CombinedCorrector
    range: string
  Vertical_Corrector:
    name: Vertical_Corrector
    description: Name of the vertical-plane corrector element.
    from_schema: https://w3id.org/laura/schema/magnetic
    rank: 1000
    owner: CombinedCorrector
    domain_of:
    - CombinedCorrector
    range: string
  magnetic:
    name: magnetic
    description: Magnetic field parameters.
    in_subset:
    - magnetic_properties
    from_schema: https://w3id.org/laura/schema/magnetic
    rank: 1000
    owner: CombinedCorrector
    domain_of:
    - Magnet
    range: Corrector_Magnet
  degauss:
    name: degauss
    description: Degaussing-cycle parameters.
    from_schema: https://w3id.org/laura/schema/magnetic
    rank: 1000
    owner: CombinedCorrector
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
    owner: CombinedCorrector
    domain_of:
    - PhysicalAcceleratorElement
    range: PhysicalElement
  aperture:
    name: aperture
    description: Aperture of the element.
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    owner: CombinedCorrector
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
    owner: CombinedCorrector
    domain_of:
    - StandardElement
    range: MagnetSimulationElement
  electrical:
    name: electrical
    description: Power-supply electrical limits.
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    owner: CombinedCorrector
    domain_of:
    - StandardElement
    range: ElectricalElement
  manufacturer:
    name: manufacturer
    description: Manufacturer and serial-number data.
    from_schema: https://w3id.org/laura/schema
    owner: CombinedCorrector
    domain_of:
    - ManufacturerElement
    - StandardElement
    range: ManufacturerElement
  controls:
    name: controls
    description: Control-system process-variable definitions.
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    owner: CombinedCorrector
    domain_of:
    - StandardElement
    range: ControlsInformation
  reference:
    name: reference
    description: Links to design drawings and files.
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    owner: CombinedCorrector
    domain_of:
    - StandardElement
    range: ReferenceElement
  name:
    name: name
    description: Unique element name within the machine.
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    identifier: true
    owner: CombinedCorrector
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
    owner: CombinedCorrector
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
    ifabsent: Combined_Corrector
    owner: CombinedCorrector
    domain_of:
    - AcceleratorElement
    range: string
    equals_string: Combined_Corrector
  hardware_model:
    name: hardware_model
    description: Model or variant name within the hardware type (e.g., ``Generic``,
      ``TESLA``).
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    ifabsent: string(Generic)
    owner: CombinedCorrector
    domain_of:
    - AcceleratorElement
    range: string
  machine_area:
    name: machine_area
    description: Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    owner: CombinedCorrector
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
    owner: CombinedCorrector
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
    owner: CombinedCorrector
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
    owner: CombinedCorrector
    domain_of:
    - AcceleratorElement
    range: string
  inputs:
    name: inputs
    description: Signal types this element consumes (e.g. ``[current, voltage]``).
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    owner: CombinedCorrector
    domain_of:
    - AcceleratorElement
    range: IOTypeEnum
    multivalued: true
  outputs:
    name: outputs
    description: Signal types this element produces (e.g. ``[power, phase]``).
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    owner: CombinedCorrector
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
    owner: CombinedCorrector
    domain_of:
    - AcceleratorElement
    range: AcceleratorElement
    multivalued: true
  downstream:
    name: downstream
    description: Names of elements this one feeds; the inverse of ``upstream``.
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    owner: CombinedCorrector
    domain_of:
    - AcceleratorElement
    range: AcceleratorElement
    multivalued: true
class_uri: laura:CombinedCorrector

```
</details></div>