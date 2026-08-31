# Enum: LaserProfileTypeEnum 




_Transverse intensity profile model for a laser beam._



<div data-search-exclude markdown="1">

URI: [laura:LaserProfileTypeEnum](https://w3id.org/laura/LaserProfileTypeEnum)

## Permissible Values
| Value | Meaning | Description |
| --- | --- | --- |
| gaussian | None |  |
| laguerre-gaussian | None |  |
| laguerre-gaussian-donut | None | Donut-like Laguerre-Gaussian mode, in which a single azimuthal mode is kept r... |
| flattened-gaussian | None |  |
| file | None |  |




## Slots

| Name | Description |
| ---  | --- |
| [profile_type](profile_type.md) | Transverse intensity profile model |










## Identifier and Mapping Information





### Schema Source


* from schema: https://w3id.org/laura/schema






## LinkML Source

<details>
```yaml
name: LaserProfileTypeEnum
description: Transverse intensity profile model for a laser beam.
from_schema: https://w3id.org/laura/schema
rank: 1000
permissible_values:
  gaussian:
    text: gaussian
  laguerre-gaussian:
    text: laguerre-gaussian
  laguerre-gaussian-donut:
    text: laguerre-gaussian-donut
    description: Donut-like Laguerre-Gaussian mode, in which a single azimuthal mode
      is kept rather than the cosine combination of +m and -m.
  flattened-gaussian:
    text: flattened-gaussian
  file:
    text: file

```
</details>

</div>