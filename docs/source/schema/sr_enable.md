---
search:
  boost: 5.0
---

# Slot: sr_enable 


_Enable synchrotron-radiation energy loss._



<div data-search-exclude markdown="1">



URI: [laura:sr_enable](https://w3id.org/laura/sr_enable)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [MagnetSimulationElement](MagnetSimulationElement.md) | Simulation attributes specific to magnets: integrator settings, fringe-field ... |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [Boolean](Boolean.md) |
| Domain Of | [MagnetSimulationElement](MagnetSimulationElement.md) |

### Cardinality and Requirements

| Property | Value |
| --- | --- |
### Slot Characteristics

| Property | Value |
| --- | --- |
| If Absent | `True` |
| Owner | [MagnetSimulationElement](MagnetSimulationElement.md) |












## Identifier and Mapping Information





### Schema Source


* from schema: https://w3id.org/laura/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | laura:sr_enable |
| native | laura:sr_enable |




## LinkML Source

<details>
```yaml
name: sr_enable
description: Enable synchrotron-radiation energy loss.
from_schema: https://w3id.org/laura/schema
rank: 1000
ifabsent: 'True'
owner: MagnetSimulationElement
domain_of:
- MagnetSimulationElement
range: boolean

```
</details></div>