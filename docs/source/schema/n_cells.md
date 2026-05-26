---
search:
  boost: 5.0
---

# Slot: n_cells 

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
| Range | [String](String.md) |
| Domain Of | [RFCavityElement](RFCavityElement.md), [WakefieldElement](WakefieldElement.md), [RFDeflectingCavityElement](RFDeflectingCavityElement.md) |

### Cardinality and Requirements

| Property | Value |
| --- | --- |










## Identifier and Mapping Information






## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | laura:n_cells |
| native | laura:n_cells |




## LinkML Source

<details>
```yaml
name: n_cells
domain_of:
- RFCavityElement
- WakefieldElement
- RFDeflectingCavityElement
range: string

```
</details></div>