# Slot: current 


_Current carried by the wire [A]._



<div data-search-exclude markdown="1">



URI: [laura:current](https://w3id.org/laura/current)
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
| ucum_code | A |

</details>











## Identifier and Mapping Information





### Schema Source


* from schema: https://w3id.org/laura/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | laura:current |
| native | laura:current |




## LinkML Source

<details>
```yaml
name: current
description: Current carried by the wire [A].
from_schema: https://w3id.org/laura/schema
rank: 1000
ifabsent: float(0.0)
owner: WireSimulationElement
domain_of:
- WireSimulationElement
range: double
unit:
  ucum_code: A

```
</details></div>