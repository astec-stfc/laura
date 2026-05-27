---
search:
  boost: 5.0
---

# Slot: power_calibration 


_Calibration constant relating measured power to cavity gradient._



<div data-search-exclude markdown="1">



URI: [laura:power_calibration](https://w3id.org/laura/power_calibration)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [RFCavityElement](RFCavityElement.md) | RF cavity accelerating-structure parameters |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [Float](Float.md) |
| Domain Of | [RFCavityElement](RFCavityElement.md) |

### Cardinality and Requirements

| Property | Value |
| --- | --- |
| Multivalued | Yes |
### Slot Characteristics

| Property | Value |
| --- | --- |
| Owner | [RFCavityElement](RFCavityElement.md) |












## Identifier and Mapping Information





### Schema Source


* from schema: https://w3id.org/laura/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | laura:power_calibration |
| native | laura:power_calibration |




## LinkML Source

<details>
```yaml
name: power_calibration
description: Calibration constant relating measured power to cavity gradient.
from_schema: https://w3id.org/laura/schema
rank: 1000
owner: RFCavityElement
domain_of:
- RFCavityElement
range: float
multivalued: true

```
</details></div>