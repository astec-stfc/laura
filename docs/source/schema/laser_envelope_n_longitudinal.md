# Slot: laser_envelope_n_longitudinal 


_Number of longitudinal grid points for the laser-envelope solver, if it is to run on a finer grid than the wakefield. Defaults to the wakefield grid's n_longitudinal._



<div data-search-exclude markdown="1">



URI: [laura:laser_envelope_n_longitudinal](https://w3id.org/laura/laser_envelope_n_longitudinal)
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
| Owner | [PlasmaSimulationElement](PlasmaSimulationElement.md) |












## Identifier and Mapping Information





### Schema Source


* from schema: https://w3id.org/laura/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | laura:laser_envelope_n_longitudinal |
| native | laura:laser_envelope_n_longitudinal |




## LinkML Source

<details>
```yaml
name: laser_envelope_n_longitudinal
description: Number of longitudinal grid points for the laser-envelope solver, if
  it is to run on a finer grid than the wakefield. Defaults to the wakefield grid's
  n_longitudinal.
from_schema: https://w3id.org/laura/schema
rank: 1000
owner: PlasmaSimulationElement
domain_of:
- PlasmaSimulationElement
range: integer

```
</details></div>