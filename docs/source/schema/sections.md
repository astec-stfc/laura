---
search:
  boost: 5.0
---

# Slot: sections 

<div data-search-exclude markdown="1">



URI: [laura:sections](https://w3id.org/laura/sections)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [MachineLayout](MachineLayout.md) | An ordered list of section names defining a beamline layout (a contiguous seq... |  no  |
| [MachineModel](MachineModel.md) | Top-level container for a complete accelerator lattice: elements, sections, l... |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [String](String.md) |
| Domain Of | [MachineLayout](MachineLayout.md), [MachineModel](MachineModel.md) |

### Cardinality and Requirements

| Property | Value |
| --- | --- |










## Identifier and Mapping Information






## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | laura:sections |
| native | laura:sections |




## LinkML Source

<details>
```yaml
name: sections
domain_of:
- MachineLayout
- MachineModel
range: string

```
</details></div>