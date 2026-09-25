# Enum: NumericDtypeEnum 




_Numeric storage type of a control variable's value, or of an individual element of a waveform's array._



<div data-search-exclude markdown="1">

URI: [laura:NumericDtypeEnum](https://w3id.org/laura/NumericDtypeEnum)

## Permissible Values
| Value | Meaning | Description |
| --- | --- | --- |
| int8 | None | Signed 8-bit integer |
| int16 | None | Signed 16-bit integer |
| int32 | None | Signed 32-bit integer |
| int64 | None | Signed 64-bit integer |
| uint8 | None | Unsigned 8-bit integer |
| uint16 | None | Unsigned 16-bit integer |
| uint32 | None | Unsigned 32-bit integer |
| uint64 | None | Unsigned 64-bit integer |
| float32 | None | Single-precision float |
| float64 | None | Double-precision float |




## Slots

| Name | Description |
| ---  | --- |
| [element_dtype](element_dtype.md) | Numeric type of the value, or of one element of the array for ``control_type:... |










## Identifier and Mapping Information





### Schema Source


* from schema: https://w3id.org/laura/schema






## LinkML Source

<details>
```yaml
name: NumericDtypeEnum
description: Numeric storage type of a control variable's value, or of an individual
  element of a waveform's array.
from_schema: https://w3id.org/laura/schema
rank: 1000
permissible_values:
  int8:
    text: int8
    description: Signed 8-bit integer.
  int16:
    text: int16
    description: Signed 16-bit integer.
  int32:
    text: int32
    description: Signed 32-bit integer.
  int64:
    text: int64
    description: Signed 64-bit integer.
  uint8:
    text: uint8
    description: Unsigned 8-bit integer.
  uint16:
    text: uint16
    description: Unsigned 16-bit integer.
  uint32:
    text: uint32
    description: Unsigned 32-bit integer.
  uint64:
    text: uint64
    description: Unsigned 64-bit integer.
  float32:
    text: float32
    description: Single-precision float.
  float64:
    text: float64
    description: Double-precision float.

```
</details>

</div>