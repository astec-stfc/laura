---
search:
  boost: 5.0
---

# Slot: bore 


_Magnet bore radius [m]._



<div data-search-exclude markdown="1">



URI: [laura:bore](https://w3id.org/laura/bore)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [MagneticElement](MagneticElement.md) | Magnetic field parameters for a beamline magnet, including multipole componen... |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [Float](Float.md) |
| Domain Of | [MagneticElement](MagneticElement.md) |

### Cardinality and Requirements

| Property | Value |
| --- | --- |
### Slot Characteristics

| Property | Value |
| --- | --- |
| If Absent | `float(0.037)` |
| Owner | [MagneticElement](MagneticElement.md) |


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
| self | laura:bore |
| native | laura:bore |




## LinkML Source

<details>
```yaml
name: bore
description: Magnet bore radius [m].
from_schema: https://w3id.org/laura/schema
rank: 1000
ifabsent: float(0.037)
owner: MagneticElement
domain_of:
- MagneticElement
range: float
minimum_value: 0.0
unit:
  ucum_code: m

```
</details></div>