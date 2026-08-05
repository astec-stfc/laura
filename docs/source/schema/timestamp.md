# Slot: timestamp 


_Time at which ``value`` was read from the control system. Absent means the value has never been read, or came from a source that does not timestamp it._



<div data-search-exclude markdown="1">



URI: [laura:timestamp](https://w3id.org/laura/timestamp)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [ControlVariable](ControlVariable.md) | A single process-variable entry mapping a logical name to a control-system PV... |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [Datetime](Datetime.md) |
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
| self | laura:timestamp |
| native | laura:timestamp |




## LinkML Source

<details>
```yaml
name: timestamp
description: Time at which ``value`` was read from the control system. Absent means
  the value has never been read, or came from a source that does not timestamp it.
from_schema: https://w3id.org/laura/schema
rank: 1000
owner: ControlVariable
domain_of:
- ControlVariable
range: datetime

```
</details></div>