# Slot: exit_gap 


_Full gap between pole faces at the exit face [m]. Absent means the same as ``gap``. See ``exit_edge_field_integral``._



<div data-search-exclude markdown="1">



URI: [laura:exit_gap](https://w3id.org/laura/exit_gap)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [MagneticElement](MagneticElement.md) | Magnetic field parameters for a beamline magnet, including multipole componen... |  no  |
| [DipoleMagnet](DipoleMagnet.md) |  |  no  |
| [QuadrupoleMagnet](QuadrupoleMagnet.md) |  |  no  |
| [SextupoleMagnet](SextupoleMagnet.md) | Sextupole magnet field, principal multipole order 2 |  no  |
| [OctupoleMagnet](OctupoleMagnet.md) | Octupole magnet field, principal multipole order 3 |  no  |
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


### Value Constraints

| Property | Value |
| --- | --- |
| Minimum Value | 0 |


<details>
<summary>Additional Constraints</summary>
**Unit:**

| Property | Value |
| --- | --- |
| ucum_code | m |

</details>











## Identifier and Mapping Information





### Schema Source


* from schema: https://w3id.org/laura/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | laura:exit_gap |
| native | laura:exit_gap |




## LinkML Source

<details>
```yaml
name: exit_gap
description: Full gap between pole faces at the exit face [m]. Absent means the same
  as ``gap``. See ``exit_edge_field_integral``.
from_schema: https://w3id.org/laura/schema
rank: 1000
owner: MagneticElement
domain_of:
- MagneticElement
range: float
minimum_value: 0.0
unit:
  ucum_code: m

```
</details></div>