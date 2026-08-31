# Slot: r_min_plasma 


_Minimum radial extension of the plasma column [m]. Non-zero gives a hollow channel, with no plasma inside this radius. Codes that assume a filled column ignore it._



<div data-search-exclude markdown="1">



URI: [laura:r_min_plasma](https://w3id.org/laura/r_min_plasma)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [PlasmaSimulationElement](PlasmaSimulationElement.md) | Simulation attributes for plasma-accelerator stages |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [Float](Float.md) |
| Domain Of | [PlasmaSimulationElement](PlasmaSimulationElement.md) |

### Cardinality and Requirements

| Property | Value |
| --- | --- |
### Slot Characteristics

| Property | Value |
| --- | --- |
| Owner | [PlasmaSimulationElement](PlasmaSimulationElement.md) |


### Value Constraints

| Property | Value |
| --- | --- |
| Minimum Value | 0 |


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
| self | laura:r_min_plasma |
| native | laura:r_min_plasma |




## LinkML Source

<details>
```yaml
name: r_min_plasma
description: Minimum radial extension of the plasma column [m]. Non-zero gives a hollow
  channel, with no plasma inside this radius. Codes that assume a filled column ignore
  it.
from_schema: https://w3id.org/laura/schema
rank: 1000
owner: PlasmaSimulationElement
domain_of:
- PlasmaSimulationElement
range: float
minimum_value: 0.0
unit:
  ucum_code: m

```
</details></div>