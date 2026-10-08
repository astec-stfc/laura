# Class: MatrixTransformSimulationElement 


_Zero- through third-order transfer-map coefficients for a matrix transform element. Each coefficient collection accepts the dense form or the named coefficient mapping understood by the Python model._



<div data-search-exclude markdown="1">



URI: [laura:MatrixTransformSimulationElement](https://w3id.org/laura/MatrixTransformSimulationElement)





```mermaid
 classDiagram
    class MatrixTransformSimulationElement
    click MatrixTransformSimulationElement href "../MatrixTransformSimulationElement/"
      SimulationElement <|-- MatrixTransformSimulationElement
        click SimulationElement href "../SimulationElement/"
      
      MatrixTransformSimulationElement : apply
        
      MatrixTransformSimulationElement : c_matrix
        
          
    
        
        
        MatrixTransformSimulationElement --> "0..1" MatrixValue : c_matrix
        click MatrixValue href "../MatrixValue/"
    

        
      MatrixTransformSimulationElement : csr_enable
        
      MatrixTransformSimulationElement : csr_method
        
      MatrixTransformSimulationElement : csrdz
        
      MatrixTransformSimulationElement : deltaL
        
      MatrixTransformSimulationElement : field_definition
        
      MatrixTransformSimulationElement : field_reference_position
        
      MatrixTransformSimulationElement : horizontal_offset
        
      MatrixTransformSimulationElement : integration_order
        
      MatrixTransformSimulationElement : lsc_bins
        
      MatrixTransformSimulationElement : lsc_enable
        
      MatrixTransformSimulationElement : mat6_calc_method
        
      MatrixTransformSimulationElement : n_kicks
        
      MatrixTransformSimulationElement : num_steps
        
      MatrixTransformSimulationElement : r_matrix
        
          
    
        
        
        MatrixTransformSimulationElement --> "0..1" MatrixValue : r_matrix
        click MatrixValue href "../MatrixValue/"
    

        
      MatrixTransformSimulationElement : scale_field
        
      MatrixTransformSimulationElement : smooth
        
      MatrixTransformSimulationElement : space_charge_method
        
      MatrixTransformSimulationElement : spin_taylor
        
          
    
        
        
        MatrixTransformSimulationElement --> "0..1" MatrixValue : spin_taylor
        click MatrixValue href "../MatrixValue/"
    

        
      MatrixTransformSimulationElement : spin_tracking_method
        
      MatrixTransformSimulationElement : t_matrix
        
          
    
        
        
        MatrixTransformSimulationElement --> "0..1" MatrixValue : t_matrix
        click MatrixValue href "../MatrixValue/"
    

        
      MatrixTransformSimulationElement : tracking_method
        
      MatrixTransformSimulationElement : u_matrix
        
          
    
        
        
        MatrixTransformSimulationElement --> "0..1" MatrixValue : u_matrix
        click MatrixValue href "../MatrixValue/"
    

        
      MatrixTransformSimulationElement : vertical_offset
        
      MatrixTransformSimulationElement : wakefield_definition
        
      MatrixTransformSimulationElement : wakefield_enable
        
      
```





## Inheritance
* [SimulationElement](SimulationElement.md)
    * **MatrixTransformSimulationElement**


## Class Properties

| Property | Value |
| --- | --- |
| Class URI | [laura:MatrixTransformSimulationElement](https://w3id.org/laura/MatrixTransformSimulationElement) |


## Slots

| Name | Cardinality and Range | Description | Inheritance |
| ---  | --- | --- | --- |
| [apply](apply.md) | 0..1 <br/> [Boolean](Boolean.md) | Whether to apply the transfer map | direct |
| [c_matrix](c_matrix.md) | 0..1 <br/> [MatrixValue](MatrixValue.md) | C-matrix (zeroth-order transfer vector) | direct |
| [r_matrix](r_matrix.md) | 0..1 <br/> [MatrixValue](MatrixValue.md) | R-matrix (first-order transfer matrix) | direct |
| [t_matrix](t_matrix.md) | 0..1 <br/> [MatrixValue](MatrixValue.md) | T-matrix (second-order transfer tensor) | direct |
| [u_matrix](u_matrix.md) | 0..1 <br/> [MatrixValue](MatrixValue.md) | U-matrix (third-order transfer tensor) | direct |
| [spin_taylor](spin_taylor.md) | 0..1 <br/> [MatrixValue](MatrixValue.md) | Sparse quaternion Taylor terms | direct |
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
| [MatrixTransform](MatrixTransform.md) | [simulation](simulation.md) | range | [MatrixTransformSimulationElement](MatrixTransformSimulationElement.md) |












## Identifier and Mapping Information





### Schema Source


* from schema: https://w3id.org/laura/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | laura:MatrixTransformSimulationElement |
| native | laura:MatrixTransformSimulationElement |






## LinkML Source

<!-- TODO: investigate https://stackoverflow.com/questions/37606292/how-to-create-tabbed-code-blocks-in-mkdocs-or-sphinx -->

### Direct

<details>
```yaml
name: MatrixTransformSimulationElement
description: Zero- through third-order transfer-map coefficients for a matrix transform
  element. Each coefficient collection accepts the dense form or the named coefficient
  mapping understood by the Python model.
from_schema: https://w3id.org/laura/schema
is_a: SimulationElement
attributes:
  apply:
    name: apply
    description: Whether to apply the transfer map.
    from_schema: https://w3id.org/laura/schema/simulation
    rank: 1000
    ifabsent: 'False'
    domain_of:
    - MatrixTransformSimulationElement
    range: boolean
  c_matrix:
    name: c_matrix
    description: C-matrix (zeroth-order transfer vector).
    from_schema: https://w3id.org/laura/schema/simulation
    rank: 1000
    domain_of:
    - MatrixTransformSimulationElement
    range: MatrixValue
  r_matrix:
    name: r_matrix
    description: R-matrix (first-order transfer matrix).
    from_schema: https://w3id.org/laura/schema/simulation
    rank: 1000
    domain_of:
    - MatrixTransformSimulationElement
    range: MatrixValue
  t_matrix:
    name: t_matrix
    description: T-matrix (second-order transfer tensor).
    from_schema: https://w3id.org/laura/schema/simulation
    rank: 1000
    domain_of:
    - MatrixTransformSimulationElement
    range: MatrixValue
  u_matrix:
    name: u_matrix
    description: U-matrix (third-order transfer tensor).
    from_schema: https://w3id.org/laura/schema/simulation
    rank: 1000
    domain_of:
    - MatrixTransformSimulationElement
    range: MatrixValue
  spin_taylor:
    name: spin_taylor
    description: Sparse quaternion Taylor terms. Each term stores a quaternion component
      index, coefficient, and six orbital exponents.
    from_schema: https://w3id.org/laura/schema/simulation
    rank: 1000
    domain_of:
    - MatrixTransformSimulationElement
    range: MatrixValue
class_uri: laura:MatrixTransformSimulationElement

```
</details>

### Induced

<details>
```yaml
name: MatrixTransformSimulationElement
description: Zero- through third-order transfer-map coefficients for a matrix transform
  element. Each coefficient collection accepts the dense form or the named coefficient
  mapping understood by the Python model.
from_schema: https://w3id.org/laura/schema
is_a: SimulationElement
attributes:
  apply:
    name: apply
    description: Whether to apply the transfer map.
    from_schema: https://w3id.org/laura/schema/simulation
    rank: 1000
    ifabsent: 'False'
    owner: MatrixTransformSimulationElement
    domain_of:
    - MatrixTransformSimulationElement
    range: boolean
  c_matrix:
    name: c_matrix
    description: C-matrix (zeroth-order transfer vector).
    from_schema: https://w3id.org/laura/schema/simulation
    rank: 1000
    owner: MatrixTransformSimulationElement
    domain_of:
    - MatrixTransformSimulationElement
    range: MatrixValue
  r_matrix:
    name: r_matrix
    description: R-matrix (first-order transfer matrix).
    from_schema: https://w3id.org/laura/schema/simulation
    rank: 1000
    owner: MatrixTransformSimulationElement
    domain_of:
    - MatrixTransformSimulationElement
    range: MatrixValue
  t_matrix:
    name: t_matrix
    description: T-matrix (second-order transfer tensor).
    from_schema: https://w3id.org/laura/schema/simulation
    rank: 1000
    owner: MatrixTransformSimulationElement
    domain_of:
    - MatrixTransformSimulationElement
    range: MatrixValue
  u_matrix:
    name: u_matrix
    description: U-matrix (third-order transfer tensor).
    from_schema: https://w3id.org/laura/schema/simulation
    rank: 1000
    owner: MatrixTransformSimulationElement
    domain_of:
    - MatrixTransformSimulationElement
    range: MatrixValue
  spin_taylor:
    name: spin_taylor
    description: Sparse quaternion Taylor terms. Each term stores a quaternion component
      index, coefficient, and six orbital exponents.
    from_schema: https://w3id.org/laura/schema/simulation
    rank: 1000
    owner: MatrixTransformSimulationElement
    domain_of:
    - MatrixTransformSimulationElement
    range: MatrixValue
  n_kicks:
    name: n_kicks
    description: Number of integration kicks.
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    owner: MatrixTransformSimulationElement
    domain_of:
    - SimulationElement
    range: integer
  lsc_bins:
    name: lsc_bins
    description: Number of bins used in longitudinal space-charge calculations.
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    owner: MatrixTransformSimulationElement
    domain_of:
    - SimulationElement
    range: integer
  csr_enable:
    name: csr_enable
    description: Whether coherent synchrotron radiation effects are enabled.
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    ifabsent: 'true'
    owner: MatrixTransformSimulationElement
    domain_of:
    - SimulationElement
    range: boolean
  lsc_enable:
    name: lsc_enable
    description: Whether longitudinal space-charge effects are enabled.
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    ifabsent: 'true'
    owner: MatrixTransformSimulationElement
    domain_of:
    - SimulationElement
    range: boolean
  tracking_method:
    name: tracking_method
    description: Phase-space tracking algorithm requested from the target code.
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    owner: MatrixTransformSimulationElement
    domain_of:
    - SimulationElement
    range: string
  mat6_calc_method:
    name: mat6_calc_method
    description: Method used to calculate the element's 6x6 transfer matrix.
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    owner: MatrixTransformSimulationElement
    domain_of:
    - SimulationElement
    range: string
  spin_tracking_method:
    name: spin_tracking_method
    description: Spin-tracking algorithm requested from the target code.
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    owner: MatrixTransformSimulationElement
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
    owner: MatrixTransformSimulationElement
    domain_of:
    - SimulationElement
    range: integer
    minimum_value: 1
  num_steps:
    name: num_steps
    description: Number of integration steps through the element.
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    owner: MatrixTransformSimulationElement
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
    owner: MatrixTransformSimulationElement
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
    owner: MatrixTransformSimulationElement
    domain_of:
    - SimulationElement
    range: string
  space_charge_method:
    name: space_charge_method
    description: Space-charge tracking method.
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    owner: MatrixTransformSimulationElement
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
    owner: MatrixTransformSimulationElement
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
    owner: MatrixTransformSimulationElement
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
    owner: MatrixTransformSimulationElement
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
    owner: MatrixTransformSimulationElement
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
    owner: MatrixTransformSimulationElement
    domain_of:
    - SimulationElement
    range: string
  wakefield_definition:
    name: wakefield_definition
    description: Path to the wakefield impedance file.
    from_schema: https://w3id.org/laura/schema/simulation
    rank: 1000
    owner: MatrixTransformSimulationElement
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
    owner: MatrixTransformSimulationElement
    domain_of:
    - SimulationElement
    range: boolean
  field_reference_position:
    name: field_reference_position
    description: Longitudinal origin of the field map [m].
    from_schema: https://w3id.org/laura/schema/simulation
    rank: 1000
    owner: MatrixTransformSimulationElement
    domain_of:
    - SimulationElement
    range: string
  scale_field:
    name: scale_field
    description: Multiplicative scale factor applied to the field map.
    from_schema: https://w3id.org/laura/schema/simulation
    rank: 1000
    ifabsent: float(1)
    owner: MatrixTransformSimulationElement
    domain_of:
    - SimulationElement
    range: float
class_uri: laura:MatrixTransformSimulationElement

```
</details></div>