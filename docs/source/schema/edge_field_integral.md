# Slot: edge_field_integral 


_Enge fringe-field integral parameter (dimensionless), used as the single combined value by codes that only support one edge focussing keyword. Unset (None) by default -- rather than forcing a laura default into every output, an unset value is simply omitted from the written file so the target code's own built-in default applies. If given, it also becomes the default for any of edge_field_integral_entrance/edge_field_integral_exit that are themselves not given (see MagneticElement.resolve_edge_field_integrals)._



<div data-search-exclude markdown="1">



URI: [laura:edge_field_integral](https://w3id.org/laura/edge_field_integral)
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
| self | laura:edge_field_integral |
| native | laura:edge_field_integral |




## LinkML Source

<details>
```yaml
name: edge_field_integral
description: Enge fringe-field integral parameter (dimensionless), used as the single
  combined value by codes that only support one edge focussing keyword. Unset (None)
  by default -- rather than forcing a laura default into every output, an unset value
  is simply omitted from the written file so the target code's own built-in default
  applies. If given, it also becomes the default for any of edge_field_integral_entrance/edge_field_integral_exit
  that are themselves not given (see MagneticElement.resolve_edge_field_integrals).
from_schema: https://w3id.org/laura/schema
rank: 1000
owner: MagneticElement
domain_of:
- MagneticElement
range: float
required: false

```
</details></div>