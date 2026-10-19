# Slot: geometry 


_Whether the reference orbit closes on itself. Per-section rather than per-machine because a forked branch may differ from its parent._



<div data-search-exclude markdown="1">



URI: [laura:geometry](https://w3id.org/laura/geometry)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [SectionLattice](SectionLattice.md) | An ordered list of element names defining a contiguous beamline section |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [LatticeGeometryEnum](LatticeGeometryEnum.md) |
| Domain Of | [SectionLattice](SectionLattice.md) |

### Cardinality and Requirements

| Property | Value |
| --- | --- |
### Slot Characteristics

| Property | Value |
| --- | --- |
| Owner | [SectionLattice](SectionLattice.md) |












## Identifier and Mapping Information





### Schema Source


* from schema: https://w3id.org/laura/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | laura:geometry |
| native | laura:geometry |




## LinkML Source

<details>
```yaml
name: geometry
description: Whether the reference orbit closes on itself. Per-section rather than
  per-machine because a forked branch may differ from its parent.
from_schema: https://w3id.org/laura/schema
rank: 1000
owner: SectionLattice
domain_of:
- SectionLattice
range: LatticeGeometryEnum
required: false

```
</details></div>