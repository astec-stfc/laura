# Slot: laguerre_polynomial_order_m 


_Azimuthal order of Laguerre-Gaussian polynomial mode (for ``profile_type = laguerre-gaussian``)._



<div data-search-exclude markdown="1">



URI: [laura:laguerre_polynomial_order_m](https://w3id.org/laura/laguerre_polynomial_order_m)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [LaserElement](LaserElement.md) | Laser-beam parameters (wavelength, pulse energy, profile, etc |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [Integer](Integer.md) |
| Domain Of | [LaserElement](LaserElement.md) |

### Cardinality and Requirements

| Property | Value |
| --- | --- |
### Slot Characteristics

| Property | Value |
| --- | --- |
| If Absent | `int(0)` |
| Owner | [LaserElement](LaserElement.md) |


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
| self | laura:laguerre_polynomial_order_m |
| native | laura:laguerre_polynomial_order_m |




## LinkML Source

<details>
```yaml
name: laguerre_polynomial_order_m
description: Azimuthal order of Laguerre-Gaussian polynomial mode (for ``profile_type
  = laguerre-gaussian``).
from_schema: https://w3id.org/laura/schema
rank: 1000
ifabsent: int(0)
owner: LaserElement
domain_of:
- LaserElement
range: integer
minimum_value: 0

```
</details></div>