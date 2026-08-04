# Slot: dimensional_parameter 


_Dimensional parameter setting the transverse scale (MAD-X ``cnll``). May be a functional expression._



<div data-search-exclude markdown="1">



URI: [laura:dimensional_parameter](https://w3id.org/laura/dimensional_parameter)
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












## Identifier and Mapping Information





### Schema Source


* from schema: https://w3id.org/laura/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | laura:dimensional_parameter |
| native | laura:dimensional_parameter |




## LinkML Source

<details>
```yaml
name: dimensional_parameter
description: Dimensional parameter setting the transverse scale (MAD-X ``cnll``).
  May be a functional expression.
from_schema: https://w3id.org/laura/schema
rank: 1000
ifabsent: float(0.0)
owner: NonLinearLens_Magnet
domain_of:
- NonLinearLens_Magnet
range: float

```
</details></div>