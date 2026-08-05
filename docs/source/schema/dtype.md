# Slot: dtype 


_Data type, held as a Python type and serialised by name (e.g., ``float``, ``int``, ``str``)._



<div data-search-exclude markdown="1">



URI: [laura:dtype](https://w3id.org/laura/dtype)
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
| If Absent | `string(float)` |
| Owner | [ControlVariable](ControlVariable.md) |












## Identifier and Mapping Information





### Schema Source


* from schema: https://w3id.org/laura/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | laura:dtype |
| native | laura:dtype |




## LinkML Source

<details>
```yaml
name: dtype
description: Data type, held as a Python type and serialised by name (e.g., ``float``,
  ``int``, ``str``).
from_schema: https://w3id.org/laura/schema
rank: 1000
ifabsent: string(float)
owner: ControlVariable
domain_of:
- ControlVariable
range: string

```
</details></div>