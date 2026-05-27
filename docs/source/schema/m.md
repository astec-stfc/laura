---
search:
  boost: 5.0
---

# Slot: m 


_Linear slope of the unsaturated region._



<div data-search-exclude markdown="1">



URI: [laura:m](https://w3id.org/laura/m)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [LinearSaturationFit](LinearSaturationFit.md) | Bi-linear saturation model mapping magnet current to integrated field strengt... |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [Float](Float.md) |
| Domain Of | [LinearSaturationFit](LinearSaturationFit.md) |

### Cardinality and Requirements

| Property | Value |
| --- | --- |
### Slot Characteristics

| Property | Value |
| --- | --- |
| If Absent | `float(0)` |
| Owner | [LinearSaturationFit](LinearSaturationFit.md) |












## Identifier and Mapping Information





### Schema Source


* from schema: https://w3id.org/laura/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | laura:m |
| native | laura:m |




## LinkML Source

<details>
```yaml
name: m
description: Linear slope of the unsaturated region.
from_schema: https://w3id.org/laura/schema
rank: 1000
ifabsent: float(0)
owner: LinearSaturationFit
domain_of:
- LinearSaturationFit
range: float

```
</details></div>