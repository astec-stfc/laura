# Slot: wakefield_definition 


_Path to the wakefield impedance file._



<div data-search-exclude markdown="1">



URI: [laura:wakefield_definition](https://w3id.org/laura/wakefield_definition)
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
| Range | [String](String.md) |
| Domain Of | [SimulationElement](SimulationElement.md) |

### Cardinality and Requirements

| Property | Value |
| --- | --- |
### Slot Characteristics

| Property | Value |
| --- | --- |
| Owner | [SimulationElement](SimulationElement.md) |












## Identifier and Mapping Information





### Schema Source


* from schema: https://w3id.org/laura/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | laura:wakefield_definition |
| native | laura:wakefield_definition |




## LinkML Source

<details>
```yaml
name: wakefield_definition
description: Path to the wakefield impedance file.
from_schema: https://w3id.org/laura/schema
rank: 1000
owner: SimulationElement
domain_of:
- SimulationElement
range: string

```
</details></div>