# Slot: ionization_initial_level 


_Ionization level the atoms start at; 0 for a neutral atom. Starting part-way up avoids spending macroparticles on levels the driver ionizes far ahead of the wake, as with the first five levels of nitrogen._



<div data-search-exclude markdown="1">



URI: [laura:ionization_initial_level](https://w3id.org/laura/ionization_initial_level)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [PlasmaElement](PlasmaElement.md) | Plasma channel parameters for a laser-driven plasma-accelerator stage |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [Integer](Integer.md) |
| Domain Of | [PlasmaElement](PlasmaElement.md) |

### Cardinality and Requirements

| Property | Value |
| --- | --- |
### Slot Characteristics

| Property | Value |
| --- | --- |
| If Absent | `int(0)` |
| Owner | [PlasmaElement](PlasmaElement.md) |


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
| self | laura:ionization_initial_level |
| native | laura:ionization_initial_level |




## LinkML Source

<details>
```yaml
name: ionization_initial_level
description: Ionization level the atoms start at; 0 for a neutral atom. Starting part-way
  up avoids spending macroparticles on levels the driver ionizes far ahead of the
  wake, as with the first five levels of nitrogen.
from_schema: https://w3id.org/laura/schema
rank: 1000
ifabsent: int(0)
owner: PlasmaElement
domain_of:
- PlasmaElement
range: integer
minimum_value: 0

```
</details></div>