# Slot: intensity 


_Measured photon intensity._



<div data-search-exclude markdown="1">



URI: [laura:intensity](https://w3id.org/laura/intensity)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [PhotonIntensityMonitorDiagnostic](PhotonIntensityMonitorDiagnostic.md) | Photon intensity monitor diagnostic data |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [Double](Double.md) |
| Domain Of | [PhotonIntensityMonitorDiagnostic](PhotonIntensityMonitorDiagnostic.md) |

### Cardinality and Requirements

| Property | Value |
| --- | --- |
### Slot Characteristics

| Property | Value |
| --- | --- |
| If Absent | `float(0.0)` |
| Owner | [PhotonIntensityMonitorDiagnostic](PhotonIntensityMonitorDiagnostic.md) |












## Identifier and Mapping Information





### Schema Source


* from schema: https://w3id.org/laura/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | laura:intensity |
| native | laura:intensity |




## LinkML Source

<details>
```yaml
name: intensity
description: Measured photon intensity.
from_schema: https://w3id.org/laura/schema
rank: 1000
ifabsent: float(0.0)
owner: PhotonIntensityMonitorDiagnostic
domain_of:
- PhotonIntensityMonitorDiagnostic
range: double

```
</details></div>