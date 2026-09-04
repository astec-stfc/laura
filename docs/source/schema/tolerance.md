# Slot: tolerance 


_Current tolerance band during the degauss cycle [A]._



<div data-search-exclude markdown="1">



URI: [laura:tolerance](https://w3id.org/laura/tolerance)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [DegaussableElement](DegaussableElement.md) | Degaussing (demagnetisation cycle) parameters for magnets that require a fiel... |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [Double](Double.md) |
| Domain Of | [DegaussableElement](DegaussableElement.md) |

### Cardinality and Requirements

| Property | Value |
| --- | --- |
### Slot Characteristics

| Property | Value |
| --- | --- |
| If Absent | `float(0.5)` |
| Owner | [DegaussableElement](DegaussableElement.md) |


<details>
<summary>Additional Constraints</summary>
**Unit:**

| Property | Value |
| --- | --- |
| ucum_code | A |

</details>








## Aliases


* degauss_tolerance




## Identifier and Mapping Information





### Schema Source


* from schema: https://w3id.org/laura/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | laura:tolerance |
| native | laura:tolerance |




## LinkML Source

<details>
```yaml
name: tolerance
description: Current tolerance band during the degauss cycle [A].
from_schema: https://w3id.org/laura/schema
aliases:
- degauss_tolerance
rank: 1000
ifabsent: float(0.5)
owner: DegaussableElement
domain_of:
- DegaussableElement
range: double
unit:
  ucum_code: A

```
</details></div>