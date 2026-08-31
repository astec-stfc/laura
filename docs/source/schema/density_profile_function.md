# Slot: density_profile_function 


_Dotted path to a callable ``f(z, r) -> relative density``, written as ``package.module:function`` or ``package.module.function``. Used when density_profile_type is ``custom``._



<div data-search-exclude markdown="1">



URI: [laura:density_profile_function](https://w3id.org/laura/density_profile_function)
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
| Owner | [PlasmaElement](PlasmaElement.md) |












## Identifier and Mapping Information





### Schema Source


* from schema: https://w3id.org/laura/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | laura:density_profile_function |
| native | laura:density_profile_function |




## LinkML Source

<details>
```yaml
name: density_profile_function
description: Dotted path to a callable ``f(z, r) -> relative density``, written as
  ``package.module:function`` or ``package.module.function``. Used when density_profile_type
  is ``custom``.
from_schema: https://w3id.org/laura/schema
rank: 1000
owner: PlasmaElement
domain_of:
- PlasmaElement
range: string

```
</details></div>