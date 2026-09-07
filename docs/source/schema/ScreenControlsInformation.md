# Class: ScreenControlsInformation 


_Control interface of a screen, which also drives an actuator between named positions._



<div data-search-exclude markdown="1">



URI: [laura:ScreenControlsInformation](https://w3id.org/laura/ScreenControlsInformation)





```mermaid
 classDiagram
    class ScreenControlsInformation
    click ScreenControlsInformation href "../ScreenControlsInformation/"
      ControlsInformation <|-- ScreenControlsInformation
        click ControlsInformation href "../ControlsInformation/"
      
      ScreenControlsInformation : identifier_pattern
        
      ScreenControlsInformation : movement_type
        
      ScreenControlsInformation : schema
        
      ScreenControlsInformation : variables
        
          
    
        
        
        ScreenControlsInformation --> "*" ControlVariable : variables
        click ControlVariable href "../ControlVariable/"
    

        
      
```





## Inheritance
* [ControlsInformation](ControlsInformation.md)
    * **ScreenControlsInformation**


## Class Properties

| Property | Value |
| --- | --- |
| Class URI | [laura:ScreenControlsInformation](https://w3id.org/laura/ScreenControlsInformation) |


## Slots

| Name | Cardinality and Range | Description | Inheritance |
| ---  | --- | --- | --- |
| [movement_type](movement_type.md) | 0..1 <br/> [String](String.md) | How the screen is moved, e | direct |
| [variables](variables.md) | * <br/> [ControlVariable](ControlVariable.md) | Named control variables keyed by logical name | [ControlsInformation](ControlsInformation.md) |
| [schema](schema.md) | 0..1 <br/> [String](String.md) | The shared controls schema file ``variables`` was expanded from, if any | [ControlsInformation](ControlsInformation.md) |
| [identifier_pattern](identifier_pattern.md) | 0..1 <br/> [String](String.md) | What ``{name}`` in that file was substituted with, where it was not the eleme... | [ControlsInformation](ControlsInformation.md) |





## Usages

| used by | used in | type | used |
| ---  | --- | --- | --- |
| [Screen](Screen.md) | [controls](controls.md) | range | [ScreenControlsInformation](ScreenControlsInformation.md) |












## Identifier and Mapping Information





### Schema Source


* from schema: https://w3id.org/laura/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | laura:ScreenControlsInformation |
| native | laura:ScreenControlsInformation |






## LinkML Source

<!-- TODO: investigate https://stackoverflow.com/questions/37606292/how-to-create-tabbed-code-blocks-in-mkdocs-or-sphinx -->

### Direct

<details>
```yaml
name: ScreenControlsInformation
description: Control interface of a screen, which also drives an actuator between
  named positions.
from_schema: https://w3id.org/laura/schema
is_a: ControlsInformation
attributes:
  movement_type:
    name: movement_type
    description: How the screen is moved, e.g. ``VMOTOR``.
    from_schema: https://w3id.org/laura/schema/controls
    rank: 1000
    ifabsent: string(Unknown)
    domain_of:
    - ScreenControlsInformation
    range: string
class_uri: laura:ScreenControlsInformation

```
</details>

### Induced

<details>
```yaml
name: ScreenControlsInformation
description: Control interface of a screen, which also drives an actuator between
  named positions.
from_schema: https://w3id.org/laura/schema
is_a: ControlsInformation
attributes:
  movement_type:
    name: movement_type
    description: How the screen is moved, e.g. ``VMOTOR``.
    from_schema: https://w3id.org/laura/schema/controls
    rank: 1000
    ifabsent: string(Unknown)
    owner: ScreenControlsInformation
    domain_of:
    - ScreenControlsInformation
    range: string
  variables:
    name: variables
    description: Named control variables keyed by logical name.
    from_schema: https://w3id.org/laura/schema/controls
    rank: 1000
    owner: ScreenControlsInformation
    domain_of:
    - ControlsInformation
    range: ControlVariable
    multivalued: true
    inlined: true
    inlined_as_list: false
  schema:
    name: schema
    description: 'The shared controls schema file ``variables`` was expanded from,
      if any.  Kept only as a record of where they came from: the expansion happens
      while the element YAML is read, so ``variables`` is always already resolved
      by the time anything sees this class.'
    from_schema: https://w3id.org/laura/schema/controls
    rank: 1000
    owner: ScreenControlsInformation
    domain_of:
    - ControlsInformation
    range: string
  identifier_pattern:
    name: identifier_pattern
    description: What ``{name}`` in that file was substituted with, where it was not
      the element's own name.
    from_schema: https://w3id.org/laura/schema/controls
    rank: 1000
    owner: ScreenControlsInformation
    domain_of:
    - ControlsInformation
    range: string
class_uri: laura:ScreenControlsInformation

```
</details></div>