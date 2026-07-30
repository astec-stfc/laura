# LAURA Model Files: Detailed Breakdown

## 1. laura/models/element.py

### baseElement class

| Method/Property | Classification | Notes | Essential? | Backwards-compat burden |
|---|---|---|---|---|
| `validate_name()` | Validators | Field validator for `name` field; validates string format. Currently commented out, so minimal logic | NO - can be removed | LOW |
| `validate_alias()` | Validators | Converts alias input (str/list/dict) to list format; handles normalization | **YES** - breaks YAML parsing if removed | **HIGH** |
| `validate_subelement()` | Validators | Converts True→"", False→None; normalizes subelement field | YES - core logic | **HIGH** |
| `escape_string_list()` | Utility | Creates YAML-quoted string from list; used in export | NO - output only | LOW |
| `from_CATAP()` | Utility | Passthrough class method; bridges CATAP loader | NO - redundant, just `cls(**fields)` | LOW |
| `_resolve_attribute_path()` | Attribute cascading | Finds full nested path for an attribute name; core to cascading | **YES** - essential | **HIGH** |
| `_find_field_paths()` | Attribute cascading | Recursive search through nested Pydantic models; finds all paths | **YES** - essential | **HIGH** |
| `_get_nested_attribute()` | Attribute cascading | Traverses tuple path to retrieve nested value | **YES** - essential | **HIGH** |
| `_set_nested_attribute()` | Attribute cascading | Traverses tuple path to set nested value | **YES** - essential | **HIGH** |
| `__getattr__()` | Attribute cascading | Custom getter; resolves nested attributes by name; enables flattened access | **YES** - core feature | **HIGH** |
| `__setattr__()` | Attribute cascading | Custom setter; cascades updates, handles nested assignment | **YES** - core feature | **HIGH** |
| `_handle_cascading_updates()` | Attribute cascading | Applies CASCADING_RULES when attributes change | PARTIAL - only used if rules defined; currently empty dict | MEDIUM |
| `no_controls` | Custom property | Returns repr without `controls` field; debugging aid | NO - utility only | LOW |
| `subdirectory` | Custom property | Computes file path based on hardware_class/type; used in export | YES - essential for file I/O | **HIGH** |
| `YAML_filename` | Custom property | Combines subdirectory + name; used in export | YES - essential for file I/O | **HIGH** |
| `hardware_info` | Custom property | Dict of {class, type}; convenient accessor | NO - direct field access is simple | LOW |
| `flat()` | Utility method | Flattens nested dict with "_" separator; used in exports/queries | NO - can be standalone function | MEDIUM |
| `is_subelement()` | Utility method | Returns bool if element is sub-element; used in layout calculations | YES - functional logic | **HIGH** |

**Summary**: Attribute cascading infrastructure (__getattr__/__setattr__/path-finding) is **essential** and tightly integrated. Validators and file-path properties are **essential** for schema wrapping and I/O. Utility methods are **optional** but convenient.

---

### Element class

| Method/Property | Classification | Notes | Essential? | Backwards-compat burden |
|---|---|---|---|---|
| Field overrides: simulation, electrical, manufacturer, controls, reference | Field definitions | Auto-constructing default factories; convenience | YES - schema extension | **HIGH** |
| `update_from_controls()` | Utility method | Applies control system data to element; thin wrapper | NO - could be in controls module | MEDIUM |

---

### PhysicalBaseElement class

| Method/Property | Classification | Notes | Essential? | Backwards-compat burden |
|---|---|---|---|---|
| Field override: physical | Field definition | Uses PhysicalElement directly instead of schema base | YES - type consistency | **HIGH** |
| `bend_angle` | Custom property | Returns [0,0,0] Rotation; marked with TODO (incomplete) | NO - placeholder | LOW |
| `start_angle` | Custom property | Adds rotation + global_rotation; incomplete | NO - placeholder | LOW |
| `end_angle` | Custom property | Same as start_angle; incomplete | NO - placeholder | LOW |

---

### Magnet class

