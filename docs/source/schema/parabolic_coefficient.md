---
search:
  boost: 5.0
---

# Slot: parabolic_coefficient 


_Parabolic coefficient for a transverse density profile._



<div data-search-exclude markdown="1">



URI: [laura:parabolic_coefficient](https://w3id.org/laura/parabolic_coefficient)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [PlasmaElement](PlasmaElement.md) | Plasma channel parameters for a laser-driven plasma-accelerator stage |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [Float](Float.md) |
| Domain Of | [PlasmaElement](PlasmaElement.md) |

### Cardinality and Requirements

| Property | Value |
| --- | --- |
### Slot Characteristics

| Property | Value |
| --- | --- |
| If Absent | `float(0)` |
| Owner | [PlasmaElement](PlasmaElement.md) |












## Identifier and Mapping Information





### Schema Source


* from schema: https://w3id.org/laura/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | laura:parabolic_coefficient |
| native | laura:parabolic_coefficient |




## LinkML Source

<details>
```yaml
name: parabolic_coefficient
description: Parabolic coefficient for a transverse density profile.
from_schema: https://w3id.org/laura/schema
rank: 1000
ifabsent: float(0)
owner: PlasmaElement
domain_of:
- PlasmaElement
range: float

```
</details></div>