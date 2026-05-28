---
search:
  boost: 10.0
---

# Class: BLMDiagnosticElement 


_Bunch-length monitor (BLM) diagnostic data._



<div data-search-exclude markdown="1">



URI: [laura:BLMDiagnosticElement](https://w3id.org/laura/BLMDiagnosticElement)





```mermaid
 classDiagram
    class BLMDiagnosticElement
    click BLMDiagnosticElement href "../BLMDiagnosticElement/"
      DiagnosticElement <|-- BLMDiagnosticElement
        click DiagnosticElement href "../DiagnosticElement/"
      
      BLMDiagnosticElement : type
        
      
```





## Inheritance
* [DiagnosticElement](DiagnosticElement.md)
    * **BLMDiagnosticElement**


## Class Properties

| Property | Value |
| --- | --- |
| Class URI | [laura:BLMDiagnosticElement](https://w3id.org/laura/BLMDiagnosticElement) |


## Slots

| Name | Cardinality and Range | Description | Inheritance |
| ---  | --- | --- | --- |
| [type](type.md) | 0..1 <br/> [String](String.md) | BLM type (e | direct |





## Usages

| used by | used in | type | used |
| ---  | --- | --- | --- |
| [BunchLengthMonitor](BunchLengthMonitor.md) | [diagnostic](diagnostic.md) | range | [BLMDiagnosticElement](BLMDiagnosticElement.md) |








## In Subsets


* [DiagnosticProperties](DiagnosticProperties.md)






## Identifier and Mapping Information





### Schema Source


* from schema: https://w3id.org/laura/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | laura:BLMDiagnosticElement |
| native | laura:BLMDiagnosticElement |






## LinkML Source

<!-- TODO: investigate https://stackoverflow.com/questions/37606292/how-to-create-tabbed-code-blocks-in-mkdocs-or-sphinx -->

### Direct

<details>
```yaml
name: BLMDiagnosticElement
description: Bunch-length monitor (BLM) diagnostic data.
in_subset:
- diagnostic_properties
from_schema: https://w3id.org/laura/schema
is_a: DiagnosticElement
attributes:
  type:
    name: type
    description: BLM type (e.g., ``CDR``). Accepted in YAML as ``blm_type``.
    from_schema: https://w3id.org/laura/schema/diagnostics
    aliases:
    - blm_type
    ifabsent: string(CDR)
    domain_of:
    - BPMDiagnosticElement
    - BAMDiagnosticElement
    - BLMDiagnosticElement
    - ScreenDiagnosticElement
    - ChargeDiagnosticElement
    - CameraDiagnosticElement
    range: string
class_uri: laura:BLMDiagnosticElement

```
</details>

### Induced

<details>
```yaml
name: BLMDiagnosticElement
description: Bunch-length monitor (BLM) diagnostic data.
in_subset:
- diagnostic_properties
from_schema: https://w3id.org/laura/schema
is_a: DiagnosticElement
attributes:
  type:
    name: type
    description: BLM type (e.g., ``CDR``). Accepted in YAML as ``blm_type``.
    from_schema: https://w3id.org/laura/schema/diagnostics
    aliases:
    - blm_type
    ifabsent: string(CDR)
    owner: BLMDiagnosticElement
    domain_of:
    - BPMDiagnosticElement
    - BAMDiagnosticElement
    - BLMDiagnosticElement
    - ScreenDiagnosticElement
    - ChargeDiagnosticElement
    - CameraDiagnosticElement
    range: string
class_uri: laura:BLMDiagnosticElement

```
</details></div>