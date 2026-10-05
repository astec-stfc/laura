# Enum: WaveformInterpolationEnum 




_How a sampled waveform behaves between the points it was sampled at._



<div data-search-exclude markdown="1">

URI: [laura:WaveformInterpolationEnum](https://w3id.org/laura/WaveformInterpolationEnum)

## Permissible Values
| Value | Meaning | Description |
| --- | --- | --- |
| linear | None | Straight line between neighbouring knots. What every tracking code does by de... |
| hold | None | Each knot's value holds until the next one, so the waveform is a staircase. No... |
| spline | None | Cubic spline through the knots, for a measured trace sampled too coarsely for... |













## Identifier and Mapping Information





### Schema Source


* from schema: https://w3id.org/laura/schema






## LinkML Source

<details>
```yaml
name: WaveformInterpolationEnum
description: How a sampled waveform behaves between the points it was sampled at.
from_schema: https://w3id.org/laura/schema
rank: 1000
permissible_values:
  linear:
    text: linear
    description: Straight line between neighbouring knots. What every tracking code
      does by default.
  hold:
    text: hold
    description: Each knot's value holds until the next one, so the waveform is a
      staircase. No code offers this natively; a device that steps rather than slews
      has to say so here, or it will be read as a slew.
  spline:
    text: spline
    description: Cubic spline through the knots, for a measured trace sampled too
      coarsely for straight lines to be honest about it.

```
</details>

</div>
