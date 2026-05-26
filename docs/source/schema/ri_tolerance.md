---
search:
  boost: 5.0
---

# Slot: ri_tolerance 


_Read-back vs. set-point tolerance fraction (default 0.1 = 10 %)._



<div data-search-exclude markdown="1">



URI: [laura:ri_tolerance](https://w3id.org/laura/ri_tolerance)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [ElectricalElement](ElectricalElement.md) | Power-supply electrical limits for a beamline element |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [Float](Float.md) |
| Domain Of | [ElectricalElement](ElectricalElement.md) |

### Cardinality and Requirements

| Property | Value |
| --- | --- |
### Slot Characteristics

| Property | Value |
| --- | --- |
| Owner | [ElectricalElement](ElectricalElement.md) |









## Aliases


* read_tolerance




## Identifier and Mapping Information





### Schema Source


* from schema: https://w3id.org/laura/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | laura:ri_tolerance |
| native | laura:ri_tolerance |




## LinkML Source

<details>
```yaml
name: ri_tolerance
description: Read-back vs. set-point tolerance fraction (default 0.1 = 10 %).
from_schema: https://w3id.org/laura/schema
aliases:
- read_tolerance
rank: 1000
owner: ElectricalElement
domain_of:
- ElectricalElement
range: float

```
</details></div>