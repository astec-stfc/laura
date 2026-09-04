# Slot: angle 


_Integrated bending angle [rad]. Dipoles only._



<div data-search-exclude markdown="1">



URI: [laura:angle](https://w3id.org/laura/angle)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [MagneticElement](MagneticElement.md) | Magnetic field parameters for a beamline magnet, including multipole componen... |  no  |
| [DipoleMagnet](DipoleMagnet.md) |  |  no  |
| [QuadrupoleMagnet](QuadrupoleMagnet.md) |  |  no  |
| [SextupoleMagnet](SextupoleMagnet.md) | Sextupole magnet field, principal multipole order 2 |  no  |
| [OctupoleMagnet](OctupoleMagnet.md) | Octupole magnet field, principal multipole order 3 |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [Double](Double.md) |
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
| self | laura:angle |
| native | laura:angle |




## LinkML Source

<details>
```yaml
name: angle
description: Integrated bending angle [rad]. Dipoles only.
from_schema: https://w3id.org/laura/schema
rank: 1000
owner: MagneticElement
domain_of:
- MagneticElement
range: double
unit:
  ucum_code: rad

```
</details></div>