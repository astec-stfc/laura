# Slot: severity 


_Alarm severity reported with ``value``. Absent means no severity was supplied; it does not mean the reading was healthy._



<div data-search-exclude markdown="1">



URI: [laura:severity](https://w3id.org/laura/severity)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [ControlVariable](ControlVariable.md) | A single process-variable entry mapping a logical name to a control-system PV... |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [AlarmSeverityEnum](AlarmSeverityEnum.md) |
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
| self | laura:severity |
| native | laura:severity |




## LinkML Source

<details>
```yaml
name: severity
description: Alarm severity reported with ``value``. Absent means no severity was
  supplied; it does not mean the reading was healthy.
from_schema: https://w3id.org/laura/schema
rank: 1000
owner: ControlVariable
domain_of:
- ControlVariable
range: AlarmSeverityEnum

```
</details></div>