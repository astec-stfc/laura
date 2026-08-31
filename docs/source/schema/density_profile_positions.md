# Slot: density_profile_positions 


_Longitudinal positions [m] of a tabulated density profile, used when density_profile_type is ``tabulated``._



<div data-search-exclude markdown="1">



URI: [laura:density_profile_positions](https://w3id.org/laura/density_profile_positions)
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
| Multivalued | Yes |
### Slot Characteristics

| Property | Value |
| --- | --- |
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
| self | laura:density_profile_positions |
| native | laura:density_profile_positions |




## LinkML Source

<details>
```yaml
name: density_profile_positions
description: Longitudinal positions [m] of a tabulated density profile, used when
  density_profile_type is ``tabulated``.
from_schema: https://w3id.org/laura/schema
rank: 1000
owner: PlasmaElement
domain_of:
- PlasmaElement
range: float
multivalued: true
unit:
  ucum_code: m

```
</details></div>