---
search:
  boost: 5.0
---

# Slot: horizontal_kick 


_Horizontal deflection [rad]. May be a functional expression._



<div data-search-exclude markdown="1">



URI: [laura:horizontal_kick](https://w3id.org/laura/horizontal_kick)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [CorrectorMagnet](CorrectorMagnet.md) | Steering-corrector field, expressed as horizontal and vertical kicks rather t... |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [Float](Float.md) |
| Domain Of | [CorrectorMagnet](CorrectorMagnet.md) |

### Cardinality and Requirements

| Property | Value |
| --- | --- |
### Slot Characteristics

| Property | Value |
| --- | --- |
| If Absent | `float(0.0)` |
| Owner | [CorrectorMagnet](CorrectorMagnet.md) |












## Identifier and Mapping Information





### Schema Source


* from schema: https://w3id.org/laura/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | laura:horizontal_kick |
| native | laura:horizontal_kick |




## LinkML Source

<details>
```yaml
name: horizontal_kick
description: Horizontal deflection [rad]. May be a functional expression.
from_schema: https://w3id.org/laura/schema
rank: 1000
ifabsent: float(0.0)
owner: Corrector_Magnet
domain_of:
- Corrector_Magnet
range: float

```
</details></div>