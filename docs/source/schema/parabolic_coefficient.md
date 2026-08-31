# Slot: parabolic_coefficient 


_Parabolic coefficient of a transverse density channel [m^-^2]. The longitudinal profile is multiplied by ``1 + parabolic_coefficient * r^2``._



<div data-search-exclude markdown="1">



URI: [laura:parabolic_coefficient](https://w3id.org/laura/parabolic_coefficient)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [PlasmaElement](PlasmaElement.md) | Plasma channel parameters for a laser-driven plasma-accelerator stage |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [Float](Float.md) |
| Domain Of | [PlasmaElement](PlasmaElement.md) |

### Cardinality and Requirements

| Property | Value |
| --- | --- |
### Slot Characteristics

| Property | Value |
| --- | --- |
| If Absent | `float(0)` |
| Owner | [PlasmaElement](PlasmaElement.md) |


<details>
<summary>Additional Constraints</summary>
**Unit:**

| Property | Value |
| --- | --- |
| ucum_code | m-2 |

</details>











## Identifier and Mapping Information





### Schema Source


* from schema: https://w3id.org/laura/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | laura:parabolic_coefficient |
| native | laura:parabolic_coefficient |




## LinkML Source

<details>
```yaml
name: parabolic_coefficient
description: Parabolic coefficient of a transverse density channel [m^-^2]. The longitudinal
  profile is multiplied by ``1 + parabolic_coefficient * r^2``.
from_schema: https://w3id.org/laura/schema
rank: 1000
ifabsent: float(0)
owner: PlasmaElement
domain_of:
- PlasmaElement
range: float
unit:
  ucum_code: m-2

```
</details></div>