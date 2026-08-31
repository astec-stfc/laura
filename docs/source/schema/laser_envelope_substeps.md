# Slot: laser_envelope_substeps 


_Number of envelope-solver steps taken per wakefield step. Raise it where the envelope evolves faster than the wake it drives._



<div data-search-exclude markdown="1">



URI: [laura:laser_envelope_substeps](https://w3id.org/laura/laser_envelope_substeps)
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
| If Absent | `int(1)` |
| Owner | [PlasmaSimulationElement](PlasmaSimulationElement.md) |












## Identifier and Mapping Information





### Schema Source


* from schema: https://w3id.org/laura/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | laura:laser_envelope_substeps |
| native | laura:laser_envelope_substeps |




## LinkML Source

<details>
```yaml
name: laser_envelope_substeps
description: Number of envelope-solver steps taken per wakefield step. Raise it where
  the envelope evolves faster than the wake it drives.
from_schema: https://w3id.org/laura/schema
rank: 1000
ifabsent: int(1)
owner: PlasmaSimulationElement
domain_of:
- PlasmaSimulationElement
range: integer

```
</details></div>