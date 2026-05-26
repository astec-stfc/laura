---
search:
  boost: 5.0
---

# Slot: coupling_cell_length 

<div data-search-exclude markdown="1">



URI: [laura:coupling_cell_length](https://w3id.org/laura/coupling_cell_length)
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
| self | laura:coupling_cell_length |
| native | laura:coupling_cell_length |




## LinkML Source

<details>
```yaml
name: coupling_cell_length
domain_of:
- RFCavityElement
- WakefieldElement
- RFDeflectingCavityElement
range: string

```
</details></div>