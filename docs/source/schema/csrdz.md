# Slot: csrdz 


_Step size for CSR calculations._



<div data-search-exclude markdown="1">



URI: [laura:csrdz](https://w3id.org/laura/csrdz)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [DriftSimulationElement](DriftSimulationElement.md) | Simulation attributes for field-free drift sections |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [Double](Double.md) |
| Domain Of | [DriftSimulationElement](DriftSimulationElement.md) |

### Cardinality and Requirements

| Property | Value |
| --- | --- |
### Slot Characteristics

| Property | Value |
| --- | --- |
| If Absent | `float(0.01)` |
| Owner | [DriftSimulationElement](DriftSimulationElement.md) |












## Identifier and Mapping Information





### Schema Source


* from schema: https://w3id.org/laura/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | laura:csrdz |
| native | laura:csrdz |




## LinkML Source

<details>
```yaml
name: csrdz
description: Step size for CSR calculations.
from_schema: https://w3id.org/laura/schema
rank: 1000
ifabsent: float(0.01)
owner: DriftSimulationElement
domain_of:
- DriftSimulationElement
range: double

```
</details></div>