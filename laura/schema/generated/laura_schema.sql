-- # Class: Position Description: Cartesian position in the global accelerator coordinate system. All components are in metres.
--     * Slot: id
--     * Slot: x Description: Horizontal component [m].
--     * Slot: y Description: Vertical component [m].
--     * Slot: z Description: Longitudinal (beam-direction) component [m].
-- # Class: Rotation Description: Euler-angle rotation relative to the global coordinate system. All angles are in radians, bounded to [-pi, pi].
--     * Slot: id
--     * Slot: phi Description: Rotation about the horizontal (x) axis [rad].
--     * Slot: psi Description: Rotation about the vertical (y) axis [rad].
--     * Slot: theta Description: Rotation about the longitudinal (z) axis [rad].
-- # Class: ElementPositionError Description: Alignment position and rotation errors for a physically-located element.
--     * Slot: id
--     * Slot: position_id Description: Positional misalignment error [m].
--     * Slot: rotation_id Description: Angular misalignment error [rad].
-- # Class: ElementSurvey Description: Survey-measured position and rotation of an element. Structure is identical to ElementPositionError.
--     * Slot: id
--     * Slot: position_id Description: Surveyed position.
--     * Slot: rotation_id Description: Surveyed rotation.
-- # Class: PhysicalElement Description: Physical placement data: position, rotation, length, and associated survey / alignment-error information.
--     * Slot: id
--     * Slot: length Description: Effective length along the beam axis [m].
--     * Slot: maximum_position Description: Maximum downstream s-coordinate [m].
--     * Slot: minimum_position Description: Minimum upstream s-coordinate [m].
--     * Slot: physical_angle Description: Bending angle in the horizontal plane [rad]. Derived from ``magnetic.angle`` when available.
--     * Slot: middle_id Description: Longitudinal midpoint (centre) of the element. Also accepted as ``position`` or ``centre`` in YAML.
--     * Slot: datum_id Description: Datum reference position.
--     * Slot: rotation_id Description: Local rotation in the global frame.
--     * Slot: global_rotation_id Description: Accumulated global rotation including parent-frame contributions.
--     * Slot: error_id Description: Alignment errors.
--     * Slot: survey_id Description: Survey-measured position and rotation.
-- # Class: ElectricalElement Description: Power-supply electrical limits for a beamline element.
--     * Slot: id
--     * Slot: min_i Description: Minimum current [A].
--     * Slot: max_i Description: Maximum current [A].
--     * Slot: read_tolerance Description: Read-back vs. set-point tolerance fraction (default 0.1 = 10 %).
-- # Class: ManufacturerElement Description: Manufacturer and serial-number metadata.
--     * Slot: id
--     * Slot: manufacturer Description: Name of the manufacturer.
--     * Slot: serial_number Description: Manufacturer serial number.
-- # Class: ReferenceElement Description: Links to engineering drawings and design files.
--     * Slot: id
-- # Class: ControlVariable Description: A single process-variable entry mapping a logical name to a control-system PV identifier.
--     * Slot: id
--     * Slot: identifier Description: Protocol-specific PV name (e.g., EPICS PV address).
--     * Slot: dtype Description: Data type (e.g., ``float``, ``int``).
--     * Slot: protocol Description: Control-system protocol (e.g., ``EPICS``, ``Tango``).
--     * Slot: units Description: Physical units string (e.g., ``A``, ``T/m``).
--     * Slot: description Description: Human-readable description.
--     * Slot: read_only Description: Whether the variable is read-only.
--     * Slot: value Description: Last-read value.
--     * Slot: target Description: Set-point target value.
--     * Slot: expression Description: Optional expression string for derived values.
-- # Class: ControlsInformation Description: Collection of process-variable definitions for an element's control interface.
--     * Slot: id
-- # Class: ShutterElement Description: Shutter interlock configuration.
--     * Slot: id
-- # Class: ValveElement Description: Vacuum valve configuration (no additional fields).
--     * Slot: id
-- # Class: LightingElement Description: Lighting element (no additional fields currently defined).
--     * Slot: id
-- # Class: AcceleratorElement Description: Root base class for all LAURA accelerator elements.  Every lattice element is an instance of a concrete subclass identified by ``hardware_type``.
--     * Slot: name Description: Unique element name within the machine.
--     * Slot: hardware_class Description: Functional category (e.g., ``Magnet``, ``Diagnostic``).
--     * Slot: hardware_type Description: Python class name used for MODEL_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.
--     * Slot: hardware_model Description: Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).
--     * Slot: machine_area Description: Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).
--     * Slot: virtual_name Description: Alternative internal name used by the control system when the physical name is inaccessible.
--     * Slot: subelement Description: If set, this element is a logical sub-component of the named parent element.
-- # Class: StandardElement Description: Accelerator element with control-system, electrical, manufacturer, simulation, and reference sub-models.
--     * Slot: name Description: Unique element name within the machine.
--     * Slot: hardware_class Description: Functional category (e.g., ``Magnet``, ``Diagnostic``).
--     * Slot: hardware_type Description: Python class name used for MODEL_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.
--     * Slot: hardware_model Description: Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).
--     * Slot: machine_area Description: Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).
--     * Slot: virtual_name Description: Alternative internal name used by the control system when the physical name is inaccessible.
--     * Slot: subelement Description: If set, this element is a logical sub-component of the named parent element.
--     * Slot: simulation_id Description: Simulation / tracking attributes.
--     * Slot: electrical_id Description: Power-supply electrical limits.
--     * Slot: manufacturer_id Description: Manufacturer and serial-number data.
--     * Slot: controls_id Description: Control-system process-variable definitions.
--     * Slot: reference_id Description: Links to design drawings and files.
-- # Class: Element Description: Concrete schema counterpart of the Python ``Element`` wrapper class. Inherits standard element composition fields.
--     * Slot: name Description: Unique element name within the machine.
--     * Slot: hardware_class Description: Functional category (e.g., ``Magnet``, ``Diagnostic``).
--     * Slot: hardware_type Description: Python class name used for MODEL_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.
--     * Slot: hardware_model Description: Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).
--     * Slot: machine_area Description: Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).
--     * Slot: virtual_name Description: Alternative internal name used by the control system when the physical name is inaccessible.
--     * Slot: subelement Description: If set, this element is a logical sub-component of the named parent element.
--     * Slot: simulation_id Description: Simulation / tracking attributes.
--     * Slot: electrical_id Description: Power-supply electrical limits.
--     * Slot: manufacturer_id Description: Manufacturer and serial-number data.
--     * Slot: controls_id Description: Control-system process-variable definitions.
--     * Slot: reference_id Description: Links to design drawings and files.
-- # Class: PhysicalAcceleratorElement Description: Accelerator element with a well-defined physical position and orientation in the beamline.
--     * Slot: name Description: Unique element name within the machine.
--     * Slot: hardware_class Description: Functional category (e.g., ``Magnet``, ``Diagnostic``).
--     * Slot: hardware_type Description: Python class name used for MODEL_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.
--     * Slot: hardware_model Description: Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).
--     * Slot: machine_area Description: Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).
--     * Slot: virtual_name Description: Alternative internal name used by the control system when the physical name is inaccessible.
--     * Slot: subelement Description: If set, this element is a logical sub-component of the named parent element.
--     * Slot: physical_id Description: Position, rotation, and length data.
--     * Slot: simulation_id Description: Simulation / tracking attributes.
--     * Slot: electrical_id Description: Power-supply electrical limits.
--     * Slot: manufacturer_id Description: Manufacturer and serial-number data.
--     * Slot: controls_id Description: Control-system process-variable definitions.
--     * Slot: reference_id Description: Links to design drawings and files.
-- # Class: MagnetBaseElement Description: Base class for all magnetic focusing and bending elements. (Named ``MagnetBaseElement`` in the schema to avoid collision with the ``magnetic`` composition-model class; maps to ``Magnet`` in Python.)
--     * Slot: name Description: Unique element name within the machine.
--     * Slot: hardware_class Description: Functional category (e.g., ``Magnet``, ``Diagnostic``).
--     * Slot: hardware_type Description: Python class name used for MODEL_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.
--     * Slot: hardware_model Description: Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).
--     * Slot: machine_area Description: Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).
--     * Slot: virtual_name Description: Alternative internal name used by the control system when the physical name is inaccessible.
--     * Slot: subelement Description: If set, this element is a logical sub-component of the named parent element.
--     * Slot: magnetic_id Description: Magnetic field parameters.
--     * Slot: degauss_id Description: Degaussing-cycle parameters.
--     * Slot: physical_id Description: Position, rotation, and length data.
--     * Slot: simulation_id Description: Simulation / tracking attributes.
--     * Slot: electrical_id Description: Power-supply electrical limits.
--     * Slot: manufacturer_id Description: Manufacturer and serial-number data.
--     * Slot: controls_id Description: Control-system process-variable definitions.
--     * Slot: reference_id Description: Links to design drawings and files.
-- # Class: Diagnostic Description: Base class for all beam-diagnostic instruments.
--     * Slot: name Description: Unique element name within the machine.
--     * Slot: hardware_class Description: Functional category (e.g., ``Magnet``, ``Diagnostic``).
--     * Slot: hardware_type Description: Python class name used for MODEL_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.
--     * Slot: hardware_model Description: Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).
--     * Slot: machine_area Description: Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).
--     * Slot: virtual_name Description: Alternative internal name used by the control system when the physical name is inaccessible.
--     * Slot: subelement Description: If set, this element is a logical sub-component of the named parent element.
--     * Slot: diagnostic_id Description: Instrument-specific diagnostic parameters.
--     * Slot: physical_id Description: Position, rotation, and length data.
--     * Slot: simulation_id Description: Simulation / tracking attributes.
--     * Slot: electrical_id Description: Power-supply electrical limits.
--     * Slot: manufacturer_id Description: Manufacturer and serial-number data.
--     * Slot: controls_id Description: Control-system process-variable definitions.
--     * Slot: reference_id Description: Links to design drawings and files.
-- # Class: BeamPositionMonitor Description: Beam-position monitor (BPM).
--     * Slot: name Description: Unique element name within the machine.
--     * Slot: hardware_class Description: Functional category (e.g., ``Magnet``, ``Diagnostic``).
--     * Slot: hardware_type Description: Python class name used for MODEL_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.
--     * Slot: hardware_model Description: Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).
--     * Slot: machine_area Description: Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).
--     * Slot: virtual_name Description: Alternative internal name used by the control system when the physical name is inaccessible.
--     * Slot: subelement Description: If set, this element is a logical sub-component of the named parent element.
--     * Slot: diagnostic_id Description: Instrument-specific diagnostic parameters.
--     * Slot: physical_id Description: Position, rotation, and length data.
--     * Slot: simulation_id Description: Simulation / tracking attributes.
--     * Slot: electrical_id Description: Power-supply electrical limits.
--     * Slot: manufacturer_id Description: Manufacturer and serial-number data.
--     * Slot: controls_id Description: Control-system process-variable definitions.
--     * Slot: reference_id Description: Links to design drawings and files.
-- # Class: BeamArrivalMonitor Description: Beam-arrival-time monitor (BAM).
--     * Slot: name Description: Unique element name within the machine.
--     * Slot: hardware_class Description: Functional category (e.g., ``Magnet``, ``Diagnostic``).
--     * Slot: hardware_type Description: Python class name used for MODEL_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.
--     * Slot: hardware_model Description: Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).
--     * Slot: machine_area Description: Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).
--     * Slot: virtual_name Description: Alternative internal name used by the control system when the physical name is inaccessible.
--     * Slot: subelement Description: If set, this element is a logical sub-component of the named parent element.
--     * Slot: diagnostic_id Description: Instrument-specific diagnostic parameters.
--     * Slot: physical_id Description: Position, rotation, and length data.
--     * Slot: simulation_id Description: Simulation / tracking attributes.
--     * Slot: electrical_id Description: Power-supply electrical limits.
--     * Slot: manufacturer_id Description: Manufacturer and serial-number data.
--     * Slot: controls_id Description: Control-system process-variable definitions.
--     * Slot: reference_id Description: Links to design drawings and files.
-- # Class: BunchLengthMonitor Description: Bunch-length monitor (BLM / CDR detector).
--     * Slot: name Description: Unique element name within the machine.
--     * Slot: hardware_class Description: Functional category (e.g., ``Magnet``, ``Diagnostic``).
--     * Slot: hardware_type Description: Python class name used for MODEL_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.
--     * Slot: hardware_model Description: Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).
--     * Slot: machine_area Description: Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).
--     * Slot: virtual_name Description: Alternative internal name used by the control system when the physical name is inaccessible.
--     * Slot: subelement Description: If set, this element is a logical sub-component of the named parent element.
--     * Slot: diagnostic_id Description: Instrument-specific diagnostic parameters.
--     * Slot: physical_id Description: Position, rotation, and length data.
--     * Slot: simulation_id Description: Simulation / tracking attributes.
--     * Slot: electrical_id Description: Power-supply electrical limits.
--     * Slot: manufacturer_id Description: Manufacturer and serial-number data.
--     * Slot: controls_id Description: Control-system process-variable definitions.
--     * Slot: reference_id Description: Links to design drawings and files.
-- # Class: Camera Description: Camera-based beam-profile monitor.
--     * Slot: name Description: Unique element name within the machine.
--     * Slot: hardware_class Description: Functional category (e.g., ``Magnet``, ``Diagnostic``).
--     * Slot: hardware_type Description: Python class name used for MODEL_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.
--     * Slot: hardware_model Description: Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).
--     * Slot: machine_area Description: Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).
--     * Slot: virtual_name Description: Alternative internal name used by the control system when the physical name is inaccessible.
--     * Slot: subelement Description: If set, this element is a logical sub-component of the named parent element.
--     * Slot: diagnostic_id Description: Instrument-specific diagnostic parameters.
--     * Slot: physical_id Description: Position, rotation, and length data.
--     * Slot: simulation_id Description: Simulation / tracking attributes.
--     * Slot: electrical_id Description: Power-supply electrical limits.
--     * Slot: manufacturer_id Description: Manufacturer and serial-number data.
--     * Slot: controls_id Description: Control-system process-variable definitions.
--     * Slot: reference_id Description: Links to design drawings and files.
-- # Class: Screen Description: Scintillator or OTR screen with an associated camera.
--     * Slot: name Description: Unique element name within the machine.
--     * Slot: hardware_class Description: Functional category (e.g., ``Magnet``, ``Diagnostic``).
--     * Slot: hardware_type Description: Python class name used for MODEL_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.
--     * Slot: hardware_model Description: Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).
--     * Slot: machine_area Description: Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).
--     * Slot: virtual_name Description: Alternative internal name used by the control system when the physical name is inaccessible.
--     * Slot: subelement Description: If set, this element is a logical sub-component of the named parent element.
--     * Slot: diagnostic_id Description: Instrument-specific diagnostic parameters.
--     * Slot: physical_id Description: Position, rotation, and length data.
--     * Slot: simulation_id Description: Simulation / tracking attributes.
--     * Slot: electrical_id Description: Power-supply electrical limits.
--     * Slot: manufacturer_id Description: Manufacturer and serial-number data.
--     * Slot: controls_id Description: Control-system process-variable definitions.
--     * Slot: reference_id Description: Links to design drawings and files.
-- # Class: ChargeDiagnostic Description: Base class for charge-measurement diagnostics.
--     * Slot: name Description: Unique element name within the machine.
--     * Slot: hardware_class Description: Functional category (e.g., ``Magnet``, ``Diagnostic``).
--     * Slot: hardware_type Description: Python class name used for MODEL_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.
--     * Slot: hardware_model Description: Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).
--     * Slot: machine_area Description: Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).
--     * Slot: virtual_name Description: Alternative internal name used by the control system when the physical name is inaccessible.
--     * Slot: subelement Description: If set, this element is a logical sub-component of the named parent element.
--     * Slot: diagnostic_id Description: Instrument-specific diagnostic parameters.
--     * Slot: physical_id Description: Position, rotation, and length data.
--     * Slot: simulation_id Description: Simulation / tracking attributes.
--     * Slot: electrical_id Description: Power-supply electrical limits.
--     * Slot: manufacturer_id Description: Manufacturer and serial-number data.
--     * Slot: controls_id Description: Control-system process-variable definitions.
--     * Slot: reference_id Description: Links to design drawings and files.
-- # Class: WallCurrentMonitor Description: Wall-current monitor (WCM) for non-destructive charge measurement.
--     * Slot: name Description: Unique element name within the machine.
--     * Slot: hardware_class Description: Functional category (e.g., ``Magnet``, ``Diagnostic``).
--     * Slot: hardware_type Description: Python class name used for MODEL_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.
--     * Slot: hardware_model Description: Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).
--     * Slot: machine_area Description: Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).
--     * Slot: virtual_name Description: Alternative internal name used by the control system when the physical name is inaccessible.
--     * Slot: subelement Description: If set, this element is a logical sub-component of the named parent element.
--     * Slot: diagnostic_id Description: Instrument-specific diagnostic parameters.
--     * Slot: physical_id Description: Position, rotation, and length data.
--     * Slot: simulation_id Description: Simulation / tracking attributes.
--     * Slot: electrical_id Description: Power-supply electrical limits.
--     * Slot: manufacturer_id Description: Manufacturer and serial-number data.
--     * Slot: controls_id Description: Control-system process-variable definitions.
--     * Slot: reference_id Description: Links to design drawings and files.
-- # Class: FaradayCupMonitor Description: Faraday cup for destructive charge measurement.
--     * Slot: name Description: Unique element name within the machine.
--     * Slot: hardware_class Description: Functional category (e.g., ``Magnet``, ``Diagnostic``).
--     * Slot: hardware_type Description: Python class name used for MODEL_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.
--     * Slot: hardware_model Description: Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).
--     * Slot: machine_area Description: Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).
--     * Slot: virtual_name Description: Alternative internal name used by the control system when the physical name is inaccessible.
--     * Slot: subelement Description: If set, this element is a logical sub-component of the named parent element.
--     * Slot: diagnostic_id Description: Instrument-specific diagnostic parameters.
--     * Slot: physical_id Description: Position, rotation, and length data.
--     * Slot: simulation_id Description: Simulation / tracking attributes.
--     * Slot: electrical_id Description: Power-supply electrical limits.
--     * Slot: manufacturer_id Description: Manufacturer and serial-number data.
--     * Slot: controls_id Description: Control-system process-variable definitions.
--     * Slot: reference_id Description: Links to design drawings and files.
-- # Class: IntegratedCurrentTransformer Description: Integrated current transformer (ICT) for non-destructive single-shot charge measurement.
--     * Slot: name Description: Unique element name within the machine.
--     * Slot: hardware_class Description: Functional category (e.g., ``Magnet``, ``Diagnostic``).
--     * Slot: hardware_type Description: Python class name used for MODEL_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.
--     * Slot: hardware_model Description: Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).
--     * Slot: machine_area Description: Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).
--     * Slot: virtual_name Description: Alternative internal name used by the control system when the physical name is inaccessible.
--     * Slot: subelement Description: If set, this element is a logical sub-component of the named parent element.
--     * Slot: diagnostic_id Description: Instrument-specific diagnostic parameters.
--     * Slot: physical_id Description: Position, rotation, and length data.
--     * Slot: simulation_id Description: Simulation / tracking attributes.
--     * Slot: electrical_id Description: Power-supply electrical limits.
--     * Slot: manufacturer_id Description: Manufacturer and serial-number data.
--     * Slot: controls_id Description: Control-system process-variable definitions.
--     * Slot: reference_id Description: Links to design drawings and files.
-- # Class: RFCavity Description: Accelerating RF cavity.
--     * Slot: name Description: Unique element name within the machine.
--     * Slot: hardware_class Description: Functional category (e.g., ``Magnet``, ``Diagnostic``).
--     * Slot: hardware_type Description: Python class name used for MODEL_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.
--     * Slot: hardware_model Description: Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).
--     * Slot: machine_area Description: Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).
--     * Slot: virtual_name Description: Alternative internal name used by the control system when the physical name is inaccessible.
--     * Slot: subelement Description: If set, this element is a logical sub-component of the named parent element.
--     * Slot: cavity_id Description: RF structure parameters.
--     * Slot: physical_id Description: Position, rotation, and length data.
--     * Slot: simulation_id Description: Simulation / tracking attributes.
--     * Slot: electrical_id Description: Power-supply electrical limits.
--     * Slot: manufacturer_id Description: Manufacturer and serial-number data.
--     * Slot: controls_id Description: Control-system process-variable definitions.
--     * Slot: reference_id Description: Links to design drawings and files.
-- # Class: RFDeflectingCavity Description: Transverse-deflecting (streak) RF cavity.
--     * Slot: name Description: Unique element name within the machine.
--     * Slot: hardware_class Description: Functional category (e.g., ``Magnet``, ``Diagnostic``).
--     * Slot: hardware_type Description: Python class name used for MODEL_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.
--     * Slot: hardware_model Description: Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).
--     * Slot: machine_area Description: Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).
--     * Slot: virtual_name Description: Alternative internal name used by the control system when the physical name is inaccessible.
--     * Slot: subelement Description: If set, this element is a logical sub-component of the named parent element.
--     * Slot: cavity_id Description: RF structure parameters.
--     * Slot: physical_id Description: Position, rotation, and length data.
--     * Slot: simulation_id Description: Simulation / tracking attributes.
--     * Slot: electrical_id Description: Power-supply electrical limits.
--     * Slot: manufacturer_id Description: Manufacturer and serial-number data.
--     * Slot: controls_id Description: Control-system process-variable definitions.
--     * Slot: reference_id Description: Links to design drawings and files.
-- # Class: Wakefield Description: Passive wakefield structure (dielectric, corrugated, etc.).
--     * Slot: name Description: Unique element name within the machine.
--     * Slot: hardware_class Description: Functional category (e.g., ``Magnet``, ``Diagnostic``).
--     * Slot: hardware_type Description: Python class name used for MODEL_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.
--     * Slot: hardware_model Description: Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).
--     * Slot: machine_area Description: Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).
--     * Slot: virtual_name Description: Alternative internal name used by the control system when the physical name is inaccessible.
--     * Slot: subelement Description: If set, this element is a logical sub-component of the named parent element.
--     * Slot: cavity_id Description: Wakefield structure parameters.
--     * Slot: physical_id Description: Position, rotation, and length data.
--     * Slot: simulation_id Description: Simulation / tracking attributes.
--     * Slot: electrical_id Description: Power-supply electrical limits.
--     * Slot: manufacturer_id Description: Manufacturer and serial-number data.
--     * Slot: controls_id Description: Control-system process-variable definitions.
--     * Slot: reference_id Description: Links to design drawings and files.
-- # Class: LowLevelRF Description: Low-level RF (LLRF) controller.
--     * Slot: name Description: Unique element name within the machine.
--     * Slot: hardware_class Description: Functional category (e.g., ``Magnet``, ``Diagnostic``).
--     * Slot: hardware_type Description: Python class name used for MODEL_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.
--     * Slot: hardware_model Description: Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).
--     * Slot: machine_area Description: Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).
--     * Slot: virtual_name Description: Alternative internal name used by the control system when the physical name is inaccessible.
--     * Slot: subelement Description: If set, this element is a logical sub-component of the named parent element.
--     * Slot: llrf_id Description: LLRF parameters.
--     * Slot: simulation_id Description: Simulation / tracking attributes.
--     * Slot: electrical_id Description: Power-supply electrical limits.
--     * Slot: manufacturer_id Description: Manufacturer and serial-number data.
--     * Slot: controls_id Description: Control-system process-variable definitions.
--     * Slot: reference_id Description: Links to design drawings and files.
-- # Class: RFModulator Description: RF modulator (klystron driver) element.
--     * Slot: name Description: Unique element name within the machine.
--     * Slot: hardware_class Description: Functional category (e.g., ``Magnet``, ``Diagnostic``).
--     * Slot: hardware_type Description: Python class name used for MODEL_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.
--     * Slot: hardware_model Description: Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).
--     * Slot: machine_area Description: Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).
--     * Slot: virtual_name Description: Alternative internal name used by the control system when the physical name is inaccessible.
--     * Slot: subelement Description: If set, this element is a logical sub-component of the named parent element.
--     * Slot: modulator_id Description: Modulator parameters.
--     * Slot: simulation_id Description: Simulation / tracking attributes.
--     * Slot: electrical_id Description: Power-supply electrical limits.
--     * Slot: manufacturer_id Description: Manufacturer and serial-number data.
--     * Slot: controls_id Description: Control-system process-variable definitions.
--     * Slot: reference_id Description: Links to design drawings and files.
-- # Class: RFProtection Description: RF protection system element.
--     * Slot: name Description: Unique element name within the machine.
--     * Slot: hardware_class Description: Functional category (e.g., ``Magnet``, ``Diagnostic``).
--     * Slot: hardware_type Description: Python class name used for MODEL_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.
--     * Slot: hardware_model Description: Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).
--     * Slot: machine_area Description: Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).
--     * Slot: virtual_name Description: Alternative internal name used by the control system when the physical name is inaccessible.
--     * Slot: subelement Description: If set, this element is a logical sub-component of the named parent element.
--     * Slot: protection_id Description: RF protection parameters.
--     * Slot: simulation_id Description: Simulation / tracking attributes.
--     * Slot: electrical_id Description: Power-supply electrical limits.
--     * Slot: manufacturer_id Description: Manufacturer and serial-number data.
--     * Slot: controls_id Description: Control-system process-variable definitions.
--     * Slot: reference_id Description: Links to design drawings and files.
-- # Class: RFHeartbeat Description: RF timing heartbeat / signal-monitor element.
--     * Slot: name Description: Unique element name within the machine.
--     * Slot: hardware_class Description: Functional category (e.g., ``Magnet``, ``Diagnostic``).
--     * Slot: hardware_type Description: Python class name used for MODEL_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.
--     * Slot: hardware_model Description: Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).
--     * Slot: machine_area Description: Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).
--     * Slot: virtual_name Description: Alternative internal name used by the control system when the physical name is inaccessible.
--     * Slot: subelement Description: If set, this element is a logical sub-component of the named parent element.
--     * Slot: heartbeat_id Description: RF heartbeat parameters.
--     * Slot: simulation_id Description: Simulation / tracking attributes.
--     * Slot: electrical_id Description: Power-supply electrical limits.
--     * Slot: manufacturer_id Description: Manufacturer and serial-number data.
--     * Slot: controls_id Description: Control-system process-variable definitions.
--     * Slot: reference_id Description: Links to design drawings and files.
-- # Class: PID Description: Proportional-integral-derivative (PID) feedback controller.
--     * Slot: name Description: Unique element name within the machine.
--     * Slot: hardware_class Description: Functional category (e.g., ``Magnet``, ``Diagnostic``).
--     * Slot: hardware_type Description: Python class name used for MODEL_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.
--     * Slot: hardware_model Description: Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).
--     * Slot: machine_area Description: Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).
--     * Slot: virtual_name Description: Alternative internal name used by the control system when the physical name is inaccessible.
--     * Slot: subelement Description: If set, this element is a logical sub-component of the named parent element.
--     * Slot: pid_id Description: PID gain parameters.
--     * Slot: simulation_id Description: Simulation / tracking attributes.
--     * Slot: electrical_id Description: Power-supply electrical limits.
--     * Slot: manufacturer_id Description: Manufacturer and serial-number data.
--     * Slot: controls_id Description: Control-system process-variable definitions.
--     * Slot: reference_id Description: Links to design drawings and files.
-- # Class: TwissMatch Description: Virtual Twiss-parameter matching point -- a zero-length marker that defines the desired optical functions at a location in the lattice.
--     * Slot: name Description: Unique element name within the machine.
--     * Slot: hardware_class Description: Functional category (e.g., ``Magnet``, ``Diagnostic``).
--     * Slot: hardware_type Description: Python class name used for MODEL_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.
--     * Slot: hardware_model Description: Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).
--     * Slot: machine_area Description: Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).
--     * Slot: virtual_name Description: Alternative internal name used by the control system when the physical name is inaccessible.
--     * Slot: subelement Description: If set, this element is a logical sub-component of the named parent element.
--     * Slot: physical_id Description: Position, rotation, and length data.
--     * Slot: simulation_id Description: Simulation / tracking attributes.
--     * Slot: electrical_id Description: Power-supply electrical limits.
--     * Slot: manufacturer_id Description: Manufacturer and serial-number data.
--     * Slot: controls_id Description: Control-system process-variable definitions.
--     * Slot: reference_id Description: Links to design drawings and files.
-- # Class: Stage Description: Motorised positioning stage.
--     * Slot: name Description: Unique element name within the machine.
--     * Slot: hardware_class Description: Functional category (e.g., ``Magnet``, ``Diagnostic``).
--     * Slot: hardware_type Description: Python class name used for MODEL_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.
--     * Slot: hardware_model Description: Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).
--     * Slot: machine_area Description: Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).
--     * Slot: virtual_name Description: Alternative internal name used by the control system when the physical name is inaccessible.
--     * Slot: subelement Description: If set, this element is a logical sub-component of the named parent element.
--     * Slot: physical_id Description: Position, rotation, and length data.
--     * Slot: simulation_id Description: Simulation / tracking attributes.
--     * Slot: electrical_id Description: Power-supply electrical limits.
--     * Slot: manufacturer_id Description: Manufacturer and serial-number data.
--     * Slot: controls_id Description: Control-system process-variable definitions.
--     * Slot: reference_id Description: Links to design drawings and files.
-- # Class: VacuumGauge Description: Vacuum-pressure gauge.
--     * Slot: name Description: Unique element name within the machine.
--     * Slot: hardware_class Description: Functional category (e.g., ``Magnet``, ``Diagnostic``).
--     * Slot: hardware_type Description: Python class name used for MODEL_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.
--     * Slot: hardware_model Description: Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).
--     * Slot: machine_area Description: Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).
--     * Slot: virtual_name Description: Alternative internal name used by the control system when the physical name is inaccessible.
--     * Slot: subelement Description: If set, this element is a logical sub-component of the named parent element.
--     * Slot: physical_id Description: Position, rotation, and length data.
--     * Slot: simulation_id Description: Simulation / tracking attributes.
--     * Slot: electrical_id Description: Power-supply electrical limits.
--     * Slot: manufacturer_id Description: Manufacturer and serial-number data.
--     * Slot: controls_id Description: Control-system process-variable definitions.
--     * Slot: reference_id Description: Links to design drawings and files.
-- # Class: Laser Description: Laser system element (full laser setup including beam parameters).
--     * Slot: name Description: Unique element name within the machine.
--     * Slot: hardware_class Description: Functional category (e.g., ``Magnet``, ``Diagnostic``).
--     * Slot: hardware_type Description: Python class name used for MODEL_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.
--     * Slot: hardware_model Description: Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).
--     * Slot: machine_area Description: Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).
--     * Slot: virtual_name Description: Alternative internal name used by the control system when the physical name is inaccessible.
--     * Slot: subelement Description: If set, this element is a logical sub-component of the named parent element.
--     * Slot: laser_id Description: Laser-beam parameters.
--     * Slot: physical_id Description: Position, rotation, and length data.
--     * Slot: simulation_id Description: Simulation / tracking attributes.
--     * Slot: electrical_id Description: Power-supply electrical limits.
--     * Slot: manufacturer_id Description: Manufacturer and serial-number data.
--     * Slot: controls_id Description: Control-system process-variable definitions.
--     * Slot: reference_id Description: Links to design drawings and files.
-- # Class: Shutter Description: Beam or laser shutter with interlock logic.
--     * Slot: name Description: Unique element name within the machine.
--     * Slot: hardware_class Description: Functional category (e.g., ``Magnet``, ``Diagnostic``).
--     * Slot: hardware_type Description: Python class name used for MODEL_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.
--     * Slot: hardware_model Description: Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).
--     * Slot: machine_area Description: Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).
--     * Slot: virtual_name Description: Alternative internal name used by the control system when the physical name is inaccessible.
--     * Slot: subelement Description: If set, this element is a logical sub-component of the named parent element.
--     * Slot: shutter_id Description: Shutter interlock configuration.
--     * Slot: physical_id Description: Position, rotation, and length data.
--     * Slot: simulation_id Description: Simulation / tracking attributes.
--     * Slot: electrical_id Description: Power-supply electrical limits.
--     * Slot: manufacturer_id Description: Manufacturer and serial-number data.
--     * Slot: controls_id Description: Control-system process-variable definitions.
--     * Slot: reference_id Description: Links to design drawings and files.
-- # Class: Valve Description: Vacuum gate valve.
--     * Slot: name Description: Unique element name within the machine.
--     * Slot: hardware_class Description: Functional category (e.g., ``Magnet``, ``Diagnostic``).
--     * Slot: hardware_type Description: Python class name used for MODEL_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.
--     * Slot: hardware_model Description: Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).
--     * Slot: machine_area Description: Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).
--     * Slot: virtual_name Description: Alternative internal name used by the control system when the physical name is inaccessible.
--     * Slot: subelement Description: If set, this element is a logical sub-component of the named parent element.
--     * Slot: valve_id Description: Valve configuration.
--     * Slot: physical_id Description: Position, rotation, and length data.
--     * Slot: simulation_id Description: Simulation / tracking attributes.
--     * Slot: electrical_id Description: Power-supply electrical limits.
--     * Slot: manufacturer_id Description: Manufacturer and serial-number data.
--     * Slot: controls_id Description: Control-system process-variable definitions.
--     * Slot: reference_id Description: Links to design drawings and files.
-- # Class: Marker Description: Virtual survey marker -- a zero-length reference point used for alignment.
--     * Slot: name Description: Unique element name within the machine.
--     * Slot: hardware_class Description: Functional category (e.g., ``Magnet``, ``Diagnostic``).
--     * Slot: hardware_type Description: Python class name used for MODEL_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.
--     * Slot: hardware_model Description: Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).
--     * Slot: machine_area Description: Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).
--     * Slot: virtual_name Description: Alternative internal name used by the control system when the physical name is inaccessible.
--     * Slot: subelement Description: If set, this element is a logical sub-component of the named parent element.
--     * Slot: physical_id Description: Position, rotation, and length data.
--     * Slot: simulation_id Description: Simulation / tracking attributes.
--     * Slot: electrical_id Description: Power-supply electrical limits.
--     * Slot: manufacturer_id Description: Manufacturer and serial-number data.
--     * Slot: controls_id Description: Control-system process-variable definitions.
--     * Slot: reference_id Description: Links to design drawings and files.
-- # Class: Aperture Description: Mechanical aperture restriction in the beam pipe.
--     * Slot: name Description: Unique element name within the machine.
--     * Slot: hardware_class Description: Functional category (e.g., ``Magnet``, ``Diagnostic``).
--     * Slot: hardware_type Description: Python class name used for MODEL_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.
--     * Slot: hardware_model Description: Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).
--     * Slot: machine_area Description: Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).
--     * Slot: virtual_name Description: Alternative internal name used by the control system when the physical name is inaccessible.
--     * Slot: subelement Description: If set, this element is a logical sub-component of the named parent element.
--     * Slot: aperture_id Description: Aperture geometry parameters.
--     * Slot: physical_id Description: Position, rotation, and length data.
--     * Slot: simulation_id Description: Simulation / tracking attributes.
--     * Slot: electrical_id Description: Power-supply electrical limits.
--     * Slot: manufacturer_id Description: Manufacturer and serial-number data.
--     * Slot: controls_id Description: Control-system process-variable definitions.
--     * Slot: reference_id Description: Links to design drawings and files.
-- # Class: Collimator Description: Movable collimator jaw (extends Aperture).
--     * Slot: name Description: Unique element name within the machine.
--     * Slot: hardware_class Description: Functional category (e.g., ``Magnet``, ``Diagnostic``).
--     * Slot: hardware_type Description: Python class name used for MODEL_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.
--     * Slot: hardware_model Description: Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).
--     * Slot: machine_area Description: Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).
--     * Slot: virtual_name Description: Alternative internal name used by the control system when the physical name is inaccessible.
--     * Slot: subelement Description: If set, this element is a logical sub-component of the named parent element.
--     * Slot: aperture_id Description: Aperture geometry parameters.
--     * Slot: physical_id Description: Position, rotation, and length data.
--     * Slot: simulation_id Description: Simulation / tracking attributes.
--     * Slot: electrical_id Description: Power-supply electrical limits.
--     * Slot: manufacturer_id Description: Manufacturer and serial-number data.
--     * Slot: controls_id Description: Control-system process-variable definitions.
--     * Slot: reference_id Description: Links to design drawings and files.
-- # Class: Drift Description: Field-free drift space between elements.
--     * Slot: name Description: Unique element name within the machine.
--     * Slot: hardware_class Description: Functional category (e.g., ``Magnet``, ``Diagnostic``).
--     * Slot: hardware_type Description: Python class name used for MODEL_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.
--     * Slot: hardware_model Description: Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).
--     * Slot: machine_area Description: Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).
--     * Slot: virtual_name Description: Alternative internal name used by the control system when the physical name is inaccessible.
--     * Slot: subelement Description: If set, this element is a logical sub-component of the named parent element.
--     * Slot: physical_id Description: Position, rotation, and length data.
--     * Slot: simulation_id Description: Simulation / tracking attributes.
--     * Slot: electrical_id Description: Power-supply electrical limits.
--     * Slot: manufacturer_id Description: Manufacturer and serial-number data.
--     * Slot: controls_id Description: Control-system process-variable definitions.
--     * Slot: reference_id Description: Links to design drawings and files.
-- # Class: Plasma Description: Laser-driven plasma-accelerator stage.
--     * Slot: name Description: Unique element name within the machine.
--     * Slot: hardware_class Description: Functional category (e.g., ``Magnet``, ``Diagnostic``).
--     * Slot: hardware_type Description: Python class name used for MODEL_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.
--     * Slot: hardware_model Description: Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).
--     * Slot: machine_area Description: Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).
--     * Slot: virtual_name Description: Alternative internal name used by the control system when the physical name is inaccessible.
--     * Slot: subelement Description: If set, this element is a logical sub-component of the named parent element.
--     * Slot: plasma_id Description: Plasma channel parameters.
--     * Slot: laser_id Description: Laser driving the plasma stage.
--     * Slot: physical_id Description: Position, rotation, and length data.
--     * Slot: simulation_id Description: Simulation / tracking attributes.
--     * Slot: electrical_id Description: Power-supply electrical limits.
--     * Slot: manufacturer_id Description: Manufacturer and serial-number data.
--     * Slot: controls_id Description: Control-system process-variable definitions.
--     * Slot: reference_id Description: Links to design drawings and files.
-- # Class: LaserEnergyMeter Description: Laser pulse-energy diagnostic (photodiode / pyroelectric).
--     * Slot: name Description: Unique element name within the machine.
--     * Slot: hardware_class Description: Functional category (e.g., ``Magnet``, ``Diagnostic``).
--     * Slot: hardware_type Description: Python class name used for MODEL_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.
--     * Slot: hardware_model Description: Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).
--     * Slot: machine_area Description: Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).
--     * Slot: virtual_name Description: Alternative internal name used by the control system when the physical name is inaccessible.
--     * Slot: subelement Description: If set, this element is a logical sub-component of the named parent element.
--     * Slot: laser_id Description: Energy-meter instrument parameters.
--     * Slot: simulation_id Description: Simulation / tracking attributes.
--     * Slot: electrical_id Description: Power-supply electrical limits.
--     * Slot: manufacturer_id Description: Manufacturer and serial-number data.
--     * Slot: controls_id Description: Control-system process-variable definitions.
--     * Slot: reference_id Description: Links to design drawings and files.
-- # Class: LaserHalfWavePlate Description: Half-wave plate for laser polarisation rotation.
--     * Slot: name Description: Unique element name within the machine.
--     * Slot: hardware_class Description: Functional category (e.g., ``Magnet``, ``Diagnostic``).
--     * Slot: hardware_type Description: Python class name used for MODEL_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.
--     * Slot: hardware_model Description: Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).
--     * Slot: machine_area Description: Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).
--     * Slot: virtual_name Description: Alternative internal name used by the control system when the physical name is inaccessible.
--     * Slot: subelement Description: If set, this element is a logical sub-component of the named parent element.
--     * Slot: laser_id Description: Half-wave plate parameters.
--     * Slot: simulation_id Description: Simulation / tracking attributes.
--     * Slot: electrical_id Description: Power-supply electrical limits.
--     * Slot: manufacturer_id Description: Manufacturer and serial-number data.
--     * Slot: controls_id Description: Control-system process-variable definitions.
--     * Slot: reference_id Description: Links to design drawings and files.
-- # Class: LaserMirror Description: Laser steering or focusing mirror.
--     * Slot: name Description: Unique element name within the machine.
--     * Slot: hardware_class Description: Functional category (e.g., ``Magnet``, ``Diagnostic``).
--     * Slot: hardware_type Description: Python class name used for MODEL_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.
--     * Slot: hardware_model Description: Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).
--     * Slot: machine_area Description: Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).
--     * Slot: virtual_name Description: Alternative internal name used by the control system when the physical name is inaccessible.
--     * Slot: subelement Description: If set, this element is a logical sub-component of the named parent element.
--     * Slot: laser_id Description: Mirror steering parameters.
--     * Slot: simulation_id Description: Simulation / tracking attributes.
--     * Slot: electrical_id Description: Power-supply electrical limits.
--     * Slot: manufacturer_id Description: Manufacturer and serial-number data.
--     * Slot: controls_id Description: Control-system process-variable definitions.
--     * Slot: reference_id Description: Links to design drawings and files.
-- # Class: LaserMirrorElement Description: Mirror steering parameters for a laser mirror.
--     * Slot: id
--     * Slot: step_max Description: Maximum step size for mirror adjustment.
--     * Slot: vertical_channel Description: Vertical control channel index.
--     * Slot: horizontal_channel Description: Horizontal control channel index.
--     * Slot: sense_id Description: Mirror sense/interlock configuration.
-- # Class: LaserMirrorSense Description: Mirror sense switch values.
--     * Slot: id
--     * Slot: left Description: Left sense value.
--     * Slot: right Description: Right sense value.
--     * Slot: up Description: Up sense value.
--     * Slot: down Description: Down sense value.
-- # Class: LaserAttenuator Description: Laser power attenuator (waveplate + polariser combination).
--     * Slot: maximum Description: Maximum attenuation angle [deg].
--     * Slot: minimum Description: Minimum attenuation angle [deg].
--     * Slot: name Description: Unique element name within the machine.
--     * Slot: hardware_class Description: Functional category (e.g., ``Magnet``, ``Diagnostic``).
--     * Slot: hardware_type Description: Python class name used for MODEL_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.
--     * Slot: hardware_model Description: Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).
--     * Slot: machine_area Description: Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).
--     * Slot: virtual_name Description: Alternative internal name used by the control system when the physical name is inaccessible.
--     * Slot: subelement Description: If set, this element is a logical sub-component of the named parent element.
--     * Slot: simulation_id Description: Simulation / tracking attributes.
--     * Slot: electrical_id Description: Power-supply electrical limits.
--     * Slot: manufacturer_id Description: Manufacturer and serial-number data.
--     * Slot: controls_id Description: Control-system process-variable definitions.
--     * Slot: reference_id Description: Links to design drawings and files.
-- # Class: Lighting Description: Experimental-hall lighting element.
--     * Slot: name Description: Unique element name within the machine.
--     * Slot: hardware_class Description: Functional category (e.g., ``Magnet``, ``Diagnostic``).
--     * Slot: hardware_type Description: Python class name used for MODEL_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML.
--     * Slot: hardware_model Description: Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``).
--     * Slot: machine_area Description: Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``).
--     * Slot: virtual_name Description: Alternative internal name used by the control system when the physical name is inaccessible.
--     * Slot: subelement Description: If set, this element is a logical sub-component of the named parent element.
--     * Slot: lights_id Description: Lighting configuration.
--     * Slot: simulation_id Description: Simulation / tracking attributes.
--     * Slot: electrical_id Description: Power-supply electrical limits.
--     * Slot: manufacturer_id Description: Manufacturer and serial-number data.
--     * Slot: controls_id Description: Control-system process-variable definitions.
--     * Slot: reference_id Description: Links to design drawings and files.
-- # Class: SectionLattice Description: An ordered list of element names defining a contiguous beamline section.
--     * Slot: name Description: Unique section name.
--     * Slot: master_lattice Description: Name of the master lattice this section belongs to.
-- # Class: MachineLayout Description: An ordered list of section names defining a beamline layout (a contiguous sequence of sections).
--     * Slot: name Description: Unique layout name.
--     * Slot: master_lattice Description: Name of the master lattice this layout belongs to.
-- # Class: MachineModel Description: Top-level container for a complete accelerator lattice: elements, sections, layouts, and named lattice configurations.
--     * Slot: id
-- # Class: SimulationElement Description: Base simulation attributes: field-map files and reference positions for tracking codes.
--     * Slot: id
--     * Slot: field_definition Description: Path to the 3-D field-map file.
--     * Slot: wakefield_definition Description: Path to the wakefield impedance file.
--     * Slot: field_reference_position Description: Longitudinal origin of the field map [m].
--     * Slot: scale_field Description: Multiplicative scale factor applied to the field map.
-- # Class: MagnetSimulationElement Description: Simulation attributes specific to magnets: integrator settings, fringe-field model, and radiation flags.
--     * Slot: id
--     * Slot: n_kicks Description: Number of integration kicks.
--     * Slot: field_amplitude Description: Field amplitude scaling for magnet tracking.
--     * Slot: n_slices Description: Number of longitudinal slices for thick-lens tracking.
--     * Slot: smooth Description: Use a smoothed field profile.
--     * Slot: edge_field_integral Description: Fringe-field integral for edge focussing.
--     * Slot: edge1_effects Description: Enable entrance-edge focussing effects.
--     * Slot: edge2_effects Description: Enable exit-edge focussing effects.
--     * Slot: sr_enable Description: Enable synchrotron-radiation energy loss.
--     * Slot: isr_enable Description: Enable incoherent synchrotron-radiation emittance growth.
--     * Slot: csr_enable Description: Enable coherent synchrotron radiation.
--     * Slot: csr_bins Description: Number of longitudinal bins for the CSR mesh.
--     * Slot: integration_order Description: Order of the symplectic integrator.
--     * Slot: nonlinear Description: Include higher-order (sextupole+) field components.
--     * Slot: smoothing_half_width Description: Half-width of the current-profile smoothing kernel.
--     * Slot: edge_order Description: Polynomial order of the edge-field expansion.
--     * Slot: deltaL Description: Longitudinal step-size override for thick-lens integration [m].
--     * Slot: smooth_points Description: Number of points used to smooth the field map [ASTRA].
--     * Slot: field_definition Description: Path to the 3-D field-map file.
--     * Slot: wakefield_definition Description: Path to the wakefield impedance file.
--     * Slot: field_reference_position Description: Longitudinal origin of the field map [m].
--     * Slot: scale_field Description: Multiplicative scale factor applied to the field map.
-- # Class: RFCavitySimulationElement Description: Simulation attributes for RF cavity elements.
--     * Slot: id
--     * Slot: t_column Description: Time column in the wake file.
--     * Slot: z_column Description: Longitudinal position column in the wake file.
--     * Slot: wx_column Description: Horizontal wake column in the wake file.
--     * Slot: wy_column Description: Vertical wake column in the wake file.
--     * Slot: wz_column Description: Longitudinal wake column in the wake file.
--     * Slot: n_kicks Description: Number of cavity kicks to apply.
--     * Slot: lsc_bins Description: Number of longitudinal space-charge bins.
--     * Slot: field_amplitude Description: Cavity field amplitude.
--     * Slot: change_p0 Description: Flag indicating whether the cavity changes reference momentum.
--     * Slot: end1_focus Description: Apply entrance focusing.
--     * Slot: end2_focus Description: Apply exit focusing.
--     * Slot: body_focus_model Description: Cavity body focusing model.
--     * Slot: current_bins Description: Number of current bins.
--     * Slot: interpolate_current_bins Description: Flag indicating current-bin interpolation.
--     * Slot: smooth_current_bins Description: Flag indicating current-bin smoothing.
--     * Slot: smooth Description: Cavity smoothing parameter.
--     * Slot: ez_peak Description: Peak longitudinal electric field.
--     * Slot: field_file_name Description: Cavity field file name.
--     * Slot: wakefile Description: Wake file name.
--     * Slot: zwakefile Description: Longitudinal wake file name.
--     * Slot: trwakefile Description: Transverse wake file name.
--     * Slot: field_definition Description: Path to the 3-D field-map file.
--     * Slot: wakefield_definition Description: Path to the wakefield impedance file.
--     * Slot: field_reference_position Description: Longitudinal origin of the field map [m].
--     * Slot: scale_field Description: Multiplicative scale factor applied to the field map.
-- # Class: WakefieldSimulationElement Description: Simulation attributes for passive wakefield structures.
--     * Slot: id
--     * Slot: t_column Description: Time column in the wake file.
--     * Slot: z_column Description: Longitudinal position column in the wake file.
--     * Slot: wx_column Description: Horizontal wake column in the wake file.
--     * Slot: wy_column Description: Vertical wake column in the wake file.
--     * Slot: wz_column Description: Longitudinal wake column in the wake file.
--     * Slot: allow_long_beam Description: Allow beams longer than the wakefield.
--     * Slot: bunched_beam Description: Use bunched beam mode.
--     * Slot: change_momentum Description: Allow wakefield to change bunch momentum.
--     * Slot: factor Description: Wake scaling factor.
--     * Slot: interpolate Description: Interpolate points in wake file.
--     * Slot: scale_kick Description: Factor by which to scale wake kicks.
--     * Slot: scale_field_ex Description: x-component of the longitudinal direction vector.
--     * Slot: scale_field_ey Description: y-component of the longitudinal direction vector.
--     * Slot: scale_field_ez Description: z-component of the longitudinal direction vector.
--     * Slot: scale_field_hx Description: x-component of the horizontal direction vector.
--     * Slot: scale_field_hy Description: y-component of the horizontal direction vector.
--     * Slot: scale_field_hz Description: z-component of the horizontal direction vector.
--     * Slot: equal_grid Description: Interpolation between equidistant and equal-charge grids.
--     * Slot: interpolation_method Description: Interpolation method for ASTRA.
--     * Slot: smooth Description: Smoothing parameter for Gaussian interpolation.
--     * Slot: subbins Description: Sub-binning parameter.
--     * Slot: field_definition Description: Path to the 3-D field-map file.
--     * Slot: wakefield_definition Description: Path to the wakefield impedance file.
--     * Slot: field_reference_position Description: Longitudinal origin of the field map [m].
--     * Slot: scale_field Description: Multiplicative scale factor applied to the field map.
-- # Class: DriftSimulationElement Description: Simulation attributes for field-free drift sections.
--     * Slot: id
--     * Slot: lsc_bins Description: Number of bins for LSC calculations.
--     * Slot: lsc_interpolate Description: Flag to allow interpolation of computed LSC wake.
--     * Slot: csr_enable Description: Enable CSR drift calculations.
--     * Slot: lsc_enable Description: Enable LSC drift calculations.
--     * Slot: use_stupakov Description: Use Stupakov formula.
--     * Slot: csrdz Description: Step size for CSR calculations.
--     * Slot: lsc_high_frequency_cutoff_start Description: High-frequency cutoff start for LSC.
--     * Slot: lsc_high_frequency_cutoff_end Description: High-frequency cutoff end for LSC.
--     * Slot: lsc_low_frequency_cutoff_start Description: Low-frequency cutoff start for LSC.
--     * Slot: lsc_low_frequency_cutoff_end Description: Low-frequency cutoff end for LSC.
--     * Slot: field_definition Description: Path to the 3-D field-map file.
--     * Slot: wakefield_definition Description: Path to the wakefield impedance file.
--     * Slot: field_reference_position Description: Longitudinal origin of the field map [m].
--     * Slot: scale_field Description: Multiplicative scale factor applied to the field map.
-- # Class: DiagnosticSimulationElement Description: Simulation attributes for beam-diagnostic elements.
--     * Slot: id
--     * Slot: output_filename Description: Output filename for diagnostic data.
--     * Slot: field_definition Description: Path to the 3-D field-map file.
--     * Slot: wakefield_definition Description: Path to the wakefield impedance file.
--     * Slot: field_reference_position Description: Longitudinal origin of the field map [m].
--     * Slot: scale_field Description: Multiplicative scale factor applied to the field map.
-- # Class: PlasmaSimulationElement Description: Simulation attributes for plasma-accelerator stages.
--     * Slot: id
--     * Slot: wakefield_model Description: Wakefield model identifier.
--     * Slot: bunch_pusher Description: Pusher used to evolve bunch particles in time.
--     * Slot: dt_bunch Description: Time-step control for bunch evolution (or 'auto').
--     * Slot: n_out Description: Number of distribution dumps during the plasma stage.
--     * Slot: min_longitudinal_position Description: Minimum longitudinal position [m].
--     * Slot: max_longitudinal_position Description: Maximum longitudinal position [m].
--     * Slot: n_longitudinal Description: Number of grid points in the longitudinal direction.
--     * Slot: n_radial Description: Number of grid points in the radial direction.
--     * Slot: plasma_particles_per_cell Description: Number of plasma particles per cell.
--     * Slot: r_max Description: Radial extent of the simulation box [m].
--     * Slot: r_max_plasma Description: Maximum radial extension of the plasma column.
--     * Slot: dz_fields Description: Interval for plasma wakefield updates.
--     * Slot: plasma_pusher Description: Pusher used to evolve the plasma in time.
--     * Slot: field_definition Description: Path to the 3-D field-map file.
--     * Slot: wakefield_definition Description: Path to the wakefield impedance file.
--     * Slot: field_reference_position Description: Longitudinal origin of the field map [m].
--     * Slot: scale_field Description: Multiplicative scale factor applied to the field map.
-- # Class: TwissMatchSimulationElement Description: Simulation attributes for Twiss-matching points.
--     * Slot: id
--     * Slot: beta_x Description: Horizontal beta.
--     * Slot: beta_y Description: Vertical beta.
--     * Slot: alpha_x Description: Horizontal alpha.
--     * Slot: alpha_y Description: Vertical alpha.
--     * Slot: eta_x Description: Horizontal dispersion.
--     * Slot: eta_y Description: Vertical dispersion.
--     * Slot: eta_xp Description: Horizontal dispersion derivative.
--     * Slot: eta_yp Description: Vertical dispersion derivative.
--     * Slot: from_beam Description: Compute transform from tracked beam properties.
--     * Slot: field_definition Description: Path to the 3-D field-map file.
--     * Slot: wakefield_definition Description: Path to the wakefield impedance file.
--     * Slot: field_reference_position Description: Longitudinal origin of the field map [m].
--     * Slot: scale_field Description: Multiplicative scale factor applied to the field map.
-- # Class: Multipole Description: Individual multipole field component, characterised by order and integrated normal / skew strengths at a reference radius.
--     * Slot: id
--     * Slot: order Description: Multipole order (0 = dipole, 1 = quadrupole, ?).
--     * Slot: normal Description: Integrated normal (upright) multipole strength [T.m^{1-n}].
--     * Slot: skew Description: Integrated skew (rotated) multipole strength [T.m^{1-n}].
--     * Slot: radius Description: Reference radius for multipole normalisation [m].
-- # Class: Multipoles Description: Complete set of integrated multipole strengths up to decapole order, as named slots for efficient element look-up.
--     * Slot: id
--     * Slot: K0L_id Description: Integrated dipole field.
--     * Slot: K1L_id Description: Integrated quadrupole gradient.
--     * Slot: K2L_id Description: Integrated sextupole strength.
--     * Slot: K3L_id Description: Integrated octupole strength.
--     * Slot: K4L_id Description: Integrated decapole strength.
-- # Class: FieldIntegral Description: Polynomial fit of integrated field strength as a function of magnet current.
--     * Slot: id
-- # Class: LinearSaturationFit Description: Bi-linear saturation model mapping magnet current to integrated field strength (K-value conversion).
--     * Slot: id
--     * Slot: m Description: Linear slope of the unsaturated region.
--     * Slot: I_max Description: Current at which saturation begins [A].
--     * Slot: f Description: Saturation fraction (slope ratio below/above I_max).
--     * Slot: a Description: Quadratic saturation coefficient.
--     * Slot: I0 Description: Current offset [A].
--     * Slot: d Description: Constant offset term.
--     * Slot: L Description: Effective magnetic length [m].
-- # Class: MagneticElement Description: Magnetic field parameters for a beamline magnet, including multipole components, field integrals, and geometric edge parameters.
--     * Slot: id
--     * Slot: order Description: Principal multipole order (0 = dipole, 1 = quad, ?).
--     * Slot: skew Description: Whether the magnet is rotated 45? to produce a skew field component.
--     * Slot: length Description: Magnetic (effective) length [m].
--     * Slot: settle_time Description: Power-supply settle time after a change [s].
--     * Slot: entrance_edge_angle Description: Fringe-field entrance edge angle [rad].
--     * Slot: exit_edge_angle Description: Fringe-field exit edge angle [rad].
--     * Slot: gap Description: Full gap between pole faces [m].
--     * Slot: bore Description: Magnet bore radius [m].
--     * Slot: plane Description: Principal bending / focusing plane (``Horizontal``, ``Vertical``, or ``Combined``).
--     * Slot: width Description: Physical width of the magnet in the bending plane [m].
--     * Slot: tilt Description: Global tilt about the beam axis [rad].
--     * Slot: edge_field_integral Description: Enge fringe-field integral parameter (dimensionless).
--     * Slot: fringe_field_coefficient Description: Coefficient controlling the fringe-field roll-off rate.
--     * Slot: gradient Description: Peak field gradient [T/m] (quads) or peak field [T] (dipoles).
--     * Slot: multipoles_id Description: Integrated multipole field components.
--     * Slot: systematic_multipoles_id Description: Systematic (design) multipole errors at the reference radius.
--     * Slot: random_multipoles_id Description: Random multipole errors at the reference radius.
--     * Slot: field_integral_coefficients_id Description: Polynomial calibration of integrated field vs. current.
--     * Slot: linear_saturation_coefficients_id Description: Bi-linear saturation calibration.
-- # Class: ApertureElement Description: Transverse aperture geometry for drift-space checks and collimators.
--     * Slot: id
--     * Slot: number_of_elements Description: Number of aperture sub-elements (e.g., for multi-leaf collimators).
--     * Slot: horizontal_size Description: Full horizontal aperture [m].
--     * Slot: vertical_size Description: Full vertical aperture [m].
--     * Slot: shape Description: Cross-sectional aperture shape.
--     * Slot: radius Description: Radius for circular apertures [m].
--     * Slot: negative_extent Description: Upstream / inner extent [m].
--     * Slot: positive_extent Description: Downstream / outer extent [m].
-- # Class: DegaussableElement Description: Degaussing (demagnetisation cycle) parameters for magnets that require a field-reset procedure.
--     * Slot: id
--     * Slot: tolerance Description: Current tolerance band during the degauss cycle [A].
--     * Slot: steps Description: Number of degauss steps per half-cycle.
-- # Class: RFCavityElement Description: RF cavity accelerating-structure parameters.
--     * Slot: id
--     * Slot: cell_length Description: Length of a single cell [m].
--     * Slot: coupling_cell_length Description: Length of the coupling cell [m].
--     * Slot: design_gamma Description: Design Lorentz factor.
--     * Slot: design_power Description: Design peak power [W].
--     * Slot: frequency Description: Operating frequency [Hz].
--     * Slot: n_cells Description: Number of cells.
--     * Slot: crest Description: On-crest phase offset providing maximum energy gain [deg].
--     * Slot: phase Description: Operating phase offset [deg].
--     * Slot: shunt_impedance Description: Shunt impedance [M?/m].
--     * Slot: mode_numerator Description: Mode fraction numerator.
--     * Slot: mode_denominator Description: Mode fraction denominator.
--     * Slot: structure_type Description: RF structure type (e.g., ``SW`` standing-wave, ``TW`` travelling-wave).
--     * Slot: attenuation_constant Description: Attenuation constant ? of a travelling-wave structure [Np/m].
-- # Class: WakefieldElement Description: Passive wakefield structure parameters.
--     * Slot: id
--     * Slot: cell_length Description: Length of a single cell [m].
--     * Slot: n_cells Description: Number of cells.
--     * Slot: coupling_cell_length Description: Length of the coupling cell [m].
-- # Class: RFDeflectingCavityElement Description: Transverse-deflecting RF cavity parameters -- a subset of RFCavityElement for streak-mode operation.
--     * Slot: id
--     * Slot: cell_length Description: Length of a single cell [m].
--     * Slot: coupling_cell_length Description: Length of the coupling cell [m].
--     * Slot: crest Description: On-crest phase offset providing maximum energy gain [deg].
--     * Slot: design_gamma Description: Design Lorentz factor.
--     * Slot: design_power Description: Design peak power [W].
--     * Slot: frequency Description: Operating frequency [Hz].
--     * Slot: n_cells Description: Number of cells.
--     * Slot: phase Description: Operating phase offset [deg].
--     * Slot: shunt_impedance Description: Shunt impedance [M?/m].
--     * Slot: mode_numerator Description: Mode fraction numerator.
--     * Slot: mode_denominator Description: Mode fraction denominator.
-- # Class: PIDElement Description: PID feedback-controller parameters.
--     * Slot: id
--     * Slot: Kp Description: Proportional gain.
--     * Slot: Ki Description: Integral gain.
--     * Slot: Kd Description: Derivative gain.
--     * Slot: forward_channel Description: Forward channel index.
--     * Slot: probe_channel Description: Probe channel index.
--     * Slot: enable Description: Enable command/value.
--     * Slot: disable Description: Disable command/value.
--     * Slot: phase_range_id Description: Phase tuning range.
--     * Slot: phase_weight_range_id Description: Phase weighting range.
-- # Class: PIDPhaseRange Description: Numeric min/max range for PID phase control.
--     * Slot: id
--     * Slot: min Description: Minimum value.
--     * Slot: max Description: Maximum value.
-- # Class: PIDWeightRange Description: Numeric min/max range for PID phase weighting.
--     * Slot: id
--     * Slot: min Description: Minimum value.
--     * Slot: max Description: Maximum value.
-- # Class: Trace Description: LLRF trace metadata.
--     * Slot: id
--     * Slot: data_size Description: Number of points in a trace.
--     * Slot: data_count Description: Number of one-record trace entries.
--     * Slot: data_chunk_size Description: Chunk size for one-record traces.
--     * Slot: number_of_start_zeros Description: Number of leading zeros in a trace.
-- # Class: ChannelNames Description: Names for LLRF channels 1..8.
--     * Slot: id
--     * Slot: ch1
--     * Slot: ch2
--     * Slot: ch3
--     * Slot: ch4
--     * Slot: ch5
--     * Slot: ch6
--     * Slot: ch7
--     * Slot: ch8
-- # Class: LLRFTiming Description: Start/end window timing definition.
--     * Slot: id
--     * Slot: start Description: Start time.
--     * Slot: end Description: End time.
-- # Class: LLRFTimings Description: Collection of timing windows for key LLRF channels.
--     * Slot: id
--     * Slot: klystron_forward_id Description: Timing for klystron forward power.
--     * Slot: klystron_reverse_id Description: Timing for klystron reverse power.
--     * Slot: cavity_forward_id Description: Timing for cavity forward power.
--     * Slot: cavity_reverse_id Description: Timing for cavity reverse power.
--     * Slot: cavity_probe_id Description: Timing for cavity probe.
-- # Class: LowLevelRFElement Description: Low-level RF (LLRF) system parameters.
--     * Slot: id
--     * Slot: max_amplitude Description: Maximum allowed amplitude.
--     * Slot: crest_phase Description: Cavity crest phase.
--     * Slot: trace_id Description: Trace metadata.
--     * Slot: channel_names_id Description: Channel labels.
--     * Slot: timings_id Description: Timing windows for LLRF channels.
-- # Class: RFModulatorElement Description: RF modulator (klystron driver) parameters.
--     * Slot: id
-- # Class: RFProtectionElement Description: RF protection system parameters.
--     * Slot: id
--     * Slot: prot_type Description: Protection system type.
-- # Class: RFHeartbeatElement Description: RF heartbeat / timing-monitor element parameters.
--     * Slot: id
-- # Class: DiagnosticElement Description: Base class for diagnostic instrument sub-models.  Concrete sub-models extend this with instrument-specific fields.
--     * Slot: id
-- # Class: BPMDiagnosticElement Description: Beam-position monitor (BPM) diagnostic data.
--     * Slot: id
--     * Slot: type Description: BPM type (e.g., ``Stripline``, ``Cavity``, ``Button``). Accepted in YAML as ``bpm_type``.
-- # Class: BAMDiagnosticElement Description: Beam-arrival monitor (BAM) diagnostic data.
--     * Slot: id
--     * Slot: type Description: BAM type. Accepted in YAML as ``bam_type``.
-- # Class: BLMDiagnosticElement Description: Bunch-length monitor (BLM) diagnostic data.
--     * Slot: id
--     * Slot: type Description: BLM type (e.g., ``CDR``). Accepted in YAML as ``blm_type``.
-- # Class: ScreenDiagnosticElement Description: Scintillator or OTR screen diagnostic data.
--     * Slot: id
--     * Slot: type Description: Screen type (e.g., ``OTR``, ``YAG``).
--     * Slot: has_camera Description: Whether the screen has an associated camera.
--     * Slot: camera_name Description: Name of the associated camera element.
-- # Class: ChargeDiagnosticElement Description: Charge-measurement diagnostic data (base for ICT, FCM, WCM).
--     * Slot: id
--     * Slot: type Description: Charge-diagnostic type. Accepted in YAML as ``charge_type``.
-- # Class: CameraPixelResultsIndices Description: Indices into camera pixel-analysis result arrays.
--     * Slot: id
--     * Slot: x Description: Beam centroid index in x.
--     * Slot: y Description: Beam centroid index in y.
--     * Slot: x_sigma Description: Beam sigma index in x.
--     * Slot: y_sigma Description: Beam sigma index in y.
--     * Slot: covariance Description: Beam covariance index.
-- # Class: CameraPixelResultsNames Description: Names of camera pixel-analysis result arrays.
--     * Slot: id
--     * Slot: x Description: Beam centroid name in x.
--     * Slot: y Description: Beam centroid name in y.
--     * Slot: x_sigma Description: Beam sigma name in x.
--     * Slot: y_sigma Description: Beam sigma name in y.
--     * Slot: covariance Description: Beam covariance name.
-- # Class: CameraMask Description: Camera analysis mask parameters.
--     * Slot: id
--     * Slot: use_maximum_values Description: If True, use maximum mask radius constraints.
-- # Class: CameraSensor Description: Camera sensor hardware configuration.
--     * Slot: id
--     * Slot: x_pixels Description: Raw sensor pixel count in x.
--     * Slot: y_pixels Description: Raw sensor pixel count in y.
--     * Slot: x_scale_factor Description: Pixel binning factor in x.
--     * Slot: y_scale_factor Description: Pixel binning factor in y.
--     * Slot: beam_pixel_average Description: Average pixel value for beam detection.
--     * Slot: x_pixels_to_mm Description: Pixel-to-mm scale factor in x.
--     * Slot: y_pixels_to_mm Description: Pixel-to-mm scale factor in y.
--     * Slot: bit_depth Description: Camera bit depth.
-- # Class: CameraDiagnosticElement Description: Camera diagnostic data, including sensor parameters, analysis mask, and pixel-to-mm scale factors.
--     * Slot: id
--     * Slot: type Description: Camera type / model string (e.g., ``PCO``, ``Manta``). Accepted in YAML as ``CAM_TYPE``.
--     * Slot: x_pixels Description: Image width reported by the control system [pix].
--     * Slot: y_pixels Description: Image height reported by the control system [pix].
--     * Slot: rotation Description: Camera rotation relative to the screen plane [deg].
--     * Slot: flipped_horizontally Description: True if the image is mirrored left-right.
--     * Slot: flipped_vertically Description: True if the image is mirrored top-bottom.
--     * Slot: screen_name Description: Name of the screen element to which this camera is attached.
--     * Slot: has_led Description: True if the camera mount includes an LED backlight.
--     * Slot: pixel_results_indices_id Description: Indices of pixel analysis result arrays.
--     * Slot: pixel_results_names_id Description: Names of pixel analysis result arrays.
--     * Slot: mask_id Description: Camera analysis mask configuration.
--     * Slot: sensor_id Description: Camera sensor hardware configuration.
-- # Class: LaserElement Description: Laser-beam parameters (wavelength, pulse energy, profile, etc.) for a laser element or laser-driven plasma stage.
--     * Slot: id
--     * Slot: initial_position Description: Initial longitudinal position of the laser pulse [m].
--     * Slot: waist Description: Laser beam waist (1/e^2 radius) [m].
--     * Slot: wavelength Description: Laser wavelength [m].
--     * Slot: pulse_energy Description: Laser pulse energy [J].
--     * Slot: pulse_duration_fwhm Description: Pulse duration at FWHM [s].
--     * Slot: focal_position Description: Focal (waist) position along the propagation axis [m].
--     * Slot: cep_phase Description: Carrier-envelope phase [rad].
--     * Slot: polarization Description: Laser polarization state.
--     * Slot: profile_type Description: Transverse intensity profile model.
--     * Slot: laguerre_polynomial_order_p Description: Radial Laguerre-Gaussian mode index p (for ``profile_type = laguerre-gaussian``).
--     * Slot: flatness Description: Flatness order N of a flattened-Gaussian profile (for ``profile_type = flattened-gaussian``).
-- # Class: LaserEnergyMeterElement Description: Laser energy-meter sub-model (no additional fields).
--     * Slot: id
-- # Class: LaserHalfWavePlateElement Description: Half-wave plate sub-model (no additional fields).
--     * Slot: id
-- # Class: PlasmaElement Description: Plasma channel parameters for a laser-driven plasma-accelerator stage.
--     * Slot: id
--     * Slot: density Description: Plasma (electron) number density [m^-^3].
--     * Slot: species Description: Plasma species name (e.g., ``electron``).
--     * Slot: ramp_up Description: Entrance density-ramp length [m].
--     * Slot: plateau Description: Flat-top plateau length [m].
--     * Slot: ramp_down Description: Exit density-ramp length [m].
--     * Slot: ramp_decay_length Description: Exponential decay length of the density ramp [m].
--     * Slot: density_profile Description: If True, use a user-defined profile; if False, use a flat-top model.
--     * Slot: parabolic_coefficient Description: Parabolic coefficient for a transverse density profile.
-- # Class: ReferenceElement_drawings
--     * Slot: ReferenceElement_id Description: Autocreated FK slot
--     * Slot: drawings Description: Engineering-drawing identifiers or URIs.
-- # Class: ReferenceElement_design_files
--     * Slot: ReferenceElement_id Description: Autocreated FK slot
--     * Slot: design_files Description: Design-file paths or URIs.
-- # Class: ControlsInformation_variables
--     * Slot: ControlsInformation_id Description: Autocreated FK slot
--     * Slot: variables_id Description: Named control variables keyed by logical name.
-- # Class: ShutterElement_interlocks
--     * Slot: ShutterElement_id Description: Autocreated FK slot
--     * Slot: interlocks Description: Names of the interlocks guarding this shutter.
-- # Class: AcceleratorElement_alias
--     * Slot: AcceleratorElement_name Description: Autocreated FK slot
--     * Slot: alias Description: Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.
-- # Class: StandardElement_alias
--     * Slot: StandardElement_name Description: Autocreated FK slot
--     * Slot: alias Description: Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.
-- # Class: Element_alias
--     * Slot: Element_name Description: Autocreated FK slot
--     * Slot: alias Description: Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.
-- # Class: PhysicalAcceleratorElement_alias
--     * Slot: PhysicalAcceleratorElement_name Description: Autocreated FK slot
--     * Slot: alias Description: Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.
-- # Class: MagnetBaseElement_alias
--     * Slot: MagnetBaseElement_name Description: Autocreated FK slot
--     * Slot: alias Description: Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.
-- # Class: Diagnostic_alias
--     * Slot: Diagnostic_name Description: Autocreated FK slot
--     * Slot: alias Description: Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.
-- # Class: BeamPositionMonitor_alias
--     * Slot: BeamPositionMonitor_name Description: Autocreated FK slot
--     * Slot: alias Description: Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.
-- # Class: BeamArrivalMonitor_alias
--     * Slot: BeamArrivalMonitor_name Description: Autocreated FK slot
--     * Slot: alias Description: Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.
-- # Class: BunchLengthMonitor_alias
--     * Slot: BunchLengthMonitor_name Description: Autocreated FK slot
--     * Slot: alias Description: Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.
-- # Class: Camera_alias
--     * Slot: Camera_name Description: Autocreated FK slot
--     * Slot: alias Description: Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.
-- # Class: Screen_alias
--     * Slot: Screen_name Description: Autocreated FK slot
--     * Slot: alias Description: Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.
-- # Class: ChargeDiagnostic_alias
--     * Slot: ChargeDiagnostic_name Description: Autocreated FK slot
--     * Slot: alias Description: Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.
-- # Class: WallCurrentMonitor_alias
--     * Slot: WallCurrentMonitor_name Description: Autocreated FK slot
--     * Slot: alias Description: Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.
-- # Class: FaradayCupMonitor_alias
--     * Slot: FaradayCupMonitor_name Description: Autocreated FK slot
--     * Slot: alias Description: Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.
-- # Class: IntegratedCurrentTransformer_alias
--     * Slot: IntegratedCurrentTransformer_name Description: Autocreated FK slot
--     * Slot: alias Description: Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.
-- # Class: RFCavity_alias
--     * Slot: RFCavity_name Description: Autocreated FK slot
--     * Slot: alias Description: Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.
-- # Class: RFDeflectingCavity_alias
--     * Slot: RFDeflectingCavity_name Description: Autocreated FK slot
--     * Slot: alias Description: Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.
-- # Class: Wakefield_alias
--     * Slot: Wakefield_name Description: Autocreated FK slot
--     * Slot: alias Description: Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.
-- # Class: LowLevelRF_alias
--     * Slot: LowLevelRF_name Description: Autocreated FK slot
--     * Slot: alias Description: Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.
-- # Class: RFModulator_alias
--     * Slot: RFModulator_name Description: Autocreated FK slot
--     * Slot: alias Description: Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.
-- # Class: RFProtection_alias
--     * Slot: RFProtection_name Description: Autocreated FK slot
--     * Slot: alias Description: Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.
-- # Class: RFHeartbeat_alias
--     * Slot: RFHeartbeat_name Description: Autocreated FK slot
--     * Slot: alias Description: Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.
-- # Class: PID_alias
--     * Slot: PID_name Description: Autocreated FK slot
--     * Slot: alias Description: Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.
-- # Class: TwissMatch_alias
--     * Slot: TwissMatch_name Description: Autocreated FK slot
--     * Slot: alias Description: Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.
-- # Class: Stage_alias
--     * Slot: Stage_name Description: Autocreated FK slot
--     * Slot: alias Description: Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.
-- # Class: VacuumGauge_alias
--     * Slot: VacuumGauge_name Description: Autocreated FK slot
--     * Slot: alias Description: Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.
-- # Class: Laser_alias
--     * Slot: Laser_name Description: Autocreated FK slot
--     * Slot: alias Description: Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.
-- # Class: Shutter_alias
--     * Slot: Shutter_name Description: Autocreated FK slot
--     * Slot: alias Description: Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.
-- # Class: Valve_alias
--     * Slot: Valve_name Description: Autocreated FK slot
--     * Slot: alias Description: Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.
-- # Class: Marker_alias
--     * Slot: Marker_name Description: Autocreated FK slot
--     * Slot: alias Description: Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.
-- # Class: Aperture_alias
--     * Slot: Aperture_name Description: Autocreated FK slot
--     * Slot: alias Description: Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.
-- # Class: Collimator_alias
--     * Slot: Collimator_name Description: Autocreated FK slot
--     * Slot: alias Description: Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.
-- # Class: Drift_alias
--     * Slot: Drift_name Description: Autocreated FK slot
--     * Slot: alias Description: Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.
-- # Class: Plasma_alias
--     * Slot: Plasma_name Description: Autocreated FK slot
--     * Slot: alias Description: Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.
-- # Class: LaserEnergyMeter_alias
--     * Slot: LaserEnergyMeter_name Description: Autocreated FK slot
--     * Slot: alias Description: Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.
-- # Class: LaserHalfWavePlate_alias
--     * Slot: LaserHalfWavePlate_name Description: Autocreated FK slot
--     * Slot: alias Description: Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.
-- # Class: LaserMirror_alias
--     * Slot: LaserMirror_name Description: Autocreated FK slot
--     * Slot: alias Description: Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.
-- # Class: LaserAttenuator_alias
--     * Slot: LaserAttenuator_name Description: Autocreated FK slot
--     * Slot: alias Description: Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.
-- # Class: Lighting_alias
--     * Slot: Lighting_name Description: Autocreated FK slot
--     * Slot: alias Description: Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.
-- # Class: SectionLattice_elements
--     * Slot: SectionLattice_name Description: Autocreated FK slot
--     * Slot: elements Description: Ordered list of element names in this section.
-- # Class: MachineLayout_sections
--     * Slot: MachineLayout_name Description: Autocreated FK slot
--     * Slot: sections Description: Ordered list of section names.
-- # Class: MachineModel_elements
--     * Slot: MachineModel_id Description: Autocreated FK slot
--     * Slot: elements_name Description: All elements in the machine, keyed by name.
-- # Class: MachineModel_sections
--     * Slot: MachineModel_id Description: Autocreated FK slot
--     * Slot: sections_name Description: All named beamline sections.
-- # Class: MachineModel_layouts
--     * Slot: MachineModel_id Description: Autocreated FK slot
--     * Slot: layouts_name Description: All named beamline layouts.
-- # Class: FieldIntegral_coefficients
--     * Slot: FieldIntegral_id Description: Autocreated FK slot
--     * Slot: coefficients Description: Polynomial coefficients ordered from lowest to highest degree: ``FieldIntegral = sum c_n . I^n``.
-- # Class: DegaussableElement_values
--     * Slot: DegaussableElement_id Description: Autocreated FK slot
--     * Slot: values Description: Sequence of peak currents applied during the degauss cycle [A].
-- # Class: RFCavityElement_power_calibration
--     * Slot: RFCavityElement_id Description: Autocreated FK slot
--     * Slot: power_calibration Description: Calibration constant relating measured power to cavity gradient.
-- # Class: RFCavityElement_gradient_calibration
--     * Slot: RFCavityElement_id Description: Autocreated FK slot
--     * Slot: gradient_calibration Description: Calibration relating measured signal to gradient [MV/m per a.u.].
-- # Class: ScreenDiagnosticElement_devices
--     * Slot: ScreenDiagnosticElement_id Description: Autocreated FK slot
--     * Slot: devices Description: List of attached devices.
-- # Class: CameraMask_middle
--     * Slot: CameraMask_id Description: Autocreated FK slot
--     * Slot: middle Description: Center of the mask in pixels [x, y].
-- # Class: CameraMask_radius
--     * Slot: CameraMask_id Description: Autocreated FK slot
--     * Slot: radius Description: Mask radius in pixels [x, y].
-- # Class: CameraMask_maximum
--     * Slot: CameraMask_id Description: Autocreated FK slot
--     * Slot: maximum Description: Maximum mask radius in pixels [x, y].
-- # Class: CameraSensor_middle
--     * Slot: CameraSensor_id Description: Autocreated FK slot
--     * Slot: middle Description: Sensor optical center in pixels [x, y].
-- # Class: CameraSensor_minimum
--     * Slot: CameraSensor_id Description: Autocreated FK slot
--     * Slot: minimum Description: Minimum pixel positions [x, y].
-- # Class: CameraSensor_maximum
--     * Slot: CameraSensor_id Description: Autocreated FK slot
--     * Slot: maximum Description: Maximum pixel positions [x, y].
-- # Class: CameraSensor_operating_middle
--     * Slot: CameraSensor_id Description: Autocreated FK slot
--     * Slot: operating_middle Description: Operating center positions in pixels [x, y].
-- # Class: CameraSensor_mechanical_middle
--     * Slot: CameraSensor_id Description: Autocreated FK slot
--     * Slot: mechanical_middle Description: Mechanical center of the camera in pixels [x, y].

