# Slot: wire_diameter 


_Diameter of the scanning wire [m]._



<div data-search-exclude markdown="1">



URI: [laura:wire_diameter](https://w3id.org/laura/wire_diameter)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [WireScannerDiagnosticElement](WireScannerDiagnosticElement.md) | Intercepting wire-scanner diagnostic: a thin wire swept through the beam to m... |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [Float](Float.md) |
| Domain Of | [WireScannerDiagnosticElement](WireScannerDiagnosticElement.md) |

### Cardinality and Requirements

| Property | Value |
| --- | --- |
### Slot Characteristics

| Property | Value |
| --- | --- |
| If Absent | `float(0.0)` |
| Owner | [WireScannerDiagnosticElement](WireScannerDiagnosticElement.md) |


### Value Constraints

| Property | Value |
| --- | --- |
| Minimum Value | 0 |


<details>
<summary>Additional Constraints</summary>
**Unit:**

| Property | Value |
| --- | --- |
| ucum_code | m |

</details>











## Identifier and Mapping Information





### Schema Source


* from schema: https://w3id.org/laura/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | laura:wire_diameter |
| native | laura:wire_diameter |




## LinkML Source

<details>
```yaml
name: wire_diameter
description: Diameter of the scanning wire [m].
from_schema: https://w3id.org/laura/schema
rank: 1000
ifabsent: float(0.0)
owner: WireScannerDiagnosticElement
domain_of:
- WireScannerDiagnosticElement
range: float
minimum_value: 0
unit:
  ucum_code: m

```
</details></div>