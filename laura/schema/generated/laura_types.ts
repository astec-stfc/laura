export type TwissMatchName = string;
export type StageName = string;
export type VacuumGaugeName = string;
export type LaserName = string;
export type ShutterName = string;
export type ValveName = string;
export type MarkerName = string;
export type ApertureName = string;
export type CollimatorName = string;
export type DriftName = string;
export type LightingName = string;
export type PowerSupplyName = string;
export type SectionLatticeName = string;
export type MachineLayoutName = string;
export type MagnetName = string;
export type RFCavityName = string;
export type RFDeflectingCavityName = string;
export type WakefieldName = string;
export type LowLevelRFName = string;
export type RFModulatorName = string;
export type RFProtectionName = string;
export type RFHeartbeatName = string;
export type PIDName = string;
export type DiagnosticName = string;
export type BeamPositionMonitorName = string;
export type BeamArrivalMonitorName = string;
export type BunchLengthMonitorName = string;
export type CameraName = string;
export type ScreenName = string;
export type ChargeDiagnosticName = string;
export type WallCurrentMonitorName = string;
export type FaradayCupMonitorName = string;
export type IntegratedCurrentTransformerName = string;
export type PhotonMonitorName = string;
export type PlasmaName = string;
export type LaserEnergyMeterName = string;
export type LaserHalfWavePlateName = string;
export type LaserMirrorName = string;
export type LaserAttenuatorName = string;
export type DipoleName = string;
export type QuadrupoleName = string;
export type SextupoleName = string;
export type OctupoleName = string;
export type HorizontalCorrectorName = string;
export type VerticalCorrectorName = string;
export type CombinedCorrectorName = string;
export type SolenoidName = string;
export type WigglerName = string;
export type NonLinearLensName = string;
export type AcceleratorElementName = string;
export type StandardElementName = string;
export type ElementName = string;
export type PhysicalAcceleratorElementName = string;
/**
* Input types for accelerator elements.
*/
export enum IOTypeEnum {
    
    /** Electrical current. */
    current = "current",
    /** Electrical voltage. */
    voltage = "voltage",
    /** Phase in radians. */
    phase = "phase",
    /** Control setpoint. */
    setpoint = "setpoint",
    /** On/Off state. */
    on_off_state = "on_off_state",
    /** Open/Closed state. */
    open_closed_state = "open_closed_state",
    /** Physical position. */
    position = "position",
    /** Physical rotation. */
    rotation = "rotation",
    /** Electrical power. */
    power = "power",
    /** Gas pressure. */
    pressure = "pressure",
    /** Electrical charge. */
    charge = "charge",
    /** Absolute timing. */
    absolute_time = "absolute_time",
    /** Relative timing. */
    relative_time = "relative_time",
    /** Shot number. */
    shot_number = "shot_number",
    /** Single value. */
    value = "value",
    /** Multivalued waveform. */
    waveform = "waveform",
    /** Magnetic field. */
    magnetic_field = "magnetic_field",
};
/**
* Kind of quantity a control variable carries.
*/
export enum ControlTypeEnum {
    
    /** Single numeric value. */
    scalar = "scalar",
    /** Two-state value. */
    binary = "binary",
    /** Enumerated state, mapped through ``states``. */
    state = "state",
    /** Textual value. */
    string = "string",
    /** Array-valued trace. */
    waveform = "waveform",
    /** Value with associated statistics (the default). */
    statistical = "statistical",
};
/**
* Cross-sectional shape of a beam-pipe aperture.
*/
export enum ApertureShapeEnum {
    
    circular = "circular",
    rectangular = "rectangular",
    elliptical = "elliptical",
};
/**
* Bending plane enum.
*/
export enum BendingPlaneEnum {
    
    /** Horizontal bending plane. */
    Horizontal = "Horizontal",
    /** Vertical bending plane. */
    Vertical = "Vertical",
    /** Combined Horizontal and Vertical bending plane. */
    Combined = "Combined",
};
/**
* High-level category organising elements by function within the accelerator.  Corresponds to the YAML ``hardware_class`` field.
*/
export enum HardwareClassEnum {
    
    /** Magnetic focusing or bending element. */
    Magnet = "Magnet",
    /** Beam-diagnostic instrument. */
    Diagnostic = "Diagnostic",
    /** Radio-frequency accelerating or deflecting structure. */
    RF = "RF",
    /** Vacuum instrumentation (gauges, valves). */
    Vacuum = "Vacuum",
    /** Laser optical element or complete laser system. */
    Laser = "Laser",
    /** Plasma-based accelerating stage. */
    Plasma = "Plasma",
    /** Control-system feedback element. */
    Feedback = "Feedback",
    /** Virtual survey marker with no physical aperture. */
    Marker = "Marker",
    /** Mechanical aperture or collimator. */
    Aperture = "Aperture",
    /** Motorised positioning stage. */
    Stage = "Stage",
    /** Experimental-hall lighting element. */
    Lighting = "Lighting",
    /** Beam or laser shutter. */
    Shutter = "Shutter",
    /** Passive wakefield structure. */
    Wakefield = "Wakefield",
    /** Virtual Twiss-parameter matching point. */
    TwissMatch = "TwissMatch",
    /** Drift element. */
    Drift = "Drift",
    /** Generic element. */
    Generic = "Generic",
    /** Beam monitor element. */
    Monitor = "Monitor",
    /** Simulation element. */
    Simulation = "Simulation",
};
/**
* Polarization state of a laser beam.
*/
export enum LaserPolarizationEnum {
    
    linear = "linear",
    circular = "circular",
    elliptical = "elliptical",
};
/**
* Transverse intensity profile model for a laser beam.
*/
export enum LaserProfileTypeEnum {
    
    gaussian = "gaussian",
    laguerre_gaussian = "laguerre-gaussian",
    flattened_gaussian = "flattened-gaussian",
    file = "file",
};


/**
 * Cartesian position in the global accelerator coordinate system. All components are in metres.
 */
export interface Position {
    /** Horizontal component [m]. */
    x?: number,
    /** Vertical component [m]. */
    y?: number,
    /** Longitudinal (beam-direction) component [m]. */
    z?: number,
}


/**
 * Euler-angle rotation relative to the global coordinate system. All angles are in radians, bounded to [-pi, pi].
 */
export interface Rotation {
    /** Rotation about the horizontal (x) axis [rad]. */
    phi?: number,
    /** Rotation about the vertical (y) axis [rad]. */
    psi?: number,
    /** Rotation about the longitudinal (z) axis [rad]. */
    theta?: number,
}


/**
 * Alignment position and rotation errors for a physically-located element.
 */
export interface ElementPositionError {
    /** Positional misalignment error [m]. */
    position?: Position,
    /** Angular misalignment error [rad]. */
    rotation?: Rotation,
}


/**
 * Survey-measured position and rotation of an element. Structure is identical to ElementPositionError.
 */
export interface ElementSurvey {
    /** Surveyed position. */
    position?: Position,
    /** Surveyed rotation. */
    rotation?: Rotation,
}