CREATE TABLE "Position" (
	id INTEGER NOT NULL,
	x FLOAT,
	y FLOAT,
	z FLOAT,
	PRIMARY KEY (id)
);
CREATE INDEX "ix_Position_id" ON "Position" (id);

CREATE TABLE "Rotation" (
	id INTEGER NOT NULL,
	phi FLOAT,
	psi FLOAT,
	theta FLOAT,
	PRIMARY KEY (id)
);
CREATE INDEX "ix_Rotation_id" ON "Rotation" (id);

CREATE TABLE "ElectricalElement" (
	id INTEGER NOT NULL,
	min_i FLOAT,
	max_i FLOAT,
	read_tolerance FLOAT,
	PRIMARY KEY (id)
);
CREATE INDEX "ix_ElectricalElement_id" ON "ElectricalElement" (id);

CREATE TABLE "ManufacturerElement" (
	id INTEGER NOT NULL,
	manufacturer TEXT,
	serial_number TEXT,
	PRIMARY KEY (id)
);
CREATE INDEX "ix_ManufacturerElement_id" ON "ManufacturerElement" (id);

CREATE TABLE "ReferenceElement" (
	id INTEGER NOT NULL,
	PRIMARY KEY (id)
);
CREATE INDEX "ix_ReferenceElement_id" ON "ReferenceElement" (id);

