---
search:
  boost: 5.0
---

# Slot: maximum 


_Maximum attenuation angle [deg]._



<div data-search-exclude markdown="1">



URI: [laura:maximum](https://w3id.org/laura/maximum)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [LaserAttenuator](LaserAttenuator.md) | Laser power attenuator (waveplate + polariser combination) |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [Float](Float.md) |
| Domain Of | [LaserAttenuator](LaserAttenuator.md) |

### Cardinality and Requirements

| Property | Value |
| --- | --- |
### Slot Characteristics

| Property | Value |
| --- | --- |
| Owner | [LaserAttenuator](LaserAttenuator.md) |


<details>
<summary>Additional Constraints</summary>
**Unit:**

| Property | Value |
| --- | --- |
| ucum_code | deg |

</details>











## Identifier and Mapping Information





### Schema Source


* from schema: https://w3id.org/laura/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | laura:maximum |
| native | laura:maximum |




## LinkML Source

<details>
```yaml
name: maximum
description: Maximum attenuation angle [deg].
from_schema: https://w3id.org/laura/schema
rank: 1000
owner: LaserAttenuator
domain_of:
- LaserAttenuator
range: float
unit:
  ucum_code: deg

```
</details></div>