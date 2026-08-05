# Slot: io_type 


_Physical quantity this variable carries (e.g. ``voltage``, ``beam_position``), as opposed to ``control_type``, which is the shape of its value._



<div data-search-exclude markdown="1">



URI: [laura:io_type](https://w3id.org/laura/io_type)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [ControlVariable](ControlVariable.md) | A single process-variable entry mapping a logical name to a control-system PV... |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [IOTypeEnum](IOTypeEnum.md) |
| Domain Of | [ControlVariable](ControlVariable.md) |

### Cardinality and Requirements

| Property | Value |
| --- | --- |
### Slot Characteristics

| Property | Value |
| --- | --- |
| If Absent | `string(unknown)` |
| Owner | [ControlVariable](ControlVariable.md) |












## Identifier and Mapping Information





### Schema Source


* from schema: https://w3id.org/laura/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | laura:io_type |
| native | laura:io_type |




## LinkML Source

<details>
```yaml
name: io_type
description: Physical quantity this variable carries (e.g. ``voltage``, ``beam_position``),
  as opposed to ``control_type``, which is the shape of its value.
from_schema: https://w3id.org/laura/schema
rank: 1000
ifabsent: string(unknown)
owner: ControlVariable
domain_of:
- ControlVariable
range: IOTypeEnum

```
</details></div>