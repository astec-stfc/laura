---
search:
  boost: 10.0
---

# Class: ControlsInformation 


_Collection of process-variable definitions for an element's control interface._



<div data-search-exclude markdown="1">



URI: [laura:ControlsInformation](https://w3id.org/laura/ControlsInformation)





```mermaid
 classDiagram
    class ControlsInformation
    click ControlsInformation href "../ControlsInformation/"
      ControlsInformation : variables
        
          
    
        
        
        ControlsInformation --> "*" ControlVariable : variables
        click ControlVariable href "../ControlVariable/"
    

        
      
```




<!-- no inheritance hierarchy -->

## Class Properties

| Property | Value |
| --- | --- |
| Class URI | [laura:ControlsInformation](https://w3id.org/laura/ControlsInformation) |


## Slots

| Name | Cardinality and Range | Description | Inheritance |
| ---  | --- | --- | --- |
| [variables](variables.md) | * <br/> [ControlVariable](ControlVariable.md) | Named control variables keyed by logical name | direct |





## Usages

| used by | used in | type | used |
| ---  | --- | --- | --- |
| [StandardElement](StandardElement.md) | [controls](controls.md) | range | [ControlsInformation](ControlsInformation.md) |
| [Element](Element.md) | [controls](controls.md) | range | [ControlsInformation](ControlsInformation.md) |
| [PhysicalAcceleratorElement](PhysicalAcceleratorElement.md) | [controls](controls.md) | range | [ControlsInformation](ControlsInformation.md) |
| [MagnetBaseElement](MagnetBaseElement.md) | [controls](controls.md) | range | [ControlsInformation](ControlsInformation.md) |
| [Diagnostic](Diagnostic.md) | [controls](controls.md) | range | [ControlsInformation](ControlsInformation.md) |
| [BeamPositionMonitor](BeamPositionMonitor.md) | [controls](controls.md) | range | [ControlsInformation](ControlsInformation.md) |
| [BeamArrivalMonitor](BeamArrivalMonitor.md) | [controls](controls.md) | range | [ControlsInformation](ControlsInformation.md) |
| [BunchLengthMonitor](BunchLengthMonitor.md) | [controls](controls.md) | range | [ControlsInformation](ControlsInformation.md) |
| [Camera](Camera.md) | [controls](controls.md) | range | [ControlsInformation](ControlsInformation.md) |
| [Screen](Screen.md) | [controls](controls.md) | range | [ControlsInformation](ControlsInformation.md) |
| [ChargeDiagnostic](ChargeDiagnostic.md) | [controls](controls.md) | range | [ControlsInformation](ControlsInformation.md) |
| [WallCurrentMonitor](WallCurrentMonitor.md) | [controls](controls.md) | range | [ControlsInformation](ControlsInformation.md) |
| [FaradayCupMonitor](FaradayCupMonitor.md) | [controls](controls.md) | range | [ControlsInformation](ControlsInformation.md) |
| [IntegratedCurrentTransformer](IntegratedCurrentTransformer.md) | [controls](controls.md) | range | [ControlsInformation](ControlsInformation.md) |
| [RFCavity](RFCavity.md) | [controls](controls.md) | range | [ControlsInformation](ControlsInformation.md) |
| [RFDeflectingCavity](RFDeflectingCavity.md) | [controls](controls.md) | range | [ControlsInformation](ControlsInformation.md) |
| [Wakefield](Wakefield.md) | [controls](controls.md) | range | [ControlsInformation](ControlsInformation.md) |
| [LowLevelRF](LowLevelRF.md) | [controls](controls.md) | range | [ControlsInformation](ControlsInformation.md) |
| [RFModulator](RFModulator.md) | [controls](controls.md) | range | [ControlsInformation](ControlsInformation.md) |
| [RFProtection](RFProtection.md) | [controls](controls.md) | range | [ControlsInformation](ControlsInformation.md) |
| [RFHeartbeat](RFHeartbeat.md) | [controls](controls.md) | range | [ControlsInformation](ControlsInformation.md) |
| [PID](PID.md) | [controls](controls.md) | range | [ControlsInformation](ControlsInformation.md) |
| [TwissMatch](TwissMatch.md) | [controls](controls.md) | range | [ControlsInformation](ControlsInformation.md) |
| [Stage](Stage.md) | [controls](controls.md) | range | [ControlsInformation](ControlsInformation.md) |
| [VacuumGauge](VacuumGauge.md) | [controls](controls.md) | range | [ControlsInformation](ControlsInformation.md) |
| [Laser](Laser.md) | [controls](controls.md) | range | [ControlsInformation](ControlsInformation.md) |
| [Shutter](Shutter.md) | [controls](controls.md) | range | [ControlsInformation](ControlsInformation.md) |
| [Valve](Valve.md) | [controls](controls.md) | range | [ControlsInformation](ControlsInformation.md) |
| [Marker](Marker.md) | [controls](controls.md) | range | [ControlsInformation](ControlsInformation.md) |
| [Aperture](Aperture.md) | [controls](controls.md) | range | [ControlsInformation](ControlsInformation.md) |
| [Collimator](Collimator.md) | [controls](controls.md) | range | [ControlsInformation](ControlsInformation.md) |
| [Drift](Drift.md) | [controls](controls.md) | range | [ControlsInformation](ControlsInformation.md) |
| [Plasma](Plasma.md) | [controls](controls.md) | range | [ControlsInformation](ControlsInformation.md) |
| [LaserEnergyMeter](LaserEnergyMeter.md) | [controls](controls.md) | range | [ControlsInformation](ControlsInformation.md) |
| [LaserHalfWavePlate](LaserHalfWavePlate.md) | [controls](controls.md) | range | [ControlsInformation](ControlsInformation.md) |
| [LaserMirror](LaserMirror.md) | [controls](controls.md) | range | [ControlsInformation](ControlsInformation.md) |
| [LaserAttenuator](LaserAttenuator.md) | [controls](controls.md) | range | [ControlsInformation](ControlsInformation.md) |
| [Lighting](Lighting.md) | [controls](controls.md) | range | [ControlsInformation](ControlsInformation.md) |












## Identifier and Mapping Information





### Schema Source


* from schema: https://w3id.org/laura/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | laura:ControlsInformation |
| native | laura:ControlsInformation |






## LinkML Source

<!-- TODO: investigate https://stackoverflow.com/questions/37606292/how-to-create-tabbed-code-blocks-in-mkdocs-or-sphinx -->

### Direct

<details>
```yaml
name: ControlsInformation
description: Collection of process-variable definitions for an element's control interface.
from_schema: https://w3id.org/laura/schema
attributes:
  variables:
    name: variables
    description: Named control variables keyed by logical name.
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    domain_of:
    - ControlsInformation
    range: ControlVariable
    multivalued: true
class_uri: laura:ControlsInformation

```
</details>

### Induced

<details>
```yaml
name: ControlsInformation
description: Collection of process-variable definitions for an element's control interface.
from_schema: https://w3id.org/laura/schema
attributes:
  variables:
    name: variables
    description: Named control variables keyed by logical name.
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    owner: ControlsInformation
    domain_of:
    - ControlsInformation
    range: ControlVariable
    multivalued: true
class_uri: laura:ControlsInformation

```
</details></div>