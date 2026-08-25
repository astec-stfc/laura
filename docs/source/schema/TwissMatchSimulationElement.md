# Class: TwissMatchSimulationElement


_Simulation attributes for Twiss-matching points._



<div data-search-exclude markdown="1">



URI: [laura:TwissMatchSimulationElement](https://w3id.org/laura/TwissMatchSimulationElement)





```mermaid
 classDiagram
    class TwissMatchSimulationElement
    click TwissMatchSimulationElement href "../TwissMatchSimulationElement/"
      SimulationElement <|-- TwissMatchSimulationElement
        click SimulationElement href "../SimulationElement/"

      TwissMatchSimulationElement : alpha_x

      TwissMatchSimulationElement : alpha_y

      TwissMatchSimulationElement : beta_x

      TwissMatchSimulationElement : beta_y

      TwissMatchSimulationElement : csr_enable

      TwissMatchSimulationElement : csr_method

      TwissMatchSimulationElement : csrdz

      TwissMatchSimulationElement : deltaL

      TwissMatchSimulationElement : eta_x

      TwissMatchSimulationElement : eta_xp

      TwissMatchSimulationElement : eta_y

      TwissMatchSimulationElement : eta_yp

      TwissMatchSimulationElement : field_definition

      TwissMatchSimulationElement : field_reference_position

      TwissMatchSimulationElement : from_beam

      TwissMatchSimulationElement : horizontal_offset

      TwissMatchSimulationElement : integration_order

      TwissMatchSimulationElement : lsc_bins

      TwissMatchSimulationElement : lsc_enable

      TwissMatchSimulationElement : mat6_calc_method

      TwissMatchSimulationElement : n_kicks

      TwissMatchSimulationElement : num_steps

      TwissMatchSimulationElement : scale_field

      TwissMatchSimulationElement : smooth

      TwissMatchSimulationElement : space_charge_method

      TwissMatchSimulationElement : spin_tracking_method

      TwissMatchSimulationElement : tracking_method

      TwissMatchSimulationElement : vertical_offset

      TwissMatchSimulationElement : wakefield_definition

      TwissMatchSimulationElement : wakefield_enable


```





## Inheritance
* [SimulationElement](SimulationElement.md)
    * **TwissMatchSimulationElement**


## Class Properties

| Property | Value |
| --- | --- |
| Class URI | [laura:TwissMatchSimulationElement](https://w3id.org/laura/TwissMatchSimulationElement) |


## Slots

| Name | Cardinality and Range | Description | Inheritance |
| ---  | --- | --- | --- |
| [beta_x](beta_x.md) | 0..1 <br/> [Float](Float.md) | Horizontal beta | direct |
| [beta_y](beta_y.md) | 0..1 <br/> [Float](Float.md) | Vertical beta | direct |
| [alpha_x](alpha_x.md) | 0..1 <br/> [Float](Float.md) | Horizontal alpha | direct |
| [alpha_y](alpha_y.md) | 0..1 <br/> [Float](Float.md) | Vertical alpha | direct |
| [eta_x](eta_x.md) | 0..1 <br/> [Float](Float.md) | Horizontal dispersion | direct |
| [eta_y](eta_y.md) | 0..1 <br/> [Float](Float.md) | Vertical dispersion | direct |
| [eta_xp](eta_xp.md) | 0..1 <br/> [Float](Float.md) | Horizontal dispersion derivative | direct |
| [eta_yp](eta_yp.md) | 0..1 <br/> [Float](Float.md) | Vertical dispersion derivative | direct |
| [from_beam](from_beam.md) | 0..1 <br/> [Boolean](Boolean.md) | Compute transform from tracked beam properties | direct |
| [n_kicks](n_kicks.md) | 0..1 <br/> [Integer](Integer.md) | Number of integration kicks | [SimulationElement](SimulationElement.md) |
| [lsc_bins](lsc_bins.md) | 0..1 <br/> [Integer](Integer.md) | Number of bins used in longitudinal space-charge calculations | [SimulationElement](SimulationElement.md) |
| [csr_enable](csr_enable.md) | 0..1 <br/> [Boolean](Boolean.md) | Whether coherent synchrotron radiation effects are enabled | [SimulationElement](SimulationElement.md) |
| [lsc_enable](lsc_enable.md) | 0..1 <br/> [Boolean](Boolean.md) | Whether longitudinal space-charge effects are enabled | [SimulationElement](SimulationElement.md) |
| [tracking_method](tracking_method.md) | 0..1 <br/> [String](String.md) | Phase-space tracking algorithm requested from the target code | [SimulationElement](SimulationElement.md) |
| [mat6_calc_method](mat6_calc_method.md) | 0..1 <br/> [String](String.md) | Method used to calculate the element's 6x6 transfer matrix | [SimulationElement](SimulationElement.md) |
| [spin_tracking_method](spin_tracking_method.md) | 0..1 <br/> [String](String.md) | Spin-tracking algorithm requested from the target code | [SimulationElement](SimulationElement.md) |
| [integration_order](integration_order.md) | 0..1 <br/> [Integer](Integer.md) | Order of the target code's integration formula | [SimulationElement](SimulationElement.md) |
| [num_steps](num_steps.md) | 0..1 <br/> [Integer](Integer.md) | Number of integration steps through the element | [SimulationElement](SimulationElement.md) |
| [deltaL](deltaL.md) | 0..1 <br/> [Float](Float.md) | Longitudinal integration step size [m] | [SimulationElement](SimulationElement.md) |
| [csr_method](csr_method.md) | 0..1 <br/> [String](String.md) | Coherent-synchrotron-radiation tracking method | [SimulationElement](SimulationElement.md) |
| [space_charge_method](space_charge_method.md) | 0..1 <br/> [String](String.md) | Space-charge tracking method | [SimulationElement](SimulationElement.md) |
| [csrdz](csrdz.md) | 0..1 <br/> [Float](Float.md) | Longitudinal step size between CSR kicks [m] | [SimulationElement](SimulationElement.md) |
| [smooth](smooth.md) | 0..1 <br/> [Float](Float.md)&nbsp;or&nbsp;<br />[Integer](Integer.md) | Smoothing control for field or wake interpolation | [SimulationElement](SimulationElement.md) |
| [horizontal_offset](horizontal_offset.md) | 0..1 <br/> [Float](Float.md) | Horizontal simulation offset from the reference orbit [m] | [SimulationElement](SimulationElement.md) |
| [vertical_offset](vertical_offset.md) | 0..1 <br/> [Float](Float.md) | Vertical simulation offset from the reference orbit [m] | [SimulationElement](SimulationElement.md) |
| [field_definition](field_definition.md) | 0..1 <br/> [String](String.md) | Path to the 3-D field-map file | [SimulationElement](SimulationElement.md) |
| [wakefield_definition](wakefield_definition.md) | 0..1 <br/> [String](String.md) | Path to the wakefield impedance file | [SimulationElement](SimulationElement.md) |
| [wakefield_enable](wakefield_enable.md) | 0..1 <br/> [Boolean](Boolean.md) | Whether the wakefield named by wakefield_definition is applied | [SimulationElement](SimulationElement.md) |
| [field_reference_position](field_reference_position.md) | 0..1 <br/> [String](String.md) | Longitudinal origin of the field map [m] | [SimulationElement](SimulationElement.md) |
| [scale_field](scale_field.md) | 0..1 <br/> [Float](Float.md) | Multiplicative scale factor applied to the field map | [SimulationElement](SimulationElement.md) |





## Usages

| used by | used in | type | used |
| ---  | --- | --- | --- |
| [TwissMatch](TwissMatch.md) | [simulation](simulation.md) | range | [TwissMatchSimulationElement](TwissMatchSimulationElement.md) |












## Identifier and Mapping Information





### Schema Source


* from schema: https://w3id.org/laura/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | laura:TwissMatchSimulationElement |
| native | laura:TwissMatchSimulationElement |






## LinkML Source

<!-- TODO: investigate https://stackoverflow.com/questions/37606292/how-to-create-tabbed-code-blocks-in-mkdocs-or-sphinx -->

### Direct

<details>
```yaml
name: TwissMatchSimulationElement
description: Simulation attributes for Twiss-matching points.
from_schema: https://w3id.org/laura/schema
is_a: SimulationElement
attributes:
  beta_x:
    name: beta_x
    description: Horizontal beta.
    from_schema: https://w3id.org/laura/schema/simulation
    rank: 1000
    ifabsent: float(1.0)
    domain_of:
    - TwissMatchSimulationElement
    range: float
  beta_y:
    name: beta_y
    description: Vertical beta.
    from_schema: https://w3id.org/laura/schema/simulation
    rank: 1000
    ifabsent: float(1.0)
    domain_of:
    - TwissMatchSimulationElement
    range: float
  alpha_x:
    name: alpha_x
    description: Horizontal alpha.
    from_schema: https://w3id.org/laura/schema/simulation
    rank: 1000
    ifabsent: float(0.0)
    domain_of:
    - TwissMatchSimulationElement
    range: float
  alpha_y:
    name: alpha_y
    description: Vertical alpha.
    from_schema: https://w3id.org/laura/schema/simulation
    rank: 1000
    ifabsent: float(0.0)
    domain_of:
    - TwissMatchSimulationElement
    range: float
  eta_x:
    name: eta_x
    description: Horizontal dispersion.
    from_schema: https://w3id.org/laura/schema/simulation
    rank: 1000
    ifabsent: float(0.0)
    domain_of:
    - TwissMatchSimulationElement
    range: float
  eta_y:
    name: eta_y
    description: Vertical dispersion.
    from_schema: https://w3id.org/laura/schema/simulation
    rank: 1000
    ifabsent: float(0.0)
    domain_of:
    - TwissMatchSimulationElement
    range: float
  eta_xp:
    name: eta_xp
    description: Horizontal dispersion derivative.
    from_schema: https://w3id.org/laura/schema/simulation
    rank: 1000
    ifabsent: float(0.0)
    domain_of:
    - TwissMatchSimulationElement
    range: float
  eta_yp:
    name: eta_yp
    description: Vertical dispersion derivative.
    from_schema: https://w3id.org/laura/schema/simulation
    rank: 1000
    ifabsent: float(0.0)
    domain_of:
    - TwissMatchSimulationElement
    range: float
  from_beam:
    name: from_beam
    description: Compute transform from tracked beam properties.
    from_schema: https://w3id.org/laura/schema/simulation
    rank: 1000
    ifabsent: 'True'
    domain_of:
    - TwissMatchSimulationElement
    range: boolean
class_uri: laura:TwissMatchSimulationElement

```
</details>

### Induced

<details>
```yaml
name: TwissMatchSimulationElement
description: Simulation attributes for Twiss-matching points.
from_schema: https://w3id.org/laura/schema
is_a: SimulationElement
attributes:
  beta_x:
    name: beta_x
    description: Horizontal beta.
    from_schema: https://w3id.org/laura/schema/simulation
    rank: 1000
    ifabsent: float(1.0)
    owner: TwissMatchSimulationElement
    domain_of:
    - TwissMatchSimulationElement
    range: float
  beta_y:
    name: beta_y
    description: Vertical beta.
    from_schema: https://w3id.org/laura/schema/simulation
    rank: 1000
    ifabsent: float(1.0)
    owner: TwissMatchSimulationElement
    domain_of:
    - TwissMatchSimulationElement
    range: float
  alpha_x:
    name: alpha_x
    description: Horizontal alpha.
    from_schema: https://w3id.org/laura/schema/simulation
    rank: 1000
    ifabsent: float(0.0)
    owner: TwissMatchSimulationElement
    domain_of:
    - TwissMatchSimulationElement
    range: float
  alpha_y:
    name: alpha_y
    description: Vertical alpha.
    from_schema: https://w3id.org/laura/schema/simulation
    rank: 1000
    ifabsent: float(0.0)
    owner: TwissMatchSimulationElement
    domain_of:
    - TwissMatchSimulationElement
    range: float
  eta_x:
    name: eta_x
    description: Horizontal dispersion.
    from_schema: https://w3id.org/laura/schema/simulation
    rank: 1000
    ifabsent: float(0.0)
    owner: TwissMatchSimulationElement
    domain_of:
    - TwissMatchSimulationElement
    range: float
  eta_y:
    name: eta_y
    description: Vertical dispersion.
    from_schema: https://w3id.org/laura/schema/simulation
    rank: 1000
    ifabsent: float(0.0)
    owner: TwissMatchSimulationElement
    domain_of:
    - TwissMatchSimulationElement
    range: float
  eta_xp:
    name: eta_xp
    description: Horizontal dispersion derivative.
    from_schema: https://w3id.org/laura/schema/simulation
    rank: 1000
    ifabsent: float(0.0)
    owner: TwissMatchSimulationElement
    domain_of:
    - TwissMatchSimulationElement
    range: float
  eta_yp:
    name: eta_yp
    description: Vertical dispersion derivative.
    from_schema: https://w3id.org/laura/schema/simulation
    rank: 1000
    ifabsent: float(0.0)
    owner: TwissMatchSimulationElement
    domain_of:
    - TwissMatchSimulationElement
    range: float
  from_beam:
    name: from_beam
    description: Compute transform from tracked beam properties.
    from_schema: https://w3id.org/laura/schema/simulation
    rank: 1000
    ifabsent: 'True'
    owner: TwissMatchSimulationElement
    domain_of:
    - TwissMatchSimulationElement
    range: boolean
  n_kicks:
    name: n_kicks
    description: Number of integration kicks.
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    owner: TwissMatchSimulationElement
    domain_of:
    - SimulationElement
    range: integer
  lsc_bins:
    name: lsc_bins
    description: Number of bins used in longitudinal space-charge calculations.
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    owner: TwissMatchSimulationElement
    domain_of:
    - SimulationElement
    range: integer
  csr_enable:
    name: csr_enable
    description: Whether coherent synchrotron radiation effects are enabled.
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    ifabsent: 'true'
    owner: TwissMatchSimulationElement
    domain_of:
    - SimulationElement
    range: boolean
  lsc_enable:
    name: lsc_enable
    description: Whether longitudinal space-charge effects are enabled.
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    ifabsent: 'true'
    owner: TwissMatchSimulationElement
    domain_of:
    - SimulationElement
    range: boolean
  tracking_method:
    name: tracking_method
    description: Phase-space tracking algorithm requested from the target code.
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    owner: TwissMatchSimulationElement
    domain_of:
    - SimulationElement
    range: string
  mat6_calc_method:
    name: mat6_calc_method
    description: Method used to calculate the element's 6x6 transfer matrix.
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    owner: TwissMatchSimulationElement
    domain_of:
    - SimulationElement
    range: string
  spin_tracking_method:
    name: spin_tracking_method
    description: Spin-tracking algorithm requested from the target code.
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    owner: TwissMatchSimulationElement
    domain_of:
    - SimulationElement
    range: string
  integration_order:
    name: integration_order
    description: Order of the target code's integration formula.
    from_schema: https://w3id.org/laura/schema
    aliases:
    - integrator_order
    rank: 1000
    owner: TwissMatchSimulationElement
    domain_of:
    - SimulationElement
    range: integer
    minimum_value: 1
  num_steps:
    name: num_steps
    description: Number of integration steps through the element.
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    owner: TwissMatchSimulationElement
    domain_of:
    - SimulationElement
    range: integer
    minimum_value: 1
  deltaL:
    name: deltaL
    description: Longitudinal integration step size [m].
    from_schema: https://w3id.org/laura/schema
    aliases:
    - ds_step
    rank: 1000
    owner: TwissMatchSimulationElement
    domain_of:
    - SimulationElement
    range: float
    minimum_value: 0
    unit:
      ucum_code: m
  csr_method:
    name: csr_method
    description: Coherent-synchrotron-radiation tracking method.
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    owner: TwissMatchSimulationElement
    domain_of:
    - SimulationElement
    range: string
  space_charge_method:
    name: space_charge_method
    description: Space-charge tracking method.
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    owner: TwissMatchSimulationElement
    domain_of:
    - SimulationElement
    range: string
  csrdz:
    name: csrdz
    description: Longitudinal step size between CSR kicks [m].
    from_schema: https://w3id.org/laura/schema
    aliases:
    - csr_ds_step
    rank: 1000
    owner: TwissMatchSimulationElement
    domain_of:
    - SimulationElement
    range: float
    minimum_value: 0
    unit:
      ucum_code: m
  smooth:
    name: smooth
    description: Smoothing control for field or wake interpolation.
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    owner: TwissMatchSimulationElement
    domain_of:
    - SimulationElement
    range: float
    any_of:
    - range: integer
    - range: float
  horizontal_offset:
    name: horizontal_offset
    description: Horizontal simulation offset from the reference orbit [m].
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    ifabsent: float(0.0)
    owner: TwissMatchSimulationElement
    domain_of:
    - SimulationElement
    range: float
    unit:
      ucum_code: m
  vertical_offset:
    name: vertical_offset
    description: Vertical simulation offset from the reference orbit [m].
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    ifabsent: float(0.0)
    owner: TwissMatchSimulationElement
    domain_of:
    - SimulationElement
    range: float
    unit:
      ucum_code: m
  field_definition:
    name: field_definition
    description: Path to the 3-D field-map file.
    from_schema: https://w3id.org/laura/schema/simulation
    rank: 1000
    owner: TwissMatchSimulationElement
    domain_of:
    - SimulationElement
    range: string
  wakefield_definition:
    name: wakefield_definition
    description: Path to the wakefield impedance file.
    from_schema: https://w3id.org/laura/schema/simulation
    rank: 1000
    owner: TwissMatchSimulationElement
    domain_of:
    - SimulationElement
    range: string
  wakefield_enable:
    name: wakefield_enable
    description: Whether the wakefield named by wakefield_definition is applied. Set
      false to track the element without its wakefield while keeping the definition
      itself.
    from_schema: https://w3id.org/laura/schema/simulation
    rank: 1000
    ifabsent: 'true'
    owner: TwissMatchSimulationElement
    domain_of:
    - SimulationElement
    range: boolean
  field_reference_position:
    name: field_reference_position
    description: Longitudinal origin of the field map [m].
    from_schema: https://w3id.org/laura/schema/simulation
    rank: 1000
    owner: TwissMatchSimulationElement
    domain_of:
    - SimulationElement
    range: string
  scale_field:
    name: scale_field
    description: Multiplicative scale factor applied to the field map.
    from_schema: https://w3id.org/laura/schema/simulation
    rank: 1000
    ifabsent: float(1)
    owner: TwissMatchSimulationElement
    domain_of:
    - SimulationElement
    range: float
class_uri: laura:TwissMatchSimulationElement

```
</details></div>