/**
 * Positions an element relative to a named reference element's local frame. The ``offset`` field is expressed in the reference element's local frame at the chosen ``point`` (start / middle / end).  Use ``world_offset`` instead to supply an offset already in global world coordinates.
 */
export interface ReferencePlacement {
    /** Name of the reference element. */
    element: string,
    /** Which point on the reference element to use as the origin frame: 'start', 'middle', or 'end'. */
    point?: string,
    /** Offset expressed in the reference element's local frame at the chosen point. */
    offset?: Position,
    /** Offset already expressed in global world coordinates. */
    world_offset?: Position,
    /** Scalar offset [m] along the local beam direction (s-axis) from the reference point.  Equivalent to ``offset: [0, 0, s_offset]`` but expressed as a single number.  Mutually exclusive with ``offset`` and ``world_offset``. */
    s_offset?: number,
}


/**
 * Physical placement data: position, rotation, length, and associated survey / alignment-error information.
 */
export interface PhysicalElement {
    /** Longitudinal midpoint (centre) of the element. Also accepted as ``position`` or ``centre`` in YAML. */
    middle?: Position,
    /** Datum reference position. */
    datum?: Position,
    /** Local rotation in the global frame. */
    rotation?: Rotation,
    /** Accumulated global rotation including parent-frame contributions. */
    global_rotation?: Rotation,
    /** Alignment errors. */
    error?: ElementPositionError,
    /** Survey-measured position and rotation. */
    survey?: ElementSurvey,
    /** Effective length along the beam axis [m]. */
    length?: number,
    /** Bending angle in the horizontal plane [rad]. Derived from ``magnetic.angle`` when available. */
    physical_angle?: number,
    /** Place this element relative to another element's frame instead of using absolute world coordinates.  Mutually exclusive with ``middle``/``position``/``centre`` and ``s``. */
    reference_placement?: ReferencePlacement,
    /** Arc-length position [m] along the design trajectory (s=0 at the global origin along +Z).  Alternative to absolute world coordinates (``middle``/``position``/``centre``) and ``reference_placement``. Converted to {x,y,z} by LAURA during lattice assembly. */
    s?: number,
    /** Which point of the element the ``s`` value refers to: ``start``, ``middle``, or ``end``.  Defaults to ``middle``. */
    s_point?: string,
}


/**
 * A single process-variable entry mapping a logical name to a control-system PV identifier.
 */
export interface ControlVariable {
    /** Protocol-specific PV name (e.g., EPICS PV address). */
    identifier?: string,
    /** Data type, held as a Python type and serialised by name (e.g., ``float``, ``int``, ``str``). */
    dtype?: string,
    /** Control-system protocol (e.g., ``EPICS``, ``Tango``). */
    protocol?: string,
    /** Physical units string (e.g., ``A``, ``T/m``). */
    units?: string,
    /** Human-readable description. */
    description?: string,
    /** Whether the variable is read-only. */
    read_only?: boolean,
    /** Last-read value. Scalar for most control types; a list for ``waveform``. */
    value?: string,
    /** Kind of quantity this variable carries. Accepted in YAML as ``type``. */
    control_type?: string,
    /** Dotted attribute path on the owning element that ``expression`` writes to (e.g., ``magnetic.k1l``). Not a set-point value. */
    target?: string,
    /** Expression graph computing the value written to ``target``, as nested mappings of the form ``{op: mul, args: [<symbol>, <symbol>]}``, where a symbol is a variable name or a dotted attribute path. Operators are ``add``, ``sub``, ``mul``, ``truediv`` and ``pow``. */
    expression?: string,
    /** Mapping of state name to underlying control-system value, for ``control_type: state``. */
    states?: string,
    /** Name of the readback variable this set-point drives. */
    readback?: string,
    /** Name of the set-point variable this readback follows. */
    setpoint?: string,
    /** Signal generating this variable's value over time, as ``{function: <import path>, **kwargs}`` -- see ``laura.utils.signals``. Stored with ``function`` as a fully qualified import path so it resolves without LAURA. */
    update?: string,
    /** Response model describing how this variable's readback follows its set-point, as ``{model: <import path>, **kwargs}`` -- see ``laura.utils.dynamics``. Only meaningful alongside ``readback`` or ``setpoint``. */
    dynamics?: string,
}


/**
 * Collection of process-variable definitions for an element's control interface.
 */
export interface ControlsInformation {
    /** Named control variables keyed by logical name. */
    variables?: ControlVariable[],
}


/**
 * Shutter interlock configuration.
 */
export interface ShutterElement {
    /** Names of the interlocks guarding this shutter. */
    interlocks?: string[],
}


/**
 * Vacuum valve configuration (no additional fields).
 */
export interface ValveElement {
}


/**
 * Lighting element (no additional fields currently defined).
 */
export interface LightingElement {
}


/**
 * Virtual Twiss-parameter matching point -- a zero-length marker that defines the desired optical functions at a location in the lattice.
 */
export interface TwissMatch extends PhysicalAcceleratorElement {
}


/**
 * Motorised positioning stage.
 */
export interface Stage extends PhysicalAcceleratorElement {
}


/**
 * Vacuum-pressure gauge.
 */
export interface VacuumGauge extends PhysicalAcceleratorElement {
}


/**
 * Laser system element (full laser setup including beam parameters).
 */
export interface Laser extends PhysicalAcceleratorElement {
    /** Laser-beam parameters. */
    laser?: LaserElement,
}


/**
 * Beam or laser shutter with interlock logic.
 */
export interface Shutter extends PhysicalAcceleratorElement {
    /** Shutter interlock configuration. */
    shutter?: ShutterElement,
}


/**
 * Transverse aperture geometry for drift-space checks and collimators.
 */
export interface ApertureElement {
    /** Number of aperture sub-elements (e.g., for multi-leaf collimators). */
    number_of_elements?: number,
    /** Full horizontal aperture [m]. */
    horizontal_size?: number,
    /** Full vertical aperture [m]. */
    vertical_size?: number,
    /** Cross-sectional aperture shape. */
    shape?: string,
    /** Radius for circular apertures [m]. */
    radius?: number,
    /** Upstream / inner extent [m]. */
    negative_extent?: number,
    /** Downstream / outer extent [m]. */
    positive_extent?: number,
}


/**
 * Vacuum gate valve.
 */
export interface Valve extends PhysicalAcceleratorElement {
    /** Valve configuration. */
    valve?: ValveElement,
}


/**
 * Virtual survey marker -- a zero-length reference point used for alignment.
 */
export interface Marker extends PhysicalAcceleratorElement {
}


/**
 * Mechanical aperture restriction in the beam pipe.
 */
export interface Aperture extends PhysicalAcceleratorElement {
    /** Aperture geometry parameters. */
    aperture?: ApertureElement,
}


/**
 * Movable collimator jaw (extends Aperture).
 */
export interface Collimator extends Aperture {
}


/**
 * Field-free drift space between elements.
 */
export interface Drift extends PhysicalAcceleratorElement {
}


/**
 * Experimental-hall lighting element.
 */
export interface Lighting extends StandardElement {
    /** Lighting configuration. */
    lights?: LightingElement,
}


/**
 * Generic power-supply unit providing control/setpoint-driven outputs (for example current/voltage) to other accelerator components.
 */
