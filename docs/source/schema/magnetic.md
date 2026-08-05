# Slot: magnetic 


_Magnetic field parameters._



<div data-search-exclude markdown="1">



URI: [laura:magnetic](https://w3id.org/laura/magnetic)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [Magnet](Magnet.md) | Base class for all magnetic focusing and bending elements |  no  |
| [Dipole](Dipole.md) |  |  yes  |
| [Quadrupole](Quadrupole.md) |  |  yes  |
| [Sextupole](Sextupole.md) | Sextupole chromaticity-correction magnet |  yes  |
| [Octupole](Octupole.md) | Octupole magnet |  yes  |
| [HorizontalCorrector](HorizontalCorrector.md) | Horizontal steering corrector |  yes  |
| [VerticalCorrector](VerticalCorrector.md) | Vertical steering corrector |  yes  |
| [CombinedCorrector](CombinedCorrector.md) | Combined horizontal/vertical steering corrector, naming the two single-plane ... |  yes  |
| [Solenoid](Solenoid.md) | Solenoid focusing magnet |  yes  |
| [Wiggler](Wiggler.md) | Wiggler / undulator insertion device |  yes  |
| [NonLinearLens](NonLinearLens.md) | Non-linear integrable-optics lens |  yes  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [MagneticElement](MagneticElement.md) |
| Domain Of | [Magnet](Magnet.md) |

### Cardinality and Requirements

| Property | Value |
| --- | --- |
### Slot Characteristics

| Property | Value |
| --- | --- |
| Owner | [Magnet](Magnet.md) |








## In Subsets


* [MagneticProperties](MagneticProperties.md)






## Identifier and Mapping Information





### Schema Source


* from schema: https://w3id.org/laura/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | laura:magnetic |
| native | laura:magnetic |




## LinkML Source

<details>
```yaml
name: magnetic
description: Magnetic field parameters.
in_subset:
- magnetic_properties
from_schema: https://w3id.org/laura/schema
rank: 1000
owner: Magnet
domain_of:
- Magnet
range: MagneticElement

```
</details></div>