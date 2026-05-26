---
search:
  boost: 5.0
---

# Slot: tilt 


_Global tilt about the beam axis [rad]._



<div data-search-exclude markdown="1">



URI: [laura:tilt](https://w3id.org/laura/tilt)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [MagneticElement](MagneticElement.md) | Magnetic field parameters for a beamline magnet, including multipole componen... |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [Float](Float.md) |
| Domain Of | [MagneticElement](MagneticElement.md) |

### Cardinality and Requirements

| Property | Value |
| --- | --- |
### Slot Characteristics

| Property | Value |
| --- | --- |
| Owner | [MagneticElement](MagneticElement.md) |


<details>
<summary>Additional Constraints</summary>
**Unit:**

| Property | Value |
| --- | --- |
| ucum_code | rad |

</details>











## Identifier and Mapping Information





### Schema Source


* from schema: https://w3id.org/laura/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | laura:tilt |
| native | laura:tilt |




## LinkML Source

<details>
```yaml
name: tilt
description: Global tilt about the beam axis [rad].
from_schema: https://w3id.org/laura/schema
rank: 1000
owner: MagneticElement
domain_of:
- MagneticElement
range: float
unit:
  ucum_code: rad

```
</details></div>