CREATE TABLE "ControlVariable" (
	id INTEGER NOT NULL,
	identifier TEXT,
	dtype TEXT,
	protocol TEXT,
	units TEXT,
	description TEXT,
	read_only BOOLEAN,
	value FLOAT,
	target FLOAT,
	expression TEXT,
	PRIMARY KEY (id)
);
CREATE INDEX "ix_ControlVariable_id" ON "ControlVariable" (id);

CREATE TABLE "ControlsInformation" (
	id INTEGER NOT NULL,
	PRIMARY KEY (id)
);
CREATE INDEX "ix_ControlsInformation_id" ON "ControlsInformation" (id);

CREATE TABLE "ShutterElement" (
	id INTEGER NOT NULL,
	PRIMARY KEY (id)
);
CREATE INDEX "ix_ShutterElement_id" ON "ShutterElement" (id);

CREATE TABLE "ValveElement" (
	id INTEGER NOT NULL,
	PRIMARY KEY (id)
);
CREATE INDEX "ix_ValveElement_id" ON "ValveElement" (id);

CREATE TABLE "LightingElement" (
	id INTEGER NOT NULL,
	PRIMARY KEY (id)
);
CREATE INDEX "ix_LightingElement_id" ON "LightingElement" (id);

CREATE TABLE "AcceleratorElement" (
	name TEXT NOT NULL,
	hardware_class VARCHAR(10) NOT NULL,
	hardware_type TEXT,
	hardware_model TEXT,
	machine_area TEXT,
	virtual_name TEXT,
	subelement TEXT,
	PRIMARY KEY (name)
);
CREATE INDEX "ix_AcceleratorElement_name" ON "AcceleratorElement" (name);

