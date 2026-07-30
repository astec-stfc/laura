---
search:
  boost: 5.0
---

# Slot: type 

<div data-search-exclude markdown="1">



URI: [laura:type](https://w3id.org/laura/type)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [BPMDiagnosticElement](BPMDiagnosticElement.md) | Beam-position monitor (BPM) diagnostic data |  no  |
| [BAMDiagnosticElement](BAMDiagnosticElement.md) | Beam-arrival monitor (BAM) diagnostic data |  no  |
| [PhotonIntensityMonitorDiagnostic](PhotonIntensityMonitorDiagnostic.md) | Photon intensity monitor diagnostic data |  no  |
| [BLMDiagnosticElement](BLMDiagnosticElement.md) | Bunch-length monitor (BLM) diagnostic data |  no  |
| [ScreenDiagnosticElement](ScreenDiagnosticElement.md) | Scintillator or OTR screen diagnostic data |  no  |
| [ChargeDiagnosticElement](ChargeDiagnosticElement.md) | Charge-measurement diagnostic data (base for ICT, FCM, WCM) |  no  |
| [CameraDiagnosticElement](CameraDiagnosticElement.md) | Camera diagnostic data, including sensor parameters, analysis mask, and pixel... |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [String](String.md) |
| Domain Of | [BPMDiagnosticElement](BPMDiagnosticElement.md), [BAMDiagnosticElement](BAMDiagnosticElement.md), [PhotonIntensityMonitorDiagnostic](PhotonIntensityMonitorDiagnostic.md), [BLMDiagnosticElement](BLMDiagnosticElement.md), [ScreenDiagnosticElement](ScreenDiagnosticElement.md), [ChargeDiagnosticElement](ChargeDiagnosticElement.md), [CameraDiagnosticElement](CameraDiagnosticElement.md) |

### Cardinality and Requirements

| Property | Value |
| --- | --- |










## Identifier and Mapping Information






## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | laura:type |
| native | laura:type |




## LinkML Source

<details>
```yaml
name: type
domain_of:
- BPMDiagnosticElement
- BAMDiagnosticElement
- PhotonIntensityMonitorDiagnostic
- BLMDiagnosticElement
- ScreenDiagnosticElement
- ChargeDiagnosticElement
- CameraDiagnosticElement
range: string

```
</details></div>