---
search:
  boost: 5.0
---

# Slot: max 


_Maximum value._



<div data-search-exclude markdown="1">



URI: [laura:max](https://w3id.org/laura/max)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [PIDPhaseRange](PIDPhaseRange.md) | Numeric min/max range for PID phase control |  no  |
| [PIDWeightRange](PIDWeightRange.md) | Numeric min/max range for PID phase weighting |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [Float](Float.md) |
| Domain Of | [PIDPhaseRange](PIDPhaseRange.md) |

### Cardinality and Requirements

| Property | Value |
| --- | --- |
### Slot Characteristics

| Property | Value |
| --- | --- |
| Owner | [PIDPhaseRange](PIDPhaseRange.md) |












## Identifier and Mapping Information





### Schema Source


* from schema: https://w3id.org/laura/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | laura:max |
| native | laura:max |




## LinkML Source

<details>
```yaml
name: max
description: Maximum value.
from_schema: https://w3id.org/laura/schema
rank: 1000
owner: PIDPhaseRange
domain_of:
- PIDPhaseRange
range: float

```
</details></div>