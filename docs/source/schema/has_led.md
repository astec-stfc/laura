---
search:
  boost: 5.0
---

# Slot: has_led 


_True if the camera mount includes an LED backlight._



<div data-search-exclude markdown="1">



URI: [laura:has_led](https://w3id.org/laura/has_led)
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












## Identifier and Mapping Information





### Schema Source


* from schema: https://w3id.org/laura/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | laura:has_led |
| native | laura:has_led |




## LinkML Source

<details>
```yaml
name: has_led
description: True if the camera mount includes an LED backlight.
from_schema: https://w3id.org/laura/schema
rank: 1000
ifabsent: 'True'
owner: CameraDiagnosticElement
domain_of:
- CameraDiagnosticElement
range: boolean

```
</details></div>