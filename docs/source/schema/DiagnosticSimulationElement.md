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
      
      DiagnosticSimulationElement : field_definition
        
      DiagnosticSimulationElement : field_reference_position
        
      DiagnosticSimulationElement : output_filename
        
      DiagnosticSimulationElement : scale_field
        
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