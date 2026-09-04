# Class: OctupoleMagnet 


_Octupole magnet field, principal multipole order 3._



<div data-search-exclude markdown="1">



URI: [laura:OctupoleMagnet](https://w3id.org/laura/OctupoleMagnet)





```mermaid
 classDiagram
    class OctupoleMagnet
    click OctupoleMagnet href "../OctupoleMagnet/"
      MagneticElement <|-- OctupoleMagnet
        click MagneticElement href "../MagneticElement/"
      
      OctupoleMagnet : angle
        
      OctupoleMagnet : bore
        
      OctupoleMagnet : edge_field_integral
        
      OctupoleMagnet : entrance_edge_angle
        
      OctupoleMagnet : exit_edge_angle
        
      OctupoleMagnet : field_integral_coefficients
        
          
    
        
        
        OctupoleMagnet --> "0..1" FieldIntegral : field_integral_coefficients
        click FieldIntegral href "../FieldIntegral/"
    

        
      OctupoleMagnet : fringe_field_coefficient
        
      OctupoleMagnet : gap
        
      OctupoleMagnet : gradient
        
      OctupoleMagnet : length
        
      OctupoleMagnet : linear_saturation_coefficients
        
          
    
        
        
        OctupoleMagnet --> "0..1" LinearSaturationFit : linear_saturation_coefficients
        click LinearSaturationFit href "../LinearSaturationFit/"
    

        
      OctupoleMagnet : multipoles
        
          
    
        
        
        OctupoleMagnet --> "0..1" Multipoles : multipoles
        click Multipoles href "../Multipoles/"
    

        
      OctupoleMagnet : order
        
      OctupoleMagnet : plane
        
          
    
        
        
        OctupoleMagnet --> "0..1" BendingPlaneEnum : plane
        click BendingPlaneEnum href "../BendingPlaneEnum/"
    

        
      OctupoleMagnet : random_multipoles
        
          
    
        
        
        OctupoleMagnet --> "0..1" Multipoles : random_multipoles
        click Multipoles href "../Multipoles/"
    

        
      OctupoleMagnet : settle_time
        
      OctupoleMagnet : skew
        
      OctupoleMagnet : systematic_multipoles
        
          
    
        
        
        OctupoleMagnet --> "0..1" Multipoles : systematic_multipoles
        click Multipoles href "../Multipoles/"
    

        
      OctupoleMagnet : tilt
        
      OctupoleMagnet : width
        
      
```





## Inheritance
* [MagneticElement](MagneticElement.md)
    * **OctupoleMagnet**


## Slots

| Name | Cardinality and Range | Description | Inheritance |
| ---  | --- | --- | --- |
| [order](order.md) | 0..1 <br/> [Integer](Integer.md) | Principal multipole order (0 = dipole, 1 = quad, ?) | [MagneticElement](MagneticElement.md) |
| [skew](skew.md) | 0..1 <br/> [Boolean](Boolean.md) | Whether the magnet is rotated 45? to produce a skew field component | [MagneticElement](MagneticElement.md) |
| [length](length.md) | 0..1 <br/> [Double](Double.md) | Magnetic (effective) length [m] | [MagneticElement](MagneticElement.md) |
| [multipoles](multipoles.md) | 0..1 <br/> [Multipoles](Multipoles.md) | Integrated multipole field components | [MagneticElement](MagneticElement.md) |
| [systematic_multipoles](systematic_multipoles.md) | 0..1 <br/> [Multipoles](Multipoles.md) | Systematic (design) multipole errors at the reference radius | [MagneticElement](MagneticElement.md) |
| [random_multipoles](random_multipoles.md) | 0..1 <br/> [Multipoles](Multipoles.md) | Random multipole errors at the reference radius | [MagneticElement](MagneticElement.md) |
| [field_integral_coefficients](field_integral_coefficients.md) | 0..1 <br/> [FieldIntegral](FieldIntegral.md) | Polynomial calibration of integrated field vs | [MagneticElement](MagneticElement.md) |
| [linear_saturation_coefficients](linear_saturation_coefficients.md) | 0..1 <br/> [LinearSaturationFit](LinearSaturationFit.md) | Bi-linear saturation calibration | [MagneticElement](MagneticElement.md) |
| [settle_time](settle_time.md) | 0..1 <br/> [Double](Double.md) | Power-supply settle time after a change [s] | [MagneticElement](MagneticElement.md) |
| [entrance_edge_angle](entrance_edge_angle.md) | 0..1 <br/> [String](String.md)&nbsp;or&nbsp;<br />[Double](Double.md) | Fringe-field entrance edge angle [rad] | [MagneticElement](MagneticElement.md) |
| [exit_edge_angle](exit_edge_angle.md) | 0..1 <br/> [String](String.md)&nbsp;or&nbsp;<br />[Double](Double.md) | Fringe-field exit edge angle [rad] | [MagneticElement](MagneticElement.md) |
| [gap](gap.md) | 0..1 <br/> [Double](Double.md) | Full gap between pole faces [m] | [MagneticElement](MagneticElement.md) |
| [bore](bore.md) | 0..1 <br/> [Double](Double.md) | Magnet bore radius [m] | [MagneticElement](MagneticElement.md) |
| [plane](plane.md) | 0..1 <br/> [BendingPlaneEnum](BendingPlaneEnum.md) | Principal bending / focusing plane (``Horizontal``, ``Vertical``, or ``Combin... | [MagneticElement](MagneticElement.md) |
| [width](width.md) | 0..1 <br/> [Double](Double.md) | Physical width of the magnet in the bending plane [m] | [MagneticElement](MagneticElement.md) |
| [tilt](tilt.md) | 0..1 <br/> [Double](Double.md) | Global tilt about the beam axis [rad] | [MagneticElement](MagneticElement.md) |
| [edge_field_integral](edge_field_integral.md) | 0..1 <br/> [Double](Double.md) | Enge fringe-field integral parameter (dimensionless) | [MagneticElement](MagneticElement.md) |
| [fringe_field_coefficient](fringe_field_coefficient.md) | 0..1 <br/> [Double](Double.md) | Coefficient controlling the fringe-field roll-off rate | [MagneticElement](MagneticElement.md) |
| [gradient](gradient.md) | 0..1 <br/> [Double](Double.md) | Peak field gradient [T/m] (quads) or peak field [T] (dipoles) | [MagneticElement](MagneticElement.md) |
| [angle](angle.md) | 0..1 <br/> [Double](Double.md) | Integrated bending angle [rad] | [MagneticElement](MagneticElement.md) |





## Usages

| used by | used in | type | used |
| ---  | --- | --- | --- |
| [Octupole](Octupole.md) | [magnetic](magnetic.md) | range | [OctupoleMagnet](OctupoleMagnet.md) |












## Identifier and Mapping Information





### Schema Source


* from schema: https://w3id.org/laura/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | laura:OctupoleMagnet |
| native | laura:OctupoleMagnet |






## LinkML Source

<!-- TODO: investigate https://stackoverflow.com/questions/37606292/how-to-create-tabbed-code-blocks-in-mkdocs-or-sphinx -->

### Direct

<details>
```yaml
name: Octupole_Magnet
description: Octupole magnet field, principal multipole order 3.
from_schema: https://w3id.org/laura/schema
is_a: MagneticElement
slot_usage:
  order:
    name: order
    ifabsent: '3'
    equals_number: 3

```
</details>

### Induced

<details>
```yaml
name: Octupole_Magnet
description: Octupole magnet field, principal multipole order 3.
from_schema: https://w3id.org/laura/schema
is_a: MagneticElement
slot_usage:
  order:
    name: order
    ifabsent: '3'
    equals_number: 3
attributes:
  order:
    name: order
    description: Principal multipole order (0 = dipole, 1 = quad, ?).
    from_schema: https://w3id.org/laura/schema/magnetic
    ifabsent: '3'
    owner: Octupole_Magnet
    domain_of:
    - Multipole
    - MagneticElement
    - Corrector_Magnet
    - Solenoid_Magnet
    range: integer
    minimum_value: -1
    equals_number: 3
  skew:
    name: skew
    description: Whether the magnet is rotated 45? to produce a skew field component.
    from_schema: https://w3id.org/laura/schema/magnetic
    ifabsent: 'False'
    owner: Octupole_Magnet
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
    owner: Octupole_Magnet
    domain_of:
    - PhysicalElement
    - MagneticElement
    - Corrector_Magnet
    - Solenoid_Magnet
    - Wiggler_Magnet
    - NonLinearLens_Magnet
    range: double
    minimum_value: 0.0
    unit:
      ucum_code: m
  multipoles:
    name: multipoles
    description: Integrated multipole field components.
    from_schema: https://w3id.org/laura/schema/magnetic
    rank: 1000
    owner: Octupole_Magnet
    domain_of:
    - MagneticElement
    range: Multipoles
  systematic_multipoles:
    name: systematic_multipoles
    description: Systematic (design) multipole errors at the reference radius.
    from_schema: https://w3id.org/laura/schema/magnetic
    rank: 1000
    owner: Octupole_Magnet
    domain_of:
    - MagneticElement
    range: Multipoles
  random_multipoles:
    name: random_multipoles
    description: Random multipole errors at the reference radius.
    from_schema: https://w3id.org/laura/schema/magnetic
    rank: 1000
    owner: Octupole_Magnet
    domain_of:
    - MagneticElement
    range: Multipoles
  field_integral_coefficients:
    name: field_integral_coefficients
    description: Polynomial calibration of integrated field vs. current.
    from_schema: https://w3id.org/laura/schema/magnetic
    rank: 1000
    owner: Octupole_Magnet
    domain_of:
    - MagneticElement
    - Solenoid_Magnet
    range: FieldIntegral
  linear_saturation_coefficients:
    name: linear_saturation_coefficients
    description: Bi-linear saturation calibration.
    from_schema: https://w3id.org/laura/schema/magnetic
    rank: 1000
    owner: Octupole_Magnet
    domain_of:
    - MagneticElement
    - Solenoid_Magnet
    range: LinearSaturationFit
  settle_time:
    name: settle_time
    description: Power-supply settle time after a change [s].
    from_schema: https://w3id.org/laura/schema/magnetic
    rank: 1000
    owner: Octupole_Magnet
    domain_of:
    - MagneticElement
    - Solenoid_Magnet
    range: double
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
    owner: Octupole_Magnet
    domain_of:
    - MagneticElement
    range: string
    unit:
      ucum_code: rad
    any_of:
    - range: double
    - range: string
  exit_edge_angle:
    name: exit_edge_angle
    description: Fringe-field exit edge angle [rad].
    in_subset:
    - functional_parameters
    - bend_angle_reference
    from_schema: https://w3id.org/laura/schema/magnetic
    rank: 1000
    owner: Octupole_Magnet
    domain_of:
    - MagneticElement
    range: string
    unit:
      ucum_code: rad
    any_of:
    - range: double
    - range: string
  gap:
    name: gap
    description: Full gap between pole faces [m].
    from_schema: https://w3id.org/laura/schema/magnetic
    rank: 1000
    ifabsent: float(0.032)
    owner: Octupole_Magnet
    domain_of:
    - MagneticElement
    range: double
    minimum_value: 0.0
    unit:
      ucum_code: m
  bore:
    name: bore
    description: Magnet bore radius [m].
    from_schema: https://w3id.org/laura/schema/magnetic
    rank: 1000
    ifabsent: float(0.037)
    owner: Octupole_Magnet
    domain_of:
    - MagneticElement
    range: double
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
    owner: Octupole_Magnet
    domain_of:
    - MagneticElement
    range: BendingPlaneEnum
  width:
    name: width
    description: Physical width of the magnet in the bending plane [m].
    from_schema: https://w3id.org/laura/schema/magnetic
    ifabsent: float(0.2)
    owner: Octupole_Magnet
    domain_of:
    - BeamBeamSimulationElement
    - MagneticElement
    range: double
    unit:
      ucum_code: m
  tilt:
    name: tilt
    description: Global tilt about the beam axis [rad].
    from_schema: https://w3id.org/laura/schema/magnetic
    ifabsent: float(0.0)
    owner: Octupole_Magnet
    domain_of:
    - ElectrostaticSeparatorSimulationElement
    - MagneticElement
    - Corrector_Magnet
    range: double
    unit:
      ucum_code: rad
  edge_field_integral:
    name: edge_field_integral
    description: Enge fringe-field integral parameter (dimensionless).
    from_schema: https://w3id.org/laura/schema/magnetic
    ifabsent: float(0.5)
    owner: Octupole_Magnet
    domain_of:
    - MagnetSimulationElement
    - MagneticElement
    range: double
  fringe_field_coefficient:
    name: fringe_field_coefficient
    description: Coefficient controlling the fringe-field roll-off rate.
    from_schema: https://w3id.org/laura/schema/magnetic
    rank: 1000
    ifabsent: float(0.0)
    owner: Octupole_Magnet
    domain_of:
    - MagneticElement
    range: double
  gradient:
    name: gradient
    description: Peak field gradient [T/m] (quads) or peak field [T] (dipoles).
    from_schema: https://w3id.org/laura/schema/magnetic
    rank: 1000
    owner: Octupole_Magnet
    domain_of:
    - MagneticElement
    range: double
    unit:
      ucum_code: T.m-1
  angle:
    name: angle
    description: Integrated bending angle [rad]. Dipoles only.
    from_schema: https://w3id.org/laura/schema/magnetic
    rank: 1000
    owner: Octupole_Magnet
    domain_of:
    - MagneticElement
    range: double
    unit:
      ucum_code: rad

```
</details></div>