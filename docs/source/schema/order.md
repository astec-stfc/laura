---
search:
  boost: 5.0
---

# Slot: order 

<div data-search-exclude markdown="1">



URI: [laura:order](https://w3id.org/laura/order)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [Multipole](Multipole.md) | Individual multipole field component, characterised by order and integrated n... |  no  |
| [MagneticElement](MagneticElement.md) | Magnetic field parameters for a beamline magnet, including multipole componen... |  no  |
| [DipoleMagnet](DipoleMagnet.md) |  |  yes  |
| [QuadrupoleMagnet](QuadrupoleMagnet.md) |  |  yes  |






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
| self | laura:order |
| native | laura:order |




## LinkML Source

<details>
```yaml
name: order
domain_of:
- Multipole
- MagneticElement
range: string

```
</details></div>