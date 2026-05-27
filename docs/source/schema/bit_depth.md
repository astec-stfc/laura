---
search:
  boost: 5.0
---

# Slot: bit_depth 


_Camera bit depth._



<div data-search-exclude markdown="1">



URI: [laura:bit_depth](https://w3id.org/laura/bit_depth)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [CameraSensor](CameraSensor.md) | Camera sensor hardware configuration |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [Integer](Integer.md) |
| Domain Of | [CameraSensor](CameraSensor.md) |

### Cardinality and Requirements

| Property | Value |
| --- | --- |
### Slot Characteristics

| Property | Value |
| --- | --- |
| If Absent | `int(16)` |
| Owner | [CameraSensor](CameraSensor.md) |












## Identifier and Mapping Information





### Schema Source


* from schema: https://w3id.org/laura/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | laura:bit_depth |
| native | laura:bit_depth |




## LinkML Source

<details>
```yaml
name: bit_depth
description: Camera bit depth.
from_schema: https://w3id.org/laura/schema
rank: 1000
ifabsent: int(16)
owner: CameraSensor
domain_of:
- CameraSensor
range: integer

```
</details></div>