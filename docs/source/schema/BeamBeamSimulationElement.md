# Class: BeamBeamSimulationElement


_Simulation attributes for a weak-strong beam-beam interaction._



<div data-search-exclude markdown="1">



URI: [laura:BeamBeamSimulationElement](https://w3id.org/laura/BeamBeamSimulationElement)





```mermaid
 classDiagram
    class BeamBeamSimulationElement
    click BeamBeamSimulationElement href "../BeamBeamSimulationElement/"
      SimulationElement <|-- BeamBeamSimulationElement
        click SimulationElement href "../SimulationElement/"

      BeamBeamSimulationElement : charge

      BeamBeamSimulationElement : csr_enable

      BeamBeamSimulationElement : csr_method

      BeamBeamSimulationElement : csrdz

      BeamBeamSimulationElement : deltaL

      BeamBeamSimulationElement : field_definition

      BeamBeamSimulationElement : field_reference_position

      BeamBeamSimulationElement : horizontal_offset

      BeamBeamSimulationElement : horizontal_sigma

      BeamBeamSimulationElement : integration_order

      BeamBeamSimulationElement : lsc_bins

      BeamBeamSimulationElement : lsc_enable

      BeamBeamSimulationElement : mat6_calc_method

      BeamBeamSimulationElement : n_kicks

      BeamBeamSimulationElement : n_particles

      BeamBeamSimulationElement : num_steps

      BeamBeamSimulationElement : scale_field

      BeamBeamSimulationElement : smooth

      BeamBeamSimulationElement : space_charge_method

      BeamBeamSimulationElement : spin_tracking_method

      BeamBeamSimulationElement : tracking_method

      BeamBeamSimulationElement : vertical_offset

      BeamBeamSimulationElement : vertical_sigma

      BeamBeamSimulationElement : wakefield_definition

      BeamBeamSimulationElement : wakefield_enable

      BeamBeamSimulationElement : width


```





## Inheritance
* [SimulationElement](SimulationElement.md)
    * **BeamBeamSimulationElement**


## Class Properties

| Property | Value |
| --- | --- |
| Class URI | [laura:BeamBeamSimulationElement](https://w3id.org/laura/BeamBeamSimulationElement) |


## Slots

| Name | Cardinality and Range | Description | Inheritance |
| ---  | --- | --- | --- |
| [charge](charge.md) | 0..1 <br/> [Float](Float.md) | Opposing-beam particle charge in units of the elementary charge | direct |
| [n_particles](n_particles.md) | 0..1 <br/> [Float](Float.md) | Number of particles in the opposing bunch | direct |
| [horizontal_sigma](horizontal_sigma.md) | 0..1 <br/> [Float](Float.md) | Horizontal RMS size of the opposing bunch [m] | direct |
| [vertical_sigma](vertical_sigma.md) | 0..1 <br/> [Float](Float.md) | Vertical RMS size of the opposing bunch [m] | direct |
| [width](width.md) | 0..1 <br/> [Float](Float.md) | Opposing-bunch length for the 3-D weak-strong model [m] | direct |
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
| [BeamBeam](BeamBeam.md) | [simulation](simulation.md) | range | [BeamBeamSimulationElement](BeamBeamSimulationElement.md) |












## Identifier and Mapping Information





### Schema Source


* from schema: https://w3id.org/laura/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | laura:BeamBeamSimulationElement |
| native | laura:BeamBeamSimulationElement |






## LinkML Source

<!-- TODO: investigate https://stackoverflow.com/questions/37606292/how-to-create-tabbed-code-blocks-in-mkdocs-or-sphinx -->

### Direct

<details>
```yaml
name: BeamBeamSimulationElement
description: Simulation attributes for a weak-strong beam-beam interaction.
from_schema: https://w3id.org/laura/schema
is_a: SimulationElement
attributes:
  charge:
    name: charge
    description: Opposing-beam particle charge in units of the elementary charge.
    from_schema: https://w3id.org/laura/schema/simulation
    rank: 1000
    ifabsent: float(1.0)
    domain_of:
    - BeamBeamSimulationElement
    range: float
  n_particles:
    name: n_particles
    description: Number of particles in the opposing bunch.
    from_schema: https://w3id.org/laura/schema/simulation
    rank: 1000
    ifabsent: float(0.0)
    domain_of:
    - BeamBeamSimulationElement
    range: float
  horizontal_sigma:
    name: horizontal_sigma
    description: Horizontal RMS size of the opposing bunch [m].
    from_schema: https://w3id.org/laura/schema/simulation
    rank: 1000
    ifabsent: float(0.0)
    domain_of:
    - BeamBeamSimulationElement
    range: float
    unit:
      ucum_code: m
  vertical_sigma:
    name: vertical_sigma
    description: Vertical RMS size of the opposing bunch [m].
    from_schema: https://w3id.org/laura/schema/simulation
    rank: 1000
    ifabsent: float(0.0)
    domain_of:
    - BeamBeamSimulationElement
    range: float
    unit:
      ucum_code: m
  width:
    name: width
    description: Opposing-bunch length for the 3-D weak-strong model [m].
    from_schema: https://w3id.org/laura/schema/simulation
    rank: 1000
    ifabsent: float(0.0)
    domain_of:
    - BeamBeamSimulationElement
    - MagneticElement
    range: float
    unit:
      ucum_code: m
class_uri: laura:BeamBeamSimulationElement

```
</details>

### Induced

<details>
```yaml
name: BeamBeamSimulationElement
description: Simulation attributes for a weak-strong beam-beam interaction.
from_schema: https://w3id.org/laura/schema
is_a: SimulationElement
attributes:
  charge:
    name: charge
    description: Opposing-beam particle charge in units of the elementary charge.
    from_schema: https://w3id.org/laura/schema/simulation
    rank: 1000
    ifabsent: float(1.0)
    owner: BeamBeamSimulationElement
    domain_of:
    - BeamBeamSimulationElement
    range: float
  n_particles:
    name: n_particles
    description: Number of particles in the opposing bunch.
    from_schema: https://w3id.org/laura/schema/simulation
    rank: 1000
    ifabsent: float(0.0)
    owner: BeamBeamSimulationElement
    domain_of:
    - BeamBeamSimulationElement
    range: float
  horizontal_sigma:
    name: horizontal_sigma
    description: Horizontal RMS size of the opposing bunch [m].
    from_schema: https://w3id.org/laura/schema/simulation
    rank: 1000
    ifabsent: float(0.0)
    owner: BeamBeamSimulationElement
    domain_of:
    - BeamBeamSimulationElement
    range: float
    unit:
      ucum_code: m
  vertical_sigma:
    name: vertical_sigma
    description: Vertical RMS size of the opposing bunch [m].
    from_schema: https://w3id.org/laura/schema/simulation
    rank: 1000
    ifabsent: float(0.0)
    owner: BeamBeamSimulationElement
    domain_of:
    - BeamBeamSimulationElement
    range: float
    unit:
      ucum_code: m
  width:
    name: width
    description: Opposing-bunch length for the 3-D weak-strong model [m].
    from_schema: https://w3id.org/laura/schema/simulation
    rank: 1000
    ifabsent: float(0.0)
    owner: BeamBeamSimulationElement
    domain_of:
    - BeamBeamSimulationElement
    - MagneticElement
    range: float
    unit:
      ucum_code: m
  n_kicks:
    name: n_kicks
    description: Number of integration kicks.
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    owner: BeamBeamSimulationElement
    domain_of:
    - SimulationElement
    range: integer
  lsc_bins:
    name: lsc_bins
    description: Number of bins used in longitudinal space-charge calculations.
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    owner: BeamBeamSimulationElement
    domain_of:
    - SimulationElement
    range: integer
  csr_enable:
    name: csr_enable
    description: Whether coherent synchrotron radiation effects are enabled.
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    ifabsent: 'true'
    owner: BeamBeamSimulationElement
    domain_of:
    - SimulationElement
    range: boolean
  lsc_enable:
    name: lsc_enable
    description: Whether longitudinal space-charge effects are enabled.
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    ifabsent: 'true'
    owner: BeamBeamSimulationElement
    domain_of:
    - SimulationElement
    range: boolean
  tracking_method:
    name: tracking_method
    description: Phase-space tracking algorithm requested from the target code.
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    owner: BeamBeamSimulationElement
    domain_of:
    - SimulationElement
    range: string
  mat6_calc_method:
    name: mat6_calc_method
    description: Method used to calculate the element's 6x6 transfer matrix.
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    owner: BeamBeamSimulationElement
    domain_of:
    - SimulationElement
    range: string
  spin_tracking_method:
    name: spin_tracking_method
    description: Spin-tracking algorithm requested from the target code.
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    owner: BeamBeamSimulationElement
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
    owner: BeamBeamSimulationElement
    domain_of:
    - SimulationElement
    range: integer
    minimum_value: 1
  num_steps:
    name: num_steps
    description: Number of integration steps through the element.
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    owner: BeamBeamSimulationElement
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
    owner: BeamBeamSimulationElement
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
    owner: BeamBeamSimulationElement
    domain_of:
    - SimulationElement
    range: string
  space_charge_method:
    name: space_charge_method
    description: Space-charge tracking method.
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    owner: BeamBeamSimulationElement
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
    owner: BeamBeamSimulationElement
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
    owner: BeamBeamSimulationElement
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
    owner: BeamBeamSimulationElement
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
    owner: BeamBeamSimulationElement
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
    owner: BeamBeamSimulationElement
    domain_of:
    - SimulationElement
    range: string
  wakefield_definition:
    name: wakefield_definition
    description: Path to the wakefield impedance file.
    from_schema: https://w3id.org/laura/schema/simulation
    rank: 1000
    owner: BeamBeamSimulationElement
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
    owner: BeamBeamSimulationElement
    domain_of:
    - SimulationElement
    range: boolean
  field_reference_position:
    name: field_reference_position
    description: Longitudinal origin of the field map [m].
    from_schema: https://w3id.org/laura/schema/simulation
    rank: 1000
    owner: BeamBeamSimulationElement
    domain_of:
    - SimulationElement
    range: string
  scale_field:
    name: scale_field
    description: Multiplicative scale factor applied to the field map.
    from_schema: https://w3id.org/laura/schema/simulation
    rank: 1000
    ifabsent: float(1)
    owner: BeamBeamSimulationElement
    domain_of:
    - SimulationElement
    range: float
class_uri: laura:BeamBeamSimulationElement

```
</details></div>