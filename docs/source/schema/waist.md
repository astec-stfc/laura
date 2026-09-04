# Slot: waist 


_Laser beam waist (1/e^2 radius) [m]._



<div data-search-exclude markdown="1">



URI: [laura:waist](https://w3id.org/laura/waist)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [LaserElement](LaserElement.md) | Laser-beam parameters (wavelength, pulse energy, profile, etc |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [Double](Double.md) |
| Domain Of | [LaserElement](LaserElement.md) |

### Cardinality and Requirements

| Property | Value |
| --- | --- |
### Slot Characteristics

| Property | Value |
| --- | --- |
| If Absent | `float(0)` |
| Owner | [LaserElement](LaserElement.md) |


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
| self | laura:waist |
| native | laura:waist |




## LinkML Source

<details>
```yaml
name: waist
description: Laser beam waist (1/e^2 radius) [m].
from_schema: https://w3id.org/laura/schema
rank: 1000
ifabsent: float(0)
owner: LaserElement
domain_of:
- LaserElement
range: double
minimum_value: 0.0
unit:
  ucum_code: m

```
</details></div>