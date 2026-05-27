---
search:
  boost: 5.0
---

# Slot: use_maximum_values 


_If True, use maximum mask radius constraints._



<div data-search-exclude markdown="1">



URI: [laura:use_maximum_values](https://w3id.org/laura/use_maximum_values)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [CameraMask](CameraMask.md) | Camera analysis mask parameters |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [Boolean](Boolean.md) |
| Domain Of | [CameraMask](CameraMask.md) |

### Cardinality and Requirements

| Property | Value |
| --- | --- |
### Slot Characteristics

| Property | Value |
| --- | --- |
| If Absent | `True` |
| Owner | [CameraMask](CameraMask.md) |









## Aliases


* USE_MASK_RAD_LIMITS




## Identifier and Mapping Information





### Schema Source


* from schema: https://w3id.org/laura/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | laura:use_maximum_values |
| native | laura:use_maximum_values |




## LinkML Source

<details>
```yaml
name: use_maximum_values
description: If True, use maximum mask radius constraints.
from_schema: https://w3id.org/laura/schema
aliases:
- USE_MASK_RAD_LIMITS
rank: 1000
ifabsent: 'True'
owner: CameraMask
domain_of:
- CameraMask
range: boolean

```
</details></div>