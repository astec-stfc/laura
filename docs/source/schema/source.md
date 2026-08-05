# Slot: source 


_Whether these values are design, measured or simulated. Defaults to ``design``, which is what an untagged lattice file has always been._



<div data-search-exclude markdown="1">



URI: [laura:source](https://w3id.org/laura/source)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [MachineModel](MachineModel.md) | Top-level container for a complete accelerator lattice: elements, sections, l... |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [LatticeSourceEnum](LatticeSourceEnum.md) |
| Domain Of | [MachineModel](MachineModel.md) |

### Cardinality and Requirements

| Property | Value |
| --- | --- |
### Slot Characteristics

| Property | Value |
| --- | --- |
| If Absent | `string(design)` |
| Owner | [MachineModel](MachineModel.md) |












## Identifier and Mapping Information





### Schema Source


* from schema: https://w3id.org/laura/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | laura:source |
| native | laura:source |




## LinkML Source

<details>
```yaml
name: source
description: Whether these values are design, measured or simulated. Defaults to ``design``,
  which is what an untagged lattice file has always been.
from_schema: https://w3id.org/laura/schema
rank: 1000
ifabsent: string(design)
owner: MachineModel
domain_of:
- MachineModel
range: LatticeSourceEnum

```
</details></div>