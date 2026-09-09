# Enum: LatticeGeometryEnum 




_Whether the reference orbit closes on itself. Mirrors Bmad's ``parameter[geometry]``._



<div data-search-exclude markdown="1">

URI: [laura:LatticeGeometryEnum](https://w3id.org/laura/LatticeGeometryEnum)

## Permissible Values
| Value | Meaning | Description |
| --- | --- | --- |
| open | None | Single-pass beamline such as a linac or transfer line |
| closed | None | Recirculating machine such as a storage ring, for which closed orbits and per... |




## Slots

| Name | Description |
| ---  | --- |
| [geometry](geometry.md) | Whether the reference orbit closes on itself |










## Identifier and Mapping Information





### Schema Source


* from schema: https://w3id.org/laura/schema






## LinkML Source

<details>
```yaml
name: LatticeGeometryEnum
description: Whether the reference orbit closes on itself. Mirrors Bmad's ``parameter[geometry]``.
from_schema: https://w3id.org/laura/schema
rank: 1000
permissible_values:
  open:
    text: open
    description: Single-pass beamline such as a linac or transfer line. Twiss parameters
      propagate from a specified starting condition.
  closed:
    text: closed
    description: Recirculating machine such as a storage ring, for which closed orbits
      and periodic Twiss parameters are computed.

```
</details>

</div>