# Slot: readback_tolerance 


_Fractional deviation within which a readback counts as having reached its set-point (0.01 = 1 %). Named to avoid colliding with ``DegaussableElement.tolerance``, which is an absolute current band._



<div data-search-exclude markdown="1">



URI: [laura:readback_tolerance](https://w3id.org/laura/readback_tolerance)
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


### Value Constraints

| Property | Value |
| --- | --- |
| Minimum Value | 0 |












## Identifier and Mapping Information





### Schema Source


* from schema: https://w3id.org/laura/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | laura:readback_tolerance |
| native | laura:readback_tolerance |




## LinkML Source

<details>
```yaml
name: readback_tolerance
description: Fractional deviation within which a readback counts as having reached
  its set-point (0.01 = 1 %). Named to avoid colliding with ``DegaussableElement.tolerance``,
  which is an absolute current band.
from_schema: https://w3id.org/laura/schema
rank: 1000
owner: ControlVariable
domain_of:
- ControlVariable
range: float
minimum_value: 0.0

```
</details></div>