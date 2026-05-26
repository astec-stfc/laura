---
search:
  boost: 5.0
---

# Slot: coefficients 


_Polynomial coefficients ordered from lowest to highest degree: ``FieldIntegral = sum c_n . I^n``._



<div data-search-exclude markdown="1">



URI: [laura:coefficients](https://w3id.org/laura/coefficients)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [FieldIntegral](FieldIntegral.md) | Polynomial fit of integrated field strength as a function of magnet current |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [Float](Float.md) |
| Domain Of | [FieldIntegral](FieldIntegral.md) |

### Cardinality and Requirements

| Property | Value |
| --- | --- |
| Multivalued | Yes |
### Slot Characteristics

| Property | Value |
| --- | --- |
| Owner | [FieldIntegral](FieldIntegral.md) |












## Identifier and Mapping Information





### Schema Source


* from schema: https://w3id.org/laura/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | laura:coefficients |
| native | laura:coefficients |




## LinkML Source

<details>
```yaml
name: coefficients
description: 'Polynomial coefficients ordered from lowest to highest degree: ``FieldIntegral
  = sum c_n . I^n``.'
from_schema: https://w3id.org/laura/schema
rank: 1000
owner: FieldIntegral
domain_of:
- FieldIntegral
range: float
multivalued: true

```
</details></div>