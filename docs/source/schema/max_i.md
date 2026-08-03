# Slot: max_i 


_Maximum current [A]._



<div data-search-exclude markdown="1">



URI: [laura:max_i](https://w3id.org/laura/max_i)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [ElectricalElement](ElectricalElement.md) | Power-supply electrical limits for a beamline element |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [Float](Float.md) |
| Domain Of | [ElectricalElement](ElectricalElement.md) |

### Cardinality and Requirements

| Property | Value |
| --- | --- |
### Slot Characteristics

| Property | Value |
| --- | --- |
| If Absent | `float(0)` |
| Owner | [ElectricalElement](ElectricalElement.md) |


<details>
<summary>Additional Constraints</summary>
**Unit:**

| Property | Value |
| --- | --- |
| ucum_code | A |

</details>








## Aliases


* maxI




## Identifier and Mapping Information





### Schema Source


* from schema: https://w3id.org/laura/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | laura:max_i |
| native | laura:max_i |




## LinkML Source

<details>
```yaml
name: max_i
description: Maximum current [A].
from_schema: https://w3id.org/laura/schema
aliases:
- maxI
rank: 1000
ifabsent: float(0)
owner: ElectricalElement
domain_of:
- ElectricalElement
range: float
unit:
  ucum_code: A

```
</details></div>