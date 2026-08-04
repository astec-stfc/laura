# Slot: wakefield_enable 


_Whether the wakefield named by wakefield_definition is applied. Set false to track the element without its wakefield while keeping the definition itself._



<div data-search-exclude markdown="1">



URI: [laura:wakefield_enable](https://w3id.org/laura/wakefield_enable)
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
| [MatrixTransformSimulationElement](MatrixTransformSimulationElement.md) | Zero-, first-, and second-order transfer-map coefficients for a matrix transf... |  no  |
| [ElectrostaticSeparatorSimulationElement](ElectrostaticSeparatorSimulationElement.md) | Simulation attributes for a static electrostatic separator |  no  |
| [ACDipoleSimulationElement](ACDipoleSimulationElement.md) | Simulation attributes for an AC dipole / tune exciter |  no  |
| [WireSimulationElement](WireSimulationElement.md) | Simulation attributes for a compensating wire |  no  |
| [BeamBeamSimulationElement](BeamBeamSimulationElement.md) | Simulation attributes for a weak-strong beam-beam interaction |  no  |
| [RFMultipoleSimulationElement](RFMultipoleSimulationElement.md) | Simulation attributes for a thin RF multipole kick |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [Boolean](Boolean.md) |
| Domain Of | [SimulationElement](SimulationElement.md) |

### Cardinality and Requirements

| Property | Value |
| --- | --- |
### Slot Characteristics

| Property | Value |
| --- | --- |
| If Absent | `true` |
| Owner | [SimulationElement](SimulationElement.md) |












## Identifier and Mapping Information





### Schema Source


* from schema: https://w3id.org/laura/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | laura:wakefield_enable |
| native | laura:wakefield_enable |




## LinkML Source

<details>
```yaml
name: wakefield_enable
description: Whether the wakefield named by wakefield_definition is applied. Set false
  to track the element without its wakefield while keeping the definition itself.
from_schema: https://w3id.org/laura/schema
rank: 1000
ifabsent: 'true'
owner: SimulationElement
domain_of:
- SimulationElement
range: boolean

```
</details></div>