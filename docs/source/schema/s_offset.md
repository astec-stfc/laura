# Slot: s_offset 


_Scalar offset [m] along the local beam direction (s-axis) from the reference point.  Equivalent to ``offset: [0, 0, s_offset]`` but expressed as a single number.  Mutually exclusive with ``offset`` and ``world_offset``._



<div data-search-exclude markdown="1">



URI: [laura:s_offset](https://w3id.org/laura/s_offset)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [ReferencePlacement](ReferencePlacement.md) | Positions an element relative to a named reference element's local frame |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [Float](Float.md) |
| Domain Of | [ReferencePlacement](ReferencePlacement.md) |

### Cardinality and Requirements

| Property | Value |
| --- | --- |
### Slot Characteristics

| Property | Value |
| --- | --- |
| Owner | [ReferencePlacement](ReferencePlacement.md) |


<details>
<summary>Additional Constraints</summary>
**Unit:**

| Property | Value |
| --- | --- |
| ucum_code | m |

</details>











## Identifier and Mapping Information





### Schema Source


* from schema: https://w3id.org/laura/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | laura:s_offset |
| native | laura:s_offset |




## LinkML Source

<details>
```yaml
name: s_offset
description: 'Scalar offset [m] along the local beam direction (s-axis) from the reference
  point.  Equivalent to ``offset: [0, 0, s_offset]`` but expressed as a single number.  Mutually
  exclusive with ``offset`` and ``world_offset``.'
from_schema: https://w3id.org/laura/schema
rank: 1000
owner: ReferencePlacement
domain_of:
- ReferencePlacement
range: float
unit:
  ucum_code: m

```
</details></div>