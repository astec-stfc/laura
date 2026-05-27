---
search:
  boost: 5.0
---

# Slot: interpolation_method 


_Interpolation method for ASTRA._



<div data-search-exclude markdown="1">



URI: [laura:interpolation_method](https://w3id.org/laura/interpolation_method)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [WakefieldSimulationElement](WakefieldSimulationElement.md) | Simulation attributes for passive wakefield structures |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [Integer](Integer.md) |
| Domain Of | [WakefieldSimulationElement](WakefieldSimulationElement.md) |

### Cardinality and Requirements

| Property | Value |
| --- | --- |
### Slot Characteristics

| Property | Value |
| --- | --- |
| If Absent | `int(2)` |
| Owner | [WakefieldSimulationElement](WakefieldSimulationElement.md) |












## Identifier and Mapping Information





### Schema Source


* from schema: https://w3id.org/laura/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | laura:interpolation_method |
| native | laura:interpolation_method |




## LinkML Source

<details>
```yaml
name: interpolation_method
description: Interpolation method for ASTRA.
from_schema: https://w3id.org/laura/schema
rank: 1000
ifabsent: int(2)
owner: WakefieldSimulationElement
domain_of:
- WakefieldSimulationElement
range: integer

```
</details></div>