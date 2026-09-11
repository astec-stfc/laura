# Slot: diagnostic 

<div data-search-exclude markdown="1">



URI: [laura:diagnostic](https://w3id.org/laura/diagnostic)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [Diagnostic](Diagnostic.md) | Base class for all beam-diagnostic instruments |  no  |
| [BeamPositionMonitor](BeamPositionMonitor.md) | Beam-position monitor (BPM) |  no  |
| [BeamArrivalMonitor](BeamArrivalMonitor.md) | Beam-arrival-time monitor (BAM) |  no  |
| [BunchLengthMonitor](BunchLengthMonitor.md) | Bunch-length monitor (BLM / CDR detector) |  no  |
| [Camera](Camera.md) | Camera-based beam-profile monitor |  no  |
| [Screen](Screen.md) | Scintillator or OTR screen with an associated camera |  no  |
| [ChargeDiagnostic](ChargeDiagnostic.md) | Base class for charge-measurement diagnostics |  no  |
| [WallCurrentMonitor](WallCurrentMonitor.md) | Wall-current monitor (WCM) for non-destructive charge measurement |  no  |
| [FaradayCupMonitor](FaradayCupMonitor.md) | Faraday cup for destructive charge measurement |  no  |
| [IntegratedCurrentTransformer](IntegratedCurrentTransformer.md) | Integrated current transformer (ICT) for non-destructive single-shot charge m... |  no  |
| [PhotonMonitor](PhotonMonitor.md) | Photon intensity monitor |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [String](String.md) |
| Domain Of | [Diagnostic](Diagnostic.md), [BeamPositionMonitor](BeamPositionMonitor.md), [BeamArrivalMonitor](BeamArrivalMonitor.md), [BunchLengthMonitor](BunchLengthMonitor.md), [Camera](Camera.md), [Screen](Screen.md), [ChargeDiagnostic](ChargeDiagnostic.md), [PhotonMonitor](PhotonMonitor.md) |

### Cardinality and Requirements

| Property | Value |
| --- | --- |










## Identifier and Mapping Information






## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | laura:diagnostic |
| native | laura:diagnostic |




## LinkML Source

<details>
```yaml
name: diagnostic
domain_of:
- Diagnostic
- BeamPositionMonitor
- BeamArrivalMonitor
- BunchLengthMonitor
- Camera
- Screen
- ChargeDiagnostic
- PhotonMonitor
range: string

```
</details></div>