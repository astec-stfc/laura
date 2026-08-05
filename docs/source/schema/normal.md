# Slot: normal 


_Integrated normal (upright) multipole strength [T.m^{1-n}]._



<div data-search-exclude markdown="1">



URI: [laura:normal](https://w3id.org/laura/normal)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [Multipole](Multipole.md) | Individual multipole field component, characterised by order and integrated n... |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [Float](Float.md)&nbsp;or&nbsp;<br />[String](String.md) |
| Domain Of | [Multipole](Multipole.md) |

### Cardinality and Requirements

| Property | Value |
| --- | --- |
### Slot Characteristics

| Property | Value |
| --- | --- |
| If Absent | `float(0)` |
| Owner | [Multipole](Multipole.md) |


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
| self | laura:normal |
| native | laura:normal |




## LinkML Source

<details>
```yaml
name: normal
description: Integrated normal (upright) multipole strength [T.m^{1-n}].
in_subset:
- functional_parameters
from_schema: https://w3id.org/laura/schema
rank: 1000
ifabsent: float(0)
owner: Multipole
domain_of:
- Multipole
range: float
any_of:
- range: float
- range: string

```
</details></div>