---
search:
  boost: 5.0
---

# Slot: point 


_Which point on the reference element to use as the origin frame: 'start', 'middle', or 'end'._



<div data-search-exclude markdown="1">



URI: [laura:point](https://w3id.org/laura/point)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [ReferencePlacement](ReferencePlacement.md) | Positions an element relative to a named reference element's local frame |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [String](String.md) |
| Domain Of | [ReferencePlacement](ReferencePlacement.md) |

### Cardinality and Requirements

| Property | Value |
| --- | --- |
### Slot Characteristics

| Property | Value |
| --- | --- |
| If Absent | `string(end)` |
| Owner | [ReferencePlacement](ReferencePlacement.md) |












## Identifier and Mapping Information





### Schema Source


* from schema: https://w3id.org/laura/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | laura:point |
| native | laura:point |




## LinkML Source

<details>
```yaml
name: point
description: 'Which point on the reference element to use as the origin frame: ''start'',
  ''middle'', or ''end''.'
from_schema: https://w3id.org/laura/schema
rank: 1000
ifabsent: string(end)
owner: ReferencePlacement
domain_of:
- ReferencePlacement
range: string

```
</details></div>