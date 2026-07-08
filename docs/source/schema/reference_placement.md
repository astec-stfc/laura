---
search:
  boost: 5.0
---

# Slot: reference_placement 


_Place this element relative to another element's frame instead of using absolute world coordinates.  Mutually exclusive with ``middle``/``position``/``centre`` and ``s``._



<div data-search-exclude markdown="1">



URI: [laura:reference_placement](https://w3id.org/laura/reference_placement)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [PhysicalElement](PhysicalElement.md) | Physical placement data: position, rotation, length, and associated survey / ... |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [ReferencePlacement](ReferencePlacement.md) |
| Domain Of | [PhysicalElement](PhysicalElement.md) |

### Cardinality and Requirements

| Property | Value |
| --- | --- |
### Slot Characteristics

| Property | Value |
| --- | --- |
| Owner | [PhysicalElement](PhysicalElement.md) |








## In Subsets


* [PhysicalProperties](PhysicalProperties.md)






## Identifier and Mapping Information





### Schema Source


* from schema: https://w3id.org/laura/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | laura:reference_placement |
| native | laura:reference_placement |




## LinkML Source

<details>
```yaml
name: reference_placement
description: Place this element relative to another element's frame instead of using
  absolute world coordinates.  Mutually exclusive with ``middle``/``position``/``centre``
  and ``s``.
in_subset:
- physical_properties
from_schema: https://w3id.org/laura/schema
rank: 1000
owner: PhysicalElement
domain_of:
- PhysicalElement
range: ReferencePlacement

```
</details></div>