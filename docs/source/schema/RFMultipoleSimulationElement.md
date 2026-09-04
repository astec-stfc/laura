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
      
      RFMultipoleSimulationElement : field_amplitude
        
      RFMultipoleSimulationElement : field_definition
        
      RFMultipoleSimulationElement : field_reference_position
        
      RFMultipoleSimulationElement : frequency
        
      RFMultipoleSimulationElement : knl
        
      RFMultipoleSimulationElement : ksl
        
      RFMultipoleSimulationElement : phase
        
      RFMultipoleSimulationElement : pnl
        
      RFMultipoleSimulationElement : psl
        
      RFMultipoleSimulationElement : scale_field
        
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