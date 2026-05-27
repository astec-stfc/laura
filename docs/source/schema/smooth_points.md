---
search:
  boost: 5.0
---

# Slot: smooth_points 


_Number of points used to smooth the field map [ASTRA]._



<div data-search-exclude markdown="1">



URI: [laura:smooth_points](https://w3id.org/laura/smooth_points)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [MagnetSimulationElement](MagnetSimulationElement.md) | Simulation attributes specific to magnets: integrator settings, fringe-field ... |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [Float](Float.md) |
| Domain Of | [MagnetSimulationElement](MagnetSimulationElement.md) |

### Cardinality and Requirements

| Property | Value |
| --- | --- |
### Slot Characteristics

| Property | Value |
| --- | --- |
| If Absent | `float(2)` |
| Owner | [MagnetSimulationElement](MagnetSimulationElement.md) |












## Identifier and Mapping Information





### Schema Source


* from schema: https://w3id.org/laura/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | laura:smooth_points |
| native | laura:smooth_points |




## LinkML Source

<details>
```yaml
name: smooth_points
description: Number of points used to smooth the field map [ASTRA].
from_schema: https://w3id.org/laura/schema
rank: 1000
ifabsent: float(2)
owner: MagnetSimulationElement
domain_of:
- MagnetSimulationElement
range: float

```
</details></div>