---
search:
  boost: 5.0
---

# Slot: smooth 

<div data-search-exclude markdown="1">



URI: [laura:smooth](https://w3id.org/laura/smooth)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [MagnetSimulationElement](MagnetSimulationElement.md) | Simulation attributes specific to magnets: integrator settings, fringe-field ... |  no  |
| [RFCavitySimulationElement](RFCavitySimulationElement.md) | Simulation attributes for RF cavity elements |  no  |
| [WakefieldSimulationElement](WakefieldSimulationElement.md) | Simulation attributes for passive wakefield structures |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [String](String.md) |
| Domain Of | [MagnetSimulationElement](MagnetSimulationElement.md), [RFCavitySimulationElement](RFCavitySimulationElement.md), [WakefieldSimulationElement](WakefieldSimulationElement.md) |

### Cardinality and Requirements

| Property | Value |
| --- | --- |










## Identifier and Mapping Information






## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | laura:smooth |
| native | laura:smooth |




## LinkML Source

<details>
```yaml
name: smooth
domain_of:
- MagnetSimulationElement
- RFCavitySimulationElement
- WakefieldSimulationElement
range: string

```
</details></div>