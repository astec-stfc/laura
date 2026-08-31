# Slot: laser_envelope_use_phase 


_Whether the envelope solver carries an explicit phase term, which allows a coarser longitudinal grid at the cost of a more expensive step._



<div data-search-exclude markdown="1">



URI: [laura:laser_envelope_use_phase](https://w3id.org/laura/laser_envelope_use_phase)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [PlasmaSimulationElement](PlasmaSimulationElement.md) | Simulation attributes for plasma-accelerator stages |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [Boolean](Boolean.md) |
| Domain Of | [PlasmaSimulationElement](PlasmaSimulationElement.md) |

### Cardinality and Requirements

| Property | Value |
| --- | --- |
### Slot Characteristics

| Property | Value |
| --- | --- |
| If Absent | `true` |
| Owner | [PlasmaSimulationElement](PlasmaSimulationElement.md) |












## Identifier and Mapping Information





### Schema Source


* from schema: https://w3id.org/laura/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | laura:laser_envelope_use_phase |
| native | laura:laser_envelope_use_phase |




## LinkML Source

<details>
```yaml
name: laser_envelope_use_phase
description: Whether the envelope solver carries an explicit phase term, which allows
  a coarser longitudinal grid at the cost of a more expensive step.
from_schema: https://w3id.org/laura/schema
rank: 1000
ifabsent: 'true'
owner: PlasmaSimulationElement
domain_of:
- PlasmaSimulationElement
range: boolean

```
</details></div>