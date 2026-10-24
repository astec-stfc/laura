# Slot: quantity_kind 


_The physical kind of quantity (e.g., ``ElectricCurrent``), in NARAD's ``QuantityKindEnum`` terms._



<div data-search-exclude markdown="1">



URI: [laura:quantity_kind](https://w3id.org/laura/quantity_kind)
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
| self | laura:quantity_kind |
| native | laura:quantity_kind |
| exact | pals:quantity_kind |




## LinkML Source

<details>
```yaml
name: quantity_kind
description: The physical kind of quantity (e.g., ``ElectricCurrent``), in NARAD's
  ``QuantityKindEnum`` terms.
from_schema: https://w3id.org/laura/schema
exact_mappings:
- pals:quantity_kind
rank: 1000
owner: ControlVariable
domain_of:
- ControlVariable
range: string

```
</details></div>