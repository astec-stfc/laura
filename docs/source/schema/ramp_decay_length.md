---
search:
  boost: 5.0
---

# Slot: ramp_decay_length 


_Exponential decay length of the density ramp [m]._



<div data-search-exclude markdown="1">



URI: [laura:ramp_decay_length](https://w3id.org/laura/ramp_decay_length)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [PlasmaElement](PlasmaElement.md) | Plasma channel parameters for a laser-driven plasma-accelerator stage |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [Float](Float.md) |
| Domain Of | [PlasmaElement](PlasmaElement.md) |

### Cardinality and Requirements

| Property | Value |
| --- | --- |
### Slot Characteristics

| Property | Value |
| --- | --- |
| If Absent | `float(0.001)` |
| Owner | [PlasmaElement](PlasmaElement.md) |


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
| self | laura:ramp_decay_length |
| native | laura:ramp_decay_length |




## LinkML Source

<details>
```yaml
name: ramp_decay_length
description: Exponential decay length of the density ramp [m].
from_schema: https://w3id.org/laura/schema
rank: 1000
ifabsent: float(0.001)
owner: PlasmaElement
domain_of:
- PlasmaElement
range: float
minimum_value: 0.0
unit:
  ucum_code: m

```
</details></div>