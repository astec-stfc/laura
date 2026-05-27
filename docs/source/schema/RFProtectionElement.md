---
search:
  boost: 10.0
---

# Class: RFProtectionElement 


_RF protection system parameters._



<div data-search-exclude markdown="1">



URI: [laura:RFProtectionElement](https://w3id.org/laura/RFProtectionElement)





```mermaid
 classDiagram
    class RFProtectionElement
    click RFProtectionElement href "../RFProtectionElement/"
      RFProtectionElement : prot_type
        
      
```




<!-- no inheritance hierarchy -->

## Class Properties

| Property | Value |
| --- | --- |
| Class URI | [laura:RFProtectionElement](https://w3id.org/laura/RFProtectionElement) |


## Slots

| Name | Cardinality and Range | Description | Inheritance |
| ---  | --- | --- | --- |
| [prot_type](prot_type.md) | 0..1 <br/> [String](String.md) | Protection system type | direct |





## Usages

| used by | used in | type | used |
| ---  | --- | --- | --- |
| [RFProtection](RFProtection.md) | [protection](protection.md) | range | [RFProtectionElement](RFProtectionElement.md) |












## Identifier and Mapping Information





### Schema Source


* from schema: https://w3id.org/laura/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | laura:RFProtectionElement |
| native | laura:RFProtectionElement |






## LinkML Source

<!-- TODO: investigate https://stackoverflow.com/questions/37606292/how-to-create-tabbed-code-blocks-in-mkdocs-or-sphinx -->

### Direct

<details>
```yaml
name: RFProtectionElement
description: RF protection system parameters.
from_schema: https://w3id.org/laura/schema
attributes:
  prot_type:
    name: prot_type
    description: Protection system type.
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    domain_of:
    - RFProtectionElement
    range: string
class_uri: laura:RFProtectionElement

```
</details>

### Induced

<details>
```yaml
name: RFProtectionElement
description: RF protection system parameters.
from_schema: https://w3id.org/laura/schema
attributes:
  prot_type:
    name: prot_type
    description: Protection system type.
    from_schema: https://w3id.org/laura/schema
    rank: 1000
    owner: RFProtectionElement
    domain_of:
    - RFProtectionElement
    range: string
class_uri: laura:RFProtectionElement

```
</details></div>