---
search:
  boost: 2.0
---


# Enum: ControlTypeEnum 




_Kind of quantity a control variable carries._



<div data-search-exclude markdown="1">

URI: [laura:ControlTypeEnum](https://w3id.org/laura/ControlTypeEnum)

## Permissible Values
| Value | Meaning | Description |
| --- | --- | --- |
| scalar | None | Single numeric value |
| binary | None | Two-state value |
| state | None | Enumerated state, mapped through ``states`` |
| string | None | Textual value |
| waveform | None | Array-valued trace |
| statistical | None | Value with associated statistics (the default) |




## Slots

| Name | Description |
| ---  | --- |
| [control_type](control_type.md) | Kind of quantity this variable carries |










## Identifier and Mapping Information





### Schema Source


* from schema: https://w3id.org/laura/schema






## LinkML Source

<details>
```yaml
name: ControlTypeEnum
description: Kind of quantity a control variable carries.
from_schema: https://w3id.org/laura/schema
rank: 1000
permissible_values:
  scalar:
    text: scalar
    description: Single numeric value.
  binary:
    text: binary
    description: Two-state value.
  state:
    text: state
    description: Enumerated state, mapped through ``states``.
  string:
    text: string
    description: Textual value.
  waveform:
    text: waveform
    description: Array-valued trace.
  statistical:
    text: statistical
    description: Value with associated statistics (the default).

```
</details>

</div>