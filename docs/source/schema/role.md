# Slot: role 


_What the variable is to its element (e.g., ``Setpoint``, ``Readback``, ``MaximumLimit``), in NARAD's ``SignalRoleEnum`` terms._



<div data-search-exclude markdown="1">



URI: [laura:role](https://w3id.org/laura/role)
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
| self | laura:role |
| native | laura:role |
| exact | pals:signal_role |




## LinkML Source

<details>
```yaml
name: role
description: What the variable is to its element (e.g., ``Setpoint``, ``Readback``,
  ``MaximumLimit``), in NARAD's ``SignalRoleEnum`` terms.
from_schema: https://w3id.org/laura/schema
exact_mappings:
- pals:signal_role
rank: 1000
owner: ControlVariable
domain_of:
- ControlVariable
range: string

```
</details></div>