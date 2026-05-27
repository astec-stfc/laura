---
search:
  boost: 5.0
---

# Slot: length 


_Effective length along the beam axis [m]._



<div data-search-exclude markdown="1">



URI: [laura:length](https://w3id.org/laura/length)
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
| If Absent | `float(0)` |
| Owner | [PhysicalElement](PhysicalElement.md) |


### Value Constraints

| Property | Value |
| --- | --- |
| Minimum Value | 0 |


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
| self | laura:length |
| native | laura:length |




## LinkML Source

<details>
```yaml
name: length
description: Effective length along the beam axis [m].
from_schema: https://w3id.org/laura/schema
rank: 1000
ifabsent: float(0)
owner: PhysicalElement
domain_of:
- PhysicalElement
range: float
minimum_value: 0.0
unit:
  ucum_code: m

```
</details></div>