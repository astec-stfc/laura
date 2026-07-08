---
search:
  boost: 5.0
---

# Slot: exit_edge_angle 


_Fringe-field exit edge angle [rad]._



<div data-search-exclude markdown="1">



URI: [laura:exit_edge_angle](https://w3id.org/laura/exit_edge_angle)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [MagneticElement](MagneticElement.md) | Magnetic field parameters for a beamline magnet, including multipole componen... |  no  |
| [DipoleMagnet](DipoleMagnet.md) |  |  no  |
| [QuadrupoleMagnet](QuadrupoleMagnet.md) |  |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [String](String.md)&nbsp;or&nbsp;<br />[Float](Float.md) |
| Domain Of | [MagneticElement](MagneticElement.md) |

### Cardinality and Requirements

| Property | Value |
| --- | --- |
### Slot Characteristics

| Property | Value |
| --- | --- |
| Owner | [MagneticElement](MagneticElement.md) |


<details>
<summary>Additional Constraints</summary>
**Unit:**

| Property | Value |
| --- | --- |
| ucum_code | rad |

</details>

<details>
<summary>Expressions & Logic</summary>
#### Any Of

Value must satisfy at least one of:
- AnonymousSlotExpression({'range': 'float'})
- AnonymousSlotExpression({'range': 'string'})

</details>











## Identifier and Mapping Information





### Schema Source


* from schema: https://w3id.org/laura/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | laura:exit_edge_angle |
| native | laura:exit_edge_angle |




## LinkML Source

<details>
```yaml
name: exit_edge_angle
description: Fringe-field exit edge angle [rad].
from_schema: https://w3id.org/laura/schema
rank: 1000
owner: MagneticElement
domain_of:
- MagneticElement
range: string
unit:
  ucum_code: rad
any_of:
- range: float
- range: string

```
</details></div>