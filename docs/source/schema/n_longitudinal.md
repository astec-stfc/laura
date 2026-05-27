---
search:
  boost: 5.0
---

# Slot: n_longitudinal 


_Number of grid points in the longitudinal direction._



<div data-search-exclude markdown="1">



URI: [laura:n_longitudinal](https://w3id.org/laura/n_longitudinal)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [PlasmaSimulationElement](PlasmaSimulationElement.md) | Simulation attributes for plasma-accelerator stages |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [Integer](Integer.md) |
| Domain Of | [PlasmaSimulationElement](PlasmaSimulationElement.md) |

### Cardinality and Requirements

| Property | Value |
| --- | --- |
### Slot Characteristics

| Property | Value |
| --- | --- |
| If Absent | `int(0)` |
| Owner | [PlasmaSimulationElement](PlasmaSimulationElement.md) |












## Identifier and Mapping Information





### Schema Source


* from schema: https://w3id.org/laura/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | laura:n_longitudinal |
| native | laura:n_longitudinal |




## LinkML Source

<details>
```yaml
name: n_longitudinal
description: Number of grid points in the longitudinal direction.
from_schema: https://w3id.org/laura/schema
rank: 1000
ifabsent: int(0)
owner: PlasmaSimulationElement
domain_of:
- PlasmaSimulationElement
range: integer

```
</details></div>