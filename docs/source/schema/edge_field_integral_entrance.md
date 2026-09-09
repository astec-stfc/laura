# Slot: edge_field_integral_entrance 


_Fringe-field integral for entrance-edge focussing._



<div data-search-exclude markdown="1">



URI: [laura:edge_field_integral_entrance](https://w3id.org/laura/edge_field_integral_entrance)
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
| Range | [Float](Float.md) |
| Domain Of | [MagneticElement](MagneticElement.md) |

### Cardinality and Requirements

| Property | Value |
| --- | --- |
### Slot Characteristics

| Property | Value |
| --- | --- |
| If Absent | `float(0.5)` |
| Owner | [MagneticElement](MagneticElement.md) |












## Identifier and Mapping Information





### Schema Source


* from schema: https://w3id.org/laura/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | laura:edge_field_integral_entrance |
| native | laura:edge_field_integral_entrance |




## LinkML Source

<details>
```yaml
name: edge_field_integral_entrance
description: Fringe-field integral for entrance-edge focussing.
from_schema: https://w3id.org/laura/schema
rank: 1000
ifabsent: float(0.5)
owner: MagneticElement
domain_of:
- MagneticElement
range: float

```
</details></div>