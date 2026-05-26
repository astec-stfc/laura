---
search:
  boost: 10.0
---

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
      
      DriftSimulationElement : field_definition
        
      DriftSimulationElement : field_reference_position
        
      DriftSimulationElement : scale_field
        
      DriftSimulationElement : wakefield_definition
        
      
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
| [field_definition](field_definition.md) | 0..1 <br/> [String](String.md) | Path to the 3-D field-map file | [SimulationElement](SimulationElement.md) |
| [wakefield_definition](wakefield_definition.md) | 0..1 <br/> [String](String.md) | Path to the wakefield impedance file | [SimulationElement](SimulationElement.md) |
| [field_reference_position](field_reference_position.md) | 0..1 <br/> [Float](Float.md) | Longitudinal origin of the field map [m] | [SimulationElement](SimulationElement.md) |
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
attributes:
  field_definition:
    name: field_definition
    description: Path to the 3-D field-map file.
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    owner: DriftSimulationElement
    domain_of:
    - SimulationElement
    range: string
  wakefield_definition:
    name: wakefield_definition
    description: Path to the wakefield impedance file.
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    owner: DriftSimulationElement
    domain_of:
    - SimulationElement
    range: string
  field_reference_position:
    name: field_reference_position
    description: Longitudinal origin of the field map [m].
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    owner: DriftSimulationElement
    domain_of:
    - SimulationElement
    range: float
    unit:
      ucum_code: m
  scale_field:
    name: scale_field
    description: Multiplicative scale factor applied to the field map.
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    owner: DriftSimulationElement
    domain_of:
    - SimulationElement
    range: float
class_uri: laura:DriftSimulationElement

```
</details></div>