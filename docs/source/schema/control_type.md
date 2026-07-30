---
search:
  boost: 5.0
---

# Slot: control_type 


_Kind of quantity this variable carries. Accepted in YAML as ``type``._



<div data-search-exclude markdown="1">



URI: [laura:control_type](https://w3id.org/laura/control_type)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [ControlVariable](ControlVariable.md) | A single process-variable entry mapping a logical name to a control-system PV... |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [ControlTypeEnum](ControlTypeEnum.md) |
| Domain Of | [ControlVariable](ControlVariable.md) |

### Cardinality and Requirements

| Property | Value |
| --- | --- |
### Slot Characteristics

| Property | Value |
| --- | --- |
| If Absent | `string(statistical)` |
| Owner | [ControlVariable](ControlVariable.md) |









## Aliases


* type




## Identifier and Mapping Information





### Schema Source


* from schema: https://w3id.org/laura/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | laura:control_type |
| native | laura:control_type |




## LinkML Source

<details>
```yaml
name: control_type
description: Kind of quantity this variable carries. Accepted in YAML as ``type``.
from_schema: https://w3id.org/laura/schema
aliases:
- type
rank: 1000
ifabsent: string(statistical)
owner: ControlVariable
domain_of:
- ControlVariable
range: ControlTypeEnum

```
</details></div>