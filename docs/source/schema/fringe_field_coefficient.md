# Slot: fringe_field_coefficient 


_Coefficient controlling the fringe-field roll-off rate._



<div data-search-exclude markdown="1">



URI: [laura:fringe_field_coefficient](https://w3id.org/laura/fringe_field_coefficient)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [MagneticElement](MagneticElement.md) | Magnetic field parameters for a beamline magnet, including multipole componen... |  no  |
| [DipoleMagnet](DipoleMagnet.md) |  |  no  |
| [QuadrupoleMagnet](QuadrupoleMagnet.md) |  |  no  |
| [SextupoleMagnet](SextupoleMagnet.md) | Sextupole magnet field, principal multipole order 2 |  no  |
| [OctupoleMagnet](OctupoleMagnet.md) | Octupole magnet field, principal multipole order 3 |  no  |
| [CorrectorMagnet](CorrectorMagnet.md) | Steering-corrector field |  no  |






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
| If Absent | `float(0.0)` |
| Owner | [MagneticElement](MagneticElement.md) |












## Identifier and Mapping Information





### Schema Source


* from schema: https://w3id.org/laura/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | laura:fringe_field_coefficient |
| native | laura:fringe_field_coefficient |




## LinkML Source

<details>
```yaml
name: fringe_field_coefficient
description: Coefficient controlling the fringe-field roll-off rate.
from_schema: https://w3id.org/laura/schema
rank: 1000
ifabsent: float(0.0)
owner: MagneticElement
domain_of:
- MagneticElement
range: float

```
</details></div>