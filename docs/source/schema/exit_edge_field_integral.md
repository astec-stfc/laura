# Slot: exit_edge_field_integral 


_Enge fringe-field integral at the exit face. Absent means the exit face matches the entrance, which is what a lattice quoting a single integral means and what Bmad's own ``fintx`` default does, so files that set only ``edge_field_integral`` are unaffected. Set it only when the faces genuinely differ: a bend split by superposition carries the entrance fringe on its first piece and the exit fringe on its last, and collapsing the two both invents a fringe mid-magnet and drops the real one. The fringe integral enters only the vertical edge kick, so getting this wrong is invisible to every horizontal check._



<div data-search-exclude markdown="1">



URI: [laura:exit_edge_field_integral](https://w3id.org/laura/exit_edge_field_integral)
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












## Identifier and Mapping Information





### Schema Source


* from schema: https://w3id.org/laura/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | laura:exit_edge_field_integral |
| native | laura:exit_edge_field_integral |




## LinkML Source

<details>
```yaml
name: exit_edge_field_integral
description: 'Enge fringe-field integral at the exit face. Absent means the exit face
  matches the entrance, which is what a lattice quoting a single integral means and
  what Bmad''s own ``fintx`` default does, so files that set only ``edge_field_integral``
  are unaffected. Set it only when the faces genuinely differ: a bend split by superposition
  carries the entrance fringe on its first piece and the exit fringe on its last,
  and collapsing the two both invents a fringe mid-magnet and drops the real one.
  The fringe integral enters only the vertical edge kick, so getting this wrong is
  invisible to every horizontal check.'
from_schema: https://w3id.org/laura/schema
rank: 1000
owner: MagneticElement
domain_of:
- MagneticElement
range: float

```
</details></div>