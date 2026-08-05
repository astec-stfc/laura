# Slot: integration_order 


_Order of the symplectic integrator._



<div data-search-exclude markdown="1">



URI: [laura:integration_order](https://w3id.org/laura/integration_order)
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












## Identifier and Mapping Information





### Schema Source


* from schema: https://w3id.org/laura/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | laura:integration_order |
| native | laura:integration_order |




## LinkML Source

<details>
```yaml
name: integration_order
description: Order of the symplectic integrator.
from_schema: https://w3id.org/laura/schema
rank: 1000
ifabsent: int(4)
owner: MagnetSimulationElement
domain_of:
- MagnetSimulationElement
range: integer

```
</details></div>