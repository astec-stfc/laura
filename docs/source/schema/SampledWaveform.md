# Class: SampledWaveform 


_A pulse shape sampled at a sparse set of points, for a device whose strength is a program rather than a constant: an injection kicker, an extraction septum, a tune exciter driven from a measured trace. Only the knots are stored, and the value between them follows ``interpolation``._



<div data-search-exclude markdown="1">



URI: [laura:SampledWaveform](https://w3id.org/laura/SampledWaveform)





```mermaid
 classDiagram
    class SampledWaveform
    click SampledWaveform href "../SampledWaveform/"
      SampledWaveform : factor
        
      SampledWaveform : interpolation
        
          
    
        
        
        SampledWaveform --> "0..1" WaveformInterpolationEnum : interpolation
        click WaveformInterpolationEnum href "../WaveformInterpolationEnum/"
    

        
      SampledWaveform : time
        
      
```




<!-- no inheritance hierarchy -->

## Class Properties

| Property | Value |
| --- | --- |
| Class URI | [laura:SampledWaveform](https://w3id.org/laura/SampledWaveform) |


## Slots

| Name | Cardinality and Range | Description | Inheritance |
| ---  | --- | --- | --- |
| [time](time.md) | * <br/> [Float](Float.md) | Sample times, measured from the moment the device fires [s] | direct |
| [factor](factor.md) | * <br/> [Float](Float.md) | Strength at each of the times in ``time``, as a fraction of the element's nom... | direct |
| [interpolation](interpolation.md) | 0..1 <br/> [WaveformInterpolationEnum](WaveformInterpolationEnum.md) | How the strength behaves between the sampled knots | direct |





## Usages

| used by | used in | type | used |
| ---  | --- | --- | --- |
| [ACDipoleSimulationElement](ACDipoleSimulationElement.md) | [waveform](waveform.md) | range | [SampledWaveform](SampledWaveform.md) |












## Identifier and Mapping Information





### Schema Source


* from schema: https://w3id.org/laura/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | laura:SampledWaveform |
| native | laura:SampledWaveform |






## LinkML Source

<!-- TODO: investigate https://stackoverflow.com/questions/37606292/how-to-create-tabbed-code-blocks-in-mkdocs-or-sphinx -->

### Direct

<details>
```yaml
name: SampledWaveform
description: 'A pulse shape sampled at a sparse set of points, for a device whose
  strength is a program rather than a constant: an injection kicker, an extraction
  septum, a tune exciter driven from a measured trace. Only the knots are stored,
  and the value between them follows ``interpolation``.'
from_schema: https://w3id.org/laura/schema
attributes:
  time:
    name: time
    description: Sample times, measured from the moment the device fires [s]. Must
      be non-decreasing and the same length as ``factor``.
    from_schema: https://w3id.org/laura/schema/simulation
    rank: 1000
    domain_of:
    - SampledWaveform
    range: float
    multivalued: true
    unit:
      ucum_code: s
  factor:
    name: factor
    description: Strength at each of the times in ``time``, as a fraction of the element's
      nominal strength; 1.0 is full strength.
    from_schema: https://w3id.org/laura/schema/simulation
    rank: 1000
    domain_of:
    - SampledWaveform
    - WakefieldSimulationElement
    range: float
    multivalued: true
  interpolation:
    name: interpolation
    description: How the strength behaves between the sampled knots.
    from_schema: https://w3id.org/laura/schema/simulation
    rank: 1000
    ifabsent: WaveformInterpolationEnum(linear)
    domain_of:
    - SampledWaveform
    range: WaveformInterpolationEnum
class_uri: laura:SampledWaveform

```
</details>

### Induced

<details>
```yaml
name: SampledWaveform
description: 'A pulse shape sampled at a sparse set of points, for a device whose
  strength is a program rather than a constant: an injection kicker, an extraction
  septum, a tune exciter driven from a measured trace. Only the knots are stored,
  and the value between them follows ``interpolation``.'
from_schema: https://w3id.org/laura/schema
attributes:
  time:
    name: time
    description: Sample times, measured from the moment the device fires [s]. Must
      be non-decreasing and the same length as ``factor``.
    from_schema: https://w3id.org/laura/schema/simulation
    rank: 1000
    owner: SampledWaveform
    domain_of:
    - SampledWaveform
    range: float
    multivalued: true
    unit:
      ucum_code: s
  factor:
    name: factor
    description: Strength at each of the times in ``time``, as a fraction of the element's
      nominal strength; 1.0 is full strength.
    from_schema: https://w3id.org/laura/schema/simulation
    rank: 1000
    owner: SampledWaveform
    domain_of:
    - SampledWaveform
    - WakefieldSimulationElement
    range: float
    multivalued: true
  interpolation:
    name: interpolation
    description: How the strength behaves between the sampled knots.
    from_schema: https://w3id.org/laura/schema/simulation
    rank: 1000
    ifabsent: WaveformInterpolationEnum(linear)
    owner: SampledWaveform
    domain_of:
    - SampledWaveform
    range: WaveformInterpolationEnum
class_uri: laura:SampledWaveform

```
</details></div>