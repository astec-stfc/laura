---
search:
  boost: 5.0
---

# Slot: pulse_duration_fwhm 


_Pulse duration at FWHM [s]._



<div data-search-exclude markdown="1">



URI: [laura:pulse_duration_fwhm](https://w3id.org/laura/pulse_duration_fwhm)
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


### Value Constraints

| Property | Value |
| --- | --- |
| Minimum Value | 0 |


<details>
<summary>Additional Constraints</summary>
**Unit:**

| Property | Value |
| --- | --- |
| ucum_code | s |

</details>











## Identifier and Mapping Information





### Schema Source


* from schema: https://w3id.org/laura/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | laura:pulse_duration_fwhm |
| native | laura:pulse_duration_fwhm |




## LinkML Source

<details>
```yaml
name: pulse_duration_fwhm
description: Pulse duration at FWHM [s].
from_schema: https://w3id.org/laura/schema
rank: 1000
owner: LaserElement
domain_of:
- LaserElement
range: float
minimum_value: 0.0
unit:
  ucum_code: s

```
</details></div>