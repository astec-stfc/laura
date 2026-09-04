# Enum: LatticeTypeEnum 




_What a section or layout carries.  Mirrors ``laura.models.elementList.LatticeType``._



<div data-search-exclude markdown="1">

URI: [laura:LatticeTypeEnum](https://w3id.org/laura/LatticeTypeEnum)

## Permissible Values
| Value | Meaning | Description |
| --- | --- | --- |
| beam | None | A beamline |
| rf | None | An RF distribution line |
| laser | None | A laser transport line |




## Slots

| Name | Description |
| ---  | --- |
| [section_type](section_type.md) | What this section carries |
| [layout_type](layout_type.md) | What this layout carries |










## Identifier and Mapping Information





### Schema Source


* from schema: https://w3id.org/laura/schema






## LinkML Source

<details>
```yaml
name: LatticeTypeEnum
description: What a section or layout carries.  Mirrors ``laura.models.elementList.LatticeType``.
from_schema: https://w3id.org/laura/schema
rank: 1000
permissible_values:
  beam:
    text: beam
    description: A beamline.
  rf:
    text: rf
    description: An RF distribution line.
  laser:
    text: laser
    description: A laser transport line.

```
</details>

</div>