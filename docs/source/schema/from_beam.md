---
search:
  boost: 5.0
---

# Slot: from_beam 


_Compute transform from tracked beam properties._



<div data-search-exclude markdown="1">



URI: [laura:from_beam](https://w3id.org/laura/from_beam)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [TwissMatchSimulationElement](TwissMatchSimulationElement.md) | Simulation attributes for Twiss-matching points |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [Boolean](Boolean.md) |
| Domain Of | [TwissMatchSimulationElement](TwissMatchSimulationElement.md) |

### Cardinality and Requirements

| Property | Value |
| --- | --- |
### Slot Characteristics

| Property | Value |
| --- | --- |
| If Absent | `True` |
| Owner | [TwissMatchSimulationElement](TwissMatchSimulationElement.md) |












## Identifier and Mapping Information





### Schema Source


* from schema: https://w3id.org/laura/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | laura:from_beam |
| native | laura:from_beam |




## LinkML Source

<details>
```yaml
name: from_beam
description: Compute transform from tracked beam properties.
from_schema: https://w3id.org/laura/schema
rank: 1000
ifabsent: 'True'
owner: TwissMatchSimulationElement
domain_of:
- TwissMatchSimulationElement
range: boolean

```
</details></div>