CREATE TABLE "LaserMirrorSense" (
	id INTEGER NOT NULL,
	"left" FLOAT,
	"right" FLOAT,
	up FLOAT,
	down FLOAT,
	PRIMARY KEY (id)
);
CREATE INDEX "ix_LaserMirrorSense_id" ON "LaserMirrorSense" (id);

CREATE TABLE "SectionLattice" (
	name TEXT NOT NULL,
	master_lattice TEXT,
	PRIMARY KEY (name)
);
CREATE INDEX "ix_SectionLattice_name" ON "SectionLattice" (name);

CREATE TABLE "MachineLayout" (
	name TEXT NOT NULL,
	master_lattice TEXT,
	PRIMARY KEY (name)
);
CREATE INDEX "ix_MachineLayout_name" ON "MachineLayout" (name);

CREATE TABLE "MachineModel" (
	id INTEGER NOT NULL,
	PRIMARY KEY (id)
);
CREATE INDEX "ix_MachineModel_id" ON "MachineModel" (id);

CREATE TABLE "SimulationElement" (
	id INTEGER NOT NULL,
	field_definition TEXT,
	wakefield_definition TEXT,
	field_reference_position TEXT,
	scale_field FLOAT,
	PRIMARY KEY (id)
);
CREATE INDEX "ix_SimulationElement_id" ON "SimulationElement" (id);

CREATE TABLE "MagnetSimulationElement" (
	id INTEGER NOT NULL,
	n_kicks INTEGER,
	field_amplitude FLOAT,
	n_slices INTEGER,
	smooth BOOLEAN,
	edge_field_integral FLOAT,
	edge1_effects BOOLEAN,
	edge2_effects BOOLEAN,
	sr_enable BOOLEAN,
	isr_enable BOOLEAN,
	csr_enable BOOLEAN,
	csr_bins INTEGER,
	integration_order INTEGER,
	nonlinear BOOLEAN,
	smoothing_half_width INTEGER,
	edge_order INTEGER,
	"deltaL" FLOAT,
	smooth_points FLOAT,
	field_definition TEXT,
	wakefield_definition TEXT,
	field_reference_position TEXT,
	scale_field FLOAT,
	PRIMARY KEY (id)
);
CREATE INDEX "ix_MagnetSimulationElement_id" ON "MagnetSimulationElement" (id);

CREATE TABLE "RFCavitySimulationElement" (
	id INTEGER NOT NULL,
	t_column TEXT,
	z_column TEXT,
	wx_column TEXT,
	wy_column TEXT,
	wz_column TEXT,
	n_kicks INTEGER,
	lsc_bins INTEGER,
	field_amplitude FLOAT,
	change_p0 INTEGER,
	end1_focus INTEGER,
	end2_focus INTEGER,
	body_focus_model TEXT,
	current_bins INTEGER,
	interpolate_current_bins INTEGER,
	smooth_current_bins INTEGER,
	smooth INTEGER,
	ez_peak FLOAT,
	field_file_name TEXT,
	wakefile TEXT,
	zwakefile TEXT,
	trwakefile TEXT,
	field_definition TEXT,
	wakefield_definition TEXT,
	field_reference_position TEXT,
	scale_field FLOAT,
	PRIMARY KEY (id)
);
CREATE INDEX "ix_RFCavitySimulationElement_id" ON "RFCavitySimulationElement" (id);

CREATE TABLE "WakefieldSimulationElement" (
	id INTEGER NOT NULL,
	t_column TEXT,
	z_column TEXT,
	wx_column TEXT,
	wy_column TEXT,
	wz_column TEXT,
	allow_long_beam BOOLEAN,
	bunched_beam BOOLEAN,
	change_momentum BOOLEAN,
	factor FLOAT,
	interpolate BOOLEAN,
	scale_kick FLOAT,
	scale_field_ex FLOAT,
	scale_field_ey FLOAT,
	scale_field_ez FLOAT,
	scale_field_hx FLOAT,
	scale_field_hy FLOAT,
	scale_field_hz FLOAT,
	equal_grid FLOAT,
	interpolation_method INTEGER,
	smooth FLOAT,
	subbins INTEGER,
	field_definition TEXT,
	wakefield_definition TEXT,
	field_reference_position TEXT,
	scale_field FLOAT,
	PRIMARY KEY (id)
);
CREATE INDEX "ix_WakefieldSimulationElement_id" ON "WakefieldSimulationElement" (id);

CREATE TABLE "DriftSimulationElement" (
	id INTEGER NOT NULL,
	lsc_bins INTEGER,
	lsc_interpolate INTEGER,
	csr_enable BOOLEAN,
	lsc_enable BOOLEAN,
	use_stupakov INTEGER,
	csrdz FLOAT,
	lsc_high_frequency_cutoff_start FLOAT,
	lsc_high_frequency_cutoff_end FLOAT,
	lsc_low_frequency_cutoff_start FLOAT,
	lsc_low_frequency_cutoff_end FLOAT,
	field_definition TEXT,
	wakefield_definition TEXT,
	field_reference_position TEXT,
	scale_field FLOAT,
	PRIMARY KEY (id)
);
CREATE INDEX "ix_DriftSimulationElement_id" ON "DriftSimulationElement" (id);

CREATE TABLE "DiagnosticSimulationElement" (
	id INTEGER NOT NULL,
	output_filename TEXT,
	field_definition TEXT,
	wakefield_definition TEXT,
	field_reference_position TEXT,
	scale_field FLOAT,
	PRIMARY KEY (id)
);
CREATE INDEX "ix_DiagnosticSimulationElement_id" ON "DiagnosticSimulationElement" (id);

CREATE TABLE "PlasmaSimulationElement" (
	id INTEGER NOT NULL,
	wakefield_model TEXT,
	bunch_pusher TEXT,
	dt_bunch TEXT,
	n_out INTEGER,
	min_longitudinal_position FLOAT,
	max_longitudinal_position FLOAT,
	n_longitudinal INTEGER,
	n_radial INTEGER,
	plasma_particles_per_cell INTEGER,
	r_max FLOAT,
	r_max_plasma FLOAT,
	dz_fields FLOAT,
	plasma_pusher TEXT,
	field_definition TEXT,
	wakefield_definition TEXT,
	field_reference_position TEXT,
	scale_field FLOAT,
	PRIMARY KEY (id)
);
CREATE INDEX "ix_PlasmaSimulationElement_id" ON "PlasmaSimulationElement" (id);

CREATE TABLE "TwissMatchSimulationElement" (
	id INTEGER NOT NULL,
	beta_x FLOAT,
	beta_y FLOAT,
	alpha_x FLOAT,
	alpha_y FLOAT,
	eta_x FLOAT,
	eta_y FLOAT,
	eta_xp FLOAT,
	eta_yp FLOAT,
	from_beam BOOLEAN,
	field_definition TEXT,
	wakefield_definition TEXT,
	field_reference_position TEXT,
	scale_field FLOAT,
	PRIMARY KEY (id)
);
CREATE INDEX "ix_TwissMatchSimulationElement_id" ON "TwissMatchSimulationElement" (id);

CREATE TABLE "Multipole" (
	id INTEGER NOT NULL,
	"order" INTEGER,
	normal FLOAT,
	skew FLOAT,
	radius FLOAT,
	PRIMARY KEY (id)
);
CREATE INDEX "ix_Multipole_id" ON "Multipole" (id);

CREATE TABLE "FieldIntegral" (
	id INTEGER NOT NULL,
	PRIMARY KEY (id)
);
CREATE INDEX "ix_FieldIntegral_id" ON "FieldIntegral" (id);

CREATE TABLE "LinearSaturationFit" (
	id INTEGER NOT NULL,
	m FLOAT,
	"I_max" FLOAT,
	f FLOAT,
	a FLOAT,
	"I0" FLOAT,
	d FLOAT,
	"L" FLOAT,
	PRIMARY KEY (id)
);
CREATE INDEX "ix_LinearSaturationFit_id" ON "LinearSaturationFit" (id);

CREATE TABLE "ApertureElement" (
	id INTEGER NOT NULL,
	number_of_elements INTEGER,
	horizontal_size FLOAT,
	vertical_size FLOAT,
	shape VARCHAR(11),
	radius FLOAT,
	negative_extent FLOAT,
	positive_extent FLOAT,
	PRIMARY KEY (id)
);
CREATE INDEX "ix_ApertureElement_id" ON "ApertureElement" (id);

CREATE TABLE "DegaussableElement" (
	id INTEGER NOT NULL,
	tolerance FLOAT,
	steps INTEGER,
	PRIMARY KEY (id)
);
CREATE INDEX "ix_DegaussableElement_id" ON "DegaussableElement" (id);

CREATE TABLE "RFCavityElement" (
	id INTEGER NOT NULL,
	cell_length FLOAT,
	coupling_cell_length FLOAT,
	design_gamma FLOAT,
	design_power FLOAT,
	frequency FLOAT,
	n_cells INTEGER,
	crest FLOAT,
	phase FLOAT,
	shunt_impedance FLOAT,
	mode_numerator INTEGER,
	mode_denominator INTEGER,
	structure_type TEXT,
	attenuation_constant FLOAT,
	PRIMARY KEY (id)
);
CREATE INDEX "ix_RFCavityElement_id" ON "RFCavityElement" (id);

CREATE TABLE "WakefieldElement" (
	id INTEGER NOT NULL,
	cell_length FLOAT,
	n_cells INTEGER,
	coupling_cell_length FLOAT,
	PRIMARY KEY (id)
);
CREATE INDEX "ix_WakefieldElement_id" ON "WakefieldElement" (id);

