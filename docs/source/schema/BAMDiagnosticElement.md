---
search:
  boost: 10.0
---

# Class: BAMDiagnosticElement 


_Beam-arrival monitor (BAM) diagnostic data._



<div data-search-exclude markdown="1">



URI: [laura:BAMDiagnosticElement](https://w3id.org/laura/BAMDiagnosticElement)





```mermaid
 classDiagram
    class BAMDiagnosticElement
    click BAMDiagnosticElement href "../BAMDiagnosticElement/"
      DiagnosticElement <|-- BAMDiagnosticElement
        click DiagnosticElement href "../DiagnosticElement/"
      
      BAMDiagnosticElement : type
        
      
```





## Inheritance
* [DiagnosticElement](DiagnosticElement.md)
    * **BAMDiagnosticElement**


## Class Properties

| Property | Value |
| --- | --- |
| Class URI | [laura:BAMDiagnosticElement](https://w3id.org/laura/BAMDiagnosticElement) |


## Slots

| Name | Cardinality and Range | Description | Inheritance |
| ---  | --- | --- | --- |
| [type](type.md) | 0..1 <br/> [String](String.md) | BAM type | direct |





## Usages

| used by | used in | type | used |
| ---  | --- | --- | --- |
| [BeamArrivalMonitor](BeamArrivalMonitor.md) | [diagnostic](diagnostic.md) | range | [BAMDiagnosticElement](BAMDiagnosticElement.md) |








## In Subsets


* [DiagnosticProperties](DiagnosticProperties.md)






## Identifier and Mapping Information





### Schema Source


* from schema: https://w3id.org/laura/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | laura:BAMDiagnosticElement |
| native | laura:BAMDiagnosticElement |






## LinkML Source

<!-- TODO: investigate https://stackoverflow.com/questions/37606292/how-to-create-tabbed-code-blocks-in-mkdocs-or-sphinx -->

### Direct

<details>
```yaml
name: BAMDiagnosticElement
description: Beam-arrival monitor (BAM) diagnostic data.
in_subset:
- diagnostic_properties
from_schema: https://w3id.org/laura/schema
is_a: DiagnosticElement
attributes:
  type:
    name: type
    description: BAM type. Accepted in YAML as ``bam_type``.
    from_schema: https://w3id.org/laura/schema/diagnostics
    aliases:
    - bam_type
    ifabsent: string(DESY)
    domain_of:
    - BPMDiagnosticElement
    - BAMDiagnosticElement
    - PhotonIntensityMonitorDiagnostic
    - BLMDiagnosticElement
    - ScreenDiagnosticElement
    - ChargeDiagnosticElement
    - CameraDiagnosticElement
    range: string
class_uri: laura:BAMDiagnosticElement

```
</details>

### Induced

<details>
```yaml
name: BAMDiagnosticElement
description: Beam-arrival monitor (BAM) diagnostic data.
in_subset:
- diagnostic_properties
from_schema: https://w3id.org/laura/schema
is_a: DiagnosticElement
attributes:
  type:
    name: type
    description: BAM type. Accepted in YAML as ``bam_type``.
    from_schema: https://w3id.org/laura/schema/diagnostics
    aliases:
    - bam_type
    ifabsent: string(DESY)
    owner: BAMDiagnosticElement
    domain_of:
    - BPMDiagnosticElement
    - BAMDiagnosticElement
    - PhotonIntensityMonitorDiagnostic
    - BLMDiagnosticElement
    - ScreenDiagnosticElement
    - ChargeDiagnosticElement
    - CameraDiagnosticElement
    range: string
class_uri: laura:BAMDiagnosticElement

```
</details></div>