# Slot: n_cells 


_Number of cells._



<div data-search-exclude markdown="1">



URI: [laura:n_cells](https://w3id.org/laura/n_cells)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [RFCavityElement](RFCavityElement.md) | RF cavity accelerating-structure parameters |  no  |
| [WakefieldElement](WakefieldElement.md) | Passive wakefield structure parameters |  no  |
| [RFDeflectingCavityElement](RFDeflectingCavityElement.md) | Transverse-deflecting RF cavity parameters -- a subset of RFCavityElement for... |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [Double](Double.md) |
| Domain Of | [RFCavityElement](RFCavityElement.md), [WakefieldElement](WakefieldElement.md), [RFDeflectingCavityElement](RFDeflectingCavityElement.md) |

### Cardinality and Requirements

| Property | Value |
| --- | --- |
### Slot Characteristics

| Property | Value |
| --- | --- |
| If Absent | `float(1)` |


### Value Constraints

| Property | Value |
| --- | --- |
| Minimum Value | 0 |












## Identifier and Mapping Information





### Schema Source


* from schema: https://w3id.org/laura/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | laura:n_cells |
| native | laura:n_cells |




## LinkML Source

<details>
```yaml
name: n_cells
description: Number of cells.
from_schema: https://w3id.org/laura/schema
rank: 1000
ifabsent: float(1)
domain_of:
- RFCavityElement
- WakefieldElement
- RFDeflectingCavityElement
range: double
minimum_value: 0

```
</details></div>