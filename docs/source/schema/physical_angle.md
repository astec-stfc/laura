---
search:
  boost: 5.0
---

# Slot: physical_angle 


_Bending angle in the horizontal plane [rad]. Derived from ``magnetic.angle`` when available._



<div data-search-exclude markdown="1">



URI: [laura:physical_angle](https://w3id.org/laura/physical_angle)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [PhysicalElement](PhysicalElement.md) | Physical placement data: position, rotation, length, and associated survey / ... |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [Float](Float.md) |
| Domain Of | [PhysicalElement](PhysicalElement.md) |

### Cardinality and Requirements

| Property | Value |
| --- | --- |
### Slot Characteristics

| Property | Value |
| --- | --- |
| Owner | [PhysicalElement](PhysicalElement.md) |


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
| self | laura:physical_angle |
| native | laura:physical_angle |




## LinkML Source

<details>
```yaml
name: physical_angle
description: Bending angle in the horizontal plane [rad]. Derived from ``magnetic.angle``
  when available.
from_schema: https://w3id.org/laura/schema
rank: 1000
owner: PhysicalElement
domain_of:
- PhysicalElement
range: float
unit:
  ucum_code: rad

```
</details></div>