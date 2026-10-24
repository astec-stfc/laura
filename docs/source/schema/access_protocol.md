# Slot: access_protocol 


_How the variable is reached, where ``protocol`` names only the control system (e.g., ``EPICS Channel Access``)._



<div data-search-exclude markdown="1">



URI: [laura:access_protocol](https://w3id.org/laura/access_protocol)
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
| self | laura:access_protocol |
| native | laura:access_protocol |
| exact | pals:access_protocol |




## LinkML Source

<details>
```yaml
name: access_protocol
description: How the variable is reached, where ``protocol`` names only the control
  system (e.g., ``EPICS Channel Access``).
from_schema: https://w3id.org/laura/schema
exact_mappings:
- pals:access_protocol
rank: 1000
owner: ControlVariable
domain_of:
- ControlVariable
range: string

```
</details></div>