# Slot: particles_per_angular_cell 


_Number of plasma particles per angular cell._



<div data-search-exclude markdown="1">



URI: [laura:particles_per_angular_cell](https://w3id.org/laura/particles_per_angular_cell)
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
| If Absent | `int(4)` |
| Owner | [PlasmaSimulationElement](PlasmaSimulationElement.md) |












## Identifier and Mapping Information





### Schema Source


* from schema: https://w3id.org/laura/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | laura:particles_per_angular_cell |
| native | laura:particles_per_angular_cell |




## LinkML Source

<details>
```yaml
name: particles_per_angular_cell
description: Number of plasma particles per angular cell.
from_schema: https://w3id.org/laura/schema
rank: 1000
ifabsent: int(4)
owner: PlasmaSimulationElement
domain_of:
- PlasmaSimulationElement
range: integer

```
</details></div>