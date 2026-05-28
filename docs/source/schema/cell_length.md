---
search:
  boost: 5.0
---

# Slot: cell_length 


_Length of a single cell [m]._



<div data-search-exclude markdown="1">



URI: [laura:cell_length](https://w3id.org/laura/cell_length)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [RFCavityElement](RFCavityElement.md) | RF cavity accelerating-structure parameters |  no  |
| [WakefieldElement](WakefieldElement.md) | Passive wakefield structure parameters |  no  |
| [RFDeflectingCavityElement](RFDeflectingCavityElement.md) | Transverse-deflecting RF cavity parameters -- a subset of RFCavityElement for... |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [Float](Float.md) |
| Domain Of | [RFCavityElement](RFCavityElement.md), [WakefieldElement](WakefieldElement.md), [RFDeflectingCavityElement](RFDeflectingCavityElement.md) |

### Cardinality and Requirements

| Property | Value |
| --- | --- |
### Slot Characteristics

| Property | Value |
| --- | --- |
| If Absent | `float(0.03333333333333333)` |


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
| self | laura:cell_length |
| native | laura:cell_length |




## LinkML Source

<details>
```yaml
name: cell_length
description: Length of a single cell [m].
from_schema: https://w3id.org/laura/schema
rank: 1000
ifabsent: float(0.03333333333333333)
domain_of:
- RFCavityElement
- WakefieldElement
- RFDeflectingCavityElement
range: float
minimum_value: 0.0
unit:
  ucum_code: m

```
</details></div>