# Slot: reference_energy 


_Reference total energy of the design particle [eV]._



<div data-search-exclude markdown="1">



URI: [laura:reference_energy](https://w3id.org/laura/reference_energy)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [SectionLattice](SectionLattice.md) | An ordered list of element names defining a contiguous beamline section |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [Float](Float.md) |
| Domain Of | [SectionLattice](SectionLattice.md) |

### Cardinality and Requirements

| Property | Value |
| --- | --- |
### Slot Characteristics

| Property | Value |
| --- | --- |
| Owner | [SectionLattice](SectionLattice.md) |


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
| self | laura:reference_energy |
| native | laura:reference_energy |




## LinkML Source

<details>
```yaml
name: reference_energy
description: Reference total energy of the design particle [eV].
from_schema: https://w3id.org/laura/schema
rank: 1000
owner: SectionLattice
domain_of:
- SectionLattice
range: float
required: false
minimum_value: 0.0
unit:
  ucum_code: eV

```
</details></div>