export interface PowerSupply extends StandardElement {
}


/**
 * An ordered list of element names defining a contiguous beamline section.
 */
export interface SectionLattice {
    /** Unique section name. */
    name: string,
    /** Name of the master lattice this section belongs to. */
    master_lattice?: string,
    /** Ordered list of element names in this section. */
    elements?: string[],
}


/**
 * An ordered list of section names defining a beamline layout (a contiguous sequence of sections).
 */
export interface MachineLayout {
    /** Unique layout name. */
    name: string,
    /** Name of the master lattice this layout belongs to. */
    master_lattice?: string,
    /** Ordered list of section names. */
    sections?: string[],
}


/**
 * Top-level container for a complete accelerator lattice: elements, sections, layouts, and named lattice configurations.
 */
export interface MachineModel {
    /** All elements in the machine, keyed by name. */
    elements?: AcceleratorElementName[],
    /** All named beamline sections. */
    sections?: SectionLatticeName[],
    /** All named beamline layouts. */
    layouts?: MachineLayoutName[],
}


/**
 * Base simulation attributes: field-map files and reference positions for tracking codes.
 */
export interface SimulationElement {
    /** Path to the 3-D field-map file. */
    field_definition?: string,
    /** Path to the wakefield impedance file. */
    wakefield_definition?: string,
    /** Whether the wakefield named by wakefield_definition is applied. Set false to track the element without its wakefield while keeping the definition itself. */
    wakefield_enable?: boolean,
    /** Longitudinal origin of the field map [m]. */
    field_reference_position?: string,
    /** Multiplicative scale factor applied to the field map. */
    scale_field?: number,
}


/**
 * Simulation attributes specific to magnets: integrator settings, fringe-field model, and radiation flags.
 */
export interface MagnetSimulationElement extends SimulationElement {
    /** Number of integration kicks. */
    n_kicks?: number,
    /** Field amplitude scaling for magnet tracking. */
    field_amplitude?: number,
    /** Number of longitudinal slices for thick-lens tracking. */
    n_slices?: number,
    /** Number of smoothing passes applied to the field map (ASTRA Q_smooth / S_smooth). */
    smooth?: number,
    /** Fringe-field integral for edge focussing. */
    edge_field_integral?: number,
    /** Enable entrance-edge focussing effects. */
    edge1_effects?: boolean,
    /** Enable exit-edge focussing effects. */
    edge2_effects?: boolean,
    /** Enable synchrotron-radiation energy loss. */
    sr_enable?: boolean,
    /** Enable incoherent synchrotron-radiation emittance growth. */
    isr_enable?: boolean,
    /** Enable coherent synchrotron radiation. */
    csr_enable?: boolean,
    /** Number of longitudinal bins for the CSR mesh. */
    csr_bins?: number,
    /** Order of the symplectic integrator. */
    integration_order?: number,
    /** Include higher-order (sextupole+) field components. */
    nonlinear?: boolean,
    /** Half-width of the current-profile smoothing kernel. */
    smoothing_half_width?: number,
    /** Polynomial order of the edge-field expansion. */
    edge_order?: number,
    /** Longitudinal step-size override for thick-lens integration [m]. */
    deltaL?: number,
    /** Number of points used to smooth the field map [ASTRA]. */
    smooth_points?: number,
}


/**
 * Simulation attributes for RF cavity elements.
 */
export interface RFCavitySimulationElement extends SimulationElement {
    /** Time column in the wake file. */
    t_column?: string,
    /** Longitudinal position column in the wake file. */
    z_column?: string,
    /** Horizontal wake column in the wake file. */
    wx_column?: string,
    /** Vertical wake column in the wake file. */
    wy_column?: string,
    /** Longitudinal wake column in the wake file. */
    wz_column?: string,
    /** Number of cavity kicks to apply. */
    n_kicks?: number,
    /** Number of longitudinal space-charge bins. */
    lsc_bins?: number,
    /** Flag indicating whether the cavity changes reference momentum. */
    change_p0?: number,
    /** Apply entrance focusing. */
    end1_focus?: number,
    /** Apply exit focusing. */
    end2_focus?: number,
    /** Cavity body focusing model. */
    body_focus_model?: string,
    /** Number of current bins. */
    current_bins?: number,
    /** Flag indicating current-bin interpolation. */
    interpolate_current_bins?: number,
    /** Flag indicating current-bin smoothing. */
    smooth_current_bins?: number,
    /** Cavity smoothing parameter. */
    smooth?: number,
    /** Peak longitudinal electric field. */
    ez_peak?: number,
    /** Cavity field file name. */
    field_file_name?: string,
    /** Wake file name. */
    wakefile?: string,
    /** Longitudinal wake file name. */
    zwakefile?: string,
    /** Transverse wake file name. */
    trwakefile?: string,
    /** Cavity field amplitude. */
    field_amplitude: number,
}


/**
 * Simulation attributes for passive wakefield structures.
 */
export interface WakefieldSimulationElement extends SimulationElement {
    /** Time column in the wake file. */
    t_column?: string,
    /** Longitudinal position column in the wake file. */
    z_column?: string,
    /** Horizontal wake column in the wake file. */
    wx_column?: string,
    /** Vertical wake column in the wake file. */
    wy_column?: string,
    /** Longitudinal wake column in the wake file. */
    wz_column?: string,
    /** Allow beams longer than the wakefield. */
    allow_long_beam?: boolean,
    /** Use bunched beam mode. */
    bunched_beam?: boolean,
    /** Allow wakefield to change bunch momentum. */
    change_momentum?: boolean,
    /** Wake scaling factor. */
    factor?: number,
    /** Interpolate points in wake file. */
    interpolate?: boolean,
    /** Factor by which to scale wake kicks. */
    scale_kick?: number,
    /** x-component of the longitudinal direction vector. */
    scale_field_ex?: number,
    /** y-component of the longitudinal direction vector. */
    scale_field_ey?: number,
    /** z-component of the longitudinal direction vector. */
    scale_field_ez?: number,
    /** x-component of the horizontal direction vector. */
    scale_field_hx?: number,
    /** y-component of the horizontal direction vector. */
    scale_field_hy?: number,
    /** z-component of the horizontal direction vector. */
    scale_field_hz?: number,
    /** Interpolation between equidistant and equal-charge grids. */
    equal_grid?: number,
    /** Interpolation method for ASTRA. */
    interpolation_method?: number,
    /** Smoothing parameter for Gaussian interpolation. */
    smooth?: number,
    /** Sub-binning parameter. */
    subbins?: number,
}


/**
 * Simulation attributes for field-free drift sections.
 */
export interface DriftSimulationElement extends SimulationElement {
    /** Number of bins for LSC calculations. */
    lsc_bins?: number,
    /** Flag to allow interpolation of computed LSC wake. */
    lsc_interpolate?: number,
    /** Enable CSR drift calculations. */
    csr_enable?: boolean,
    /** Enable LSC drift calculations. */
    lsc_enable?: boolean,
    /** Use Stupakov formula. */
    use_stupakov?: number,
    /** Step size for CSR calculations. */
    csrdz?: number,
    /** High-frequency cutoff start for LSC. */
    lsc_high_frequency_cutoff_start?: number,
    /** High-frequency cutoff end for LSC. */
    lsc_high_frequency_cutoff_end?: number,
    /** Low-frequency cutoff start for LSC. */
    lsc_low_frequency_cutoff_start?: number,
    /** Low-frequency cutoff end for LSC. */
    lsc_low_frequency_cutoff_end?: number,
}


