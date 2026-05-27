---
search:
  boost: 5.0
---

# Slot: dt_bunch 


_Time-step control for bunch evolution (or 'auto')._



<div data-search-exclude markdown="1">



URI: [laura:dt_bunch](https://w3id.org/laura/dt_bunch)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [PlasmaSimulationElement](PlasmaSimulationElement.md) | Simulation attributes for plasma-accelerator stages |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [String](String.md) |
| Domain Of | [PlasmaSimulationElement](PlasmaSimulationElement.md) |

### Cardinality and Requirements

| Property | Value |
| --- | --- |
### Slot Characteristics

| Property | Value |
| --- | --- |
| If Absent | `string(auto)` |
| Owner | [PlasmaSimulationElement](PlasmaSimulationElement.md) |












## Identifier and Mapping Information





### Schema Source


* from schema: https://w3id.org/laura/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | laura:dt_bunch |
| native | laura:dt_bunch |




## LinkML Source

<details>
```yaml
name: dt_bunch
description: Time-step control for bunch evolution (or 'auto').
from_schema: https://w3id.org/laura/schema
rank: 1000
ifabsent: string(auto)
owner: PlasmaSimulationElement
domain_of:
- PlasmaSimulationElement
range: string

```
</details></div>