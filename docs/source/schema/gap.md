---
search:
  boost: 5.0
---

# Slot: gap 


_Full gap between pole faces [m]._



<div data-search-exclude markdown="1">



URI: [laura:gap](https://w3id.org/laura/gap)
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
| If Absent | `float(0.032)` |
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
| self | laura:gap |
| native | laura:gap |




## LinkML Source

<details>
```yaml
name: gap
description: Full gap between pole faces [m].
from_schema: https://w3id.org/laura/schema
rank: 1000
ifabsent: float(0.032)
owner: MagneticElement
domain_of:
- MagneticElement
range: float
minimum_value: 0.0
unit:
  ucum_code: m

```
</details></div>