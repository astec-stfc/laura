# Slot: tilt 

<div data-search-exclude markdown="1">



URI: [laura:tilt](https://w3id.org/laura/tilt)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [ElectrostaticSeparatorSimulationElement](ElectrostaticSeparatorSimulationElement.md) | Simulation attributes for a static electrostatic separator |  no  |
| [MagneticElement](MagneticElement.md) | Magnetic field parameters for a beamline magnet, including multipole componen... |  no  |
| [DipoleMagnet](DipoleMagnet.md) |  |  no  |
| [QuadrupoleMagnet](QuadrupoleMagnet.md) |  |  no  |
| [SextupoleMagnet](SextupoleMagnet.md) | Sextupole magnet field, principal multipole order 2 |  no  |
| [OctupoleMagnet](OctupoleMagnet.md) | Octupole magnet field, principal multipole order 3 |  no  |
| [CorrectorMagnet](CorrectorMagnet.md) | Steering-corrector field, expressed as horizontal and vertical kicks rather t... |  no  |
| [CombinedSolenoidQuadrupoleMagnet](CombinedSolenoidQuadrupoleMagnet.md) | Combined solenoid and quadrupole magnetic field |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [String](String.md) |
| Domain Of | [ElectrostaticSeparatorSimulationElement](ElectrostaticSeparatorSimulationElement.md), [MagneticElement](MagneticElement.md), [CorrectorMagnet](CorrectorMagnet.md) |

### Cardinality and Requirements

| Property | Value |
| --- | --- |










## Identifier and Mapping Information






## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | laura:tilt |
| native | laura:tilt |




## LinkML Source

<details>
```yaml
name: tilt
domain_of:
- ElectrostaticSeparatorSimulationElement
- MagneticElement
- Corrector_Magnet
range: string

```
</details></div>