---
search:
  boost: 5.0
---

# Slot: focal_position 


_Focal (waist) position along the propagation axis [m]._



<div data-search-exclude markdown="1">



URI: [laura:focal_position](https://w3id.org/laura/focal_position)
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
| self | laura:focal_position |
| native | laura:focal_position |




## LinkML Source

<details>
```yaml
name: focal_position
description: Focal (waist) position along the propagation axis [m].
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