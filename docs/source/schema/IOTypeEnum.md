---
search:
  boost: 2.0
---


# Enum: IOTypeEnum 




_Input types for accelerator elements._



<div data-search-exclude markdown="1">

URI: [laura:IOTypeEnum](https://w3id.org/laura/IOTypeEnum)

## Permissible Values
| Value | Meaning | Description |
| --- | --- | --- |
| current | None | Electrical current |
| voltage | None | Electrical voltage |
| phase | None | Phase in radians |
| setpoint | None | Control setpoint |
| on_off_state | None | On/Off state |
| open_closed_state | None | Open/Closed state |
| position | None | Physical position |
| rotation | None | Physical rotation |
| power | None | Electrical power |
| pressure | None | Gas pressure |
| charge | None | Electrical charge |
| absolute_time | None | Absolute timing |
| relative_time | None | Relative timing |
| shot_number | None | Shot number |
| value | None | Single value |
| waveform | None | Multivalued waveform |
| magnetic_field | None | Magnetic field |




## Slots

| Name | Description |
| ---  | --- |
| [inputs](inputs.md) | (List) of input types |
| [outputs](outputs.md) | (List) of output types |










## Identifier and Mapping Information





### Schema Source


* from schema: https://w3id.org/laura/schema






## LinkML Source

<details>
```yaml
name: IOTypeEnum
description: Input types for accelerator elements.
from_schema: https://w3id.org/laura/schema
rank: 1000
permissible_values:
  current:
    text: current
    description: Electrical current.
  voltage:
    text: voltage
    description: Electrical voltage.
  phase:
    text: phase
    description: Phase in radians.
  setpoint:
    text: setpoint
    description: Control setpoint.
  on_off_state:
    text: on_off_state
    description: On/Off state.
  open_closed_state:
    text: open_closed_state
    description: Open/Closed state.
  position:
    text: position
    description: Physical position.
  rotation:
    text: rotation
    description: Physical rotation.
  power:
    text: power
    description: Electrical power.
  pressure:
    text: pressure
    description: Gas pressure.
  charge:
    text: charge
    description: Electrical charge.
  absolute_time:
    text: absolute_time
    description: Absolute timing.
  relative_time:
    text: relative_time
    description: Relative timing.
  shot_number:
    text: shot_number
    description: Shot number.
  value:
    text: value
    description: Single value.
  waveform:
    text: waveform
    description: Multivalued waveform.
  magnetic_field:
    text: magnetic_field
    description: Magnetic field.

```
</details>

</div>