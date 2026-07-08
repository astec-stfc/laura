---
search:
  boost: 5.0
---

# Slot: s_point 


_Which point of the element the ``s`` value refers to: ``start``, ``middle``, or ``end``.  Defaults to ``middle``._



<div data-search-exclude markdown="1">



URI: [laura:s_point](https://w3id.org/laura/s_point)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [PhysicalElement](PhysicalElement.md) | Physical placement data: position, rotation, length, and associated survey / ... |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [String](String.md) |
| Domain Of | [PhysicalElement](PhysicalElement.md) |

### Cardinality and Requirements

| Property | Value |
| --- | --- |
### Slot Characteristics

| Property | Value |
| --- | --- |
| If Absent | `string(middle)` |
| Owner | [PhysicalElement](PhysicalElement.md) |












## Identifier and Mapping Information





### Schema Source


* from schema: https://w3id.org/laura/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | laura:s_point |
| native | laura:s_point |




## LinkML Source

<details>
```yaml
name: s_point
description: 'Which point of the element the ``s`` value refers to: ``start``, ``middle``,
  or ``end``.  Defaults to ``middle``.'
from_schema: https://w3id.org/laura/schema
rank: 1000
ifabsent: string(middle)
owner: PhysicalElement
domain_of:
- PhysicalElement
range: string

```
</details></div>