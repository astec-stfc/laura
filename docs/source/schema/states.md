---
search:
  boost: 5.0
---

# Slot: states 


_Mapping of state name to underlying control-system value, for ``control_type: state``._



<div data-search-exclude markdown="1">



URI: [laura:states](https://w3id.org/laura/states)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [ControlVariable](ControlVariable.md) | A single process-variable entry mapping a logical name to a control-system PV... |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [String](String.md) |
| Domain Of | [ControlVariable](ControlVariable.md) |

### Cardinality and Requirements

| Property | Value |
| --- | --- |
### Slot Characteristics

| Property | Value |
| --- | --- |
| Owner | [ControlVariable](ControlVariable.md) |












## Identifier and Mapping Information





### Schema Source


* from schema: https://w3id.org/laura/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | laura:states |
| native | laura:states |




## LinkML Source

<details>
```yaml
name: states
description: 'Mapping of state name to underlying control-system value, for ``control_type:
  state``.'
from_schema: https://w3id.org/laura/schema
rank: 1000
owner: ControlVariable
domain_of:
- ControlVariable
range: string

```
</details></div>