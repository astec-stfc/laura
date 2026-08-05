# Slot: step 


_Smallest meaningful change in this variable, in ``units``. Below this a set-point change is lost in noise or resolution._



<div data-search-exclude markdown="1">



URI: [laura:step](https://w3id.org/laura/step)
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
| self | laura:step |
| native | laura:step |




## LinkML Source

<details>
```yaml
name: step
description: Smallest meaningful change in this variable, in ``units``. Below this
  a set-point change is lost in noise or resolution.
from_schema: https://w3id.org/laura/schema
rank: 1000
owner: ControlVariable
domain_of:
- ControlVariable
range: float

```
</details></div>