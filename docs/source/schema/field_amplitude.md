---
search:
  boost: 5.0
---

# Slot: field_amplitude 

<div data-search-exclude markdown="1">



URI: [laura:field_amplitude](https://w3id.org/laura/field_amplitude)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [MagnetSimulationElement](MagnetSimulationElement.md) | Simulation attributes specific to magnets: integrator settings, fringe-field ... |  no  |
| [RFCavitySimulationElement](RFCavitySimulationElement.md) | Simulation attributes for RF cavity elements |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [String](String.md) |
| Domain Of | [MagnetSimulationElement](MagnetSimulationElement.md), [RFCavitySimulationElement](RFCavitySimulationElement.md) |

### Cardinality and Requirements

| Property | Value |
| --- | --- |










## Identifier and Mapping Information






## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | laura:field_amplitude |
| native | laura:field_amplitude |




## LinkML Source

<details>
```yaml
name: field_amplitude
domain_of:
- MagnetSimulationElement
- RFCavitySimulationElement
range: string

```
</details></div>