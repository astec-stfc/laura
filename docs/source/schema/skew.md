---
search:
  boost: 5.0
---

# Slot: skew 

<div data-search-exclude markdown="1">



URI: [laura:skew](https://w3id.org/laura/skew)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [Multipole](Multipole.md) | Individual multipole field component, characterised by order and integrated n... |  no  |
| [MagneticElement](MagneticElement.md) | Magnetic field parameters for a beamline magnet, including multipole componen... |  no  |
| [DipoleMagnet](DipoleMagnet.md) |  |  no  |
| [QuadrupoleMagnet](QuadrupoleMagnet.md) |  |  no  |
| [SextupoleMagnet](SextupoleMagnet.md) | Sextupole magnet field, principal multipole order 2 |  no  |
| [OctupoleMagnet](OctupoleMagnet.md) | Octupole magnet field, principal multipole order 3 |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [String](String.md) |
| Domain Of | [Multipole](Multipole.md), [MagneticElement](MagneticElement.md) |

### Cardinality and Requirements

| Property | Value |
| --- | --- |










## Identifier and Mapping Information






## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | laura:skew |
| native | laura:skew |




## LinkML Source

<details>
```yaml
name: skew
domain_of:
- Multipole
- MagneticElement
range: string

```
</details></div>