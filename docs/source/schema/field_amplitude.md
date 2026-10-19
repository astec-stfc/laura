# Slot: field_amplitude 


_Field amplitude scaling._



<div data-search-exclude markdown="1">



URI: [laura:field_amplitude](https://w3id.org/laura/field_amplitude)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [MagnetSimulationElement](MagnetSimulationElement.md) | Simulation attributes specific to magnets: integrator settings, fringe-field ... |  yes  |
| [ACDipoleSimulationElement](ACDipoleSimulationElement.md) | Simulation attributes for an AC dipole / tune exciter |  yes  |
| [RFMultipoleSimulationElement](RFMultipoleSimulationElement.md) | Simulation attributes for a thin RF multipole kick |  yes  |
| [RFCavitySimulationElement](RFCavitySimulationElement.md) | Simulation attributes for RF cavity elements |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [Float](Float.md)&nbsp;or&nbsp;<br />[String](String.md) |
| Domain Of | [MagnetSimulationElement](MagnetSimulationElement.md), [RFCavitySimulationElement](RFCavitySimulationElement.md), [ACDipoleSimulationElement](ACDipoleSimulationElement.md), [RFMultipoleSimulationElement](RFMultipoleSimulationElement.md) |

### Cardinality and Requirements

| Property | Value |
| --- | --- |
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
| self | laura:field_amplitude |
| native | laura:field_amplitude |




## LinkML Source

<details>
```yaml
name: field_amplitude
description: Field amplitude scaling.
in_subset:
- functional_parameters
from_schema: https://w3id.org/laura/schema
rank: 1000
domain_of:
- MagnetSimulationElement
- RFCavitySimulationElement
- ACDipoleSimulationElement
- RFMultipoleSimulationElement
range: float
any_of:
- range: float
- range: string

```
</details></div>