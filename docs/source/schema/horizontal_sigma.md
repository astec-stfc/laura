# Slot: horizontal_sigma 


_Horizontal RMS size of the opposing bunch [m]._



<div data-search-exclude markdown="1">



URI: [laura:horizontal_sigma](https://w3id.org/laura/horizontal_sigma)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [BeamBeamSimulationElement](BeamBeamSimulationElement.md) | Simulation attributes for a weak-strong beam-beam interaction |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [Double](Double.md) |
| Domain Of | [BeamBeamSimulationElement](BeamBeamSimulationElement.md) |

### Cardinality and Requirements

| Property | Value |
| --- | --- |
### Slot Characteristics

| Property | Value |
| --- | --- |
| If Absent | `float(0.0)` |
| Owner | [BeamBeamSimulationElement](BeamBeamSimulationElement.md) |


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
| self | laura:horizontal_sigma |
| native | laura:horizontal_sigma |




## LinkML Source

<details>
```yaml
name: horizontal_sigma
description: Horizontal RMS size of the opposing bunch [m].
from_schema: https://w3id.org/laura/schema
rank: 1000
ifabsent: float(0.0)
owner: BeamBeamSimulationElement
domain_of:
- BeamBeamSimulationElement
range: double
unit:
  ucum_code: m

```
</details></div>