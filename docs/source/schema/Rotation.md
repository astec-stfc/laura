---
search:
  boost: 5.0
---

# Slot: rotation 

<div data-search-exclude markdown="1">



URI: [laura:rotation](https://w3id.org/laura/rotation)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [ElementPositionError](ElementPositionError.md) | Alignment position and rotation errors for a physically-located element |  no  |
| [ElementSurvey](ElementSurvey.md) | Survey-measured position and rotation of an element |  no  |
| [PhysicalElement](PhysicalElement.md) | Physical placement data: position, rotation, length, and associated survey / ... |  no  |
| [CameraDiagnosticElement](CameraDiagnosticElement.md) | Camera diagnostic data, including sensor parameters, analysis mask, and pixel... |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [String](String.md) |
| Domain Of | [ElementPositionError](ElementPositionError.md), [ElementSurvey](ElementSurvey.md), [PhysicalElement](PhysicalElement.md), [CameraDiagnosticElement](CameraDiagnosticElement.md) |

### Cardinality and Requirements

| Property | Value |
| --- | --- |










## Identifier and Mapping Information






## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | laura:rotation |
| native | laura:rotation |




## LinkML Source

<details>
```yaml
name: rotation
domain_of:
- ElementPositionError
- ElementSurvey
- PhysicalElement
- CameraDiagnosticElement
range: string

```
</details></div>