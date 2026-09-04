# Slot: s 


_Arc-length position [m] along the design trajectory (s=0 at the global origin along +Z).  Alternative to absolute world coordinates (``middle``/``position``/``centre``) and ``reference_placement``. Converted to {x,y,z} by LAURA during lattice assembly._



<div data-search-exclude markdown="1">



URI: [laura:s](https://w3id.org/laura/s)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [PhysicalElement](PhysicalElement.md) | Physical placement data: position, rotation, length, and associated survey / ... |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [Double](Double.md) |
| Domain Of | [PhysicalElement](PhysicalElement.md) |

### Cardinality and Requirements

| Property | Value |
| --- | --- |
### Slot Characteristics

| Property | Value |
| --- | --- |
| Owner | [PhysicalElement](PhysicalElement.md) |


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
| self | laura:s |
| native | laura:s |




## LinkML Source

<details>
```yaml
name: s
description: Arc-length position [m] along the design trajectory (s=0 at the global
  origin along +Z).  Alternative to absolute world coordinates (``middle``/``position``/``centre``)
  and ``reference_placement``. Converted to {x,y,z} by LAURA during lattice assembly.
from_schema: https://w3id.org/laura/schema
rank: 1000
owner: PhysicalElement
domain_of:
- PhysicalElement
range: double
unit:
  ucum_code: m

```
</details></div>