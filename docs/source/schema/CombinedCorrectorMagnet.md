# Class: CombinedCorrectorMagnet 


_The pair of steering-corrector fields inside one combined corrector._



<div data-search-exclude markdown="1">



URI: [laura:CombinedCorrectorMagnet](https://w3id.org/laura/CombinedCorrectorMagnet)





```mermaid
 classDiagram
    class CombinedCorrectorMagnet
    click CombinedCorrectorMagnet href "../CombinedCorrectorMagnet/"
      CombinedCorrectorMagnet : horizontal
        
          
    
        
        
        CombinedCorrectorMagnet --> "0..1" CorrectorMagnet : horizontal
        click CorrectorMagnet href "../CorrectorMagnet/"
    

        
      CombinedCorrectorMagnet : vertical
        
          
    
        
        
        CombinedCorrectorMagnet --> "0..1" CorrectorMagnet : vertical
        click CorrectorMagnet href "../CorrectorMagnet/"
    

        
      
```




<!-- no inheritance hierarchy -->

## Class Properties

| Property | Value |
| --- | --- |
| Class URI | [laura:CombinedCorrectorMagnet](https://w3id.org/laura/CombinedCorrectorMagnet) |


## Slots

| Name | Cardinality and Range | Description | Inheritance |
| ---  | --- | --- | --- |
| [horizontal](horizontal.md) | 0..1 <br/> [CorrectorMagnet](CorrectorMagnet.md) | Horizontal-plane corrector field, with its own calibration | direct |
| [vertical](vertical.md) | 0..1 <br/> [CorrectorMagnet](CorrectorMagnet.md) | Vertical-plane corrector field, with its own calibration | direct |





## Usages

| used by | used in | type | used |
| ---  | --- | --- | --- |
| [CombinedCorrector](CombinedCorrector.md) | [magnetic](magnetic.md) | range | [CombinedCorrectorMagnet](CombinedCorrectorMagnet.md) |












## Identifier and Mapping Information





### Schema Source


* from schema: https://w3id.org/laura/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | laura:CombinedCorrectorMagnet |
| native | laura:CombinedCorrectorMagnet |






## LinkML Source

<!-- TODO: investigate https://stackoverflow.com/questions/37606292/how-to-create-tabbed-code-blocks-in-mkdocs-or-sphinx -->

### Direct

<details>
```yaml
name: CombinedCorrectorMagnet
description: The pair of steering-corrector fields inside one combined corrector.
from_schema: https://w3id.org/laura/schema
attributes:
  horizontal:
    name: horizontal
    description: Horizontal-plane corrector field, with its own calibration.
    from_schema: https://w3id.org/laura/schema/magnetic
    rank: 1000
    domain_of:
    - CombinedCorrectorMagnet
    range: Corrector_Magnet
  vertical:
    name: vertical
    description: Vertical-plane corrector field, with its own calibration.
    from_schema: https://w3id.org/laura/schema/magnetic
    rank: 1000
    domain_of:
    - CombinedCorrectorMagnet
    range: Corrector_Magnet
class_uri: laura:CombinedCorrectorMagnet

```
</details>

### Induced

<details>
```yaml
name: CombinedCorrectorMagnet
description: The pair of steering-corrector fields inside one combined corrector.
from_schema: https://w3id.org/laura/schema
attributes:
  horizontal:
    name: horizontal
    description: Horizontal-plane corrector field, with its own calibration.
    from_schema: https://w3id.org/laura/schema/magnetic
    rank: 1000
    owner: CombinedCorrectorMagnet
    domain_of:
    - CombinedCorrectorMagnet
    range: Corrector_Magnet
  vertical:
    name: vertical
    description: Vertical-plane corrector field, with its own calibration.
    from_schema: https://w3id.org/laura/schema/magnetic
    rank: 1000
    owner: CombinedCorrectorMagnet
    domain_of:
    - CombinedCorrectorMagnet
    range: Corrector_Magnet
class_uri: laura:CombinedCorrectorMagnet

```
</details></div>