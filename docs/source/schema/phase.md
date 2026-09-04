# Slot: phase 


_Operating phase offset [deg]._



<div data-search-exclude markdown="1">



URI: [laura:phase](https://w3id.org/laura/phase)
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
| Range | [Double](Double.md)&nbsp;or&nbsp;<br />[String](String.md) |
| Domain Of | [ACDipoleSimulationElement](ACDipoleSimulationElement.md), [RFMultipoleSimulationElement](RFMultipoleSimulationElement.md), [RFCavityElement](RFCavityElement.md), [RFDeflectingCavityElement](RFDeflectingCavityElement.md) |

### Cardinality and Requirements

| Property | Value |
| --- | --- |
### Slot Characteristics

| Property | Value |
| --- | --- |
| If Absent | `float(0.0)` |


<details>
<summary>Additional Constraints</summary>
**Unit:**

| Property | Value |
| --- | --- |
| ucum_code | deg |

</details>

<details>
<summary>Expressions & Logic</summary>
#### Any Of

Value must satisfy at least one of:
- AnonymousSlotExpression({'range': 'double'})
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
| self | laura:phase |
| native | laura:phase |




## LinkML Source

<details>
```yaml
name: phase
description: Operating phase offset [deg].
in_subset:
- functional_parameters
from_schema: https://w3id.org/laura/schema
rank: 1000
ifabsent: float(0.0)
domain_of:
- ACDipoleSimulationElement
- RFMultipoleSimulationElement
- RFCavityElement
- RFDeflectingCavityElement
range: double
unit:
  ucum_code: deg
any_of:
- range: double
- range: string

```
</details></div>