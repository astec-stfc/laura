---
search:
  boost: 5.0
---

# Slot: dynamics 


_Response model describing how this variable's readback follows its set-point, as ``{model: <import path>, **kwargs}`` -- see ``laura.utils.dynamics``. Only meaningful alongside ``readback`` or ``setpoint``._



<div data-search-exclude markdown="1">



URI: [laura:dynamics](https://w3id.org/laura/dynamics)
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
| self | laura:dynamics |
| native | laura:dynamics |




## LinkML Source

<details>
```yaml
name: dynamics
description: 'Response model describing how this variable''s readback follows its
  set-point, as ``{model: <import path>, **kwargs}`` -- see ``laura.utils.dynamics``.
  Only meaningful alongside ``readback`` or ``setpoint``.'
from_schema: https://w3id.org/laura/schema
rank: 1000
owner: ControlVariable
domain_of:
- ControlVariable
range: string

```
</details></div>