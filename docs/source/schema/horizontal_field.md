# Slot: horizontal_field 


_Horizontal deflecting electric field [V/m]._



<div data-search-exclude markdown="1">



URI: [laura:horizontal_field](https://w3id.org/laura/horizontal_field)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [ElectrostaticSeparatorSimulationElement](ElectrostaticSeparatorSimulationElement.md) | Simulation attributes for a static electrostatic separator |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [Float](Float.md)&nbsp;or&nbsp;<br />[String](String.md) |
| Domain Of | [ElectrostaticSeparatorSimulationElement](ElectrostaticSeparatorSimulationElement.md) |

### Cardinality and Requirements

| Property | Value |
| --- | --- |
### Slot Characteristics

| Property | Value |
| --- | --- |
| If Absent | `float(0.0)` |
| Owner | [ElectrostaticSeparatorSimulationElement](ElectrostaticSeparatorSimulationElement.md) |


<details>
<summary>Additional Constraints</summary>
**Unit:**

| Property | Value |
| --- | --- |
| ucum_code | V/m |

</details>

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
| self | laura:horizontal_field |
| native | laura:horizontal_field |




## LinkML Source

<details>
```yaml
name: horizontal_field
description: Horizontal deflecting electric field [V/m].
in_subset:
- functional_parameters
from_schema: https://w3id.org/laura/schema
rank: 1000
ifabsent: float(0.0)
owner: ElectrostaticSeparatorSimulationElement
domain_of:
- ElectrostaticSeparatorSimulationElement
range: float
unit:
  ucum_code: V/m
any_of:
- range: float
- range: string

```
</details></div>