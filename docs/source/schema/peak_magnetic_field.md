---
search:
  boost: 5.0
---

# Slot: peak_magnetic_field 


_Peak on-axis field [T]._



<div data-search-exclude markdown="1">



URI: [laura:peak_magnetic_field](https://w3id.org/laura/peak_magnetic_field)
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












## Identifier and Mapping Information





### Schema Source


* from schema: https://w3id.org/laura/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | laura:peak_magnetic_field |
| native | laura:peak_magnetic_field |




## LinkML Source

<details>
```yaml
name: peak_magnetic_field
description: Peak on-axis field [T].
from_schema: https://w3id.org/laura/schema
rank: 1000
ifabsent: float(0.0)
owner: Wiggler_Magnet
domain_of:
- Wiggler_Magnet
range: float

```
</details></div>