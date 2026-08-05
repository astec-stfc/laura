# Slot: n_kicks 


_Number of integration kicks._



<div data-search-exclude markdown="1">



URI: [laura:n_kicks](https://w3id.org/laura/n_kicks)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [MagnetSimulationElement](MagnetSimulationElement.md) | Simulation attributes specific to magnets: integrator settings, fringe-field ... |  yes  |
| [RFCavitySimulationElement](RFCavitySimulationElement.md) | Simulation attributes for RF cavity elements |  yes  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [Integer](Integer.md) |
| Domain Of | [MagnetSimulationElement](MagnetSimulationElement.md), [RFCavitySimulationElement](RFCavitySimulationElement.md) |

### Cardinality and Requirements

| Property | Value |
| --- | --- |










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
domain_of:
- MagnetSimulationElement
- RFCavitySimulationElement
range: integer

```
</details></div>