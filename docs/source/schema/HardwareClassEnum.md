---
search:
  boost: 2.0
---


# Enum: HardwareClassEnum 




_High-level category organising elements by function within the accelerator.  Corresponds to the YAML ``hardware_class`` field._



<div data-search-exclude markdown="1">

URI: [laura:HardwareClassEnum](https://w3id.org/laura/HardwareClassEnum)

## Permissible Values
| Value | Meaning | Description |
| --- | --- | --- |
| Magnet | None | Magnetic focusing or bending element |
| Diagnostic | None | Beam-diagnostic instrument |
| RF | None | Radio-frequency accelerating or deflecting structure |
| Vacuum | None | Vacuum instrumentation (gauges, valves) |
| Laser | None | Laser optical element or complete laser system |
| Plasma | None | Plasma-based accelerating stage |
| Feedback | None | Control-system feedback element |
| Marker | None | Virtual survey marker with no physical aperture |
| Aperture | None | Mechanical aperture or collimator |
| Stage | None | Motorised positioning stage |
| Lighting | None | Experimental-hall lighting element |
| Shutter | None | Beam or laser shutter |
| Wakefield | None | Passive wakefield structure |
| TwissMatch | None | Virtual Twiss-parameter matching point |




## Slots

| Name | Description |
| ---  | --- |
| [hardware_class](hardware_class.md) | Functional category (e |










## Identifier and Mapping Information





### Schema Source


* from schema: https://w3id.org/laura/schema






## LinkML Source

<details>
```yaml
name: HardwareClassEnum
description: High-level category organising elements by function within the accelerator.  Corresponds
  to the YAML ``hardware_class`` field.
from_schema: https://w3id.org/laura/schema
rank: 1000
permissible_values:
  Magnet:
    text: Magnet
    description: Magnetic focusing or bending element.
  Diagnostic:
    text: Diagnostic
    description: Beam-diagnostic instrument.
  RF:
    text: RF
    description: Radio-frequency accelerating or deflecting structure.
  Vacuum:
    text: Vacuum
    description: Vacuum instrumentation (gauges, valves).
  Laser:
    text: Laser
    description: Laser optical element or complete laser system.
  Plasma:
    text: Plasma
    description: Plasma-based accelerating stage.
  Feedback:
    text: Feedback
    description: Control-system feedback element.
  Marker:
    text: Marker
    description: Virtual survey marker with no physical aperture.
  Aperture:
    text: Aperture
    description: Mechanical aperture or collimator.
  Stage:
    text: Stage
    description: Motorised positioning stage.
  Lighting:
    text: Lighting
    description: Experimental-hall lighting element.
  Shutter:
    text: Shutter
    description: Beam or laser shutter.
  Wakefield:
    text: Wakefield
    description: Passive wakefield structure.
  TwissMatch:
    text: TwissMatch
    description: Virtual Twiss-parameter matching point.

```
</details>

</div>