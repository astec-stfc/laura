---
search:
  boost: 5.0
---

# Slot: smooth_current_bins 


_Flag indicating current-bin smoothing._



<div data-search-exclude markdown="1">



URI: [laura:smooth_current_bins](https://w3id.org/laura/smooth_current_bins)
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
| self | laura:smooth_current_bins |
| native | laura:smooth_current_bins |




## LinkML Source

<details>
```yaml
name: smooth_current_bins
description: Flag indicating current-bin smoothing.
from_schema: https://w3id.org/laura/schema
rank: 1000
ifabsent: int(1)
owner: RFCavitySimulationElement
domain_of:
- RFCavitySimulationElement
range: integer

```
</details></div>