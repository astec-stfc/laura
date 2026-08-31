# Slot: laser_evolution 


_Whether the driver is evolved by a laser-envelope solver as the stage is tracked, rather than held at its initial profile. Applies to codes that model the laser as an envelope; a full PIC code such as FBPIC always resolves the laser on the grid and ignores this._



<div data-search-exclude markdown="1">



URI: [laura:laser_evolution](https://w3id.org/laura/laser_evolution)
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
| self | laura:laser_evolution |
| native | laura:laser_evolution |




## LinkML Source

<details>
```yaml
name: laser_evolution
description: Whether the driver is evolved by a laser-envelope solver as the stage
  is tracked, rather than held at its initial profile. Applies to codes that model
  the laser as an envelope; a full PIC code such as FBPIC always resolves the laser
  on the grid and ignores this.
from_schema: https://w3id.org/laura/schema
rank: 1000
ifabsent: 'true'
owner: PlasmaSimulationElement
domain_of:
- PlasmaSimulationElement
range: boolean

```
</details></div>