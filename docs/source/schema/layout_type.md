# Slot: layout_type 


_What this layout carries._



<div data-search-exclude markdown="1">



URI: [laura:layout_type](https://w3id.org/laura/layout_type)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [MachineLayout](MachineLayout.md) | A beamline layout: a contiguous sequence of sections |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [LatticeTypeEnum](LatticeTypeEnum.md) |
| Domain Of | [MachineLayout](MachineLayout.md) |

### Cardinality and Requirements

| Property | Value |
| --- | --- |
### Slot Characteristics

| Property | Value |
| --- | --- |
| If Absent | `string(beam)` |
| Owner | [MachineLayout](MachineLayout.md) |












## Identifier and Mapping Information





### Schema Source


* from schema: https://w3id.org/laura/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | laura:layout_type |
| native | laura:layout_type |




## LinkML Source

<details>
```yaml
name: layout_type
description: What this layout carries.
from_schema: https://w3id.org/laura/schema
rank: 1000
ifabsent: string(beam)
owner: MachineLayout
domain_of:
- MachineLayout
range: LatticeTypeEnum

```
</details></div>