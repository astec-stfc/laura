# Slot: protocol 


_How the variable is reached (e.g., ``CA``, ``PVA``); NARAD's ``access_protocol`` spells these out (``EPICS Channel Access``)._



<div data-search-exclude markdown="1">



URI: [laura:protocol](https://w3id.org/laura/protocol)
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
| self | laura:protocol |
| native | laura:protocol |
| close | pals:access_protocol |




## LinkML Source

<details>
```yaml
name: protocol
description: How the variable is reached (e.g., ``CA``, ``PVA``); NARAD's ``access_protocol``
  spells these out (``EPICS Channel Access``).
from_schema: https://w3id.org/laura/schema
close_mappings:
- pals:access_protocol
rank: 1000
owner: ControlVariable
domain_of:
- ControlVariable
range: string

```
</details></div>