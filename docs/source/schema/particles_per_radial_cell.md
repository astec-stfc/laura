# Slot: particles_per_radial_cell 


_Number of plasma particles per radial cell._



<div data-search-exclude markdown="1">



URI: [laura:particles_per_radial_cell](https://w3id.org/laura/particles_per_radial_cell)
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
| self | laura:particles_per_radial_cell |
| native | laura:particles_per_radial_cell |




## LinkML Source

<details>
```yaml
name: particles_per_radial_cell
description: Number of plasma particles per radial cell.
from_schema: https://w3id.org/laura/schema
rank: 1000
ifabsent: int(2)
owner: PlasmaSimulationElement
domain_of:
- PlasmaSimulationElement
range: integer

```
</details></div>