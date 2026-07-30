---
search:
  boost: 5.0
---

# Slot: num_periods 


_Number of full magnetic periods._



<div data-search-exclude markdown="1">



URI: [laura:num_periods](https://w3id.org/laura/num_periods)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [WigglerMagnet](WigglerMagnet.md) | Periodic wiggler/undulator field |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [Integer](Integer.md) |
| Domain Of | [WigglerMagnet](WigglerMagnet.md) |

### Cardinality and Requirements

| Property | Value |
| --- | --- |
### Slot Characteristics

| Property | Value |
| --- | --- |
| If Absent | `int(0)` |
| Owner | [WigglerMagnet](WigglerMagnet.md) |


### Value Constraints

| Property | Value |
| --- | --- |
| Minimum Value | 0 |












## Identifier and Mapping Information





### Schema Source


* from schema: https://w3id.org/laura/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | laura:num_periods |
| native | laura:num_periods |




## LinkML Source

<details>
```yaml
name: num_periods
description: Number of full magnetic periods.
from_schema: https://w3id.org/laura/schema
rank: 1000
ifabsent: int(0)
owner: Wiggler_Magnet
domain_of:
- Wiggler_Magnet
range: integer
minimum_value: 0

```
</details></div>