# Slot: read_tolerance 


_Read-back vs. set-point tolerance fraction (default 0.1 = 10 %)._



<div data-search-exclude markdown="1">



URI: [laura:read_tolerance](https://w3id.org/laura/read_tolerance)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [ElectricalElement](ElectricalElement.md) | Power-supply electrical limits for a beamline element |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [Double](Double.md) |
| Domain Of | [ElectricalElement](ElectricalElement.md) |

### Cardinality and Requirements

| Property | Value |
| --- | --- |
### Slot Characteristics

| Property | Value |
| --- | --- |
| If Absent | `float(0.1)` |
| Owner | [ElectricalElement](ElectricalElement.md) |









## Aliases


* ri_tolerance




## Identifier and Mapping Information





### Schema Source


* from schema: https://w3id.org/laura/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | laura:read_tolerance |
| native | laura:read_tolerance |




## LinkML Source

<details>
```yaml
name: read_tolerance
description: Read-back vs. set-point tolerance fraction (default 0.1 = 10 %).
from_schema: https://w3id.org/laura/schema
aliases:
- ri_tolerance
rank: 1000
ifabsent: float(0.1)
owner: ElectricalElement
domain_of:
- ElectricalElement
range: double

```
</details></div>