| Method/Property | Classification | Notes | Essential? | Backwards-compat burden |
|---|---|---|---|---|
| Field overrides: hardware_class, degauss, simulation, magnetic, physical | Field definitions | Type overrides, default factories | YES - schema extension | **HIGH** |
| `bend_angle` | Custom property | **Overrides** PhysicalBaseElement; uses magnetic.angle if available | YES - corrects incomplete parent | **HIGH** |
| `end_angle` | Custom property | Returns start_angle + bend_angle; corrects parent | YES - corrects incomplete parent | **HIGH** |

**Note**: Magnet class fixes incomplete properties from PhysicalBaseElement; suggests parent needs redesign.

---

### Concrete Magnet Types (Dipole, Quadrupole, etc.)

| Class | Key Implementation | Notes |
|---|---|---|
| All 8 classes | Field overrides only | hardware_type (frozen), magnetic type (type-specific), some have specialized fields |
| Dipole | `__init__()` sets `physical._parent = self` | Enables parent backref in computed_field |

**No methods beyond field definitions** (except Dipole.__init__ for parent linkage).

---

## 2. laura/models/physical.py

### Position class

| Method/Property | Classification | Notes | Essential? | Backwards-compat burden |
|---|---|---|---|---|
| `ser_model()` | Serialization override | Custom JSON serializer; converts [x,y,z] to list format | YES - API contract | **HIGH** |
| `array` | Custom property | Returns numpy array [x,y,z]; convenience | NO - can use `list(position)` instead | MEDIUM |
| `from_list()` | Constructor variant | Alternate constructor from 3-element list | NO - convenience only | LOW |
| `from_values()` | Constructor variant | Alternate constructor from 3 args | NO - convenience only | LOW |
| `__iter__()` | Dunder | Makes Position iterable; essential for `list(position)` pattern | YES - widely used | **HIGH** |
| `__eq__()` | Dunder | Custom equality; treats 0/None as zero vector | YES - semantic equality | **HIGH** |
| `__add__()` | Dunder | Vector addition | NO - utility math only | LOW |
| `__radd__()` | Dunder | Reverse vector addition | NO - utility math only | LOW |
| `__sub__()` | Dunder | Vector subtraction | NO - utility math only | LOW |
| `__rsub__()` | Dunder | Reverse vector subtraction | NO - utility math only | LOW |
| `dot()` | Method | Dot product; converts list to Position if needed | NO - utility math | LOW |
| `vector_angle()` | Method | Angle between vectors | NO - utility math | LOW |
| `length()` | Method | Vector length (norm) | NO - utility math | LOW |

**Summary**: `__iter__`, serializer, and __eq__ are **essential** for LAURA's data flow. Math methods are **optional utilities**.

---

### Rotation class

| Method/Property | Classification | Notes | Essential? | Backwards-compat burden |
|---|---|---|---|---|
| `ser_model()` | Serialization override | Custom JSON serializer; [phi,psi,theta] list format | YES - API contract | **HIGH** |
| `array` | Custom property | Returns numpy array | NO - convenience | MEDIUM |
| `from_list()` | Constructor variant | 3-element list constructor | NO - convenience | LOW |
| `from_values()` | Constructor variant | 3-arg constructor | NO - convenience | LOW |
| `__iter__()` | Dunder | Makes iterable; essential for `list(rotation)` | YES - widely used | **HIGH** |
| `__eq__()` | Dunder | Custom equality; treats 0/None as zero rotation | YES - semantic | **HIGH** |
| `__add__()` | Dunder | Rotation addition | NO - utility | LOW |
| `__radd__()` | Dunder | Reverse rotation addition | NO - utility | LOW |
| `__sub__()` | Dunder | Rotation subtraction | NO - utility | LOW |
| `__rsub__()` | Dunder | Reverse rotation subtraction | NO - utility | LOW |
| `__abs__()` | Dunder | Absolute rotation values | NO - utility | LOW |
| `__gt__()` | Dunder | Greater-than comparison (any component) | NO - utility | LOW |

**Summary**: Same pattern as Position; serializer/iter/eq are **essential**, math ops are **optional**.

---

### ElementError class

