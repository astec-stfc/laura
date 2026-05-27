---
search:
  boost: 5.0
---

# Slot: scale_field 


_Multiplicative scale factor applied to the field map._



<div data-search-exclude markdown="1">



URI: [laura:scale_field](https://w3id.org/laura/scale_field)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [SimulationElement](SimulationElement.md) | Base simulation attributes: field-map files and reference positions for track... |  no  |
| [MagnetSimulationElement](MagnetSimulationElement.md) | Simulation attributes specific to magnets: integrator settings, fringe-field ... |  no  |
| [RFCavitySimulationElement](RFCavitySimulationElement.md) | Simulation attributes for RF cavity elements |  no  |
| [WakefieldSimulationElement](WakefieldSimulationElement.md) | Simulation attributes for passive wakefield structures |  no  |
| [DriftSimulationElement](DriftSimulationElement.md) | Simulation attributes for field-free drift sections |  no  |
| [DiagnosticSimulationElement](DiagnosticSimulationElement.md) | Simulation attributes for beam-diagnostic elements |  no  |
| [PlasmaSimulationElement](PlasmaSimulationElement.md) | Simulation attributes for plasma-accelerator stages |  no  |
| [TwissMatchSimulationElement](TwissMatchSimulationElement.md) | Simulation attributes for Twiss-matching points |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [Float](Float.md) |
| Domain Of | [SimulationElement](SimulationElement.md) |

### Cardinality and Requirements

| Property | Value |
| --- | --- |
### Slot Characteristics

| Property | Value |
| --- | --- |
| If Absent | `float(1)` |
| Owner | [SimulationElement](SimulationElement.md) |












## Identifier and Mapping Information





### Schema Source


* from schema: https://w3id.org/laura/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | laura:scale_field |
| native | laura:scale_field |




## LinkML Source

<details>
```yaml
name: scale_field
description: Multiplicative scale factor applied to the field map.
from_schema: https://w3id.org/laura/schema
rank: 1000
ifabsent: float(1)
owner: SimulationElement
domain_of:
- SimulationElement
range: float

```
</details></div>