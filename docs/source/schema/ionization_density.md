# Slot: ionization_density 


_Number density of the ionizable species [m^-^3], counting atoms rather than electrons. Defaults to density. A dopant is typically a small fraction of the background._



<div data-search-exclude markdown="1">



URI: [laura:ionization_density](https://w3id.org/laura/ionization_density)
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
| Owner | [PlasmaElement](PlasmaElement.md) |


### Value Constraints

| Property | Value |
| --- | --- |
| Minimum Value | 0 |


<details>
<summary>Additional Constraints</summary>
**Unit:**

| Property | Value |
| --- | --- |
| ucum_code | m-3 |

</details>











## Identifier and Mapping Information





### Schema Source


* from schema: https://w3id.org/laura/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | laura:ionization_density |
| native | laura:ionization_density |




## LinkML Source

<details>
```yaml
name: ionization_density
description: Number density of the ionizable species [m^-^3], counting atoms rather
  than electrons. Defaults to density. A dopant is typically a small fraction of the
  background.
from_schema: https://w3id.org/laura/schema
rank: 1000
owner: PlasmaElement
domain_of:
- PlasmaElement
range: float
minimum_value: 0.0
unit:
  ucum_code: m-3

```
</details></div>