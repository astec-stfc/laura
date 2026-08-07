# Slot: plane 


_Principal bending / focusing plane (``Horizontal``, ``Vertical``, or ``Combined``)._



<div data-search-exclude markdown="1">



URI: [laura:plane](https://w3id.org/laura/plane)
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
| Range | [BendingPlaneEnum](BendingPlaneEnum.md) |
| Domain Of | [MagneticElement](MagneticElement.md) |

### Cardinality and Requirements

| Property | Value |
| --- | --- |
### Slot Characteristics

| Property | Value |
| --- | --- |
| If Absent | `string(Horizontal)` |
| Owner | [MagneticElement](MagneticElement.md) |












## Identifier and Mapping Information





### Schema Source


* from schema: https://w3id.org/laura/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | laura:plane |
| native | laura:plane |




## LinkML Source

<details>
```yaml
name: plane
description: Principal bending / focusing plane (``Horizontal``, ``Vertical``, or
  ``Combined``).
from_schema: https://w3id.org/laura/schema
rank: 1000
ifabsent: string(Horizontal)
owner: MagneticElement
domain_of:
- MagneticElement
range: BendingPlaneEnum

```
</details></div>