---
search:
  boost: 10.0
---

# Class: RFDeflectingCavityElement 


_Transverse-deflecting RF cavity parameters -- a subset of RFCavityElement for streak-mode operation._



<div data-search-exclude markdown="1">



URI: [laura:RFDeflectingCavityElement](https://w3id.org/laura/RFDeflectingCavityElement)





```mermaid
 classDiagram
    class RFDeflectingCavityElement
    click RFDeflectingCavityElement href "../RFDeflectingCavityElement/"
      RFDeflectingCavityElement : coupling_cell_length
        
      RFDeflectingCavityElement : design_gamma
        
      RFDeflectingCavityElement : design_power
        
      RFDeflectingCavityElement : frequency
        
      RFDeflectingCavityElement : mode_denominator
        
      RFDeflectingCavityElement : mode_numerator
        
      RFDeflectingCavityElement : n_cells
        
      RFDeflectingCavityElement : phase
        
      RFDeflectingCavityElement : shunt_impedance
        
      
```




<!-- no inheritance hierarchy -->

## Class Properties

| Property | Value |
| --- | --- |
| Class URI | [laura:RFDeflectingCavityElement](https://w3id.org/laura/RFDeflectingCavityElement) |


## Slots

| Name | Cardinality and Range | Description | Inheritance |
| ---  | --- | --- | --- |
| [coupling_cell_length](coupling_cell_length.md) | 0..1 <br/> [Float](Float.md) | Length of the coupling cell [m] | direct |
| [design_gamma](design_gamma.md) | 0..1 <br/> [Float](Float.md) | Design Lorentz factor ? | direct |
| [design_power](design_power.md) | 0..1 <br/> [Float](Float.md) | Design peak power [W] | direct |
| [frequency](frequency.md) | 0..1 <br/> [Float](Float.md) | Operating frequency [Hz] | direct |
| [n_cells](n_cells.md) | 0..1 <br/> [Integer](Integer.md) | Number of cells | direct |
| [phase](phase.md) | 0..1 <br/> [Float](Float.md) | Operating phase offset [deg] | direct |
| [shunt_impedance](shunt_impedance.md) | 0..1 <br/> [Float](Float.md) | Shunt impedance [M?/m] | direct |
| [mode_numerator](mode_numerator.md) | 0..1 <br/> [Integer](Integer.md) | Mode fraction numerator | direct |
| [mode_denominator](mode_denominator.md) | 0..1 <br/> [Integer](Integer.md) | Mode fraction denominator | direct |





## Usages

| used by | used in | type | used |
| ---  | --- | --- | --- |
| [RFDeflectingCavity](RFDeflectingCavity.md) | [cavity](cavity.md) | range | [RFDeflectingCavityElement](RFDeflectingCavityElement.md) |








## In Subsets


* [RfProperties](RfProperties.md)






## Identifier and Mapping Information





### Schema Source


* from schema: https://w3id.org/laura/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | laura:RFDeflectingCavityElement |
| native | laura:RFDeflectingCavityElement |






## LinkML Source

<!-- TODO: investigate https://stackoverflow.com/questions/37606292/how-to-create-tabbed-code-blocks-in-mkdocs-or-sphinx -->

### Direct

<details>
```yaml
name: RFDeflectingCavityElement
description: Transverse-deflecting RF cavity parameters -- a subset of RFCavityElement
  for streak-mode operation.
in_subset:
- rf_properties
from_schema: https://w3id.org/laura/schema
attributes:
  coupling_cell_length:
    name: coupling_cell_length
    description: Length of the coupling cell [m].
    from_schema: https://w3id.org/laura/schema
    domain_of:
    - RFCavityElement
    - WakefieldElement
    - RFDeflectingCavityElement
    range: float
    unit:
      ucum_code: m
  design_gamma:
    name: design_gamma
    description: Design Lorentz factor ?.
    from_schema: https://w3id.org/laura/schema
    domain_of:
    - RFCavityElement
    - RFDeflectingCavityElement
    range: float
    minimum_value: 1.0
  design_power:
    name: design_power
    description: Design peak power [W].
    from_schema: https://w3id.org/laura/schema
    domain_of:
    - RFCavityElement
    - RFDeflectingCavityElement
    range: float
    unit:
      ucum_code: W
  frequency:
    name: frequency
    description: Operating frequency [Hz].
    from_schema: https://w3id.org/laura/schema
    domain_of:
    - RFCavityElement
    - RFDeflectingCavityElement
    range: float
    unit:
      ucum_code: Hz
  n_cells:
    name: n_cells
    description: Number of cells.
    from_schema: https://w3id.org/laura/schema
    domain_of:
    - RFCavityElement
    - WakefieldElement
    - RFDeflectingCavityElement
    range: integer
    minimum_value: 1
  phase:
    name: phase
    description: Operating phase offset [deg].
    from_schema: https://w3id.org/laura/schema
    domain_of:
    - RFCavityElement
    - RFDeflectingCavityElement
    range: float
    unit:
      ucum_code: deg
  shunt_impedance:
    name: shunt_impedance
    description: Shunt impedance [M?/m].
    from_schema: https://w3id.org/laura/schema
    domain_of:
    - RFCavityElement
    - RFDeflectingCavityElement
    range: float
  mode_numerator:
    name: mode_numerator
    description: Mode fraction numerator.
    from_schema: https://w3id.org/laura/schema
    domain_of:
    - RFCavityElement
    - RFDeflectingCavityElement
    range: integer
  mode_denominator:
    name: mode_denominator
    description: Mode fraction denominator.
    from_schema: https://w3id.org/laura/schema
    domain_of:
    - RFCavityElement
    - RFDeflectingCavityElement
    range: integer
class_uri: laura:RFDeflectingCavityElement

```
</details>

### Induced

<details>
```yaml
name: RFDeflectingCavityElement
description: Transverse-deflecting RF cavity parameters -- a subset of RFCavityElement
  for streak-mode operation.
in_subset:
- rf_properties
from_schema: https://w3id.org/laura/schema
attributes:
  coupling_cell_length:
    name: coupling_cell_length
    description: Length of the coupling cell [m].
    from_schema: https://w3id.org/laura/schema
    owner: RFDeflectingCavityElement
    domain_of:
    - RFCavityElement
    - WakefieldElement
    - RFDeflectingCavityElement
    range: float
    unit:
      ucum_code: m
  design_gamma:
    name: design_gamma
    description: Design Lorentz factor ?.
    from_schema: https://w3id.org/laura/schema
    owner: RFDeflectingCavityElement
    domain_of:
    - RFCavityElement
    - RFDeflectingCavityElement
    range: float
    minimum_value: 1.0
  design_power:
    name: design_power
    description: Design peak power [W].
    from_schema: https://w3id.org/laura/schema
    owner: RFDeflectingCavityElement
    domain_of:
    - RFCavityElement
    - RFDeflectingCavityElement
    range: float
    unit:
      ucum_code: W
  frequency:
    name: frequency
    description: Operating frequency [Hz].
    from_schema: https://w3id.org/laura/schema
    owner: RFDeflectingCavityElement
    domain_of:
    - RFCavityElement
    - RFDeflectingCavityElement
    range: float
    unit:
      ucum_code: Hz
  n_cells:
    name: n_cells
    description: Number of cells.
    from_schema: https://w3id.org/laura/schema
    owner: RFDeflectingCavityElement
    domain_of:
    - RFCavityElement
    - WakefieldElement
    - RFDeflectingCavityElement
    range: integer
    minimum_value: 1
  phase:
    name: phase
    description: Operating phase offset [deg].
    from_schema: https://w3id.org/laura/schema
    owner: RFDeflectingCavityElement
    domain_of:
    - RFCavityElement
    - RFDeflectingCavityElement
    range: float
    unit:
      ucum_code: deg
  shunt_impedance:
    name: shunt_impedance
    description: Shunt impedance [M?/m].
    from_schema: https://w3id.org/laura/schema
    owner: RFDeflectingCavityElement
    domain_of:
    - RFCavityElement
    - RFDeflectingCavityElement
    range: float
  mode_numerator:
    name: mode_numerator
    description: Mode fraction numerator.
    from_schema: https://w3id.org/laura/schema
    owner: RFDeflectingCavityElement
    domain_of:
    - RFCavityElement
    - RFDeflectingCavityElement
    range: integer
  mode_denominator:
    name: mode_denominator
    description: Mode fraction denominator.
    from_schema: https://w3id.org/laura/schema
    owner: RFDeflectingCavityElement
    domain_of:
    - RFCavityElement
    - RFDeflectingCavityElement
    range: integer
class_uri: laura:RFDeflectingCavityElement

```
</details></div>