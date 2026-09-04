
from sqlalchemy import Column, Index, Table, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import *
from sqlalchemy.orm import declarative_base
from sqlalchemy.ext.associationproxy import association_proxy

Base = declarative_base()
metadata = Base.metadata


class ElectricalElement(Base):
    """
    Power-supply electrical limits for a beamline element.
    """
    __tablename__ = 'ElectricalElement'

    id = Column(Integer(), primary_key=True, autoincrement=True , nullable=False )
    min_i = Column(Float())
    max_i = Column(Float())
    read_tolerance = Column(Float())
    

    def __repr__(self):
        return f"ElectricalElement(id={self.id},min_i={self.min_i},max_i={self.max_i},read_tolerance={self.read_tolerance},)"



    


class ManufacturerElement(Base):
    """
    Manufacturer and serial-number metadata.
    """
    __tablename__ = 'ManufacturerElement'

    id = Column(Integer(), primary_key=True, autoincrement=True , nullable=False )
    manufacturer = Column(Text())
    serial_number = Column(Text())
    

    def __repr__(self):
        return f"ManufacturerElement(id={self.id},manufacturer={self.manufacturer},serial_number={self.serial_number},)"



    


class ReferenceElement(Base):
    """
    Links to engineering drawings and design files.
    """
    __tablename__ = 'ReferenceElement'

    id = Column(Integer(), primary_key=True, autoincrement=True , nullable=False )
    
    
    drawings_rel = relationship( "ReferenceElementDrawings" )
    drawings = association_proxy("drawings_rel", "drawings",
                                  creator=lambda x_: ReferenceElementDrawings(drawings=x_))
    
    
    design_files_rel = relationship( "ReferenceElementDesignFiles" )
    design_files = association_proxy("design_files_rel", "design_files",
                                  creator=lambda x_: ReferenceElementDesignFiles(design_files=x_))
    

    def __repr__(self):
        return f"ReferenceElement(id={self.id},)"



    


class AcceleratorElement(Base):
    """
    Root base class for all LAURA accelerator elements.  Every lattice element is an instance of a concrete subclass identified by ``hardware_type``.
    """
    __tablename__ = 'AcceleratorElement'

    name = Column(Text(), primary_key=True, nullable=False )
    hardware_class = Column(Enum('Magnet', 'Diagnostic', 'RF', 'Vacuum', 'Laser', 'Plasma', 'Feedback', 'Marker', 'Aperture', 'Stage', 'Lighting', 'Shutter', 'Wakefield', 'TwissMatch', 'Drift', 'Generic', 'Monitor', 'Simulation', 'Valve', 'LaserMirror', 'LaserEnergyMeter', 'LaserAttenuator', name='HardwareClassEnum'), nullable=False )
    hardware_type = Column(Text())
    hardware_model = Column(Text())
    machine_area = Column(Text())
    virtual_name = Column(Text())
    subelement = Column(Text())
    
    
    alias_rel = relationship( "AcceleratorElementAlias" )
    alias = association_proxy("alias_rel", "alias",
                                  creator=lambda x_: AcceleratorElementAlias(alias=x_))
    
    
    inputs_rel = relationship( "AcceleratorElementInputs" )
    inputs = association_proxy("inputs_rel", "inputs",
                                  creator=lambda x_: AcceleratorElementInputs(inputs=x_))
    
    
    outputs_rel = relationship( "AcceleratorElementOutputs" )
    outputs = association_proxy("outputs_rel", "outputs",
                                  creator=lambda x_: AcceleratorElementOutputs(outputs=x_))
    
    
    # ManyToMany
    upstream = relationship(
        "AcceleratorElement",
        secondary="AcceleratorElement_upstream",
        primaryjoin="AcceleratorElement.name == AcceleratorElementUpstream.AcceleratorElement_name",
        secondaryjoin="AcceleratorElement.name == AcceleratorElementUpstream.upstream_name",
    )
    
    
    # ManyToMany
    downstream = relationship(
        "AcceleratorElement",
        secondary="AcceleratorElement_downstream",
        primaryjoin="AcceleratorElement.name == AcceleratorElementDownstream.AcceleratorElement_name",
        secondaryjoin="AcceleratorElement.name == AcceleratorElementDownstream.downstream_name",
    )
    

    def __repr__(self):
        return f"AcceleratorElement(name={self.name},hardware_class={self.hardware_class},hardware_type={self.hardware_type},hardware_model={self.hardware_model},machine_area={self.machine_area},virtual_name={self.virtual_name},subelement={self.subelement},)"



    


class Position(Base):
    """
    Cartesian position in the global accelerator coordinate system. All components are in metres.
    """
    __tablename__ = 'Position'

    id = Column(Integer(), primary_key=True, autoincrement=True , nullable=False )
    x = Column(Float())
    y = Column(Float())
    z = Column(Float())
    

    def __repr__(self):
        return f"Position(id={self.id},x={self.x},y={self.y},z={self.z},)"



    


class Rotation(Base):
    """
    Euler-angle rotation relative to the global coordinate system. All angles are in radians, bounded to [-pi, pi].
    """
    __tablename__ = 'Rotation'

    id = Column(Integer(), primary_key=True, autoincrement=True , nullable=False )
    phi = Column(Float())
    psi = Column(Float())
    theta = Column(Float())
    

    def __repr__(self):
        return f"Rotation(id={self.id},phi={self.phi},psi={self.psi},theta={self.theta},)"



    


class ElementPositionError(Base):
    """
    Alignment position and rotation errors for a physically-located element.
    """
    __tablename__ = 'ElementPositionError'

    id = Column(Integer(), primary_key=True, autoincrement=True , nullable=False )
    position_id = Column(Integer(), ForeignKey('Position.id'))
    position = relationship("Position", uselist=False, foreign_keys=[position_id])
    rotation_id = Column(Integer(), ForeignKey('Rotation.id'))
    rotation = relationship("Rotation", uselist=False, foreign_keys=[rotation_id])
    

    def __repr__(self):
        return f"ElementPositionError(id={self.id},position_id={self.position_id},rotation_id={self.rotation_id},)"



    


class ElementSurvey(Base):
    """
    Survey-measured position and rotation of an element. Structure is identical to ElementPositionError.
    """
    __tablename__ = 'ElementSurvey'

    id = Column(Integer(), primary_key=True, autoincrement=True , nullable=False )
    position_id = Column(Integer(), ForeignKey('Position.id'))
    position = relationship("Position", uselist=False, foreign_keys=[position_id])
    rotation_id = Column(Integer(), ForeignKey('Rotation.id'))
    rotation = relationship("Rotation", uselist=False, foreign_keys=[rotation_id])
    

    def __repr__(self):
        return f"ElementSurvey(id={self.id},position_id={self.position_id},rotation_id={self.rotation_id},)"



    


class ReferencePlacement(Base):
    """
    Positions an element relative to a named reference element's local frame. The ``offset`` field is expressed in the reference element's local frame at the chosen ``point`` (start / middle / end).  Use ``world_offset`` instead to supply an offset already in global world coordinates.
    """
    __tablename__ = 'ReferencePlacement'

    id = Column(Integer(), primary_key=True, autoincrement=True , nullable=False )
    element = Column(Text(), nullable=False )
    point = Column(Text())
    s_offset = Column(Float())
    offset_id = Column(Integer(), ForeignKey('Position.id'))
    offset = relationship("Position", uselist=False, foreign_keys=[offset_id])
    world_offset_id = Column(Integer(), ForeignKey('Position.id'))
    world_offset = relationship("Position", uselist=False, foreign_keys=[world_offset_id])
    

    def __repr__(self):
        return f"ReferencePlacement(id={self.id},element={self.element},point={self.point},s_offset={self.s_offset},offset_id={self.offset_id},world_offset_id={self.world_offset_id},)"



    


class PhysicalElement(Base):
    """
    Physical placement data: position, rotation, length, and associated survey / alignment-error information.
    """
    __tablename__ = 'PhysicalElement'

    id = Column(Integer(), primary_key=True, autoincrement=True , nullable=False )
    length = Column(Float())
    physical_angle = Column(Float())
    s = Column(Float())
    s_point = Column(Text())
    middle_id = Column(Integer(), ForeignKey('Position.id'))
    middle = relationship("Position", uselist=False, foreign_keys=[middle_id])
    datum_id = Column(Integer(), ForeignKey('Position.id'))
    datum = relationship("Position", uselist=False, foreign_keys=[datum_id])
    rotation_id = Column(Integer(), ForeignKey('Rotation.id'))
    rotation = relationship("Rotation", uselist=False, foreign_keys=[rotation_id])
    global_rotation_id = Column(Integer(), ForeignKey('Rotation.id'))
    global_rotation = relationship("Rotation", uselist=False, foreign_keys=[global_rotation_id])
    error_id = Column(Integer(), ForeignKey('ElementPositionError.id'))
    error = relationship("ElementPositionError", uselist=False, foreign_keys=[error_id])
    survey_id = Column(Integer(), ForeignKey('ElementSurvey.id'))
    survey = relationship("ElementSurvey", uselist=False, foreign_keys=[survey_id])
    reference_placement_id = Column(Integer(), ForeignKey('ReferencePlacement.id'))
    reference_placement = relationship("ReferencePlacement", uselist=False, foreign_keys=[reference_placement_id])
    

    def __repr__(self):
        return f"PhysicalElement(id={self.id},length={self.length},physical_angle={self.physical_angle},s={self.s},s_point={self.s_point},middle_id={self.middle_id},datum_id={self.datum_id},rotation_id={self.rotation_id},global_rotation_id={self.global_rotation_id},error_id={self.error_id},survey_id={self.survey_id},reference_placement_id={self.reference_placement_id},)"



    


class ControlVariable(Base):
    """
    A single process-variable entry mapping a logical name to a control-system PV identifier.
    """
    __tablename__ = 'ControlVariable'

    name = Column(Text(), primary_key=True, nullable=False )
    identifier = Column(Text())
    dtype = Column(Text())
    protocol = Column(Text())
    units = Column(Text())
    description = Column(Text())
    read_only = Column(Boolean())
    value = Column(Text())
    control_type = Column(Enum('scalar', 'binary', 'state', 'string', 'waveform', 'statistical', name='ControlTypeEnum'))
    target = Column(Text())
    expression = Column(Text())
    states = Column(Text())
    readback = Column(Text())
    setpoint = Column(Text())
    update = Column(Text())
    dynamics = Column(Text())
    auto_buffer = Column(Boolean())
    buffer_size = Column(Integer())
    ControlsInformation_id = Column(Integer(), ForeignKey('ControlsInformation.id'), primary_key=True)
    

    def __repr__(self):
        return f"ControlVariable(name={self.name},identifier={self.identifier},dtype={self.dtype},protocol={self.protocol},units={self.units},description={self.description},read_only={self.read_only},value={self.value},control_type={self.control_type},target={self.target},expression={self.expression},states={self.states},readback={self.readback},setpoint={self.setpoint},update={self.update},dynamics={self.dynamics},auto_buffer={self.auto_buffer},buffer_size={self.buffer_size},ControlsInformation_id={self.ControlsInformation_id},)"



    


class ControlsInformation(Base):
    """
    Collection of process-variable definitions for an element's control interface.
    """
    __tablename__ = 'ControlsInformation'

    id = Column(Integer(), primary_key=True, autoincrement=True , nullable=False )
    
    
    # One-To-Many: OneToAnyMapping(source_class='ControlsInformation', source_slot='variables', mapping_type=None, target_class='ControlVariable', target_slot='ControlsInformation_id', join_class=None, uses_join_table=None, multivalued=False)
    variables = relationship( "ControlVariable", foreign_keys="[ControlVariable.ControlsInformation_id]")
    

    def __repr__(self):
        return f"ControlsInformation(id={self.id},)"



    


class ShutterElement(Base):
    """
    Shutter interlock configuration.
    """
    __tablename__ = 'ShutterElement'

    id = Column(Integer(), primary_key=True, autoincrement=True , nullable=False )
    
    
    interlocks_rel = relationship( "ShutterElementInterlocks" )
    interlocks = association_proxy("interlocks_rel", "interlocks",
                                  creator=lambda x_: ShutterElementInterlocks(interlocks=x_))
    

    def __repr__(self):
        return f"ShutterElement(id={self.id},)"



    


class ValveElement(Base):
    """
    Vacuum valve configuration (no additional fields).
    """
    __tablename__ = 'ValveElement'

    id = Column(Integer(), primary_key=True, autoincrement=True , nullable=False )
    

    def __repr__(self):
        return f"ValveElement(id={self.id},)"



    


class LightingElement(Base):
    """
    Lighting element (no additional fields currently defined).
    """
    __tablename__ = 'LightingElement'

    id = Column(Integer(), primary_key=True, autoincrement=True , nullable=False )
    

    def __repr__(self):
        return f"LightingElement(id={self.id},)"



    


class ApertureElement(Base):
    """
    Transverse aperture geometry for drift-space checks and collimators.
    """
    __tablename__ = 'ApertureElement'

    id = Column(Integer(), primary_key=True, autoincrement=True , nullable=False )
    number_of_elements = Column(Integer())
    horizontal_size = Column(Float())
    vertical_size = Column(Float())
    shape = Column(Enum('circular', 'rectangular', 'elliptical', name='ApertureShapeEnum'))
    radius = Column(Float())
    negative_extent = Column(Float())
    positive_extent = Column(Float())
    

    def __repr__(self):
        return f"ApertureElement(id={self.id},number_of_elements={self.number_of_elements},horizontal_size={self.horizontal_size},vertical_size={self.vertical_size},shape={self.shape},radius={self.radius},negative_extent={self.negative_extent},positive_extent={self.positive_extent},)"



    


class FunctionalDefinition(Base):
    """
    One named constant a lattice makes available to its elements, e.g. ``quad1_k1l: -2``.  A class rather than a bare map because LinkML has no free-form mapping type; the same keyed-inlined pattern as ControlVariable.
    """
    __tablename__ = 'FunctionalDefinition'

    id = Column(Integer(), primary_key=True, autoincrement=True)
    name = Column(Text(), nullable=False )
    value = Column(Float(), nullable=False )
    SectionLattice_name = Column(Text(), ForeignKey('SectionLattice.name'))
    MachineLayout_name = Column(Text(), ForeignKey('MachineLayout.name'))
    

    def __repr__(self):
        return f"FunctionalDefinition(name={self.name},value={self.value},SectionLattice_name={self.SectionLattice_name},MachineLayout_name={self.MachineLayout_name},)"



    


class SectionLattice(Base):
    """
    A contiguous beamline section: an ordered run of elements.
    """
    __tablename__ = 'SectionLattice'

    name = Column(Text(), primary_key=True, nullable=False )
    master_lattice = Column(Text())
    section_type = Column(Enum('beam', 'rf', 'laser', name='LatticeTypeEnum'))
    revolution_frequency = Column(Float())
    
    
    # ManyToMany
    elements = relationship( "AcceleratorElement", secondary="SectionLattice_elements")
    
    
    # One-To-Many: OneToAnyMapping(source_class='SectionLattice', source_slot='functional_definitions', mapping_type=None, target_class='FunctionalDefinition', target_slot='SectionLattice_name', join_class=None, uses_join_table=None, multivalued=False)
    functional_definitions = relationship( "FunctionalDefinition", foreign_keys="[FunctionalDefinition.SectionLattice_name]")
    

    def __repr__(self):
        return f"SectionLattice(name={self.name},master_lattice={self.master_lattice},section_type={self.section_type},revolution_frequency={self.revolution_frequency},)"



    


class MachineLayout(Base):
    """
    A beamline layout: a contiguous sequence of sections.
    """
    __tablename__ = 'MachineLayout'

    name = Column(Text(), primary_key=True, nullable=False )
    master_lattice = Column(Text())
    layout_type = Column(Enum('beam', 'rf', 'laser', name='LatticeTypeEnum'))
    revolution_frequency = Column(Float())
    
    
    # ManyToMany
    sections = relationship( "SectionLattice", secondary="MachineLayout_sections")
    
    
    # One-To-Many: OneToAnyMapping(source_class='MachineLayout', source_slot='functional_definitions', mapping_type=None, target_class='FunctionalDefinition', target_slot='MachineLayout_name', join_class=None, uses_join_table=None, multivalued=False)
    functional_definitions = relationship( "FunctionalDefinition", foreign_keys="[FunctionalDefinition.MachineLayout_name]")
    

    def __repr__(self):
        return f"MachineLayout(name={self.name},master_lattice={self.master_lattice},layout_type={self.layout_type},revolution_frequency={self.revolution_frequency},)"



    


class MachineModel(Base):
    """
    Top-level container for a complete accelerator lattice: elements, sections, layouts, and named lattice configurations.
    """
    __tablename__ = 'MachineModel'

    id = Column(Integer(), primary_key=True, autoincrement=True , nullable=False )
    
    
    # ManyToMany
    elements = relationship( "AcceleratorElement", secondary="MachineModel_elements")
    
    
    # ManyToMany
    sections = relationship( "SectionLattice", secondary="MachineModel_sections")
    
    
    # ManyToMany
    layouts = relationship( "MachineLayout", secondary="MachineModel_layouts")
    

    def __repr__(self):
        return f"MachineModel(id={self.id},)"



    


class MatrixValue(Base):
    """
    An unconstrained serializable matrix value. The handwritten matrix model validates dense arrays and named coefficient mappings into NumPy arrays.
    """
    __tablename__ = 'MatrixValue'

    id = Column(Integer(), primary_key=True, autoincrement=True , nullable=False )
    

    def __repr__(self):
        return f"MatrixValue(id={self.id},)"



    


class SimulationElement(Base):
    """
    Base simulation attributes: field-map files and reference positions for tracking codes.
    """
    __tablename__ = 'SimulationElement'

    id = Column(Integer(), primary_key=True, autoincrement=True , nullable=False )
    field_definition = Column(Text())
    wakefield_definition = Column(Text())
    wakefield_enable = Column(Boolean())
    field_reference_position = Column(Text())
    scale_field = Column(Float())
    

    def __repr__(self):
        return f"SimulationElement(id={self.id},field_definition={self.field_definition},wakefield_definition={self.wakefield_definition},wakefield_enable={self.wakefield_enable},field_reference_position={self.field_reference_position},scale_field={self.scale_field},)"



    


class Multipole(Base):
    """
    Individual multipole field component, characterised by order and integrated normal / skew strengths at a reference radius.
    """
    __tablename__ = 'Multipole'

    id = Column(Integer(), primary_key=True, autoincrement=True , nullable=False )
    order = Column(Integer())
    normal = Column(Float())
    skew = Column(Float())
    radius = Column(Float())
    

    def __repr__(self):
        return f"Multipole(id={self.id},order={self.order},normal={self.normal},skew={self.skew},radius={self.radius},)"



    


class Multipoles(Base):
    """
    Complete set of integrated multipole strengths up to decapole order, as named slots for efficient element look-up.
    """
    __tablename__ = 'Multipoles'

    id = Column(Integer(), primary_key=True, autoincrement=True , nullable=False )
    K0L_id = Column(Integer(), ForeignKey('Multipole.id'))
    K0L = relationship("Multipole", uselist=False, foreign_keys=[K0L_id])
    K1L_id = Column(Integer(), ForeignKey('Multipole.id'))
    K1L = relationship("Multipole", uselist=False, foreign_keys=[K1L_id])
    K2L_id = Column(Integer(), ForeignKey('Multipole.id'))
    K2L = relationship("Multipole", uselist=False, foreign_keys=[K2L_id])
    K3L_id = Column(Integer(), ForeignKey('Multipole.id'))
    K3L = relationship("Multipole", uselist=False, foreign_keys=[K3L_id])
    K4L_id = Column(Integer(), ForeignKey('Multipole.id'))
    K4L = relationship("Multipole", uselist=False, foreign_keys=[K4L_id])
    

    def __repr__(self):
        return f"Multipoles(id={self.id},K0L_id={self.K0L_id},K1L_id={self.K1L_id},K2L_id={self.K2L_id},K3L_id={self.K3L_id},K4L_id={self.K4L_id},)"



    


class FieldIntegral(Base):
    """
    Polynomial fit of integrated field strength as a function of magnet current.
    """
    __tablename__ = 'FieldIntegral'

    id = Column(Integer(), primary_key=True, autoincrement=True , nullable=False )
    
    
    coefficients_rel = relationship( "FieldIntegralCoefficients" )
    coefficients = association_proxy("coefficients_rel", "coefficients",
                                  creator=lambda x_: FieldIntegralCoefficients(coefficients=x_))
    

    def __repr__(self):
        return f"FieldIntegral(id={self.id},)"



    


class LinearSaturationFit(Base):
    """
    Bi-linear saturation model mapping magnet current to integrated field strength (K-value conversion).
    """
    __tablename__ = 'LinearSaturationFit'

    id = Column(Integer(), primary_key=True, autoincrement=True , nullable=False )
    m = Column(Float())
    I_max = Column(Float())
    f = Column(Float())
    a = Column(Float())
    I0 = Column(Float())
    d = Column(Float())
    L = Column(Float())
    

    def __repr__(self):
        return f"LinearSaturationFit(id={self.id},m={self.m},I_max={self.I_max},f={self.f},a={self.a},I0={self.I0},d={self.d},L={self.L},)"



    


class MagneticElement(Base):
    """
    Magnetic field parameters for a beamline magnet, including multipole components, field integrals, and geometric edge parameters.
    """
    __tablename__ = 'MagneticElement'

    id = Column(Integer(), primary_key=True, autoincrement=True , nullable=False )
    order = Column(Integer())
    skew = Column(Boolean())
    length = Column(Float())
    settle_time = Column(Float())
    entrance_edge_angle = Column(Text())
    exit_edge_angle = Column(Text())
    gap = Column(Float())
    bore = Column(Float())
    plane = Column(Enum('Horizontal', 'Vertical', 'Combined', name='BendingPlaneEnum'))
    width = Column(Float())
    tilt = Column(Float())
    edge_field_integral = Column(Float())
    fringe_field_coefficient = Column(Float())
    gradient = Column(Float())
    angle = Column(Float())
    multipoles_id = Column(Integer(), ForeignKey('Multipoles.id'))
    multipoles = relationship("Multipoles", uselist=False, foreign_keys=[multipoles_id])
    systematic_multipoles_id = Column(Integer(), ForeignKey('Multipoles.id'))
    systematic_multipoles = relationship("Multipoles", uselist=False, foreign_keys=[systematic_multipoles_id])
    random_multipoles_id = Column(Integer(), ForeignKey('Multipoles.id'))
    random_multipoles = relationship("Multipoles", uselist=False, foreign_keys=[random_multipoles_id])
    field_integral_coefficients_id = Column(Integer(), ForeignKey('FieldIntegral.id'))
    field_integral_coefficients = relationship("FieldIntegral", uselist=False, foreign_keys=[field_integral_coefficients_id])
    linear_saturation_coefficients_id = Column(Integer(), ForeignKey('LinearSaturationFit.id'))
    linear_saturation_coefficients = relationship("LinearSaturationFit", uselist=False, foreign_keys=[linear_saturation_coefficients_id])
    

    def __repr__(self):
        return f"MagneticElement(id={self.id},order={self.order},skew={self.skew},length={self.length},settle_time={self.settle_time},entrance_edge_angle={self.entrance_edge_angle},exit_edge_angle={self.exit_edge_angle},gap={self.gap},bore={self.bore},plane={self.plane},width={self.width},tilt={self.tilt},edge_field_integral={self.edge_field_integral},fringe_field_coefficient={self.fringe_field_coefficient},gradient={self.gradient},angle={self.angle},multipoles_id={self.multipoles_id},systematic_multipoles_id={self.systematic_multipoles_id},random_multipoles_id={self.random_multipoles_id},field_integral_coefficients_id={self.field_integral_coefficients_id},linear_saturation_coefficients_id={self.linear_saturation_coefficients_id},)"



    


class DegaussableElement(Base):
    """
    Degaussing (demagnetisation cycle) parameters for magnets that require a field-reset procedure.
    """
    __tablename__ = 'DegaussableElement'

    id = Column(Integer(), primary_key=True, autoincrement=True , nullable=False )
    tolerance = Column(Float())
    steps = Column(Integer())
    
    
    values_rel = relationship( "DegaussableElementValues" )
    values = association_proxy("values_rel", "values",
                                  creator=lambda x_: DegaussableElementValues(values=x_))
    

    def __repr__(self):
        return f"DegaussableElement(id={self.id},tolerance={self.tolerance},steps={self.steps},)"



    


class RFCavityElement(Base):
    """
    RF cavity accelerating-structure parameters.
    """
    __tablename__ = 'RFCavityElement'

    id = Column(Integer(), primary_key=True, autoincrement=True , nullable=False )
    cell_length = Column(Float())
    coupling_cell_length = Column(Float())
    design_gamma = Column(Float())
    design_power = Column(Float())
    frequency = Column(Float())
    n_cells = Column(Float())
    crest = Column(Float())
    phase = Column(Float())
    shunt_impedance = Column(Float())
    mode_numerator = Column(Float())
    mode_denominator = Column(Integer())
    structure_type = Column(Text())
    attenuation_constant = Column(Float())
    
    
    power_calibration_rel = relationship( "RFCavityElementPowerCalibration" )
    power_calibration = association_proxy("power_calibration_rel", "power_calibration",
                                  creator=lambda x_: RFCavityElementPowerCalibration(power_calibration=x_))
    
    
    gradient_calibration_rel = relationship( "RFCavityElementGradientCalibration" )
    gradient_calibration = association_proxy("gradient_calibration_rel", "gradient_calibration",
                                  creator=lambda x_: RFCavityElementGradientCalibration(gradient_calibration=x_))
    

    def __repr__(self):
        return f"RFCavityElement(id={self.id},cell_length={self.cell_length},coupling_cell_length={self.coupling_cell_length},design_gamma={self.design_gamma},design_power={self.design_power},frequency={self.frequency},n_cells={self.n_cells},crest={self.crest},phase={self.phase},shunt_impedance={self.shunt_impedance},mode_numerator={self.mode_numerator},mode_denominator={self.mode_denominator},structure_type={self.structure_type},attenuation_constant={self.attenuation_constant},)"



    


class WakefieldElement(Base):
    """
    Passive wakefield structure parameters.
    """
    __tablename__ = 'WakefieldElement'

    id = Column(Integer(), primary_key=True, autoincrement=True , nullable=False )
    cell_length = Column(Float())
    n_cells = Column(Float())
    coupling_cell_length = Column(Float())
    

    def __repr__(self):
        return f"WakefieldElement(id={self.id},cell_length={self.cell_length},n_cells={self.n_cells},coupling_cell_length={self.coupling_cell_length},)"



    


class RFDeflectingCavityElement(Base):
    """
    Transverse-deflecting RF cavity parameters -- a subset of RFCavityElement for streak-mode operation.
    """
    __tablename__ = 'RFDeflectingCavityElement'

    id = Column(Integer(), primary_key=True, autoincrement=True , nullable=False )
    cell_length = Column(Float())
    coupling_cell_length = Column(Float())
    crest = Column(Float())
    design_gamma = Column(Float())
    design_power = Column(Float())
    frequency = Column(Float())
    n_cells = Column(Float())
    phase = Column(Float())
    shunt_impedance = Column(Float())
    mode_numerator = Column(Float())
    mode_denominator = Column(Integer())
    

    def __repr__(self):
        return f"RFDeflectingCavityElement(id={self.id},cell_length={self.cell_length},coupling_cell_length={self.coupling_cell_length},crest={self.crest},design_gamma={self.design_gamma},design_power={self.design_power},frequency={self.frequency},n_cells={self.n_cells},phase={self.phase},shunt_impedance={self.shunt_impedance},mode_numerator={self.mode_numerator},mode_denominator={self.mode_denominator},)"



    


class PIDElement(Base):
    """
    PID feedback-controller parameters.
    """
    __tablename__ = 'PIDElement'

    id = Column(Integer(), primary_key=True, autoincrement=True , nullable=False )
    Kp = Column(Float())
    Ki = Column(Float())
    Kd = Column(Float())
    forward_channel = Column(Integer())
    probe_channel = Column(Integer())
    enable = Column(Text())
    disable = Column(Text())
    phase_range_id = Column(Integer(), ForeignKey('PIDPhaseRange.id'))
    phase_range = relationship("PIDPhaseRange", uselist=False, foreign_keys=[phase_range_id])
    phase_weight_range_id = Column(Integer(), ForeignKey('PIDWeightRange.id'))
    phase_weight_range = relationship("PIDWeightRange", uselist=False, foreign_keys=[phase_weight_range_id])
    

    def __repr__(self):
        return f"PIDElement(id={self.id},Kp={self.Kp},Ki={self.Ki},Kd={self.Kd},forward_channel={self.forward_channel},probe_channel={self.probe_channel},enable={self.enable},disable={self.disable},phase_range_id={self.phase_range_id},phase_weight_range_id={self.phase_weight_range_id},)"



    


class PIDPhaseRange(Base):
    """
    Numeric min/max range for PID phase control.
    """
    __tablename__ = 'PIDPhaseRange'

    id = Column(Integer(), primary_key=True, autoincrement=True , nullable=False )
    min = Column(Float())
    max = Column(Float())
    

    def __repr__(self):
        return f"PIDPhaseRange(id={self.id},min={self.min},max={self.max},)"



    


class Trace(Base):
    """
    LLRF trace metadata.
    """
    __tablename__ = 'Trace'

    id = Column(Integer(), primary_key=True, autoincrement=True , nullable=False )
    data_size = Column(Integer())
    data_count = Column(Integer())
    data_chunk_size = Column(Integer())
    number_of_start_zeros = Column(Integer())
    

    def __repr__(self):
        return f"Trace(id={self.id},data_size={self.data_size},data_count={self.data_count},data_chunk_size={self.data_chunk_size},number_of_start_zeros={self.number_of_start_zeros},)"



    


class ChannelNames(Base):
    """
    Names for LLRF channels 1..8.
    """
    __tablename__ = 'ChannelNames'

    id = Column(Integer(), primary_key=True, autoincrement=True , nullable=False )
    ch1 = Column(Text())
    ch2 = Column(Text())
    ch3 = Column(Text())
    ch4 = Column(Text())
    ch5 = Column(Text())
    ch6 = Column(Text())
    ch7 = Column(Text())
    ch8 = Column(Text())
    

    def __repr__(self):
        return f"ChannelNames(id={self.id},ch1={self.ch1},ch2={self.ch2},ch3={self.ch3},ch4={self.ch4},ch5={self.ch5},ch6={self.ch6},ch7={self.ch7},ch8={self.ch8},)"



    


class LLRFTiming(Base):
    """
    Start/end window timing definition.
    """
    __tablename__ = 'LLRFTiming'

    id = Column(Integer(), primary_key=True, autoincrement=True , nullable=False )
    start = Column(Float())
    end = Column(Float())
    

    def __repr__(self):
        return f"LLRFTiming(id={self.id},start={self.start},end={self.end},)"



    


class LLRFTimings(Base):
    """
    Collection of timing windows for key LLRF channels.
    """
    __tablename__ = 'LLRFTimings'

    id = Column(Integer(), primary_key=True, autoincrement=True , nullable=False )
    klystron_forward_id = Column(Integer(), ForeignKey('LLRFTiming.id'))
    klystron_forward = relationship("LLRFTiming", uselist=False, foreign_keys=[klystron_forward_id])
    klystron_reverse_id = Column(Integer(), ForeignKey('LLRFTiming.id'))
    klystron_reverse = relationship("LLRFTiming", uselist=False, foreign_keys=[klystron_reverse_id])
    cavity_forward_id = Column(Integer(), ForeignKey('LLRFTiming.id'))
    cavity_forward = relationship("LLRFTiming", uselist=False, foreign_keys=[cavity_forward_id])
    cavity_reverse_id = Column(Integer(), ForeignKey('LLRFTiming.id'))
    cavity_reverse = relationship("LLRFTiming", uselist=False, foreign_keys=[cavity_reverse_id])
    cavity_probe_id = Column(Integer(), ForeignKey('LLRFTiming.id'))
    cavity_probe = relationship("LLRFTiming", uselist=False, foreign_keys=[cavity_probe_id])
    

    def __repr__(self):
        return f"LLRFTimings(id={self.id},klystron_forward_id={self.klystron_forward_id},klystron_reverse_id={self.klystron_reverse_id},cavity_forward_id={self.cavity_forward_id},cavity_reverse_id={self.cavity_reverse_id},cavity_probe_id={self.cavity_probe_id},)"



    


class LowLevelRFElement(Base):
    """
    Low-level RF (LLRF) system parameters.
    """
    __tablename__ = 'LowLevelRFElement'

    id = Column(Integer(), primary_key=True, autoincrement=True , nullable=False )
    max_amplitude = Column(Float())
    crest_phase = Column(Float())
    trace_id = Column(Integer(), ForeignKey('Trace.id'))
    trace = relationship("Trace", uselist=False, foreign_keys=[trace_id])
    channel_names_id = Column(Integer(), ForeignKey('ChannelNames.id'))
    channel_names = relationship("ChannelNames", uselist=False, foreign_keys=[channel_names_id])
    timings_id = Column(Integer(), ForeignKey('LLRFTimings.id'))
    timings = relationship("LLRFTimings", uselist=False, foreign_keys=[timings_id])
    

    def __repr__(self):
        return f"LowLevelRFElement(id={self.id},max_amplitude={self.max_amplitude},crest_phase={self.crest_phase},trace_id={self.trace_id},channel_names_id={self.channel_names_id},timings_id={self.timings_id},)"



    


class RFModulatorElement(Base):
    """
    RF modulator (klystron driver) parameters.
    """
    __tablename__ = 'RFModulatorElement'

    id = Column(Integer(), primary_key=True, autoincrement=True , nullable=False )
    

    def __repr__(self):
        return f"RFModulatorElement(id={self.id},)"



    


class RFProtectionElement(Base):
    """
    RF protection system parameters.
    """
    __tablename__ = 'RFProtectionElement'

    id = Column(Integer(), primary_key=True, autoincrement=True , nullable=False )
    prot_type = Column(Text())
    

    def __repr__(self):
        return f"RFProtectionElement(id={self.id},prot_type={self.prot_type},)"



    


class RFHeartbeatElement(Base):
    """
    RF heartbeat / timing-monitor element parameters.
    """
    __tablename__ = 'RFHeartbeatElement'

    id = Column(Integer(), primary_key=True, autoincrement=True , nullable=False )
    

    def __repr__(self):
        return f"RFHeartbeatElement(id={self.id},)"



    


class DiagnosticElement(Base):
    """
    Base class for diagnostic instrument sub-models.  Concrete sub-models extend this with instrument-specific fields.
    """
    __tablename__ = 'DiagnosticElement'

    id = Column(Integer(), primary_key=True, autoincrement=True , nullable=False )
    

    def __repr__(self):
        return f"DiagnosticElement(id={self.id},)"



    


class CameraPixelResultsIndices(Base):
    """
    Indices into camera pixel-analysis result arrays.
    """
    __tablename__ = 'CameraPixelResultsIndices'

    id = Column(Integer(), primary_key=True, autoincrement=True , nullable=False )
    x = Column(Integer())
    y = Column(Integer())
    x_sigma = Column(Integer())
    y_sigma = Column(Integer())
    covariance = Column(Integer())
    

    def __repr__(self):
        return f"CameraPixelResultsIndices(id={self.id},x={self.x},y={self.y},x_sigma={self.x_sigma},y_sigma={self.y_sigma},covariance={self.covariance},)"



    


class CameraPixelResultsNames(Base):
    """
    Names of camera pixel-analysis result arrays.
    """
    __tablename__ = 'CameraPixelResultsNames'

    id = Column(Integer(), primary_key=True, autoincrement=True , nullable=False )
    x = Column(Text())
    y = Column(Text())
    x_sigma = Column(Text())
    y_sigma = Column(Text())
    covariance = Column(Text())
    

    def __repr__(self):
        return f"CameraPixelResultsNames(id={self.id},x={self.x},y={self.y},x_sigma={self.x_sigma},y_sigma={self.y_sigma},covariance={self.covariance},)"



    


class CameraMask(Base):
    """
    Camera analysis mask parameters.
    """
    __tablename__ = 'CameraMask'

    id = Column(Integer(), primary_key=True, autoincrement=True , nullable=False )
    use_maximum_values = Column(Boolean())
    
    
    middle_rel = relationship( "CameraMaskMiddle" )
    middle = association_proxy("middle_rel", "middle",
                                  creator=lambda x_: CameraMaskMiddle(middle=x_))
    
    
    radius_rel = relationship( "CameraMaskRadius" )
    radius = association_proxy("radius_rel", "radius",
                                  creator=lambda x_: CameraMaskRadius(radius=x_))
    
    
    maximum_rel = relationship( "CameraMaskMaximum" )
    maximum = association_proxy("maximum_rel", "maximum",
                                  creator=lambda x_: CameraMaskMaximum(maximum=x_))
    

    def __repr__(self):
        return f"CameraMask(id={self.id},use_maximum_values={self.use_maximum_values},)"



    


class CameraSensor(Base):
    """
    Camera sensor hardware configuration.
    """
    __tablename__ = 'CameraSensor'

    id = Column(Integer(), primary_key=True, autoincrement=True , nullable=False )
    x_pixels = Column(Integer())
    y_pixels = Column(Integer())
    x_scale_factor = Column(Integer())
    y_scale_factor = Column(Integer())
    beam_pixel_average = Column(Float())
    x_pixels_to_mm = Column(Float())
    y_pixels_to_mm = Column(Float())
    bit_depth = Column(Integer())
    
    
    middle_rel = relationship( "CameraSensorMiddle" )
    middle = association_proxy("middle_rel", "middle",
                                  creator=lambda x_: CameraSensorMiddle(middle=x_))
    
    
    minimum_rel = relationship( "CameraSensorMinimum" )
    minimum = association_proxy("minimum_rel", "minimum",
                                  creator=lambda x_: CameraSensorMinimum(minimum=x_))
    
    
    maximum_rel = relationship( "CameraSensorMaximum" )
    maximum = association_proxy("maximum_rel", "maximum",
                                  creator=lambda x_: CameraSensorMaximum(maximum=x_))
    
    
    operating_middle_rel = relationship( "CameraSensorOperatingMiddle" )
    operating_middle = association_proxy("operating_middle_rel", "operating_middle",
                                  creator=lambda x_: CameraSensorOperatingMiddle(operating_middle=x_))
    
    
    mechanical_middle_rel = relationship( "CameraSensorMechanicalMiddle" )
    mechanical_middle = association_proxy("mechanical_middle_rel", "mechanical_middle",
                                  creator=lambda x_: CameraSensorMechanicalMiddle(mechanical_middle=x_))
    

    def __repr__(self):
        return f"CameraSensor(id={self.id},x_pixels={self.x_pixels},y_pixels={self.y_pixels},x_scale_factor={self.x_scale_factor},y_scale_factor={self.y_scale_factor},beam_pixel_average={self.beam_pixel_average},x_pixels_to_mm={self.x_pixels_to_mm},y_pixels_to_mm={self.y_pixels_to_mm},bit_depth={self.bit_depth},)"



    


class LaserMirrorElement(Base):
    """
    Mirror steering parameters for a laser mirror.
    """
    __tablename__ = 'LaserMirrorElement'

    id = Column(Integer(), primary_key=True, autoincrement=True , nullable=False )
    step_max = Column(Float())
    vertical_channel = Column(Integer())
    horizontal_channel = Column(Integer())
    sense_id = Column(Integer(), ForeignKey('LaserMirrorSense.id'))
    sense = relationship("LaserMirrorSense", uselist=False, foreign_keys=[sense_id])
    

    def __repr__(self):
        return f"LaserMirrorElement(id={self.id},step_max={self.step_max},vertical_channel={self.vertical_channel},horizontal_channel={self.horizontal_channel},sense_id={self.sense_id},)"



    


class LaserMirrorSense(Base):
    """
    Mirror sense switch values.
    """
    __tablename__ = 'LaserMirrorSense'

    id = Column(Integer(), primary_key=True, autoincrement=True , nullable=False )
    left = Column(Float())
    right = Column(Float())
    up = Column(Float())
    down = Column(Float())
    

    def __repr__(self):
        return f"LaserMirrorSense(id={self.id},left={self.left},right={self.right},up={self.up},down={self.down},)"



    


class LaserElement(Base):
    """
    Laser-beam parameters (wavelength, pulse energy, profile, etc.) for a laser element or laser-driven plasma stage.
    """
    __tablename__ = 'LaserElement'

    id = Column(Integer(), primary_key=True, autoincrement=True , nullable=False )
    initial_position = Column(Float())
    waist = Column(Float())
    wavelength = Column(Float())
    pulse_energy = Column(Float())
    pulse_duration_fwhm = Column(Float())
    focal_position = Column(Float())
    cep_phase = Column(Float())
    polarization = Column(Enum('linear', 'circular', 'elliptical', name='LaserPolarizationEnum'))
    profile_type = Column(Enum('gaussian', 'laguerre-gaussian', 'flattened-gaussian', 'file', name='LaserProfileTypeEnum'))
    laguerre_polynomial_order_p = Column(Integer())
    flatness = Column(Integer())
    

    def __repr__(self):
        return f"LaserElement(id={self.id},initial_position={self.initial_position},waist={self.waist},wavelength={self.wavelength},pulse_energy={self.pulse_energy},pulse_duration_fwhm={self.pulse_duration_fwhm},focal_position={self.focal_position},cep_phase={self.cep_phase},polarization={self.polarization},profile_type={self.profile_type},laguerre_polynomial_order_p={self.laguerre_polynomial_order_p},flatness={self.flatness},)"



    


class LaserEnergyMeterElement(Base):
    """
    Laser energy-meter sub-model (no additional fields).
    """
    __tablename__ = 'LaserEnergyMeterElement'

    id = Column(Integer(), primary_key=True, autoincrement=True , nullable=False )
    

    def __repr__(self):
        return f"LaserEnergyMeterElement(id={self.id},)"



    


class LaserHalfWavePlateElement(Base):
    """
    Half-wave plate sub-model (no additional fields).
    """
    __tablename__ = 'LaserHalfWavePlateElement'

    id = Column(Integer(), primary_key=True, autoincrement=True , nullable=False )
    

    def __repr__(self):
        return f"LaserHalfWavePlateElement(id={self.id},)"



    


class PlasmaElement(Base):
    """
    Plasma channel parameters for a laser-driven plasma-accelerator stage.
    """
    __tablename__ = 'PlasmaElement'

    id = Column(Integer(), primary_key=True, autoincrement=True , nullable=False )
    density = Column(Float())
    species = Column(Text())
    ramp_up = Column(Float())
    plateau = Column(Float())
    ramp_down = Column(Float())
    ramp_decay_length = Column(Float())
    density_profile = Column(Boolean())
    parabolic_coefficient = Column(Float())
    

    def __repr__(self):
        return f"PlasmaElement(id={self.id},density={self.density},species={self.species},ramp_up={self.ramp_up},plateau={self.plateau},ramp_down={self.ramp_down},ramp_decay_length={self.ramp_decay_length},density_profile={self.density_profile},parabolic_coefficient={self.parabolic_coefficient},)"



    


class CorrectorMagnet(Base):
    """
    Steering-corrector field, expressed as horizontal and vertical kicks rather than multipole coefficients.
    """
    __tablename__ = 'Corrector_Magnet'

    id = Column(Integer(), primary_key=True, autoincrement=True , nullable=False )
    length = Column(Float())
    order = Column(Integer())
    tilt = Column(Float())
    horizontal_kick = Column(Float())
    vertical_kick = Column(Float())
    

    def __repr__(self):
        return f"Corrector_Magnet(id={self.id},length={self.length},order={self.order},tilt={self.tilt},horizontal_kick={self.horizontal_kick},vertical_kick={self.vertical_kick},)"



    


class SolenoidFields(Base):
    """
    Solenoid integrated axial field components ``S0L``–``S12L`` [T.m].
    """
    __tablename__ = 'SolenoidFields'

    id = Column(Integer(), primary_key=True, autoincrement=True , nullable=False )
    S0L = Column(Float())
    S1L = Column(Float())
    S2L = Column(Float())
    S3L = Column(Float())
    S4L = Column(Float())
    S5L = Column(Float())
    S6L = Column(Float())
    S7L = Column(Float())
    S8L = Column(Float())
    S9L = Column(Float())
    S10L = Column(Float())
    S11L = Column(Float())
    S12L = Column(Float())
    

    def __repr__(self):
        return f"SolenoidFields(id={self.id},S0L={self.S0L},S1L={self.S1L},S2L={self.S2L},S3L={self.S3L},S4L={self.S4L},S5L={self.S5L},S6L={self.S6L},S7L={self.S7L},S8L={self.S8L},S9L={self.S9L},S10L={self.S10L},S11L={self.S11L},S12L={self.S12L},)"



    


class SolenoidMagnet(Base):
    """
    Solenoid field model, including systematic and random field errors and the current-to-field calibration.
    """
    __tablename__ = 'Solenoid_Magnet'

    id = Column(Integer(), primary_key=True, autoincrement=True , nullable=False )
    length = Column(Float())
    order = Column(Integer())
    settle_time = Column(Float())
    fields_id = Column(Integer(), ForeignKey('SolenoidFields.id'))
    fields = relationship("SolenoidFields", uselist=False, foreign_keys=[fields_id])
    systematic_fields_id = Column(Integer(), ForeignKey('SolenoidFields.id'))
    systematic_fields = relationship("SolenoidFields", uselist=False, foreign_keys=[systematic_fields_id])
    random_fields_id = Column(Integer(), ForeignKey('SolenoidFields.id'))
    random_fields = relationship("SolenoidFields", uselist=False, foreign_keys=[random_fields_id])
    field_integral_coefficients_id = Column(Integer(), ForeignKey('FieldIntegral.id'))
    field_integral_coefficients = relationship("FieldIntegral", uselist=False, foreign_keys=[field_integral_coefficients_id])
    linear_saturation_coefficients_id = Column(Integer(), ForeignKey('LinearSaturationFit.id'))
    linear_saturation_coefficients = relationship("LinearSaturationFit", uselist=False, foreign_keys=[linear_saturation_coefficients_id])
    

    def __repr__(self):
        return f"Solenoid_Magnet(id={self.id},length={self.length},order={self.order},settle_time={self.settle_time},fields_id={self.fields_id},systematic_fields_id={self.systematic_fields_id},random_fields_id={self.random_fields_id},field_integral_coefficients_id={self.field_integral_coefficients_id},linear_saturation_coefficients_id={self.linear_saturation_coefficients_id},)"



    


class WigglerMagnet(Base):
    """
    Periodic wiggler/undulator field.
    """
    __tablename__ = 'Wiggler_Magnet'

    id = Column(Integer(), primary_key=True, autoincrement=True , nullable=False )
    length = Column(Float())
    strength = Column(Float())
    peak_magnetic_field = Column(Float())
    period = Column(Float())
    num_periods = Column(Integer())
    helical = Column(Boolean())
    quadratic_roll_off_x = Column(Float())
    quadratic_roll_off_y = Column(Float())
    transverse_gradient_x = Column(Float())
    transverse_gradient_y = Column(Float())
    

    def __repr__(self):
        return f"Wiggler_Magnet(id={self.id},length={self.length},strength={self.strength},peak_magnetic_field={self.peak_magnetic_field},period={self.period},num_periods={self.num_periods},helical={self.helical},quadratic_roll_off_x={self.quadratic_roll_off_x},quadratic_roll_off_y={self.quadratic_roll_off_y},transverse_gradient_x={self.transverse_gradient_x},transverse_gradient_y={self.transverse_gradient_y},)"



    


class NonLinearLensMagnet(Base):
    """
    Integrable-optics non-linear lens field.  See the MAD-X manual and Danilov/Nagaitsev, PAC2011 WEP070.
    """
    __tablename__ = 'NonLinearLens_Magnet'

    id = Column(Integer(), primary_key=True, autoincrement=True , nullable=False )
    length = Column(Float())
    integrated_strength = Column(Float())
    dimensional_parameter = Column(Float())
    

    def __repr__(self):
        return f"NonLinearLens_Magnet(id={self.id},length={self.length},integrated_strength={self.integrated_strength},dimensional_parameter={self.dimensional_parameter},)"



    


class ReferenceElementDrawings(Base):
    """
    None
    """
    __tablename__ = 'ReferenceElement_drawings'

    ReferenceElement_id = Column(Integer(), ForeignKey('ReferenceElement.id'), primary_key=True)
    drawings = Column(Text(), primary_key=True)
    

    def __repr__(self):
        return f"ReferenceElement_drawings(ReferenceElement_id={self.ReferenceElement_id},drawings={self.drawings},)"



    


class ReferenceElementDesignFiles(Base):
    """
    None
    """
    __tablename__ = 'ReferenceElement_design_files'

    ReferenceElement_id = Column(Integer(), ForeignKey('ReferenceElement.id'), primary_key=True)
    design_files = Column(Text(), primary_key=True)
    

    def __repr__(self):
        return f"ReferenceElement_design_files(ReferenceElement_id={self.ReferenceElement_id},design_files={self.design_files},)"



    


class AcceleratorElementAlias(Base):
    """
    None
    """
    __tablename__ = 'AcceleratorElement_alias'

    AcceleratorElement_name = Column(Text(), ForeignKey('AcceleratorElement.name'), primary_key=True)
    alias = Column(Text(), primary_key=True)
    

    def __repr__(self):
        return f"AcceleratorElement_alias(AcceleratorElement_name={self.AcceleratorElement_name},alias={self.alias},)"



    


class AcceleratorElementInputs(Base):
    """
    None
    """
    __tablename__ = 'AcceleratorElement_inputs'

    AcceleratorElement_name = Column(Text(), ForeignKey('AcceleratorElement.name'), primary_key=True)
    inputs = Column(Enum('current', 'voltage', 'phase', 'setpoint', 'on_off_state', 'open_closed_state', 'position', 'rotation', 'power', 'pressure', 'charge', 'absolute_time', 'relative_time', 'shot_number', 'value', 'waveform', 'magnetic_field', name='IOTypeEnum'), primary_key=True)
    

    def __repr__(self):
        return f"AcceleratorElement_inputs(AcceleratorElement_name={self.AcceleratorElement_name},inputs={self.inputs},)"



    


class AcceleratorElementOutputs(Base):
    """
    None
    """
    __tablename__ = 'AcceleratorElement_outputs'

    AcceleratorElement_name = Column(Text(), ForeignKey('AcceleratorElement.name'), primary_key=True)
    outputs = Column(Enum('current', 'voltage', 'phase', 'setpoint', 'on_off_state', 'open_closed_state', 'position', 'rotation', 'power', 'pressure', 'charge', 'absolute_time', 'relative_time', 'shot_number', 'value', 'waveform', 'magnetic_field', name='IOTypeEnum'), primary_key=True)
    

    def __repr__(self):
        return f"AcceleratorElement_outputs(AcceleratorElement_name={self.AcceleratorElement_name},outputs={self.outputs},)"



    


class AcceleratorElementUpstream(Base):
    """
    None
    """
    __tablename__ = 'AcceleratorElement_upstream'

    AcceleratorElement_name = Column(Text(), ForeignKey('AcceleratorElement.name'), primary_key=True)
    upstream_name = Column(Text(), ForeignKey('AcceleratorElement.name'), primary_key=True)
    

    def __repr__(self):
        return f"AcceleratorElement_upstream(AcceleratorElement_name={self.AcceleratorElement_name},upstream_name={self.upstream_name},)"



    


class AcceleratorElementDownstream(Base):
    """
    None
    """
    __tablename__ = 'AcceleratorElement_downstream'

    AcceleratorElement_name = Column(Text(), ForeignKey('AcceleratorElement.name'), primary_key=True)
    downstream_name = Column(Text(), ForeignKey('AcceleratorElement.name'), primary_key=True)
    

    def __repr__(self):
        return f"AcceleratorElement_downstream(AcceleratorElement_name={self.AcceleratorElement_name},downstream_name={self.downstream_name},)"



    


class StandardElementAlias(Base):
    """
    None
    """
    __tablename__ = 'StandardElement_alias'

    StandardElement_name = Column(Text(), ForeignKey('StandardElement.name'), primary_key=True)
    alias = Column(Text(), primary_key=True)
    

    def __repr__(self):
        return f"StandardElement_alias(StandardElement_name={self.StandardElement_name},alias={self.alias},)"



    


class StandardElementInputs(Base):
    """
    None
    """
    __tablename__ = 'StandardElement_inputs'

    StandardElement_name = Column(Text(), ForeignKey('StandardElement.name'), primary_key=True)
    inputs = Column(Enum('current', 'voltage', 'phase', 'setpoint', 'on_off_state', 'open_closed_state', 'position', 'rotation', 'power', 'pressure', 'charge', 'absolute_time', 'relative_time', 'shot_number', 'value', 'waveform', 'magnetic_field', name='IOTypeEnum'), primary_key=True)
    

    def __repr__(self):
        return f"StandardElement_inputs(StandardElement_name={self.StandardElement_name},inputs={self.inputs},)"



    


class StandardElementOutputs(Base):
    """
    None
    """
    __tablename__ = 'StandardElement_outputs'

    StandardElement_name = Column(Text(), ForeignKey('StandardElement.name'), primary_key=True)
    outputs = Column(Enum('current', 'voltage', 'phase', 'setpoint', 'on_off_state', 'open_closed_state', 'position', 'rotation', 'power', 'pressure', 'charge', 'absolute_time', 'relative_time', 'shot_number', 'value', 'waveform', 'magnetic_field', name='IOTypeEnum'), primary_key=True)
    

    def __repr__(self):
        return f"StandardElement_outputs(StandardElement_name={self.StandardElement_name},outputs={self.outputs},)"



    


class StandardElementUpstream(Base):
    """
    None
    """
    __tablename__ = 'StandardElement_upstream'

    StandardElement_name = Column(Text(), ForeignKey('StandardElement.name'), primary_key=True)
    upstream_name = Column(Text(), ForeignKey('AcceleratorElement.name'), primary_key=True)
    

    def __repr__(self):
        return f"StandardElement_upstream(StandardElement_name={self.StandardElement_name},upstream_name={self.upstream_name},)"



    


class StandardElementDownstream(Base):
    """
    None
    """
    __tablename__ = 'StandardElement_downstream'

    StandardElement_name = Column(Text(), ForeignKey('StandardElement.name'), primary_key=True)
    downstream_name = Column(Text(), ForeignKey('AcceleratorElement.name'), primary_key=True)
    

    def __repr__(self):
        return f"StandardElement_downstream(StandardElement_name={self.StandardElement_name},downstream_name={self.downstream_name},)"



    


class ElementAlias(Base):
    """
    None
    """
    __tablename__ = 'Element_alias'

    Element_name = Column(Text(), ForeignKey('Element.name'), primary_key=True)
    alias = Column(Text(), primary_key=True)
    

    def __repr__(self):
        return f"Element_alias(Element_name={self.Element_name},alias={self.alias},)"



    


class ElementInputs(Base):
    """
    None
    """
    __tablename__ = 'Element_inputs'

    Element_name = Column(Text(), ForeignKey('Element.name'), primary_key=True)
    inputs = Column(Enum('current', 'voltage', 'phase', 'setpoint', 'on_off_state', 'open_closed_state', 'position', 'rotation', 'power', 'pressure', 'charge', 'absolute_time', 'relative_time', 'shot_number', 'value', 'waveform', 'magnetic_field', name='IOTypeEnum'), primary_key=True)
    

    def __repr__(self):
        return f"Element_inputs(Element_name={self.Element_name},inputs={self.inputs},)"



    


class ElementOutputs(Base):
    """
    None
    """
    __tablename__ = 'Element_outputs'

    Element_name = Column(Text(), ForeignKey('Element.name'), primary_key=True)
    outputs = Column(Enum('current', 'voltage', 'phase', 'setpoint', 'on_off_state', 'open_closed_state', 'position', 'rotation', 'power', 'pressure', 'charge', 'absolute_time', 'relative_time', 'shot_number', 'value', 'waveform', 'magnetic_field', name='IOTypeEnum'), primary_key=True)
    

    def __repr__(self):
        return f"Element_outputs(Element_name={self.Element_name},outputs={self.outputs},)"



    


class ElementUpstream(Base):
    """
    None
    """
    __tablename__ = 'Element_upstream'

    Element_name = Column(Text(), ForeignKey('Element.name'), primary_key=True)
    upstream_name = Column(Text(), ForeignKey('AcceleratorElement.name'), primary_key=True)
    

    def __repr__(self):
        return f"Element_upstream(Element_name={self.Element_name},upstream_name={self.upstream_name},)"



    


class ElementDownstream(Base):
    """
    None
    """
    __tablename__ = 'Element_downstream'

    Element_name = Column(Text(), ForeignKey('Element.name'), primary_key=True)
    downstream_name = Column(Text(), ForeignKey('AcceleratorElement.name'), primary_key=True)
    

    def __repr__(self):
        return f"Element_downstream(Element_name={self.Element_name},downstream_name={self.downstream_name},)"



    


class PhysicalAcceleratorElementAlias(Base):
    """
    None
    """
    __tablename__ = 'PhysicalAcceleratorElement_alias'

    PhysicalAcceleratorElement_name = Column(Text(), ForeignKey('PhysicalAcceleratorElement.name'), primary_key=True)
    alias = Column(Text(), primary_key=True)
    

    def __repr__(self):
        return f"PhysicalAcceleratorElement_alias(PhysicalAcceleratorElement_name={self.PhysicalAcceleratorElement_name},alias={self.alias},)"



    


class PhysicalAcceleratorElementInputs(Base):
    """
    None
    """
    __tablename__ = 'PhysicalAcceleratorElement_inputs'

    PhysicalAcceleratorElement_name = Column(Text(), ForeignKey('PhysicalAcceleratorElement.name'), primary_key=True)
    inputs = Column(Enum('current', 'voltage', 'phase', 'setpoint', 'on_off_state', 'open_closed_state', 'position', 'rotation', 'power', 'pressure', 'charge', 'absolute_time', 'relative_time', 'shot_number', 'value', 'waveform', 'magnetic_field', name='IOTypeEnum'), primary_key=True)
    

    def __repr__(self):
        return f"PhysicalAcceleratorElement_inputs(PhysicalAcceleratorElement_name={self.PhysicalAcceleratorElement_name},inputs={self.inputs},)"



    


class PhysicalAcceleratorElementOutputs(Base):
    """
    None
    """
    __tablename__ = 'PhysicalAcceleratorElement_outputs'

    PhysicalAcceleratorElement_name = Column(Text(), ForeignKey('PhysicalAcceleratorElement.name'), primary_key=True)
    outputs = Column(Enum('current', 'voltage', 'phase', 'setpoint', 'on_off_state', 'open_closed_state', 'position', 'rotation', 'power', 'pressure', 'charge', 'absolute_time', 'relative_time', 'shot_number', 'value', 'waveform', 'magnetic_field', name='IOTypeEnum'), primary_key=True)
    

    def __repr__(self):
        return f"PhysicalAcceleratorElement_outputs(PhysicalAcceleratorElement_name={self.PhysicalAcceleratorElement_name},outputs={self.outputs},)"



    


class PhysicalAcceleratorElementUpstream(Base):
    """
    None
    """
    __tablename__ = 'PhysicalAcceleratorElement_upstream'

    PhysicalAcceleratorElement_name = Column(Text(), ForeignKey('PhysicalAcceleratorElement.name'), primary_key=True)
    upstream_name = Column(Text(), ForeignKey('AcceleratorElement.name'), primary_key=True)
    

    def __repr__(self):
        return f"PhysicalAcceleratorElement_upstream(PhysicalAcceleratorElement_name={self.PhysicalAcceleratorElement_name},upstream_name={self.upstream_name},)"



    


class PhysicalAcceleratorElementDownstream(Base):
    """
    None
    """
    __tablename__ = 'PhysicalAcceleratorElement_downstream'

    PhysicalAcceleratorElement_name = Column(Text(), ForeignKey('PhysicalAcceleratorElement.name'), primary_key=True)
    downstream_name = Column(Text(), ForeignKey('AcceleratorElement.name'), primary_key=True)
    

    def __repr__(self):
        return f"PhysicalAcceleratorElement_downstream(PhysicalAcceleratorElement_name={self.PhysicalAcceleratorElement_name},downstream_name={self.downstream_name},)"



    


class ShutterElementInterlocks(Base):
    """
    None
    """
    __tablename__ = 'ShutterElement_interlocks'

    ShutterElement_id = Column(Integer(), ForeignKey('ShutterElement.id'), primary_key=True)
    interlocks = Column(Text(), primary_key=True)
    

    def __repr__(self):
        return f"ShutterElement_interlocks(ShutterElement_id={self.ShutterElement_id},interlocks={self.interlocks},)"



    


class TwissMatchAlias(Base):
    """
    None
    """
    __tablename__ = 'TwissMatch_alias'

    TwissMatch_name = Column(Text(), ForeignKey('TwissMatch.name'), primary_key=True)
    alias = Column(Text(), primary_key=True)
    

    def __repr__(self):
        return f"TwissMatch_alias(TwissMatch_name={self.TwissMatch_name},alias={self.alias},)"



    


class TwissMatchInputs(Base):
    """
    None
    """
    __tablename__ = 'TwissMatch_inputs'

    TwissMatch_name = Column(Text(), ForeignKey('TwissMatch.name'), primary_key=True)
    inputs = Column(Enum('current', 'voltage', 'phase', 'setpoint', 'on_off_state', 'open_closed_state', 'position', 'rotation', 'power', 'pressure', 'charge', 'absolute_time', 'relative_time', 'shot_number', 'value', 'waveform', 'magnetic_field', name='IOTypeEnum'), primary_key=True)
    

    def __repr__(self):
        return f"TwissMatch_inputs(TwissMatch_name={self.TwissMatch_name},inputs={self.inputs},)"



    


class TwissMatchOutputs(Base):
    """
    None
    """
    __tablename__ = 'TwissMatch_outputs'

    TwissMatch_name = Column(Text(), ForeignKey('TwissMatch.name'), primary_key=True)
    outputs = Column(Enum('current', 'voltage', 'phase', 'setpoint', 'on_off_state', 'open_closed_state', 'position', 'rotation', 'power', 'pressure', 'charge', 'absolute_time', 'relative_time', 'shot_number', 'value', 'waveform', 'magnetic_field', name='IOTypeEnum'), primary_key=True)
    

    def __repr__(self):
        return f"TwissMatch_outputs(TwissMatch_name={self.TwissMatch_name},outputs={self.outputs},)"



    


class TwissMatchUpstream(Base):
    """
    None
    """
    __tablename__ = 'TwissMatch_upstream'

    TwissMatch_name = Column(Text(), ForeignKey('TwissMatch.name'), primary_key=True)
    upstream_name = Column(Text(), ForeignKey('AcceleratorElement.name'), primary_key=True)
    

    def __repr__(self):
        return f"TwissMatch_upstream(TwissMatch_name={self.TwissMatch_name},upstream_name={self.upstream_name},)"



    


class TwissMatchDownstream(Base):
    """
    None
    """
    __tablename__ = 'TwissMatch_downstream'

    TwissMatch_name = Column(Text(), ForeignKey('TwissMatch.name'), primary_key=True)
    downstream_name = Column(Text(), ForeignKey('AcceleratorElement.name'), primary_key=True)
    

    def __repr__(self):
        return f"TwissMatch_downstream(TwissMatch_name={self.TwissMatch_name},downstream_name={self.downstream_name},)"



    


class MatrixTransformAlias(Base):
    """
    None
    """
    __tablename__ = 'MatrixTransform_alias'

    MatrixTransform_name = Column(Text(), ForeignKey('MatrixTransform.name'), primary_key=True)
    alias = Column(Text(), primary_key=True)
    

    def __repr__(self):
        return f"MatrixTransform_alias(MatrixTransform_name={self.MatrixTransform_name},alias={self.alias},)"



    


class MatrixTransformInputs(Base):
    """
    None
    """
    __tablename__ = 'MatrixTransform_inputs'

    MatrixTransform_name = Column(Text(), ForeignKey('MatrixTransform.name'), primary_key=True)
    inputs = Column(Enum('current', 'voltage', 'phase', 'setpoint', 'on_off_state', 'open_closed_state', 'position', 'rotation', 'power', 'pressure', 'charge', 'absolute_time', 'relative_time', 'shot_number', 'value', 'waveform', 'magnetic_field', name='IOTypeEnum'), primary_key=True)
    

    def __repr__(self):
        return f"MatrixTransform_inputs(MatrixTransform_name={self.MatrixTransform_name},inputs={self.inputs},)"



    


class MatrixTransformOutputs(Base):
    """
    None
    """
    __tablename__ = 'MatrixTransform_outputs'

    MatrixTransform_name = Column(Text(), ForeignKey('MatrixTransform.name'), primary_key=True)
    outputs = Column(Enum('current', 'voltage', 'phase', 'setpoint', 'on_off_state', 'open_closed_state', 'position', 'rotation', 'power', 'pressure', 'charge', 'absolute_time', 'relative_time', 'shot_number', 'value', 'waveform', 'magnetic_field', name='IOTypeEnum'), primary_key=True)
    

    def __repr__(self):
        return f"MatrixTransform_outputs(MatrixTransform_name={self.MatrixTransform_name},outputs={self.outputs},)"



    


class MatrixTransformUpstream(Base):
    """
    None
    """
    __tablename__ = 'MatrixTransform_upstream'

    MatrixTransform_name = Column(Text(), ForeignKey('MatrixTransform.name'), primary_key=True)
    upstream_name = Column(Text(), ForeignKey('AcceleratorElement.name'), primary_key=True)
    

    def __repr__(self):
        return f"MatrixTransform_upstream(MatrixTransform_name={self.MatrixTransform_name},upstream_name={self.upstream_name},)"



    


class MatrixTransformDownstream(Base):
    """
    None
    """
    __tablename__ = 'MatrixTransform_downstream'

    MatrixTransform_name = Column(Text(), ForeignKey('MatrixTransform.name'), primary_key=True)
    downstream_name = Column(Text(), ForeignKey('AcceleratorElement.name'), primary_key=True)
    

    def __repr__(self):
        return f"MatrixTransform_downstream(MatrixTransform_name={self.MatrixTransform_name},downstream_name={self.downstream_name},)"



    


class ElectrostaticSeparatorAlias(Base):
    """
    None
    """
    __tablename__ = 'ElectrostaticSeparator_alias'

    ElectrostaticSeparator_name = Column(Text(), ForeignKey('ElectrostaticSeparator.name'), primary_key=True)
    alias = Column(Text(), primary_key=True)
    

    def __repr__(self):
        return f"ElectrostaticSeparator_alias(ElectrostaticSeparator_name={self.ElectrostaticSeparator_name},alias={self.alias},)"



    


class ElectrostaticSeparatorInputs(Base):
    """
    None
    """
    __tablename__ = 'ElectrostaticSeparator_inputs'

    ElectrostaticSeparator_name = Column(Text(), ForeignKey('ElectrostaticSeparator.name'), primary_key=True)
    inputs = Column(Enum('current', 'voltage', 'phase', 'setpoint', 'on_off_state', 'open_closed_state', 'position', 'rotation', 'power', 'pressure', 'charge', 'absolute_time', 'relative_time', 'shot_number', 'value', 'waveform', 'magnetic_field', name='IOTypeEnum'), primary_key=True)
    

    def __repr__(self):
        return f"ElectrostaticSeparator_inputs(ElectrostaticSeparator_name={self.ElectrostaticSeparator_name},inputs={self.inputs},)"



    


class ElectrostaticSeparatorOutputs(Base):
    """
    None
    """
    __tablename__ = 'ElectrostaticSeparator_outputs'

    ElectrostaticSeparator_name = Column(Text(), ForeignKey('ElectrostaticSeparator.name'), primary_key=True)
    outputs = Column(Enum('current', 'voltage', 'phase', 'setpoint', 'on_off_state', 'open_closed_state', 'position', 'rotation', 'power', 'pressure', 'charge', 'absolute_time', 'relative_time', 'shot_number', 'value', 'waveform', 'magnetic_field', name='IOTypeEnum'), primary_key=True)
    

    def __repr__(self):
        return f"ElectrostaticSeparator_outputs(ElectrostaticSeparator_name={self.ElectrostaticSeparator_name},outputs={self.outputs},)"



    


class ElectrostaticSeparatorUpstream(Base):
    """
    None
    """
    __tablename__ = 'ElectrostaticSeparator_upstream'

    ElectrostaticSeparator_name = Column(Text(), ForeignKey('ElectrostaticSeparator.name'), primary_key=True)
    upstream_name = Column(Text(), ForeignKey('AcceleratorElement.name'), primary_key=True)
    

    def __repr__(self):
        return f"ElectrostaticSeparator_upstream(ElectrostaticSeparator_name={self.ElectrostaticSeparator_name},upstream_name={self.upstream_name},)"



    


class ElectrostaticSeparatorDownstream(Base):
    """
    None
    """
    __tablename__ = 'ElectrostaticSeparator_downstream'

    ElectrostaticSeparator_name = Column(Text(), ForeignKey('ElectrostaticSeparator.name'), primary_key=True)
    downstream_name = Column(Text(), ForeignKey('AcceleratorElement.name'), primary_key=True)
    

    def __repr__(self):
        return f"ElectrostaticSeparator_downstream(ElectrostaticSeparator_name={self.ElectrostaticSeparator_name},downstream_name={self.downstream_name},)"



    


class ACDipoleAlias(Base):
    """
    None
    """
    __tablename__ = 'ACDipole_alias'

    ACDipole_name = Column(Text(), ForeignKey('ACDipole.name'), primary_key=True)
    alias = Column(Text(), primary_key=True)
    

    def __repr__(self):
        return f"ACDipole_alias(ACDipole_name={self.ACDipole_name},alias={self.alias},)"



    


class ACDipoleInputs(Base):
    """
    None
    """
    __tablename__ = 'ACDipole_inputs'

    ACDipole_name = Column(Text(), ForeignKey('ACDipole.name'), primary_key=True)
    inputs = Column(Enum('current', 'voltage', 'phase', 'setpoint', 'on_off_state', 'open_closed_state', 'position', 'rotation', 'power', 'pressure', 'charge', 'absolute_time', 'relative_time', 'shot_number', 'value', 'waveform', 'magnetic_field', name='IOTypeEnum'), primary_key=True)
    

    def __repr__(self):
        return f"ACDipole_inputs(ACDipole_name={self.ACDipole_name},inputs={self.inputs},)"



    


class ACDipoleOutputs(Base):
    """
    None
    """
    __tablename__ = 'ACDipole_outputs'

    ACDipole_name = Column(Text(), ForeignKey('ACDipole.name'), primary_key=True)
    outputs = Column(Enum('current', 'voltage', 'phase', 'setpoint', 'on_off_state', 'open_closed_state', 'position', 'rotation', 'power', 'pressure', 'charge', 'absolute_time', 'relative_time', 'shot_number', 'value', 'waveform', 'magnetic_field', name='IOTypeEnum'), primary_key=True)
    

    def __repr__(self):
        return f"ACDipole_outputs(ACDipole_name={self.ACDipole_name},outputs={self.outputs},)"



    


class ACDipoleUpstream(Base):
    """
    None
    """
    __tablename__ = 'ACDipole_upstream'

    ACDipole_name = Column(Text(), ForeignKey('ACDipole.name'), primary_key=True)
    upstream_name = Column(Text(), ForeignKey('AcceleratorElement.name'), primary_key=True)
    

    def __repr__(self):
        return f"ACDipole_upstream(ACDipole_name={self.ACDipole_name},upstream_name={self.upstream_name},)"



    


class ACDipoleDownstream(Base):
    """
    None
    """
    __tablename__ = 'ACDipole_downstream'

    ACDipole_name = Column(Text(), ForeignKey('ACDipole.name'), primary_key=True)
    downstream_name = Column(Text(), ForeignKey('AcceleratorElement.name'), primary_key=True)
    

    def __repr__(self):
        return f"ACDipole_downstream(ACDipole_name={self.ACDipole_name},downstream_name={self.downstream_name},)"



    


class HorizontalACDipoleAlias(Base):
    """
    None
    """
    __tablename__ = 'Horizontal_AC_Dipole_alias'

    Horizontal_AC_Dipole_name = Column(Text(), ForeignKey('Horizontal_AC_Dipole.name'), primary_key=True)
    alias = Column(Text(), primary_key=True)
    

    def __repr__(self):
        return f"Horizontal_AC_Dipole_alias(Horizontal_AC_Dipole_name={self.Horizontal_AC_Dipole_name},alias={self.alias},)"



    


class HorizontalACDipoleInputs(Base):
    """
    None
    """
    __tablename__ = 'Horizontal_AC_Dipole_inputs'

    Horizontal_AC_Dipole_name = Column(Text(), ForeignKey('Horizontal_AC_Dipole.name'), primary_key=True)
    inputs = Column(Enum('current', 'voltage', 'phase', 'setpoint', 'on_off_state', 'open_closed_state', 'position', 'rotation', 'power', 'pressure', 'charge', 'absolute_time', 'relative_time', 'shot_number', 'value', 'waveform', 'magnetic_field', name='IOTypeEnum'), primary_key=True)
    

    def __repr__(self):
        return f"Horizontal_AC_Dipole_inputs(Horizontal_AC_Dipole_name={self.Horizontal_AC_Dipole_name},inputs={self.inputs},)"



    


class HorizontalACDipoleOutputs(Base):
    """
    None
    """
    __tablename__ = 'Horizontal_AC_Dipole_outputs'

    Horizontal_AC_Dipole_name = Column(Text(), ForeignKey('Horizontal_AC_Dipole.name'), primary_key=True)
    outputs = Column(Enum('current', 'voltage', 'phase', 'setpoint', 'on_off_state', 'open_closed_state', 'position', 'rotation', 'power', 'pressure', 'charge', 'absolute_time', 'relative_time', 'shot_number', 'value', 'waveform', 'magnetic_field', name='IOTypeEnum'), primary_key=True)
    

    def __repr__(self):
        return f"Horizontal_AC_Dipole_outputs(Horizontal_AC_Dipole_name={self.Horizontal_AC_Dipole_name},outputs={self.outputs},)"



    


class HorizontalACDipoleUpstream(Base):
    """
    None
    """
    __tablename__ = 'Horizontal_AC_Dipole_upstream'

    Horizontal_AC_Dipole_name = Column(Text(), ForeignKey('Horizontal_AC_Dipole.name'), primary_key=True)
    upstream_name = Column(Text(), ForeignKey('AcceleratorElement.name'), primary_key=True)
    

    def __repr__(self):
        return f"Horizontal_AC_Dipole_upstream(Horizontal_AC_Dipole_name={self.Horizontal_AC_Dipole_name},upstream_name={self.upstream_name},)"



    


class HorizontalACDipoleDownstream(Base):
    """
    None
    """
    __tablename__ = 'Horizontal_AC_Dipole_downstream'

    Horizontal_AC_Dipole_name = Column(Text(), ForeignKey('Horizontal_AC_Dipole.name'), primary_key=True)
    downstream_name = Column(Text(), ForeignKey('AcceleratorElement.name'), primary_key=True)
    

    def __repr__(self):
        return f"Horizontal_AC_Dipole_downstream(Horizontal_AC_Dipole_name={self.Horizontal_AC_Dipole_name},downstream_name={self.downstream_name},)"



    


class VerticalACDipoleAlias(Base):
    """
    None
    """
    __tablename__ = 'Vertical_AC_Dipole_alias'

    Vertical_AC_Dipole_name = Column(Text(), ForeignKey('Vertical_AC_Dipole.name'), primary_key=True)
    alias = Column(Text(), primary_key=True)
    

    def __repr__(self):
        return f"Vertical_AC_Dipole_alias(Vertical_AC_Dipole_name={self.Vertical_AC_Dipole_name},alias={self.alias},)"



    


class VerticalACDipoleInputs(Base):
    """
    None
    """
    __tablename__ = 'Vertical_AC_Dipole_inputs'

    Vertical_AC_Dipole_name = Column(Text(), ForeignKey('Vertical_AC_Dipole.name'), primary_key=True)
    inputs = Column(Enum('current', 'voltage', 'phase', 'setpoint', 'on_off_state', 'open_closed_state', 'position', 'rotation', 'power', 'pressure', 'charge', 'absolute_time', 'relative_time', 'shot_number', 'value', 'waveform', 'magnetic_field', name='IOTypeEnum'), primary_key=True)
    

    def __repr__(self):
        return f"Vertical_AC_Dipole_inputs(Vertical_AC_Dipole_name={self.Vertical_AC_Dipole_name},inputs={self.inputs},)"



    


class VerticalACDipoleOutputs(Base):
    """
    None
    """
    __tablename__ = 'Vertical_AC_Dipole_outputs'

    Vertical_AC_Dipole_name = Column(Text(), ForeignKey('Vertical_AC_Dipole.name'), primary_key=True)
    outputs = Column(Enum('current', 'voltage', 'phase', 'setpoint', 'on_off_state', 'open_closed_state', 'position', 'rotation', 'power', 'pressure', 'charge', 'absolute_time', 'relative_time', 'shot_number', 'value', 'waveform', 'magnetic_field', name='IOTypeEnum'), primary_key=True)
    

    def __repr__(self):
        return f"Vertical_AC_Dipole_outputs(Vertical_AC_Dipole_name={self.Vertical_AC_Dipole_name},outputs={self.outputs},)"



    


class VerticalACDipoleUpstream(Base):
    """
    None
    """
    __tablename__ = 'Vertical_AC_Dipole_upstream'

    Vertical_AC_Dipole_name = Column(Text(), ForeignKey('Vertical_AC_Dipole.name'), primary_key=True)
    upstream_name = Column(Text(), ForeignKey('AcceleratorElement.name'), primary_key=True)
    

    def __repr__(self):
        return f"Vertical_AC_Dipole_upstream(Vertical_AC_Dipole_name={self.Vertical_AC_Dipole_name},upstream_name={self.upstream_name},)"



    


class VerticalACDipoleDownstream(Base):
    """
    None
    """
    __tablename__ = 'Vertical_AC_Dipole_downstream'

    Vertical_AC_Dipole_name = Column(Text(), ForeignKey('Vertical_AC_Dipole.name'), primary_key=True)
    downstream_name = Column(Text(), ForeignKey('AcceleratorElement.name'), primary_key=True)
    

    def __repr__(self):
        return f"Vertical_AC_Dipole_downstream(Vertical_AC_Dipole_name={self.Vertical_AC_Dipole_name},downstream_name={self.downstream_name},)"



    


class WireAlias(Base):
    """
    None
    """
    __tablename__ = 'Wire_alias'

    Wire_name = Column(Text(), ForeignKey('Wire.name'), primary_key=True)
    alias = Column(Text(), primary_key=True)
    

    def __repr__(self):
        return f"Wire_alias(Wire_name={self.Wire_name},alias={self.alias},)"



    


class WireInputs(Base):
    """
    None
    """
    __tablename__ = 'Wire_inputs'

    Wire_name = Column(Text(), ForeignKey('Wire.name'), primary_key=True)
    inputs = Column(Enum('current', 'voltage', 'phase', 'setpoint', 'on_off_state', 'open_closed_state', 'position', 'rotation', 'power', 'pressure', 'charge', 'absolute_time', 'relative_time', 'shot_number', 'value', 'waveform', 'magnetic_field', name='IOTypeEnum'), primary_key=True)
    

    def __repr__(self):
        return f"Wire_inputs(Wire_name={self.Wire_name},inputs={self.inputs},)"



    


class WireOutputs(Base):
    """
    None
    """
    __tablename__ = 'Wire_outputs'

    Wire_name = Column(Text(), ForeignKey('Wire.name'), primary_key=True)
    outputs = Column(Enum('current', 'voltage', 'phase', 'setpoint', 'on_off_state', 'open_closed_state', 'position', 'rotation', 'power', 'pressure', 'charge', 'absolute_time', 'relative_time', 'shot_number', 'value', 'waveform', 'magnetic_field', name='IOTypeEnum'), primary_key=True)
    

    def __repr__(self):
        return f"Wire_outputs(Wire_name={self.Wire_name},outputs={self.outputs},)"



    


class WireUpstream(Base):
    """
    None
    """
    __tablename__ = 'Wire_upstream'

    Wire_name = Column(Text(), ForeignKey('Wire.name'), primary_key=True)
    upstream_name = Column(Text(), ForeignKey('AcceleratorElement.name'), primary_key=True)
    

    def __repr__(self):
        return f"Wire_upstream(Wire_name={self.Wire_name},upstream_name={self.upstream_name},)"



    


class WireDownstream(Base):
    """
    None
    """
    __tablename__ = 'Wire_downstream'

    Wire_name = Column(Text(), ForeignKey('Wire.name'), primary_key=True)
    downstream_name = Column(Text(), ForeignKey('AcceleratorElement.name'), primary_key=True)
    

    def __repr__(self):
        return f"Wire_downstream(Wire_name={self.Wire_name},downstream_name={self.downstream_name},)"



    


class BeamBeamAlias(Base):
    """
    None
    """
    __tablename__ = 'BeamBeam_alias'

    BeamBeam_name = Column(Text(), ForeignKey('BeamBeam.name'), primary_key=True)
    alias = Column(Text(), primary_key=True)
    

    def __repr__(self):
        return f"BeamBeam_alias(BeamBeam_name={self.BeamBeam_name},alias={self.alias},)"



    


class BeamBeamInputs(Base):
    """
    None
    """
    __tablename__ = 'BeamBeam_inputs'

    BeamBeam_name = Column(Text(), ForeignKey('BeamBeam.name'), primary_key=True)
    inputs = Column(Enum('current', 'voltage', 'phase', 'setpoint', 'on_off_state', 'open_closed_state', 'position', 'rotation', 'power', 'pressure', 'charge', 'absolute_time', 'relative_time', 'shot_number', 'value', 'waveform', 'magnetic_field', name='IOTypeEnum'), primary_key=True)
    

    def __repr__(self):
        return f"BeamBeam_inputs(BeamBeam_name={self.BeamBeam_name},inputs={self.inputs},)"



    


class BeamBeamOutputs(Base):
    """
    None
    """
    __tablename__ = 'BeamBeam_outputs'

    BeamBeam_name = Column(Text(), ForeignKey('BeamBeam.name'), primary_key=True)
    outputs = Column(Enum('current', 'voltage', 'phase', 'setpoint', 'on_off_state', 'open_closed_state', 'position', 'rotation', 'power', 'pressure', 'charge', 'absolute_time', 'relative_time', 'shot_number', 'value', 'waveform', 'magnetic_field', name='IOTypeEnum'), primary_key=True)
    

    def __repr__(self):
        return f"BeamBeam_outputs(BeamBeam_name={self.BeamBeam_name},outputs={self.outputs},)"



    


class BeamBeamUpstream(Base):
    """
    None
    """
    __tablename__ = 'BeamBeam_upstream'

    BeamBeam_name = Column(Text(), ForeignKey('BeamBeam.name'), primary_key=True)
    upstream_name = Column(Text(), ForeignKey('AcceleratorElement.name'), primary_key=True)
    

    def __repr__(self):
        return f"BeamBeam_upstream(BeamBeam_name={self.BeamBeam_name},upstream_name={self.upstream_name},)"



    


class BeamBeamDownstream(Base):
    """
    None
    """
    __tablename__ = 'BeamBeam_downstream'

    BeamBeam_name = Column(Text(), ForeignKey('BeamBeam.name'), primary_key=True)
    downstream_name = Column(Text(), ForeignKey('AcceleratorElement.name'), primary_key=True)
    

    def __repr__(self):
        return f"BeamBeam_downstream(BeamBeam_name={self.BeamBeam_name},downstream_name={self.downstream_name},)"



    


class RFMultipoleAlias(Base):
    """
    None
    """
    __tablename__ = 'RFMultipole_alias'

    RFMultipole_name = Column(Text(), ForeignKey('RFMultipole.name'), primary_key=True)
    alias = Column(Text(), primary_key=True)
    

    def __repr__(self):
        return f"RFMultipole_alias(RFMultipole_name={self.RFMultipole_name},alias={self.alias},)"



    


class RFMultipoleInputs(Base):
    """
    None
    """
    __tablename__ = 'RFMultipole_inputs'

    RFMultipole_name = Column(Text(), ForeignKey('RFMultipole.name'), primary_key=True)
    inputs = Column(Enum('current', 'voltage', 'phase', 'setpoint', 'on_off_state', 'open_closed_state', 'position', 'rotation', 'power', 'pressure', 'charge', 'absolute_time', 'relative_time', 'shot_number', 'value', 'waveform', 'magnetic_field', name='IOTypeEnum'), primary_key=True)
    

    def __repr__(self):
        return f"RFMultipole_inputs(RFMultipole_name={self.RFMultipole_name},inputs={self.inputs},)"



    


class RFMultipoleOutputs(Base):
    """
    None
    """
    __tablename__ = 'RFMultipole_outputs'

    RFMultipole_name = Column(Text(), ForeignKey('RFMultipole.name'), primary_key=True)
    outputs = Column(Enum('current', 'voltage', 'phase', 'setpoint', 'on_off_state', 'open_closed_state', 'position', 'rotation', 'power', 'pressure', 'charge', 'absolute_time', 'relative_time', 'shot_number', 'value', 'waveform', 'magnetic_field', name='IOTypeEnum'), primary_key=True)
    

    def __repr__(self):
        return f"RFMultipole_outputs(RFMultipole_name={self.RFMultipole_name},outputs={self.outputs},)"



    


class RFMultipoleUpstream(Base):
    """
    None
    """
    __tablename__ = 'RFMultipole_upstream'

    RFMultipole_name = Column(Text(), ForeignKey('RFMultipole.name'), primary_key=True)
    upstream_name = Column(Text(), ForeignKey('AcceleratorElement.name'), primary_key=True)
    

    def __repr__(self):
        return f"RFMultipole_upstream(RFMultipole_name={self.RFMultipole_name},upstream_name={self.upstream_name},)"



    


class RFMultipoleDownstream(Base):
    """
    None
    """
    __tablename__ = 'RFMultipole_downstream'

    RFMultipole_name = Column(Text(), ForeignKey('RFMultipole.name'), primary_key=True)
    downstream_name = Column(Text(), ForeignKey('AcceleratorElement.name'), primary_key=True)
    

    def __repr__(self):
        return f"RFMultipole_downstream(RFMultipole_name={self.RFMultipole_name},downstream_name={self.downstream_name},)"



    


class StageAlias(Base):
    """
    None
    """
    __tablename__ = 'Stage_alias'

    Stage_name = Column(Text(), ForeignKey('Stage.name'), primary_key=True)
    alias = Column(Text(), primary_key=True)
    

    def __repr__(self):
        return f"Stage_alias(Stage_name={self.Stage_name},alias={self.alias},)"



    


class StageInputs(Base):
    """
    None
    """
    __tablename__ = 'Stage_inputs'

    Stage_name = Column(Text(), ForeignKey('Stage.name'), primary_key=True)
    inputs = Column(Enum('current', 'voltage', 'phase', 'setpoint', 'on_off_state', 'open_closed_state', 'position', 'rotation', 'power', 'pressure', 'charge', 'absolute_time', 'relative_time', 'shot_number', 'value', 'waveform', 'magnetic_field', name='IOTypeEnum'), primary_key=True)
    

    def __repr__(self):
        return f"Stage_inputs(Stage_name={self.Stage_name},inputs={self.inputs},)"



    


class StageOutputs(Base):
    """
    None
    """
    __tablename__ = 'Stage_outputs'

    Stage_name = Column(Text(), ForeignKey('Stage.name'), primary_key=True)
    outputs = Column(Enum('current', 'voltage', 'phase', 'setpoint', 'on_off_state', 'open_closed_state', 'position', 'rotation', 'power', 'pressure', 'charge', 'absolute_time', 'relative_time', 'shot_number', 'value', 'waveform', 'magnetic_field', name='IOTypeEnum'), primary_key=True)
    

    def __repr__(self):
        return f"Stage_outputs(Stage_name={self.Stage_name},outputs={self.outputs},)"



    


class StageUpstream(Base):
    """
    None
    """
    __tablename__ = 'Stage_upstream'

    Stage_name = Column(Text(), ForeignKey('Stage.name'), primary_key=True)
    upstream_name = Column(Text(), ForeignKey('AcceleratorElement.name'), primary_key=True)
    

    def __repr__(self):
        return f"Stage_upstream(Stage_name={self.Stage_name},upstream_name={self.upstream_name},)"



    


class StageDownstream(Base):
    """
    None
    """
    __tablename__ = 'Stage_downstream'

    Stage_name = Column(Text(), ForeignKey('Stage.name'), primary_key=True)
    downstream_name = Column(Text(), ForeignKey('AcceleratorElement.name'), primary_key=True)
    

    def __repr__(self):
        return f"Stage_downstream(Stage_name={self.Stage_name},downstream_name={self.downstream_name},)"



    


class VacuumGaugeAlias(Base):
    """
    None
    """
    __tablename__ = 'VacuumGauge_alias'

    VacuumGauge_name = Column(Text(), ForeignKey('VacuumGauge.name'), primary_key=True)
    alias = Column(Text(), primary_key=True)
    

    def __repr__(self):
        return f"VacuumGauge_alias(VacuumGauge_name={self.VacuumGauge_name},alias={self.alias},)"



    


class VacuumGaugeInputs(Base):
    """
    None
    """
    __tablename__ = 'VacuumGauge_inputs'

    VacuumGauge_name = Column(Text(), ForeignKey('VacuumGauge.name'), primary_key=True)
    inputs = Column(Enum('current', 'voltage', 'phase', 'setpoint', 'on_off_state', 'open_closed_state', 'position', 'rotation', 'power', 'pressure', 'charge', 'absolute_time', 'relative_time', 'shot_number', 'value', 'waveform', 'magnetic_field', name='IOTypeEnum'), primary_key=True)
    

    def __repr__(self):
        return f"VacuumGauge_inputs(VacuumGauge_name={self.VacuumGauge_name},inputs={self.inputs},)"



    


class VacuumGaugeOutputs(Base):
    """
    None
    """
    __tablename__ = 'VacuumGauge_outputs'

    VacuumGauge_name = Column(Text(), ForeignKey('VacuumGauge.name'), primary_key=True)
    outputs = Column(Enum('current', 'voltage', 'phase', 'setpoint', 'on_off_state', 'open_closed_state', 'position', 'rotation', 'power', 'pressure', 'charge', 'absolute_time', 'relative_time', 'shot_number', 'value', 'waveform', 'magnetic_field', name='IOTypeEnum'), primary_key=True)
    

    def __repr__(self):
        return f"VacuumGauge_outputs(VacuumGauge_name={self.VacuumGauge_name},outputs={self.outputs},)"



    


class VacuumGaugeUpstream(Base):
    """
    None
    """
    __tablename__ = 'VacuumGauge_upstream'

    VacuumGauge_name = Column(Text(), ForeignKey('VacuumGauge.name'), primary_key=True)
    upstream_name = Column(Text(), ForeignKey('AcceleratorElement.name'), primary_key=True)
    

    def __repr__(self):
        return f"VacuumGauge_upstream(VacuumGauge_name={self.VacuumGauge_name},upstream_name={self.upstream_name},)"



    


class VacuumGaugeDownstream(Base):
    """
    None
    """
    __tablename__ = 'VacuumGauge_downstream'

    VacuumGauge_name = Column(Text(), ForeignKey('VacuumGauge.name'), primary_key=True)
    downstream_name = Column(Text(), ForeignKey('AcceleratorElement.name'), primary_key=True)
    

    def __repr__(self):
        return f"VacuumGauge_downstream(VacuumGauge_name={self.VacuumGauge_name},downstream_name={self.downstream_name},)"



    


class LaserAlias(Base):
    """
    None
    """
    __tablename__ = 'Laser_alias'

    Laser_name = Column(Text(), ForeignKey('Laser.name'), primary_key=True)
    alias = Column(Text(), primary_key=True)
    

    def __repr__(self):
        return f"Laser_alias(Laser_name={self.Laser_name},alias={self.alias},)"



    


class LaserInputs(Base):
    """
    None
    """
    __tablename__ = 'Laser_inputs'

    Laser_name = Column(Text(), ForeignKey('Laser.name'), primary_key=True)
    inputs = Column(Enum('current', 'voltage', 'phase', 'setpoint', 'on_off_state', 'open_closed_state', 'position', 'rotation', 'power', 'pressure', 'charge', 'absolute_time', 'relative_time', 'shot_number', 'value', 'waveform', 'magnetic_field', name='IOTypeEnum'), primary_key=True)
    

    def __repr__(self):
        return f"Laser_inputs(Laser_name={self.Laser_name},inputs={self.inputs},)"



    


class LaserOutputs(Base):
    """
    None
    """
    __tablename__ = 'Laser_outputs'

    Laser_name = Column(Text(), ForeignKey('Laser.name'), primary_key=True)
    outputs = Column(Enum('current', 'voltage', 'phase', 'setpoint', 'on_off_state', 'open_closed_state', 'position', 'rotation', 'power', 'pressure', 'charge', 'absolute_time', 'relative_time', 'shot_number', 'value', 'waveform', 'magnetic_field', name='IOTypeEnum'), primary_key=True)
    

    def __repr__(self):
        return f"Laser_outputs(Laser_name={self.Laser_name},outputs={self.outputs},)"



    


class LaserUpstream(Base):
    """
    None
    """
    __tablename__ = 'Laser_upstream'

    Laser_name = Column(Text(), ForeignKey('Laser.name'), primary_key=True)
    upstream_name = Column(Text(), ForeignKey('AcceleratorElement.name'), primary_key=True)
    

    def __repr__(self):
        return f"Laser_upstream(Laser_name={self.Laser_name},upstream_name={self.upstream_name},)"



    


class LaserDownstream(Base):
    """
    None
    """
    __tablename__ = 'Laser_downstream'

    Laser_name = Column(Text(), ForeignKey('Laser.name'), primary_key=True)
    downstream_name = Column(Text(), ForeignKey('AcceleratorElement.name'), primary_key=True)
    

    def __repr__(self):
        return f"Laser_downstream(Laser_name={self.Laser_name},downstream_name={self.downstream_name},)"



    


class ShutterAlias(Base):
    """
    None
    """
    __tablename__ = 'Shutter_alias'

    Shutter_name = Column(Text(), ForeignKey('Shutter.name'), primary_key=True)
    alias = Column(Text(), primary_key=True)
    

    def __repr__(self):
        return f"Shutter_alias(Shutter_name={self.Shutter_name},alias={self.alias},)"



    


class ShutterInputs(Base):
    """
    None
    """
    __tablename__ = 'Shutter_inputs'

    Shutter_name = Column(Text(), ForeignKey('Shutter.name'), primary_key=True)
    inputs = Column(Enum('current', 'voltage', 'phase', 'setpoint', 'on_off_state', 'open_closed_state', 'position', 'rotation', 'power', 'pressure', 'charge', 'absolute_time', 'relative_time', 'shot_number', 'value', 'waveform', 'magnetic_field', name='IOTypeEnum'), primary_key=True)
    

    def __repr__(self):
        return f"Shutter_inputs(Shutter_name={self.Shutter_name},inputs={self.inputs},)"



    


class ShutterOutputs(Base):
    """
    None
    """
    __tablename__ = 'Shutter_outputs'

    Shutter_name = Column(Text(), ForeignKey('Shutter.name'), primary_key=True)
    outputs = Column(Enum('current', 'voltage', 'phase', 'setpoint', 'on_off_state', 'open_closed_state', 'position', 'rotation', 'power', 'pressure', 'charge', 'absolute_time', 'relative_time', 'shot_number', 'value', 'waveform', 'magnetic_field', name='IOTypeEnum'), primary_key=True)
    

    def __repr__(self):
        return f"Shutter_outputs(Shutter_name={self.Shutter_name},outputs={self.outputs},)"



    


class ShutterUpstream(Base):
    """
    None
    """
    __tablename__ = 'Shutter_upstream'

    Shutter_name = Column(Text(), ForeignKey('Shutter.name'), primary_key=True)
    upstream_name = Column(Text(), ForeignKey('AcceleratorElement.name'), primary_key=True)
    

    def __repr__(self):
        return f"Shutter_upstream(Shutter_name={self.Shutter_name},upstream_name={self.upstream_name},)"



    


class ShutterDownstream(Base):
    """
    None
    """
    __tablename__ = 'Shutter_downstream'

    Shutter_name = Column(Text(), ForeignKey('Shutter.name'), primary_key=True)
    downstream_name = Column(Text(), ForeignKey('AcceleratorElement.name'), primary_key=True)
    

    def __repr__(self):
        return f"Shutter_downstream(Shutter_name={self.Shutter_name},downstream_name={self.downstream_name},)"



    


class ValveAlias(Base):
    """
    None
    """
    __tablename__ = 'Valve_alias'

    Valve_name = Column(Text(), ForeignKey('Valve.name'), primary_key=True)
    alias = Column(Text(), primary_key=True)
    

    def __repr__(self):
        return f"Valve_alias(Valve_name={self.Valve_name},alias={self.alias},)"



    


class ValveInputs(Base):
    """
    None
    """
    __tablename__ = 'Valve_inputs'

    Valve_name = Column(Text(), ForeignKey('Valve.name'), primary_key=True)
    inputs = Column(Enum('current', 'voltage', 'phase', 'setpoint', 'on_off_state', 'open_closed_state', 'position', 'rotation', 'power', 'pressure', 'charge', 'absolute_time', 'relative_time', 'shot_number', 'value', 'waveform', 'magnetic_field', name='IOTypeEnum'), primary_key=True)
    

    def __repr__(self):
        return f"Valve_inputs(Valve_name={self.Valve_name},inputs={self.inputs},)"



    


class ValveOutputs(Base):
    """
    None
    """
    __tablename__ = 'Valve_outputs'

    Valve_name = Column(Text(), ForeignKey('Valve.name'), primary_key=True)
    outputs = Column(Enum('current', 'voltage', 'phase', 'setpoint', 'on_off_state', 'open_closed_state', 'position', 'rotation', 'power', 'pressure', 'charge', 'absolute_time', 'relative_time', 'shot_number', 'value', 'waveform', 'magnetic_field', name='IOTypeEnum'), primary_key=True)
    

    def __repr__(self):
        return f"Valve_outputs(Valve_name={self.Valve_name},outputs={self.outputs},)"



    


class ValveUpstream(Base):
    """
    None
    """
    __tablename__ = 'Valve_upstream'

    Valve_name = Column(Text(), ForeignKey('Valve.name'), primary_key=True)
    upstream_name = Column(Text(), ForeignKey('AcceleratorElement.name'), primary_key=True)
    

    def __repr__(self):
        return f"Valve_upstream(Valve_name={self.Valve_name},upstream_name={self.upstream_name},)"



    


class ValveDownstream(Base):
    """
    None
    """
    __tablename__ = 'Valve_downstream'

    Valve_name = Column(Text(), ForeignKey('Valve.name'), primary_key=True)
    downstream_name = Column(Text(), ForeignKey('AcceleratorElement.name'), primary_key=True)
    

    def __repr__(self):
        return f"Valve_downstream(Valve_name={self.Valve_name},downstream_name={self.downstream_name},)"



    


class MarkerAlias(Base):
    """
    None
    """
    __tablename__ = 'Marker_alias'

    Marker_name = Column(Text(), ForeignKey('Marker.name'), primary_key=True)
    alias = Column(Text(), primary_key=True)
    

    def __repr__(self):
        return f"Marker_alias(Marker_name={self.Marker_name},alias={self.alias},)"



    


class MarkerInputs(Base):
    """
    None
    """
    __tablename__ = 'Marker_inputs'

    Marker_name = Column(Text(), ForeignKey('Marker.name'), primary_key=True)
    inputs = Column(Enum('current', 'voltage', 'phase', 'setpoint', 'on_off_state', 'open_closed_state', 'position', 'rotation', 'power', 'pressure', 'charge', 'absolute_time', 'relative_time', 'shot_number', 'value', 'waveform', 'magnetic_field', name='IOTypeEnum'), primary_key=True)
    

    def __repr__(self):
        return f"Marker_inputs(Marker_name={self.Marker_name},inputs={self.inputs},)"



    


class MarkerOutputs(Base):
    """
    None
    """
    __tablename__ = 'Marker_outputs'

    Marker_name = Column(Text(), ForeignKey('Marker.name'), primary_key=True)
    outputs = Column(Enum('current', 'voltage', 'phase', 'setpoint', 'on_off_state', 'open_closed_state', 'position', 'rotation', 'power', 'pressure', 'charge', 'absolute_time', 'relative_time', 'shot_number', 'value', 'waveform', 'magnetic_field', name='IOTypeEnum'), primary_key=True)
    

    def __repr__(self):
        return f"Marker_outputs(Marker_name={self.Marker_name},outputs={self.outputs},)"



    


class MarkerUpstream(Base):
    """
    None
    """
    __tablename__ = 'Marker_upstream'

    Marker_name = Column(Text(), ForeignKey('Marker.name'), primary_key=True)
    upstream_name = Column(Text(), ForeignKey('AcceleratorElement.name'), primary_key=True)
    

    def __repr__(self):
        return f"Marker_upstream(Marker_name={self.Marker_name},upstream_name={self.upstream_name},)"



    


class MarkerDownstream(Base):
    """
    None
    """
    __tablename__ = 'Marker_downstream'

    Marker_name = Column(Text(), ForeignKey('Marker.name'), primary_key=True)
    downstream_name = Column(Text(), ForeignKey('AcceleratorElement.name'), primary_key=True)
    

    def __repr__(self):
        return f"Marker_downstream(Marker_name={self.Marker_name},downstream_name={self.downstream_name},)"



    


class ApertureAlias(Base):
    """
    None
    """
    __tablename__ = 'Aperture_alias'

    Aperture_name = Column(Text(), ForeignKey('Aperture.name'), primary_key=True)
    alias = Column(Text(), primary_key=True)
    

    def __repr__(self):
        return f"Aperture_alias(Aperture_name={self.Aperture_name},alias={self.alias},)"



    


class ApertureInputs(Base):
    """
    None
    """
    __tablename__ = 'Aperture_inputs'

    Aperture_name = Column(Text(), ForeignKey('Aperture.name'), primary_key=True)
    inputs = Column(Enum('current', 'voltage', 'phase', 'setpoint', 'on_off_state', 'open_closed_state', 'position', 'rotation', 'power', 'pressure', 'charge', 'absolute_time', 'relative_time', 'shot_number', 'value', 'waveform', 'magnetic_field', name='IOTypeEnum'), primary_key=True)
    

    def __repr__(self):
        return f"Aperture_inputs(Aperture_name={self.Aperture_name},inputs={self.inputs},)"



    


class ApertureOutputs(Base):
    """
    None
    """
    __tablename__ = 'Aperture_outputs'

    Aperture_name = Column(Text(), ForeignKey('Aperture.name'), primary_key=True)
    outputs = Column(Enum('current', 'voltage', 'phase', 'setpoint', 'on_off_state', 'open_closed_state', 'position', 'rotation', 'power', 'pressure', 'charge', 'absolute_time', 'relative_time', 'shot_number', 'value', 'waveform', 'magnetic_field', name='IOTypeEnum'), primary_key=True)
    

    def __repr__(self):
        return f"Aperture_outputs(Aperture_name={self.Aperture_name},outputs={self.outputs},)"



    


class ApertureUpstream(Base):
    """
    None
    """
    __tablename__ = 'Aperture_upstream'

    Aperture_name = Column(Text(), ForeignKey('Aperture.name'), primary_key=True)
    upstream_name = Column(Text(), ForeignKey('AcceleratorElement.name'), primary_key=True)
    

    def __repr__(self):
        return f"Aperture_upstream(Aperture_name={self.Aperture_name},upstream_name={self.upstream_name},)"



    


class ApertureDownstream(Base):
    """
    None
    """
    __tablename__ = 'Aperture_downstream'

    Aperture_name = Column(Text(), ForeignKey('Aperture.name'), primary_key=True)
    downstream_name = Column(Text(), ForeignKey('AcceleratorElement.name'), primary_key=True)
    

    def __repr__(self):
        return f"Aperture_downstream(Aperture_name={self.Aperture_name},downstream_name={self.downstream_name},)"



    


class CollimatorAlias(Base):
    """
    None
    """
    __tablename__ = 'Collimator_alias'

    Collimator_name = Column(Text(), ForeignKey('Collimator.name'), primary_key=True)
    alias = Column(Text(), primary_key=True)
    

    def __repr__(self):
        return f"Collimator_alias(Collimator_name={self.Collimator_name},alias={self.alias},)"



    


class CollimatorInputs(Base):
    """
    None
    """
    __tablename__ = 'Collimator_inputs'

    Collimator_name = Column(Text(), ForeignKey('Collimator.name'), primary_key=True)
    inputs = Column(Enum('current', 'voltage', 'phase', 'setpoint', 'on_off_state', 'open_closed_state', 'position', 'rotation', 'power', 'pressure', 'charge', 'absolute_time', 'relative_time', 'shot_number', 'value', 'waveform', 'magnetic_field', name='IOTypeEnum'), primary_key=True)
    

    def __repr__(self):
        return f"Collimator_inputs(Collimator_name={self.Collimator_name},inputs={self.inputs},)"



    


class CollimatorOutputs(Base):
    """
    None
    """
    __tablename__ = 'Collimator_outputs'

    Collimator_name = Column(Text(), ForeignKey('Collimator.name'), primary_key=True)
    outputs = Column(Enum('current', 'voltage', 'phase', 'setpoint', 'on_off_state', 'open_closed_state', 'position', 'rotation', 'power', 'pressure', 'charge', 'absolute_time', 'relative_time', 'shot_number', 'value', 'waveform', 'magnetic_field', name='IOTypeEnum'), primary_key=True)
    

    def __repr__(self):
        return f"Collimator_outputs(Collimator_name={self.Collimator_name},outputs={self.outputs},)"



    


class CollimatorUpstream(Base):
    """
    None
    """
    __tablename__ = 'Collimator_upstream'

    Collimator_name = Column(Text(), ForeignKey('Collimator.name'), primary_key=True)
    upstream_name = Column(Text(), ForeignKey('AcceleratorElement.name'), primary_key=True)
    

    def __repr__(self):
        return f"Collimator_upstream(Collimator_name={self.Collimator_name},upstream_name={self.upstream_name},)"



    


class CollimatorDownstream(Base):
    """
    None
    """
    __tablename__ = 'Collimator_downstream'

    Collimator_name = Column(Text(), ForeignKey('Collimator.name'), primary_key=True)
    downstream_name = Column(Text(), ForeignKey('AcceleratorElement.name'), primary_key=True)
    

    def __repr__(self):
        return f"Collimator_downstream(Collimator_name={self.Collimator_name},downstream_name={self.downstream_name},)"



    


class DriftAlias(Base):
    """
    None
    """
    __tablename__ = 'Drift_alias'

    Drift_name = Column(Text(), ForeignKey('Drift.name'), primary_key=True)
    alias = Column(Text(), primary_key=True)
    

    def __repr__(self):
        return f"Drift_alias(Drift_name={self.Drift_name},alias={self.alias},)"



    


class DriftInputs(Base):
    """
    None
    """
    __tablename__ = 'Drift_inputs'

    Drift_name = Column(Text(), ForeignKey('Drift.name'), primary_key=True)
    inputs = Column(Enum('current', 'voltage', 'phase', 'setpoint', 'on_off_state', 'open_closed_state', 'position', 'rotation', 'power', 'pressure', 'charge', 'absolute_time', 'relative_time', 'shot_number', 'value', 'waveform', 'magnetic_field', name='IOTypeEnum'), primary_key=True)
    

    def __repr__(self):
        return f"Drift_inputs(Drift_name={self.Drift_name},inputs={self.inputs},)"



    


class DriftOutputs(Base):
    """
    None
    """
    __tablename__ = 'Drift_outputs'

    Drift_name = Column(Text(), ForeignKey('Drift.name'), primary_key=True)
    outputs = Column(Enum('current', 'voltage', 'phase', 'setpoint', 'on_off_state', 'open_closed_state', 'position', 'rotation', 'power', 'pressure', 'charge', 'absolute_time', 'relative_time', 'shot_number', 'value', 'waveform', 'magnetic_field', name='IOTypeEnum'), primary_key=True)
    

    def __repr__(self):
        return f"Drift_outputs(Drift_name={self.Drift_name},outputs={self.outputs},)"



    


class DriftUpstream(Base):
    """
    None
    """
    __tablename__ = 'Drift_upstream'

    Drift_name = Column(Text(), ForeignKey('Drift.name'), primary_key=True)
    upstream_name = Column(Text(), ForeignKey('AcceleratorElement.name'), primary_key=True)
    

    def __repr__(self):
        return f"Drift_upstream(Drift_name={self.Drift_name},upstream_name={self.upstream_name},)"



    


class DriftDownstream(Base):
    """
    None
    """
    __tablename__ = 'Drift_downstream'

    Drift_name = Column(Text(), ForeignKey('Drift.name'), primary_key=True)
    downstream_name = Column(Text(), ForeignKey('AcceleratorElement.name'), primary_key=True)
    

    def __repr__(self):
        return f"Drift_downstream(Drift_name={self.Drift_name},downstream_name={self.downstream_name},)"



    


class LightingAlias(Base):
    """
    None
    """
    __tablename__ = 'Lighting_alias'

    Lighting_name = Column(Text(), ForeignKey('Lighting.name'), primary_key=True)
    alias = Column(Text(), primary_key=True)
    

    def __repr__(self):
        return f"Lighting_alias(Lighting_name={self.Lighting_name},alias={self.alias},)"



    


class LightingInputs(Base):
    """
    None
    """
    __tablename__ = 'Lighting_inputs'

    Lighting_name = Column(Text(), ForeignKey('Lighting.name'), primary_key=True)
    inputs = Column(Enum('current', 'voltage', 'phase', 'setpoint', 'on_off_state', 'open_closed_state', 'position', 'rotation', 'power', 'pressure', 'charge', 'absolute_time', 'relative_time', 'shot_number', 'value', 'waveform', 'magnetic_field', name='IOTypeEnum'), primary_key=True)
    

    def __repr__(self):
        return f"Lighting_inputs(Lighting_name={self.Lighting_name},inputs={self.inputs},)"



    


class LightingOutputs(Base):
    """
    None
    """
    __tablename__ = 'Lighting_outputs'

    Lighting_name = Column(Text(), ForeignKey('Lighting.name'), primary_key=True)
    outputs = Column(Enum('current', 'voltage', 'phase', 'setpoint', 'on_off_state', 'open_closed_state', 'position', 'rotation', 'power', 'pressure', 'charge', 'absolute_time', 'relative_time', 'shot_number', 'value', 'waveform', 'magnetic_field', name='IOTypeEnum'), primary_key=True)
    

    def __repr__(self):
        return f"Lighting_outputs(Lighting_name={self.Lighting_name},outputs={self.outputs},)"



    


class LightingUpstream(Base):
    """
    None
    """
    __tablename__ = 'Lighting_upstream'

    Lighting_name = Column(Text(), ForeignKey('Lighting.name'), primary_key=True)
    upstream_name = Column(Text(), ForeignKey('AcceleratorElement.name'), primary_key=True)
    

    def __repr__(self):
        return f"Lighting_upstream(Lighting_name={self.Lighting_name},upstream_name={self.upstream_name},)"



    


class LightingDownstream(Base):
    """
    None
    """
    __tablename__ = 'Lighting_downstream'

    Lighting_name = Column(Text(), ForeignKey('Lighting.name'), primary_key=True)
    downstream_name = Column(Text(), ForeignKey('AcceleratorElement.name'), primary_key=True)
    

    def __repr__(self):
        return f"Lighting_downstream(Lighting_name={self.Lighting_name},downstream_name={self.downstream_name},)"



    


class PowerSupplyAlias(Base):
    """
    None
    """
    __tablename__ = 'PowerSupply_alias'

    PowerSupply_name = Column(Text(), ForeignKey('PowerSupply.name'), primary_key=True)
    alias = Column(Text(), primary_key=True)
    

    def __repr__(self):
        return f"PowerSupply_alias(PowerSupply_name={self.PowerSupply_name},alias={self.alias},)"



    


class PowerSupplyInputs(Base):
    """
    None
    """
    __tablename__ = 'PowerSupply_inputs'

    PowerSupply_name = Column(Text(), ForeignKey('PowerSupply.name'), primary_key=True)
    inputs = Column(Enum('current', 'voltage', 'phase', 'setpoint', 'on_off_state', 'open_closed_state', 'position', 'rotation', 'power', 'pressure', 'charge', 'absolute_time', 'relative_time', 'shot_number', 'value', 'waveform', 'magnetic_field', name='IOTypeEnum'), primary_key=True)
    

    def __repr__(self):
        return f"PowerSupply_inputs(PowerSupply_name={self.PowerSupply_name},inputs={self.inputs},)"



    


class PowerSupplyOutputs(Base):
    """
    None
    """
    __tablename__ = 'PowerSupply_outputs'

    PowerSupply_name = Column(Text(), ForeignKey('PowerSupply.name'), primary_key=True)
    outputs = Column(Enum('current', 'voltage', 'phase', 'setpoint', 'on_off_state', 'open_closed_state', 'position', 'rotation', 'power', 'pressure', 'charge', 'absolute_time', 'relative_time', 'shot_number', 'value', 'waveform', 'magnetic_field', name='IOTypeEnum'), primary_key=True)
    

    def __repr__(self):
        return f"PowerSupply_outputs(PowerSupply_name={self.PowerSupply_name},outputs={self.outputs},)"



    


class PowerSupplyUpstream(Base):
    """
    None
    """
    __tablename__ = 'PowerSupply_upstream'

    PowerSupply_name = Column(Text(), ForeignKey('PowerSupply.name'), primary_key=True)
    upstream_name = Column(Text(), ForeignKey('AcceleratorElement.name'), primary_key=True)
    

    def __repr__(self):
        return f"PowerSupply_upstream(PowerSupply_name={self.PowerSupply_name},upstream_name={self.upstream_name},)"



    


class PowerSupplyDownstream(Base):
    """
    None
    """
    __tablename__ = 'PowerSupply_downstream'

    PowerSupply_name = Column(Text(), ForeignKey('PowerSupply.name'), primary_key=True)
    downstream_name = Column(Text(), ForeignKey('AcceleratorElement.name'), primary_key=True)
    

    def __repr__(self):
        return f"PowerSupply_downstream(PowerSupply_name={self.PowerSupply_name},downstream_name={self.downstream_name},)"



    


class SectionLatticeElements(Base):
    """
    None
    """
    __tablename__ = 'SectionLattice_elements'

    SectionLattice_name = Column(Text(), ForeignKey('SectionLattice.name'), primary_key=True)
    elements_name = Column(Text(), ForeignKey('AcceleratorElement.name'), primary_key=True)
    

    def __repr__(self):
        return f"SectionLattice_elements(SectionLattice_name={self.SectionLattice_name},elements_name={self.elements_name},)"



    


class MachineLayoutSections(Base):
    """
    None
    """
    __tablename__ = 'MachineLayout_sections'

    MachineLayout_name = Column(Text(), ForeignKey('MachineLayout.name'), primary_key=True)
    sections_name = Column(Text(), ForeignKey('SectionLattice.name'), primary_key=True)
    

    def __repr__(self):
        return f"MachineLayout_sections(MachineLayout_name={self.MachineLayout_name},sections_name={self.sections_name},)"



    


class MachineModelElements(Base):
    """
    None
    """
    __tablename__ = 'MachineModel_elements'

    MachineModel_id = Column(Integer(), ForeignKey('MachineModel.id'), primary_key=True)
    elements_name = Column(Text(), ForeignKey('AcceleratorElement.name'), primary_key=True)
    

    def __repr__(self):
        return f"MachineModel_elements(MachineModel_id={self.MachineModel_id},elements_name={self.elements_name},)"



    


class MachineModelSections(Base):
    """
    None
    """
    __tablename__ = 'MachineModel_sections'

    MachineModel_id = Column(Integer(), ForeignKey('MachineModel.id'), primary_key=True)
    sections_name = Column(Text(), ForeignKey('SectionLattice.name'), primary_key=True)
    

    def __repr__(self):
        return f"MachineModel_sections(MachineModel_id={self.MachineModel_id},sections_name={self.sections_name},)"



    


class MachineModelLayouts(Base):
    """
    None
    """
    __tablename__ = 'MachineModel_layouts'

    MachineModel_id = Column(Integer(), ForeignKey('MachineModel.id'), primary_key=True)
    layouts_name = Column(Text(), ForeignKey('MachineLayout.name'), primary_key=True)
    

    def __repr__(self):
        return f"MachineModel_layouts(MachineModel_id={self.MachineModel_id},layouts_name={self.layouts_name},)"



    


class ACDipoleSimulationElementRamp(Base):
    """
    None
    """
    __tablename__ = 'ACDipoleSimulationElement_ramp'

    ACDipoleSimulationElement_id = Column(Integer(), ForeignKey('ACDipoleSimulationElement.id'), primary_key=True)
    ramp = Column(Integer(), primary_key=True)
    

    def __repr__(self):
        return f"ACDipoleSimulationElement_ramp(ACDipoleSimulationElement_id={self.ACDipoleSimulationElement_id},ramp={self.ramp},)"



    


class RFMultipoleSimulationElementKnl(Base):
    """
    None
    """
    __tablename__ = 'RFMultipoleSimulationElement_knl'

    RFMultipoleSimulationElement_id = Column(Integer(), ForeignKey('RFMultipoleSimulationElement.id'), primary_key=True)
    knl = Column(Float(), primary_key=True)
    

    def __repr__(self):
        return f"RFMultipoleSimulationElement_knl(RFMultipoleSimulationElement_id={self.RFMultipoleSimulationElement_id},knl={self.knl},)"



    


class RFMultipoleSimulationElementKsl(Base):
    """
    None
    """
    __tablename__ = 'RFMultipoleSimulationElement_ksl'

    RFMultipoleSimulationElement_id = Column(Integer(), ForeignKey('RFMultipoleSimulationElement.id'), primary_key=True)
    ksl = Column(Float(), primary_key=True)
    

    def __repr__(self):
        return f"RFMultipoleSimulationElement_ksl(RFMultipoleSimulationElement_id={self.RFMultipoleSimulationElement_id},ksl={self.ksl},)"



    


class RFMultipoleSimulationElementPnl(Base):
    """
    None
    """
    __tablename__ = 'RFMultipoleSimulationElement_pnl'

    RFMultipoleSimulationElement_id = Column(Integer(), ForeignKey('RFMultipoleSimulationElement.id'), primary_key=True)
    pnl = Column(Float(), primary_key=True)
    

    def __repr__(self):
        return f"RFMultipoleSimulationElement_pnl(RFMultipoleSimulationElement_id={self.RFMultipoleSimulationElement_id},pnl={self.pnl},)"



    


class RFMultipoleSimulationElementPsl(Base):
    """
    None
    """
    __tablename__ = 'RFMultipoleSimulationElement_psl'

    RFMultipoleSimulationElement_id = Column(Integer(), ForeignKey('RFMultipoleSimulationElement.id'), primary_key=True)
    psl = Column(Float(), primary_key=True)
    

    def __repr__(self):
        return f"RFMultipoleSimulationElement_psl(RFMultipoleSimulationElement_id={self.RFMultipoleSimulationElement_id},psl={self.psl},)"



    


class MagnetAlias(Base):
    """
    None
    """
    __tablename__ = 'Magnet_alias'

    Magnet_name = Column(Text(), ForeignKey('Magnet.name'), primary_key=True)
    alias = Column(Text(), primary_key=True)
    

    def __repr__(self):
        return f"Magnet_alias(Magnet_name={self.Magnet_name},alias={self.alias},)"



    


class MagnetInputs(Base):
    """
    None
    """
    __tablename__ = 'Magnet_inputs'

    Magnet_name = Column(Text(), ForeignKey('Magnet.name'), primary_key=True)
    inputs = Column(Enum('current', 'voltage', 'phase', 'setpoint', 'on_off_state', 'open_closed_state', 'position', 'rotation', 'power', 'pressure', 'charge', 'absolute_time', 'relative_time', 'shot_number', 'value', 'waveform', 'magnetic_field', name='IOTypeEnum'), primary_key=True)
    

    def __repr__(self):
        return f"Magnet_inputs(Magnet_name={self.Magnet_name},inputs={self.inputs},)"



    


class MagnetOutputs(Base):
    """
    None
    """
    __tablename__ = 'Magnet_outputs'

    Magnet_name = Column(Text(), ForeignKey('Magnet.name'), primary_key=True)
    outputs = Column(Enum('current', 'voltage', 'phase', 'setpoint', 'on_off_state', 'open_closed_state', 'position', 'rotation', 'power', 'pressure', 'charge', 'absolute_time', 'relative_time', 'shot_number', 'value', 'waveform', 'magnetic_field', name='IOTypeEnum'), primary_key=True)
    

    def __repr__(self):
        return f"Magnet_outputs(Magnet_name={self.Magnet_name},outputs={self.outputs},)"



    


class MagnetUpstream(Base):
    """
    None
    """
    __tablename__ = 'Magnet_upstream'

    Magnet_name = Column(Text(), ForeignKey('Magnet.name'), primary_key=True)
    upstream_name = Column(Text(), ForeignKey('AcceleratorElement.name'), primary_key=True)
    

    def __repr__(self):
        return f"Magnet_upstream(Magnet_name={self.Magnet_name},upstream_name={self.upstream_name},)"



    


class MagnetDownstream(Base):
    """
    None
    """
    __tablename__ = 'Magnet_downstream'

    Magnet_name = Column(Text(), ForeignKey('Magnet.name'), primary_key=True)
    downstream_name = Column(Text(), ForeignKey('AcceleratorElement.name'), primary_key=True)
    

    def __repr__(self):
        return f"Magnet_downstream(Magnet_name={self.Magnet_name},downstream_name={self.downstream_name},)"



    


class FieldIntegralCoefficients(Base):
    """
    None
    """
    __tablename__ = 'FieldIntegral_coefficients'

    FieldIntegral_id = Column(Integer(), ForeignKey('FieldIntegral.id'), primary_key=True)
    coefficients = Column(Float(), primary_key=True)
    

    def __repr__(self):
        return f"FieldIntegral_coefficients(FieldIntegral_id={self.FieldIntegral_id},coefficients={self.coefficients},)"



    


class DegaussableElementValues(Base):
    """
    None
    """
    __tablename__ = 'DegaussableElement_values'

    DegaussableElement_id = Column(Integer(), ForeignKey('DegaussableElement.id'), primary_key=True)
    values = Column(Float(), primary_key=True)
    

    def __repr__(self):
        return f"DegaussableElement_values(DegaussableElement_id={self.DegaussableElement_id},values={self.values},)"



    


class RFCavityAlias(Base):
    """
    None
    """
    __tablename__ = 'RFCavity_alias'

    RFCavity_name = Column(Text(), ForeignKey('RFCavity.name'), primary_key=True)
    alias = Column(Text(), primary_key=True)
    

    def __repr__(self):
        return f"RFCavity_alias(RFCavity_name={self.RFCavity_name},alias={self.alias},)"



    


class RFCavityInputs(Base):
    """
    None
    """
    __tablename__ = 'RFCavity_inputs'

    RFCavity_name = Column(Text(), ForeignKey('RFCavity.name'), primary_key=True)
    inputs = Column(Enum('current', 'voltage', 'phase', 'setpoint', 'on_off_state', 'open_closed_state', 'position', 'rotation', 'power', 'pressure', 'charge', 'absolute_time', 'relative_time', 'shot_number', 'value', 'waveform', 'magnetic_field', name='IOTypeEnum'), primary_key=True)
    

    def __repr__(self):
        return f"RFCavity_inputs(RFCavity_name={self.RFCavity_name},inputs={self.inputs},)"



    


class RFCavityOutputs(Base):
    """
    None
    """
    __tablename__ = 'RFCavity_outputs'

    RFCavity_name = Column(Text(), ForeignKey('RFCavity.name'), primary_key=True)
    outputs = Column(Enum('current', 'voltage', 'phase', 'setpoint', 'on_off_state', 'open_closed_state', 'position', 'rotation', 'power', 'pressure', 'charge', 'absolute_time', 'relative_time', 'shot_number', 'value', 'waveform', 'magnetic_field', name='IOTypeEnum'), primary_key=True)
    

    def __repr__(self):
        return f"RFCavity_outputs(RFCavity_name={self.RFCavity_name},outputs={self.outputs},)"



    


class RFCavityUpstream(Base):
    """
    None
    """
    __tablename__ = 'RFCavity_upstream'

    RFCavity_name = Column(Text(), ForeignKey('RFCavity.name'), primary_key=True)
    upstream_name = Column(Text(), ForeignKey('AcceleratorElement.name'), primary_key=True)
    

    def __repr__(self):
        return f"RFCavity_upstream(RFCavity_name={self.RFCavity_name},upstream_name={self.upstream_name},)"



    


class RFCavityDownstream(Base):
    """
    None
    """
    __tablename__ = 'RFCavity_downstream'

    RFCavity_name = Column(Text(), ForeignKey('RFCavity.name'), primary_key=True)
    downstream_name = Column(Text(), ForeignKey('AcceleratorElement.name'), primary_key=True)
    

    def __repr__(self):
        return f"RFCavity_downstream(RFCavity_name={self.RFCavity_name},downstream_name={self.downstream_name},)"



    


class RFDeflectingCavityAlias(Base):
    """
    None
    """
    __tablename__ = 'RFDeflectingCavity_alias'

    RFDeflectingCavity_name = Column(Text(), ForeignKey('RFDeflectingCavity.name'), primary_key=True)
    alias = Column(Text(), primary_key=True)
    

    def __repr__(self):
        return f"RFDeflectingCavity_alias(RFDeflectingCavity_name={self.RFDeflectingCavity_name},alias={self.alias},)"



    


class RFDeflectingCavityInputs(Base):
    """
    None
    """
    __tablename__ = 'RFDeflectingCavity_inputs'

    RFDeflectingCavity_name = Column(Text(), ForeignKey('RFDeflectingCavity.name'), primary_key=True)
    inputs = Column(Enum('current', 'voltage', 'phase', 'setpoint', 'on_off_state', 'open_closed_state', 'position', 'rotation', 'power', 'pressure', 'charge', 'absolute_time', 'relative_time', 'shot_number', 'value', 'waveform', 'magnetic_field', name='IOTypeEnum'), primary_key=True)
    

    def __repr__(self):
        return f"RFDeflectingCavity_inputs(RFDeflectingCavity_name={self.RFDeflectingCavity_name},inputs={self.inputs},)"



    


class RFDeflectingCavityOutputs(Base):
    """
    None
    """
    __tablename__ = 'RFDeflectingCavity_outputs'

    RFDeflectingCavity_name = Column(Text(), ForeignKey('RFDeflectingCavity.name'), primary_key=True)
    outputs = Column(Enum('current', 'voltage', 'phase', 'setpoint', 'on_off_state', 'open_closed_state', 'position', 'rotation', 'power', 'pressure', 'charge', 'absolute_time', 'relative_time', 'shot_number', 'value', 'waveform', 'magnetic_field', name='IOTypeEnum'), primary_key=True)
    

    def __repr__(self):
        return f"RFDeflectingCavity_outputs(RFDeflectingCavity_name={self.RFDeflectingCavity_name},outputs={self.outputs},)"



    


class RFDeflectingCavityUpstream(Base):
    """
    None
    """
    __tablename__ = 'RFDeflectingCavity_upstream'

    RFDeflectingCavity_name = Column(Text(), ForeignKey('RFDeflectingCavity.name'), primary_key=True)
    upstream_name = Column(Text(), ForeignKey('AcceleratorElement.name'), primary_key=True)
    

    def __repr__(self):
        return f"RFDeflectingCavity_upstream(RFDeflectingCavity_name={self.RFDeflectingCavity_name},upstream_name={self.upstream_name},)"



    


class RFDeflectingCavityDownstream(Base):
    """
    None
    """
    __tablename__ = 'RFDeflectingCavity_downstream'

    RFDeflectingCavity_name = Column(Text(), ForeignKey('RFDeflectingCavity.name'), primary_key=True)
    downstream_name = Column(Text(), ForeignKey('AcceleratorElement.name'), primary_key=True)
    

    def __repr__(self):
        return f"RFDeflectingCavity_downstream(RFDeflectingCavity_name={self.RFDeflectingCavity_name},downstream_name={self.downstream_name},)"



    


class CrabCavityAlias(Base):
    """
    None
    """
    __tablename__ = 'CrabCavity_alias'

    CrabCavity_name = Column(Text(), ForeignKey('CrabCavity.name'), primary_key=True)
    alias = Column(Text(), primary_key=True)
    

    def __repr__(self):
        return f"CrabCavity_alias(CrabCavity_name={self.CrabCavity_name},alias={self.alias},)"



    


class CrabCavityInputs(Base):
    """
    None
    """
    __tablename__ = 'CrabCavity_inputs'

    CrabCavity_name = Column(Text(), ForeignKey('CrabCavity.name'), primary_key=True)
    inputs = Column(Enum('current', 'voltage', 'phase', 'setpoint', 'on_off_state', 'open_closed_state', 'position', 'rotation', 'power', 'pressure', 'charge', 'absolute_time', 'relative_time', 'shot_number', 'value', 'waveform', 'magnetic_field', name='IOTypeEnum'), primary_key=True)
    

    def __repr__(self):
        return f"CrabCavity_inputs(CrabCavity_name={self.CrabCavity_name},inputs={self.inputs},)"



    


class CrabCavityOutputs(Base):
    """
    None
    """
    __tablename__ = 'CrabCavity_outputs'

    CrabCavity_name = Column(Text(), ForeignKey('CrabCavity.name'), primary_key=True)
    outputs = Column(Enum('current', 'voltage', 'phase', 'setpoint', 'on_off_state', 'open_closed_state', 'position', 'rotation', 'power', 'pressure', 'charge', 'absolute_time', 'relative_time', 'shot_number', 'value', 'waveform', 'magnetic_field', name='IOTypeEnum'), primary_key=True)
    

    def __repr__(self):
        return f"CrabCavity_outputs(CrabCavity_name={self.CrabCavity_name},outputs={self.outputs},)"



    


class CrabCavityUpstream(Base):
    """
    None
    """
    __tablename__ = 'CrabCavity_upstream'

    CrabCavity_name = Column(Text(), ForeignKey('CrabCavity.name'), primary_key=True)
    upstream_name = Column(Text(), ForeignKey('AcceleratorElement.name'), primary_key=True)
    

    def __repr__(self):
        return f"CrabCavity_upstream(CrabCavity_name={self.CrabCavity_name},upstream_name={self.upstream_name},)"



    


class CrabCavityDownstream(Base):
    """
    None
    """
    __tablename__ = 'CrabCavity_downstream'

    CrabCavity_name = Column(Text(), ForeignKey('CrabCavity.name'), primary_key=True)
    downstream_name = Column(Text(), ForeignKey('AcceleratorElement.name'), primary_key=True)
    

    def __repr__(self):
        return f"CrabCavity_downstream(CrabCavity_name={self.CrabCavity_name},downstream_name={self.downstream_name},)"



    


class WakefieldAlias(Base):
    """
    None
    """
    __tablename__ = 'Wakefield_alias'

    Wakefield_name = Column(Text(), ForeignKey('Wakefield.name'), primary_key=True)
    alias = Column(Text(), primary_key=True)
    

    def __repr__(self):
        return f"Wakefield_alias(Wakefield_name={self.Wakefield_name},alias={self.alias},)"



    


class WakefieldInputs(Base):
    """
    None
    """
    __tablename__ = 'Wakefield_inputs'

    Wakefield_name = Column(Text(), ForeignKey('Wakefield.name'), primary_key=True)
    inputs = Column(Enum('current', 'voltage', 'phase', 'setpoint', 'on_off_state', 'open_closed_state', 'position', 'rotation', 'power', 'pressure', 'charge', 'absolute_time', 'relative_time', 'shot_number', 'value', 'waveform', 'magnetic_field', name='IOTypeEnum'), primary_key=True)
    

    def __repr__(self):
        return f"Wakefield_inputs(Wakefield_name={self.Wakefield_name},inputs={self.inputs},)"



    


class WakefieldOutputs(Base):
    """
    None
    """
    __tablename__ = 'Wakefield_outputs'

    Wakefield_name = Column(Text(), ForeignKey('Wakefield.name'), primary_key=True)
    outputs = Column(Enum('current', 'voltage', 'phase', 'setpoint', 'on_off_state', 'open_closed_state', 'position', 'rotation', 'power', 'pressure', 'charge', 'absolute_time', 'relative_time', 'shot_number', 'value', 'waveform', 'magnetic_field', name='IOTypeEnum'), primary_key=True)
    

    def __repr__(self):
        return f"Wakefield_outputs(Wakefield_name={self.Wakefield_name},outputs={self.outputs},)"



    


class WakefieldUpstream(Base):
    """
    None
    """
    __tablename__ = 'Wakefield_upstream'

    Wakefield_name = Column(Text(), ForeignKey('Wakefield.name'), primary_key=True)
    upstream_name = Column(Text(), ForeignKey('AcceleratorElement.name'), primary_key=True)
    

    def __repr__(self):
        return f"Wakefield_upstream(Wakefield_name={self.Wakefield_name},upstream_name={self.upstream_name},)"



    


class WakefieldDownstream(Base):
    """
    None
    """
    __tablename__ = 'Wakefield_downstream'

    Wakefield_name = Column(Text(), ForeignKey('Wakefield.name'), primary_key=True)
    downstream_name = Column(Text(), ForeignKey('AcceleratorElement.name'), primary_key=True)
    

    def __repr__(self):
        return f"Wakefield_downstream(Wakefield_name={self.Wakefield_name},downstream_name={self.downstream_name},)"



    


class LowLevelRFAlias(Base):
    """
    None
    """
    __tablename__ = 'LowLevelRF_alias'

    LowLevelRF_name = Column(Text(), ForeignKey('LowLevelRF.name'), primary_key=True)
    alias = Column(Text(), primary_key=True)
    

    def __repr__(self):
        return f"LowLevelRF_alias(LowLevelRF_name={self.LowLevelRF_name},alias={self.alias},)"



    


class LowLevelRFInputs(Base):
    """
    None
    """
    __tablename__ = 'LowLevelRF_inputs'

    LowLevelRF_name = Column(Text(), ForeignKey('LowLevelRF.name'), primary_key=True)
    inputs = Column(Enum('current', 'voltage', 'phase', 'setpoint', 'on_off_state', 'open_closed_state', 'position', 'rotation', 'power', 'pressure', 'charge', 'absolute_time', 'relative_time', 'shot_number', 'value', 'waveform', 'magnetic_field', name='IOTypeEnum'), primary_key=True)
    

    def __repr__(self):
        return f"LowLevelRF_inputs(LowLevelRF_name={self.LowLevelRF_name},inputs={self.inputs},)"



    


class LowLevelRFOutputs(Base):
    """
    None
    """
    __tablename__ = 'LowLevelRF_outputs'

    LowLevelRF_name = Column(Text(), ForeignKey('LowLevelRF.name'), primary_key=True)
    outputs = Column(Enum('current', 'voltage', 'phase', 'setpoint', 'on_off_state', 'open_closed_state', 'position', 'rotation', 'power', 'pressure', 'charge', 'absolute_time', 'relative_time', 'shot_number', 'value', 'waveform', 'magnetic_field', name='IOTypeEnum'), primary_key=True)
    

    def __repr__(self):
        return f"LowLevelRF_outputs(LowLevelRF_name={self.LowLevelRF_name},outputs={self.outputs},)"



    


class LowLevelRFUpstream(Base):
    """
    None
    """
    __tablename__ = 'LowLevelRF_upstream'

    LowLevelRF_name = Column(Text(), ForeignKey('LowLevelRF.name'), primary_key=True)
    upstream_name = Column(Text(), ForeignKey('AcceleratorElement.name'), primary_key=True)
    

    def __repr__(self):
        return f"LowLevelRF_upstream(LowLevelRF_name={self.LowLevelRF_name},upstream_name={self.upstream_name},)"



    


class LowLevelRFDownstream(Base):
    """
    None
    """
    __tablename__ = 'LowLevelRF_downstream'

    LowLevelRF_name = Column(Text(), ForeignKey('LowLevelRF.name'), primary_key=True)
    downstream_name = Column(Text(), ForeignKey('AcceleratorElement.name'), primary_key=True)
    

    def __repr__(self):
        return f"LowLevelRF_downstream(LowLevelRF_name={self.LowLevelRF_name},downstream_name={self.downstream_name},)"



    


class RFModulatorAlias(Base):
    """
    None
    """
    __tablename__ = 'RFModulator_alias'

    RFModulator_name = Column(Text(), ForeignKey('RFModulator.name'), primary_key=True)
    alias = Column(Text(), primary_key=True)
    

    def __repr__(self):
        return f"RFModulator_alias(RFModulator_name={self.RFModulator_name},alias={self.alias},)"



    


class RFModulatorInputs(Base):
    """
    None
    """
    __tablename__ = 'RFModulator_inputs'

    RFModulator_name = Column(Text(), ForeignKey('RFModulator.name'), primary_key=True)
    inputs = Column(Enum('current', 'voltage', 'phase', 'setpoint', 'on_off_state', 'open_closed_state', 'position', 'rotation', 'power', 'pressure', 'charge', 'absolute_time', 'relative_time', 'shot_number', 'value', 'waveform', 'magnetic_field', name='IOTypeEnum'), primary_key=True)
    

    def __repr__(self):
        return f"RFModulator_inputs(RFModulator_name={self.RFModulator_name},inputs={self.inputs},)"



    


class RFModulatorOutputs(Base):
    """
    None
    """
    __tablename__ = 'RFModulator_outputs'

    RFModulator_name = Column(Text(), ForeignKey('RFModulator.name'), primary_key=True)
    outputs = Column(Enum('current', 'voltage', 'phase', 'setpoint', 'on_off_state', 'open_closed_state', 'position', 'rotation', 'power', 'pressure', 'charge', 'absolute_time', 'relative_time', 'shot_number', 'value', 'waveform', 'magnetic_field', name='IOTypeEnum'), primary_key=True)
    

    def __repr__(self):
        return f"RFModulator_outputs(RFModulator_name={self.RFModulator_name},outputs={self.outputs},)"



    


class RFModulatorUpstream(Base):
    """
    None
    """
    __tablename__ = 'RFModulator_upstream'

    RFModulator_name = Column(Text(), ForeignKey('RFModulator.name'), primary_key=True)
    upstream_name = Column(Text(), ForeignKey('AcceleratorElement.name'), primary_key=True)
    

    def __repr__(self):
        return f"RFModulator_upstream(RFModulator_name={self.RFModulator_name},upstream_name={self.upstream_name},)"



    


class RFModulatorDownstream(Base):
    """
    None
    """
    __tablename__ = 'RFModulator_downstream'

    RFModulator_name = Column(Text(), ForeignKey('RFModulator.name'), primary_key=True)
    downstream_name = Column(Text(), ForeignKey('AcceleratorElement.name'), primary_key=True)
    

    def __repr__(self):
        return f"RFModulator_downstream(RFModulator_name={self.RFModulator_name},downstream_name={self.downstream_name},)"



    


class RFProtectionAlias(Base):
    """
    None
    """
    __tablename__ = 'RFProtection_alias'

    RFProtection_name = Column(Text(), ForeignKey('RFProtection.name'), primary_key=True)
    alias = Column(Text(), primary_key=True)
    

    def __repr__(self):
        return f"RFProtection_alias(RFProtection_name={self.RFProtection_name},alias={self.alias},)"



    


class RFProtectionInputs(Base):
    """
    None
    """
    __tablename__ = 'RFProtection_inputs'

    RFProtection_name = Column(Text(), ForeignKey('RFProtection.name'), primary_key=True)
    inputs = Column(Enum('current', 'voltage', 'phase', 'setpoint', 'on_off_state', 'open_closed_state', 'position', 'rotation', 'power', 'pressure', 'charge', 'absolute_time', 'relative_time', 'shot_number', 'value', 'waveform', 'magnetic_field', name='IOTypeEnum'), primary_key=True)
    

    def __repr__(self):
        return f"RFProtection_inputs(RFProtection_name={self.RFProtection_name},inputs={self.inputs},)"



    


class RFProtectionOutputs(Base):
    """
    None
    """
    __tablename__ = 'RFProtection_outputs'

    RFProtection_name = Column(Text(), ForeignKey('RFProtection.name'), primary_key=True)
    outputs = Column(Enum('current', 'voltage', 'phase', 'setpoint', 'on_off_state', 'open_closed_state', 'position', 'rotation', 'power', 'pressure', 'charge', 'absolute_time', 'relative_time', 'shot_number', 'value', 'waveform', 'magnetic_field', name='IOTypeEnum'), primary_key=True)
    

    def __repr__(self):
        return f"RFProtection_outputs(RFProtection_name={self.RFProtection_name},outputs={self.outputs},)"



    


class RFProtectionUpstream(Base):
    """
    None
    """
    __tablename__ = 'RFProtection_upstream'

    RFProtection_name = Column(Text(), ForeignKey('RFProtection.name'), primary_key=True)
    upstream_name = Column(Text(), ForeignKey('AcceleratorElement.name'), primary_key=True)
    

    def __repr__(self):
        return f"RFProtection_upstream(RFProtection_name={self.RFProtection_name},upstream_name={self.upstream_name},)"



    


class RFProtectionDownstream(Base):
    """
    None
    """
    __tablename__ = 'RFProtection_downstream'

    RFProtection_name = Column(Text(), ForeignKey('RFProtection.name'), primary_key=True)
    downstream_name = Column(Text(), ForeignKey('AcceleratorElement.name'), primary_key=True)
    

    def __repr__(self):
        return f"RFProtection_downstream(RFProtection_name={self.RFProtection_name},downstream_name={self.downstream_name},)"



    


class RFHeartbeatAlias(Base):
    """
    None
    """
    __tablename__ = 'RFHeartbeat_alias'

    RFHeartbeat_name = Column(Text(), ForeignKey('RFHeartbeat.name'), primary_key=True)
    alias = Column(Text(), primary_key=True)
    

    def __repr__(self):
        return f"RFHeartbeat_alias(RFHeartbeat_name={self.RFHeartbeat_name},alias={self.alias},)"



    


class RFHeartbeatInputs(Base):
    """
    None
    """
    __tablename__ = 'RFHeartbeat_inputs'

    RFHeartbeat_name = Column(Text(), ForeignKey('RFHeartbeat.name'), primary_key=True)
    inputs = Column(Enum('current', 'voltage', 'phase', 'setpoint', 'on_off_state', 'open_closed_state', 'position', 'rotation', 'power', 'pressure', 'charge', 'absolute_time', 'relative_time', 'shot_number', 'value', 'waveform', 'magnetic_field', name='IOTypeEnum'), primary_key=True)
    

    def __repr__(self):
        return f"RFHeartbeat_inputs(RFHeartbeat_name={self.RFHeartbeat_name},inputs={self.inputs},)"



    


class RFHeartbeatOutputs(Base):
    """
    None
    """
    __tablename__ = 'RFHeartbeat_outputs'

    RFHeartbeat_name = Column(Text(), ForeignKey('RFHeartbeat.name'), primary_key=True)
    outputs = Column(Enum('current', 'voltage', 'phase', 'setpoint', 'on_off_state', 'open_closed_state', 'position', 'rotation', 'power', 'pressure', 'charge', 'absolute_time', 'relative_time', 'shot_number', 'value', 'waveform', 'magnetic_field', name='IOTypeEnum'), primary_key=True)
    

    def __repr__(self):
        return f"RFHeartbeat_outputs(RFHeartbeat_name={self.RFHeartbeat_name},outputs={self.outputs},)"



    


class RFHeartbeatUpstream(Base):
    """
    None
    """
    __tablename__ = 'RFHeartbeat_upstream'

    RFHeartbeat_name = Column(Text(), ForeignKey('RFHeartbeat.name'), primary_key=True)
    upstream_name = Column(Text(), ForeignKey('AcceleratorElement.name'), primary_key=True)
    

    def __repr__(self):
        return f"RFHeartbeat_upstream(RFHeartbeat_name={self.RFHeartbeat_name},upstream_name={self.upstream_name},)"



    


class RFHeartbeatDownstream(Base):
    """
    None
    """
    __tablename__ = 'RFHeartbeat_downstream'

    RFHeartbeat_name = Column(Text(), ForeignKey('RFHeartbeat.name'), primary_key=True)
    downstream_name = Column(Text(), ForeignKey('AcceleratorElement.name'), primary_key=True)
    

    def __repr__(self):
        return f"RFHeartbeat_downstream(RFHeartbeat_name={self.RFHeartbeat_name},downstream_name={self.downstream_name},)"



    


class PIDAlias(Base):
    """
    None
    """
    __tablename__ = 'PID_alias'

    PID_name = Column(Text(), ForeignKey('PID.name'), primary_key=True)
    alias = Column(Text(), primary_key=True)
    

    def __repr__(self):
        return f"PID_alias(PID_name={self.PID_name},alias={self.alias},)"



    


class PIDInputs(Base):
    """
    None
    """
    __tablename__ = 'PID_inputs'

    PID_name = Column(Text(), ForeignKey('PID.name'), primary_key=True)
    inputs = Column(Enum('current', 'voltage', 'phase', 'setpoint', 'on_off_state', 'open_closed_state', 'position', 'rotation', 'power', 'pressure', 'charge', 'absolute_time', 'relative_time', 'shot_number', 'value', 'waveform', 'magnetic_field', name='IOTypeEnum'), primary_key=True)
    

    def __repr__(self):
        return f"PID_inputs(PID_name={self.PID_name},inputs={self.inputs},)"



    


class PIDOutputs(Base):
    """
    None
    """
    __tablename__ = 'PID_outputs'

    PID_name = Column(Text(), ForeignKey('PID.name'), primary_key=True)
    outputs = Column(Enum('current', 'voltage', 'phase', 'setpoint', 'on_off_state', 'open_closed_state', 'position', 'rotation', 'power', 'pressure', 'charge', 'absolute_time', 'relative_time', 'shot_number', 'value', 'waveform', 'magnetic_field', name='IOTypeEnum'), primary_key=True)
    

    def __repr__(self):
        return f"PID_outputs(PID_name={self.PID_name},outputs={self.outputs},)"



    


class PIDUpstream(Base):
    """
    None
    """
    __tablename__ = 'PID_upstream'

    PID_name = Column(Text(), ForeignKey('PID.name'), primary_key=True)
    upstream_name = Column(Text(), ForeignKey('AcceleratorElement.name'), primary_key=True)
    

    def __repr__(self):
        return f"PID_upstream(PID_name={self.PID_name},upstream_name={self.upstream_name},)"



    


class PIDDownstream(Base):
    """
    None
    """
    __tablename__ = 'PID_downstream'

    PID_name = Column(Text(), ForeignKey('PID.name'), primary_key=True)
    downstream_name = Column(Text(), ForeignKey('AcceleratorElement.name'), primary_key=True)
    

    def __repr__(self):
        return f"PID_downstream(PID_name={self.PID_name},downstream_name={self.downstream_name},)"



    


class RFCavityElementPowerCalibration(Base):
    """
    None
    """
    __tablename__ = 'RFCavityElement_power_calibration'

    RFCavityElement_id = Column(Integer(), ForeignKey('RFCavityElement.id'), primary_key=True)
    power_calibration = Column(Float(), primary_key=True)
    

    def __repr__(self):
        return f"RFCavityElement_power_calibration(RFCavityElement_id={self.RFCavityElement_id},power_calibration={self.power_calibration},)"



    


class RFCavityElementGradientCalibration(Base):
    """
    None
    """
    __tablename__ = 'RFCavityElement_gradient_calibration'

    RFCavityElement_id = Column(Integer(), ForeignKey('RFCavityElement.id'), primary_key=True)
    gradient_calibration = Column(Float(), primary_key=True)
    

    def __repr__(self):
        return f"RFCavityElement_gradient_calibration(RFCavityElement_id={self.RFCavityElement_id},gradient_calibration={self.gradient_calibration},)"



    


class DiagnosticAlias(Base):
    """
    None
    """
    __tablename__ = 'Diagnostic_alias'

    Diagnostic_name = Column(Text(), ForeignKey('Diagnostic.name'), primary_key=True)
    alias = Column(Text(), primary_key=True)
    

    def __repr__(self):
        return f"Diagnostic_alias(Diagnostic_name={self.Diagnostic_name},alias={self.alias},)"



    


class DiagnosticInputs(Base):
    """
    None
    """
    __tablename__ = 'Diagnostic_inputs'

    Diagnostic_name = Column(Text(), ForeignKey('Diagnostic.name'), primary_key=True)
    inputs = Column(Enum('current', 'voltage', 'phase', 'setpoint', 'on_off_state', 'open_closed_state', 'position', 'rotation', 'power', 'pressure', 'charge', 'absolute_time', 'relative_time', 'shot_number', 'value', 'waveform', 'magnetic_field', name='IOTypeEnum'), primary_key=True)
    

    def __repr__(self):
        return f"Diagnostic_inputs(Diagnostic_name={self.Diagnostic_name},inputs={self.inputs},)"



    


class DiagnosticOutputs(Base):
    """
    None
    """
    __tablename__ = 'Diagnostic_outputs'

    Diagnostic_name = Column(Text(), ForeignKey('Diagnostic.name'), primary_key=True)
    outputs = Column(Enum('current', 'voltage', 'phase', 'setpoint', 'on_off_state', 'open_closed_state', 'position', 'rotation', 'power', 'pressure', 'charge', 'absolute_time', 'relative_time', 'shot_number', 'value', 'waveform', 'magnetic_field', name='IOTypeEnum'), primary_key=True)
    

    def __repr__(self):
        return f"Diagnostic_outputs(Diagnostic_name={self.Diagnostic_name},outputs={self.outputs},)"



    


class DiagnosticUpstream(Base):
    """
    None
    """
    __tablename__ = 'Diagnostic_upstream'

    Diagnostic_name = Column(Text(), ForeignKey('Diagnostic.name'), primary_key=True)
    upstream_name = Column(Text(), ForeignKey('AcceleratorElement.name'), primary_key=True)
    

    def __repr__(self):
        return f"Diagnostic_upstream(Diagnostic_name={self.Diagnostic_name},upstream_name={self.upstream_name},)"



    


class DiagnosticDownstream(Base):
    """
    None
    """
    __tablename__ = 'Diagnostic_downstream'

    Diagnostic_name = Column(Text(), ForeignKey('Diagnostic.name'), primary_key=True)
    downstream_name = Column(Text(), ForeignKey('AcceleratorElement.name'), primary_key=True)
    

    def __repr__(self):
        return f"Diagnostic_downstream(Diagnostic_name={self.Diagnostic_name},downstream_name={self.downstream_name},)"



    


class BeamPositionMonitorAlias(Base):
    """
    None
    """
    __tablename__ = 'BeamPositionMonitor_alias'

    BeamPositionMonitor_name = Column(Text(), ForeignKey('BeamPositionMonitor.name'), primary_key=True)
    alias = Column(Text(), primary_key=True)
    

    def __repr__(self):
        return f"BeamPositionMonitor_alias(BeamPositionMonitor_name={self.BeamPositionMonitor_name},alias={self.alias},)"



    


class BeamPositionMonitorInputs(Base):
    """
    None
    """
    __tablename__ = 'BeamPositionMonitor_inputs'

    BeamPositionMonitor_name = Column(Text(), ForeignKey('BeamPositionMonitor.name'), primary_key=True)
    inputs = Column(Enum('current', 'voltage', 'phase', 'setpoint', 'on_off_state', 'open_closed_state', 'position', 'rotation', 'power', 'pressure', 'charge', 'absolute_time', 'relative_time', 'shot_number', 'value', 'waveform', 'magnetic_field', name='IOTypeEnum'), primary_key=True)
    

    def __repr__(self):
        return f"BeamPositionMonitor_inputs(BeamPositionMonitor_name={self.BeamPositionMonitor_name},inputs={self.inputs},)"



    


class BeamPositionMonitorOutputs(Base):
    """
    None
    """
    __tablename__ = 'BeamPositionMonitor_outputs'

    BeamPositionMonitor_name = Column(Text(), ForeignKey('BeamPositionMonitor.name'), primary_key=True)
    outputs = Column(Enum('current', 'voltage', 'phase', 'setpoint', 'on_off_state', 'open_closed_state', 'position', 'rotation', 'power', 'pressure', 'charge', 'absolute_time', 'relative_time', 'shot_number', 'value', 'waveform', 'magnetic_field', name='IOTypeEnum'), primary_key=True)
    

    def __repr__(self):
        return f"BeamPositionMonitor_outputs(BeamPositionMonitor_name={self.BeamPositionMonitor_name},outputs={self.outputs},)"



    


class BeamPositionMonitorUpstream(Base):
    """
    None
    """
    __tablename__ = 'BeamPositionMonitor_upstream'

    BeamPositionMonitor_name = Column(Text(), ForeignKey('BeamPositionMonitor.name'), primary_key=True)
    upstream_name = Column(Text(), ForeignKey('AcceleratorElement.name'), primary_key=True)
    

    def __repr__(self):
        return f"BeamPositionMonitor_upstream(BeamPositionMonitor_name={self.BeamPositionMonitor_name},upstream_name={self.upstream_name},)"



    


class BeamPositionMonitorDownstream(Base):
    """
    None
    """
    __tablename__ = 'BeamPositionMonitor_downstream'

    BeamPositionMonitor_name = Column(Text(), ForeignKey('BeamPositionMonitor.name'), primary_key=True)
    downstream_name = Column(Text(), ForeignKey('AcceleratorElement.name'), primary_key=True)
    

    def __repr__(self):
        return f"BeamPositionMonitor_downstream(BeamPositionMonitor_name={self.BeamPositionMonitor_name},downstream_name={self.downstream_name},)"



    


class BeamArrivalMonitorAlias(Base):
    """
    None
    """
    __tablename__ = 'BeamArrivalMonitor_alias'

    BeamArrivalMonitor_name = Column(Text(), ForeignKey('BeamArrivalMonitor.name'), primary_key=True)
    alias = Column(Text(), primary_key=True)
    

    def __repr__(self):
        return f"BeamArrivalMonitor_alias(BeamArrivalMonitor_name={self.BeamArrivalMonitor_name},alias={self.alias},)"



    


class BeamArrivalMonitorInputs(Base):
    """
    None
    """
    __tablename__ = 'BeamArrivalMonitor_inputs'

    BeamArrivalMonitor_name = Column(Text(), ForeignKey('BeamArrivalMonitor.name'), primary_key=True)
    inputs = Column(Enum('current', 'voltage', 'phase', 'setpoint', 'on_off_state', 'open_closed_state', 'position', 'rotation', 'power', 'pressure', 'charge', 'absolute_time', 'relative_time', 'shot_number', 'value', 'waveform', 'magnetic_field', name='IOTypeEnum'), primary_key=True)
    

    def __repr__(self):
        return f"BeamArrivalMonitor_inputs(BeamArrivalMonitor_name={self.BeamArrivalMonitor_name},inputs={self.inputs},)"



    


class BeamArrivalMonitorOutputs(Base):
    """
    None
    """
    __tablename__ = 'BeamArrivalMonitor_outputs'

    BeamArrivalMonitor_name = Column(Text(), ForeignKey('BeamArrivalMonitor.name'), primary_key=True)
    outputs = Column(Enum('current', 'voltage', 'phase', 'setpoint', 'on_off_state', 'open_closed_state', 'position', 'rotation', 'power', 'pressure', 'charge', 'absolute_time', 'relative_time', 'shot_number', 'value', 'waveform', 'magnetic_field', name='IOTypeEnum'), primary_key=True)
    

    def __repr__(self):
        return f"BeamArrivalMonitor_outputs(BeamArrivalMonitor_name={self.BeamArrivalMonitor_name},outputs={self.outputs},)"



    


class BeamArrivalMonitorUpstream(Base):
    """
    None
    """
    __tablename__ = 'BeamArrivalMonitor_upstream'

    BeamArrivalMonitor_name = Column(Text(), ForeignKey('BeamArrivalMonitor.name'), primary_key=True)
    upstream_name = Column(Text(), ForeignKey('AcceleratorElement.name'), primary_key=True)
    

    def __repr__(self):
        return f"BeamArrivalMonitor_upstream(BeamArrivalMonitor_name={self.BeamArrivalMonitor_name},upstream_name={self.upstream_name},)"



    


class BeamArrivalMonitorDownstream(Base):
    """
    None
    """
    __tablename__ = 'BeamArrivalMonitor_downstream'

    BeamArrivalMonitor_name = Column(Text(), ForeignKey('BeamArrivalMonitor.name'), primary_key=True)
    downstream_name = Column(Text(), ForeignKey('AcceleratorElement.name'), primary_key=True)
    

    def __repr__(self):
        return f"BeamArrivalMonitor_downstream(BeamArrivalMonitor_name={self.BeamArrivalMonitor_name},downstream_name={self.downstream_name},)"



    


class BunchLengthMonitorAlias(Base):
    """
    None
    """
    __tablename__ = 'BunchLengthMonitor_alias'

    BunchLengthMonitor_name = Column(Text(), ForeignKey('BunchLengthMonitor.name'), primary_key=True)
    alias = Column(Text(), primary_key=True)
    

    def __repr__(self):
        return f"BunchLengthMonitor_alias(BunchLengthMonitor_name={self.BunchLengthMonitor_name},alias={self.alias},)"



    


class BunchLengthMonitorInputs(Base):
    """
    None
    """
    __tablename__ = 'BunchLengthMonitor_inputs'

    BunchLengthMonitor_name = Column(Text(), ForeignKey('BunchLengthMonitor.name'), primary_key=True)
    inputs = Column(Enum('current', 'voltage', 'phase', 'setpoint', 'on_off_state', 'open_closed_state', 'position', 'rotation', 'power', 'pressure', 'charge', 'absolute_time', 'relative_time', 'shot_number', 'value', 'waveform', 'magnetic_field', name='IOTypeEnum'), primary_key=True)
    

    def __repr__(self):
        return f"BunchLengthMonitor_inputs(BunchLengthMonitor_name={self.BunchLengthMonitor_name},inputs={self.inputs},)"



    


class BunchLengthMonitorOutputs(Base):
    """
    None
    """
    __tablename__ = 'BunchLengthMonitor_outputs'

    BunchLengthMonitor_name = Column(Text(), ForeignKey('BunchLengthMonitor.name'), primary_key=True)
    outputs = Column(Enum('current', 'voltage', 'phase', 'setpoint', 'on_off_state', 'open_closed_state', 'position', 'rotation', 'power', 'pressure', 'charge', 'absolute_time', 'relative_time', 'shot_number', 'value', 'waveform', 'magnetic_field', name='IOTypeEnum'), primary_key=True)
    

    def __repr__(self):
        return f"BunchLengthMonitor_outputs(BunchLengthMonitor_name={self.BunchLengthMonitor_name},outputs={self.outputs},)"



    


class BunchLengthMonitorUpstream(Base):
    """
    None
    """
    __tablename__ = 'BunchLengthMonitor_upstream'

    BunchLengthMonitor_name = Column(Text(), ForeignKey('BunchLengthMonitor.name'), primary_key=True)
    upstream_name = Column(Text(), ForeignKey('AcceleratorElement.name'), primary_key=True)
    

    def __repr__(self):
        return f"BunchLengthMonitor_upstream(BunchLengthMonitor_name={self.BunchLengthMonitor_name},upstream_name={self.upstream_name},)"



    


class BunchLengthMonitorDownstream(Base):
    """
    None
    """
    __tablename__ = 'BunchLengthMonitor_downstream'

    BunchLengthMonitor_name = Column(Text(), ForeignKey('BunchLengthMonitor.name'), primary_key=True)
    downstream_name = Column(Text(), ForeignKey('AcceleratorElement.name'), primary_key=True)
    

    def __repr__(self):
        return f"BunchLengthMonitor_downstream(BunchLengthMonitor_name={self.BunchLengthMonitor_name},downstream_name={self.downstream_name},)"



    


class CameraAlias(Base):
    """
    None
    """
    __tablename__ = 'Camera_alias'

    Camera_name = Column(Text(), ForeignKey('Camera.name'), primary_key=True)
    alias = Column(Text(), primary_key=True)
    

    def __repr__(self):
        return f"Camera_alias(Camera_name={self.Camera_name},alias={self.alias},)"



    


class CameraInputs(Base):
    """
    None
    """
    __tablename__ = 'Camera_inputs'

    Camera_name = Column(Text(), ForeignKey('Camera.name'), primary_key=True)
    inputs = Column(Enum('current', 'voltage', 'phase', 'setpoint', 'on_off_state', 'open_closed_state', 'position', 'rotation', 'power', 'pressure', 'charge', 'absolute_time', 'relative_time', 'shot_number', 'value', 'waveform', 'magnetic_field', name='IOTypeEnum'), primary_key=True)
    

    def __repr__(self):
        return f"Camera_inputs(Camera_name={self.Camera_name},inputs={self.inputs},)"



    


class CameraOutputs(Base):
    """
    None
    """
    __tablename__ = 'Camera_outputs'

    Camera_name = Column(Text(), ForeignKey('Camera.name'), primary_key=True)
    outputs = Column(Enum('current', 'voltage', 'phase', 'setpoint', 'on_off_state', 'open_closed_state', 'position', 'rotation', 'power', 'pressure', 'charge', 'absolute_time', 'relative_time', 'shot_number', 'value', 'waveform', 'magnetic_field', name='IOTypeEnum'), primary_key=True)
    

    def __repr__(self):
        return f"Camera_outputs(Camera_name={self.Camera_name},outputs={self.outputs},)"



    


class CameraUpstream(Base):
    """
    None
    """
    __tablename__ = 'Camera_upstream'

    Camera_name = Column(Text(), ForeignKey('Camera.name'), primary_key=True)
    upstream_name = Column(Text(), ForeignKey('AcceleratorElement.name'), primary_key=True)
    

    def __repr__(self):
        return f"Camera_upstream(Camera_name={self.Camera_name},upstream_name={self.upstream_name},)"



    


class CameraDownstream(Base):
    """
    None
    """
    __tablename__ = 'Camera_downstream'

    Camera_name = Column(Text(), ForeignKey('Camera.name'), primary_key=True)
    downstream_name = Column(Text(), ForeignKey('AcceleratorElement.name'), primary_key=True)
    

    def __repr__(self):
        return f"Camera_downstream(Camera_name={self.Camera_name},downstream_name={self.downstream_name},)"



    


class ScreenAlias(Base):
    """
    None
    """
    __tablename__ = 'Screen_alias'

    Screen_name = Column(Text(), ForeignKey('Screen.name'), primary_key=True)
    alias = Column(Text(), primary_key=True)
    

    def __repr__(self):
        return f"Screen_alias(Screen_name={self.Screen_name},alias={self.alias},)"



    


class ScreenInputs(Base):
    """
    None
    """
    __tablename__ = 'Screen_inputs'

    Screen_name = Column(Text(), ForeignKey('Screen.name'), primary_key=True)
    inputs = Column(Enum('current', 'voltage', 'phase', 'setpoint', 'on_off_state', 'open_closed_state', 'position', 'rotation', 'power', 'pressure', 'charge', 'absolute_time', 'relative_time', 'shot_number', 'value', 'waveform', 'magnetic_field', name='IOTypeEnum'), primary_key=True)
    

    def __repr__(self):
        return f"Screen_inputs(Screen_name={self.Screen_name},inputs={self.inputs},)"



    


class ScreenOutputs(Base):
    """
    None
    """
    __tablename__ = 'Screen_outputs'

    Screen_name = Column(Text(), ForeignKey('Screen.name'), primary_key=True)
    outputs = Column(Enum('current', 'voltage', 'phase', 'setpoint', 'on_off_state', 'open_closed_state', 'position', 'rotation', 'power', 'pressure', 'charge', 'absolute_time', 'relative_time', 'shot_number', 'value', 'waveform', 'magnetic_field', name='IOTypeEnum'), primary_key=True)
    

    def __repr__(self):
        return f"Screen_outputs(Screen_name={self.Screen_name},outputs={self.outputs},)"



    


class ScreenUpstream(Base):
    """
    None
    """
    __tablename__ = 'Screen_upstream'

    Screen_name = Column(Text(), ForeignKey('Screen.name'), primary_key=True)
    upstream_name = Column(Text(), ForeignKey('AcceleratorElement.name'), primary_key=True)
    

    def __repr__(self):
        return f"Screen_upstream(Screen_name={self.Screen_name},upstream_name={self.upstream_name},)"



    


class ScreenDownstream(Base):
    """
    None
    """
    __tablename__ = 'Screen_downstream'

    Screen_name = Column(Text(), ForeignKey('Screen.name'), primary_key=True)
    downstream_name = Column(Text(), ForeignKey('AcceleratorElement.name'), primary_key=True)
    

    def __repr__(self):
        return f"Screen_downstream(Screen_name={self.Screen_name},downstream_name={self.downstream_name},)"



    


class ChargeDiagnosticAlias(Base):
    """
    None
    """
    __tablename__ = 'ChargeDiagnostic_alias'

    ChargeDiagnostic_name = Column(Text(), ForeignKey('ChargeDiagnostic.name'), primary_key=True)
    alias = Column(Text(), primary_key=True)
    

    def __repr__(self):
        return f"ChargeDiagnostic_alias(ChargeDiagnostic_name={self.ChargeDiagnostic_name},alias={self.alias},)"



    


class ChargeDiagnosticInputs(Base):
    """
    None
    """
    __tablename__ = 'ChargeDiagnostic_inputs'

    ChargeDiagnostic_name = Column(Text(), ForeignKey('ChargeDiagnostic.name'), primary_key=True)
    inputs = Column(Enum('current', 'voltage', 'phase', 'setpoint', 'on_off_state', 'open_closed_state', 'position', 'rotation', 'power', 'pressure', 'charge', 'absolute_time', 'relative_time', 'shot_number', 'value', 'waveform', 'magnetic_field', name='IOTypeEnum'), primary_key=True)
    

    def __repr__(self):
        return f"ChargeDiagnostic_inputs(ChargeDiagnostic_name={self.ChargeDiagnostic_name},inputs={self.inputs},)"



    


class ChargeDiagnosticOutputs(Base):
    """
    None
    """
    __tablename__ = 'ChargeDiagnostic_outputs'

    ChargeDiagnostic_name = Column(Text(), ForeignKey('ChargeDiagnostic.name'), primary_key=True)
    outputs = Column(Enum('current', 'voltage', 'phase', 'setpoint', 'on_off_state', 'open_closed_state', 'position', 'rotation', 'power', 'pressure', 'charge', 'absolute_time', 'relative_time', 'shot_number', 'value', 'waveform', 'magnetic_field', name='IOTypeEnum'), primary_key=True)
    

    def __repr__(self):
        return f"ChargeDiagnostic_outputs(ChargeDiagnostic_name={self.ChargeDiagnostic_name},outputs={self.outputs},)"



    


class ChargeDiagnosticUpstream(Base):
    """
    None
    """
    __tablename__ = 'ChargeDiagnostic_upstream'

    ChargeDiagnostic_name = Column(Text(), ForeignKey('ChargeDiagnostic.name'), primary_key=True)
    upstream_name = Column(Text(), ForeignKey('AcceleratorElement.name'), primary_key=True)
    

    def __repr__(self):
        return f"ChargeDiagnostic_upstream(ChargeDiagnostic_name={self.ChargeDiagnostic_name},upstream_name={self.upstream_name},)"



    


class ChargeDiagnosticDownstream(Base):
    """
    None
    """
    __tablename__ = 'ChargeDiagnostic_downstream'

    ChargeDiagnostic_name = Column(Text(), ForeignKey('ChargeDiagnostic.name'), primary_key=True)
    downstream_name = Column(Text(), ForeignKey('AcceleratorElement.name'), primary_key=True)
    

    def __repr__(self):
        return f"ChargeDiagnostic_downstream(ChargeDiagnostic_name={self.ChargeDiagnostic_name},downstream_name={self.downstream_name},)"



    


class WallCurrentMonitorAlias(Base):
    """
    None
    """
    __tablename__ = 'WallCurrentMonitor_alias'

    WallCurrentMonitor_name = Column(Text(), ForeignKey('WallCurrentMonitor.name'), primary_key=True)
    alias = Column(Text(), primary_key=True)
    

    def __repr__(self):
        return f"WallCurrentMonitor_alias(WallCurrentMonitor_name={self.WallCurrentMonitor_name},alias={self.alias},)"



    


class WallCurrentMonitorInputs(Base):
    """
    None
    """
    __tablename__ = 'WallCurrentMonitor_inputs'

    WallCurrentMonitor_name = Column(Text(), ForeignKey('WallCurrentMonitor.name'), primary_key=True)
    inputs = Column(Enum('current', 'voltage', 'phase', 'setpoint', 'on_off_state', 'open_closed_state', 'position', 'rotation', 'power', 'pressure', 'charge', 'absolute_time', 'relative_time', 'shot_number', 'value', 'waveform', 'magnetic_field', name='IOTypeEnum'), primary_key=True)
    

    def __repr__(self):
        return f"WallCurrentMonitor_inputs(WallCurrentMonitor_name={self.WallCurrentMonitor_name},inputs={self.inputs},)"



    


class WallCurrentMonitorOutputs(Base):
    """
    None
    """
    __tablename__ = 'WallCurrentMonitor_outputs'

    WallCurrentMonitor_name = Column(Text(), ForeignKey('WallCurrentMonitor.name'), primary_key=True)
    outputs = Column(Enum('current', 'voltage', 'phase', 'setpoint', 'on_off_state', 'open_closed_state', 'position', 'rotation', 'power', 'pressure', 'charge', 'absolute_time', 'relative_time', 'shot_number', 'value', 'waveform', 'magnetic_field', name='IOTypeEnum'), primary_key=True)
    

    def __repr__(self):
        return f"WallCurrentMonitor_outputs(WallCurrentMonitor_name={self.WallCurrentMonitor_name},outputs={self.outputs},)"



    


class WallCurrentMonitorUpstream(Base):
    """
    None
    """
    __tablename__ = 'WallCurrentMonitor_upstream'

    WallCurrentMonitor_name = Column(Text(), ForeignKey('WallCurrentMonitor.name'), primary_key=True)
    upstream_name = Column(Text(), ForeignKey('AcceleratorElement.name'), primary_key=True)
    

    def __repr__(self):
        return f"WallCurrentMonitor_upstream(WallCurrentMonitor_name={self.WallCurrentMonitor_name},upstream_name={self.upstream_name},)"



    


class WallCurrentMonitorDownstream(Base):
    """
    None
    """
    __tablename__ = 'WallCurrentMonitor_downstream'

    WallCurrentMonitor_name = Column(Text(), ForeignKey('WallCurrentMonitor.name'), primary_key=True)
    downstream_name = Column(Text(), ForeignKey('AcceleratorElement.name'), primary_key=True)
    

    def __repr__(self):
        return f"WallCurrentMonitor_downstream(WallCurrentMonitor_name={self.WallCurrentMonitor_name},downstream_name={self.downstream_name},)"



    


class FaradayCupMonitorAlias(Base):
    """
    None
    """
    __tablename__ = 'FaradayCupMonitor_alias'

    FaradayCupMonitor_name = Column(Text(), ForeignKey('FaradayCupMonitor.name'), primary_key=True)
    alias = Column(Text(), primary_key=True)
    

    def __repr__(self):
        return f"FaradayCupMonitor_alias(FaradayCupMonitor_name={self.FaradayCupMonitor_name},alias={self.alias},)"



    


class FaradayCupMonitorInputs(Base):
    """
    None
    """
    __tablename__ = 'FaradayCupMonitor_inputs'

    FaradayCupMonitor_name = Column(Text(), ForeignKey('FaradayCupMonitor.name'), primary_key=True)
    inputs = Column(Enum('current', 'voltage', 'phase', 'setpoint', 'on_off_state', 'open_closed_state', 'position', 'rotation', 'power', 'pressure', 'charge', 'absolute_time', 'relative_time', 'shot_number', 'value', 'waveform', 'magnetic_field', name='IOTypeEnum'), primary_key=True)
    

    def __repr__(self):
        return f"FaradayCupMonitor_inputs(FaradayCupMonitor_name={self.FaradayCupMonitor_name},inputs={self.inputs},)"



    


class FaradayCupMonitorOutputs(Base):
    """
    None
    """
    __tablename__ = 'FaradayCupMonitor_outputs'

    FaradayCupMonitor_name = Column(Text(), ForeignKey('FaradayCupMonitor.name'), primary_key=True)
    outputs = Column(Enum('current', 'voltage', 'phase', 'setpoint', 'on_off_state', 'open_closed_state', 'position', 'rotation', 'power', 'pressure', 'charge', 'absolute_time', 'relative_time', 'shot_number', 'value', 'waveform', 'magnetic_field', name='IOTypeEnum'), primary_key=True)
    

    def __repr__(self):
        return f"FaradayCupMonitor_outputs(FaradayCupMonitor_name={self.FaradayCupMonitor_name},outputs={self.outputs},)"



    


class FaradayCupMonitorUpstream(Base):
    """
    None
    """
    __tablename__ = 'FaradayCupMonitor_upstream'

    FaradayCupMonitor_name = Column(Text(), ForeignKey('FaradayCupMonitor.name'), primary_key=True)
    upstream_name = Column(Text(), ForeignKey('AcceleratorElement.name'), primary_key=True)
    

    def __repr__(self):
        return f"FaradayCupMonitor_upstream(FaradayCupMonitor_name={self.FaradayCupMonitor_name},upstream_name={self.upstream_name},)"



    


class FaradayCupMonitorDownstream(Base):
    """
    None
    """
    __tablename__ = 'FaradayCupMonitor_downstream'

    FaradayCupMonitor_name = Column(Text(), ForeignKey('FaradayCupMonitor.name'), primary_key=True)
    downstream_name = Column(Text(), ForeignKey('AcceleratorElement.name'), primary_key=True)
    

    def __repr__(self):
        return f"FaradayCupMonitor_downstream(FaradayCupMonitor_name={self.FaradayCupMonitor_name},downstream_name={self.downstream_name},)"



    


class IntegratedCurrentTransformerAlias(Base):
    """
    None
    """
    __tablename__ = 'IntegratedCurrentTransformer_alias'

    IntegratedCurrentTransformer_name = Column(Text(), ForeignKey('IntegratedCurrentTransformer.name'), primary_key=True)
    alias = Column(Text(), primary_key=True)
    

    def __repr__(self):
        return f"IntegratedCurrentTransformer_alias(IntegratedCurrentTransformer_name={self.IntegratedCurrentTransformer_name},alias={self.alias},)"



    


class IntegratedCurrentTransformerInputs(Base):
    """
    None
    """
    __tablename__ = 'IntegratedCurrentTransformer_inputs'

    IntegratedCurrentTransformer_name = Column(Text(), ForeignKey('IntegratedCurrentTransformer.name'), primary_key=True)
    inputs = Column(Enum('current', 'voltage', 'phase', 'setpoint', 'on_off_state', 'open_closed_state', 'position', 'rotation', 'power', 'pressure', 'charge', 'absolute_time', 'relative_time', 'shot_number', 'value', 'waveform', 'magnetic_field', name='IOTypeEnum'), primary_key=True)
    

    def __repr__(self):
        return f"IntegratedCurrentTransformer_inputs(IntegratedCurrentTransformer_name={self.IntegratedCurrentTransformer_name},inputs={self.inputs},)"



    


class IntegratedCurrentTransformerOutputs(Base):
    """
    None
    """
    __tablename__ = 'IntegratedCurrentTransformer_outputs'

    IntegratedCurrentTransformer_name = Column(Text(), ForeignKey('IntegratedCurrentTransformer.name'), primary_key=True)
    outputs = Column(Enum('current', 'voltage', 'phase', 'setpoint', 'on_off_state', 'open_closed_state', 'position', 'rotation', 'power', 'pressure', 'charge', 'absolute_time', 'relative_time', 'shot_number', 'value', 'waveform', 'magnetic_field', name='IOTypeEnum'), primary_key=True)
    

    def __repr__(self):
        return f"IntegratedCurrentTransformer_outputs(IntegratedCurrentTransformer_name={self.IntegratedCurrentTransformer_name},outputs={self.outputs},)"



    


class IntegratedCurrentTransformerUpstream(Base):
    """
    None
    """
    __tablename__ = 'IntegratedCurrentTransformer_upstream'

    IntegratedCurrentTransformer_name = Column(Text(), ForeignKey('IntegratedCurrentTransformer.name'), primary_key=True)
    upstream_name = Column(Text(), ForeignKey('AcceleratorElement.name'), primary_key=True)
    

    def __repr__(self):
        return f"IntegratedCurrentTransformer_upstream(IntegratedCurrentTransformer_name={self.IntegratedCurrentTransformer_name},upstream_name={self.upstream_name},)"



    


class IntegratedCurrentTransformerDownstream(Base):
    """
    None
    """
    __tablename__ = 'IntegratedCurrentTransformer_downstream'

    IntegratedCurrentTransformer_name = Column(Text(), ForeignKey('IntegratedCurrentTransformer.name'), primary_key=True)
    downstream_name = Column(Text(), ForeignKey('AcceleratorElement.name'), primary_key=True)
    

    def __repr__(self):
        return f"IntegratedCurrentTransformer_downstream(IntegratedCurrentTransformer_name={self.IntegratedCurrentTransformer_name},downstream_name={self.downstream_name},)"



    


class PhotonMonitorAlias(Base):
    """
    None
    """
    __tablename__ = 'PhotonMonitor_alias'

    PhotonMonitor_name = Column(Text(), ForeignKey('PhotonMonitor.name'), primary_key=True)
    alias = Column(Text(), primary_key=True)
    

    def __repr__(self):
        return f"PhotonMonitor_alias(PhotonMonitor_name={self.PhotonMonitor_name},alias={self.alias},)"



    


class PhotonMonitorInputs(Base):
    """
    None
    """
    __tablename__ = 'PhotonMonitor_inputs'

    PhotonMonitor_name = Column(Text(), ForeignKey('PhotonMonitor.name'), primary_key=True)
    inputs = Column(Enum('current', 'voltage', 'phase', 'setpoint', 'on_off_state', 'open_closed_state', 'position', 'rotation', 'power', 'pressure', 'charge', 'absolute_time', 'relative_time', 'shot_number', 'value', 'waveform', 'magnetic_field', name='IOTypeEnum'), primary_key=True)
    

    def __repr__(self):
        return f"PhotonMonitor_inputs(PhotonMonitor_name={self.PhotonMonitor_name},inputs={self.inputs},)"



    


class PhotonMonitorOutputs(Base):
    """
    None
    """
    __tablename__ = 'PhotonMonitor_outputs'

    PhotonMonitor_name = Column(Text(), ForeignKey('PhotonMonitor.name'), primary_key=True)
    outputs = Column(Enum('current', 'voltage', 'phase', 'setpoint', 'on_off_state', 'open_closed_state', 'position', 'rotation', 'power', 'pressure', 'charge', 'absolute_time', 'relative_time', 'shot_number', 'value', 'waveform', 'magnetic_field', name='IOTypeEnum'), primary_key=True)
    

    def __repr__(self):
        return f"PhotonMonitor_outputs(PhotonMonitor_name={self.PhotonMonitor_name},outputs={self.outputs},)"



    


class PhotonMonitorUpstream(Base):
    """
    None
    """
    __tablename__ = 'PhotonMonitor_upstream'

    PhotonMonitor_name = Column(Text(), ForeignKey('PhotonMonitor.name'), primary_key=True)
    upstream_name = Column(Text(), ForeignKey('AcceleratorElement.name'), primary_key=True)
    

    def __repr__(self):
        return f"PhotonMonitor_upstream(PhotonMonitor_name={self.PhotonMonitor_name},upstream_name={self.upstream_name},)"



    


class PhotonMonitorDownstream(Base):
    """
    None
    """
    __tablename__ = 'PhotonMonitor_downstream'

    PhotonMonitor_name = Column(Text(), ForeignKey('PhotonMonitor.name'), primary_key=True)
    downstream_name = Column(Text(), ForeignKey('AcceleratorElement.name'), primary_key=True)
    

    def __repr__(self):
        return f"PhotonMonitor_downstream(PhotonMonitor_name={self.PhotonMonitor_name},downstream_name={self.downstream_name},)"



    


class ScreenDiagnosticElementDevices(Base):
    """
    None
    """
    __tablename__ = 'ScreenDiagnosticElement_devices'

    ScreenDiagnosticElement_id = Column(Integer(), ForeignKey('ScreenDiagnosticElement.id'), primary_key=True)
    devices = Column(Text(), primary_key=True)
    

    def __repr__(self):
        return f"ScreenDiagnosticElement_devices(ScreenDiagnosticElement_id={self.ScreenDiagnosticElement_id},devices={self.devices},)"



    


class CameraMaskMiddle(Base):
    """
    None
    """
    __tablename__ = 'CameraMask_middle'

    CameraMask_id = Column(Integer(), ForeignKey('CameraMask.id'), primary_key=True)
    middle = Column(Float(), primary_key=True)
    

    def __repr__(self):
        return f"CameraMask_middle(CameraMask_id={self.CameraMask_id},middle={self.middle},)"



    


class CameraMaskRadius(Base):
    """
    None
    """
    __tablename__ = 'CameraMask_radius'

    CameraMask_id = Column(Integer(), ForeignKey('CameraMask.id'), primary_key=True)
    radius = Column(Float(), primary_key=True)
    

    def __repr__(self):
        return f"CameraMask_radius(CameraMask_id={self.CameraMask_id},radius={self.radius},)"



    


class CameraMaskMaximum(Base):
    """
    None
    """
    __tablename__ = 'CameraMask_maximum'

    CameraMask_id = Column(Integer(), ForeignKey('CameraMask.id'), primary_key=True)
    maximum = Column(Float(), primary_key=True)
    

    def __repr__(self):
        return f"CameraMask_maximum(CameraMask_id={self.CameraMask_id},maximum={self.maximum},)"



    


class CameraSensorMiddle(Base):
    """
    None
    """
    __tablename__ = 'CameraSensor_middle'

    CameraSensor_id = Column(Integer(), ForeignKey('CameraSensor.id'), primary_key=True)
    middle = Column(Float(), primary_key=True)
    

    def __repr__(self):
        return f"CameraSensor_middle(CameraSensor_id={self.CameraSensor_id},middle={self.middle},)"



    


class CameraSensorMinimum(Base):
    """
    None
    """
    __tablename__ = 'CameraSensor_minimum'

    CameraSensor_id = Column(Integer(), ForeignKey('CameraSensor.id'), primary_key=True)
    minimum = Column(Float(), primary_key=True)
    

    def __repr__(self):
        return f"CameraSensor_minimum(CameraSensor_id={self.CameraSensor_id},minimum={self.minimum},)"



    


class CameraSensorMaximum(Base):
    """
    None
    """
    __tablename__ = 'CameraSensor_maximum'

    CameraSensor_id = Column(Integer(), ForeignKey('CameraSensor.id'), primary_key=True)
    maximum = Column(Float(), primary_key=True)
    

    def __repr__(self):
        return f"CameraSensor_maximum(CameraSensor_id={self.CameraSensor_id},maximum={self.maximum},)"



    


class CameraSensorOperatingMiddle(Base):
    """
    None
    """
    __tablename__ = 'CameraSensor_operating_middle'

    CameraSensor_id = Column(Integer(), ForeignKey('CameraSensor.id'), primary_key=True)
    operating_middle = Column(Float(), primary_key=True)
    

    def __repr__(self):
        return f"CameraSensor_operating_middle(CameraSensor_id={self.CameraSensor_id},operating_middle={self.operating_middle},)"



    


class CameraSensorMechanicalMiddle(Base):
    """
    None
    """
    __tablename__ = 'CameraSensor_mechanical_middle'

    CameraSensor_id = Column(Integer(), ForeignKey('CameraSensor.id'), primary_key=True)
    mechanical_middle = Column(Float(), primary_key=True)
    

    def __repr__(self):
        return f"CameraSensor_mechanical_middle(CameraSensor_id={self.CameraSensor_id},mechanical_middle={self.mechanical_middle},)"



    


class PlasmaAlias(Base):
    """
    None
    """
    __tablename__ = 'Plasma_alias'

    Plasma_name = Column(Text(), ForeignKey('Plasma.name'), primary_key=True)
    alias = Column(Text(), primary_key=True)
    

    def __repr__(self):
        return f"Plasma_alias(Plasma_name={self.Plasma_name},alias={self.alias},)"



    


class PlasmaInputs(Base):
    """
    None
    """
    __tablename__ = 'Plasma_inputs'

    Plasma_name = Column(Text(), ForeignKey('Plasma.name'), primary_key=True)
    inputs = Column(Enum('current', 'voltage', 'phase', 'setpoint', 'on_off_state', 'open_closed_state', 'position', 'rotation', 'power', 'pressure', 'charge', 'absolute_time', 'relative_time', 'shot_number', 'value', 'waveform', 'magnetic_field', name='IOTypeEnum'), primary_key=True)
    

    def __repr__(self):
        return f"Plasma_inputs(Plasma_name={self.Plasma_name},inputs={self.inputs},)"



    


class PlasmaOutputs(Base):
    """
    None
    """
    __tablename__ = 'Plasma_outputs'

    Plasma_name = Column(Text(), ForeignKey('Plasma.name'), primary_key=True)
    outputs = Column(Enum('current', 'voltage', 'phase', 'setpoint', 'on_off_state', 'open_closed_state', 'position', 'rotation', 'power', 'pressure', 'charge', 'absolute_time', 'relative_time', 'shot_number', 'value', 'waveform', 'magnetic_field', name='IOTypeEnum'), primary_key=True)
    

    def __repr__(self):
        return f"Plasma_outputs(Plasma_name={self.Plasma_name},outputs={self.outputs},)"



    


class PlasmaUpstream(Base):
    """
    None
    """
    __tablename__ = 'Plasma_upstream'

    Plasma_name = Column(Text(), ForeignKey('Plasma.name'), primary_key=True)
    upstream_name = Column(Text(), ForeignKey('AcceleratorElement.name'), primary_key=True)
    

    def __repr__(self):
        return f"Plasma_upstream(Plasma_name={self.Plasma_name},upstream_name={self.upstream_name},)"



    


class PlasmaDownstream(Base):
    """
    None
    """
    __tablename__ = 'Plasma_downstream'

    Plasma_name = Column(Text(), ForeignKey('Plasma.name'), primary_key=True)
    downstream_name = Column(Text(), ForeignKey('AcceleratorElement.name'), primary_key=True)
    

    def __repr__(self):
        return f"Plasma_downstream(Plasma_name={self.Plasma_name},downstream_name={self.downstream_name},)"



    


class LaserEnergyMeterAlias(Base):
    """
    None
    """
    __tablename__ = 'LaserEnergyMeter_alias'

    LaserEnergyMeter_name = Column(Text(), ForeignKey('LaserEnergyMeter.name'), primary_key=True)
    alias = Column(Text(), primary_key=True)
    

    def __repr__(self):
        return f"LaserEnergyMeter_alias(LaserEnergyMeter_name={self.LaserEnergyMeter_name},alias={self.alias},)"



    


class LaserEnergyMeterInputs(Base):
    """
    None
    """
    __tablename__ = 'LaserEnergyMeter_inputs'

    LaserEnergyMeter_name = Column(Text(), ForeignKey('LaserEnergyMeter.name'), primary_key=True)
    inputs = Column(Enum('current', 'voltage', 'phase', 'setpoint', 'on_off_state', 'open_closed_state', 'position', 'rotation', 'power', 'pressure', 'charge', 'absolute_time', 'relative_time', 'shot_number', 'value', 'waveform', 'magnetic_field', name='IOTypeEnum'), primary_key=True)
    

    def __repr__(self):
        return f"LaserEnergyMeter_inputs(LaserEnergyMeter_name={self.LaserEnergyMeter_name},inputs={self.inputs},)"



    


class LaserEnergyMeterOutputs(Base):
    """
    None
    """
    __tablename__ = 'LaserEnergyMeter_outputs'

    LaserEnergyMeter_name = Column(Text(), ForeignKey('LaserEnergyMeter.name'), primary_key=True)
    outputs = Column(Enum('current', 'voltage', 'phase', 'setpoint', 'on_off_state', 'open_closed_state', 'position', 'rotation', 'power', 'pressure', 'charge', 'absolute_time', 'relative_time', 'shot_number', 'value', 'waveform', 'magnetic_field', name='IOTypeEnum'), primary_key=True)
    

    def __repr__(self):
        return f"LaserEnergyMeter_outputs(LaserEnergyMeter_name={self.LaserEnergyMeter_name},outputs={self.outputs},)"



    


class LaserEnergyMeterUpstream(Base):
    """
    None
    """
    __tablename__ = 'LaserEnergyMeter_upstream'

    LaserEnergyMeter_name = Column(Text(), ForeignKey('LaserEnergyMeter.name'), primary_key=True)
    upstream_name = Column(Text(), ForeignKey('AcceleratorElement.name'), primary_key=True)
    

    def __repr__(self):
        return f"LaserEnergyMeter_upstream(LaserEnergyMeter_name={self.LaserEnergyMeter_name},upstream_name={self.upstream_name},)"



    


class LaserEnergyMeterDownstream(Base):
    """
    None
    """
    __tablename__ = 'LaserEnergyMeter_downstream'

    LaserEnergyMeter_name = Column(Text(), ForeignKey('LaserEnergyMeter.name'), primary_key=True)
    downstream_name = Column(Text(), ForeignKey('AcceleratorElement.name'), primary_key=True)
    

    def __repr__(self):
        return f"LaserEnergyMeter_downstream(LaserEnergyMeter_name={self.LaserEnergyMeter_name},downstream_name={self.downstream_name},)"



    


class LaserHalfWavePlateAlias(Base):
    """
    None
    """
    __tablename__ = 'LaserHalfWavePlate_alias'

    LaserHalfWavePlate_name = Column(Text(), ForeignKey('LaserHalfWavePlate.name'), primary_key=True)
    alias = Column(Text(), primary_key=True)
    

    def __repr__(self):
        return f"LaserHalfWavePlate_alias(LaserHalfWavePlate_name={self.LaserHalfWavePlate_name},alias={self.alias},)"



    


class LaserHalfWavePlateInputs(Base):
    """
    None
    """
    __tablename__ = 'LaserHalfWavePlate_inputs'

    LaserHalfWavePlate_name = Column(Text(), ForeignKey('LaserHalfWavePlate.name'), primary_key=True)
    inputs = Column(Enum('current', 'voltage', 'phase', 'setpoint', 'on_off_state', 'open_closed_state', 'position', 'rotation', 'power', 'pressure', 'charge', 'absolute_time', 'relative_time', 'shot_number', 'value', 'waveform', 'magnetic_field', name='IOTypeEnum'), primary_key=True)
    

    def __repr__(self):
        return f"LaserHalfWavePlate_inputs(LaserHalfWavePlate_name={self.LaserHalfWavePlate_name},inputs={self.inputs},)"



    


class LaserHalfWavePlateOutputs(Base):
    """
    None
    """
    __tablename__ = 'LaserHalfWavePlate_outputs'

    LaserHalfWavePlate_name = Column(Text(), ForeignKey('LaserHalfWavePlate.name'), primary_key=True)
    outputs = Column(Enum('current', 'voltage', 'phase', 'setpoint', 'on_off_state', 'open_closed_state', 'position', 'rotation', 'power', 'pressure', 'charge', 'absolute_time', 'relative_time', 'shot_number', 'value', 'waveform', 'magnetic_field', name='IOTypeEnum'), primary_key=True)
    

    def __repr__(self):
        return f"LaserHalfWavePlate_outputs(LaserHalfWavePlate_name={self.LaserHalfWavePlate_name},outputs={self.outputs},)"



    


class LaserHalfWavePlateUpstream(Base):
    """
    None
    """
    __tablename__ = 'LaserHalfWavePlate_upstream'

    LaserHalfWavePlate_name = Column(Text(), ForeignKey('LaserHalfWavePlate.name'), primary_key=True)
    upstream_name = Column(Text(), ForeignKey('AcceleratorElement.name'), primary_key=True)
    

    def __repr__(self):
        return f"LaserHalfWavePlate_upstream(LaserHalfWavePlate_name={self.LaserHalfWavePlate_name},upstream_name={self.upstream_name},)"



    


class LaserHalfWavePlateDownstream(Base):
    """
    None
    """
    __tablename__ = 'LaserHalfWavePlate_downstream'

    LaserHalfWavePlate_name = Column(Text(), ForeignKey('LaserHalfWavePlate.name'), primary_key=True)
    downstream_name = Column(Text(), ForeignKey('AcceleratorElement.name'), primary_key=True)
    

    def __repr__(self):
        return f"LaserHalfWavePlate_downstream(LaserHalfWavePlate_name={self.LaserHalfWavePlate_name},downstream_name={self.downstream_name},)"



    


class LaserMirrorAlias(Base):
    """
    None
    """
    __tablename__ = 'LaserMirror_alias'

    LaserMirror_name = Column(Text(), ForeignKey('LaserMirror.name'), primary_key=True)
    alias = Column(Text(), primary_key=True)
    

    def __repr__(self):
        return f"LaserMirror_alias(LaserMirror_name={self.LaserMirror_name},alias={self.alias},)"



    


class LaserMirrorInputs(Base):
    """
    None
    """
    __tablename__ = 'LaserMirror_inputs'

    LaserMirror_name = Column(Text(), ForeignKey('LaserMirror.name'), primary_key=True)
    inputs = Column(Enum('current', 'voltage', 'phase', 'setpoint', 'on_off_state', 'open_closed_state', 'position', 'rotation', 'power', 'pressure', 'charge', 'absolute_time', 'relative_time', 'shot_number', 'value', 'waveform', 'magnetic_field', name='IOTypeEnum'), primary_key=True)
    

    def __repr__(self):
        return f"LaserMirror_inputs(LaserMirror_name={self.LaserMirror_name},inputs={self.inputs},)"



    


class LaserMirrorOutputs(Base):
    """
    None
    """
    __tablename__ = 'LaserMirror_outputs'

    LaserMirror_name = Column(Text(), ForeignKey('LaserMirror.name'), primary_key=True)
    outputs = Column(Enum('current', 'voltage', 'phase', 'setpoint', 'on_off_state', 'open_closed_state', 'position', 'rotation', 'power', 'pressure', 'charge', 'absolute_time', 'relative_time', 'shot_number', 'value', 'waveform', 'magnetic_field', name='IOTypeEnum'), primary_key=True)
    

    def __repr__(self):
        return f"LaserMirror_outputs(LaserMirror_name={self.LaserMirror_name},outputs={self.outputs},)"



    


class LaserMirrorUpstream(Base):
    """
    None
    """
    __tablename__ = 'LaserMirror_upstream'

    LaserMirror_name = Column(Text(), ForeignKey('LaserMirror.name'), primary_key=True)
    upstream_name = Column(Text(), ForeignKey('AcceleratorElement.name'), primary_key=True)
    

    def __repr__(self):
        return f"LaserMirror_upstream(LaserMirror_name={self.LaserMirror_name},upstream_name={self.upstream_name},)"



    


class LaserMirrorDownstream(Base):
    """
    None
    """
    __tablename__ = 'LaserMirror_downstream'

    LaserMirror_name = Column(Text(), ForeignKey('LaserMirror.name'), primary_key=True)
    downstream_name = Column(Text(), ForeignKey('AcceleratorElement.name'), primary_key=True)
    

    def __repr__(self):
        return f"LaserMirror_downstream(LaserMirror_name={self.LaserMirror_name},downstream_name={self.downstream_name},)"



    


class LaserAttenuatorAlias(Base):
    """
    None
    """
    __tablename__ = 'LaserAttenuator_alias'

    LaserAttenuator_name = Column(Text(), ForeignKey('LaserAttenuator.name'), primary_key=True)
    alias = Column(Text(), primary_key=True)
    

    def __repr__(self):
        return f"LaserAttenuator_alias(LaserAttenuator_name={self.LaserAttenuator_name},alias={self.alias},)"



    


class LaserAttenuatorInputs(Base):
    """
    None
    """
    __tablename__ = 'LaserAttenuator_inputs'

    LaserAttenuator_name = Column(Text(), ForeignKey('LaserAttenuator.name'), primary_key=True)
    inputs = Column(Enum('current', 'voltage', 'phase', 'setpoint', 'on_off_state', 'open_closed_state', 'position', 'rotation', 'power', 'pressure', 'charge', 'absolute_time', 'relative_time', 'shot_number', 'value', 'waveform', 'magnetic_field', name='IOTypeEnum'), primary_key=True)
    

    def __repr__(self):
        return f"LaserAttenuator_inputs(LaserAttenuator_name={self.LaserAttenuator_name},inputs={self.inputs},)"



    


class LaserAttenuatorOutputs(Base):
    """
    None
    """
    __tablename__ = 'LaserAttenuator_outputs'

    LaserAttenuator_name = Column(Text(), ForeignKey('LaserAttenuator.name'), primary_key=True)
    outputs = Column(Enum('current', 'voltage', 'phase', 'setpoint', 'on_off_state', 'open_closed_state', 'position', 'rotation', 'power', 'pressure', 'charge', 'absolute_time', 'relative_time', 'shot_number', 'value', 'waveform', 'magnetic_field', name='IOTypeEnum'), primary_key=True)
    

    def __repr__(self):
        return f"LaserAttenuator_outputs(LaserAttenuator_name={self.LaserAttenuator_name},outputs={self.outputs},)"



    


class LaserAttenuatorUpstream(Base):
    """
    None
    """
    __tablename__ = 'LaserAttenuator_upstream'

    LaserAttenuator_name = Column(Text(), ForeignKey('LaserAttenuator.name'), primary_key=True)
    upstream_name = Column(Text(), ForeignKey('AcceleratorElement.name'), primary_key=True)
    

    def __repr__(self):
        return f"LaserAttenuator_upstream(LaserAttenuator_name={self.LaserAttenuator_name},upstream_name={self.upstream_name},)"



    


class LaserAttenuatorDownstream(Base):
    """
    None
    """
    __tablename__ = 'LaserAttenuator_downstream'

    LaserAttenuator_name = Column(Text(), ForeignKey('LaserAttenuator.name'), primary_key=True)
    downstream_name = Column(Text(), ForeignKey('AcceleratorElement.name'), primary_key=True)
    

    def __repr__(self):
        return f"LaserAttenuator_downstream(LaserAttenuator_name={self.LaserAttenuator_name},downstream_name={self.downstream_name},)"



    


class DipoleAlias(Base):
    """
    None
    """
    __tablename__ = 'Dipole_alias'

    Dipole_name = Column(Text(), ForeignKey('Dipole.name'), primary_key=True)
    alias = Column(Text(), primary_key=True)
    

    def __repr__(self):
        return f"Dipole_alias(Dipole_name={self.Dipole_name},alias={self.alias},)"



    


class DipoleInputs(Base):
    """
    None
    """
    __tablename__ = 'Dipole_inputs'

    Dipole_name = Column(Text(), ForeignKey('Dipole.name'), primary_key=True)
    inputs = Column(Enum('current', 'voltage', 'phase', 'setpoint', 'on_off_state', 'open_closed_state', 'position', 'rotation', 'power', 'pressure', 'charge', 'absolute_time', 'relative_time', 'shot_number', 'value', 'waveform', 'magnetic_field', name='IOTypeEnum'), primary_key=True)
    

    def __repr__(self):
        return f"Dipole_inputs(Dipole_name={self.Dipole_name},inputs={self.inputs},)"



    


class DipoleOutputs(Base):
    """
    None
    """
    __tablename__ = 'Dipole_outputs'

    Dipole_name = Column(Text(), ForeignKey('Dipole.name'), primary_key=True)
    outputs = Column(Enum('current', 'voltage', 'phase', 'setpoint', 'on_off_state', 'open_closed_state', 'position', 'rotation', 'power', 'pressure', 'charge', 'absolute_time', 'relative_time', 'shot_number', 'value', 'waveform', 'magnetic_field', name='IOTypeEnum'), primary_key=True)
    

    def __repr__(self):
        return f"Dipole_outputs(Dipole_name={self.Dipole_name},outputs={self.outputs},)"



    


class DipoleUpstream(Base):
    """
    None
    """
    __tablename__ = 'Dipole_upstream'

    Dipole_name = Column(Text(), ForeignKey('Dipole.name'), primary_key=True)
    upstream_name = Column(Text(), ForeignKey('AcceleratorElement.name'), primary_key=True)
    

    def __repr__(self):
        return f"Dipole_upstream(Dipole_name={self.Dipole_name},upstream_name={self.upstream_name},)"



    


class DipoleDownstream(Base):
    """
    None
    """
    __tablename__ = 'Dipole_downstream'

    Dipole_name = Column(Text(), ForeignKey('Dipole.name'), primary_key=True)
    downstream_name = Column(Text(), ForeignKey('AcceleratorElement.name'), primary_key=True)
    

    def __repr__(self):
        return f"Dipole_downstream(Dipole_name={self.Dipole_name},downstream_name={self.downstream_name},)"



    


class QuadrupoleAlias(Base):
    """
    None
    """
    __tablename__ = 'Quadrupole_alias'

    Quadrupole_name = Column(Text(), ForeignKey('Quadrupole.name'), primary_key=True)
    alias = Column(Text(), primary_key=True)
    

    def __repr__(self):
        return f"Quadrupole_alias(Quadrupole_name={self.Quadrupole_name},alias={self.alias},)"



    


class QuadrupoleInputs(Base):
    """
    None
    """
    __tablename__ = 'Quadrupole_inputs'

    Quadrupole_name = Column(Text(), ForeignKey('Quadrupole.name'), primary_key=True)
    inputs = Column(Enum('current', 'voltage', 'phase', 'setpoint', 'on_off_state', 'open_closed_state', 'position', 'rotation', 'power', 'pressure', 'charge', 'absolute_time', 'relative_time', 'shot_number', 'value', 'waveform', 'magnetic_field', name='IOTypeEnum'), primary_key=True)
    

    def __repr__(self):
        return f"Quadrupole_inputs(Quadrupole_name={self.Quadrupole_name},inputs={self.inputs},)"



    


class QuadrupoleOutputs(Base):
    """
    None
    """
    __tablename__ = 'Quadrupole_outputs'

    Quadrupole_name = Column(Text(), ForeignKey('Quadrupole.name'), primary_key=True)
    outputs = Column(Enum('current', 'voltage', 'phase', 'setpoint', 'on_off_state', 'open_closed_state', 'position', 'rotation', 'power', 'pressure', 'charge', 'absolute_time', 'relative_time', 'shot_number', 'value', 'waveform', 'magnetic_field', name='IOTypeEnum'), primary_key=True)
    

    def __repr__(self):
        return f"Quadrupole_outputs(Quadrupole_name={self.Quadrupole_name},outputs={self.outputs},)"



    


class QuadrupoleUpstream(Base):
    """
    None
    """
    __tablename__ = 'Quadrupole_upstream'

    Quadrupole_name = Column(Text(), ForeignKey('Quadrupole.name'), primary_key=True)
    upstream_name = Column(Text(), ForeignKey('AcceleratorElement.name'), primary_key=True)
    

    def __repr__(self):
        return f"Quadrupole_upstream(Quadrupole_name={self.Quadrupole_name},upstream_name={self.upstream_name},)"



    


class QuadrupoleDownstream(Base):
    """
    None
    """
    __tablename__ = 'Quadrupole_downstream'

    Quadrupole_name = Column(Text(), ForeignKey('Quadrupole.name'), primary_key=True)
    downstream_name = Column(Text(), ForeignKey('AcceleratorElement.name'), primary_key=True)
    

    def __repr__(self):
        return f"Quadrupole_downstream(Quadrupole_name={self.Quadrupole_name},downstream_name={self.downstream_name},)"



    


class SextupoleAlias(Base):
    """
    None
    """
    __tablename__ = 'Sextupole_alias'

    Sextupole_name = Column(Text(), ForeignKey('Sextupole.name'), primary_key=True)
    alias = Column(Text(), primary_key=True)
    

    def __repr__(self):
        return f"Sextupole_alias(Sextupole_name={self.Sextupole_name},alias={self.alias},)"



    


class SextupoleInputs(Base):
    """
    None
    """
    __tablename__ = 'Sextupole_inputs'

    Sextupole_name = Column(Text(), ForeignKey('Sextupole.name'), primary_key=True)
    inputs = Column(Enum('current', 'voltage', 'phase', 'setpoint', 'on_off_state', 'open_closed_state', 'position', 'rotation', 'power', 'pressure', 'charge', 'absolute_time', 'relative_time', 'shot_number', 'value', 'waveform', 'magnetic_field', name='IOTypeEnum'), primary_key=True)
    

    def __repr__(self):
        return f"Sextupole_inputs(Sextupole_name={self.Sextupole_name},inputs={self.inputs},)"



    


class SextupoleOutputs(Base):
    """
    None
    """
    __tablename__ = 'Sextupole_outputs'

    Sextupole_name = Column(Text(), ForeignKey('Sextupole.name'), primary_key=True)
    outputs = Column(Enum('current', 'voltage', 'phase', 'setpoint', 'on_off_state', 'open_closed_state', 'position', 'rotation', 'power', 'pressure', 'charge', 'absolute_time', 'relative_time', 'shot_number', 'value', 'waveform', 'magnetic_field', name='IOTypeEnum'), primary_key=True)
    

    def __repr__(self):
        return f"Sextupole_outputs(Sextupole_name={self.Sextupole_name},outputs={self.outputs},)"



    


class SextupoleUpstream(Base):
    """
    None
    """
    __tablename__ = 'Sextupole_upstream'

    Sextupole_name = Column(Text(), ForeignKey('Sextupole.name'), primary_key=True)
    upstream_name = Column(Text(), ForeignKey('AcceleratorElement.name'), primary_key=True)
    

    def __repr__(self):
        return f"Sextupole_upstream(Sextupole_name={self.Sextupole_name},upstream_name={self.upstream_name},)"



    


class SextupoleDownstream(Base):
    """
    None
    """
    __tablename__ = 'Sextupole_downstream'

    Sextupole_name = Column(Text(), ForeignKey('Sextupole.name'), primary_key=True)
    downstream_name = Column(Text(), ForeignKey('AcceleratorElement.name'), primary_key=True)
    

    def __repr__(self):
        return f"Sextupole_downstream(Sextupole_name={self.Sextupole_name},downstream_name={self.downstream_name},)"



    


class OctupoleAlias(Base):
    """
    None
    """
    __tablename__ = 'Octupole_alias'

    Octupole_name = Column(Text(), ForeignKey('Octupole.name'), primary_key=True)
    alias = Column(Text(), primary_key=True)
    

    def __repr__(self):
        return f"Octupole_alias(Octupole_name={self.Octupole_name},alias={self.alias},)"



    


class OctupoleInputs(Base):
    """
    None
    """
    __tablename__ = 'Octupole_inputs'

    Octupole_name = Column(Text(), ForeignKey('Octupole.name'), primary_key=True)
    inputs = Column(Enum('current', 'voltage', 'phase', 'setpoint', 'on_off_state', 'open_closed_state', 'position', 'rotation', 'power', 'pressure', 'charge', 'absolute_time', 'relative_time', 'shot_number', 'value', 'waveform', 'magnetic_field', name='IOTypeEnum'), primary_key=True)
    

    def __repr__(self):
        return f"Octupole_inputs(Octupole_name={self.Octupole_name},inputs={self.inputs},)"



    


class OctupoleOutputs(Base):
    """
    None
    """
    __tablename__ = 'Octupole_outputs'

    Octupole_name = Column(Text(), ForeignKey('Octupole.name'), primary_key=True)
    outputs = Column(Enum('current', 'voltage', 'phase', 'setpoint', 'on_off_state', 'open_closed_state', 'position', 'rotation', 'power', 'pressure', 'charge', 'absolute_time', 'relative_time', 'shot_number', 'value', 'waveform', 'magnetic_field', name='IOTypeEnum'), primary_key=True)
    

    def __repr__(self):
        return f"Octupole_outputs(Octupole_name={self.Octupole_name},outputs={self.outputs},)"



    


class OctupoleUpstream(Base):
    """
    None
    """
    __tablename__ = 'Octupole_upstream'

    Octupole_name = Column(Text(), ForeignKey('Octupole.name'), primary_key=True)
    upstream_name = Column(Text(), ForeignKey('AcceleratorElement.name'), primary_key=True)
    

    def __repr__(self):
        return f"Octupole_upstream(Octupole_name={self.Octupole_name},upstream_name={self.upstream_name},)"



    


class OctupoleDownstream(Base):
    """
    None
    """
    __tablename__ = 'Octupole_downstream'

    Octupole_name = Column(Text(), ForeignKey('Octupole.name'), primary_key=True)
    downstream_name = Column(Text(), ForeignKey('AcceleratorElement.name'), primary_key=True)
    

    def __repr__(self):
        return f"Octupole_downstream(Octupole_name={self.Octupole_name},downstream_name={self.downstream_name},)"



    


class HorizontalCorrectorAlias(Base):
    """
    None
    """
    __tablename__ = 'HorizontalCorrector_alias'

    HorizontalCorrector_name = Column(Text(), ForeignKey('HorizontalCorrector.name'), primary_key=True)
    alias = Column(Text(), primary_key=True)
    

    def __repr__(self):
        return f"HorizontalCorrector_alias(HorizontalCorrector_name={self.HorizontalCorrector_name},alias={self.alias},)"



    


class HorizontalCorrectorInputs(Base):
    """
    None
    """
    __tablename__ = 'HorizontalCorrector_inputs'

    HorizontalCorrector_name = Column(Text(), ForeignKey('HorizontalCorrector.name'), primary_key=True)
    inputs = Column(Enum('current', 'voltage', 'phase', 'setpoint', 'on_off_state', 'open_closed_state', 'position', 'rotation', 'power', 'pressure', 'charge', 'absolute_time', 'relative_time', 'shot_number', 'value', 'waveform', 'magnetic_field', name='IOTypeEnum'), primary_key=True)
    

    def __repr__(self):
        return f"HorizontalCorrector_inputs(HorizontalCorrector_name={self.HorizontalCorrector_name},inputs={self.inputs},)"



    


class HorizontalCorrectorOutputs(Base):
    """
    None
    """
    __tablename__ = 'HorizontalCorrector_outputs'

    HorizontalCorrector_name = Column(Text(), ForeignKey('HorizontalCorrector.name'), primary_key=True)
    outputs = Column(Enum('current', 'voltage', 'phase', 'setpoint', 'on_off_state', 'open_closed_state', 'position', 'rotation', 'power', 'pressure', 'charge', 'absolute_time', 'relative_time', 'shot_number', 'value', 'waveform', 'magnetic_field', name='IOTypeEnum'), primary_key=True)
    

    def __repr__(self):
        return f"HorizontalCorrector_outputs(HorizontalCorrector_name={self.HorizontalCorrector_name},outputs={self.outputs},)"



    


class HorizontalCorrectorUpstream(Base):
    """
    None
    """
    __tablename__ = 'HorizontalCorrector_upstream'

    HorizontalCorrector_name = Column(Text(), ForeignKey('HorizontalCorrector.name'), primary_key=True)
    upstream_name = Column(Text(), ForeignKey('AcceleratorElement.name'), primary_key=True)
    

    def __repr__(self):
        return f"HorizontalCorrector_upstream(HorizontalCorrector_name={self.HorizontalCorrector_name},upstream_name={self.upstream_name},)"



    


class HorizontalCorrectorDownstream(Base):
    """
    None
    """
    __tablename__ = 'HorizontalCorrector_downstream'

    HorizontalCorrector_name = Column(Text(), ForeignKey('HorizontalCorrector.name'), primary_key=True)
    downstream_name = Column(Text(), ForeignKey('AcceleratorElement.name'), primary_key=True)
    

    def __repr__(self):
        return f"HorizontalCorrector_downstream(HorizontalCorrector_name={self.HorizontalCorrector_name},downstream_name={self.downstream_name},)"



    


class VerticalCorrectorAlias(Base):
    """
    None
    """
    __tablename__ = 'VerticalCorrector_alias'

    VerticalCorrector_name = Column(Text(), ForeignKey('VerticalCorrector.name'), primary_key=True)
    alias = Column(Text(), primary_key=True)
    

    def __repr__(self):
        return f"VerticalCorrector_alias(VerticalCorrector_name={self.VerticalCorrector_name},alias={self.alias},)"



    


class VerticalCorrectorInputs(Base):
    """
    None
    """
    __tablename__ = 'VerticalCorrector_inputs'

    VerticalCorrector_name = Column(Text(), ForeignKey('VerticalCorrector.name'), primary_key=True)
    inputs = Column(Enum('current', 'voltage', 'phase', 'setpoint', 'on_off_state', 'open_closed_state', 'position', 'rotation', 'power', 'pressure', 'charge', 'absolute_time', 'relative_time', 'shot_number', 'value', 'waveform', 'magnetic_field', name='IOTypeEnum'), primary_key=True)
    

    def __repr__(self):
        return f"VerticalCorrector_inputs(VerticalCorrector_name={self.VerticalCorrector_name},inputs={self.inputs},)"



    


class VerticalCorrectorOutputs(Base):
    """
    None
    """
    __tablename__ = 'VerticalCorrector_outputs'

    VerticalCorrector_name = Column(Text(), ForeignKey('VerticalCorrector.name'), primary_key=True)
    outputs = Column(Enum('current', 'voltage', 'phase', 'setpoint', 'on_off_state', 'open_closed_state', 'position', 'rotation', 'power', 'pressure', 'charge', 'absolute_time', 'relative_time', 'shot_number', 'value', 'waveform', 'magnetic_field', name='IOTypeEnum'), primary_key=True)
    

    def __repr__(self):
        return f"VerticalCorrector_outputs(VerticalCorrector_name={self.VerticalCorrector_name},outputs={self.outputs},)"



    


class VerticalCorrectorUpstream(Base):
    """
    None
    """
    __tablename__ = 'VerticalCorrector_upstream'

    VerticalCorrector_name = Column(Text(), ForeignKey('VerticalCorrector.name'), primary_key=True)
    upstream_name = Column(Text(), ForeignKey('AcceleratorElement.name'), primary_key=True)
    

    def __repr__(self):
        return f"VerticalCorrector_upstream(VerticalCorrector_name={self.VerticalCorrector_name},upstream_name={self.upstream_name},)"



    


class VerticalCorrectorDownstream(Base):
    """
    None
    """
    __tablename__ = 'VerticalCorrector_downstream'

    VerticalCorrector_name = Column(Text(), ForeignKey('VerticalCorrector.name'), primary_key=True)
    downstream_name = Column(Text(), ForeignKey('AcceleratorElement.name'), primary_key=True)
    

    def __repr__(self):
        return f"VerticalCorrector_downstream(VerticalCorrector_name={self.VerticalCorrector_name},downstream_name={self.downstream_name},)"



    


class CombinedCorrectorAlias(Base):
    """
    None
    """
    __tablename__ = 'CombinedCorrector_alias'

    CombinedCorrector_name = Column(Text(), ForeignKey('CombinedCorrector.name'), primary_key=True)
    alias = Column(Text(), primary_key=True)
    

    def __repr__(self):
        return f"CombinedCorrector_alias(CombinedCorrector_name={self.CombinedCorrector_name},alias={self.alias},)"



    


class CombinedCorrectorInputs(Base):
    """
    None
    """
    __tablename__ = 'CombinedCorrector_inputs'

    CombinedCorrector_name = Column(Text(), ForeignKey('CombinedCorrector.name'), primary_key=True)
    inputs = Column(Enum('current', 'voltage', 'phase', 'setpoint', 'on_off_state', 'open_closed_state', 'position', 'rotation', 'power', 'pressure', 'charge', 'absolute_time', 'relative_time', 'shot_number', 'value', 'waveform', 'magnetic_field', name='IOTypeEnum'), primary_key=True)
    

    def __repr__(self):
        return f"CombinedCorrector_inputs(CombinedCorrector_name={self.CombinedCorrector_name},inputs={self.inputs},)"



    


class CombinedCorrectorOutputs(Base):
    """
    None
    """
    __tablename__ = 'CombinedCorrector_outputs'

    CombinedCorrector_name = Column(Text(), ForeignKey('CombinedCorrector.name'), primary_key=True)
    outputs = Column(Enum('current', 'voltage', 'phase', 'setpoint', 'on_off_state', 'open_closed_state', 'position', 'rotation', 'power', 'pressure', 'charge', 'absolute_time', 'relative_time', 'shot_number', 'value', 'waveform', 'magnetic_field', name='IOTypeEnum'), primary_key=True)
    

    def __repr__(self):
        return f"CombinedCorrector_outputs(CombinedCorrector_name={self.CombinedCorrector_name},outputs={self.outputs},)"



    


class CombinedCorrectorUpstream(Base):
    """
    None
    """
    __tablename__ = 'CombinedCorrector_upstream'

    CombinedCorrector_name = Column(Text(), ForeignKey('CombinedCorrector.name'), primary_key=True)
    upstream_name = Column(Text(), ForeignKey('AcceleratorElement.name'), primary_key=True)
    

    def __repr__(self):
        return f"CombinedCorrector_upstream(CombinedCorrector_name={self.CombinedCorrector_name},upstream_name={self.upstream_name},)"



    


class CombinedCorrectorDownstream(Base):
    """
    None
    """
    __tablename__ = 'CombinedCorrector_downstream'

    CombinedCorrector_name = Column(Text(), ForeignKey('CombinedCorrector.name'), primary_key=True)
    downstream_name = Column(Text(), ForeignKey('AcceleratorElement.name'), primary_key=True)
    

    def __repr__(self):
        return f"CombinedCorrector_downstream(CombinedCorrector_name={self.CombinedCorrector_name},downstream_name={self.downstream_name},)"



    


class SolenoidAlias(Base):
    """
    None
    """
    __tablename__ = 'Solenoid_alias'

    Solenoid_name = Column(Text(), ForeignKey('Solenoid.name'), primary_key=True)
    alias = Column(Text(), primary_key=True)
    

    def __repr__(self):
        return f"Solenoid_alias(Solenoid_name={self.Solenoid_name},alias={self.alias},)"



    


class SolenoidInputs(Base):
    """
    None
    """
    __tablename__ = 'Solenoid_inputs'

    Solenoid_name = Column(Text(), ForeignKey('Solenoid.name'), primary_key=True)
    inputs = Column(Enum('current', 'voltage', 'phase', 'setpoint', 'on_off_state', 'open_closed_state', 'position', 'rotation', 'power', 'pressure', 'charge', 'absolute_time', 'relative_time', 'shot_number', 'value', 'waveform', 'magnetic_field', name='IOTypeEnum'), primary_key=True)
    

    def __repr__(self):
        return f"Solenoid_inputs(Solenoid_name={self.Solenoid_name},inputs={self.inputs},)"



    


class SolenoidOutputs(Base):
    """
    None
    """
    __tablename__ = 'Solenoid_outputs'

    Solenoid_name = Column(Text(), ForeignKey('Solenoid.name'), primary_key=True)
    outputs = Column(Enum('current', 'voltage', 'phase', 'setpoint', 'on_off_state', 'open_closed_state', 'position', 'rotation', 'power', 'pressure', 'charge', 'absolute_time', 'relative_time', 'shot_number', 'value', 'waveform', 'magnetic_field', name='IOTypeEnum'), primary_key=True)
    

    def __repr__(self):
        return f"Solenoid_outputs(Solenoid_name={self.Solenoid_name},outputs={self.outputs},)"



    


class SolenoidUpstream(Base):
    """
    None
    """
    __tablename__ = 'Solenoid_upstream'

    Solenoid_name = Column(Text(), ForeignKey('Solenoid.name'), primary_key=True)
    upstream_name = Column(Text(), ForeignKey('AcceleratorElement.name'), primary_key=True)
    

    def __repr__(self):
        return f"Solenoid_upstream(Solenoid_name={self.Solenoid_name},upstream_name={self.upstream_name},)"



    


class SolenoidDownstream(Base):
    """
    None
    """
    __tablename__ = 'Solenoid_downstream'

    Solenoid_name = Column(Text(), ForeignKey('Solenoid.name'), primary_key=True)
    downstream_name = Column(Text(), ForeignKey('AcceleratorElement.name'), primary_key=True)
    

    def __repr__(self):
        return f"Solenoid_downstream(Solenoid_name={self.Solenoid_name},downstream_name={self.downstream_name},)"



    


class WigglerAlias(Base):
    """
    None
    """
    __tablename__ = 'Wiggler_alias'

    Wiggler_name = Column(Text(), ForeignKey('Wiggler.name'), primary_key=True)
    alias = Column(Text(), primary_key=True)
    

    def __repr__(self):
        return f"Wiggler_alias(Wiggler_name={self.Wiggler_name},alias={self.alias},)"



    


class WigglerInputs(Base):
    """
    None
    """
    __tablename__ = 'Wiggler_inputs'

    Wiggler_name = Column(Text(), ForeignKey('Wiggler.name'), primary_key=True)
    inputs = Column(Enum('current', 'voltage', 'phase', 'setpoint', 'on_off_state', 'open_closed_state', 'position', 'rotation', 'power', 'pressure', 'charge', 'absolute_time', 'relative_time', 'shot_number', 'value', 'waveform', 'magnetic_field', name='IOTypeEnum'), primary_key=True)
    

    def __repr__(self):
        return f"Wiggler_inputs(Wiggler_name={self.Wiggler_name},inputs={self.inputs},)"



    


class WigglerOutputs(Base):
    """
    None
    """
    __tablename__ = 'Wiggler_outputs'

    Wiggler_name = Column(Text(), ForeignKey('Wiggler.name'), primary_key=True)
    outputs = Column(Enum('current', 'voltage', 'phase', 'setpoint', 'on_off_state', 'open_closed_state', 'position', 'rotation', 'power', 'pressure', 'charge', 'absolute_time', 'relative_time', 'shot_number', 'value', 'waveform', 'magnetic_field', name='IOTypeEnum'), primary_key=True)
    

    def __repr__(self):
        return f"Wiggler_outputs(Wiggler_name={self.Wiggler_name},outputs={self.outputs},)"



    


class WigglerUpstream(Base):
    """
    None
    """
    __tablename__ = 'Wiggler_upstream'

    Wiggler_name = Column(Text(), ForeignKey('Wiggler.name'), primary_key=True)
    upstream_name = Column(Text(), ForeignKey('AcceleratorElement.name'), primary_key=True)
    

    def __repr__(self):
        return f"Wiggler_upstream(Wiggler_name={self.Wiggler_name},upstream_name={self.upstream_name},)"



    


class WigglerDownstream(Base):
    """
    None
    """
    __tablename__ = 'Wiggler_downstream'

    Wiggler_name = Column(Text(), ForeignKey('Wiggler.name'), primary_key=True)
    downstream_name = Column(Text(), ForeignKey('AcceleratorElement.name'), primary_key=True)
    

    def __repr__(self):
        return f"Wiggler_downstream(Wiggler_name={self.Wiggler_name},downstream_name={self.downstream_name},)"



    


class NonLinearLensAlias(Base):
    """
    None
    """
    __tablename__ = 'NonLinearLens_alias'

    NonLinearLens_name = Column(Text(), ForeignKey('NonLinearLens.name'), primary_key=True)
    alias = Column(Text(), primary_key=True)
    

    def __repr__(self):
        return f"NonLinearLens_alias(NonLinearLens_name={self.NonLinearLens_name},alias={self.alias},)"



    


class NonLinearLensInputs(Base):
    """
    None
    """
    __tablename__ = 'NonLinearLens_inputs'

    NonLinearLens_name = Column(Text(), ForeignKey('NonLinearLens.name'), primary_key=True)
    inputs = Column(Enum('current', 'voltage', 'phase', 'setpoint', 'on_off_state', 'open_closed_state', 'position', 'rotation', 'power', 'pressure', 'charge', 'absolute_time', 'relative_time', 'shot_number', 'value', 'waveform', 'magnetic_field', name='IOTypeEnum'), primary_key=True)
    

    def __repr__(self):
        return f"NonLinearLens_inputs(NonLinearLens_name={self.NonLinearLens_name},inputs={self.inputs},)"



    


class NonLinearLensOutputs(Base):
    """
    None
    """
    __tablename__ = 'NonLinearLens_outputs'

    NonLinearLens_name = Column(Text(), ForeignKey('NonLinearLens.name'), primary_key=True)
    outputs = Column(Enum('current', 'voltage', 'phase', 'setpoint', 'on_off_state', 'open_closed_state', 'position', 'rotation', 'power', 'pressure', 'charge', 'absolute_time', 'relative_time', 'shot_number', 'value', 'waveform', 'magnetic_field', name='IOTypeEnum'), primary_key=True)
    

    def __repr__(self):
        return f"NonLinearLens_outputs(NonLinearLens_name={self.NonLinearLens_name},outputs={self.outputs},)"



    


class NonLinearLensUpstream(Base):
    """
    None
    """
    __tablename__ = 'NonLinearLens_upstream'

    NonLinearLens_name = Column(Text(), ForeignKey('NonLinearLens.name'), primary_key=True)
    upstream_name = Column(Text(), ForeignKey('AcceleratorElement.name'), primary_key=True)
    

    def __repr__(self):
        return f"NonLinearLens_upstream(NonLinearLens_name={self.NonLinearLens_name},upstream_name={self.upstream_name},)"



    


class NonLinearLensDownstream(Base):
    """
    None
    """
    __tablename__ = 'NonLinearLens_downstream'

    NonLinearLens_name = Column(Text(), ForeignKey('NonLinearLens.name'), primary_key=True)
    downstream_name = Column(Text(), ForeignKey('AcceleratorElement.name'), primary_key=True)
    

    def __repr__(self):
        return f"NonLinearLens_downstream(NonLinearLens_name={self.NonLinearLens_name},downstream_name={self.downstream_name},)"



    


class StandardElement(AcceleratorElement):
    """
    Accelerator element with control-system, electrical, manufacturer, simulation, and reference sub-models.
    """
    __tablename__ = 'StandardElement'

    name = Column(Text(), primary_key=True, nullable=False )
    hardware_class = Column(Enum('Magnet', 'Diagnostic', 'RF', 'Vacuum', 'Laser', 'Plasma', 'Feedback', 'Marker', 'Aperture', 'Stage', 'Lighting', 'Shutter', 'Wakefield', 'TwissMatch', 'Drift', 'Generic', 'Monitor', 'Simulation', 'Valve', 'LaserMirror', 'LaserEnergyMeter', 'LaserAttenuator', name='HardwareClassEnum'), nullable=False )
    hardware_type = Column(Text())
    hardware_model = Column(Text())
    machine_area = Column(Text())
    virtual_name = Column(Text())
    subelement = Column(Text())
    simulation_id = Column(Integer(), ForeignKey('SimulationElement.id'))
    simulation = relationship("SimulationElement", uselist=False, foreign_keys=[simulation_id])
    electrical_id = Column(Integer(), ForeignKey('ElectricalElement.id'))
    electrical = relationship("ElectricalElement", uselist=False, foreign_keys=[electrical_id])
    manufacturer_id = Column(Integer(), ForeignKey('ManufacturerElement.id'))
    manufacturer = relationship("ManufacturerElement", uselist=False, foreign_keys=[manufacturer_id])
    controls_id = Column(Integer(), ForeignKey('ControlsInformation.id'))
    controls = relationship("ControlsInformation", uselist=False, foreign_keys=[controls_id])
    reference_id = Column(Integer(), ForeignKey('ReferenceElement.id'))
    reference = relationship("ReferenceElement", uselist=False, foreign_keys=[reference_id])
    
    
    alias_rel = relationship( "StandardElementAlias" )
    alias = association_proxy("alias_rel", "alias",
                                  creator=lambda x_: StandardElementAlias(alias=x_))
    
    
    inputs_rel = relationship( "StandardElementInputs" )
    inputs = association_proxy("inputs_rel", "inputs",
                                  creator=lambda x_: StandardElementInputs(inputs=x_))
    
    
    outputs_rel = relationship( "StandardElementOutputs" )
    outputs = association_proxy("outputs_rel", "outputs",
                                  creator=lambda x_: StandardElementOutputs(outputs=x_))
    
    
    # ManyToMany
    upstream = relationship( "AcceleratorElement", secondary="StandardElement_upstream")
    
    
    # ManyToMany
    downstream = relationship( "AcceleratorElement", secondary="StandardElement_downstream")
    

    def __repr__(self):
        return f"StandardElement(name={self.name},hardware_class={self.hardware_class},hardware_type={self.hardware_type},hardware_model={self.hardware_model},machine_area={self.machine_area},virtual_name={self.virtual_name},subelement={self.subelement},simulation_id={self.simulation_id},electrical_id={self.electrical_id},manufacturer_id={self.manufacturer_id},controls_id={self.controls_id},reference_id={self.reference_id},)"



    
    # Using concrete inheritance: see https://docs.sqlalchemy.org/en/14/orm/inheritance.html
    __mapper_args__ = {
        'concrete': True
    }
    


class MagnetSimulationElement(SimulationElement):
    """
    Simulation attributes specific to magnets: integrator settings, fringe-field model, and radiation flags.
    """
    __tablename__ = 'MagnetSimulationElement'

    id = Column(Integer(), primary_key=True, autoincrement=True , nullable=False )
    n_kicks = Column(Integer())
    field_amplitude = Column(Float())
    n_slices = Column(Integer())
    smooth = Column(Integer())
    edge_field_integral = Column(Float())
    edge1_effects = Column(Boolean())
    edge2_effects = Column(Boolean())
    sr_enable = Column(Boolean())
    isr_enable = Column(Boolean())
    csr_enable = Column(Boolean())
    csr_bins = Column(Integer())
    integration_order = Column(Integer())
    nonlinear = Column(Boolean())
    smoothing_half_width = Column(Integer())
    edge_order = Column(Integer())
    deltaL = Column(Float())
    smooth_points = Column(Float())
    field_definition = Column(Text())
    wakefield_definition = Column(Text())
    wakefield_enable = Column(Boolean())
    field_reference_position = Column(Text())
    scale_field = Column(Float())
    

    def __repr__(self):
        return f"MagnetSimulationElement(id={self.id},n_kicks={self.n_kicks},field_amplitude={self.field_amplitude},n_slices={self.n_slices},smooth={self.smooth},edge_field_integral={self.edge_field_integral},edge1_effects={self.edge1_effects},edge2_effects={self.edge2_effects},sr_enable={self.sr_enable},isr_enable={self.isr_enable},csr_enable={self.csr_enable},csr_bins={self.csr_bins},integration_order={self.integration_order},nonlinear={self.nonlinear},smoothing_half_width={self.smoothing_half_width},edge_order={self.edge_order},deltaL={self.deltaL},smooth_points={self.smooth_points},field_definition={self.field_definition},wakefield_definition={self.wakefield_definition},wakefield_enable={self.wakefield_enable},field_reference_position={self.field_reference_position},scale_field={self.scale_field},)"



    
    # Using concrete inheritance: see https://docs.sqlalchemy.org/en/14/orm/inheritance.html
    __mapper_args__ = {
        'concrete': True
    }
    


class RFCavitySimulationElement(SimulationElement):
    """
    Simulation attributes for RF cavity elements.
    """
    __tablename__ = 'RFCavitySimulationElement'

    id = Column(Integer(), primary_key=True, autoincrement=True , nullable=False )
    t_column = Column(Text())
    z_column = Column(Text())
    wx_column = Column(Text())
    wy_column = Column(Text())
    wz_column = Column(Text())
    n_kicks = Column(Integer())
    lsc_bins = Column(Integer())
    change_p0 = Column(Integer())
    end1_focus = Column(Integer())
    end2_focus = Column(Integer())
    body_focus_model = Column(Text())
    current_bins = Column(Integer())
    interpolate_current_bins = Column(Integer())
    smooth_current_bins = Column(Integer())
    smooth = Column(Integer())
    ez_peak = Column(Float())
    field_file_name = Column(Text())
    wakefile = Column(Text())
    zwakefile = Column(Text())
    trwakefile = Column(Text())
    field_amplitude = Column(Float(), nullable=False )
    field_definition = Column(Text())
    wakefield_definition = Column(Text())
    wakefield_enable = Column(Boolean())
    field_reference_position = Column(Text())
    scale_field = Column(Float())
    

    def __repr__(self):
        return f"RFCavitySimulationElement(id={self.id},t_column={self.t_column},z_column={self.z_column},wx_column={self.wx_column},wy_column={self.wy_column},wz_column={self.wz_column},n_kicks={self.n_kicks},lsc_bins={self.lsc_bins},change_p0={self.change_p0},end1_focus={self.end1_focus},end2_focus={self.end2_focus},body_focus_model={self.body_focus_model},current_bins={self.current_bins},interpolate_current_bins={self.interpolate_current_bins},smooth_current_bins={self.smooth_current_bins},smooth={self.smooth},ez_peak={self.ez_peak},field_file_name={self.field_file_name},wakefile={self.wakefile},zwakefile={self.zwakefile},trwakefile={self.trwakefile},field_amplitude={self.field_amplitude},field_definition={self.field_definition},wakefield_definition={self.wakefield_definition},wakefield_enable={self.wakefield_enable},field_reference_position={self.field_reference_position},scale_field={self.scale_field},)"



    
    # Using concrete inheritance: see https://docs.sqlalchemy.org/en/14/orm/inheritance.html
    __mapper_args__ = {
        'concrete': True
    }
    


class WakefieldSimulationElement(SimulationElement):
    """
    Simulation attributes for passive wakefield structures.
    """
    __tablename__ = 'WakefieldSimulationElement'

    id = Column(Integer(), primary_key=True, autoincrement=True , nullable=False )
    t_column = Column(Text())
    z_column = Column(Text())
    wx_column = Column(Text())
    wy_column = Column(Text())
    wz_column = Column(Text())
    allow_long_beam = Column(Boolean())
    bunched_beam = Column(Boolean())
    change_momentum = Column(Boolean())
    factor = Column(Float())
    interpolate = Column(Boolean())
    scale_kick = Column(Float())
    scale_field_ex = Column(Float())
    scale_field_ey = Column(Float())
    scale_field_ez = Column(Float())
    scale_field_hx = Column(Float())
    scale_field_hy = Column(Float())
    scale_field_hz = Column(Float())
    equal_grid = Column(Float())
    interpolation_method = Column(Integer())
    smooth = Column(Float())
    subbins = Column(Integer())
    field_definition = Column(Text())
    wakefield_definition = Column(Text())
    wakefield_enable = Column(Boolean())
    field_reference_position = Column(Text())
    scale_field = Column(Float())
    

    def __repr__(self):
        return f"WakefieldSimulationElement(id={self.id},t_column={self.t_column},z_column={self.z_column},wx_column={self.wx_column},wy_column={self.wy_column},wz_column={self.wz_column},allow_long_beam={self.allow_long_beam},bunched_beam={self.bunched_beam},change_momentum={self.change_momentum},factor={self.factor},interpolate={self.interpolate},scale_kick={self.scale_kick},scale_field_ex={self.scale_field_ex},scale_field_ey={self.scale_field_ey},scale_field_ez={self.scale_field_ez},scale_field_hx={self.scale_field_hx},scale_field_hy={self.scale_field_hy},scale_field_hz={self.scale_field_hz},equal_grid={self.equal_grid},interpolation_method={self.interpolation_method},smooth={self.smooth},subbins={self.subbins},field_definition={self.field_definition},wakefield_definition={self.wakefield_definition},wakefield_enable={self.wakefield_enable},field_reference_position={self.field_reference_position},scale_field={self.scale_field},)"



    
    # Using concrete inheritance: see https://docs.sqlalchemy.org/en/14/orm/inheritance.html
    __mapper_args__ = {
        'concrete': True
    }
    


class DriftSimulationElement(SimulationElement):
    """
    Simulation attributes for field-free drift sections.
    """
    __tablename__ = 'DriftSimulationElement'

    id = Column(Integer(), primary_key=True, autoincrement=True , nullable=False )
    lsc_bins = Column(Integer())
    lsc_interpolate = Column(Integer())
    csr_enable = Column(Boolean())
    lsc_enable = Column(Boolean())
    use_stupakov = Column(Integer())
    csrdz = Column(Float())
    lsc_high_frequency_cutoff_start = Column(Float())
    lsc_high_frequency_cutoff_end = Column(Float())
    lsc_low_frequency_cutoff_start = Column(Float())
    lsc_low_frequency_cutoff_end = Column(Float())
    field_definition = Column(Text())
    wakefield_definition = Column(Text())
    wakefield_enable = Column(Boolean())
    field_reference_position = Column(Text())
    scale_field = Column(Float())
    

    def __repr__(self):
        return f"DriftSimulationElement(id={self.id},lsc_bins={self.lsc_bins},lsc_interpolate={self.lsc_interpolate},csr_enable={self.csr_enable},lsc_enable={self.lsc_enable},use_stupakov={self.use_stupakov},csrdz={self.csrdz},lsc_high_frequency_cutoff_start={self.lsc_high_frequency_cutoff_start},lsc_high_frequency_cutoff_end={self.lsc_high_frequency_cutoff_end},lsc_low_frequency_cutoff_start={self.lsc_low_frequency_cutoff_start},lsc_low_frequency_cutoff_end={self.lsc_low_frequency_cutoff_end},field_definition={self.field_definition},wakefield_definition={self.wakefield_definition},wakefield_enable={self.wakefield_enable},field_reference_position={self.field_reference_position},scale_field={self.scale_field},)"



    
    # Using concrete inheritance: see https://docs.sqlalchemy.org/en/14/orm/inheritance.html
    __mapper_args__ = {
        'concrete': True
    }
    


class DiagnosticSimulationElement(SimulationElement):
    """
    Simulation attributes for beam-diagnostic elements.
    """
    __tablename__ = 'DiagnosticSimulationElement'

    id = Column(Integer(), primary_key=True, autoincrement=True , nullable=False )
    output_filename = Column(Text())
    field_definition = Column(Text())
    wakefield_definition = Column(Text())
    wakefield_enable = Column(Boolean())
    field_reference_position = Column(Text())
    scale_field = Column(Float())
    

    def __repr__(self):
        return f"DiagnosticSimulationElement(id={self.id},output_filename={self.output_filename},field_definition={self.field_definition},wakefield_definition={self.wakefield_definition},wakefield_enable={self.wakefield_enable},field_reference_position={self.field_reference_position},scale_field={self.scale_field},)"



    
    # Using concrete inheritance: see https://docs.sqlalchemy.org/en/14/orm/inheritance.html
    __mapper_args__ = {
        'concrete': True
    }
    


class PlasmaSimulationElement(SimulationElement):
    """
    Simulation attributes for plasma-accelerator stages.
    """
    __tablename__ = 'PlasmaSimulationElement'

    id = Column(Integer(), primary_key=True, autoincrement=True , nullable=False )
    wakefield_model = Column(Text())
    bunch_pusher = Column(Text())
    dt_bunch = Column(Text())
    n_out = Column(Integer())
    min_longitudinal_position = Column(Float())
    max_longitudinal_position = Column(Float())
    n_longitudinal = Column(Integer())
    n_radial = Column(Integer())
    plasma_particles_per_cell = Column(Integer())
    r_max = Column(Float())
    r_max_plasma = Column(Float())
    dz_fields = Column(Float())
    plasma_pusher = Column(Text())
    field_definition = Column(Text())
    wakefield_definition = Column(Text())
    wakefield_enable = Column(Boolean())
    field_reference_position = Column(Text())
    scale_field = Column(Float())
    

    def __repr__(self):
        return f"PlasmaSimulationElement(id={self.id},wakefield_model={self.wakefield_model},bunch_pusher={self.bunch_pusher},dt_bunch={self.dt_bunch},n_out={self.n_out},min_longitudinal_position={self.min_longitudinal_position},max_longitudinal_position={self.max_longitudinal_position},n_longitudinal={self.n_longitudinal},n_radial={self.n_radial},plasma_particles_per_cell={self.plasma_particles_per_cell},r_max={self.r_max},r_max_plasma={self.r_max_plasma},dz_fields={self.dz_fields},plasma_pusher={self.plasma_pusher},field_definition={self.field_definition},wakefield_definition={self.wakefield_definition},wakefield_enable={self.wakefield_enable},field_reference_position={self.field_reference_position},scale_field={self.scale_field},)"



    
    # Using concrete inheritance: see https://docs.sqlalchemy.org/en/14/orm/inheritance.html
    __mapper_args__ = {
        'concrete': True
    }
    


class TwissMatchSimulationElement(SimulationElement):
    """
    Simulation attributes for Twiss-matching points.
    """
    __tablename__ = 'TwissMatchSimulationElement'

    id = Column(Integer(), primary_key=True, autoincrement=True , nullable=False )
    beta_x = Column(Float())
    beta_y = Column(Float())
    alpha_x = Column(Float())
    alpha_y = Column(Float())
    eta_x = Column(Float())
    eta_y = Column(Float())
    eta_xp = Column(Float())
    eta_yp = Column(Float())
    from_beam = Column(Boolean())
    field_definition = Column(Text())
    wakefield_definition = Column(Text())
    wakefield_enable = Column(Boolean())
    field_reference_position = Column(Text())
    scale_field = Column(Float())
    

    def __repr__(self):
        return f"TwissMatchSimulationElement(id={self.id},beta_x={self.beta_x},beta_y={self.beta_y},alpha_x={self.alpha_x},alpha_y={self.alpha_y},eta_x={self.eta_x},eta_y={self.eta_y},eta_xp={self.eta_xp},eta_yp={self.eta_yp},from_beam={self.from_beam},field_definition={self.field_definition},wakefield_definition={self.wakefield_definition},wakefield_enable={self.wakefield_enable},field_reference_position={self.field_reference_position},scale_field={self.scale_field},)"



    
    # Using concrete inheritance: see https://docs.sqlalchemy.org/en/14/orm/inheritance.html
    __mapper_args__ = {
        'concrete': True
    }
    


class MatrixTransformSimulationElement(SimulationElement):
    """
    Zero-, first-, and second-order transfer-map coefficients for a matrix transform element. Each coefficient collection accepts the dense form or the named coefficient mapping understood by the Python model.
    """
    __tablename__ = 'MatrixTransformSimulationElement'

    id = Column(Integer(), primary_key=True, autoincrement=True , nullable=False )
    apply = Column(Boolean())
    field_definition = Column(Text())
    wakefield_definition = Column(Text())
    wakefield_enable = Column(Boolean())
    field_reference_position = Column(Text())
    scale_field = Column(Float())
    c_matrix_id = Column(Integer(), ForeignKey('MatrixValue.id'))
    c_matrix = relationship("MatrixValue", uselist=False, foreign_keys=[c_matrix_id])
    r_matrix_id = Column(Integer(), ForeignKey('MatrixValue.id'))
    r_matrix = relationship("MatrixValue", uselist=False, foreign_keys=[r_matrix_id])
    t_matrix_id = Column(Integer(), ForeignKey('MatrixValue.id'))
    t_matrix = relationship("MatrixValue", uselist=False, foreign_keys=[t_matrix_id])
    

    def __repr__(self):
        return f"MatrixTransformSimulationElement(id={self.id},apply={self.apply},field_definition={self.field_definition},wakefield_definition={self.wakefield_definition},wakefield_enable={self.wakefield_enable},field_reference_position={self.field_reference_position},scale_field={self.scale_field},c_matrix_id={self.c_matrix_id},r_matrix_id={self.r_matrix_id},t_matrix_id={self.t_matrix_id},)"



    
    # Using concrete inheritance: see https://docs.sqlalchemy.org/en/14/orm/inheritance.html
    __mapper_args__ = {
        'concrete': True
    }
    


class ElectrostaticSeparatorSimulationElement(SimulationElement):
    """
    Simulation attributes for a static electrostatic separator.
    """
    __tablename__ = 'ElectrostaticSeparatorSimulationElement'

    id = Column(Integer(), primary_key=True, autoincrement=True , nullable=False )
    horizontal_field = Column(Float())
    vertical_field = Column(Float())
    tilt = Column(Float())
    field_definition = Column(Text())
    wakefield_definition = Column(Text())
    wakefield_enable = Column(Boolean())
    field_reference_position = Column(Text())
    scale_field = Column(Float())
    

    def __repr__(self):
        return f"ElectrostaticSeparatorSimulationElement(id={self.id},horizontal_field={self.horizontal_field},vertical_field={self.vertical_field},tilt={self.tilt},field_definition={self.field_definition},wakefield_definition={self.wakefield_definition},wakefield_enable={self.wakefield_enable},field_reference_position={self.field_reference_position},scale_field={self.scale_field},)"



    
    # Using concrete inheritance: see https://docs.sqlalchemy.org/en/14/orm/inheritance.html
    __mapper_args__ = {
        'concrete': True
    }
    


class ACDipoleSimulationElement(SimulationElement):
    """
    Simulation attributes for an AC dipole / tune exciter.
    """
    __tablename__ = 'ACDipoleSimulationElement'

    id = Column(Integer(), primary_key=True, autoincrement=True , nullable=False )
    field_amplitude = Column(Float())
    frequency = Column(Float())
    phase = Column(Float())
    field_definition = Column(Text())
    wakefield_definition = Column(Text())
    wakefield_enable = Column(Boolean())
    field_reference_position = Column(Text())
    scale_field = Column(Float())
    
    
    ramp_rel = relationship( "ACDipoleSimulationElementRamp" )
    ramp = association_proxy("ramp_rel", "ramp",
                                  creator=lambda x_: ACDipoleSimulationElementRamp(ramp=x_))
    

    def __repr__(self):
        return f"ACDipoleSimulationElement(id={self.id},field_amplitude={self.field_amplitude},frequency={self.frequency},phase={self.phase},field_definition={self.field_definition},wakefield_definition={self.wakefield_definition},wakefield_enable={self.wakefield_enable},field_reference_position={self.field_reference_position},scale_field={self.scale_field},)"



    
    # Using concrete inheritance: see https://docs.sqlalchemy.org/en/14/orm/inheritance.html
    __mapper_args__ = {
        'concrete': True
    }
    


class WireSimulationElement(SimulationElement):
    """
    Simulation attributes for a compensating wire.
    """
    __tablename__ = 'WireSimulationElement'

    id = Column(Integer(), primary_key=True, autoincrement=True , nullable=False )
    current = Column(Float())
    interaction_length = Column(Float())
    horizontal_offset = Column(Float())
    vertical_offset = Column(Float())
    field_definition = Column(Text())
    wakefield_definition = Column(Text())
    wakefield_enable = Column(Boolean())
    field_reference_position = Column(Text())
    scale_field = Column(Float())
    

    def __repr__(self):
        return f"WireSimulationElement(id={self.id},current={self.current},interaction_length={self.interaction_length},horizontal_offset={self.horizontal_offset},vertical_offset={self.vertical_offset},field_definition={self.field_definition},wakefield_definition={self.wakefield_definition},wakefield_enable={self.wakefield_enable},field_reference_position={self.field_reference_position},scale_field={self.scale_field},)"



    
    # Using concrete inheritance: see https://docs.sqlalchemy.org/en/14/orm/inheritance.html
    __mapper_args__ = {
        'concrete': True
    }
    


class BeamBeamSimulationElement(SimulationElement):
    """
    Simulation attributes for a weak-strong beam-beam interaction.
    """
    __tablename__ = 'BeamBeamSimulationElement'

    id = Column(Integer(), primary_key=True, autoincrement=True , nullable=False )
    charge = Column(Float())
    n_particles = Column(Float())
    horizontal_offset = Column(Float())
    vertical_offset = Column(Float())
    horizontal_sigma = Column(Float())
    vertical_sigma = Column(Float())
    width = Column(Float())
    field_definition = Column(Text())
    wakefield_definition = Column(Text())
    wakefield_enable = Column(Boolean())
    field_reference_position = Column(Text())
    scale_field = Column(Float())
    

    def __repr__(self):
        return f"BeamBeamSimulationElement(id={self.id},charge={self.charge},n_particles={self.n_particles},horizontal_offset={self.horizontal_offset},vertical_offset={self.vertical_offset},horizontal_sigma={self.horizontal_sigma},vertical_sigma={self.vertical_sigma},width={self.width},field_definition={self.field_definition},wakefield_definition={self.wakefield_definition},wakefield_enable={self.wakefield_enable},field_reference_position={self.field_reference_position},scale_field={self.scale_field},)"



    
    # Using concrete inheritance: see https://docs.sqlalchemy.org/en/14/orm/inheritance.html
    __mapper_args__ = {
        'concrete': True
    }
    


class RFMultipoleSimulationElement(SimulationElement):
    """
    Simulation attributes for a thin RF multipole kick.
    """
    __tablename__ = 'RFMultipoleSimulationElement'

    id = Column(Integer(), primary_key=True, autoincrement=True , nullable=False )
    frequency = Column(Float())
    phase = Column(Float())
    field_amplitude = Column(Float())
    field_definition = Column(Text())
    wakefield_definition = Column(Text())
    wakefield_enable = Column(Boolean())
    field_reference_position = Column(Text())
    scale_field = Column(Float())
    
    
    knl_rel = relationship( "RFMultipoleSimulationElementKnl" )
    knl = association_proxy("knl_rel", "knl",
                                  creator=lambda x_: RFMultipoleSimulationElementKnl(knl=x_))
    
    
    ksl_rel = relationship( "RFMultipoleSimulationElementKsl" )
    ksl = association_proxy("ksl_rel", "ksl",
                                  creator=lambda x_: RFMultipoleSimulationElementKsl(ksl=x_))
    
    
    pnl_rel = relationship( "RFMultipoleSimulationElementPnl" )
    pnl = association_proxy("pnl_rel", "pnl",
                                  creator=lambda x_: RFMultipoleSimulationElementPnl(pnl=x_))
    
    
    psl_rel = relationship( "RFMultipoleSimulationElementPsl" )
    psl = association_proxy("psl_rel", "psl",
                                  creator=lambda x_: RFMultipoleSimulationElementPsl(psl=x_))
    

    def __repr__(self):
        return f"RFMultipoleSimulationElement(id={self.id},frequency={self.frequency},phase={self.phase},field_amplitude={self.field_amplitude},field_definition={self.field_definition},wakefield_definition={self.wakefield_definition},wakefield_enable={self.wakefield_enable},field_reference_position={self.field_reference_position},scale_field={self.scale_field},)"



    
    # Using concrete inheritance: see https://docs.sqlalchemy.org/en/14/orm/inheritance.html
    __mapper_args__ = {
        'concrete': True
    }
    


class PIDWeightRange(PIDPhaseRange):
    """
    Numeric min/max range for PID phase weighting.
    """
    __tablename__ = 'PIDWeightRange'

    id = Column(Integer(), primary_key=True, autoincrement=True , nullable=False )
    min = Column(Float())
    max = Column(Float())
    

    def __repr__(self):
        return f"PIDWeightRange(id={self.id},min={self.min},max={self.max},)"



    
    # Using concrete inheritance: see https://docs.sqlalchemy.org/en/14/orm/inheritance.html
    __mapper_args__ = {
        'concrete': True
    }
    


class BPMDiagnosticElement(DiagnosticElement):
    """
    Beam-position monitor (BPM) diagnostic data.
    """
    __tablename__ = 'BPMDiagnosticElement'

    id = Column(Integer(), primary_key=True, autoincrement=True , nullable=False )
    type = Column(Text())
    

    def __repr__(self):
        return f"BPMDiagnosticElement(id={self.id},type={self.type},)"



    
    # Using concrete inheritance: see https://docs.sqlalchemy.org/en/14/orm/inheritance.html
    __mapper_args__ = {
        'concrete': True
    }
    


class BAMDiagnosticElement(DiagnosticElement):
    """
    Beam-arrival monitor (BAM) diagnostic data.
    """
    __tablename__ = 'BAMDiagnosticElement'

    id = Column(Integer(), primary_key=True, autoincrement=True , nullable=False )
    type = Column(Text())
    

    def __repr__(self):
        return f"BAMDiagnosticElement(id={self.id},type={self.type},)"



    
    # Using concrete inheritance: see https://docs.sqlalchemy.org/en/14/orm/inheritance.html
    __mapper_args__ = {
        'concrete': True
    }
    


class PhotonIntensityMonitorDiagnostic(DiagnosticElement):
    """
    Photon intensity monitor diagnostic data.
    """
    __tablename__ = 'PhotonIntensityMonitorDiagnostic'

    id = Column(Integer(), primary_key=True, autoincrement=True , nullable=False )
    type = Column(Text())
    intensity = Column(Float())
    

    def __repr__(self):
        return f"PhotonIntensityMonitorDiagnostic(id={self.id},type={self.type},intensity={self.intensity},)"



    
    # Using concrete inheritance: see https://docs.sqlalchemy.org/en/14/orm/inheritance.html
    __mapper_args__ = {
        'concrete': True
    }
    


class BLMDiagnosticElement(DiagnosticElement):
    """
    Bunch-length monitor (BLM) diagnostic data.
    """
    __tablename__ = 'BLMDiagnosticElement'

    id = Column(Integer(), primary_key=True, autoincrement=True , nullable=False )
    type = Column(Text())
    

    def __repr__(self):
        return f"BLMDiagnosticElement(id={self.id},type={self.type},)"



    
    # Using concrete inheritance: see https://docs.sqlalchemy.org/en/14/orm/inheritance.html
    __mapper_args__ = {
        'concrete': True
    }
    


class ScreenDiagnosticElement(DiagnosticElement):
    """
    Scintillator or OTR screen diagnostic data.
    """
    __tablename__ = 'ScreenDiagnosticElement'

    id = Column(Integer(), primary_key=True, autoincrement=True , nullable=False )
    type = Column(Text())
    has_camera = Column(Boolean())
    camera_name = Column(Text())
    
    
    devices_rel = relationship( "ScreenDiagnosticElementDevices" )
    devices = association_proxy("devices_rel", "devices",
                                  creator=lambda x_: ScreenDiagnosticElementDevices(devices=x_))
    

    def __repr__(self):
        return f"ScreenDiagnosticElement(id={self.id},type={self.type},has_camera={self.has_camera},camera_name={self.camera_name},)"



    
    # Using concrete inheritance: see https://docs.sqlalchemy.org/en/14/orm/inheritance.html
    __mapper_args__ = {
        'concrete': True
    }
    


class ChargeDiagnosticElement(DiagnosticElement):
    """
    Charge-measurement diagnostic data (base for ICT, FCM, WCM).
    """
    __tablename__ = 'ChargeDiagnosticElement'

    id = Column(Integer(), primary_key=True, autoincrement=True , nullable=False )
    type = Column(Text())
    

    def __repr__(self):
        return f"ChargeDiagnosticElement(id={self.id},type={self.type},)"



    
    # Using concrete inheritance: see https://docs.sqlalchemy.org/en/14/orm/inheritance.html
    __mapper_args__ = {
        'concrete': True
    }
    


class CameraDiagnosticElement(DiagnosticElement):
    """
    Camera diagnostic data, including sensor parameters, analysis mask, and pixel-to-mm scale factors.
    """
    __tablename__ = 'CameraDiagnosticElement'

    id = Column(Integer(), primary_key=True, autoincrement=True , nullable=False )
    type = Column(Text())
    x_pixels = Column(Integer())
    y_pixels = Column(Integer())
    rotation = Column(Float())
    flipped_horizontally = Column(Boolean())
    flipped_vertically = Column(Boolean())
    screen_name = Column(Text())
    has_led = Column(Boolean())
    pixel_results_indices_id = Column(Integer(), ForeignKey('CameraPixelResultsIndices.id'))
    pixel_results_indices = relationship("CameraPixelResultsIndices", uselist=False, foreign_keys=[pixel_results_indices_id])
    pixel_results_names_id = Column(Integer(), ForeignKey('CameraPixelResultsNames.id'))
    pixel_results_names = relationship("CameraPixelResultsNames", uselist=False, foreign_keys=[pixel_results_names_id])
    mask_id = Column(Integer(), ForeignKey('CameraMask.id'))
    mask = relationship("CameraMask", uselist=False, foreign_keys=[mask_id])
    sensor_id = Column(Integer(), ForeignKey('CameraSensor.id'))
    sensor = relationship("CameraSensor", uselist=False, foreign_keys=[sensor_id])
    

    def __repr__(self):
        return f"CameraDiagnosticElement(id={self.id},type={self.type},x_pixels={self.x_pixels},y_pixels={self.y_pixels},rotation={self.rotation},flipped_horizontally={self.flipped_horizontally},flipped_vertically={self.flipped_vertically},screen_name={self.screen_name},has_led={self.has_led},pixel_results_indices_id={self.pixel_results_indices_id},pixel_results_names_id={self.pixel_results_names_id},mask_id={self.mask_id},sensor_id={self.sensor_id},)"



    
    # Using concrete inheritance: see https://docs.sqlalchemy.org/en/14/orm/inheritance.html
    __mapper_args__ = {
        'concrete': True
    }
    


class DipoleMagnet(MagneticElement):
    """
    None
    """
    __tablename__ = 'Dipole_Magnet'

    id = Column(Integer(), primary_key=True, autoincrement=True , nullable=False )
    order = Column(Integer())
    skew = Column(Boolean())
    length = Column(Float())
    settle_time = Column(Float())
    entrance_edge_angle = Column(Text())
    exit_edge_angle = Column(Text())
    gap = Column(Float())
    bore = Column(Float())
    plane = Column(Enum('Horizontal', 'Vertical', 'Combined', name='BendingPlaneEnum'))
    width = Column(Float())
    tilt = Column(Float())
    edge_field_integral = Column(Float())
    fringe_field_coefficient = Column(Float())
    gradient = Column(Float())
    angle = Column(Float())
    multipoles_id = Column(Integer(), ForeignKey('Multipoles.id'))
    multipoles = relationship("Multipoles", uselist=False, foreign_keys=[multipoles_id])
    systematic_multipoles_id = Column(Integer(), ForeignKey('Multipoles.id'))
    systematic_multipoles = relationship("Multipoles", uselist=False, foreign_keys=[systematic_multipoles_id])
    random_multipoles_id = Column(Integer(), ForeignKey('Multipoles.id'))
    random_multipoles = relationship("Multipoles", uselist=False, foreign_keys=[random_multipoles_id])
    field_integral_coefficients_id = Column(Integer(), ForeignKey('FieldIntegral.id'))
    field_integral_coefficients = relationship("FieldIntegral", uselist=False, foreign_keys=[field_integral_coefficients_id])
    linear_saturation_coefficients_id = Column(Integer(), ForeignKey('LinearSaturationFit.id'))
    linear_saturation_coefficients = relationship("LinearSaturationFit", uselist=False, foreign_keys=[linear_saturation_coefficients_id])
    

    def __repr__(self):
        return f"Dipole_Magnet(id={self.id},order={self.order},skew={self.skew},length={self.length},settle_time={self.settle_time},entrance_edge_angle={self.entrance_edge_angle},exit_edge_angle={self.exit_edge_angle},gap={self.gap},bore={self.bore},plane={self.plane},width={self.width},tilt={self.tilt},edge_field_integral={self.edge_field_integral},fringe_field_coefficient={self.fringe_field_coefficient},gradient={self.gradient},angle={self.angle},multipoles_id={self.multipoles_id},systematic_multipoles_id={self.systematic_multipoles_id},random_multipoles_id={self.random_multipoles_id},field_integral_coefficients_id={self.field_integral_coefficients_id},linear_saturation_coefficients_id={self.linear_saturation_coefficients_id},)"



    
    # Using concrete inheritance: see https://docs.sqlalchemy.org/en/14/orm/inheritance.html
    __mapper_args__ = {
        'concrete': True
    }
    


class QuadrupoleMagnet(MagneticElement):
    """
    None
    """
    __tablename__ = 'Quadrupole_Magnet'

    id = Column(Integer(), primary_key=True, autoincrement=True , nullable=False )
    order = Column(Integer())
    skew = Column(Boolean())
    length = Column(Float())
    settle_time = Column(Float())
    entrance_edge_angle = Column(Text())
    exit_edge_angle = Column(Text())
    gap = Column(Float())
    bore = Column(Float())
    plane = Column(Enum('Horizontal', 'Vertical', 'Combined', name='BendingPlaneEnum'))
    width = Column(Float())
    tilt = Column(Float())
    edge_field_integral = Column(Float())
    fringe_field_coefficient = Column(Float())
    gradient = Column(Float())
    angle = Column(Float())
    multipoles_id = Column(Integer(), ForeignKey('Multipoles.id'))
    multipoles = relationship("Multipoles", uselist=False, foreign_keys=[multipoles_id])
    systematic_multipoles_id = Column(Integer(), ForeignKey('Multipoles.id'))
    systematic_multipoles = relationship("Multipoles", uselist=False, foreign_keys=[systematic_multipoles_id])
    random_multipoles_id = Column(Integer(), ForeignKey('Multipoles.id'))
    random_multipoles = relationship("Multipoles", uselist=False, foreign_keys=[random_multipoles_id])
    field_integral_coefficients_id = Column(Integer(), ForeignKey('FieldIntegral.id'))
    field_integral_coefficients = relationship("FieldIntegral", uselist=False, foreign_keys=[field_integral_coefficients_id])
    linear_saturation_coefficients_id = Column(Integer(), ForeignKey('LinearSaturationFit.id'))
    linear_saturation_coefficients = relationship("LinearSaturationFit", uselist=False, foreign_keys=[linear_saturation_coefficients_id])
    

    def __repr__(self):
        return f"Quadrupole_Magnet(id={self.id},order={self.order},skew={self.skew},length={self.length},settle_time={self.settle_time},entrance_edge_angle={self.entrance_edge_angle},exit_edge_angle={self.exit_edge_angle},gap={self.gap},bore={self.bore},plane={self.plane},width={self.width},tilt={self.tilt},edge_field_integral={self.edge_field_integral},fringe_field_coefficient={self.fringe_field_coefficient},gradient={self.gradient},angle={self.angle},multipoles_id={self.multipoles_id},systematic_multipoles_id={self.systematic_multipoles_id},random_multipoles_id={self.random_multipoles_id},field_integral_coefficients_id={self.field_integral_coefficients_id},linear_saturation_coefficients_id={self.linear_saturation_coefficients_id},)"



    
    # Using concrete inheritance: see https://docs.sqlalchemy.org/en/14/orm/inheritance.html
    __mapper_args__ = {
        'concrete': True
    }
    


class SextupoleMagnet(MagneticElement):
    """
    Sextupole magnet field, principal multipole order 2.
    """
    __tablename__ = 'Sextupole_Magnet'

    id = Column(Integer(), primary_key=True, autoincrement=True , nullable=False )
    order = Column(Integer())
    skew = Column(Boolean())
    length = Column(Float())
    settle_time = Column(Float())
    entrance_edge_angle = Column(Text())
    exit_edge_angle = Column(Text())
    gap = Column(Float())
    bore = Column(Float())
    plane = Column(Enum('Horizontal', 'Vertical', 'Combined', name='BendingPlaneEnum'))
    width = Column(Float())
    tilt = Column(Float())
    edge_field_integral = Column(Float())
    fringe_field_coefficient = Column(Float())
    gradient = Column(Float())
    angle = Column(Float())
    multipoles_id = Column(Integer(), ForeignKey('Multipoles.id'))
    multipoles = relationship("Multipoles", uselist=False, foreign_keys=[multipoles_id])
    systematic_multipoles_id = Column(Integer(), ForeignKey('Multipoles.id'))
    systematic_multipoles = relationship("Multipoles", uselist=False, foreign_keys=[systematic_multipoles_id])
    random_multipoles_id = Column(Integer(), ForeignKey('Multipoles.id'))
    random_multipoles = relationship("Multipoles", uselist=False, foreign_keys=[random_multipoles_id])
    field_integral_coefficients_id = Column(Integer(), ForeignKey('FieldIntegral.id'))
    field_integral_coefficients = relationship("FieldIntegral", uselist=False, foreign_keys=[field_integral_coefficients_id])
    linear_saturation_coefficients_id = Column(Integer(), ForeignKey('LinearSaturationFit.id'))
    linear_saturation_coefficients = relationship("LinearSaturationFit", uselist=False, foreign_keys=[linear_saturation_coefficients_id])
    

    def __repr__(self):
        return f"Sextupole_Magnet(id={self.id},order={self.order},skew={self.skew},length={self.length},settle_time={self.settle_time},entrance_edge_angle={self.entrance_edge_angle},exit_edge_angle={self.exit_edge_angle},gap={self.gap},bore={self.bore},plane={self.plane},width={self.width},tilt={self.tilt},edge_field_integral={self.edge_field_integral},fringe_field_coefficient={self.fringe_field_coefficient},gradient={self.gradient},angle={self.angle},multipoles_id={self.multipoles_id},systematic_multipoles_id={self.systematic_multipoles_id},random_multipoles_id={self.random_multipoles_id},field_integral_coefficients_id={self.field_integral_coefficients_id},linear_saturation_coefficients_id={self.linear_saturation_coefficients_id},)"



    
    # Using concrete inheritance: see https://docs.sqlalchemy.org/en/14/orm/inheritance.html
    __mapper_args__ = {
        'concrete': True
    }
    


class OctupoleMagnet(MagneticElement):
    """
    Octupole magnet field, principal multipole order 3.
    """
    __tablename__ = 'Octupole_Magnet'

    id = Column(Integer(), primary_key=True, autoincrement=True , nullable=False )
    order = Column(Integer())
    skew = Column(Boolean())
    length = Column(Float())
    settle_time = Column(Float())
    entrance_edge_angle = Column(Text())
    exit_edge_angle = Column(Text())
    gap = Column(Float())
    bore = Column(Float())
    plane = Column(Enum('Horizontal', 'Vertical', 'Combined', name='BendingPlaneEnum'))
    width = Column(Float())
    tilt = Column(Float())
    edge_field_integral = Column(Float())
    fringe_field_coefficient = Column(Float())
    gradient = Column(Float())
    angle = Column(Float())
    multipoles_id = Column(Integer(), ForeignKey('Multipoles.id'))
    multipoles = relationship("Multipoles", uselist=False, foreign_keys=[multipoles_id])
    systematic_multipoles_id = Column(Integer(), ForeignKey('Multipoles.id'))
    systematic_multipoles = relationship("Multipoles", uselist=False, foreign_keys=[systematic_multipoles_id])
    random_multipoles_id = Column(Integer(), ForeignKey('Multipoles.id'))
    random_multipoles = relationship("Multipoles", uselist=False, foreign_keys=[random_multipoles_id])
    field_integral_coefficients_id = Column(Integer(), ForeignKey('FieldIntegral.id'))
    field_integral_coefficients = relationship("FieldIntegral", uselist=False, foreign_keys=[field_integral_coefficients_id])
    linear_saturation_coefficients_id = Column(Integer(), ForeignKey('LinearSaturationFit.id'))
    linear_saturation_coefficients = relationship("LinearSaturationFit", uselist=False, foreign_keys=[linear_saturation_coefficients_id])
    

    def __repr__(self):
        return f"Octupole_Magnet(id={self.id},order={self.order},skew={self.skew},length={self.length},settle_time={self.settle_time},entrance_edge_angle={self.entrance_edge_angle},exit_edge_angle={self.exit_edge_angle},gap={self.gap},bore={self.bore},plane={self.plane},width={self.width},tilt={self.tilt},edge_field_integral={self.edge_field_integral},fringe_field_coefficient={self.fringe_field_coefficient},gradient={self.gradient},angle={self.angle},multipoles_id={self.multipoles_id},systematic_multipoles_id={self.systematic_multipoles_id},random_multipoles_id={self.random_multipoles_id},field_integral_coefficients_id={self.field_integral_coefficients_id},linear_saturation_coefficients_id={self.linear_saturation_coefficients_id},)"



    
    # Using concrete inheritance: see https://docs.sqlalchemy.org/en/14/orm/inheritance.html
    __mapper_args__ = {
        'concrete': True
    }
    


class Element(StandardElement):
    """
    Concrete schema counterpart of the Python ``Element`` wrapper class. Inherits standard element composition fields.
    """
    __tablename__ = 'Element'

    name = Column(Text(), primary_key=True, nullable=False )
    hardware_class = Column(Enum('Magnet', 'Diagnostic', 'RF', 'Vacuum', 'Laser', 'Plasma', 'Feedback', 'Marker', 'Aperture', 'Stage', 'Lighting', 'Shutter', 'Wakefield', 'TwissMatch', 'Drift', 'Generic', 'Monitor', 'Simulation', 'Valve', 'LaserMirror', 'LaserEnergyMeter', 'LaserAttenuator', name='HardwareClassEnum'), nullable=False )
    hardware_type = Column(Text())
    hardware_model = Column(Text())
    machine_area = Column(Text())
    virtual_name = Column(Text())
    subelement = Column(Text())
    simulation_id = Column(Integer(), ForeignKey('SimulationElement.id'))
    simulation = relationship("SimulationElement", uselist=False, foreign_keys=[simulation_id])
    electrical_id = Column(Integer(), ForeignKey('ElectricalElement.id'))
    electrical = relationship("ElectricalElement", uselist=False, foreign_keys=[electrical_id])
    manufacturer_id = Column(Integer(), ForeignKey('ManufacturerElement.id'))
    manufacturer = relationship("ManufacturerElement", uselist=False, foreign_keys=[manufacturer_id])
    controls_id = Column(Integer(), ForeignKey('ControlsInformation.id'))
    controls = relationship("ControlsInformation", uselist=False, foreign_keys=[controls_id])
    reference_id = Column(Integer(), ForeignKey('ReferenceElement.id'))
    reference = relationship("ReferenceElement", uselist=False, foreign_keys=[reference_id])
    
    
    alias_rel = relationship( "ElementAlias" )
    alias = association_proxy("alias_rel", "alias",
                                  creator=lambda x_: ElementAlias(alias=x_))
    
    
    inputs_rel = relationship( "ElementInputs" )
    inputs = association_proxy("inputs_rel", "inputs",
                                  creator=lambda x_: ElementInputs(inputs=x_))
    
    
    outputs_rel = relationship( "ElementOutputs" )
    outputs = association_proxy("outputs_rel", "outputs",
                                  creator=lambda x_: ElementOutputs(outputs=x_))
    
    
    # ManyToMany
    upstream = relationship( "AcceleratorElement", secondary="Element_upstream")
    
    
    # ManyToMany
    downstream = relationship( "AcceleratorElement", secondary="Element_downstream")
    

    def __repr__(self):
        return f"Element(name={self.name},hardware_class={self.hardware_class},hardware_type={self.hardware_type},hardware_model={self.hardware_model},machine_area={self.machine_area},virtual_name={self.virtual_name},subelement={self.subelement},simulation_id={self.simulation_id},electrical_id={self.electrical_id},manufacturer_id={self.manufacturer_id},controls_id={self.controls_id},reference_id={self.reference_id},)"



    
    # Using concrete inheritance: see https://docs.sqlalchemy.org/en/14/orm/inheritance.html
    __mapper_args__ = {
        'concrete': True
    }
    


class Lighting(StandardElement):
    """
    Experimental-hall lighting element.
    """
    __tablename__ = 'Lighting'

    name = Column(Text(), primary_key=True, nullable=False )
    hardware_class = Column(Enum('Magnet', 'Diagnostic', 'RF', 'Vacuum', 'Laser', 'Plasma', 'Feedback', 'Marker', 'Aperture', 'Stage', 'Lighting', 'Shutter', 'Wakefield', 'TwissMatch', 'Drift', 'Generic', 'Monitor', 'Simulation', 'Valve', 'LaserMirror', 'LaserEnergyMeter', 'LaserAttenuator', name='HardwareClassEnum'), nullable=False )
    hardware_type = Column(Text())
    hardware_model = Column(Text())
    machine_area = Column(Text())
    virtual_name = Column(Text())
    subelement = Column(Text())
    lights_id = Column(Integer(), ForeignKey('LightingElement.id'))
    lights = relationship("LightingElement", uselist=False, foreign_keys=[lights_id])
    simulation_id = Column(Integer(), ForeignKey('SimulationElement.id'))
    simulation = relationship("SimulationElement", uselist=False, foreign_keys=[simulation_id])
    electrical_id = Column(Integer(), ForeignKey('ElectricalElement.id'))
    electrical = relationship("ElectricalElement", uselist=False, foreign_keys=[electrical_id])
    manufacturer_id = Column(Integer(), ForeignKey('ManufacturerElement.id'))
    manufacturer = relationship("ManufacturerElement", uselist=False, foreign_keys=[manufacturer_id])
    controls_id = Column(Integer(), ForeignKey('ControlsInformation.id'))
    controls = relationship("ControlsInformation", uselist=False, foreign_keys=[controls_id])
    reference_id = Column(Integer(), ForeignKey('ReferenceElement.id'))
    reference = relationship("ReferenceElement", uselist=False, foreign_keys=[reference_id])
    
    
    alias_rel = relationship( "LightingAlias" )
    alias = association_proxy("alias_rel", "alias",
                                  creator=lambda x_: LightingAlias(alias=x_))
    
    
    inputs_rel = relationship( "LightingInputs" )
    inputs = association_proxy("inputs_rel", "inputs",
                                  creator=lambda x_: LightingInputs(inputs=x_))
    
    
    outputs_rel = relationship( "LightingOutputs" )
    outputs = association_proxy("outputs_rel", "outputs",
                                  creator=lambda x_: LightingOutputs(outputs=x_))
    
    
    # ManyToMany
    upstream = relationship( "AcceleratorElement", secondary="Lighting_upstream")
    
    
    # ManyToMany
    downstream = relationship( "AcceleratorElement", secondary="Lighting_downstream")
    

    def __repr__(self):
        return f"Lighting(name={self.name},hardware_class={self.hardware_class},hardware_type={self.hardware_type},hardware_model={self.hardware_model},machine_area={self.machine_area},virtual_name={self.virtual_name},subelement={self.subelement},lights_id={self.lights_id},simulation_id={self.simulation_id},electrical_id={self.electrical_id},manufacturer_id={self.manufacturer_id},controls_id={self.controls_id},reference_id={self.reference_id},)"



    
    # Using concrete inheritance: see https://docs.sqlalchemy.org/en/14/orm/inheritance.html
    __mapper_args__ = {
        'concrete': True
    }
    


class PowerSupply(StandardElement):
    """
    Generic power-supply unit providing control/setpoint-driven outputs (for example current/voltage) to other accelerator components.
    """
    __tablename__ = 'PowerSupply'

    name = Column(Text(), primary_key=True, nullable=False )
    hardware_class = Column(Enum('Magnet', 'Diagnostic', 'RF', 'Vacuum', 'Laser', 'Plasma', 'Feedback', 'Marker', 'Aperture', 'Stage', 'Lighting', 'Shutter', 'Wakefield', 'TwissMatch', 'Drift', 'Generic', 'Monitor', 'Simulation', 'Valve', 'LaserMirror', 'LaserEnergyMeter', 'LaserAttenuator', name='HardwareClassEnum'), nullable=False )
    hardware_type = Column(Text())
    hardware_model = Column(Text())
    machine_area = Column(Text())
    virtual_name = Column(Text())
    subelement = Column(Text())
    simulation_id = Column(Integer(), ForeignKey('SimulationElement.id'))
    simulation = relationship("SimulationElement", uselist=False, foreign_keys=[simulation_id])
    electrical_id = Column(Integer(), ForeignKey('ElectricalElement.id'))
    electrical = relationship("ElectricalElement", uselist=False, foreign_keys=[electrical_id])
    manufacturer_id = Column(Integer(), ForeignKey('ManufacturerElement.id'))
    manufacturer = relationship("ManufacturerElement", uselist=False, foreign_keys=[manufacturer_id])
    controls_id = Column(Integer(), ForeignKey('ControlsInformation.id'))
    controls = relationship("ControlsInformation", uselist=False, foreign_keys=[controls_id])
    reference_id = Column(Integer(), ForeignKey('ReferenceElement.id'))
    reference = relationship("ReferenceElement", uselist=False, foreign_keys=[reference_id])
    
    
    alias_rel = relationship( "PowerSupplyAlias" )
    alias = association_proxy("alias_rel", "alias",
                                  creator=lambda x_: PowerSupplyAlias(alias=x_))
    
    
    inputs_rel = relationship( "PowerSupplyInputs" )
    inputs = association_proxy("inputs_rel", "inputs",
                                  creator=lambda x_: PowerSupplyInputs(inputs=x_))
    
    
    outputs_rel = relationship( "PowerSupplyOutputs" )
    outputs = association_proxy("outputs_rel", "outputs",
                                  creator=lambda x_: PowerSupplyOutputs(outputs=x_))
    
    
    # ManyToMany
    upstream = relationship( "AcceleratorElement", secondary="PowerSupply_upstream")
    
    
    # ManyToMany
    downstream = relationship( "AcceleratorElement", secondary="PowerSupply_downstream")
    

    def __repr__(self):
        return f"PowerSupply(name={self.name},hardware_class={self.hardware_class},hardware_type={self.hardware_type},hardware_model={self.hardware_model},machine_area={self.machine_area},virtual_name={self.virtual_name},subelement={self.subelement},simulation_id={self.simulation_id},electrical_id={self.electrical_id},manufacturer_id={self.manufacturer_id},controls_id={self.controls_id},reference_id={self.reference_id},)"



    
    # Using concrete inheritance: see https://docs.sqlalchemy.org/en/14/orm/inheritance.html
    __mapper_args__ = {
        'concrete': True
    }
    


class LowLevelRF(StandardElement):
    """
    Low-level RF (LLRF) controller.
    """
    __tablename__ = 'LowLevelRF'

    name = Column(Text(), primary_key=True, nullable=False )
    hardware_class = Column(Enum('Magnet', 'Diagnostic', 'RF', 'Vacuum', 'Laser', 'Plasma', 'Feedback', 'Marker', 'Aperture', 'Stage', 'Lighting', 'Shutter', 'Wakefield', 'TwissMatch', 'Drift', 'Generic', 'Monitor', 'Simulation', 'Valve', 'LaserMirror', 'LaserEnergyMeter', 'LaserAttenuator', name='HardwareClassEnum'), nullable=False )
    hardware_type = Column(Text())
    hardware_model = Column(Text())
    machine_area = Column(Text())
    virtual_name = Column(Text())
    subelement = Column(Text())
    llrf_id = Column(Integer(), ForeignKey('LowLevelRFElement.id'))
    llrf = relationship("LowLevelRFElement", uselist=False, foreign_keys=[llrf_id])
    simulation_id = Column(Integer(), ForeignKey('SimulationElement.id'))
    simulation = relationship("SimulationElement", uselist=False, foreign_keys=[simulation_id])
    electrical_id = Column(Integer(), ForeignKey('ElectricalElement.id'))
    electrical = relationship("ElectricalElement", uselist=False, foreign_keys=[electrical_id])
    manufacturer_id = Column(Integer(), ForeignKey('ManufacturerElement.id'))
    manufacturer = relationship("ManufacturerElement", uselist=False, foreign_keys=[manufacturer_id])
    controls_id = Column(Integer(), ForeignKey('ControlsInformation.id'))
    controls = relationship("ControlsInformation", uselist=False, foreign_keys=[controls_id])
    reference_id = Column(Integer(), ForeignKey('ReferenceElement.id'))
    reference = relationship("ReferenceElement", uselist=False, foreign_keys=[reference_id])
    
    
    alias_rel = relationship( "LowLevelRFAlias" )
    alias = association_proxy("alias_rel", "alias",
                                  creator=lambda x_: LowLevelRFAlias(alias=x_))
    
    
    inputs_rel = relationship( "LowLevelRFInputs" )
    inputs = association_proxy("inputs_rel", "inputs",
                                  creator=lambda x_: LowLevelRFInputs(inputs=x_))
    
    
    outputs_rel = relationship( "LowLevelRFOutputs" )
    outputs = association_proxy("outputs_rel", "outputs",
                                  creator=lambda x_: LowLevelRFOutputs(outputs=x_))
    
    
    # ManyToMany
    upstream = relationship( "AcceleratorElement", secondary="LowLevelRF_upstream")
    
    
    # ManyToMany
    downstream = relationship( "AcceleratorElement", secondary="LowLevelRF_downstream")
    

    def __repr__(self):
        return f"LowLevelRF(name={self.name},hardware_class={self.hardware_class},hardware_type={self.hardware_type},hardware_model={self.hardware_model},machine_area={self.machine_area},virtual_name={self.virtual_name},subelement={self.subelement},llrf_id={self.llrf_id},simulation_id={self.simulation_id},electrical_id={self.electrical_id},manufacturer_id={self.manufacturer_id},controls_id={self.controls_id},reference_id={self.reference_id},)"



    
    # Using concrete inheritance: see https://docs.sqlalchemy.org/en/14/orm/inheritance.html
    __mapper_args__ = {
        'concrete': True
    }
    


class RFModulator(StandardElement):
    """
    RF modulator (klystron driver) element.
    """
    __tablename__ = 'RFModulator'

    name = Column(Text(), primary_key=True, nullable=False )
    hardware_class = Column(Enum('Magnet', 'Diagnostic', 'RF', 'Vacuum', 'Laser', 'Plasma', 'Feedback', 'Marker', 'Aperture', 'Stage', 'Lighting', 'Shutter', 'Wakefield', 'TwissMatch', 'Drift', 'Generic', 'Monitor', 'Simulation', 'Valve', 'LaserMirror', 'LaserEnergyMeter', 'LaserAttenuator', name='HardwareClassEnum'), nullable=False )
    hardware_type = Column(Text())
    hardware_model = Column(Text())
    machine_area = Column(Text())
    virtual_name = Column(Text())
    subelement = Column(Text())
    modulator_id = Column(Integer(), ForeignKey('RFModulatorElement.id'))
    modulator = relationship("RFModulatorElement", uselist=False, foreign_keys=[modulator_id])
    simulation_id = Column(Integer(), ForeignKey('SimulationElement.id'))
    simulation = relationship("SimulationElement", uselist=False, foreign_keys=[simulation_id])
    electrical_id = Column(Integer(), ForeignKey('ElectricalElement.id'))
    electrical = relationship("ElectricalElement", uselist=False, foreign_keys=[electrical_id])
    manufacturer_id = Column(Integer(), ForeignKey('ManufacturerElement.id'))
    manufacturer = relationship("ManufacturerElement", uselist=False, foreign_keys=[manufacturer_id])
    controls_id = Column(Integer(), ForeignKey('ControlsInformation.id'))
    controls = relationship("ControlsInformation", uselist=False, foreign_keys=[controls_id])
    reference_id = Column(Integer(), ForeignKey('ReferenceElement.id'))
    reference = relationship("ReferenceElement", uselist=False, foreign_keys=[reference_id])
    
    
    alias_rel = relationship( "RFModulatorAlias" )
    alias = association_proxy("alias_rel", "alias",
                                  creator=lambda x_: RFModulatorAlias(alias=x_))
    
    
    inputs_rel = relationship( "RFModulatorInputs" )
    inputs = association_proxy("inputs_rel", "inputs",
                                  creator=lambda x_: RFModulatorInputs(inputs=x_))
    
    
    outputs_rel = relationship( "RFModulatorOutputs" )
    outputs = association_proxy("outputs_rel", "outputs",
                                  creator=lambda x_: RFModulatorOutputs(outputs=x_))
    
    
    # ManyToMany
    upstream = relationship( "AcceleratorElement", secondary="RFModulator_upstream")
    
    
    # ManyToMany
    downstream = relationship( "AcceleratorElement", secondary="RFModulator_downstream")
    

    def __repr__(self):
        return f"RFModulator(name={self.name},hardware_class={self.hardware_class},hardware_type={self.hardware_type},hardware_model={self.hardware_model},machine_area={self.machine_area},virtual_name={self.virtual_name},subelement={self.subelement},modulator_id={self.modulator_id},simulation_id={self.simulation_id},electrical_id={self.electrical_id},manufacturer_id={self.manufacturer_id},controls_id={self.controls_id},reference_id={self.reference_id},)"



    
    # Using concrete inheritance: see https://docs.sqlalchemy.org/en/14/orm/inheritance.html
    __mapper_args__ = {
        'concrete': True
    }
    


class RFProtection(StandardElement):
    """
    RF protection system element.
    """
    __tablename__ = 'RFProtection'

    name = Column(Text(), primary_key=True, nullable=False )
    hardware_class = Column(Enum('Magnet', 'Diagnostic', 'RF', 'Vacuum', 'Laser', 'Plasma', 'Feedback', 'Marker', 'Aperture', 'Stage', 'Lighting', 'Shutter', 'Wakefield', 'TwissMatch', 'Drift', 'Generic', 'Monitor', 'Simulation', 'Valve', 'LaserMirror', 'LaserEnergyMeter', 'LaserAttenuator', name='HardwareClassEnum'), nullable=False )
    hardware_type = Column(Text())
    hardware_model = Column(Text())
    machine_area = Column(Text())
    virtual_name = Column(Text())
    subelement = Column(Text())
    protection_id = Column(Integer(), ForeignKey('RFProtectionElement.id'))
    protection = relationship("RFProtectionElement", uselist=False, foreign_keys=[protection_id])
    simulation_id = Column(Integer(), ForeignKey('SimulationElement.id'))
    simulation = relationship("SimulationElement", uselist=False, foreign_keys=[simulation_id])
    electrical_id = Column(Integer(), ForeignKey('ElectricalElement.id'))
    electrical = relationship("ElectricalElement", uselist=False, foreign_keys=[electrical_id])
    manufacturer_id = Column(Integer(), ForeignKey('ManufacturerElement.id'))
    manufacturer = relationship("ManufacturerElement", uselist=False, foreign_keys=[manufacturer_id])
    controls_id = Column(Integer(), ForeignKey('ControlsInformation.id'))
    controls = relationship("ControlsInformation", uselist=False, foreign_keys=[controls_id])
    reference_id = Column(Integer(), ForeignKey('ReferenceElement.id'))
    reference = relationship("ReferenceElement", uselist=False, foreign_keys=[reference_id])
    
    
    alias_rel = relationship( "RFProtectionAlias" )
    alias = association_proxy("alias_rel", "alias",
                                  creator=lambda x_: RFProtectionAlias(alias=x_))
    
    
    inputs_rel = relationship( "RFProtectionInputs" )
    inputs = association_proxy("inputs_rel", "inputs",
                                  creator=lambda x_: RFProtectionInputs(inputs=x_))
    
    
    outputs_rel = relationship( "RFProtectionOutputs" )
    outputs = association_proxy("outputs_rel", "outputs",
                                  creator=lambda x_: RFProtectionOutputs(outputs=x_))
    
    
    # ManyToMany
    upstream = relationship( "AcceleratorElement", secondary="RFProtection_upstream")
    
    
    # ManyToMany
    downstream = relationship( "AcceleratorElement", secondary="RFProtection_downstream")
    

    def __repr__(self):
        return f"RFProtection(name={self.name},hardware_class={self.hardware_class},hardware_type={self.hardware_type},hardware_model={self.hardware_model},machine_area={self.machine_area},virtual_name={self.virtual_name},subelement={self.subelement},protection_id={self.protection_id},simulation_id={self.simulation_id},electrical_id={self.electrical_id},manufacturer_id={self.manufacturer_id},controls_id={self.controls_id},reference_id={self.reference_id},)"



    
    # Using concrete inheritance: see https://docs.sqlalchemy.org/en/14/orm/inheritance.html
    __mapper_args__ = {
        'concrete': True
    }
    


class RFHeartbeat(StandardElement):
    """
    RF timing heartbeat / signal-monitor element.
    """
    __tablename__ = 'RFHeartbeat'

    name = Column(Text(), primary_key=True, nullable=False )
    hardware_class = Column(Enum('Magnet', 'Diagnostic', 'RF', 'Vacuum', 'Laser', 'Plasma', 'Feedback', 'Marker', 'Aperture', 'Stage', 'Lighting', 'Shutter', 'Wakefield', 'TwissMatch', 'Drift', 'Generic', 'Monitor', 'Simulation', 'Valve', 'LaserMirror', 'LaserEnergyMeter', 'LaserAttenuator', name='HardwareClassEnum'), nullable=False )
    hardware_type = Column(Text())
    hardware_model = Column(Text())
    machine_area = Column(Text())
    virtual_name = Column(Text())
    subelement = Column(Text())
    heartbeat_id = Column(Integer(), ForeignKey('RFHeartbeatElement.id'))
    heartbeat = relationship("RFHeartbeatElement", uselist=False, foreign_keys=[heartbeat_id])
    simulation_id = Column(Integer(), ForeignKey('SimulationElement.id'))
    simulation = relationship("SimulationElement", uselist=False, foreign_keys=[simulation_id])
    electrical_id = Column(Integer(), ForeignKey('ElectricalElement.id'))
    electrical = relationship("ElectricalElement", uselist=False, foreign_keys=[electrical_id])
    manufacturer_id = Column(Integer(), ForeignKey('ManufacturerElement.id'))
    manufacturer = relationship("ManufacturerElement", uselist=False, foreign_keys=[manufacturer_id])
    controls_id = Column(Integer(), ForeignKey('ControlsInformation.id'))
    controls = relationship("ControlsInformation", uselist=False, foreign_keys=[controls_id])
    reference_id = Column(Integer(), ForeignKey('ReferenceElement.id'))
    reference = relationship("ReferenceElement", uselist=False, foreign_keys=[reference_id])
    
    
    alias_rel = relationship( "RFHeartbeatAlias" )
    alias = association_proxy("alias_rel", "alias",
                                  creator=lambda x_: RFHeartbeatAlias(alias=x_))
    
    
    inputs_rel = relationship( "RFHeartbeatInputs" )
    inputs = association_proxy("inputs_rel", "inputs",
                                  creator=lambda x_: RFHeartbeatInputs(inputs=x_))
    
    
    outputs_rel = relationship( "RFHeartbeatOutputs" )
    outputs = association_proxy("outputs_rel", "outputs",
                                  creator=lambda x_: RFHeartbeatOutputs(outputs=x_))
    
    
    # ManyToMany
    upstream = relationship( "AcceleratorElement", secondary="RFHeartbeat_upstream")
    
    
    # ManyToMany
    downstream = relationship( "AcceleratorElement", secondary="RFHeartbeat_downstream")
    

    def __repr__(self):
        return f"RFHeartbeat(name={self.name},hardware_class={self.hardware_class},hardware_type={self.hardware_type},hardware_model={self.hardware_model},machine_area={self.machine_area},virtual_name={self.virtual_name},subelement={self.subelement},heartbeat_id={self.heartbeat_id},simulation_id={self.simulation_id},electrical_id={self.electrical_id},manufacturer_id={self.manufacturer_id},controls_id={self.controls_id},reference_id={self.reference_id},)"



    
    # Using concrete inheritance: see https://docs.sqlalchemy.org/en/14/orm/inheritance.html
    __mapper_args__ = {
        'concrete': True
    }
    


class PID(StandardElement):
    """
    Proportional-integral-derivative (PID) feedback controller.
    """
    __tablename__ = 'PID'

    name = Column(Text(), primary_key=True, nullable=False )
    hardware_class = Column(Enum('Magnet', 'Diagnostic', 'RF', 'Vacuum', 'Laser', 'Plasma', 'Feedback', 'Marker', 'Aperture', 'Stage', 'Lighting', 'Shutter', 'Wakefield', 'TwissMatch', 'Drift', 'Generic', 'Monitor', 'Simulation', 'Valve', 'LaserMirror', 'LaserEnergyMeter', 'LaserAttenuator', name='HardwareClassEnum'), nullable=False )
    hardware_type = Column(Text())
    hardware_model = Column(Text())
    machine_area = Column(Text())
    virtual_name = Column(Text())
    subelement = Column(Text())
    pid_id = Column(Integer(), ForeignKey('PIDElement.id'))
    pid = relationship("PIDElement", uselist=False, foreign_keys=[pid_id])
    simulation_id = Column(Integer(), ForeignKey('SimulationElement.id'))
    simulation = relationship("SimulationElement", uselist=False, foreign_keys=[simulation_id])
    electrical_id = Column(Integer(), ForeignKey('ElectricalElement.id'))
    electrical = relationship("ElectricalElement", uselist=False, foreign_keys=[electrical_id])
    manufacturer_id = Column(Integer(), ForeignKey('ManufacturerElement.id'))
    manufacturer = relationship("ManufacturerElement", uselist=False, foreign_keys=[manufacturer_id])
    controls_id = Column(Integer(), ForeignKey('ControlsInformation.id'))
    controls = relationship("ControlsInformation", uselist=False, foreign_keys=[controls_id])
    reference_id = Column(Integer(), ForeignKey('ReferenceElement.id'))
    reference = relationship("ReferenceElement", uselist=False, foreign_keys=[reference_id])
    
    
    alias_rel = relationship( "PIDAlias" )
    alias = association_proxy("alias_rel", "alias",
                                  creator=lambda x_: PIDAlias(alias=x_))
    
    
    inputs_rel = relationship( "PIDInputs" )
    inputs = association_proxy("inputs_rel", "inputs",
                                  creator=lambda x_: PIDInputs(inputs=x_))
    
    
    outputs_rel = relationship( "PIDOutputs" )
    outputs = association_proxy("outputs_rel", "outputs",
                                  creator=lambda x_: PIDOutputs(outputs=x_))
    
    
    # ManyToMany
    upstream = relationship( "AcceleratorElement", secondary="PID_upstream")
    
    
    # ManyToMany
    downstream = relationship( "AcceleratorElement", secondary="PID_downstream")
    

    def __repr__(self):
        return f"PID(name={self.name},hardware_class={self.hardware_class},hardware_type={self.hardware_type},hardware_model={self.hardware_model},machine_area={self.machine_area},virtual_name={self.virtual_name},subelement={self.subelement},pid_id={self.pid_id},simulation_id={self.simulation_id},electrical_id={self.electrical_id},manufacturer_id={self.manufacturer_id},controls_id={self.controls_id},reference_id={self.reference_id},)"



    
    # Using concrete inheritance: see https://docs.sqlalchemy.org/en/14/orm/inheritance.html
    __mapper_args__ = {
        'concrete': True
    }
    


class LaserEnergyMeter(StandardElement):
    """
    Laser pulse-energy diagnostic (photodiode / pyroelectric).
    """
    __tablename__ = 'LaserEnergyMeter'

    name = Column(Text(), primary_key=True, nullable=False )
    hardware_class = Column(Enum('Magnet', 'Diagnostic', 'RF', 'Vacuum', 'Laser', 'Plasma', 'Feedback', 'Marker', 'Aperture', 'Stage', 'Lighting', 'Shutter', 'Wakefield', 'TwissMatch', 'Drift', 'Generic', 'Monitor', 'Simulation', 'Valve', 'LaserMirror', 'LaserEnergyMeter', 'LaserAttenuator', name='HardwareClassEnum'), nullable=False )
    hardware_type = Column(Text())
    hardware_model = Column(Text())
    machine_area = Column(Text())
    virtual_name = Column(Text())
    subelement = Column(Text())
    laser_id = Column(Integer(), ForeignKey('LaserEnergyMeterElement.id'))
    laser = relationship("LaserEnergyMeterElement", uselist=False, foreign_keys=[laser_id])
    simulation_id = Column(Integer(), ForeignKey('SimulationElement.id'))
    simulation = relationship("SimulationElement", uselist=False, foreign_keys=[simulation_id])
    electrical_id = Column(Integer(), ForeignKey('ElectricalElement.id'))
    electrical = relationship("ElectricalElement", uselist=False, foreign_keys=[electrical_id])
    manufacturer_id = Column(Integer(), ForeignKey('ManufacturerElement.id'))
    manufacturer = relationship("ManufacturerElement", uselist=False, foreign_keys=[manufacturer_id])
    controls_id = Column(Integer(), ForeignKey('ControlsInformation.id'))
    controls = relationship("ControlsInformation", uselist=False, foreign_keys=[controls_id])
    reference_id = Column(Integer(), ForeignKey('ReferenceElement.id'))
    reference = relationship("ReferenceElement", uselist=False, foreign_keys=[reference_id])
    
    
    alias_rel = relationship( "LaserEnergyMeterAlias" )
    alias = association_proxy("alias_rel", "alias",
                                  creator=lambda x_: LaserEnergyMeterAlias(alias=x_))
    
    
    inputs_rel = relationship( "LaserEnergyMeterInputs" )
    inputs = association_proxy("inputs_rel", "inputs",
                                  creator=lambda x_: LaserEnergyMeterInputs(inputs=x_))
    
    
    outputs_rel = relationship( "LaserEnergyMeterOutputs" )
    outputs = association_proxy("outputs_rel", "outputs",
                                  creator=lambda x_: LaserEnergyMeterOutputs(outputs=x_))
    
    
    # ManyToMany
    upstream = relationship( "AcceleratorElement", secondary="LaserEnergyMeter_upstream")
    
    
    # ManyToMany
    downstream = relationship( "AcceleratorElement", secondary="LaserEnergyMeter_downstream")
    

    def __repr__(self):
        return f"LaserEnergyMeter(name={self.name},hardware_class={self.hardware_class},hardware_type={self.hardware_type},hardware_model={self.hardware_model},machine_area={self.machine_area},virtual_name={self.virtual_name},subelement={self.subelement},laser_id={self.laser_id},simulation_id={self.simulation_id},electrical_id={self.electrical_id},manufacturer_id={self.manufacturer_id},controls_id={self.controls_id},reference_id={self.reference_id},)"



    
    # Using concrete inheritance: see https://docs.sqlalchemy.org/en/14/orm/inheritance.html
    __mapper_args__ = {
        'concrete': True
    }
    


class LaserHalfWavePlate(StandardElement):
    """
    Half-wave plate for laser polarisation rotation.
    """
    __tablename__ = 'LaserHalfWavePlate'

    name = Column(Text(), primary_key=True, nullable=False )
    hardware_class = Column(Enum('Magnet', 'Diagnostic', 'RF', 'Vacuum', 'Laser', 'Plasma', 'Feedback', 'Marker', 'Aperture', 'Stage', 'Lighting', 'Shutter', 'Wakefield', 'TwissMatch', 'Drift', 'Generic', 'Monitor', 'Simulation', 'Valve', 'LaserMirror', 'LaserEnergyMeter', 'LaserAttenuator', name='HardwareClassEnum'), nullable=False )
    hardware_type = Column(Text())
    hardware_model = Column(Text())
    machine_area = Column(Text())
    virtual_name = Column(Text())
    subelement = Column(Text())
    laser_id = Column(Integer(), ForeignKey('LaserHalfWavePlateElement.id'))
    laser = relationship("LaserHalfWavePlateElement", uselist=False, foreign_keys=[laser_id])
    simulation_id = Column(Integer(), ForeignKey('SimulationElement.id'))
    simulation = relationship("SimulationElement", uselist=False, foreign_keys=[simulation_id])
    electrical_id = Column(Integer(), ForeignKey('ElectricalElement.id'))
    electrical = relationship("ElectricalElement", uselist=False, foreign_keys=[electrical_id])
    manufacturer_id = Column(Integer(), ForeignKey('ManufacturerElement.id'))
    manufacturer = relationship("ManufacturerElement", uselist=False, foreign_keys=[manufacturer_id])
    controls_id = Column(Integer(), ForeignKey('ControlsInformation.id'))
    controls = relationship("ControlsInformation", uselist=False, foreign_keys=[controls_id])
    reference_id = Column(Integer(), ForeignKey('ReferenceElement.id'))
    reference = relationship("ReferenceElement", uselist=False, foreign_keys=[reference_id])
    
    
    alias_rel = relationship( "LaserHalfWavePlateAlias" )
    alias = association_proxy("alias_rel", "alias",
                                  creator=lambda x_: LaserHalfWavePlateAlias(alias=x_))
    
    
    inputs_rel = relationship( "LaserHalfWavePlateInputs" )
    inputs = association_proxy("inputs_rel", "inputs",
                                  creator=lambda x_: LaserHalfWavePlateInputs(inputs=x_))
    
    
    outputs_rel = relationship( "LaserHalfWavePlateOutputs" )
    outputs = association_proxy("outputs_rel", "outputs",
                                  creator=lambda x_: LaserHalfWavePlateOutputs(outputs=x_))
    
    
    # ManyToMany
    upstream = relationship( "AcceleratorElement", secondary="LaserHalfWavePlate_upstream")
    
    
    # ManyToMany
    downstream = relationship( "AcceleratorElement", secondary="LaserHalfWavePlate_downstream")
    

    def __repr__(self):
        return f"LaserHalfWavePlate(name={self.name},hardware_class={self.hardware_class},hardware_type={self.hardware_type},hardware_model={self.hardware_model},machine_area={self.machine_area},virtual_name={self.virtual_name},subelement={self.subelement},laser_id={self.laser_id},simulation_id={self.simulation_id},electrical_id={self.electrical_id},manufacturer_id={self.manufacturer_id},controls_id={self.controls_id},reference_id={self.reference_id},)"



    
    # Using concrete inheritance: see https://docs.sqlalchemy.org/en/14/orm/inheritance.html
    __mapper_args__ = {
        'concrete': True
    }
    


class LaserMirror(StandardElement):
    """
    Laser steering or focusing mirror.
    """
    __tablename__ = 'LaserMirror'

    name = Column(Text(), primary_key=True, nullable=False )
    hardware_class = Column(Enum('Magnet', 'Diagnostic', 'RF', 'Vacuum', 'Laser', 'Plasma', 'Feedback', 'Marker', 'Aperture', 'Stage', 'Lighting', 'Shutter', 'Wakefield', 'TwissMatch', 'Drift', 'Generic', 'Monitor', 'Simulation', 'Valve', 'LaserMirror', 'LaserEnergyMeter', 'LaserAttenuator', name='HardwareClassEnum'), nullable=False )
    hardware_type = Column(Text())
    hardware_model = Column(Text())
    machine_area = Column(Text())
    virtual_name = Column(Text())
    subelement = Column(Text())
    laser_id = Column(Integer(), ForeignKey('LaserMirrorElement.id'))
    laser = relationship("LaserMirrorElement", uselist=False, foreign_keys=[laser_id])
    simulation_id = Column(Integer(), ForeignKey('SimulationElement.id'))
    simulation = relationship("SimulationElement", uselist=False, foreign_keys=[simulation_id])
    electrical_id = Column(Integer(), ForeignKey('ElectricalElement.id'))
    electrical = relationship("ElectricalElement", uselist=False, foreign_keys=[electrical_id])
    manufacturer_id = Column(Integer(), ForeignKey('ManufacturerElement.id'))
    manufacturer = relationship("ManufacturerElement", uselist=False, foreign_keys=[manufacturer_id])
    controls_id = Column(Integer(), ForeignKey('ControlsInformation.id'))
    controls = relationship("ControlsInformation", uselist=False, foreign_keys=[controls_id])
    reference_id = Column(Integer(), ForeignKey('ReferenceElement.id'))
    reference = relationship("ReferenceElement", uselist=False, foreign_keys=[reference_id])
    
    
    alias_rel = relationship( "LaserMirrorAlias" )
    alias = association_proxy("alias_rel", "alias",
                                  creator=lambda x_: LaserMirrorAlias(alias=x_))
    
    
    inputs_rel = relationship( "LaserMirrorInputs" )
    inputs = association_proxy("inputs_rel", "inputs",
                                  creator=lambda x_: LaserMirrorInputs(inputs=x_))
    
    
    outputs_rel = relationship( "LaserMirrorOutputs" )
    outputs = association_proxy("outputs_rel", "outputs",
                                  creator=lambda x_: LaserMirrorOutputs(outputs=x_))
    
    
    # ManyToMany
    upstream = relationship( "AcceleratorElement", secondary="LaserMirror_upstream")
    
    
    # ManyToMany
    downstream = relationship( "AcceleratorElement", secondary="LaserMirror_downstream")
    

    def __repr__(self):
        return f"LaserMirror(name={self.name},hardware_class={self.hardware_class},hardware_type={self.hardware_type},hardware_model={self.hardware_model},machine_area={self.machine_area},virtual_name={self.virtual_name},subelement={self.subelement},laser_id={self.laser_id},simulation_id={self.simulation_id},electrical_id={self.electrical_id},manufacturer_id={self.manufacturer_id},controls_id={self.controls_id},reference_id={self.reference_id},)"



    
    # Using concrete inheritance: see https://docs.sqlalchemy.org/en/14/orm/inheritance.html
    __mapper_args__ = {
        'concrete': True
    }
    


class LaserAttenuator(StandardElement):
    """
    Laser power attenuator (waveplate + polariser combination).
    """
    __tablename__ = 'LaserAttenuator'

    maximum = Column(Float())
    minimum = Column(Float())
    name = Column(Text(), primary_key=True, nullable=False )
    hardware_class = Column(Enum('Magnet', 'Diagnostic', 'RF', 'Vacuum', 'Laser', 'Plasma', 'Feedback', 'Marker', 'Aperture', 'Stage', 'Lighting', 'Shutter', 'Wakefield', 'TwissMatch', 'Drift', 'Generic', 'Monitor', 'Simulation', 'Valve', 'LaserMirror', 'LaserEnergyMeter', 'LaserAttenuator', name='HardwareClassEnum'), nullable=False )
    hardware_type = Column(Text())
    hardware_model = Column(Text())
    machine_area = Column(Text())
    virtual_name = Column(Text())
    subelement = Column(Text())
    simulation_id = Column(Integer(), ForeignKey('SimulationElement.id'))
    simulation = relationship("SimulationElement", uselist=False, foreign_keys=[simulation_id])
    electrical_id = Column(Integer(), ForeignKey('ElectricalElement.id'))
    electrical = relationship("ElectricalElement", uselist=False, foreign_keys=[electrical_id])
    manufacturer_id = Column(Integer(), ForeignKey('ManufacturerElement.id'))
    manufacturer = relationship("ManufacturerElement", uselist=False, foreign_keys=[manufacturer_id])
    controls_id = Column(Integer(), ForeignKey('ControlsInformation.id'))
    controls = relationship("ControlsInformation", uselist=False, foreign_keys=[controls_id])
    reference_id = Column(Integer(), ForeignKey('ReferenceElement.id'))
    reference = relationship("ReferenceElement", uselist=False, foreign_keys=[reference_id])
    
    
    alias_rel = relationship( "LaserAttenuatorAlias" )
    alias = association_proxy("alias_rel", "alias",
                                  creator=lambda x_: LaserAttenuatorAlias(alias=x_))
    
    
    inputs_rel = relationship( "LaserAttenuatorInputs" )
    inputs = association_proxy("inputs_rel", "inputs",
                                  creator=lambda x_: LaserAttenuatorInputs(inputs=x_))
    
    
    outputs_rel = relationship( "LaserAttenuatorOutputs" )
    outputs = association_proxy("outputs_rel", "outputs",
                                  creator=lambda x_: LaserAttenuatorOutputs(outputs=x_))
    
    
    # ManyToMany
    upstream = relationship( "AcceleratorElement", secondary="LaserAttenuator_upstream")
    
    
    # ManyToMany
    downstream = relationship( "AcceleratorElement", secondary="LaserAttenuator_downstream")
    

    def __repr__(self):
        return f"LaserAttenuator(maximum={self.maximum},minimum={self.minimum},name={self.name},hardware_class={self.hardware_class},hardware_type={self.hardware_type},hardware_model={self.hardware_model},machine_area={self.machine_area},virtual_name={self.virtual_name},subelement={self.subelement},simulation_id={self.simulation_id},electrical_id={self.electrical_id},manufacturer_id={self.manufacturer_id},controls_id={self.controls_id},reference_id={self.reference_id},)"



    
    # Using concrete inheritance: see https://docs.sqlalchemy.org/en/14/orm/inheritance.html
    __mapper_args__ = {
        'concrete': True
    }
    


class PhysicalAcceleratorElement(Element):
    """
    Accelerator element with a well-defined physical position and orientation in the beamline.
    """
    __tablename__ = 'PhysicalAcceleratorElement'

    name = Column(Text(), primary_key=True, nullable=False )
    hardware_class = Column(Enum('Magnet', 'Diagnostic', 'RF', 'Vacuum', 'Laser', 'Plasma', 'Feedback', 'Marker', 'Aperture', 'Stage', 'Lighting', 'Shutter', 'Wakefield', 'TwissMatch', 'Drift', 'Generic', 'Monitor', 'Simulation', 'Valve', 'LaserMirror', 'LaserEnergyMeter', 'LaserAttenuator', name='HardwareClassEnum'), nullable=False )
    hardware_type = Column(Text())
    hardware_model = Column(Text())
    machine_area = Column(Text())
    virtual_name = Column(Text())
    subelement = Column(Text())
    physical_id = Column(Integer(), ForeignKey('PhysicalElement.id'))
    physical = relationship("PhysicalElement", uselist=False, foreign_keys=[physical_id])
    simulation_id = Column(Integer(), ForeignKey('SimulationElement.id'))
    simulation = relationship("SimulationElement", uselist=False, foreign_keys=[simulation_id])
    electrical_id = Column(Integer(), ForeignKey('ElectricalElement.id'))
    electrical = relationship("ElectricalElement", uselist=False, foreign_keys=[electrical_id])
    manufacturer_id = Column(Integer(), ForeignKey('ManufacturerElement.id'))
    manufacturer = relationship("ManufacturerElement", uselist=False, foreign_keys=[manufacturer_id])
    controls_id = Column(Integer(), ForeignKey('ControlsInformation.id'))
    controls = relationship("ControlsInformation", uselist=False, foreign_keys=[controls_id])
    reference_id = Column(Integer(), ForeignKey('ReferenceElement.id'))
    reference = relationship("ReferenceElement", uselist=False, foreign_keys=[reference_id])
    
    
    alias_rel = relationship( "PhysicalAcceleratorElementAlias" )
    alias = association_proxy("alias_rel", "alias",
                                  creator=lambda x_: PhysicalAcceleratorElementAlias(alias=x_))
    
    
    inputs_rel = relationship( "PhysicalAcceleratorElementInputs" )
    inputs = association_proxy("inputs_rel", "inputs",
                                  creator=lambda x_: PhysicalAcceleratorElementInputs(inputs=x_))
    
    
    outputs_rel = relationship( "PhysicalAcceleratorElementOutputs" )
    outputs = association_proxy("outputs_rel", "outputs",
                                  creator=lambda x_: PhysicalAcceleratorElementOutputs(outputs=x_))
    
    
    # ManyToMany
    upstream = relationship( "AcceleratorElement", secondary="PhysicalAcceleratorElement_upstream")
    
    
    # ManyToMany
    downstream = relationship( "AcceleratorElement", secondary="PhysicalAcceleratorElement_downstream")
    

    def __repr__(self):
        return f"PhysicalAcceleratorElement(name={self.name},hardware_class={self.hardware_class},hardware_type={self.hardware_type},hardware_model={self.hardware_model},machine_area={self.machine_area},virtual_name={self.virtual_name},subelement={self.subelement},physical_id={self.physical_id},simulation_id={self.simulation_id},electrical_id={self.electrical_id},manufacturer_id={self.manufacturer_id},controls_id={self.controls_id},reference_id={self.reference_id},)"



    
    # Using concrete inheritance: see https://docs.sqlalchemy.org/en/14/orm/inheritance.html
    __mapper_args__ = {
        'concrete': True
    }
    


class TwissMatch(PhysicalAcceleratorElement):
    """
    Virtual Twiss-parameter matching point -- a zero-length marker that defines the desired optical functions at a location in the lattice.
    """
    __tablename__ = 'TwissMatch'

    name = Column(Text(), primary_key=True, nullable=False )
    hardware_class = Column(Enum('Magnet', 'Diagnostic', 'RF', 'Vacuum', 'Laser', 'Plasma', 'Feedback', 'Marker', 'Aperture', 'Stage', 'Lighting', 'Shutter', 'Wakefield', 'TwissMatch', 'Drift', 'Generic', 'Monitor', 'Simulation', 'Valve', 'LaserMirror', 'LaserEnergyMeter', 'LaserAttenuator', name='HardwareClassEnum'), nullable=False )
    hardware_type = Column(Text())
    hardware_model = Column(Text())
    machine_area = Column(Text())
    virtual_name = Column(Text())
    subelement = Column(Text())
    physical_id = Column(Integer(), ForeignKey('PhysicalElement.id'))
    physical = relationship("PhysicalElement", uselist=False, foreign_keys=[physical_id])
    simulation_id = Column(Integer(), ForeignKey('TwissMatchSimulationElement.id'))
    simulation = relationship("TwissMatchSimulationElement", uselist=False, foreign_keys=[simulation_id])
    electrical_id = Column(Integer(), ForeignKey('ElectricalElement.id'))
    electrical = relationship("ElectricalElement", uselist=False, foreign_keys=[electrical_id])
    manufacturer_id = Column(Integer(), ForeignKey('ManufacturerElement.id'))
    manufacturer = relationship("ManufacturerElement", uselist=False, foreign_keys=[manufacturer_id])
    controls_id = Column(Integer(), ForeignKey('ControlsInformation.id'))
    controls = relationship("ControlsInformation", uselist=False, foreign_keys=[controls_id])
    reference_id = Column(Integer(), ForeignKey('ReferenceElement.id'))
    reference = relationship("ReferenceElement", uselist=False, foreign_keys=[reference_id])
    
    
    alias_rel = relationship( "TwissMatchAlias" )
    alias = association_proxy("alias_rel", "alias",
                                  creator=lambda x_: TwissMatchAlias(alias=x_))
    
    
    inputs_rel = relationship( "TwissMatchInputs" )
    inputs = association_proxy("inputs_rel", "inputs",
                                  creator=lambda x_: TwissMatchInputs(inputs=x_))
    
    
    outputs_rel = relationship( "TwissMatchOutputs" )
    outputs = association_proxy("outputs_rel", "outputs",
                                  creator=lambda x_: TwissMatchOutputs(outputs=x_))
    
    
    # ManyToMany
    upstream = relationship( "AcceleratorElement", secondary="TwissMatch_upstream")
    
    
    # ManyToMany
    downstream = relationship( "AcceleratorElement", secondary="TwissMatch_downstream")
    

    def __repr__(self):
        return f"TwissMatch(name={self.name},hardware_class={self.hardware_class},hardware_type={self.hardware_type},hardware_model={self.hardware_model},machine_area={self.machine_area},virtual_name={self.virtual_name},subelement={self.subelement},physical_id={self.physical_id},simulation_id={self.simulation_id},electrical_id={self.electrical_id},manufacturer_id={self.manufacturer_id},controls_id={self.controls_id},reference_id={self.reference_id},)"



    
    # Using concrete inheritance: see https://docs.sqlalchemy.org/en/14/orm/inheritance.html
    __mapper_args__ = {
        'concrete': True
    }
    


class MatrixTransform(PhysicalAcceleratorElement):
    """
    Transfer-map element with zero-, first-, and second-order coefficients.
    """
    __tablename__ = 'MatrixTransform'

    name = Column(Text(), primary_key=True, nullable=False )
    hardware_class = Column(Enum('Magnet', 'Diagnostic', 'RF', 'Vacuum', 'Laser', 'Plasma', 'Feedback', 'Marker', 'Aperture', 'Stage', 'Lighting', 'Shutter', 'Wakefield', 'TwissMatch', 'Drift', 'Generic', 'Monitor', 'Simulation', 'Valve', 'LaserMirror', 'LaserEnergyMeter', 'LaserAttenuator', name='HardwareClassEnum'), nullable=False )
    hardware_type = Column(Text())
    hardware_model = Column(Text())
    machine_area = Column(Text())
    virtual_name = Column(Text())
    subelement = Column(Text())
    physical_id = Column(Integer(), ForeignKey('PhysicalElement.id'))
    physical = relationship("PhysicalElement", uselist=False, foreign_keys=[physical_id])
    simulation_id = Column(Integer(), ForeignKey('MatrixTransformSimulationElement.id'))
    simulation = relationship("MatrixTransformSimulationElement", uselist=False, foreign_keys=[simulation_id])
    electrical_id = Column(Integer(), ForeignKey('ElectricalElement.id'))
    electrical = relationship("ElectricalElement", uselist=False, foreign_keys=[electrical_id])
    manufacturer_id = Column(Integer(), ForeignKey('ManufacturerElement.id'))
    manufacturer = relationship("ManufacturerElement", uselist=False, foreign_keys=[manufacturer_id])
    controls_id = Column(Integer(), ForeignKey('ControlsInformation.id'))
    controls = relationship("ControlsInformation", uselist=False, foreign_keys=[controls_id])
    reference_id = Column(Integer(), ForeignKey('ReferenceElement.id'))
    reference = relationship("ReferenceElement", uselist=False, foreign_keys=[reference_id])
    
    
    alias_rel = relationship( "MatrixTransformAlias" )
    alias = association_proxy("alias_rel", "alias",
                                  creator=lambda x_: MatrixTransformAlias(alias=x_))
    
    
    inputs_rel = relationship( "MatrixTransformInputs" )
    inputs = association_proxy("inputs_rel", "inputs",
                                  creator=lambda x_: MatrixTransformInputs(inputs=x_))
    
    
    outputs_rel = relationship( "MatrixTransformOutputs" )
    outputs = association_proxy("outputs_rel", "outputs",
                                  creator=lambda x_: MatrixTransformOutputs(outputs=x_))
    
    
    # ManyToMany
    upstream = relationship( "AcceleratorElement", secondary="MatrixTransform_upstream")
    
    
    # ManyToMany
    downstream = relationship( "AcceleratorElement", secondary="MatrixTransform_downstream")
    

    def __repr__(self):
        return f"MatrixTransform(name={self.name},hardware_class={self.hardware_class},hardware_type={self.hardware_type},hardware_model={self.hardware_model},machine_area={self.machine_area},virtual_name={self.virtual_name},subelement={self.subelement},physical_id={self.physical_id},simulation_id={self.simulation_id},electrical_id={self.electrical_id},manufacturer_id={self.manufacturer_id},controls_id={self.controls_id},reference_id={self.reference_id},)"



    
    # Using concrete inheritance: see https://docs.sqlalchemy.org/en/14/orm/inheritance.html
    __mapper_args__ = {
        'concrete': True
    }
    


class ElectrostaticSeparator(PhysicalAcceleratorElement):
    """
    Static electrostatic transverse-deflection element.
    """
    __tablename__ = 'ElectrostaticSeparator'

    name = Column(Text(), primary_key=True, nullable=False )
    hardware_class = Column(Enum('Magnet', 'Diagnostic', 'RF', 'Vacuum', 'Laser', 'Plasma', 'Feedback', 'Marker', 'Aperture', 'Stage', 'Lighting', 'Shutter', 'Wakefield', 'TwissMatch', 'Drift', 'Generic', 'Monitor', 'Simulation', 'Valve', 'LaserMirror', 'LaserEnergyMeter', 'LaserAttenuator', name='HardwareClassEnum'), nullable=False )
    hardware_type = Column(Text())
    hardware_model = Column(Text())
    machine_area = Column(Text())
    virtual_name = Column(Text())
    subelement = Column(Text())
    physical_id = Column(Integer(), ForeignKey('PhysicalElement.id'))
    physical = relationship("PhysicalElement", uselist=False, foreign_keys=[physical_id])
    simulation_id = Column(Integer(), ForeignKey('ElectrostaticSeparatorSimulationElement.id'))
    simulation = relationship("ElectrostaticSeparatorSimulationElement", uselist=False, foreign_keys=[simulation_id])
    electrical_id = Column(Integer(), ForeignKey('ElectricalElement.id'))
    electrical = relationship("ElectricalElement", uselist=False, foreign_keys=[electrical_id])
    manufacturer_id = Column(Integer(), ForeignKey('ManufacturerElement.id'))
    manufacturer = relationship("ManufacturerElement", uselist=False, foreign_keys=[manufacturer_id])
    controls_id = Column(Integer(), ForeignKey('ControlsInformation.id'))
    controls = relationship("ControlsInformation", uselist=False, foreign_keys=[controls_id])
    reference_id = Column(Integer(), ForeignKey('ReferenceElement.id'))
    reference = relationship("ReferenceElement", uselist=False, foreign_keys=[reference_id])
    
    
    alias_rel = relationship( "ElectrostaticSeparatorAlias" )
    alias = association_proxy("alias_rel", "alias",
                                  creator=lambda x_: ElectrostaticSeparatorAlias(alias=x_))
    
    
    inputs_rel = relationship( "ElectrostaticSeparatorInputs" )
    inputs = association_proxy("inputs_rel", "inputs",
                                  creator=lambda x_: ElectrostaticSeparatorInputs(inputs=x_))
    
    
    outputs_rel = relationship( "ElectrostaticSeparatorOutputs" )
    outputs = association_proxy("outputs_rel", "outputs",
                                  creator=lambda x_: ElectrostaticSeparatorOutputs(outputs=x_))
    
    
    # ManyToMany
    upstream = relationship( "AcceleratorElement", secondary="ElectrostaticSeparator_upstream")
    
    
    # ManyToMany
    downstream = relationship( "AcceleratorElement", secondary="ElectrostaticSeparator_downstream")
    

    def __repr__(self):
        return f"ElectrostaticSeparator(name={self.name},hardware_class={self.hardware_class},hardware_type={self.hardware_type},hardware_model={self.hardware_model},machine_area={self.machine_area},virtual_name={self.virtual_name},subelement={self.subelement},physical_id={self.physical_id},simulation_id={self.simulation_id},electrical_id={self.electrical_id},manufacturer_id={self.manufacturer_id},controls_id={self.controls_id},reference_id={self.reference_id},)"



    
    # Using concrete inheritance: see https://docs.sqlalchemy.org/en/14/orm/inheritance.html
    __mapper_args__ = {
        'concrete': True
    }
    


class ACDipole(PhysicalAcceleratorElement):
    """
    Base class for horizontal and vertical AC-dipole tune exciters.
    """
    __tablename__ = 'ACDipole'

    name = Column(Text(), primary_key=True, nullable=False )
    hardware_class = Column(Enum('Magnet', 'Diagnostic', 'RF', 'Vacuum', 'Laser', 'Plasma', 'Feedback', 'Marker', 'Aperture', 'Stage', 'Lighting', 'Shutter', 'Wakefield', 'TwissMatch', 'Drift', 'Generic', 'Monitor', 'Simulation', 'Valve', 'LaserMirror', 'LaserEnergyMeter', 'LaserAttenuator', name='HardwareClassEnum'), nullable=False )
    hardware_type = Column(Text())
    hardware_model = Column(Text())
    machine_area = Column(Text())
    virtual_name = Column(Text())
    subelement = Column(Text())
    physical_id = Column(Integer(), ForeignKey('PhysicalElement.id'))
    physical = relationship("PhysicalElement", uselist=False, foreign_keys=[physical_id])
    simulation_id = Column(Integer(), ForeignKey('ACDipoleSimulationElement.id'))
    simulation = relationship("ACDipoleSimulationElement", uselist=False, foreign_keys=[simulation_id])
    electrical_id = Column(Integer(), ForeignKey('ElectricalElement.id'))
    electrical = relationship("ElectricalElement", uselist=False, foreign_keys=[electrical_id])
    manufacturer_id = Column(Integer(), ForeignKey('ManufacturerElement.id'))
    manufacturer = relationship("ManufacturerElement", uselist=False, foreign_keys=[manufacturer_id])
    controls_id = Column(Integer(), ForeignKey('ControlsInformation.id'))
    controls = relationship("ControlsInformation", uselist=False, foreign_keys=[controls_id])
    reference_id = Column(Integer(), ForeignKey('ReferenceElement.id'))
    reference = relationship("ReferenceElement", uselist=False, foreign_keys=[reference_id])
    
    
    alias_rel = relationship( "ACDipoleAlias" )
    alias = association_proxy("alias_rel", "alias",
                                  creator=lambda x_: ACDipoleAlias(alias=x_))
    
    
    inputs_rel = relationship( "ACDipoleInputs" )
    inputs = association_proxy("inputs_rel", "inputs",
                                  creator=lambda x_: ACDipoleInputs(inputs=x_))
    
    
    outputs_rel = relationship( "ACDipoleOutputs" )
    outputs = association_proxy("outputs_rel", "outputs",
                                  creator=lambda x_: ACDipoleOutputs(outputs=x_))
    
    
    # ManyToMany
    upstream = relationship( "AcceleratorElement", secondary="ACDipole_upstream")
    
    
    # ManyToMany
    downstream = relationship( "AcceleratorElement", secondary="ACDipole_downstream")
    

    def __repr__(self):
        return f"ACDipole(name={self.name},hardware_class={self.hardware_class},hardware_type={self.hardware_type},hardware_model={self.hardware_model},machine_area={self.machine_area},virtual_name={self.virtual_name},subelement={self.subelement},physical_id={self.physical_id},simulation_id={self.simulation_id},electrical_id={self.electrical_id},manufacturer_id={self.manufacturer_id},controls_id={self.controls_id},reference_id={self.reference_id},)"



    
    # Using concrete inheritance: see https://docs.sqlalchemy.org/en/14/orm/inheritance.html
    __mapper_args__ = {
        'concrete': True
    }
    


class Wire(PhysicalAcceleratorElement):
    """
    Current-carrying wire for long-range beam-beam compensation.
    """
    __tablename__ = 'Wire'

    name = Column(Text(), primary_key=True, nullable=False )
    hardware_class = Column(Enum('Magnet', 'Diagnostic', 'RF', 'Vacuum', 'Laser', 'Plasma', 'Feedback', 'Marker', 'Aperture', 'Stage', 'Lighting', 'Shutter', 'Wakefield', 'TwissMatch', 'Drift', 'Generic', 'Monitor', 'Simulation', 'Valve', 'LaserMirror', 'LaserEnergyMeter', 'LaserAttenuator', name='HardwareClassEnum'), nullable=False )
    hardware_type = Column(Text())
    hardware_model = Column(Text())
    machine_area = Column(Text())
    virtual_name = Column(Text())
    subelement = Column(Text())
    physical_id = Column(Integer(), ForeignKey('PhysicalElement.id'))
    physical = relationship("PhysicalElement", uselist=False, foreign_keys=[physical_id])
    simulation_id = Column(Integer(), ForeignKey('WireSimulationElement.id'))
    simulation = relationship("WireSimulationElement", uselist=False, foreign_keys=[simulation_id])
    electrical_id = Column(Integer(), ForeignKey('ElectricalElement.id'))
    electrical = relationship("ElectricalElement", uselist=False, foreign_keys=[electrical_id])
    manufacturer_id = Column(Integer(), ForeignKey('ManufacturerElement.id'))
    manufacturer = relationship("ManufacturerElement", uselist=False, foreign_keys=[manufacturer_id])
    controls_id = Column(Integer(), ForeignKey('ControlsInformation.id'))
    controls = relationship("ControlsInformation", uselist=False, foreign_keys=[controls_id])
    reference_id = Column(Integer(), ForeignKey('ReferenceElement.id'))
    reference = relationship("ReferenceElement", uselist=False, foreign_keys=[reference_id])
    
    
    alias_rel = relationship( "WireAlias" )
    alias = association_proxy("alias_rel", "alias",
                                  creator=lambda x_: WireAlias(alias=x_))
    
    
    inputs_rel = relationship( "WireInputs" )
    inputs = association_proxy("inputs_rel", "inputs",
                                  creator=lambda x_: WireInputs(inputs=x_))
    
    
    outputs_rel = relationship( "WireOutputs" )
    outputs = association_proxy("outputs_rel", "outputs",
                                  creator=lambda x_: WireOutputs(outputs=x_))
    
    
    # ManyToMany
    upstream = relationship( "AcceleratorElement", secondary="Wire_upstream")
    
    
    # ManyToMany
    downstream = relationship( "AcceleratorElement", secondary="Wire_downstream")
    

    def __repr__(self):
        return f"Wire(name={self.name},hardware_class={self.hardware_class},hardware_type={self.hardware_type},hardware_model={self.hardware_model},machine_area={self.machine_area},virtual_name={self.virtual_name},subelement={self.subelement},physical_id={self.physical_id},simulation_id={self.simulation_id},electrical_id={self.electrical_id},manufacturer_id={self.manufacturer_id},controls_id={self.controls_id},reference_id={self.reference_id},)"



    
    # Using concrete inheritance: see https://docs.sqlalchemy.org/en/14/orm/inheritance.html
    __mapper_args__ = {
        'concrete': True
    }
    


class BeamBeam(PhysicalAcceleratorElement):
    """
    Weak-strong beam-beam interaction element.
    """
    __tablename__ = 'BeamBeam'

    name = Column(Text(), primary_key=True, nullable=False )
    hardware_class = Column(Enum('Magnet', 'Diagnostic', 'RF', 'Vacuum', 'Laser', 'Plasma', 'Feedback', 'Marker', 'Aperture', 'Stage', 'Lighting', 'Shutter', 'Wakefield', 'TwissMatch', 'Drift', 'Generic', 'Monitor', 'Simulation', 'Valve', 'LaserMirror', 'LaserEnergyMeter', 'LaserAttenuator', name='HardwareClassEnum'), nullable=False )
    hardware_type = Column(Text())
    hardware_model = Column(Text())
    machine_area = Column(Text())
    virtual_name = Column(Text())
    subelement = Column(Text())
    physical_id = Column(Integer(), ForeignKey('PhysicalElement.id'))
    physical = relationship("PhysicalElement", uselist=False, foreign_keys=[physical_id])
    simulation_id = Column(Integer(), ForeignKey('BeamBeamSimulationElement.id'))
    simulation = relationship("BeamBeamSimulationElement", uselist=False, foreign_keys=[simulation_id])
    electrical_id = Column(Integer(), ForeignKey('ElectricalElement.id'))
    electrical = relationship("ElectricalElement", uselist=False, foreign_keys=[electrical_id])
    manufacturer_id = Column(Integer(), ForeignKey('ManufacturerElement.id'))
    manufacturer = relationship("ManufacturerElement", uselist=False, foreign_keys=[manufacturer_id])
    controls_id = Column(Integer(), ForeignKey('ControlsInformation.id'))
    controls = relationship("ControlsInformation", uselist=False, foreign_keys=[controls_id])
    reference_id = Column(Integer(), ForeignKey('ReferenceElement.id'))
    reference = relationship("ReferenceElement", uselist=False, foreign_keys=[reference_id])
    
    
    alias_rel = relationship( "BeamBeamAlias" )
    alias = association_proxy("alias_rel", "alias",
                                  creator=lambda x_: BeamBeamAlias(alias=x_))
    
    
    inputs_rel = relationship( "BeamBeamInputs" )
    inputs = association_proxy("inputs_rel", "inputs",
                                  creator=lambda x_: BeamBeamInputs(inputs=x_))
    
    
    outputs_rel = relationship( "BeamBeamOutputs" )
    outputs = association_proxy("outputs_rel", "outputs",
                                  creator=lambda x_: BeamBeamOutputs(outputs=x_))
    
    
    # ManyToMany
    upstream = relationship( "AcceleratorElement", secondary="BeamBeam_upstream")
    
    
    # ManyToMany
    downstream = relationship( "AcceleratorElement", secondary="BeamBeam_downstream")
    

    def __repr__(self):
        return f"BeamBeam(name={self.name},hardware_class={self.hardware_class},hardware_type={self.hardware_type},hardware_model={self.hardware_model},machine_area={self.machine_area},virtual_name={self.virtual_name},subelement={self.subelement},physical_id={self.physical_id},simulation_id={self.simulation_id},electrical_id={self.electrical_id},manufacturer_id={self.manufacturer_id},controls_id={self.controls_id},reference_id={self.reference_id},)"



    
    # Using concrete inheritance: see https://docs.sqlalchemy.org/en/14/orm/inheritance.html
    __mapper_args__ = {
        'concrete': True
    }
    


class RFMultipole(PhysicalAcceleratorElement):
    """
    Thin RF-driven multipole kick.
    """
    __tablename__ = 'RFMultipole'

    name = Column(Text(), primary_key=True, nullable=False )
    hardware_class = Column(Enum('Magnet', 'Diagnostic', 'RF', 'Vacuum', 'Laser', 'Plasma', 'Feedback', 'Marker', 'Aperture', 'Stage', 'Lighting', 'Shutter', 'Wakefield', 'TwissMatch', 'Drift', 'Generic', 'Monitor', 'Simulation', 'Valve', 'LaserMirror', 'LaserEnergyMeter', 'LaserAttenuator', name='HardwareClassEnum'), nullable=False )
    hardware_type = Column(Text())
    hardware_model = Column(Text())
    machine_area = Column(Text())
    virtual_name = Column(Text())
    subelement = Column(Text())
    physical_id = Column(Integer(), ForeignKey('PhysicalElement.id'))
    physical = relationship("PhysicalElement", uselist=False, foreign_keys=[physical_id])
    simulation_id = Column(Integer(), ForeignKey('RFMultipoleSimulationElement.id'))
    simulation = relationship("RFMultipoleSimulationElement", uselist=False, foreign_keys=[simulation_id])
    electrical_id = Column(Integer(), ForeignKey('ElectricalElement.id'))
    electrical = relationship("ElectricalElement", uselist=False, foreign_keys=[electrical_id])
    manufacturer_id = Column(Integer(), ForeignKey('ManufacturerElement.id'))
    manufacturer = relationship("ManufacturerElement", uselist=False, foreign_keys=[manufacturer_id])
    controls_id = Column(Integer(), ForeignKey('ControlsInformation.id'))
    controls = relationship("ControlsInformation", uselist=False, foreign_keys=[controls_id])
    reference_id = Column(Integer(), ForeignKey('ReferenceElement.id'))
    reference = relationship("ReferenceElement", uselist=False, foreign_keys=[reference_id])
    
    
    alias_rel = relationship( "RFMultipoleAlias" )
    alias = association_proxy("alias_rel", "alias",
                                  creator=lambda x_: RFMultipoleAlias(alias=x_))
    
    
    inputs_rel = relationship( "RFMultipoleInputs" )
    inputs = association_proxy("inputs_rel", "inputs",
                                  creator=lambda x_: RFMultipoleInputs(inputs=x_))
    
    
    outputs_rel = relationship( "RFMultipoleOutputs" )
    outputs = association_proxy("outputs_rel", "outputs",
                                  creator=lambda x_: RFMultipoleOutputs(outputs=x_))
    
    
    # ManyToMany
    upstream = relationship( "AcceleratorElement", secondary="RFMultipole_upstream")
    
    
    # ManyToMany
    downstream = relationship( "AcceleratorElement", secondary="RFMultipole_downstream")
    

    def __repr__(self):
        return f"RFMultipole(name={self.name},hardware_class={self.hardware_class},hardware_type={self.hardware_type},hardware_model={self.hardware_model},machine_area={self.machine_area},virtual_name={self.virtual_name},subelement={self.subelement},physical_id={self.physical_id},simulation_id={self.simulation_id},electrical_id={self.electrical_id},manufacturer_id={self.manufacturer_id},controls_id={self.controls_id},reference_id={self.reference_id},)"



    
    # Using concrete inheritance: see https://docs.sqlalchemy.org/en/14/orm/inheritance.html
    __mapper_args__ = {
        'concrete': True
    }
    


class Stage(PhysicalAcceleratorElement):
    """
    Motorised positioning stage.
    """
    __tablename__ = 'Stage'

    name = Column(Text(), primary_key=True, nullable=False )
    hardware_class = Column(Enum('Magnet', 'Diagnostic', 'RF', 'Vacuum', 'Laser', 'Plasma', 'Feedback', 'Marker', 'Aperture', 'Stage', 'Lighting', 'Shutter', 'Wakefield', 'TwissMatch', 'Drift', 'Generic', 'Monitor', 'Simulation', 'Valve', 'LaserMirror', 'LaserEnergyMeter', 'LaserAttenuator', name='HardwareClassEnum'), nullable=False )
    hardware_type = Column(Text())
    hardware_model = Column(Text())
    machine_area = Column(Text())
    virtual_name = Column(Text())
    subelement = Column(Text())
    physical_id = Column(Integer(), ForeignKey('PhysicalElement.id'))
    physical = relationship("PhysicalElement", uselist=False, foreign_keys=[physical_id])
    simulation_id = Column(Integer(), ForeignKey('SimulationElement.id'))
    simulation = relationship("SimulationElement", uselist=False, foreign_keys=[simulation_id])
    electrical_id = Column(Integer(), ForeignKey('ElectricalElement.id'))
    electrical = relationship("ElectricalElement", uselist=False, foreign_keys=[electrical_id])
    manufacturer_id = Column(Integer(), ForeignKey('ManufacturerElement.id'))
    manufacturer = relationship("ManufacturerElement", uselist=False, foreign_keys=[manufacturer_id])
    controls_id = Column(Integer(), ForeignKey('ControlsInformation.id'))
    controls = relationship("ControlsInformation", uselist=False, foreign_keys=[controls_id])
    reference_id = Column(Integer(), ForeignKey('ReferenceElement.id'))
    reference = relationship("ReferenceElement", uselist=False, foreign_keys=[reference_id])
    
    
    alias_rel = relationship( "StageAlias" )
    alias = association_proxy("alias_rel", "alias",
                                  creator=lambda x_: StageAlias(alias=x_))
    
    
    inputs_rel = relationship( "StageInputs" )
    inputs = association_proxy("inputs_rel", "inputs",
                                  creator=lambda x_: StageInputs(inputs=x_))
    
    
    outputs_rel = relationship( "StageOutputs" )
    outputs = association_proxy("outputs_rel", "outputs",
                                  creator=lambda x_: StageOutputs(outputs=x_))
    
    
    # ManyToMany
    upstream = relationship( "AcceleratorElement", secondary="Stage_upstream")
    
    
    # ManyToMany
    downstream = relationship( "AcceleratorElement", secondary="Stage_downstream")
    

    def __repr__(self):
        return f"Stage(name={self.name},hardware_class={self.hardware_class},hardware_type={self.hardware_type},hardware_model={self.hardware_model},machine_area={self.machine_area},virtual_name={self.virtual_name},subelement={self.subelement},physical_id={self.physical_id},simulation_id={self.simulation_id},electrical_id={self.electrical_id},manufacturer_id={self.manufacturer_id},controls_id={self.controls_id},reference_id={self.reference_id},)"



    
    # Using concrete inheritance: see https://docs.sqlalchemy.org/en/14/orm/inheritance.html
    __mapper_args__ = {
        'concrete': True
    }
    


class VacuumGauge(PhysicalAcceleratorElement):
    """
    Vacuum-pressure gauge.
    """
    __tablename__ = 'VacuumGauge'

    name = Column(Text(), primary_key=True, nullable=False )
    hardware_class = Column(Enum('Magnet', 'Diagnostic', 'RF', 'Vacuum', 'Laser', 'Plasma', 'Feedback', 'Marker', 'Aperture', 'Stage', 'Lighting', 'Shutter', 'Wakefield', 'TwissMatch', 'Drift', 'Generic', 'Monitor', 'Simulation', 'Valve', 'LaserMirror', 'LaserEnergyMeter', 'LaserAttenuator', name='HardwareClassEnum'), nullable=False )
    hardware_type = Column(Text())
    hardware_model = Column(Text())
    machine_area = Column(Text())
    virtual_name = Column(Text())
    subelement = Column(Text())
    physical_id = Column(Integer(), ForeignKey('PhysicalElement.id'))
    physical = relationship("PhysicalElement", uselist=False, foreign_keys=[physical_id])
    simulation_id = Column(Integer(), ForeignKey('SimulationElement.id'))
    simulation = relationship("SimulationElement", uselist=False, foreign_keys=[simulation_id])
    electrical_id = Column(Integer(), ForeignKey('ElectricalElement.id'))
    electrical = relationship("ElectricalElement", uselist=False, foreign_keys=[electrical_id])
    manufacturer_id = Column(Integer(), ForeignKey('ManufacturerElement.id'))
    manufacturer = relationship("ManufacturerElement", uselist=False, foreign_keys=[manufacturer_id])
    controls_id = Column(Integer(), ForeignKey('ControlsInformation.id'))
    controls = relationship("ControlsInformation", uselist=False, foreign_keys=[controls_id])
    reference_id = Column(Integer(), ForeignKey('ReferenceElement.id'))
    reference = relationship("ReferenceElement", uselist=False, foreign_keys=[reference_id])
    
    
    alias_rel = relationship( "VacuumGaugeAlias" )
    alias = association_proxy("alias_rel", "alias",
                                  creator=lambda x_: VacuumGaugeAlias(alias=x_))
    
    
    inputs_rel = relationship( "VacuumGaugeInputs" )
    inputs = association_proxy("inputs_rel", "inputs",
                                  creator=lambda x_: VacuumGaugeInputs(inputs=x_))
    
    
    outputs_rel = relationship( "VacuumGaugeOutputs" )
    outputs = association_proxy("outputs_rel", "outputs",
                                  creator=lambda x_: VacuumGaugeOutputs(outputs=x_))
    
    
    # ManyToMany
    upstream = relationship( "AcceleratorElement", secondary="VacuumGauge_upstream")
    
    
    # ManyToMany
    downstream = relationship( "AcceleratorElement", secondary="VacuumGauge_downstream")
    

    def __repr__(self):
        return f"VacuumGauge(name={self.name},hardware_class={self.hardware_class},hardware_type={self.hardware_type},hardware_model={self.hardware_model},machine_area={self.machine_area},virtual_name={self.virtual_name},subelement={self.subelement},physical_id={self.physical_id},simulation_id={self.simulation_id},electrical_id={self.electrical_id},manufacturer_id={self.manufacturer_id},controls_id={self.controls_id},reference_id={self.reference_id},)"



    
    # Using concrete inheritance: see https://docs.sqlalchemy.org/en/14/orm/inheritance.html
    __mapper_args__ = {
        'concrete': True
    }
    


class Laser(PhysicalAcceleratorElement):
    """
    Laser system element (full laser setup including beam parameters).
    """
    __tablename__ = 'Laser'

    name = Column(Text(), primary_key=True, nullable=False )
    hardware_class = Column(Enum('Magnet', 'Diagnostic', 'RF', 'Vacuum', 'Laser', 'Plasma', 'Feedback', 'Marker', 'Aperture', 'Stage', 'Lighting', 'Shutter', 'Wakefield', 'TwissMatch', 'Drift', 'Generic', 'Monitor', 'Simulation', 'Valve', 'LaserMirror', 'LaserEnergyMeter', 'LaserAttenuator', name='HardwareClassEnum'), nullable=False )
    hardware_type = Column(Text())
    hardware_model = Column(Text())
    machine_area = Column(Text())
    virtual_name = Column(Text())
    subelement = Column(Text())
    laser_id = Column(Integer(), ForeignKey('LaserElement.id'))
    laser = relationship("LaserElement", uselist=False, foreign_keys=[laser_id])
    physical_id = Column(Integer(), ForeignKey('PhysicalElement.id'))
    physical = relationship("PhysicalElement", uselist=False, foreign_keys=[physical_id])
    simulation_id = Column(Integer(), ForeignKey('SimulationElement.id'))
    simulation = relationship("SimulationElement", uselist=False, foreign_keys=[simulation_id])
    electrical_id = Column(Integer(), ForeignKey('ElectricalElement.id'))
    electrical = relationship("ElectricalElement", uselist=False, foreign_keys=[electrical_id])
    manufacturer_id = Column(Integer(), ForeignKey('ManufacturerElement.id'))
    manufacturer = relationship("ManufacturerElement", uselist=False, foreign_keys=[manufacturer_id])
    controls_id = Column(Integer(), ForeignKey('ControlsInformation.id'))
    controls = relationship("ControlsInformation", uselist=False, foreign_keys=[controls_id])
    reference_id = Column(Integer(), ForeignKey('ReferenceElement.id'))
    reference = relationship("ReferenceElement", uselist=False, foreign_keys=[reference_id])
    
    
    alias_rel = relationship( "LaserAlias" )
    alias = association_proxy("alias_rel", "alias",
                                  creator=lambda x_: LaserAlias(alias=x_))
    
    
    inputs_rel = relationship( "LaserInputs" )
    inputs = association_proxy("inputs_rel", "inputs",
                                  creator=lambda x_: LaserInputs(inputs=x_))
    
    
    outputs_rel = relationship( "LaserOutputs" )
    outputs = association_proxy("outputs_rel", "outputs",
                                  creator=lambda x_: LaserOutputs(outputs=x_))
    
    
    # ManyToMany
    upstream = relationship( "AcceleratorElement", secondary="Laser_upstream")
    
    
    # ManyToMany
    downstream = relationship( "AcceleratorElement", secondary="Laser_downstream")
    

    def __repr__(self):
        return f"Laser(name={self.name},hardware_class={self.hardware_class},hardware_type={self.hardware_type},hardware_model={self.hardware_model},machine_area={self.machine_area},virtual_name={self.virtual_name},subelement={self.subelement},laser_id={self.laser_id},physical_id={self.physical_id},simulation_id={self.simulation_id},electrical_id={self.electrical_id},manufacturer_id={self.manufacturer_id},controls_id={self.controls_id},reference_id={self.reference_id},)"



    
    # Using concrete inheritance: see https://docs.sqlalchemy.org/en/14/orm/inheritance.html
    __mapper_args__ = {
        'concrete': True
    }
    


class Shutter(PhysicalAcceleratorElement):
    """
    Beam or laser shutter with interlock logic.
    """
    __tablename__ = 'Shutter'

    name = Column(Text(), primary_key=True, nullable=False )
    hardware_class = Column(Enum('Magnet', 'Diagnostic', 'RF', 'Vacuum', 'Laser', 'Plasma', 'Feedback', 'Marker', 'Aperture', 'Stage', 'Lighting', 'Shutter', 'Wakefield', 'TwissMatch', 'Drift', 'Generic', 'Monitor', 'Simulation', 'Valve', 'LaserMirror', 'LaserEnergyMeter', 'LaserAttenuator', name='HardwareClassEnum'), nullable=False )
    hardware_type = Column(Text())
    hardware_model = Column(Text())
    machine_area = Column(Text())
    virtual_name = Column(Text())
    subelement = Column(Text())
    shutter_id = Column(Integer(), ForeignKey('ShutterElement.id'))
    shutter = relationship("ShutterElement", uselist=False, foreign_keys=[shutter_id])
    physical_id = Column(Integer(), ForeignKey('PhysicalElement.id'))
    physical = relationship("PhysicalElement", uselist=False, foreign_keys=[physical_id])
    simulation_id = Column(Integer(), ForeignKey('SimulationElement.id'))
    simulation = relationship("SimulationElement", uselist=False, foreign_keys=[simulation_id])
    electrical_id = Column(Integer(), ForeignKey('ElectricalElement.id'))
    electrical = relationship("ElectricalElement", uselist=False, foreign_keys=[electrical_id])
    manufacturer_id = Column(Integer(), ForeignKey('ManufacturerElement.id'))
    manufacturer = relationship("ManufacturerElement", uselist=False, foreign_keys=[manufacturer_id])
    controls_id = Column(Integer(), ForeignKey('ControlsInformation.id'))
    controls = relationship("ControlsInformation", uselist=False, foreign_keys=[controls_id])
    reference_id = Column(Integer(), ForeignKey('ReferenceElement.id'))
    reference = relationship("ReferenceElement", uselist=False, foreign_keys=[reference_id])
    
    
    alias_rel = relationship( "ShutterAlias" )
    alias = association_proxy("alias_rel", "alias",
                                  creator=lambda x_: ShutterAlias(alias=x_))
    
    
    inputs_rel = relationship( "ShutterInputs" )
    inputs = association_proxy("inputs_rel", "inputs",
                                  creator=lambda x_: ShutterInputs(inputs=x_))
    
    
    outputs_rel = relationship( "ShutterOutputs" )
    outputs = association_proxy("outputs_rel", "outputs",
                                  creator=lambda x_: ShutterOutputs(outputs=x_))
    
    
    # ManyToMany
    upstream = relationship( "AcceleratorElement", secondary="Shutter_upstream")
    
    
    # ManyToMany
    downstream = relationship( "AcceleratorElement", secondary="Shutter_downstream")
    

    def __repr__(self):
        return f"Shutter(name={self.name},hardware_class={self.hardware_class},hardware_type={self.hardware_type},hardware_model={self.hardware_model},machine_area={self.machine_area},virtual_name={self.virtual_name},subelement={self.subelement},shutter_id={self.shutter_id},physical_id={self.physical_id},simulation_id={self.simulation_id},electrical_id={self.electrical_id},manufacturer_id={self.manufacturer_id},controls_id={self.controls_id},reference_id={self.reference_id},)"



    
    # Using concrete inheritance: see https://docs.sqlalchemy.org/en/14/orm/inheritance.html
    __mapper_args__ = {
        'concrete': True
    }
    


class Valve(PhysicalAcceleratorElement):
    """
    Vacuum gate valve.
    """
    __tablename__ = 'Valve'

    name = Column(Text(), primary_key=True, nullable=False )
    hardware_class = Column(Enum('Magnet', 'Diagnostic', 'RF', 'Vacuum', 'Laser', 'Plasma', 'Feedback', 'Marker', 'Aperture', 'Stage', 'Lighting', 'Shutter', 'Wakefield', 'TwissMatch', 'Drift', 'Generic', 'Monitor', 'Simulation', 'Valve', 'LaserMirror', 'LaserEnergyMeter', 'LaserAttenuator', name='HardwareClassEnum'), nullable=False )
    hardware_type = Column(Text())
    hardware_model = Column(Text())
    machine_area = Column(Text())
    virtual_name = Column(Text())
    subelement = Column(Text())
    valve_id = Column(Integer(), ForeignKey('ValveElement.id'))
    valve = relationship("ValveElement", uselist=False, foreign_keys=[valve_id])
    physical_id = Column(Integer(), ForeignKey('PhysicalElement.id'))
    physical = relationship("PhysicalElement", uselist=False, foreign_keys=[physical_id])
    simulation_id = Column(Integer(), ForeignKey('SimulationElement.id'))
    simulation = relationship("SimulationElement", uselist=False, foreign_keys=[simulation_id])
    electrical_id = Column(Integer(), ForeignKey('ElectricalElement.id'))
    electrical = relationship("ElectricalElement", uselist=False, foreign_keys=[electrical_id])
    manufacturer_id = Column(Integer(), ForeignKey('ManufacturerElement.id'))
    manufacturer = relationship("ManufacturerElement", uselist=False, foreign_keys=[manufacturer_id])
    controls_id = Column(Integer(), ForeignKey('ControlsInformation.id'))
    controls = relationship("ControlsInformation", uselist=False, foreign_keys=[controls_id])
    reference_id = Column(Integer(), ForeignKey('ReferenceElement.id'))
    reference = relationship("ReferenceElement", uselist=False, foreign_keys=[reference_id])
    
    
    alias_rel = relationship( "ValveAlias" )
    alias = association_proxy("alias_rel", "alias",
                                  creator=lambda x_: ValveAlias(alias=x_))
    
    
    inputs_rel = relationship( "ValveInputs" )
    inputs = association_proxy("inputs_rel", "inputs",
                                  creator=lambda x_: ValveInputs(inputs=x_))
    
    
    outputs_rel = relationship( "ValveOutputs" )
    outputs = association_proxy("outputs_rel", "outputs",
                                  creator=lambda x_: ValveOutputs(outputs=x_))
    
    
    # ManyToMany
    upstream = relationship( "AcceleratorElement", secondary="Valve_upstream")
    
    
    # ManyToMany
    downstream = relationship( "AcceleratorElement", secondary="Valve_downstream")
    

    def __repr__(self):
        return f"Valve(name={self.name},hardware_class={self.hardware_class},hardware_type={self.hardware_type},hardware_model={self.hardware_model},machine_area={self.machine_area},virtual_name={self.virtual_name},subelement={self.subelement},valve_id={self.valve_id},physical_id={self.physical_id},simulation_id={self.simulation_id},electrical_id={self.electrical_id},manufacturer_id={self.manufacturer_id},controls_id={self.controls_id},reference_id={self.reference_id},)"



    
    # Using concrete inheritance: see https://docs.sqlalchemy.org/en/14/orm/inheritance.html
    __mapper_args__ = {
        'concrete': True
    }
    


class Marker(PhysicalAcceleratorElement):
    """
    Virtual survey marker -- a zero-length reference point used for alignment.
    """
    __tablename__ = 'Marker'

    name = Column(Text(), primary_key=True, nullable=False )
    hardware_class = Column(Enum('Magnet', 'Diagnostic', 'RF', 'Vacuum', 'Laser', 'Plasma', 'Feedback', 'Marker', 'Aperture', 'Stage', 'Lighting', 'Shutter', 'Wakefield', 'TwissMatch', 'Drift', 'Generic', 'Monitor', 'Simulation', 'Valve', 'LaserMirror', 'LaserEnergyMeter', 'LaserAttenuator', name='HardwareClassEnum'), nullable=False )
    hardware_type = Column(Text())
    hardware_model = Column(Text())
    machine_area = Column(Text())
    virtual_name = Column(Text())
    subelement = Column(Text())
    physical_id = Column(Integer(), ForeignKey('PhysicalElement.id'))
    physical = relationship("PhysicalElement", uselist=False, foreign_keys=[physical_id])
    simulation_id = Column(Integer(), ForeignKey('SimulationElement.id'))
    simulation = relationship("SimulationElement", uselist=False, foreign_keys=[simulation_id])
    electrical_id = Column(Integer(), ForeignKey('ElectricalElement.id'))
    electrical = relationship("ElectricalElement", uselist=False, foreign_keys=[electrical_id])
    manufacturer_id = Column(Integer(), ForeignKey('ManufacturerElement.id'))
    manufacturer = relationship("ManufacturerElement", uselist=False, foreign_keys=[manufacturer_id])
    controls_id = Column(Integer(), ForeignKey('ControlsInformation.id'))
    controls = relationship("ControlsInformation", uselist=False, foreign_keys=[controls_id])
    reference_id = Column(Integer(), ForeignKey('ReferenceElement.id'))
    reference = relationship("ReferenceElement", uselist=False, foreign_keys=[reference_id])
    
    
    alias_rel = relationship( "MarkerAlias" )
    alias = association_proxy("alias_rel", "alias",
                                  creator=lambda x_: MarkerAlias(alias=x_))
    
    
    inputs_rel = relationship( "MarkerInputs" )
    inputs = association_proxy("inputs_rel", "inputs",
                                  creator=lambda x_: MarkerInputs(inputs=x_))
    
    
    outputs_rel = relationship( "MarkerOutputs" )
    outputs = association_proxy("outputs_rel", "outputs",
                                  creator=lambda x_: MarkerOutputs(outputs=x_))
    
    
    # ManyToMany
    upstream = relationship( "AcceleratorElement", secondary="Marker_upstream")
    
    
    # ManyToMany
    downstream = relationship( "AcceleratorElement", secondary="Marker_downstream")
    

    def __repr__(self):
        return f"Marker(name={self.name},hardware_class={self.hardware_class},hardware_type={self.hardware_type},hardware_model={self.hardware_model},machine_area={self.machine_area},virtual_name={self.virtual_name},subelement={self.subelement},physical_id={self.physical_id},simulation_id={self.simulation_id},electrical_id={self.electrical_id},manufacturer_id={self.manufacturer_id},controls_id={self.controls_id},reference_id={self.reference_id},)"



    
    # Using concrete inheritance: see https://docs.sqlalchemy.org/en/14/orm/inheritance.html
    __mapper_args__ = {
        'concrete': True
    }
    


class Aperture(PhysicalAcceleratorElement):
    """
    Mechanical aperture restriction in the beam pipe.
    """
    __tablename__ = 'Aperture'

    name = Column(Text(), primary_key=True, nullable=False )
    hardware_class = Column(Enum('Magnet', 'Diagnostic', 'RF', 'Vacuum', 'Laser', 'Plasma', 'Feedback', 'Marker', 'Aperture', 'Stage', 'Lighting', 'Shutter', 'Wakefield', 'TwissMatch', 'Drift', 'Generic', 'Monitor', 'Simulation', 'Valve', 'LaserMirror', 'LaserEnergyMeter', 'LaserAttenuator', name='HardwareClassEnum'), nullable=False )
    hardware_type = Column(Text())
    hardware_model = Column(Text())
    machine_area = Column(Text())
    virtual_name = Column(Text())
    subelement = Column(Text())
    aperture_id = Column(Integer(), ForeignKey('ApertureElement.id'))
    aperture = relationship("ApertureElement", uselist=False, foreign_keys=[aperture_id])
    physical_id = Column(Integer(), ForeignKey('PhysicalElement.id'))
    physical = relationship("PhysicalElement", uselist=False, foreign_keys=[physical_id])
    simulation_id = Column(Integer(), ForeignKey('SimulationElement.id'))
    simulation = relationship("SimulationElement", uselist=False, foreign_keys=[simulation_id])
    electrical_id = Column(Integer(), ForeignKey('ElectricalElement.id'))
    electrical = relationship("ElectricalElement", uselist=False, foreign_keys=[electrical_id])
    manufacturer_id = Column(Integer(), ForeignKey('ManufacturerElement.id'))
    manufacturer = relationship("ManufacturerElement", uselist=False, foreign_keys=[manufacturer_id])
    controls_id = Column(Integer(), ForeignKey('ControlsInformation.id'))
    controls = relationship("ControlsInformation", uselist=False, foreign_keys=[controls_id])
    reference_id = Column(Integer(), ForeignKey('ReferenceElement.id'))
    reference = relationship("ReferenceElement", uselist=False, foreign_keys=[reference_id])
    
    
    alias_rel = relationship( "ApertureAlias" )
    alias = association_proxy("alias_rel", "alias",
                                  creator=lambda x_: ApertureAlias(alias=x_))
    
    
    inputs_rel = relationship( "ApertureInputs" )
    inputs = association_proxy("inputs_rel", "inputs",
                                  creator=lambda x_: ApertureInputs(inputs=x_))
    
    
    outputs_rel = relationship( "ApertureOutputs" )
    outputs = association_proxy("outputs_rel", "outputs",
                                  creator=lambda x_: ApertureOutputs(outputs=x_))
    
    
    # ManyToMany
    upstream = relationship( "AcceleratorElement", secondary="Aperture_upstream")
    
    
    # ManyToMany
    downstream = relationship( "AcceleratorElement", secondary="Aperture_downstream")
    

    def __repr__(self):
        return f"Aperture(name={self.name},hardware_class={self.hardware_class},hardware_type={self.hardware_type},hardware_model={self.hardware_model},machine_area={self.machine_area},virtual_name={self.virtual_name},subelement={self.subelement},aperture_id={self.aperture_id},physical_id={self.physical_id},simulation_id={self.simulation_id},electrical_id={self.electrical_id},manufacturer_id={self.manufacturer_id},controls_id={self.controls_id},reference_id={self.reference_id},)"



    
    # Using concrete inheritance: see https://docs.sqlalchemy.org/en/14/orm/inheritance.html
    __mapper_args__ = {
        'concrete': True
    }
    


class Drift(PhysicalAcceleratorElement):
    """
    Field-free drift space between elements.
    """
    __tablename__ = 'Drift'

    name = Column(Text(), primary_key=True, nullable=False )
    hardware_class = Column(Enum('Magnet', 'Diagnostic', 'RF', 'Vacuum', 'Laser', 'Plasma', 'Feedback', 'Marker', 'Aperture', 'Stage', 'Lighting', 'Shutter', 'Wakefield', 'TwissMatch', 'Drift', 'Generic', 'Monitor', 'Simulation', 'Valve', 'LaserMirror', 'LaserEnergyMeter', 'LaserAttenuator', name='HardwareClassEnum'), nullable=False )
    hardware_type = Column(Text())
    hardware_model = Column(Text())
    machine_area = Column(Text())
    virtual_name = Column(Text())
    subelement = Column(Text())
    physical_id = Column(Integer(), ForeignKey('PhysicalElement.id'))
    physical = relationship("PhysicalElement", uselist=False, foreign_keys=[physical_id])
    simulation_id = Column(Integer(), ForeignKey('DriftSimulationElement.id'))
    simulation = relationship("DriftSimulationElement", uselist=False, foreign_keys=[simulation_id])
    electrical_id = Column(Integer(), ForeignKey('ElectricalElement.id'))
    electrical = relationship("ElectricalElement", uselist=False, foreign_keys=[electrical_id])
    manufacturer_id = Column(Integer(), ForeignKey('ManufacturerElement.id'))
    manufacturer = relationship("ManufacturerElement", uselist=False, foreign_keys=[manufacturer_id])
    controls_id = Column(Integer(), ForeignKey('ControlsInformation.id'))
    controls = relationship("ControlsInformation", uselist=False, foreign_keys=[controls_id])
    reference_id = Column(Integer(), ForeignKey('ReferenceElement.id'))
    reference = relationship("ReferenceElement", uselist=False, foreign_keys=[reference_id])
    
    
    alias_rel = relationship( "DriftAlias" )
    alias = association_proxy("alias_rel", "alias",
                                  creator=lambda x_: DriftAlias(alias=x_))
    
    
    inputs_rel = relationship( "DriftInputs" )
    inputs = association_proxy("inputs_rel", "inputs",
                                  creator=lambda x_: DriftInputs(inputs=x_))
    
    
    outputs_rel = relationship( "DriftOutputs" )
    outputs = association_proxy("outputs_rel", "outputs",
                                  creator=lambda x_: DriftOutputs(outputs=x_))
    
    
    # ManyToMany
    upstream = relationship( "AcceleratorElement", secondary="Drift_upstream")
    
    
    # ManyToMany
    downstream = relationship( "AcceleratorElement", secondary="Drift_downstream")
    

    def __repr__(self):
        return f"Drift(name={self.name},hardware_class={self.hardware_class},hardware_type={self.hardware_type},hardware_model={self.hardware_model},machine_area={self.machine_area},virtual_name={self.virtual_name},subelement={self.subelement},physical_id={self.physical_id},simulation_id={self.simulation_id},electrical_id={self.electrical_id},manufacturer_id={self.manufacturer_id},controls_id={self.controls_id},reference_id={self.reference_id},)"



    
    # Using concrete inheritance: see https://docs.sqlalchemy.org/en/14/orm/inheritance.html
    __mapper_args__ = {
        'concrete': True
    }
    


class Magnet(PhysicalAcceleratorElement):
    """
    Base class for all magnetic focusing and bending elements. (Named ``MagnetBaseElement`` in the schema to avoid collision with the ``magnetic`` composition-model class; maps to ``Magnet`` in Python.)
    """
    __tablename__ = 'Magnet'

    name = Column(Text(), primary_key=True, nullable=False )
    hardware_class = Column(Enum('Magnet', 'Diagnostic', 'RF', 'Vacuum', 'Laser', 'Plasma', 'Feedback', 'Marker', 'Aperture', 'Stage', 'Lighting', 'Shutter', 'Wakefield', 'TwissMatch', 'Drift', 'Generic', 'Monitor', 'Simulation', 'Valve', 'LaserMirror', 'LaserEnergyMeter', 'LaserAttenuator', name='HardwareClassEnum'), nullable=False )
    hardware_type = Column(Text())
    hardware_model = Column(Text())
    machine_area = Column(Text())
    virtual_name = Column(Text())
    subelement = Column(Text())
    magnetic_id = Column(Integer(), ForeignKey('MagneticElement.id'))
    magnetic = relationship("MagneticElement", uselist=False, foreign_keys=[magnetic_id])
    degauss_id = Column(Integer(), ForeignKey('DegaussableElement.id'))
    degauss = relationship("DegaussableElement", uselist=False, foreign_keys=[degauss_id])
    physical_id = Column(Integer(), ForeignKey('PhysicalElement.id'))
    physical = relationship("PhysicalElement", uselist=False, foreign_keys=[physical_id])
    simulation_id = Column(Integer(), ForeignKey('MagnetSimulationElement.id'))
    simulation = relationship("MagnetSimulationElement", uselist=False, foreign_keys=[simulation_id])
    electrical_id = Column(Integer(), ForeignKey('ElectricalElement.id'))
    electrical = relationship("ElectricalElement", uselist=False, foreign_keys=[electrical_id])
    manufacturer_id = Column(Integer(), ForeignKey('ManufacturerElement.id'))
    manufacturer = relationship("ManufacturerElement", uselist=False, foreign_keys=[manufacturer_id])
    controls_id = Column(Integer(), ForeignKey('ControlsInformation.id'))
    controls = relationship("ControlsInformation", uselist=False, foreign_keys=[controls_id])
    reference_id = Column(Integer(), ForeignKey('ReferenceElement.id'))
    reference = relationship("ReferenceElement", uselist=False, foreign_keys=[reference_id])
    
    
    alias_rel = relationship( "MagnetAlias" )
    alias = association_proxy("alias_rel", "alias",
                                  creator=lambda x_: MagnetAlias(alias=x_))
    
    
    inputs_rel = relationship( "MagnetInputs" )
    inputs = association_proxy("inputs_rel", "inputs",
                                  creator=lambda x_: MagnetInputs(inputs=x_))
    
    
    outputs_rel = relationship( "MagnetOutputs" )
    outputs = association_proxy("outputs_rel", "outputs",
                                  creator=lambda x_: MagnetOutputs(outputs=x_))
    
    
    # ManyToMany
    upstream = relationship( "AcceleratorElement", secondary="Magnet_upstream")
    
    
    # ManyToMany
    downstream = relationship( "AcceleratorElement", secondary="Magnet_downstream")
    

    def __repr__(self):
        return f"Magnet(name={self.name},hardware_class={self.hardware_class},hardware_type={self.hardware_type},hardware_model={self.hardware_model},machine_area={self.machine_area},virtual_name={self.virtual_name},subelement={self.subelement},magnetic_id={self.magnetic_id},degauss_id={self.degauss_id},physical_id={self.physical_id},simulation_id={self.simulation_id},electrical_id={self.electrical_id},manufacturer_id={self.manufacturer_id},controls_id={self.controls_id},reference_id={self.reference_id},)"



    
    # Using concrete inheritance: see https://docs.sqlalchemy.org/en/14/orm/inheritance.html
    __mapper_args__ = {
        'concrete': True
    }
    


class RFCavity(PhysicalAcceleratorElement):
    """
    Accelerating RF cavity.
    """
    __tablename__ = 'RFCavity'

    name = Column(Text(), primary_key=True, nullable=False )
    hardware_class = Column(Enum('Magnet', 'Diagnostic', 'RF', 'Vacuum', 'Laser', 'Plasma', 'Feedback', 'Marker', 'Aperture', 'Stage', 'Lighting', 'Shutter', 'Wakefield', 'TwissMatch', 'Drift', 'Generic', 'Monitor', 'Simulation', 'Valve', 'LaserMirror', 'LaserEnergyMeter', 'LaserAttenuator', name='HardwareClassEnum'), nullable=False )
    hardware_type = Column(Text())
    hardware_model = Column(Text())
    machine_area = Column(Text())
    virtual_name = Column(Text())
    subelement = Column(Text())
    cavity_id = Column(Integer(), ForeignKey('RFCavityElement.id'))
    cavity = relationship("RFCavityElement", uselist=False, foreign_keys=[cavity_id])
    physical_id = Column(Integer(), ForeignKey('PhysicalElement.id'))
    physical = relationship("PhysicalElement", uselist=False, foreign_keys=[physical_id])
    simulation_id = Column(Integer(), ForeignKey('RFCavitySimulationElement.id'))
    simulation = relationship("RFCavitySimulationElement", uselist=False, foreign_keys=[simulation_id])
    electrical_id = Column(Integer(), ForeignKey('ElectricalElement.id'))
    electrical = relationship("ElectricalElement", uselist=False, foreign_keys=[electrical_id])
    manufacturer_id = Column(Integer(), ForeignKey('ManufacturerElement.id'))
    manufacturer = relationship("ManufacturerElement", uselist=False, foreign_keys=[manufacturer_id])
    controls_id = Column(Integer(), ForeignKey('ControlsInformation.id'))
    controls = relationship("ControlsInformation", uselist=False, foreign_keys=[controls_id])
    reference_id = Column(Integer(), ForeignKey('ReferenceElement.id'))
    reference = relationship("ReferenceElement", uselist=False, foreign_keys=[reference_id])
    
    
    alias_rel = relationship( "RFCavityAlias" )
    alias = association_proxy("alias_rel", "alias",
                                  creator=lambda x_: RFCavityAlias(alias=x_))
    
    
    inputs_rel = relationship( "RFCavityInputs" )
    inputs = association_proxy("inputs_rel", "inputs",
                                  creator=lambda x_: RFCavityInputs(inputs=x_))
    
    
    outputs_rel = relationship( "RFCavityOutputs" )
    outputs = association_proxy("outputs_rel", "outputs",
                                  creator=lambda x_: RFCavityOutputs(outputs=x_))
    
    
    # ManyToMany
    upstream = relationship( "AcceleratorElement", secondary="RFCavity_upstream")
    
    
    # ManyToMany
    downstream = relationship( "AcceleratorElement", secondary="RFCavity_downstream")
    

    def __repr__(self):
        return f"RFCavity(name={self.name},hardware_class={self.hardware_class},hardware_type={self.hardware_type},hardware_model={self.hardware_model},machine_area={self.machine_area},virtual_name={self.virtual_name},subelement={self.subelement},cavity_id={self.cavity_id},physical_id={self.physical_id},simulation_id={self.simulation_id},electrical_id={self.electrical_id},manufacturer_id={self.manufacturer_id},controls_id={self.controls_id},reference_id={self.reference_id},)"



    
    # Using concrete inheritance: see https://docs.sqlalchemy.org/en/14/orm/inheritance.html
    __mapper_args__ = {
        'concrete': True
    }
    


class Wakefield(PhysicalAcceleratorElement):
    """
    Passive wakefield structure (dielectric, corrugated, etc.).
    """
    __tablename__ = 'Wakefield'

    name = Column(Text(), primary_key=True, nullable=False )
    hardware_class = Column(Enum('Magnet', 'Diagnostic', 'RF', 'Vacuum', 'Laser', 'Plasma', 'Feedback', 'Marker', 'Aperture', 'Stage', 'Lighting', 'Shutter', 'Wakefield', 'TwissMatch', 'Drift', 'Generic', 'Monitor', 'Simulation', 'Valve', 'LaserMirror', 'LaserEnergyMeter', 'LaserAttenuator', name='HardwareClassEnum'), nullable=False )
    hardware_type = Column(Text())
    hardware_model = Column(Text())
    machine_area = Column(Text())
    virtual_name = Column(Text())
    subelement = Column(Text())
    cavity_id = Column(Integer(), ForeignKey('WakefieldElement.id'))
    cavity = relationship("WakefieldElement", uselist=False, foreign_keys=[cavity_id])
    physical_id = Column(Integer(), ForeignKey('PhysicalElement.id'))
    physical = relationship("PhysicalElement", uselist=False, foreign_keys=[physical_id])
    simulation_id = Column(Integer(), ForeignKey('WakefieldSimulationElement.id'))
    simulation = relationship("WakefieldSimulationElement", uselist=False, foreign_keys=[simulation_id])
    electrical_id = Column(Integer(), ForeignKey('ElectricalElement.id'))
    electrical = relationship("ElectricalElement", uselist=False, foreign_keys=[electrical_id])
    manufacturer_id = Column(Integer(), ForeignKey('ManufacturerElement.id'))
    manufacturer = relationship("ManufacturerElement", uselist=False, foreign_keys=[manufacturer_id])
    controls_id = Column(Integer(), ForeignKey('ControlsInformation.id'))
    controls = relationship("ControlsInformation", uselist=False, foreign_keys=[controls_id])
    reference_id = Column(Integer(), ForeignKey('ReferenceElement.id'))
    reference = relationship("ReferenceElement", uselist=False, foreign_keys=[reference_id])
    
    
    alias_rel = relationship( "WakefieldAlias" )
    alias = association_proxy("alias_rel", "alias",
                                  creator=lambda x_: WakefieldAlias(alias=x_))
    
    
    inputs_rel = relationship( "WakefieldInputs" )
    inputs = association_proxy("inputs_rel", "inputs",
                                  creator=lambda x_: WakefieldInputs(inputs=x_))
    
    
    outputs_rel = relationship( "WakefieldOutputs" )
    outputs = association_proxy("outputs_rel", "outputs",
                                  creator=lambda x_: WakefieldOutputs(outputs=x_))
    
    
    # ManyToMany
    upstream = relationship( "AcceleratorElement", secondary="Wakefield_upstream")
    
    
    # ManyToMany
    downstream = relationship( "AcceleratorElement", secondary="Wakefield_downstream")
    

    def __repr__(self):
        return f"Wakefield(name={self.name},hardware_class={self.hardware_class},hardware_type={self.hardware_type},hardware_model={self.hardware_model},machine_area={self.machine_area},virtual_name={self.virtual_name},subelement={self.subelement},cavity_id={self.cavity_id},physical_id={self.physical_id},simulation_id={self.simulation_id},electrical_id={self.electrical_id},manufacturer_id={self.manufacturer_id},controls_id={self.controls_id},reference_id={self.reference_id},)"



    
    # Using concrete inheritance: see https://docs.sqlalchemy.org/en/14/orm/inheritance.html
    __mapper_args__ = {
        'concrete': True
    }
    


class Diagnostic(PhysicalAcceleratorElement):
    """
    Base class for all beam-diagnostic instruments.
    """
    __tablename__ = 'Diagnostic'

    name = Column(Text(), primary_key=True, nullable=False )
    hardware_class = Column(Enum('Magnet', 'Diagnostic', 'RF', 'Vacuum', 'Laser', 'Plasma', 'Feedback', 'Marker', 'Aperture', 'Stage', 'Lighting', 'Shutter', 'Wakefield', 'TwissMatch', 'Drift', 'Generic', 'Monitor', 'Simulation', 'Valve', 'LaserMirror', 'LaserEnergyMeter', 'LaserAttenuator', name='HardwareClassEnum'), nullable=False )
    hardware_type = Column(Text())
    hardware_model = Column(Text())
    machine_area = Column(Text())
    virtual_name = Column(Text())
    subelement = Column(Text())
    diagnostic_id = Column(Integer(), ForeignKey('DiagnosticElement.id'))
    diagnostic = relationship("DiagnosticElement", uselist=False, foreign_keys=[diagnostic_id])
    physical_id = Column(Integer(), ForeignKey('PhysicalElement.id'))
    physical = relationship("PhysicalElement", uselist=False, foreign_keys=[physical_id])
    simulation_id = Column(Integer(), ForeignKey('DiagnosticSimulationElement.id'))
    simulation = relationship("DiagnosticSimulationElement", uselist=False, foreign_keys=[simulation_id])
    electrical_id = Column(Integer(), ForeignKey('ElectricalElement.id'))
    electrical = relationship("ElectricalElement", uselist=False, foreign_keys=[electrical_id])
    manufacturer_id = Column(Integer(), ForeignKey('ManufacturerElement.id'))
    manufacturer = relationship("ManufacturerElement", uselist=False, foreign_keys=[manufacturer_id])
    controls_id = Column(Integer(), ForeignKey('ControlsInformation.id'))
    controls = relationship("ControlsInformation", uselist=False, foreign_keys=[controls_id])
    reference_id = Column(Integer(), ForeignKey('ReferenceElement.id'))
    reference = relationship("ReferenceElement", uselist=False, foreign_keys=[reference_id])
    
    
    alias_rel = relationship( "DiagnosticAlias" )
    alias = association_proxy("alias_rel", "alias",
                                  creator=lambda x_: DiagnosticAlias(alias=x_))
    
    
    inputs_rel = relationship( "DiagnosticInputs" )
    inputs = association_proxy("inputs_rel", "inputs",
                                  creator=lambda x_: DiagnosticInputs(inputs=x_))
    
    
    outputs_rel = relationship( "DiagnosticOutputs" )
    outputs = association_proxy("outputs_rel", "outputs",
                                  creator=lambda x_: DiagnosticOutputs(outputs=x_))
    
    
    # ManyToMany
    upstream = relationship( "AcceleratorElement", secondary="Diagnostic_upstream")
    
    
    # ManyToMany
    downstream = relationship( "AcceleratorElement", secondary="Diagnostic_downstream")
    

    def __repr__(self):
        return f"Diagnostic(name={self.name},hardware_class={self.hardware_class},hardware_type={self.hardware_type},hardware_model={self.hardware_model},machine_area={self.machine_area},virtual_name={self.virtual_name},subelement={self.subelement},diagnostic_id={self.diagnostic_id},physical_id={self.physical_id},simulation_id={self.simulation_id},electrical_id={self.electrical_id},manufacturer_id={self.manufacturer_id},controls_id={self.controls_id},reference_id={self.reference_id},)"



    
    # Using concrete inheritance: see https://docs.sqlalchemy.org/en/14/orm/inheritance.html
    __mapper_args__ = {
        'concrete': True
    }
    


class Plasma(PhysicalAcceleratorElement):
    """
    Laser-driven plasma-accelerator stage.
    """
    __tablename__ = 'Plasma'

    name = Column(Text(), primary_key=True, nullable=False )
    hardware_class = Column(Enum('Magnet', 'Diagnostic', 'RF', 'Vacuum', 'Laser', 'Plasma', 'Feedback', 'Marker', 'Aperture', 'Stage', 'Lighting', 'Shutter', 'Wakefield', 'TwissMatch', 'Drift', 'Generic', 'Monitor', 'Simulation', 'Valve', 'LaserMirror', 'LaserEnergyMeter', 'LaserAttenuator', name='HardwareClassEnum'), nullable=False )
    hardware_type = Column(Text())
    hardware_model = Column(Text())
    machine_area = Column(Text())
    virtual_name = Column(Text())
    subelement = Column(Text())
    plasma_id = Column(Integer(), ForeignKey('PlasmaElement.id'))
    plasma = relationship("PlasmaElement", uselist=False, foreign_keys=[plasma_id])
    laser_id = Column(Integer(), ForeignKey('LaserElement.id'))
    laser = relationship("LaserElement", uselist=False, foreign_keys=[laser_id])
    physical_id = Column(Integer(), ForeignKey('PhysicalElement.id'))
    physical = relationship("PhysicalElement", uselist=False, foreign_keys=[physical_id])
    simulation_id = Column(Integer(), ForeignKey('PlasmaSimulationElement.id'))
    simulation = relationship("PlasmaSimulationElement", uselist=False, foreign_keys=[simulation_id])
    electrical_id = Column(Integer(), ForeignKey('ElectricalElement.id'))
    electrical = relationship("ElectricalElement", uselist=False, foreign_keys=[electrical_id])
    manufacturer_id = Column(Integer(), ForeignKey('ManufacturerElement.id'))
    manufacturer = relationship("ManufacturerElement", uselist=False, foreign_keys=[manufacturer_id])
    controls_id = Column(Integer(), ForeignKey('ControlsInformation.id'))
    controls = relationship("ControlsInformation", uselist=False, foreign_keys=[controls_id])
    reference_id = Column(Integer(), ForeignKey('ReferenceElement.id'))
    reference = relationship("ReferenceElement", uselist=False, foreign_keys=[reference_id])
    
    
    alias_rel = relationship( "PlasmaAlias" )
    alias = association_proxy("alias_rel", "alias",
                                  creator=lambda x_: PlasmaAlias(alias=x_))
    
    
    inputs_rel = relationship( "PlasmaInputs" )
    inputs = association_proxy("inputs_rel", "inputs",
                                  creator=lambda x_: PlasmaInputs(inputs=x_))
    
    
    outputs_rel = relationship( "PlasmaOutputs" )
    outputs = association_proxy("outputs_rel", "outputs",
                                  creator=lambda x_: PlasmaOutputs(outputs=x_))
    
    
    # ManyToMany
    upstream = relationship( "AcceleratorElement", secondary="Plasma_upstream")
    
    
    # ManyToMany
    downstream = relationship( "AcceleratorElement", secondary="Plasma_downstream")
    

    def __repr__(self):
        return f"Plasma(name={self.name},hardware_class={self.hardware_class},hardware_type={self.hardware_type},hardware_model={self.hardware_model},machine_area={self.machine_area},virtual_name={self.virtual_name},subelement={self.subelement},plasma_id={self.plasma_id},laser_id={self.laser_id},physical_id={self.physical_id},simulation_id={self.simulation_id},electrical_id={self.electrical_id},manufacturer_id={self.manufacturer_id},controls_id={self.controls_id},reference_id={self.reference_id},)"



    
    # Using concrete inheritance: see https://docs.sqlalchemy.org/en/14/orm/inheritance.html
    __mapper_args__ = {
        'concrete': True
    }
    


class HorizontalACDipole(ACDipole):
    """
    Horizontally deflecting AC-dipole tune exciter.
    """
    __tablename__ = 'Horizontal_AC_Dipole'

    name = Column(Text(), primary_key=True, nullable=False )
    hardware_class = Column(Enum('Magnet', 'Diagnostic', 'RF', 'Vacuum', 'Laser', 'Plasma', 'Feedback', 'Marker', 'Aperture', 'Stage', 'Lighting', 'Shutter', 'Wakefield', 'TwissMatch', 'Drift', 'Generic', 'Monitor', 'Simulation', 'Valve', 'LaserMirror', 'LaserEnergyMeter', 'LaserAttenuator', name='HardwareClassEnum'), nullable=False )
    hardware_type = Column(Text())
    hardware_model = Column(Text())
    machine_area = Column(Text())
    virtual_name = Column(Text())
    subelement = Column(Text())
    physical_id = Column(Integer(), ForeignKey('PhysicalElement.id'))
    physical = relationship("PhysicalElement", uselist=False, foreign_keys=[physical_id])
    simulation_id = Column(Integer(), ForeignKey('ACDipoleSimulationElement.id'))
    simulation = relationship("ACDipoleSimulationElement", uselist=False, foreign_keys=[simulation_id])
    electrical_id = Column(Integer(), ForeignKey('ElectricalElement.id'))
    electrical = relationship("ElectricalElement", uselist=False, foreign_keys=[electrical_id])
    manufacturer_id = Column(Integer(), ForeignKey('ManufacturerElement.id'))
    manufacturer = relationship("ManufacturerElement", uselist=False, foreign_keys=[manufacturer_id])
    controls_id = Column(Integer(), ForeignKey('ControlsInformation.id'))
    controls = relationship("ControlsInformation", uselist=False, foreign_keys=[controls_id])
    reference_id = Column(Integer(), ForeignKey('ReferenceElement.id'))
    reference = relationship("ReferenceElement", uselist=False, foreign_keys=[reference_id])
    
    
    alias_rel = relationship( "HorizontalACDipoleAlias" )
    alias = association_proxy("alias_rel", "alias",
                                  creator=lambda x_: HorizontalACDipoleAlias(alias=x_))
    
    
    inputs_rel = relationship( "HorizontalACDipoleInputs" )
    inputs = association_proxy("inputs_rel", "inputs",
                                  creator=lambda x_: HorizontalACDipoleInputs(inputs=x_))
    
    
    outputs_rel = relationship( "HorizontalACDipoleOutputs" )
    outputs = association_proxy("outputs_rel", "outputs",
                                  creator=lambda x_: HorizontalACDipoleOutputs(outputs=x_))
    
    
    # ManyToMany
    upstream = relationship( "AcceleratorElement", secondary="Horizontal_AC_Dipole_upstream")
    
    
    # ManyToMany
    downstream = relationship( "AcceleratorElement", secondary="Horizontal_AC_Dipole_downstream")
    

    def __repr__(self):
        return f"Horizontal_AC_Dipole(name={self.name},hardware_class={self.hardware_class},hardware_type={self.hardware_type},hardware_model={self.hardware_model},machine_area={self.machine_area},virtual_name={self.virtual_name},subelement={self.subelement},physical_id={self.physical_id},simulation_id={self.simulation_id},electrical_id={self.electrical_id},manufacturer_id={self.manufacturer_id},controls_id={self.controls_id},reference_id={self.reference_id},)"



    
    # Using concrete inheritance: see https://docs.sqlalchemy.org/en/14/orm/inheritance.html
    __mapper_args__ = {
        'concrete': True
    }
    


class VerticalACDipole(ACDipole):
    """
    Vertically deflecting AC-dipole tune exciter.
    """
    __tablename__ = 'Vertical_AC_Dipole'

    name = Column(Text(), primary_key=True, nullable=False )
    hardware_class = Column(Enum('Magnet', 'Diagnostic', 'RF', 'Vacuum', 'Laser', 'Plasma', 'Feedback', 'Marker', 'Aperture', 'Stage', 'Lighting', 'Shutter', 'Wakefield', 'TwissMatch', 'Drift', 'Generic', 'Monitor', 'Simulation', 'Valve', 'LaserMirror', 'LaserEnergyMeter', 'LaserAttenuator', name='HardwareClassEnum'), nullable=False )
    hardware_type = Column(Text())
    hardware_model = Column(Text())
    machine_area = Column(Text())
    virtual_name = Column(Text())
    subelement = Column(Text())
    physical_id = Column(Integer(), ForeignKey('PhysicalElement.id'))
    physical = relationship("PhysicalElement", uselist=False, foreign_keys=[physical_id])
    simulation_id = Column(Integer(), ForeignKey('ACDipoleSimulationElement.id'))
    simulation = relationship("ACDipoleSimulationElement", uselist=False, foreign_keys=[simulation_id])
    electrical_id = Column(Integer(), ForeignKey('ElectricalElement.id'))
    electrical = relationship("ElectricalElement", uselist=False, foreign_keys=[electrical_id])
    manufacturer_id = Column(Integer(), ForeignKey('ManufacturerElement.id'))
    manufacturer = relationship("ManufacturerElement", uselist=False, foreign_keys=[manufacturer_id])
    controls_id = Column(Integer(), ForeignKey('ControlsInformation.id'))
    controls = relationship("ControlsInformation", uselist=False, foreign_keys=[controls_id])
    reference_id = Column(Integer(), ForeignKey('ReferenceElement.id'))
    reference = relationship("ReferenceElement", uselist=False, foreign_keys=[reference_id])
    
    
    alias_rel = relationship( "VerticalACDipoleAlias" )
    alias = association_proxy("alias_rel", "alias",
                                  creator=lambda x_: VerticalACDipoleAlias(alias=x_))
    
    
    inputs_rel = relationship( "VerticalACDipoleInputs" )
    inputs = association_proxy("inputs_rel", "inputs",
                                  creator=lambda x_: VerticalACDipoleInputs(inputs=x_))
    
    
    outputs_rel = relationship( "VerticalACDipoleOutputs" )
    outputs = association_proxy("outputs_rel", "outputs",
                                  creator=lambda x_: VerticalACDipoleOutputs(outputs=x_))
    
    
    # ManyToMany
    upstream = relationship( "AcceleratorElement", secondary="Vertical_AC_Dipole_upstream")
    
    
    # ManyToMany
    downstream = relationship( "AcceleratorElement", secondary="Vertical_AC_Dipole_downstream")
    

    def __repr__(self):
        return f"Vertical_AC_Dipole(name={self.name},hardware_class={self.hardware_class},hardware_type={self.hardware_type},hardware_model={self.hardware_model},machine_area={self.machine_area},virtual_name={self.virtual_name},subelement={self.subelement},physical_id={self.physical_id},simulation_id={self.simulation_id},electrical_id={self.electrical_id},manufacturer_id={self.manufacturer_id},controls_id={self.controls_id},reference_id={self.reference_id},)"



    
    # Using concrete inheritance: see https://docs.sqlalchemy.org/en/14/orm/inheritance.html
    __mapper_args__ = {
        'concrete': True
    }
    


class Collimator(Aperture):
    """
    Movable collimator jaw (extends Aperture).
    """
    __tablename__ = 'Collimator'

    name = Column(Text(), primary_key=True, nullable=False )
    hardware_class = Column(Enum('Magnet', 'Diagnostic', 'RF', 'Vacuum', 'Laser', 'Plasma', 'Feedback', 'Marker', 'Aperture', 'Stage', 'Lighting', 'Shutter', 'Wakefield', 'TwissMatch', 'Drift', 'Generic', 'Monitor', 'Simulation', 'Valve', 'LaserMirror', 'LaserEnergyMeter', 'LaserAttenuator', name='HardwareClassEnum'), nullable=False )
    hardware_type = Column(Text())
    hardware_model = Column(Text())
    machine_area = Column(Text())
    virtual_name = Column(Text())
    subelement = Column(Text())
    aperture_id = Column(Integer(), ForeignKey('ApertureElement.id'))
    aperture = relationship("ApertureElement", uselist=False, foreign_keys=[aperture_id])
    physical_id = Column(Integer(), ForeignKey('PhysicalElement.id'))
    physical = relationship("PhysicalElement", uselist=False, foreign_keys=[physical_id])
    simulation_id = Column(Integer(), ForeignKey('SimulationElement.id'))
    simulation = relationship("SimulationElement", uselist=False, foreign_keys=[simulation_id])
    electrical_id = Column(Integer(), ForeignKey('ElectricalElement.id'))
    electrical = relationship("ElectricalElement", uselist=False, foreign_keys=[electrical_id])
    manufacturer_id = Column(Integer(), ForeignKey('ManufacturerElement.id'))
    manufacturer = relationship("ManufacturerElement", uselist=False, foreign_keys=[manufacturer_id])
    controls_id = Column(Integer(), ForeignKey('ControlsInformation.id'))
    controls = relationship("ControlsInformation", uselist=False, foreign_keys=[controls_id])
    reference_id = Column(Integer(), ForeignKey('ReferenceElement.id'))
    reference = relationship("ReferenceElement", uselist=False, foreign_keys=[reference_id])
    
    
    alias_rel = relationship( "CollimatorAlias" )
    alias = association_proxy("alias_rel", "alias",
                                  creator=lambda x_: CollimatorAlias(alias=x_))
    
    
    inputs_rel = relationship( "CollimatorInputs" )
    inputs = association_proxy("inputs_rel", "inputs",
                                  creator=lambda x_: CollimatorInputs(inputs=x_))
    
    
    outputs_rel = relationship( "CollimatorOutputs" )
    outputs = association_proxy("outputs_rel", "outputs",
                                  creator=lambda x_: CollimatorOutputs(outputs=x_))
    
    
    # ManyToMany
    upstream = relationship( "AcceleratorElement", secondary="Collimator_upstream")
    
    
    # ManyToMany
    downstream = relationship( "AcceleratorElement", secondary="Collimator_downstream")
    

    def __repr__(self):
        return f"Collimator(name={self.name},hardware_class={self.hardware_class},hardware_type={self.hardware_type},hardware_model={self.hardware_model},machine_area={self.machine_area},virtual_name={self.virtual_name},subelement={self.subelement},aperture_id={self.aperture_id},physical_id={self.physical_id},simulation_id={self.simulation_id},electrical_id={self.electrical_id},manufacturer_id={self.manufacturer_id},controls_id={self.controls_id},reference_id={self.reference_id},)"



    
    # Using concrete inheritance: see https://docs.sqlalchemy.org/en/14/orm/inheritance.html
    __mapper_args__ = {
        'concrete': True
    }
    


class RFDeflectingCavity(RFCavity):
    """
    Transverse-deflecting (streak) RF cavity.
    """
    __tablename__ = 'RFDeflectingCavity'

    name = Column(Text(), primary_key=True, nullable=False )
    hardware_class = Column(Enum('Magnet', 'Diagnostic', 'RF', 'Vacuum', 'Laser', 'Plasma', 'Feedback', 'Marker', 'Aperture', 'Stage', 'Lighting', 'Shutter', 'Wakefield', 'TwissMatch', 'Drift', 'Generic', 'Monitor', 'Simulation', 'Valve', 'LaserMirror', 'LaserEnergyMeter', 'LaserAttenuator', name='HardwareClassEnum'), nullable=False )
    hardware_type = Column(Text())
    hardware_model = Column(Text())
    machine_area = Column(Text())
    virtual_name = Column(Text())
    subelement = Column(Text())
    cavity_id = Column(Integer(), ForeignKey('RFDeflectingCavityElement.id'))
    cavity = relationship("RFDeflectingCavityElement", uselist=False, foreign_keys=[cavity_id])
    physical_id = Column(Integer(), ForeignKey('PhysicalElement.id'))
    physical = relationship("PhysicalElement", uselist=False, foreign_keys=[physical_id])
    simulation_id = Column(Integer(), ForeignKey('RFCavitySimulationElement.id'))
    simulation = relationship("RFCavitySimulationElement", uselist=False, foreign_keys=[simulation_id])
    electrical_id = Column(Integer(), ForeignKey('ElectricalElement.id'))
    electrical = relationship("ElectricalElement", uselist=False, foreign_keys=[electrical_id])
    manufacturer_id = Column(Integer(), ForeignKey('ManufacturerElement.id'))
    manufacturer = relationship("ManufacturerElement", uselist=False, foreign_keys=[manufacturer_id])
    controls_id = Column(Integer(), ForeignKey('ControlsInformation.id'))
    controls = relationship("ControlsInformation", uselist=False, foreign_keys=[controls_id])
    reference_id = Column(Integer(), ForeignKey('ReferenceElement.id'))
    reference = relationship("ReferenceElement", uselist=False, foreign_keys=[reference_id])
    
    
    alias_rel = relationship( "RFDeflectingCavityAlias" )
    alias = association_proxy("alias_rel", "alias",
                                  creator=lambda x_: RFDeflectingCavityAlias(alias=x_))
    
    
    inputs_rel = relationship( "RFDeflectingCavityInputs" )
    inputs = association_proxy("inputs_rel", "inputs",
                                  creator=lambda x_: RFDeflectingCavityInputs(inputs=x_))
    
    
    outputs_rel = relationship( "RFDeflectingCavityOutputs" )
    outputs = association_proxy("outputs_rel", "outputs",
                                  creator=lambda x_: RFDeflectingCavityOutputs(outputs=x_))
    
    
    # ManyToMany
    upstream = relationship( "AcceleratorElement", secondary="RFDeflectingCavity_upstream")
    
    
    # ManyToMany
    downstream = relationship( "AcceleratorElement", secondary="RFDeflectingCavity_downstream")
    

    def __repr__(self):
        return f"RFDeflectingCavity(name={self.name},hardware_class={self.hardware_class},hardware_type={self.hardware_type},hardware_model={self.hardware_model},machine_area={self.machine_area},virtual_name={self.virtual_name},subelement={self.subelement},cavity_id={self.cavity_id},physical_id={self.physical_id},simulation_id={self.simulation_id},electrical_id={self.electrical_id},manufacturer_id={self.manufacturer_id},controls_id={self.controls_id},reference_id={self.reference_id},)"



    
    # Using concrete inheritance: see https://docs.sqlalchemy.org/en/14/orm/inheritance.html
    __mapper_args__ = {
        'concrete': True
    }
    


class CrabCavity(RFCavity):
    """
    Transverse-deflecting crab cavity for crossing-angle compensation.
    """
    __tablename__ = 'CrabCavity'

    name = Column(Text(), primary_key=True, nullable=False )
    hardware_class = Column(Enum('Magnet', 'Diagnostic', 'RF', 'Vacuum', 'Laser', 'Plasma', 'Feedback', 'Marker', 'Aperture', 'Stage', 'Lighting', 'Shutter', 'Wakefield', 'TwissMatch', 'Drift', 'Generic', 'Monitor', 'Simulation', 'Valve', 'LaserMirror', 'LaserEnergyMeter', 'LaserAttenuator', name='HardwareClassEnum'), nullable=False )
    hardware_type = Column(Text())
    hardware_model = Column(Text())
    machine_area = Column(Text())
    virtual_name = Column(Text())
    subelement = Column(Text())
    cavity_id = Column(Integer(), ForeignKey('RFDeflectingCavityElement.id'))
    cavity = relationship("RFDeflectingCavityElement", uselist=False, foreign_keys=[cavity_id])
    physical_id = Column(Integer(), ForeignKey('PhysicalElement.id'))
    physical = relationship("PhysicalElement", uselist=False, foreign_keys=[physical_id])
    simulation_id = Column(Integer(), ForeignKey('RFCavitySimulationElement.id'))
    simulation = relationship("RFCavitySimulationElement", uselist=False, foreign_keys=[simulation_id])
    electrical_id = Column(Integer(), ForeignKey('ElectricalElement.id'))
    electrical = relationship("ElectricalElement", uselist=False, foreign_keys=[electrical_id])
    manufacturer_id = Column(Integer(), ForeignKey('ManufacturerElement.id'))
    manufacturer = relationship("ManufacturerElement", uselist=False, foreign_keys=[manufacturer_id])
    controls_id = Column(Integer(), ForeignKey('ControlsInformation.id'))
    controls = relationship("ControlsInformation", uselist=False, foreign_keys=[controls_id])
    reference_id = Column(Integer(), ForeignKey('ReferenceElement.id'))
    reference = relationship("ReferenceElement", uselist=False, foreign_keys=[reference_id])
    
    
    alias_rel = relationship( "CrabCavityAlias" )
    alias = association_proxy("alias_rel", "alias",
                                  creator=lambda x_: CrabCavityAlias(alias=x_))
    
    
    inputs_rel = relationship( "CrabCavityInputs" )
    inputs = association_proxy("inputs_rel", "inputs",
                                  creator=lambda x_: CrabCavityInputs(inputs=x_))
    
    
    outputs_rel = relationship( "CrabCavityOutputs" )
    outputs = association_proxy("outputs_rel", "outputs",
                                  creator=lambda x_: CrabCavityOutputs(outputs=x_))
    
    
    # ManyToMany
    upstream = relationship( "AcceleratorElement", secondary="CrabCavity_upstream")
    
    
    # ManyToMany
    downstream = relationship( "AcceleratorElement", secondary="CrabCavity_downstream")
    

    def __repr__(self):
        return f"CrabCavity(name={self.name},hardware_class={self.hardware_class},hardware_type={self.hardware_type},hardware_model={self.hardware_model},machine_area={self.machine_area},virtual_name={self.virtual_name},subelement={self.subelement},cavity_id={self.cavity_id},physical_id={self.physical_id},simulation_id={self.simulation_id},electrical_id={self.electrical_id},manufacturer_id={self.manufacturer_id},controls_id={self.controls_id},reference_id={self.reference_id},)"



    
    # Using concrete inheritance: see https://docs.sqlalchemy.org/en/14/orm/inheritance.html
    __mapper_args__ = {
        'concrete': True
    }
    


class BeamPositionMonitor(Diagnostic):
    """
    Beam-position monitor (BPM).
    """
    __tablename__ = 'BeamPositionMonitor'

    name = Column(Text(), primary_key=True, nullable=False )
    hardware_class = Column(Enum('Magnet', 'Diagnostic', 'RF', 'Vacuum', 'Laser', 'Plasma', 'Feedback', 'Marker', 'Aperture', 'Stage', 'Lighting', 'Shutter', 'Wakefield', 'TwissMatch', 'Drift', 'Generic', 'Monitor', 'Simulation', 'Valve', 'LaserMirror', 'LaserEnergyMeter', 'LaserAttenuator', name='HardwareClassEnum'), nullable=False )
    hardware_type = Column(Text())
    hardware_model = Column(Text())
    machine_area = Column(Text())
    virtual_name = Column(Text())
    subelement = Column(Text())
    diagnostic_id = Column(Integer(), ForeignKey('BPMDiagnosticElement.id'))
    diagnostic = relationship("BPMDiagnosticElement", uselist=False, foreign_keys=[diagnostic_id])
    physical_id = Column(Integer(), ForeignKey('PhysicalElement.id'))
    physical = relationship("PhysicalElement", uselist=False, foreign_keys=[physical_id])
    simulation_id = Column(Integer(), ForeignKey('DiagnosticSimulationElement.id'))
    simulation = relationship("DiagnosticSimulationElement", uselist=False, foreign_keys=[simulation_id])
    electrical_id = Column(Integer(), ForeignKey('ElectricalElement.id'))
    electrical = relationship("ElectricalElement", uselist=False, foreign_keys=[electrical_id])
    manufacturer_id = Column(Integer(), ForeignKey('ManufacturerElement.id'))
    manufacturer = relationship("ManufacturerElement", uselist=False, foreign_keys=[manufacturer_id])
    controls_id = Column(Integer(), ForeignKey('ControlsInformation.id'))
    controls = relationship("ControlsInformation", uselist=False, foreign_keys=[controls_id])
    reference_id = Column(Integer(), ForeignKey('ReferenceElement.id'))
    reference = relationship("ReferenceElement", uselist=False, foreign_keys=[reference_id])
    
    
    alias_rel = relationship( "BeamPositionMonitorAlias" )
    alias = association_proxy("alias_rel", "alias",
                                  creator=lambda x_: BeamPositionMonitorAlias(alias=x_))
    
    
    inputs_rel = relationship( "BeamPositionMonitorInputs" )
    inputs = association_proxy("inputs_rel", "inputs",
                                  creator=lambda x_: BeamPositionMonitorInputs(inputs=x_))
    
    
    outputs_rel = relationship( "BeamPositionMonitorOutputs" )
    outputs = association_proxy("outputs_rel", "outputs",
                                  creator=lambda x_: BeamPositionMonitorOutputs(outputs=x_))
    
    
    # ManyToMany
    upstream = relationship( "AcceleratorElement", secondary="BeamPositionMonitor_upstream")
    
    
    # ManyToMany
    downstream = relationship( "AcceleratorElement", secondary="BeamPositionMonitor_downstream")
    

    def __repr__(self):
        return f"BeamPositionMonitor(name={self.name},hardware_class={self.hardware_class},hardware_type={self.hardware_type},hardware_model={self.hardware_model},machine_area={self.machine_area},virtual_name={self.virtual_name},subelement={self.subelement},diagnostic_id={self.diagnostic_id},physical_id={self.physical_id},simulation_id={self.simulation_id},electrical_id={self.electrical_id},manufacturer_id={self.manufacturer_id},controls_id={self.controls_id},reference_id={self.reference_id},)"



    
    # Using concrete inheritance: see https://docs.sqlalchemy.org/en/14/orm/inheritance.html
    __mapper_args__ = {
        'concrete': True
    }
    


class BeamArrivalMonitor(Diagnostic):
    """
    Beam-arrival-time monitor (BAM).
    """
    __tablename__ = 'BeamArrivalMonitor'

    name = Column(Text(), primary_key=True, nullable=False )
    hardware_class = Column(Enum('Magnet', 'Diagnostic', 'RF', 'Vacuum', 'Laser', 'Plasma', 'Feedback', 'Marker', 'Aperture', 'Stage', 'Lighting', 'Shutter', 'Wakefield', 'TwissMatch', 'Drift', 'Generic', 'Monitor', 'Simulation', 'Valve', 'LaserMirror', 'LaserEnergyMeter', 'LaserAttenuator', name='HardwareClassEnum'), nullable=False )
    hardware_type = Column(Text())
    hardware_model = Column(Text())
    machine_area = Column(Text())
    virtual_name = Column(Text())
    subelement = Column(Text())
    diagnostic_id = Column(Integer(), ForeignKey('BAMDiagnosticElement.id'))
    diagnostic = relationship("BAMDiagnosticElement", uselist=False, foreign_keys=[diagnostic_id])
    physical_id = Column(Integer(), ForeignKey('PhysicalElement.id'))
    physical = relationship("PhysicalElement", uselist=False, foreign_keys=[physical_id])
    simulation_id = Column(Integer(), ForeignKey('DiagnosticSimulationElement.id'))
    simulation = relationship("DiagnosticSimulationElement", uselist=False, foreign_keys=[simulation_id])
    electrical_id = Column(Integer(), ForeignKey('ElectricalElement.id'))
    electrical = relationship("ElectricalElement", uselist=False, foreign_keys=[electrical_id])
    manufacturer_id = Column(Integer(), ForeignKey('ManufacturerElement.id'))
    manufacturer = relationship("ManufacturerElement", uselist=False, foreign_keys=[manufacturer_id])
    controls_id = Column(Integer(), ForeignKey('ControlsInformation.id'))
    controls = relationship("ControlsInformation", uselist=False, foreign_keys=[controls_id])
    reference_id = Column(Integer(), ForeignKey('ReferenceElement.id'))
    reference = relationship("ReferenceElement", uselist=False, foreign_keys=[reference_id])
    
    
    alias_rel = relationship( "BeamArrivalMonitorAlias" )
    alias = association_proxy("alias_rel", "alias",
                                  creator=lambda x_: BeamArrivalMonitorAlias(alias=x_))
    
    
    inputs_rel = relationship( "BeamArrivalMonitorInputs" )
    inputs = association_proxy("inputs_rel", "inputs",
                                  creator=lambda x_: BeamArrivalMonitorInputs(inputs=x_))
    
    
    outputs_rel = relationship( "BeamArrivalMonitorOutputs" )
    outputs = association_proxy("outputs_rel", "outputs",
                                  creator=lambda x_: BeamArrivalMonitorOutputs(outputs=x_))
    
    
    # ManyToMany
    upstream = relationship( "AcceleratorElement", secondary="BeamArrivalMonitor_upstream")
    
    
    # ManyToMany
    downstream = relationship( "AcceleratorElement", secondary="BeamArrivalMonitor_downstream")
    

    def __repr__(self):
        return f"BeamArrivalMonitor(name={self.name},hardware_class={self.hardware_class},hardware_type={self.hardware_type},hardware_model={self.hardware_model},machine_area={self.machine_area},virtual_name={self.virtual_name},subelement={self.subelement},diagnostic_id={self.diagnostic_id},physical_id={self.physical_id},simulation_id={self.simulation_id},electrical_id={self.electrical_id},manufacturer_id={self.manufacturer_id},controls_id={self.controls_id},reference_id={self.reference_id},)"



    
    # Using concrete inheritance: see https://docs.sqlalchemy.org/en/14/orm/inheritance.html
    __mapper_args__ = {
        'concrete': True
    }
    


class BunchLengthMonitor(Diagnostic):
    """
    Bunch-length monitor (BLM / CDR detector).
    """
    __tablename__ = 'BunchLengthMonitor'

    name = Column(Text(), primary_key=True, nullable=False )
    hardware_class = Column(Enum('Magnet', 'Diagnostic', 'RF', 'Vacuum', 'Laser', 'Plasma', 'Feedback', 'Marker', 'Aperture', 'Stage', 'Lighting', 'Shutter', 'Wakefield', 'TwissMatch', 'Drift', 'Generic', 'Monitor', 'Simulation', 'Valve', 'LaserMirror', 'LaserEnergyMeter', 'LaserAttenuator', name='HardwareClassEnum'), nullable=False )
    hardware_type = Column(Text())
    hardware_model = Column(Text())
    machine_area = Column(Text())
    virtual_name = Column(Text())
    subelement = Column(Text())
    diagnostic_id = Column(Integer(), ForeignKey('BLMDiagnosticElement.id'))
    diagnostic = relationship("BLMDiagnosticElement", uselist=False, foreign_keys=[diagnostic_id])
    physical_id = Column(Integer(), ForeignKey('PhysicalElement.id'))
    physical = relationship("PhysicalElement", uselist=False, foreign_keys=[physical_id])
    simulation_id = Column(Integer(), ForeignKey('DiagnosticSimulationElement.id'))
    simulation = relationship("DiagnosticSimulationElement", uselist=False, foreign_keys=[simulation_id])
    electrical_id = Column(Integer(), ForeignKey('ElectricalElement.id'))
    electrical = relationship("ElectricalElement", uselist=False, foreign_keys=[electrical_id])
    manufacturer_id = Column(Integer(), ForeignKey('ManufacturerElement.id'))
    manufacturer = relationship("ManufacturerElement", uselist=False, foreign_keys=[manufacturer_id])
    controls_id = Column(Integer(), ForeignKey('ControlsInformation.id'))
    controls = relationship("ControlsInformation", uselist=False, foreign_keys=[controls_id])
    reference_id = Column(Integer(), ForeignKey('ReferenceElement.id'))
    reference = relationship("ReferenceElement", uselist=False, foreign_keys=[reference_id])
    
    
    alias_rel = relationship( "BunchLengthMonitorAlias" )
    alias = association_proxy("alias_rel", "alias",
                                  creator=lambda x_: BunchLengthMonitorAlias(alias=x_))
    
    
    inputs_rel = relationship( "BunchLengthMonitorInputs" )
    inputs = association_proxy("inputs_rel", "inputs",
                                  creator=lambda x_: BunchLengthMonitorInputs(inputs=x_))
    
    
    outputs_rel = relationship( "BunchLengthMonitorOutputs" )
    outputs = association_proxy("outputs_rel", "outputs",
                                  creator=lambda x_: BunchLengthMonitorOutputs(outputs=x_))
    
    
    # ManyToMany
    upstream = relationship( "AcceleratorElement", secondary="BunchLengthMonitor_upstream")
    
    
    # ManyToMany
    downstream = relationship( "AcceleratorElement", secondary="BunchLengthMonitor_downstream")
    

    def __repr__(self):
        return f"BunchLengthMonitor(name={self.name},hardware_class={self.hardware_class},hardware_type={self.hardware_type},hardware_model={self.hardware_model},machine_area={self.machine_area},virtual_name={self.virtual_name},subelement={self.subelement},diagnostic_id={self.diagnostic_id},physical_id={self.physical_id},simulation_id={self.simulation_id},electrical_id={self.electrical_id},manufacturer_id={self.manufacturer_id},controls_id={self.controls_id},reference_id={self.reference_id},)"



    
    # Using concrete inheritance: see https://docs.sqlalchemy.org/en/14/orm/inheritance.html
    __mapper_args__ = {
        'concrete': True
    }
    


class Camera(Diagnostic):
    """
    Camera-based beam-profile monitor.
    """
    __tablename__ = 'Camera'

    name = Column(Text(), primary_key=True, nullable=False )
    hardware_class = Column(Enum('Magnet', 'Diagnostic', 'RF', 'Vacuum', 'Laser', 'Plasma', 'Feedback', 'Marker', 'Aperture', 'Stage', 'Lighting', 'Shutter', 'Wakefield', 'TwissMatch', 'Drift', 'Generic', 'Monitor', 'Simulation', 'Valve', 'LaserMirror', 'LaserEnergyMeter', 'LaserAttenuator', name='HardwareClassEnum'), nullable=False )
    hardware_type = Column(Text())
    hardware_model = Column(Text())
    machine_area = Column(Text())
    virtual_name = Column(Text())
    subelement = Column(Text())
    diagnostic_id = Column(Integer(), ForeignKey('CameraDiagnosticElement.id'))
    diagnostic = relationship("CameraDiagnosticElement", uselist=False, foreign_keys=[diagnostic_id])
    physical_id = Column(Integer(), ForeignKey('PhysicalElement.id'))
    physical = relationship("PhysicalElement", uselist=False, foreign_keys=[physical_id])
    simulation_id = Column(Integer(), ForeignKey('DiagnosticSimulationElement.id'))
    simulation = relationship("DiagnosticSimulationElement", uselist=False, foreign_keys=[simulation_id])
    electrical_id = Column(Integer(), ForeignKey('ElectricalElement.id'))
    electrical = relationship("ElectricalElement", uselist=False, foreign_keys=[electrical_id])
    manufacturer_id = Column(Integer(), ForeignKey('ManufacturerElement.id'))
    manufacturer = relationship("ManufacturerElement", uselist=False, foreign_keys=[manufacturer_id])
    controls_id = Column(Integer(), ForeignKey('ControlsInformation.id'))
    controls = relationship("ControlsInformation", uselist=False, foreign_keys=[controls_id])
    reference_id = Column(Integer(), ForeignKey('ReferenceElement.id'))
    reference = relationship("ReferenceElement", uselist=False, foreign_keys=[reference_id])
    
    
    alias_rel = relationship( "CameraAlias" )
    alias = association_proxy("alias_rel", "alias",
                                  creator=lambda x_: CameraAlias(alias=x_))
    
    
    inputs_rel = relationship( "CameraInputs" )
    inputs = association_proxy("inputs_rel", "inputs",
                                  creator=lambda x_: CameraInputs(inputs=x_))
    
    
    outputs_rel = relationship( "CameraOutputs" )
    outputs = association_proxy("outputs_rel", "outputs",
                                  creator=lambda x_: CameraOutputs(outputs=x_))
    
    
    # ManyToMany
    upstream = relationship( "AcceleratorElement", secondary="Camera_upstream")
    
    
    # ManyToMany
    downstream = relationship( "AcceleratorElement", secondary="Camera_downstream")
    

    def __repr__(self):
        return f"Camera(name={self.name},hardware_class={self.hardware_class},hardware_type={self.hardware_type},hardware_model={self.hardware_model},machine_area={self.machine_area},virtual_name={self.virtual_name},subelement={self.subelement},diagnostic_id={self.diagnostic_id},physical_id={self.physical_id},simulation_id={self.simulation_id},electrical_id={self.electrical_id},manufacturer_id={self.manufacturer_id},controls_id={self.controls_id},reference_id={self.reference_id},)"



    
    # Using concrete inheritance: see https://docs.sqlalchemy.org/en/14/orm/inheritance.html
    __mapper_args__ = {
        'concrete': True
    }
    


class Screen(Diagnostic):
    """
    Scintillator or OTR screen with an associated camera.
    """
    __tablename__ = 'Screen'

    name = Column(Text(), primary_key=True, nullable=False )
    hardware_class = Column(Enum('Magnet', 'Diagnostic', 'RF', 'Vacuum', 'Laser', 'Plasma', 'Feedback', 'Marker', 'Aperture', 'Stage', 'Lighting', 'Shutter', 'Wakefield', 'TwissMatch', 'Drift', 'Generic', 'Monitor', 'Simulation', 'Valve', 'LaserMirror', 'LaserEnergyMeter', 'LaserAttenuator', name='HardwareClassEnum'), nullable=False )
    hardware_type = Column(Text())
    hardware_model = Column(Text())
    machine_area = Column(Text())
    virtual_name = Column(Text())
    subelement = Column(Text())
    diagnostic_id = Column(Integer(), ForeignKey('ScreenDiagnosticElement.id'))
    diagnostic = relationship("ScreenDiagnosticElement", uselist=False, foreign_keys=[diagnostic_id])
    physical_id = Column(Integer(), ForeignKey('PhysicalElement.id'))
    physical = relationship("PhysicalElement", uselist=False, foreign_keys=[physical_id])
    simulation_id = Column(Integer(), ForeignKey('DiagnosticSimulationElement.id'))
    simulation = relationship("DiagnosticSimulationElement", uselist=False, foreign_keys=[simulation_id])
    electrical_id = Column(Integer(), ForeignKey('ElectricalElement.id'))
    electrical = relationship("ElectricalElement", uselist=False, foreign_keys=[electrical_id])
    manufacturer_id = Column(Integer(), ForeignKey('ManufacturerElement.id'))
    manufacturer = relationship("ManufacturerElement", uselist=False, foreign_keys=[manufacturer_id])
    controls_id = Column(Integer(), ForeignKey('ControlsInformation.id'))
    controls = relationship("ControlsInformation", uselist=False, foreign_keys=[controls_id])
    reference_id = Column(Integer(), ForeignKey('ReferenceElement.id'))
    reference = relationship("ReferenceElement", uselist=False, foreign_keys=[reference_id])
    
    
    alias_rel = relationship( "ScreenAlias" )
    alias = association_proxy("alias_rel", "alias",
                                  creator=lambda x_: ScreenAlias(alias=x_))
    
    
    inputs_rel = relationship( "ScreenInputs" )
    inputs = association_proxy("inputs_rel", "inputs",
                                  creator=lambda x_: ScreenInputs(inputs=x_))
    
    
    outputs_rel = relationship( "ScreenOutputs" )
    outputs = association_proxy("outputs_rel", "outputs",
                                  creator=lambda x_: ScreenOutputs(outputs=x_))
    
    
    # ManyToMany
    upstream = relationship( "AcceleratorElement", secondary="Screen_upstream")
    
    
    # ManyToMany
    downstream = relationship( "AcceleratorElement", secondary="Screen_downstream")
    

    def __repr__(self):
        return f"Screen(name={self.name},hardware_class={self.hardware_class},hardware_type={self.hardware_type},hardware_model={self.hardware_model},machine_area={self.machine_area},virtual_name={self.virtual_name},subelement={self.subelement},diagnostic_id={self.diagnostic_id},physical_id={self.physical_id},simulation_id={self.simulation_id},electrical_id={self.electrical_id},manufacturer_id={self.manufacturer_id},controls_id={self.controls_id},reference_id={self.reference_id},)"



    
    # Using concrete inheritance: see https://docs.sqlalchemy.org/en/14/orm/inheritance.html
    __mapper_args__ = {
        'concrete': True
    }
    


class ChargeDiagnostic(Diagnostic):
    """
    Base class for charge-measurement diagnostics.
    """
    __tablename__ = 'ChargeDiagnostic'

    name = Column(Text(), primary_key=True, nullable=False )
    hardware_class = Column(Enum('Magnet', 'Diagnostic', 'RF', 'Vacuum', 'Laser', 'Plasma', 'Feedback', 'Marker', 'Aperture', 'Stage', 'Lighting', 'Shutter', 'Wakefield', 'TwissMatch', 'Drift', 'Generic', 'Monitor', 'Simulation', 'Valve', 'LaserMirror', 'LaserEnergyMeter', 'LaserAttenuator', name='HardwareClassEnum'), nullable=False )
    hardware_type = Column(Text())
    hardware_model = Column(Text())
    machine_area = Column(Text())
    virtual_name = Column(Text())
    subelement = Column(Text())
    diagnostic_id = Column(Integer(), ForeignKey('ChargeDiagnosticElement.id'))
    diagnostic = relationship("ChargeDiagnosticElement", uselist=False, foreign_keys=[diagnostic_id])
    physical_id = Column(Integer(), ForeignKey('PhysicalElement.id'))
    physical = relationship("PhysicalElement", uselist=False, foreign_keys=[physical_id])
    simulation_id = Column(Integer(), ForeignKey('DiagnosticSimulationElement.id'))
    simulation = relationship("DiagnosticSimulationElement", uselist=False, foreign_keys=[simulation_id])
    electrical_id = Column(Integer(), ForeignKey('ElectricalElement.id'))
    electrical = relationship("ElectricalElement", uselist=False, foreign_keys=[electrical_id])
    manufacturer_id = Column(Integer(), ForeignKey('ManufacturerElement.id'))
    manufacturer = relationship("ManufacturerElement", uselist=False, foreign_keys=[manufacturer_id])
    controls_id = Column(Integer(), ForeignKey('ControlsInformation.id'))
    controls = relationship("ControlsInformation", uselist=False, foreign_keys=[controls_id])
    reference_id = Column(Integer(), ForeignKey('ReferenceElement.id'))
    reference = relationship("ReferenceElement", uselist=False, foreign_keys=[reference_id])
    
    
    alias_rel = relationship( "ChargeDiagnosticAlias" )
    alias = association_proxy("alias_rel", "alias",
                                  creator=lambda x_: ChargeDiagnosticAlias(alias=x_))
    
    
    inputs_rel = relationship( "ChargeDiagnosticInputs" )
    inputs = association_proxy("inputs_rel", "inputs",
                                  creator=lambda x_: ChargeDiagnosticInputs(inputs=x_))
    
    
    outputs_rel = relationship( "ChargeDiagnosticOutputs" )
    outputs = association_proxy("outputs_rel", "outputs",
                                  creator=lambda x_: ChargeDiagnosticOutputs(outputs=x_))
    
    
    # ManyToMany
    upstream = relationship( "AcceleratorElement", secondary="ChargeDiagnostic_upstream")
    
    
    # ManyToMany
    downstream = relationship( "AcceleratorElement", secondary="ChargeDiagnostic_downstream")
    

    def __repr__(self):
        return f"ChargeDiagnostic(name={self.name},hardware_class={self.hardware_class},hardware_type={self.hardware_type},hardware_model={self.hardware_model},machine_area={self.machine_area},virtual_name={self.virtual_name},subelement={self.subelement},diagnostic_id={self.diagnostic_id},physical_id={self.physical_id},simulation_id={self.simulation_id},electrical_id={self.electrical_id},manufacturer_id={self.manufacturer_id},controls_id={self.controls_id},reference_id={self.reference_id},)"



    
    # Using concrete inheritance: see https://docs.sqlalchemy.org/en/14/orm/inheritance.html
    __mapper_args__ = {
        'concrete': True
    }
    


class PhotonMonitor(Diagnostic):
    """
    Photon intensity monitor.
    """
    __tablename__ = 'PhotonMonitor'

    name = Column(Text(), primary_key=True, nullable=False )
    hardware_class = Column(Enum('Magnet', 'Diagnostic', 'RF', 'Vacuum', 'Laser', 'Plasma', 'Feedback', 'Marker', 'Aperture', 'Stage', 'Lighting', 'Shutter', 'Wakefield', 'TwissMatch', 'Drift', 'Generic', 'Monitor', 'Simulation', 'Valve', 'LaserMirror', 'LaserEnergyMeter', 'LaserAttenuator', name='HardwareClassEnum'), nullable=False )
    hardware_type = Column(Text())
    hardware_model = Column(Text())
    machine_area = Column(Text())
    virtual_name = Column(Text())
    subelement = Column(Text())
    diagnostic_id = Column(Integer(), ForeignKey('PhotonIntensityMonitorDiagnostic.id'))
    diagnostic = relationship("PhotonIntensityMonitorDiagnostic", uselist=False, foreign_keys=[diagnostic_id])
    physical_id = Column(Integer(), ForeignKey('PhysicalElement.id'))
    physical = relationship("PhysicalElement", uselist=False, foreign_keys=[physical_id])
    simulation_id = Column(Integer(), ForeignKey('DiagnosticSimulationElement.id'))
    simulation = relationship("DiagnosticSimulationElement", uselist=False, foreign_keys=[simulation_id])
    electrical_id = Column(Integer(), ForeignKey('ElectricalElement.id'))
    electrical = relationship("ElectricalElement", uselist=False, foreign_keys=[electrical_id])
    manufacturer_id = Column(Integer(), ForeignKey('ManufacturerElement.id'))
    manufacturer = relationship("ManufacturerElement", uselist=False, foreign_keys=[manufacturer_id])
    controls_id = Column(Integer(), ForeignKey('ControlsInformation.id'))
    controls = relationship("ControlsInformation", uselist=False, foreign_keys=[controls_id])
    reference_id = Column(Integer(), ForeignKey('ReferenceElement.id'))
    reference = relationship("ReferenceElement", uselist=False, foreign_keys=[reference_id])
    
    
    alias_rel = relationship( "PhotonMonitorAlias" )
    alias = association_proxy("alias_rel", "alias",
                                  creator=lambda x_: PhotonMonitorAlias(alias=x_))
    
    
    inputs_rel = relationship( "PhotonMonitorInputs" )
    inputs = association_proxy("inputs_rel", "inputs",
                                  creator=lambda x_: PhotonMonitorInputs(inputs=x_))
    
    
    outputs_rel = relationship( "PhotonMonitorOutputs" )
    outputs = association_proxy("outputs_rel", "outputs",
                                  creator=lambda x_: PhotonMonitorOutputs(outputs=x_))
    
    
    # ManyToMany
    upstream = relationship( "AcceleratorElement", secondary="PhotonMonitor_upstream")
    
    
    # ManyToMany
    downstream = relationship( "AcceleratorElement", secondary="PhotonMonitor_downstream")
    

    def __repr__(self):
        return f"PhotonMonitor(name={self.name},hardware_class={self.hardware_class},hardware_type={self.hardware_type},hardware_model={self.hardware_model},machine_area={self.machine_area},virtual_name={self.virtual_name},subelement={self.subelement},diagnostic_id={self.diagnostic_id},physical_id={self.physical_id},simulation_id={self.simulation_id},electrical_id={self.electrical_id},manufacturer_id={self.manufacturer_id},controls_id={self.controls_id},reference_id={self.reference_id},)"



    
    # Using concrete inheritance: see https://docs.sqlalchemy.org/en/14/orm/inheritance.html
    __mapper_args__ = {
        'concrete': True
    }
    


class Dipole(Magnet):
    """
    None
    """
    __tablename__ = 'Dipole'

    name = Column(Text(), primary_key=True, nullable=False )
    hardware_class = Column(Enum('Magnet', 'Diagnostic', 'RF', 'Vacuum', 'Laser', 'Plasma', 'Feedback', 'Marker', 'Aperture', 'Stage', 'Lighting', 'Shutter', 'Wakefield', 'TwissMatch', 'Drift', 'Generic', 'Monitor', 'Simulation', 'Valve', 'LaserMirror', 'LaserEnergyMeter', 'LaserAttenuator', name='HardwareClassEnum'), nullable=False )
    hardware_type = Column(Text())
    hardware_model = Column(Text())
    machine_area = Column(Text())
    virtual_name = Column(Text())
    subelement = Column(Text())
    magnetic_id = Column(Integer(), ForeignKey('Dipole_Magnet.id'))
    magnetic = relationship("DipoleMagnet", uselist=False, foreign_keys=[magnetic_id])
    degauss_id = Column(Integer(), ForeignKey('DegaussableElement.id'))
    degauss = relationship("DegaussableElement", uselist=False, foreign_keys=[degauss_id])
    physical_id = Column(Integer(), ForeignKey('PhysicalElement.id'))
    physical = relationship("PhysicalElement", uselist=False, foreign_keys=[physical_id])
    simulation_id = Column(Integer(), ForeignKey('MagnetSimulationElement.id'))
    simulation = relationship("MagnetSimulationElement", uselist=False, foreign_keys=[simulation_id])
    electrical_id = Column(Integer(), ForeignKey('ElectricalElement.id'))
    electrical = relationship("ElectricalElement", uselist=False, foreign_keys=[electrical_id])
    manufacturer_id = Column(Integer(), ForeignKey('ManufacturerElement.id'))
    manufacturer = relationship("ManufacturerElement", uselist=False, foreign_keys=[manufacturer_id])
    controls_id = Column(Integer(), ForeignKey('ControlsInformation.id'))
    controls = relationship("ControlsInformation", uselist=False, foreign_keys=[controls_id])
    reference_id = Column(Integer(), ForeignKey('ReferenceElement.id'))
    reference = relationship("ReferenceElement", uselist=False, foreign_keys=[reference_id])
    
    
    alias_rel = relationship( "DipoleAlias" )
    alias = association_proxy("alias_rel", "alias",
                                  creator=lambda x_: DipoleAlias(alias=x_))
    
    
    inputs_rel = relationship( "DipoleInputs" )
    inputs = association_proxy("inputs_rel", "inputs",
                                  creator=lambda x_: DipoleInputs(inputs=x_))
    
    
    outputs_rel = relationship( "DipoleOutputs" )
    outputs = association_proxy("outputs_rel", "outputs",
                                  creator=lambda x_: DipoleOutputs(outputs=x_))
    
    
    # ManyToMany
    upstream = relationship( "AcceleratorElement", secondary="Dipole_upstream")
    
    
    # ManyToMany
    downstream = relationship( "AcceleratorElement", secondary="Dipole_downstream")
    

    def __repr__(self):
        return f"Dipole(name={self.name},hardware_class={self.hardware_class},hardware_type={self.hardware_type},hardware_model={self.hardware_model},machine_area={self.machine_area},virtual_name={self.virtual_name},subelement={self.subelement},magnetic_id={self.magnetic_id},degauss_id={self.degauss_id},physical_id={self.physical_id},simulation_id={self.simulation_id},electrical_id={self.electrical_id},manufacturer_id={self.manufacturer_id},controls_id={self.controls_id},reference_id={self.reference_id},)"



    
    # Using concrete inheritance: see https://docs.sqlalchemy.org/en/14/orm/inheritance.html
    __mapper_args__ = {
        'concrete': True
    }
    


class Quadrupole(Magnet):
    """
    None
    """
    __tablename__ = 'Quadrupole'

    name = Column(Text(), primary_key=True, nullable=False )
    hardware_class = Column(Enum('Magnet', 'Diagnostic', 'RF', 'Vacuum', 'Laser', 'Plasma', 'Feedback', 'Marker', 'Aperture', 'Stage', 'Lighting', 'Shutter', 'Wakefield', 'TwissMatch', 'Drift', 'Generic', 'Monitor', 'Simulation', 'Valve', 'LaserMirror', 'LaserEnergyMeter', 'LaserAttenuator', name='HardwareClassEnum'), nullable=False )
    hardware_type = Column(Text())
    hardware_model = Column(Text())
    machine_area = Column(Text())
    virtual_name = Column(Text())
    subelement = Column(Text())
    magnetic_id = Column(Integer(), ForeignKey('Quadrupole_Magnet.id'))
    magnetic = relationship("QuadrupoleMagnet", uselist=False, foreign_keys=[magnetic_id])
    degauss_id = Column(Integer(), ForeignKey('DegaussableElement.id'))
    degauss = relationship("DegaussableElement", uselist=False, foreign_keys=[degauss_id])
    physical_id = Column(Integer(), ForeignKey('PhysicalElement.id'))
    physical = relationship("PhysicalElement", uselist=False, foreign_keys=[physical_id])
    simulation_id = Column(Integer(), ForeignKey('MagnetSimulationElement.id'))
    simulation = relationship("MagnetSimulationElement", uselist=False, foreign_keys=[simulation_id])
    electrical_id = Column(Integer(), ForeignKey('ElectricalElement.id'))
    electrical = relationship("ElectricalElement", uselist=False, foreign_keys=[electrical_id])
    manufacturer_id = Column(Integer(), ForeignKey('ManufacturerElement.id'))
    manufacturer = relationship("ManufacturerElement", uselist=False, foreign_keys=[manufacturer_id])
    controls_id = Column(Integer(), ForeignKey('ControlsInformation.id'))
    controls = relationship("ControlsInformation", uselist=False, foreign_keys=[controls_id])
    reference_id = Column(Integer(), ForeignKey('ReferenceElement.id'))
    reference = relationship("ReferenceElement", uselist=False, foreign_keys=[reference_id])
    
    
    alias_rel = relationship( "QuadrupoleAlias" )
    alias = association_proxy("alias_rel", "alias",
                                  creator=lambda x_: QuadrupoleAlias(alias=x_))
    
    
    inputs_rel = relationship( "QuadrupoleInputs" )
    inputs = association_proxy("inputs_rel", "inputs",
                                  creator=lambda x_: QuadrupoleInputs(inputs=x_))
    
    
    outputs_rel = relationship( "QuadrupoleOutputs" )
    outputs = association_proxy("outputs_rel", "outputs",
                                  creator=lambda x_: QuadrupoleOutputs(outputs=x_))
    
    
    # ManyToMany
    upstream = relationship( "AcceleratorElement", secondary="Quadrupole_upstream")
    
    
    # ManyToMany
    downstream = relationship( "AcceleratorElement", secondary="Quadrupole_downstream")
    

    def __repr__(self):
        return f"Quadrupole(name={self.name},hardware_class={self.hardware_class},hardware_type={self.hardware_type},hardware_model={self.hardware_model},machine_area={self.machine_area},virtual_name={self.virtual_name},subelement={self.subelement},magnetic_id={self.magnetic_id},degauss_id={self.degauss_id},physical_id={self.physical_id},simulation_id={self.simulation_id},electrical_id={self.electrical_id},manufacturer_id={self.manufacturer_id},controls_id={self.controls_id},reference_id={self.reference_id},)"



    
    # Using concrete inheritance: see https://docs.sqlalchemy.org/en/14/orm/inheritance.html
    __mapper_args__ = {
        'concrete': True
    }
    


class Sextupole(Magnet):
    """
    Sextupole chromaticity-correction magnet.
    """
    __tablename__ = 'Sextupole'

    name = Column(Text(), primary_key=True, nullable=False )
    hardware_class = Column(Enum('Magnet', 'Diagnostic', 'RF', 'Vacuum', 'Laser', 'Plasma', 'Feedback', 'Marker', 'Aperture', 'Stage', 'Lighting', 'Shutter', 'Wakefield', 'TwissMatch', 'Drift', 'Generic', 'Monitor', 'Simulation', 'Valve', 'LaserMirror', 'LaserEnergyMeter', 'LaserAttenuator', name='HardwareClassEnum'), nullable=False )
    hardware_type = Column(Text())
    hardware_model = Column(Text())
    machine_area = Column(Text())
    virtual_name = Column(Text())
    subelement = Column(Text())
    magnetic_id = Column(Integer(), ForeignKey('Sextupole_Magnet.id'))
    magnetic = relationship("SextupoleMagnet", uselist=False, foreign_keys=[magnetic_id])
    degauss_id = Column(Integer(), ForeignKey('DegaussableElement.id'))
    degauss = relationship("DegaussableElement", uselist=False, foreign_keys=[degauss_id])
    physical_id = Column(Integer(), ForeignKey('PhysicalElement.id'))
    physical = relationship("PhysicalElement", uselist=False, foreign_keys=[physical_id])
    simulation_id = Column(Integer(), ForeignKey('MagnetSimulationElement.id'))
    simulation = relationship("MagnetSimulationElement", uselist=False, foreign_keys=[simulation_id])
    electrical_id = Column(Integer(), ForeignKey('ElectricalElement.id'))
    electrical = relationship("ElectricalElement", uselist=False, foreign_keys=[electrical_id])
    manufacturer_id = Column(Integer(), ForeignKey('ManufacturerElement.id'))
    manufacturer = relationship("ManufacturerElement", uselist=False, foreign_keys=[manufacturer_id])
    controls_id = Column(Integer(), ForeignKey('ControlsInformation.id'))
    controls = relationship("ControlsInformation", uselist=False, foreign_keys=[controls_id])
    reference_id = Column(Integer(), ForeignKey('ReferenceElement.id'))
    reference = relationship("ReferenceElement", uselist=False, foreign_keys=[reference_id])
    
    
    alias_rel = relationship( "SextupoleAlias" )
    alias = association_proxy("alias_rel", "alias",
                                  creator=lambda x_: SextupoleAlias(alias=x_))
    
    
    inputs_rel = relationship( "SextupoleInputs" )
    inputs = association_proxy("inputs_rel", "inputs",
                                  creator=lambda x_: SextupoleInputs(inputs=x_))
    
    
    outputs_rel = relationship( "SextupoleOutputs" )
    outputs = association_proxy("outputs_rel", "outputs",
                                  creator=lambda x_: SextupoleOutputs(outputs=x_))
    
    
    # ManyToMany
    upstream = relationship( "AcceleratorElement", secondary="Sextupole_upstream")
    
    
    # ManyToMany
    downstream = relationship( "AcceleratorElement", secondary="Sextupole_downstream")
    

    def __repr__(self):
        return f"Sextupole(name={self.name},hardware_class={self.hardware_class},hardware_type={self.hardware_type},hardware_model={self.hardware_model},machine_area={self.machine_area},virtual_name={self.virtual_name},subelement={self.subelement},magnetic_id={self.magnetic_id},degauss_id={self.degauss_id},physical_id={self.physical_id},simulation_id={self.simulation_id},electrical_id={self.electrical_id},manufacturer_id={self.manufacturer_id},controls_id={self.controls_id},reference_id={self.reference_id},)"



    
    # Using concrete inheritance: see https://docs.sqlalchemy.org/en/14/orm/inheritance.html
    __mapper_args__ = {
        'concrete': True
    }
    


class Octupole(Magnet):
    """
    Octupole magnet.
    """
    __tablename__ = 'Octupole'

    name = Column(Text(), primary_key=True, nullable=False )
    hardware_class = Column(Enum('Magnet', 'Diagnostic', 'RF', 'Vacuum', 'Laser', 'Plasma', 'Feedback', 'Marker', 'Aperture', 'Stage', 'Lighting', 'Shutter', 'Wakefield', 'TwissMatch', 'Drift', 'Generic', 'Monitor', 'Simulation', 'Valve', 'LaserMirror', 'LaserEnergyMeter', 'LaserAttenuator', name='HardwareClassEnum'), nullable=False )
    hardware_type = Column(Text())
    hardware_model = Column(Text())
    machine_area = Column(Text())
    virtual_name = Column(Text())
    subelement = Column(Text())
    magnetic_id = Column(Integer(), ForeignKey('Octupole_Magnet.id'))
    magnetic = relationship("OctupoleMagnet", uselist=False, foreign_keys=[magnetic_id])
    degauss_id = Column(Integer(), ForeignKey('DegaussableElement.id'))
    degauss = relationship("DegaussableElement", uselist=False, foreign_keys=[degauss_id])
    physical_id = Column(Integer(), ForeignKey('PhysicalElement.id'))
    physical = relationship("PhysicalElement", uselist=False, foreign_keys=[physical_id])
    simulation_id = Column(Integer(), ForeignKey('MagnetSimulationElement.id'))
    simulation = relationship("MagnetSimulationElement", uselist=False, foreign_keys=[simulation_id])
    electrical_id = Column(Integer(), ForeignKey('ElectricalElement.id'))
    electrical = relationship("ElectricalElement", uselist=False, foreign_keys=[electrical_id])
    manufacturer_id = Column(Integer(), ForeignKey('ManufacturerElement.id'))
    manufacturer = relationship("ManufacturerElement", uselist=False, foreign_keys=[manufacturer_id])
    controls_id = Column(Integer(), ForeignKey('ControlsInformation.id'))
    controls = relationship("ControlsInformation", uselist=False, foreign_keys=[controls_id])
    reference_id = Column(Integer(), ForeignKey('ReferenceElement.id'))
    reference = relationship("ReferenceElement", uselist=False, foreign_keys=[reference_id])
    
    
    alias_rel = relationship( "OctupoleAlias" )
    alias = association_proxy("alias_rel", "alias",
                                  creator=lambda x_: OctupoleAlias(alias=x_))
    
    
    inputs_rel = relationship( "OctupoleInputs" )
    inputs = association_proxy("inputs_rel", "inputs",
                                  creator=lambda x_: OctupoleInputs(inputs=x_))
    
    
    outputs_rel = relationship( "OctupoleOutputs" )
    outputs = association_proxy("outputs_rel", "outputs",
                                  creator=lambda x_: OctupoleOutputs(outputs=x_))
    
    
    # ManyToMany
    upstream = relationship( "AcceleratorElement", secondary="Octupole_upstream")
    
    
    # ManyToMany
    downstream = relationship( "AcceleratorElement", secondary="Octupole_downstream")
    

    def __repr__(self):
        return f"Octupole(name={self.name},hardware_class={self.hardware_class},hardware_type={self.hardware_type},hardware_model={self.hardware_model},machine_area={self.machine_area},virtual_name={self.virtual_name},subelement={self.subelement},magnetic_id={self.magnetic_id},degauss_id={self.degauss_id},physical_id={self.physical_id},simulation_id={self.simulation_id},electrical_id={self.electrical_id},manufacturer_id={self.manufacturer_id},controls_id={self.controls_id},reference_id={self.reference_id},)"



    
    # Using concrete inheritance: see https://docs.sqlalchemy.org/en/14/orm/inheritance.html
    __mapper_args__ = {
        'concrete': True
    }
    


class Solenoid(Magnet):
    """
    Solenoid focusing magnet.
    """
    __tablename__ = 'Solenoid'

    name = Column(Text(), primary_key=True, nullable=False )
    hardware_class = Column(Enum('Magnet', 'Diagnostic', 'RF', 'Vacuum', 'Laser', 'Plasma', 'Feedback', 'Marker', 'Aperture', 'Stage', 'Lighting', 'Shutter', 'Wakefield', 'TwissMatch', 'Drift', 'Generic', 'Monitor', 'Simulation', 'Valve', 'LaserMirror', 'LaserEnergyMeter', 'LaserAttenuator', name='HardwareClassEnum'), nullable=False )
    hardware_type = Column(Text())
    hardware_model = Column(Text())
    machine_area = Column(Text())
    virtual_name = Column(Text())
    subelement = Column(Text())
    magnetic_id = Column(Integer(), ForeignKey('Solenoid_Magnet.id'))
    magnetic = relationship("SolenoidMagnet", uselist=False, foreign_keys=[magnetic_id])
    degauss_id = Column(Integer(), ForeignKey('DegaussableElement.id'))
    degauss = relationship("DegaussableElement", uselist=False, foreign_keys=[degauss_id])
    physical_id = Column(Integer(), ForeignKey('PhysicalElement.id'))
    physical = relationship("PhysicalElement", uselist=False, foreign_keys=[physical_id])
    simulation_id = Column(Integer(), ForeignKey('MagnetSimulationElement.id'))
    simulation = relationship("MagnetSimulationElement", uselist=False, foreign_keys=[simulation_id])
    electrical_id = Column(Integer(), ForeignKey('ElectricalElement.id'))
    electrical = relationship("ElectricalElement", uselist=False, foreign_keys=[electrical_id])
    manufacturer_id = Column(Integer(), ForeignKey('ManufacturerElement.id'))
    manufacturer = relationship("ManufacturerElement", uselist=False, foreign_keys=[manufacturer_id])
    controls_id = Column(Integer(), ForeignKey('ControlsInformation.id'))
    controls = relationship("ControlsInformation", uselist=False, foreign_keys=[controls_id])
    reference_id = Column(Integer(), ForeignKey('ReferenceElement.id'))
    reference = relationship("ReferenceElement", uselist=False, foreign_keys=[reference_id])
    
    
    alias_rel = relationship( "SolenoidAlias" )
    alias = association_proxy("alias_rel", "alias",
                                  creator=lambda x_: SolenoidAlias(alias=x_))
    
    
    inputs_rel = relationship( "SolenoidInputs" )
    inputs = association_proxy("inputs_rel", "inputs",
                                  creator=lambda x_: SolenoidInputs(inputs=x_))
    
    
    outputs_rel = relationship( "SolenoidOutputs" )
    outputs = association_proxy("outputs_rel", "outputs",
                                  creator=lambda x_: SolenoidOutputs(outputs=x_))
    
    
    # ManyToMany
    upstream = relationship( "AcceleratorElement", secondary="Solenoid_upstream")
    
    
    # ManyToMany
    downstream = relationship( "AcceleratorElement", secondary="Solenoid_downstream")
    

    def __repr__(self):
        return f"Solenoid(name={self.name},hardware_class={self.hardware_class},hardware_type={self.hardware_type},hardware_model={self.hardware_model},machine_area={self.machine_area},virtual_name={self.virtual_name},subelement={self.subelement},magnetic_id={self.magnetic_id},degauss_id={self.degauss_id},physical_id={self.physical_id},simulation_id={self.simulation_id},electrical_id={self.electrical_id},manufacturer_id={self.manufacturer_id},controls_id={self.controls_id},reference_id={self.reference_id},)"



    
    # Using concrete inheritance: see https://docs.sqlalchemy.org/en/14/orm/inheritance.html
    __mapper_args__ = {
        'concrete': True
    }
    


class Wiggler(Magnet):
    """
    Wiggler / undulator insertion device.
    """
    __tablename__ = 'Wiggler'

    name = Column(Text(), primary_key=True, nullable=False )
    hardware_class = Column(Enum('Magnet', 'Diagnostic', 'RF', 'Vacuum', 'Laser', 'Plasma', 'Feedback', 'Marker', 'Aperture', 'Stage', 'Lighting', 'Shutter', 'Wakefield', 'TwissMatch', 'Drift', 'Generic', 'Monitor', 'Simulation', 'Valve', 'LaserMirror', 'LaserEnergyMeter', 'LaserAttenuator', name='HardwareClassEnum'), nullable=False )
    hardware_type = Column(Text())
    hardware_model = Column(Text())
    machine_area = Column(Text())
    virtual_name = Column(Text())
    subelement = Column(Text())
    laser_id = Column(Integer(), ForeignKey('LaserElement.id'))
    laser = relationship("LaserElement", uselist=False, foreign_keys=[laser_id])
    magnetic_id = Column(Integer(), ForeignKey('Wiggler_Magnet.id'))
    magnetic = relationship("WigglerMagnet", uselist=False, foreign_keys=[magnetic_id])
    degauss_id = Column(Integer(), ForeignKey('DegaussableElement.id'))
    degauss = relationship("DegaussableElement", uselist=False, foreign_keys=[degauss_id])
    physical_id = Column(Integer(), ForeignKey('PhysicalElement.id'))
    physical = relationship("PhysicalElement", uselist=False, foreign_keys=[physical_id])
    simulation_id = Column(Integer(), ForeignKey('MagnetSimulationElement.id'))
    simulation = relationship("MagnetSimulationElement", uselist=False, foreign_keys=[simulation_id])
    electrical_id = Column(Integer(), ForeignKey('ElectricalElement.id'))
    electrical = relationship("ElectricalElement", uselist=False, foreign_keys=[electrical_id])
    manufacturer_id = Column(Integer(), ForeignKey('ManufacturerElement.id'))
    manufacturer = relationship("ManufacturerElement", uselist=False, foreign_keys=[manufacturer_id])
    controls_id = Column(Integer(), ForeignKey('ControlsInformation.id'))
    controls = relationship("ControlsInformation", uselist=False, foreign_keys=[controls_id])
    reference_id = Column(Integer(), ForeignKey('ReferenceElement.id'))
    reference = relationship("ReferenceElement", uselist=False, foreign_keys=[reference_id])
    
    
    alias_rel = relationship( "WigglerAlias" )
    alias = association_proxy("alias_rel", "alias",
                                  creator=lambda x_: WigglerAlias(alias=x_))
    
    
    inputs_rel = relationship( "WigglerInputs" )
    inputs = association_proxy("inputs_rel", "inputs",
                                  creator=lambda x_: WigglerInputs(inputs=x_))
    
    
    outputs_rel = relationship( "WigglerOutputs" )
    outputs = association_proxy("outputs_rel", "outputs",
                                  creator=lambda x_: WigglerOutputs(outputs=x_))
    
    
    # ManyToMany
    upstream = relationship( "AcceleratorElement", secondary="Wiggler_upstream")
    
    
    # ManyToMany
    downstream = relationship( "AcceleratorElement", secondary="Wiggler_downstream")
    

    def __repr__(self):
        return f"Wiggler(name={self.name},hardware_class={self.hardware_class},hardware_type={self.hardware_type},hardware_model={self.hardware_model},machine_area={self.machine_area},virtual_name={self.virtual_name},subelement={self.subelement},laser_id={self.laser_id},magnetic_id={self.magnetic_id},degauss_id={self.degauss_id},physical_id={self.physical_id},simulation_id={self.simulation_id},electrical_id={self.electrical_id},manufacturer_id={self.manufacturer_id},controls_id={self.controls_id},reference_id={self.reference_id},)"



    
    # Using concrete inheritance: see https://docs.sqlalchemy.org/en/14/orm/inheritance.html
    __mapper_args__ = {
        'concrete': True
    }
    


class NonLinearLens(Magnet):
    """
    Non-linear integrable-optics lens.
    """
    __tablename__ = 'NonLinearLens'

    name = Column(Text(), primary_key=True, nullable=False )
    hardware_class = Column(Enum('Magnet', 'Diagnostic', 'RF', 'Vacuum', 'Laser', 'Plasma', 'Feedback', 'Marker', 'Aperture', 'Stage', 'Lighting', 'Shutter', 'Wakefield', 'TwissMatch', 'Drift', 'Generic', 'Monitor', 'Simulation', 'Valve', 'LaserMirror', 'LaserEnergyMeter', 'LaserAttenuator', name='HardwareClassEnum'), nullable=False )
    hardware_type = Column(Text())
    hardware_model = Column(Text())
    machine_area = Column(Text())
    virtual_name = Column(Text())
    subelement = Column(Text())
    magnetic_id = Column(Integer(), ForeignKey('NonLinearLens_Magnet.id'))
    magnetic = relationship("NonLinearLensMagnet", uselist=False, foreign_keys=[magnetic_id])
    degauss_id = Column(Integer(), ForeignKey('DegaussableElement.id'))
    degauss = relationship("DegaussableElement", uselist=False, foreign_keys=[degauss_id])
    physical_id = Column(Integer(), ForeignKey('PhysicalElement.id'))
    physical = relationship("PhysicalElement", uselist=False, foreign_keys=[physical_id])
    simulation_id = Column(Integer(), ForeignKey('MagnetSimulationElement.id'))
    simulation = relationship("MagnetSimulationElement", uselist=False, foreign_keys=[simulation_id])
    electrical_id = Column(Integer(), ForeignKey('ElectricalElement.id'))
    electrical = relationship("ElectricalElement", uselist=False, foreign_keys=[electrical_id])
    manufacturer_id = Column(Integer(), ForeignKey('ManufacturerElement.id'))
    manufacturer = relationship("ManufacturerElement", uselist=False, foreign_keys=[manufacturer_id])
    controls_id = Column(Integer(), ForeignKey('ControlsInformation.id'))
    controls = relationship("ControlsInformation", uselist=False, foreign_keys=[controls_id])
    reference_id = Column(Integer(), ForeignKey('ReferenceElement.id'))
    reference = relationship("ReferenceElement", uselist=False, foreign_keys=[reference_id])
    
    
    alias_rel = relationship( "NonLinearLensAlias" )
    alias = association_proxy("alias_rel", "alias",
                                  creator=lambda x_: NonLinearLensAlias(alias=x_))
    
    
    inputs_rel = relationship( "NonLinearLensInputs" )
    inputs = association_proxy("inputs_rel", "inputs",
                                  creator=lambda x_: NonLinearLensInputs(inputs=x_))
    
    
    outputs_rel = relationship( "NonLinearLensOutputs" )
    outputs = association_proxy("outputs_rel", "outputs",
                                  creator=lambda x_: NonLinearLensOutputs(outputs=x_))
    
    
    # ManyToMany
    upstream = relationship( "AcceleratorElement", secondary="NonLinearLens_upstream")
    
    
    # ManyToMany
    downstream = relationship( "AcceleratorElement", secondary="NonLinearLens_downstream")
    

    def __repr__(self):
        return f"NonLinearLens(name={self.name},hardware_class={self.hardware_class},hardware_type={self.hardware_type},hardware_model={self.hardware_model},machine_area={self.machine_area},virtual_name={self.virtual_name},subelement={self.subelement},magnetic_id={self.magnetic_id},degauss_id={self.degauss_id},physical_id={self.physical_id},simulation_id={self.simulation_id},electrical_id={self.electrical_id},manufacturer_id={self.manufacturer_id},controls_id={self.controls_id},reference_id={self.reference_id},)"



    
    # Using concrete inheritance: see https://docs.sqlalchemy.org/en/14/orm/inheritance.html
    __mapper_args__ = {
        'concrete': True
    }
    


class WallCurrentMonitor(ChargeDiagnostic):
    """
    Wall-current monitor (WCM) for non-destructive charge measurement.
    """
    __tablename__ = 'WallCurrentMonitor'

    name = Column(Text(), primary_key=True, nullable=False )
    hardware_class = Column(Enum('Magnet', 'Diagnostic', 'RF', 'Vacuum', 'Laser', 'Plasma', 'Feedback', 'Marker', 'Aperture', 'Stage', 'Lighting', 'Shutter', 'Wakefield', 'TwissMatch', 'Drift', 'Generic', 'Monitor', 'Simulation', 'Valve', 'LaserMirror', 'LaserEnergyMeter', 'LaserAttenuator', name='HardwareClassEnum'), nullable=False )
    hardware_type = Column(Text())
    hardware_model = Column(Text())
    machine_area = Column(Text())
    virtual_name = Column(Text())
    subelement = Column(Text())
    diagnostic_id = Column(Integer(), ForeignKey('ChargeDiagnosticElement.id'))
    diagnostic = relationship("ChargeDiagnosticElement", uselist=False, foreign_keys=[diagnostic_id])
    physical_id = Column(Integer(), ForeignKey('PhysicalElement.id'))
    physical = relationship("PhysicalElement", uselist=False, foreign_keys=[physical_id])
    simulation_id = Column(Integer(), ForeignKey('DiagnosticSimulationElement.id'))
    simulation = relationship("DiagnosticSimulationElement", uselist=False, foreign_keys=[simulation_id])
    electrical_id = Column(Integer(), ForeignKey('ElectricalElement.id'))
    electrical = relationship("ElectricalElement", uselist=False, foreign_keys=[electrical_id])
    manufacturer_id = Column(Integer(), ForeignKey('ManufacturerElement.id'))
    manufacturer = relationship("ManufacturerElement", uselist=False, foreign_keys=[manufacturer_id])
    controls_id = Column(Integer(), ForeignKey('ControlsInformation.id'))
    controls = relationship("ControlsInformation", uselist=False, foreign_keys=[controls_id])
    reference_id = Column(Integer(), ForeignKey('ReferenceElement.id'))
    reference = relationship("ReferenceElement", uselist=False, foreign_keys=[reference_id])
    
    
    alias_rel = relationship( "WallCurrentMonitorAlias" )
    alias = association_proxy("alias_rel", "alias",
                                  creator=lambda x_: WallCurrentMonitorAlias(alias=x_))
    
    
    inputs_rel = relationship( "WallCurrentMonitorInputs" )
    inputs = association_proxy("inputs_rel", "inputs",
                                  creator=lambda x_: WallCurrentMonitorInputs(inputs=x_))
    
    
    outputs_rel = relationship( "WallCurrentMonitorOutputs" )
    outputs = association_proxy("outputs_rel", "outputs",
                                  creator=lambda x_: WallCurrentMonitorOutputs(outputs=x_))
    
    
    # ManyToMany
    upstream = relationship( "AcceleratorElement", secondary="WallCurrentMonitor_upstream")
    
    
    # ManyToMany
    downstream = relationship( "AcceleratorElement", secondary="WallCurrentMonitor_downstream")
    

    def __repr__(self):
        return f"WallCurrentMonitor(name={self.name},hardware_class={self.hardware_class},hardware_type={self.hardware_type},hardware_model={self.hardware_model},machine_area={self.machine_area},virtual_name={self.virtual_name},subelement={self.subelement},diagnostic_id={self.diagnostic_id},physical_id={self.physical_id},simulation_id={self.simulation_id},electrical_id={self.electrical_id},manufacturer_id={self.manufacturer_id},controls_id={self.controls_id},reference_id={self.reference_id},)"



    
    # Using concrete inheritance: see https://docs.sqlalchemy.org/en/14/orm/inheritance.html
    __mapper_args__ = {
        'concrete': True
    }
    


class FaradayCupMonitor(ChargeDiagnostic):
    """
    Faraday cup for destructive charge measurement.
    """
    __tablename__ = 'FaradayCupMonitor'

    name = Column(Text(), primary_key=True, nullable=False )
    hardware_class = Column(Enum('Magnet', 'Diagnostic', 'RF', 'Vacuum', 'Laser', 'Plasma', 'Feedback', 'Marker', 'Aperture', 'Stage', 'Lighting', 'Shutter', 'Wakefield', 'TwissMatch', 'Drift', 'Generic', 'Monitor', 'Simulation', 'Valve', 'LaserMirror', 'LaserEnergyMeter', 'LaserAttenuator', name='HardwareClassEnum'), nullable=False )
    hardware_type = Column(Text())
    hardware_model = Column(Text())
    machine_area = Column(Text())
    virtual_name = Column(Text())
    subelement = Column(Text())
    diagnostic_id = Column(Integer(), ForeignKey('ChargeDiagnosticElement.id'))
    diagnostic = relationship("ChargeDiagnosticElement", uselist=False, foreign_keys=[diagnostic_id])
    physical_id = Column(Integer(), ForeignKey('PhysicalElement.id'))
    physical = relationship("PhysicalElement", uselist=False, foreign_keys=[physical_id])
    simulation_id = Column(Integer(), ForeignKey('DiagnosticSimulationElement.id'))
    simulation = relationship("DiagnosticSimulationElement", uselist=False, foreign_keys=[simulation_id])
    electrical_id = Column(Integer(), ForeignKey('ElectricalElement.id'))
    electrical = relationship("ElectricalElement", uselist=False, foreign_keys=[electrical_id])
    manufacturer_id = Column(Integer(), ForeignKey('ManufacturerElement.id'))
    manufacturer = relationship("ManufacturerElement", uselist=False, foreign_keys=[manufacturer_id])
    controls_id = Column(Integer(), ForeignKey('ControlsInformation.id'))
    controls = relationship("ControlsInformation", uselist=False, foreign_keys=[controls_id])
    reference_id = Column(Integer(), ForeignKey('ReferenceElement.id'))
    reference = relationship("ReferenceElement", uselist=False, foreign_keys=[reference_id])
    
    
    alias_rel = relationship( "FaradayCupMonitorAlias" )
    alias = association_proxy("alias_rel", "alias",
                                  creator=lambda x_: FaradayCupMonitorAlias(alias=x_))
    
    
    inputs_rel = relationship( "FaradayCupMonitorInputs" )
    inputs = association_proxy("inputs_rel", "inputs",
                                  creator=lambda x_: FaradayCupMonitorInputs(inputs=x_))
    
    
    outputs_rel = relationship( "FaradayCupMonitorOutputs" )
    outputs = association_proxy("outputs_rel", "outputs",
                                  creator=lambda x_: FaradayCupMonitorOutputs(outputs=x_))
    
    
    # ManyToMany
    upstream = relationship( "AcceleratorElement", secondary="FaradayCupMonitor_upstream")
    
    
    # ManyToMany
    downstream = relationship( "AcceleratorElement", secondary="FaradayCupMonitor_downstream")
    

    def __repr__(self):
        return f"FaradayCupMonitor(name={self.name},hardware_class={self.hardware_class},hardware_type={self.hardware_type},hardware_model={self.hardware_model},machine_area={self.machine_area},virtual_name={self.virtual_name},subelement={self.subelement},diagnostic_id={self.diagnostic_id},physical_id={self.physical_id},simulation_id={self.simulation_id},electrical_id={self.electrical_id},manufacturer_id={self.manufacturer_id},controls_id={self.controls_id},reference_id={self.reference_id},)"



    
    # Using concrete inheritance: see https://docs.sqlalchemy.org/en/14/orm/inheritance.html
    __mapper_args__ = {
        'concrete': True
    }
    


class IntegratedCurrentTransformer(ChargeDiagnostic):
    """
    Integrated current transformer (ICT) for non-destructive single-shot charge measurement.
    """
    __tablename__ = 'IntegratedCurrentTransformer'

    name = Column(Text(), primary_key=True, nullable=False )
    hardware_class = Column(Enum('Magnet', 'Diagnostic', 'RF', 'Vacuum', 'Laser', 'Plasma', 'Feedback', 'Marker', 'Aperture', 'Stage', 'Lighting', 'Shutter', 'Wakefield', 'TwissMatch', 'Drift', 'Generic', 'Monitor', 'Simulation', 'Valve', 'LaserMirror', 'LaserEnergyMeter', 'LaserAttenuator', name='HardwareClassEnum'), nullable=False )
    hardware_type = Column(Text())
    hardware_model = Column(Text())
    machine_area = Column(Text())
    virtual_name = Column(Text())
    subelement = Column(Text())
    diagnostic_id = Column(Integer(), ForeignKey('ChargeDiagnosticElement.id'))
    diagnostic = relationship("ChargeDiagnosticElement", uselist=False, foreign_keys=[diagnostic_id])
    physical_id = Column(Integer(), ForeignKey('PhysicalElement.id'))
    physical = relationship("PhysicalElement", uselist=False, foreign_keys=[physical_id])
    simulation_id = Column(Integer(), ForeignKey('DiagnosticSimulationElement.id'))
    simulation = relationship("DiagnosticSimulationElement", uselist=False, foreign_keys=[simulation_id])
    electrical_id = Column(Integer(), ForeignKey('ElectricalElement.id'))
    electrical = relationship("ElectricalElement", uselist=False, foreign_keys=[electrical_id])
    manufacturer_id = Column(Integer(), ForeignKey('ManufacturerElement.id'))
    manufacturer = relationship("ManufacturerElement", uselist=False, foreign_keys=[manufacturer_id])
    controls_id = Column(Integer(), ForeignKey('ControlsInformation.id'))
    controls = relationship("ControlsInformation", uselist=False, foreign_keys=[controls_id])
    reference_id = Column(Integer(), ForeignKey('ReferenceElement.id'))
    reference = relationship("ReferenceElement", uselist=False, foreign_keys=[reference_id])
    
    
    alias_rel = relationship( "IntegratedCurrentTransformerAlias" )
    alias = association_proxy("alias_rel", "alias",
                                  creator=lambda x_: IntegratedCurrentTransformerAlias(alias=x_))
    
    
    inputs_rel = relationship( "IntegratedCurrentTransformerInputs" )
    inputs = association_proxy("inputs_rel", "inputs",
                                  creator=lambda x_: IntegratedCurrentTransformerInputs(inputs=x_))
    
    
    outputs_rel = relationship( "IntegratedCurrentTransformerOutputs" )
    outputs = association_proxy("outputs_rel", "outputs",
                                  creator=lambda x_: IntegratedCurrentTransformerOutputs(outputs=x_))
    
    
    # ManyToMany
    upstream = relationship( "AcceleratorElement", secondary="IntegratedCurrentTransformer_upstream")
    
    
    # ManyToMany
    downstream = relationship( "AcceleratorElement", secondary="IntegratedCurrentTransformer_downstream")
    

    def __repr__(self):
        return f"IntegratedCurrentTransformer(name={self.name},hardware_class={self.hardware_class},hardware_type={self.hardware_type},hardware_model={self.hardware_model},machine_area={self.machine_area},virtual_name={self.virtual_name},subelement={self.subelement},diagnostic_id={self.diagnostic_id},physical_id={self.physical_id},simulation_id={self.simulation_id},electrical_id={self.electrical_id},manufacturer_id={self.manufacturer_id},controls_id={self.controls_id},reference_id={self.reference_id},)"



    
    # Using concrete inheritance: see https://docs.sqlalchemy.org/en/14/orm/inheritance.html
    __mapper_args__ = {
        'concrete': True
    }
    


class HorizontalCorrector(Dipole):
    """
    Horizontal steering corrector.
    """
    __tablename__ = 'HorizontalCorrector'

    name = Column(Text(), primary_key=True, nullable=False )
    hardware_class = Column(Enum('Magnet', 'Diagnostic', 'RF', 'Vacuum', 'Laser', 'Plasma', 'Feedback', 'Marker', 'Aperture', 'Stage', 'Lighting', 'Shutter', 'Wakefield', 'TwissMatch', 'Drift', 'Generic', 'Monitor', 'Simulation', 'Valve', 'LaserMirror', 'LaserEnergyMeter', 'LaserAttenuator', name='HardwareClassEnum'), nullable=False )
    hardware_type = Column(Text())
    hardware_model = Column(Text())
    machine_area = Column(Text())
    virtual_name = Column(Text())
    subelement = Column(Text())
    magnetic_id = Column(Integer(), ForeignKey('Corrector_Magnet.id'))
    magnetic = relationship("CorrectorMagnet", uselist=False, foreign_keys=[magnetic_id])
    degauss_id = Column(Integer(), ForeignKey('DegaussableElement.id'))
    degauss = relationship("DegaussableElement", uselist=False, foreign_keys=[degauss_id])
    physical_id = Column(Integer(), ForeignKey('PhysicalElement.id'))
    physical = relationship("PhysicalElement", uselist=False, foreign_keys=[physical_id])
    simulation_id = Column(Integer(), ForeignKey('MagnetSimulationElement.id'))
    simulation = relationship("MagnetSimulationElement", uselist=False, foreign_keys=[simulation_id])
    electrical_id = Column(Integer(), ForeignKey('ElectricalElement.id'))
    electrical = relationship("ElectricalElement", uselist=False, foreign_keys=[electrical_id])
    manufacturer_id = Column(Integer(), ForeignKey('ManufacturerElement.id'))
    manufacturer = relationship("ManufacturerElement", uselist=False, foreign_keys=[manufacturer_id])
    controls_id = Column(Integer(), ForeignKey('ControlsInformation.id'))
    controls = relationship("ControlsInformation", uselist=False, foreign_keys=[controls_id])
    reference_id = Column(Integer(), ForeignKey('ReferenceElement.id'))
    reference = relationship("ReferenceElement", uselist=False, foreign_keys=[reference_id])
    
    
    alias_rel = relationship( "HorizontalCorrectorAlias" )
    alias = association_proxy("alias_rel", "alias",
                                  creator=lambda x_: HorizontalCorrectorAlias(alias=x_))
    
    
    inputs_rel = relationship( "HorizontalCorrectorInputs" )
    inputs = association_proxy("inputs_rel", "inputs",
                                  creator=lambda x_: HorizontalCorrectorInputs(inputs=x_))
    
    
    outputs_rel = relationship( "HorizontalCorrectorOutputs" )
    outputs = association_proxy("outputs_rel", "outputs",
                                  creator=lambda x_: HorizontalCorrectorOutputs(outputs=x_))
    
    
    # ManyToMany
    upstream = relationship( "AcceleratorElement", secondary="HorizontalCorrector_upstream")
    
    
    # ManyToMany
    downstream = relationship( "AcceleratorElement", secondary="HorizontalCorrector_downstream")
    

    def __repr__(self):
        return f"HorizontalCorrector(name={self.name},hardware_class={self.hardware_class},hardware_type={self.hardware_type},hardware_model={self.hardware_model},machine_area={self.machine_area},virtual_name={self.virtual_name},subelement={self.subelement},magnetic_id={self.magnetic_id},degauss_id={self.degauss_id},physical_id={self.physical_id},simulation_id={self.simulation_id},electrical_id={self.electrical_id},manufacturer_id={self.manufacturer_id},controls_id={self.controls_id},reference_id={self.reference_id},)"



    
    # Using concrete inheritance: see https://docs.sqlalchemy.org/en/14/orm/inheritance.html
    __mapper_args__ = {
        'concrete': True
    }
    


class VerticalCorrector(Dipole):
    """
    Vertical steering corrector.
    """
    __tablename__ = 'VerticalCorrector'

    name = Column(Text(), primary_key=True, nullable=False )
    hardware_class = Column(Enum('Magnet', 'Diagnostic', 'RF', 'Vacuum', 'Laser', 'Plasma', 'Feedback', 'Marker', 'Aperture', 'Stage', 'Lighting', 'Shutter', 'Wakefield', 'TwissMatch', 'Drift', 'Generic', 'Monitor', 'Simulation', 'Valve', 'LaserMirror', 'LaserEnergyMeter', 'LaserAttenuator', name='HardwareClassEnum'), nullable=False )
    hardware_type = Column(Text())
    hardware_model = Column(Text())
    machine_area = Column(Text())
    virtual_name = Column(Text())
    subelement = Column(Text())
    magnetic_id = Column(Integer(), ForeignKey('Corrector_Magnet.id'))
    magnetic = relationship("CorrectorMagnet", uselist=False, foreign_keys=[magnetic_id])
    degauss_id = Column(Integer(), ForeignKey('DegaussableElement.id'))
    degauss = relationship("DegaussableElement", uselist=False, foreign_keys=[degauss_id])
    physical_id = Column(Integer(), ForeignKey('PhysicalElement.id'))
    physical = relationship("PhysicalElement", uselist=False, foreign_keys=[physical_id])
    simulation_id = Column(Integer(), ForeignKey('MagnetSimulationElement.id'))
    simulation = relationship("MagnetSimulationElement", uselist=False, foreign_keys=[simulation_id])
    electrical_id = Column(Integer(), ForeignKey('ElectricalElement.id'))
    electrical = relationship("ElectricalElement", uselist=False, foreign_keys=[electrical_id])
    manufacturer_id = Column(Integer(), ForeignKey('ManufacturerElement.id'))
    manufacturer = relationship("ManufacturerElement", uselist=False, foreign_keys=[manufacturer_id])
    controls_id = Column(Integer(), ForeignKey('ControlsInformation.id'))
    controls = relationship("ControlsInformation", uselist=False, foreign_keys=[controls_id])
    reference_id = Column(Integer(), ForeignKey('ReferenceElement.id'))
    reference = relationship("ReferenceElement", uselist=False, foreign_keys=[reference_id])
    
    
    alias_rel = relationship( "VerticalCorrectorAlias" )
    alias = association_proxy("alias_rel", "alias",
                                  creator=lambda x_: VerticalCorrectorAlias(alias=x_))
    
    
    inputs_rel = relationship( "VerticalCorrectorInputs" )
    inputs = association_proxy("inputs_rel", "inputs",
                                  creator=lambda x_: VerticalCorrectorInputs(inputs=x_))
    
    
    outputs_rel = relationship( "VerticalCorrectorOutputs" )
    outputs = association_proxy("outputs_rel", "outputs",
                                  creator=lambda x_: VerticalCorrectorOutputs(outputs=x_))
    
    
    # ManyToMany
    upstream = relationship( "AcceleratorElement", secondary="VerticalCorrector_upstream")
    
    
    # ManyToMany
    downstream = relationship( "AcceleratorElement", secondary="VerticalCorrector_downstream")
    

    def __repr__(self):
        return f"VerticalCorrector(name={self.name},hardware_class={self.hardware_class},hardware_type={self.hardware_type},hardware_model={self.hardware_model},machine_area={self.machine_area},virtual_name={self.virtual_name},subelement={self.subelement},magnetic_id={self.magnetic_id},degauss_id={self.degauss_id},physical_id={self.physical_id},simulation_id={self.simulation_id},electrical_id={self.electrical_id},manufacturer_id={self.manufacturer_id},controls_id={self.controls_id},reference_id={self.reference_id},)"



    
    # Using concrete inheritance: see https://docs.sqlalchemy.org/en/14/orm/inheritance.html
    __mapper_args__ = {
        'concrete': True
    }
    


class CombinedCorrector(Dipole):
    """
    Combined horizontal/vertical steering corrector, naming the two single-plane correctors it stands in for.
    """
    __tablename__ = 'CombinedCorrector'

    Horizontal_Corrector = Column(Text())
    Vertical_Corrector = Column(Text())
    name = Column(Text(), primary_key=True, nullable=False )
    hardware_class = Column(Enum('Magnet', 'Diagnostic', 'RF', 'Vacuum', 'Laser', 'Plasma', 'Feedback', 'Marker', 'Aperture', 'Stage', 'Lighting', 'Shutter', 'Wakefield', 'TwissMatch', 'Drift', 'Generic', 'Monitor', 'Simulation', 'Valve', 'LaserMirror', 'LaserEnergyMeter', 'LaserAttenuator', name='HardwareClassEnum'), nullable=False )
    hardware_type = Column(Text())
    hardware_model = Column(Text())
    machine_area = Column(Text())
    virtual_name = Column(Text())
    subelement = Column(Text())
    magnetic_id = Column(Integer(), ForeignKey('Corrector_Magnet.id'))
    magnetic = relationship("CorrectorMagnet", uselist=False, foreign_keys=[magnetic_id])
    degauss_id = Column(Integer(), ForeignKey('DegaussableElement.id'))
    degauss = relationship("DegaussableElement", uselist=False, foreign_keys=[degauss_id])
    physical_id = Column(Integer(), ForeignKey('PhysicalElement.id'))
    physical = relationship("PhysicalElement", uselist=False, foreign_keys=[physical_id])
    simulation_id = Column(Integer(), ForeignKey('MagnetSimulationElement.id'))
    simulation = relationship("MagnetSimulationElement", uselist=False, foreign_keys=[simulation_id])
    electrical_id = Column(Integer(), ForeignKey('ElectricalElement.id'))
    electrical = relationship("ElectricalElement", uselist=False, foreign_keys=[electrical_id])
    manufacturer_id = Column(Integer(), ForeignKey('ManufacturerElement.id'))
    manufacturer = relationship("ManufacturerElement", uselist=False, foreign_keys=[manufacturer_id])
    controls_id = Column(Integer(), ForeignKey('ControlsInformation.id'))
    controls = relationship("ControlsInformation", uselist=False, foreign_keys=[controls_id])
    reference_id = Column(Integer(), ForeignKey('ReferenceElement.id'))
    reference = relationship("ReferenceElement", uselist=False, foreign_keys=[reference_id])
    
    
    alias_rel = relationship( "CombinedCorrectorAlias" )
    alias = association_proxy("alias_rel", "alias",
                                  creator=lambda x_: CombinedCorrectorAlias(alias=x_))
    
    
    inputs_rel = relationship( "CombinedCorrectorInputs" )
    inputs = association_proxy("inputs_rel", "inputs",
                                  creator=lambda x_: CombinedCorrectorInputs(inputs=x_))
    
    
    outputs_rel = relationship( "CombinedCorrectorOutputs" )
    outputs = association_proxy("outputs_rel", "outputs",
                                  creator=lambda x_: CombinedCorrectorOutputs(outputs=x_))
    
    
    # ManyToMany
    upstream = relationship( "AcceleratorElement", secondary="CombinedCorrector_upstream")
    
    
    # ManyToMany
    downstream = relationship( "AcceleratorElement", secondary="CombinedCorrector_downstream")
    

    def __repr__(self):
        return f"CombinedCorrector(Horizontal_Corrector={self.Horizontal_Corrector},Vertical_Corrector={self.Vertical_Corrector},name={self.name},hardware_class={self.hardware_class},hardware_type={self.hardware_type},hardware_model={self.hardware_model},machine_area={self.machine_area},virtual_name={self.virtual_name},subelement={self.subelement},magnetic_id={self.magnetic_id},degauss_id={self.degauss_id},physical_id={self.physical_id},simulation_id={self.simulation_id},electrical_id={self.electrical_id},manufacturer_id={self.manufacturer_id},controls_id={self.controls_id},reference_id={self.reference_id},)"



    
    # Using concrete inheritance: see https://docs.sqlalchemy.org/en/14/orm/inheritance.html
    __mapper_args__ = {
        'concrete': True
    }
    


