---
search:
  boost: 5.0
---

# Slot: cep_phase 


_Carrier-envelope phase [rad]._



<div data-search-exclude markdown="1">



URI: [laura:cep_phase](https://w3id.org/laura/cep_phase)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [LaserElement](LaserElement.md) | Laser-beam parameters (wavelength, pulse energy, profile, etc |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [Float](Float.md) |
| Domain Of | [LaserElement](LaserElement.md) |

### Cardinality and Requirements

| Property | Value |
| --- | --- |
### Slot Characteristics

| Property | Value |
| --- | --- |
| Owner | [LaserElement](LaserElement.md) |


<details>
<summary>Additional Constraints</summary>
**Unit:**

| Property | Value |
| --- | --- |
| ucum_code | rad |

</details>











## Identifier and Mapping Information





### Schema Source


* from schema: https://w3id.org/laura/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | laura:cep_phase |
| native | laura:cep_phase |




## LinkML Source

<details>
```yaml
name: cep_phase
description: Carrier-envelope phase [rad].
from_schema: https://w3id.org/laura/schema
rank: 1000
owner: LaserElement
domain_of:
- LaserElement
range: float
unit:
  ucum_code: rad

```
</details></div>