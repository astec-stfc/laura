---
search:
  boost: 5.0
---

# Slot: radius 

<div data-search-exclude markdown="1">



URI: [laura:radius](https://w3id.org/laura/radius)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [Multipole](Multipole.md) | Individual multipole field component, characterised by order and integrated n... |  no  |
| [ApertureElement](ApertureElement.md) | Transverse aperture geometry for drift-space checks and collimators |  no  |
| [CameraMask](CameraMask.md) | Camera analysis mask parameters |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [String](String.md) |
| Domain Of | [Multipole](Multipole.md), [ApertureElement](ApertureElement.md), [CameraMask](CameraMask.md) |

### Cardinality and Requirements

| Property | Value |
| --- | --- |










## Identifier and Mapping Information






## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | laura:radius |
| native | laura:radius |




## LinkML Source

<details>
```yaml
name: radius
domain_of:
- Multipole
- ApertureElement
- CameraMask
range: string

```
</details></div>