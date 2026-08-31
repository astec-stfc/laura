# Slot: propagation_direction 


_Laser propagation direction; +1 means laser  and particles co-propagate, -1 means they counter-propagate._



<div data-search-exclude markdown="1">



URI: [laura:propagation_direction](https://w3id.org/laura/propagation_direction)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [LaserElement](LaserElement.md) | Laser-beam parameters (wavelength, pulse energy, profile, etc |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [Integer](Integer.md) |
| Domain Of | [LaserElement](LaserElement.md) |

### Cardinality and Requirements

| Property | Value |
| --- | --- |
### Slot Characteristics

| Property | Value |
| --- | --- |
| If Absent | `int(1)` |
| Owner | [LaserElement](LaserElement.md) |


### Value Constraints

| Property | Value |
| --- | --- |
| Minimum Value | -1 |
| Maximum Value | 1 |












## Identifier and Mapping Information





### Schema Source


* from schema: https://w3id.org/laura/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | laura:propagation_direction |
| native | laura:propagation_direction |




## LinkML Source

<details>
```yaml
name: propagation_direction
description: Laser propagation direction; +1 means laser  and particles co-propagate,
  -1 means they counter-propagate.
from_schema: https://w3id.org/laura/schema
rank: 1000
ifabsent: int(1)
owner: LaserElement
domain_of:
- LaserElement
range: integer
minimum_value: -1
maximum_value: 1

```
</details></div>