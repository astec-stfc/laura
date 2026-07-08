---
search:
  boost: 5.0
---

# Slot: number_of_elements 


_Number of aperture sub-elements (e.g., for multi-leaf collimators)._



<div data-search-exclude markdown="1">



URI: [laura:number_of_elements](https://w3id.org/laura/number_of_elements)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [ApertureElement](ApertureElement.md) | Transverse aperture geometry for drift-space checks and collimators |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [Integer](Integer.md) |
| Domain Of | [ApertureElement](ApertureElement.md) |

### Cardinality and Requirements

| Property | Value |
| --- | --- |
### Slot Characteristics

| Property | Value |
| --- | --- |
| If Absent | `int(0)` |
| Owner | [ApertureElement](ApertureElement.md) |


### Value Constraints

| Property | Value |
| --- | --- |
| Minimum Value | 0 |












## Identifier and Mapping Information





### Schema Source


* from schema: https://w3id.org/laura/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | laura:number_of_elements |
| native | laura:number_of_elements |




## LinkML Source

<details>
```yaml
name: number_of_elements
description: Number of aperture sub-elements (e.g., for multi-leaf collimators).
from_schema: https://w3id.org/laura/schema
rank: 1000
ifabsent: int(0)
owner: ApertureElement
domain_of:
- ApertureElement
range: integer
minimum_value: 0

```
</details></div>