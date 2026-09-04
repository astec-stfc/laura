# LAURA Accelerator Element Schema

Linked Data schema for the LAURA (Lattice Architecture for a Unified Representation of Accelerators) accelerator element model.  Covers all element types, their physical, magnetic, diagnostic, RF, and control-system properties.

URI: https://w3id.org/laura/schema

Name: laura_schema



## Classes

| Class | Description |
| --- | --- |
| [AcceleratorElement](AcceleratorElement.md) | Root base class for all LAURA accelerator elements |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[StandardElement](StandardElement.md) | Accelerator element with control-system, electrical, manufacturer, simulation... |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[Element](Element.md) | Concrete schema counterpart of the Python ``Element`` wrapper class |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[PhysicalAcceleratorElement](PhysicalAcceleratorElement.md) | Accelerator element with a well-defined physical position and orientation in ... |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[ACDipole](ACDipole.md) | Base class for horizontal and vertical AC-dipole tune exciters |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[HorizontalACDipole](HorizontalACDipole.md) | Horizontally deflecting AC-dipole tune exciter |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[VerticalACDipole](VerticalACDipole.md) | Vertically deflecting AC-dipole tune exciter |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[Aperture](Aperture.md) | Mechanical aperture restriction in the beam pipe |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[Collimator](Collimator.md) | Movable collimator jaw (extends Aperture) |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[BeamBeam](BeamBeam.md) | Weak-strong beam-beam interaction element |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[Diagnostic](Diagnostic.md) | Base class for all beam-diagnostic instruments |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[BeamArrivalMonitor](BeamArrivalMonitor.md) | Beam-arrival-time monitor (BAM) |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[BeamPositionMonitor](BeamPositionMonitor.md) | Beam-position monitor (BPM) |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[BunchLengthMonitor](BunchLengthMonitor.md) | Bunch-length monitor (BLM / CDR detector) |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[Camera](Camera.md) | Camera-based beam-profile monitor |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[ChargeDiagnostic](ChargeDiagnostic.md) | Base class for charge-measurement diagnostics |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[FaradayCupMonitor](FaradayCupMonitor.md) | Faraday cup for destructive charge measurement |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[IntegratedCurrentTransformer](IntegratedCurrentTransformer.md) | Integrated current transformer (ICT) for non-destructive single-shot charge m... |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[WallCurrentMonitor](WallCurrentMonitor.md) | Wall-current monitor (WCM) for non-destructive charge measurement |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[PhotonMonitor](PhotonMonitor.md) | Photon intensity monitor |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[Screen](Screen.md) | Scintillator or OTR screen with an associated camera |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[Drift](Drift.md) | Field-free drift space between elements |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[ElectrostaticSeparator](ElectrostaticSeparator.md) | Static electrostatic transverse-deflection element |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[Laser](Laser.md) | Laser system element (full laser setup including beam parameters) |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[Magnet](Magnet.md) | Base class for all magnetic focusing and bending elements |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[Dipole](Dipole.md) |  |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[CombinedCorrector](CombinedCorrector.md) | Combined horizontal/vertical steering corrector, naming the two single-plane ... |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[HorizontalCorrector](HorizontalCorrector.md) | Horizontal steering corrector |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[VerticalCorrector](VerticalCorrector.md) | Vertical steering corrector |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[NonLinearLens](NonLinearLens.md) | Non-linear integrable-optics lens |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[Octupole](Octupole.md) | Octupole magnet |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[Quadrupole](Quadrupole.md) |  |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[Sextupole](Sextupole.md) | Sextupole chromaticity-correction magnet |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[Solenoid](Solenoid.md) | Solenoid focusing magnet |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[Wiggler](Wiggler.md) | Wiggler / undulator insertion device |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[Marker](Marker.md) | Virtual survey marker -- a zero-length reference point used for alignment |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[MatrixTransform](MatrixTransform.md) | Transfer-map element with zero-, first-, and second-order coefficients |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[Plasma](Plasma.md) | Laser-driven plasma-accelerator stage |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[RFCavity](RFCavity.md) | Accelerating RF cavity |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[CrabCavity](CrabCavity.md) | Transverse-deflecting crab cavity for crossing-angle compensation |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[RFDeflectingCavity](RFDeflectingCavity.md) | Transverse-deflecting (streak) RF cavity |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[RFMultipole](RFMultipole.md) | Thin RF-driven multipole kick |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[Shutter](Shutter.md) | Beam or laser shutter with interlock logic |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[Stage](Stage.md) | Motorised positioning stage |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[TwissMatch](TwissMatch.md) | Virtual Twiss-parameter matching point -- a zero-length marker that defines t... |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[VacuumGauge](VacuumGauge.md) | Vacuum-pressure gauge |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[Valve](Valve.md) | Vacuum gate valve |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[Wakefield](Wakefield.md) | Passive wakefield structure (dielectric, corrugated, etc |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[Wire](Wire.md) | Current-carrying wire for long-range beam-beam compensation |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[LaserAttenuator](LaserAttenuator.md) | Laser power attenuator (waveplate + polariser combination) |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[LaserEnergyMeter](LaserEnergyMeter.md) | Laser pulse-energy diagnostic (photodiode / pyroelectric) |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[LaserHalfWavePlate](LaserHalfWavePlate.md) | Half-wave plate for laser polarisation rotation |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[LaserMirror](LaserMirror.md) | Laser steering or focusing mirror |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[Lighting](Lighting.md) | Experimental-hall lighting element |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[LowLevelRF](LowLevelRF.md) | Low-level RF (LLRF) controller |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[PID](PID.md) | Proportional-integral-derivative (PID) feedback controller |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[PowerSupply](PowerSupply.md) | Generic power-supply unit providing control/setpoint-driven outputs (for exam... |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[RFHeartbeat](RFHeartbeat.md) | RF timing heartbeat / signal-monitor element |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[RFModulator](RFModulator.md) | RF modulator (klystron driver) element |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[RFProtection](RFProtection.md) | RF protection system element |
| [ApertureElement](ApertureElement.md) | Transverse aperture geometry for drift-space checks and collimators |
| [CameraMask](CameraMask.md) | Camera analysis mask parameters |
| [CameraPixelResultsIndices](CameraPixelResultsIndices.md) | Indices into camera pixel-analysis result arrays |
| [CameraPixelResultsNames](CameraPixelResultsNames.md) | Names of camera pixel-analysis result arrays |
| [CameraSensor](CameraSensor.md) | Camera sensor hardware configuration |
| [ChannelNames](ChannelNames.md) | Names for LLRF channels 1 |
| [ControlsInformation](ControlsInformation.md) | Collection of process-variable definitions for an element's control interface |
| [ControlVariable](ControlVariable.md) | A single process-variable entry mapping a logical name to a control-system PV... |
| [CorrectorMagnet](CorrectorMagnet.md) | Steering-corrector field, expressed as horizontal and vertical kicks rather t... |
| [DegaussableElement](DegaussableElement.md) | Degaussing (demagnetisation cycle) parameters for magnets that require a fiel... |
| [DiagnosticElement](DiagnosticElement.md) | Base class for diagnostic instrument sub-models |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[BAMDiagnosticElement](BAMDiagnosticElement.md) | Beam-arrival monitor (BAM) diagnostic data |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[BLMDiagnosticElement](BLMDiagnosticElement.md) | Bunch-length monitor (BLM) diagnostic data |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[BPMDiagnosticElement](BPMDiagnosticElement.md) | Beam-position monitor (BPM) diagnostic data |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[CameraDiagnosticElement](CameraDiagnosticElement.md) | Camera diagnostic data, including sensor parameters, analysis mask, and pixel... |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[ChargeDiagnosticElement](ChargeDiagnosticElement.md) | Charge-measurement diagnostic data (base for ICT, FCM, WCM) |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[PhotonIntensityMonitorDiagnostic](PhotonIntensityMonitorDiagnostic.md) | Photon intensity monitor diagnostic data |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[ScreenDiagnosticElement](ScreenDiagnosticElement.md) | Scintillator or OTR screen diagnostic data |
| [ElectricalElement](ElectricalElement.md) | Power-supply electrical limits for a beamline element |
| [ElementPositionError](ElementPositionError.md) | Alignment position and rotation errors for a physically-located element |
| [ElementSurvey](ElementSurvey.md) | Survey-measured position and rotation of an element |
| [FieldIntegral](FieldIntegral.md) | Polynomial fit of integrated field strength as a function of magnet current |
| [LaserElement](LaserElement.md) | Laser-beam parameters (wavelength, pulse energy, profile, etc |
| [LaserEnergyMeterElement](LaserEnergyMeterElement.md) | Laser energy-meter sub-model (no additional fields) |
| [LaserHalfWavePlateElement](LaserHalfWavePlateElement.md) | Half-wave plate sub-model (no additional fields) |
| [LaserMirrorElement](LaserMirrorElement.md) | Mirror steering parameters for a laser mirror |
| [LaserMirrorSense](LaserMirrorSense.md) | Mirror sense switch values |
| [LightingElement](LightingElement.md) | Lighting element (no additional fields currently defined) |
| [LinearSaturationFit](LinearSaturationFit.md) | Bi-linear saturation model mapping magnet current to integrated field strengt... |
| [LLRFTiming](LLRFTiming.md) | Start/end window timing definition |
| [LLRFTimings](LLRFTimings.md) | Collection of timing windows for key LLRF channels |
| [LowLevelRFElement](LowLevelRFElement.md) | Low-level RF (LLRF) system parameters |
| [MachineLayout](MachineLayout.md) | An ordered list of section names defining a beamline layout (a contiguous seq... |
| [MachineModel](MachineModel.md) | Top-level container for a complete accelerator lattice: elements, sections, l... |
| [MagneticElement](MagneticElement.md) | Magnetic field parameters for a beamline magnet, including multipole componen... |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[DipoleMagnet](DipoleMagnet.md) |  |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[OctupoleMagnet](OctupoleMagnet.md) | Octupole magnet field, principal multipole order 3 |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[QuadrupoleMagnet](QuadrupoleMagnet.md) |  |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[SextupoleMagnet](SextupoleMagnet.md) | Sextupole magnet field, principal multipole order 2 |
| [ManufacturerElement](ManufacturerElement.md) | Manufacturer and serial-number metadata |
| [MatrixValue](MatrixValue.md) | An unconstrained serializable matrix value |
| [Multipole](Multipole.md) | Individual multipole field component, characterised by order and integrated n... |
| [Multipoles](Multipoles.md) | Complete set of integrated multipole strengths up to decapole order, as named... |
| [NonLinearLensMagnet](NonLinearLensMagnet.md) | Integrable-optics non-linear lens field |
| [PhysicalElement](PhysicalElement.md) | Physical placement data: position, rotation, length, and associated survey / ... |
| [PIDElement](PIDElement.md) | PID feedback-controller parameters |
| [PIDPhaseRange](PIDPhaseRange.md) | Numeric min/max range for PID phase control |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[PIDWeightRange](PIDWeightRange.md) | Numeric min/max range for PID phase weighting |
| [PlasmaElement](PlasmaElement.md) | Plasma channel parameters for a laser-driven plasma-accelerator stage |
| [Position](Position.md) | Cartesian position in the global accelerator coordinate system |
| [ReferenceElement](ReferenceElement.md) | Links to engineering drawings and design files |
| [ReferencePlacement](ReferencePlacement.md) | Positions an element relative to a named reference element's local frame |
| [RFCavityElement](RFCavityElement.md) | RF cavity accelerating-structure parameters |
| [RFDeflectingCavityElement](RFDeflectingCavityElement.md) | Transverse-deflecting RF cavity parameters -- a subset of RFCavityElement for... |
| [RFHeartbeatElement](RFHeartbeatElement.md) | RF heartbeat / timing-monitor element parameters |
| [RFModulatorElement](RFModulatorElement.md) | RF modulator (klystron driver) parameters |
| [RFProtectionElement](RFProtectionElement.md) | RF protection system parameters |
| [Rotation](Rotation.md) | Euler-angle rotation relative to the global coordinate system |
| [SectionLattice](SectionLattice.md) | An ordered list of element names defining a contiguous beamline section |
| [ShutterElement](ShutterElement.md) | Shutter interlock configuration |
| [SimulationElement](SimulationElement.md) | Base simulation attributes: field-map files and reference positions for track... |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[ACDipoleSimulationElement](ACDipoleSimulationElement.md) | Simulation attributes for an AC dipole / tune exciter |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[BeamBeamSimulationElement](BeamBeamSimulationElement.md) | Simulation attributes for a weak-strong beam-beam interaction |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[DiagnosticSimulationElement](DiagnosticSimulationElement.md) | Simulation attributes for beam-diagnostic elements |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[DriftSimulationElement](DriftSimulationElement.md) | Simulation attributes for field-free drift sections |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[ElectrostaticSeparatorSimulationElement](ElectrostaticSeparatorSimulationElement.md) | Simulation attributes for a static electrostatic separator |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[MagnetSimulationElement](MagnetSimulationElement.md) | Simulation attributes specific to magnets: integrator settings, fringe-field ... |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[MatrixTransformSimulationElement](MatrixTransformSimulationElement.md) | Zero-, first-, and second-order transfer-map coefficients for a matrix transf... |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[PlasmaSimulationElement](PlasmaSimulationElement.md) | Simulation attributes for plasma-accelerator stages |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[RFCavitySimulationElement](RFCavitySimulationElement.md) | Simulation attributes for RF cavity elements |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[RFMultipoleSimulationElement](RFMultipoleSimulationElement.md) | Simulation attributes for a thin RF multipole kick |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[TwissMatchSimulationElement](TwissMatchSimulationElement.md) | Simulation attributes for Twiss-matching points |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[WakefieldSimulationElement](WakefieldSimulationElement.md) | Simulation attributes for passive wakefield structures |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[WireSimulationElement](WireSimulationElement.md) | Simulation attributes for a compensating wire |
| [SolenoidMagnet](SolenoidMagnet.md) | Solenoid field model, including systematic and random field errors and the cu... |
| [SolenoidFields](SolenoidFields.md) | Solenoid integrated axial field components ``S0L``–``S12L`` [T |
| [Trace](Trace.md) | LLRF trace metadata |
| [ValveElement](ValveElement.md) | Vacuum valve configuration (no additional fields) |
| [WakefieldElement](WakefieldElement.md) | Passive wakefield structure parameters |
| [WigglerMagnet](WigglerMagnet.md) | Periodic wiggler/undulator field |



## Slots

| Slot | Description |
| --- | --- |
| [a](a.md) | Quadratic saturation coefficient |
| [alias](alias.md) | Human-readable aliases for the element |
| [allow_long_beam](allow_long_beam.md) | Allow beams longer than the wakefield |
| [alpha_x](alpha_x.md) | Horizontal alpha |
| [alpha_y](alpha_y.md) | Vertical alpha |
| [angle](angle.md) | Integrated bending angle [rad] |
| [aperture](aperture.md) | Aperture geometry parameters |
| [apply](apply.md) | Whether to apply the transfer map |
| [attenuation_constant](attenuation_constant.md) | Attenuation constant ? of a travelling-wave structure [Np/m] |
| [auto_buffer](auto_buffer.md) | Whether the control system buffers readings for this variable automatically |
| [beam_pixel_average](beam_pixel_average.md) | Average pixel value for beam detection |
| [beta_x](beta_x.md) | Horizontal beta |
| [beta_y](beta_y.md) | Vertical beta |
| [bit_depth](bit_depth.md) | Camera bit depth |
| [body_focus_model](body_focus_model.md) | Cavity body focusing model |
| [bore](bore.md) | Magnet bore radius [m] |
| [buffer_size](buffer_size.md) | Number of readings retained in the buffer |
| [bunch_pusher](bunch_pusher.md) | Pusher used to evolve bunch particles in time |
| [bunched_beam](bunched_beam.md) | Use bunched beam mode |
| [c_matrix](c_matrix.md) | C-matrix (zeroth-order transfer vector) |
| [camera_name](camera_name.md) | Name of the associated camera element |
| [cavity](cavity.md) | RF structure parameters |
| [cavity_forward](cavity_forward.md) | Timing for cavity forward power |
| [cavity_probe](cavity_probe.md) | Timing for cavity probe |
| [cavity_reverse](cavity_reverse.md) | Timing for cavity reverse power |
| [cell_length](cell_length.md) | Length of a single cell [m] |
| [cep_phase](cep_phase.md) | Carrier-envelope phase [rad] |
| [ch1](ch1.md) |  |
| [ch2](ch2.md) |  |
| [ch3](ch3.md) |  |
| [ch4](ch4.md) |  |
| [ch5](ch5.md) |  |
| [ch6](ch6.md) |  |
| [ch7](ch7.md) |  |
| [ch8](ch8.md) |  |
| [change_momentum](change_momentum.md) | Allow wakefield to change bunch momentum |
| [change_p0](change_p0.md) | Flag indicating whether the cavity changes reference momentum |
| [channel_names](channel_names.md) | Channel labels |
| [charge](charge.md) | Opposing-beam particle charge in units of the elementary charge |
| [coefficients](coefficients.md) | Polynomial coefficients ordered from lowest to highest degree: ``FieldIntegra... |
| [control_type](control_type.md) | Kind of quantity this variable carries |
| [controls](controls.md) | Control-system process-variable definitions |
| [coupling_cell_length](coupling_cell_length.md) | Length of the coupling cell [m] |
| [covariance](covariance.md) | Beam covariance index |
| [crest](crest.md) | On-crest phase offset providing maximum energy gain [deg] |
| [crest_phase](crest_phase.md) | Cavity crest phase |
| [csr_bins](csr_bins.md) | Number of longitudinal bins for the CSR mesh |
| [csr_enable](csr_enable.md) | Enable coherent synchrotron radiation |
| [csrdz](csrdz.md) | Step size for CSR calculations |
| [current](current.md) | Current carried by the wire [A] |
| [current_bins](current_bins.md) | Number of current bins |
| [d](d.md) | Constant offset term |
| [data_chunk_size](data_chunk_size.md) | Chunk size for one-record traces |
| [data_count](data_count.md) | Number of one-record trace entries |
| [data_size](data_size.md) | Number of points in a trace |
| [datum](datum.md) | Datum reference position |
| [degauss](degauss.md) | Degaussing-cycle parameters |
| [deltaL](deltaL.md) | Longitudinal step-size override for thick-lens integration [m] |
| [density](density.md) | Plasma (electron) number density [m^-^3] |
| [density_profile](density_profile.md) | If True, use a user-defined profile; if False, use a flat-top model |
| [description](description.md) | Human-readable description |
| [design_files](design_files.md) | Design-file paths or URIs |
| [design_gamma](design_gamma.md) | Design Lorentz factor |
| [design_power](design_power.md) | Design peak power [W] |
| [devices](devices.md) | List of attached devices |
| [diagnostic](diagnostic.md) | Instrument-specific diagnostic parameters |
| [dimensional_parameter](dimensional_parameter.md) | Dimensional parameter setting the transverse scale (MAD-X ``cnll``) |
| [disable](disable.md) | Disable command/value |
| [down](down.md) | Down sense value |
| [downstream](downstream.md) | Names of elements this one feeds; the inverse of ``upstream`` |
| [drawings](drawings.md) | Engineering-drawing identifiers or URIs |
| [dt_bunch](dt_bunch.md) | Time-step control for bunch evolution (or 'auto') |
| [dtype](dtype.md) | Data type, held as a Python type and serialised by name (e |
| [dynamics](dynamics.md) | Response model describing how this variable's readback follows its set-point,... |
| [dz_fields](dz_fields.md) | Interval for plasma wakefield updates |
| [edge1_effects](edge1_effects.md) | Enable entrance-edge focussing effects |
| [edge2_effects](edge2_effects.md) | Enable exit-edge focussing effects |
| [edge_field_integral](edge_field_integral.md) | Fringe-field integral for edge focussing |
| [edge_order](edge_order.md) | Polynomial order of the edge-field expansion |
| [electrical](electrical.md) | Power-supply electrical limits |
| [element](element.md) | Name of the reference element |
| [elements](elements.md) | Ordered list of element names in this section |
| [enable](enable.md) | Enable command/value |
| [end](end.md) | End time |
| [end1_focus](end1_focus.md) | Apply entrance focusing |
| [end2_focus](end2_focus.md) | Apply exit focusing |
| [entrance_edge_angle](entrance_edge_angle.md) | Fringe-field entrance edge angle [rad] |
| [equal_grid](equal_grid.md) | Interpolation between equidistant and equal-charge grids |
| [error](error.md) | Alignment errors |
| [eta_x](eta_x.md) | Horizontal dispersion |
| [eta_xp](eta_xp.md) | Horizontal dispersion derivative |
| [eta_y](eta_y.md) | Vertical dispersion |
| [eta_yp](eta_yp.md) | Vertical dispersion derivative |
| [exit_edge_angle](exit_edge_angle.md) | Fringe-field exit edge angle [rad] |
| [expression](expression.md) | Expression graph computing the value written to ``target``, as nested mapping... |
| [ez_peak](ez_peak.md) | Peak longitudinal electric field |
| [f](f.md) | Saturation fraction (slope ratio below/above I_max) |
| [factor](factor.md) | Wake scaling factor |
| [field_amplitude](field_amplitude.md) | Field amplitude scaling |
| [field_definition](field_definition.md) | Path to the 3-D field-map file |
| [field_file_name](field_file_name.md) | Cavity field file name |
| [field_integral_coefficients](field_integral_coefficients.md) | Polynomial calibration of integrated field vs |
| [field_reference_position](field_reference_position.md) | Longitudinal origin of the field map [m] |
| [fields](fields.md) | Nominal integrated axial field components |
| [flatness](flatness.md) | Flatness order N of a flattened-Gaussian profile (for ``profile_type = flatte... |
| [flipped_horizontally](flipped_horizontally.md) | True if the image is mirrored left-right |
| [flipped_vertically](flipped_vertically.md) | True if the image is mirrored top-bottom |
| [focal_position](focal_position.md) | Focal (waist) position along the propagation axis [m] |
| [forward_channel](forward_channel.md) | Forward channel index |
| [frequency](frequency.md) | Operating frequency [Hz] |
| [fringe_field_coefficient](fringe_field_coefficient.md) | Coefficient controlling the fringe-field roll-off rate |
| [from_beam](from_beam.md) | Compute transform from tracked beam properties |
| [gap](gap.md) | Full gap between pole faces [m] |
| [global_rotation](global_rotation.md) | Accumulated global rotation including parent-frame contributions |
| [gradient](gradient.md) | Peak field gradient [T/m] (quads) or peak field [T] (dipoles) |
| [gradient_calibration](gradient_calibration.md) | Calibration relating measured signal to gradient [MV/m per a |
| [hardware_class](hardware_class.md) | Functional category (e |
| [hardware_model](hardware_model.md) | Model or variant name within the hardware type (e |
| [hardware_type](hardware_type.md) | Python class name used for ELEMENT_REGISTRY dispatch |
| [has_camera](has_camera.md) | Whether the screen has an associated camera |
| [has_led](has_led.md) | True if the camera mount includes an LED backlight |
| [heartbeat](heartbeat.md) | RF heartbeat parameters |
| [helical](helical.md) | True for a helical device, False for planar |
| [horizontal_channel](horizontal_channel.md) | Horizontal control channel index |
| [Horizontal_Corrector](Horizontal_Corrector.md) | Name of the horizontal-plane corrector element |
| [horizontal_field](horizontal_field.md) | Horizontal deflecting electric field [V/m] |
| [horizontal_kick](horizontal_kick.md) | Horizontal deflection [rad] |
| [horizontal_offset](horizontal_offset.md) | Horizontal wire offset from the reference orbit [m] |
| [horizontal_sigma](horizontal_sigma.md) | Horizontal RMS size of the opposing bunch [m] |
| [horizontal_size](horizontal_size.md) | Full horizontal aperture [m] |
| [I0](I0.md) | Current offset [A] |
| [I_max](I_max.md) | Current at which saturation begins [A] |
| [identifier](identifier.md) | Protocol-specific PV name (e |
| [initial_position](initial_position.md) | Initial longitudinal position of the laser pulse [m] |
| [inputs](inputs.md) | Signal types this element consumes (e |
| [integrated_strength](integrated_strength.md) | Integrated lens strength (MAD-X ``knll``) |
| [integration_order](integration_order.md) | Order of the symplectic integrator |
| [intensity](intensity.md) | Measured photon intensity |
| [interaction_length](interaction_length.md) | Effective interaction length [m] |
| [interlocks](interlocks.md) | Names of the interlocks guarding this shutter |
| [interpolate](interpolate.md) | Interpolate points in wake file |
| [interpolate_current_bins](interpolate_current_bins.md) | Flag indicating current-bin interpolation |
| [interpolation_method](interpolation_method.md) | Interpolation method for ASTRA |
| [isr_enable](isr_enable.md) | Enable incoherent synchrotron-radiation emittance growth |
| [K0L](K0L.md) | Integrated dipole field |
| [K1L](K1L.md) | Integrated quadrupole gradient |
| [K2L](K2L.md) | Integrated sextupole strength |
| [K3L](K3L.md) | Integrated octupole strength |
| [K4L](K4L.md) | Integrated decapole strength |
| [Kd](Kd.md) | Derivative gain |
| [Ki](Ki.md) | Integral gain |
| [klystron_forward](klystron_forward.md) | Timing for klystron forward power |
| [klystron_reverse](klystron_reverse.md) | Timing for klystron reverse power |
| [knl](knl.md) | Integrated normal multipole strengths, dipole through decapole |
| [Kp](Kp.md) | Proportional gain |
| [ksl](ksl.md) | Integrated skew multipole strengths, dipole through decapole |
| [L](L.md) | Effective magnetic length [m] |
| [laguerre_polynomial_order_p](laguerre_polynomial_order_p.md) | Radial Laguerre-Gaussian mode index p (for ``profile_type = laguerre-gaussian... |
| [laser](laser.md) | Laser-beam parameters |
| [layouts](layouts.md) | All named beamline layouts |
| [left](left.md) | Left sense value |
| [length](length.md) | Effective length along the beam axis [m] |
| [lights](lights.md) | Lighting configuration |
| [linear_saturation_coefficients](linear_saturation_coefficients.md) | Bi-linear saturation calibration |
| [llrf](llrf.md) | LLRF parameters |
| [lsc_bins](lsc_bins.md) | Number of bins used in longitudinal space-charge calculations |
| [lsc_enable](lsc_enable.md) | Enable LSC drift calculations |
| [lsc_high_frequency_cutoff_end](lsc_high_frequency_cutoff_end.md) | High-frequency cutoff end for LSC |
| [lsc_high_frequency_cutoff_start](lsc_high_frequency_cutoff_start.md) | High-frequency cutoff start for LSC |
| [lsc_interpolate](lsc_interpolate.md) | Flag to allow interpolation of computed LSC wake |
| [lsc_low_frequency_cutoff_end](lsc_low_frequency_cutoff_end.md) | Low-frequency cutoff end for LSC |
| [lsc_low_frequency_cutoff_start](lsc_low_frequency_cutoff_start.md) | Low-frequency cutoff start for LSC |
| [m](m.md) | Linear slope of the unsaturated region |
| [machine_area](machine_area.md) | Machine area label grouping related elements (e |
| [magnetic](magnetic.md) | Magnetic field parameters |
| [manufacturer](manufacturer.md) | Name of the manufacturer |
| [mask](mask.md) | Camera analysis mask configuration |
| [master_lattice](master_lattice.md) | Name of the master lattice this section belongs to |
| [max](max.md) | Maximum value |
| [max_amplitude](max_amplitude.md) | Maximum allowed amplitude |
| [max_i](max_i.md) | Maximum current [A] |
| [max_longitudinal_position](max_longitudinal_position.md) | Maximum longitudinal position [m] |
| [maximum](maximum.md) | Maximum mask radius in pixels [x, y] |
| [mechanical_middle](mechanical_middle.md) | Mechanical center of the camera in pixels [x, y] |
| [middle](middle.md) | Longitudinal midpoint (centre) of the element |
| [min](min.md) | Minimum value |
| [min_i](min_i.md) | Minimum current [A] |
| [min_longitudinal_position](min_longitudinal_position.md) | Minimum longitudinal position [m] |
| [minimum](minimum.md) | Minimum pixel positions [x, y] |
| [mode_denominator](mode_denominator.md) | Mode fraction denominator |
| [mode_numerator](mode_numerator.md) | Mode fraction numerator |
| [modulator](modulator.md) | Modulator parameters |
| [multipoles](multipoles.md) | Integrated multipole field components |
| [n_cells](n_cells.md) | Number of cells |
| [n_kicks](n_kicks.md) | Number of integration kicks |
| [n_longitudinal](n_longitudinal.md) | Number of grid points in the longitudinal direction |
| [n_out](n_out.md) | Number of distribution dumps during the plasma stage |
| [n_particles](n_particles.md) | Number of particles in the opposing bunch |
| [n_radial](n_radial.md) | Number of grid points in the radial direction |
| [n_slices](n_slices.md) | Number of longitudinal slices for thick-lens tracking |
| [name](name.md) | Unique element name within the machine |
| [negative_extent](negative_extent.md) | Upstream / inner extent [m] |
| [nonlinear](nonlinear.md) | Include higher-order (sextupole+) field components |
| [normal](normal.md) | Integrated normal (upright) multipole strength [T |
| [num_periods](num_periods.md) | Number of full magnetic periods |
| [number_of_elements](number_of_elements.md) | Number of aperture sub-elements (e |
| [number_of_start_zeros](number_of_start_zeros.md) | Number of leading zeros in a trace |
| [offset](offset.md) | Offset expressed in the reference element's local frame at the chosen point |
| [operating_middle](operating_middle.md) | Operating center positions in pixels [x, y] |
| [order](order.md) | Multipole order (0 = dipole, 1 = quadrupole, ?) |
| [output_filename](output_filename.md) | Output filename for diagnostic data |
| [outputs](outputs.md) | Signal types this element produces (e |
| [parabolic_coefficient](parabolic_coefficient.md) | Parabolic coefficient for a transverse density profile |
| [peak_magnetic_field](peak_magnetic_field.md) | Peak on-axis field [T] |
| [period](period.md) | Magnetic period length [m] |
| [phase](phase.md) | Operating phase offset [deg] |
| [phase_range](phase_range.md) | Phase tuning range |
| [phase_weight_range](phase_weight_range.md) | Phase weighting range |
| [phi](phi.md) | Rotation about the horizontal (x) axis [rad] |
| [physical](physical.md) | Position, rotation, and length data |
| [physical_angle](physical_angle.md) | Bending angle in the horizontal plane [rad] |
| [pid](pid.md) | PID gain parameters |
| [pixel_results_indices](pixel_results_indices.md) | Indices of pixel analysis result arrays |
| [pixel_results_names](pixel_results_names.md) | Names of pixel analysis result arrays |
| [plane](plane.md) | Principal bending / focusing plane (``Horizontal``, ``Vertical``, or ``Combin... |
| [plasma](plasma.md) | Plasma channel parameters |
| [plasma_particles_per_cell](plasma_particles_per_cell.md) | Number of plasma particles per cell |
| [plasma_pusher](plasma_pusher.md) | Pusher used to evolve the plasma in time |
| [plateau](plateau.md) | Flat-top plateau length [m] |
| [pnl](pnl.md) | Normal multipole phases [deg], dipole through decapole |
| [point](point.md) | Which point on the reference element to use as the origin frame: 'start', 'mi... |
| [polarization](polarization.md) | Laser polarization state |
| [position](position.md) | Positional misalignment error [m] |
| [positive_extent](positive_extent.md) | Downstream / outer extent [m] |
| [power_calibration](power_calibration.md) | Calibration constant relating measured power to cavity gradient |
| [probe_channel](probe_channel.md) | Probe channel index |
| [profile_type](profile_type.md) | Transverse intensity profile model |
| [prot_type](prot_type.md) | Protection system type |
| [protection](protection.md) | RF protection parameters |
| [protocol](protocol.md) | Control-system protocol (e |
| [psi](psi.md) | Rotation about the vertical (y) axis [rad] |
| [psl](psl.md) | Skew multipole phases [deg], dipole through decapole |
| [pulse_duration_fwhm](pulse_duration_fwhm.md) | Pulse duration at FWHM [s] |
| [pulse_energy](pulse_energy.md) | Laser pulse energy [J] |
| [quadratic_roll_off_x](quadratic_roll_off_x.md) | Quadratic field roll-off in x [1/m^2] |
| [quadratic_roll_off_y](quadratic_roll_off_y.md) | Quadratic field roll-off in y [1/m^2] |
| [r_matrix](r_matrix.md) | R-matrix (first-order transfer matrix) |
| [r_max](r_max.md) | Radial extent of the simulation box [m] |
| [r_max_plasma](r_max_plasma.md) | Maximum radial extension of the plasma column |
| [radius](radius.md) | Radius for circular apertures [m] |
| [ramp](ramp.md) | Turn numbers [ramp1, ramp2, ramp3, ramp4] defining the drive ramp |
| [ramp_decay_length](ramp_decay_length.md) | Exponential decay length of the density ramp [m] |
| [ramp_down](ramp_down.md) | Exit density-ramp length [m] |
| [ramp_up](ramp_up.md) | Entrance density-ramp length [m] |
| [random_fields](random_fields.md) | Random field errors |
| [random_multipoles](random_multipoles.md) | Random multipole errors at the reference radius |
| [read_only](read_only.md) | Whether the variable is read-only |
| [read_tolerance](read_tolerance.md) | Read-back vs |
| [readback](readback.md) | Name of the readback variable this set-point drives |
| [reference](reference.md) | Links to design drawings and files |
| [reference_placement](reference_placement.md) | Place this element relative to another element's frame instead of using absol... |
| [right](right.md) | Right sense value |
| [rotation](rotation.md) | Angular misalignment error [rad] |
| [s](s.md) | Arc-length position [m] along the design trajectory (s=0 at the global origin... |
| [S0L](S0L.md) | Integrated solenoid field, order 0 [T |
| [S10L](S10L.md) | Integrated solenoid field, order 10 [T |
| [S11L](S11L.md) | Integrated solenoid field, order 11 [T |
| [S12L](S12L.md) | Integrated solenoid field, order 12 [T |
| [S1L](S1L.md) | Integrated solenoid field, order 1 [T |
| [S2L](S2L.md) | Integrated solenoid field, order 2 [T |
| [S3L](S3L.md) | Integrated solenoid field, order 3 [T |
| [S4L](S4L.md) | Integrated solenoid field, order 4 [T |
| [S5L](S5L.md) | Integrated solenoid field, order 5 [T |
| [S6L](S6L.md) | Integrated solenoid field, order 6 [T |
| [S7L](S7L.md) | Integrated solenoid field, order 7 [T |
| [S8L](S8L.md) | Integrated solenoid field, order 8 [T |
| [S9L](S9L.md) | Integrated solenoid field, order 9 [T |
| [s_offset](s_offset.md) | Scalar offset [m] along the local beam direction (s-axis) from the reference ... |
| [s_point](s_point.md) | Which point of the element the ``s`` value refers to: ``start``, ``middle``, ... |
| [scale_field](scale_field.md) | Multiplicative scale factor applied to the field map |
| [scale_field_ex](scale_field_ex.md) | x-component of the longitudinal direction vector |
| [scale_field_ey](scale_field_ey.md) | y-component of the longitudinal direction vector |
| [scale_field_ez](scale_field_ez.md) | z-component of the longitudinal direction vector |
| [scale_field_hx](scale_field_hx.md) | x-component of the horizontal direction vector |
| [scale_field_hy](scale_field_hy.md) | y-component of the horizontal direction vector |
| [scale_field_hz](scale_field_hz.md) | z-component of the horizontal direction vector |
| [scale_kick](scale_kick.md) | Factor by which to scale wake kicks |
| [screen_name](screen_name.md) | Name of the screen element to which this camera is attached |
| [sections](sections.md) | Ordered list of section names |
| [sense](sense.md) | Mirror sense/interlock configuration |
| [sensor](sensor.md) | Camera sensor hardware configuration |
| [serial_number](serial_number.md) | Manufacturer serial number |
| [setpoint](setpoint.md) | Name of the set-point variable this readback follows |
| [settle_time](settle_time.md) | Power-supply settle time after a change [s] |
| [shape](shape.md) | Cross-sectional aperture shape |
| [shunt_impedance](shunt_impedance.md) | Shunt impedance [M?/m] |
| [shutter](shutter.md) | Shutter interlock configuration |
| [simulation](simulation.md) | Simulation / tracking attributes |
| [skew](skew.md) | Integrated skew (rotated) multipole strength [T |
| [smooth](smooth.md) | Number of smoothing passes applied to the field map (ASTRA Q_smooth / S_smoot... |
| [smooth_current_bins](smooth_current_bins.md) | Flag indicating current-bin smoothing |
| [smooth_points](smooth_points.md) | Number of points used to smooth the field map [ASTRA] |
| [smoothing_half_width](smoothing_half_width.md) | Half-width of the current-profile smoothing kernel |
| [species](species.md) | Plasma species name (e |
| [sr_enable](sr_enable.md) | Enable synchrotron-radiation energy loss |
| [start](start.md) | Start time |
| [states](states.md) | Mapping of state name to underlying control-system value, for ``control_type:... |
| [step_max](step_max.md) | Maximum step size for mirror adjustment |
| [steps](steps.md) | Number of degauss steps per half-cycle |
| [strength](strength.md) | Deflection parameter K |
| [structure_type](structure_type.md) | RF structure type (e |
| [subbins](subbins.md) | Sub-binning parameter |
| [subelement](subelement.md) | If set, this element is a logical sub-component of the named parent element |
| [survey](survey.md) | Survey-measured position and rotation |
| [systematic_fields](systematic_fields.md) | Systematic field errors |
| [systematic_multipoles](systematic_multipoles.md) | Systematic (design) multipole errors at the reference radius |
| [t_column](t_column.md) | Time column in the wake file |
| [t_matrix](t_matrix.md) | T-matrix (second-order transfer tensor) |
| [target](target.md) | Dotted attribute path on the owning element that ``expression`` writes to (e |
| [theta](theta.md) | Rotation about the longitudinal (z) axis [rad] |
| [tilt](tilt.md) | Rotation about the beam axis [rad] |
| [timings](timings.md) | Timing windows for LLRF channels |
| [tolerance](tolerance.md) | Current tolerance band during the degauss cycle [A] |
| [trace](trace.md) | Trace metadata |
| [transverse_gradient_x](transverse_gradient_x.md) | Transverse field gradient in x [1/m] |
| [transverse_gradient_y](transverse_gradient_y.md) | Transverse field gradient in y [1/m] |
| [trwakefile](trwakefile.md) | Transverse wake file name |
| [type](type.md) | BPM type (e |
| [units](units.md) | Physical units string (e |
| [up](up.md) | Up sense value |
| [update](update.md) | Signal generating this variable's value over time, as ``{function: <import pa... |
| [upstream](upstream.md) | Names of elements feeding this one, whose ``outputs`` supply its ``inputs`` |
| [use_maximum_values](use_maximum_values.md) | If True, use maximum mask radius constraints |
| [use_stupakov](use_stupakov.md) | Use Stupakov formula |
| [value](value.md) | Last-read value |
| [values](values.md) | Sequence of peak currents applied during the degauss cycle [A] |
| [valve](valve.md) | Valve configuration |
| [variables](variables.md) | Named control variables keyed by logical name |
| [vertical_channel](vertical_channel.md) | Vertical control channel index |
| [Vertical_Corrector](Vertical_Corrector.md) | Name of the vertical-plane corrector element |
| [vertical_field](vertical_field.md) | Vertical deflecting electric field [V/m] |
| [vertical_kick](vertical_kick.md) | Vertical deflection [rad] |
| [vertical_offset](vertical_offset.md) | Vertical wire offset from the reference orbit [m] |
| [vertical_sigma](vertical_sigma.md) | Vertical RMS size of the opposing bunch [m] |
| [vertical_size](vertical_size.md) | Full vertical aperture [m] |
| [virtual_name](virtual_name.md) | Alternative internal name used by the control system when the physical name i... |
| [waist](waist.md) | Laser beam waist (1/e^2 radius) [m] |
| [wakefield_definition](wakefield_definition.md) | Path to the wakefield impedance file |
| [wakefield_enable](wakefield_enable.md) | Whether the wakefield named by wakefield_definition is applied |
| [wakefield_model](wakefield_model.md) | Wakefield model identifier |
| [wakefile](wakefile.md) | Wake file name |
| [wavelength](wavelength.md) | Laser wavelength [m] |
| [width](width.md) | Opposing-bunch length for the 3-D weak-strong model [m] |
| [world_offset](world_offset.md) | Offset already expressed in global world coordinates |
| [wx_column](wx_column.md) | Horizontal wake column in the wake file |
| [wy_column](wy_column.md) | Vertical wake column in the wake file |
| [wz_column](wz_column.md) | Longitudinal wake column in the wake file |
| [x](x.md) | Horizontal component [m] |
| [x_pixels](x_pixels.md) | Raw sensor pixel count in x |
| [x_pixels_to_mm](x_pixels_to_mm.md) | Pixel-to-mm scale factor in x |
| [x_scale_factor](x_scale_factor.md) | Pixel binning factor in x |
| [x_sigma](x_sigma.md) | Beam sigma index in x |
| [y](y.md) | Vertical component [m] |
| [y_pixels](y_pixels.md) | Raw sensor pixel count in y |
| [y_pixels_to_mm](y_pixels_to_mm.md) | Pixel-to-mm scale factor in y |
| [y_scale_factor](y_scale_factor.md) | Pixel binning factor in y |
| [y_sigma](y_sigma.md) | Beam sigma index in y |
| [z](z.md) | Longitudinal (beam-direction) component [m] |
| [z_column](z_column.md) | Longitudinal position column in the wake file |
| [zwakefile](zwakefile.md) | Longitudinal wake file name |


## Enumerations

| Enumeration | Description |
| --- | --- |
| [ApertureShapeEnum](ApertureShapeEnum.md) | Cross-sectional shape of a beam-pipe aperture |
| [BendingPlaneEnum](BendingPlaneEnum.md) | Bending plane enum |
| [ControlTypeEnum](ControlTypeEnum.md) | Kind of quantity a control variable carries |
| [HardwareClassEnum](HardwareClassEnum.md) | High-level category organising elements by function within the accelerator |
| [IOTypeEnum](IOTypeEnum.md) | Input types for accelerator elements |
| [LaserPolarizationEnum](LaserPolarizationEnum.md) | Polarization state of a laser beam |
| [LaserProfileTypeEnum](LaserProfileTypeEnum.md) | Transverse intensity profile model for a laser beam |


## Types

| Type | Description |
| --- | --- |
| [Boolean](Boolean.md) | A binary (true or false) value |
| [Curie](Curie.md) | a compact URI |
| [Date](Date.md) | a date (year, month and day) in an idealized calendar |
| [DateOrDatetime](DateOrDatetime.md) | Either a date or a datetime |
| [Datetime](Datetime.md) | The combination of a date and time |
| [Decimal](Decimal.md) | A real number with arbitrary precision that conforms to the xsd:decimal speci... |
| [Double](Double.md) | A real number that conforms to the xsd:double specification |
| [Float](Float.md) | A real number that conforms to the xsd:float specification |
| [Integer](Integer.md) | An integer |
| [Jsonpath](Jsonpath.md) | A string encoding a JSON Path |
| [Jsonpointer](Jsonpointer.md) | A string encoding a JSON Pointer |
| [Ncname](Ncname.md) | Prefix part of CURIE |
| [Nodeidentifier](Nodeidentifier.md) | A URI, CURIE or BNODE that represents a node in a model |
| [Objectidentifier](Objectidentifier.md) | A URI or CURIE that represents an object in the model |
| [Sparqlpath](Sparqlpath.md) | A string encoding a SPARQL Property Path |
| [String](String.md) | A character string |
| [Time](Time.md) | A time object represents a (local) time of day, independent of any particular... |
| [Uri](Uri.md) | a complete URI |
| [Uriorcurie](Uriorcurie.md) | a URI or a CURIE |


## Subsets

| Subset | Description |
| --- | --- |
| [BendAngleReference](BendAngleReference.md) | Slots that additionally accept an expression referencing the dipole bend angl... |
| [DiagnosticProperties](DiagnosticProperties.md) | Slots specific to beam-diagnostic instruments |
| [FunctionalParameters](FunctionalParameters.md) | Slots whose value may be the name of a functional definition (a symbolic para... |
| [LaserProperties](LaserProperties.md) | Slots specific to laser-related elements |
| [MagneticProperties](MagneticProperties.md) | Slots specific to magnetic elements |
| [PhysicalProperties](PhysicalProperties.md) | Slots relevant to the physical placement or geometry of an element |
| [RfProperties](RfProperties.md) | Slots specific to RF cavity elements |
