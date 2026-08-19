# Class: Diagnostic 


_Base class for all beam-diagnostic instruments._



<div data-search-exclude markdown="1">



URI: [laura:Diagnostic](https://w3id.org/laura/Diagnostic)





```mermaid
 classDiagram
    class Diagnostic
    click Diagnostic href "../Diagnostic/"
      PhysicalAcceleratorElement <|-- Diagnostic
        click PhysicalAcceleratorElement href "../PhysicalAcceleratorElement/"
      

      Diagnostic <|-- BeamPositionMonitor
        click BeamPositionMonitor href "../BeamPositionMonitor/"
      Diagnostic <|-- BeamArrivalMonitor
        click BeamArrivalMonitor href "../BeamArrivalMonitor/"
      Diagnostic <|-- BunchLengthMonitor
        click BunchLengthMonitor href "../BunchLengthMonitor/"
      Diagnostic <|-- Camera
        click Camera href "../Camera/"
      Diagnostic <|-- Screen
        click Screen href "../Screen/"
      Diagnostic <|-- ChargeDiagnostic
        click ChargeDiagnostic href "../ChargeDiagnostic/"
      Diagnostic <|-- PhotonMonitor
        click PhotonMonitor href "../PhotonMonitor/"
      

      Diagnostic : alias
        
      Diagnostic : aperture
        
          
    
        
        
        Diagnostic --> "0..1" ApertureElement : aperture
        click ApertureElement href "../ApertureElement/"
    

        
      Diagnostic : controls
        
          
    
        
        
        Diagnostic --> "0..1" ControlsInformation : controls
        click ControlsInformation href "../ControlsInformation/"
    

        
      Diagnostic : diagnostic
        
          
    
        
        
        Diagnostic --> "0..1" DiagnosticElement : diagnostic
        click DiagnosticElement href "../DiagnosticElement/"
    

        
      Diagnostic : downstream
        
          
    
        
        
        Diagnostic --> "*" AcceleratorElement : downstream
        click AcceleratorElement href "../AcceleratorElement/"
    

        
      Diagnostic : electrical
        
          
    
        
        
        Diagnostic --> "0..1" ElectricalElement : electrical
        click ElectricalElement href "../ElectricalElement/"
    

        
      Diagnostic : hardware_class
        
          
    
        
        
        Diagnostic --> "1" HardwareClassEnum : hardware_class
        click HardwareClassEnum href "../HardwareClassEnum/"
    

        
      Diagnostic : hardware_model
        
      Diagnostic : hardware_type
        
      Diagnostic : inputs
        
          
    
        
        
        Diagnostic --> "*" IOTypeEnum : inputs
        click IOTypeEnum href "../IOTypeEnum/"
    

        
      Diagnostic : machine_area
        
      Diagnostic : manufacturer
        
          
    
        
        
        Diagnostic --> "0..1" ManufacturerElement : manufacturer
        click ManufacturerElement href "../ManufacturerElement/"
    

        
      Diagnostic : name
        
      Diagnostic : outputs
        
          
    
        
        
        Diagnostic --> "*" IOTypeEnum : outputs
        click IOTypeEnum href "../IOTypeEnum/"
    

        
      Diagnostic : physical
        
          
    
        
        
        Diagnostic --> "0..1" PhysicalElement : physical
        click PhysicalElement href "../PhysicalElement/"
    

        
      Diagnostic : reference
        
          
    
        
        
        Diagnostic --> "0..1" ReferenceElement : reference
        click ReferenceElement href "../ReferenceElement/"
    

        
      Diagnostic : simulation
        
          
    
        
        
        Diagnostic --> "0..1" DiagnosticSimulationElement : simulation
        click DiagnosticSimulationElement href "../DiagnosticSimulationElement/"
    

        
      Diagnostic : subelement
        
      Diagnostic : upstream
        
          
    
        
        
        Diagnostic --> "*" AcceleratorElement : upstream
        click AcceleratorElement href "../AcceleratorElement/"
    

        
      Diagnostic : virtual_name
        
      
```





## Inheritance
* [AcceleratorElement](AcceleratorElement.md)
    * [StandardElement](StandardElement.md)
        * [Element](Element.md)
            * [PhysicalAcceleratorElement](PhysicalAcceleratorElement.md)
                * **Diagnostic**
                    * [BeamPositionMonitor](BeamPositionMonitor.md)
                    * [BeamArrivalMonitor](BeamArrivalMonitor.md)
                    * [BunchLengthMonitor](BunchLengthMonitor.md)
                    * [Camera](Camera.md)
                    * [Screen](Screen.md)
                    * [ChargeDiagnostic](ChargeDiagnostic.md)
                    * [PhotonMonitor](PhotonMonitor.md)


## Class Properties

| Property | Value |
| --- | --- |
| Class URI | [laura:Diagnostic](https://w3id.org/laura/Diagnostic) |


## Slots

| Name | Cardinality and Range | Description | Inheritance |
| ---  | --- | --- | --- |
| [diagnostic](diagnostic.md) | 0..1 <br/> [DiagnosticElement](DiagnosticElement.md) | Instrument-specific diagnostic parameters | direct |
| [physical](physical.md) | 0..1 <br/> [PhysicalElement](PhysicalElement.md) | Position, rotation, and length data | [PhysicalAcceleratorElement](PhysicalAcceleratorElement.md) |
| [aperture](aperture.md) | 0..1 <br/> [ApertureElement](ApertureElement.md) | Aperture of the element | [PhysicalAcceleratorElement](PhysicalAcceleratorElement.md) |
| [simulation](simulation.md) | 0..1 <br/> [DiagnosticSimulationElement](DiagnosticSimulationElement.md) | Simulation / tracking attributes | [StandardElement](StandardElement.md) |
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
| self | laura:Diagnostic |
| native | laura:Diagnostic |






## LinkML Source

<!-- TODO: investigate https://stackoverflow.com/questions/37606292/how-to-create-tabbed-code-blocks-in-mkdocs-or-sphinx -->

### Direct

<details>
```yaml
name: Diagnostic
description: Base class for all beam-diagnostic instruments.
from_schema: https://w3id.org/laura/schema
is_a: PhysicalAcceleratorElement
slot_usage:
  simulation:
    name: simulation
    range: DiagnosticSimulationElement
attributes:
  diagnostic:
    name: diagnostic
    description: Instrument-specific diagnostic parameters.
    in_subset:
    - diagnostic_properties
    from_schema: https://w3id.org/laura/schema/diagnostics
    rank: 1000
    domain_of:
    - Diagnostic
    - BeamPositionMonitor
    - BeamArrivalMonitor
    - BunchLengthMonitor
    - Camera
    - Screen
    - ChargeDiagnostic
    - PhotonMonitor
    range: DiagnosticElement
class_uri: laura:Diagnostic

```
</details>

### Induced

<details>
```yaml
name: Diagnostic
description: Base class for all beam-diagnostic instruments.
from_schema: https://w3id.org/laura/schema
is_a: PhysicalAcceleratorElement
slot_usage:
  simulation:
    name: simulation
    range: DiagnosticSimulationElement
attributes:
  diagnostic:
    name: diagnostic
    description: Instrument-specific diagnostic parameters.
    in_subset:
    - diagnostic_properties
    from_schema: https://w3id.org/laura/schema/diagnostics
    rank: 1000
    owner: Diagnostic
    domain_of:
    - Diagnostic
    - BeamPositionMonitor
    - BeamArrivalMonitor
    - BunchLengthMonitor
    - Camera
    - Screen
    - ChargeDiagnostic
    - PhotonMonitor
    range: DiagnosticElement
  physical:
    name: physical
    description: Position, rotation, and length data.
    in_subset:
    - physical_properties
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    owner: Diagnostic
    domain_of:
    - PhysicalAcceleratorElement
    range: PhysicalElement
  aperture:
    name: aperture
    description: Aperture of the element.
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    owner: Diagnostic
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
    owner: Diagnostic
    domain_of:
    - StandardElement
    range: DiagnosticSimulationElement
  electrical:
    name: electrical
    description: Power-supply electrical limits.
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    owner: Diagnostic
    domain_of:
    - StandardElement
    range: ElectricalElement
  manufacturer:
    name: manufacturer
    description: Manufacturer and serial-number data.
    from_schema: https://w3id.org/laura/schema
    owner: Diagnostic
    domain_of:
    - ManufacturerElement
    - StandardElement
    range: ManufacturerElement
  controls:
    name: controls
    description: Control-system process-variable definitions.
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    owner: Diagnostic
    domain_of:
    - StandardElement
    range: ControlsInformation
  reference:
    name: reference
    description: Links to design drawings and files.
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    owner: Diagnostic
    domain_of:
    - StandardElement
    range: ReferenceElement
  name:
    name: name
    description: Unique element name within the machine.
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    identifier: true
    owner: Diagnostic
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
    owner: Diagnostic
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
    owner: Diagnostic
    domain_of:
    - AcceleratorElement
    range: string
  hardware_model:
    name: hardware_model
    description: Model or variant name within the hardware type (e.g., ``Generic``,
      ``TESLA``).
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    ifabsent: string(Generic)
    owner: Diagnostic
    domain_of:
    - AcceleratorElement
    range: string
  machine_area:
    name: machine_area
    description: Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    owner: Diagnostic
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
    owner: Diagnostic
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
    owner: Diagnostic
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
    owner: Diagnostic
    domain_of:
    - AcceleratorElement
    range: string
  inputs:
    name: inputs
    description: Signal types this element consumes (e.g. ``[current, voltage]``).
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    owner: Diagnostic
    domain_of:
    - AcceleratorElement
    range: IOTypeEnum
    multivalued: true
  outputs:
    name: outputs
    description: Signal types this element produces (e.g. ``[power, phase]``).
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    owner: Diagnostic
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
    owner: Diagnostic
    domain_of:
    - AcceleratorElement
    range: AcceleratorElement
    multivalued: true
  downstream:
    name: downstream
    description: Names of elements this one feeds; the inverse of ``upstream``.
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    owner: Diagnostic
    domain_of:
    - AcceleratorElement
    range: AcceleratorElement
    multivalued: true
class_uri: laura:Diagnostic

```
</details></div>