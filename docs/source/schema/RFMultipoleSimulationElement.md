# Class: RFMultipoleSimulationElement 


_Simulation attributes for a thin RF multipole kick._



<div data-search-exclude markdown="1">



URI: [laura:RFMultipoleSimulationElement](https://w3id.org/laura/RFMultipoleSimulationElement)





```mermaid
 classDiagram
    class RFMultipoleSimulationElement
    click RFMultipoleSimulationElement href "../RFMultipoleSimulationElement/"
      SimulationElement <|-- RFMultipoleSimulationElement
        click SimulationElement href "../SimulationElement/"
      
      RFMultipoleSimulationElement : csr_enable
        
      RFMultipoleSimulationElement : csr_method
        
      RFMultipoleSimulationElement : csrdz
        
      RFMultipoleSimulationElement : deltaL
        
      RFMultipoleSimulationElement : field_amplitude
        
      RFMultipoleSimulationElement : field_definition
        
      RFMultipoleSimulationElement : field_reference_position
        
      RFMultipoleSimulationElement : frequency
        
      RFMultipoleSimulationElement : horizontal_offset
        
      RFMultipoleSimulationElement : integration_order
        
      RFMultipoleSimulationElement : knl
        
      RFMultipoleSimulationElement : ksl
        
      RFMultipoleSimulationElement : lsc_bins
        
      RFMultipoleSimulationElement : lsc_enable
        
      RFMultipoleSimulationElement : mat6_calc_method
        
      RFMultipoleSimulationElement : n_kicks
        
      RFMultipoleSimulationElement : num_steps
        
      RFMultipoleSimulationElement : phase
        
      RFMultipoleSimulationElement : pnl
        
      RFMultipoleSimulationElement : psl
        
      RFMultipoleSimulationElement : scale_field
        
      RFMultipoleSimulationElement : smooth
        
      RFMultipoleSimulationElement : space_charge_method
        
      RFMultipoleSimulationElement : spin_tracking_method
        
      RFMultipoleSimulationElement : tracking_method
        
      RFMultipoleSimulationElement : vertical_offset
        
      RFMultipoleSimulationElement : wakefield_definition
        
      RFMultipoleSimulationElement : wakefield_enable
        
      
```





## Inheritance
* [SimulationElement](SimulationElement.md)
    * **RFMultipoleSimulationElement**


## Class Properties

| Property | Value |
| --- | --- |
| Class URI | [laura:RFMultipoleSimulationElement](https://w3id.org/laura/RFMultipoleSimulationElement) |


## Slots

| Name | Cardinality and Range | Description | Inheritance |
| ---  | --- | --- | --- |
| [frequency](frequency.md) | 0..1 <br/> [Float](Float.md) | RF frequency [Hz] | direct |
| [phase](phase.md) | 0..1 <br/> [Float](Float.md)&nbsp;or&nbsp;<br />[String](String.md) | Overall phase lag [deg] | direct |
| [field_amplitude](field_amplitude.md) | 0..1 <br/> [Float](Float.md)&nbsp;or&nbsp;<br />[String](String.md) | Longitudinal voltage [V] | direct |
| [knl](knl.md) | * <br/> [Float](Float.md) | Integrated normal multipole strengths, dipole through decapole | direct |
| [ksl](ksl.md) | * <br/> [Float](Float.md) | Integrated skew multipole strengths, dipole through decapole | direct |
| [pnl](pnl.md) | * <br/> [Float](Float.md) | Normal multipole phases [deg], dipole through decapole | direct |
| [psl](psl.md) | * <br/> [Float](Float.md) | Skew multipole phases [deg], dipole through decapole | direct |
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
| [RFMultipole](RFMultipole.md) | [simulation](simulation.md) | range | [RFMultipoleSimulationElement](RFMultipoleSimulationElement.md) |












## Identifier and Mapping Information





### Schema Source


* from schema: https://w3id.org/laura/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | laura:RFMultipoleSimulationElement |
| native | laura:RFMultipoleSimulationElement |






## LinkML Source

<!-- TODO: investigate https://stackoverflow.com/questions/37606292/how-to-create-tabbed-code-blocks-in-mkdocs-or-sphinx -->

### Direct

<details>
```yaml
name: RFMultipoleSimulationElement
description: Simulation attributes for a thin RF multipole kick.
from_schema: https://w3id.org/laura/schema
is_a: SimulationElement
slots:
- frequency
- phase
- field_amplitude
slot_usage:
  frequency:
    name: frequency
    description: RF frequency [Hz].
    ifabsent: float(0.0)
  phase:
    name: phase
    description: Overall phase lag [deg].
    ifabsent: float(0.0)
  field_amplitude:
    name: field_amplitude
    description: Longitudinal voltage [V].
    ifabsent: float(0.0)
attributes:
  knl:
    name: knl
    description: Integrated normal multipole strengths, dipole through decapole.
    from_schema: https://w3id.org/laura/schema/simulation
    rank: 1000
    domain_of:
    - RFMultipoleSimulationElement
    range: float
    multivalued: true
  ksl:
    name: ksl
    description: Integrated skew multipole strengths, dipole through decapole.
    from_schema: https://w3id.org/laura/schema/simulation
    rank: 1000
    domain_of:
    - RFMultipoleSimulationElement
    range: float
    multivalued: true
  pnl:
    name: pnl
    description: Normal multipole phases [deg], dipole through decapole.
    from_schema: https://w3id.org/laura/schema/simulation
    rank: 1000
    domain_of:
    - RFMultipoleSimulationElement
    range: float
    multivalued: true
  psl:
    name: psl
    description: Skew multipole phases [deg], dipole through decapole.
    from_schema: https://w3id.org/laura/schema/simulation
    rank: 1000
    domain_of:
    - RFMultipoleSimulationElement
    range: float
    multivalued: true
class_uri: laura:RFMultipoleSimulationElement

```
</details>

### Induced

<details>
```yaml
name: RFMultipoleSimulationElement
description: Simulation attributes for a thin RF multipole kick.
from_schema: https://w3id.org/laura/schema
is_a: SimulationElement
slot_usage:
  frequency:
    name: frequency
    description: RF frequency [Hz].
    ifabsent: float(0.0)
  phase:
    name: phase
    description: Overall phase lag [deg].
    ifabsent: float(0.0)
  field_amplitude:
    name: field_amplitude
    description: Longitudinal voltage [V].
    ifabsent: float(0.0)
attributes:
  knl:
    name: knl
    description: Integrated normal multipole strengths, dipole through decapole.
    from_schema: https://w3id.org/laura/schema/simulation
    rank: 1000
    owner: RFMultipoleSimulationElement
    domain_of:
    - RFMultipoleSimulationElement
    range: float
    multivalued: true
  ksl:
    name: ksl
    description: Integrated skew multipole strengths, dipole through decapole.
    from_schema: https://w3id.org/laura/schema/simulation
    rank: 1000
    owner: RFMultipoleSimulationElement
    domain_of:
    - RFMultipoleSimulationElement
    range: float
    multivalued: true
  pnl:
    name: pnl
    description: Normal multipole phases [deg], dipole through decapole.
    from_schema: https://w3id.org/laura/schema/simulation
    rank: 1000
    owner: RFMultipoleSimulationElement
    domain_of:
    - RFMultipoleSimulationElement
    range: float
    multivalued: true
  psl:
    name: psl
    description: Skew multipole phases [deg], dipole through decapole.
    from_schema: https://w3id.org/laura/schema/simulation
    rank: 1000
    owner: RFMultipoleSimulationElement
    domain_of:
    - RFMultipoleSimulationElement
    range: float
    multivalued: true
  frequency:
    name: frequency
    description: RF frequency [Hz].
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    ifabsent: float(0.0)
    owner: RFMultipoleSimulationElement
    domain_of:
    - ACDipoleSimulationElement
    - RFMultipoleSimulationElement
    - RFCavityElement
    - RFDeflectingCavityElement
    range: float
    minimum_value: 0.0
    unit:
      ucum_code: Hz
  phase:
    name: phase
    description: Overall phase lag [deg].
    in_subset:
    - functional_parameters
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    ifabsent: float(0.0)
    owner: RFMultipoleSimulationElement
    domain_of:
    - ACDipoleSimulationElement
    - RFMultipoleSimulationElement
    - RFCavityElement
    - RFDeflectingCavityElement
    range: float
    unit:
      ucum_code: deg
    any_of:
    - range: float
    - range: string
  field_amplitude:
    name: field_amplitude
    description: Longitudinal voltage [V].
    in_subset:
    - functional_parameters
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    ifabsent: float(0.0)
    owner: RFMultipoleSimulationElement
    domain_of:
    - MagnetSimulationElement
    - RFCavitySimulationElement
    - ACDipoleSimulationElement
    - RFMultipoleSimulationElement
    range: float
    any_of:
    - range: float
    - range: string
  n_kicks:
    name: n_kicks
    description: Number of integration kicks.
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    owner: RFMultipoleSimulationElement
    domain_of:
    - SimulationElement
    range: integer
  lsc_bins:
    name: lsc_bins
    description: Number of bins used in longitudinal space-charge calculations.
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    owner: RFMultipoleSimulationElement
    domain_of:
    - SimulationElement
    range: integer
  csr_enable:
    name: csr_enable
    description: Whether coherent synchrotron radiation effects are enabled.
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    ifabsent: 'true'
    owner: RFMultipoleSimulationElement
    domain_of:
    - SimulationElement
    range: boolean
  lsc_enable:
    name: lsc_enable
    description: Whether longitudinal space-charge effects are enabled.
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    ifabsent: 'true'
    owner: RFMultipoleSimulationElement
    domain_of:
    - SimulationElement
    range: boolean
  tracking_method:
    name: tracking_method
    description: Phase-space tracking algorithm requested from the target code.
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    owner: RFMultipoleSimulationElement
    domain_of:
    - SimulationElement
    range: string
  mat6_calc_method:
    name: mat6_calc_method
    description: Method used to calculate the element's 6x6 transfer matrix.
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    owner: RFMultipoleSimulationElement
    domain_of:
    - SimulationElement
    range: string
  spin_tracking_method:
    name: spin_tracking_method
    description: Spin-tracking algorithm requested from the target code.
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    owner: RFMultipoleSimulationElement
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
    owner: RFMultipoleSimulationElement
    domain_of:
    - SimulationElement
    range: integer
    minimum_value: 1
  num_steps:
    name: num_steps
    description: Number of integration steps through the element.
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    owner: RFMultipoleSimulationElement
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
    owner: RFMultipoleSimulationElement
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
    owner: RFMultipoleSimulationElement
    domain_of:
    - SimulationElement
    range: string
  space_charge_method:
    name: space_charge_method
    description: Space-charge tracking method.
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    owner: RFMultipoleSimulationElement
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
    owner: RFMultipoleSimulationElement
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
    owner: RFMultipoleSimulationElement
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
    owner: RFMultipoleSimulationElement
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
    owner: RFMultipoleSimulationElement
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
    owner: RFMultipoleSimulationElement
    domain_of:
    - SimulationElement
    range: string
  wakefield_definition:
    name: wakefield_definition
    description: Path to the wakefield impedance file.
    from_schema: https://w3id.org/laura/schema/simulation
    rank: 1000
    owner: RFMultipoleSimulationElement
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
    owner: RFMultipoleSimulationElement
    domain_of:
    - SimulationElement
    range: boolean
  field_reference_position:
    name: field_reference_position
    description: Longitudinal origin of the field map [m].
    from_schema: https://w3id.org/laura/schema/simulation
    rank: 1000
    owner: RFMultipoleSimulationElement
    domain_of:
    - SimulationElement
    range: string
  scale_field:
    name: scale_field
    description: Multiplicative scale factor applied to the field map.
    from_schema: https://w3id.org/laura/schema/simulation
    rank: 1000
    ifabsent: float(1)
    owner: RFMultipoleSimulationElement
    domain_of:
    - SimulationElement
    range: float
class_uri: laura:RFMultipoleSimulationElement

```
</details></div>