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
| [SextupoleMagnet](SextupoleMagnet.md) | Sextupole magnet field, principal multipole order 2 |  yes  |
| [OctupoleMagnet](OctupoleMagnet.md) | Octupole magnet field, principal multipole order 3 |  yes  |
| [CorrectorMagnet](CorrectorMagnet.md) | Steering-corrector field, expressed as horizontal and vertical kicks rather t... |  no  |
| [SolenoidMagnet](SolenoidMagnet.md) | Solenoid field model, including systematic and random field errors and the cu... |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [String](String.md) |
| Domain Of | [Multipole](Multipole.md), [MagneticElement](MagneticElement.md), [CorrectorMagnet](CorrectorMagnet.md), [SolenoidMagnet](SolenoidMagnet.md) |

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
- Corrector_Magnet
- Solenoid_Magnet
range: string

```
</details></div>