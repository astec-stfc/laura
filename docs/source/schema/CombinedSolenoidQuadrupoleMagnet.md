# Class: CombinedSolenoidQuadrupoleMagnet 


_Combined solenoid and quadrupole magnetic field._



<div data-search-exclude markdown="1">



URI: [laura:CombinedSolenoidQuadrupole_Magnet](https://w3id.org/laura/CombinedSolenoidQuadrupole_Magnet)





```mermaid
 classDiagram
    class CombinedSolenoidQuadrupoleMagnet
    click CombinedSolenoidQuadrupoleMagnet href "../CombinedSolenoidQuadrupoleMagnet/"
      MagneticElement <|-- CombinedSolenoidQuadrupoleMagnet
        click MagneticElement href "../MagneticElement/"
      
      CombinedSolenoidQuadrupoleMagnet : angle
        
      CombinedSolenoidQuadrupoleMagnet : bore
        
      CombinedSolenoidQuadrupoleMagnet : edge_field_integral
        
      CombinedSolenoidQuadrupoleMagnet : entrance_edge_angle
        
      CombinedSolenoidQuadrupoleMagnet : exit_edge_angle
        
      CombinedSolenoidQuadrupoleMagnet : exit_edge_field_integral
        
      CombinedSolenoidQuadrupoleMagnet : exit_gap
        
      CombinedSolenoidQuadrupoleMagnet : field_integral_coefficients
        
          
    
        
        
        CombinedSolenoidQuadrupoleMagnet --> "0..1" FieldIntegral : field_integral_coefficients
        click FieldIntegral href "../FieldIntegral/"
    

        
      CombinedSolenoidQuadrupoleMagnet : fringe_field_coefficient
        
      CombinedSolenoidQuadrupoleMagnet : gap
        
      CombinedSolenoidQuadrupoleMagnet : gradient
        
      CombinedSolenoidQuadrupoleMagnet : length
        
      CombinedSolenoidQuadrupoleMagnet : linear_saturation_coefficients
        
          
    
        
        
        CombinedSolenoidQuadrupoleMagnet --> "0..1" LinearSaturationFit : linear_saturation_coefficients
        click LinearSaturationFit href "../LinearSaturationFit/"
    

        
      CombinedSolenoidQuadrupoleMagnet : multipoles
        
          
    
        
        
        CombinedSolenoidQuadrupoleMagnet --> "0..1" Multipoles : multipoles
        click Multipoles href "../Multipoles/"
    

        
      CombinedSolenoidQuadrupoleMagnet : order
        
      CombinedSolenoidQuadrupoleMagnet : plane
        
          
    
        
        
        CombinedSolenoidQuadrupoleMagnet --> "0..1" BendingPlaneEnum : plane
        click BendingPlaneEnum href "../BendingPlaneEnum/"
    

        
      CombinedSolenoidQuadrupoleMagnet : random_multipoles
        
          
    
        
        
        CombinedSolenoidQuadrupoleMagnet --> "0..1" Multipoles : random_multipoles
        click Multipoles href "../Multipoles/"
    

        
      CombinedSolenoidQuadrupoleMagnet : settle_time
        
      CombinedSolenoidQuadrupoleMagnet : skew
        
      CombinedSolenoidQuadrupoleMagnet : solenoid_fields
        
          
    
        
        
        CombinedSolenoidQuadrupoleMagnet --> "0..1" SolenoidFields : solenoid_fields
        click SolenoidFields href "../SolenoidFields/"
    

        
      CombinedSolenoidQuadrupoleMagnet : systematic_multipoles
        
          
    
        
        
        CombinedSolenoidQuadrupoleMagnet --> "0..1" Multipoles : systematic_multipoles
        click Multipoles href "../Multipoles/"
    

        
      CombinedSolenoidQuadrupoleMagnet : tilt
        
      CombinedSolenoidQuadrupoleMagnet : width
        
      
```





## Inheritance
* [MagneticElement](MagneticElement.md)
    * **CombinedSolenoidQuadrupoleMagnet**


## Class Properties

| Property | Value |
| --- | --- |
| Class URI | [laura:CombinedSolenoidQuadrupole_Magnet](https://w3id.org/laura/CombinedSolenoidQuadrupole_Magnet) |


## Slots

| Name | Cardinality and Range | Description | Inheritance |
| ---  | --- | --- | --- |
| [solenoid_fields](solenoid_fields.md) | 0..1 <br/> [SolenoidFields](SolenoidFields.md) | Nominal integrated axial solenoid field components | direct |
| [order](order.md) | 0..1 <br/> [Integer](Integer.md) | Principal multipole order (0 = dipole, 1 = quad, ?) | [MagneticElement](MagneticElement.md) |
| [skew](skew.md) | 0..1 <br/> [Boolean](Boolean.md) | Whether the magnet is rotated 45? to produce a skew field component | [MagneticElement](MagneticElement.md) |
| [length](length.md) | 0..1 <br/> [Float](Float.md) | Magnetic (effective) length [m] | [MagneticElement](MagneticElement.md) |
| [multipoles](multipoles.md) | 0..1 <br/> [Multipoles](Multipoles.md) | Integrated multipole field components | [MagneticElement](MagneticElement.md) |
| [systematic_multipoles](systematic_multipoles.md) | 0..1 <br/> [Multipoles](Multipoles.md) | Systematic (design) multipole errors at the reference radius | [MagneticElement](MagneticElement.md) |
| [random_multipoles](random_multipoles.md) | 0..1 <br/> [Multipoles](Multipoles.md) | Random multipole errors at the reference radius | [MagneticElement](MagneticElement.md) |
| [field_integral_coefficients](field_integral_coefficients.md) | 0..1 <br/> [FieldIntegral](FieldIntegral.md) | Polynomial calibration of integrated field vs | [MagneticElement](MagneticElement.md) |
| [linear_saturation_coefficients](linear_saturation_coefficients.md) | 0..1 <br/> [LinearSaturationFit](LinearSaturationFit.md) | Bi-linear saturation calibration | [MagneticElement](MagneticElement.md) |
| [settle_time](settle_time.md) | 0..1 <br/> [Float](Float.md) | Power-supply settle time after a change [s] | [MagneticElement](MagneticElement.md) |
| [entrance_edge_angle](entrance_edge_angle.md) | 0..1 <br/> [String](String.md)&nbsp;or&nbsp;<br />[Float](Float.md) | Fringe-field entrance edge angle [rad] | [MagneticElement](MagneticElement.md) |
| [exit_edge_angle](exit_edge_angle.md) | 0..1 <br/> [String](String.md)&nbsp;or&nbsp;<br />[Float](Float.md) | Fringe-field exit edge angle [rad] | [MagneticElement](MagneticElement.md) |
| [gap](gap.md) | 0..1 <br/> [Float](Float.md) | Full gap between pole faces [m] | [MagneticElement](MagneticElement.md) |
| [bore](bore.md) | 0..1 <br/> [Float](Float.md) | Magnet bore radius [m] | [MagneticElement](MagneticElement.md) |
| [plane](plane.md) | 0..1 <br/> [BendingPlaneEnum](BendingPlaneEnum.md) | Principal bending / focusing plane (``Horizontal``, ``Vertical``, or ``Combin... | [MagneticElement](MagneticElement.md) |
| [width](width.md) | 0..1 <br/> [Float](Float.md) | Physical width of the magnet in the bending plane [m] | [MagneticElement](MagneticElement.md) |
| [tilt](tilt.md) | 0..1 <br/> [Float](Float.md) | Global tilt about the beam axis [rad] | [MagneticElement](MagneticElement.md) |
| [edge_field_integral](edge_field_integral.md) | 0..1 <br/> [Float](Float.md) | Enge fringe-field integral parameter (dimensionless) at the entrance face, an... | [MagneticElement](MagneticElement.md) |
| [exit_edge_field_integral](exit_edge_field_integral.md) | 0..1 <br/> [Float](Float.md) | Enge fringe-field integral at the exit face | [MagneticElement](MagneticElement.md) |
| [exit_gap](exit_gap.md) | 0..1 <br/> [Float](Float.md) | Full gap between pole faces at the exit face [m] | [MagneticElement](MagneticElement.md) |
| [fringe_field_coefficient](fringe_field_coefficient.md) | 0..1 <br/> [Float](Float.md) | Coefficient controlling the fringe-field roll-off rate | [MagneticElement](MagneticElement.md) |
| [gradient](gradient.md) | 0..1 <br/> [Float](Float.md) | Peak field gradient [T/m] (quads) or peak field [T] (dipoles) | [MagneticElement](MagneticElement.md) |
| [angle](angle.md) | 0..1 <br/> [Float](Float.md) | Integrated bending angle [rad] | [MagneticElement](MagneticElement.md) |





## Usages

| used by | used in | type | used |
| ---  | --- | --- | --- |
| [CombinedSolenoidQuadrupole](CombinedSolenoidQuadrupole.md) | [magnetic](magnetic.md) | range | [CombinedSolenoidQuadrupoleMagnet](CombinedSolenoidQuadrupoleMagnet.md) |












## Identifier and Mapping Information





### Schema Source


* from schema: https://w3id.org/laura/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | laura:CombinedSolenoidQuadrupole_Magnet |
| native | laura:CombinedSolenoidQuadrupoleMagnet |






## LinkML Source

<!-- TODO: investigate https://stackoverflow.com/questions/37606292/how-to-create-tabbed-code-blocks-in-mkdocs-or-sphinx -->

### Direct

<details>
```yaml
name: CombinedSolenoidQuadrupole_Magnet
description: Combined solenoid and quadrupole magnetic field.
from_schema: https://w3id.org/laura/schema
is_a: MagneticElement
slot_usage:
  order:
    name: order
    ifabsent: int(1)
    equals_number: 1
attributes:
  solenoid_fields:
    name: solenoid_fields
    description: Nominal integrated axial solenoid field components.
    from_schema: https://w3id.org/laura/schema/magnetic
    rank: 1000
    domain_of:
    - CombinedSolenoidQuadrupole_Magnet
    range: SolenoidFields
class_uri: laura:CombinedSolenoidQuadrupole_Magnet

```
</details>

### Induced

<details>
```yaml
name: CombinedSolenoidQuadrupole_Magnet
description: Combined solenoid and quadrupole magnetic field.
from_schema: https://w3id.org/laura/schema
is_a: MagneticElement
slot_usage:
  order:
    name: order
    ifabsent: int(1)
    equals_number: 1
attributes:
  solenoid_fields:
    name: solenoid_fields
    description: Nominal integrated axial solenoid field components.
    from_schema: https://w3id.org/laura/schema/magnetic
    rank: 1000
    owner: CombinedSolenoidQuadrupole_Magnet
    domain_of:
    - CombinedSolenoidQuadrupole_Magnet
    range: SolenoidFields
  order:
    name: order
    description: Principal multipole order (0 = dipole, 1 = quad, ?).
    from_schema: https://w3id.org/laura/schema/magnetic
    ifabsent: int(1)
    owner: CombinedSolenoidQuadrupole_Magnet
    domain_of:
    - Multipole
    - MagneticElement
    - Corrector_Magnet
    - Solenoid_Magnet
    range: integer
    minimum_value: -1
    equals_number: 1
  skew:
    name: skew
    description: Whether the magnet is rotated 45? to produce a skew field component.
    from_schema: https://w3id.org/laura/schema/magnetic
    ifabsent: 'False'
    owner: CombinedSolenoidQuadrupole_Magnet
    domain_of:
    - Multipole
    - MagneticElement
    range: boolean
  length:
    name: length
    description: Magnetic (effective) length [m].
    from_schema: https://w3id.org/laura/schema/magnetic
    aliases:
    - magnetic_length
    ifabsent: float(0)
    owner: CombinedSolenoidQuadrupole_Magnet
    domain_of:
    - PhysicalElement
    - MagneticElement
    - Corrector_Magnet
    - Solenoid_Magnet
    - Wiggler_Magnet
    - NonLinearLens_Magnet
    range: float
    minimum_value: 0.0
    unit:
      ucum_code: m
  multipoles:
    name: multipoles
    description: Integrated multipole field components.
    from_schema: https://w3id.org/laura/schema/magnetic
    rank: 1000
    owner: CombinedSolenoidQuadrupole_Magnet
    domain_of:
    - MagneticElement
    range: Multipoles
  systematic_multipoles:
    name: systematic_multipoles
    description: Systematic (design) multipole errors at the reference radius.
    from_schema: https://w3id.org/laura/schema/magnetic
    rank: 1000
    owner: CombinedSolenoidQuadrupole_Magnet
    domain_of:
    - MagneticElement
    range: Multipoles
  random_multipoles:
    name: random_multipoles
    description: Random multipole errors at the reference radius.
    from_schema: https://w3id.org/laura/schema/magnetic
    rank: 1000
    owner: CombinedSolenoidQuadrupole_Magnet
    domain_of:
    - MagneticElement
    range: Multipoles
  field_integral_coefficients:
    name: field_integral_coefficients
    description: Polynomial calibration of integrated field vs. current.
    from_schema: https://w3id.org/laura/schema/magnetic
    rank: 1000
    owner: CombinedSolenoidQuadrupole_Magnet
    domain_of:
    - MagneticElement
    - Solenoid_Magnet
    range: FieldIntegral
  linear_saturation_coefficients:
    name: linear_saturation_coefficients
    description: Bi-linear saturation calibration.
    from_schema: https://w3id.org/laura/schema/magnetic
    rank: 1000
    owner: CombinedSolenoidQuadrupole_Magnet
    domain_of:
    - MagneticElement
    - Solenoid_Magnet
    range: LinearSaturationFit
  settle_time:
    name: settle_time
    description: Power-supply settle time after a change [s].
    from_schema: https://w3id.org/laura/schema/magnetic
    rank: 1000
    owner: CombinedSolenoidQuadrupole_Magnet
    domain_of:
    - MagneticElement
    - Solenoid_Magnet
    range: float
    unit:
      ucum_code: s
  entrance_edge_angle:
    name: entrance_edge_angle
    description: Fringe-field entrance edge angle [rad].
    in_subset:
    - functional_parameters
    - bend_angle_reference
    from_schema: https://w3id.org/laura/schema/magnetic
    rank: 1000
    owner: CombinedSolenoidQuadrupole_Magnet
    domain_of:
    - MagneticElement
    range: string
    unit:
      ucum_code: rad
    any_of:
    - range: float
    - range: string
  exit_edge_angle:
    name: exit_edge_angle
    description: Fringe-field exit edge angle [rad].
    in_subset:
    - functional_parameters
    - bend_angle_reference
    from_schema: https://w3id.org/laura/schema/magnetic
    rank: 1000
    owner: CombinedSolenoidQuadrupole_Magnet
    domain_of:
    - MagneticElement
    range: string
    unit:
      ucum_code: rad
    any_of:
    - range: float
    - range: string
  gap:
    name: gap
    description: Full gap between pole faces [m].
    from_schema: https://w3id.org/laura/schema/magnetic
    rank: 1000
    ifabsent: float(0.032)
    owner: CombinedSolenoidQuadrupole_Magnet
    domain_of:
    - MagneticElement
    range: float
    minimum_value: 0.0
    unit:
      ucum_code: m
  bore:
    name: bore
    description: Magnet bore radius [m].
    from_schema: https://w3id.org/laura/schema/magnetic
    rank: 1000
    ifabsent: float(0.037)
    owner: CombinedSolenoidQuadrupole_Magnet
    domain_of:
    - MagneticElement
    range: float
    minimum_value: 0.0
    unit:
      ucum_code: m
  plane:
    name: plane
    description: Principal bending / focusing plane (``Horizontal``, ``Vertical``,
      or ``Combined``).
    from_schema: https://w3id.org/laura/schema/magnetic
    rank: 1000
    ifabsent: string(Horizontal)
    owner: CombinedSolenoidQuadrupole_Magnet
    domain_of:
    - MagneticElement
    range: BendingPlaneEnum
  width:
    name: width
    description: Physical width of the magnet in the bending plane [m].
    from_schema: https://w3id.org/laura/schema/magnetic
    ifabsent: float(0.2)
    owner: CombinedSolenoidQuadrupole_Magnet
    domain_of:
    - BeamBeamSimulationElement
    - MagneticElement
    range: float
    unit:
      ucum_code: m
  tilt:
    name: tilt
    description: Global tilt about the beam axis [rad].
    from_schema: https://w3id.org/laura/schema/magnetic
    ifabsent: float(0.0)
    owner: CombinedSolenoidQuadrupole_Magnet
    domain_of:
    - ElectrostaticSeparatorSimulationElement
    - MagneticElement
    - Corrector_Magnet
    range: float
    unit:
      ucum_code: rad
  edge_field_integral:
    name: edge_field_integral
    description: Enge fringe-field integral parameter (dimensionless) at the entrance
      face, and at both faces unless ``exit_edge_field_integral`` says otherwise.
    from_schema: https://w3id.org/laura/schema/magnetic
    ifabsent: float(0.5)
    owner: CombinedSolenoidQuadrupole_Magnet
    domain_of:
    - MagnetSimulationElement
    - MagneticElement
    range: float
  exit_edge_field_integral:
    name: exit_edge_field_integral
    description: 'Enge fringe-field integral at the exit face. Absent means the exit
      face matches the entrance, which is what a lattice quoting a single integral
      means and what Bmad''s own ``fintx`` default does, so files that set only ``edge_field_integral``
      are unaffected. Set it only when the faces genuinely differ: a bend split by
      superposition carries the entrance fringe on its first piece and the exit fringe
      on its last, and collapsing the two both invents a fringe mid-magnet and drops
      the real one. The fringe integral enters only the vertical edge kick, so getting
      this wrong is invisible to every horizontal check.'
    from_schema: https://w3id.org/laura/schema/magnetic
    rank: 1000
    owner: CombinedSolenoidQuadrupole_Magnet
    domain_of:
    - MagneticElement
    range: float
  exit_gap:
    name: exit_gap
    description: Full gap between pole faces at the exit face [m]. Absent means the
      same as ``gap``. See ``exit_edge_field_integral``.
    from_schema: https://w3id.org/laura/schema/magnetic
    rank: 1000
    owner: CombinedSolenoidQuadrupole_Magnet
    domain_of:
    - MagneticElement
    range: float
    minimum_value: 0.0
    unit:
      ucum_code: m
  fringe_field_coefficient:
    name: fringe_field_coefficient
    description: Coefficient controlling the fringe-field roll-off rate.
    from_schema: https://w3id.org/laura/schema/magnetic
    rank: 1000
    ifabsent: float(0.0)
    owner: CombinedSolenoidQuadrupole_Magnet
    domain_of:
    - MagneticElement
    range: float
  gradient:
    name: gradient
    description: Peak field gradient [T/m] (quads) or peak field [T] (dipoles).
    from_schema: https://w3id.org/laura/schema/magnetic
    rank: 1000
    owner: CombinedSolenoidQuadrupole_Magnet
    domain_of:
    - MagneticElement
    range: float
    unit:
      ucum_code: T.m-1
  angle:
    name: angle
    description: 'Integrated bending angle [rad]. Dipoles only. Part of the data model
      (lattice YAML may set it), but derived from multipoles.K0L rather than stored:
      the MagneticElement wrapper implements it as a read/write property so a symbolic
      bend angle survives round-tripping and reads follow the global resolution mode.
      Listed in _PYDANTIC_EXCLUDED_SLOTS in generate_pydantic.py so the generated
      base does not also declare it as a field, which would make pydantic treat the
      property object as the field default.'
    from_schema: https://w3id.org/laura/schema/magnetic
    rank: 1000
    owner: CombinedSolenoidQuadrupole_Magnet
    domain_of:
    - MagneticElement
    range: float
    unit:
      ucum_code: rad
class_uri: laura:CombinedSolenoidQuadrupole_Magnet

```
</details></div>