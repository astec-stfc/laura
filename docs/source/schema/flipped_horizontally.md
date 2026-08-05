# Slot: flipped_horizontally 


_True if the image is mirrored left-right._



<div data-search-exclude markdown="1">



URI: [laura:flipped_horizontally](https://w3id.org/laura/flipped_horizontally)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [CameraDiagnosticElement](CameraDiagnosticElement.md) | Camera diagnostic data, including sensor parameters, analysis mask, and pixel... |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [Boolean](Boolean.md) |
| Domain Of | [CameraDiagnosticElement](CameraDiagnosticElement.md) |

### Cardinality and Requirements

| Property | Value |
| --- | --- |
### Slot Characteristics

| Property | Value |
| --- | --- |
| If Absent | `True` |
| Owner | [CameraDiagnosticElement](CameraDiagnosticElement.md) |









## Aliases


* IMAGE_FLIP_LR




## Identifier and Mapping Information





### Schema Source


* from schema: https://w3id.org/laura/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | laura:flipped_horizontally |
| native | laura:flipped_horizontally |




## LinkML Source

<details>
```yaml
name: flipped_horizontally
description: True if the image is mirrored left-right.
from_schema: https://w3id.org/laura/schema
aliases:
- IMAGE_FLIP_LR
rank: 1000
ifabsent: 'True'
owner: CameraDiagnosticElement
domain_of:
- CameraDiagnosticElement
range: boolean

```
</details></div>