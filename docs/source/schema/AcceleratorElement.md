# Class: AcceleratorElement 


_Root base class for all LAURA accelerator elements.  Every lattice element is an instance of a concrete subclass identified by ``hardware_type``._



<div data-search-exclude markdown="1">



URI: [laura:AcceleratorElement](https://w3id.org/laura/AcceleratorElement)





```mermaid
 classDiagram
    class AcceleratorElement
    click AcceleratorElement href "../AcceleratorElement/"
      AcceleratorElement <|-- StandardElement
        click StandardElement href "../StandardElement/"
      
      AcceleratorElement : alias
        
      AcceleratorElement : downstream
        
          
    
        
        
        AcceleratorElement --> "*" AcceleratorElement : downstream
        click AcceleratorElement href "../AcceleratorElement/"
    

        
      AcceleratorElement : hardware_class
        
          
    
        
        
        AcceleratorElement --> "1" HardwareClassEnum : hardware_class
        click HardwareClassEnum href "../HardwareClassEnum/"
    

        
      AcceleratorElement : hardware_model
        
      AcceleratorElement : hardware_type
        
      AcceleratorElement : inputs
        
          
    
        
        
        AcceleratorElement --> "*" IOTypeEnum : inputs
        click IOTypeEnum href "../IOTypeEnum/"
    

        
      AcceleratorElement : machine_area
        
      AcceleratorElement : name
        
      AcceleratorElement : outputs
        
          
    
        
        
        AcceleratorElement --> "*" IOTypeEnum : outputs
        click IOTypeEnum href "../IOTypeEnum/"
    

        
      AcceleratorElement : subelement
        
      AcceleratorElement : upstream
        
          
    
        
        
        AcceleratorElement --> "*" AcceleratorElement : upstream
        click AcceleratorElement href "../AcceleratorElement/"
    

        
      AcceleratorElement : virtual_name
        
      
```





## Inheritance
* **AcceleratorElement**
    * [StandardElement](StandardElement.md)


## Class Properties

| Property | Value |
| --- | --- |
| Class URI | [laura:AcceleratorElement](https://w3id.org/laura/AcceleratorElement) |
| Tree Root | Yes |


## Slots

| Name | Cardinality and Range | Description | Inheritance |
| ---  | --- | --- | --- |
| [name](name.md) | 1 <br/> [String](String.md) | Unique element name within the machine | direct |
| [hardware_class](hardware_class.md) | 1 <br/> [HardwareClassEnum](HardwareClassEnum.md) | Functional category (e | direct |
| [hardware_type](hardware_type.md) | 0..1 <br/> [String](String.md) | Python class name used for ELEMENT_REGISTRY dispatch | direct |
| [hardware_model](hardware_model.md) | 0..1 <br/> [String](String.md) | Model or variant name within the hardware type (e | direct |
| [machine_area](machine_area.md) | 0..1 <br/> [String](String.md) | Machine area label grouping related elements (e | direct |
| [virtual_name](virtual_name.md) | 0..1 <br/> [String](String.md) | Alternative internal name used by the control system when the physical name i... | direct |
| [alias](alias.md) | * <br/> [String](String.md) | Human-readable aliases for the element | direct |
| [subelement](subelement.md) | 0..1 <br/> [String](String.md) | If set, this element is a logical sub-component of the named parent element | direct |
| [inputs](inputs.md) | * <br/> [IOTypeEnum](IOTypeEnum.md) | Signal types this element consumes (e | direct |
| [outputs](outputs.md) | * <br/> [IOTypeEnum](IOTypeEnum.md) | Signal types this element produces (e | direct |
| [upstream](upstream.md) | * <br/> [AcceleratorElement](AcceleratorElement.md) | Names of elements feeding this one, whose ``outputs`` supply its ``inputs`` | direct |
| [downstream](downstream.md) | * <br/> [AcceleratorElement](AcceleratorElement.md) | Names of elements this one feeds; the inverse of ``upstream`` | direct |





## Usages

| used by | used in | type | used |
| ---  | --- | --- | --- |
| [AcceleratorElement](AcceleratorElement.md) | [upstream](upstream.md) | range | [AcceleratorElement](AcceleratorElement.md) |
| [AcceleratorElement](AcceleratorElement.md) | [downstream](downstream.md) | range | [AcceleratorElement](AcceleratorElement.md) |
| [StandardElement](StandardElement.md) | [upstream](upstream.md) | range | [AcceleratorElement](AcceleratorElement.md) |
| [StandardElement](StandardElement.md) | [downstream](downstream.md) | range | [AcceleratorElement](AcceleratorElement.md) |
| [Element](Element.md) | [upstream](upstream.md) | range | [AcceleratorElement](AcceleratorElement.md) |
| [Element](Element.md) | [downstream](downstream.md) | range | [AcceleratorElement](AcceleratorElement.md) |
| [PhysicalAcceleratorElement](PhysicalAcceleratorElement.md) | [upstream](upstream.md) | range | [AcceleratorElement](AcceleratorElement.md) |
| [PhysicalAcceleratorElement](PhysicalAcceleratorElement.md) | [downstream](downstream.md) | range | [AcceleratorElement](AcceleratorElement.md) |
| [TwissMatch](TwissMatch.md) | [upstream](upstream.md) | range | [AcceleratorElement](AcceleratorElement.md) |
| [TwissMatch](TwissMatch.md) | [downstream](downstream.md) | range | [AcceleratorElement](AcceleratorElement.md) |
| [MatrixTransform](MatrixTransform.md) | [upstream](upstream.md) | range | [AcceleratorElement](AcceleratorElement.md) |
| [MatrixTransform](MatrixTransform.md) | [downstream](downstream.md) | range | [AcceleratorElement](AcceleratorElement.md) |
| [ElectrostaticSeparator](ElectrostaticSeparator.md) | [upstream](upstream.md) | range | [AcceleratorElement](AcceleratorElement.md) |
| [ElectrostaticSeparator](ElectrostaticSeparator.md) | [downstream](downstream.md) | range | [AcceleratorElement](AcceleratorElement.md) |
| [ACDipole](ACDipole.md) | [upstream](upstream.md) | range | [AcceleratorElement](AcceleratorElement.md) |
| [ACDipole](ACDipole.md) | [downstream](downstream.md) | range | [AcceleratorElement](AcceleratorElement.md) |
| [HorizontalACDipole](HorizontalACDipole.md) | [upstream](upstream.md) | range | [AcceleratorElement](AcceleratorElement.md) |
| [HorizontalACDipole](HorizontalACDipole.md) | [downstream](downstream.md) | range | [AcceleratorElement](AcceleratorElement.md) |
| [VerticalACDipole](VerticalACDipole.md) | [upstream](upstream.md) | range | [AcceleratorElement](AcceleratorElement.md) |
| [VerticalACDipole](VerticalACDipole.md) | [downstream](downstream.md) | range | [AcceleratorElement](AcceleratorElement.md) |
| [Wire](Wire.md) | [upstream](upstream.md) | range | [AcceleratorElement](AcceleratorElement.md) |
| [Wire](Wire.md) | [downstream](downstream.md) | range | [AcceleratorElement](AcceleratorElement.md) |
| [BeamBeam](BeamBeam.md) | [upstream](upstream.md) | range | [AcceleratorElement](AcceleratorElement.md) |
| [BeamBeam](BeamBeam.md) | [downstream](downstream.md) | range | [AcceleratorElement](AcceleratorElement.md) |
| [RFMultipole](RFMultipole.md) | [upstream](upstream.md) | range | [AcceleratorElement](AcceleratorElement.md) |
| [RFMultipole](RFMultipole.md) | [downstream](downstream.md) | range | [AcceleratorElement](AcceleratorElement.md) |
| [Stage](Stage.md) | [upstream](upstream.md) | range | [AcceleratorElement](AcceleratorElement.md) |
| [Stage](Stage.md) | [downstream](downstream.md) | range | [AcceleratorElement](AcceleratorElement.md) |
| [VacuumGauge](VacuumGauge.md) | [upstream](upstream.md) | range | [AcceleratorElement](AcceleratorElement.md) |
| [VacuumGauge](VacuumGauge.md) | [downstream](downstream.md) | range | [AcceleratorElement](AcceleratorElement.md) |
| [Laser](Laser.md) | [upstream](upstream.md) | range | [AcceleratorElement](AcceleratorElement.md) |
| [Laser](Laser.md) | [downstream](downstream.md) | range | [AcceleratorElement](AcceleratorElement.md) |
| [Shutter](Shutter.md) | [upstream](upstream.md) | range | [AcceleratorElement](AcceleratorElement.md) |
| [Shutter](Shutter.md) | [downstream](downstream.md) | range | [AcceleratorElement](AcceleratorElement.md) |
| [Valve](Valve.md) | [upstream](upstream.md) | range | [AcceleratorElement](AcceleratorElement.md) |
| [Valve](Valve.md) | [downstream](downstream.md) | range | [AcceleratorElement](AcceleratorElement.md) |
| [Marker](Marker.md) | [upstream](upstream.md) | range | [AcceleratorElement](AcceleratorElement.md) |
| [Marker](Marker.md) | [downstream](downstream.md) | range | [AcceleratorElement](AcceleratorElement.md) |
| [Aperture](Aperture.md) | [upstream](upstream.md) | range | [AcceleratorElement](AcceleratorElement.md) |
| [Aperture](Aperture.md) | [downstream](downstream.md) | range | [AcceleratorElement](AcceleratorElement.md) |
| [Collimator](Collimator.md) | [upstream](upstream.md) | range | [AcceleratorElement](AcceleratorElement.md) |
| [Collimator](Collimator.md) | [downstream](downstream.md) | range | [AcceleratorElement](AcceleratorElement.md) |
| [Drift](Drift.md) | [upstream](upstream.md) | range | [AcceleratorElement](AcceleratorElement.md) |
| [Drift](Drift.md) | [downstream](downstream.md) | range | [AcceleratorElement](AcceleratorElement.md) |
| [Lighting](Lighting.md) | [upstream](upstream.md) | range | [AcceleratorElement](AcceleratorElement.md) |
| [Lighting](Lighting.md) | [downstream](downstream.md) | range | [AcceleratorElement](AcceleratorElement.md) |
| [PowerSupply](PowerSupply.md) | [upstream](upstream.md) | range | [AcceleratorElement](AcceleratorElement.md) |
| [PowerSupply](PowerSupply.md) | [downstream](downstream.md) | range | [AcceleratorElement](AcceleratorElement.md) |
| [MachineModel](MachineModel.md) | [elements](elements.md) | range | [AcceleratorElement](AcceleratorElement.md) |
| [Magnet](Magnet.md) | [upstream](upstream.md) | range | [AcceleratorElement](AcceleratorElement.md) |
| [Magnet](Magnet.md) | [downstream](downstream.md) | range | [AcceleratorElement](AcceleratorElement.md) |
| [RFCavity](RFCavity.md) | [upstream](upstream.md) | range | [AcceleratorElement](AcceleratorElement.md) |
| [RFCavity](RFCavity.md) | [downstream](downstream.md) | range | [AcceleratorElement](AcceleratorElement.md) |
| [RFDeflectingCavity](RFDeflectingCavity.md) | [upstream](upstream.md) | range | [AcceleratorElement](AcceleratorElement.md) |
| [RFDeflectingCavity](RFDeflectingCavity.md) | [downstream](downstream.md) | range | [AcceleratorElement](AcceleratorElement.md) |
| [CrabCavity](CrabCavity.md) | [upstream](upstream.md) | range | [AcceleratorElement](AcceleratorElement.md) |
| [CrabCavity](CrabCavity.md) | [downstream](downstream.md) | range | [AcceleratorElement](AcceleratorElement.md) |
| [Wakefield](Wakefield.md) | [upstream](upstream.md) | range | [AcceleratorElement](AcceleratorElement.md) |
| [Wakefield](Wakefield.md) | [downstream](downstream.md) | range | [AcceleratorElement](AcceleratorElement.md) |
| [LowLevelRF](LowLevelRF.md) | [upstream](upstream.md) | range | [AcceleratorElement](AcceleratorElement.md) |
| [LowLevelRF](LowLevelRF.md) | [downstream](downstream.md) | range | [AcceleratorElement](AcceleratorElement.md) |
| [RFModulator](RFModulator.md) | [upstream](upstream.md) | range | [AcceleratorElement](AcceleratorElement.md) |
| [RFModulator](RFModulator.md) | [downstream](downstream.md) | range | [AcceleratorElement](AcceleratorElement.md) |
| [RFProtection](RFProtection.md) | [upstream](upstream.md) | range | [AcceleratorElement](AcceleratorElement.md) |
| [RFProtection](RFProtection.md) | [downstream](downstream.md) | range | [AcceleratorElement](AcceleratorElement.md) |
| [RFHeartbeat](RFHeartbeat.md) | [upstream](upstream.md) | range | [AcceleratorElement](AcceleratorElement.md) |
| [RFHeartbeat](RFHeartbeat.md) | [downstream](downstream.md) | range | [AcceleratorElement](AcceleratorElement.md) |
| [PID](PID.md) | [upstream](upstream.md) | range | [AcceleratorElement](AcceleratorElement.md) |
| [PID](PID.md) | [downstream](downstream.md) | range | [AcceleratorElement](AcceleratorElement.md) |
| [Diagnostic](Diagnostic.md) | [upstream](upstream.md) | range | [AcceleratorElement](AcceleratorElement.md) |
| [Diagnostic](Diagnostic.md) | [downstream](downstream.md) | range | [AcceleratorElement](AcceleratorElement.md) |
| [BeamPositionMonitor](BeamPositionMonitor.md) | [upstream](upstream.md) | range | [AcceleratorElement](AcceleratorElement.md) |
| [BeamPositionMonitor](BeamPositionMonitor.md) | [downstream](downstream.md) | range | [AcceleratorElement](AcceleratorElement.md) |
| [BeamArrivalMonitor](BeamArrivalMonitor.md) | [upstream](upstream.md) | range | [AcceleratorElement](AcceleratorElement.md) |
| [BeamArrivalMonitor](BeamArrivalMonitor.md) | [downstream](downstream.md) | range | [AcceleratorElement](AcceleratorElement.md) |
| [BunchLengthMonitor](BunchLengthMonitor.md) | [upstream](upstream.md) | range | [AcceleratorElement](AcceleratorElement.md) |
| [BunchLengthMonitor](BunchLengthMonitor.md) | [downstream](downstream.md) | range | [AcceleratorElement](AcceleratorElement.md) |
| [Camera](Camera.md) | [upstream](upstream.md) | range | [AcceleratorElement](AcceleratorElement.md) |
| [Camera](Camera.md) | [downstream](downstream.md) | range | [AcceleratorElement](AcceleratorElement.md) |
| [Screen](Screen.md) | [upstream](upstream.md) | range | [AcceleratorElement](AcceleratorElement.md) |
| [Screen](Screen.md) | [downstream](downstream.md) | range | [AcceleratorElement](AcceleratorElement.md) |
| [WireScanner](WireScanner.md) | [upstream](upstream.md) | range | [AcceleratorElement](AcceleratorElement.md) |
| [WireScanner](WireScanner.md) | [downstream](downstream.md) | range | [AcceleratorElement](AcceleratorElement.md) |
| [ChargeDiagnostic](ChargeDiagnostic.md) | [upstream](upstream.md) | range | [AcceleratorElement](AcceleratorElement.md) |
| [ChargeDiagnostic](ChargeDiagnostic.md) | [downstream](downstream.md) | range | [AcceleratorElement](AcceleratorElement.md) |
| [WallCurrentMonitor](WallCurrentMonitor.md) | [upstream](upstream.md) | range | [AcceleratorElement](AcceleratorElement.md) |
| [WallCurrentMonitor](WallCurrentMonitor.md) | [downstream](downstream.md) | range | [AcceleratorElement](AcceleratorElement.md) |
| [FaradayCupMonitor](FaradayCupMonitor.md) | [upstream](upstream.md) | range | [AcceleratorElement](AcceleratorElement.md) |
| [FaradayCupMonitor](FaradayCupMonitor.md) | [downstream](downstream.md) | range | [AcceleratorElement](AcceleratorElement.md) |
| [IntegratedCurrentTransformer](IntegratedCurrentTransformer.md) | [upstream](upstream.md) | range | [AcceleratorElement](AcceleratorElement.md) |
| [IntegratedCurrentTransformer](IntegratedCurrentTransformer.md) | [downstream](downstream.md) | range | [AcceleratorElement](AcceleratorElement.md) |
| [PhotonMonitor](PhotonMonitor.md) | [upstream](upstream.md) | range | [AcceleratorElement](AcceleratorElement.md) |
| [PhotonMonitor](PhotonMonitor.md) | [downstream](downstream.md) | range | [AcceleratorElement](AcceleratorElement.md) |
| [Plasma](Plasma.md) | [upstream](upstream.md) | range | [AcceleratorElement](AcceleratorElement.md) |
| [Plasma](Plasma.md) | [downstream](downstream.md) | range | [AcceleratorElement](AcceleratorElement.md) |
| [LaserEnergyMeter](LaserEnergyMeter.md) | [upstream](upstream.md) | range | [AcceleratorElement](AcceleratorElement.md) |
| [LaserEnergyMeter](LaserEnergyMeter.md) | [downstream](downstream.md) | range | [AcceleratorElement](AcceleratorElement.md) |
| [LaserHalfWavePlate](LaserHalfWavePlate.md) | [upstream](upstream.md) | range | [AcceleratorElement](AcceleratorElement.md) |
| [LaserHalfWavePlate](LaserHalfWavePlate.md) | [downstream](downstream.md) | range | [AcceleratorElement](AcceleratorElement.md) |
| [LaserMirror](LaserMirror.md) | [upstream](upstream.md) | range | [AcceleratorElement](AcceleratorElement.md) |
| [LaserMirror](LaserMirror.md) | [downstream](downstream.md) | range | [AcceleratorElement](AcceleratorElement.md) |
| [LaserAttenuator](LaserAttenuator.md) | [upstream](upstream.md) | range | [AcceleratorElement](AcceleratorElement.md) |
| [LaserAttenuator](LaserAttenuator.md) | [downstream](downstream.md) | range | [AcceleratorElement](AcceleratorElement.md) |
| [Dipole](Dipole.md) | [upstream](upstream.md) | range | [AcceleratorElement](AcceleratorElement.md) |
| [Dipole](Dipole.md) | [downstream](downstream.md) | range | [AcceleratorElement](AcceleratorElement.md) |
| [Quadrupole](Quadrupole.md) | [upstream](upstream.md) | range | [AcceleratorElement](AcceleratorElement.md) |
| [Quadrupole](Quadrupole.md) | [downstream](downstream.md) | range | [AcceleratorElement](AcceleratorElement.md) |
| [Sextupole](Sextupole.md) | [upstream](upstream.md) | range | [AcceleratorElement](AcceleratorElement.md) |
| [Sextupole](Sextupole.md) | [downstream](downstream.md) | range | [AcceleratorElement](AcceleratorElement.md) |
| [Octupole](Octupole.md) | [upstream](upstream.md) | range | [AcceleratorElement](AcceleratorElement.md) |
| [Octupole](Octupole.md) | [downstream](downstream.md) | range | [AcceleratorElement](AcceleratorElement.md) |
| [Decapole](Decapole.md) | [upstream](upstream.md) | range | [AcceleratorElement](AcceleratorElement.md) |
| [Decapole](Decapole.md) | [downstream](downstream.md) | range | [AcceleratorElement](AcceleratorElement.md) |
| [HorizontalCorrector](HorizontalCorrector.md) | [upstream](upstream.md) | range | [AcceleratorElement](AcceleratorElement.md) |
| [HorizontalCorrector](HorizontalCorrector.md) | [downstream](downstream.md) | range | [AcceleratorElement](AcceleratorElement.md) |
| [VerticalCorrector](VerticalCorrector.md) | [upstream](upstream.md) | range | [AcceleratorElement](AcceleratorElement.md) |
| [VerticalCorrector](VerticalCorrector.md) | [downstream](downstream.md) | range | [AcceleratorElement](AcceleratorElement.md) |
| [CombinedCorrector](CombinedCorrector.md) | [upstream](upstream.md) | range | [AcceleratorElement](AcceleratorElement.md) |
| [CombinedCorrector](CombinedCorrector.md) | [downstream](downstream.md) | range | [AcceleratorElement](AcceleratorElement.md) |
| [Solenoid](Solenoid.md) | [upstream](upstream.md) | range | [AcceleratorElement](AcceleratorElement.md) |
| [Solenoid](Solenoid.md) | [downstream](downstream.md) | range | [AcceleratorElement](AcceleratorElement.md) |
| [CombinedSolenoidQuadrupole](CombinedSolenoidQuadrupole.md) | [upstream](upstream.md) | range | [AcceleratorElement](AcceleratorElement.md) |
| [CombinedSolenoidQuadrupole](CombinedSolenoidQuadrupole.md) | [downstream](downstream.md) | range | [AcceleratorElement](AcceleratorElement.md) |
| [Wiggler](Wiggler.md) | [upstream](upstream.md) | range | [AcceleratorElement](AcceleratorElement.md) |
| [Wiggler](Wiggler.md) | [downstream](downstream.md) | range | [AcceleratorElement](AcceleratorElement.md) |
| [NonLinearLens](NonLinearLens.md) | [upstream](upstream.md) | range | [AcceleratorElement](AcceleratorElement.md) |
| [NonLinearLens](NonLinearLens.md) | [downstream](downstream.md) | range | [AcceleratorElement](AcceleratorElement.md) |












## Identifier and Mapping Information





### Schema Source


* from schema: https://w3id.org/laura/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | laura:AcceleratorElement |
| native | laura:AcceleratorElement |






## LinkML Source

<!-- TODO: investigate https://stackoverflow.com/questions/37606292/how-to-create-tabbed-code-blocks-in-mkdocs-or-sphinx -->

### Direct

<details>
```yaml
name: AcceleratorElement
description: Root base class for all LAURA accelerator elements.  Every lattice element
  is an instance of a concrete subclass identified by ``hardware_type``.
from_schema: https://w3id.org/laura/schema
attributes:
  name:
    name: name
    description: Unique element name within the machine.
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    identifier: true
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
    domain_of:
    - AcceleratorElement
    range: string
  machine_area:
    name: machine_area
    description: Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).
    from_schema: https://w3id.org/laura/schema
    rank: 1000
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
    domain_of:
    - AcceleratorElement
    range: string
  inputs:
    name: inputs
    description: Signal types this element consumes (e.g. ``[current, voltage]``).
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    domain_of:
    - AcceleratorElement
    range: IOTypeEnum
    multivalued: true
  outputs:
    name: outputs
    description: Signal types this element produces (e.g. ``[power, phase]``).
    from_schema: https://w3id.org/laura/schema
    rank: 1000
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
    domain_of:
    - AcceleratorElement
    range: AcceleratorElement
    multivalued: true
  downstream:
    name: downstream
    description: Names of elements this one feeds; the inverse of ``upstream``.
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    domain_of:
    - AcceleratorElement
    range: AcceleratorElement
    multivalued: true
class_uri: laura:AcceleratorElement
tree_root: true

```
</details>

### Induced

<details>
```yaml
name: AcceleratorElement
description: Root base class for all LAURA accelerator elements.  Every lattice element
  is an instance of a concrete subclass identified by ``hardware_type``.
from_schema: https://w3id.org/laura/schema
attributes:
  name:
    name: name
    description: Unique element name within the machine.
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    identifier: true
    owner: AcceleratorElement
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
    owner: AcceleratorElement
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
    owner: AcceleratorElement
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
    owner: AcceleratorElement
    domain_of:
    - AcceleratorElement
    range: string
  machine_area:
    name: machine_area
    description: Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    owner: AcceleratorElement
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
    owner: AcceleratorElement
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
    owner: AcceleratorElement
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
    owner: AcceleratorElement
    domain_of:
    - AcceleratorElement
    range: string
  inputs:
    name: inputs
    description: Signal types this element consumes (e.g. ``[current, voltage]``).
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    owner: AcceleratorElement
    domain_of:
    - AcceleratorElement
    range: IOTypeEnum
    multivalued: true
  outputs:
    name: outputs
    description: Signal types this element produces (e.g. ``[power, phase]``).
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    owner: AcceleratorElement
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
    owner: AcceleratorElement
    domain_of:
    - AcceleratorElement
    range: AcceleratorElement
    multivalued: true
  downstream:
    name: downstream
    description: Names of elements this one feeds; the inverse of ``upstream``.
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    owner: AcceleratorElement
    domain_of:
    - AcceleratorElement
    range: AcceleratorElement
    multivalued: true
class_uri: laura:AcceleratorElement
tree_root: true

```
</details></div>