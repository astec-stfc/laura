# Slot: structure_type 


_RF structure type (e.g., ``SW`` standing-wave, ``TW`` travelling-wave)._



<div data-search-exclude markdown="1">



URI: [laura:structure_type](https://w3id.org/laura/structure_type)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [RFCavityElement](RFCavityElement.md) | RF cavity accelerating-structure parameters |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [String](String.md) |
| Domain Of | [RFCavityElement](RFCavityElement.md) |

### Cardinality and Requirements

| Property | Value |
| --- | --- |
### Slot Characteristics

| Property | Value |
| --- | --- |
| If Absent | `string(StandingWave)` |
| Owner | [RFCavityElement](RFCavityElement.md) |









## Aliases


* structure_Type




## Identifier and Mapping Information





### Schema Source


* from schema: https://w3id.org/laura/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | laura:structure_type |
| native | laura:structure_type |




## LinkML Source

<details>
```yaml
name: structure_type
description: RF structure type (e.g., ``SW`` standing-wave, ``TW`` travelling-wave).
from_schema: https://w3id.org/laura/schema
aliases:
- structure_Type
rank: 1000
ifabsent: string(StandingWave)
owner: RFCavityElement
domain_of:
- RFCavityElement
range: string

```
</details></div>