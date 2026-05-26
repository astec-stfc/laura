---
search:
  boost: 10.0
---

# Class: PIDElement 


_PID feedback-controller parameters._



<div data-search-exclude markdown="1">



URI: [laura:PIDElement](https://w3id.org/laura/PIDElement)





```mermaid
 classDiagram
    class PIDElement
    click PIDElement href "../PIDElement/"
      PIDElement : Kd
        
      PIDElement : Ki
        
      PIDElement : Kp
        
      
```




<!-- no inheritance hierarchy -->

## Class Properties

| Property | Value |
| --- | --- |
| Class URI | [laura:PIDElement](https://w3id.org/laura/PIDElement) |


## Slots

| Name | Cardinality and Range | Description | Inheritance |
| ---  | --- | --- | --- |
| [Kp](Kp.md) | 0..1 <br/> [Float](Float.md) | Proportional gain | direct |
| [Ki](Ki.md) | 0..1 <br/> [Float](Float.md) | Integral gain | direct |
| [Kd](Kd.md) | 0..1 <br/> [Float](Float.md) | Derivative gain | direct |





## Usages

| used by | used in | type | used |
| ---  | --- | --- | --- |
| [PID](PID.md) | [pid](pid.md) | range | [PIDElement](PIDElement.md) |












## Identifier and Mapping Information





### Schema Source


* from schema: https://w3id.org/laura/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | laura:PIDElement |
| native | laura:PIDElement |






## LinkML Source

<!-- TODO: investigate https://stackoverflow.com/questions/37606292/how-to-create-tabbed-code-blocks-in-mkdocs-or-sphinx -->

### Direct

<details>
```yaml
name: PIDElement
description: PID feedback-controller parameters.
from_schema: https://w3id.org/laura/schema
attributes:
  Kp:
    name: Kp
    description: Proportional gain.
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    domain_of:
    - PIDElement
    range: float
  Ki:
    name: Ki
    description: Integral gain.
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    domain_of:
    - PIDElement
    range: float
  Kd:
    name: Kd
    description: Derivative gain.
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    domain_of:
    - PIDElement
    range: float
class_uri: laura:PIDElement

```
</details>

### Induced

<details>
```yaml
name: PIDElement
description: PID feedback-controller parameters.
from_schema: https://w3id.org/laura/schema
attributes:
  Kp:
    name: Kp
    description: Proportional gain.
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    owner: PIDElement
    domain_of:
    - PIDElement
    range: float
  Ki:
    name: Ki
    description: Integral gain.
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    owner: PIDElement
    domain_of:
    - PIDElement
    range: float
  Kd:
    name: Kd
    description: Derivative gain.
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    owner: PIDElement
    domain_of:
    - PIDElement
    range: float
class_uri: laura:PIDElement

```
</details></div>