/**
 * Simulation attributes for beam-diagnostic elements.
 */
export interface DiagnosticSimulationElement extends SimulationElement {
    /** Output filename for diagnostic data. */
    output_filename?: string,
}


/**
 * Simulation attributes for plasma-accelerator stages.
 */
export interface PlasmaSimulationElement extends SimulationElement {
    /** Wakefield model identifier. */
    wakefield_model?: string,
    /** Pusher used to evolve bunch particles in time. */
    bunch_pusher?: string,
    /** Time-step control for bunch evolution (or 'auto'). */
    dt_bunch?: string,
    /** Number of distribution dumps during the plasma stage. */
    n_out?: number,
    /** Minimum longitudinal position [m]. */
    min_longitudinal_position?: number,
    /** Maximum longitudinal position [m]. */
    max_longitudinal_position?: number,
    /** Number of grid points in the longitudinal direction. */
    n_longitudinal?: number,
    /** Number of grid points in the radial direction. */
    n_radial?: number,
    /** Number of plasma particles per cell. */
    plasma_particles_per_cell?: number,
    /** Radial extent of the simulation box [m]. */
    r_max?: number,
    /** Maximum radial extension of the plasma column. */
    r_max_plasma?: number,
    /** Interval for plasma wakefield updates. */
    dz_fields?: number,
    /** Pusher used to evolve the plasma in time. */
    plasma_pusher?: string,
}


/**
 * Simulation attributes for Twiss-matching points.
 */
export interface TwissMatchSimulationElement extends SimulationElement {
    /** Horizontal beta. */
    beta_x?: number,
    /** Vertical beta. */
    beta_y?: number,
    /** Horizontal alpha. */
    alpha_x?: number,
    /** Vertical alpha. */
    alpha_y?: number,
    /** Horizontal dispersion. */
    eta_x?: number,
    /** Vertical dispersion. */
    eta_y?: number,
    /** Horizontal dispersion derivative. */
    eta_xp?: number,
    /** Vertical dispersion derivative. */
    eta_yp?: number,
    /** Compute transform from tracked beam properties. */
    from_beam?: boolean,
}


/**
 * Base class for all magnetic focusing and bending elements. (Named ``MagnetBaseElement`` in the schema to avoid collision with the ``magnetic`` composition-model class; maps to ``Magnet`` in Python.)
 */
export interface Magnet extends PhysicalAcceleratorElement {
    /** Magnetic field parameters. */
    magnetic?: MagneticElement,
    /** Degaussing-cycle parameters. */
    degauss?: DegaussableElement,
}


/**
 * Individual multipole field component, characterised by order and integrated normal / skew strengths at a reference radius.
 */
export interface Multipole {
    /** Multipole order (0 = dipole, 1 = quadrupole, ?). */
    order?: number,
    /** Integrated normal (upright) multipole strength [T.m^{1-n}]. */
    normal?: number,
    /** Integrated skew (rotated) multipole strength [T.m^{1-n}]. */
    skew?: number,
    /** Reference radius for multipole normalisation [m]. */
    radius?: number,
}


/**
 * Complete set of integrated multipole strengths up to decapole order, as named slots for efficient element look-up.
 */
export interface Multipoles {
    /** Integrated dipole field. */
    K0L?: Multipole,
    /** Integrated quadrupole gradient. */
    K1L?: Multipole,
    /** Integrated sextupole strength. */
    K2L?: Multipole,
    /** Integrated octupole strength. */
    K3L?: Multipole,
    /** Integrated decapole strength. */
    K4L?: Multipole,
}


/**
 * Polynomial fit of integrated field strength as a function of magnet current.
 */
export interface FieldIntegral {
    /** Polynomial coefficients ordered from lowest to highest degree: ``FieldIntegral = sum c_n . I^n``. */
    coefficients?: number[],
}


/**
 * Bi-linear saturation model mapping magnet current to integrated field strength (K-value conversion).
 */
export interface LinearSaturationFit {
    /** Linear slope of the unsaturated region. */
    m?: number,
    /** Current at which saturation begins [A]. */
    I_max?: number,
    /** Saturation fraction (slope ratio below/above I_max). */
    f?: number,
    /** Quadratic saturation coefficient. */
    a?: number,
    /** Current offset [A]. */
    I0?: number,
    /** Constant offset term. */
    d?: number,
    /** Effective magnetic length [m]. */
    L?: number,
}


/**
 * Magnetic field parameters for a beamline magnet, including multipole components, field integrals, and geometric edge parameters.
 */
export interface MagneticElement {
    /** Principal multipole order (0 = dipole, 1 = quad, ?). */
    order?: number,
    /** Whether the magnet is rotated 45? to produce a skew field component. */
    skew?: boolean,
    /** Magnetic (effective) length [m]. */
    length?: number,
    /** Integrated multipole field components. */
    multipoles?: Multipoles,
    /** Systematic (design) multipole errors at the reference radius. */
    systematic_multipoles?: Multipoles,
    /** Random multipole errors at the reference radius. */
    random_multipoles?: Multipoles,
    /** Polynomial calibration of integrated field vs. current. */
    field_integral_coefficients?: FieldIntegral,
    /** Bi-linear saturation calibration. */
    linear_saturation_coefficients?: LinearSaturationFit,
    /** Power-supply settle time after a change [s]. */
    settle_time?: number,
    /** Fringe-field entrance edge angle [rad]. */
    entrance_edge_angle?: string,
    /** Fringe-field exit edge angle [rad]. */
    exit_edge_angle?: string,
    /** Full gap between pole faces [m]. */
    gap?: number,
    /** Magnet bore radius [m]. */
    bore?: number,
    /** Principal bending / focusing plane (``Horizontal``, ``Vertical``, or ``Combined``). */
    plane?: string,
    /** Physical width of the magnet in the bending plane [m]. */
    width?: number,
    /** Global tilt about the beam axis [rad]. */
    tilt?: number,
    /** Enge fringe-field integral parameter (dimensionless). */
    edge_field_integral?: number,
    /** Coefficient controlling the fringe-field roll-off rate. */
    fringe_field_coefficient?: number,
    /** Peak field gradient [T/m] (quads) or peak field [T] (dipoles). */
    gradient?: number,
    /** Integrated bending angle [rad]. Dipoles only. Part of the data model (lattice YAML may set it), but derived from multipoles.K0L rather than stored: the MagneticElement wrapper implements it as a read/write property so a symbolic bend angle survives round-tripping and reads follow the global resolution mode. Listed in _PYDANTIC_EXCLUDED_SLOTS in generate_pydantic.py so the generated base does not also declare it as a field, which would make pydantic treat the property object as the field default. */
    angle?: number,
}


