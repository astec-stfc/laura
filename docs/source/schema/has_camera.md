---
search:
  boost: 5.0
---

# Slot: has_camera 


_Whether the screen has an associated camera._



<div data-search-exclude markdown="1">



URI: [laura:has_camera](https://w3id.org/laura/has_camera)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [ScreenDiagnosticElement](ScreenDiagnosticElement.md) | Scintillator or OTR screen diagnostic data |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [Boolean](Boolean.md) |
| Domain Of | [ScreenDiagnosticElement](ScreenDiagnosticElement.md) |

### Cardinality and Requirements

| Property | Value |
| --- | --- |
### Slot Characteristics

| Property | Value |
| --- | --- |
| If Absent | `True` |
| Owner | [ScreenDiagnosticElement](ScreenDiagnosticElement.md) |












## Identifier and Mapping Information





### Schema Source


* from schema: https://w3id.org/laura/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | laura:has_camera |
| native | laura:has_camera |




## LinkML Source

<details>
```yaml
name: has_camera
description: Whether the screen has an associated camera.
from_schema: https://w3id.org/laura/schema
rank: 1000
ifabsent: 'True'
owner: ScreenDiagnosticElement
domain_of:
- ScreenDiagnosticElement
range: boolean

```
</details></div>