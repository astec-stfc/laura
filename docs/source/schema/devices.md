---
search:
  boost: 5.0
---

# Slot: devices 


_List of attached devices._



<div data-search-exclude markdown="1">



URI: [laura:devices](https://w3id.org/laura/devices)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [ScreenDiagnosticElement](ScreenDiagnosticElement.md) | Scintillator or OTR screen diagnostic data |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [String](String.md) |
| Domain Of | [ScreenDiagnosticElement](ScreenDiagnosticElement.md) |

### Cardinality and Requirements

| Property | Value |
| --- | --- |
| Multivalued | Yes |
### Slot Characteristics

| Property | Value |
| --- | --- |
| Owner | [ScreenDiagnosticElement](ScreenDiagnosticElement.md) |












## Identifier and Mapping Information





### Schema Source


* from schema: https://w3id.org/laura/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | laura:devices |
| native | laura:devices |




## LinkML Source

<details>
```yaml
name: devices
description: List of attached devices.
from_schema: https://w3id.org/laura/schema
rank: 1000
owner: ScreenDiagnosticElement
domain_of:
- ScreenDiagnosticElement
range: string
multivalued: true

```
</details></div>