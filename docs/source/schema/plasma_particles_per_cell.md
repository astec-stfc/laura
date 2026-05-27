---
search:
  boost: 5.0
---

# Slot: plasma_particles_per_cell 


_Number of plasma particles per cell._



<div data-search-exclude markdown="1">



URI: [laura:plasma_particles_per_cell](https://w3id.org/laura/plasma_particles_per_cell)
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
| If Absent | `int(2)` |
| Owner | [PlasmaSimulationElement](PlasmaSimulationElement.md) |












## Identifier and Mapping Information





### Schema Source


* from schema: https://w3id.org/laura/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | laura:plasma_particles_per_cell |
| native | laura:plasma_particles_per_cell |




## LinkML Source

<details>
```yaml
name: plasma_particles_per_cell
description: Number of plasma particles per cell.
from_schema: https://w3id.org/laura/schema
rank: 1000
ifabsent: int(2)
owner: PlasmaSimulationElement
domain_of:
- PlasmaSimulationElement
range: integer

```
</details></div>