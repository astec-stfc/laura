---
search:
  boost: 5.0
---

# Slot: field_integral_coefficients 

<div data-search-exclude markdown="1">



URI: [laura:field_integral_coefficients](https://w3id.org/laura/field_integral_coefficients)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [MagneticElement](MagneticElement.md) | Magnetic field parameters for a beamline magnet, including multipole componen... |  no  |
| [DipoleMagnet](DipoleMagnet.md) |  |  no  |
| [QuadrupoleMagnet](QuadrupoleMagnet.md) |  |  no  |
| [SextupoleMagnet](SextupoleMagnet.md) | Sextupole magnet field, principal multipole order 2 |  no  |
| [OctupoleMagnet](OctupoleMagnet.md) | Octupole magnet field, principal multipole order 3 |  no  |
| [SolenoidMagnet](SolenoidMagnet.md) | Solenoid field model, including systematic and random field errors and the cu... |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [String](String.md) |
| Domain Of | [MagneticElement](MagneticElement.md), [SolenoidMagnet](SolenoidMagnet.md) |

### Cardinality and Requirements

| Property | Value |
| --- | --- |










## Identifier and Mapping Information






## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | laura:field_integral_coefficients |
| native | laura:field_integral_coefficients |




## LinkML Source

<details>
```yaml
name: field_integral_coefficients
domain_of:
- MagneticElement
- Solenoid_Magnet
range: string

```
</details></div>