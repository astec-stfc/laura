# Slot: degauss 


_Degaussing-cycle parameters._



<div data-search-exclude markdown="1">



URI: [laura:degauss](https://w3id.org/laura/degauss)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [Magnet](Magnet.md) | Base class for all magnetic focusing and bending elements |  no  |
| [Dipole](Dipole.md) |  |  no  |
| [Quadrupole](Quadrupole.md) |  |  no  |
| [Sextupole](Sextupole.md) | Sextupole chromaticity-correction magnet |  no  |
| [Octupole](Octupole.md) | Octupole magnet |  no  |
| [Decapole](Decapole.md) | Decapole magnet |  no  |
| [HorizontalCorrector](HorizontalCorrector.md) | Horizontal steering corrector |  no  |
| [VerticalCorrector](VerticalCorrector.md) | Vertical steering corrector |  no  |
| [CombinedCorrector](CombinedCorrector.md) | Combined horizontal/vertical steering corrector, naming the two single-plane ... |  no  |
| [Solenoid](Solenoid.md) | Solenoid focusing magnet |  no  |
| [CombinedSolenoidQuadrupole](CombinedSolenoidQuadrupole.md) | Magnet combining coaxial solenoid and quadrupole fields |  no  |
| [Wiggler](Wiggler.md) | Wiggler / undulator insertion device |  no  |
| [NonLinearLens](NonLinearLens.md) | Non-linear integrable-optics lens |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [DegaussableElement](DegaussableElement.md) |
| Domain Of | [Magnet](Magnet.md) |

### Cardinality and Requirements

| Property | Value |
| --- | --- |
### Slot Characteristics

| Property | Value |
| --- | --- |
| Owner | [Magnet](Magnet.md) |












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
owner: Magnet
domain_of:
- Magnet
range: DegaussableElement

```
</details></div>