# Slot: horizontal_kick 


_Horizontal deflection [rad]. May be a functional expression. Derived from multipoles.K0L.normal._



<div data-search-exclude markdown="1">



URI: [laura:horizontal_kick](https://w3id.org/laura/horizontal_kick)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [CorrectorMagnet](CorrectorMagnet.md) | Steering-corrector field |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [Float](Float.md)&nbsp;or&nbsp;<br />[String](String.md) |
| Domain Of | [CorrectorMagnet](CorrectorMagnet.md) |

### Cardinality and Requirements

| Property | Value |
| --- | --- |
### Slot Characteristics

| Property | Value |
| --- | --- |
| If Absent | `float(0.0)` |
| Owner | [CorrectorMagnet](CorrectorMagnet.md) |


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







## In Subsets


* [FunctionalParameters](FunctionalParameters.md)






## Identifier and Mapping Information





### Schema Source


* from schema: https://w3id.org/laura/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | laura:horizontal_kick |
| native | laura:horizontal_kick |




## LinkML Source

<details>
```yaml
name: horizontal_kick
description: Horizontal deflection [rad]. May be a functional expression. Derived
  from multipoles.K0L.normal.
in_subset:
- functional_parameters
from_schema: https://w3id.org/laura/schema
rank: 1000
ifabsent: float(0.0)
owner: Corrector_Magnet
domain_of:
- Corrector_Magnet
range: float
unit:
  ucum_code: rad
any_of:
- range: float
- range: string

```
</details></div>