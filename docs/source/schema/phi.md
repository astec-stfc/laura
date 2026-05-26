---
search:
  boost: 5.0
---

# Slot: phi 


_Rotation about the horizontal (x) axis [rad]._



<div data-search-exclude markdown="1">



URI: [laura:phi](https://w3id.org/laura/phi)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [Rotation](Rotation.md) | Euler-angle rotation relative to the global coordinate system |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [Float](Float.md) |
| Domain Of | [Rotation](Rotation.md) |

### Cardinality and Requirements

| Property | Value |
| --- | --- |
### Slot Characteristics

| Property | Value |
| --- | --- |
| Owner | [Rotation](Rotation.md) |


### Value Constraints

| Property | Value |
| --- | --- |
| Minimum Value | -3 |
| Maximum Value | 3 |


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
| self | laura:phi |
| native | laura:phi |




## LinkML Source

<details>
```yaml
name: phi
description: Rotation about the horizontal (x) axis [rad].
from_schema: https://w3id.org/laura/schema
rank: 1000
owner: Rotation
domain_of:
- Rotation
range: float
minimum_value: -3.141592653589793
maximum_value: 3.141592653589793
unit:
  ucum_code: rad

```
</details></div>