/**
 * Degaussing (demagnetisation cycle) parameters for magnets that require a field-reset procedure.
 */
export interface DegaussableElement {
    /** Current tolerance band during the degauss cycle [A]. */
    tolerance?: number,
    /** Sequence of peak currents applied during the degauss cycle [A]. */
    values?: number[],
    /** Number of degauss steps per half-cycle. */
    steps?: number,
}


/**
 * Accelerating RF cavity.
 */
export interface RFCavity extends PhysicalAcceleratorElement {
    /** RF structure parameters. */
    cavity?: RFCavityElement,
}


/**
 * Transverse-deflecting (streak) RF cavity.
 */
export interface RFDeflectingCavity extends RFCavity {
    /** RF structure parameters. */
    cavity?: RFDeflectingCavityElement,
}


/**
 * Passive wakefield structure (dielectric, corrugated, etc.).
 */
export interface Wakefield extends PhysicalAcceleratorElement {
    /** Wakefield structure parameters. */
    cavity?: WakefieldElement,
}


/**
 * Low-level RF (LLRF) controller.
 */
export interface LowLevelRF extends StandardElement {
    /** LLRF parameters. */
    llrf?: LowLevelRFElement,
}


/**
 * RF modulator (klystron driver) element.
 */
export interface RFModulator extends StandardElement {
    /** Modulator parameters. */
    modulator?: RFModulatorElement,
}


/**
 * RF protection system element.
 */
export interface RFProtection extends StandardElement {
    /** RF protection parameters. */
    protection?: RFProtectionElement,
}


/**
 * RF timing heartbeat / signal-monitor element.
 */
export interface RFHeartbeat extends StandardElement {
    /** RF heartbeat parameters. */
    heartbeat?: RFHeartbeatElement,
}


/**
 * Proportional-integral-derivative (PID) feedback controller.
 */
export interface PID extends StandardElement {
    /** PID gain parameters. */
    pid?: PIDElement,
}


/**
 * RF cavity accelerating-structure parameters.
 */
export interface RFCavityElement {
    /** Length of a single cell [m]. */
    cell_length?: number,
    /** Length of the coupling cell [m]. */
    coupling_cell_length?: number,
    /** Design Lorentz factor. */
    design_gamma?: number,
    /** Design peak power [W]. */
    design_power?: number,
    /** Operating frequency [Hz]. */
    frequency?: number,
    /** Number of cells. */
    n_cells?: number,
    /** On-crest phase offset providing maximum energy gain [deg]. */
    crest?: number,
    /** Operating phase offset [deg]. */
    phase?: number,
    /** Shunt impedance [M?/m]. */
    shunt_impedance?: number,
    /** Mode fraction numerator. */
    mode_numerator?: number,
    /** Mode fraction denominator. */
    mode_denominator?: number,
    /** RF structure type (e.g., ``SW`` standing-wave, ``TW`` travelling-wave). */
    structure_type?: string,
    /** Attenuation constant ? of a travelling-wave structure [Np/m]. */
    attenuation_constant?: number,
    /** Calibration constant relating measured power to cavity gradient. */
    power_calibration?: number[],
    /** Calibration relating measured signal to gradient [MV/m per a.u.]. */
    gradient_calibration?: number[],
}


/**
 * Passive wakefield structure parameters.
 */
export interface WakefieldElement {
    /** Length of a single cell [m]. */
    cell_length?: number,
    /** Number of cells. */
    n_cells?: number,
    /** Length of the coupling cell [m]. */
    coupling_cell_length?: number,
}


/**
 * Transverse-deflecting RF cavity parameters -- a subset of RFCavityElement for streak-mode operation.
 */
export interface RFDeflectingCavityElement {
    /** Length of a single cell [m]. */
    cell_length?: number,
    /** Length of the coupling cell [m]. */
    coupling_cell_length?: number,
    /** On-crest phase offset providing maximum energy gain [deg]. */
    crest?: number,
    /** Design Lorentz factor. */
    design_gamma?: number,
    /** Design peak power [W]. */
    design_power?: number,
    /** Operating frequency [Hz]. */
    frequency?: number,
    /** Number of cells. */
    n_cells?: number,
    /** Operating phase offset [deg]. */
    phase?: number,
    /** Shunt impedance [M?/m]. */
    shunt_impedance?: number,
    /** Mode fraction numerator. */
    mode_numerator?: number,
    /** Mode fraction denominator. */
    mode_denominator?: number,
}


/**
 * PID feedback-controller parameters.
 */
export interface PIDElement {
    /** Proportional gain. */
    Kp?: number,
    /** Integral gain. */
    Ki?: number,
    /** Derivative gain. */
    Kd?: number,
    /** Forward channel index. */
    forward_channel?: number,
    /** Probe channel index. */
    probe_channel?: number,
    /** Enable command/value. */
    enable?: string,
    /** Disable command/value. */
    disable?: string,
    /** Phase tuning range. */
    phase_range?: PIDPhaseRange,
    /** Phase weighting range. */
    phase_weight_range?: PIDWeightRange,
}


/**
 * Numeric min/max range for PID phase control.
 */
export interface PIDPhaseRange {
    /** Minimum value. */
    min?: number,
    /** Maximum value. */
    max?: number,
}


/**
 * Numeric min/max range for PID phase weighting.
 */
export interface PIDWeightRange extends PIDPhaseRange {
}


/**
 * LLRF trace metadata.
 */
export interface Trace {
    /** Number of points in a trace. */
    data_size?: number,
    /** Number of one-record trace entries. */
    data_count?: number,
    /** Chunk size for one-record traces. */
    data_chunk_size?: number,
    /** Number of leading zeros in a trace. */
    number_of_start_zeros?: number,
}


/**
 * Names for LLRF channels 1..8.
 */
export interface ChannelNames {
    ch1?: string,
    ch2?: string,
    ch3?: string,
    ch4?: string,
    ch5?: string,
    ch6?: string,
    ch7?: string,
    ch8?: string,
}


/**
 * Start/end window timing definition.
 */
export interface LLRFTiming {
    /** Start time. */
    start?: number,
    /** End time. */
    end?: number,
}


/**
 * Collection of timing windows for key LLRF channels.
 */
export interface LLRFTimings {
    /** Timing for klystron forward power. */
    klystron_forward?: LLRFTiming,
    /** Timing for klystron reverse power. */
    klystron_reverse?: LLRFTiming,
    /** Timing for cavity forward power. */
    cavity_forward?: LLRFTiming,
    /** Timing for cavity reverse power. */
    cavity_reverse?: LLRFTiming,
    /** Timing for cavity probe. */
    cavity_probe?: LLRFTiming,
}


/**
 * Low-level RF (LLRF) system parameters.
 */
export interface LowLevelRFElement {
    /** Trace metadata. */
    trace?: Trace,
    /** Maximum allowed amplitude. */
    max_amplitude?: number,
    /** Channel labels. */
    channel_names?: ChannelNames,
    /** Cavity crest phase. */
    crest_phase?: number,
    /** Timing windows for LLRF channels. */
    timings?: LLRFTimings,
}


/**
 * RF modulator (klystron driver) parameters.
 */
export interface RFModulatorElement {
}


