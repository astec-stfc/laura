# Class: NonLinearLensMagnet 


_Integrable-optics non-linear lens field.  See the MAD-X manual and Danilov/Nagaitsev, PAC2011 WEP070._



<div data-search-exclude markdown="1">



URI: [laura:NonLinearLens_Magnet](https://w3id.org/laura/NonLinearLens_Magnet)





```mermaid
 classDiagram
    class NonLinearLensMagnet
    click NonLinearLensMagnet href "../NonLinearLensMagnet/"
      NonLinearLensMagnet : dimensional_parameter
        
      NonLinearLensMagnet : integrated_strength
        
      NonLinearLensMagnet : length
        
      
```




<!-- no inheritance hierarchy -->

## Class Properties

| Property | Value |
| --- | --- |
| Class URI | [laura:NonLinearLens_Magnet](https://w3id.org/laura/NonLinearLens_Magnet) |


## Slots

| Name | Cardinality and Range | Description | Inheritance |
| ---  | --- | --- | --- |
| [length](length.md) | 0..1 <br/> [Float](Float.md) | Magnetic length [m] | direct |
| [integrated_strength](integrated_strength.md) | 0..1 <br/> [Float](Float.md) | Integrated lens strength (MAD-X ``knll``) | direct |
| [dimensional_parameter](dimensional_parameter.md) | 0..1 <br/> [Float](Float.md) | Dimensional parameter setting the transverse scale (MAD-X ``cnll``) | direct |





## Usages

| used by | used in | type | used |
| ---  | --- | --- | --- |
| [NonLinearLens](NonLinearLens.md) | [magnetic](magnetic.md) | range | [NonLinearLensMagnet](NonLinearLensMagnet.md) |












## Identifier and Mapping Information





### Schema Source


* from schema: https://w3id.org/laura/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | laura:NonLinearLens_Magnet |
| native | laura:NonLinearLensMagnet |






## LinkML Source

<!-- TODO: investigate https://stackoverflow.com/questions/37606292/how-to-create-tabbed-code-blocks-in-mkdocs-or-sphinx -->

### Direct

<details>
```yaml
name: NonLinearLens_Magnet
description: Integrable-optics non-linear lens field.  See the MAD-X manual and Danilov/Nagaitsev,
  PAC2011 WEP070.
from_schema: https://w3id.org/laura/schema
attributes:
  length:
    name: length
    description: Magnetic length [m].
    from_schema: https://w3id.org/laura/schema/magnetic
    ifabsent: float(0.0)
    domain_of:
    - PhysicalElement
    - MagneticElement
    - Solenoid_Magnet
    - Wiggler_Magnet
    - NonLinearLens_Magnet
    range: float
    minimum_value: 0
  integrated_strength:
    name: integrated_strength
    description: Integrated lens strength (MAD-X ``knll``). May be a functional expression.
    from_schema: https://w3id.org/laura/schema/magnetic
    rank: 1000
    ifabsent: float(0.0)
    domain_of:
    - NonLinearLens_Magnet
    range: float
    minimum_value: 0
  dimensional_parameter:
    name: dimensional_parameter
    description: Dimensional parameter setting the transverse scale (MAD-X ``cnll``).
      May be a functional expression.
    from_schema: https://w3id.org/laura/schema/magnetic
    rank: 1000
    ifabsent: float(0.0)
    domain_of:
    - NonLinearLens_Magnet
    range: float
class_uri: laura:NonLinearLens_Magnet

```
</details>

### Induced

<details>
```yaml
name: NonLinearLens_Magnet
description: Integrable-optics non-linear lens field.  See the MAD-X manual and Danilov/Nagaitsev,
  PAC2011 WEP070.
from_schema: https://w3id.org/laura/schema
attributes:
  length:
    name: length
    description: Magnetic length [m].
    from_schema: https://w3id.org/laura/schema/magnetic
    ifabsent: float(0.0)
    owner: NonLinearLens_Magnet
    domain_of:
    - PhysicalElement
    - MagneticElement
    - Solenoid_Magnet
    - Wiggler_Magnet
    - NonLinearLens_Magnet
    range: float
    minimum_value: 0
  integrated_strength:
    name: integrated_strength
    description: Integrated lens strength (MAD-X ``knll``). May be a functional expression.
    from_schema: https://w3id.org/laura/schema/magnetic
    rank: 1000
    ifabsent: float(0.0)
    owner: NonLinearLens_Magnet
    domain_of:
    - NonLinearLens_Magnet
    range: float
    minimum_value: 0
  dimensional_parameter:
    name: dimensional_parameter
    description: Dimensional parameter setting the transverse scale (MAD-X ``cnll``).
      May be a functional expression.
    from_schema: https://w3id.org/laura/schema/magnetic
    rank: 1000
    ifabsent: float(0.0)
    owner: NonLinearLens_Magnet
    domain_of:
    - NonLinearLens_Magnet
    range: float
class_uri: laura:NonLinearLens_Magnet

```
</details></div>