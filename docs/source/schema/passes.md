# Slot: passes 


_The beam order, one entry per section traversal. Distinct from sections, which is keyed by name and so cannot express a section entered twice._



<div data-search-exclude markdown="1">



URI: [laura:passes](https://w3id.org/laura/passes)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [MachineLayout](MachineLayout.md) | An ordered list of section names defining a beamline layout (a contiguous seq... |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [LayoutPass](LayoutPass.md) |
| Domain Of | [MachineLayout](MachineLayout.md) |

### Cardinality and Requirements

| Property | Value |
| --- | --- |
| Multivalued | Yes |
### Slot Characteristics

| Property | Value |
| --- | --- |
| Owner | [MachineLayout](MachineLayout.md) |












## Identifier and Mapping Information





### Schema Source


* from schema: https://w3id.org/laura/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | laura:passes |
| native | laura:passes |




## LinkML Source

<details>
```yaml
name: passes
description: The beam order, one entry per section traversal. Distinct from sections,
  which is keyed by name and so cannot express a section entered twice.
from_schema: https://w3id.org/laura/schema
rank: 1000
owner: MachineLayout
domain_of:
- MachineLayout
range: LayoutPass
multivalued: true

```
</details></div>