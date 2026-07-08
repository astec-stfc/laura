---
search:
  boost: 5.0
---

# Slot: field_amplitude 


_Field amplitude scaling._



<div data-search-exclude markdown="1">



URI: [laura:field_amplitude](https://w3id.org/laura/field_amplitude)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [MagnetSimulationElement](MagnetSimulationElement.md) | Simulation attributes specific to magnets: integrator settings, fringe-field ... |  yes  |
| [RFCavitySimulationElement](RFCavitySimulationElement.md) | Simulation attributes for RF cavity elements |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [Float](Float.md) |
| Domain Of | [MagnetSimulationElement](MagnetSimulationElement.md), [RFCavitySimulationElement](RFCavitySimulationElement.md) |

### Cardinality and Requirements

| Property | Value |
| --- | --- |










## Identifier and Mapping Information





### Schema Source


* from schema: https://w3id.org/laura/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | laura:field_amplitude |
| native | laura:field_amplitude |




## LinkML Source

<details>
```yaml
name: field_amplitude
description: Field amplitude scaling.
from_schema: https://w3id.org/laura/schema
rank: 1000
domain_of:
- MagnetSimulationElement
- RFCavitySimulationElement
range: float

```
</details></div>