---
search:
  boost: 5.0
---

# Slot: density_profile 


_If True, use a user-defined profile; if False, use a flat-top model._



<div data-search-exclude markdown="1">



URI: [laura:density_profile](https://w3id.org/laura/density_profile)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [PlasmaElement](PlasmaElement.md) | Plasma channel parameters for a laser-driven plasma-accelerator stage |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [Boolean](Boolean.md) |
| Domain Of | [PlasmaElement](PlasmaElement.md) |

### Cardinality and Requirements

| Property | Value |
| --- | --- |
### Slot Characteristics

| Property | Value |
| --- | --- |
| If Absent | `False` |
| Owner | [PlasmaElement](PlasmaElement.md) |












## Identifier and Mapping Information





### Schema Source


* from schema: https://w3id.org/laura/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | laura:density_profile |
| native | laura:density_profile |




## LinkML Source

<details>
```yaml
name: density_profile
description: If True, use a user-defined profile; if False, use a flat-top model.
from_schema: https://w3id.org/laura/schema
rank: 1000
ifabsent: 'False'
owner: PlasmaElement
domain_of:
- PlasmaElement
range: boolean

```
</details></div>