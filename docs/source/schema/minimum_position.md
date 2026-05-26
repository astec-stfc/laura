---
search:
  boost: 5.0
---

# Slot: minimum_position 


_Minimum upstream s-coordinate [m]._



<div data-search-exclude markdown="1">



URI: [laura:minimum_position](https://w3id.org/laura/minimum_position)
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
| ucum_code | m |

</details>











## Identifier and Mapping Information





### Schema Source


* from schema: https://w3id.org/laura/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | laura:minimum_position |
| native | laura:minimum_position |




## LinkML Source

<details>
```yaml
name: minimum_position
description: Minimum upstream s-coordinate [m].
from_schema: https://w3id.org/laura/schema
rank: 1000
owner: PhysicalElement
domain_of:
- PhysicalElement
range: float
unit:
  ucum_code: m

```
</details></div>