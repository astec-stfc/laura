---
search:
  boost: 5.0
---

# Slot: master_lattice 

<div data-search-exclude markdown="1">



URI: [laura:master_lattice](https://w3id.org/laura/master_lattice)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [SectionLattice](SectionLattice.md) | An ordered list of element names defining a contiguous beamline section |  no  |
| [MachineLayout](MachineLayout.md) | An ordered list of section names defining a beamline layout (a contiguous seq... |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [String](String.md) |
| Domain Of | [SectionLattice](SectionLattice.md), [MachineLayout](MachineLayout.md) |

### Cardinality and Requirements

| Property | Value |
| --- | --- |










## Identifier and Mapping Information






## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | laura:master_lattice |
| native | laura:master_lattice |




## LinkML Source

<details>
```yaml
name: master_lattice
domain_of:
- SectionLattice
- MachineLayout
range: string

```
</details></div>