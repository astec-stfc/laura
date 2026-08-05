# Slot: min_value 


_Lowest value this variable may be set to, in ``units``. Advisory operating limit for anything writing a set-point, not a hardware interlock._



<div data-search-exclude markdown="1">



URI: [laura:min_value](https://w3id.org/laura/min_value)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [ControlVariable](ControlVariable.md) | A single process-variable entry mapping a logical name to a control-system PV... |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [Float](Float.md) |
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
| self | laura:min_value |
| native | laura:min_value |




## LinkML Source

<details>
```yaml
name: min_value
description: Lowest value this variable may be set to, in ``units``. Advisory operating
  limit for anything writing a set-point, not a hardware interlock.
from_schema: https://w3id.org/laura/schema
rank: 1000
owner: ControlVariable
domain_of:
- ControlVariable
range: float

```
</details></div>