CREATE TABLE "RFDeflectingCavityElement" (
	id INTEGER NOT NULL,
	cell_length FLOAT,
	coupling_cell_length FLOAT,
	crest FLOAT,
	design_gamma FLOAT,
	design_power FLOAT,
	frequency FLOAT,
	n_cells INTEGER,
	phase FLOAT,
	shunt_impedance FLOAT,
	mode_numerator INTEGER,
	mode_denominator INTEGER,
	PRIMARY KEY (id)
);
CREATE INDEX "ix_RFDeflectingCavityElement_id" ON "RFDeflectingCavityElement" (id);

CREATE TABLE "PIDPhaseRange" (
	id INTEGER NOT NULL,
	min FLOAT,
	max FLOAT,
	PRIMARY KEY (id)
);
CREATE INDEX "ix_PIDPhaseRange_id" ON "PIDPhaseRange" (id);

CREATE TABLE "PIDWeightRange" (
	id INTEGER NOT NULL,
	min FLOAT,
	max FLOAT,
	PRIMARY KEY (id)
);
CREATE INDEX "ix_PIDWeightRange_id" ON "PIDWeightRange" (id);

CREATE TABLE "Trace" (
	id INTEGER NOT NULL,
	data_size INTEGER,
	data_count INTEGER,
	data_chunk_size INTEGER,
	number_of_start_zeros INTEGER,
	PRIMARY KEY (id)
);
CREATE INDEX "ix_Trace_id" ON "Trace" (id);

CREATE TABLE "ChannelNames" (
	id INTEGER NOT NULL,
	ch1 TEXT,
	ch2 TEXT,
	ch3 TEXT,
	ch4 TEXT,
	ch5 TEXT,
	ch6 TEXT,
	ch7 TEXT,
	ch8 TEXT,
	PRIMARY KEY (id)
);
CREATE INDEX "ix_ChannelNames_id" ON "ChannelNames" (id);

CREATE TABLE "LLRFTiming" (
	id INTEGER NOT NULL,
	start FLOAT,
	"end" FLOAT,
	PRIMARY KEY (id)
);
CREATE INDEX "ix_LLRFTiming_id" ON "LLRFTiming" (id);

CREATE TABLE "RFModulatorElement" (
	id INTEGER NOT NULL,
	PRIMARY KEY (id)
);
CREATE INDEX "ix_RFModulatorElement_id" ON "RFModulatorElement" (id);

CREATE TABLE "RFProtectionElement" (
	id INTEGER NOT NULL,
	prot_type TEXT,
	PRIMARY KEY (id)
);
CREATE INDEX "ix_RFProtectionElement_id" ON "RFProtectionElement" (id);

CREATE TABLE "RFHeartbeatElement" (
	id INTEGER NOT NULL,
	PRIMARY KEY (id)
);
CREATE INDEX "ix_RFHeartbeatElement_id" ON "RFHeartbeatElement" (id);

CREATE TABLE "DiagnosticElement" (
	id INTEGER NOT NULL,
	PRIMARY KEY (id)
);
CREATE INDEX "ix_DiagnosticElement_id" ON "DiagnosticElement" (id);

CREATE TABLE "BPMDiagnosticElement" (
	id INTEGER NOT NULL,
	type TEXT,
	PRIMARY KEY (id)
);
CREATE INDEX "ix_BPMDiagnosticElement_id" ON "BPMDiagnosticElement" (id);

CREATE TABLE "BAMDiagnosticElement" (
	id INTEGER NOT NULL,
	type TEXT,
	PRIMARY KEY (id)
);
CREATE INDEX "ix_BAMDiagnosticElement_id" ON "BAMDiagnosticElement" (id);

CREATE TABLE "BLMDiagnosticElement" (
	id INTEGER NOT NULL,
	type TEXT,
	PRIMARY KEY (id)
);
CREATE INDEX "ix_BLMDiagnosticElement_id" ON "BLMDiagnosticElement" (id);

CREATE TABLE "ScreenDiagnosticElement" (
	id INTEGER NOT NULL,
	type TEXT,
	has_camera BOOLEAN,
	camera_name TEXT,
	PRIMARY KEY (id)
);
CREATE INDEX "ix_ScreenDiagnosticElement_id" ON "ScreenDiagnosticElement" (id);

CREATE TABLE "ChargeDiagnosticElement" (
	id INTEGER NOT NULL,
	type TEXT,
	PRIMARY KEY (id)
);
CREATE INDEX "ix_ChargeDiagnosticElement_id" ON "ChargeDiagnosticElement" (id);

CREATE TABLE "CameraPixelResultsIndices" (
	id INTEGER NOT NULL,
	x INTEGER,
	y INTEGER,
	x_sigma INTEGER,
	y_sigma INTEGER,
	covariance INTEGER,
	PRIMARY KEY (id)
);
CREATE INDEX "ix_CameraPixelResultsIndices_id" ON "CameraPixelResultsIndices" (id);

CREATE TABLE "CameraPixelResultsNames" (
	id INTEGER NOT NULL,
	x TEXT,
	y TEXT,
	x_sigma TEXT,
	y_sigma TEXT,
	covariance TEXT,
	PRIMARY KEY (id)
);
CREATE INDEX "ix_CameraPixelResultsNames_id" ON "CameraPixelResultsNames" (id);

CREATE TABLE "CameraMask" (
	id INTEGER NOT NULL,
	use_maximum_values BOOLEAN,
	PRIMARY KEY (id)
);
CREATE INDEX "ix_CameraMask_id" ON "CameraMask" (id);

CREATE TABLE "CameraSensor" (
	id INTEGER NOT NULL,
	x_pixels INTEGER,
	y_pixels INTEGER,
	x_scale_factor INTEGER,
	y_scale_factor INTEGER,
	beam_pixel_average FLOAT,
	x_pixels_to_mm FLOAT,
	y_pixels_to_mm FLOAT,
	bit_depth INTEGER,
	PRIMARY KEY (id)
);
CREATE INDEX "ix_CameraSensor_id" ON "CameraSensor" (id);

CREATE TABLE "LaserElement" (
	id INTEGER NOT NULL,
	initial_position FLOAT,
	waist FLOAT,
	wavelength FLOAT,
	pulse_energy FLOAT,
	pulse_duration_fwhm FLOAT,
	focal_position FLOAT,
	cep_phase FLOAT,
	polarization VARCHAR(10),
	profile_type VARCHAR(18),
	laguerre_polynomial_order_p INTEGER,
	flatness INTEGER,
	PRIMARY KEY (id)
);
CREATE INDEX "ix_LaserElement_id" ON "LaserElement" (id);

CREATE TABLE "LaserEnergyMeterElement" (
	id INTEGER NOT NULL,
	PRIMARY KEY (id)
);
CREATE INDEX "ix_LaserEnergyMeterElement_id" ON "LaserEnergyMeterElement" (id);

CREATE TABLE "LaserHalfWavePlateElement" (
	id INTEGER NOT NULL,
	PRIMARY KEY (id)
);
CREATE INDEX "ix_LaserHalfWavePlateElement_id" ON "LaserHalfWavePlateElement" (id);

CREATE TABLE "PlasmaElement" (
	id INTEGER NOT NULL,
	density FLOAT,
	species TEXT,
	ramp_up FLOAT,
	plateau FLOAT,
	ramp_down FLOAT,
	ramp_decay_length FLOAT,
	density_profile BOOLEAN,
	parabolic_coefficient FLOAT,
	PRIMARY KEY (id)
);
CREATE INDEX "ix_PlasmaElement_id" ON "PlasmaElement" (id);

CREATE TABLE "ElementPositionError" (
	id INTEGER NOT NULL,
	position_id INTEGER,
	rotation_id INTEGER,
	PRIMARY KEY (id),
	FOREIGN KEY(position_id) REFERENCES "Position" (id),
	FOREIGN KEY(rotation_id) REFERENCES "Rotation" (id)
);
CREATE INDEX "ix_ElementPositionError_id" ON "ElementPositionError" (id);

CREATE TABLE "ElementSurvey" (
	id INTEGER NOT NULL,
	position_id INTEGER,
	rotation_id INTEGER,
	PRIMARY KEY (id),
	FOREIGN KEY(position_id) REFERENCES "Position" (id),
	FOREIGN KEY(rotation_id) REFERENCES "Rotation" (id)
);
CREATE INDEX "ix_ElementSurvey_id" ON "ElementSurvey" (id);

CREATE TABLE "StandardElement" (
	name TEXT NOT NULL,
	hardware_class VARCHAR(10) NOT NULL,
	hardware_type TEXT,
	hardware_model TEXT,
	machine_area TEXT,
	virtual_name TEXT,
	subelement TEXT,
	simulation_id INTEGER,
	electrical_id INTEGER,
	manufacturer_id INTEGER,
	controls_id INTEGER,
	reference_id INTEGER,
	PRIMARY KEY (name),
	FOREIGN KEY(simulation_id) REFERENCES "SimulationElement" (id),
	FOREIGN KEY(electrical_id) REFERENCES "ElectricalElement" (id),
	FOREIGN KEY(manufacturer_id) REFERENCES "ManufacturerElement" (id),
	FOREIGN KEY(controls_id) REFERENCES "ControlsInformation" (id),
	FOREIGN KEY(reference_id) REFERENCES "ReferenceElement" (id)
);
CREATE INDEX "ix_StandardElement_name" ON "StandardElement" (name);

CREATE TABLE "Element" (
	name TEXT NOT NULL,
	hardware_class VARCHAR(10) NOT NULL,
	hardware_type TEXT,
	hardware_model TEXT,
	machine_area TEXT,
	virtual_name TEXT,
	subelement TEXT,
	simulation_id INTEGER,
	electrical_id INTEGER,
	manufacturer_id INTEGER,
	controls_id INTEGER,
	reference_id INTEGER,
	PRIMARY KEY (name),
	FOREIGN KEY(simulation_id) REFERENCES "SimulationElement" (id),
	FOREIGN KEY(electrical_id) REFERENCES "ElectricalElement" (id),
	FOREIGN KEY(manufacturer_id) REFERENCES "ManufacturerElement" (id),
	FOREIGN KEY(controls_id) REFERENCES "ControlsInformation" (id),
	FOREIGN KEY(reference_id) REFERENCES "ReferenceElement" (id)
);
CREATE INDEX "ix_Element_name" ON "Element" (name);

CREATE TABLE "RFModulator" (
	name TEXT NOT NULL,
	hardware_class VARCHAR(10) NOT NULL,
	hardware_type TEXT,
	hardware_model TEXT,
	machine_area TEXT,
	virtual_name TEXT,
	subelement TEXT,
	modulator_id INTEGER,
	simulation_id INTEGER,
	electrical_id INTEGER,
	manufacturer_id INTEGER,
	controls_id INTEGER,
	reference_id INTEGER,
	PRIMARY KEY (name),
	FOREIGN KEY(modulator_id) REFERENCES "RFModulatorElement" (id),
	FOREIGN KEY(simulation_id) REFERENCES "SimulationElement" (id),
	FOREIGN KEY(electrical_id) REFERENCES "ElectricalElement" (id),
	FOREIGN KEY(manufacturer_id) REFERENCES "ManufacturerElement" (id),
	FOREIGN KEY(controls_id) REFERENCES "ControlsInformation" (id),
	FOREIGN KEY(reference_id) REFERENCES "ReferenceElement" (id)
);
CREATE INDEX "ix_RFModulator_name" ON "RFModulator" (name);

CREATE TABLE "RFProtection" (
	name TEXT NOT NULL,
	hardware_class VARCHAR(10) NOT NULL,
	hardware_type TEXT,
	hardware_model TEXT,
	machine_area TEXT,
	virtual_name TEXT,
	subelement TEXT,
	protection_id INTEGER,
	simulation_id INTEGER,
	electrical_id INTEGER,
	manufacturer_id INTEGER,
	controls_id INTEGER,
	reference_id INTEGER,
	PRIMARY KEY (name),
	FOREIGN KEY(protection_id) REFERENCES "RFProtectionElement" (id),
	FOREIGN KEY(simulation_id) REFERENCES "SimulationElement" (id),
	FOREIGN KEY(electrical_id) REFERENCES "ElectricalElement" (id),
	FOREIGN KEY(manufacturer_id) REFERENCES "ManufacturerElement" (id),
	FOREIGN KEY(controls_id) REFERENCES "ControlsInformation" (id),
	FOREIGN KEY(reference_id) REFERENCES "ReferenceElement" (id)
);
CREATE INDEX "ix_RFProtection_name" ON "RFProtection" (name);

CREATE TABLE "RFHeartbeat" (
	name TEXT NOT NULL,
	hardware_class VARCHAR(10) NOT NULL,
	hardware_type TEXT,
	hardware_model TEXT,
	machine_area TEXT,
	virtual_name TEXT,
	subelement TEXT,
	heartbeat_id INTEGER,
	simulation_id INTEGER,
	electrical_id INTEGER,
	manufacturer_id INTEGER,
	controls_id INTEGER,
	reference_id INTEGER,
	PRIMARY KEY (name),
	FOREIGN KEY(heartbeat_id) REFERENCES "RFHeartbeatElement" (id),
	FOREIGN KEY(simulation_id) REFERENCES "SimulationElement" (id),
	FOREIGN KEY(electrical_id) REFERENCES "ElectricalElement" (id),
	FOREIGN KEY(manufacturer_id) REFERENCES "ManufacturerElement" (id),
	FOREIGN KEY(controls_id) REFERENCES "ControlsInformation" (id),
	FOREIGN KEY(reference_id) REFERENCES "ReferenceElement" (id)
);
CREATE INDEX "ix_RFHeartbeat_name" ON "RFHeartbeat" (name);

CREATE TABLE "LaserEnergyMeter" (
	name TEXT NOT NULL,
	hardware_class VARCHAR(10) NOT NULL,
	hardware_type TEXT,
	hardware_model TEXT,
	machine_area TEXT,
	virtual_name TEXT,
	subelement TEXT,
	laser_id INTEGER,
	simulation_id INTEGER,
	electrical_id INTEGER,
	manufacturer_id INTEGER,
	controls_id INTEGER,
	reference_id INTEGER,
	PRIMARY KEY (name),
	FOREIGN KEY(laser_id) REFERENCES "LaserEnergyMeterElement" (id),
	FOREIGN KEY(simulation_id) REFERENCES "SimulationElement" (id),
	FOREIGN KEY(electrical_id) REFERENCES "ElectricalElement" (id),
	FOREIGN KEY(manufacturer_id) REFERENCES "ManufacturerElement" (id),
	FOREIGN KEY(controls_id) REFERENCES "ControlsInformation" (id),
	FOREIGN KEY(reference_id) REFERENCES "ReferenceElement" (id)
);
CREATE INDEX "ix_LaserEnergyMeter_name" ON "LaserEnergyMeter" (name);

CREATE TABLE "LaserHalfWavePlate" (
	name TEXT NOT NULL,
	hardware_class VARCHAR(10) NOT NULL,
	hardware_type TEXT,
	hardware_model TEXT,
	machine_area TEXT,
	virtual_name TEXT,
	subelement TEXT,
	laser_id INTEGER,
	simulation_id INTEGER,
	electrical_id INTEGER,
	manufacturer_id INTEGER,
	controls_id INTEGER,
	reference_id INTEGER,
	PRIMARY KEY (name),
	FOREIGN KEY(laser_id) REFERENCES "LaserHalfWavePlateElement" (id),
	FOREIGN KEY(simulation_id) REFERENCES "SimulationElement" (id),
	FOREIGN KEY(electrical_id) REFERENCES "ElectricalElement" (id),
	FOREIGN KEY(manufacturer_id) REFERENCES "ManufacturerElement" (id),
	FOREIGN KEY(controls_id) REFERENCES "ControlsInformation" (id),
	FOREIGN KEY(reference_id) REFERENCES "ReferenceElement" (id)
);
CREATE INDEX "ix_LaserHalfWavePlate_name" ON "LaserHalfWavePlate" (name);

CREATE TABLE "LaserMirrorElement" (
	id INTEGER NOT NULL,
	step_max FLOAT,
	vertical_channel INTEGER,
	horizontal_channel INTEGER,
	sense_id INTEGER,
	PRIMARY KEY (id),
	FOREIGN KEY(sense_id) REFERENCES "LaserMirrorSense" (id)
);
CREATE INDEX "ix_LaserMirrorElement_id" ON "LaserMirrorElement" (id);

CREATE TABLE "LaserAttenuator" (
	maximum FLOAT,
	minimum FLOAT,
	name TEXT NOT NULL,
	hardware_class VARCHAR(10) NOT NULL,
	hardware_type TEXT,
	hardware_model TEXT,
	machine_area TEXT,
	virtual_name TEXT,
	subelement TEXT,
	simulation_id INTEGER,
	electrical_id INTEGER,
	manufacturer_id INTEGER,
	controls_id INTEGER,
	reference_id INTEGER,
	PRIMARY KEY (name),
	FOREIGN KEY(simulation_id) REFERENCES "SimulationElement" (id),
	FOREIGN KEY(electrical_id) REFERENCES "ElectricalElement" (id),
	FOREIGN KEY(manufacturer_id) REFERENCES "ManufacturerElement" (id),
	FOREIGN KEY(controls_id) REFERENCES "ControlsInformation" (id),
	FOREIGN KEY(reference_id) REFERENCES "ReferenceElement" (id)
);
CREATE INDEX "ix_LaserAttenuator_name" ON "LaserAttenuator" (name);

CREATE TABLE "Lighting" (
	name TEXT NOT NULL,
	hardware_class VARCHAR(10) NOT NULL,
	hardware_type TEXT,
	hardware_model TEXT,
	machine_area TEXT,
	virtual_name TEXT,
	subelement TEXT,
	lights_id INTEGER,
	simulation_id INTEGER,
	electrical_id INTEGER,
	manufacturer_id INTEGER,
	controls_id INTEGER,
	reference_id INTEGER,
	PRIMARY KEY (name),
	FOREIGN KEY(lights_id) REFERENCES "LightingElement" (id),
	FOREIGN KEY(simulation_id) REFERENCES "SimulationElement" (id),
	FOREIGN KEY(electrical_id) REFERENCES "ElectricalElement" (id),
	FOREIGN KEY(manufacturer_id) REFERENCES "ManufacturerElement" (id),
	FOREIGN KEY(controls_id) REFERENCES "ControlsInformation" (id),
	FOREIGN KEY(reference_id) REFERENCES "ReferenceElement" (id)
);
CREATE INDEX "ix_Lighting_name" ON "Lighting" (name);

CREATE TABLE "Multipoles" (
	id INTEGER NOT NULL,
	"K0L_id" INTEGER,
	"K1L_id" INTEGER,
	"K2L_id" INTEGER,
	"K3L_id" INTEGER,
	"K4L_id" INTEGER,
	PRIMARY KEY (id),
	FOREIGN KEY("K0L_id") REFERENCES "Multipole" (id),
	FOREIGN KEY("K1L_id") REFERENCES "Multipole" (id),
	FOREIGN KEY("K2L_id") REFERENCES "Multipole" (id),
	FOREIGN KEY("K3L_id") REFERENCES "Multipole" (id),
	FOREIGN KEY("K4L_id") REFERENCES "Multipole" (id)
);
CREATE INDEX "ix_Multipoles_id" ON "Multipoles" (id);

CREATE TABLE "PIDElement" (
	id INTEGER NOT NULL,
	"Kp" FLOAT,
	"Ki" FLOAT,
	"Kd" FLOAT,
	forward_channel INTEGER,
	probe_channel INTEGER,
	enable TEXT,
	disable TEXT,
	phase_range_id INTEGER,
	phase_weight_range_id INTEGER,
	PRIMARY KEY (id),
	FOREIGN KEY(phase_range_id) REFERENCES "PIDPhaseRange" (id),
	FOREIGN KEY(phase_weight_range_id) REFERENCES "PIDWeightRange" (id)
);
CREATE INDEX "ix_PIDElement_id" ON "PIDElement" (id);

CREATE TABLE "LLRFTimings" (
	id INTEGER NOT NULL,
	klystron_forward_id INTEGER,
	klystron_reverse_id INTEGER,
	cavity_forward_id INTEGER,
	cavity_reverse_id INTEGER,
	cavity_probe_id INTEGER,
	PRIMARY KEY (id),
	FOREIGN KEY(klystron_forward_id) REFERENCES "LLRFTiming" (id),
	FOREIGN KEY(klystron_reverse_id) REFERENCES "LLRFTiming" (id),
	FOREIGN KEY(cavity_forward_id) REFERENCES "LLRFTiming" (id),
	FOREIGN KEY(cavity_reverse_id) REFERENCES "LLRFTiming" (id),
	FOREIGN KEY(cavity_probe_id) REFERENCES "LLRFTiming" (id)
);
CREATE INDEX "ix_LLRFTimings_id" ON "LLRFTimings" (id);

CREATE TABLE "CameraDiagnosticElement" (
	id INTEGER NOT NULL,
	type TEXT,
	x_pixels INTEGER,
	y_pixels INTEGER,
	rotation FLOAT,
	flipped_horizontally BOOLEAN,
	flipped_vertically BOOLEAN,
	screen_name TEXT,
	has_led BOOLEAN,
	pixel_results_indices_id INTEGER,
	pixel_results_names_id INTEGER,
	mask_id INTEGER,
	sensor_id INTEGER,
	PRIMARY KEY (id),
	FOREIGN KEY(pixel_results_indices_id) REFERENCES "CameraPixelResultsIndices" (id),
	FOREIGN KEY(pixel_results_names_id) REFERENCES "CameraPixelResultsNames" (id),
	FOREIGN KEY(mask_id) REFERENCES "CameraMask" (id),
	FOREIGN KEY(sensor_id) REFERENCES "CameraSensor" (id)
);
CREATE INDEX "ix_CameraDiagnosticElement_id" ON "CameraDiagnosticElement" (id);

CREATE TABLE "ReferenceElement_drawings" (
	"ReferenceElement_id" INTEGER,
	drawings TEXT,
	PRIMARY KEY ("ReferenceElement_id", drawings),
	FOREIGN KEY("ReferenceElement_id") REFERENCES "ReferenceElement" (id)
);
CREATE INDEX "ix_ReferenceElement_drawings_ReferenceElement_id" ON "ReferenceElement_drawings" ("ReferenceElement_id");
CREATE INDEX "ix_ReferenceElement_drawings_drawings" ON "ReferenceElement_drawings" (drawings);

CREATE TABLE "ReferenceElement_design_files" (
	"ReferenceElement_id" INTEGER,
	design_files TEXT,
	PRIMARY KEY ("ReferenceElement_id", design_files),
	FOREIGN KEY("ReferenceElement_id") REFERENCES "ReferenceElement" (id)
);
CREATE INDEX "ix_ReferenceElement_design_files_design_files" ON "ReferenceElement_design_files" (design_files);
CREATE INDEX "ix_ReferenceElement_design_files_ReferenceElement_id" ON "ReferenceElement_design_files" ("ReferenceElement_id");

CREATE TABLE "ControlsInformation_variables" (
	"ControlsInformation_id" INTEGER,
	variables_id INTEGER,
	PRIMARY KEY ("ControlsInformation_id", variables_id),
	FOREIGN KEY("ControlsInformation_id") REFERENCES "ControlsInformation" (id),
	FOREIGN KEY(variables_id) REFERENCES "ControlVariable" (id)
);
CREATE INDEX "ix_ControlsInformation_variables_ControlsInformation_id" ON "ControlsInformation_variables" ("ControlsInformation_id");
CREATE INDEX "ix_ControlsInformation_variables_variables_id" ON "ControlsInformation_variables" (variables_id);

