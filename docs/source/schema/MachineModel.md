---
search:
  boost: 10.0
---

# Class: MachineModel 


_Top-level container for a complete accelerator lattice: elements, sections, layouts, and named lattice configurations._



<div data-search-exclude markdown="1">



URI: [laura:MachineModel](https://w3id.org/laura/MachineModel)





```mermaid
 classDiagram
    class MachineModel
    click MachineModel href "../MachineModel/"
      MachineModel : elements
        
          
    
        
        
        MachineModel --> "*" AcceleratorElement : elements
        click AcceleratorElement href "../AcceleratorElement/"
    

        
      MachineModel : layouts
        
          
    
        
        
        MachineModel --> "*" MachineLayout : layouts
        click MachineLayout href "../MachineLayout/"
    

        
      MachineModel : sections
        
          
    
        
        
        MachineModel --> "*" SectionLattice : sections
        click SectionLattice href "../SectionLattice/"
    

        
      
```




<!-- no inheritance hierarchy -->

## Class Properties

| Property | Value |
| --- | --- |
| Class URI | [laura:MachineModel](https://w3id.org/laura/MachineModel) |


## Slots

| Name | Cardinality and Range | Description | Inheritance |
| ---  | --- | --- | --- |
| [elements](elements.md) | * <br/> [AcceleratorElement](AcceleratorElement.md) | All elements in the machine, keyed by name | direct |
| [sections](sections.md) | * <br/> [SectionLattice](SectionLattice.md) | All named beamline sections | direct |
| [layouts](layouts.md) | * <br/> [MachineLayout](MachineLayout.md) | All named beamline layouts | direct |















## Identifier and Mapping Information





### Schema Source


* from schema: https://w3id.org/laura/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | laura:MachineModel |
| native | laura:MachineModel |






## LinkML Source

<!-- TODO: investigate https://stackoverflow.com/questions/37606292/how-to-create-tabbed-code-blocks-in-mkdocs-or-sphinx -->

### Direct

<details>
```yaml
name: MachineModel
description: 'Top-level container for a complete accelerator lattice: elements, sections,
  layouts, and named lattice configurations.'
from_schema: https://w3id.org/laura/schema
attributes:
  elements:
    name: elements
    description: All elements in the machine, keyed by name.
    from_schema: https://w3id.org/laura/schema/machine
    domain_of:
    - SectionLattice
    - MachineModel
    range: AcceleratorElement
    multivalued: true
  sections:
    name: sections
    description: All named beamline sections.
    from_schema: https://w3id.org/laura/schema/machine
    domain_of:
    - MachineLayout
    - MachineModel
    range: SectionLattice
    multivalued: true
  layouts:
    name: layouts
    description: All named beamline layouts.
    from_schema: https://w3id.org/laura/schema/machine
    rank: 1000
    domain_of:
    - MachineModel
    range: MachineLayout
    multivalued: true
class_uri: laura:MachineModel

```
</details>

### Induced

<details>
```yaml
name: MachineModel
description: 'Top-level container for a complete accelerator lattice: elements, sections,
  layouts, and named lattice configurations.'
from_schema: https://w3id.org/laura/schema
attributes:
  elements:
    name: elements
    description: All elements in the machine, keyed by name.
    from_schema: https://w3id.org/laura/schema/machine
    owner: MachineModel
    domain_of:
    - SectionLattice
    - MachineModel
    range: AcceleratorElement
    multivalued: true
  sections:
    name: sections
    description: All named beamline sections.
    from_schema: https://w3id.org/laura/schema/machine
    owner: MachineModel
    domain_of:
    - MachineLayout
    - MachineModel
    range: SectionLattice
    multivalued: true
  layouts:
    name: layouts
    description: All named beamline layouts.
    from_schema: https://w3id.org/laura/schema/machine
    rank: 1000
    owner: MachineModel
    domain_of:
    - MachineModel
    range: MachineLayout
    multivalued: true
class_uri: laura:MachineModel

```
</details></div>