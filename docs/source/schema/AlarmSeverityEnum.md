# Enum: AlarmSeverityEnum 




_Alarm severity reported alongside a control-system reading, following the EPICS severity levels._



<div data-search-exclude markdown="1">

URI: [laura:AlarmSeverityEnum](https://w3id.org/laura/AlarmSeverityEnum)

## Permissible Values
| Value | Meaning | Description |
| --- | --- | --- |
| no_alarm | None | Value is within its alarm limits |
| minor | None | Value has crossed a warning limit |
| major | None | Value has crossed an alarm limit |
| invalid | None | Value could not be read, or is not trustworthy |




## Slots

| Name | Description |
| ---  | --- |
| [severity](severity.md) | Alarm severity reported with ``value`` |










## Identifier and Mapping Information





### Schema Source


* from schema: https://w3id.org/laura/schema






## LinkML Source

<details>
```yaml
name: AlarmSeverityEnum
description: Alarm severity reported alongside a control-system reading, following
  the EPICS severity levels.
from_schema: https://w3id.org/laura/schema
rank: 1000
permissible_values:
  no_alarm:
    text: no_alarm
    description: Value is within its alarm limits.
  minor:
    text: minor
    description: Value has crossed a warning limit.
  major:
    text: major
    description: Value has crossed an alarm limit.
  invalid:
    text: invalid
    description: Value could not be read, or is not trustworthy.

```
</details>

</div>