# Slot: temperature 


_Initial temperature of the plasma species [eV], assumed isotropic and Maxwellian. Zero means a cold plasma, which is the usual assumption for a laser-wakefield stage; a finite value matters where the initial momentum spread competes with the wake, as in a plasma lens or a low-amplitude wake._



<div data-search-exclude markdown="1">



URI: [laura:temperature](https://w3id.org/laura/temperature)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [PlasmaElement](PlasmaElement.md) | Plasma channel parameters for a laser-driven plasma-accelerator stage |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [Float](Float.md) |
| Domain Of | [PlasmaElement](PlasmaElement.md) |

### Cardinality and Requirements

| Property | Value |
| --- | --- |
### Slot Characteristics

| Property | Value |
| --- | --- |
| If Absent | `float(0)` |
| Owner | [PlasmaElement](PlasmaElement.md) |


### Value Constraints

| Property | Value |
| --- | --- |
| Minimum Value | 0 |


<details>
<summary>Additional Constraints</summary>
**Unit:**

| Property | Value |
| --- | --- |
| ucum_code | eV |

</details>











## Identifier and Mapping Information





### Schema Source


* from schema: https://w3id.org/laura/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | laura:temperature |
| native | laura:temperature |




## LinkML Source

<details>
```yaml
name: temperature
description: Initial temperature of the plasma species [eV], assumed isotropic and
  Maxwellian. Zero means a cold plasma, which is the usual assumption for a laser-wakefield
  stage; a finite value matters where the initial momentum spread competes with the
  wake, as in a plasma lens or a low-amplitude wake.
from_schema: https://w3id.org/laura/schema
rank: 1000
ifabsent: float(0)
owner: PlasmaElement
domain_of:
- PlasmaElement
range: float
minimum_value: 0.0
unit:
  ucum_code: eV

```
</details></div>