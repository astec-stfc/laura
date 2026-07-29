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
-- # Class: ReferencePlacement Description: Positions an element relative to a named reference element's local frame. The ``offset`` field is expressed in the reference element's local frame at the chosen ``point`` (start / middle / end).  Use ``world_offset`` instead to supply an offset already in global world coordinates.
--     * Slot: id
--     * Slot: element Description: Name of the reference element.
--     * Slot: point Description: Which point on the reference element to use as the origin frame: 'start', 'middle', or 'end'.
--     * Slot: s_offset Description: Scalar offset [m] along the local beam direction (s-axis) from the reference point.  Equivalent to ``offset: [0, 0, s_offset]`` but expressed as a single number.  Mutually exclusive with ``offset`` and ``world_offset``.
--     * Slot: offset_id Description: Offset expressed in the reference element's local frame at the chosen point.
--     * Slot: world_offset_id Description: Offset already expressed in global world coordinates.
-- # Class: PhysicalElement Description: Physical placement data: position, rotation, length, and associated survey / alignment-error information.
--     * Slot: id
--     * Slot: length Description: Effective length along the beam axis [m].
--     * Slot: physical_angle Description: Bending angle in the horizontal plane [rad]. Derived from ``magnetic.angle`` when available.
--     * Slot: s Description: Arc-length position [m] along the design trajectory (s=0 at the global origin along +Z).  Alternative to absolute world coordinates (``middle``/``position``/``centre``) and ``reference_placement``. Converted to {x,y,z} by LAURA during lattice assembly.
--     * Slot: s_point Description: Which point of the element the ``s`` value refers to: ``start``, ``middle``, or ``end``.  Defaults to ``middle``.
--     * Slot: middle_id Description: Longitudinal midpoint (centre) of the element. Also accepted as ``position`` or ``centre`` in YAML.
--     * Slot: datum_id Description: Datum reference position.
--     * Slot: rotation_id Description: Local rotation in the global frame.
--     * Slot: global_rotation_id Description: Accumulated global rotation including parent-frame contributions.
--     * Slot: error_id Description: Alignment errors.
--     * Slot: survey_id Description: Survey-measured position and rotation.
--     * Slot: reference_placement_id Description: Place this element relative to another element's frame instead of using absolute world coordinates.  Mutually exclusive with ``middle``/``position``/``centre`` and ``s``.
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
--     * Slot: ControlsInformation_id Description: Autocreated FK slot
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
-- # Class: ApertureElement Description: Transverse aperture geometry for drift-space checks and collimators.
--     * Slot: id
--     * Slot: number_of_elements Description: Number of aperture sub-elements (e.g., for multi-leaf collimators).
--     * Slot: horizontal_size Description: Full horizontal aperture [m].
--     * Slot: vertical_size Description: Full vertical aperture [m].
--     * Slot: shape Description: Cross-sectional aperture shape.
--     * Slot: radius Description: Radius for circular apertures [m].
--     * Slot: negative_extent Description: Upstream / inner extent [m].
--     * Slot: positive_extent Description: Downstream / outer extent [m].
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
-- # Class: PowerSupply Description: Generic power-supply unit providing control/setpoint-driven outputs (for example current/voltage) to other accelerator components.
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
--     * Slot: wakefield_enable Description: Whether the wakefield named by wakefield_definition is applied. Set false to track the element without its wakefield while keeping the definition itself.
--     * Slot: field_reference_position Description: Longitudinal origin of the field map [m].
--     * Slot: scale_field Description: Multiplicative scale factor applied to the field map.
-- # Class: MagnetSimulationElement Description: Simulation attributes specific to magnets: integrator settings, fringe-field model, and radiation flags.
--     * Slot: id
--     * Slot: n_kicks Description: Number of integration kicks.
--     * Slot: field_amplitude Description: Field amplitude scaling for magnet tracking.
--     * Slot: n_slices Description: Number of longitudinal slices for thick-lens tracking.
--     * Slot: smooth Description: Number of smoothing passes applied to the field map (ASTRA Q_smooth / S_smooth).
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
--     * Slot: wakefield_enable Description: Whether the wakefield named by wakefield_definition is applied. Set false to track the element without its wakefield while keeping the definition itself.
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
--     * Slot: field_amplitude Description: Cavity field amplitude.
--     * Slot: field_definition Description: Path to the 3-D field-map file.
--     * Slot: wakefield_definition Description: Path to the wakefield impedance file.
--     * Slot: wakefield_enable Description: Whether the wakefield named by wakefield_definition is applied. Set false to track the element without its wakefield while keeping the definition itself.
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
--     * Slot: wakefield_enable Description: Whether the wakefield named by wakefield_definition is applied. Set false to track the element without its wakefield while keeping the definition itself.
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
--     * Slot: wakefield_enable Description: Whether the wakefield named by wakefield_definition is applied. Set false to track the element without its wakefield while keeping the definition itself.
--     * Slot: field_reference_position Description: Longitudinal origin of the field map [m].
--     * Slot: scale_field Description: Multiplicative scale factor applied to the field map.
-- # Class: DiagnosticSimulationElement Description: Simulation attributes for beam-diagnostic elements.
--     * Slot: id
--     * Slot: output_filename Description: Output filename for diagnostic data.
--     * Slot: field_definition Description: Path to the 3-D field-map file.
--     * Slot: wakefield_definition Description: Path to the wakefield impedance file.
--     * Slot: wakefield_enable Description: Whether the wakefield named by wakefield_definition is applied. Set false to track the element without its wakefield while keeping the definition itself.
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
--     * Slot: wakefield_enable Description: Whether the wakefield named by wakefield_definition is applied. Set false to track the element without its wakefield while keeping the definition itself.
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
--     * Slot: wakefield_enable Description: Whether the wakefield named by wakefield_definition is applied. Set false to track the element without its wakefield while keeping the definition itself.
--     * Slot: field_reference_position Description: Longitudinal origin of the field map [m].
--     * Slot: scale_field Description: Multiplicative scale factor applied to the field map.
-- # Class: Magnet Description: Base class for all magnetic focusing and bending elements. (Named ``MagnetBaseElement`` in the schema to avoid collision with the ``magnetic`` composition-model class; maps to ``Magnet`` in Python.)
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
--     * Slot: angle Description: Integrated bending angle [rad]. Dipoles only. Part of the data model (lattice YAML may set it), but derived from multipoles.K0L rather than stored: the MagneticElement wrapper implements it as a read/write property so a symbolic bend angle survives round-tripping and reads follow the global resolution mode. Listed in _PYDANTIC_EXCLUDED_SLOTS in generate_pydantic.py so the generated base does not also declare it as a field, which would make pydantic treat the property object as the field default.
--     * Slot: multipoles_id Description: Integrated multipole field components.
--     * Slot: systematic_multipoles_id Description: Systematic (design) multipole errors at the reference radius.
--     * Slot: random_multipoles_id Description: Random multipole errors at the reference radius.
--     * Slot: field_integral_coefficients_id Description: Polynomial calibration of integrated field vs. current.
--     * Slot: linear_saturation_coefficients_id Description: Bi-linear saturation calibration.
-- # Class: DegaussableElement Description: Degaussing (demagnetisation cycle) parameters for magnets that require a field-reset procedure.
--     * Slot: id
--     * Slot: tolerance Description: Current tolerance band during the degauss cycle [A].
--     * Slot: steps Description: Number of degauss steps per half-cycle.
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
-- # Class: Dipole_Magnet
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
--     * Slot: angle Description: Integrated bending angle [rad]. Dipoles only. Part of the data model (lattice YAML may set it), but derived from multipoles.K0L rather than stored: the MagneticElement wrapper implements it as a read/write property so a symbolic bend angle survives round-tripping and reads follow the global resolution mode. Listed in _PYDANTIC_EXCLUDED_SLOTS in generate_pydantic.py so the generated base does not also declare it as a field, which would make pydantic treat the property object as the field default.
--     * Slot: multipoles_id Description: Integrated multipole field components.
--     * Slot: systematic_multipoles_id Description: Systematic (design) multipole errors at the reference radius.
--     * Slot: random_multipoles_id Description: Random multipole errors at the reference radius.
--     * Slot: field_integral_coefficients_id Description: Polynomial calibration of integrated field vs. current.
--     * Slot: linear_saturation_coefficients_id Description: Bi-linear saturation calibration.
-- # Class: Dipole
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
-- # Class: Quadrupole_Magnet
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
--     * Slot: angle Description: Integrated bending angle [rad]. Dipoles only. Part of the data model (lattice YAML may set it), but derived from multipoles.K0L rather than stored: the MagneticElement wrapper implements it as a read/write property so a symbolic bend angle survives round-tripping and reads follow the global resolution mode. Listed in _PYDANTIC_EXCLUDED_SLOTS in generate_pydantic.py so the generated base does not also declare it as a field, which would make pydantic treat the property object as the field default.
--     * Slot: multipoles_id Description: Integrated multipole field components.
--     * Slot: systematic_multipoles_id Description: Systematic (design) multipole errors at the reference radius.
--     * Slot: random_multipoles_id Description: Random multipole errors at the reference radius.
--     * Slot: field_integral_coefficients_id Description: Polynomial calibration of integrated field vs. current.
--     * Slot: linear_saturation_coefficients_id Description: Bi-linear saturation calibration.
-- # Class: Quadrupole
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
-- # Class: ReferenceElement_drawings
--     * Slot: ReferenceElement_id Description: Autocreated FK slot
--     * Slot: drawings Description: Engineering-drawing identifiers or URIs.
-- # Class: ReferenceElement_design_files
--     * Slot: ReferenceElement_id Description: Autocreated FK slot
--     * Slot: design_files Description: Design-file paths or URIs.
-- # Class: ShutterElement_interlocks
--     * Slot: ShutterElement_id Description: Autocreated FK slot
--     * Slot: interlocks Description: Names of the interlocks guarding this shutter.
-- # Class: AcceleratorElement_alias
--     * Slot: AcceleratorElement_name Description: Autocreated FK slot
--     * Slot: alias Description: Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.
-- # Class: AcceleratorElement_inputs
--     * Slot: AcceleratorElement_name Description: Autocreated FK slot
--     * Slot: inputs Description: (List) of input types
-- # Class: AcceleratorElement_outputs
--     * Slot: AcceleratorElement_name Description: Autocreated FK slot
--     * Slot: outputs Description: (List) of output types
-- # Class: AcceleratorElement_upstream
--     * Slot: AcceleratorElement_name Description: Autocreated FK slot
--     * Slot: upstream_name Description: (List) of upstream elements.
-- # Class: AcceleratorElement_downstream
--     * Slot: AcceleratorElement_name Description: Autocreated FK slot
--     * Slot: downstream_name Description: (List) of upstream elements.
-- # Class: StandardElement_alias
--     * Slot: StandardElement_name Description: Autocreated FK slot
--     * Slot: alias Description: Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.
-- # Class: StandardElement_inputs
--     * Slot: StandardElement_name Description: Autocreated FK slot
--     * Slot: inputs Description: (List) of input types
-- # Class: StandardElement_outputs
--     * Slot: StandardElement_name Description: Autocreated FK slot
--     * Slot: outputs Description: (List) of output types
-- # Class: StandardElement_upstream
--     * Slot: StandardElement_name Description: Autocreated FK slot
--     * Slot: upstream_name Description: (List) of upstream elements.
-- # Class: StandardElement_downstream
--     * Slot: StandardElement_name Description: Autocreated FK slot
--     * Slot: downstream_name Description: (List) of upstream elements.
-- # Class: Element_alias
--     * Slot: Element_name Description: Autocreated FK slot
--     * Slot: alias Description: Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.
-- # Class: Element_inputs
--     * Slot: Element_name Description: Autocreated FK slot
--     * Slot: inputs Description: (List) of input types
-- # Class: Element_outputs
--     * Slot: Element_name Description: Autocreated FK slot
--     * Slot: outputs Description: (List) of output types
-- # Class: Element_upstream
--     * Slot: Element_name Description: Autocreated FK slot
--     * Slot: upstream_name Description: (List) of upstream elements.
-- # Class: Element_downstream
--     * Slot: Element_name Description: Autocreated FK slot
--     * Slot: downstream_name Description: (List) of upstream elements.
-- # Class: PhysicalAcceleratorElement_alias
--     * Slot: PhysicalAcceleratorElement_name Description: Autocreated FK slot
--     * Slot: alias Description: Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.
-- # Class: PhysicalAcceleratorElement_inputs
--     * Slot: PhysicalAcceleratorElement_name Description: Autocreated FK slot
--     * Slot: inputs Description: (List) of input types
-- # Class: PhysicalAcceleratorElement_outputs
--     * Slot: PhysicalAcceleratorElement_name Description: Autocreated FK slot
--     * Slot: outputs Description: (List) of output types
-- # Class: PhysicalAcceleratorElement_upstream
--     * Slot: PhysicalAcceleratorElement_name Description: Autocreated FK slot
--     * Slot: upstream_name Description: (List) of upstream elements.
-- # Class: PhysicalAcceleratorElement_downstream
--     * Slot: PhysicalAcceleratorElement_name Description: Autocreated FK slot
--     * Slot: downstream_name Description: (List) of upstream elements.
-- # Class: TwissMatch_alias
--     * Slot: TwissMatch_name Description: Autocreated FK slot
--     * Slot: alias Description: Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.
-- # Class: TwissMatch_inputs
--     * Slot: TwissMatch_name Description: Autocreated FK slot
--     * Slot: inputs Description: (List) of input types
-- # Class: TwissMatch_outputs
--     * Slot: TwissMatch_name Description: Autocreated FK slot
--     * Slot: outputs Description: (List) of output types
-- # Class: TwissMatch_upstream
--     * Slot: TwissMatch_name Description: Autocreated FK slot
--     * Slot: upstream_name Description: (List) of upstream elements.
-- # Class: TwissMatch_downstream
--     * Slot: TwissMatch_name Description: Autocreated FK slot
--     * Slot: downstream_name Description: (List) of upstream elements.
-- # Class: Stage_alias
--     * Slot: Stage_name Description: Autocreated FK slot
--     * Slot: alias Description: Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.
-- # Class: Stage_inputs
--     * Slot: Stage_name Description: Autocreated FK slot
--     * Slot: inputs Description: (List) of input types
-- # Class: Stage_outputs
--     * Slot: Stage_name Description: Autocreated FK slot
--     * Slot: outputs Description: (List) of output types
-- # Class: Stage_upstream
--     * Slot: Stage_name Description: Autocreated FK slot
--     * Slot: upstream_name Description: (List) of upstream elements.
-- # Class: Stage_downstream
--     * Slot: Stage_name Description: Autocreated FK slot
--     * Slot: downstream_name Description: (List) of upstream elements.
-- # Class: VacuumGauge_alias
--     * Slot: VacuumGauge_name Description: Autocreated FK slot
--     * Slot: alias Description: Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.
-- # Class: VacuumGauge_inputs
--     * Slot: VacuumGauge_name Description: Autocreated FK slot
--     * Slot: inputs Description: (List) of input types
-- # Class: VacuumGauge_outputs
--     * Slot: VacuumGauge_name Description: Autocreated FK slot
--     * Slot: outputs Description: (List) of output types
-- # Class: VacuumGauge_upstream
--     * Slot: VacuumGauge_name Description: Autocreated FK slot
--     * Slot: upstream_name Description: (List) of upstream elements.
-- # Class: VacuumGauge_downstream
--     * Slot: VacuumGauge_name Description: Autocreated FK slot
--     * Slot: downstream_name Description: (List) of upstream elements.
-- # Class: Laser_alias
--     * Slot: Laser_name Description: Autocreated FK slot
--     * Slot: alias Description: Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.
-- # Class: Laser_inputs
--     * Slot: Laser_name Description: Autocreated FK slot
--     * Slot: inputs Description: (List) of input types
-- # Class: Laser_outputs
--     * Slot: Laser_name Description: Autocreated FK slot
--     * Slot: outputs Description: (List) of output types
-- # Class: Laser_upstream
--     * Slot: Laser_name Description: Autocreated FK slot
--     * Slot: upstream_name Description: (List) of upstream elements.
-- # Class: Laser_downstream
--     * Slot: Laser_name Description: Autocreated FK slot
--     * Slot: downstream_name Description: (List) of upstream elements.
-- # Class: Shutter_alias
--     * Slot: Shutter_name Description: Autocreated FK slot
--     * Slot: alias Description: Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.
-- # Class: Shutter_inputs
--     * Slot: Shutter_name Description: Autocreated FK slot
--     * Slot: inputs Description: (List) of input types
-- # Class: Shutter_outputs
--     * Slot: Shutter_name Description: Autocreated FK slot
--     * Slot: outputs Description: (List) of output types
-- # Class: Shutter_upstream
--     * Slot: Shutter_name Description: Autocreated FK slot
--     * Slot: upstream_name Description: (List) of upstream elements.
-- # Class: Shutter_downstream
--     * Slot: Shutter_name Description: Autocreated FK slot
--     * Slot: downstream_name Description: (List) of upstream elements.
-- # Class: Valve_alias
--     * Slot: Valve_name Description: Autocreated FK slot
--     * Slot: alias Description: Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.
-- # Class: Valve_inputs
--     * Slot: Valve_name Description: Autocreated FK slot
--     * Slot: inputs Description: (List) of input types
-- # Class: Valve_outputs
--     * Slot: Valve_name Description: Autocreated FK slot
--     * Slot: outputs Description: (List) of output types
-- # Class: Valve_upstream
--     * Slot: Valve_name Description: Autocreated FK slot
--     * Slot: upstream_name Description: (List) of upstream elements.
-- # Class: Valve_downstream
--     * Slot: Valve_name Description: Autocreated FK slot
--     * Slot: downstream_name Description: (List) of upstream elements.
-- # Class: Marker_alias
--     * Slot: Marker_name Description: Autocreated FK slot
--     * Slot: alias Description: Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.
-- # Class: Marker_inputs
--     * Slot: Marker_name Description: Autocreated FK slot
--     * Slot: inputs Description: (List) of input types
-- # Class: Marker_outputs
--     * Slot: Marker_name Description: Autocreated FK slot
--     * Slot: outputs Description: (List) of output types
-- # Class: Marker_upstream
--     * Slot: Marker_name Description: Autocreated FK slot
--     * Slot: upstream_name Description: (List) of upstream elements.
-- # Class: Marker_downstream
--     * Slot: Marker_name Description: Autocreated FK slot
--     * Slot: downstream_name Description: (List) of upstream elements.
-- # Class: Aperture_alias
--     * Slot: Aperture_name Description: Autocreated FK slot
--     * Slot: alias Description: Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.
-- # Class: Aperture_inputs
--     * Slot: Aperture_name Description: Autocreated FK slot
--     * Slot: inputs Description: (List) of input types
-- # Class: Aperture_outputs
--     * Slot: Aperture_name Description: Autocreated FK slot
--     * Slot: outputs Description: (List) of output types
-- # Class: Aperture_upstream
--     * Slot: Aperture_name Description: Autocreated FK slot
--     * Slot: upstream_name Description: (List) of upstream elements.
-- # Class: Aperture_downstream
--     * Slot: Aperture_name Description: Autocreated FK slot
--     * Slot: downstream_name Description: (List) of upstream elements.
-- # Class: Collimator_alias
--     * Slot: Collimator_name Description: Autocreated FK slot
--     * Slot: alias Description: Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.
-- # Class: Collimator_inputs
--     * Slot: Collimator_name Description: Autocreated FK slot
--     * Slot: inputs Description: (List) of input types
-- # Class: Collimator_outputs
--     * Slot: Collimator_name Description: Autocreated FK slot
--     * Slot: outputs Description: (List) of output types
-- # Class: Collimator_upstream
--     * Slot: Collimator_name Description: Autocreated FK slot
--     * Slot: upstream_name Description: (List) of upstream elements.
-- # Class: Collimator_downstream
--     * Slot: Collimator_name Description: Autocreated FK slot
--     * Slot: downstream_name Description: (List) of upstream elements.
-- # Class: Drift_alias
--     * Slot: Drift_name Description: Autocreated FK slot
--     * Slot: alias Description: Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.
-- # Class: Drift_inputs
--     * Slot: Drift_name Description: Autocreated FK slot
--     * Slot: inputs Description: (List) of input types
-- # Class: Drift_outputs
--     * Slot: Drift_name Description: Autocreated FK slot
--     * Slot: outputs Description: (List) of output types
-- # Class: Drift_upstream
--     * Slot: Drift_name Description: Autocreated FK slot
--     * Slot: upstream_name Description: (List) of upstream elements.
-- # Class: Drift_downstream
--     * Slot: Drift_name Description: Autocreated FK slot
--     * Slot: downstream_name Description: (List) of upstream elements.
-- # Class: Lighting_alias
--     * Slot: Lighting_name Description: Autocreated FK slot
--     * Slot: alias Description: Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.
-- # Class: Lighting_inputs
--     * Slot: Lighting_name Description: Autocreated FK slot
--     * Slot: inputs Description: (List) of input types
-- # Class: Lighting_outputs
--     * Slot: Lighting_name Description: Autocreated FK slot
--     * Slot: outputs Description: (List) of output types
-- # Class: Lighting_upstream
--     * Slot: Lighting_name Description: Autocreated FK slot
--     * Slot: upstream_name Description: (List) of upstream elements.
-- # Class: Lighting_downstream
--     * Slot: Lighting_name Description: Autocreated FK slot
--     * Slot: downstream_name Description: (List) of upstream elements.
-- # Class: PowerSupply_alias
--     * Slot: PowerSupply_name Description: Autocreated FK slot
--     * Slot: alias Description: Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.
-- # Class: PowerSupply_inputs
--     * Slot: PowerSupply_name Description: Autocreated FK slot
--     * Slot: inputs Description: (List) of input types
-- # Class: PowerSupply_outputs
--     * Slot: PowerSupply_name Description: Autocreated FK slot
--     * Slot: outputs Description: (List) of output types
-- # Class: PowerSupply_upstream
--     * Slot: PowerSupply_name Description: Autocreated FK slot
--     * Slot: upstream_name Description: (List) of upstream elements.
-- # Class: PowerSupply_downstream
--     * Slot: PowerSupply_name Description: Autocreated FK slot
--     * Slot: downstream_name Description: (List) of upstream elements.
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
-- # Class: Magnet_alias
--     * Slot: Magnet_name Description: Autocreated FK slot
--     * Slot: alias Description: Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.
-- # Class: Magnet_inputs
--     * Slot: Magnet_name Description: Autocreated FK slot
--     * Slot: inputs Description: (List) of input types
-- # Class: Magnet_outputs
--     * Slot: Magnet_name Description: Autocreated FK slot
--     * Slot: outputs Description: (List) of output types
-- # Class: Magnet_upstream
--     * Slot: Magnet_name Description: Autocreated FK slot
--     * Slot: upstream_name Description: (List) of upstream elements.
-- # Class: Magnet_downstream
--     * Slot: Magnet_name Description: Autocreated FK slot
--     * Slot: downstream_name Description: (List) of upstream elements.
-- # Class: FieldIntegral_coefficients
--     * Slot: FieldIntegral_id Description: Autocreated FK slot
--     * Slot: coefficients Description: Polynomial coefficients ordered from lowest to highest degree: ``FieldIntegral = sum c_n . I^n``.
-- # Class: DegaussableElement_values
--     * Slot: DegaussableElement_id Description: Autocreated FK slot
--     * Slot: values Description: Sequence of peak currents applied during the degauss cycle [A].
-- # Class: RFCavity_alias
--     * Slot: RFCavity_name Description: Autocreated FK slot
--     * Slot: alias Description: Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.
-- # Class: RFCavity_inputs
--     * Slot: RFCavity_name Description: Autocreated FK slot
--     * Slot: inputs Description: (List) of input types
-- # Class: RFCavity_outputs
--     * Slot: RFCavity_name Description: Autocreated FK slot
--     * Slot: outputs Description: (List) of output types
-- # Class: RFCavity_upstream
--     * Slot: RFCavity_name Description: Autocreated FK slot
--     * Slot: upstream_name Description: (List) of upstream elements.
-- # Class: RFCavity_downstream
--     * Slot: RFCavity_name Description: Autocreated FK slot
--     * Slot: downstream_name Description: (List) of upstream elements.
-- # Class: RFDeflectingCavity_alias
--     * Slot: RFDeflectingCavity_name Description: Autocreated FK slot
--     * Slot: alias Description: Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.
-- # Class: RFDeflectingCavity_inputs
--     * Slot: RFDeflectingCavity_name Description: Autocreated FK slot
--     * Slot: inputs Description: (List) of input types
-- # Class: RFDeflectingCavity_outputs
--     * Slot: RFDeflectingCavity_name Description: Autocreated FK slot
--     * Slot: outputs Description: (List) of output types
-- # Class: RFDeflectingCavity_upstream
--     * Slot: RFDeflectingCavity_name Description: Autocreated FK slot
--     * Slot: upstream_name Description: (List) of upstream elements.
-- # Class: RFDeflectingCavity_downstream
--     * Slot: RFDeflectingCavity_name Description: Autocreated FK slot
--     * Slot: downstream_name Description: (List) of upstream elements.
-- # Class: Wakefield_alias
--     * Slot: Wakefield_name Description: Autocreated FK slot
--     * Slot: alias Description: Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.
-- # Class: Wakefield_inputs
--     * Slot: Wakefield_name Description: Autocreated FK slot
--     * Slot: inputs Description: (List) of input types
-- # Class: Wakefield_outputs
--     * Slot: Wakefield_name Description: Autocreated FK slot
--     * Slot: outputs Description: (List) of output types
-- # Class: Wakefield_upstream
--     * Slot: Wakefield_name Description: Autocreated FK slot
--     * Slot: upstream_name Description: (List) of upstream elements.
-- # Class: Wakefield_downstream
--     * Slot: Wakefield_name Description: Autocreated FK slot
--     * Slot: downstream_name Description: (List) of upstream elements.
-- # Class: LowLevelRF_alias
--     * Slot: LowLevelRF_name Description: Autocreated FK slot
--     * Slot: alias Description: Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.
-- # Class: LowLevelRF_inputs
--     * Slot: LowLevelRF_name Description: Autocreated FK slot
--     * Slot: inputs Description: (List) of input types
-- # Class: LowLevelRF_outputs
--     * Slot: LowLevelRF_name Description: Autocreated FK slot
--     * Slot: outputs Description: (List) of output types
-- # Class: LowLevelRF_upstream
--     * Slot: LowLevelRF_name Description: Autocreated FK slot
--     * Slot: upstream_name Description: (List) of upstream elements.
-- # Class: LowLevelRF_downstream
--     * Slot: LowLevelRF_name Description: Autocreated FK slot
--     * Slot: downstream_name Description: (List) of upstream elements.
-- # Class: RFModulator_alias
--     * Slot: RFModulator_name Description: Autocreated FK slot
--     * Slot: alias Description: Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.
-- # Class: RFModulator_inputs
--     * Slot: RFModulator_name Description: Autocreated FK slot
--     * Slot: inputs Description: (List) of input types
-- # Class: RFModulator_outputs
--     * Slot: RFModulator_name Description: Autocreated FK slot
--     * Slot: outputs Description: (List) of output types
-- # Class: RFModulator_upstream
--     * Slot: RFModulator_name Description: Autocreated FK slot
--     * Slot: upstream_name Description: (List) of upstream elements.
-- # Class: RFModulator_downstream
--     * Slot: RFModulator_name Description: Autocreated FK slot
--     * Slot: downstream_name Description: (List) of upstream elements.
-- # Class: RFProtection_alias
--     * Slot: RFProtection_name Description: Autocreated FK slot
--     * Slot: alias Description: Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.
-- # Class: RFProtection_inputs
--     * Slot: RFProtection_name Description: Autocreated FK slot
--     * Slot: inputs Description: (List) of input types
-- # Class: RFProtection_outputs
--     * Slot: RFProtection_name Description: Autocreated FK slot
--     * Slot: outputs Description: (List) of output types
-- # Class: RFProtection_upstream
--     * Slot: RFProtection_name Description: Autocreated FK slot
--     * Slot: upstream_name Description: (List) of upstream elements.
-- # Class: RFProtection_downstream
--     * Slot: RFProtection_name Description: Autocreated FK slot
--     * Slot: downstream_name Description: (List) of upstream elements.
-- # Class: RFHeartbeat_alias
--     * Slot: RFHeartbeat_name Description: Autocreated FK slot
--     * Slot: alias Description: Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.
-- # Class: RFHeartbeat_inputs
--     * Slot: RFHeartbeat_name Description: Autocreated FK slot
--     * Slot: inputs Description: (List) of input types
-- # Class: RFHeartbeat_outputs
--     * Slot: RFHeartbeat_name Description: Autocreated FK slot
--     * Slot: outputs Description: (List) of output types
-- # Class: RFHeartbeat_upstream
--     * Slot: RFHeartbeat_name Description: Autocreated FK slot
--     * Slot: upstream_name Description: (List) of upstream elements.
-- # Class: RFHeartbeat_downstream
--     * Slot: RFHeartbeat_name Description: Autocreated FK slot
--     * Slot: downstream_name Description: (List) of upstream elements.
-- # Class: PID_alias
--     * Slot: PID_name Description: Autocreated FK slot
--     * Slot: alias Description: Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.
-- # Class: PID_inputs
--     * Slot: PID_name Description: Autocreated FK slot
--     * Slot: inputs Description: (List) of input types
-- # Class: PID_outputs
--     * Slot: PID_name Description: Autocreated FK slot
--     * Slot: outputs Description: (List) of output types
-- # Class: PID_upstream
--     * Slot: PID_name Description: Autocreated FK slot
--     * Slot: upstream_name Description: (List) of upstream elements.
-- # Class: PID_downstream
--     * Slot: PID_name Description: Autocreated FK slot
--     * Slot: downstream_name Description: (List) of upstream elements.
-- # Class: RFCavityElement_power_calibration
--     * Slot: RFCavityElement_id Description: Autocreated FK slot
--     * Slot: power_calibration Description: Calibration constant relating measured power to cavity gradient.
-- # Class: RFCavityElement_gradient_calibration
--     * Slot: RFCavityElement_id Description: Autocreated FK slot
--     * Slot: gradient_calibration Description: Calibration relating measured signal to gradient [MV/m per a.u.].
-- # Class: Diagnostic_alias
--     * Slot: Diagnostic_name Description: Autocreated FK slot
--     * Slot: alias Description: Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.
-- # Class: Diagnostic_inputs
--     * Slot: Diagnostic_name Description: Autocreated FK slot
--     * Slot: inputs Description: (List) of input types
-- # Class: Diagnostic_outputs
--     * Slot: Diagnostic_name Description: Autocreated FK slot
--     * Slot: outputs Description: (List) of output types
-- # Class: Diagnostic_upstream
--     * Slot: Diagnostic_name Description: Autocreated FK slot
--     * Slot: upstream_name Description: (List) of upstream elements.
-- # Class: Diagnostic_downstream
--     * Slot: Diagnostic_name Description: Autocreated FK slot
--     * Slot: downstream_name Description: (List) of upstream elements.
-- # Class: BeamPositionMonitor_alias
--     * Slot: BeamPositionMonitor_name Description: Autocreated FK slot
--     * Slot: alias Description: Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.
-- # Class: BeamPositionMonitor_inputs
--     * Slot: BeamPositionMonitor_name Description: Autocreated FK slot
--     * Slot: inputs Description: (List) of input types
-- # Class: BeamPositionMonitor_outputs
--     * Slot: BeamPositionMonitor_name Description: Autocreated FK slot
--     * Slot: outputs Description: (List) of output types
-- # Class: BeamPositionMonitor_upstream
--     * Slot: BeamPositionMonitor_name Description: Autocreated FK slot
--     * Slot: upstream_name Description: (List) of upstream elements.
-- # Class: BeamPositionMonitor_downstream
--     * Slot: BeamPositionMonitor_name Description: Autocreated FK slot
--     * Slot: downstream_name Description: (List) of upstream elements.
-- # Class: BeamArrivalMonitor_alias
--     * Slot: BeamArrivalMonitor_name Description: Autocreated FK slot
--     * Slot: alias Description: Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.
-- # Class: BeamArrivalMonitor_inputs
--     * Slot: BeamArrivalMonitor_name Description: Autocreated FK slot
--     * Slot: inputs Description: (List) of input types
-- # Class: BeamArrivalMonitor_outputs
--     * Slot: BeamArrivalMonitor_name Description: Autocreated FK slot
--     * Slot: outputs Description: (List) of output types
-- # Class: BeamArrivalMonitor_upstream
--     * Slot: BeamArrivalMonitor_name Description: Autocreated FK slot
--     * Slot: upstream_name Description: (List) of upstream elements.
-- # Class: BeamArrivalMonitor_downstream
--     * Slot: BeamArrivalMonitor_name Description: Autocreated FK slot
--     * Slot: downstream_name Description: (List) of upstream elements.
-- # Class: BunchLengthMonitor_alias
--     * Slot: BunchLengthMonitor_name Description: Autocreated FK slot
--     * Slot: alias Description: Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.
-- # Class: BunchLengthMonitor_inputs
--     * Slot: BunchLengthMonitor_name Description: Autocreated FK slot
--     * Slot: inputs Description: (List) of input types
-- # Class: BunchLengthMonitor_outputs
--     * Slot: BunchLengthMonitor_name Description: Autocreated FK slot
--     * Slot: outputs Description: (List) of output types
-- # Class: BunchLengthMonitor_upstream
--     * Slot: BunchLengthMonitor_name Description: Autocreated FK slot
--     * Slot: upstream_name Description: (List) of upstream elements.
-- # Class: BunchLengthMonitor_downstream
--     * Slot: BunchLengthMonitor_name Description: Autocreated FK slot
--     * Slot: downstream_name Description: (List) of upstream elements.
-- # Class: Camera_alias
--     * Slot: Camera_name Description: Autocreated FK slot
--     * Slot: alias Description: Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.
-- # Class: Camera_inputs
--     * Slot: Camera_name Description: Autocreated FK slot
--     * Slot: inputs Description: (List) of input types
-- # Class: Camera_outputs
--     * Slot: Camera_name Description: Autocreated FK slot
--     * Slot: outputs Description: (List) of output types
-- # Class: Camera_upstream
--     * Slot: Camera_name Description: Autocreated FK slot
--     * Slot: upstream_name Description: (List) of upstream elements.
-- # Class: Camera_downstream
--     * Slot: Camera_name Description: Autocreated FK slot
--     * Slot: downstream_name Description: (List) of upstream elements.
-- # Class: Screen_alias
--     * Slot: Screen_name Description: Autocreated FK slot
--     * Slot: alias Description: Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.
-- # Class: Screen_inputs
--     * Slot: Screen_name Description: Autocreated FK slot
--     * Slot: inputs Description: (List) of input types
-- # Class: Screen_outputs
--     * Slot: Screen_name Description: Autocreated FK slot
--     * Slot: outputs Description: (List) of output types
-- # Class: Screen_upstream
--     * Slot: Screen_name Description: Autocreated FK slot
--     * Slot: upstream_name Description: (List) of upstream elements.
-- # Class: Screen_downstream
--     * Slot: Screen_name Description: Autocreated FK slot
--     * Slot: downstream_name Description: (List) of upstream elements.
-- # Class: ChargeDiagnostic_alias
--     * Slot: ChargeDiagnostic_name Description: Autocreated FK slot
--     * Slot: alias Description: Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.
-- # Class: ChargeDiagnostic_inputs
--     * Slot: ChargeDiagnostic_name Description: Autocreated FK slot
--     * Slot: inputs Description: (List) of input types
-- # Class: ChargeDiagnostic_outputs
--     * Slot: ChargeDiagnostic_name Description: Autocreated FK slot
--     * Slot: outputs Description: (List) of output types
-- # Class: ChargeDiagnostic_upstream
--     * Slot: ChargeDiagnostic_name Description: Autocreated FK slot
--     * Slot: upstream_name Description: (List) of upstream elements.
-- # Class: ChargeDiagnostic_downstream
--     * Slot: ChargeDiagnostic_name Description: Autocreated FK slot
--     * Slot: downstream_name Description: (List) of upstream elements.
-- # Class: WallCurrentMonitor_alias
--     * Slot: WallCurrentMonitor_name Description: Autocreated FK slot
--     * Slot: alias Description: Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.
-- # Class: WallCurrentMonitor_inputs
--     * Slot: WallCurrentMonitor_name Description: Autocreated FK slot
--     * Slot: inputs Description: (List) of input types
-- # Class: WallCurrentMonitor_outputs
--     * Slot: WallCurrentMonitor_name Description: Autocreated FK slot
--     * Slot: outputs Description: (List) of output types
-- # Class: WallCurrentMonitor_upstream
--     * Slot: WallCurrentMonitor_name Description: Autocreated FK slot
--     * Slot: upstream_name Description: (List) of upstream elements.
-- # Class: WallCurrentMonitor_downstream
--     * Slot: WallCurrentMonitor_name Description: Autocreated FK slot
--     * Slot: downstream_name Description: (List) of upstream elements.
-- # Class: FaradayCupMonitor_alias
--     * Slot: FaradayCupMonitor_name Description: Autocreated FK slot
--     * Slot: alias Description: Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.
-- # Class: FaradayCupMonitor_inputs
--     * Slot: FaradayCupMonitor_name Description: Autocreated FK slot
--     * Slot: inputs Description: (List) of input types
-- # Class: FaradayCupMonitor_outputs
--     * Slot: FaradayCupMonitor_name Description: Autocreated FK slot
--     * Slot: outputs Description: (List) of output types
-- # Class: FaradayCupMonitor_upstream
--     * Slot: FaradayCupMonitor_name Description: Autocreated FK slot
--     * Slot: upstream_name Description: (List) of upstream elements.
-- # Class: FaradayCupMonitor_downstream
--     * Slot: FaradayCupMonitor_name Description: Autocreated FK slot
--     * Slot: downstream_name Description: (List) of upstream elements.
-- # Class: IntegratedCurrentTransformer_alias
--     * Slot: IntegratedCurrentTransformer_name Description: Autocreated FK slot
--     * Slot: alias Description: Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.
-- # Class: IntegratedCurrentTransformer_inputs
--     * Slot: IntegratedCurrentTransformer_name Description: Autocreated FK slot
--     * Slot: inputs Description: (List) of input types
-- # Class: IntegratedCurrentTransformer_outputs
--     * Slot: IntegratedCurrentTransformer_name Description: Autocreated FK slot
--     * Slot: outputs Description: (List) of output types
-- # Class: IntegratedCurrentTransformer_upstream
--     * Slot: IntegratedCurrentTransformer_name Description: Autocreated FK slot
--     * Slot: upstream_name Description: (List) of upstream elements.
-- # Class: IntegratedCurrentTransformer_downstream
--     * Slot: IntegratedCurrentTransformer_name Description: Autocreated FK slot
--     * Slot: downstream_name Description: (List) of upstream elements.
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
-- # Class: Plasma_alias
--     * Slot: Plasma_name Description: Autocreated FK slot
--     * Slot: alias Description: Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.
-- # Class: Plasma_inputs
--     * Slot: Plasma_name Description: Autocreated FK slot
--     * Slot: inputs Description: (List) of input types
-- # Class: Plasma_outputs
--     * Slot: Plasma_name Description: Autocreated FK slot
--     * Slot: outputs Description: (List) of output types
-- # Class: Plasma_upstream
--     * Slot: Plasma_name Description: Autocreated FK slot
--     * Slot: upstream_name Description: (List) of upstream elements.
-- # Class: Plasma_downstream
--     * Slot: Plasma_name Description: Autocreated FK slot
--     * Slot: downstream_name Description: (List) of upstream elements.
-- # Class: LaserEnergyMeter_alias
--     * Slot: LaserEnergyMeter_name Description: Autocreated FK slot
--     * Slot: alias Description: Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.
-- # Class: LaserEnergyMeter_inputs
--     * Slot: LaserEnergyMeter_name Description: Autocreated FK slot
--     * Slot: inputs Description: (List) of input types
-- # Class: LaserEnergyMeter_outputs
--     * Slot: LaserEnergyMeter_name Description: Autocreated FK slot
--     * Slot: outputs Description: (List) of output types
-- # Class: LaserEnergyMeter_upstream
--     * Slot: LaserEnergyMeter_name Description: Autocreated FK slot
--     * Slot: upstream_name Description: (List) of upstream elements.
-- # Class: LaserEnergyMeter_downstream
--     * Slot: LaserEnergyMeter_name Description: Autocreated FK slot
--     * Slot: downstream_name Description: (List) of upstream elements.
-- # Class: LaserHalfWavePlate_alias
--     * Slot: LaserHalfWavePlate_name Description: Autocreated FK slot
--     * Slot: alias Description: Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.
-- # Class: LaserHalfWavePlate_inputs
--     * Slot: LaserHalfWavePlate_name Description: Autocreated FK slot
--     * Slot: inputs Description: (List) of input types
-- # Class: LaserHalfWavePlate_outputs
--     * Slot: LaserHalfWavePlate_name Description: Autocreated FK slot
--     * Slot: outputs Description: (List) of output types
-- # Class: LaserHalfWavePlate_upstream
--     * Slot: LaserHalfWavePlate_name Description: Autocreated FK slot
--     * Slot: upstream_name Description: (List) of upstream elements.
-- # Class: LaserHalfWavePlate_downstream
--     * Slot: LaserHalfWavePlate_name Description: Autocreated FK slot
--     * Slot: downstream_name Description: (List) of upstream elements.
-- # Class: LaserMirror_alias
--     * Slot: LaserMirror_name Description: Autocreated FK slot
--     * Slot: alias Description: Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.
-- # Class: LaserMirror_inputs
--     * Slot: LaserMirror_name Description: Autocreated FK slot
--     * Slot: inputs Description: (List) of input types
-- # Class: LaserMirror_outputs
--     * Slot: LaserMirror_name Description: Autocreated FK slot
--     * Slot: outputs Description: (List) of output types
-- # Class: LaserMirror_upstream
--     * Slot: LaserMirror_name Description: Autocreated FK slot
--     * Slot: upstream_name Description: (List) of upstream elements.
-- # Class: LaserMirror_downstream
--     * Slot: LaserMirror_name Description: Autocreated FK slot
--     * Slot: downstream_name Description: (List) of upstream elements.
-- # Class: LaserAttenuator_alias
--     * Slot: LaserAttenuator_name Description: Autocreated FK slot
--     * Slot: alias Description: Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.
-- # Class: LaserAttenuator_inputs
--     * Slot: LaserAttenuator_name Description: Autocreated FK slot
--     * Slot: inputs Description: (List) of input types
-- # Class: LaserAttenuator_outputs
--     * Slot: LaserAttenuator_name Description: Autocreated FK slot
--     * Slot: outputs Description: (List) of output types
-- # Class: LaserAttenuator_upstream
--     * Slot: LaserAttenuator_name Description: Autocreated FK slot
--     * Slot: upstream_name Description: (List) of upstream elements.
-- # Class: LaserAttenuator_downstream
--     * Slot: LaserAttenuator_name Description: Autocreated FK slot
--     * Slot: downstream_name Description: (List) of upstream elements.
-- # Class: Dipole_alias
--     * Slot: Dipole_name Description: Autocreated FK slot
--     * Slot: alias Description: Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.
-- # Class: Dipole_inputs
--     * Slot: Dipole_name Description: Autocreated FK slot
--     * Slot: inputs Description: (List) of input types
-- # Class: Dipole_outputs
--     * Slot: Dipole_name Description: Autocreated FK slot
--     * Slot: outputs Description: (List) of output types
-- # Class: Dipole_upstream
--     * Slot: Dipole_name Description: Autocreated FK slot
--     * Slot: upstream_name Description: (List) of upstream elements.
-- # Class: Dipole_downstream
--     * Slot: Dipole_name Description: Autocreated FK slot
--     * Slot: downstream_name Description: (List) of upstream elements.
-- # Class: Quadrupole_alias
--     * Slot: Quadrupole_name Description: Autocreated FK slot
--     * Slot: alias Description: Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings.
-- # Class: Quadrupole_inputs
--     * Slot: Quadrupole_name Description: Autocreated FK slot
--     * Slot: inputs Description: (List) of input types
-- # Class: Quadrupole_outputs
--     * Slot: Quadrupole_name Description: Autocreated FK slot
--     * Slot: outputs Description: (List) of output types
-- # Class: Quadrupole_upstream
--     * Slot: Quadrupole_name Description: Autocreated FK slot
--     * Slot: upstream_name Description: (List) of upstream elements.
-- # Class: Quadrupole_downstream
--     * Slot: Quadrupole_name Description: Autocreated FK slot
--     * Slot: downstream_name Description: (List) of upstream elements.

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
	wakefield_enable BOOLEAN,
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
	smooth INTEGER,
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
	wakefield_enable BOOLEAN,
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
	field_amplitude FLOAT NOT NULL,
	field_definition TEXT,
	wakefield_definition TEXT,
	wakefield_enable BOOLEAN,
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
	wakefield_enable BOOLEAN,
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
	wakefield_enable BOOLEAN,
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
	wakefield_enable BOOLEAN,
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
	wakefield_enable BOOLEAN,
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
	wakefield_enable BOOLEAN,
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
	n_cells FLOAT,
	crest FLOAT,
	phase FLOAT,
	shunt_impedance FLOAT,
	mode_numerator FLOAT,
	mode_denominator INTEGER,
	structure_type TEXT,
	attenuation_constant FLOAT,
	PRIMARY KEY (id)
);
CREATE INDEX "ix_RFCavityElement_id" ON "RFCavityElement" (id);

