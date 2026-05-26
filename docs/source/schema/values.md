---
search:
  boost: 5.0
---

# Slot: values 


_Sequence of peak currents applied during the degauss cycle [A]._



<div data-search-exclude markdown="1">



URI: [laura:values](https://w3id.org/laura/values)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [DegaussableElement](DegaussableElement.md) | Degaussing (demagnetisation cycle) parameters for magnets that require a fiel... |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [Float](Float.md) |
| Domain Of | [DegaussableElement](DegaussableElement.md) |

### Cardinality and Requirements

| Property | Value |
| --- | --- |
| Multivalued | Yes |
### Slot Characteristics

| Property | Value |
| --- | --- |
| Owner | [DegaussableElement](DegaussableElement.md) |


<details>
<summary>Additional Constraints</summary>
**Unit:**

| Property | Value |
| --- | --- |
| ucum_code | A |

</details>








## Aliases


* degauss_values




## Identifier and Mapping Information





### Schema Source


* from schema: https://w3id.org/laura/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | laura:values |
| native | laura:values |




## LinkML Source

<details>
```yaml
name: values
description: Sequence of peak currents applied during the degauss cycle [A].
from_schema: https://w3id.org/laura/schema
aliases:
- degauss_values
rank: 1000
owner: DegaussableElement
domain_of:
- DegaussableElement
range: float
multivalued: true
unit:
  ucum_code: A

```
</details></div>