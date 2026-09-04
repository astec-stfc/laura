# Class: CorrectorMagnet 


_Steering-corrector field. A dipole magnet whose order-0 multipole is addressed by beam plane: the normal component is the horizontal kick and the skew component is the vertical kick. Inherits from  Dipole_Magnet / MagneticElement._



<div data-search-exclude markdown="1">



URI: [laura:Corrector_Magnet](https://w3id.org/laura/Corrector_Magnet)





```mermaid
 classDiagram
    class CorrectorMagnet
    click CorrectorMagnet href "../CorrectorMagnet/"
      DipoleMagnet <|-- CorrectorMagnet
        click DipoleMagnet href "../DipoleMagnet/"
      
      CorrectorMagnet : angle
        
      CorrectorMagnet : bore
        
      CorrectorMagnet : edge_field_integral
        
      CorrectorMagnet : entrance_edge_angle
        
      CorrectorMagnet : exit_edge_angle
        
      CorrectorMagnet : field_integral_coefficients
        
          
    
        
        
        CorrectorMagnet --> "0..1" FieldIntegral : field_integral_coefficients
        click FieldIntegral href "../FieldIntegral/"
    

        
      CorrectorMagnet : fringe_field_coefficient
        
      CorrectorMagnet : gap
        
      CorrectorMagnet : gradient
        
      CorrectorMagnet : horizontal_kick
        
      CorrectorMagnet : length
        
      CorrectorMagnet : linear_saturation_coefficients
        
          
    
        
        
        CorrectorMagnet --> "0..1" LinearSaturationFit : linear_saturation_coefficients
        click LinearSaturationFit href "../LinearSaturationFit/"
    

        
      CorrectorMagnet : multipoles
        
          
    
        
        
        CorrectorMagnet --> "0..1" Multipoles : multipoles
        click Multipoles href "../Multipoles/"
    

        
      CorrectorMagnet : order
        
      CorrectorMagnet : plane
        
          
    
        
        
        CorrectorMagnet --> "0..1" BendingPlaneEnum : plane
        click BendingPlaneEnum href "../BendingPlaneEnum/"
    

        
      CorrectorMagnet : random_multipoles
        
          
    
        
        
        CorrectorMagnet --> "0..1" Multipoles : random_multipoles
        click Multipoles href "../Multipoles/"
    

        
      CorrectorMagnet : settle_time
        
      CorrectorMagnet : skew
        
      CorrectorMagnet : systematic_multipoles
        
          
    
        
        
        CorrectorMagnet --> "0..1" Multipoles : systematic_multipoles
        click Multipoles href "../Multipoles/"
    

        
      CorrectorMagnet : tilt
        
      CorrectorMagnet : vertical_kick
        
      CorrectorMagnet : width
        
      
```





## Inheritance
* [MagneticElement](MagneticElement.md)
    * [DipoleMagnet](DipoleMagnet.md)
        * **CorrectorMagnet**


## Class Properties

| Property | Value |
| --- | --- |
| Class URI | [laura:Corrector_Magnet](https://w3id.org/laura/Corrector_Magnet) |


## Slots

| Name | Cardinality and Range | Description | Inheritance |
| ---  | --- | --- | --- |
| [horizontal_kick](horizontal_kick.md) | 0..1 <br/> [Float](Float.md)&nbsp;or&nbsp;<br />[String](String.md) | Horizontal deflection [rad] | direct |
| [vertical_kick](vertical_kick.md) | 0..1 <br/> [Float](Float.md)&nbsp;or&nbsp;<br />[String](String.md) | Vertical deflection [rad] | direct |
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
| [edge_field_integral](edge_field_integral.md) | 0..1 <br/> [Float](Float.md) | Enge fringe-field integral parameter (dimensionless) | [MagneticElement](MagneticElement.md) |
| [fringe_field_coefficient](fringe_field_coefficient.md) | 0..1 <br/> [Float](Float.md) | Coefficient controlling the fringe-field roll-off rate | [MagneticElement](MagneticElement.md) |
| [gradient](gradient.md) | 0..1 <br/> [Float](Float.md) | Peak field gradient [T/m] (quads) or peak field [T] (dipoles) | [MagneticElement](MagneticElement.md) |
| [angle](angle.md) | 0..1 <br/> [Float](Float.md) | Integrated bending angle [rad] | [MagneticElement](MagneticElement.md) |





## Usages

| used by | used in | type | used |
| ---  | --- | --- | --- |
| [HorizontalCorrector](HorizontalCorrector.md) | [magnetic](magnetic.md) | range | [CorrectorMagnet](CorrectorMagnet.md) |
| [VerticalCorrector](VerticalCorrector.md) | [magnetic](magnetic.md) | range | [CorrectorMagnet](CorrectorMagnet.md) |
| [CombinedCorrectorMagnet](CombinedCorrectorMagnet.md) | [horizontal](horizontal.md) | range | [CorrectorMagnet](CorrectorMagnet.md) |
| [CombinedCorrectorMagnet](CombinedCorrectorMagnet.md) | [vertical](vertical.md) | range | [CorrectorMagnet](CorrectorMagnet.md) |












## Identifier and Mapping Information





### Schema Source


* from schema: https://w3id.org/laura/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | laura:Corrector_Magnet |
| native | laura:CorrectorMagnet |






## LinkML Source

<!-- TODO: investigate https://stackoverflow.com/questions/37606292/how-to-create-tabbed-code-blocks-in-mkdocs-or-sphinx -->

### Direct

<details>
```yaml
name: Corrector_Magnet
description: 'Steering-corrector field. A dipole magnet whose order-0 multipole is
  addressed by beam plane: the normal component is the horizontal kick and the skew
  component is the vertical kick. Inherits from  Dipole_Magnet / MagneticElement.'
from_schema: https://w3id.org/laura/schema
is_a: Dipole_Magnet
attributes:
  horizontal_kick:
    name: horizontal_kick
    description: Horizontal deflection [rad]. May be a functional expression. Derived
      from multipoles.K0L.normal.
    in_subset:
    - functional_parameters
    from_schema: https://w3id.org/laura/schema/magnetic
    rank: 1000
    ifabsent: float(0.0)
    domain_of:
    - Corrector_Magnet
    range: float
    unit:
      ucum_code: rad
    any_of:
    - range: float
    - range: string
  vertical_kick:
    name: vertical_kick
    description: Vertical deflection [rad]. May be a functional expression. Derived
      from multipoles.K0L.skew.
    in_subset:
    - functional_parameters
    from_schema: https://w3id.org/laura/schema/magnetic
    rank: 1000
    ifabsent: float(0.0)
    domain_of:
    - Corrector_Magnet
    range: float
    unit:
      ucum_code: rad
    any_of:
    - range: float
    - range: string
class_uri: laura:Corrector_Magnet

```
</details>

### Induced

<details>
```yaml
name: Corrector_Magnet
description: 'Steering-corrector field. A dipole magnet whose order-0 multipole is
  addressed by beam plane: the normal component is the horizontal kick and the skew
  component is the vertical kick. Inherits from  Dipole_Magnet / MagneticElement.'
from_schema: https://w3id.org/laura/schema
is_a: Dipole_Magnet
attributes:
  horizontal_kick:
    name: horizontal_kick
    description: Horizontal deflection [rad]. May be a functional expression. Derived
      from multipoles.K0L.normal.
    in_subset:
    - functional_parameters
    from_schema: https://w3id.org/laura/schema/magnetic
    rank: 1000
    ifabsent: float(0.0)
    owner: Corrector_Magnet
    domain_of:
    - Corrector_Magnet
    range: float
    unit:
      ucum_code: rad
    any_of:
    - range: float
    - range: string
  vertical_kick:
    name: vertical_kick
    description: Vertical deflection [rad]. May be a functional expression. Derived
      from multipoles.K0L.skew.
    in_subset:
    - functional_parameters
    from_schema: https://w3id.org/laura/schema/magnetic
    rank: 1000
    ifabsent: float(0.0)
    owner: Corrector_Magnet
    domain_of:
    - Corrector_Magnet
    range: float
    unit:
      ucum_code: rad
    any_of:
    - range: float
    - range: string
  order:
    name: order
    description: Principal multipole order (0 = dipole, 1 = quad, ?).
    from_schema: https://w3id.org/laura/schema/magnetic
    ifabsent: '0'
    owner: Corrector_Magnet
    domain_of:
    - Multipole
    - MagneticElement
    - Solenoid_Magnet
    range: integer
    minimum_value: -1
    equals_number: 0
  skew:
    name: skew
    description: Whether the magnet is rotated 45? to produce a skew field component.
    from_schema: https://w3id.org/laura/schema/magnetic
    ifabsent: 'False'
    owner: Corrector_Magnet
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
    owner: Corrector_Magnet
    domain_of:
    - PhysicalElement
    - MagneticElement
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
    owner: Corrector_Magnet
    domain_of:
    - MagneticElement
    range: Multipoles
  systematic_multipoles:
    name: systematic_multipoles
    description: Systematic (design) multipole errors at the reference radius.
    from_schema: https://w3id.org/laura/schema/magnetic
    rank: 1000
    owner: Corrector_Magnet
    domain_of:
    - MagneticElement
    range: Multipoles
  random_multipoles:
    name: random_multipoles
    description: Random multipole errors at the reference radius.
    from_schema: https://w3id.org/laura/schema/magnetic
    rank: 1000
    owner: Corrector_Magnet
    domain_of:
    - MagneticElement
    range: Multipoles
  field_integral_coefficients:
    name: field_integral_coefficients
    description: Polynomial calibration of integrated field vs. current.
    from_schema: https://w3id.org/laura/schema/magnetic
    rank: 1000
    owner: Corrector_Magnet
    domain_of:
    - MagneticElement
    - Solenoid_Magnet
    range: FieldIntegral
  linear_saturation_coefficients:
    name: linear_saturation_coefficients
    description: Bi-linear saturation calibration.
    from_schema: https://w3id.org/laura/schema/magnetic
    rank: 1000
    owner: Corrector_Magnet
    domain_of:
    - MagneticElement
    - Solenoid_Magnet
    range: LinearSaturationFit
  settle_time:
    name: settle_time
    description: Power-supply settle time after a change [s].
    from_schema: https://w3id.org/laura/schema/magnetic
    rank: 1000
    owner: Corrector_Magnet
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
    owner: Corrector_Magnet
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
    owner: Corrector_Magnet
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
    owner: Corrector_Magnet
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
    owner: Corrector_Magnet
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
    owner: Corrector_Magnet
    domain_of:
    - MagneticElement
    range: BendingPlaneEnum
  width:
    name: width
    description: Physical width of the magnet in the bending plane [m].
    from_schema: https://w3id.org/laura/schema/magnetic
    rank: 1000
    ifabsent: float(0.2)
    owner: Corrector_Magnet
    domain_of:
    - MagneticElement
    range: float
    unit:
      ucum_code: m
  tilt:
    name: tilt
    description: Global tilt about the beam axis [rad].
    from_schema: https://w3id.org/laura/schema/magnetic
    rank: 1000
    ifabsent: float(0.0)
    owner: Corrector_Magnet
    domain_of:
    - MagneticElement
    range: float
    unit:
      ucum_code: rad
  edge_field_integral:
    name: edge_field_integral
    description: Enge fringe-field integral parameter (dimensionless).
    from_schema: https://w3id.org/laura/schema/magnetic
    ifabsent: float(0.5)
    owner: Corrector_Magnet
    domain_of:
    - MagnetSimulationElement
    - MagneticElement
    range: float
  fringe_field_coefficient:
    name: fringe_field_coefficient
    description: Coefficient controlling the fringe-field roll-off rate.
    from_schema: https://w3id.org/laura/schema/magnetic
    rank: 1000
    ifabsent: float(0.0)
    owner: Corrector_Magnet
    domain_of:
    - MagneticElement
    range: float
  gradient:
    name: gradient
    description: Peak field gradient [T/m] (quads) or peak field [T] (dipoles).
    from_schema: https://w3id.org/laura/schema/magnetic
    rank: 1000
    owner: Corrector_Magnet
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
    owner: Corrector_Magnet
    domain_of:
    - MagneticElement
    range: float
    unit:
      ucum_code: rad
class_uri: laura:Corrector_Magnet

```
</details></div>