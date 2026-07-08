---
search:
  boost: 5.0
---

# Slot: physical 


_Position, rotation, and length data._



<div data-search-exclude markdown="1">



URI: [laura:physical](https://w3id.org/laura/physical)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [PhysicalAcceleratorElement](PhysicalAcceleratorElement.md) | Accelerator element with a well-defined physical position and orientation in ... |  no  |
| [TwissMatch](TwissMatch.md) | Virtual Twiss-parameter matching point -- a zero-length marker that defines t... |  no  |
| [Stage](Stage.md) | Motorised positioning stage |  no  |
| [VacuumGauge](VacuumGauge.md) | Vacuum-pressure gauge |  no  |
| [Laser](Laser.md) | Laser system element (full laser setup including beam parameters) |  no  |
| [Shutter](Shutter.md) | Beam or laser shutter with interlock logic |  no  |
| [Valve](Valve.md) | Vacuum gate valve |  no  |
| [Marker](Marker.md) | Virtual survey marker -- a zero-length reference point used for alignment |  no  |
| [Aperture](Aperture.md) | Mechanical aperture restriction in the beam pipe |  no  |
| [Collimator](Collimator.md) | Movable collimator jaw (extends Aperture) |  no  |
| [Drift](Drift.md) | Field-free drift space between elements |  no  |
| [Magnet](Magnet.md) | Base class for all magnetic focusing and bending elements |  no  |
| [RFCavity](RFCavity.md) | Accelerating RF cavity |  no  |
| [RFDeflectingCavity](RFDeflectingCavity.md) | Transverse-deflecting (streak) RF cavity |  no  |
| [Wakefield](Wakefield.md) | Passive wakefield structure (dielectric, corrugated, etc |  no  |
| [Diagnostic](Diagnostic.md) | Base class for all beam-diagnostic instruments |  no  |
| [BeamPositionMonitor](BeamPositionMonitor.md) | Beam-position monitor (BPM) |  no  |
| [BeamArrivalMonitor](BeamArrivalMonitor.md) | Beam-arrival-time monitor (BAM) |  no  |
| [BunchLengthMonitor](BunchLengthMonitor.md) | Bunch-length monitor (BLM / CDR detector) |  no  |
| [Camera](Camera.md) | Camera-based beam-profile monitor |  no  |
| [Screen](Screen.md) | Scintillator or OTR screen with an associated camera |  no  |
| [ChargeDiagnostic](ChargeDiagnostic.md) | Base class for charge-measurement diagnostics |  no  |
| [WallCurrentMonitor](WallCurrentMonitor.md) | Wall-current monitor (WCM) for non-destructive charge measurement |  no  |
| [FaradayCupMonitor](FaradayCupMonitor.md) | Faraday cup for destructive charge measurement |  no  |
| [IntegratedCurrentTransformer](IntegratedCurrentTransformer.md) | Integrated current transformer (ICT) for non-destructive single-shot charge m... |  no  |
| [Plasma](Plasma.md) | Laser-driven plasma-accelerator stage |  no  |
| [Dipole](Dipole.md) |  |  no  |
| [Quadrupole](Quadrupole.md) |  |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [PhysicalElement](PhysicalElement.md) |
| Domain Of | [PhysicalAcceleratorElement](PhysicalAcceleratorElement.md) |

### Cardinality and Requirements

| Property | Value |
| --- | --- |
### Slot Characteristics

| Property | Value |
| --- | --- |
| Owner | [PhysicalAcceleratorElement](PhysicalAcceleratorElement.md) |








## In Subsets


* [PhysicalProperties](PhysicalProperties.md)






## Identifier and Mapping Information





### Schema Source


* from schema: https://w3id.org/laura/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | laura:physical |
| native | laura:physical |




## LinkML Source

<details>
```yaml
name: physical
description: Position, rotation, and length data.
in_subset:
- physical_properties
from_schema: https://w3id.org/laura/schema
rank: 1000
owner: PhysicalAcceleratorElement
domain_of:
- PhysicalAcceleratorElement
range: PhysicalElement

```
</details></div>