| Method/Property | Classification | Notes | Essential? | Backwards-compat burden |
|---|---|---|---|---|
| `validate_position()` | Validators | Converts list/dict/ndarray to Position; flexible input | YES - schema wrapping | **HIGH** |
| `validate_rotation()` | Validators | Converts list/dict/ndarray to Rotation; flexible input | YES - schema wrapping | **HIGH** |
| `__str__()` | Dunder | Repr of non-zero fields only; debugging | NO - convenience | LOW |
| `__repr__()` | Dunder | Formatted repr | NO - convenience | LOW |
| `__eq__()` | Dunder | Treats 0 as zero error; semantic equality | YES - functional | **HIGH** |

---

### ElementSurvey class

| Method/Property | Classification | Notes | Essential? | Backwards-compat burden |
|---|---|---|---|---|
| (empty) | Inheritance only | Inherits all from ElementError | N/A | N/A |

---

### PhysicalElement class

| Method/Property | Classification | Notes | Essential? | Backwards-compat burden |
|---|---|---|---|---|
| Field override: middle | Field definition | Alias "position"/"centre"; flexible input | YES - schema wrapping | **HIGH** |
| Field overrides: datum, rotation, global_rotation, error, survey, max/min_position | Field definitions | Core physical data | YES - essential | **HIGH** |
| `_parent` | PrivateAttr | Back-reference to parent element; enables computed angle | YES - essential for angle calc | **HIGH** |
| `__str__()` | Dunder | Repr of non-zero fields | NO - convenience | LOW |
| `__repr__()` | Dunder | Formatted repr | NO - convenience | LOW |
| `_physical_angle` | computed_field | **CRITICAL**: Looks up parent.magnetic.angle; enables bend_angle/start/end calculations | **YES** - essential | **VERY HIGH** |
| `validate_middle()` | Validators | Converts float/list/dict to Position; flexible input | YES - schema wrapping | **HIGH** |
| `validate_rotation()` | Validators | Converts float/list/dict to Rotation; flexible input | YES - schema wrapping | **HIGH** |
| `rotation_matrix` | Custom property | **CRITICAL**: Computes combined rotation matrix (yaw/pitch/roll); cached; used in all position calculations | **YES** - essential | **VERY HIGH** |
| `rotated_position()` | Method | Applies rotation_matrix to vector; core to start/end calculations | **YES** - essential | **VERY HIGH** |
| `start` | Custom property | **CRITICAL**: Computes element start position using rotation_matrix and length; handles bent vs straight | **YES** - essential | **VERY HIGH** |
| `end` | Custom property | **CRITICAL**: Computes element end position using rotation_matrix and length | **YES** - essential | **VERY HIGH** |

**Summary**: PhysicalElement is **heavily algorithmic**. start, end, rotation_matrix, _physical_angle are **critical** for lattice geometry. Cannot be removed.

---

## 3. laura/models/magnetic.py

### Multipole class

| Method/Property | Classification | Notes | Essential? | Backwards-compat burden |
|---|---|---|---|---|
| (empty) | Wrapper only | Inherits from _MultipoleBase; no new logic | N/A | N/A |

---

### Multipoles class

| Method/Property | Classification | Notes | Essential? | Backwards-compat burden |
|---|---|---|---|---|
| Field definitions | Generated | K0L through K4L fields created dynamically | YES - schema definition | **HIGH** |
| `validate_Multipole()` | Validators | Converts list/dict to Multipole; flexible input | YES - schema wrapping | **HIGH** |
| `__str__()` | Dunder | Lists non-zero multipoles | NO - debugging only | LOW |
| `__repr__()` | Dunder | Formatted repr | NO - debugging only | LOW |
| `ser_model()` | model_serializer | Returns all K*L fields as dict | YES - serialization | **HIGH** |
| `normal()` | Utility method | Getter for normal component at order; convenience | YES - widely used | **HIGH** |
| `skew()` | Utility method | Getter for skew component at order; convenience | YES - widely used | **HIGH** |
| `__eq__()` | Dunder | Compares serialized dicts | YES - functional | **HIGH** |

**Summary**: normal()/skew() are **essential** conveniences used throughout. Serializer is **essential** for API/export.

---

### FieldIntegral class

