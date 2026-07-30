---
search:
  boost: 5.0
---

# Slot: expression 


_Expression graph computing the value written to ``target``, as nested mappings of the form ``{op: mul, args: [<symbol>, <symbol>]}``, where a symbol is a variable name or a dotted attribute path. Operators are ``add``, ``sub``, ``mul``, ``truediv`` and ``pow``._



<div data-search-exclude markdown="1">



URI: [laura:expression](https://w3id.org/laura/expression)
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
| self | laura:expression |
| native | laura:expression |




## LinkML Source

<details>
```yaml
name: expression
description: 'Expression graph computing the value written to ``target``, as nested
  mappings of the form ``{op: mul, args: [<symbol>, <symbol>]}``, where a symbol is
  a variable name or a dotted attribute path. Operators are ``add``, ``sub``, ``mul``,
  ``truediv`` and ``pow``.'
from_schema: https://w3id.org/laura/schema
rank: 1000
owner: ControlVariable
domain_of:
- ControlVariable
range: string

```
</details></div>