# Slot: integrated_strength 


_Integrated lens strength (MAD-X ``knll``). May be a functional expression._



<div data-search-exclude markdown="1">



URI: [laura:integrated_strength](https://w3id.org/laura/integrated_strength)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [NonLinearLensMagnet](NonLinearLensMagnet.md) | Integrable-optics non-linear lens field |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [Float](Float.md) |
| Domain Of | [NonLinearLensMagnet](NonLinearLensMagnet.md) |

### Cardinality and Requirements

| Property | Value |
| --- | --- |
### Slot Characteristics

| Property | Value |
| --- | --- |
| If Absent | `float(0.0)` |
| Owner | [NonLinearLensMagnet](NonLinearLensMagnet.md) |


### Value Constraints

| Property | Value |
| --- | --- |
| Minimum Value | 0 |












## Identifier and Mapping Information





### Schema Source


* from schema: https://w3id.org/laura/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | laura:integrated_strength |
| native | laura:integrated_strength |




## LinkML Source

<details>
```yaml
name: integrated_strength
description: Integrated lens strength (MAD-X ``knll``). May be a functional expression.
from_schema: https://w3id.org/laura/schema
rank: 1000
ifabsent: float(0.0)
owner: NonLinearLens_Magnet
domain_of:
- NonLinearLens_Magnet
range: float
minimum_value: 0

```
</details></div>