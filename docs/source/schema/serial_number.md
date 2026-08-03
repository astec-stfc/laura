# Slot: serial_number 


_Manufacturer serial number._



<div data-search-exclude markdown="1">



URI: [schema:serialNumber](http://schema.org/serialNumber)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [ManufacturerElement](ManufacturerElement.md) | Manufacturer and serial-number metadata |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [String](String.md) |
| Domain Of | [ManufacturerElement](ManufacturerElement.md) |
| Slot URI | [schema:serialNumber](http://schema.org/serialNumber) |

### Cardinality and Requirements

| Property | Value |
| --- | --- |
### Slot Characteristics

| Property | Value |
| --- | --- |
| If Absent | `string()` |
| Owner | [ManufacturerElement](ManufacturerElement.md) |












## Identifier and Mapping Information





### Schema Source


* from schema: https://w3id.org/laura/schema




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | schema:serialNumber |
| native | laura:serial_number |




## LinkML Source

<details>
```yaml
name: serial_number
description: Manufacturer serial number.
from_schema: https://w3id.org/laura/schema
rank: 1000
slot_uri: schema:serialNumber
ifabsent: string()
owner: ManufacturerElement
domain_of:
- ManufacturerElement
range: string

```
</details></div>