CREATE TABLE "ShutterElement_interlocks" (
	"ShutterElement_id" INTEGER,
	interlocks TEXT,
	PRIMARY KEY ("ShutterElement_id", interlocks),
	FOREIGN KEY("ShutterElement_id") REFERENCES "ShutterElement" (id)
);
CREATE INDEX "ix_ShutterElement_interlocks_ShutterElement_id" ON "ShutterElement_interlocks" ("ShutterElement_id");
CREATE INDEX "ix_ShutterElement_interlocks_interlocks" ON "ShutterElement_interlocks" (interlocks);

CREATE TABLE "AcceleratorElement_alias" (
	"AcceleratorElement_name" TEXT,
	alias TEXT,
	PRIMARY KEY ("AcceleratorElement_name", alias),
	FOREIGN KEY("AcceleratorElement_name") REFERENCES "AcceleratorElement" (name)
);
CREATE INDEX "ix_AcceleratorElement_alias_alias" ON "AcceleratorElement_alias" (alias);
CREATE INDEX "ix_AcceleratorElement_alias_AcceleratorElement_name" ON "AcceleratorElement_alias" ("AcceleratorElement_name");

CREATE TABLE "SectionLattice_elements" (
	"SectionLattice_name" TEXT,
	elements TEXT,
	PRIMARY KEY ("SectionLattice_name", elements),
	FOREIGN KEY("SectionLattice_name") REFERENCES "SectionLattice" (name)
);
CREATE INDEX "ix_SectionLattice_elements_SectionLattice_name" ON "SectionLattice_elements" ("SectionLattice_name");
CREATE INDEX "ix_SectionLattice_elements_elements" ON "SectionLattice_elements" (elements);

CREATE TABLE "MachineLayout_sections" (
	"MachineLayout_name" TEXT,
	sections TEXT,
	PRIMARY KEY ("MachineLayout_name", sections),
	FOREIGN KEY("MachineLayout_name") REFERENCES "MachineLayout" (name)
);
CREATE INDEX "ix_MachineLayout_sections_sections" ON "MachineLayout_sections" (sections);
CREATE INDEX "ix_MachineLayout_sections_MachineLayout_name" ON "MachineLayout_sections" ("MachineLayout_name");

CREATE TABLE "MachineModel_elements" (
	"MachineModel_id" INTEGER,
	elements_name TEXT,
	PRIMARY KEY ("MachineModel_id", elements_name),
	FOREIGN KEY("MachineModel_id") REFERENCES "MachineModel" (id),
	FOREIGN KEY(elements_name) REFERENCES "AcceleratorElement" (name)
);
CREATE INDEX "ix_MachineModel_elements_elements_name" ON "MachineModel_elements" (elements_name);
CREATE INDEX "ix_MachineModel_elements_MachineModel_id" ON "MachineModel_elements" ("MachineModel_id");

CREATE TABLE "MachineModel_sections" (
	"MachineModel_id" INTEGER,
	sections_name TEXT,
	PRIMARY KEY ("MachineModel_id", sections_name),
	FOREIGN KEY("MachineModel_id") REFERENCES "MachineModel" (id),
	FOREIGN KEY(sections_name) REFERENCES "SectionLattice" (name)
);
CREATE INDEX "ix_MachineModel_sections_sections_name" ON "MachineModel_sections" (sections_name);
CREATE INDEX "ix_MachineModel_sections_MachineModel_id" ON "MachineModel_sections" ("MachineModel_id");

CREATE TABLE "MachineModel_layouts" (
	"MachineModel_id" INTEGER,
	layouts_name TEXT,
	PRIMARY KEY ("MachineModel_id", layouts_name),
	FOREIGN KEY("MachineModel_id") REFERENCES "MachineModel" (id),
	FOREIGN KEY(layouts_name) REFERENCES "MachineLayout" (name)
);
CREATE INDEX "ix_MachineModel_layouts_MachineModel_id" ON "MachineModel_layouts" ("MachineModel_id");
CREATE INDEX "ix_MachineModel_layouts_layouts_name" ON "MachineModel_layouts" (layouts_name);

CREATE TABLE "FieldIntegral_coefficients" (
	"FieldIntegral_id" INTEGER,
	coefficients FLOAT,
	PRIMARY KEY ("FieldIntegral_id", coefficients),
	FOREIGN KEY("FieldIntegral_id") REFERENCES "FieldIntegral" (id)
);
CREATE INDEX "ix_FieldIntegral_coefficients_coefficients" ON "FieldIntegral_coefficients" (coefficients);
CREATE INDEX "ix_FieldIntegral_coefficients_FieldIntegral_id" ON "FieldIntegral_coefficients" ("FieldIntegral_id");

CREATE TABLE "DegaussableElement_values" (
	"DegaussableElement_id" INTEGER,
	"values" FLOAT,
	PRIMARY KEY ("DegaussableElement_id", "values"),
	FOREIGN KEY("DegaussableElement_id") REFERENCES "DegaussableElement" (id)
);
CREATE INDEX "ix_DegaussableElement_values_DegaussableElement_id" ON "DegaussableElement_values" ("DegaussableElement_id");
CREATE INDEX "ix_DegaussableElement_values_values" ON "DegaussableElement_values" ("values");

CREATE TABLE "RFCavityElement_power_calibration" (
	"RFCavityElement_id" INTEGER,
	power_calibration FLOAT,
	PRIMARY KEY ("RFCavityElement_id", power_calibration),
	FOREIGN KEY("RFCavityElement_id") REFERENCES "RFCavityElement" (id)
);
CREATE INDEX "ix_RFCavityElement_power_calibration_power_calibration" ON "RFCavityElement_power_calibration" (power_calibration);
CREATE INDEX "ix_RFCavityElement_power_calibration_RFCavityElement_id" ON "RFCavityElement_power_calibration" ("RFCavityElement_id");

CREATE TABLE "RFCavityElement_gradient_calibration" (
	"RFCavityElement_id" INTEGER,
	gradient_calibration FLOAT,
	PRIMARY KEY ("RFCavityElement_id", gradient_calibration),
	FOREIGN KEY("RFCavityElement_id") REFERENCES "RFCavityElement" (id)
);
CREATE INDEX "ix_RFCavityElement_gradient_calibration_RFCavityElement_id" ON "RFCavityElement_gradient_calibration" ("RFCavityElement_id");
CREATE INDEX "ix_RFCavityElement_gradient_calibration_gradient_calibration" ON "RFCavityElement_gradient_calibration" (gradient_calibration);

CREATE TABLE "ScreenDiagnosticElement_devices" (
	"ScreenDiagnosticElement_id" INTEGER,
	devices TEXT,
	PRIMARY KEY ("ScreenDiagnosticElement_id", devices),
	FOREIGN KEY("ScreenDiagnosticElement_id") REFERENCES "ScreenDiagnosticElement" (id)
);
CREATE INDEX "ix_ScreenDiagnosticElement_devices_devices" ON "ScreenDiagnosticElement_devices" (devices);
CREATE INDEX "ix_ScreenDiagnosticElement_devices_ScreenDiagnosticElement_id" ON "ScreenDiagnosticElement_devices" ("ScreenDiagnosticElement_id");

CREATE TABLE "CameraMask_middle" (
	"CameraMask_id" INTEGER,
	middle FLOAT,
	PRIMARY KEY ("CameraMask_id", middle),
	FOREIGN KEY("CameraMask_id") REFERENCES "CameraMask" (id)
);
CREATE INDEX "ix_CameraMask_middle_middle" ON "CameraMask_middle" (middle);
CREATE INDEX "ix_CameraMask_middle_CameraMask_id" ON "CameraMask_middle" ("CameraMask_id");

CREATE TABLE "CameraMask_radius" (
	"CameraMask_id" INTEGER,
	radius FLOAT,
	PRIMARY KEY ("CameraMask_id", radius),
	FOREIGN KEY("CameraMask_id") REFERENCES "CameraMask" (id)
);
CREATE INDEX "ix_CameraMask_radius_radius" ON "CameraMask_radius" (radius);
CREATE INDEX "ix_CameraMask_radius_CameraMask_id" ON "CameraMask_radius" ("CameraMask_id");

CREATE TABLE "CameraMask_maximum" (
	"CameraMask_id" INTEGER,
	maximum FLOAT,
	PRIMARY KEY ("CameraMask_id", maximum),
	FOREIGN KEY("CameraMask_id") REFERENCES "CameraMask" (id)
);
CREATE INDEX "ix_CameraMask_maximum_CameraMask_id" ON "CameraMask_maximum" ("CameraMask_id");
CREATE INDEX "ix_CameraMask_maximum_maximum" ON "CameraMask_maximum" (maximum);

CREATE TABLE "CameraSensor_middle" (
	"CameraSensor_id" INTEGER,
	middle FLOAT,
	PRIMARY KEY ("CameraSensor_id", middle),
	FOREIGN KEY("CameraSensor_id") REFERENCES "CameraSensor" (id)
);
CREATE INDEX "ix_CameraSensor_middle_middle" ON "CameraSensor_middle" (middle);
CREATE INDEX "ix_CameraSensor_middle_CameraSensor_id" ON "CameraSensor_middle" ("CameraSensor_id");

CREATE TABLE "CameraSensor_minimum" (
	"CameraSensor_id" INTEGER,
	minimum FLOAT,
	PRIMARY KEY ("CameraSensor_id", minimum),
	FOREIGN KEY("CameraSensor_id") REFERENCES "CameraSensor" (id)
);
CREATE INDEX "ix_CameraSensor_minimum_minimum" ON "CameraSensor_minimum" (minimum);
CREATE INDEX "ix_CameraSensor_minimum_CameraSensor_id" ON "CameraSensor_minimum" ("CameraSensor_id");

CREATE TABLE "CameraSensor_maximum" (
	"CameraSensor_id" INTEGER,
	maximum FLOAT,
	PRIMARY KEY ("CameraSensor_id", maximum),
	FOREIGN KEY("CameraSensor_id") REFERENCES "CameraSensor" (id)
);
CREATE INDEX "ix_CameraSensor_maximum_maximum" ON "CameraSensor_maximum" (maximum);
CREATE INDEX "ix_CameraSensor_maximum_CameraSensor_id" ON "CameraSensor_maximum" ("CameraSensor_id");

CREATE TABLE "CameraSensor_operating_middle" (
	"CameraSensor_id" INTEGER,
	operating_middle FLOAT,
	PRIMARY KEY ("CameraSensor_id", operating_middle),
	FOREIGN KEY("CameraSensor_id") REFERENCES "CameraSensor" (id)
);
CREATE INDEX "ix_CameraSensor_operating_middle_CameraSensor_id" ON "CameraSensor_operating_middle" ("CameraSensor_id");
CREATE INDEX "ix_CameraSensor_operating_middle_operating_middle" ON "CameraSensor_operating_middle" (operating_middle);

CREATE TABLE "CameraSensor_mechanical_middle" (
	"CameraSensor_id" INTEGER,
	mechanical_middle FLOAT,
	PRIMARY KEY ("CameraSensor_id", mechanical_middle),
	FOREIGN KEY("CameraSensor_id") REFERENCES "CameraSensor" (id)
);
CREATE INDEX "ix_CameraSensor_mechanical_middle_CameraSensor_id" ON "CameraSensor_mechanical_middle" ("CameraSensor_id");
CREATE INDEX "ix_CameraSensor_mechanical_middle_mechanical_middle" ON "CameraSensor_mechanical_middle" (mechanical_middle);

CREATE TABLE "PhysicalElement" (
	id INTEGER NOT NULL,
	length FLOAT,
	maximum_position FLOAT,
	minimum_position FLOAT,
	physical_angle FLOAT,
	middle_id INTEGER,
	datum_id INTEGER,
	rotation_id INTEGER,
	global_rotation_id INTEGER,
	error_id INTEGER,
	survey_id INTEGER,
	PRIMARY KEY (id),
	FOREIGN KEY(middle_id) REFERENCES "Position" (id),
	FOREIGN KEY(datum_id) REFERENCES "Position" (id),
	FOREIGN KEY(rotation_id) REFERENCES "Rotation" (id),
	FOREIGN KEY(global_rotation_id) REFERENCES "Rotation" (id),
	FOREIGN KEY(error_id) REFERENCES "ElementPositionError" (id),
	FOREIGN KEY(survey_id) REFERENCES "ElementSurvey" (id)
);
CREATE INDEX "ix_PhysicalElement_id" ON "PhysicalElement" (id);

CREATE TABLE "PID" (
	name TEXT NOT NULL,
	hardware_class VARCHAR(10) NOT NULL,
	hardware_type TEXT,
	hardware_model TEXT,
	machine_area TEXT,
	virtual_name TEXT,
	subelement TEXT,
	pid_id INTEGER,
	simulation_id INTEGER,
	electrical_id INTEGER,
	manufacturer_id INTEGER,
	controls_id INTEGER,
	reference_id INTEGER,
	PRIMARY KEY (name),
	FOREIGN KEY(pid_id) REFERENCES "PIDElement" (id),
	FOREIGN KEY(simulation_id) REFERENCES "SimulationElement" (id),
	FOREIGN KEY(electrical_id) REFERENCES "ElectricalElement" (id),
	FOREIGN KEY(manufacturer_id) REFERENCES "ManufacturerElement" (id),
	FOREIGN KEY(controls_id) REFERENCES "ControlsInformation" (id),
	FOREIGN KEY(reference_id) REFERENCES "ReferenceElement" (id)
);
CREATE INDEX "ix_PID_name" ON "PID" (name);

CREATE TABLE "LaserMirror" (
	name TEXT NOT NULL,
	hardware_class VARCHAR(10) NOT NULL,
	hardware_type TEXT,
	hardware_model TEXT,
	machine_area TEXT,
	virtual_name TEXT,
	subelement TEXT,
	laser_id INTEGER,
	simulation_id INTEGER,
	electrical_id INTEGER,
	manufacturer_id INTEGER,
	controls_id INTEGER,
	reference_id INTEGER,
	PRIMARY KEY (name),
	FOREIGN KEY(laser_id) REFERENCES "LaserMirrorElement" (id),
	FOREIGN KEY(simulation_id) REFERENCES "SimulationElement" (id),
	FOREIGN KEY(electrical_id) REFERENCES "ElectricalElement" (id),
	FOREIGN KEY(manufacturer_id) REFERENCES "ManufacturerElement" (id),
	FOREIGN KEY(controls_id) REFERENCES "ControlsInformation" (id),
	FOREIGN KEY(reference_id) REFERENCES "ReferenceElement" (id)
);
CREATE INDEX "ix_LaserMirror_name" ON "LaserMirror" (name);

CREATE TABLE "MagneticElement" (
	id INTEGER NOT NULL,
	"order" INTEGER,
	skew BOOLEAN,
	length FLOAT,
	settle_time FLOAT,
	entrance_edge_angle FLOAT,
	exit_edge_angle FLOAT,
	gap FLOAT,
	bore FLOAT,
	plane VARCHAR(10),
	width FLOAT,
	tilt FLOAT,
	edge_field_integral FLOAT,
	fringe_field_coefficient FLOAT,
	gradient FLOAT,
	multipoles_id INTEGER,
	systematic_multipoles_id INTEGER,
	random_multipoles_id INTEGER,
	field_integral_coefficients_id INTEGER,
	linear_saturation_coefficients_id INTEGER,
	PRIMARY KEY (id),
	FOREIGN KEY(multipoles_id) REFERENCES "Multipoles" (id),
	FOREIGN KEY(systematic_multipoles_id) REFERENCES "Multipoles" (id),
	FOREIGN KEY(random_multipoles_id) REFERENCES "Multipoles" (id),
	FOREIGN KEY(field_integral_coefficients_id) REFERENCES "FieldIntegral" (id),
	FOREIGN KEY(linear_saturation_coefficients_id) REFERENCES "LinearSaturationFit" (id)
);
CREATE INDEX "ix_MagneticElement_id" ON "MagneticElement" (id);

CREATE TABLE "LowLevelRFElement" (
	id INTEGER NOT NULL,
	max_amplitude FLOAT,
	crest_phase FLOAT,
	trace_id INTEGER,
	channel_names_id INTEGER,
	timings_id INTEGER,
	PRIMARY KEY (id),
	FOREIGN KEY(trace_id) REFERENCES "Trace" (id),
	FOREIGN KEY(channel_names_id) REFERENCES "ChannelNames" (id),
	FOREIGN KEY(timings_id) REFERENCES "LLRFTimings" (id)
);
CREATE INDEX "ix_LowLevelRFElement_id" ON "LowLevelRFElement" (id);

CREATE TABLE "StandardElement_alias" (
	"StandardElement_name" TEXT,
	alias TEXT,
	PRIMARY KEY ("StandardElement_name", alias),
	FOREIGN KEY("StandardElement_name") REFERENCES "StandardElement" (name)
);
CREATE INDEX "ix_StandardElement_alias_StandardElement_name" ON "StandardElement_alias" ("StandardElement_name");
CREATE INDEX "ix_StandardElement_alias_alias" ON "StandardElement_alias" (alias);

CREATE TABLE "Element_alias" (
	"Element_name" TEXT,
	alias TEXT,
	PRIMARY KEY ("Element_name", alias),
	FOREIGN KEY("Element_name") REFERENCES "Element" (name)
);
CREATE INDEX "ix_Element_alias_alias" ON "Element_alias" (alias);
CREATE INDEX "ix_Element_alias_Element_name" ON "Element_alias" ("Element_name");

CREATE TABLE "RFModulator_alias" (
	"RFModulator_name" TEXT,
	alias TEXT,
	PRIMARY KEY ("RFModulator_name", alias),
	FOREIGN KEY("RFModulator_name") REFERENCES "RFModulator" (name)
);
CREATE INDEX "ix_RFModulator_alias_RFModulator_name" ON "RFModulator_alias" ("RFModulator_name");
CREATE INDEX "ix_RFModulator_alias_alias" ON "RFModulator_alias" (alias);

CREATE TABLE "RFProtection_alias" (
	"RFProtection_name" TEXT,
	alias TEXT,
	PRIMARY KEY ("RFProtection_name", alias),
	FOREIGN KEY("RFProtection_name") REFERENCES "RFProtection" (name)
);
CREATE INDEX "ix_RFProtection_alias_alias" ON "RFProtection_alias" (alias);
CREATE INDEX "ix_RFProtection_alias_RFProtection_name" ON "RFProtection_alias" ("RFProtection_name");

CREATE TABLE "RFHeartbeat_alias" (
	"RFHeartbeat_name" TEXT,
	alias TEXT,
	PRIMARY KEY ("RFHeartbeat_name", alias),
	FOREIGN KEY("RFHeartbeat_name") REFERENCES "RFHeartbeat" (name)
);
CREATE INDEX "ix_RFHeartbeat_alias_alias" ON "RFHeartbeat_alias" (alias);
CREATE INDEX "ix_RFHeartbeat_alias_RFHeartbeat_name" ON "RFHeartbeat_alias" ("RFHeartbeat_name");

CREATE TABLE "LaserEnergyMeter_alias" (
	"LaserEnergyMeter_name" TEXT,
	alias TEXT,
	PRIMARY KEY ("LaserEnergyMeter_name", alias),
	FOREIGN KEY("LaserEnergyMeter_name") REFERENCES "LaserEnergyMeter" (name)
);
CREATE INDEX "ix_LaserEnergyMeter_alias_LaserEnergyMeter_name" ON "LaserEnergyMeter_alias" ("LaserEnergyMeter_name");
CREATE INDEX "ix_LaserEnergyMeter_alias_alias" ON "LaserEnergyMeter_alias" (alias);

CREATE TABLE "LaserHalfWavePlate_alias" (
	"LaserHalfWavePlate_name" TEXT,
	alias TEXT,
	PRIMARY KEY ("LaserHalfWavePlate_name", alias),
	FOREIGN KEY("LaserHalfWavePlate_name") REFERENCES "LaserHalfWavePlate" (name)
);
CREATE INDEX "ix_LaserHalfWavePlate_alias_LaserHalfWavePlate_name" ON "LaserHalfWavePlate_alias" ("LaserHalfWavePlate_name");
CREATE INDEX "ix_LaserHalfWavePlate_alias_alias" ON "LaserHalfWavePlate_alias" (alias);

CREATE TABLE "LaserAttenuator_alias" (
	"LaserAttenuator_name" TEXT,
	alias TEXT,
	PRIMARY KEY ("LaserAttenuator_name", alias),
	FOREIGN KEY("LaserAttenuator_name") REFERENCES "LaserAttenuator" (name)
);
CREATE INDEX "ix_LaserAttenuator_alias_alias" ON "LaserAttenuator_alias" (alias);
CREATE INDEX "ix_LaserAttenuator_alias_LaserAttenuator_name" ON "LaserAttenuator_alias" ("LaserAttenuator_name");

CREATE TABLE "Lighting_alias" (
	"Lighting_name" TEXT,
	alias TEXT,
	PRIMARY KEY ("Lighting_name", alias),
	FOREIGN KEY("Lighting_name") REFERENCES "Lighting" (name)
);
CREATE INDEX "ix_Lighting_alias_Lighting_name" ON "Lighting_alias" ("Lighting_name");
CREATE INDEX "ix_Lighting_alias_alias" ON "Lighting_alias" (alias);

CREATE TABLE "PhysicalAcceleratorElement" (
	name TEXT NOT NULL,
	hardware_class VARCHAR(10) NOT NULL,
	hardware_type TEXT,
	hardware_model TEXT,
	machine_area TEXT,
	virtual_name TEXT,
	subelement TEXT,
	physical_id INTEGER,
	simulation_id INTEGER,
	electrical_id INTEGER,
	manufacturer_id INTEGER,
	controls_id INTEGER,
	reference_id INTEGER,
	PRIMARY KEY (name),
	FOREIGN KEY(physical_id) REFERENCES "PhysicalElement" (id),
	FOREIGN KEY(simulation_id) REFERENCES "SimulationElement" (id),
	FOREIGN KEY(electrical_id) REFERENCES "ElectricalElement" (id),
	FOREIGN KEY(manufacturer_id) REFERENCES "ManufacturerElement" (id),
	FOREIGN KEY(controls_id) REFERENCES "ControlsInformation" (id),
	FOREIGN KEY(reference_id) REFERENCES "ReferenceElement" (id)
);
CREATE INDEX "ix_PhysicalAcceleratorElement_name" ON "PhysicalAcceleratorElement" (name);

