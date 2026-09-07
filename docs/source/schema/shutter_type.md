# Slot: shutter_type 


_What the shutter blocks, e.g. ``BEAM`` or ``LASER``._



<div data-search-exclude markdown="1">



URI: [laura:shutter_type](https://w3id.org/laura/shutter_type)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [ShutterControlsInformation](ShutterControlsInformation.md) | Control interface of a beam or laser shutter |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [String](String.md) |
| Domain Of | [ShutterControlsInformation](ShutterControlsInformation.md) |

### Cardinality and Requirements

| Property | Value |
| --- | --- |
### Slot Characteristics

| Property | Value |
| --- | --- |
| If Absent | `string(Unknown)` |
| Owner | [ShutterControlsInformation](ShutterControlsInformation.md) |












## Identifier and Mapping Information





### Schema Source


* from schema: https://w3id.org/laura/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | laura:shutter_type |
| native | laura:shutter_type |




## LinkML Source

<details>
```yaml
name: shutter_type
description: What the shutter blocks, e.g. ``BEAM`` or ``LASER``.
from_schema: https://w3id.org/laura/schema
rank: 1000
ifabsent: string(Unknown)
owner: ShutterControlsInformation
domain_of:
- ShutterControlsInformation
range: string

```
</details></div>