# Class: MagnetSimulationElement 


_Simulation attributes specific to magnets: integrator settings, fringe-field model, and radiation flags._



<div data-search-exclude markdown="1">



URI: [laura:MagnetSimulationElement](https://w3id.org/laura/MagnetSimulationElement)





```mermaid
 classDiagram
    class MagnetSimulationElement
    click MagnetSimulationElement href "../MagnetSimulationElement/"
      SimulationElement <|-- MagnetSimulationElement
        click SimulationElement href "../SimulationElement/"
      
      MagnetSimulationElement : csr_bins
        
      MagnetSimulationElement : csr_enable
        
      MagnetSimulationElement : deltaL
        
      MagnetSimulationElement : edge1_effects
        
      MagnetSimulationElement : edge2_effects
        
      MagnetSimulationElement : edge_field_integral
        
      MagnetSimulationElement : edge_order
        
      MagnetSimulationElement : field_amplitude
        
      MagnetSimulationElement : field_definition
        
      MagnetSimulationElement : field_reference_position
        
      MagnetSimulationElement : integration_order
        
      MagnetSimulationElement : isr_enable
        
      MagnetSimulationElement : n_kicks
        
      MagnetSimulationElement : n_slices
        
      MagnetSimulationElement : nonlinear
        
      MagnetSimulationElement : scale_field
        
      MagnetSimulationElement : smooth
        
      MagnetSimulationElement : smooth_points
        
      MagnetSimulationElement : smoothing_half_width
        
      MagnetSimulationElement : sr_enable
        
      MagnetSimulationElement : wakefield_definition
        
      MagnetSimulationElement : wakefield_enable
        
      
```





## Inheritance
* [SimulationElement](SimulationElement.md)
    * **MagnetSimulationElement**


## Class Properties

| Property | Value |
| --- | --- |
| Class URI | [laura:MagnetSimulationElement](https://w3id.org/laura/MagnetSimulationElement) |


## Slots

| Name | Cardinality and Range | Description | Inheritance |
| ---  | --- | --- | --- |
| [n_kicks](n_kicks.md) | 0..1 <br/> [Integer](Integer.md) | Number of integration kicks | direct |
| [field_amplitude](field_amplitude.md) | 0..1 <br/> [Float](Float.md)&nbsp;or&nbsp;<br />[String](String.md) | Field amplitude scaling for magnet tracking | direct |
| [n_slices](n_slices.md) | 0..1 <br/> [Integer](Integer.md) | Number of longitudinal slices for thick-lens tracking | direct |
| [smooth](smooth.md) | 0..1 <br/> [Integer](Integer.md) | Number of smoothing passes applied to the field map (ASTRA Q_smooth / S_smoot... | direct |
| [edge_field_integral](edge_field_integral.md) | 0..1 <br/> [Float](Float.md) | Fringe-field integral for edge focussing | direct |
| [edge1_effects](edge1_effects.md) | 0..1 <br/> [Boolean](Boolean.md) | Enable entrance-edge focussing effects | direct |
| [edge2_effects](edge2_effects.md) | 0..1 <br/> [Boolean](Boolean.md) | Enable exit-edge focussing effects | direct |
| [sr_enable](sr_enable.md) | 0..1 <br/> [Boolean](Boolean.md) | Enable synchrotron-radiation energy loss | direct |
| [isr_enable](isr_enable.md) | 0..1 <br/> [Boolean](Boolean.md) | Enable incoherent synchrotron-radiation emittance growth | direct |
| [csr_enable](csr_enable.md) | 0..1 <br/> [Boolean](Boolean.md) | Enable coherent synchrotron radiation | direct |
| [csr_bins](csr_bins.md) | 0..1 <br/> [Integer](Integer.md) | Number of longitudinal bins for the CSR mesh | direct |
| [integration_order](integration_order.md) | 0..1 <br/> [Integer](Integer.md) | Order of the symplectic integrator | direct |
| [nonlinear](nonlinear.md) | 0..1 <br/> [Boolean](Boolean.md) | Include higher-order (sextupole+) field components | direct |
| [smoothing_half_width](smoothing_half_width.md) | 0..1 <br/> [Integer](Integer.md) | Half-width of the current-profile smoothing kernel | direct |
| [edge_order](edge_order.md) | 0..1 <br/> [Integer](Integer.md) | Polynomial order of the edge-field expansion | direct |
| [deltaL](deltaL.md) | 0..1 <br/> [Float](Float.md) | Longitudinal step-size override for thick-lens integration [m] | direct |
| [smooth_points](smooth_points.md) | 0..1 <br/> [Float](Float.md) | Number of points used to smooth the field map [ASTRA] | direct |
| [field_definition](field_definition.md) | 0..1 <br/> [String](String.md) | Path to the 3-D field-map file | [SimulationElement](SimulationElement.md) |
| [wakefield_definition](wakefield_definition.md) | 0..1 <br/> [String](String.md) | Path to the wakefield impedance file | [SimulationElement](SimulationElement.md) |
| [wakefield_enable](wakefield_enable.md) | 0..1 <br/> [Boolean](Boolean.md) | Whether the wakefield named by wakefield_definition is applied | [SimulationElement](SimulationElement.md) |
| [field_reference_position](field_reference_position.md) | 0..1 <br/> [String](String.md) | Longitudinal origin of the field map [m] | [SimulationElement](SimulationElement.md) |
| [scale_field](scale_field.md) | 0..1 <br/> [Float](Float.md) | Multiplicative scale factor applied to the field map | [SimulationElement](SimulationElement.md) |





## Usages

| used by | used in | type | used |
| ---  | --- | --- | --- |
| [Magnet](Magnet.md) | [simulation](simulation.md) | range | [MagnetSimulationElement](MagnetSimulationElement.md) |
| [Dipole](Dipole.md) | [simulation](simulation.md) | range | [MagnetSimulationElement](MagnetSimulationElement.md) |
| [Quadrupole](Quadrupole.md) | [simulation](simulation.md) | range | [MagnetSimulationElement](MagnetSimulationElement.md) |
| [Sextupole](Sextupole.md) | [simulation](simulation.md) | range | [MagnetSimulationElement](MagnetSimulationElement.md) |
| [Octupole](Octupole.md) | [simulation](simulation.md) | range | [MagnetSimulationElement](MagnetSimulationElement.md) |
| [Decapole](Decapole.md) | [simulation](simulation.md) | range | [MagnetSimulationElement](MagnetSimulationElement.md) |
| [HorizontalCorrector](HorizontalCorrector.md) | [simulation](simulation.md) | range | [MagnetSimulationElement](MagnetSimulationElement.md) |
| [VerticalCorrector](VerticalCorrector.md) | [simulation](simulation.md) | range | [MagnetSimulationElement](MagnetSimulationElement.md) |
| [CombinedCorrector](CombinedCorrector.md) | [simulation](simulation.md) | range | [MagnetSimulationElement](MagnetSimulationElement.md) |
| [Solenoid](Solenoid.md) | [simulation](simulation.md) | range | [MagnetSimulationElement](MagnetSimulationElement.md) |
| [CombinedSolenoidQuadrupole](CombinedSolenoidQuadrupole.md) | [simulation](simulation.md) | range | [MagnetSimulationElement](MagnetSimulationElement.md) |
| [Wiggler](Wiggler.md) | [simulation](simulation.md) | range | [MagnetSimulationElement](MagnetSimulationElement.md) |
| [NonLinearLens](NonLinearLens.md) | [simulation](simulation.md) | range | [MagnetSimulationElement](MagnetSimulationElement.md) |












## Identifier and Mapping Information





### Schema Source


* from schema: https://w3id.org/laura/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | laura:MagnetSimulationElement |
| native | laura:MagnetSimulationElement |






## LinkML Source

<!-- TODO: investigate https://stackoverflow.com/questions/37606292/how-to-create-tabbed-code-blocks-in-mkdocs-or-sphinx -->

### Direct

<details>
```yaml
name: MagnetSimulationElement
description: 'Simulation attributes specific to magnets: integrator settings, fringe-field
  model, and radiation flags.'
from_schema: https://w3id.org/laura/schema
is_a: SimulationElement
slots:
- n_kicks
- field_amplitude
slot_usage:
  n_kicks:
    name: n_kicks
    description: Number of integration kicks.
    ifabsent: int(4)
    minimum_value: 1
  field_amplitude:
    name: field_amplitude
    description: Field amplitude scaling for magnet tracking.
    ifabsent: float(0.0)
attributes:
  n_slices:
    name: n_slices
    description: Number of longitudinal slices for thick-lens tracking.
    from_schema: https://w3id.org/laura/schema/simulation
    rank: 1000
    ifabsent: int(4)
    domain_of:
    - MagnetSimulationElement
    range: integer
    minimum_value: 1
  smooth:
    name: smooth
    description: Number of smoothing passes applied to the field map (ASTRA Q_smooth
      / S_smooth).
    from_schema: https://w3id.org/laura/schema/simulation
    rank: 1000
    domain_of:
    - MagnetSimulationElement
    - RFCavitySimulationElement
    - WakefieldSimulationElement
    range: integer
  edge_field_integral:
    name: edge_field_integral
    description: Fringe-field integral for edge focussing.
    from_schema: https://w3id.org/laura/schema/simulation
    rank: 1000
    ifabsent: float(0.5)
    domain_of:
    - MagnetSimulationElement
    - MagneticElement
    range: float
  edge1_effects:
    name: edge1_effects
    description: Enable entrance-edge focussing effects.
    from_schema: https://w3id.org/laura/schema/simulation
    rank: 1000
    domain_of:
    - MagnetSimulationElement
    range: boolean
  edge2_effects:
    name: edge2_effects
    description: Enable exit-edge focussing effects.
    from_schema: https://w3id.org/laura/schema/simulation
    rank: 1000
    domain_of:
    - MagnetSimulationElement
    range: boolean
  sr_enable:
    name: sr_enable
    description: Enable synchrotron-radiation energy loss.
    from_schema: https://w3id.org/laura/schema/simulation
    rank: 1000
    ifabsent: 'True'
    domain_of:
    - MagnetSimulationElement
    range: boolean
  isr_enable:
    name: isr_enable
    description: Enable incoherent synchrotron-radiation emittance growth.
    from_schema: https://w3id.org/laura/schema/simulation
    rank: 1000
    ifabsent: 'True'
    domain_of:
    - MagnetSimulationElement
    range: boolean
  csr_enable:
    name: csr_enable
    description: Enable coherent synchrotron radiation.
    from_schema: https://w3id.org/laura/schema/simulation
    rank: 1000
    ifabsent: 'True'
    domain_of:
    - MagnetSimulationElement
    - DriftSimulationElement
    range: boolean
  csr_bins:
    name: csr_bins
    description: Number of longitudinal bins for the CSR mesh.
    from_schema: https://w3id.org/laura/schema/simulation
    rank: 1000
    ifabsent: int(100)
    domain_of:
    - MagnetSimulationElement
    range: integer
  integration_order:
    name: integration_order
    description: Order of the symplectic integrator.
    from_schema: https://w3id.org/laura/schema/simulation
    rank: 1000
    ifabsent: int(4)
    domain_of:
    - MagnetSimulationElement
    range: integer
  nonlinear:
    name: nonlinear
    description: Include higher-order (sextupole+) field components.
    from_schema: https://w3id.org/laura/schema/simulation
    rank: 1000
    domain_of:
    - MagnetSimulationElement
    range: boolean
  smoothing_half_width:
    name: smoothing_half_width
    description: Half-width of the current-profile smoothing kernel.
    from_schema: https://w3id.org/laura/schema/simulation
    rank: 1000
    ifabsent: int(1)
    domain_of:
    - MagnetSimulationElement
    range: integer
  edge_order:
    name: edge_order
    description: Polynomial order of the edge-field expansion.
    from_schema: https://w3id.org/laura/schema/simulation
    rank: 1000
    ifabsent: int(2)
    domain_of:
    - MagnetSimulationElement
    range: integer
  deltaL:
    name: deltaL
    description: Longitudinal step-size override for thick-lens integration [m].
    from_schema: https://w3id.org/laura/schema/simulation
    rank: 1000
    ifabsent: float(0.0)
    domain_of:
    - MagnetSimulationElement
    range: float
    unit:
      ucum_code: m
  smooth_points:
    name: smooth_points
    description: Number of points used to smooth the field map [ASTRA].
    from_schema: https://w3id.org/laura/schema/simulation
    rank: 1000
    ifabsent: float(2)
    domain_of:
    - MagnetSimulationElement
    range: float
class_uri: laura:MagnetSimulationElement

```
</details>

### Induced

<details>
```yaml
name: MagnetSimulationElement
description: 'Simulation attributes specific to magnets: integrator settings, fringe-field
  model, and radiation flags.'
from_schema: https://w3id.org/laura/schema
is_a: SimulationElement
slot_usage:
  n_kicks:
    name: n_kicks
    description: Number of integration kicks.
    ifabsent: int(4)
    minimum_value: 1
  field_amplitude:
    name: field_amplitude
    description: Field amplitude scaling for magnet tracking.
    ifabsent: float(0.0)
attributes:
  n_slices:
    name: n_slices
    description: Number of longitudinal slices for thick-lens tracking.
    from_schema: https://w3id.org/laura/schema/simulation
    rank: 1000
    ifabsent: int(4)
    owner: MagnetSimulationElement
    domain_of:
    - MagnetSimulationElement
    range: integer
    minimum_value: 1
  smooth:
    name: smooth
    description: Number of smoothing passes applied to the field map (ASTRA Q_smooth
      / S_smooth).
    from_schema: https://w3id.org/laura/schema/simulation
    rank: 1000
    owner: MagnetSimulationElement
    domain_of:
    - MagnetSimulationElement
    - RFCavitySimulationElement
    - WakefieldSimulationElement
    range: integer
  edge_field_integral:
    name: edge_field_integral
    description: Fringe-field integral for edge focussing.
    from_schema: https://w3id.org/laura/schema/simulation
    rank: 1000
    ifabsent: float(0.5)
    owner: MagnetSimulationElement
    domain_of:
    - MagnetSimulationElement
    - MagneticElement
    range: float
  edge1_effects:
    name: edge1_effects
    description: Enable entrance-edge focussing effects.
    from_schema: https://w3id.org/laura/schema/simulation
    rank: 1000
    owner: MagnetSimulationElement
    domain_of:
    - MagnetSimulationElement
    range: boolean
  edge2_effects:
    name: edge2_effects
    description: Enable exit-edge focussing effects.
    from_schema: https://w3id.org/laura/schema/simulation
    rank: 1000
    owner: MagnetSimulationElement
    domain_of:
    - MagnetSimulationElement
    range: boolean
  sr_enable:
    name: sr_enable
    description: Enable synchrotron-radiation energy loss.
    from_schema: https://w3id.org/laura/schema/simulation
    rank: 1000
    ifabsent: 'True'
    owner: MagnetSimulationElement
    domain_of:
    - MagnetSimulationElement
    range: boolean
  isr_enable:
    name: isr_enable
    description: Enable incoherent synchrotron-radiation emittance growth.
    from_schema: https://w3id.org/laura/schema/simulation
    rank: 1000
    ifabsent: 'True'
    owner: MagnetSimulationElement
    domain_of:
    - MagnetSimulationElement
    range: boolean
  csr_enable:
    name: csr_enable
    description: Enable coherent synchrotron radiation.
    from_schema: https://w3id.org/laura/schema/simulation
    rank: 1000
    ifabsent: 'True'
    owner: MagnetSimulationElement
    domain_of:
    - MagnetSimulationElement
    - DriftSimulationElement
    range: boolean
  csr_bins:
    name: csr_bins
    description: Number of longitudinal bins for the CSR mesh.
    from_schema: https://w3id.org/laura/schema/simulation
    rank: 1000
    ifabsent: int(100)
    owner: MagnetSimulationElement
    domain_of:
    - MagnetSimulationElement
    range: integer
  integration_order:
    name: integration_order
    description: Order of the symplectic integrator.
    from_schema: https://w3id.org/laura/schema/simulation
    rank: 1000
    ifabsent: int(4)
    owner: MagnetSimulationElement
    domain_of:
    - MagnetSimulationElement
    range: integer
  nonlinear:
    name: nonlinear
    description: Include higher-order (sextupole+) field components.
    from_schema: https://w3id.org/laura/schema/simulation
    rank: 1000
    owner: MagnetSimulationElement
    domain_of:
    - MagnetSimulationElement
    range: boolean
  smoothing_half_width:
    name: smoothing_half_width
    description: Half-width of the current-profile smoothing kernel.
    from_schema: https://w3id.org/laura/schema/simulation
    rank: 1000
    ifabsent: int(1)
    owner: MagnetSimulationElement
    domain_of:
    - MagnetSimulationElement
    range: integer
  edge_order:
    name: edge_order
    description: Polynomial order of the edge-field expansion.
    from_schema: https://w3id.org/laura/schema/simulation
    rank: 1000
    ifabsent: int(2)
    owner: MagnetSimulationElement
    domain_of:
    - MagnetSimulationElement
    range: integer
  deltaL:
    name: deltaL
    description: Longitudinal step-size override for thick-lens integration [m].
    from_schema: https://w3id.org/laura/schema/simulation
    rank: 1000
    ifabsent: float(0.0)
    owner: MagnetSimulationElement
    domain_of:
    - MagnetSimulationElement
    range: float
    unit:
      ucum_code: m
  smooth_points:
    name: smooth_points
    description: Number of points used to smooth the field map [ASTRA].
    from_schema: https://w3id.org/laura/schema/simulation
    rank: 1000
    ifabsent: float(2)
    owner: MagnetSimulationElement
    domain_of:
    - MagnetSimulationElement
    range: float
  n_kicks:
    name: n_kicks
    description: Number of integration kicks.
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    ifabsent: int(4)
    owner: MagnetSimulationElement
    domain_of:
    - MagnetSimulationElement
    - RFCavitySimulationElement
    range: integer
    minimum_value: 1
  field_amplitude:
    name: field_amplitude
    description: Field amplitude scaling for magnet tracking.
    in_subset:
    - functional_parameters
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    ifabsent: float(0.0)
    owner: MagnetSimulationElement
    domain_of:
    - MagnetSimulationElement
    - RFCavitySimulationElement
    - ACDipoleSimulationElement
    - RFMultipoleSimulationElement
    range: float
    any_of:
    - range: float
    - range: string
  field_definition:
    name: field_definition
    description: Path to the 3-D field-map file.
    from_schema: https://w3id.org/laura/schema/simulation
    rank: 1000
    owner: MagnetSimulationElement
    domain_of:
    - SimulationElement
    range: string
  wakefield_definition:
    name: wakefield_definition
    description: Path to the wakefield impedance file.
    from_schema: https://w3id.org/laura/schema/simulation
    rank: 1000
    owner: MagnetSimulationElement
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
    owner: MagnetSimulationElement
    domain_of:
    - SimulationElement
    range: boolean
  field_reference_position:
    name: field_reference_position
    description: Longitudinal origin of the field map [m].
    from_schema: https://w3id.org/laura/schema/simulation
    rank: 1000
    owner: MagnetSimulationElement
    domain_of:
    - SimulationElement
    range: string
  scale_field:
    name: scale_field
    description: Multiplicative scale factor applied to the field map.
    from_schema: https://w3id.org/laura/schema/simulation
    rank: 1000
    ifabsent: float(1)
    owner: MagnetSimulationElement
    domain_of:
    - SimulationElement
    range: float
class_uri: laura:MagnetSimulationElement

```
</details></div>