/**
 * RF protection system parameters.
 */
export interface RFProtectionElement {
    /** Protection system type. */
    prot_type?: string,
}


/**
 * RF heartbeat / timing-monitor element parameters.
 */
export interface RFHeartbeatElement {
}


/**
 * Base class for all beam-diagnostic instruments.
 */
export interface Diagnostic extends PhysicalAcceleratorElement {
    /** Instrument-specific diagnostic parameters. */
    diagnostic?: DiagnosticElement,
}


/**
 * Beam-position monitor (BPM).
 */
export interface BeamPositionMonitor extends Diagnostic {
    /** Instrument-specific diagnostic parameters. */
    diagnostic?: BPMDiagnosticElement,
}


/**
 * Beam-arrival-time monitor (BAM).
 */
export interface BeamArrivalMonitor extends Diagnostic {
    /** Instrument-specific diagnostic parameters. */
    diagnostic?: BAMDiagnosticElement,
}


/**
 * Bunch-length monitor (BLM / CDR detector).
 */
export interface BunchLengthMonitor extends Diagnostic {
    /** Instrument-specific diagnostic parameters. */
    diagnostic?: BLMDiagnosticElement,
}


/**
 * Camera-based beam-profile monitor.
 */
export interface Camera extends Diagnostic {
    /** Instrument-specific diagnostic parameters. */
    diagnostic?: CameraDiagnosticElement,
}


/**
 * Scintillator or OTR screen with an associated camera.
 */
export interface Screen extends Diagnostic {
    /** Instrument-specific diagnostic parameters. */
    diagnostic?: ScreenDiagnosticElement,
}


/**
 * Base class for charge-measurement diagnostics.
 */
export interface ChargeDiagnostic extends Diagnostic {
    /** Instrument-specific diagnostic parameters. */
    diagnostic?: ChargeDiagnosticElement,
}


/**
 * Wall-current monitor (WCM) for non-destructive charge measurement.
 */
export interface WallCurrentMonitor extends ChargeDiagnostic {
}


/**
 * Faraday cup for destructive charge measurement.
 */
export interface FaradayCupMonitor extends ChargeDiagnostic {
}


/**
 * Integrated current transformer (ICT) for non-destructive single-shot charge measurement.
 */
export interface IntegratedCurrentTransformer extends ChargeDiagnostic {
}


/**
 * Photon intensity monitor.
 */
export interface PhotonMonitor extends Diagnostic {
    /** Instrument-specific diagnostic parameters. */
    intensity?: PhotonIntensityMonitorDiagnostic,
}


/**
 * Base class for diagnostic instrument sub-models.  Concrete sub-models extend this with instrument-specific fields.
 */
export interface DiagnosticElement {
}


/**
 * Beam-position monitor (BPM) diagnostic data.
 */
export interface BPMDiagnosticElement extends DiagnosticElement {
    /** BPM type (e.g., ``Stripline``, ``Cavity``, ``Button``). Accepted in YAML as ``bpm_type``. */
    type?: string,
}


/**
 * Beam-arrival monitor (BAM) diagnostic data.
 */
export interface BAMDiagnosticElement extends DiagnosticElement {
    /** BAM type. Accepted in YAML as ``bam_type``. */
    type?: string,
}


/**
 * Photon intensity monitor diagnostic data.
 */
export interface PhotonIntensityMonitorDiagnostic extends DiagnosticElement {
    /** Photon intensity monitor type. Accepted in YAML as ``intensity_monitor_type``. */
    type?: string,
    /** Measured photon intensity. */
    intensity?: number,
}


/**
 * Bunch-length monitor (BLM) diagnostic data.
 */
export interface BLMDiagnosticElement extends DiagnosticElement {
    /** BLM type (e.g., ``CDR``). Accepted in YAML as ``blm_type``. */
    type?: string,
}


/**
 * Scintillator or OTR screen diagnostic data.
 */
export interface ScreenDiagnosticElement extends DiagnosticElement {
    /** Screen type (e.g., ``OTR``, ``YAG``). */
    type?: string,
    /** Whether the screen has an associated camera. */
    has_camera?: boolean,
    /** Name of the associated camera element. */
    camera_name?: string,
    /** List of attached devices. */
    devices?: string[],
}


/**
 * Charge-measurement diagnostic data (base for ICT, FCM, WCM).
 */
export interface ChargeDiagnosticElement extends DiagnosticElement {
    /** Charge-diagnostic type. Accepted in YAML as ``charge_type``. */
    type?: string,
}


/**
 * Indices into camera pixel-analysis result arrays.
 */
export interface CameraPixelResultsIndices {
    /** Beam centroid index in x. */
    x?: number,
    /** Beam centroid index in y. */
    y?: number,
    /** Beam sigma index in x. */
    x_sigma?: number,
    /** Beam sigma index in y. */
    y_sigma?: number,
    /** Beam covariance index. */
    covariance?: number,
}


/**
 * Names of camera pixel-analysis result arrays.
 */
export interface CameraPixelResultsNames {
    /** Beam centroid name in x. */
    x?: string,
    /** Beam centroid name in y. */
    y?: string,
    /** Beam sigma name in x. */
    x_sigma?: string,
    /** Beam sigma name in y. */
    y_sigma?: string,
    /** Beam covariance name. */
    covariance?: string,
}


/**
 * Camera analysis mask parameters.
 */
export interface CameraMask {
    /** Center of the mask in pixels [x, y]. */
    middle?: number[],
    /** Mask radius in pixels [x, y]. */
    radius?: number[],
    /** Maximum mask radius in pixels [x, y]. */
    maximum?: number[],
    /** If True, use maximum mask radius constraints. */
    use_maximum_values?: boolean,
}


/**
 * Camera sensor hardware configuration.
 */
export interface CameraSensor {
    /** Raw sensor pixel count in x. */
    x_pixels?: number,
    /** Raw sensor pixel count in y. */
    y_pixels?: number,
    /** Pixel binning factor in x. */
    x_scale_factor?: number,
    /** Pixel binning factor in y. */
    y_scale_factor?: number,
    /** Average pixel value for beam detection. */
    beam_pixel_average?: number,
    /** Sensor optical center in pixels [x, y]. */
    middle?: number[],
    /** Pixel-to-mm scale factor in x. */
    x_pixels_to_mm?: number,
    /** Pixel-to-mm scale factor in y. */
    y_pixels_to_mm?: number,
    /** Minimum pixel positions [x, y]. */
    minimum?: number[],
    /** Maximum pixel positions [x, y]. */
    maximum?: number[],
    /** Camera bit depth. */
    bit_depth?: number,
    /** Operating center positions in pixels [x, y]. */
    operating_middle?: number[],
    /** Mechanical center of the camera in pixels [x, y]. */
    mechanical_middle?: number[],
}


/**
 * Camera diagnostic data, including sensor parameters, analysis mask, and pixel-to-mm scale factors.
 */
