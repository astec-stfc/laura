# Slot: deltaL 


_Longitudinal step-size override for thick-lens integration [m]._



<div data-search-exclude markdown="1">



URI: [laura:deltaL](https://w3id.org/laura/deltaL)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [MagnetSimulationElement](MagnetSimulationElement.md) | Simulation attributes specific to magnets: integrator settings, fringe-field ... |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [Double](Double.md) |
| Domain Of | [MagnetSimulationElement](MagnetSimulationElement.md) |

### Cardinality and Requirements

| Property | Value |
| --- | --- |
### Slot Characteristics

| Property | Value |
| --- | --- |
| If Absent | `float(0.0)` |
| Owner | [MagnetSimulationElement](MagnetSimulationElement.md) |


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
| self | laura:deltaL |
| native | laura:deltaL |




## LinkML Source

<details>
```yaml
name: deltaL
description: Longitudinal step-size override for thick-lens integration [m].
from_schema: https://w3id.org/laura/schema
rank: 1000
ifabsent: float(0.0)
owner: MagnetSimulationElement
domain_of:
- MagnetSimulationElement
range: double
unit:
  ucum_code: m

```
</details></div>