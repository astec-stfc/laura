---
search:
  boost: 10.0
---

# Class: CameraDiagnosticElement 


_Camera diagnostic data, including sensor parameters, analysis mask, and pixel-to-mm scale factors._



<div data-search-exclude markdown="1">



URI: [laura:CameraDiagnosticElement](https://w3id.org/laura/CameraDiagnosticElement)





```mermaid
 classDiagram
    class CameraDiagnosticElement
    click CameraDiagnosticElement href "../CameraDiagnosticElement/"
      DiagnosticElement <|-- CameraDiagnosticElement
        click DiagnosticElement href "../DiagnosticElement/"
      
      CameraDiagnosticElement : flipped_horizontally
        
      CameraDiagnosticElement : flipped_vertically
        
      CameraDiagnosticElement : has_led
        
      CameraDiagnosticElement : rotation
        
      CameraDiagnosticElement : screen_name
        
      CameraDiagnosticElement : type
        
      CameraDiagnosticElement : x_pixels
        
      CameraDiagnosticElement : y_pixels
        
      
```





## Inheritance
* [DiagnosticElement](DiagnosticElement.md)
    * **CameraDiagnosticElement**


## Class Properties

| Property | Value |
| --- | --- |
| Class URI | [laura:CameraDiagnosticElement](https://w3id.org/laura/CameraDiagnosticElement) |


## Slots

| Name | Cardinality and Range | Description | Inheritance |
| ---  | --- | --- | --- |
| [type](type.md) | 0..1 <br/> [String](String.md) | Camera type / model string (e | direct |
| [x_pixels](x_pixels.md) | 0..1 <br/> [Integer](Integer.md) | Image width reported by the control system [pix] | direct |
| [y_pixels](y_pixels.md) | 0..1 <br/> [Integer](Integer.md) | Image height reported by the control system [pix] | direct |
| [rotation](rotation.md) | 0..1 <br/> [Float](Float.md) | Camera rotation relative to the screen plane [deg] | direct |
| [flipped_horizontally](flipped_horizontally.md) | 0..1 <br/> [Boolean](Boolean.md) | True if the image is mirrored left-right | direct |
| [flipped_vertically](flipped_vertically.md) | 0..1 <br/> [Boolean](Boolean.md) | True if the image is mirrored top-bottom | direct |
| [screen_name](screen_name.md) | 0..1 <br/> [String](String.md) | Name of the screen element to which this camera is attached | direct |
| [has_led](has_led.md) | 0..1 <br/> [Boolean](Boolean.md) | True if the camera mount includes an LED backlight | direct |





## Usages

| used by | used in | type | used |
| ---  | --- | --- | --- |
| [Camera](Camera.md) | [diagnostic](diagnostic.md) | range | [CameraDiagnosticElement](CameraDiagnosticElement.md) |








## In Subsets


* [DiagnosticProperties](DiagnosticProperties.md)






## Identifier and Mapping Information





### Schema Source


* from schema: https://w3id.org/laura/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | laura:CameraDiagnosticElement |
| native | laura:CameraDiagnosticElement |






## LinkML Source

<!-- TODO: investigate https://stackoverflow.com/questions/37606292/how-to-create-tabbed-code-blocks-in-mkdocs-or-sphinx -->

### Direct

<details>
```yaml
name: CameraDiagnosticElement
description: Camera diagnostic data, including sensor parameters, analysis mask, and
  pixel-to-mm scale factors.
in_subset:
- diagnostic_properties
from_schema: https://w3id.org/laura/schema
is_a: DiagnosticElement
attributes:
  type:
    name: type
    description: Camera type / model string (e.g., ``PCO``, ``Manta``). Accepted in
      YAML as ``CAM_TYPE``.
    from_schema: https://w3id.org/laura/schema
    aliases:
    - CAM_TYPE
    domain_of:
    - BPMDiagnosticElement
    - BAMDiagnosticElement
    - BLMDiagnosticElement
    - ScreenDiagnosticElement
    - ChargeDiagnosticElement
    - CameraDiagnosticElement
    range: string
  x_pixels:
    name: x_pixels
    description: Image width reported by the control system [pix].
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    domain_of:
    - CameraDiagnosticElement
    range: integer
  y_pixels:
    name: y_pixels
    description: Image height reported by the control system [pix].
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    domain_of:
    - CameraDiagnosticElement
    range: integer
  rotation:
    name: rotation
    description: Camera rotation relative to the screen plane [deg].
    from_schema: https://w3id.org/laura/schema
    domain_of:
    - ElementPositionError
    - ElementSurvey
    - PhysicalElement
    - CameraDiagnosticElement
    range: float
    unit:
      ucum_code: deg
  flipped_horizontally:
    name: flipped_horizontally
    description: True if the image is mirrored left-right.
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    domain_of:
    - CameraDiagnosticElement
    range: boolean
  flipped_vertically:
    name: flipped_vertically
    description: True if the image is mirrored top-bottom.
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    domain_of:
    - CameraDiagnosticElement
    range: boolean
  screen_name:
    name: screen_name
    description: Name of the screen element to which this camera is attached.
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    domain_of:
    - CameraDiagnosticElement
    range: string
  has_led:
    name: has_led
    description: True if the camera mount includes an LED backlight.
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    domain_of:
    - CameraDiagnosticElement
    range: boolean
class_uri: laura:CameraDiagnosticElement

```
</details>

### Induced

<details>
```yaml
name: CameraDiagnosticElement
description: Camera diagnostic data, including sensor parameters, analysis mask, and
  pixel-to-mm scale factors.
in_subset:
- diagnostic_properties
from_schema: https://w3id.org/laura/schema
is_a: DiagnosticElement
attributes:
  type:
    name: type
    description: Camera type / model string (e.g., ``PCO``, ``Manta``). Accepted in
      YAML as ``CAM_TYPE``.
    from_schema: https://w3id.org/laura/schema
    aliases:
    - CAM_TYPE
    owner: CameraDiagnosticElement
    domain_of:
    - BPMDiagnosticElement
    - BAMDiagnosticElement
    - BLMDiagnosticElement
    - ScreenDiagnosticElement
    - ChargeDiagnosticElement
    - CameraDiagnosticElement
    range: string
  x_pixels:
    name: x_pixels
    description: Image width reported by the control system [pix].
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    owner: CameraDiagnosticElement
    domain_of:
    - CameraDiagnosticElement
    range: integer
  y_pixels:
    name: y_pixels
    description: Image height reported by the control system [pix].
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    owner: CameraDiagnosticElement
    domain_of:
    - CameraDiagnosticElement
    range: integer
  rotation:
    name: rotation
    description: Camera rotation relative to the screen plane [deg].
    from_schema: https://w3id.org/laura/schema
    owner: CameraDiagnosticElement
    domain_of:
    - ElementPositionError
    - ElementSurvey
    - PhysicalElement
    - CameraDiagnosticElement
    range: float
    unit:
      ucum_code: deg
  flipped_horizontally:
    name: flipped_horizontally
    description: True if the image is mirrored left-right.
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    owner: CameraDiagnosticElement
    domain_of:
    - CameraDiagnosticElement
    range: boolean
  flipped_vertically:
    name: flipped_vertically
    description: True if the image is mirrored top-bottom.
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    owner: CameraDiagnosticElement
    domain_of:
    - CameraDiagnosticElement
    range: boolean
  screen_name:
    name: screen_name
    description: Name of the screen element to which this camera is attached.
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    owner: CameraDiagnosticElement
    domain_of:
    - CameraDiagnosticElement
    range: string
  has_led:
    name: has_led
    description: True if the camera mount includes an LED backlight.
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    owner: CameraDiagnosticElement
    domain_of:
    - CameraDiagnosticElement
    range: boolean
class_uri: laura:CameraDiagnosticElement

```
</details></div>