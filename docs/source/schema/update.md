# Slot: update 


_Signal generating this variable's value over time, as ``{function: <import path>, **kwargs}`` -- see ``laura.utils.signals``. Stored with ``function`` as a fully qualified import path so it resolves without LAURA._



<div data-search-exclude markdown="1">



URI: [laura:update](https://w3id.org/laura/update)
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
| self | laura:update |
| native | laura:update |




## LinkML Source

<details>
```yaml
name: update
description: 'Signal generating this variable''s value over time, as ``{function:
  <import path>, **kwargs}`` -- see ``laura.utils.signals``. Stored with ``function``
  as a fully qualified import path so it resolves without LAURA.'
from_schema: https://w3id.org/laura/schema
rank: 1000
owner: ControlVariable
domain_of:
- ControlVariable
range: string

```
</details></div>