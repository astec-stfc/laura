---
search:
  boost: 5.0
---

# Slot: laser 

<div data-search-exclude markdown="1">



URI: [laura:laser](https://w3id.org/laura/laser)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [Laser](Laser.md) | Laser system element (full laser setup including beam parameters) |  no  |
| [Plasma](Plasma.md) | Laser-driven plasma-accelerator stage |  no  |
| [LaserEnergyMeter](LaserEnergyMeter.md) | Laser pulse-energy diagnostic (photodiode / pyroelectric) |  no  |
| [LaserHalfWavePlate](LaserHalfWavePlate.md) | Half-wave plate for laser polarisation rotation |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [String](String.md) |
| Domain Of | [Laser](Laser.md), [Plasma](Plasma.md), [LaserEnergyMeter](LaserEnergyMeter.md), [LaserHalfWavePlate](LaserHalfWavePlate.md) |

### Cardinality and Requirements

| Property | Value |
| --- | --- |










## Identifier and Mapping Information






## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | laura:laser |
| native | laura:laser |




## LinkML Source

<details>
```yaml
name: laser
domain_of:
- Laser
- Plasma
- LaserEnergyMeter
- LaserHalfWavePlate
range: string

```
</details></div>