---
search:
  boost: 5.0
---

# Slot: horizontal_size 


_Full horizontal aperture [m]._



<div data-search-exclude markdown="1">



URI: [laura:horizontal_size](https://w3id.org/laura/horizontal_size)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [ApertureElement](ApertureElement.md) | Transverse aperture geometry for drift-space checks and collimators |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [Float](Float.md) |
| Domain Of | [ApertureElement](ApertureElement.md) |

### Cardinality and Requirements

| Property | Value |
| --- | --- |
### Slot Characteristics

| Property | Value |
| --- | --- |
| If Absent | `float(0.0)` |
| Owner | [ApertureElement](ApertureElement.md) |


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
| self | laura:horizontal_size |
| native | laura:horizontal_size |




## LinkML Source

<details>
```yaml
name: horizontal_size
description: Full horizontal aperture [m].
from_schema: https://w3id.org/laura/schema
rank: 1000
ifabsent: float(0.0)
owner: ApertureElement
domain_of:
- ApertureElement
range: float
minimum_value: 0.0
unit:
  ucum_code: m

```
</details></div>