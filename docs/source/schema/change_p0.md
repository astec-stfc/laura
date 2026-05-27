---
search:
  boost: 5.0
---

# Slot: change_p0 


_Flag indicating whether the cavity changes reference momentum._



<div data-search-exclude markdown="1">



URI: [laura:change_p0](https://w3id.org/laura/change_p0)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [RFCavitySimulationElement](RFCavitySimulationElement.md) | Simulation attributes for RF cavity elements |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [Integer](Integer.md) |
| Domain Of | [RFCavitySimulationElement](RFCavitySimulationElement.md) |

### Cardinality and Requirements

| Property | Value |
| --- | --- |
### Slot Characteristics

| Property | Value |
| --- | --- |
| If Absent | `int(1)` |
| Owner | [RFCavitySimulationElement](RFCavitySimulationElement.md) |












## Identifier and Mapping Information





### Schema Source


* from schema: https://w3id.org/laura/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | laura:change_p0 |
| native | laura:change_p0 |




## LinkML Source

<details>
```yaml
name: change_p0
description: Flag indicating whether the cavity changes reference momentum.
from_schema: https://w3id.org/laura/schema
rank: 1000
ifabsent: int(1)
owner: RFCavitySimulationElement
domain_of:
- RFCavitySimulationElement
range: integer

```
</details></div>