# Slot: density_profile_start 


_Longitudinal position at which the density profile begins [m]. ramp_up, plateau and ramp_down are measured from here, and the density is zero upstream of it._



<div data-search-exclude markdown="1">



URI: [laura:density_profile_start](https://w3id.org/laura/density_profile_start)
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
| ucum_code | m |

</details>











## Identifier and Mapping Information





### Schema Source


* from schema: https://w3id.org/laura/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | laura:density_profile_start |
| native | laura:density_profile_start |




## LinkML Source

<details>
```yaml
name: density_profile_start
description: Longitudinal position at which the density profile begins [m]. ramp_up,
  plateau and ramp_down are measured from here, and the density is zero upstream of
  it.
from_schema: https://w3id.org/laura/schema
rank: 1000
ifabsent: float(0)
owner: PlasmaElement
domain_of:
- PlasmaElement
range: float
unit:
  ucum_code: m

```
</details></div>