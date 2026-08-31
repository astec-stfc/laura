# Slot: density_profile_type 


_Shape of the longitudinal density profile used when density_profile is True. ``decaying`` is a 1/(1 + dz/ramp_decay_length)^2 ramp either side of the plateau; ``linear`` ramps linearly over ramp_up and ramp_down; ``tabulated`` interpolates density_profile_positions against density_profile_values; ``custom`` calls density_profile_function._



<div data-search-exclude markdown="1">



URI: [laura:density_profile_type](https://w3id.org/laura/density_profile_type)
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
| If Absent | `string(decaying)` |
| Owner | [PlasmaElement](PlasmaElement.md) |












## Identifier and Mapping Information





### Schema Source


* from schema: https://w3id.org/laura/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | laura:density_profile_type |
| native | laura:density_profile_type |




## LinkML Source

<details>
```yaml
name: density_profile_type
description: Shape of the longitudinal density profile used when density_profile is
  True. ``decaying`` is a 1/(1 + dz/ramp_decay_length)^2 ramp either side of the plateau;
  ``linear`` ramps linearly over ramp_up and ramp_down; ``tabulated`` interpolates
  density_profile_positions against density_profile_values; ``custom`` calls density_profile_function.
from_schema: https://w3id.org/laura/schema
rank: 1000
ifabsent: string(decaying)
owner: PlasmaElement
domain_of:
- PlasmaElement
range: string

```
</details></div>