CREATE TABLE "WakefieldElement" (
	id INTEGER NOT NULL,
	cell_length FLOAT,
	n_cells FLOAT,
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
	n_cells FLOAT,
	phase FLOAT,
	shunt_impedance FLOAT,
	mode_numerator FLOAT,
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

CREATE TABLE "LaserMirrorSense" (
	id INTEGER NOT NULL,
	"left" FLOAT,
	"right" FLOAT,
	up FLOAT,
	down FLOAT,
	PRIMARY KEY (id)
);
CREATE INDEX "ix_LaserMirrorSense_id" ON "LaserMirrorSense" (id);

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

CREATE TABLE "ReferencePlacement" (
	id INTEGER NOT NULL,
	element TEXT NOT NULL,
	point TEXT,
	s_offset FLOAT,
	offset_id INTEGER,
	world_offset_id INTEGER,
	PRIMARY KEY (id),
	FOREIGN KEY(offset_id) REFERENCES "Position" (id),
	FOREIGN KEY(world_offset_id) REFERENCES "Position" (id)
);
CREATE INDEX "ix_ReferencePlacement_id" ON "ReferencePlacement" (id);

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
	"ControlsInformation_id" INTEGER,
	PRIMARY KEY (id),
	FOREIGN KEY("ControlsInformation_id") REFERENCES "ControlsInformation" (id)
);
CREATE INDEX "ix_ControlVariable_id" ON "ControlVariable" (id);

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

