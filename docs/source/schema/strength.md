---
search:
  boost: 5.0
---

# Slot: strength 


_Deflection parameter K. May be a functional expression._



<div data-search-exclude markdown="1">



URI: [laura:strength](https://w3id.org/laura/strength)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [WigglerMagnet](WigglerMagnet.md) | Periodic wiggler/undulator field |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [Float](Float.md) |
| Domain Of | [WigglerMagnet](WigglerMagnet.md) |

### Cardinality and Requirements

| Property | Value |
| --- | --- |
### Slot Characteristics

| Property | Value |
| --- | --- |
| If Absent | `float(0.0)` |
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
| self | laura:strength |
| native | laura:strength |




## LinkML Source

<details>
```yaml
name: strength
description: Deflection parameter K. May be a functional expression.
from_schema: https://w3id.org/laura/schema
rank: 1000
ifabsent: float(0.0)
owner: Wiggler_Magnet
domain_of:
- Wiggler_Magnet
range: float
minimum_value: 0

```
</details></div>