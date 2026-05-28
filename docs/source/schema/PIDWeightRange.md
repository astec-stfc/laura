---
search:
  boost: 10.0
---

# Class: PIDWeightRange 


_Numeric min/max range for PID phase weighting._



<div data-search-exclude markdown="1">



URI: [laura:PIDWeightRange](https://w3id.org/laura/PIDWeightRange)





```mermaid
 classDiagram
    class PIDWeightRange
    click PIDWeightRange href "../PIDWeightRange/"
      PIDPhaseRange <|-- PIDWeightRange
        click PIDPhaseRange href "../PIDPhaseRange/"
      
      PIDWeightRange : max
        
      PIDWeightRange : min
        
      
```





## Inheritance
* [PIDPhaseRange](PIDPhaseRange.md)
    * **PIDWeightRange**


## Class Properties

| Property | Value |
| --- | --- |
| Class URI | [laura:PIDWeightRange](https://w3id.org/laura/PIDWeightRange) |


## Slots

| Name | Cardinality and Range | Description | Inheritance |
| ---  | --- | --- | --- |
| [min](min.md) | 0..1 <br/> [Float](Float.md) | Minimum value | [PIDPhaseRange](PIDPhaseRange.md) |
| [max](max.md) | 0..1 <br/> [Float](Float.md) | Maximum value | [PIDPhaseRange](PIDPhaseRange.md) |





## Usages

| used by | used in | type | used |
| ---  | --- | --- | --- |
| [PIDElement](PIDElement.md) | [phase_weight_range](phase_weight_range.md) | range | [PIDWeightRange](PIDWeightRange.md) |












## Identifier and Mapping Information





### Schema Source


* from schema: https://w3id.org/laura/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | laura:PIDWeightRange |
| native | laura:PIDWeightRange |






## LinkML Source

<!-- TODO: investigate https://stackoverflow.com/questions/37606292/how-to-create-tabbed-code-blocks-in-mkdocs-or-sphinx -->

### Direct

<details>
```yaml
name: PIDWeightRange
description: Numeric min/max range for PID phase weighting.
from_schema: https://w3id.org/laura/schema
is_a: PIDPhaseRange
class_uri: laura:PIDWeightRange

```
</details>

### Induced

<details>
```yaml
name: PIDWeightRange
description: Numeric min/max range for PID phase weighting.
from_schema: https://w3id.org/laura/schema
is_a: PIDPhaseRange
attributes:
  min:
    name: min
    description: Minimum value.
    from_schema: https://w3id.org/laura/schema/rf
    rank: 1000
    owner: PIDWeightRange
    domain_of:
    - PIDPhaseRange
    range: float
  max:
    name: max
    description: Maximum value.
    from_schema: https://w3id.org/laura/schema/rf
    rank: 1000
    owner: PIDWeightRange
    domain_of:
    - PIDPhaseRange
    range: float
class_uri: laura:PIDWeightRange

```
</details></div>