CREATE TABLE "PowerSupply" (
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
CREATE INDEX "ix_PowerSupply_name" ON "PowerSupply" (name);

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

CREATE TABLE "ReferenceElement_drawings" (
	"ReferenceElement_id" INTEGER,
	drawings TEXT,
	PRIMARY KEY ("ReferenceElement_id", drawings),
	FOREIGN KEY("ReferenceElement_id") REFERENCES "ReferenceElement" (id)
);
CREATE INDEX "ix_ReferenceElement_drawings_drawings" ON "ReferenceElement_drawings" (drawings);
CREATE INDEX "ix_ReferenceElement_drawings_ReferenceElement_id" ON "ReferenceElement_drawings" ("ReferenceElement_id");

CREATE TABLE "ReferenceElement_design_files" (
	"ReferenceElement_id" INTEGER,
	design_files TEXT,
	PRIMARY KEY ("ReferenceElement_id", design_files),
	FOREIGN KEY("ReferenceElement_id") REFERENCES "ReferenceElement" (id)
);
CREATE INDEX "ix_ReferenceElement_design_files_design_files" ON "ReferenceElement_design_files" (design_files);
CREATE INDEX "ix_ReferenceElement_design_files_ReferenceElement_id" ON "ReferenceElement_design_files" ("ReferenceElement_id");

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

CREATE TABLE "AcceleratorElement_inputs" (
	"AcceleratorElement_name" TEXT,
	inputs VARCHAR(17),
	PRIMARY KEY ("AcceleratorElement_name", inputs),
	FOREIGN KEY("AcceleratorElement_name") REFERENCES "AcceleratorElement" (name)
);
CREATE INDEX "ix_AcceleratorElement_inputs_AcceleratorElement_name" ON "AcceleratorElement_inputs" ("AcceleratorElement_name");
CREATE INDEX "ix_AcceleratorElement_inputs_inputs" ON "AcceleratorElement_inputs" (inputs);

CREATE TABLE "AcceleratorElement_outputs" (
	"AcceleratorElement_name" TEXT,
	outputs VARCHAR(17),
	PRIMARY KEY ("AcceleratorElement_name", outputs),
	FOREIGN KEY("AcceleratorElement_name") REFERENCES "AcceleratorElement" (name)
);
CREATE INDEX "ix_AcceleratorElement_outputs_AcceleratorElement_name" ON "AcceleratorElement_outputs" ("AcceleratorElement_name");
CREATE INDEX "ix_AcceleratorElement_outputs_outputs" ON "AcceleratorElement_outputs" (outputs);

CREATE TABLE "AcceleratorElement_upstream" (
	"AcceleratorElement_name" TEXT,
	upstream_name TEXT,
	PRIMARY KEY ("AcceleratorElement_name", upstream_name),
	FOREIGN KEY("AcceleratorElement_name") REFERENCES "AcceleratorElement" (name),
	FOREIGN KEY(upstream_name) REFERENCES "AcceleratorElement" (name)
);
CREATE INDEX "ix_AcceleratorElement_upstream_upstream_name" ON "AcceleratorElement_upstream" (upstream_name);
CREATE INDEX "ix_AcceleratorElement_upstream_AcceleratorElement_name" ON "AcceleratorElement_upstream" ("AcceleratorElement_name");

CREATE TABLE "AcceleratorElement_downstream" (
	"AcceleratorElement_name" TEXT,
	downstream_name TEXT,
	PRIMARY KEY ("AcceleratorElement_name", downstream_name),
	FOREIGN KEY("AcceleratorElement_name") REFERENCES "AcceleratorElement" (name),
	FOREIGN KEY(downstream_name) REFERENCES "AcceleratorElement" (name)
);
CREATE INDEX "ix_AcceleratorElement_downstream_AcceleratorElement_name" ON "AcceleratorElement_downstream" ("AcceleratorElement_name");
CREATE INDEX "ix_AcceleratorElement_downstream_downstream_name" ON "AcceleratorElement_downstream" (downstream_name);

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
CREATE INDEX "ix_MachineModel_layouts_layouts_name" ON "MachineModel_layouts" (layouts_name);
CREATE INDEX "ix_MachineModel_layouts_MachineModel_id" ON "MachineModel_layouts" ("MachineModel_id");

CREATE TABLE "FieldIntegral_coefficients" (
	"FieldIntegral_id" INTEGER,
	coefficients FLOAT,
	PRIMARY KEY ("FieldIntegral_id", coefficients),
	FOREIGN KEY("FieldIntegral_id") REFERENCES "FieldIntegral" (id)
);
CREATE INDEX "ix_FieldIntegral_coefficients_FieldIntegral_id" ON "FieldIntegral_coefficients" ("FieldIntegral_id");
CREATE INDEX "ix_FieldIntegral_coefficients_coefficients" ON "FieldIntegral_coefficients" (coefficients);

CREATE TABLE "DegaussableElement_values" (
	"DegaussableElement_id" INTEGER,
	"values" FLOAT,
	PRIMARY KEY ("DegaussableElement_id", "values"),
	FOREIGN KEY("DegaussableElement_id") REFERENCES "DegaussableElement" (id)
);
CREATE INDEX "ix_DegaussableElement_values_values" ON "DegaussableElement_values" ("values");
CREATE INDEX "ix_DegaussableElement_values_DegaussableElement_id" ON "DegaussableElement_values" ("DegaussableElement_id");

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
CREATE INDEX "ix_RFCavityElement_gradient_calibration_gradient_calibration" ON "RFCavityElement_gradient_calibration" (gradient_calibration);
CREATE INDEX "ix_RFCavityElement_gradient_calibration_RFCavityElement_id" ON "RFCavityElement_gradient_calibration" ("RFCavityElement_id");

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
CREATE INDEX "ix_CameraMask_middle_CameraMask_id" ON "CameraMask_middle" ("CameraMask_id");
CREATE INDEX "ix_CameraMask_middle_middle" ON "CameraMask_middle" (middle);

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
CREATE INDEX "ix_CameraMask_maximum_maximum" ON "CameraMask_maximum" (maximum);
CREATE INDEX "ix_CameraMask_maximum_CameraMask_id" ON "CameraMask_maximum" ("CameraMask_id");

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
CREATE INDEX "ix_CameraSensor_minimum_CameraSensor_id" ON "CameraSensor_minimum" ("CameraSensor_id");
CREATE INDEX "ix_CameraSensor_minimum_minimum" ON "CameraSensor_minimum" (minimum);

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
CREATE INDEX "ix_CameraSensor_operating_middle_operating_middle" ON "CameraSensor_operating_middle" (operating_middle);
CREATE INDEX "ix_CameraSensor_operating_middle_CameraSensor_id" ON "CameraSensor_operating_middle" ("CameraSensor_id");

CREATE TABLE "CameraSensor_mechanical_middle" (
	"CameraSensor_id" INTEGER,
	mechanical_middle FLOAT,
	PRIMARY KEY ("CameraSensor_id", mechanical_middle),
	FOREIGN KEY("CameraSensor_id") REFERENCES "CameraSensor" (id)
);
CREATE INDEX "ix_CameraSensor_mechanical_middle_mechanical_middle" ON "CameraSensor_mechanical_middle" (mechanical_middle);
CREATE INDEX "ix_CameraSensor_mechanical_middle_CameraSensor_id" ON "CameraSensor_mechanical_middle" ("CameraSensor_id");

CREATE TABLE "PhysicalElement" (
	id INTEGER NOT NULL,
	length FLOAT,
	physical_angle FLOAT,
	s FLOAT,
	s_point TEXT,
	middle_id INTEGER,
	datum_id INTEGER,
	rotation_id INTEGER,
	global_rotation_id INTEGER,
	error_id INTEGER,
	survey_id INTEGER,
	reference_placement_id INTEGER,
	PRIMARY KEY (id),
	FOREIGN KEY(middle_id) REFERENCES "Position" (id),
	FOREIGN KEY(datum_id) REFERENCES "Position" (id),
	FOREIGN KEY(rotation_id) REFERENCES "Rotation" (id),
	FOREIGN KEY(global_rotation_id) REFERENCES "Rotation" (id),
	FOREIGN KEY(error_id) REFERENCES "ElementPositionError" (id),
	FOREIGN KEY(survey_id) REFERENCES "ElementSurvey" (id),
	FOREIGN KEY(reference_placement_id) REFERENCES "ReferencePlacement" (id)
);
CREATE INDEX "ix_PhysicalElement_id" ON "PhysicalElement" (id);

CREATE TABLE "MagneticElement" (
	id INTEGER NOT NULL,
	"order" INTEGER,
	skew BOOLEAN,
	length FLOAT,
	settle_time FLOAT,
	entrance_edge_angle TEXT,
	exit_edge_angle TEXT,
	gap FLOAT,
	bore FLOAT,
	plane VARCHAR(10),
	width FLOAT,
	tilt FLOAT,
	edge_field_integral FLOAT,
	fringe_field_coefficient FLOAT,
	gradient FLOAT,
	angle FLOAT,
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

CREATE TABLE "Dipole_Magnet" (
	id INTEGER NOT NULL,
	"order" INTEGER,
	skew BOOLEAN,
	length FLOAT,
	settle_time FLOAT,
	entrance_edge_angle TEXT,
	exit_edge_angle TEXT,
	gap FLOAT,
	bore FLOAT,
	plane VARCHAR(10),
	width FLOAT,
	tilt FLOAT,
	edge_field_integral FLOAT,
	fringe_field_coefficient FLOAT,
	gradient FLOAT,
	angle FLOAT,
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
CREATE INDEX "ix_Dipole_Magnet_id" ON "Dipole_Magnet" (id);

CREATE TABLE "Quadrupole_Magnet" (
	id INTEGER NOT NULL,
	"order" INTEGER,
	skew BOOLEAN,
	length FLOAT,
	settle_time FLOAT,
	entrance_edge_angle TEXT,
	exit_edge_angle TEXT,
	gap FLOAT,
	bore FLOAT,
	plane VARCHAR(10),
	width FLOAT,
	tilt FLOAT,
	edge_field_integral FLOAT,
	fringe_field_coefficient FLOAT,
	gradient FLOAT,
	angle FLOAT,
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
CREATE INDEX "ix_Quadrupole_Magnet_id" ON "Quadrupole_Magnet" (id);

CREATE TABLE "StandardElement_alias" (
	"StandardElement_name" TEXT,
	alias TEXT,
	PRIMARY KEY ("StandardElement_name", alias),
	FOREIGN KEY("StandardElement_name") REFERENCES "StandardElement" (name)
);
CREATE INDEX "ix_StandardElement_alias_alias" ON "StandardElement_alias" (alias);
CREATE INDEX "ix_StandardElement_alias_StandardElement_name" ON "StandardElement_alias" ("StandardElement_name");

CREATE TABLE "StandardElement_inputs" (
	"StandardElement_name" TEXT,
	inputs VARCHAR(17),
	PRIMARY KEY ("StandardElement_name", inputs),
	FOREIGN KEY("StandardElement_name") REFERENCES "StandardElement" (name)
);
CREATE INDEX "ix_StandardElement_inputs_StandardElement_name" ON "StandardElement_inputs" ("StandardElement_name");
CREATE INDEX "ix_StandardElement_inputs_inputs" ON "StandardElement_inputs" (inputs);

CREATE TABLE "StandardElement_outputs" (
	"StandardElement_name" TEXT,
	outputs VARCHAR(17),
	PRIMARY KEY ("StandardElement_name", outputs),
	FOREIGN KEY("StandardElement_name") REFERENCES "StandardElement" (name)
);
CREATE INDEX "ix_StandardElement_outputs_StandardElement_name" ON "StandardElement_outputs" ("StandardElement_name");
CREATE INDEX "ix_StandardElement_outputs_outputs" ON "StandardElement_outputs" (outputs);

CREATE TABLE "StandardElement_upstream" (
	"StandardElement_name" TEXT,
	upstream_name TEXT,
	PRIMARY KEY ("StandardElement_name", upstream_name),
	FOREIGN KEY("StandardElement_name") REFERENCES "StandardElement" (name),
	FOREIGN KEY(upstream_name) REFERENCES "AcceleratorElement" (name)
);
CREATE INDEX "ix_StandardElement_upstream_upstream_name" ON "StandardElement_upstream" (upstream_name);
CREATE INDEX "ix_StandardElement_upstream_StandardElement_name" ON "StandardElement_upstream" ("StandardElement_name");

CREATE TABLE "StandardElement_downstream" (
	"StandardElement_name" TEXT,
	downstream_name TEXT,
	PRIMARY KEY ("StandardElement_name", downstream_name),
	FOREIGN KEY("StandardElement_name") REFERENCES "StandardElement" (name),
	FOREIGN KEY(downstream_name) REFERENCES "AcceleratorElement" (name)
);
CREATE INDEX "ix_StandardElement_downstream_StandardElement_name" ON "StandardElement_downstream" ("StandardElement_name");
CREATE INDEX "ix_StandardElement_downstream_downstream_name" ON "StandardElement_downstream" (downstream_name);

CREATE TABLE "Element_alias" (
	"Element_name" TEXT,
	alias TEXT,
	PRIMARY KEY ("Element_name", alias),
	FOREIGN KEY("Element_name") REFERENCES "Element" (name)
);
CREATE INDEX "ix_Element_alias_Element_name" ON "Element_alias" ("Element_name");
CREATE INDEX "ix_Element_alias_alias" ON "Element_alias" (alias);

CREATE TABLE "Element_inputs" (
	"Element_name" TEXT,
	inputs VARCHAR(17),
	PRIMARY KEY ("Element_name", inputs),
	FOREIGN KEY("Element_name") REFERENCES "Element" (name)
);
CREATE INDEX "ix_Element_inputs_Element_name" ON "Element_inputs" ("Element_name");
CREATE INDEX "ix_Element_inputs_inputs" ON "Element_inputs" (inputs);

CREATE TABLE "Element_outputs" (
	"Element_name" TEXT,
	outputs VARCHAR(17),
	PRIMARY KEY ("Element_name", outputs),
	FOREIGN KEY("Element_name") REFERENCES "Element" (name)
);
CREATE INDEX "ix_Element_outputs_outputs" ON "Element_outputs" (outputs);
CREATE INDEX "ix_Element_outputs_Element_name" ON "Element_outputs" ("Element_name");

CREATE TABLE "Element_upstream" (
	"Element_name" TEXT,
	upstream_name TEXT,
	PRIMARY KEY ("Element_name", upstream_name),
	FOREIGN KEY("Element_name") REFERENCES "Element" (name),
	FOREIGN KEY(upstream_name) REFERENCES "AcceleratorElement" (name)
);
CREATE INDEX "ix_Element_upstream_upstream_name" ON "Element_upstream" (upstream_name);
CREATE INDEX "ix_Element_upstream_Element_name" ON "Element_upstream" ("Element_name");

CREATE TABLE "Element_downstream" (
	"Element_name" TEXT,
	downstream_name TEXT,
	PRIMARY KEY ("Element_name", downstream_name),
	FOREIGN KEY("Element_name") REFERENCES "Element" (name),
	FOREIGN KEY(downstream_name) REFERENCES "AcceleratorElement" (name)
);
CREATE INDEX "ix_Element_downstream_downstream_name" ON "Element_downstream" (downstream_name);
CREATE INDEX "ix_Element_downstream_Element_name" ON "Element_downstream" ("Element_name");

CREATE TABLE "Lighting_alias" (
	"Lighting_name" TEXT,
	alias TEXT,
	PRIMARY KEY ("Lighting_name", alias),
	FOREIGN KEY("Lighting_name") REFERENCES "Lighting" (name)
);
CREATE INDEX "ix_Lighting_alias_Lighting_name" ON "Lighting_alias" ("Lighting_name");
CREATE INDEX "ix_Lighting_alias_alias" ON "Lighting_alias" (alias);

CREATE TABLE "Lighting_inputs" (
	"Lighting_name" TEXT,
	inputs VARCHAR(17),
	PRIMARY KEY ("Lighting_name", inputs),
	FOREIGN KEY("Lighting_name") REFERENCES "Lighting" (name)
);
CREATE INDEX "ix_Lighting_inputs_inputs" ON "Lighting_inputs" (inputs);
CREATE INDEX "ix_Lighting_inputs_Lighting_name" ON "Lighting_inputs" ("Lighting_name");

CREATE TABLE "Lighting_outputs" (
	"Lighting_name" TEXT,
	outputs VARCHAR(17),
	PRIMARY KEY ("Lighting_name", outputs),
	FOREIGN KEY("Lighting_name") REFERENCES "Lighting" (name)
);
CREATE INDEX "ix_Lighting_outputs_Lighting_name" ON "Lighting_outputs" ("Lighting_name");
CREATE INDEX "ix_Lighting_outputs_outputs" ON "Lighting_outputs" (outputs);

CREATE TABLE "Lighting_upstream" (
	"Lighting_name" TEXT,
	upstream_name TEXT,
	PRIMARY KEY ("Lighting_name", upstream_name),
	FOREIGN KEY("Lighting_name") REFERENCES "Lighting" (name),
	FOREIGN KEY(upstream_name) REFERENCES "AcceleratorElement" (name)
);
CREATE INDEX "ix_Lighting_upstream_upstream_name" ON "Lighting_upstream" (upstream_name);
CREATE INDEX "ix_Lighting_upstream_Lighting_name" ON "Lighting_upstream" ("Lighting_name");

CREATE TABLE "Lighting_downstream" (
	"Lighting_name" TEXT,
	downstream_name TEXT,
	PRIMARY KEY ("Lighting_name", downstream_name),
	FOREIGN KEY("Lighting_name") REFERENCES "Lighting" (name),
	FOREIGN KEY(downstream_name) REFERENCES "AcceleratorElement" (name)
);
CREATE INDEX "ix_Lighting_downstream_downstream_name" ON "Lighting_downstream" (downstream_name);
CREATE INDEX "ix_Lighting_downstream_Lighting_name" ON "Lighting_downstream" ("Lighting_name");

CREATE TABLE "PowerSupply_alias" (
	"PowerSupply_name" TEXT,
	alias TEXT,
	PRIMARY KEY ("PowerSupply_name", alias),
	FOREIGN KEY("PowerSupply_name") REFERENCES "PowerSupply" (name)
);
CREATE INDEX "ix_PowerSupply_alias_alias" ON "PowerSupply_alias" (alias);
CREATE INDEX "ix_PowerSupply_alias_PowerSupply_name" ON "PowerSupply_alias" ("PowerSupply_name");

CREATE TABLE "PowerSupply_inputs" (
	"PowerSupply_name" TEXT,
	inputs VARCHAR(17),
	PRIMARY KEY ("PowerSupply_name", inputs),
	FOREIGN KEY("PowerSupply_name") REFERENCES "PowerSupply" (name)
);
CREATE INDEX "ix_PowerSupply_inputs_inputs" ON "PowerSupply_inputs" (inputs);
CREATE INDEX "ix_PowerSupply_inputs_PowerSupply_name" ON "PowerSupply_inputs" ("PowerSupply_name");

CREATE TABLE "PowerSupply_outputs" (
	"PowerSupply_name" TEXT,
	outputs VARCHAR(17),
	PRIMARY KEY ("PowerSupply_name", outputs),
	FOREIGN KEY("PowerSupply_name") REFERENCES "PowerSupply" (name)
);
CREATE INDEX "ix_PowerSupply_outputs_PowerSupply_name" ON "PowerSupply_outputs" ("PowerSupply_name");
CREATE INDEX "ix_PowerSupply_outputs_outputs" ON "PowerSupply_outputs" (outputs);

CREATE TABLE "PowerSupply_upstream" (
	"PowerSupply_name" TEXT,
	upstream_name TEXT,
	PRIMARY KEY ("PowerSupply_name", upstream_name),
	FOREIGN KEY("PowerSupply_name") REFERENCES "PowerSupply" (name),
	FOREIGN KEY(upstream_name) REFERENCES "AcceleratorElement" (name)
);
CREATE INDEX "ix_PowerSupply_upstream_upstream_name" ON "PowerSupply_upstream" (upstream_name);
CREATE INDEX "ix_PowerSupply_upstream_PowerSupply_name" ON "PowerSupply_upstream" ("PowerSupply_name");

CREATE TABLE "PowerSupply_downstream" (
	"PowerSupply_name" TEXT,
	downstream_name TEXT,
	PRIMARY KEY ("PowerSupply_name", downstream_name),
	FOREIGN KEY("PowerSupply_name") REFERENCES "PowerSupply" (name),
	FOREIGN KEY(downstream_name) REFERENCES "AcceleratorElement" (name)
);
CREATE INDEX "ix_PowerSupply_downstream_PowerSupply_name" ON "PowerSupply_downstream" ("PowerSupply_name");
CREATE INDEX "ix_PowerSupply_downstream_downstream_name" ON "PowerSupply_downstream" (downstream_name);

CREATE TABLE "RFModulator_alias" (
	"RFModulator_name" TEXT,
	alias TEXT,
	PRIMARY KEY ("RFModulator_name", alias),
	FOREIGN KEY("RFModulator_name") REFERENCES "RFModulator" (name)
);
CREATE INDEX "ix_RFModulator_alias_alias" ON "RFModulator_alias" (alias);
CREATE INDEX "ix_RFModulator_alias_RFModulator_name" ON "RFModulator_alias" ("RFModulator_name");

CREATE TABLE "RFModulator_inputs" (
	"RFModulator_name" TEXT,
	inputs VARCHAR(17),
	PRIMARY KEY ("RFModulator_name", inputs),
	FOREIGN KEY("RFModulator_name") REFERENCES "RFModulator" (name)
);
CREATE INDEX "ix_RFModulator_inputs_RFModulator_name" ON "RFModulator_inputs" ("RFModulator_name");
CREATE INDEX "ix_RFModulator_inputs_inputs" ON "RFModulator_inputs" (inputs);

CREATE TABLE "RFModulator_outputs" (
	"RFModulator_name" TEXT,
	outputs VARCHAR(17),
	PRIMARY KEY ("RFModulator_name", outputs),
	FOREIGN KEY("RFModulator_name") REFERENCES "RFModulator" (name)
);
CREATE INDEX "ix_RFModulator_outputs_outputs" ON "RFModulator_outputs" (outputs);
CREATE INDEX "ix_RFModulator_outputs_RFModulator_name" ON "RFModulator_outputs" ("RFModulator_name");

CREATE TABLE "RFModulator_upstream" (
	"RFModulator_name" TEXT,
	upstream_name TEXT,
	PRIMARY KEY ("RFModulator_name", upstream_name),
	FOREIGN KEY("RFModulator_name") REFERENCES "RFModulator" (name),
	FOREIGN KEY(upstream_name) REFERENCES "AcceleratorElement" (name)
);
CREATE INDEX "ix_RFModulator_upstream_upstream_name" ON "RFModulator_upstream" (upstream_name);
CREATE INDEX "ix_RFModulator_upstream_RFModulator_name" ON "RFModulator_upstream" ("RFModulator_name");

CREATE TABLE "RFModulator_downstream" (
	"RFModulator_name" TEXT,
	downstream_name TEXT,
	PRIMARY KEY ("RFModulator_name", downstream_name),
	FOREIGN KEY("RFModulator_name") REFERENCES "RFModulator" (name),
	FOREIGN KEY(downstream_name) REFERENCES "AcceleratorElement" (name)
);
CREATE INDEX "ix_RFModulator_downstream_RFModulator_name" ON "RFModulator_downstream" ("RFModulator_name");
CREATE INDEX "ix_RFModulator_downstream_downstream_name" ON "RFModulator_downstream" (downstream_name);

CREATE TABLE "RFProtection_alias" (
	"RFProtection_name" TEXT,
	alias TEXT,
	PRIMARY KEY ("RFProtection_name", alias),
	FOREIGN KEY("RFProtection_name") REFERENCES "RFProtection" (name)
);
CREATE INDEX "ix_RFProtection_alias_alias" ON "RFProtection_alias" (alias);
CREATE INDEX "ix_RFProtection_alias_RFProtection_name" ON "RFProtection_alias" ("RFProtection_name");

CREATE TABLE "RFProtection_inputs" (
	"RFProtection_name" TEXT,
	inputs VARCHAR(17),
	PRIMARY KEY ("RFProtection_name", inputs),
	FOREIGN KEY("RFProtection_name") REFERENCES "RFProtection" (name)
);
CREATE INDEX "ix_RFProtection_inputs_RFProtection_name" ON "RFProtection_inputs" ("RFProtection_name");
CREATE INDEX "ix_RFProtection_inputs_inputs" ON "RFProtection_inputs" (inputs);

CREATE TABLE "RFProtection_outputs" (
	"RFProtection_name" TEXT,
	outputs VARCHAR(17),
	PRIMARY KEY ("RFProtection_name", outputs),
	FOREIGN KEY("RFProtection_name") REFERENCES "RFProtection" (name)
);
CREATE INDEX "ix_RFProtection_outputs_RFProtection_name" ON "RFProtection_outputs" ("RFProtection_name");
CREATE INDEX "ix_RFProtection_outputs_outputs" ON "RFProtection_outputs" (outputs);

CREATE TABLE "RFProtection_upstream" (
	"RFProtection_name" TEXT,
	upstream_name TEXT,
	PRIMARY KEY ("RFProtection_name", upstream_name),
	FOREIGN KEY("RFProtection_name") REFERENCES "RFProtection" (name),
	FOREIGN KEY(upstream_name) REFERENCES "AcceleratorElement" (name)
);
CREATE INDEX "ix_RFProtection_upstream_upstream_name" ON "RFProtection_upstream" (upstream_name);
CREATE INDEX "ix_RFProtection_upstream_RFProtection_name" ON "RFProtection_upstream" ("RFProtection_name");

CREATE TABLE "RFProtection_downstream" (
	"RFProtection_name" TEXT,
	downstream_name TEXT,
	PRIMARY KEY ("RFProtection_name", downstream_name),
	FOREIGN KEY("RFProtection_name") REFERENCES "RFProtection" (name),
	FOREIGN KEY(downstream_name) REFERENCES "AcceleratorElement" (name)
);
CREATE INDEX "ix_RFProtection_downstream_downstream_name" ON "RFProtection_downstream" (downstream_name);
CREATE INDEX "ix_RFProtection_downstream_RFProtection_name" ON "RFProtection_downstream" ("RFProtection_name");

CREATE TABLE "RFHeartbeat_alias" (
	"RFHeartbeat_name" TEXT,
	alias TEXT,
	PRIMARY KEY ("RFHeartbeat_name", alias),
	FOREIGN KEY("RFHeartbeat_name") REFERENCES "RFHeartbeat" (name)
);
CREATE INDEX "ix_RFHeartbeat_alias_alias" ON "RFHeartbeat_alias" (alias);
CREATE INDEX "ix_RFHeartbeat_alias_RFHeartbeat_name" ON "RFHeartbeat_alias" ("RFHeartbeat_name");

CREATE TABLE "RFHeartbeat_inputs" (
	"RFHeartbeat_name" TEXT,
	inputs VARCHAR(17),
	PRIMARY KEY ("RFHeartbeat_name", inputs),
	FOREIGN KEY("RFHeartbeat_name") REFERENCES "RFHeartbeat" (name)
);
CREATE INDEX "ix_RFHeartbeat_inputs_RFHeartbeat_name" ON "RFHeartbeat_inputs" ("RFHeartbeat_name");
CREATE INDEX "ix_RFHeartbeat_inputs_inputs" ON "RFHeartbeat_inputs" (inputs);

CREATE TABLE "RFHeartbeat_outputs" (
	"RFHeartbeat_name" TEXT,
	outputs VARCHAR(17),
	PRIMARY KEY ("RFHeartbeat_name", outputs),
	FOREIGN KEY("RFHeartbeat_name") REFERENCES "RFHeartbeat" (name)
);
CREATE INDEX "ix_RFHeartbeat_outputs_outputs" ON "RFHeartbeat_outputs" (outputs);
CREATE INDEX "ix_RFHeartbeat_outputs_RFHeartbeat_name" ON "RFHeartbeat_outputs" ("RFHeartbeat_name");

CREATE TABLE "RFHeartbeat_upstream" (
	"RFHeartbeat_name" TEXT,
	upstream_name TEXT,
	PRIMARY KEY ("RFHeartbeat_name", upstream_name),
	FOREIGN KEY("RFHeartbeat_name") REFERENCES "RFHeartbeat" (name),
	FOREIGN KEY(upstream_name) REFERENCES "AcceleratorElement" (name)
);
CREATE INDEX "ix_RFHeartbeat_upstream_RFHeartbeat_name" ON "RFHeartbeat_upstream" ("RFHeartbeat_name");
CREATE INDEX "ix_RFHeartbeat_upstream_upstream_name" ON "RFHeartbeat_upstream" (upstream_name);

CREATE TABLE "RFHeartbeat_downstream" (
	"RFHeartbeat_name" TEXT,
	downstream_name TEXT,
	PRIMARY KEY ("RFHeartbeat_name", downstream_name),
	FOREIGN KEY("RFHeartbeat_name") REFERENCES "RFHeartbeat" (name),
	FOREIGN KEY(downstream_name) REFERENCES "AcceleratorElement" (name)
);
CREATE INDEX "ix_RFHeartbeat_downstream_RFHeartbeat_name" ON "RFHeartbeat_downstream" ("RFHeartbeat_name");
CREATE INDEX "ix_RFHeartbeat_downstream_downstream_name" ON "RFHeartbeat_downstream" (downstream_name);

CREATE TABLE "LaserEnergyMeter_alias" (
	"LaserEnergyMeter_name" TEXT,
	alias TEXT,
	PRIMARY KEY ("LaserEnergyMeter_name", alias),
	FOREIGN KEY("LaserEnergyMeter_name") REFERENCES "LaserEnergyMeter" (name)
);
CREATE INDEX "ix_LaserEnergyMeter_alias_alias" ON "LaserEnergyMeter_alias" (alias);
CREATE INDEX "ix_LaserEnergyMeter_alias_LaserEnergyMeter_name" ON "LaserEnergyMeter_alias" ("LaserEnergyMeter_name");

CREATE TABLE "LaserEnergyMeter_inputs" (
	"LaserEnergyMeter_name" TEXT,
	inputs VARCHAR(17),
	PRIMARY KEY ("LaserEnergyMeter_name", inputs),
	FOREIGN KEY("LaserEnergyMeter_name") REFERENCES "LaserEnergyMeter" (name)
);
CREATE INDEX "ix_LaserEnergyMeter_inputs_LaserEnergyMeter_name" ON "LaserEnergyMeter_inputs" ("LaserEnergyMeter_name");
CREATE INDEX "ix_LaserEnergyMeter_inputs_inputs" ON "LaserEnergyMeter_inputs" (inputs);

CREATE TABLE "LaserEnergyMeter_outputs" (
	"LaserEnergyMeter_name" TEXT,
	outputs VARCHAR(17),
	PRIMARY KEY ("LaserEnergyMeter_name", outputs),
	FOREIGN KEY("LaserEnergyMeter_name") REFERENCES "LaserEnergyMeter" (name)
);
CREATE INDEX "ix_LaserEnergyMeter_outputs_LaserEnergyMeter_name" ON "LaserEnergyMeter_outputs" ("LaserEnergyMeter_name");
CREATE INDEX "ix_LaserEnergyMeter_outputs_outputs" ON "LaserEnergyMeter_outputs" (outputs);

CREATE TABLE "LaserEnergyMeter_upstream" (
	"LaserEnergyMeter_name" TEXT,
	upstream_name TEXT,
	PRIMARY KEY ("LaserEnergyMeter_name", upstream_name),
	FOREIGN KEY("LaserEnergyMeter_name") REFERENCES "LaserEnergyMeter" (name),
	FOREIGN KEY(upstream_name) REFERENCES "AcceleratorElement" (name)
);
CREATE INDEX "ix_LaserEnergyMeter_upstream_upstream_name" ON "LaserEnergyMeter_upstream" (upstream_name);
CREATE INDEX "ix_LaserEnergyMeter_upstream_LaserEnergyMeter_name" ON "LaserEnergyMeter_upstream" ("LaserEnergyMeter_name");

CREATE TABLE "LaserEnergyMeter_downstream" (
	"LaserEnergyMeter_name" TEXT,
	downstream_name TEXT,
	PRIMARY KEY ("LaserEnergyMeter_name", downstream_name),
	FOREIGN KEY("LaserEnergyMeter_name") REFERENCES "LaserEnergyMeter" (name),
	FOREIGN KEY(downstream_name) REFERENCES "AcceleratorElement" (name)
);
CREATE INDEX "ix_LaserEnergyMeter_downstream_LaserEnergyMeter_name" ON "LaserEnergyMeter_downstream" ("LaserEnergyMeter_name");
CREATE INDEX "ix_LaserEnergyMeter_downstream_downstream_name" ON "LaserEnergyMeter_downstream" (downstream_name);

CREATE TABLE "LaserHalfWavePlate_alias" (
	"LaserHalfWavePlate_name" TEXT,
	alias TEXT,
	PRIMARY KEY ("LaserHalfWavePlate_name", alias),
	FOREIGN KEY("LaserHalfWavePlate_name") REFERENCES "LaserHalfWavePlate" (name)
);
CREATE INDEX "ix_LaserHalfWavePlate_alias_LaserHalfWavePlate_name" ON "LaserHalfWavePlate_alias" ("LaserHalfWavePlate_name");
CREATE INDEX "ix_LaserHalfWavePlate_alias_alias" ON "LaserHalfWavePlate_alias" (alias);

CREATE TABLE "LaserHalfWavePlate_inputs" (
	"LaserHalfWavePlate_name" TEXT,
	inputs VARCHAR(17),
	PRIMARY KEY ("LaserHalfWavePlate_name", inputs),
	FOREIGN KEY("LaserHalfWavePlate_name") REFERENCES "LaserHalfWavePlate" (name)
);
CREATE INDEX "ix_LaserHalfWavePlate_inputs_inputs" ON "LaserHalfWavePlate_inputs" (inputs);
CREATE INDEX "ix_LaserHalfWavePlate_inputs_LaserHalfWavePlate_name" ON "LaserHalfWavePlate_inputs" ("LaserHalfWavePlate_name");

CREATE TABLE "LaserHalfWavePlate_outputs" (
	"LaserHalfWavePlate_name" TEXT,
	outputs VARCHAR(17),
	PRIMARY KEY ("LaserHalfWavePlate_name", outputs),
	FOREIGN KEY("LaserHalfWavePlate_name") REFERENCES "LaserHalfWavePlate" (name)
);
CREATE INDEX "ix_LaserHalfWavePlate_outputs_LaserHalfWavePlate_name" ON "LaserHalfWavePlate_outputs" ("LaserHalfWavePlate_name");
CREATE INDEX "ix_LaserHalfWavePlate_outputs_outputs" ON "LaserHalfWavePlate_outputs" (outputs);

CREATE TABLE "LaserHalfWavePlate_upstream" (
	"LaserHalfWavePlate_name" TEXT,
	upstream_name TEXT,
	PRIMARY KEY ("LaserHalfWavePlate_name", upstream_name),
	FOREIGN KEY("LaserHalfWavePlate_name") REFERENCES "LaserHalfWavePlate" (name),
	FOREIGN KEY(upstream_name) REFERENCES "AcceleratorElement" (name)
);
CREATE INDEX "ix_LaserHalfWavePlate_upstream_upstream_name" ON "LaserHalfWavePlate_upstream" (upstream_name);
CREATE INDEX "ix_LaserHalfWavePlate_upstream_LaserHalfWavePlate_name" ON "LaserHalfWavePlate_upstream" ("LaserHalfWavePlate_name");

CREATE TABLE "LaserHalfWavePlate_downstream" (
	"LaserHalfWavePlate_name" TEXT,
	downstream_name TEXT,
	PRIMARY KEY ("LaserHalfWavePlate_name", downstream_name),
	FOREIGN KEY("LaserHalfWavePlate_name") REFERENCES "LaserHalfWavePlate" (name),
	FOREIGN KEY(downstream_name) REFERENCES "AcceleratorElement" (name)
);
CREATE INDEX "ix_LaserHalfWavePlate_downstream_LaserHalfWavePlate_name" ON "LaserHalfWavePlate_downstream" ("LaserHalfWavePlate_name");
CREATE INDEX "ix_LaserHalfWavePlate_downstream_downstream_name" ON "LaserHalfWavePlate_downstream" (downstream_name);

CREATE TABLE "LaserAttenuator_alias" (
	"LaserAttenuator_name" TEXT,
	alias TEXT,
	PRIMARY KEY ("LaserAttenuator_name", alias),
	FOREIGN KEY("LaserAttenuator_name") REFERENCES "LaserAttenuator" (name)
);
CREATE INDEX "ix_LaserAttenuator_alias_alias" ON "LaserAttenuator_alias" (alias);
CREATE INDEX "ix_LaserAttenuator_alias_LaserAttenuator_name" ON "LaserAttenuator_alias" ("LaserAttenuator_name");

CREATE TABLE "LaserAttenuator_inputs" (
	"LaserAttenuator_name" TEXT,
	inputs VARCHAR(17),
	PRIMARY KEY ("LaserAttenuator_name", inputs),
	FOREIGN KEY("LaserAttenuator_name") REFERENCES "LaserAttenuator" (name)
);
CREATE INDEX "ix_LaserAttenuator_inputs_LaserAttenuator_name" ON "LaserAttenuator_inputs" ("LaserAttenuator_name");
CREATE INDEX "ix_LaserAttenuator_inputs_inputs" ON "LaserAttenuator_inputs" (inputs);

CREATE TABLE "LaserAttenuator_outputs" (
	"LaserAttenuator_name" TEXT,
	outputs VARCHAR(17),
	PRIMARY KEY ("LaserAttenuator_name", outputs),
	FOREIGN KEY("LaserAttenuator_name") REFERENCES "LaserAttenuator" (name)
);
CREATE INDEX "ix_LaserAttenuator_outputs_LaserAttenuator_name" ON "LaserAttenuator_outputs" ("LaserAttenuator_name");
CREATE INDEX "ix_LaserAttenuator_outputs_outputs" ON "LaserAttenuator_outputs" (outputs);

CREATE TABLE "LaserAttenuator_upstream" (
	"LaserAttenuator_name" TEXT,
	upstream_name TEXT,
	PRIMARY KEY ("LaserAttenuator_name", upstream_name),
	FOREIGN KEY("LaserAttenuator_name") REFERENCES "LaserAttenuator" (name),
	FOREIGN KEY(upstream_name) REFERENCES "AcceleratorElement" (name)
);
CREATE INDEX "ix_LaserAttenuator_upstream_LaserAttenuator_name" ON "LaserAttenuator_upstream" ("LaserAttenuator_name");
CREATE INDEX "ix_LaserAttenuator_upstream_upstream_name" ON "LaserAttenuator_upstream" (upstream_name);

CREATE TABLE "LaserAttenuator_downstream" (
	"LaserAttenuator_name" TEXT,
	downstream_name TEXT,
	PRIMARY KEY ("LaserAttenuator_name", downstream_name),
	FOREIGN KEY("LaserAttenuator_name") REFERENCES "LaserAttenuator" (name),
	FOREIGN KEY(downstream_name) REFERENCES "AcceleratorElement" (name)
);
CREATE INDEX "ix_LaserAttenuator_downstream_LaserAttenuator_name" ON "LaserAttenuator_downstream" ("LaserAttenuator_name");
CREATE INDEX "ix_LaserAttenuator_downstream_downstream_name" ON "LaserAttenuator_downstream" (downstream_name);

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

CREATE TABLE "Magnet" (
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
CREATE INDEX "ix_Magnet_name" ON "Magnet" (name);

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

CREATE TABLE "Dipole" (
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
	FOREIGN KEY(magnetic_id) REFERENCES "Dipole_Magnet" (id),
	FOREIGN KEY(degauss_id) REFERENCES "DegaussableElement" (id),
	FOREIGN KEY(physical_id) REFERENCES "PhysicalElement" (id),
	FOREIGN KEY(simulation_id) REFERENCES "MagnetSimulationElement" (id),
	FOREIGN KEY(electrical_id) REFERENCES "ElectricalElement" (id),
	FOREIGN KEY(manufacturer_id) REFERENCES "ManufacturerElement" (id),
	FOREIGN KEY(controls_id) REFERENCES "ControlsInformation" (id),
	FOREIGN KEY(reference_id) REFERENCES "ReferenceElement" (id)
);
CREATE INDEX "ix_Dipole_name" ON "Dipole" (name);

CREATE TABLE "Quadrupole" (
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
	FOREIGN KEY(magnetic_id) REFERENCES "Quadrupole_Magnet" (id),
	FOREIGN KEY(degauss_id) REFERENCES "DegaussableElement" (id),
	FOREIGN KEY(physical_id) REFERENCES "PhysicalElement" (id),
	FOREIGN KEY(simulation_id) REFERENCES "MagnetSimulationElement" (id),
	FOREIGN KEY(electrical_id) REFERENCES "ElectricalElement" (id),
	FOREIGN KEY(manufacturer_id) REFERENCES "ManufacturerElement" (id),
	FOREIGN KEY(controls_id) REFERENCES "ControlsInformation" (id),
	FOREIGN KEY(reference_id) REFERENCES "ReferenceElement" (id)
);
CREATE INDEX "ix_Quadrupole_name" ON "Quadrupole" (name);

CREATE TABLE "PID_alias" (
	"PID_name" TEXT,
	alias TEXT,
	PRIMARY KEY ("PID_name", alias),
	FOREIGN KEY("PID_name") REFERENCES "PID" (name)
);
CREATE INDEX "ix_PID_alias_PID_name" ON "PID_alias" ("PID_name");
CREATE INDEX "ix_PID_alias_alias" ON "PID_alias" (alias);

CREATE TABLE "PID_inputs" (
	"PID_name" TEXT,
	inputs VARCHAR(17),
	PRIMARY KEY ("PID_name", inputs),
	FOREIGN KEY("PID_name") REFERENCES "PID" (name)
);
CREATE INDEX "ix_PID_inputs_inputs" ON "PID_inputs" (inputs);
CREATE INDEX "ix_PID_inputs_PID_name" ON "PID_inputs" ("PID_name");

CREATE TABLE "PID_outputs" (
	"PID_name" TEXT,
	outputs VARCHAR(17),
	PRIMARY KEY ("PID_name", outputs),
	FOREIGN KEY("PID_name") REFERENCES "PID" (name)
);
CREATE INDEX "ix_PID_outputs_outputs" ON "PID_outputs" (outputs);
CREATE INDEX "ix_PID_outputs_PID_name" ON "PID_outputs" ("PID_name");

CREATE TABLE "PID_upstream" (
	"PID_name" TEXT,
	upstream_name TEXT,
	PRIMARY KEY ("PID_name", upstream_name),
	FOREIGN KEY("PID_name") REFERENCES "PID" (name),
	FOREIGN KEY(upstream_name) REFERENCES "AcceleratorElement" (name)
);
CREATE INDEX "ix_PID_upstream_PID_name" ON "PID_upstream" ("PID_name");
CREATE INDEX "ix_PID_upstream_upstream_name" ON "PID_upstream" (upstream_name);

CREATE TABLE "PID_downstream" (
	"PID_name" TEXT,
	downstream_name TEXT,
	PRIMARY KEY ("PID_name", downstream_name),
	FOREIGN KEY("PID_name") REFERENCES "PID" (name),
	FOREIGN KEY(downstream_name) REFERENCES "AcceleratorElement" (name)
);
CREATE INDEX "ix_PID_downstream_PID_name" ON "PID_downstream" ("PID_name");
CREATE INDEX "ix_PID_downstream_downstream_name" ON "PID_downstream" (downstream_name);

CREATE TABLE "LaserMirror_alias" (
	"LaserMirror_name" TEXT,
	alias TEXT,
	PRIMARY KEY ("LaserMirror_name", alias),
	FOREIGN KEY("LaserMirror_name") REFERENCES "LaserMirror" (name)
);
CREATE INDEX "ix_LaserMirror_alias_alias" ON "LaserMirror_alias" (alias);
CREATE INDEX "ix_LaserMirror_alias_LaserMirror_name" ON "LaserMirror_alias" ("LaserMirror_name");

CREATE TABLE "LaserMirror_inputs" (
	"LaserMirror_name" TEXT,
	inputs VARCHAR(17),
	PRIMARY KEY ("LaserMirror_name", inputs),
	FOREIGN KEY("LaserMirror_name") REFERENCES "LaserMirror" (name)
);
CREATE INDEX "ix_LaserMirror_inputs_LaserMirror_name" ON "LaserMirror_inputs" ("LaserMirror_name");
CREATE INDEX "ix_LaserMirror_inputs_inputs" ON "LaserMirror_inputs" (inputs);

CREATE TABLE "LaserMirror_outputs" (
	"LaserMirror_name" TEXT,
	outputs VARCHAR(17),
	PRIMARY KEY ("LaserMirror_name", outputs),
	FOREIGN KEY("LaserMirror_name") REFERENCES "LaserMirror" (name)
);
CREATE INDEX "ix_LaserMirror_outputs_outputs" ON "LaserMirror_outputs" (outputs);
CREATE INDEX "ix_LaserMirror_outputs_LaserMirror_name" ON "LaserMirror_outputs" ("LaserMirror_name");

CREATE TABLE "LaserMirror_upstream" (
	"LaserMirror_name" TEXT,
	upstream_name TEXT,
	PRIMARY KEY ("LaserMirror_name", upstream_name),
	FOREIGN KEY("LaserMirror_name") REFERENCES "LaserMirror" (name),
	FOREIGN KEY(upstream_name) REFERENCES "AcceleratorElement" (name)
);
CREATE INDEX "ix_LaserMirror_upstream_LaserMirror_name" ON "LaserMirror_upstream" ("LaserMirror_name");
CREATE INDEX "ix_LaserMirror_upstream_upstream_name" ON "LaserMirror_upstream" (upstream_name);

CREATE TABLE "LaserMirror_downstream" (
	"LaserMirror_name" TEXT,
	downstream_name TEXT,
	PRIMARY KEY ("LaserMirror_name", downstream_name),
	FOREIGN KEY("LaserMirror_name") REFERENCES "LaserMirror" (name),
	FOREIGN KEY(downstream_name) REFERENCES "AcceleratorElement" (name)
);
CREATE INDEX "ix_LaserMirror_downstream_LaserMirror_name" ON "LaserMirror_downstream" ("LaserMirror_name");
CREATE INDEX "ix_LaserMirror_downstream_downstream_name" ON "LaserMirror_downstream" (downstream_name);

CREATE TABLE "PhysicalAcceleratorElement_alias" (
	"PhysicalAcceleratorElement_name" TEXT,
	alias TEXT,
	PRIMARY KEY ("PhysicalAcceleratorElement_name", alias),
	FOREIGN KEY("PhysicalAcceleratorElement_name") REFERENCES "PhysicalAcceleratorElement" (name)
);
CREATE INDEX "ix_PhysicalAcceleratorElement_alias_PhysicalAcceleratorElement_name" ON "PhysicalAcceleratorElement_alias" ("PhysicalAcceleratorElement_name");
CREATE INDEX "ix_PhysicalAcceleratorElement_alias_alias" ON "PhysicalAcceleratorElement_alias" (alias);

CREATE TABLE "PhysicalAcceleratorElement_inputs" (
	"PhysicalAcceleratorElement_name" TEXT,
	inputs VARCHAR(17),
	PRIMARY KEY ("PhysicalAcceleratorElement_name", inputs),
	FOREIGN KEY("PhysicalAcceleratorElement_name") REFERENCES "PhysicalAcceleratorElement" (name)
);
CREATE INDEX "ix_PhysicalAcceleratorElement_inputs_PhysicalAcceleratorElement_name" ON "PhysicalAcceleratorElement_inputs" ("PhysicalAcceleratorElement_name");
CREATE INDEX "ix_PhysicalAcceleratorElement_inputs_inputs" ON "PhysicalAcceleratorElement_inputs" (inputs);

CREATE TABLE "PhysicalAcceleratorElement_outputs" (
	"PhysicalAcceleratorElement_name" TEXT,
	outputs VARCHAR(17),
	PRIMARY KEY ("PhysicalAcceleratorElement_name", outputs),
	FOREIGN KEY("PhysicalAcceleratorElement_name") REFERENCES "PhysicalAcceleratorElement" (name)
);
CREATE INDEX "ix_PhysicalAcceleratorElement_outputs_PhysicalAcceleratorElement_name" ON "PhysicalAcceleratorElement_outputs" ("PhysicalAcceleratorElement_name");
CREATE INDEX "ix_PhysicalAcceleratorElement_outputs_outputs" ON "PhysicalAcceleratorElement_outputs" (outputs);

CREATE TABLE "PhysicalAcceleratorElement_upstream" (
	"PhysicalAcceleratorElement_name" TEXT,
	upstream_name TEXT,
	PRIMARY KEY ("PhysicalAcceleratorElement_name", upstream_name),
	FOREIGN KEY("PhysicalAcceleratorElement_name") REFERENCES "PhysicalAcceleratorElement" (name),
	FOREIGN KEY(upstream_name) REFERENCES "AcceleratorElement" (name)
);
CREATE INDEX "ix_PhysicalAcceleratorElement_upstream_PhysicalAcceleratorElement_name" ON "PhysicalAcceleratorElement_upstream" ("PhysicalAcceleratorElement_name");
CREATE INDEX "ix_PhysicalAcceleratorElement_upstream_upstream_name" ON "PhysicalAcceleratorElement_upstream" (upstream_name);

CREATE TABLE "PhysicalAcceleratorElement_downstream" (
	"PhysicalAcceleratorElement_name" TEXT,
	downstream_name TEXT,
	PRIMARY KEY ("PhysicalAcceleratorElement_name", downstream_name),
	FOREIGN KEY("PhysicalAcceleratorElement_name") REFERENCES "PhysicalAcceleratorElement" (name),
	FOREIGN KEY(downstream_name) REFERENCES "AcceleratorElement" (name)
);
CREATE INDEX "ix_PhysicalAcceleratorElement_downstream_downstream_name" ON "PhysicalAcceleratorElement_downstream" (downstream_name);
CREATE INDEX "ix_PhysicalAcceleratorElement_downstream_PhysicalAcceleratorElement_name" ON "PhysicalAcceleratorElement_downstream" ("PhysicalAcceleratorElement_name");

CREATE TABLE "TwissMatch_alias" (
	"TwissMatch_name" TEXT,
	alias TEXT,
	PRIMARY KEY ("TwissMatch_name", alias),
	FOREIGN KEY("TwissMatch_name") REFERENCES "TwissMatch" (name)
);
CREATE INDEX "ix_TwissMatch_alias_alias" ON "TwissMatch_alias" (alias);
CREATE INDEX "ix_TwissMatch_alias_TwissMatch_name" ON "TwissMatch_alias" ("TwissMatch_name");

CREATE TABLE "TwissMatch_inputs" (
	"TwissMatch_name" TEXT,
	inputs VARCHAR(17),
	PRIMARY KEY ("TwissMatch_name", inputs),
	FOREIGN KEY("TwissMatch_name") REFERENCES "TwissMatch" (name)
);
CREATE INDEX "ix_TwissMatch_inputs_TwissMatch_name" ON "TwissMatch_inputs" ("TwissMatch_name");
CREATE INDEX "ix_TwissMatch_inputs_inputs" ON "TwissMatch_inputs" (inputs);

CREATE TABLE "TwissMatch_outputs" (
	"TwissMatch_name" TEXT,
	outputs VARCHAR(17),
	PRIMARY KEY ("TwissMatch_name", outputs),
	FOREIGN KEY("TwissMatch_name") REFERENCES "TwissMatch" (name)
);
CREATE INDEX "ix_TwissMatch_outputs_TwissMatch_name" ON "TwissMatch_outputs" ("TwissMatch_name");
CREATE INDEX "ix_TwissMatch_outputs_outputs" ON "TwissMatch_outputs" (outputs);

CREATE TABLE "TwissMatch_upstream" (
	"TwissMatch_name" TEXT,
	upstream_name TEXT,
	PRIMARY KEY ("TwissMatch_name", upstream_name),
	FOREIGN KEY("TwissMatch_name") REFERENCES "TwissMatch" (name),
	FOREIGN KEY(upstream_name) REFERENCES "AcceleratorElement" (name)
);
CREATE INDEX "ix_TwissMatch_upstream_upstream_name" ON "TwissMatch_upstream" (upstream_name);
CREATE INDEX "ix_TwissMatch_upstream_TwissMatch_name" ON "TwissMatch_upstream" ("TwissMatch_name");

CREATE TABLE "TwissMatch_downstream" (
	"TwissMatch_name" TEXT,
	downstream_name TEXT,
	PRIMARY KEY ("TwissMatch_name", downstream_name),
	FOREIGN KEY("TwissMatch_name") REFERENCES "TwissMatch" (name),
	FOREIGN KEY(downstream_name) REFERENCES "AcceleratorElement" (name)
);
CREATE INDEX "ix_TwissMatch_downstream_downstream_name" ON "TwissMatch_downstream" (downstream_name);
CREATE INDEX "ix_TwissMatch_downstream_TwissMatch_name" ON "TwissMatch_downstream" ("TwissMatch_name");

CREATE TABLE "Stage_alias" (
	"Stage_name" TEXT,
	alias TEXT,
	PRIMARY KEY ("Stage_name", alias),
	FOREIGN KEY("Stage_name") REFERENCES "Stage" (name)
);
CREATE INDEX "ix_Stage_alias_alias" ON "Stage_alias" (alias);
CREATE INDEX "ix_Stage_alias_Stage_name" ON "Stage_alias" ("Stage_name");

CREATE TABLE "Stage_inputs" (
	"Stage_name" TEXT,
	inputs VARCHAR(17),
	PRIMARY KEY ("Stage_name", inputs),
	FOREIGN KEY("Stage_name") REFERENCES "Stage" (name)
);
CREATE INDEX "ix_Stage_inputs_Stage_name" ON "Stage_inputs" ("Stage_name");
CREATE INDEX "ix_Stage_inputs_inputs" ON "Stage_inputs" (inputs);

CREATE TABLE "Stage_outputs" (
	"Stage_name" TEXT,
	outputs VARCHAR(17),
	PRIMARY KEY ("Stage_name", outputs),
	FOREIGN KEY("Stage_name") REFERENCES "Stage" (name)
);
CREATE INDEX "ix_Stage_outputs_Stage_name" ON "Stage_outputs" ("Stage_name");
CREATE INDEX "ix_Stage_outputs_outputs" ON "Stage_outputs" (outputs);

CREATE TABLE "Stage_upstream" (
	"Stage_name" TEXT,
	upstream_name TEXT,
	PRIMARY KEY ("Stage_name", upstream_name),
	FOREIGN KEY("Stage_name") REFERENCES "Stage" (name),
	FOREIGN KEY(upstream_name) REFERENCES "AcceleratorElement" (name)
);
CREATE INDEX "ix_Stage_upstream_upstream_name" ON "Stage_upstream" (upstream_name);
CREATE INDEX "ix_Stage_upstream_Stage_name" ON "Stage_upstream" ("Stage_name");

CREATE TABLE "Stage_downstream" (
	"Stage_name" TEXT,
	downstream_name TEXT,
	PRIMARY KEY ("Stage_name", downstream_name),
	FOREIGN KEY("Stage_name") REFERENCES "Stage" (name),
	FOREIGN KEY(downstream_name) REFERENCES "AcceleratorElement" (name)
);
CREATE INDEX "ix_Stage_downstream_downstream_name" ON "Stage_downstream" (downstream_name);
CREATE INDEX "ix_Stage_downstream_Stage_name" ON "Stage_downstream" ("Stage_name");

CREATE TABLE "VacuumGauge_alias" (
	"VacuumGauge_name" TEXT,
	alias TEXT,
	PRIMARY KEY ("VacuumGauge_name", alias),
	FOREIGN KEY("VacuumGauge_name") REFERENCES "VacuumGauge" (name)
);
CREATE INDEX "ix_VacuumGauge_alias_alias" ON "VacuumGauge_alias" (alias);
CREATE INDEX "ix_VacuumGauge_alias_VacuumGauge_name" ON "VacuumGauge_alias" ("VacuumGauge_name");

CREATE TABLE "VacuumGauge_inputs" (
	"VacuumGauge_name" TEXT,
	inputs VARCHAR(17),
	PRIMARY KEY ("VacuumGauge_name", inputs),
	FOREIGN KEY("VacuumGauge_name") REFERENCES "VacuumGauge" (name)
);
CREATE INDEX "ix_VacuumGauge_inputs_VacuumGauge_name" ON "VacuumGauge_inputs" ("VacuumGauge_name");
CREATE INDEX "ix_VacuumGauge_inputs_inputs" ON "VacuumGauge_inputs" (inputs);

CREATE TABLE "VacuumGauge_outputs" (
	"VacuumGauge_name" TEXT,
	outputs VARCHAR(17),
	PRIMARY KEY ("VacuumGauge_name", outputs),
	FOREIGN KEY("VacuumGauge_name") REFERENCES "VacuumGauge" (name)
);
CREATE INDEX "ix_VacuumGauge_outputs_outputs" ON "VacuumGauge_outputs" (outputs);
CREATE INDEX "ix_VacuumGauge_outputs_VacuumGauge_name" ON "VacuumGauge_outputs" ("VacuumGauge_name");

CREATE TABLE "VacuumGauge_upstream" (
	"VacuumGauge_name" TEXT,
	upstream_name TEXT,
	PRIMARY KEY ("VacuumGauge_name", upstream_name),
	FOREIGN KEY("VacuumGauge_name") REFERENCES "VacuumGauge" (name),
	FOREIGN KEY(upstream_name) REFERENCES "AcceleratorElement" (name)
);
CREATE INDEX "ix_VacuumGauge_upstream_upstream_name" ON "VacuumGauge_upstream" (upstream_name);
CREATE INDEX "ix_VacuumGauge_upstream_VacuumGauge_name" ON "VacuumGauge_upstream" ("VacuumGauge_name");

CREATE TABLE "VacuumGauge_downstream" (
	"VacuumGauge_name" TEXT,
	downstream_name TEXT,
	PRIMARY KEY ("VacuumGauge_name", downstream_name),
	FOREIGN KEY("VacuumGauge_name") REFERENCES "VacuumGauge" (name),
	FOREIGN KEY(downstream_name) REFERENCES "AcceleratorElement" (name)
);
CREATE INDEX "ix_VacuumGauge_downstream_VacuumGauge_name" ON "VacuumGauge_downstream" ("VacuumGauge_name");
CREATE INDEX "ix_VacuumGauge_downstream_downstream_name" ON "VacuumGauge_downstream" (downstream_name);

CREATE TABLE "Laser_alias" (
	"Laser_name" TEXT,
	alias TEXT,
	PRIMARY KEY ("Laser_name", alias),
	FOREIGN KEY("Laser_name") REFERENCES "Laser" (name)
);
CREATE INDEX "ix_Laser_alias_alias" ON "Laser_alias" (alias);
CREATE INDEX "ix_Laser_alias_Laser_name" ON "Laser_alias" ("Laser_name");

CREATE TABLE "Laser_inputs" (
	"Laser_name" TEXT,
	inputs VARCHAR(17),
	PRIMARY KEY ("Laser_name", inputs),
	FOREIGN KEY("Laser_name") REFERENCES "Laser" (name)
);
CREATE INDEX "ix_Laser_inputs_Laser_name" ON "Laser_inputs" ("Laser_name");
CREATE INDEX "ix_Laser_inputs_inputs" ON "Laser_inputs" (inputs);

CREATE TABLE "Laser_outputs" (
	"Laser_name" TEXT,
	outputs VARCHAR(17),
	PRIMARY KEY ("Laser_name", outputs),
	FOREIGN KEY("Laser_name") REFERENCES "Laser" (name)
);
CREATE INDEX "ix_Laser_outputs_outputs" ON "Laser_outputs" (outputs);
CREATE INDEX "ix_Laser_outputs_Laser_name" ON "Laser_outputs" ("Laser_name");

CREATE TABLE "Laser_upstream" (
	"Laser_name" TEXT,
	upstream_name TEXT,
	PRIMARY KEY ("Laser_name", upstream_name),
	FOREIGN KEY("Laser_name") REFERENCES "Laser" (name),
	FOREIGN KEY(upstream_name) REFERENCES "AcceleratorElement" (name)
);
CREATE INDEX "ix_Laser_upstream_upstream_name" ON "Laser_upstream" (upstream_name);
CREATE INDEX "ix_Laser_upstream_Laser_name" ON "Laser_upstream" ("Laser_name");

CREATE TABLE "Laser_downstream" (
	"Laser_name" TEXT,
	downstream_name TEXT,
	PRIMARY KEY ("Laser_name", downstream_name),
	FOREIGN KEY("Laser_name") REFERENCES "Laser" (name),
	FOREIGN KEY(downstream_name) REFERENCES "AcceleratorElement" (name)
);
CREATE INDEX "ix_Laser_downstream_downstream_name" ON "Laser_downstream" (downstream_name);
CREATE INDEX "ix_Laser_downstream_Laser_name" ON "Laser_downstream" ("Laser_name");

CREATE TABLE "Shutter_alias" (
	"Shutter_name" TEXT,
	alias TEXT,
	PRIMARY KEY ("Shutter_name", alias),
	FOREIGN KEY("Shutter_name") REFERENCES "Shutter" (name)
);
CREATE INDEX "ix_Shutter_alias_alias" ON "Shutter_alias" (alias);
CREATE INDEX "ix_Shutter_alias_Shutter_name" ON "Shutter_alias" ("Shutter_name");

CREATE TABLE "Shutter_inputs" (
	"Shutter_name" TEXT,
	inputs VARCHAR(17),
	PRIMARY KEY ("Shutter_name", inputs),
	FOREIGN KEY("Shutter_name") REFERENCES "Shutter" (name)
);
CREATE INDEX "ix_Shutter_inputs_Shutter_name" ON "Shutter_inputs" ("Shutter_name");
CREATE INDEX "ix_Shutter_inputs_inputs" ON "Shutter_inputs" (inputs);

CREATE TABLE "Shutter_outputs" (
	"Shutter_name" TEXT,
	outputs VARCHAR(17),
	PRIMARY KEY ("Shutter_name", outputs),
	FOREIGN KEY("Shutter_name") REFERENCES "Shutter" (name)
);
CREATE INDEX "ix_Shutter_outputs_Shutter_name" ON "Shutter_outputs" ("Shutter_name");
CREATE INDEX "ix_Shutter_outputs_outputs" ON "Shutter_outputs" (outputs);

CREATE TABLE "Shutter_upstream" (
	"Shutter_name" TEXT,
	upstream_name TEXT,
	PRIMARY KEY ("Shutter_name", upstream_name),
	FOREIGN KEY("Shutter_name") REFERENCES "Shutter" (name),
	FOREIGN KEY(upstream_name) REFERENCES "AcceleratorElement" (name)
);
CREATE INDEX "ix_Shutter_upstream_upstream_name" ON "Shutter_upstream" (upstream_name);
CREATE INDEX "ix_Shutter_upstream_Shutter_name" ON "Shutter_upstream" ("Shutter_name");

CREATE TABLE "Shutter_downstream" (
	"Shutter_name" TEXT,
	downstream_name TEXT,
	PRIMARY KEY ("Shutter_name", downstream_name),
	FOREIGN KEY("Shutter_name") REFERENCES "Shutter" (name),
	FOREIGN KEY(downstream_name) REFERENCES "AcceleratorElement" (name)
);
CREATE INDEX "ix_Shutter_downstream_downstream_name" ON "Shutter_downstream" (downstream_name);
CREATE INDEX "ix_Shutter_downstream_Shutter_name" ON "Shutter_downstream" ("Shutter_name");

CREATE TABLE "Valve_alias" (
	"Valve_name" TEXT,
	alias TEXT,
	PRIMARY KEY ("Valve_name", alias),
	FOREIGN KEY("Valve_name") REFERENCES "Valve" (name)
);
CREATE INDEX "ix_Valve_alias_alias" ON "Valve_alias" (alias);
CREATE INDEX "ix_Valve_alias_Valve_name" ON "Valve_alias" ("Valve_name");

CREATE TABLE "Valve_inputs" (
	"Valve_name" TEXT,
	inputs VARCHAR(17),
	PRIMARY KEY ("Valve_name", inputs),
	FOREIGN KEY("Valve_name") REFERENCES "Valve" (name)
);
CREATE INDEX "ix_Valve_inputs_Valve_name" ON "Valve_inputs" ("Valve_name");
CREATE INDEX "ix_Valve_inputs_inputs" ON "Valve_inputs" (inputs);

CREATE TABLE "Valve_outputs" (
	"Valve_name" TEXT,
	outputs VARCHAR(17),
	PRIMARY KEY ("Valve_name", outputs),
	FOREIGN KEY("Valve_name") REFERENCES "Valve" (name)
);
CREATE INDEX "ix_Valve_outputs_Valve_name" ON "Valve_outputs" ("Valve_name");
CREATE INDEX "ix_Valve_outputs_outputs" ON "Valve_outputs" (outputs);

CREATE TABLE "Valve_upstream" (
	"Valve_name" TEXT,
	upstream_name TEXT,
	PRIMARY KEY ("Valve_name", upstream_name),
	FOREIGN KEY("Valve_name") REFERENCES "Valve" (name),
	FOREIGN KEY(upstream_name) REFERENCES "AcceleratorElement" (name)
);
CREATE INDEX "ix_Valve_upstream_upstream_name" ON "Valve_upstream" (upstream_name);
CREATE INDEX "ix_Valve_upstream_Valve_name" ON "Valve_upstream" ("Valve_name");

CREATE TABLE "Valve_downstream" (
	"Valve_name" TEXT,
	downstream_name TEXT,
	PRIMARY KEY ("Valve_name", downstream_name),
	FOREIGN KEY("Valve_name") REFERENCES "Valve" (name),
	FOREIGN KEY(downstream_name) REFERENCES "AcceleratorElement" (name)
);
CREATE INDEX "ix_Valve_downstream_downstream_name" ON "Valve_downstream" (downstream_name);
CREATE INDEX "ix_Valve_downstream_Valve_name" ON "Valve_downstream" ("Valve_name");

CREATE TABLE "Marker_alias" (
	"Marker_name" TEXT,
	alias TEXT,
	PRIMARY KEY ("Marker_name", alias),
	FOREIGN KEY("Marker_name") REFERENCES "Marker" (name)
);
CREATE INDEX "ix_Marker_alias_alias" ON "Marker_alias" (alias);
CREATE INDEX "ix_Marker_alias_Marker_name" ON "Marker_alias" ("Marker_name");

CREATE TABLE "Marker_inputs" (
	"Marker_name" TEXT,
	inputs VARCHAR(17),
	PRIMARY KEY ("Marker_name", inputs),
	FOREIGN KEY("Marker_name") REFERENCES "Marker" (name)
);
CREATE INDEX "ix_Marker_inputs_Marker_name" ON "Marker_inputs" ("Marker_name");
CREATE INDEX "ix_Marker_inputs_inputs" ON "Marker_inputs" (inputs);

CREATE TABLE "Marker_outputs" (
	"Marker_name" TEXT,
	outputs VARCHAR(17),
	PRIMARY KEY ("Marker_name", outputs),
	FOREIGN KEY("Marker_name") REFERENCES "Marker" (name)
);
CREATE INDEX "ix_Marker_outputs_outputs" ON "Marker_outputs" (outputs);
CREATE INDEX "ix_Marker_outputs_Marker_name" ON "Marker_outputs" ("Marker_name");

CREATE TABLE "Marker_upstream" (
	"Marker_name" TEXT,
	upstream_name TEXT,
	PRIMARY KEY ("Marker_name", upstream_name),
	FOREIGN KEY("Marker_name") REFERENCES "Marker" (name),
	FOREIGN KEY(upstream_name) REFERENCES "AcceleratorElement" (name)
);
CREATE INDEX "ix_Marker_upstream_Marker_name" ON "Marker_upstream" ("Marker_name");
CREATE INDEX "ix_Marker_upstream_upstream_name" ON "Marker_upstream" (upstream_name);

CREATE TABLE "Marker_downstream" (
	"Marker_name" TEXT,
	downstream_name TEXT,
	PRIMARY KEY ("Marker_name", downstream_name),
	FOREIGN KEY("Marker_name") REFERENCES "Marker" (name),
	FOREIGN KEY(downstream_name) REFERENCES "AcceleratorElement" (name)
);
CREATE INDEX "ix_Marker_downstream_downstream_name" ON "Marker_downstream" (downstream_name);
CREATE INDEX "ix_Marker_downstream_Marker_name" ON "Marker_downstream" ("Marker_name");

CREATE TABLE "Aperture_alias" (
	"Aperture_name" TEXT,
	alias TEXT,
	PRIMARY KEY ("Aperture_name", alias),
	FOREIGN KEY("Aperture_name") REFERENCES "Aperture" (name)
);
CREATE INDEX "ix_Aperture_alias_alias" ON "Aperture_alias" (alias);
CREATE INDEX "ix_Aperture_alias_Aperture_name" ON "Aperture_alias" ("Aperture_name");

CREATE TABLE "Aperture_inputs" (
	"Aperture_name" TEXT,
	inputs VARCHAR(17),
	PRIMARY KEY ("Aperture_name", inputs),
	FOREIGN KEY("Aperture_name") REFERENCES "Aperture" (name)
);
CREATE INDEX "ix_Aperture_inputs_Aperture_name" ON "Aperture_inputs" ("Aperture_name");
CREATE INDEX "ix_Aperture_inputs_inputs" ON "Aperture_inputs" (inputs);

CREATE TABLE "Aperture_outputs" (
	"Aperture_name" TEXT,
	outputs VARCHAR(17),
	PRIMARY KEY ("Aperture_name", outputs),
	FOREIGN KEY("Aperture_name") REFERENCES "Aperture" (name)
);
CREATE INDEX "ix_Aperture_outputs_Aperture_name" ON "Aperture_outputs" ("Aperture_name");
CREATE INDEX "ix_Aperture_outputs_outputs" ON "Aperture_outputs" (outputs);

CREATE TABLE "Aperture_upstream" (
	"Aperture_name" TEXT,
	upstream_name TEXT,
	PRIMARY KEY ("Aperture_name", upstream_name),
	FOREIGN KEY("Aperture_name") REFERENCES "Aperture" (name),
	FOREIGN KEY(upstream_name) REFERENCES "AcceleratorElement" (name)
);
CREATE INDEX "ix_Aperture_upstream_upstream_name" ON "Aperture_upstream" (upstream_name);
CREATE INDEX "ix_Aperture_upstream_Aperture_name" ON "Aperture_upstream" ("Aperture_name");

CREATE TABLE "Aperture_downstream" (
	"Aperture_name" TEXT,
	downstream_name TEXT,
	PRIMARY KEY ("Aperture_name", downstream_name),
	FOREIGN KEY("Aperture_name") REFERENCES "Aperture" (name),
	FOREIGN KEY(downstream_name) REFERENCES "AcceleratorElement" (name)
);
CREATE INDEX "ix_Aperture_downstream_downstream_name" ON "Aperture_downstream" (downstream_name);
CREATE INDEX "ix_Aperture_downstream_Aperture_name" ON "Aperture_downstream" ("Aperture_name");

CREATE TABLE "Collimator_alias" (
	"Collimator_name" TEXT,
	alias TEXT,
	PRIMARY KEY ("Collimator_name", alias),
	FOREIGN KEY("Collimator_name") REFERENCES "Collimator" (name)
);
CREATE INDEX "ix_Collimator_alias_alias" ON "Collimator_alias" (alias);
CREATE INDEX "ix_Collimator_alias_Collimator_name" ON "Collimator_alias" ("Collimator_name");

CREATE TABLE "Collimator_inputs" (
	"Collimator_name" TEXT,
	inputs VARCHAR(17),
	PRIMARY KEY ("Collimator_name", inputs),
	FOREIGN KEY("Collimator_name") REFERENCES "Collimator" (name)
);
CREATE INDEX "ix_Collimator_inputs_inputs" ON "Collimator_inputs" (inputs);
CREATE INDEX "ix_Collimator_inputs_Collimator_name" ON "Collimator_inputs" ("Collimator_name");

CREATE TABLE "Collimator_outputs" (
	"Collimator_name" TEXT,
	outputs VARCHAR(17),
	PRIMARY KEY ("Collimator_name", outputs),
	FOREIGN KEY("Collimator_name") REFERENCES "Collimator" (name)
);
CREATE INDEX "ix_Collimator_outputs_Collimator_name" ON "Collimator_outputs" ("Collimator_name");
CREATE INDEX "ix_Collimator_outputs_outputs" ON "Collimator_outputs" (outputs);

CREATE TABLE "Collimator_upstream" (
	"Collimator_name" TEXT,
	upstream_name TEXT,
	PRIMARY KEY ("Collimator_name", upstream_name),
	FOREIGN KEY("Collimator_name") REFERENCES "Collimator" (name),
	FOREIGN KEY(upstream_name) REFERENCES "AcceleratorElement" (name)
);
CREATE INDEX "ix_Collimator_upstream_upstream_name" ON "Collimator_upstream" (upstream_name);
CREATE INDEX "ix_Collimator_upstream_Collimator_name" ON "Collimator_upstream" ("Collimator_name");

CREATE TABLE "Collimator_downstream" (
	"Collimator_name" TEXT,
	downstream_name TEXT,
	PRIMARY KEY ("Collimator_name", downstream_name),
	FOREIGN KEY("Collimator_name") REFERENCES "Collimator" (name),
	FOREIGN KEY(downstream_name) REFERENCES "AcceleratorElement" (name)
);
CREATE INDEX "ix_Collimator_downstream_downstream_name" ON "Collimator_downstream" (downstream_name);
CREATE INDEX "ix_Collimator_downstream_Collimator_name" ON "Collimator_downstream" ("Collimator_name");

CREATE TABLE "Drift_alias" (
	"Drift_name" TEXT,
	alias TEXT,
	PRIMARY KEY ("Drift_name", alias),
	FOREIGN KEY("Drift_name") REFERENCES "Drift" (name)
);
CREATE INDEX "ix_Drift_alias_Drift_name" ON "Drift_alias" ("Drift_name");
CREATE INDEX "ix_Drift_alias_alias" ON "Drift_alias" (alias);

CREATE TABLE "Drift_inputs" (
	"Drift_name" TEXT,
	inputs VARCHAR(17),
	PRIMARY KEY ("Drift_name", inputs),
	FOREIGN KEY("Drift_name") REFERENCES "Drift" (name)
);
CREATE INDEX "ix_Drift_inputs_inputs" ON "Drift_inputs" (inputs);
CREATE INDEX "ix_Drift_inputs_Drift_name" ON "Drift_inputs" ("Drift_name");

CREATE TABLE "Drift_outputs" (
	"Drift_name" TEXT,
	outputs VARCHAR(17),
	PRIMARY KEY ("Drift_name", outputs),
	FOREIGN KEY("Drift_name") REFERENCES "Drift" (name)
);
CREATE INDEX "ix_Drift_outputs_outputs" ON "Drift_outputs" (outputs);
CREATE INDEX "ix_Drift_outputs_Drift_name" ON "Drift_outputs" ("Drift_name");

CREATE TABLE "Drift_upstream" (
	"Drift_name" TEXT,
	upstream_name TEXT,
	PRIMARY KEY ("Drift_name", upstream_name),
	FOREIGN KEY("Drift_name") REFERENCES "Drift" (name),
	FOREIGN KEY(upstream_name) REFERENCES "AcceleratorElement" (name)
);
CREATE INDEX "ix_Drift_upstream_Drift_name" ON "Drift_upstream" ("Drift_name");
CREATE INDEX "ix_Drift_upstream_upstream_name" ON "Drift_upstream" (upstream_name);

CREATE TABLE "Drift_downstream" (
	"Drift_name" TEXT,
	downstream_name TEXT,
	PRIMARY KEY ("Drift_name", downstream_name),
	FOREIGN KEY("Drift_name") REFERENCES "Drift" (name),
	FOREIGN KEY(downstream_name) REFERENCES "AcceleratorElement" (name)
);
CREATE INDEX "ix_Drift_downstream_Drift_name" ON "Drift_downstream" ("Drift_name");
CREATE INDEX "ix_Drift_downstream_downstream_name" ON "Drift_downstream" (downstream_name);

CREATE TABLE "Magnet_alias" (
	"Magnet_name" TEXT,
	alias TEXT,
	PRIMARY KEY ("Magnet_name", alias),
	FOREIGN KEY("Magnet_name") REFERENCES "Magnet" (name)
);
CREATE INDEX "ix_Magnet_alias_alias" ON "Magnet_alias" (alias);
CREATE INDEX "ix_Magnet_alias_Magnet_name" ON "Magnet_alias" ("Magnet_name");

CREATE TABLE "Magnet_inputs" (
	"Magnet_name" TEXT,
	inputs VARCHAR(17),
	PRIMARY KEY ("Magnet_name", inputs),
	FOREIGN KEY("Magnet_name") REFERENCES "Magnet" (name)
);
CREATE INDEX "ix_Magnet_inputs_Magnet_name" ON "Magnet_inputs" ("Magnet_name");
CREATE INDEX "ix_Magnet_inputs_inputs" ON "Magnet_inputs" (inputs);

CREATE TABLE "Magnet_outputs" (
	"Magnet_name" TEXT,
	outputs VARCHAR(17),
	PRIMARY KEY ("Magnet_name", outputs),
	FOREIGN KEY("Magnet_name") REFERENCES "Magnet" (name)
);
CREATE INDEX "ix_Magnet_outputs_Magnet_name" ON "Magnet_outputs" ("Magnet_name");
CREATE INDEX "ix_Magnet_outputs_outputs" ON "Magnet_outputs" (outputs);

CREATE TABLE "Magnet_upstream" (
	"Magnet_name" TEXT,
	upstream_name TEXT,
	PRIMARY KEY ("Magnet_name", upstream_name),
	FOREIGN KEY("Magnet_name") REFERENCES "Magnet" (name),
	FOREIGN KEY(upstream_name) REFERENCES "AcceleratorElement" (name)
);
CREATE INDEX "ix_Magnet_upstream_upstream_name" ON "Magnet_upstream" (upstream_name);
CREATE INDEX "ix_Magnet_upstream_Magnet_name" ON "Magnet_upstream" ("Magnet_name");

CREATE TABLE "Magnet_downstream" (
	"Magnet_name" TEXT,
	downstream_name TEXT,
	PRIMARY KEY ("Magnet_name", downstream_name),
	FOREIGN KEY("Magnet_name") REFERENCES "Magnet" (name),
	FOREIGN KEY(downstream_name) REFERENCES "AcceleratorElement" (name)
);
CREATE INDEX "ix_Magnet_downstream_downstream_name" ON "Magnet_downstream" (downstream_name);
CREATE INDEX "ix_Magnet_downstream_Magnet_name" ON "Magnet_downstream" ("Magnet_name");

CREATE TABLE "RFCavity_alias" (
	"RFCavity_name" TEXT,
	alias TEXT,
	PRIMARY KEY ("RFCavity_name", alias),
	FOREIGN KEY("RFCavity_name") REFERENCES "RFCavity" (name)
);
CREATE INDEX "ix_RFCavity_alias_RFCavity_name" ON "RFCavity_alias" ("RFCavity_name");
CREATE INDEX "ix_RFCavity_alias_alias" ON "RFCavity_alias" (alias);

CREATE TABLE "RFCavity_inputs" (
	"RFCavity_name" TEXT,
	inputs VARCHAR(17),
	PRIMARY KEY ("RFCavity_name", inputs),
	FOREIGN KEY("RFCavity_name") REFERENCES "RFCavity" (name)
);
CREATE INDEX "ix_RFCavity_inputs_inputs" ON "RFCavity_inputs" (inputs);
CREATE INDEX "ix_RFCavity_inputs_RFCavity_name" ON "RFCavity_inputs" ("RFCavity_name");

CREATE TABLE "RFCavity_outputs" (
	"RFCavity_name" TEXT,
	outputs VARCHAR(17),
	PRIMARY KEY ("RFCavity_name", outputs),
	FOREIGN KEY("RFCavity_name") REFERENCES "RFCavity" (name)
);
CREATE INDEX "ix_RFCavity_outputs_outputs" ON "RFCavity_outputs" (outputs);
CREATE INDEX "ix_RFCavity_outputs_RFCavity_name" ON "RFCavity_outputs" ("RFCavity_name");

CREATE TABLE "RFCavity_upstream" (
	"RFCavity_name" TEXT,
	upstream_name TEXT,
	PRIMARY KEY ("RFCavity_name", upstream_name),
	FOREIGN KEY("RFCavity_name") REFERENCES "RFCavity" (name),
	FOREIGN KEY(upstream_name) REFERENCES "AcceleratorElement" (name)
);
CREATE INDEX "ix_RFCavity_upstream_RFCavity_name" ON "RFCavity_upstream" ("RFCavity_name");
CREATE INDEX "ix_RFCavity_upstream_upstream_name" ON "RFCavity_upstream" (upstream_name);

CREATE TABLE "RFCavity_downstream" (
	"RFCavity_name" TEXT,
	downstream_name TEXT,
	PRIMARY KEY ("RFCavity_name", downstream_name),
	FOREIGN KEY("RFCavity_name") REFERENCES "RFCavity" (name),
	FOREIGN KEY(downstream_name) REFERENCES "AcceleratorElement" (name)
);
CREATE INDEX "ix_RFCavity_downstream_downstream_name" ON "RFCavity_downstream" (downstream_name);
CREATE INDEX "ix_RFCavity_downstream_RFCavity_name" ON "RFCavity_downstream" ("RFCavity_name");

CREATE TABLE "RFDeflectingCavity_alias" (
	"RFDeflectingCavity_name" TEXT,
	alias TEXT,
	PRIMARY KEY ("RFDeflectingCavity_name", alias),
	FOREIGN KEY("RFDeflectingCavity_name") REFERENCES "RFDeflectingCavity" (name)
);
CREATE INDEX "ix_RFDeflectingCavity_alias_RFDeflectingCavity_name" ON "RFDeflectingCavity_alias" ("RFDeflectingCavity_name");
CREATE INDEX "ix_RFDeflectingCavity_alias_alias" ON "RFDeflectingCavity_alias" (alias);

CREATE TABLE "RFDeflectingCavity_inputs" (
	"RFDeflectingCavity_name" TEXT,
	inputs VARCHAR(17),
	PRIMARY KEY ("RFDeflectingCavity_name", inputs),
	FOREIGN KEY("RFDeflectingCavity_name") REFERENCES "RFDeflectingCavity" (name)
);
CREATE INDEX "ix_RFDeflectingCavity_inputs_inputs" ON "RFDeflectingCavity_inputs" (inputs);
CREATE INDEX "ix_RFDeflectingCavity_inputs_RFDeflectingCavity_name" ON "RFDeflectingCavity_inputs" ("RFDeflectingCavity_name");

CREATE TABLE "RFDeflectingCavity_outputs" (
	"RFDeflectingCavity_name" TEXT,
	outputs VARCHAR(17),
	PRIMARY KEY ("RFDeflectingCavity_name", outputs),
	FOREIGN KEY("RFDeflectingCavity_name") REFERENCES "RFDeflectingCavity" (name)
);
CREATE INDEX "ix_RFDeflectingCavity_outputs_outputs" ON "RFDeflectingCavity_outputs" (outputs);
CREATE INDEX "ix_RFDeflectingCavity_outputs_RFDeflectingCavity_name" ON "RFDeflectingCavity_outputs" ("RFDeflectingCavity_name");

CREATE TABLE "RFDeflectingCavity_upstream" (
	"RFDeflectingCavity_name" TEXT,
	upstream_name TEXT,
	PRIMARY KEY ("RFDeflectingCavity_name", upstream_name),
	FOREIGN KEY("RFDeflectingCavity_name") REFERENCES "RFDeflectingCavity" (name),
	FOREIGN KEY(upstream_name) REFERENCES "AcceleratorElement" (name)
);
CREATE INDEX "ix_RFDeflectingCavity_upstream_RFDeflectingCavity_name" ON "RFDeflectingCavity_upstream" ("RFDeflectingCavity_name");
CREATE INDEX "ix_RFDeflectingCavity_upstream_upstream_name" ON "RFDeflectingCavity_upstream" (upstream_name);

CREATE TABLE "RFDeflectingCavity_downstream" (
	"RFDeflectingCavity_name" TEXT,
	downstream_name TEXT,
	PRIMARY KEY ("RFDeflectingCavity_name", downstream_name),
	FOREIGN KEY("RFDeflectingCavity_name") REFERENCES "RFDeflectingCavity" (name),
	FOREIGN KEY(downstream_name) REFERENCES "AcceleratorElement" (name)
);
CREATE INDEX "ix_RFDeflectingCavity_downstream_downstream_name" ON "RFDeflectingCavity_downstream" (downstream_name);
CREATE INDEX "ix_RFDeflectingCavity_downstream_RFDeflectingCavity_name" ON "RFDeflectingCavity_downstream" ("RFDeflectingCavity_name");

CREATE TABLE "Wakefield_alias" (
	"Wakefield_name" TEXT,
	alias TEXT,
	PRIMARY KEY ("Wakefield_name", alias),
	FOREIGN KEY("Wakefield_name") REFERENCES "Wakefield" (name)
);
CREATE INDEX "ix_Wakefield_alias_Wakefield_name" ON "Wakefield_alias" ("Wakefield_name");
CREATE INDEX "ix_Wakefield_alias_alias" ON "Wakefield_alias" (alias);

CREATE TABLE "Wakefield_inputs" (
	"Wakefield_name" TEXT,
	inputs VARCHAR(17),
	PRIMARY KEY ("Wakefield_name", inputs),
	FOREIGN KEY("Wakefield_name") REFERENCES "Wakefield" (name)
);
CREATE INDEX "ix_Wakefield_inputs_inputs" ON "Wakefield_inputs" (inputs);
CREATE INDEX "ix_Wakefield_inputs_Wakefield_name" ON "Wakefield_inputs" ("Wakefield_name");

CREATE TABLE "Wakefield_outputs" (
	"Wakefield_name" TEXT,
	outputs VARCHAR(17),
	PRIMARY KEY ("Wakefield_name", outputs),
	FOREIGN KEY("Wakefield_name") REFERENCES "Wakefield" (name)
);
CREATE INDEX "ix_Wakefield_outputs_outputs" ON "Wakefield_outputs" (outputs);
CREATE INDEX "ix_Wakefield_outputs_Wakefield_name" ON "Wakefield_outputs" ("Wakefield_name");

CREATE TABLE "Wakefield_upstream" (
	"Wakefield_name" TEXT,
	upstream_name TEXT,
	PRIMARY KEY ("Wakefield_name", upstream_name),
	FOREIGN KEY("Wakefield_name") REFERENCES "Wakefield" (name),
	FOREIGN KEY(upstream_name) REFERENCES "AcceleratorElement" (name)
);
CREATE INDEX "ix_Wakefield_upstream_Wakefield_name" ON "Wakefield_upstream" ("Wakefield_name");
CREATE INDEX "ix_Wakefield_upstream_upstream_name" ON "Wakefield_upstream" (upstream_name);

CREATE TABLE "Wakefield_downstream" (
	"Wakefield_name" TEXT,
	downstream_name TEXT,
	PRIMARY KEY ("Wakefield_name", downstream_name),
	FOREIGN KEY("Wakefield_name") REFERENCES "Wakefield" (name),
	FOREIGN KEY(downstream_name) REFERENCES "AcceleratorElement" (name)
);
CREATE INDEX "ix_Wakefield_downstream_downstream_name" ON "Wakefield_downstream" (downstream_name);
CREATE INDEX "ix_Wakefield_downstream_Wakefield_name" ON "Wakefield_downstream" ("Wakefield_name");

CREATE TABLE "LowLevelRF_alias" (
	"LowLevelRF_name" TEXT,
	alias TEXT,
	PRIMARY KEY ("LowLevelRF_name", alias),
	FOREIGN KEY("LowLevelRF_name") REFERENCES "LowLevelRF" (name)
);
CREATE INDEX "ix_LowLevelRF_alias_LowLevelRF_name" ON "LowLevelRF_alias" ("LowLevelRF_name");
CREATE INDEX "ix_LowLevelRF_alias_alias" ON "LowLevelRF_alias" (alias);

CREATE TABLE "LowLevelRF_inputs" (
	"LowLevelRF_name" TEXT,
	inputs VARCHAR(17),
	PRIMARY KEY ("LowLevelRF_name", inputs),
	FOREIGN KEY("LowLevelRF_name") REFERENCES "LowLevelRF" (name)
);
CREATE INDEX "ix_LowLevelRF_inputs_LowLevelRF_name" ON "LowLevelRF_inputs" ("LowLevelRF_name");
CREATE INDEX "ix_LowLevelRF_inputs_inputs" ON "LowLevelRF_inputs" (inputs);

CREATE TABLE "LowLevelRF_outputs" (
	"LowLevelRF_name" TEXT,
	outputs VARCHAR(17),
	PRIMARY KEY ("LowLevelRF_name", outputs),
	FOREIGN KEY("LowLevelRF_name") REFERENCES "LowLevelRF" (name)
);
CREATE INDEX "ix_LowLevelRF_outputs_outputs" ON "LowLevelRF_outputs" (outputs);
CREATE INDEX "ix_LowLevelRF_outputs_LowLevelRF_name" ON "LowLevelRF_outputs" ("LowLevelRF_name");

CREATE TABLE "LowLevelRF_upstream" (
	"LowLevelRF_name" TEXT,
	upstream_name TEXT,
	PRIMARY KEY ("LowLevelRF_name", upstream_name),
	FOREIGN KEY("LowLevelRF_name") REFERENCES "LowLevelRF" (name),
	FOREIGN KEY(upstream_name) REFERENCES "AcceleratorElement" (name)
);
CREATE INDEX "ix_LowLevelRF_upstream_upstream_name" ON "LowLevelRF_upstream" (upstream_name);
CREATE INDEX "ix_LowLevelRF_upstream_LowLevelRF_name" ON "LowLevelRF_upstream" ("LowLevelRF_name");

CREATE TABLE "LowLevelRF_downstream" (
	"LowLevelRF_name" TEXT,
	downstream_name TEXT,
	PRIMARY KEY ("LowLevelRF_name", downstream_name),
	FOREIGN KEY("LowLevelRF_name") REFERENCES "LowLevelRF" (name),
	FOREIGN KEY(downstream_name) REFERENCES "AcceleratorElement" (name)
);
CREATE INDEX "ix_LowLevelRF_downstream_LowLevelRF_name" ON "LowLevelRF_downstream" ("LowLevelRF_name");
CREATE INDEX "ix_LowLevelRF_downstream_downstream_name" ON "LowLevelRF_downstream" (downstream_name);

CREATE TABLE "Diagnostic_alias" (
	"Diagnostic_name" TEXT,
	alias TEXT,
	PRIMARY KEY ("Diagnostic_name", alias),
	FOREIGN KEY("Diagnostic_name") REFERENCES "Diagnostic" (name)
);
CREATE INDEX "ix_Diagnostic_alias_alias" ON "Diagnostic_alias" (alias);
CREATE INDEX "ix_Diagnostic_alias_Diagnostic_name" ON "Diagnostic_alias" ("Diagnostic_name");

CREATE TABLE "Diagnostic_inputs" (
	"Diagnostic_name" TEXT,
	inputs VARCHAR(17),
	PRIMARY KEY ("Diagnostic_name", inputs),
	FOREIGN KEY("Diagnostic_name") REFERENCES "Diagnostic" (name)
);
CREATE INDEX "ix_Diagnostic_inputs_Diagnostic_name" ON "Diagnostic_inputs" ("Diagnostic_name");
CREATE INDEX "ix_Diagnostic_inputs_inputs" ON "Diagnostic_inputs" (inputs);

CREATE TABLE "Diagnostic_outputs" (
	"Diagnostic_name" TEXT,
	outputs VARCHAR(17),
	PRIMARY KEY ("Diagnostic_name", outputs),
	FOREIGN KEY("Diagnostic_name") REFERENCES "Diagnostic" (name)
);
CREATE INDEX "ix_Diagnostic_outputs_outputs" ON "Diagnostic_outputs" (outputs);
CREATE INDEX "ix_Diagnostic_outputs_Diagnostic_name" ON "Diagnostic_outputs" ("Diagnostic_name");

CREATE TABLE "Diagnostic_upstream" (
	"Diagnostic_name" TEXT,
	upstream_name TEXT,
	PRIMARY KEY ("Diagnostic_name", upstream_name),
	FOREIGN KEY("Diagnostic_name") REFERENCES "Diagnostic" (name),
	FOREIGN KEY(upstream_name) REFERENCES "AcceleratorElement" (name)
);
CREATE INDEX "ix_Diagnostic_upstream_Diagnostic_name" ON "Diagnostic_upstream" ("Diagnostic_name");
CREATE INDEX "ix_Diagnostic_upstream_upstream_name" ON "Diagnostic_upstream" (upstream_name);

CREATE TABLE "Diagnostic_downstream" (
	"Diagnostic_name" TEXT,
	downstream_name TEXT,
	PRIMARY KEY ("Diagnostic_name", downstream_name),
	FOREIGN KEY("Diagnostic_name") REFERENCES "Diagnostic" (name),
	FOREIGN KEY(downstream_name) REFERENCES "AcceleratorElement" (name)
);
CREATE INDEX "ix_Diagnostic_downstream_downstream_name" ON "Diagnostic_downstream" (downstream_name);
CREATE INDEX "ix_Diagnostic_downstream_Diagnostic_name" ON "Diagnostic_downstream" ("Diagnostic_name");

CREATE TABLE "BeamPositionMonitor_alias" (
	"BeamPositionMonitor_name" TEXT,
	alias TEXT,
	PRIMARY KEY ("BeamPositionMonitor_name", alias),
	FOREIGN KEY("BeamPositionMonitor_name") REFERENCES "BeamPositionMonitor" (name)
);
CREATE INDEX "ix_BeamPositionMonitor_alias_BeamPositionMonitor_name" ON "BeamPositionMonitor_alias" ("BeamPositionMonitor_name");
CREATE INDEX "ix_BeamPositionMonitor_alias_alias" ON "BeamPositionMonitor_alias" (alias);

CREATE TABLE "BeamPositionMonitor_inputs" (
	"BeamPositionMonitor_name" TEXT,
	inputs VARCHAR(17),
	PRIMARY KEY ("BeamPositionMonitor_name", inputs),
	FOREIGN KEY("BeamPositionMonitor_name") REFERENCES "BeamPositionMonitor" (name)
);
CREATE INDEX "ix_BeamPositionMonitor_inputs_inputs" ON "BeamPositionMonitor_inputs" (inputs);
CREATE INDEX "ix_BeamPositionMonitor_inputs_BeamPositionMonitor_name" ON "BeamPositionMonitor_inputs" ("BeamPositionMonitor_name");

CREATE TABLE "BeamPositionMonitor_outputs" (
	"BeamPositionMonitor_name" TEXT,
	outputs VARCHAR(17),
	PRIMARY KEY ("BeamPositionMonitor_name", outputs),
	FOREIGN KEY("BeamPositionMonitor_name") REFERENCES "BeamPositionMonitor" (name)
);
CREATE INDEX "ix_BeamPositionMonitor_outputs_BeamPositionMonitor_name" ON "BeamPositionMonitor_outputs" ("BeamPositionMonitor_name");
CREATE INDEX "ix_BeamPositionMonitor_outputs_outputs" ON "BeamPositionMonitor_outputs" (outputs);

CREATE TABLE "BeamPositionMonitor_upstream" (
	"BeamPositionMonitor_name" TEXT,
	upstream_name TEXT,
	PRIMARY KEY ("BeamPositionMonitor_name", upstream_name),
	FOREIGN KEY("BeamPositionMonitor_name") REFERENCES "BeamPositionMonitor" (name),
	FOREIGN KEY(upstream_name) REFERENCES "AcceleratorElement" (name)
);
CREATE INDEX "ix_BeamPositionMonitor_upstream_BeamPositionMonitor_name" ON "BeamPositionMonitor_upstream" ("BeamPositionMonitor_name");
CREATE INDEX "ix_BeamPositionMonitor_upstream_upstream_name" ON "BeamPositionMonitor_upstream" (upstream_name);

CREATE TABLE "BeamPositionMonitor_downstream" (
	"BeamPositionMonitor_name" TEXT,
	downstream_name TEXT,
	PRIMARY KEY ("BeamPositionMonitor_name", downstream_name),
	FOREIGN KEY("BeamPositionMonitor_name") REFERENCES "BeamPositionMonitor" (name),
	FOREIGN KEY(downstream_name) REFERENCES "AcceleratorElement" (name)
);
CREATE INDEX "ix_BeamPositionMonitor_downstream_BeamPositionMonitor_name" ON "BeamPositionMonitor_downstream" ("BeamPositionMonitor_name");
CREATE INDEX "ix_BeamPositionMonitor_downstream_downstream_name" ON "BeamPositionMonitor_downstream" (downstream_name);

CREATE TABLE "BeamArrivalMonitor_alias" (
	"BeamArrivalMonitor_name" TEXT,
	alias TEXT,
	PRIMARY KEY ("BeamArrivalMonitor_name", alias),
	FOREIGN KEY("BeamArrivalMonitor_name") REFERENCES "BeamArrivalMonitor" (name)
);
CREATE INDEX "ix_BeamArrivalMonitor_alias_BeamArrivalMonitor_name" ON "BeamArrivalMonitor_alias" ("BeamArrivalMonitor_name");
CREATE INDEX "ix_BeamArrivalMonitor_alias_alias" ON "BeamArrivalMonitor_alias" (alias);

CREATE TABLE "BeamArrivalMonitor_inputs" (
	"BeamArrivalMonitor_name" TEXT,
	inputs VARCHAR(17),
	PRIMARY KEY ("BeamArrivalMonitor_name", inputs),
	FOREIGN KEY("BeamArrivalMonitor_name") REFERENCES "BeamArrivalMonitor" (name)
);
CREATE INDEX "ix_BeamArrivalMonitor_inputs_inputs" ON "BeamArrivalMonitor_inputs" (inputs);
CREATE INDEX "ix_BeamArrivalMonitor_inputs_BeamArrivalMonitor_name" ON "BeamArrivalMonitor_inputs" ("BeamArrivalMonitor_name");

CREATE TABLE "BeamArrivalMonitor_outputs" (
	"BeamArrivalMonitor_name" TEXT,
	outputs VARCHAR(17),
	PRIMARY KEY ("BeamArrivalMonitor_name", outputs),
	FOREIGN KEY("BeamArrivalMonitor_name") REFERENCES "BeamArrivalMonitor" (name)
);
CREATE INDEX "ix_BeamArrivalMonitor_outputs_BeamArrivalMonitor_name" ON "BeamArrivalMonitor_outputs" ("BeamArrivalMonitor_name");
CREATE INDEX "ix_BeamArrivalMonitor_outputs_outputs" ON "BeamArrivalMonitor_outputs" (outputs);

CREATE TABLE "BeamArrivalMonitor_upstream" (
	"BeamArrivalMonitor_name" TEXT,
	upstream_name TEXT,
	PRIMARY KEY ("BeamArrivalMonitor_name", upstream_name),
	FOREIGN KEY("BeamArrivalMonitor_name") REFERENCES "BeamArrivalMonitor" (name),
	FOREIGN KEY(upstream_name) REFERENCES "AcceleratorElement" (name)
);
CREATE INDEX "ix_BeamArrivalMonitor_upstream_upstream_name" ON "BeamArrivalMonitor_upstream" (upstream_name);
CREATE INDEX "ix_BeamArrivalMonitor_upstream_BeamArrivalMonitor_name" ON "BeamArrivalMonitor_upstream" ("BeamArrivalMonitor_name");

CREATE TABLE "BeamArrivalMonitor_downstream" (
	"BeamArrivalMonitor_name" TEXT,
	downstream_name TEXT,
	PRIMARY KEY ("BeamArrivalMonitor_name", downstream_name),
	FOREIGN KEY("BeamArrivalMonitor_name") REFERENCES "BeamArrivalMonitor" (name),
	FOREIGN KEY(downstream_name) REFERENCES "AcceleratorElement" (name)
);
CREATE INDEX "ix_BeamArrivalMonitor_downstream_BeamArrivalMonitor_name" ON "BeamArrivalMonitor_downstream" ("BeamArrivalMonitor_name");
CREATE INDEX "ix_BeamArrivalMonitor_downstream_downstream_name" ON "BeamArrivalMonitor_downstream" (downstream_name);

CREATE TABLE "BunchLengthMonitor_alias" (
	"BunchLengthMonitor_name" TEXT,
	alias TEXT,
	PRIMARY KEY ("BunchLengthMonitor_name", alias),
	FOREIGN KEY("BunchLengthMonitor_name") REFERENCES "BunchLengthMonitor" (name)
);
CREATE INDEX "ix_BunchLengthMonitor_alias_alias" ON "BunchLengthMonitor_alias" (alias);
CREATE INDEX "ix_BunchLengthMonitor_alias_BunchLengthMonitor_name" ON "BunchLengthMonitor_alias" ("BunchLengthMonitor_name");

CREATE TABLE "BunchLengthMonitor_inputs" (
	"BunchLengthMonitor_name" TEXT,
	inputs VARCHAR(17),
	PRIMARY KEY ("BunchLengthMonitor_name", inputs),
	FOREIGN KEY("BunchLengthMonitor_name") REFERENCES "BunchLengthMonitor" (name)
);
CREATE INDEX "ix_BunchLengthMonitor_inputs_inputs" ON "BunchLengthMonitor_inputs" (inputs);
CREATE INDEX "ix_BunchLengthMonitor_inputs_BunchLengthMonitor_name" ON "BunchLengthMonitor_inputs" ("BunchLengthMonitor_name");

CREATE TABLE "BunchLengthMonitor_outputs" (
	"BunchLengthMonitor_name" TEXT,
	outputs VARCHAR(17),
	PRIMARY KEY ("BunchLengthMonitor_name", outputs),
	FOREIGN KEY("BunchLengthMonitor_name") REFERENCES "BunchLengthMonitor" (name)
);
CREATE INDEX "ix_BunchLengthMonitor_outputs_outputs" ON "BunchLengthMonitor_outputs" (outputs);
CREATE INDEX "ix_BunchLengthMonitor_outputs_BunchLengthMonitor_name" ON "BunchLengthMonitor_outputs" ("BunchLengthMonitor_name");

CREATE TABLE "BunchLengthMonitor_upstream" (
	"BunchLengthMonitor_name" TEXT,
	upstream_name TEXT,
	PRIMARY KEY ("BunchLengthMonitor_name", upstream_name),
	FOREIGN KEY("BunchLengthMonitor_name") REFERENCES "BunchLengthMonitor" (name),
	FOREIGN KEY(upstream_name) REFERENCES "AcceleratorElement" (name)
);
CREATE INDEX "ix_BunchLengthMonitor_upstream_BunchLengthMonitor_name" ON "BunchLengthMonitor_upstream" ("BunchLengthMonitor_name");
CREATE INDEX "ix_BunchLengthMonitor_upstream_upstream_name" ON "BunchLengthMonitor_upstream" (upstream_name);

CREATE TABLE "BunchLengthMonitor_downstream" (
	"BunchLengthMonitor_name" TEXT,
	downstream_name TEXT,
	PRIMARY KEY ("BunchLengthMonitor_name", downstream_name),
	FOREIGN KEY("BunchLengthMonitor_name") REFERENCES "BunchLengthMonitor" (name),
	FOREIGN KEY(downstream_name) REFERENCES "AcceleratorElement" (name)
);
CREATE INDEX "ix_BunchLengthMonitor_downstream_downstream_name" ON "BunchLengthMonitor_downstream" (downstream_name);
CREATE INDEX "ix_BunchLengthMonitor_downstream_BunchLengthMonitor_name" ON "BunchLengthMonitor_downstream" ("BunchLengthMonitor_name");

CREATE TABLE "Camera_alias" (
	"Camera_name" TEXT,
	alias TEXT,
	PRIMARY KEY ("Camera_name", alias),
	FOREIGN KEY("Camera_name") REFERENCES "Camera" (name)
);
CREATE INDEX "ix_Camera_alias_Camera_name" ON "Camera_alias" ("Camera_name");
CREATE INDEX "ix_Camera_alias_alias" ON "Camera_alias" (alias);

CREATE TABLE "Camera_inputs" (
	"Camera_name" TEXT,
	inputs VARCHAR(17),
	PRIMARY KEY ("Camera_name", inputs),
	FOREIGN KEY("Camera_name") REFERENCES "Camera" (name)
);
CREATE INDEX "ix_Camera_inputs_inputs" ON "Camera_inputs" (inputs);
CREATE INDEX "ix_Camera_inputs_Camera_name" ON "Camera_inputs" ("Camera_name");

CREATE TABLE "Camera_outputs" (
	"Camera_name" TEXT,
	outputs VARCHAR(17),
	PRIMARY KEY ("Camera_name", outputs),
	FOREIGN KEY("Camera_name") REFERENCES "Camera" (name)
);
CREATE INDEX "ix_Camera_outputs_outputs" ON "Camera_outputs" (outputs);
CREATE INDEX "ix_Camera_outputs_Camera_name" ON "Camera_outputs" ("Camera_name");

CREATE TABLE "Camera_upstream" (
	"Camera_name" TEXT,
	upstream_name TEXT,
	PRIMARY KEY ("Camera_name", upstream_name),
	FOREIGN KEY("Camera_name") REFERENCES "Camera" (name),
	FOREIGN KEY(upstream_name) REFERENCES "AcceleratorElement" (name)
);
CREATE INDEX "ix_Camera_upstream_Camera_name" ON "Camera_upstream" ("Camera_name");
CREATE INDEX "ix_Camera_upstream_upstream_name" ON "Camera_upstream" (upstream_name);

CREATE TABLE "Camera_downstream" (
	"Camera_name" TEXT,
	downstream_name TEXT,
	PRIMARY KEY ("Camera_name", downstream_name),
	FOREIGN KEY("Camera_name") REFERENCES "Camera" (name),
	FOREIGN KEY(downstream_name) REFERENCES "AcceleratorElement" (name)
);
CREATE INDEX "ix_Camera_downstream_downstream_name" ON "Camera_downstream" (downstream_name);
CREATE INDEX "ix_Camera_downstream_Camera_name" ON "Camera_downstream" ("Camera_name");

CREATE TABLE "Screen_alias" (
	"Screen_name" TEXT,
	alias TEXT,
	PRIMARY KEY ("Screen_name", alias),
	FOREIGN KEY("Screen_name") REFERENCES "Screen" (name)
);
CREATE INDEX "ix_Screen_alias_alias" ON "Screen_alias" (alias);
CREATE INDEX "ix_Screen_alias_Screen_name" ON "Screen_alias" ("Screen_name");

CREATE TABLE "Screen_inputs" (
	"Screen_name" TEXT,
	inputs VARCHAR(17),
	PRIMARY KEY ("Screen_name", inputs),
	FOREIGN KEY("Screen_name") REFERENCES "Screen" (name)
);
CREATE INDEX "ix_Screen_inputs_Screen_name" ON "Screen_inputs" ("Screen_name");
CREATE INDEX "ix_Screen_inputs_inputs" ON "Screen_inputs" (inputs);

CREATE TABLE "Screen_outputs" (
	"Screen_name" TEXT,
	outputs VARCHAR(17),
	PRIMARY KEY ("Screen_name", outputs),
	FOREIGN KEY("Screen_name") REFERENCES "Screen" (name)
);
CREATE INDEX "ix_Screen_outputs_Screen_name" ON "Screen_outputs" ("Screen_name");
CREATE INDEX "ix_Screen_outputs_outputs" ON "Screen_outputs" (outputs);

CREATE TABLE "Screen_upstream" (
	"Screen_name" TEXT,
	upstream_name TEXT,
	PRIMARY KEY ("Screen_name", upstream_name),
	FOREIGN KEY("Screen_name") REFERENCES "Screen" (name),
	FOREIGN KEY(upstream_name) REFERENCES "AcceleratorElement" (name)
);
CREATE INDEX "ix_Screen_upstream_upstream_name" ON "Screen_upstream" (upstream_name);
CREATE INDEX "ix_Screen_upstream_Screen_name" ON "Screen_upstream" ("Screen_name");

CREATE TABLE "Screen_downstream" (
	"Screen_name" TEXT,
	downstream_name TEXT,
	PRIMARY KEY ("Screen_name", downstream_name),
	FOREIGN KEY("Screen_name") REFERENCES "Screen" (name),
	FOREIGN KEY(downstream_name) REFERENCES "AcceleratorElement" (name)
);
CREATE INDEX "ix_Screen_downstream_downstream_name" ON "Screen_downstream" (downstream_name);
CREATE INDEX "ix_Screen_downstream_Screen_name" ON "Screen_downstream" ("Screen_name");

CREATE TABLE "ChargeDiagnostic_alias" (
	"ChargeDiagnostic_name" TEXT,
	alias TEXT,
	PRIMARY KEY ("ChargeDiagnostic_name", alias),
	FOREIGN KEY("ChargeDiagnostic_name") REFERENCES "ChargeDiagnostic" (name)
);
CREATE INDEX "ix_ChargeDiagnostic_alias_ChargeDiagnostic_name" ON "ChargeDiagnostic_alias" ("ChargeDiagnostic_name");
CREATE INDEX "ix_ChargeDiagnostic_alias_alias" ON "ChargeDiagnostic_alias" (alias);

CREATE TABLE "ChargeDiagnostic_inputs" (
	"ChargeDiagnostic_name" TEXT,
	inputs VARCHAR(17),
	PRIMARY KEY ("ChargeDiagnostic_name", inputs),
	FOREIGN KEY("ChargeDiagnostic_name") REFERENCES "ChargeDiagnostic" (name)
);
CREATE INDEX "ix_ChargeDiagnostic_inputs_inputs" ON "ChargeDiagnostic_inputs" (inputs);
CREATE INDEX "ix_ChargeDiagnostic_inputs_ChargeDiagnostic_name" ON "ChargeDiagnostic_inputs" ("ChargeDiagnostic_name");

CREATE TABLE "ChargeDiagnostic_outputs" (
	"ChargeDiagnostic_name" TEXT,
	outputs VARCHAR(17),
	PRIMARY KEY ("ChargeDiagnostic_name", outputs),
	FOREIGN KEY("ChargeDiagnostic_name") REFERENCES "ChargeDiagnostic" (name)
);
CREATE INDEX "ix_ChargeDiagnostic_outputs_ChargeDiagnostic_name" ON "ChargeDiagnostic_outputs" ("ChargeDiagnostic_name");
CREATE INDEX "ix_ChargeDiagnostic_outputs_outputs" ON "ChargeDiagnostic_outputs" (outputs);

CREATE TABLE "ChargeDiagnostic_upstream" (
	"ChargeDiagnostic_name" TEXT,
	upstream_name TEXT,
	PRIMARY KEY ("ChargeDiagnostic_name", upstream_name),
	FOREIGN KEY("ChargeDiagnostic_name") REFERENCES "ChargeDiagnostic" (name),
	FOREIGN KEY(upstream_name) REFERENCES "AcceleratorElement" (name)
);
CREATE INDEX "ix_ChargeDiagnostic_upstream_upstream_name" ON "ChargeDiagnostic_upstream" (upstream_name);
CREATE INDEX "ix_ChargeDiagnostic_upstream_ChargeDiagnostic_name" ON "ChargeDiagnostic_upstream" ("ChargeDiagnostic_name");

CREATE TABLE "ChargeDiagnostic_downstream" (
	"ChargeDiagnostic_name" TEXT,
	downstream_name TEXT,
	PRIMARY KEY ("ChargeDiagnostic_name", downstream_name),
	FOREIGN KEY("ChargeDiagnostic_name") REFERENCES "ChargeDiagnostic" (name),
	FOREIGN KEY(downstream_name) REFERENCES "AcceleratorElement" (name)
);
CREATE INDEX "ix_ChargeDiagnostic_downstream_ChargeDiagnostic_name" ON "ChargeDiagnostic_downstream" ("ChargeDiagnostic_name");
CREATE INDEX "ix_ChargeDiagnostic_downstream_downstream_name" ON "ChargeDiagnostic_downstream" (downstream_name);

CREATE TABLE "WallCurrentMonitor_alias" (
	"WallCurrentMonitor_name" TEXT,
	alias TEXT,
	PRIMARY KEY ("WallCurrentMonitor_name", alias),
	FOREIGN KEY("WallCurrentMonitor_name") REFERENCES "WallCurrentMonitor" (name)
);
CREATE INDEX "ix_WallCurrentMonitor_alias_WallCurrentMonitor_name" ON "WallCurrentMonitor_alias" ("WallCurrentMonitor_name");
CREATE INDEX "ix_WallCurrentMonitor_alias_alias" ON "WallCurrentMonitor_alias" (alias);

CREATE TABLE "WallCurrentMonitor_inputs" (
	"WallCurrentMonitor_name" TEXT,
	inputs VARCHAR(17),
	PRIMARY KEY ("WallCurrentMonitor_name", inputs),
	FOREIGN KEY("WallCurrentMonitor_name") REFERENCES "WallCurrentMonitor" (name)
);
CREATE INDEX "ix_WallCurrentMonitor_inputs_inputs" ON "WallCurrentMonitor_inputs" (inputs);
CREATE INDEX "ix_WallCurrentMonitor_inputs_WallCurrentMonitor_name" ON "WallCurrentMonitor_inputs" ("WallCurrentMonitor_name");

CREATE TABLE "WallCurrentMonitor_outputs" (
	"WallCurrentMonitor_name" TEXT,
	outputs VARCHAR(17),
	PRIMARY KEY ("WallCurrentMonitor_name", outputs),
	FOREIGN KEY("WallCurrentMonitor_name") REFERENCES "WallCurrentMonitor" (name)
);
CREATE INDEX "ix_WallCurrentMonitor_outputs_WallCurrentMonitor_name" ON "WallCurrentMonitor_outputs" ("WallCurrentMonitor_name");
CREATE INDEX "ix_WallCurrentMonitor_outputs_outputs" ON "WallCurrentMonitor_outputs" (outputs);

CREATE TABLE "WallCurrentMonitor_upstream" (
	"WallCurrentMonitor_name" TEXT,
	upstream_name TEXT,
	PRIMARY KEY ("WallCurrentMonitor_name", upstream_name),
	FOREIGN KEY("WallCurrentMonitor_name") REFERENCES "WallCurrentMonitor" (name),
	FOREIGN KEY(upstream_name) REFERENCES "AcceleratorElement" (name)
);
CREATE INDEX "ix_WallCurrentMonitor_upstream_upstream_name" ON "WallCurrentMonitor_upstream" (upstream_name);
CREATE INDEX "ix_WallCurrentMonitor_upstream_WallCurrentMonitor_name" ON "WallCurrentMonitor_upstream" ("WallCurrentMonitor_name");

CREATE TABLE "WallCurrentMonitor_downstream" (
	"WallCurrentMonitor_name" TEXT,
	downstream_name TEXT,
	PRIMARY KEY ("WallCurrentMonitor_name", downstream_name),
	FOREIGN KEY("WallCurrentMonitor_name") REFERENCES "WallCurrentMonitor" (name),
	FOREIGN KEY(downstream_name) REFERENCES "AcceleratorElement" (name)
);
CREATE INDEX "ix_WallCurrentMonitor_downstream_WallCurrentMonitor_name" ON "WallCurrentMonitor_downstream" ("WallCurrentMonitor_name");
CREATE INDEX "ix_WallCurrentMonitor_downstream_downstream_name" ON "WallCurrentMonitor_downstream" (downstream_name);

CREATE TABLE "FaradayCupMonitor_alias" (
	"FaradayCupMonitor_name" TEXT,
	alias TEXT,
	PRIMARY KEY ("FaradayCupMonitor_name", alias),
	FOREIGN KEY("FaradayCupMonitor_name") REFERENCES "FaradayCupMonitor" (name)
);
CREATE INDEX "ix_FaradayCupMonitor_alias_alias" ON "FaradayCupMonitor_alias" (alias);
CREATE INDEX "ix_FaradayCupMonitor_alias_FaradayCupMonitor_name" ON "FaradayCupMonitor_alias" ("FaradayCupMonitor_name");

CREATE TABLE "FaradayCupMonitor_inputs" (
	"FaradayCupMonitor_name" TEXT,
	inputs VARCHAR(17),
	PRIMARY KEY ("FaradayCupMonitor_name", inputs),
	FOREIGN KEY("FaradayCupMonitor_name") REFERENCES "FaradayCupMonitor" (name)
);
CREATE INDEX "ix_FaradayCupMonitor_inputs_inputs" ON "FaradayCupMonitor_inputs" (inputs);
CREATE INDEX "ix_FaradayCupMonitor_inputs_FaradayCupMonitor_name" ON "FaradayCupMonitor_inputs" ("FaradayCupMonitor_name");

CREATE TABLE "FaradayCupMonitor_outputs" (
	"FaradayCupMonitor_name" TEXT,
	outputs VARCHAR(17),
	PRIMARY KEY ("FaradayCupMonitor_name", outputs),
	FOREIGN KEY("FaradayCupMonitor_name") REFERENCES "FaradayCupMonitor" (name)
);
CREATE INDEX "ix_FaradayCupMonitor_outputs_FaradayCupMonitor_name" ON "FaradayCupMonitor_outputs" ("FaradayCupMonitor_name");
CREATE INDEX "ix_FaradayCupMonitor_outputs_outputs" ON "FaradayCupMonitor_outputs" (outputs);

CREATE TABLE "FaradayCupMonitor_upstream" (
	"FaradayCupMonitor_name" TEXT,
	upstream_name TEXT,
	PRIMARY KEY ("FaradayCupMonitor_name", upstream_name),
	FOREIGN KEY("FaradayCupMonitor_name") REFERENCES "FaradayCupMonitor" (name),
	FOREIGN KEY(upstream_name) REFERENCES "AcceleratorElement" (name)
);
CREATE INDEX "ix_FaradayCupMonitor_upstream_upstream_name" ON "FaradayCupMonitor_upstream" (upstream_name);
CREATE INDEX "ix_FaradayCupMonitor_upstream_FaradayCupMonitor_name" ON "FaradayCupMonitor_upstream" ("FaradayCupMonitor_name");

CREATE TABLE "FaradayCupMonitor_downstream" (
	"FaradayCupMonitor_name" TEXT,
	downstream_name TEXT,
	PRIMARY KEY ("FaradayCupMonitor_name", downstream_name),
	FOREIGN KEY("FaradayCupMonitor_name") REFERENCES "FaradayCupMonitor" (name),
	FOREIGN KEY(downstream_name) REFERENCES "AcceleratorElement" (name)
);
CREATE INDEX "ix_FaradayCupMonitor_downstream_FaradayCupMonitor_name" ON "FaradayCupMonitor_downstream" ("FaradayCupMonitor_name");
CREATE INDEX "ix_FaradayCupMonitor_downstream_downstream_name" ON "FaradayCupMonitor_downstream" (downstream_name);

CREATE TABLE "IntegratedCurrentTransformer_alias" (
	"IntegratedCurrentTransformer_name" TEXT,
	alias TEXT,
	PRIMARY KEY ("IntegratedCurrentTransformer_name", alias),
	FOREIGN KEY("IntegratedCurrentTransformer_name") REFERENCES "IntegratedCurrentTransformer" (name)
);
CREATE INDEX "ix_IntegratedCurrentTransformer_alias_alias" ON "IntegratedCurrentTransformer_alias" (alias);
CREATE INDEX "ix_IntegratedCurrentTransformer_alias_IntegratedCurrentTransformer_name" ON "IntegratedCurrentTransformer_alias" ("IntegratedCurrentTransformer_name");

CREATE TABLE "IntegratedCurrentTransformer_inputs" (
	"IntegratedCurrentTransformer_name" TEXT,
	inputs VARCHAR(17),
	PRIMARY KEY ("IntegratedCurrentTransformer_name", inputs),
	FOREIGN KEY("IntegratedCurrentTransformer_name") REFERENCES "IntegratedCurrentTransformer" (name)
);
CREATE INDEX "ix_IntegratedCurrentTransformer_inputs_inputs" ON "IntegratedCurrentTransformer_inputs" (inputs);
CREATE INDEX "ix_IntegratedCurrentTransformer_inputs_IntegratedCurrentTransformer_name" ON "IntegratedCurrentTransformer_inputs" ("IntegratedCurrentTransformer_name");

CREATE TABLE "IntegratedCurrentTransformer_outputs" (
	"IntegratedCurrentTransformer_name" TEXT,
	outputs VARCHAR(17),
	PRIMARY KEY ("IntegratedCurrentTransformer_name", outputs),
	FOREIGN KEY("IntegratedCurrentTransformer_name") REFERENCES "IntegratedCurrentTransformer" (name)
);
CREATE INDEX "ix_IntegratedCurrentTransformer_outputs_IntegratedCurrentTransformer_name" ON "IntegratedCurrentTransformer_outputs" ("IntegratedCurrentTransformer_name");
CREATE INDEX "ix_IntegratedCurrentTransformer_outputs_outputs" ON "IntegratedCurrentTransformer_outputs" (outputs);

CREATE TABLE "IntegratedCurrentTransformer_upstream" (
	"IntegratedCurrentTransformer_name" TEXT,
	upstream_name TEXT,
	PRIMARY KEY ("IntegratedCurrentTransformer_name", upstream_name),
	FOREIGN KEY("IntegratedCurrentTransformer_name") REFERENCES "IntegratedCurrentTransformer" (name),
	FOREIGN KEY(upstream_name) REFERENCES "AcceleratorElement" (name)
);
CREATE INDEX "ix_IntegratedCurrentTransformer_upstream_upstream_name" ON "IntegratedCurrentTransformer_upstream" (upstream_name);
CREATE INDEX "ix_IntegratedCurrentTransformer_upstream_IntegratedCurrentTransformer_name" ON "IntegratedCurrentTransformer_upstream" ("IntegratedCurrentTransformer_name");

CREATE TABLE "IntegratedCurrentTransformer_downstream" (
	"IntegratedCurrentTransformer_name" TEXT,
	downstream_name TEXT,
	PRIMARY KEY ("IntegratedCurrentTransformer_name", downstream_name),
	FOREIGN KEY("IntegratedCurrentTransformer_name") REFERENCES "IntegratedCurrentTransformer" (name),
	FOREIGN KEY(downstream_name) REFERENCES "AcceleratorElement" (name)
);
CREATE INDEX "ix_IntegratedCurrentTransformer_downstream_IntegratedCurrentTransformer_name" ON "IntegratedCurrentTransformer_downstream" ("IntegratedCurrentTransformer_name");
CREATE INDEX "ix_IntegratedCurrentTransformer_downstream_downstream_name" ON "IntegratedCurrentTransformer_downstream" (downstream_name);

CREATE TABLE "Plasma_alias" (
	"Plasma_name" TEXT,
	alias TEXT,
	PRIMARY KEY ("Plasma_name", alias),
	FOREIGN KEY("Plasma_name") REFERENCES "Plasma" (name)
);
CREATE INDEX "ix_Plasma_alias_Plasma_name" ON "Plasma_alias" ("Plasma_name");
CREATE INDEX "ix_Plasma_alias_alias" ON "Plasma_alias" (alias);

CREATE TABLE "Plasma_inputs" (
	"Plasma_name" TEXT,
	inputs VARCHAR(17),
	PRIMARY KEY ("Plasma_name", inputs),
	FOREIGN KEY("Plasma_name") REFERENCES "Plasma" (name)
);
CREATE INDEX "ix_Plasma_inputs_inputs" ON "Plasma_inputs" (inputs);
CREATE INDEX "ix_Plasma_inputs_Plasma_name" ON "Plasma_inputs" ("Plasma_name");

CREATE TABLE "Plasma_outputs" (
	"Plasma_name" TEXT,
	outputs VARCHAR(17),
	PRIMARY KEY ("Plasma_name", outputs),
	FOREIGN KEY("Plasma_name") REFERENCES "Plasma" (name)
);
CREATE INDEX "ix_Plasma_outputs_Plasma_name" ON "Plasma_outputs" ("Plasma_name");
CREATE INDEX "ix_Plasma_outputs_outputs" ON "Plasma_outputs" (outputs);

CREATE TABLE "Plasma_upstream" (
	"Plasma_name" TEXT,
	upstream_name TEXT,
	PRIMARY KEY ("Plasma_name", upstream_name),
	FOREIGN KEY("Plasma_name") REFERENCES "Plasma" (name),
	FOREIGN KEY(upstream_name) REFERENCES "AcceleratorElement" (name)
);
CREATE INDEX "ix_Plasma_upstream_upstream_name" ON "Plasma_upstream" (upstream_name);
CREATE INDEX "ix_Plasma_upstream_Plasma_name" ON "Plasma_upstream" ("Plasma_name");

CREATE TABLE "Plasma_downstream" (
	"Plasma_name" TEXT,
	downstream_name TEXT,
	PRIMARY KEY ("Plasma_name", downstream_name),
	FOREIGN KEY("Plasma_name") REFERENCES "Plasma" (name),
	FOREIGN KEY(downstream_name) REFERENCES "AcceleratorElement" (name)
);
CREATE INDEX "ix_Plasma_downstream_Plasma_name" ON "Plasma_downstream" ("Plasma_name");
CREATE INDEX "ix_Plasma_downstream_downstream_name" ON "Plasma_downstream" (downstream_name);

CREATE TABLE "Dipole_alias" (
	"Dipole_name" TEXT,
	alias TEXT,
	PRIMARY KEY ("Dipole_name", alias),
	FOREIGN KEY("Dipole_name") REFERENCES "Dipole" (name)
);
CREATE INDEX "ix_Dipole_alias_Dipole_name" ON "Dipole_alias" ("Dipole_name");
CREATE INDEX "ix_Dipole_alias_alias" ON "Dipole_alias" (alias);

CREATE TABLE "Dipole_inputs" (
	"Dipole_name" TEXT,
	inputs VARCHAR(17),
	PRIMARY KEY ("Dipole_name", inputs),
	FOREIGN KEY("Dipole_name") REFERENCES "Dipole" (name)
);
CREATE INDEX "ix_Dipole_inputs_inputs" ON "Dipole_inputs" (inputs);
CREATE INDEX "ix_Dipole_inputs_Dipole_name" ON "Dipole_inputs" ("Dipole_name");

CREATE TABLE "Dipole_outputs" (
	"Dipole_name" TEXT,
	outputs VARCHAR(17),
	PRIMARY KEY ("Dipole_name", outputs),
	FOREIGN KEY("Dipole_name") REFERENCES "Dipole" (name)
);
CREATE INDEX "ix_Dipole_outputs_outputs" ON "Dipole_outputs" (outputs);
CREATE INDEX "ix_Dipole_outputs_Dipole_name" ON "Dipole_outputs" ("Dipole_name");

CREATE TABLE "Dipole_upstream" (
	"Dipole_name" TEXT,
	upstream_name TEXT,
	PRIMARY KEY ("Dipole_name", upstream_name),
	FOREIGN KEY("Dipole_name") REFERENCES "Dipole" (name),
	FOREIGN KEY(upstream_name) REFERENCES "AcceleratorElement" (name)
);
CREATE INDEX "ix_Dipole_upstream_Dipole_name" ON "Dipole_upstream" ("Dipole_name");
CREATE INDEX "ix_Dipole_upstream_upstream_name" ON "Dipole_upstream" (upstream_name);

CREATE TABLE "Dipole_downstream" (
	"Dipole_name" TEXT,
	downstream_name TEXT,
	PRIMARY KEY ("Dipole_name", downstream_name),
	FOREIGN KEY("Dipole_name") REFERENCES "Dipole" (name),
	FOREIGN KEY(downstream_name) REFERENCES "AcceleratorElement" (name)
);
CREATE INDEX "ix_Dipole_downstream_downstream_name" ON "Dipole_downstream" (downstream_name);
CREATE INDEX "ix_Dipole_downstream_Dipole_name" ON "Dipole_downstream" ("Dipole_name");

CREATE TABLE "Quadrupole_alias" (
	"Quadrupole_name" TEXT,
	alias TEXT,
	PRIMARY KEY ("Quadrupole_name", alias),
	FOREIGN KEY("Quadrupole_name") REFERENCES "Quadrupole" (name)
);
CREATE INDEX "ix_Quadrupole_alias_alias" ON "Quadrupole_alias" (alias);
CREATE INDEX "ix_Quadrupole_alias_Quadrupole_name" ON "Quadrupole_alias" ("Quadrupole_name");

CREATE TABLE "Quadrupole_inputs" (
	"Quadrupole_name" TEXT,
	inputs VARCHAR(17),
	PRIMARY KEY ("Quadrupole_name", inputs),
	FOREIGN KEY("Quadrupole_name") REFERENCES "Quadrupole" (name)
);
CREATE INDEX "ix_Quadrupole_inputs_Quadrupole_name" ON "Quadrupole_inputs" ("Quadrupole_name");
CREATE INDEX "ix_Quadrupole_inputs_inputs" ON "Quadrupole_inputs" (inputs);

CREATE TABLE "Quadrupole_outputs" (
	"Quadrupole_name" TEXT,
	outputs VARCHAR(17),
	PRIMARY KEY ("Quadrupole_name", outputs),
	FOREIGN KEY("Quadrupole_name") REFERENCES "Quadrupole" (name)
);
CREATE INDEX "ix_Quadrupole_outputs_outputs" ON "Quadrupole_outputs" (outputs);
CREATE INDEX "ix_Quadrupole_outputs_Quadrupole_name" ON "Quadrupole_outputs" ("Quadrupole_name");

CREATE TABLE "Quadrupole_upstream" (
	"Quadrupole_name" TEXT,
	upstream_name TEXT,
	PRIMARY KEY ("Quadrupole_name", upstream_name),
	FOREIGN KEY("Quadrupole_name") REFERENCES "Quadrupole" (name),
	FOREIGN KEY(upstream_name) REFERENCES "AcceleratorElement" (name)
);
CREATE INDEX "ix_Quadrupole_upstream_Quadrupole_name" ON "Quadrupole_upstream" ("Quadrupole_name");
CREATE INDEX "ix_Quadrupole_upstream_upstream_name" ON "Quadrupole_upstream" (upstream_name);

CREATE TABLE "Quadrupole_downstream" (
	"Quadrupole_name" TEXT,
	downstream_name TEXT,
	PRIMARY KEY ("Quadrupole_name", downstream_name),
	FOREIGN KEY("Quadrupole_name") REFERENCES "Quadrupole" (name),
	FOREIGN KEY(downstream_name) REFERENCES "AcceleratorElement" (name)
);
CREATE INDEX "ix_Quadrupole_downstream_Quadrupole_name" ON "Quadrupole_downstream" ("Quadrupole_name");
CREATE INDEX "ix_Quadrupole_downstream_downstream_name" ON "Quadrupole_downstream" (downstream_name);