export interface CameraDiagnosticElement extends DiagnosticElement {
    /** Camera type / model string (e.g., ``PCO``, ``Manta``). Accepted in YAML as ``CAM_TYPE``. */
    type?: string,
    /** Image width reported by the control system [pix]. */
    x_pixels?: number,
    /** Image height reported by the control system [pix]. */
    y_pixels?: number,
    /** Camera rotation relative to the screen plane [deg]. */
    rotation?: number,
    /** True if the image is mirrored left-right. */
    flipped_horizontally?: boolean,
    /** True if the image is mirrored top-bottom. */
    flipped_vertically?: boolean,
    /** Name of the screen element to which this camera is attached. */
    screen_name?: string,
    /** True if the camera mount includes an LED backlight. */
    has_led?: boolean,
    /** Indices of pixel analysis result arrays. */
    pixel_results_indices?: CameraPixelResultsIndices,
    /** Names of pixel analysis result arrays. */
    pixel_results_names?: CameraPixelResultsNames,
    /** Camera analysis mask configuration. */
    mask?: CameraMask,
    /** Camera sensor hardware configuration. */
    sensor?: CameraSensor,
}


/**
 * Laser-driven plasma-accelerator stage.
 */
export interface Plasma extends PhysicalAcceleratorElement {
    /** Plasma channel parameters. */
    plasma?: PlasmaElement,
    /** Laser driving the plasma stage. */
    laser?: LaserElement,
}


/**
 * Laser pulse-energy diagnostic (photodiode / pyroelectric).
 */
export interface LaserEnergyMeter extends StandardElement {
    /** Energy-meter instrument parameters. */
    laser?: LaserEnergyMeterElement,
}


/**
 * Half-wave plate for laser polarisation rotation.
 */
export interface LaserHalfWavePlate extends StandardElement {
    /** Half-wave plate parameters. */
    laser?: LaserHalfWavePlateElement,
}


/**
 * Laser steering or focusing mirror.
 */
export interface LaserMirror extends StandardElement {
    /** Mirror steering parameters. */
    laser?: LaserMirrorElement,
}


/**
 * Mirror steering parameters for a laser mirror.
 */
export interface LaserMirrorElement {
    /** Maximum step size for mirror adjustment. */
    step_max?: number,
    /** Mirror sense/interlock configuration. */
    sense?: LaserMirrorSense,
    /** Vertical control channel index. */
    vertical_channel?: number,
    /** Horizontal control channel index. */
    horizontal_channel?: number,
}


/**
 * Mirror sense switch values.
 */
export interface LaserMirrorSense {
    /** Left sense value. */
    left?: number,
    /** Right sense value. */
    right?: number,
    /** Up sense value. */
    up?: number,
    /** Down sense value. */
    down?: number,
}


/**
 * Laser power attenuator (waveplate + polariser combination).
 */
export interface LaserAttenuator extends StandardElement {
    /** Maximum attenuation angle [deg]. */
    maximum?: number,
    /** Minimum attenuation angle [deg]. */
    minimum?: number,
}


/**
 * Laser-beam parameters (wavelength, pulse energy, profile, etc.) for a laser element or laser-driven plasma stage.
 */
export interface LaserElement {
    /** Initial longitudinal position of the laser pulse [m]. */
    initial_position?: number,
    /** Laser beam waist (1/e^2 radius) [m]. */
    waist?: number,
    /** Laser wavelength [m]. */
    wavelength?: number,
    /** Laser pulse energy [J]. */
    pulse_energy?: number,
    /** Pulse duration at FWHM [s]. */
    pulse_duration_fwhm?: number,
    /** Focal (waist) position along the propagation axis [m]. */
    focal_position?: number,
    /** Carrier-envelope phase [rad]. */
    cep_phase?: number,
    /** Laser polarization state. */
    polarization?: string,
    /** Transverse intensity profile model. */
    profile_type?: string,
    /** Radial Laguerre-Gaussian mode index p (for ``profile_type = laguerre-gaussian``). */
    laguerre_polynomial_order_p?: number,
    /** Flatness order N of a flattened-Gaussian profile (for ``profile_type = flattened-gaussian``). */
    flatness?: number,
}


/**
 * Laser energy-meter sub-model (no additional fields).
 */
export interface LaserEnergyMeterElement {
}


/**
 * Half-wave plate sub-model (no additional fields).
 */
export interface LaserHalfWavePlateElement {
}


/**
 * Plasma channel parameters for a laser-driven plasma-accelerator stage.
 */
export interface PlasmaElement {
    /** Plasma (electron) number density [m^-^3]. */
    density?: number,
    /** Plasma species name (e.g., ``electron``). */
    species?: string,
    /** Entrance density-ramp length [m]. */
    ramp_up?: number,
    /** Flat-top plateau length [m]. */
    plateau?: number,
    /** Exit density-ramp length [m]. */
    ramp_down?: number,
    /** Exponential decay length of the density ramp [m]. */
    ramp_decay_length?: number,
    /** If True, use a user-defined profile; if False, use a flat-top model. */
    density_profile?: boolean,
    /** Parabolic coefficient for a transverse density profile. */
    parabolic_coefficient?: number,
}



export interface DipoleMagnet extends MagneticElement {
}



export interface Dipole extends Magnet {
}



export interface QuadrupoleMagnet extends MagneticElement {
}



export interface Quadrupole extends Magnet {
}


/**
 * Sextupole magnet field, principal multipole order 2.
 */
export interface SextupoleMagnet extends MagneticElement {
}


/**
 * Sextupole chromaticity-correction magnet.
 */
export interface Sextupole extends Magnet {
}


/**
 * Octupole magnet field, principal multipole order 3.
 */
export interface OctupoleMagnet extends MagneticElement {
}


/**
 * Octupole magnet.
 */
export interface Octupole extends Magnet {
}


/**
 * Steering-corrector field. A dipole magnet whose order-0 multipole is addressed by beam plane: the normal component is the horizontal kick and the skew component is the vertical kick. Inherits from  Dipole_Magnet / MagneticElement.
 */
export interface CorrectorMagnet extends DipoleMagnet {
    /** Horizontal deflection [rad]. May be a functional expression. Derived from multipoles.K0L.normal. */
    horizontal_kick?: number,
    /** Vertical deflection [rad]. May be a functional expression. Derived from multipoles.K0L.skew. */
    vertical_kick?: number,
}


/**
 * Horizontal steering corrector.
 */
export interface HorizontalCorrector extends Dipole {
}


/**
 * Vertical steering corrector.
 */
export interface VerticalCorrector extends Dipole {
}


/**
 * The pair of steering-corrector fields inside one combined corrector. The two planes are separate magnets with separate windings, so they must not share a magnetic model: in the CLARA magnet table the horizontal and vertical halves of a single unit have different slope [units/A] and different magnetic lengths, so one shared calibration converts current to angle correctly for at most one of the two planes.
 */
export interface CombinedCorrectorMagnet {
    /** Horizontal-plane corrector field, with its own calibration. */
    horizontal?: CorrectorMagnet,
    /** Vertical-plane corrector field, with its own calibration. */
    vertical?: CorrectorMagnet,
}


/**
 * Combined horizontal/vertical steering corrector, naming the two single-plane correctors it stands in for.
 */
export interface CombinedCorrector extends Dipole {
    /** Name of the horizontal-plane corrector element. */
    Horizontal_Corrector?: string,
    /** Name of the vertical-plane corrector element. */
    Vertical_Corrector?: string,
}


