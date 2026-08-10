# Slot: hardware_type 


_Python class name used for ELEMENT_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML._



<div data-search-exclude markdown="1">



URI: [laura:hardware_type](https://w3id.org/laura/hardware_type)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [AcceleratorElement](AcceleratorElement.md) | Root base class for all LAURA accelerator elements |  no  |
| [StandardElement](StandardElement.md) | Accelerator element with control-system, electrical, manufacturer, simulation... |  no  |
| [Element](Element.md) | Concrete schema counterpart of the Python ``Element`` wrapper class |  no  |
| [PhysicalAcceleratorElement](PhysicalAcceleratorElement.md) | Accelerator element with a well-defined physical position and orientation in ... |  no  |
| [TwissMatch](TwissMatch.md) | Virtual Twiss-parameter matching point -- a zero-length marker that defines t... |  yes  |
| [MatrixTransform](MatrixTransform.md) | Transfer-map element with zero-, first-, and second-order coefficients |  yes  |
| [ElectrostaticSeparator](ElectrostaticSeparator.md) | Static electrostatic transverse-deflection element |  yes  |
| [ACDipole](ACDipole.md) | Base class for horizontal and vertical AC-dipole tune exciters |  no  |
| [HorizontalACDipole](HorizontalACDipole.md) | Horizontally deflecting AC-dipole tune exciter |  yes  |
| [VerticalACDipole](VerticalACDipole.md) | Vertically deflecting AC-dipole tune exciter |  yes  |
| [Wire](Wire.md) | Current-carrying wire for long-range beam-beam compensation |  yes  |
| [BeamBeam](BeamBeam.md) | Weak-strong beam-beam interaction element |  yes  |
| [RFMultipole](RFMultipole.md) | Thin RF-driven multipole kick |  yes  |
| [Stage](Stage.md) | Motorised positioning stage |  yes  |
| [VacuumGauge](VacuumGauge.md) | Vacuum-pressure gauge |  yes  |
| [Laser](Laser.md) | Laser system element (full laser setup including beam parameters) |  yes  |
| [Shutter](Shutter.md) | Beam or laser shutter with interlock logic |  yes  |
| [Valve](Valve.md) | Vacuum gate valve |  yes  |
| [Marker](Marker.md) | Virtual survey marker -- a zero-length reference point used for alignment |  yes  |
| [Aperture](Aperture.md) | Mechanical aperture restriction in the beam pipe |  yes  |
| [Collimator](Collimator.md) | Movable collimator jaw (extends Aperture) |  yes  |
| [Drift](Drift.md) | Field-free drift space between elements |  yes  |
| [Lighting](Lighting.md) | Experimental-hall lighting element |  yes  |
| [PowerSupply](PowerSupply.md) | Generic power-supply unit providing control/setpoint-driven outputs (for exam... |  yes  |
| [Magnet](Magnet.md) | Base class for all magnetic focusing and bending elements |  no  |
| [RFCavity](RFCavity.md) | Accelerating RF cavity |  yes  |
| [RFDeflectingCavity](RFDeflectingCavity.md) | Transverse-deflecting (streak) RF cavity |  yes  |
| [CrabCavity](CrabCavity.md) | Transverse-deflecting crab cavity for crossing-angle compensation |  yes  |
| [Wakefield](Wakefield.md) | Passive wakefield structure (dielectric, corrugated, etc |  yes  |
| [LowLevelRF](LowLevelRF.md) | Low-level RF (LLRF) controller |  yes  |
| [RFModulator](RFModulator.md) | RF modulator (klystron driver) element |  yes  |
| [RFProtection](RFProtection.md) | RF protection system element |  yes  |
| [RFHeartbeat](RFHeartbeat.md) | RF timing heartbeat / signal-monitor element |  yes  |
| [PID](PID.md) | Proportional-integral-derivative (PID) feedback controller |  yes  |
| [Diagnostic](Diagnostic.md) | Base class for all beam-diagnostic instruments |  no  |
| [BeamPositionMonitor](BeamPositionMonitor.md) | Beam-position monitor (BPM) |  yes  |
| [BeamArrivalMonitor](BeamArrivalMonitor.md) | Beam-arrival-time monitor (BAM) |  yes  |
| [BunchLengthMonitor](BunchLengthMonitor.md) | Bunch-length monitor (BLM / CDR detector) |  yes  |
| [Camera](Camera.md) | Camera-based beam-profile monitor |  yes  |
| [Screen](Screen.md) | Scintillator or OTR screen with an associated camera |  yes  |
| [WireScanner](WireScanner.md) | Intercepting wire scanner for transverse profile measurement |  yes  |
| [ChargeDiagnostic](ChargeDiagnostic.md) | Base class for charge-measurement diagnostics |  yes  |
| [WallCurrentMonitor](WallCurrentMonitor.md) | Wall-current monitor (WCM) for non-destructive charge measurement |  yes  |
| [FaradayCupMonitor](FaradayCupMonitor.md) | Faraday cup for destructive charge measurement |  yes  |
| [IntegratedCurrentTransformer](IntegratedCurrentTransformer.md) | Integrated current transformer (ICT) for non-destructive single-shot charge m... |  yes  |
| [PhotonMonitor](PhotonMonitor.md) | Photon intensity monitor |  yes  |
| [Plasma](Plasma.md) | Laser-driven plasma-accelerator stage |  yes  |
| [LaserEnergyMeter](LaserEnergyMeter.md) | Laser pulse-energy diagnostic (photodiode / pyroelectric) |  yes  |
| [LaserHalfWavePlate](LaserHalfWavePlate.md) | Half-wave plate for laser polarisation rotation |  yes  |
| [LaserMirror](LaserMirror.md) | Laser steering or focusing mirror |  yes  |
| [LaserAttenuator](LaserAttenuator.md) | Laser power attenuator (waveplate + polariser combination) |  yes  |
| [Dipole](Dipole.md) |  |  yes  |
| [Quadrupole](Quadrupole.md) |  |  yes  |
| [Sextupole](Sextupole.md) | Sextupole chromaticity-correction magnet |  yes  |
| [Octupole](Octupole.md) | Octupole magnet |  yes  |
| [Decapole](Decapole.md) | Decapole magnet |  yes  |
| [HorizontalCorrector](HorizontalCorrector.md) | Horizontal steering corrector |  yes  |
| [VerticalCorrector](VerticalCorrector.md) | Vertical steering corrector |  yes  |
| [CombinedCorrector](CombinedCorrector.md) | Combined horizontal/vertical steering corrector, naming the two single-plane ... |  yes  |
| [Solenoid](Solenoid.md) | Solenoid focusing magnet |  yes  |
| [CombinedSolenoidQuadrupole](CombinedSolenoidQuadrupole.md) | Magnet combining coaxial solenoid and quadrupole fields |  yes  |
| [Wiggler](Wiggler.md) | Wiggler / undulator insertion device |  yes  |
| [NonLinearLens](NonLinearLens.md) | Non-linear integrable-optics lens |  yes  |






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
| self | laura:hardware_type |
| native | laura:hardware_type |




## LinkML Source

<details>
```yaml
name: hardware_type
description: Python class name used for ELEMENT_REGISTRY dispatch.  Identifies the
  concrete subclass to instantiate when loading from YAML.
from_schema: https://w3id.org/laura/schema
rank: 1000
ifabsent: string(Generic)
owner: AcceleratorElement
domain_of:
- AcceleratorElement
range: string

```
</details></div>