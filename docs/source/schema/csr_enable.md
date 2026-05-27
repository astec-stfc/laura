---
search:
  boost: 5.0
---

# Slot: csr_enable 

<div data-search-exclude markdown="1">



URI: [laura:csr_enable](https://w3id.org/laura/csr_enable)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [MagnetSimulationElement](MagnetSimulationElement.md) | Simulation attributes specific to magnets: integrator settings, fringe-field ... |  no  |
| [DriftSimulationElement](DriftSimulationElement.md) | Simulation attributes for field-free drift sections |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [String](String.md) |
| Domain Of | [MagnetSimulationElement](MagnetSimulationElement.md), [DriftSimulationElement](DriftSimulationElement.md) |

### Cardinality and Requirements

| Property | Value |
| --- | --- |










## Identifier and Mapping Information






## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | laura:csr_enable |
| native | laura:csr_enable |




## LinkML Source

<details>
```yaml
name: csr_enable
domain_of:
- MagnetSimulationElement
- DriftSimulationElement
range: string

```
</details></div>