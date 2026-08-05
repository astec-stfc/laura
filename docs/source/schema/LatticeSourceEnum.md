# Enum: LatticeSourceEnum 




_Where the values in a machine model came from, which decides how far they can be trusted as a description of the real machine._



<div data-search-exclude markdown="1">

URI: [laura:LatticeSourceEnum](https://w3id.org/laura/LatticeSourceEnum)

## Permissible Values
| Value | Meaning | Description |
| --- | --- | --- |
| design | None | Design values; never read from hardware |
| measured | None | Read back from the machine at a point in time |
| simulated | None | Produced by a tracking or simulation code |




## Slots

| Name | Description |
| ---  | --- |
| [source](source.md) | Whether these values are design, measured or simulated |










## Identifier and Mapping Information





### Schema Source


* from schema: https://w3id.org/laura/schema






## LinkML Source

<details>
```yaml
name: LatticeSourceEnum
description: Where the values in a machine model came from, which decides how far
  they can be trusted as a description of the real machine.
from_schema: https://w3id.org/laura/schema
rank: 1000
permissible_values:
  design:
    text: design
    description: Design values; never read from hardware.
  measured:
    text: measured
    description: Read back from the machine at a point in time.
  simulated:
    text: simulated
    description: Produced by a tracking or simulation code.

```
</details>

</div>