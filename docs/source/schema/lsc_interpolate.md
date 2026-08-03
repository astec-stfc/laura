# Slot: lsc_interpolate 


_Flag to allow interpolation of computed LSC wake._



<div data-search-exclude markdown="1">



URI: [laura:lsc_interpolate](https://w3id.org/laura/lsc_interpolate)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [DriftSimulationElement](DriftSimulationElement.md) | Simulation attributes for field-free drift sections |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [Integer](Integer.md) |
| Domain Of | [DriftSimulationElement](DriftSimulationElement.md) |

### Cardinality and Requirements

| Property | Value |
| --- | --- |
### Slot Characteristics

| Property | Value |
| --- | --- |
| If Absent | `int(1)` |
| Owner | [DriftSimulationElement](DriftSimulationElement.md) |












## Identifier and Mapping Information





### Schema Source


* from schema: https://w3id.org/laura/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | laura:lsc_interpolate |
| native | laura:lsc_interpolate |




## LinkML Source

<details>
```yaml
name: lsc_interpolate
description: Flag to allow interpolation of computed LSC wake.
from_schema: https://w3id.org/laura/schema
rank: 1000
ifabsent: int(1)
owner: DriftSimulationElement
domain_of:
- DriftSimulationElement
range: integer

```
</details></div>