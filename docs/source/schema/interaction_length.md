# Slot: interaction_length 


_Effective interaction length [m]._



<div data-search-exclude markdown="1">



URI: [laura:interaction_length](https://w3id.org/laura/interaction_length)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [WireSimulationElement](WireSimulationElement.md) | Simulation attributes for a compensating wire |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [Double](Double.md) |
| Domain Of | [WireSimulationElement](WireSimulationElement.md) |

### Cardinality and Requirements

| Property | Value |
| --- | --- |
### Slot Characteristics

| Property | Value |
| --- | --- |
| If Absent | `float(0.0)` |
| Owner | [WireSimulationElement](WireSimulationElement.md) |


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
| self | laura:interaction_length |
| native | laura:interaction_length |




## LinkML Source

<details>
```yaml
name: interaction_length
description: Effective interaction length [m].
from_schema: https://w3id.org/laura/schema
rank: 1000
ifabsent: float(0.0)
owner: WireSimulationElement
domain_of:
- WireSimulationElement
range: double
unit:
  ucum_code: m

```
</details></div>