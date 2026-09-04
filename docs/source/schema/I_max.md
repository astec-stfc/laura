# Slot: I_max 


_Current at which saturation begins [A]._



<div data-search-exclude markdown="1">



URI: [laura:I_max](https://w3id.org/laura/I_max)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [LinearSaturationFit](LinearSaturationFit.md) | Bi-linear saturation model mapping magnet current to integrated field strengt... |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [Double](Double.md) |
| Domain Of | [LinearSaturationFit](LinearSaturationFit.md) |

### Cardinality and Requirements

| Property | Value |
| --- | --- |
### Slot Characteristics

| Property | Value |
| --- | --- |
| If Absent | `float(0)` |
| Owner | [LinearSaturationFit](LinearSaturationFit.md) |


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
| self | laura:I_max |
| native | laura:I_max |




## LinkML Source

<details>
```yaml
name: I_max
description: Current at which saturation begins [A].
from_schema: https://w3id.org/laura/schema
rank: 1000
ifabsent: float(0)
owner: LinearSaturationFit
domain_of:
- LinearSaturationFit
range: double
unit:
  ucum_code: A

```
</details></div>