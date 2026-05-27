---
search:
  boost: 5.0
---

# Slot: edge_order 


_Polynomial order of the edge-field expansion._



<div data-search-exclude markdown="1">



URI: [laura:edge_order](https://w3id.org/laura/edge_order)
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
| If Absent | `int(2)` |
| Owner | [MagnetSimulationElement](MagnetSimulationElement.md) |












## Identifier and Mapping Information





### Schema Source


* from schema: https://w3id.org/laura/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | laura:edge_order |
| native | laura:edge_order |




## LinkML Source

<details>
```yaml
name: edge_order
description: Polynomial order of the edge-field expansion.
from_schema: https://w3id.org/laura/schema
rank: 1000
ifabsent: int(2)
owner: MagnetSimulationElement
domain_of:
- MagnetSimulationElement
range: integer

```
</details></div>