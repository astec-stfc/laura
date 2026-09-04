# Slot: section_type 


_What this section carries._



<div data-search-exclude markdown="1">



URI: [laura:section_type](https://w3id.org/laura/section_type)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [SectionLattice](SectionLattice.md) | A contiguous beamline section: an ordered run of elements |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [LatticeTypeEnum](LatticeTypeEnum.md) |
| Domain Of | [SectionLattice](SectionLattice.md) |

### Cardinality and Requirements

| Property | Value |
| --- | --- |
### Slot Characteristics

| Property | Value |
| --- | --- |
| If Absent | `string(beam)` |
| Owner | [SectionLattice](SectionLattice.md) |












## Identifier and Mapping Information





### Schema Source


* from schema: https://w3id.org/laura/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | laura:section_type |
| native | laura:section_type |




## LinkML Source

<details>
```yaml
name: section_type
description: What this section carries.
from_schema: https://w3id.org/laura/schema
rank: 1000
ifabsent: string(beam)
owner: SectionLattice
domain_of:
- SectionLattice
range: LatticeTypeEnum

```
</details></div>