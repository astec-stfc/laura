---
search:
  boost: 5.0
---

# Slot: initial_position 


_Initial longitudinal position of the laser pulse [m]._



<div data-search-exclude markdown="1">



URI: [laura:initial_position](https://w3id.org/laura/initial_position)
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
| ucum_code | m |

</details>











## Identifier and Mapping Information





### Schema Source


* from schema: https://w3id.org/laura/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | laura:initial_position |
| native | laura:initial_position |




## LinkML Source

<details>
```yaml
name: initial_position
description: Initial longitudinal position of the laser pulse [m].
from_schema: https://w3id.org/laura/schema
rank: 1000
owner: LaserElement
domain_of:
- LaserElement
range: float
unit:
  ucum_code: m

```
</details></div>