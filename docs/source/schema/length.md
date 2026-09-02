# Slot: length 

<div data-search-exclude markdown="1">



URI: [laura:length](https://w3id.org/laura/length)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [PhysicalElement](PhysicalElement.md) | Physical placement data: position, rotation, length, and associated survey / ... |  no  |
| [MagneticElement](MagneticElement.md) | Magnetic field parameters for a beamline magnet, including multipole componen... |  no  |
| [DipoleMagnet](DipoleMagnet.md) |  |  no  |
| [QuadrupoleMagnet](QuadrupoleMagnet.md) |  |  no  |
| [SextupoleMagnet](SextupoleMagnet.md) | Sextupole magnet field, principal multipole order 2 |  no  |
| [OctupoleMagnet](OctupoleMagnet.md) | Octupole magnet field, principal multipole order 3 |  no  |
| [CorrectorMagnet](CorrectorMagnet.md) | Steering-corrector field |  no  |
| [SolenoidMagnet](SolenoidMagnet.md) | Solenoid field model, including systematic and random field errors and the cu... |  no  |
| [WigglerMagnet](WigglerMagnet.md) | Periodic wiggler/undulator field |  no  |
| [NonLinearLensMagnet](NonLinearLensMagnet.md) | Integrable-optics non-linear lens field |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [String](String.md) |
| Domain Of | [PhysicalElement](PhysicalElement.md), [MagneticElement](MagneticElement.md), [SolenoidMagnet](SolenoidMagnet.md), [WigglerMagnet](WigglerMagnet.md), [NonLinearLensMagnet](NonLinearLensMagnet.md) |

### Cardinality and Requirements

| Property | Value |
| --- | --- |










## Identifier and Mapping Information






## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | laura:length |
| native | laura:length |




## LinkML Source

<details>
```yaml
name: length
domain_of:
- PhysicalElement
- MagneticElement
- Solenoid_Magnet
- Wiggler_Magnet
- NonLinearLens_Magnet
range: string

```
</details></div>