# Slot: variables 


_Named control variables keyed by logical name._



<div data-search-exclude markdown="1">



URI: [laura:variables](https://w3id.org/laura/variables)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [ControlsInformation](ControlsInformation.md) | Collection of process-variable definitions for an element's control interface |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [ControlVariable](ControlVariable.md) |
| Domain Of | [ControlsInformation](ControlsInformation.md) |

### Cardinality and Requirements

| Property | Value |
| --- | --- |
| Multivalued | Yes |
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
| self | laura:variables |
| native | laura:variables |




## LinkML Source

<details>
```yaml
name: variables
description: Named control variables keyed by logical name.
from_schema: https://w3id.org/laura/schema
rank: 1000
owner: ControlsInformation
domain_of:
- ControlsInformation
range: ControlVariable
multivalued: true
inlined: true
inlined_as_list: false

```
</details></div>