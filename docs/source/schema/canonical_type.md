# Slot: canonical_type 


_The quantity the variable carries, independent of its PV name (e.g., ``MagnetCurrentSetpoint``), in NARAD's ``CanonicalSignalTypeEnum`` terms._



<div data-search-exclude markdown="1">



URI: [laura:canonical_type](https://w3id.org/laura/canonical_type)
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
| self | laura:canonical_type |
| native | laura:canonical_type |
| exact | pals:canonical_signal_type |




## LinkML Source

<details>
```yaml
name: canonical_type
description: The quantity the variable carries, independent of its PV name (e.g.,
  ``MagnetCurrentSetpoint``), in NARAD's ``CanonicalSignalTypeEnum`` terms.
from_schema: https://w3id.org/laura/schema
exact_mappings:
- pals:canonical_signal_type
rank: 1000
owner: ControlVariable
domain_of:
- ControlVariable
range: string

```
</details></div>