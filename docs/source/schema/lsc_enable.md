---
search:
  boost: 5.0
---

# Slot: lsc_enable 


_Enable LSC drift calculations._



<div data-search-exclude markdown="1">



URI: [laura:lsc_enable](https://w3id.org/laura/lsc_enable)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [DriftSimulationElement](DriftSimulationElement.md) | Simulation attributes for field-free drift sections |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [Boolean](Boolean.md) |
| Domain Of | [DriftSimulationElement](DriftSimulationElement.md) |

### Cardinality and Requirements

| Property | Value |
| --- | --- |
### Slot Characteristics

| Property | Value |
| --- | --- |
| If Absent | `True` |
| Owner | [DriftSimulationElement](DriftSimulationElement.md) |












## Identifier and Mapping Information





### Schema Source


* from schema: https://w3id.org/laura/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | laura:lsc_enable |
| native | laura:lsc_enable |




## LinkML Source

<details>
```yaml
name: lsc_enable
description: Enable LSC drift calculations.
from_schema: https://w3id.org/laura/schema
rank: 1000
ifabsent: 'True'
owner: DriftSimulationElement
domain_of:
- DriftSimulationElement
range: boolean

```
</details></div>