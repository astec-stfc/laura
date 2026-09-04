# Slot: vertical_size 


_Full vertical aperture [m]._



<div data-search-exclude markdown="1">



URI: [laura:vertical_size](https://w3id.org/laura/vertical_size)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [ApertureElement](ApertureElement.md) | Transverse aperture geometry for drift-space checks and collimators |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [Double](Double.md) |
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
| self | laura:vertical_size |
| native | laura:vertical_size |




## LinkML Source

<details>
```yaml
name: vertical_size
description: Full vertical aperture [m].
from_schema: https://w3id.org/laura/schema
rank: 1000
ifabsent: float(0.0)
owner: ApertureElement
domain_of:
- ApertureElement
range: double
minimum_value: 0.0
unit:
  ucum_code: m

```
</details></div>