| Method/Property | Classification | Notes | Essential? | Backwards-compat burden |
|---|---|---|---|---|
| Field override: coefficients | Field definition | Default [0] instead of schema's []; non-empty default | YES - schema wrapping | **HIGH** |
| `currentToK()` | Utility/Conversion | **CRITICAL**: Converts magnet current to K value using polynomial + speed of light scaling; core to magnet control | **YES** - essential | **VERY HIGH** |
| `__iter__()` | Dunder | Makes coefficients iterable | NO - convenience | LOW |

---

### LinearSaturationFit class

| Method/Property | Classification | Notes | Essential? | Backwards-compat burden |
|---|---|---|---|---|
| `_COEFF_KEYS` | ClassVar | Ordered list [m, I_max, f, a, I0, d, L]; defines calibration structure | YES - schema wrapping | **HIGH** |
| `order` | Field override | Magnet order; set by MagneticElement.__init__; excluded from serialization | YES - enables scaling | **HIGH** |
| `coefficients` | Custom property | Returns [m, I_max, f, a, I0, d, L] as list; convenience | NO - simple attribute access | MEDIUM |
| `from_string()` | Constructor variant | Parses CSV string to coefficients; used in YAML loading | YES - YAML parsing | **HIGH** |
| `update_from_string()` | Method | Updates coefficients from CSV string | NO - utility only | MEDIUM |
| `currentToK()` | Utility/Conversion | **CRITICAL**: Converts current to K with linear+saturation model; includes order-dependent scaling (1e9 vs 1e6) | **YES** - essential | **VERY HIGH** |
| `KLToCurrent()` | Utility/Conversion | **CRITICAL**: Inverse of currentToK (K→current); includes saturation handling; uses cubic solver | **YES** - essential | **VERY HIGH** |
| `KToCurrent()` | Utility/Conversion | **CRITICAL**: Inverse conversion; removes scaling based on order | **YES** - essential | **VERY HIGH** |
| `__iter__()` | Dunder | Makes coefficients iterable | NO - convenience | LOW |

**Summary**: Conversion methods are **critical** for magnet control. order-dependent scaling is **essential** and fragile.

---

### MagneticElement class

| Method/Property | Classification | Notes | Essential? | Backwards-compat burden |
|---|---|---|---|---|
| Field definitions | Core fields | order, skew, length, multipoles, field_integral_coefficients, etc. | YES - schema definition | **HIGH** |
| `__init__()` | Constructor override | **CRITICAL**: Propagates order to LinearSaturationFit; auto-creates Multipoles if strength data provided; sets kl/angle if given | **YES** - essential | **VERY HIGH** |
| `validate_field_integral_coefficients()` | Validators | Converts string/list/dict to FieldIntegral | YES - schema wrapping | **HIGH** |
| `KnL()` | Utility method | Gets integrated strength (KnL) for order; handles skew vs normal | YES - widely used | **HIGH** |
| `Kn()` | Utility method | Gets normalized K for order; divides KnL by length | YES - commonly used | **HIGH** |
| `kl` | Custom property (getter) | Returns KnL(self.order); convenience for main strength | YES - essential | **HIGH** |
| `kl` | Custom property (setter) | Sets normal/skew in K*L field; creates Multipoles if needed | YES - essential | **HIGH** |
| `half_gap` | computed_field | Returns gap/2; convenience | NO - trivial math | LOW |
| `get_gradient()` | Utility method | Returns gradient; if not set explicitly, calculates from K·Brho/L | YES - functional | **HIGH** |
| `currentToK()` | Proxy method | Delegates to linear_saturation_coefficients.currentToK() | YES - API passthrough | **HIGH** |
| `KToCurrent()` | Proxy method | Delegates to linear_saturation_coefficients.KToCurrent() | YES - API passthrough | **HIGH** |
| `KLToCurrent()` | Proxy method | Delegates to linear_saturation_coefficients.KLToCurrent() | YES - API passthrough | **HIGH** |

**Summary**: __init__() is **critical** for schema wrapping. KnL/kl/get_gradient are **essential**. Proxy methods keep API clean.

---

### Dipole_Magnet class

