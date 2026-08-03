# Slot: read_only 


_Whether the variable is read-only._



<div data-search-exclude markdown="1">



URI: [laura:read_only](https://w3id.org/laura/read_only)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [ControlVariable](ControlVariable.md) | A single process-variable entry mapping a logical name to a control-system PV... |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [Boolean](Boolean.md) |
| Domain Of | [ControlVariable](ControlVariable.md) |

### Cardinality and Requirements

| Property | Value |
| --- | --- |
### Slot Characteristics

| Property | Value |
| --- | --- |
| If Absent | `True` |
| Owner | [ControlVariable](ControlVariable.md) |












## Identifier and Mapping Information





### Schema Source


* from schema: https://w3id.org/laura/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | laura:read_only |
| native | laura:read_only |




## LinkML Source

<details>
```yaml
name: read_only
description: Whether the variable is read-only.
from_schema: https://w3id.org/laura/schema
rank: 1000
ifabsent: 'True'
owner: ControlVariable
domain_of:
- ControlVariable
range: boolean

```
</details></div>