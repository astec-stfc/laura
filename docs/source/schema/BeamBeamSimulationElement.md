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
        
      BeamBeamSimulationElement : field_definition
        
      BeamBeamSimulationElement : field_reference_position
        
      BeamBeamSimulationElement : horizontal_offset
        
      BeamBeamSimulationElement : horizontal_sigma
        
      BeamBeamSimulationElement : n_particles
        
      BeamBeamSimulationElement : scale_field
        
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
| [charge](charge.md) | 0..1 <br/> [Double](Double.md) | Opposing-beam particle charge in units of the elementary charge | direct |
| [n_particles](n_particles.md) | 0..1 <br/> [Double](Double.md) | Number of particles in the opposing bunch | direct |
| [horizontal_offset](horizontal_offset.md) | 0..1 <br/> [Double](Double.md) | Horizontal opposing-bunch centroid offset [m] | direct |
| [vertical_offset](vertical_offset.md) | 0..1 <br/> [Double](Double.md) | Vertical opposing-bunch centroid offset [m] | direct |
| [horizontal_sigma](horizontal_sigma.md) | 0..1 <br/> [Double](Double.md) | Horizontal RMS size of the opposing bunch [m] | direct |
| [vertical_sigma](vertical_sigma.md) | 0..1 <br/> [Double](Double.md) | Vertical RMS size of the opposing bunch [m] | direct |
| [width](width.md) | 0..1 <br/> [Double](Double.md) | Opposing-bunch length for the 3-D weak-strong model [m] | direct |
| [field_definition](field_definition.md) | 0..1 <br/> [String](String.md) | Path to the 3-D field-map file | [SimulationElement](SimulationElement.md) |
| [wakefield_definition](wakefield_definition.md) | 0..1 <br/> [String](String.md) | Path to the wakefield impedance file | [SimulationElement](SimulationElement.md) |
| [wakefield_enable](wakefield_enable.md) | 0..1 <br/> [Boolean](Boolean.md) | Whether the wakefield named by wakefield_definition is applied | [SimulationElement](SimulationElement.md) |
| [field_reference_position](field_reference_position.md) | 0..1 <br/> [String](String.md) | Longitudinal origin of the field map [m] | [SimulationElement](SimulationElement.md) |
| [scale_field](scale_field.md) | 0..1 <br/> [Double](Double.md) | Multiplicative scale factor applied to the field map | [SimulationElement](SimulationElement.md) |





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
    range: double
  n_particles:
    name: n_particles
    description: Number of particles in the opposing bunch.
    from_schema: https://w3id.org/laura/schema/simulation
    rank: 1000
    ifabsent: float(0.0)
    domain_of:
    - BeamBeamSimulationElement
    range: double
  horizontal_offset:
    name: horizontal_offset
    description: Horizontal opposing-bunch centroid offset [m].
    from_schema: https://w3id.org/laura/schema/simulation
    ifabsent: float(0.0)
    domain_of:
    - WireSimulationElement
    - BeamBeamSimulationElement
    range: double
    unit:
      ucum_code: m
  vertical_offset:
    name: vertical_offset
    description: Vertical opposing-bunch centroid offset [m].
    from_schema: https://w3id.org/laura/schema/simulation
    ifabsent: float(0.0)
    domain_of:
    - WireSimulationElement
    - BeamBeamSimulationElement
    range: double
    unit:
      ucum_code: m
  horizontal_sigma:
    name: horizontal_sigma
    description: Horizontal RMS size of the opposing bunch [m].
    from_schema: https://w3id.org/laura/schema/simulation
    rank: 1000
    ifabsent: float(0.0)
    domain_of:
    - BeamBeamSimulationElement
    range: double
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
    range: double
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
    range: double
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
    range: double
  n_particles:
    name: n_particles
    description: Number of particles in the opposing bunch.
    from_schema: https://w3id.org/laura/schema/simulation
    rank: 1000
    ifabsent: float(0.0)
    owner: BeamBeamSimulationElement
    domain_of:
    - BeamBeamSimulationElement
    range: double
  horizontal_offset:
    name: horizontal_offset
    description: Horizontal opposing-bunch centroid offset [m].
    from_schema: https://w3id.org/laura/schema/simulation
    ifabsent: float(0.0)
    owner: BeamBeamSimulationElement
    domain_of:
    - WireSimulationElement
    - BeamBeamSimulationElement
    range: double
    unit:
      ucum_code: m
  vertical_offset:
    name: vertical_offset
    description: Vertical opposing-bunch centroid offset [m].
    from_schema: https://w3id.org/laura/schema/simulation
    ifabsent: float(0.0)
    owner: BeamBeamSimulationElement
    domain_of:
    - WireSimulationElement
    - BeamBeamSimulationElement
    range: double
    unit:
      ucum_code: m
  horizontal_sigma:
    name: horizontal_sigma
    description: Horizontal RMS size of the opposing bunch [m].
    from_schema: https://w3id.org/laura/schema/simulation
    rank: 1000
    ifabsent: float(0.0)
    owner: BeamBeamSimulationElement
    domain_of:
    - BeamBeamSimulationElement
    range: double
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
    range: double
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
    range: double
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
    range: double
class_uri: laura:BeamBeamSimulationElement

```
</details></div>