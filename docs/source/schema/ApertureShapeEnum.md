# Enum: ApertureShapeEnum 




_Cross-sectional shape of a beam-pipe aperture. `scraper` is a jaw geometry rather than a pipe shape -- the extents are rectangular, but the jaws are positioned independently, so it maps to ASTRA's Scr_X/Scr_Y (not Col_X/Col_Y) and BDSIM's jcol (not rcol). It therefore has no gmad `apertureType`._



<div data-search-exclude markdown="1">

URI: [laura:ApertureShapeEnum](https://w3id.org/laura/ApertureShapeEnum)

## Permissible Values
| Value | Meaning | Description |
| --- | --- | --- |
| circular | None |  |
| rectangular | None |  |
| elliptical | None |  |
| scraper | None |  |




## Slots

| Name | Description |
| ---  | --- |
| [shape](shape.md) | Cross-sectional aperture shape |










## Identifier and Mapping Information





### Schema Source


* from schema: https://w3id.org/laura/schema






## LinkML Source

<details>
```yaml
name: ApertureShapeEnum
description: Cross-sectional shape of a beam-pipe aperture. `scraper` is a jaw geometry
  rather than a pipe shape -- the extents are rectangular, but the jaws are positioned
  independently, so it maps to ASTRA's Scr_X/Scr_Y (not Col_X/Col_Y) and BDSIM's jcol
  (not rcol). It therefore has no gmad `apertureType`.
from_schema: https://w3id.org/laura/schema
rank: 1000
permissible_values:
  circular:
    text: circular
  rectangular:
    text: rectangular
  elliptical:
    text: elliptical
  scraper:
    text: scraper

```
</details>

</div>