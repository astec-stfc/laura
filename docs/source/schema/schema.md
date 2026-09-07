# Slot: schema 


_The shared controls schema file ``variables`` was expanded from, if any.  Kept only as a record of where they came from: the expansion happens while the element YAML is read, so ``variables`` is always already resolved by the time anything sees this class._



<div data-search-exclude markdown="1">



URI: [laura:schema](https://w3id.org/laura/schema)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [ControlsInformation](ControlsInformation.md) | Collection of process-variable definitions for an element's control interface |  no  |
| [ScreenControlsInformation](ScreenControlsInformation.md) | Control interface of a screen, which also drives an actuator between named po... |  no  |
| [MirrorControlsInformation](MirrorControlsInformation.md) | Control interface of a steerable laser mirror |  no  |
| [ShutterControlsInformation](ShutterControlsInformation.md) | Control interface of a beam or laser shutter |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [String](String.md) |
| Domain Of | [ControlsInformation](ControlsInformation.md) |

### Cardinality and Requirements

| Property | Value |
| --- | --- |
### Slot Characteristics

| Property | Value |
| --- | --- |
| Owner | [ControlsInformation](ControlsInformation.md) |












## Identifier and Mapping Information





### Schema Source


* from schema: https://w3id.org/laura/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | laura:schema |
| native | laura:schema |




## LinkML Source

<details>
```yaml
name: schema
description: 'The shared controls schema file ``variables`` was expanded from, if
  any.  Kept only as a record of where they came from: the expansion happens while
  the element YAML is read, so ``variables`` is always already resolved by the time
  anything sees this class.'
from_schema: https://w3id.org/laura/schema
rank: 1000
owner: ControlsInformation
domain_of:
- ControlsInformation
range: string

```
</details></div>