# Class: DriftSimulationElement 


_Simulation attributes for field-free drift sections._



<div data-search-exclude markdown="1">



URI: [laura:DriftSimulationElement](https://w3id.org/laura/DriftSimulationElement)





```mermaid
 classDiagram
    class DriftSimulationElement
    click DriftSimulationElement href "../DriftSimulationElement/"
      SimulationElement <|-- DriftSimulationElement
        click SimulationElement href "../SimulationElement/"
      
      DriftSimulationElement : csr_enable
        
      DriftSimulationElement : csr_method
        
      DriftSimulationElement : csrdz
        
      DriftSimulationElement : deltaL
        
      DriftSimulationElement : field_definition
        
      DriftSimulationElement : field_reference_position
        
      DriftSimulationElement : horizontal_offset
        
      DriftSimulationElement : integration_order
        
      DriftSimulationElement : lsc_bins
        
      DriftSimulationElement : lsc_enable
        
      DriftSimulationElement : lsc_high_frequency_cutoff_end
        
      DriftSimulationElement : lsc_high_frequency_cutoff_start
        
      DriftSimulationElement : lsc_interpolate
        
      DriftSimulationElement : lsc_low_frequency_cutoff_end
        
      DriftSimulationElement : lsc_low_frequency_cutoff_start
        
      DriftSimulationElement : mat6_calc_method
        
      DriftSimulationElement : n_kicks
        
      DriftSimulationElement : num_steps
        
      DriftSimulationElement : scale_field
        
      DriftSimulationElement : smooth
        
      DriftSimulationElement : space_charge_method
        
      DriftSimulationElement : spin_tracking_method
        
      DriftSimulationElement : tracking_method
        
      DriftSimulationElement : use_stupakov
        
      DriftSimulationElement : vertical_offset
        
      DriftSimulationElement : wakefield_definition
        
      DriftSimulationElement : wakefield_enable
        
      
```





## Inheritance
* [SimulationElement](SimulationElement.md)
    * **DriftSimulationElement**


## Class Properties

| Property | Value |
| --- | --- |
| Class URI | [laura:DriftSimulationElement](https://w3id.org/laura/DriftSimulationElement) |


## Slots

| Name | Cardinality and Range | Description | Inheritance |
| ---  | --- | --- | --- |
| [lsc_interpolate](lsc_interpolate.md) | 0..1 <br/> [Integer](Integer.md) | Flag to allow interpolation of computed LSC wake | direct |
| [use_stupakov](use_stupakov.md) | 0..1 <br/> [Integer](Integer.md) | Use Stupakov formula | direct |
| [lsc_high_frequency_cutoff_start](lsc_high_frequency_cutoff_start.md) | 0..1 <br/> [Float](Float.md) | High-frequency cutoff start for LSC | direct |
| [lsc_high_frequency_cutoff_end](lsc_high_frequency_cutoff_end.md) | 0..1 <br/> [Float](Float.md) | High-frequency cutoff end for LSC | direct |
| [lsc_low_frequency_cutoff_start](lsc_low_frequency_cutoff_start.md) | 0..1 <br/> [Float](Float.md) | Low-frequency cutoff start for LSC | direct |
| [lsc_low_frequency_cutoff_end](lsc_low_frequency_cutoff_end.md) | 0..1 <br/> [Float](Float.md) | Low-frequency cutoff end for LSC | direct |
| [n_kicks](n_kicks.md) | 0..1 <br/> [Integer](Integer.md) | Number of integration kicks | [SimulationElement](SimulationElement.md) |
| [lsc_bins](lsc_bins.md) | 0..1 <br/> [Integer](Integer.md) | Number of bins for LSC calculations | [SimulationElement](SimulationElement.md) |
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
| [csrdz](csrdz.md) | 0..1 <br/> [Float](Float.md) | Step size for CSR calculations | [SimulationElement](SimulationElement.md) |
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
| [Drift](Drift.md) | [simulation](simulation.md) | range | [DriftSimulationElement](DriftSimulationElement.md) |












## Identifier and Mapping Information





### Schema Source


* from schema: https://w3id.org/laura/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | laura:DriftSimulationElement |
| native | laura:DriftSimulationElement |






## LinkML Source

<!-- TODO: investigate https://stackoverflow.com/questions/37606292/how-to-create-tabbed-code-blocks-in-mkdocs-or-sphinx -->

### Direct

<details>
```yaml
name: DriftSimulationElement
description: Simulation attributes for field-free drift sections.
from_schema: https://w3id.org/laura/schema
is_a: SimulationElement
slot_usage:
  lsc_bins:
    name: lsc_bins
    description: Number of bins for LSC calculations.
    ifabsent: int(20)
  csrdz:
    name: csrdz
    description: Step size for CSR calculations.
    ifabsent: float(0.01)
attributes:
  lsc_interpolate:
    name: lsc_interpolate
    description: Flag to allow interpolation of computed LSC wake.
    from_schema: https://w3id.org/laura/schema/simulation
    rank: 1000
    ifabsent: int(1)
    domain_of:
    - DriftSimulationElement
    range: integer
  use_stupakov:
    name: use_stupakov
    description: Use Stupakov formula.
    from_schema: https://w3id.org/laura/schema/simulation
    rank: 1000
    ifabsent: int(1)
    domain_of:
    - DriftSimulationElement
    range: integer
  lsc_high_frequency_cutoff_start:
    name: lsc_high_frequency_cutoff_start
    description: High-frequency cutoff start for LSC.
    from_schema: https://w3id.org/laura/schema/simulation
    rank: 1000
    domain_of:
    - DriftSimulationElement
    range: float
  lsc_high_frequency_cutoff_end:
    name: lsc_high_frequency_cutoff_end
    description: High-frequency cutoff end for LSC.
    from_schema: https://w3id.org/laura/schema/simulation
    rank: 1000
    domain_of:
    - DriftSimulationElement
    range: float
  lsc_low_frequency_cutoff_start:
    name: lsc_low_frequency_cutoff_start
    description: Low-frequency cutoff start for LSC.
    from_schema: https://w3id.org/laura/schema/simulation
    rank: 1000
    domain_of:
    - DriftSimulationElement
    range: float
  lsc_low_frequency_cutoff_end:
    name: lsc_low_frequency_cutoff_end
    description: Low-frequency cutoff end for LSC.
    from_schema: https://w3id.org/laura/schema/simulation
    rank: 1000
    domain_of:
    - DriftSimulationElement
    range: float
class_uri: laura:DriftSimulationElement

```
</details>

### Induced

<details>
```yaml
name: DriftSimulationElement
description: Simulation attributes for field-free drift sections.
from_schema: https://w3id.org/laura/schema
is_a: SimulationElement
slot_usage:
  lsc_bins:
    name: lsc_bins
    description: Number of bins for LSC calculations.
    ifabsent: int(20)
  csrdz:
    name: csrdz
    description: Step size for CSR calculations.
    ifabsent: float(0.01)
attributes:
  lsc_interpolate:
    name: lsc_interpolate
    description: Flag to allow interpolation of computed LSC wake.
    from_schema: https://w3id.org/laura/schema/simulation
    rank: 1000
    ifabsent: int(1)
    owner: DriftSimulationElement
    domain_of:
    - DriftSimulationElement
    range: integer
  use_stupakov:
    name: use_stupakov
    description: Use Stupakov formula.
    from_schema: https://w3id.org/laura/schema/simulation
    rank: 1000
    ifabsent: int(1)
    owner: DriftSimulationElement
    domain_of:
    - DriftSimulationElement
    range: integer
  lsc_high_frequency_cutoff_start:
    name: lsc_high_frequency_cutoff_start
    description: High-frequency cutoff start for LSC.
    from_schema: https://w3id.org/laura/schema/simulation
    rank: 1000
    owner: DriftSimulationElement
    domain_of:
    - DriftSimulationElement
    range: float
  lsc_high_frequency_cutoff_end:
    name: lsc_high_frequency_cutoff_end
    description: High-frequency cutoff end for LSC.
    from_schema: https://w3id.org/laura/schema/simulation
    rank: 1000
    owner: DriftSimulationElement
    domain_of:
    - DriftSimulationElement
    range: float
  lsc_low_frequency_cutoff_start:
    name: lsc_low_frequency_cutoff_start
    description: Low-frequency cutoff start for LSC.
    from_schema: https://w3id.org/laura/schema/simulation
    rank: 1000
    owner: DriftSimulationElement
    domain_of:
    - DriftSimulationElement
    range: float
  lsc_low_frequency_cutoff_end:
    name: lsc_low_frequency_cutoff_end
    description: Low-frequency cutoff end for LSC.
    from_schema: https://w3id.org/laura/schema/simulation
    rank: 1000
    owner: DriftSimulationElement
    domain_of:
    - DriftSimulationElement
    range: float
  n_kicks:
    name: n_kicks
    description: Number of integration kicks.
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    owner: DriftSimulationElement
    domain_of:
    - SimulationElement
    range: integer
  lsc_bins:
    name: lsc_bins
    description: Number of bins for LSC calculations.
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    ifabsent: int(20)
    owner: DriftSimulationElement
    domain_of:
    - SimulationElement
    range: integer
  csr_enable:
    name: csr_enable
    description: Whether coherent synchrotron radiation effects are enabled.
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    ifabsent: 'true'
    owner: DriftSimulationElement
    domain_of:
    - SimulationElement
    range: boolean
  lsc_enable:
    name: lsc_enable
    description: Whether longitudinal space-charge effects are enabled.
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    ifabsent: 'true'
    owner: DriftSimulationElement
    domain_of:
    - SimulationElement
    range: boolean
  tracking_method:
    name: tracking_method
    description: Phase-space tracking algorithm requested from the target code.
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    owner: DriftSimulationElement
    domain_of:
    - SimulationElement
    range: string
  mat6_calc_method:
    name: mat6_calc_method
    description: Method used to calculate the element's 6x6 transfer matrix.
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    owner: DriftSimulationElement
    domain_of:
    - SimulationElement
    range: string
  spin_tracking_method:
    name: spin_tracking_method
    description: Spin-tracking algorithm requested from the target code.
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    owner: DriftSimulationElement
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
    owner: DriftSimulationElement
    domain_of:
    - SimulationElement
    range: integer
    minimum_value: 1
  num_steps:
    name: num_steps
    description: Number of integration steps through the element.
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    owner: DriftSimulationElement
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
    owner: DriftSimulationElement
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
    owner: DriftSimulationElement
    domain_of:
    - SimulationElement
    range: string
  space_charge_method:
    name: space_charge_method
    description: Space-charge tracking method.
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    owner: DriftSimulationElement
    domain_of:
    - SimulationElement
    range: string
  csrdz:
    name: csrdz
    description: Step size for CSR calculations.
    from_schema: https://w3id.org/laura/schema
    aliases:
    - csr_ds_step
    rank: 1000
    ifabsent: float(0.01)
    owner: DriftSimulationElement
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
    owner: DriftSimulationElement
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
    owner: DriftSimulationElement
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
    owner: DriftSimulationElement
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
    owner: DriftSimulationElement
    domain_of:
    - SimulationElement
    range: string
  wakefield_definition:
    name: wakefield_definition
    description: Path to the wakefield impedance file.
    from_schema: https://w3id.org/laura/schema/simulation
    rank: 1000
    owner: DriftSimulationElement
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
    owner: DriftSimulationElement
    domain_of:
    - SimulationElement
    range: boolean
  field_reference_position:
    name: field_reference_position
    description: Longitudinal origin of the field map [m].
    from_schema: https://w3id.org/laura/schema/simulation
    rank: 1000
    owner: DriftSimulationElement
    domain_of:
    - SimulationElement
    range: string
  scale_field:
    name: scale_field
    description: Multiplicative scale factor applied to the field map.
    from_schema: https://w3id.org/laura/schema/simulation
    rank: 1000
    ifabsent: float(1)
    owner: DriftSimulationElement
    domain_of:
    - SimulationElement
    range: float
class_uri: laura:DriftSimulationElement

```
</details></div>