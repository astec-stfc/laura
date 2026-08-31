# Slot: ionizable 


_Whether a further, ionizable species is present alongside the plasma defined above, with electrons freed from it by the driver field as the stage is tracked. This is what makes ionization injection possible; the plasma above is then the pre-ionized background, and may have zero density if the whole gas is to be ionized by the driver. Only PIC codes that model ionization use it._



<div data-search-exclude markdown="1">



URI: [laura:ionizable](https://w3id.org/laura/ionizable)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [PlasmaElement](PlasmaElement.md) | Plasma channel parameters for a laser-driven plasma-accelerator stage |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [Boolean](Boolean.md) |
| Domain Of | [PlasmaElement](PlasmaElement.md) |

### Cardinality and Requirements

| Property | Value |
| --- | --- |
### Slot Characteristics

| Property | Value |
| --- | --- |
| If Absent | `False` |
| Owner | [PlasmaElement](PlasmaElement.md) |












## Identifier and Mapping Information





### Schema Source


* from schema: https://w3id.org/laura/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | laura:ionizable |
| native | laura:ionizable |




## LinkML Source

<details>
```yaml
name: ionizable
description: Whether a further, ionizable species is present alongside the plasma
  defined above, with electrons freed from it by the driver field as the stage is
  tracked. This is what makes ionization injection possible; the plasma above is then
  the pre-ionized background, and may have zero density if the whole gas is to be
  ionized by the driver. Only PIC codes that model ionization use it.
from_schema: https://w3id.org/laura/schema
rank: 1000
ifabsent: 'False'
owner: PlasmaElement
domain_of:
- PlasmaElement
range: boolean

```
</details></div>