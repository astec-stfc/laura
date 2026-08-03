# Slot: species 


_Plasma species name (e.g., ``electron``)._



<div data-search-exclude markdown="1">



URI: [laura:species](https://w3id.org/laura/species)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [PlasmaElement](PlasmaElement.md) | Plasma channel parameters for a laser-driven plasma-accelerator stage |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [String](String.md) |
| Domain Of | [PlasmaElement](PlasmaElement.md) |

### Cardinality and Requirements

| Property | Value |
| --- | --- |
### Slot Characteristics

| Property | Value |
| --- | --- |
| If Absent | `string(electron)` |
| Owner | [PlasmaElement](PlasmaElement.md) |












## Identifier and Mapping Information





### Schema Source


* from schema: https://w3id.org/laura/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | laura:species |
| native | laura:species |




## LinkML Source

<details>
```yaml
name: species
description: Plasma species name (e.g., ``electron``).
from_schema: https://w3id.org/laura/schema
rank: 1000
ifabsent: string(electron)
owner: PlasmaElement
domain_of:
- PlasmaElement
range: string

```
</details></div>