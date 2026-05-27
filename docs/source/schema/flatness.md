---
search:
  boost: 5.0
---

# Slot: flatness 


_Flatness order N of a flattened-Gaussian profile (for ``profile_type = flattened-gaussian``)._



<div data-search-exclude markdown="1">



URI: [laura:flatness](https://w3id.org/laura/flatness)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [LaserElement](LaserElement.md) | Laser-beam parameters (wavelength, pulse energy, profile, etc |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [Integer](Integer.md) |
| Domain Of | [LaserElement](LaserElement.md) |

### Cardinality and Requirements

| Property | Value |
| --- | --- |
### Slot Characteristics

| Property | Value |
| --- | --- |
| If Absent | `int(6)` |
| Owner | [LaserElement](LaserElement.md) |


### Value Constraints

| Property | Value |
| --- | --- |
| Minimum Value | 1 |












## Identifier and Mapping Information





### Schema Source


* from schema: https://w3id.org/laura/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | laura:flatness |
| native | laura:flatness |




## LinkML Source

<details>
```yaml
name: flatness
description: Flatness order N of a flattened-Gaussian profile (for ``profile_type
  = flattened-gaussian``).
from_schema: https://w3id.org/laura/schema
rank: 1000
ifabsent: int(6)
owner: LaserElement
domain_of:
- LaserElement
range: integer
minimum_value: 1

```
</details></div>