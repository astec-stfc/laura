# Slot: element_dtype 


_Numeric type of the value, or of one element of the array for ``control_type: waveform``. Distinct from ``dtype``, which names the Python container._



<div data-search-exclude markdown="1">



URI: [laura:element_dtype](https://w3id.org/laura/element_dtype)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [ControlVariable](ControlVariable.md) | A single process-variable entry mapping a logical name to a control-system PV... |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [NumericDtypeEnum](NumericDtypeEnum.md) |
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
| self | laura:element_dtype |
| native | laura:element_dtype |




## LinkML Source

<details>
```yaml
name: element_dtype
description: 'Numeric type of the value, or of one element of the array for ``control_type:
  waveform``. Distinct from ``dtype``, which names the Python container.'
from_schema: https://w3id.org/laura/schema
rank: 1000
owner: ControlVariable
domain_of:
- ControlVariable
range: NumericDtypeEnum

```
</details></div>