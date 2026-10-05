# Slot: time 


_Sample times, measured from the moment the device fires [s]. Must be non-decreasing and the same length as `factor`._



<div data-search-exclude markdown="1">



URI: [laura:time](https://w3id.org/laura/time)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [SampledWaveform](SampledWaveform.md) | A pulse shape sampled at a sparse set of points, for a device whose strength ... |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [Float](Float.md) |
| Domain Of | [SampledWaveform](SampledWaveform.md) |

### Cardinality and Requirements

| Property | Value |
| --- | --- |
| Multivalued | Yes |
### Slot Characteristics

| Property | Value |
| --- | --- |
| Unit | s |
| Owner | [SampledWaveform](SampledWaveform.md) |












## Identifier and Mapping Information





### Schema Source


* from schema: https://w3id.org/laura/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | laura:time |
| native | laura:time |




## LinkML Source

<details>
```yaml
name: time
description: Sample times, measured from the moment the device fires [s]. Must be
  non-decreasing and the same length as ``factor``.
from_schema: https://w3id.org/laura/schema
rank: 1000
unit:
  ucum_code: s
owner: SampledWaveform
domain_of:
- SampledWaveform
range: float
multivalued: true

```
</details></div>
