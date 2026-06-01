---
search:
  boost: 5.0
---

# Slot: hardware_model 


_Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``)._



<div data-search-exclude markdown="1">



URI: [laura:hardware_model](https://w3id.org/laura/hardware_model)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [AcceleratorElement](AcceleratorElement.md) | Root base class for all LAURA accelerator elements |  no  |
| [StandardElement](StandardElement.md) | Accelerator element with control-system, electrical, manufacturer, simulation... |  no  |
| [Element](Element.md) | Concrete schema counterpart of the Python ``Element`` wrapper class |  no  |
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
| [Lighting](Lighting.md) | Experimental-hall lighting element |  no  |
| [PowerSupply](PowerSupply.md) | Generic power-supply unit providing control/setpoint-driven outputs (for exam... |  no  |
| [Magnet](Magnet.md) | Base class for all magnetic focusing and bending elements |  no  |
| [RFCavity](RFCavity.md) | Accelerating RF cavity |  no  |
| [RFDeflectingCavity](RFDeflectingCavity.md) | Transverse-deflecting (streak) RF cavity |  no  |
| [Wakefield](Wakefield.md) | Passive wakefield structure (dielectric, corrugated, etc |  no  |
| [LowLevelRF](LowLevelRF.md) | Low-level RF (LLRF) controller |  no  |
| [RFModulator](RFModulator.md) | RF modulator (klystron driver) element |  no  |
| [RFProtection](RFProtection.md) | RF protection system element |  no  |
| [RFHeartbeat](RFHeartbeat.md) | RF timing heartbeat / signal-monitor element |  no  |
| [PID](PID.md) | Proportional-integral-derivative (PID) feedback controller |  no  |
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
| [LaserEnergyMeter](LaserEnergyMeter.md) | Laser pulse-energy diagnostic (photodiode / pyroelectric) |  no  |
| [LaserHalfWavePlate](LaserHalfWavePlate.md) | Half-wave plate for laser polarisation rotation |  no  |
| [LaserMirror](LaserMirror.md) | Laser steering or focusing mirror |  no  |
| [LaserAttenuator](LaserAttenuator.md) | Laser power attenuator (waveplate + polariser combination) |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [String](String.md) |
| Domain Of | [AcceleratorElement](AcceleratorElement.md) |

### Cardinality and Requirements

| Property | Value |
| --- | --- |
### Slot Characteristics

| Property | Value |
| --- | --- |
| If Absent | `string(Generic)` |
| Owner | [AcceleratorElement](AcceleratorElement.md) |












## Identifier and Mapping Information





### Schema Source


* from schema: https://w3id.org/laura/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | laura:hardware_model |
| native | laura:hardware_model |




## LinkML Source

<details>
```yaml
name: hardware_model
description: Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).
from_schema: https://w3id.org/laura/schema
rank: 1000
ifabsent: string(Generic)
owner: AcceleratorElement
domain_of:
- AcceleratorElement
range: string

```
</details></div>