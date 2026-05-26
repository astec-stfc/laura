---
search:
  boost: 5.0
---

# Slot: units 


_Physical units string (e.g., ``A``, ``T/m``)._



<div data-search-exclude markdown="1">



URI: [laura:units](https://w3id.org/laura/units)
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
| self | laura:units |
| native | laura:units |




## LinkML Source

<details>
```yaml
name: units
description: Physical units string (e.g., ``A``, ``T/m``).
from_schema: https://w3id.org/laura/schema
rank: 1000
owner: ControlVariable
domain_of:
- ControlVariable
range: string

```
</details></div>