| Method/Property | Classification | Notes | Essential? | Backwards-compat burden |
|---|---|---|---|---|
| `order` | Field override | Fixed to 0 (dipole) | YES - type definition | **HIGH** |
| `angle` | Custom property (getter) | Returns KnL(order=0); semantic convenience | YES - dipole-specific | **HIGH** |
| `angle` | Custom property (setter) | Sets K0L.normal in multipoles | YES - dipole-specific | **HIGH** |
| `currentToAngle()` | Utility method | Converts current→angle in degrees; specialized for dipoles | YES - dipole-specific | **HIGH** |
| `currentToK()` | Override | **CRITICAL**: Wraps parent; applies /1000 scaling (dipole uses mT·m/A); adds "degrees" key | **YES** - order-dependent scaling | **VERY HIGH** |
| `KToCurrent()` | Override | **CRITICAL**: Reverses /1000 scaling from currentToK() | **YES** - order-dependent scaling | **VERY HIGH** |
| `KLToCurrent()` | Override | **CRITICAL**: Reverses /1000 scaling from currentToK() | **YES** - order-dependent scaling | **VERY HIGH** |
| `rho` | computed_field | Bend radius l/θ; used in field calculations | YES - dipole-specific | **HIGH** |
| `field_strength()` | Utility method | Magnetic field strength ρ·Brho/L | YES - dipole-specific | **HIGH** |

**Summary**: Dipole overrides core scaling (/1000 for mT·m/A); **critical** and fragile. Cannot be removed.

---

### Quadrupole_Magnet, Sextupole_Magnet, Octupole_Magnet classes

| Method/Property | Classification | Notes | Essential? | Backwards-compat burden |
|---|---|---|---|---|
| `order` | Field override | Fixed to 1, 2, 3 respectively | YES - type definition | **HIGH** |
| `k1l`, `k2l`, `k3l` | Custom properties | Convenience aliases for kl; order-specific getters/setters | NO - kl can be used directly | MEDIUM |

**Summary**: k*l properties are **optional but convenient**.

---

### SolenoidFields class

| Method/Property | Classification | Notes | Essential? | Backwards-compat burden |
|---|---|---|---|---|
| Field definitions | Generated | S0L through S12L created dynamically | YES - schema definition | **HIGH** |
| `__repr__()` | Dunder | Formatted repr | NO - debugging | LOW |
| `ser_model()` | model_serializer | Returns all S*L fields as dict | YES - serialization | **HIGH** |
| `normal()` | Utility method | Getter for solenoid field at order | YES - widely used | **HIGH** |
| `__eq__()` | Dunder | Compares serialized dicts | YES - functional | **HIGH** |

**Summary**: Similar pattern to Multipoles; serializer and normal() are **essential**.

---

### Solenoid_Magnet class

| Method/Property | Classification | Notes | Essential? | Backwards-compat burden |
|---|---|---|---|---|
| Field definitions | Core fields | length, order, fields, systematic/random fields, coefficients, settle_time | YES - schema definition | **HIGH** |
| `__init__()` | Constructor override | Handles ks / field_amplitude aliases; auto-sets S*L field | YES - schema wrapping | **HIGH** |
| `validate_field_integral_coefficients()` | Validators | Converts string/list/dict to FieldIntegral | YES - schema wrapping | **HIGH** |
| `field_amplitude` | Custom property (getter) | Returns ks/length; convenience | NO - arithmetic only | LOW |
| `field_amplitude` | Custom property (setter) | Sets ks = fa·length | NO - arithmetic only | LOW |
| `ks` | Custom property (getter) | Returns S*L field value; convenience | YES - commonly used | **HIGH** |
| `ks` | Custom property (setter) | Sets S*L field value; convenience | YES - commonly used | **HIGH** |

**Summary**: __init__ is **essential** for schema wrapping. ks/field_amplitude are **convenience properties**.

---

### NonLinearLens_Magnet class

| Method/Property | Classification | Notes | Essential? | Backwards-compat burden |
|---|---|---|---|---|
| Field definitions | Core fields | length, integrated_strength (knll alias), dimensional_parameter (cnll alias) | YES - schema definition | **HIGH** |
| `__init__()` | Constructor | Empty passthrough; no custom logic | NO - not needed | LOW |

