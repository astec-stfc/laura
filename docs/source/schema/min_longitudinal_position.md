---
search:
  boost: 5.0
---

# Slot: min_longitudinal_position 


_Minimum longitudinal position [m]._



<div data-search-exclude markdown="1">



URI: [laura:min_longitudinal_position](https://w3id.org/laura/min_longitudinal_position)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [PlasmaSimulationElement](PlasmaSimulationElement.md) | Simulation attributes for plasma-accelerator stages |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [Float](Float.md) |
| Domain Of | [PlasmaSimulationElement](PlasmaSimulationElement.md) |

### Cardinality and Requirements

| Property | Value |
| --- | --- |
### Slot Characteristics

| Property | Value |
| --- | --- |
| If Absent | `float(0)` |
| Owner | [PlasmaSimulationElement](PlasmaSimulationElement.md) |












## Identifier and Mapping Information





### Schema Source


* from schema: https://w3id.org/laura/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | laura:min_longitudinal_position |
| native | laura:min_longitudinal_position |




## LinkML Source

<details>
```yaml
name: min_longitudinal_position
description: Minimum longitudinal position [m].
from_schema: https://w3id.org/laura/schema
rank: 1000
ifabsent: float(0)
owner: PlasmaSimulationElement
domain_of:
- PlasmaSimulationElement
range: float

```
</details></div>