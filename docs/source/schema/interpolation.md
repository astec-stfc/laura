# Slot: interpolation 


_How the strength behaves between the sampled knots._



<div data-search-exclude markdown="1">



URI: [laura:interpolation](https://w3id.org/laura/interpolation)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [SampledWaveform](SampledWaveform.md) | A pulse shape sampled at a sparse set of points, for a device whose strength ... |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [WaveformInterpolationEnum](WaveformInterpolationEnum.md) |
| Domain Of | [SampledWaveform](SampledWaveform.md) |

### Cardinality and Requirements

| Property | Value |
| --- | --- |
### Slot Characteristics

| Property | Value |
| --- | --- |
| If Absent | `WaveformInterpolationEnum(linear)` |
| Owner | [SampledWaveform](SampledWaveform.md) |












## Identifier and Mapping Information





### Schema Source


* from schema: https://w3id.org/laura/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | laura:interpolation |
| native | laura:interpolation |




## LinkML Source

<details>
```yaml
name: interpolation
description: How the strength behaves between the sampled knots.
from_schema: https://w3id.org/laura/schema
rank: 1000
ifabsent: WaveformInterpolationEnum(linear)
owner: SampledWaveform
domain_of:
- SampledWaveform
range: WaveformInterpolationEnum

```
</details></div>
