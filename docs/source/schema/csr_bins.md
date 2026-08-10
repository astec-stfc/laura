# Slot: csr_bins 


_Number of longitudinal bins for the CSR mesh._



<div data-search-exclude markdown="1">



URI: [laura:csr_bins](https://w3id.org/laura/csr_bins)
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
| If Absent | `int(100)` |
| Owner | [MagnetSimulationElement](MagnetSimulationElement.md) |












## Identifier and Mapping Information





### Schema Source


* from schema: https://w3id.org/laura/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | laura:csr_bins |
| native | laura:csr_bins |




## LinkML Source

<details>
```yaml
name: csr_bins
description: Number of longitudinal bins for the CSR mesh.
from_schema: https://w3id.org/laura/schema
rank: 1000
ifabsent: int(100)
owner: MagnetSimulationElement
domain_of:
- MagnetSimulationElement
range: integer

```
</details></div>