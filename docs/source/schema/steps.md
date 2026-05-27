---
search:
  boost: 5.0
---

# Slot: steps 


_Number of degauss steps per half-cycle._



<div data-search-exclude markdown="1">



URI: [laura:steps](https://w3id.org/laura/steps)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [DegaussableElement](DegaussableElement.md) | Degaussing (demagnetisation cycle) parameters for magnets that require a fiel... |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [Integer](Integer.md) |
| Domain Of | [DegaussableElement](DegaussableElement.md) |

### Cardinality and Requirements

| Property | Value |
| --- | --- |
### Slot Characteristics

| Property | Value |
| --- | --- |
| If Absent | `int(11)` |
| Owner | [DegaussableElement](DegaussableElement.md) |


### Value Constraints

| Property | Value |
| --- | --- |
| Minimum Value | 1 |









## Aliases


* num_degauss_steps




## Identifier and Mapping Information





### Schema Source


* from schema: https://w3id.org/laura/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | laura:steps |
| native | laura:steps |




## LinkML Source

<details>
```yaml
name: steps
description: Number of degauss steps per half-cycle.
from_schema: https://w3id.org/laura/schema
aliases:
- num_degauss_steps
rank: 1000
ifabsent: int(11)
owner: DegaussableElement
domain_of:
- DegaussableElement
range: integer
minimum_value: 1

```
</details></div>