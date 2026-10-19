# Slot: waveform 


_Sampled pulse shape, for a device whose strength is a program rather than a sinusoid -- an injection kicker or an extraction septum. An alternative to `frequency`/`phase`/`ramp` rather than an addition to them: a kicker carries a waveform and no frequency, a tune exciter a frequency and no waveform._



<div data-search-exclude markdown="1">



URI: [laura:waveform](https://w3id.org/laura/waveform)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [ACDipoleSimulationElement](ACDipoleSimulationElement.md) | Simulation attributes for an AC dipole / tune exciter |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [SampledWaveform](SampledWaveform.md) |
| Domain Of | [ACDipoleSimulationElement](ACDipoleSimulationElement.md) |

### Cardinality and Requirements

| Property | Value |
| --- | --- |
### Slot Characteristics

| Property | Value |
| --- | --- |
| Owner | [ACDipoleSimulationElement](ACDipoleSimulationElement.md) |












## Identifier and Mapping Information





### Schema Source


* from schema: https://w3id.org/laura/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | laura:waveform |
| native | laura:waveform |




## LinkML Source

<details>
```yaml
name: waveform
description: 'Sampled pulse shape, for a device whose strength is a program rather
  than a sinusoid -- an injection kicker or an extraction septum. An alternative to
  ``frequency``/``phase``/``ramp`` rather than an addition to them: a kicker carries
  a waveform and no frequency, a tune exciter a frequency and no waveform.'
from_schema: https://w3id.org/laura/schema
rank: 1000
owner: ACDipoleSimulationElement
domain_of:
- ACDipoleSimulationElement
range: SampledWaveform

```
</details></div>
