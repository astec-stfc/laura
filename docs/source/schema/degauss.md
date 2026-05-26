---
search:
  boost: 5.0
---

# Slot: degauss 


_Degaussing-cycle parameters._



<div data-search-exclude markdown="1">



URI: [laura:degauss](https://w3id.org/laura/degauss)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [MagnetBaseElement](MagnetBaseElement.md) | Base class for all magnetic focusing and bending elements |  no  |
| [Dipole](Dipole.md) | Dipole bending magnet |  no  |
| [Quadrupole](Quadrupole.md) | Quadrupole focusing magnet |  no  |
| [Sextupole](Sextupole.md) | Sextupole chromaticity-correction magnet |  no  |
| [Octupole](Octupole.md) | Octupole magnet |  no  |
| [HorizontalCorrector](HorizontalCorrector.md) | Horizontal orbit-corrector dipole |  no  |
| [VerticalCorrector](VerticalCorrector.md) | Vertical orbit-corrector dipole |  no  |
| [CombinedCorrector](CombinedCorrector.md) | Combined horizontal and vertical orbit-corrector magnet |  no  |
| [Solenoid](Solenoid.md) | Solenoid focussing magnet |  no  |
| [NonLinearLens](NonLinearLens.md) | Non-linear focusing lens (IOTA-style) |  no  |
| [Wiggler](Wiggler.md) | Wiggler / undulator permanent-magnet array |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [DegaussableElement](DegaussableElement.md) |
| Domain Of | [MagnetBaseElement](MagnetBaseElement.md) |

### Cardinality and Requirements

| Property | Value |
| --- | --- |
### Slot Characteristics

| Property | Value |
| --- | --- |
| Owner | [MagnetBaseElement](MagnetBaseElement.md) |












## Identifier and Mapping Information





### Schema Source


* from schema: https://w3id.org/laura/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | laura:degauss |
| native | laura:degauss |




## LinkML Source

<details>
```yaml
name: degauss
description: Degaussing-cycle parameters.
from_schema: https://w3id.org/laura/schema
rank: 1000
owner: MagnetBaseElement
domain_of:
- MagnetBaseElement
range: DegaussableElement

```
</details></div>