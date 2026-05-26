# LAURA Accelerator Element Schema

Linked Data schema for the LAURA (Lattice And Unified Representation of Accelerators) accelerator element model.  Covers all element types, their physical, magnetic, diagnostic, RF, and control-system properties.

URI: https://w3id.org/laura/schema

Name: laura_schema



## Classes

| Class | Description |
| --- | --- |
| [AcceleratorElement](AcceleratorElement.md) | Root base class for all LAURA accelerator elements |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[StandardElement](StandardElement.md) | Accelerator element with control-system, electrical, manufacturer, simulation... |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[LaserAttenuator](LaserAttenuator.md) | Laser power attenuator (waveplate + polariser combination) |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[LaserEnergyMeter](LaserEnergyMeter.md) | Laser pulse-energy diagnostic (photodiode / pyroelectric) |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[LaserHalfWavePlate](LaserHalfWavePlate.md) | Half-wave plate for laser polarisation rotation |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[LaserMirror](LaserMirror.md) | Laser steering or focusing mirror |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[Lighting](Lighting.md) | Experimental-hall lighting element |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[LowLevelRF](LowLevelRF.md) | Low-level RF (LLRF) controller |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[PhysicalAcceleratorElement](PhysicalAcceleratorElement.md) | Accelerator element with a well-defined physical position and orientation in ... |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[Aperture](Aperture.md) | Mechanical aperture restriction in the beam pipe |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[Collimator](Collimator.md) | Movable collimator jaw (extends Aperture) |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[Diagnostic](Diagnostic.md) | Base class for all beam-diagnostic instruments |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[BeamArrivalMonitor](BeamArrivalMonitor.md) | Beam-arrival-time monitor (BAM) |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[BeamPositionMonitor](BeamPositionMonitor.md) | Beam-position monitor (BPM) |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[BunchLengthMonitor](BunchLengthMonitor.md) | Bunch-length monitor (BLM / CDR detector) |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[Camera](Camera.md) | Camera-based beam-profile monitor |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[ChargeDiagnostic](ChargeDiagnostic.md) | Base class for charge-measurement diagnostics |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[FaradayCupMonitor](FaradayCupMonitor.md) | Faraday cup for destructive charge measurement |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[IntegratedCurrentTransformer](IntegratedCurrentTransformer.md) | Integrated current transformer (ICT) for non-destructive single-shot charge m... |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[WallCurrentMonitor](WallCurrentMonitor.md) | Wall-current monitor (WCM) for non-destructive charge measurement |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[Screen](Screen.md) | Scintillator or OTR screen with an associated camera |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[Drift](Drift.md) | Field-free drift space between elements |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[Laser](Laser.md) | Laser system element (full laser setup including beam parameters) |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[MagnetBaseElement](MagnetBaseElement.md) | Base class for all magnetic focusing and bending elements |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[Dipole](Dipole.md) | Dipole bending magnet |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[CombinedCorrector](CombinedCorrector.md) | Combined horizontal and vertical orbit-corrector magnet |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[HorizontalCorrector](HorizontalCorrector.md) | Horizontal orbit-corrector dipole |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[VerticalCorrector](VerticalCorrector.md) | Vertical orbit-corrector dipole |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[NonLinearLens](NonLinearLens.md) | Non-linear focusing lens (IOTA-style) |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[Octupole](Octupole.md) | Octupole magnet |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[Quadrupole](Quadrupole.md) | Quadrupole focusing magnet |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[Sextupole](Sextupole.md) | Sextupole chromaticity-correction magnet |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[Solenoid](Solenoid.md) | Solenoid focussing magnet |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[Wiggler](Wiggler.md) | Wiggler / undulator permanent-magnet array |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[Marker](Marker.md) | Virtual survey marker -- a zero-length reference point used for alignment |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[Plasma](Plasma.md) | Laser-driven plasma-accelerator stage |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[RFCavity](RFCavity.md) | Accelerating RF cavity |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[RFDeflectingCavity](RFDeflectingCavity.md) | Transverse-deflecting (streak) RF cavity |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[Shutter](Shutter.md) | Beam or laser shutter with interlock logic |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[Stage](Stage.md) | Motorised positioning stage |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[TwissMatch](TwissMatch.md) | Virtual Twiss-parameter matching point -- a zero-length marker that defines t... |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[VacuumGauge](VacuumGauge.md) | Vacuum-pressure gauge |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[Valve](Valve.md) | Vacuum gate valve |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[Wakefield](Wakefield.md) | Passive wakefield structure (dielectric, corrugated, etc |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[PID](PID.md) | Proportional-integral-derivative (PID) feedback controller |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[RFHeartbeat](RFHeartbeat.md) | RF timing heartbeat / signal-monitor element |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[RFModulator](RFModulator.md) | RF modulator (klystron driver) element |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[RFProtection](RFProtection.md) | RF protection system element |
| [ApertureElement](ApertureElement.md) | Transverse aperture geometry for drift-space checks and collimators |
| [ControlsInformation](ControlsInformation.md) | Collection of process-variable definitions for an element's control interface |
| [ControlVariable](ControlVariable.md) | A single process-variable entry mapping a logical name to a control-system PV... |
| [DegaussableElement](DegaussableElement.md) | Degaussing (demagnetisation cycle) parameters for magnets that require a fiel... |
| [DiagnosticElement](DiagnosticElement.md) | Base class for diagnostic instrument sub-models |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[BAMDiagnosticElement](BAMDiagnosticElement.md) | Beam-arrival monitor (BAM) diagnostic data |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[BLMDiagnosticElement](BLMDiagnosticElement.md) | Bunch-length monitor (BLM) diagnostic data |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[BPMDiagnosticElement](BPMDiagnosticElement.md) | Beam-position monitor (BPM) diagnostic data |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[CameraDiagnosticElement](CameraDiagnosticElement.md) | Camera diagnostic data, including sensor parameters, analysis mask, and pixel... |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[ChargeDiagnosticElement](ChargeDiagnosticElement.md) | Charge-measurement diagnostic data (base for ICT, FCM, WCM) |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[ScreenDiagnosticElement](ScreenDiagnosticElement.md) | Scintillator or OTR screen diagnostic data |
| [ElectricalElement](ElectricalElement.md) | Power-supply electrical limits for a beamline element |
| [ElementPositionError](ElementPositionError.md) | Alignment position and rotation errors for a physically-located element |
| [ElementSurvey](ElementSurvey.md) | Survey-measured position and rotation of an element |
| [FieldIntegral](FieldIntegral.md) | Polynomial fit of integrated field strength as a function of magnet current |
| [LaserElement](LaserElement.md) | Laser-beam parameters (wavelength, pulse energy, profile, etc |
| [LaserEnergyMeterElement](LaserEnergyMeterElement.md) | Laser energy-meter sub-model (no additional fields) |
| [LaserHalfWavePlateElement](LaserHalfWavePlateElement.md) | Half-wave plate sub-model (no additional fields) |
| [LightingElement](LightingElement.md) | Lighting element (no additional fields currently defined) |
| [LinearSaturationFit](LinearSaturationFit.md) | Bi-linear saturation model mapping magnet current to integrated field strengt... |
| [LowLevelRFElement](LowLevelRFElement.md) | Low-level RF (LLRF) system parameters |
| [MachineLayout](MachineLayout.md) | An ordered list of section names defining a beamline layout (a contiguous seq... |
| [MachineModel](MachineModel.md) | Top-level container for a complete accelerator lattice: elements, sections, l... |
| [MagneticElement](MagneticElement.md) | Magnetic field parameters for a beamline magnet, including multipole componen... |
| [ManufacturerElement](ManufacturerElement.md) | Manufacturer and serial-number metadata |
| [Multipole](Multipole.md) | Individual multipole field component, characterised by order and integrated n... |
| [Multipoles](Multipoles.md) | Complete set of integrated multipole strengths up to decapole order, as named... |
| [PhysicalElement](PhysicalElement.md) | Physical placement data: position, rotation, length, and associated survey / ... |
| [PIDElement](PIDElement.md) | PID feedback-controller parameters |
| [PlasmaElement](PlasmaElement.md) | Plasma channel parameters for a laser-driven plasma-accelerator stage |
| [Position](Position.md) | Cartesian position in the global accelerator coordinate system |
| [ReferenceElement](ReferenceElement.md) | Links to engineering drawings and design files |
| [RFCavityElement](RFCavityElement.md) | RF cavity accelerating-structure parameters |
| [RFDeflectingCavityElement](RFDeflectingCavityElement.md) | Transverse-deflecting RF cavity parameters -- a subset of RFCavityElement for... |
| [RFHeartbeatElement](RFHeartbeatElement.md) | RF heartbeat / timing-monitor element parameters |
| [RFModulatorElement](RFModulatorElement.md) | RF modulator (klystron driver) parameters |
| [RFProtectionElement](RFProtectionElement.md) | RF protection system parameters |
| [Rotation](Rotation.md) | Euler-angle rotation relative to the global coordinate system |
| [SectionLattice](SectionLattice.md) | An ordered list of element names defining a contiguous beamline section |
| [ShutterElement](ShutterElement.md) | Shutter interlock configuration |
| [SimulationElement](SimulationElement.md) | Base simulation attributes: field-map files and reference positions for track... |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[DiagnosticSimulationElement](DiagnosticSimulationElement.md) | Simulation attributes for beam-diagnostic elements |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[DriftSimulationElement](DriftSimulationElement.md) | Simulation attributes for field-free drift sections |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[MagnetSimulationElement](MagnetSimulationElement.md) | Simulation attributes specific to magnets: integrator settings, fringe-field ... |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[PlasmaSimulationElement](PlasmaSimulationElement.md) | Simulation attributes for plasma-accelerator stages |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[RFCavitySimulationElement](RFCavitySimulationElement.md) | Simulation attributes for RF cavity elements |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[TwissMatchSimulationElement](TwissMatchSimulationElement.md) | Simulation attributes for Twiss-matching points |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[WakefieldSimulationElement](WakefieldSimulationElement.md) | Simulation attributes for passive wakefield structures |
| [ValveElement](ValveElement.md) | Vacuum valve configuration (no additional fields) |
| [WakefieldElement](WakefieldElement.md) | Passive wakefield structure parameters |



## Slots

| Slot | Description |
| --- | --- |
| [a](a.md) | Quadratic saturation coefficient |
| [alias](alias.md) | Short human-readable alias |
| [aperture](aperture.md) | Aperture geometry parameters |
| [attenuation_constant](attenuation_constant.md) | Attenuation constant ? of a travelling-wave structure [Np/m] |
| [bore](bore.md) | Magnet bore radius [m] |
| [camera_name](camera_name.md) | Name of the associated camera element |
| [cavity](cavity.md) | RF structure parameters |
| [cell_length](cell_length.md) | Length of a single accelerating cell [m] |
| [cep_phase](cep_phase.md) | Carrier-envelope phase [rad] |
| [coefficients](coefficients.md) | Polynomial coefficients ordered from lowest to highest degree: ``FieldIntegra... |
| [controls](controls.md) | Control-system process-variable definitions |
| [coupling_cell_length](coupling_cell_length.md) | Length of a coupling cell [m] |
| [crest](crest.md) | On-crest phase offset providing maximum energy gain [deg] |
| [csr_bins](csr_bins.md) | Number of longitudinal bins for the CSR mesh |
| [csr_enable](csr_enable.md) | Enable coherent synchrotron radiation |
| [d](d.md) | Constant offset term |
| [datum](datum.md) | Datum reference position |
| [degauss](degauss.md) | Degaussing-cycle parameters |
| [deltaL](deltaL.md) | Longitudinal step-size override for thick-lens integration [m] |
| [density](density.md) | Plasma (electron) number density [m^-^3] |
| [density_profile](density_profile.md) | If True, use a user-defined profile; if False, use a flat-top model |
| [description](description.md) | Human-readable description |
| [design_files](design_files.md) | Design-file paths or URIs |
| [design_gamma](design_gamma.md) | Relativistic Lorentz factor ? at design operating point |
| [design_power](design_power.md) | Design peak RF power [W] |
| [diagnostic](diagnostic.md) | Instrument-specific diagnostic parameters |
| [drawings](drawings.md) | Engineering-drawing identifiers or URIs |
| [dtype](dtype.md) | Data type (e |
| [edge1_effects](edge1_effects.md) | Enable entrance-edge focussing effects |
| [edge2_effects](edge2_effects.md) | Enable exit-edge focussing effects |
| [edge_field_integral](edge_field_integral.md) | Fringe-field integral for edge focussing |
| [edge_order](edge_order.md) | Polynomial order of the edge-field expansion |
| [electrical](electrical.md) | Power-supply electrical limits |
| [elements](elements.md) | Ordered list of element names in this section |
| [entrance_edge_angle](entrance_edge_angle.md) | Fringe-field entrance edge angle [rad] |
| [error](error.md) | Alignment errors |
| [exit_edge_angle](exit_edge_angle.md) | Fringe-field exit edge angle [rad] |
| [expression](expression.md) | Optional expression string for derived values |
| [f](f.md) | Saturation fraction (slope ratio below/above I_max) |
| [field_definition](field_definition.md) | Path to the 3-D field-map file |
| [field_integral_coefficients](field_integral_coefficients.md) | Polynomial calibration of integrated field vs |
| [field_reference_position](field_reference_position.md) | Longitudinal origin of the field map [m] |
| [flatness](flatness.md) | Flatness order N of a flattened-Gaussian profile (for ``profile_type = flatte... |
| [flipped_horizontally](flipped_horizontally.md) | True if the image is mirrored left-right |
| [flipped_vertically](flipped_vertically.md) | True if the image is mirrored top-bottom |
| [focal_position](focal_position.md) | Focal (waist) position along the propagation axis [m] |
| [frequency](frequency.md) | RF operating frequency [Hz] |
| [fringe_field_coefficient](fringe_field_coefficient.md) | Coefficient controlling the fringe-field roll-off rate |
| [gap](gap.md) | Full gap between pole faces [m] |
| [global_rotation](global_rotation.md) | Accumulated global rotation including parent-frame contributions |
| [gradient](gradient.md) | Peak field gradient [T/m] (quads) or peak field [T] (dipoles) |
| [gradient_calibration](gradient_calibration.md) | Calibration relating measured signal to gradient [MV/m per a |
| [hardware_class](hardware_class.md) | Functional category (e |
| [hardware_model](hardware_model.md) | Model or variant name within the hardware type (e |
| [hardware_type](hardware_type.md) | Python class name used for MODEL_REGISTRY dispatch |
| [has_camera](has_camera.md) | Whether the screen has an associated camera |
| [has_led](has_led.md) | True if the camera mount includes an LED backlight |
| [heartbeat](heartbeat.md) | RF heartbeat parameters |
| [horizontal_size](horizontal_size.md) | Full horizontal aperture [m] |
| [I0](I0.md) | Current offset [A] |
| [I_max](I_max.md) | Current at which saturation begins [A] |
| [identifier](identifier.md) | Protocol-specific PV name (e |
| [initial_position](initial_position.md) | Initial longitudinal position of the laser pulse [m] |
| [integration_order](integration_order.md) | Order of the symplectic integrator |
| [interlocks](interlocks.md) | Names of the interlocks guarding this shutter |
| [isr_enable](isr_enable.md) | Enable incoherent synchrotron-radiation emittance growth |
| [K0L](K0L.md) | Integrated dipole field |
| [K1L](K1L.md) | Integrated quadrupole gradient |
| [K2L](K2L.md) | Integrated sextupole strength |
| [K3L](K3L.md) | Integrated octupole strength |
| [K4L](K4L.md) | Integrated decapole strength |
| [Kd](Kd.md) | Derivative gain |
| [Ki](Ki.md) | Integral gain |
| [Kp](Kp.md) | Proportional gain |
| [L](L.md) | Effective magnetic length [m] |
| [laguerre_polynomial_order_p](laguerre_polynomial_order_p.md) | Radial Laguerre-Gaussian mode index p (for ``profile_type = laguerre-gaussian... |
| [laser](laser.md) | Laser-beam parameters |
| [layouts](layouts.md) | All named beamline layouts |
| [length](length.md) | Effective length along the beam axis [m] |
| [lights](lights.md) | Lighting configuration |
| [linear_saturation_coefficients](linear_saturation_coefficients.md) | Bi-linear saturation calibration |
| [llrf](llrf.md) | LLRF parameters |
| [m](m.md) | Linear slope of the unsaturated region |
| [machine_area](machine_area.md) | Machine area label grouping related elements (e |
| [magnetic](magnetic.md) | Magnetic field parameters |
| [magnetic_length](magnetic_length.md) | Magnetic (effective) length [m] |
| [manufacturer](manufacturer.md) | Name of the manufacturer |
| [master_lattice](master_lattice.md) | Name of the master lattice this section belongs to |
| [max_i](max_i.md) | Maximum current [A] |
| [maximum](maximum.md) | Maximum attenuation angle [deg] |
| [maximum_position](maximum_position.md) | Maximum downstream s-coordinate [m] |
| [middle](middle.md) | Longitudinal midpoint (centre) of the element |
| [min_i](min_i.md) | Minimum current [A] |
| [minimum](minimum.md) | Minimum attenuation angle [deg] |
| [minimum_position](minimum_position.md) | Minimum upstream s-coordinate [m] |
| [mode_denominator](mode_denominator.md) | Denominator of the operating mode fraction |
| [mode_numerator](mode_numerator.md) | Numerator of the operating mode fraction (e |
| [modulator](modulator.md) | Modulator parameters |
| [multipoles](multipoles.md) | Integrated multipole field components |
| [n_cells](n_cells.md) | Number of accelerating cells |
| [n_kicks](n_kicks.md) | Number of integration kicks |
| [n_slices](n_slices.md) | Number of longitudinal slices for thick-lens tracking |
| [name](name.md) | Unique element name within the machine |
| [negative_extent](negative_extent.md) | Upstream / inner extent [m] |
| [nonlinear](nonlinear.md) | Include higher-order (sextupole+) field components |
| [normal](normal.md) | Integrated normal (upright) multipole strength [T |
| [number_of_elements](number_of_elements.md) | Number of aperture sub-elements (e |
| [order](order.md) | Multipole order (0 = dipole, 1 = quadrupole, ?) |
| [parabolic_coefficient](parabolic_coefficient.md) | Parabolic coefficient for a transverse density profile |
| [phase](phase.md) | Operating phase relative to crest [deg] |
| [phi](phi.md) | Rotation about the horizontal (x) axis [rad] |
| [physical](physical.md) | Position, rotation, and length data |
| [physical_angle](physical_angle.md) | Bending angle in the horizontal plane [rad] |
| [pid](pid.md) | PID gain parameters |
| [plane](plane.md) | Principal bending / focusing plane (``H``, ``V``, or ``HV``) |
| [plasma](plasma.md) | Plasma channel parameters |
| [plateau](plateau.md) | Flat-top plateau length [m] |
| [polarization](polarization.md) | Laser polarization state |
| [position](position.md) | Positional misalignment error [m] |
| [positive_extent](positive_extent.md) | Downstream / outer extent [m] |
| [power_calibration](power_calibration.md) | Calibration constant relating measured power to cavity gradient |
| [profile_type](profile_type.md) | Transverse intensity profile model |
| [protection](protection.md) | RF protection parameters |
| [protocol](protocol.md) | Control-system protocol (e |
| [psi](psi.md) | Rotation about the vertical (y) axis [rad] |
| [pulse_duration_fwhm](pulse_duration_fwhm.md) | Pulse duration at FWHM [s] |
| [pulse_energy](pulse_energy.md) | Laser pulse energy [J] |
| [radius](radius.md) | Reference radius for multipole normalisation [m] |
| [ramp_decay_length](ramp_decay_length.md) | Exponential decay length of the density ramp [m] |
| [ramp_down](ramp_down.md) | Exit density-ramp length [m] |
| [ramp_up](ramp_up.md) | Entrance density-ramp length [m] |
| [random_multipoles](random_multipoles.md) | Random multipole errors at the reference radius |
| [read_only](read_only.md) | Whether the variable is read-only |
| [reference](reference.md) | Links to design drawings and files |
| [ri_tolerance](ri_tolerance.md) | Read-back vs |
| [rotation](rotation.md) | Angular misalignment error [rad] |
| [scale_field](scale_field.md) | Multiplicative scale factor applied to the field map |
| [screen_name](screen_name.md) | Name of the screen element to which this camera is attached |
| [sections](sections.md) | Ordered list of section names |
| [serial_number](serial_number.md) | Manufacturer serial number |
| [settle_time](settle_time.md) | Power-supply settle time after a change [s] |
| [shape](shape.md) | Cross-sectional aperture shape |
| [shunt_impedance](shunt_impedance.md) | Shunt impedance [M?/m] |
| [shutter](shutter.md) | Shutter interlock configuration |
| [simulation](simulation.md) | Simulation / tracking attributes |
| [skew](skew.md) | Integrated skew (rotated) multipole strength [T |
| [smooth](smooth.md) | Use a smoothed field profile |
| [smoothing_half_width](smoothing_half_width.md) | Half-width of the current-profile smoothing kernel |
| [species](species.md) | Plasma species name (e |
| [sr_enable](sr_enable.md) | Enable synchrotron-radiation energy loss |
| [steps](steps.md) | Number of degauss steps per half-cycle |
| [structure_type](structure_type.md) | RF structure type (e |
| [subelement](subelement.md) | If set, this element is a logical sub-component of the named parent element |
| [survey](survey.md) | Survey-measured position and rotation |
| [systematic_multipoles](systematic_multipoles.md) | Systematic (design) multipole errors at the reference radius |
| [target](target.md) | Set-point target value |
| [theta](theta.md) | Rotation about the longitudinal (z) axis [rad] |
| [tilt](tilt.md) | Global tilt about the beam axis [rad] |
| [tolerance](tolerance.md) | Current tolerance band during the degauss cycle [A] |
| [type](type.md) | BPM type (e |
| [units](units.md) | Physical units string (e |
| [value](value.md) | Last-read value |
| [values](values.md) | Sequence of peak currents applied during the degauss cycle [A] |
| [valve](valve.md) | Valve configuration |
| [variables](variables.md) | Named control variables keyed by logical name |
| [vertical_size](vertical_size.md) | Full vertical aperture [m] |
| [virtual_name](virtual_name.md) | Alternative internal name used by the control system when the physical name i... |
| [waist](waist.md) | Laser beam waist (1/e^2 radius) [m] |
| [wakefield_definition](wakefield_definition.md) | Path to the wakefield impedance file |
| [wavelength](wavelength.md) | Laser wavelength [m] |
| [width](width.md) | Physical width of the magnet in the bending plane [m] |
| [x](x.md) | Horizontal component [m] |
| [x_pixels](x_pixels.md) | Image width reported by the control system [pix] |
| [y](y.md) | Vertical component [m] |
| [y_pixels](y_pixels.md) | Image height reported by the control system [pix] |
| [z](z.md) | Longitudinal (beam-direction) component [m] |


## Enumerations

| Enumeration | Description |
| --- | --- |
| [ApertureShapeEnum](ApertureShapeEnum.md) | Cross-sectional shape of a beam-pipe aperture |
| [HardwareClassEnum](HardwareClassEnum.md) | High-level category organising elements by function within the accelerator |
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
| [DiagnosticProperties](DiagnosticProperties.md) | Slots specific to beam-diagnostic instruments |
| [LaserProperties](LaserProperties.md) | Slots specific to laser-related elements |
| [MagneticProperties](MagneticProperties.md) | Slots specific to magnetic elements |
| [PhysicalProperties](PhysicalProperties.md) | Slots relevant to the physical placement or geometry of an element |
| [RfProperties](RfProperties.md) | Slots specific to RF cavity elements |
