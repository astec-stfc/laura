---
search:
  boost: 5.0
---

# Slot: design_power 


_Design peak power [W]._



<div data-search-exclude markdown="1">



URI: [laura:design_power](https://w3id.org/laura/design_power)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [RFCavityElement](RFCavityElement.md) | RF cavity accelerating-structure parameters |  no  |
| [RFDeflectingCavityElement](RFDeflectingCavityElement.md) | Transverse-deflecting RF cavity parameters -- a subset of RFCavityElement for... |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [Float](Float.md) |
| Domain Of | [RFCavityElement](RFCavityElement.md), [RFDeflectingCavityElement](RFDeflectingCavityElement.md) |

### Cardinality and Requirements

| Property | Value |
| --- | --- |
### Slot Characteristics

| Property | Value |
| --- | --- |
| If Absent | `float(25000000)` |


### Value Constraints

| Property | Value |
| --- | --- |
| Minimum Value | 0 |


<details>
<summary>Additional Constraints</summary>
**Unit:**

| Property | Value |
| --- | --- |
| ucum_code | W |

</details>











## Identifier and Mapping Information





### Schema Source


* from schema: https://w3id.org/laura/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | laura:design_power |
| native | laura:design_power |




## LinkML Source

<details>
```yaml
name: design_power
description: Design peak power [W].
from_schema: https://w3id.org/laura/schema
rank: 1000
ifabsent: float(25000000)
domain_of:
- RFCavityElement
- RFDeflectingCavityElement
range: float
minimum_value: 0.0
unit:
  ucum_code: W

```
</details></div>