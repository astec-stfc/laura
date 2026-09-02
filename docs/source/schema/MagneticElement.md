# Class: MagneticElement 


_Magnetic field parameters for a beamline magnet, including multipole components, field integrals, and geometric edge parameters._



<div data-search-exclude markdown="1">



URI: [laura:MagneticElement](https://w3id.org/laura/MagneticElement)





```mermaid
 classDiagram
    class MagneticElement
    click MagneticElement href "../MagneticElement/"
      MagneticElement <|-- DipoleMagnet
        click DipoleMagnet href "../DipoleMagnet/"
      MagneticElement <|-- QuadrupoleMagnet
        click QuadrupoleMagnet href "../QuadrupoleMagnet/"
      MagneticElement <|-- SextupoleMagnet
        click SextupoleMagnet href "../SextupoleMagnet/"
      MagneticElement <|-- OctupoleMagnet
        click OctupoleMagnet href "../OctupoleMagnet/"
      
      MagneticElement : angle
        
      MagneticElement : bore
        
      MagneticElement : edge_field_integral
        
      MagneticElement : entrance_edge_angle
        
      MagneticElement : exit_edge_angle
        
      MagneticElement : field_integral_coefficients
        
          
    
        
        
        MagneticElement --> "0..1" FieldIntegral : field_integral_coefficients
        click FieldIntegral href "../FieldIntegral/"
    

        
      MagneticElement : fringe_field_coefficient
        
      MagneticElement : gap
        
      MagneticElement : gradient
        
      MagneticElement : length
        
      MagneticElement : linear_saturation_coefficients
        
          
    
        
        
        MagneticElement --> "0..1" LinearSaturationFit : linear_saturation_coefficients
        click LinearSaturationFit href "../LinearSaturationFit/"
    

        
      MagneticElement : multipoles
        
          
    
        
        
        MagneticElement --> "0..1" Multipoles : multipoles
        click Multipoles href "../Multipoles/"
    

        
      MagneticElement : order
        
      MagneticElement : plane
        
          
    
        
        
        MagneticElement --> "0..1" BendingPlaneEnum : plane
        click BendingPlaneEnum href "../BendingPlaneEnum/"
    

        
      MagneticElement : random_multipoles
        
          
    
        
        
        MagneticElement --> "0..1" Multipoles : random_multipoles
        click Multipoles href "../Multipoles/"
    

        
      MagneticElement : settle_time
        
      MagneticElement : skew
        
      MagneticElement : systematic_multipoles
        
          
    
        
        
        MagneticElement --> "0..1" Multipoles : systematic_multipoles
        click Multipoles href "../Multipoles/"
    

        
      MagneticElement : tilt
        
      MagneticElement : width
        
      
```





## Inheritance
* **MagneticElement**
    * [DipoleMagnet](DipoleMagnet.md)
    * [QuadrupoleMagnet](QuadrupoleMagnet.md)
    * [SextupoleMagnet](SextupoleMagnet.md)
    * [OctupoleMagnet](OctupoleMagnet.md)


## Class Properties

| Property | Value |
| --- | --- |
| Class URI | [laura:MagneticElement](https://w3id.org/laura/MagneticElement) |


## Slots

| Name | Cardinality and Range | Description | Inheritance |
| ---  | --- | --- | --- |
| [order](order.md) | 0..1 <br/> [Integer](Integer.md) | Principal multipole order (0 = dipole, 1 = quad, ?) | direct |
| [skew](skew.md) | 0..1 <br/> [Boolean](Boolean.md) | Whether the magnet is rotated 45? to produce a skew field component | direct |
| [length](length.md) | 0..1 <br/> [Float](Float.md) | Magnetic (effective) length [m] | direct |
| [multipoles](multipoles.md) | 0..1 <br/> [Multipoles](Multipoles.md) | Integrated multipole field components | direct |
| [systematic_multipoles](systematic_multipoles.md) | 0..1 <br/> [Multipoles](Multipoles.md) | Systematic (design) multipole errors at the reference radius | direct |
| [random_multipoles](random_multipoles.md) | 0..1 <br/> [Multipoles](Multipoles.md) | Random multipole errors at the reference radius | direct |
| [field_integral_coefficients](field_integral_coefficients.md) | 0..1 <br/> [FieldIntegral](FieldIntegral.md) | Polynomial calibration of integrated field vs | direct |
| [linear_saturation_coefficients](linear_saturation_coefficients.md) | 0..1 <br/> [LinearSaturationFit](LinearSaturationFit.md) | Bi-linear saturation calibration | direct |
| [settle_time](settle_time.md) | 0..1 <br/> [Float](Float.md) | Power-supply settle time after a change [s] | direct |
| [entrance_edge_angle](entrance_edge_angle.md) | 0..1 <br/> [String](String.md)&nbsp;or&nbsp;<br />[Float](Float.md) | Fringe-field entrance edge angle [rad] | direct |
| [exit_edge_angle](exit_edge_angle.md) | 0..1 <br/> [String](String.md)&nbsp;or&nbsp;<br />[Float](Float.md) | Fringe-field exit edge angle [rad] | direct |
| [gap](gap.md) | 0..1 <br/> [Float](Float.md) | Full gap between pole faces [m] | direct |
| [bore](bore.md) | 0..1 <br/> [Float](Float.md) | Magnet bore radius [m] | direct |
| [plane](plane.md) | 0..1 <br/> [BendingPlaneEnum](BendingPlaneEnum.md) | Principal bending / focusing plane (``Horizontal``, ``Vertical``, or ``Combin... | direct |
| [width](width.md) | 0..1 <br/> [Float](Float.md) | Physical width of the magnet in the bending plane [m] | direct |
| [tilt](tilt.md) | 0..1 <br/> [Float](Float.md) | Global tilt about the beam axis [rad] | direct |
| [edge_field_integral](edge_field_integral.md) | 0..1 <br/> [Float](Float.md) | Enge fringe-field integral parameter (dimensionless) | direct |
| [fringe_field_coefficient](fringe_field_coefficient.md) | 0..1 <br/> [Float](Float.md) | Coefficient controlling the fringe-field roll-off rate | direct |
| [gradient](gradient.md) | 0..1 <br/> [Float](Float.md) | Peak field gradient [T/m] (quads) or peak field [T] (dipoles) | direct |
| [angle](angle.md) | 0..1 <br/> [Float](Float.md) | Integrated bending angle [rad] | direct |





## Usages

| used by | used in | type | used |
| ---  | --- | --- | --- |
| [Magnet](Magnet.md) | [magnetic](magnetic.md) | range | [MagneticElement](MagneticElement.md) |








## In Subsets


* [MagneticProperties](MagneticProperties.md)






## Identifier and Mapping Information





### Schema Source


* from schema: https://w3id.org/laura/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | laura:MagneticElement |
| native | laura:MagneticElement |






## LinkML Source

<!-- TODO: investigate https://stackoverflow.com/questions/37606292/how-to-create-tabbed-code-blocks-in-mkdocs-or-sphinx -->

### Direct

<details>
```yaml
name: MagneticElement
description: Magnetic field parameters for a beamline magnet, including multipole
  components, field integrals, and geometric edge parameters.
in_subset:
- magnetic_properties
from_schema: https://w3id.org/laura/schema
attributes:
  order:
    name: order
    description: Principal multipole order (0 = dipole, 1 = quad, ?).
    from_schema: https://w3id.org/laura/schema/magnetic
    ifabsent: int(-1)
    domain_of:
    - Multipole
    - MagneticElement
    - Solenoid_Magnet
    range: integer
    minimum_value: -1
  skew:
    name: skew
    description: Whether the magnet is rotated 45? to produce a skew field component.
    from_schema: https://w3id.org/laura/schema/magnetic
    ifabsent: 'False'
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
    domain_of:
    - MagneticElement
    range: Multipoles
  systematic_multipoles:
    name: systematic_multipoles
    description: Systematic (design) multipole errors at the reference radius.
    from_schema: https://w3id.org/laura/schema/magnetic
    rank: 1000
    domain_of:
    - MagneticElement
    range: Multipoles
  random_multipoles:
    name: random_multipoles
    description: Random multipole errors at the reference radius.
    from_schema: https://w3id.org/laura/schema/magnetic
    rank: 1000
    domain_of:
    - MagneticElement
    range: Multipoles
  field_integral_coefficients:
    name: field_integral_coefficients
    description: Polynomial calibration of integrated field vs. current.
    from_schema: https://w3id.org/laura/schema/magnetic
    rank: 1000
    domain_of:
    - MagneticElement
    - Solenoid_Magnet
    range: FieldIntegral
  linear_saturation_coefficients:
    name: linear_saturation_coefficients
    description: Bi-linear saturation calibration.
    from_schema: https://w3id.org/laura/schema/magnetic
    rank: 1000
    domain_of:
    - MagneticElement
    - Solenoid_Magnet
    range: LinearSaturationFit
  settle_time:
    name: settle_time
    description: Power-supply settle time after a change [s].
    from_schema: https://w3id.org/laura/schema/magnetic
    rank: 1000
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
    domain_of:
    - MagneticElement
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
    domain_of:
    - MagneticElement
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
    domain_of:
    - MagneticElement
    range: BendingPlaneEnum
  width:
    name: width
    description: Physical width of the magnet in the bending plane [m].
    from_schema: https://w3id.org/laura/schema/magnetic
    rank: 1000
    ifabsent: float(0.2)
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
    domain_of:
    - MagneticElement
    range: float
  gradient:
    name: gradient
    description: Peak field gradient [T/m] (quads) or peak field [T] (dipoles).
    from_schema: https://w3id.org/laura/schema/magnetic
    rank: 1000
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
    domain_of:
    - MagneticElement
    range: float
    unit:
      ucum_code: rad
class_uri: laura:MagneticElement

```
</details>

### Induced

<details>
```yaml
name: MagneticElement
description: Magnetic field parameters for a beamline magnet, including multipole
  components, field integrals, and geometric edge parameters.
in_subset:
- magnetic_properties
from_schema: https://w3id.org/laura/schema
attributes:
  order:
    name: order
    description: Principal multipole order (0 = dipole, 1 = quad, ?).
    from_schema: https://w3id.org/laura/schema/magnetic
    ifabsent: int(-1)
    owner: MagneticElement
    domain_of:
    - Multipole
    - MagneticElement
    - Solenoid_Magnet
    range: integer
    minimum_value: -1
  skew:
    name: skew
    description: Whether the magnet is rotated 45? to produce a skew field component.
    from_schema: https://w3id.org/laura/schema/magnetic
    ifabsent: 'False'
    owner: MagneticElement
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
    owner: MagneticElement
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
    owner: MagneticElement
    domain_of:
    - MagneticElement
    range: Multipoles
  systematic_multipoles:
    name: systematic_multipoles
    description: Systematic (design) multipole errors at the reference radius.
    from_schema: https://w3id.org/laura/schema/magnetic
    rank: 1000
    owner: MagneticElement
    domain_of:
    - MagneticElement
    range: Multipoles
  random_multipoles:
    name: random_multipoles
    description: Random multipole errors at the reference radius.
    from_schema: https://w3id.org/laura/schema/magnetic
    rank: 1000
    owner: MagneticElement
    domain_of:
    - MagneticElement
    range: Multipoles
  field_integral_coefficients:
    name: field_integral_coefficients
    description: Polynomial calibration of integrated field vs. current.
    from_schema: https://w3id.org/laura/schema/magnetic
    rank: 1000
    owner: MagneticElement
    domain_of:
    - MagneticElement
    - Solenoid_Magnet
    range: FieldIntegral
  linear_saturation_coefficients:
    name: linear_saturation_coefficients
    description: Bi-linear saturation calibration.
    from_schema: https://w3id.org/laura/schema/magnetic
    rank: 1000
    owner: MagneticElement
    domain_of:
    - MagneticElement
    - Solenoid_Magnet
    range: LinearSaturationFit
  settle_time:
    name: settle_time
    description: Power-supply settle time after a change [s].
    from_schema: https://w3id.org/laura/schema/magnetic
    rank: 1000
    owner: MagneticElement
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
    owner: MagneticElement
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
    owner: MagneticElement
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
    owner: MagneticElement
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
    owner: MagneticElement
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
    owner: MagneticElement
    domain_of:
    - MagneticElement
    range: BendingPlaneEnum
  width:
    name: width
    description: Physical width of the magnet in the bending plane [m].
    from_schema: https://w3id.org/laura/schema/magnetic
    rank: 1000
    ifabsent: float(0.2)
    owner: MagneticElement
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
    owner: MagneticElement
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
    owner: MagneticElement
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
    owner: MagneticElement
    domain_of:
    - MagneticElement
    range: float
  gradient:
    name: gradient
    description: Peak field gradient [T/m] (quads) or peak field [T] (dipoles).
    from_schema: https://w3id.org/laura/schema/magnetic
    rank: 1000
    owner: MagneticElement
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
    owner: MagneticElement
    domain_of:
    - MagneticElement
    range: float
    unit:
      ucum_code: rad
class_uri: laura:MagneticElement

```
</details></div>