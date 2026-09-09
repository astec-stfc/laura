# Slot: frequency 


_Operating frequency [Hz]._



<div data-search-exclude markdown="1">



URI: [laura:frequency](https://w3id.org/laura/frequency)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [ACDipoleSimulationElement](ACDipoleSimulationElement.md) | Simulation attributes for an AC dipole / tune exciter |  yes  |
| [RFMultipoleSimulationElement](RFMultipoleSimulationElement.md) | Simulation attributes for a thin RF multipole kick |  yes  |
| [RFCavityElement](RFCavityElement.md) | RF cavity accelerating-structure parameters |  no  |
| [RFDeflectingCavityElement](RFDeflectingCavityElement.md) | Transverse-deflecting RF cavity parameters -- a subset of RFCavityElement for... |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [Float](Float.md) |
| Domain Of | [ACDipoleSimulationElement](ACDipoleSimulationElement.md), [RFMultipoleSimulationElement](RFMultipoleSimulationElement.md), [RFCavityElement](RFCavityElement.md), [RFDeflectingCavityElement](RFDeflectingCavityElement.md) |

### Cardinality and Requirements

| Property | Value |
| --- | --- |
### Slot Characteristics

| Property | Value |
| --- | --- |
| If Absent | `float(2998500000.0)` |


### Value Constraints

| Property | Value |
| --- | --- |
| Minimum Value | 0 |


<details>
<summary>Additional Constraints</summary>
**Unit:**

| Property | Value |
| --- | --- |
| ucum_code | Hz |

</details>











## Identifier and Mapping Information





### Schema Source


* from schema: https://w3id.org/laura/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | laura:frequency |
| native | laura:frequency |




## LinkML Source

<details>
```yaml
name: frequency
description: Operating frequency [Hz].
from_schema: https://w3id.org/laura/schema
rank: 1000
ifabsent: float(2998500000.0)
domain_of:
- ACDipoleSimulationElement
- RFMultipoleSimulationElement
- RFCavityElement
- RFDeflectingCavityElement
range: float
minimum_value: 0.0
unit:
  ucum_code: Hz

```
</details></div>