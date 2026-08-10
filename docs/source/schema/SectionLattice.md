# Class: SectionLattice 


_An ordered list of element names defining a contiguous beamline section._



<div data-search-exclude markdown="1">



URI: [laura:SectionLattice](https://w3id.org/laura/SectionLattice)





```mermaid
 classDiagram
    class SectionLattice
    click SectionLattice href "../SectionLattice/"
      SectionLattice : beampipe_aperture_type
        
          
    
        
        
        SectionLattice --> "0..1" BeampipeShapeEnum : beampipe_aperture_type
        click BeampipeShapeEnum href "../BeampipeShapeEnum/"
    

        
      SectionLattice : beampipe_material
        
      SectionLattice : beampipe_size
        
      SectionLattice : elements
        
      SectionLattice : master_lattice
        
      SectionLattice : name
        
      
```




<!-- no inheritance hierarchy -->

## Class Properties

| Property | Value |
| --- | --- |
| Class URI | [laura:SectionLattice](https://w3id.org/laura/SectionLattice) |


## Slots

| Name | Cardinality and Range | Description | Inheritance |
| ---  | --- | --- | --- |
| [name](name.md) | 1 <br/> [String](String.md) | Unique section name | direct |
| [master_lattice](master_lattice.md) | 0..1 <br/> [String](String.md) | Name of the master lattice this section belongs to | direct |
| [elements](elements.md) | * <br/> [String](String.md) | Ordered list of element names in this section | direct |
| [beampipe_aperture_type](beampipe_aperture_type.md) | 0..1 <br/> [BeampipeShapeEnum](BeampipeShapeEnum.md) | Cross-sectional beam pipe aperture shape | direct |
| [beampipe_size](beampipe_size.md) | 0..1 <br/> [Float](Float.md) | Size of beam pipe [m] | direct |
| [beampipe_material](beampipe_material.md) | 0..1 <br/> [String](String.md) | Beam pipe material | direct |





## Usages

| used by | used in | type | used |
| ---  | --- | --- | --- |
| [MachineModel](MachineModel.md) | [sections](sections.md) | range | [SectionLattice](SectionLattice.md) |












## Identifier and Mapping Information





### Schema Source


* from schema: https://w3id.org/laura/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | laura:SectionLattice |
| native | laura:SectionLattice |






## LinkML Source

<!-- TODO: investigate https://stackoverflow.com/questions/37606292/how-to-create-tabbed-code-blocks-in-mkdocs-or-sphinx -->

### Direct

<details>
```yaml
name: SectionLattice
description: An ordered list of element names defining a contiguous beamline section.
from_schema: https://w3id.org/laura/schema
attributes:
  name:
    name: name
    description: Unique section name.
    from_schema: https://w3id.org/laura/schema/machine
    identifier: true
    domain_of:
    - AcceleratorElement
    - SectionLattice
    - MachineLayout
    range: string
  master_lattice:
    name: master_lattice
    description: Name of the master lattice this section belongs to.
    from_schema: https://w3id.org/laura/schema/machine
    rank: 1000
    domain_of:
    - SectionLattice
    - MachineLayout
    range: string
  elements:
    name: elements
    description: Ordered list of element names in this section.
    from_schema: https://w3id.org/laura/schema/machine
    rank: 1000
    domain_of:
    - SectionLattice
    - MachineModel
    range: string
    multivalued: true
  beampipe_aperture_type:
    name: beampipe_aperture_type
    description: Cross-sectional beam pipe aperture shape.
    from_schema: https://w3id.org/laura/schema/machine
    rank: 1000
    domain_of:
    - SectionLattice
    - MachineModel
    range: BeampipeShapeEnum
  beampipe_size:
    name: beampipe_size
    description: Size of beam pipe [m]. A single value for a circular aperture, or
      two values (horizontal, vertical) for a rectangular or elliptical one.
    from_schema: https://w3id.org/laura/schema/machine
    rank: 1000
    domain_of:
    - SectionLattice
    - MachineModel
    range: float
    any_of:
    - range: float
    - range: float
      multivalued: true
  beampipe_material:
    name: beampipe_material
    description: Beam pipe material
    from_schema: https://w3id.org/laura/schema/machine
    rank: 1000
    domain_of:
    - SectionLattice
    - MachineModel
    range: string
class_uri: laura:SectionLattice

```
</details>

### Induced

<details>
```yaml
name: SectionLattice
description: An ordered list of element names defining a contiguous beamline section.
from_schema: https://w3id.org/laura/schema
attributes:
  name:
    name: name
    description: Unique section name.
    from_schema: https://w3id.org/laura/schema/machine
    identifier: true
    owner: SectionLattice
    domain_of:
    - AcceleratorElement
    - SectionLattice
    - MachineLayout
    range: string
    required: true
  master_lattice:
    name: master_lattice
    description: Name of the master lattice this section belongs to.
    from_schema: https://w3id.org/laura/schema/machine
    rank: 1000
    owner: SectionLattice
    domain_of:
    - SectionLattice
    - MachineLayout
    range: string
  elements:
    name: elements
    description: Ordered list of element names in this section.
    from_schema: https://w3id.org/laura/schema/machine
    rank: 1000
    owner: SectionLattice
    domain_of:
    - SectionLattice
    - MachineModel
    range: string
    multivalued: true
  beampipe_aperture_type:
    name: beampipe_aperture_type
    description: Cross-sectional beam pipe aperture shape.
    from_schema: https://w3id.org/laura/schema/machine
    rank: 1000
    owner: SectionLattice
    domain_of:
    - SectionLattice
    - MachineModel
    range: BeampipeShapeEnum
  beampipe_size:
    name: beampipe_size
    description: Size of beam pipe [m]. A single value for a circular aperture, or
      two values (horizontal, vertical) for a rectangular or elliptical one.
    from_schema: https://w3id.org/laura/schema/machine
    rank: 1000
    owner: SectionLattice
    domain_of:
    - SectionLattice
    - MachineModel
    range: float
    any_of:
    - range: float
    - range: float
      multivalued: true
  beampipe_material:
    name: beampipe_material
    description: Beam pipe material
    from_schema: https://w3id.org/laura/schema/machine
    rank: 1000
    owner: SectionLattice
    domain_of:
    - SectionLattice
    - MachineModel
    range: string
class_uri: laura:SectionLattice

```
</details></div>