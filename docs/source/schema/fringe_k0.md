# Slot: fringe_k0 


_Hwang-Lee fringe-field integral K0 (dimensionless; PRAB 18, 122401, eqs. 28-34), both faces. Absent means a tanh profile's value. K2 is ``edge_field_integral``._



<div data-search-exclude markdown="1">



URI: [laura:fringe_k0](https://w3id.org/laura/fringe_k0)
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
| [CombinedSolenoidQuadrupoleMagnet](CombinedSolenoidQuadrupoleMagnet.md) | Combined solenoid and quadrupole magnetic field |  no  |






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












## Identifier and Mapping Information





### Schema Source


* from schema: https://w3id.org/laura/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | laura:fringe_k0 |
| native | laura:fringe_k0 |




## LinkML Source

<details>
```yaml
name: fringe_k0
description: Hwang-Lee fringe-field integral K0 (dimensionless; PRAB 18, 122401, eqs.
  28-34), both faces. Absent means a tanh profile's value. K2 is ``edge_field_integral``.
from_schema: https://w3id.org/laura/schema
rank: 1000
owner: MagneticElement
domain_of:
- MagneticElement
range: float
required: false

```
</details></div>