# Slot: angle 


_Integrated bending angle [rad]. Dipoles only. Part of the data model (lattice YAML may set it), but derived from multipoles.K0L rather than stored: the MagneticElement wrapper implements it as a read/write property so a symbolic bend angle survives round-tripping and reads follow the global resolution mode. Listed in _PYDANTIC_EXCLUDED_SLOTS in generate_pydantic.py so the generated base does not also declare it as a field, which would make pydantic treat the property object as the field default._



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
description: 'Integrated bending angle [rad]. Dipoles only. Part of the data model
  (lattice YAML may set it), but derived from multipoles.K0L rather than stored: the
  MagneticElement wrapper implements it as a read/write property so a symbolic bend
  angle survives round-tripping and reads follow the global resolution mode. Listed
  in _PYDANTIC_EXCLUDED_SLOTS in generate_pydantic.py so the generated base does not
  also declare it as a field, which would make pydantic treat the property object
  as the field default.'
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