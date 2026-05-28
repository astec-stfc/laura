---
search:
  boost: 5.0
---

# Slot: crest 


_On-crest phase offset providing maximum energy gain [deg]._



<div data-search-exclude markdown="1">



URI: [laura:crest](https://w3id.org/laura/crest)
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
| If Absent | `float(0)` |


<details>
<summary>Additional Constraints</summary>
**Unit:**

| Property | Value |
| --- | --- |
| ucum_code | deg |

</details>











## Identifier and Mapping Information





### Schema Source


* from schema: https://w3id.org/laura/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | laura:crest |
| native | laura:crest |




## LinkML Source

<details>
```yaml
name: crest
description: On-crest phase offset providing maximum energy gain [deg].
from_schema: https://w3id.org/laura/schema
rank: 1000
ifabsent: float(0)
domain_of:
- RFCavityElement
- RFDeflectingCavityElement
range: float
unit:
  ucum_code: deg

```
</details></div>