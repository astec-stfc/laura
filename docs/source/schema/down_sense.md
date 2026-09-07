# Slot: down_sense 


_Sign relating a downward move to the actuator's direction._



<div data-search-exclude markdown="1">



URI: [laura:down_sense](https://w3id.org/laura/down_sense)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [MirrorControlsInformation](MirrorControlsInformation.md) | Control interface of a steerable laser mirror |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [Integer](Integer.md) |
| Domain Of | [MirrorControlsInformation](MirrorControlsInformation.md) |

### Cardinality and Requirements

| Property | Value |
| --- | --- |
### Slot Characteristics

| Property | Value |
| --- | --- |
| If Absent | `int(1)` |
| Owner | [MirrorControlsInformation](MirrorControlsInformation.md) |












## Identifier and Mapping Information





### Schema Source


* from schema: https://w3id.org/laura/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | laura:down_sense |
| native | laura:down_sense |




## LinkML Source

<details>
```yaml
name: down_sense
description: Sign relating a downward move to the actuator's direction.
from_schema: https://w3id.org/laura/schema
rank: 1000
ifabsent: int(1)
owner: MirrorControlsInformation
domain_of:
- MirrorControlsInformation
range: integer

```
</details></div>