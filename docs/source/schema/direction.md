# Slot: direction 


_1 if this pass traverses the section forwards, -1 if backwards. A property of the path, not of the section._



<div data-search-exclude markdown="1">



URI: [laura:direction](https://w3id.org/laura/direction)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [LayoutPass](LayoutPass.md) | One traversal of one section by one beam path |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [Integer](Integer.md) |
| Domain Of | [LayoutPass](LayoutPass.md) |

### Cardinality and Requirements

| Property | Value |
| --- | --- |
### Slot Characteristics

| Property | Value |
| --- | --- |
| If Absent | `int(1)` |
| Owner | [LayoutPass](LayoutPass.md) |












## Identifier and Mapping Information





### Schema Source


* from schema: https://w3id.org/laura/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | laura:direction |
| native | laura:direction |




## LinkML Source

<details>
```yaml
name: direction
description: 1 if this pass traverses the section forwards, -1 if backwards. A property
  of the path, not of the section.
from_schema: https://w3id.org/laura/schema
rank: 1000
ifabsent: int(1)
owner: LayoutPass
domain_of:
- LayoutPass
range: integer

```
</details></div>