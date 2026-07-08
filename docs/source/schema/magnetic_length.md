---
search:
  boost: 5.0
---

# Slot: magnetic_length 


_Magnetic (effective) length [m]._



<div data-search-exclude markdown="1">



URI: [laura:magnetic_length](https://w3id.org/laura/magnetic_length)
Alias: length

<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [MagneticElement](MagneticElement.md) | Magnetic field parameters for a beamline magnet, including multipole componen... |  no  |
| [DipoleMagnet](DipoleMagnet.md) |  |  no  |
| [QuadrupoleMagnet](QuadrupoleMagnet.md) |  |  no  |






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
| If Absent | `float(0)` |
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
| self | laura:magnetic_length |
| native | laura:magnetic_length |




## LinkML Source

<details>
```yaml
name: magnetic_length
description: Magnetic (effective) length [m].
from_schema: https://w3id.org/laura/schema
rank: 1000
ifabsent: float(0)
alias: length
owner: MagneticElement
domain_of:
- MagneticElement
range: float
minimum_value: 0.0
unit:
  ucum_code: m

```
</details></div>