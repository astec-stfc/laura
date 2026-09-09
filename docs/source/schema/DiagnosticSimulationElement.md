# Class: DiagnosticSimulationElement 


_Simulation attributes for beam-diagnostic elements._



<div data-search-exclude markdown="1">



URI: [laura:DiagnosticSimulationElement](https://w3id.org/laura/DiagnosticSimulationElement)





```mermaid
 classDiagram
    class DiagnosticSimulationElement
    click DiagnosticSimulationElement href "../DiagnosticSimulationElement/"
      SimulationElement <|-- DiagnosticSimulationElement
        click SimulationElement href "../SimulationElement/"
      
      DiagnosticSimulationElement : csr_enable
        
      DiagnosticSimulationElement : csr_method
        
      DiagnosticSimulationElement : csrdz
        
      DiagnosticSimulationElement : deltaL
        
      DiagnosticSimulationElement : field_definition
        
      DiagnosticSimulationElement : field_reference_position
        
      DiagnosticSimulationElement : horizontal_offset
        
      DiagnosticSimulationElement : integration_order
        
      DiagnosticSimulationElement : lsc_bins
        
      DiagnosticSimulationElement : lsc_enable
        
      DiagnosticSimulationElement : mat6_calc_method
        
      DiagnosticSimulationElement : n_kicks
        
      DiagnosticSimulationElement : num_steps
        
      DiagnosticSimulationElement : output_filename
        
      DiagnosticSimulationElement : scale_field
        
      DiagnosticSimulationElement : smooth
        
      DiagnosticSimulationElement : space_charge_method
        
      DiagnosticSimulationElement : spin_tracking_method
        
      DiagnosticSimulationElement : tracking_method
        
      DiagnosticSimulationElement : vertical_offset
        
      DiagnosticSimulationElement : wakefield_definition
        
      DiagnosticSimulationElement : wakefield_enable
        
      
```





## Inheritance
* [SimulationElement](SimulationElement.md)
    * **DiagnosticSimulationElement**


## Class Properties

| Property | Value |
| --- | --- |
| Class URI | [laura:DiagnosticSimulationElement](https://w3id.org/laura/DiagnosticSimulationElement) |


## Slots

| Name | Cardinality and Range | Description | Inheritance |
| ---  | --- | --- | --- |
| [output_filename](output_filename.md) | 0..1 <br/> [String](String.md) | Output filename for diagnostic data | direct |
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
| [Diagnostic](Diagnostic.md) | [simulation](simulation.md) | range | [DiagnosticSimulationElement](DiagnosticSimulationElement.md) |
| [BeamPositionMonitor](BeamPositionMonitor.md) | [simulation](simulation.md) | range | [DiagnosticSimulationElement](DiagnosticSimulationElement.md) |
| [BeamArrivalMonitor](BeamArrivalMonitor.md) | [simulation](simulation.md) | range | [DiagnosticSimulationElement](DiagnosticSimulationElement.md) |
| [BunchLengthMonitor](BunchLengthMonitor.md) | [simulation](simulation.md) | range | [DiagnosticSimulationElement](DiagnosticSimulationElement.md) |
| [Camera](Camera.md) | [simulation](simulation.md) | range | [DiagnosticSimulationElement](DiagnosticSimulationElement.md) |
| [Screen](Screen.md) | [simulation](simulation.md) | range | [DiagnosticSimulationElement](DiagnosticSimulationElement.md) |
| [ChargeDiagnostic](ChargeDiagnostic.md) | [simulation](simulation.md) | range | [DiagnosticSimulationElement](DiagnosticSimulationElement.md) |
| [WallCurrentMonitor](WallCurrentMonitor.md) | [simulation](simulation.md) | range | [DiagnosticSimulationElement](DiagnosticSimulationElement.md) |
| [FaradayCupMonitor](FaradayCupMonitor.md) | [simulation](simulation.md) | range | [DiagnosticSimulationElement](DiagnosticSimulationElement.md) |
| [IntegratedCurrentTransformer](IntegratedCurrentTransformer.md) | [simulation](simulation.md) | range | [DiagnosticSimulationElement](DiagnosticSimulationElement.md) |
| [PhotonMonitor](PhotonMonitor.md) | [simulation](simulation.md) | range | [DiagnosticSimulationElement](DiagnosticSimulationElement.md) |












## Identifier and Mapping Information





### Schema Source


* from schema: https://w3id.org/laura/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | laura:DiagnosticSimulationElement |
| native | laura:DiagnosticSimulationElement |






## LinkML Source

<!-- TODO: investigate https://stackoverflow.com/questions/37606292/how-to-create-tabbed-code-blocks-in-mkdocs-or-sphinx -->

### Direct

<details>
```yaml
name: DiagnosticSimulationElement
description: Simulation attributes for beam-diagnostic elements.
from_schema: https://w3id.org/laura/schema
is_a: SimulationElement
attributes:
  output_filename:
    name: output_filename
    description: Output filename for diagnostic data.
    from_schema: https://w3id.org/laura/schema/simulation
    rank: 1000
    domain_of:
    - DiagnosticSimulationElement
    range: string
class_uri: laura:DiagnosticSimulationElement

```
</details>

### Induced

<details>
```yaml
name: DiagnosticSimulationElement
description: Simulation attributes for beam-diagnostic elements.
from_schema: https://w3id.org/laura/schema
is_a: SimulationElement
attributes:
  output_filename:
    name: output_filename
    description: Output filename for diagnostic data.
    from_schema: https://w3id.org/laura/schema/simulation
    rank: 1000
    owner: DiagnosticSimulationElement
    domain_of:
    - DiagnosticSimulationElement
    range: string
  n_kicks:
    name: n_kicks
    description: Number of integration kicks.
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    owner: DiagnosticSimulationElement
    domain_of:
    - SimulationElement
    range: integer
  lsc_bins:
    name: lsc_bins
    description: Number of bins used in longitudinal space-charge calculations.
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    owner: DiagnosticSimulationElement
    domain_of:
    - SimulationElement
    range: integer
  csr_enable:
    name: csr_enable
    description: Whether coherent synchrotron radiation effects are enabled.
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    ifabsent: 'true'
    owner: DiagnosticSimulationElement
    domain_of:
    - SimulationElement
    range: boolean
  lsc_enable:
    name: lsc_enable
    description: Whether longitudinal space-charge effects are enabled.
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    ifabsent: 'true'
    owner: DiagnosticSimulationElement
    domain_of:
    - SimulationElement
    range: boolean
  tracking_method:
    name: tracking_method
    description: Phase-space tracking algorithm requested from the target code.
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    owner: DiagnosticSimulationElement
    domain_of:
    - SimulationElement
    range: string
  mat6_calc_method:
    name: mat6_calc_method
    description: Method used to calculate the element's 6x6 transfer matrix.
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    owner: DiagnosticSimulationElement
    domain_of:
    - SimulationElement
    range: string
  spin_tracking_method:
    name: spin_tracking_method
    description: Spin-tracking algorithm requested from the target code.
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    owner: DiagnosticSimulationElement
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
    owner: DiagnosticSimulationElement
    domain_of:
    - SimulationElement
    range: integer
    minimum_value: 1
  num_steps:
    name: num_steps
    description: Number of integration steps through the element.
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    owner: DiagnosticSimulationElement
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
    owner: DiagnosticSimulationElement
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
    owner: DiagnosticSimulationElement
    domain_of:
    - SimulationElement
    range: string
  space_charge_method:
    name: space_charge_method
    description: Space-charge tracking method.
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    owner: DiagnosticSimulationElement
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
    owner: DiagnosticSimulationElement
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
    owner: DiagnosticSimulationElement
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
    owner: DiagnosticSimulationElement
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
    owner: DiagnosticSimulationElement
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
    owner: DiagnosticSimulationElement
    domain_of:
    - SimulationElement
    range: string
  wakefield_definition:
    name: wakefield_definition
    description: Path to the wakefield impedance file.
    from_schema: https://w3id.org/laura/schema/simulation
    rank: 1000
    owner: DiagnosticSimulationElement
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
    owner: DiagnosticSimulationElement
    domain_of:
    - SimulationElement
    range: boolean
  field_reference_position:
    name: field_reference_position
    description: Longitudinal origin of the field map [m].
    from_schema: https://w3id.org/laura/schema/simulation
    rank: 1000
    owner: DiagnosticSimulationElement
    domain_of:
    - SimulationElement
    range: string
  scale_field:
    name: scale_field
    description: Multiplicative scale factor applied to the field map.
    from_schema: https://w3id.org/laura/schema/simulation
    rank: 1000
    ifabsent: float(1)
    owner: DiagnosticSimulationElement
    domain_of:
    - SimulationElement
    range: float
class_uri: laura:DiagnosticSimulationElement

```
</details></div>