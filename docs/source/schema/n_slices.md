# Slot: n_slices 


_Number of longitudinal slices for thick-lens tracking._



<div data-search-exclude markdown="1">



URI: [laura:n_slices](https://w3id.org/laura/n_slices)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [MagnetSimulationElement](MagnetSimulationElement.md) | Simulation attributes specific to magnets: integrator settings, fringe-field ... |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [Integer](Integer.md) |
| Domain Of | [MagnetSimulationElement](MagnetSimulationElement.md) |

### Cardinality and Requirements

| Property | Value |
| --- | --- |
### Slot Characteristics

| Property | Value |
| --- | --- |
| If Absent | `int(4)` |
| Owner | [MagnetSimulationElement](MagnetSimulationElement.md) |


### Value Constraints

| Property | Value |
| --- | --- |
| Minimum Value | 1 |












## Identifier and Mapping Information





### Schema Source


* from schema: https://w3id.org/laura/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | laura:n_slices |
| native | laura:n_slices |




## LinkML Source

<details>
```yaml
name: n_slices
description: Number of longitudinal slices for thick-lens tracking.
from_schema: https://w3id.org/laura/schema
rank: 1000
ifabsent: int(4)
owner: MagnetSimulationElement
domain_of:
- MagnetSimulationElement
range: integer
minimum_value: 1

```
</details></div>