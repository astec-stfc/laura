---
search:
  boost: 5.0
---

# Slot: n_kicks 


_Number of integration kicks._



<div data-search-exclude markdown="1">



URI: [laura:n_kicks](https://w3id.org/laura/n_kicks)
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
| self | laura:n_kicks |
| native | laura:n_kicks |




## LinkML Source

<details>
```yaml
name: n_kicks
description: Number of integration kicks.
from_schema: https://w3id.org/laura/schema
rank: 1000
owner: MagnetSimulationElement
domain_of:
- MagnetSimulationElement
range: integer
minimum_value: 1

```
</details></div>