CREATE TABLE "MagnetBaseElement" (
	name TEXT NOT NULL,
	hardware_class VARCHAR(10) NOT NULL,
	hardware_type TEXT,
	hardware_model TEXT,
	machine_area TEXT,
	virtual_name TEXT,
	subelement TEXT,
	magnetic_id INTEGER,
	degauss_id INTEGER,
	physical_id INTEGER,
	simulation_id INTEGER,
	electrical_id INTEGER,
	manufacturer_id INTEGER,
	controls_id INTEGER,
	reference_id INTEGER,
	PRIMARY KEY (name),
	FOREIGN KEY(magnetic_id) REFERENCES "MagneticElement" (id),
	FOREIGN KEY(degauss_id) REFERENCES "DegaussableElement" (id),
	FOREIGN KEY(physical_id) REFERENCES "PhysicalElement" (id),
	FOREIGN KEY(simulation_id) REFERENCES "MagnetSimulationElement" (id),
	FOREIGN KEY(electrical_id) REFERENCES "ElectricalElement" (id),
	FOREIGN KEY(manufacturer_id) REFERENCES "ManufacturerElement" (id),
	FOREIGN KEY(controls_id) REFERENCES "ControlsInformation" (id),
	FOREIGN KEY(reference_id) REFERENCES "ReferenceElement" (id)
);
CREATE INDEX "ix_MagnetBaseElement_name" ON "MagnetBaseElement" (name);

CREATE TABLE "Diagnostic" (
	name TEXT NOT NULL,
	hardware_class VARCHAR(10) NOT NULL,
	hardware_type TEXT,
	hardware_model TEXT,
	machine_area TEXT,
	virtual_name TEXT,
	subelement TEXT,
	diagnostic_id INTEGER,
	physical_id INTEGER,
	simulation_id INTEGER,
	electrical_id INTEGER,
	manufacturer_id INTEGER,
	controls_id INTEGER,
	reference_id INTEGER,
	PRIMARY KEY (name),
	FOREIGN KEY(diagnostic_id) REFERENCES "DiagnosticElement" (id),
	FOREIGN KEY(physical_id) REFERENCES "PhysicalElement" (id),
	FOREIGN KEY(simulation_id) REFERENCES "DiagnosticSimulationElement" (id),
	FOREIGN KEY(electrical_id) REFERENCES "ElectricalElement" (id),
	FOREIGN KEY(manufacturer_id) REFERENCES "ManufacturerElement" (id),
	FOREIGN KEY(controls_id) REFERENCES "ControlsInformation" (id),
	FOREIGN KEY(reference_id) REFERENCES "ReferenceElement" (id)
);
CREATE INDEX "ix_Diagnostic_name" ON "Diagnostic" (name);

CREATE TABLE "BeamPositionMonitor" (
	name TEXT NOT NULL,
	hardware_class VARCHAR(10) NOT NULL,
	hardware_type TEXT,
	hardware_model TEXT,
	machine_area TEXT,
	virtual_name TEXT,
	subelement TEXT,
	diagnostic_id INTEGER,
	physical_id INTEGER,
	simulation_id INTEGER,
	electrical_id INTEGER,
	manufacturer_id INTEGER,
	controls_id INTEGER,
	reference_id INTEGER,
	PRIMARY KEY (name),
	FOREIGN KEY(diagnostic_id) REFERENCES "BPMDiagnosticElement" (id),
	FOREIGN KEY(physical_id) REFERENCES "PhysicalElement" (id),
	FOREIGN KEY(simulation_id) REFERENCES "DiagnosticSimulationElement" (id),
	FOREIGN KEY(electrical_id) REFERENCES "ElectricalElement" (id),
	FOREIGN KEY(manufacturer_id) REFERENCES "ManufacturerElement" (id),
	FOREIGN KEY(controls_id) REFERENCES "ControlsInformation" (id),
	FOREIGN KEY(reference_id) REFERENCES "ReferenceElement" (id)
);
CREATE INDEX "ix_BeamPositionMonitor_name" ON "BeamPositionMonitor" (name);

CREATE TABLE "BeamArrivalMonitor" (
	name TEXT NOT NULL,
	hardware_class VARCHAR(10) NOT NULL,
	hardware_type TEXT,
	hardware_model TEXT,
	machine_area TEXT,
	virtual_name TEXT,
	subelement TEXT,
	diagnostic_id INTEGER,
	physical_id INTEGER,
	simulation_id INTEGER,
	electrical_id INTEGER,
	manufacturer_id INTEGER,
	controls_id INTEGER,
	reference_id INTEGER,
	PRIMARY KEY (name),
	FOREIGN KEY(diagnostic_id) REFERENCES "BAMDiagnosticElement" (id),
	FOREIGN KEY(physical_id) REFERENCES "PhysicalElement" (id),
	FOREIGN KEY(simulation_id) REFERENCES "DiagnosticSimulationElement" (id),
	FOREIGN KEY(electrical_id) REFERENCES "ElectricalElement" (id),
	FOREIGN KEY(manufacturer_id) REFERENCES "ManufacturerElement" (id),
	FOREIGN KEY(controls_id) REFERENCES "ControlsInformation" (id),
	FOREIGN KEY(reference_id) REFERENCES "ReferenceElement" (id)
);
CREATE INDEX "ix_BeamArrivalMonitor_name" ON "BeamArrivalMonitor" (name);

CREATE TABLE "BunchLengthMonitor" (
	name TEXT NOT NULL,
	hardware_class VARCHAR(10) NOT NULL,
	hardware_type TEXT,
	hardware_model TEXT,
	machine_area TEXT,
	virtual_name TEXT,
	subelement TEXT,
	diagnostic_id INTEGER,
	physical_id INTEGER,
	simulation_id INTEGER,
	electrical_id INTEGER,
	manufacturer_id INTEGER,
	controls_id INTEGER,
	reference_id INTEGER,
	PRIMARY KEY (name),
	FOREIGN KEY(diagnostic_id) REFERENCES "BLMDiagnosticElement" (id),
	FOREIGN KEY(physical_id) REFERENCES "PhysicalElement" (id),
	FOREIGN KEY(simulation_id) REFERENCES "DiagnosticSimulationElement" (id),
	FOREIGN KEY(electrical_id) REFERENCES "ElectricalElement" (id),
	FOREIGN KEY(manufacturer_id) REFERENCES "ManufacturerElement" (id),
	FOREIGN KEY(controls_id) REFERENCES "ControlsInformation" (id),
	FOREIGN KEY(reference_id) REFERENCES "ReferenceElement" (id)
);
CREATE INDEX "ix_BunchLengthMonitor_name" ON "BunchLengthMonitor" (name);

CREATE TABLE "Camera" (
	name TEXT NOT NULL,
	hardware_class VARCHAR(10) NOT NULL,
	hardware_type TEXT,
	hardware_model TEXT,
	machine_area TEXT,
	virtual_name TEXT,
	subelement TEXT,
	diagnostic_id INTEGER,
	physical_id INTEGER,
	simulation_id INTEGER,
	electrical_id INTEGER,
	manufacturer_id INTEGER,
	controls_id INTEGER,
	reference_id INTEGER,
	PRIMARY KEY (name),
	FOREIGN KEY(diagnostic_id) REFERENCES "CameraDiagnosticElement" (id),
	FOREIGN KEY(physical_id) REFERENCES "PhysicalElement" (id),
	FOREIGN KEY(simulation_id) REFERENCES "DiagnosticSimulationElement" (id),
	FOREIGN KEY(electrical_id) REFERENCES "ElectricalElement" (id),
	FOREIGN KEY(manufacturer_id) REFERENCES "ManufacturerElement" (id),
	FOREIGN KEY(controls_id) REFERENCES "ControlsInformation" (id),
	FOREIGN KEY(reference_id) REFERENCES "ReferenceElement" (id)
);
CREATE INDEX "ix_Camera_name" ON "Camera" (name);

CREATE TABLE "Screen" (
	name TEXT NOT NULL,
	hardware_class VARCHAR(10) NOT NULL,
	hardware_type TEXT,
	hardware_model TEXT,
	machine_area TEXT,
	virtual_name TEXT,
	subelement TEXT,
	diagnostic_id INTEGER,
	physical_id INTEGER,
	simulation_id INTEGER,
	electrical_id INTEGER,
	manufacturer_id INTEGER,
	controls_id INTEGER,
	reference_id INTEGER,
	PRIMARY KEY (name),
	FOREIGN KEY(diagnostic_id) REFERENCES "ScreenDiagnosticElement" (id),
	FOREIGN KEY(physical_id) REFERENCES "PhysicalElement" (id),
	FOREIGN KEY(simulation_id) REFERENCES "DiagnosticSimulationElement" (id),
	FOREIGN KEY(electrical_id) REFERENCES "ElectricalElement" (id),
	FOREIGN KEY(manufacturer_id) REFERENCES "ManufacturerElement" (id),
	FOREIGN KEY(controls_id) REFERENCES "ControlsInformation" (id),
	FOREIGN KEY(reference_id) REFERENCES "ReferenceElement" (id)
);
CREATE INDEX "ix_Screen_name" ON "Screen" (name);

CREATE TABLE "ChargeDiagnostic" (
	name TEXT NOT NULL,
	hardware_class VARCHAR(10) NOT NULL,
	hardware_type TEXT,
	hardware_model TEXT,
	machine_area TEXT,
	virtual_name TEXT,
	subelement TEXT,
	diagnostic_id INTEGER,
	physical_id INTEGER,
	simulation_id INTEGER,
	electrical_id INTEGER,
	manufacturer_id INTEGER,
	controls_id INTEGER,
	reference_id INTEGER,
	PRIMARY KEY (name),
	FOREIGN KEY(diagnostic_id) REFERENCES "ChargeDiagnosticElement" (id),
	FOREIGN KEY(physical_id) REFERENCES "PhysicalElement" (id),
	FOREIGN KEY(simulation_id) REFERENCES "DiagnosticSimulationElement" (id),
	FOREIGN KEY(electrical_id) REFERENCES "ElectricalElement" (id),
	FOREIGN KEY(manufacturer_id) REFERENCES "ManufacturerElement" (id),
	FOREIGN KEY(controls_id) REFERENCES "ControlsInformation" (id),
	FOREIGN KEY(reference_id) REFERENCES "ReferenceElement" (id)
);
CREATE INDEX "ix_ChargeDiagnostic_name" ON "ChargeDiagnostic" (name);

CREATE TABLE "WallCurrentMonitor" (
	name TEXT NOT NULL,
	hardware_class VARCHAR(10) NOT NULL,
	hardware_type TEXT,
	hardware_model TEXT,
	machine_area TEXT,
	virtual_name TEXT,
	subelement TEXT,
	diagnostic_id INTEGER,
	physical_id INTEGER,
	simulation_id INTEGER,
	electrical_id INTEGER,
	manufacturer_id INTEGER,
	controls_id INTEGER,
	reference_id INTEGER,
	PRIMARY KEY (name),
	FOREIGN KEY(diagnostic_id) REFERENCES "ChargeDiagnosticElement" (id),
	FOREIGN KEY(physical_id) REFERENCES "PhysicalElement" (id),
	FOREIGN KEY(simulation_id) REFERENCES "DiagnosticSimulationElement" (id),
	FOREIGN KEY(electrical_id) REFERENCES "ElectricalElement" (id),
	FOREIGN KEY(manufacturer_id) REFERENCES "ManufacturerElement" (id),
	FOREIGN KEY(controls_id) REFERENCES "ControlsInformation" (id),
	FOREIGN KEY(reference_id) REFERENCES "ReferenceElement" (id)
);
CREATE INDEX "ix_WallCurrentMonitor_name" ON "WallCurrentMonitor" (name);

CREATE TABLE "FaradayCupMonitor" (
	name TEXT NOT NULL,
	hardware_class VARCHAR(10) NOT NULL,
	hardware_type TEXT,
	hardware_model TEXT,
	machine_area TEXT,
	virtual_name TEXT,
	subelement TEXT,
	diagnostic_id INTEGER,
	physical_id INTEGER,
	simulation_id INTEGER,
	electrical_id INTEGER,
	manufacturer_id INTEGER,
	controls_id INTEGER,
	reference_id INTEGER,
	PRIMARY KEY (name),
	FOREIGN KEY(diagnostic_id) REFERENCES "ChargeDiagnosticElement" (id),
	FOREIGN KEY(physical_id) REFERENCES "PhysicalElement" (id),
	FOREIGN KEY(simulation_id) REFERENCES "DiagnosticSimulationElement" (id),
	FOREIGN KEY(electrical_id) REFERENCES "ElectricalElement" (id),
	FOREIGN KEY(manufacturer_id) REFERENCES "ManufacturerElement" (id),
	FOREIGN KEY(controls_id) REFERENCES "ControlsInformation" (id),
	FOREIGN KEY(reference_id) REFERENCES "ReferenceElement" (id)
);
CREATE INDEX "ix_FaradayCupMonitor_name" ON "FaradayCupMonitor" (name);

CREATE TABLE "IntegratedCurrentTransformer" (
	name TEXT NOT NULL,
	hardware_class VARCHAR(10) NOT NULL,
	hardware_type TEXT,
	hardware_model TEXT,
	machine_area TEXT,
	virtual_name TEXT,
	subelement TEXT,
	diagnostic_id INTEGER,
	physical_id INTEGER,
	simulation_id INTEGER,
	electrical_id INTEGER,
	manufacturer_id INTEGER,
	controls_id INTEGER,
	reference_id INTEGER,
	PRIMARY KEY (name),
	FOREIGN KEY(diagnostic_id) REFERENCES "ChargeDiagnosticElement" (id),
	FOREIGN KEY(physical_id) REFERENCES "PhysicalElement" (id),
	FOREIGN KEY(simulation_id) REFERENCES "DiagnosticSimulationElement" (id),
	FOREIGN KEY(electrical_id) REFERENCES "ElectricalElement" (id),
	FOREIGN KEY(manufacturer_id) REFERENCES "ManufacturerElement" (id),
	FOREIGN KEY(controls_id) REFERENCES "ControlsInformation" (id),
	FOREIGN KEY(reference_id) REFERENCES "ReferenceElement" (id)
);
CREATE INDEX "ix_IntegratedCurrentTransformer_name" ON "IntegratedCurrentTransformer" (name);

CREATE TABLE "RFCavity" (
	name TEXT NOT NULL,
	hardware_class VARCHAR(10) NOT NULL,
	hardware_type TEXT,
	hardware_model TEXT,
	machine_area TEXT,
	virtual_name TEXT,
	subelement TEXT,
	cavity_id INTEGER,
	physical_id INTEGER,
	simulation_id INTEGER,
	electrical_id INTEGER,
	manufacturer_id INTEGER,
	controls_id INTEGER,
	reference_id INTEGER,
	PRIMARY KEY (name),
	FOREIGN KEY(cavity_id) REFERENCES "RFCavityElement" (id),
	FOREIGN KEY(physical_id) REFERENCES "PhysicalElement" (id),
	FOREIGN KEY(simulation_id) REFERENCES "RFCavitySimulationElement" (id),
	FOREIGN KEY(electrical_id) REFERENCES "ElectricalElement" (id),
	FOREIGN KEY(manufacturer_id) REFERENCES "ManufacturerElement" (id),
	FOREIGN KEY(controls_id) REFERENCES "ControlsInformation" (id),
	FOREIGN KEY(reference_id) REFERENCES "ReferenceElement" (id)
);
CREATE INDEX "ix_RFCavity_name" ON "RFCavity" (name);

CREATE TABLE "RFDeflectingCavity" (
	name TEXT NOT NULL,
	hardware_class VARCHAR(10) NOT NULL,
	hardware_type TEXT,
	hardware_model TEXT,
	machine_area TEXT,
	virtual_name TEXT,
	subelement TEXT,
	cavity_id INTEGER,
	physical_id INTEGER,
	simulation_id INTEGER,
	electrical_id INTEGER,
	manufacturer_id INTEGER,
	controls_id INTEGER,
	reference_id INTEGER,
	PRIMARY KEY (name),
	FOREIGN KEY(cavity_id) REFERENCES "RFDeflectingCavityElement" (id),
	FOREIGN KEY(physical_id) REFERENCES "PhysicalElement" (id),
	FOREIGN KEY(simulation_id) REFERENCES "RFCavitySimulationElement" (id),
	FOREIGN KEY(electrical_id) REFERENCES "ElectricalElement" (id),
	FOREIGN KEY(manufacturer_id) REFERENCES "ManufacturerElement" (id),
	FOREIGN KEY(controls_id) REFERENCES "ControlsInformation" (id),
	FOREIGN KEY(reference_id) REFERENCES "ReferenceElement" (id)
);
CREATE INDEX "ix_RFDeflectingCavity_name" ON "RFDeflectingCavity" (name);

CREATE TABLE "Wakefield" (
	name TEXT NOT NULL,
	hardware_class VARCHAR(10) NOT NULL,
	hardware_type TEXT,
	hardware_model TEXT,
	machine_area TEXT,
	virtual_name TEXT,
	subelement TEXT,
	cavity_id INTEGER,
	physical_id INTEGER,
	simulation_id INTEGER,
	electrical_id INTEGER,
	manufacturer_id INTEGER,
	controls_id INTEGER,
	reference_id INTEGER,
	PRIMARY KEY (name),
	FOREIGN KEY(cavity_id) REFERENCES "WakefieldElement" (id),
	FOREIGN KEY(physical_id) REFERENCES "PhysicalElement" (id),
	FOREIGN KEY(simulation_id) REFERENCES "WakefieldSimulationElement" (id),
	FOREIGN KEY(electrical_id) REFERENCES "ElectricalElement" (id),
	FOREIGN KEY(manufacturer_id) REFERENCES "ManufacturerElement" (id),
	FOREIGN KEY(controls_id) REFERENCES "ControlsInformation" (id),
	FOREIGN KEY(reference_id) REFERENCES "ReferenceElement" (id)
);
CREATE INDEX "ix_Wakefield_name" ON "Wakefield" (name);

CREATE TABLE "LowLevelRF" (
	name TEXT NOT NULL,
	hardware_class VARCHAR(10) NOT NULL,
	hardware_type TEXT,
	hardware_model TEXT,
	machine_area TEXT,
	virtual_name TEXT,
	subelement TEXT,
	llrf_id INTEGER,
	simulation_id INTEGER,
	electrical_id INTEGER,
	manufacturer_id INTEGER,
	controls_id INTEGER,
	reference_id INTEGER,
	PRIMARY KEY (name),
	FOREIGN KEY(llrf_id) REFERENCES "LowLevelRFElement" (id),
	FOREIGN KEY(simulation_id) REFERENCES "SimulationElement" (id),
	FOREIGN KEY(electrical_id) REFERENCES "ElectricalElement" (id),
	FOREIGN KEY(manufacturer_id) REFERENCES "ManufacturerElement" (id),
	FOREIGN KEY(controls_id) REFERENCES "ControlsInformation" (id),
	FOREIGN KEY(reference_id) REFERENCES "ReferenceElement" (id)
);
CREATE INDEX "ix_LowLevelRF_name" ON "LowLevelRF" (name);

CREATE TABLE "TwissMatch" (
	name TEXT NOT NULL,
	hardware_class VARCHAR(10) NOT NULL,
	hardware_type TEXT,
	hardware_model TEXT,
	machine_area TEXT,
	virtual_name TEXT,
	subelement TEXT,
	physical_id INTEGER,
	simulation_id INTEGER,
	electrical_id INTEGER,
	manufacturer_id INTEGER,
	controls_id INTEGER,
	reference_id INTEGER,
	PRIMARY KEY (name),
	FOREIGN KEY(physical_id) REFERENCES "PhysicalElement" (id),
	FOREIGN KEY(simulation_id) REFERENCES "TwissMatchSimulationElement" (id),
	FOREIGN KEY(electrical_id) REFERENCES "ElectricalElement" (id),
	FOREIGN KEY(manufacturer_id) REFERENCES "ManufacturerElement" (id),
	FOREIGN KEY(controls_id) REFERENCES "ControlsInformation" (id),
	FOREIGN KEY(reference_id) REFERENCES "ReferenceElement" (id)
);
CREATE INDEX "ix_TwissMatch_name" ON "TwissMatch" (name);

CREATE TABLE "Stage" (
	name TEXT NOT NULL,
	hardware_class VARCHAR(10) NOT NULL,
	hardware_type TEXT,
	hardware_model TEXT,
	machine_area TEXT,
	virtual_name TEXT,
	subelement TEXT,
	physical_id INTEGER,
	simulation_id INTEGER,
	electrical_id INTEGER,
	manufacturer_id INTEGER,
	controls_id INTEGER,
	reference_id INTEGER,
	PRIMARY KEY (name),
	FOREIGN KEY(physical_id) REFERENCES "PhysicalElement" (id),
	FOREIGN KEY(simulation_id) REFERENCES "SimulationElement" (id),
	FOREIGN KEY(electrical_id) REFERENCES "ElectricalElement" (id),
	FOREIGN KEY(manufacturer_id) REFERENCES "ManufacturerElement" (id),
	FOREIGN KEY(controls_id) REFERENCES "ControlsInformation" (id),
	FOREIGN KEY(reference_id) REFERENCES "ReferenceElement" (id)
);
CREATE INDEX "ix_Stage_name" ON "Stage" (name);

CREATE TABLE "VacuumGauge" (
	name TEXT NOT NULL,
	hardware_class VARCHAR(10) NOT NULL,
	hardware_type TEXT,
	hardware_model TEXT,
	machine_area TEXT,
	virtual_name TEXT,
	subelement TEXT,
	physical_id INTEGER,
	simulation_id INTEGER,
	electrical_id INTEGER,
	manufacturer_id INTEGER,
	controls_id INTEGER,
	reference_id INTEGER,
	PRIMARY KEY (name),
	FOREIGN KEY(physical_id) REFERENCES "PhysicalElement" (id),
	FOREIGN KEY(simulation_id) REFERENCES "SimulationElement" (id),
	FOREIGN KEY(electrical_id) REFERENCES "ElectricalElement" (id),
	FOREIGN KEY(manufacturer_id) REFERENCES "ManufacturerElement" (id),
	FOREIGN KEY(controls_id) REFERENCES "ControlsInformation" (id),
	FOREIGN KEY(reference_id) REFERENCES "ReferenceElement" (id)
);
CREATE INDEX "ix_VacuumGauge_name" ON "VacuumGauge" (name);

CREATE TABLE "Laser" (
	name TEXT NOT NULL,
	hardware_class VARCHAR(10) NOT NULL,
	hardware_type TEXT,
	hardware_model TEXT,
	machine_area TEXT,
	virtual_name TEXT,
	subelement TEXT,
	laser_id INTEGER,
	physical_id INTEGER,
	simulation_id INTEGER,
	electrical_id INTEGER,
	manufacturer_id INTEGER,
	controls_id INTEGER,
	reference_id INTEGER,
	PRIMARY KEY (name),
	FOREIGN KEY(laser_id) REFERENCES "LaserElement" (id),
	FOREIGN KEY(physical_id) REFERENCES "PhysicalElement" (id),
	FOREIGN KEY(simulation_id) REFERENCES "SimulationElement" (id),
	FOREIGN KEY(electrical_id) REFERENCES "ElectricalElement" (id),
	FOREIGN KEY(manufacturer_id) REFERENCES "ManufacturerElement" (id),
	FOREIGN KEY(controls_id) REFERENCES "ControlsInformation" (id),
	FOREIGN KEY(reference_id) REFERENCES "ReferenceElement" (id)
);
CREATE INDEX "ix_Laser_name" ON "Laser" (name);