/**
 * Solenoid integrated axial field components ``S0L``–``S12L`` [T.m].
 */
export interface SolenoidFields {
    /** Integrated solenoid field, order 0 [T.m]. */
    S0L?: number,
    /** Integrated solenoid field, order 1 [T.m]. */
    S1L?: number,
    /** Integrated solenoid field, order 2 [T.m]. */
    S2L?: number,
    /** Integrated solenoid field, order 3 [T.m]. */
    S3L?: number,
    /** Integrated solenoid field, order 4 [T.m]. */
    S4L?: number,
    /** Integrated solenoid field, order 5 [T.m]. */
    S5L?: number,
    /** Integrated solenoid field, order 6 [T.m]. */
    S6L?: number,
    /** Integrated solenoid field, order 7 [T.m]. */
    S7L?: number,
    /** Integrated solenoid field, order 8 [T.m]. */
    S8L?: number,
    /** Integrated solenoid field, order 9 [T.m]. */
    S9L?: number,
    /** Integrated solenoid field, order 10 [T.m]. */
    S10L?: number,
    /** Integrated solenoid field, order 11 [T.m]. */
    S11L?: number,
    /** Integrated solenoid field, order 12 [T.m]. */
    S12L?: number,
}


/**
 * Solenoid field model, including systematic and random field errors and the current-to-field calibration.
 */
export interface SolenoidMagnet {
    /** Magnetic length [m]. */
    length?: number,
    /** Principal solenoid multipole order. */
    order?: number,
    /** Nominal integrated axial field components. */
    fields?: SolenoidFields,
    /** Systematic field errors. */
    systematic_fields?: SolenoidFields,
    /** Random field errors. */
    random_fields?: SolenoidFields,
    /** Polynomial current-to-integrated-field coefficients. */
    field_integral_coefficients?: FieldIntegral,
    /** Linear-plus-saturation fit of field against current. */
    linear_saturation_coefficients?: LinearSaturationFit,
    /** Time to wait after a set before the field is stable [s]. */
    settle_time?: number,
}


/**
 * Solenoid focusing magnet.
 */
export interface Solenoid extends Magnet {
}


/**
 * Periodic wiggler/undulator field.
 */
export interface WigglerMagnet {
    /** Magnetic length [m]. */
    length?: number,
    /** Deflection parameter K. May be a functional expression. */
    strength?: number,
    /** Peak on-axis field [T]. */
    peak_magnetic_field?: number,
    /** Magnetic period length [m]. */
    period?: number,
    /** Number of full magnetic periods. */
    num_periods?: number,
    /** True for a helical device, False for planar. */
    helical?: boolean,
    /** Quadratic field roll-off in x [1/m^2]. */
    quadratic_roll_off_x?: number,
    /** Quadratic field roll-off in y [1/m^2]. */
    quadratic_roll_off_y?: number,
    /** Transverse field gradient in x [1/m]. */
    transverse_gradient_x?: number,
    /** Transverse field gradient in y [1/m]. */
    transverse_gradient_y?: number,
}


/**
 * Wiggler / undulator insertion device.
 */
export interface Wiggler extends Magnet {
    /** Drive laser, for laser-undulator (inverse-Compton) configurations. */
    laser?: LaserElement,
}


/**
 * Integrable-optics non-linear lens field.  See the MAD-X manual and Danilov/Nagaitsev, PAC2011 WEP070.
 */
export interface NonLinearLensMagnet {
    /** Magnetic length [m]. */
    length?: number,
    /** Integrated lens strength (MAD-X ``knll``). May be a functional expression. */
    integrated_strength?: number,
    /** Dimensional parameter setting the transverse scale (MAD-X ``cnll``). May be a functional expression. */
    dimensional_parameter?: number,
}


/**
 * Non-linear integrable-optics lens.
 */
export interface NonLinearLens extends Magnet {
}


/**
 * Power-supply electrical limits for a beamline element.
 */
export interface ElectricalElement {
    /** Minimum current [A]. */
    min_i?: number,
    /** Maximum current [A]. */
    max_i?: number,
    /** Read-back vs. set-point tolerance fraction (default 0.1 = 10 %). */
    read_tolerance?: number,
}


/**
 * Manufacturer and serial-number metadata.
 */
export interface ManufacturerElement {
    /** Name of the manufacturer. */
    manufacturer?: string,
    /** Manufacturer serial number. */
    serial_number?: string,
}


/**
 * Links to engineering drawings and design files.
 */
export interface ReferenceElement {
    /** Engineering-drawing identifiers or URIs. */
    drawings?: string[],
    /** Design-file paths or URIs. */
    design_files?: string[],
}


/**
 * Root base class for all LAURA accelerator elements.  Every lattice element is an instance of a concrete subclass identified by ``hardware_type``.
 */
export interface AcceleratorElement {
    /** Unique element name within the machine. */
    name: string,
    /** Functional category (e.g., ``Magnet``, ``Diagnostic``). */
    hardware_class: string,
    /** Python class name used for ELEMENT_REGISTRY dispatch.  Identifies the concrete subclass to instantiate when loading from YAML. */
    hardware_type?: string,
    /** Model or variant name within the hardware type (e.g., ``Generic``, ``TESLA``). */
    hardware_model?: string,
    /** Machine area label grouping related elements (e.g., ``LINAC``, ``BA1``). */
    machine_area?: string,
    /** Alternative internal name used by the control system when the physical name is inaccessible. */
    virtual_name?: string,
    /** Human-readable aliases for the element. Populated from ``name_alias`` in YAML. Accepts a single string or a list of strings. */
    alias?: string[],
    /** If set, this element is a logical sub-component of the named parent element. */
    subelement?: string,
    /** Signal types this element consumes (e.g. ``[current, voltage]``). */
    inputs?: string,
    /** Signal types this element produces (e.g. ``[power, phase]``). */
    outputs?: string,
    /** Names of elements feeding this one, whose ``outputs`` supply its ``inputs``. */
    upstream?: AcceleratorElementName[],
    /** Names of elements this one feeds; the inverse of ``upstream``. */
    downstream?: AcceleratorElementName[],
}


/**
 * Accelerator element with control-system, electrical, manufacturer, simulation, and reference sub-models.
 */
export interface StandardElement extends AcceleratorElement {
    /** Simulation / tracking attributes. */
    simulation?: SimulationElement,
    /** Power-supply electrical limits. */
    electrical?: ElectricalElement,
    /** Manufacturer and serial-number data. */
    manufacturer?: ManufacturerElement,
    /** Control-system process-variable definitions. */
    controls?: ControlsInformation,
    /** Links to design drawings and files. */
    reference?: ReferenceElement,
}


/**
 * Concrete schema counterpart of the Python ``Element`` wrapper class. Inherits standard element composition fields.
 */
export interface Element extends StandardElement {
}


/**
 * Accelerator element with a well-defined physical position and orientation in the beamline.
 */
export interface PhysicalAcceleratorElement extends Element {
    /** Position, rotation, and length data. */
    physical?: PhysicalElement,
}



