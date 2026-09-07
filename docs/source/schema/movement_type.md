# Slot: movement_type 


_How the screen is moved, e.g. ``VMOTOR``._



<div data-search-exclude markdown="1">



URI: [laura:movement_type](https://w3id.org/laura/movement_type)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [ScreenControlsInformation](ScreenControlsInformation.md) | Control interface of a screen, which also drives an actuator between named po... |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [String](String.md) |
| Domain Of | [ScreenControlsInformation](ScreenControlsInformation.md) |

### Cardinality and Requirements

| Property | Value |
| --- | --- |
### Slot Characteristics

| Property | Value |
| --- | --- |
| If Absent | `string(Unknown)` |
| Owner | [ScreenControlsInformation](ScreenControlsInformation.md) |












## Identifier and Mapping Information





### Schema Source


* from schema: https://w3id.org/laura/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | laura:movement_type |
| native | laura:movement_type |




## LinkML Source

<details>
```yaml
name: movement_type
description: How the screen is moved, e.g. ``VMOTOR``.
from_schema: https://w3id.org/laura/schema
rank: 1000
ifabsent: string(Unknown)
owner: ScreenControlsInformation
domain_of:
- ScreenControlsInformation
range: string

```
</details></div>