**Summary**: Minimal implementation; __init__() can be removed.

---

### Wiggler_Magnet class

| Method/Property | Classification | Notes | Essential? | Backwards-compat burden |
|---|---|---|---|---|
| Field definitions | Core fields | length, strength (K alias), peak_magnetic_field (B alias), period, num_periods, helical, roll-off/gradient params | YES - schema definition | **HIGH** |
| `__init__()` | Constructor | Empty passthrough; no custom logic | NO - not needed | LOW |
| `normalized_strength` | Custom property (getter) | Returns strength/√2 if planar, else strength; physics convention | YES - physically correct | **HIGH** |
| `normalized_strength` | Custom property (setter) | Inverse calculation; stores as strength | YES - physically correct | **HIGH** |
| `poles` | Custom property (getter) | Returns 2·num_periods; convenience | NO - arithmetic only | LOW |
| `poles` | Custom property (setter) | Sets num_periods = poles/2; convenience | NO - arithmetic only | LOW |

**Summary**: normalized_strength is **essential** for physics correctness. poles is **optional**.

---

## CROSS-FILE PATTERN ANALYSIS

### Critical Architectural Dependencies

1. **Attribute Cascading (element.py)**
   - `__getattr__/__setattr__` enable flattened access to nested fields
   - Underpins element.simulation.field → element.field shortcuts
   - **Cannot be removed** without breaking existing code

2. **Position/Rotation Serialization (physical.py)**
   - ser_model() converts to/from [x,y,z] / [phi,psi,theta] lists
   - **API contract** for JSON export
   - **Cannot be changed** without breaking clients

3. **Rotation Matrix + Position Geometry (physical.py)**
   - rotation_matrix, start, end form trilogy of interdependent calculations
   - **Cannot be removed** — entire lattice geometry depends on this

4. **Order-Dependent Scaling (magnetic.py)**
   - Dipole_Magnet applies /1000 to currentToK/KToCurrent
   - LinearSaturationFit.order field controls scale (1e9 vs 1e6)
   - **Fragile**: Easy to break with changes
   - **Essential**: Magnet control depends on correct scaling

5. **Parent Backref (physical.py + element.py)**
   - Dipole.__init__ sets physical._parent = self
   - PhysicalElement._physical_angle reads parent.magnetic.angle
   - Fragile design; violates separation of concerns

### Optional Utilities (Removable or Moat-able)

| Category | Examples | Burden | Action |
|---|---|---|---|
| Vector math | Position.dot, .vector_angle, .length; Rotation.__abs__, .__gt__ | LOW | Move to utils? |
| Convenience properties | normalized_strength, poles, k1l/k2l/k3l, half_gap | LOW | Document as optional |
| Debugging | __str__, __repr__, no_controls, hardware_info | LOW | Keep but mark non-essential |
| Constructor variants | Position.from_list, from_values; LinearSaturationFit.from_string | LOW | Keep for ergonomics |

### Backwards-Compatibility Risk Matrix

| Feature | Risk | Impact | Mitigation |
|---|---|---|---|
| Attribute cascading | **VERY HIGH** | Breaks lazy access to nested fields | Document as stable API |
| Position/Rotation serialization | **VERY HIGH** | Breaks JSON API | Lock down format |
| rotation_matrix | **VERY HIGH** | Breaks geometry calculations | Tests + documentation |
| Order-dependent scaling in Dipole | **VERY HIGH** | Breaks magnet control | Add integration tests |
| _physical_angle computed_field | **HIGH** | Breaks bend/start/end properties | Must maintain parent backref |
| Validators (alias, subelement) | **HIGH** | Breaks YAML parsing | Cannot change logic |
| Field definitions | **HIGH** | Breaks schema | Cannot remove |
| Multipoles.normal() / Rotation.__iter__() | **MEDIUM** | Breaks usage patterns (common but replaceable) | Document alternatives |
| Math methods (dot, vector_angle) | **LOW** | Utilities only | Safe to move |
| Debugging methods (__str__) | **LOW** | Non-essential | Safe to remove |