CREATE TABLE "Shutter" (
	name TEXT NOT NULL,
	hardware_class VARCHAR(10) NOT NULL,
	hardware_type TEXT,
	hardware_model TEXT,
	machine_area TEXT,
	virtual_name TEXT,
	subelement TEXT,
	shutter_id INTEGER,
	physical_id INTEGER,
	simulation_id INTEGER,
	electrical_id INTEGER,
	manufacturer_id INTEGER,
	controls_id INTEGER,
	reference_id INTEGER,
	PRIMARY KEY (name),
	FOREIGN KEY(shutter_id) REFERENCES "ShutterElement" (id),
	FOREIGN KEY(physical_id) REFERENCES "PhysicalElement" (id),
	FOREIGN KEY(simulation_id) REFERENCES "SimulationElement" (id),
	FOREIGN KEY(electrical_id) REFERENCES "ElectricalElement" (id),
	FOREIGN KEY(manufacturer_id) REFERENCES "ManufacturerElement" (id),
	FOREIGN KEY(controls_id) REFERENCES "ControlsInformation" (id),
	FOREIGN KEY(reference_id) REFERENCES "ReferenceElement" (id)
);
CREATE INDEX "ix_Shutter_name" ON "Shutter" (name);

CREATE TABLE "Valve" (
	name TEXT NOT NULL,
	hardware_class VARCHAR(10) NOT NULL,
	hardware_type TEXT,
	hardware_model TEXT,
	machine_area TEXT,
	virtual_name TEXT,
	subelement TEXT,
	valve_id INTEGER,
	physical_id INTEGER,
	simulation_id INTEGER,
	electrical_id INTEGER,
	manufacturer_id INTEGER,
	controls_id INTEGER,
	reference_id INTEGER,
	PRIMARY KEY (name),
	FOREIGN KEY(valve_id) REFERENCES "ValveElement" (id),
	FOREIGN KEY(physical_id) REFERENCES "PhysicalElement" (id),
	FOREIGN KEY(simulation_id) REFERENCES "SimulationElement" (id),
	FOREIGN KEY(electrical_id) REFERENCES "ElectricalElement" (id),
	FOREIGN KEY(manufacturer_id) REFERENCES "ManufacturerElement" (id),
	FOREIGN KEY(controls_id) REFERENCES "ControlsInformation" (id),
	FOREIGN KEY(reference_id) REFERENCES "ReferenceElement" (id)
);
CREATE INDEX "ix_Valve_name" ON "Valve" (name);

CREATE TABLE "Marker" (
	name TEXT NOT NULL,
	hardware_class VARCHAR(10) NOT NULL,
	hardware_type TEXT,
	hardware_model TEXT,
	machine_area TEXT,
	virtual_name TEXT,
	subelement TEXT,
	physical_id INTEGER,
	simulation_id INTEGER,
	electrical_id INTEGER,
	manufacturer_id INTEGER,
	controls_id INTEGER,
	reference_id INTEGER,
	PRIMARY KEY (name),
	FOREIGN KEY(physical_id) REFERENCES "PhysicalElement" (id),
	FOREIGN KEY(simulation_id) REFERENCES "SimulationElement" (id),
	FOREIGN KEY(electrical_id) REFERENCES "ElectricalElement" (id),
	FOREIGN KEY(manufacturer_id) REFERENCES "ManufacturerElement" (id),
	FOREIGN KEY(controls_id) REFERENCES "ControlsInformation" (id),
	FOREIGN KEY(reference_id) REFERENCES "ReferenceElement" (id)
);
CREATE INDEX "ix_Marker_name" ON "Marker" (name);

CREATE TABLE "Aperture" (
	name TEXT NOT NULL,
	hardware_class VARCHAR(10) NOT NULL,
	hardware_type TEXT,
	hardware_model TEXT,
	machine_area TEXT,
	virtual_name TEXT,
	subelement TEXT,
	aperture_id INTEGER,
	physical_id INTEGER,
	simulation_id INTEGER,
	electrical_id INTEGER,
	manufacturer_id INTEGER,
	controls_id INTEGER,
	reference_id INTEGER,
	PRIMARY KEY (name),
	FOREIGN KEY(aperture_id) REFERENCES "ApertureElement" (id),
	FOREIGN KEY(physical_id) REFERENCES "PhysicalElement" (id),
	FOREIGN KEY(simulation_id) REFERENCES "SimulationElement" (id),
	FOREIGN KEY(electrical_id) REFERENCES "ElectricalElement" (id),
	FOREIGN KEY(manufacturer_id) REFERENCES "ManufacturerElement" (id),
	FOREIGN KEY(controls_id) REFERENCES "ControlsInformation" (id),
	FOREIGN KEY(reference_id) REFERENCES "ReferenceElement" (id)
);
CREATE INDEX "ix_Aperture_name" ON "Aperture" (name);

CREATE TABLE "Collimator" (
	name TEXT NOT NULL,
	hardware_class VARCHAR(10) NOT NULL,
	hardware_type TEXT,
	hardware_model TEXT,
	machine_area TEXT,
	virtual_name TEXT,
	subelement TEXT,
	aperture_id INTEGER,
	physical_id INTEGER,
	simulation_id INTEGER,
	electrical_id INTEGER,
	manufacturer_id INTEGER,
	controls_id INTEGER,
	reference_id INTEGER,
	PRIMARY KEY (name),
	FOREIGN KEY(aperture_id) REFERENCES "ApertureElement" (id),
	FOREIGN KEY(physical_id) REFERENCES "PhysicalElement" (id),
	FOREIGN KEY(simulation_id) REFERENCES "SimulationElement" (id),
	FOREIGN KEY(electrical_id) REFERENCES "ElectricalElement" (id),
	FOREIGN KEY(manufacturer_id) REFERENCES "ManufacturerElement" (id),
	FOREIGN KEY(controls_id) REFERENCES "ControlsInformation" (id),
	FOREIGN KEY(reference_id) REFERENCES "ReferenceElement" (id)
);
CREATE INDEX "ix_Collimator_name" ON "Collimator" (name);

CREATE TABLE "Drift" (
	name TEXT NOT NULL,
	hardware_class VARCHAR(10) NOT NULL,
	hardware_type TEXT,
	hardware_model TEXT,
	machine_area TEXT,
	virtual_name TEXT,
	subelement TEXT,
	physical_id INTEGER,
	simulation_id INTEGER,
	electrical_id INTEGER,
	manufacturer_id INTEGER,
	controls_id INTEGER,
	reference_id INTEGER,
	PRIMARY KEY (name),
	FOREIGN KEY(physical_id) REFERENCES "PhysicalElement" (id),
	FOREIGN KEY(simulation_id) REFERENCES "DriftSimulationElement" (id),
	FOREIGN KEY(electrical_id) REFERENCES "ElectricalElement" (id),
	FOREIGN KEY(manufacturer_id) REFERENCES "ManufacturerElement" (id),
	FOREIGN KEY(controls_id) REFERENCES "ControlsInformation" (id),
	FOREIGN KEY(reference_id) REFERENCES "ReferenceElement" (id)
);
CREATE INDEX "ix_Drift_name" ON "Drift" (name);

CREATE TABLE "Plasma" (
	name TEXT NOT NULL,
	hardware_class VARCHAR(10) NOT NULL,
	hardware_type TEXT,
	hardware_model TEXT,
	machine_area TEXT,
	virtual_name TEXT,
	subelement TEXT,
	plasma_id INTEGER,
	laser_id INTEGER,
	physical_id INTEGER,
	simulation_id INTEGER,
	electrical_id INTEGER,
	manufacturer_id INTEGER,
	controls_id INTEGER,
	reference_id INTEGER,
	PRIMARY KEY (name),
	FOREIGN KEY(plasma_id) REFERENCES "PlasmaElement" (id),
	FOREIGN KEY(laser_id) REFERENCES "LaserElement" (id),
	FOREIGN KEY(physical_id) REFERENCES "PhysicalElement" (id),
	FOREIGN KEY(simulation_id) REFERENCES "PlasmaSimulationElement" (id),
	FOREIGN KEY(electrical_id) REFERENCES "ElectricalElement" (id),
	FOREIGN KEY(manufacturer_id) REFERENCES "ManufacturerElement" (id),
	FOREIGN KEY(controls_id) REFERENCES "ControlsInformation" (id),
	FOREIGN KEY(reference_id) REFERENCES "ReferenceElement" (id)
);
CREATE INDEX "ix_Plasma_name" ON "Plasma" (name);

CREATE TABLE "PID_alias" (
	"PID_name" TEXT,
	alias TEXT,
	PRIMARY KEY ("PID_name", alias),
	FOREIGN KEY("PID_name") REFERENCES "PID" (name)
);
CREATE INDEX "ix_PID_alias_PID_name" ON "PID_alias" ("PID_name");
CREATE INDEX "ix_PID_alias_alias" ON "PID_alias" (alias);

CREATE TABLE "LaserMirror_alias" (
	"LaserMirror_name" TEXT,
	alias TEXT,
	PRIMARY KEY ("LaserMirror_name", alias),
	FOREIGN KEY("LaserMirror_name") REFERENCES "LaserMirror" (name)
);
CREATE INDEX "ix_LaserMirror_alias_alias" ON "LaserMirror_alias" (alias);
CREATE INDEX "ix_LaserMirror_alias_LaserMirror_name" ON "LaserMirror_alias" ("LaserMirror_name");

CREATE TABLE "PhysicalAcceleratorElement_alias" (
	"PhysicalAcceleratorElement_name" TEXT,
	alias TEXT,
	PRIMARY KEY ("PhysicalAcceleratorElement_name", alias),
	FOREIGN KEY("PhysicalAcceleratorElement_name") REFERENCES "PhysicalAcceleratorElement" (name)
);
CREATE INDEX "ix_PhysicalAcceleratorElement_alias_PhysicalAcceleratorElement_name" ON "PhysicalAcceleratorElement_alias" ("PhysicalAcceleratorElement_name");
CREATE INDEX "ix_PhysicalAcceleratorElement_alias_alias" ON "PhysicalAcceleratorElement_alias" (alias);

CREATE TABLE "MagnetBaseElement_alias" (
	"MagnetBaseElement_name" TEXT,
	alias TEXT,
	PRIMARY KEY ("MagnetBaseElement_name", alias),
	FOREIGN KEY("MagnetBaseElement_name") REFERENCES "MagnetBaseElement" (name)
);
CREATE INDEX "ix_MagnetBaseElement_alias_MagnetBaseElement_name" ON "MagnetBaseElement_alias" ("MagnetBaseElement_name");
CREATE INDEX "ix_MagnetBaseElement_alias_alias" ON "MagnetBaseElement_alias" (alias);

CREATE TABLE "Diagnostic_alias" (
	"Diagnostic_name" TEXT,
	alias TEXT,
	PRIMARY KEY ("Diagnostic_name", alias),
	FOREIGN KEY("Diagnostic_name") REFERENCES "Diagnostic" (name)
);
CREATE INDEX "ix_Diagnostic_alias_alias" ON "Diagnostic_alias" (alias);
CREATE INDEX "ix_Diagnostic_alias_Diagnostic_name" ON "Diagnostic_alias" ("Diagnostic_name");

CREATE TABLE "BeamPositionMonitor_alias" (
	"BeamPositionMonitor_name" TEXT,
	alias TEXT,
	PRIMARY KEY ("BeamPositionMonitor_name", alias),
	FOREIGN KEY("BeamPositionMonitor_name") REFERENCES "BeamPositionMonitor" (name)
);
CREATE INDEX "ix_BeamPositionMonitor_alias_alias" ON "BeamPositionMonitor_alias" (alias);
CREATE INDEX "ix_BeamPositionMonitor_alias_BeamPositionMonitor_name" ON "BeamPositionMonitor_alias" ("BeamPositionMonitor_name");

CREATE TABLE "BeamArrivalMonitor_alias" (
	"BeamArrivalMonitor_name" TEXT,
	alias TEXT,
	PRIMARY KEY ("BeamArrivalMonitor_name", alias),
	FOREIGN KEY("BeamArrivalMonitor_name") REFERENCES "BeamArrivalMonitor" (name)
);
CREATE INDEX "ix_BeamArrivalMonitor_alias_BeamArrivalMonitor_name" ON "BeamArrivalMonitor_alias" ("BeamArrivalMonitor_name");
CREATE INDEX "ix_BeamArrivalMonitor_alias_alias" ON "BeamArrivalMonitor_alias" (alias);

CREATE TABLE "BunchLengthMonitor_alias" (
	"BunchLengthMonitor_name" TEXT,
	alias TEXT,
	PRIMARY KEY ("BunchLengthMonitor_name", alias),
	FOREIGN KEY("BunchLengthMonitor_name") REFERENCES "BunchLengthMonitor" (name)
);
CREATE INDEX "ix_BunchLengthMonitor_alias_BunchLengthMonitor_name" ON "BunchLengthMonitor_alias" ("BunchLengthMonitor_name");
CREATE INDEX "ix_BunchLengthMonitor_alias_alias" ON "BunchLengthMonitor_alias" (alias);

CREATE TABLE "Camera_alias" (
	"Camera_name" TEXT,
	alias TEXT,
	PRIMARY KEY ("Camera_name", alias),
	FOREIGN KEY("Camera_name") REFERENCES "Camera" (name)
);
CREATE INDEX "ix_Camera_alias_alias" ON "Camera_alias" (alias);
CREATE INDEX "ix_Camera_alias_Camera_name" ON "Camera_alias" ("Camera_name");

CREATE TABLE "Screen_alias" (
	"Screen_name" TEXT,
	alias TEXT,
	PRIMARY KEY ("Screen_name", alias),
	FOREIGN KEY("Screen_name") REFERENCES "Screen" (name)
);
CREATE INDEX "ix_Screen_alias_alias" ON "Screen_alias" (alias);
CREATE INDEX "ix_Screen_alias_Screen_name" ON "Screen_alias" ("Screen_name");

CREATE TABLE "ChargeDiagnostic_alias" (
	"ChargeDiagnostic_name" TEXT,
	alias TEXT,
	PRIMARY KEY ("ChargeDiagnostic_name", alias),
	FOREIGN KEY("ChargeDiagnostic_name") REFERENCES "ChargeDiagnostic" (name)
);
CREATE INDEX "ix_ChargeDiagnostic_alias_alias" ON "ChargeDiagnostic_alias" (alias);
CREATE INDEX "ix_ChargeDiagnostic_alias_ChargeDiagnostic_name" ON "ChargeDiagnostic_alias" ("ChargeDiagnostic_name");

CREATE TABLE "WallCurrentMonitor_alias" (
	"WallCurrentMonitor_name" TEXT,
	alias TEXT,
	PRIMARY KEY ("WallCurrentMonitor_name", alias),
	FOREIGN KEY("WallCurrentMonitor_name") REFERENCES "WallCurrentMonitor" (name)
);
CREATE INDEX "ix_WallCurrentMonitor_alias_alias" ON "WallCurrentMonitor_alias" (alias);
CREATE INDEX "ix_WallCurrentMonitor_alias_WallCurrentMonitor_name" ON "WallCurrentMonitor_alias" ("WallCurrentMonitor_name");

CREATE TABLE "FaradayCupMonitor_alias" (
	"FaradayCupMonitor_name" TEXT,
	alias TEXT,
	PRIMARY KEY ("FaradayCupMonitor_name", alias),
	FOREIGN KEY("FaradayCupMonitor_name") REFERENCES "FaradayCupMonitor" (name)
);
CREATE INDEX "ix_FaradayCupMonitor_alias_alias" ON "FaradayCupMonitor_alias" (alias);
CREATE INDEX "ix_FaradayCupMonitor_alias_FaradayCupMonitor_name" ON "FaradayCupMonitor_alias" ("FaradayCupMonitor_name");

CREATE TABLE "IntegratedCurrentTransformer_alias" (
	"IntegratedCurrentTransformer_name" TEXT,
	alias TEXT,
	PRIMARY KEY ("IntegratedCurrentTransformer_name", alias),
	FOREIGN KEY("IntegratedCurrentTransformer_name") REFERENCES "IntegratedCurrentTransformer" (name)
);
CREATE INDEX "ix_IntegratedCurrentTransformer_alias_alias" ON "IntegratedCurrentTransformer_alias" (alias);
CREATE INDEX "ix_IntegratedCurrentTransformer_alias_IntegratedCurrentTransformer_name" ON "IntegratedCurrentTransformer_alias" ("IntegratedCurrentTransformer_name");

CREATE TABLE "RFCavity_alias" (
	"RFCavity_name" TEXT,
	alias TEXT,
	PRIMARY KEY ("RFCavity_name", alias),
	FOREIGN KEY("RFCavity_name") REFERENCES "RFCavity" (name)
);
CREATE INDEX "ix_RFCavity_alias_RFCavity_name" ON "RFCavity_alias" ("RFCavity_name");
CREATE INDEX "ix_RFCavity_alias_alias" ON "RFCavity_alias" (alias);

CREATE TABLE "RFDeflectingCavity_alias" (
	"RFDeflectingCavity_name" TEXT,
	alias TEXT,
	PRIMARY KEY ("RFDeflectingCavity_name", alias),
	FOREIGN KEY("RFDeflectingCavity_name") REFERENCES "RFDeflectingCavity" (name)
);
CREATE INDEX "ix_RFDeflectingCavity_alias_RFDeflectingCavity_name" ON "RFDeflectingCavity_alias" ("RFDeflectingCavity_name");
CREATE INDEX "ix_RFDeflectingCavity_alias_alias" ON "RFDeflectingCavity_alias" (alias);

CREATE TABLE "Wakefield_alias" (
	"Wakefield_name" TEXT,
	alias TEXT,
	PRIMARY KEY ("Wakefield_name", alias),
	FOREIGN KEY("Wakefield_name") REFERENCES "Wakefield" (name)
);
CREATE INDEX "ix_Wakefield_alias_Wakefield_name" ON "Wakefield_alias" ("Wakefield_name");
CREATE INDEX "ix_Wakefield_alias_alias" ON "Wakefield_alias" (alias);

CREATE TABLE "LowLevelRF_alias" (
	"LowLevelRF_name" TEXT,
	alias TEXT,
	PRIMARY KEY ("LowLevelRF_name", alias),
	FOREIGN KEY("LowLevelRF_name") REFERENCES "LowLevelRF" (name)
);
CREATE INDEX "ix_LowLevelRF_alias_LowLevelRF_name" ON "LowLevelRF_alias" ("LowLevelRF_name");
CREATE INDEX "ix_LowLevelRF_alias_alias" ON "LowLevelRF_alias" (alias);

CREATE TABLE "TwissMatch_alias" (
	"TwissMatch_name" TEXT,
	alias TEXT,
	PRIMARY KEY ("TwissMatch_name", alias),
	FOREIGN KEY("TwissMatch_name") REFERENCES "TwissMatch" (name)
);
CREATE INDEX "ix_TwissMatch_alias_alias" ON "TwissMatch_alias" (alias);
CREATE INDEX "ix_TwissMatch_alias_TwissMatch_name" ON "TwissMatch_alias" ("TwissMatch_name");

CREATE TABLE "Stage_alias" (
	"Stage_name" TEXT,
	alias TEXT,
	PRIMARY KEY ("Stage_name", alias),
	FOREIGN KEY("Stage_name") REFERENCES "Stage" (name)
);
CREATE INDEX "ix_Stage_alias_Stage_name" ON "Stage_alias" ("Stage_name");
CREATE INDEX "ix_Stage_alias_alias" ON "Stage_alias" (alias);

CREATE TABLE "VacuumGauge_alias" (
	"VacuumGauge_name" TEXT,
	alias TEXT,
	PRIMARY KEY ("VacuumGauge_name", alias),
	FOREIGN KEY("VacuumGauge_name") REFERENCES "VacuumGauge" (name)
);
CREATE INDEX "ix_VacuumGauge_alias_VacuumGauge_name" ON "VacuumGauge_alias" ("VacuumGauge_name");
CREATE INDEX "ix_VacuumGauge_alias_alias" ON "VacuumGauge_alias" (alias);

CREATE TABLE "Laser_alias" (
	"Laser_name" TEXT,
	alias TEXT,
	PRIMARY KEY ("Laser_name", alias),
	FOREIGN KEY("Laser_name") REFERENCES "Laser" (name)
);
CREATE INDEX "ix_Laser_alias_Laser_name" ON "Laser_alias" ("Laser_name");
CREATE INDEX "ix_Laser_alias_alias" ON "Laser_alias" (alias);

CREATE TABLE "Shutter_alias" (
	"Shutter_name" TEXT,
	alias TEXT,
	PRIMARY KEY ("Shutter_name", alias),
	FOREIGN KEY("Shutter_name") REFERENCES "Shutter" (name)
);
CREATE INDEX "ix_Shutter_alias_Shutter_name" ON "Shutter_alias" ("Shutter_name");
CREATE INDEX "ix_Shutter_alias_alias" ON "Shutter_alias" (alias);

CREATE TABLE "Valve_alias" (
	"Valve_name" TEXT,
	alias TEXT,
	PRIMARY KEY ("Valve_name", alias),
	FOREIGN KEY("Valve_name") REFERENCES "Valve" (name)
);
CREATE INDEX "ix_Valve_alias_Valve_name" ON "Valve_alias" ("Valve_name");
CREATE INDEX "ix_Valve_alias_alias" ON "Valve_alias" (alias);

CREATE TABLE "Marker_alias" (
	"Marker_name" TEXT,
	alias TEXT,
	PRIMARY KEY ("Marker_name", alias),
	FOREIGN KEY("Marker_name") REFERENCES "Marker" (name)
);
CREATE INDEX "ix_Marker_alias_alias" ON "Marker_alias" (alias);
CREATE INDEX "ix_Marker_alias_Marker_name" ON "Marker_alias" ("Marker_name");

CREATE TABLE "Aperture_alias" (
	"Aperture_name" TEXT,
	alias TEXT,
	PRIMARY KEY ("Aperture_name", alias),
	FOREIGN KEY("Aperture_name") REFERENCES "Aperture" (name)
);
CREATE INDEX "ix_Aperture_alias_alias" ON "Aperture_alias" (alias);
CREATE INDEX "ix_Aperture_alias_Aperture_name" ON "Aperture_alias" ("Aperture_name");

CREATE TABLE "Collimator_alias" (
	"Collimator_name" TEXT,
	alias TEXT,
	PRIMARY KEY ("Collimator_name", alias),
	FOREIGN KEY("Collimator_name") REFERENCES "Collimator" (name)
);
CREATE INDEX "ix_Collimator_alias_alias" ON "Collimator_alias" (alias);
CREATE INDEX "ix_Collimator_alias_Collimator_name" ON "Collimator_alias" ("Collimator_name");

CREATE TABLE "Drift_alias" (
	"Drift_name" TEXT,
	alias TEXT,
	PRIMARY KEY ("Drift_name", alias),
	FOREIGN KEY("Drift_name") REFERENCES "Drift" (name)
);
CREATE INDEX "ix_Drift_alias_alias" ON "Drift_alias" (alias);
CREATE INDEX "ix_Drift_alias_Drift_name" ON "Drift_alias" ("Drift_name");

CREATE TABLE "Plasma_alias" (
	"Plasma_name" TEXT,
	alias TEXT,
	PRIMARY KEY ("Plasma_name", alias),
	FOREIGN KEY("Plasma_name") REFERENCES "Plasma" (name)
);
CREATE INDEX "ix_Plasma_alias_alias" ON "Plasma_alias" (alias);
CREATE INDEX "ix_Plasma_alias_Plasma_name" ON "Plasma_alias" ("Plasma_name");

