# RF-Track Integration Pattern Notes

Research-only notes mapping how ASTRA is wired into SIMBA and how the LAURA
translator/Exporters layers work, as a template for adding RF-Track. No code
was written or modified while producing this document.

Repos referenced:
- SIMBA: `c:\Users\jkj62.CLRC\Documents\GitHub\simba`
- LAURA: `c:\Users\jkj62.CLRC\Documents\GitHub\laura`

---

## Part A — SIMBA's "Codes" pattern (ASTRA as reference)

### A.1 `simba/Codes/ASTRA/ASTRA.py` and `ASTRARules.py`

**File:** `simba\Codes\ASTRA\ASTRA.py`

Defines one class, `astraLattice(frameworkLattice)` (line 68), the ASTRA-specific
lattice/run object. `frameworkLattice` is a `pydantic.BaseModel` defined in
`simba\Framework_objects.py:455`. `astraLattice` does **not** inherit from any
"code base class" — SIMBA has no `BaseCode`/`BaseLattice` abstract interface;
each code's lattice class inherits directly from `frameworkLattice` and
overrides the same handful of lifecycle methods by convention (duck typing,
not an ABC).

Key attributes on `astraLattice`:
- `code: str = "astra"` (line 84) — string identifier used by the registry (see A.4).
- `astra_headers: Dict[str, Any]` (line 113) — holds `astra_newrun`, `astra_output`,
  `astra_charge`, `astra_errors` instances (these classes live in **LAURA**, at
  `laura\translator\converters\codes\astra.py` — see B.1/B.1b below; SIMBA imports
  them at ASTRA.py:45-50).
- `section_header_text_ASTRA` (module-level dict, line 54) maps LAURA element
  hardware classes to ASTRA `&HEADER` names/booleans (e.g. `"cavities": {"header":
  "CAVITY", "bool": "LEField"}`).

Lifecycle methods overridden from `frameworkLattice` (this is the "contract" a
new code's Lattice class must implement, by convention):
- `model_post_init` (line 119) — builds the `&NEWRUN`/`&OUTPUT`/`&CHARGE`/`&ERROR`
  header objects from `file_block`/`globalSettings`.
- `write()` (line 337) — calls `self.section.to_astra()` (a **LAURA**
  `SectionLatticeTranslator` method, see B.1) and saves it to
  `<master_subdir>/<objectname>.in`, appending the path to `self.files`.
- `preProcess()` (line 349) — converts the previous section's beam into ASTRA
  format (`hdf5_to_astra`) and sets particle counts.
- `postProcess()` (line 416) — converts ASTRA screen/beam output files back to
  HDF5/openPMD (`astra_to_hdf5`), using a `lox`-threaded `screen_threaded_function`
  for parallel screen conversion.
- Helper methods: `find_ASTRA_filename`, `hdf5_to_astra`, `astra_to_hdf5`,
  `get_screen_scaling`.
- Several `@property` setters (`sample_interval`, `bunch_charge`, `toffset`,
  `space_charge_mode`) that forward the value into the appropriate
  `astra_headers[...]` object.

**File:** `simba\Codes\ASTRA\ASTRARules.py`

Just one module-level dict, `ASTRARules`, keyed by ASTRA namelist name
(`"NEWRUN"`, `"OUTPUT"`, `"CHARGE"`, `"SCAN"`, `"APERTURE"`, `"CAVITY"`,
`"SOLENOID"`, `"QUADRUPOLE"`) → list of raw ASTRA keyword strings. This looks
like a static reference/validation list (not obviously imported elsewhere in
the files inspected); a new code would supply an equivalent "raw keyword names
per block" list if useful for documentation/validation purposes only.

### A.2 Generators layer: `simba/Codes/Generators/astra.py` + `astra.yaml`

**File:** `simba\Codes\Generators\astra.py` defines `ASTRAGenerator(frameworkGenerator)`.
`frameworkGenerator` is the base class at
`simba\Codes\Generators\Generators.py:149` (a `pydantic.BaseModel`, not tied to
`frameworkObject`/`frameworkLattice`). It is registered by name in
`simba\Codes\Generators\__init__.py`:
```
from .astra import ASTRAGenerator
from .gpt import GPTGenerator
from .opal import OPALGenerator
```
`frameworkGenerator.code: Literal["ASTRA","astra","GPT","gpt","generic","framework","simba","SIMBA"]`
is the string tag (Generators.py:227) — note generators use a `Literal` allow-list
rather than a dynamic registry, unlike lattices (see A.4).

`ASTRAGenerator` overrides:
- `model_post_init` — calls `self.apply_alias_and_multiplier(aliases, "astra")` and
  sets `self.code = "ASTRA"`.
- `run()` — builds `self.executables["ASTRAgenerator"] + [self.objectname + ".in"]`
  and shells out via `subprocess.call`.
- `_write_ASTRA()` — iterates `self.__dict__`, renames each field via
  `aliases["aliases"]["astra"][k]["alias"]` (with optional `multiplier`), skips
  anything in `astra_generator_keywords["disallowed"]`, and formats
  `key = value,` lines (special-cased for species names and `le`).
- `write()` — wraps `_write_ASTRA()` output in `&INPUT ... /` and saves to
  `<master_subdir>/<objectname>.in`.
- `postProcess()` — reads the ASTRA-format beam file back
  (`rbf.astra.read_astra_beam_file`) and writes it out as openPMD HDF5.

**YAML files** (all in `simba\Codes\Generators\`):
- `astra.yaml` — `disallowed:` list of generic field names ASTRA's generator
  doesn't understand (excluded when writing `&INPUT`).
- `aliases.yaml` — top-level `aliases: <code>: <generic_name>: {alias: <ASTRA_name>,
  multiplier: <float>}` mapping generic beam-generator attribute names to each
  code's own keyword + unit multiplier. Same file holds `elegant`, `gpt`, `opal`
  sections too (multi-code file, not one file per code).
- `keywords.yaml`, `species.yaml`, `elegant.yaml`, `gpt.yaml`, `opal.yaml` — sibling
  per-code files loaded the same way in `Generators.py:107-142` (each opened with
  `yaml.safe_load` at import time and stored as a module-level dict, e.g.
  `astra_generator_keywords`, `gpt_generator_keywords`).

So the Generators layer is a **flat "one .py + one .yaml per code" sibling
set** inside `simba/Codes/Generators/`, registered by adding an import line to
`simba/Codes/Generators/__init__.py` and extending the `Literal[...]` on
`frameworkGenerator.code`.

### A.3 `simba/Modules/{Beams,Twiss,Fields}/astra.py`

These are **not classes** — each is a flat module of free functions operating on
a `self` that is actually the generic `beam`/`twiss`/`field` object passed in
explicitly (first positional arg), i.e. a lightweight "mixin function library"
style rather than OO inheritance.

- **`simba\Modules\Beams\astra.py`** — beam-distribution I/O:
  - `read_astra_beam_file(self, filename, normaliseZ=False, keepLost=False)` /
    `interpret_astra_data(self, data, normaliseZ=False, keepLost=False)` — parse
    ASTRA's 10-column particle file (`x y z cpx cpy cpz clock charge index status`)
    into the generic `beam.Particles` (`UnitValue` fields).
  - `write_astra_beam_file(self, filename=None, index=None, status=5,
    normaliseZ=False, zoffset=0.0)` — inverse operation; picks/keeps a reference
    particle and writes the same 10-column format via `np.savetxt`.
  - Sibling functions in the same file for CSRTrack (`read_csrtrack_beam_file`)
    and a legacy `read_pacey_beam_file`, plus `convert_csrtrackfile_to_astrafile`
    — confirms the convention: one file per code, but it can contain more than
    one "read"/"write" pair if the code has variant formats.

- **`simba\Modules\Twiss\astra.py`** — Twiss/optics I/O:
  `read_astra_twiss_files(self, filename, reset=True)` locates the matching
  `Xemit`/`Yemit`/`Zemit` files by string substitution on the given filename,
  loads them with `np.loadtxt`, and `interpret_astra_data(self, lattice_name,
  xemit, yemit, zemit)` appends parsed columns (beta/alpha/gamma, emittances,
  sigmas, dispersion placeholders, etc.) onto the generic `twiss` object's
  `.val` arrays.

- **`simba\Modules\Fields\astra.py`** — field-map I/O:
  `generate_astra_field_data(self) -> np.ndarray` builds the on-disk array
  layout per `field_type` (`LongitudinalWake`, `TransverseWake`, `3DWake`,
  `1DMagnetoStatic`, `3DMagnetoStatic`, `1DElectroDynamic` w/ `TravellingWave`/
  `StandingWave` cavity_type, `1DQuadrupole`); `write_astra_field_file(self)`
  writes it to `<name>.astra`; `read_astra_field_file(self, filename, field_type,
  cavity_type=None, frequency=None)` is the inverse parser, raising
  `NotImplementedError` for unsupported `field_type`s.

All three files are imported as `rbf.astra`, `rtf.astra`(?)/twiss astra module,
and `field` submodule — a new code needs the equivalent three files
(`simba/Modules/Beams/rftrack.py`, `simba/Modules/Twiss/rftrack.py`,
`simba/Modules/Fields/rftrack.py`) each exposing read/write functions with the
same signatures as above, following the `code` value used in `astraLattice`
(e.g. `rbf.rftrack.read_rftrack_beam_file(...)`).

### A.4 Framework wiring points (file:line)

SIMBA discovers "supported codes" by **introspection**, not a manual
dict — a new code needs its lattice class named `<code>Lattice` and importable
from `simba.Framework_lattices`, nothing else to register in `Framework.py`
itself:

- `simba\Framework_lattices.py:1-10` — the registry module; one import line per
  code, e.g. `from .Codes.ASTRA.ASTRA import astraLattice  # noqa F401`. **This
  is the single file to edit** to add a new code's lattice class to the
  registry (add `from .Codes.RFTrack.RFTrack import rftrackLattice  # noqa F401`).
- `simba\Framework.py:45` — `from . import Framework_lattices as frameworkLattices`.
- `simba\Framework.py:125-127` — `latticeClasses = [[obj[1] for obj in
  inspect.getmembers(frameworkLattices) if inspect.isclass(obj[1])]]` (built but
  not directly used for validation below — `supported_codes` is what matters).
- `simba\Framework.py:159` — `supported_codes = [code.split("Lattice")[0] for
  code in dir(frameworkLattices) if "lattice" in code.lower()]` — derives the
  allow-list purely from class names ending in `Lattice` (case-insensitive
  substring match on `"lattice"`).
- `simba\Framework.py:756-789` (`read_Lattice`) — the actual per-lattice
  construction: `code = lattice["code"]`; raises `NotImplementedError` if
  `code.lower() not in supported_codes` (line 772); otherwise
  `getattr(frameworkLattices, code.lower() + "Lattice")(...)` (line 774-789)
  instantiates it with `name`, `objectname`, `objecttype=code.lower()+"Lattice"`,
  `file_block`, `elementObjects`, `groupObjects`, `runSettings`, `settings`,
  `executables`, `global_parameters`, `machine`, `globalSettings`. **The new
  class must therefore be literally named `rftrackLattice`** for `code: rftrack`
  in a settings file to resolve.
- `simba\Framework.py:1139-1147` — the same `getattr(frameworkLattices,
  code.lower() + "Lattice")` pattern reused inside `modifyLattice`'s "change
  lattice code" path.
- `simba\Framework.py:1630-1632` — remote-execution host/code matching
  (`hosts[server]["codes"]`, compares `self.latticeObjects[lattice].code.lower()`).
- Generator side (separate mini-registry, `Literal`-based, not introspected):
  `simba\Framework.py:38-43` imports `ASTRAGenerator, GPTGenerator, OPALGenerator,
  frameworkGenerator`; `simba\Framework.py:1426-1434` — explicit
  `if kwargs["code"].lower() == "astra": code = ASTRAGenerator ... else:
  raise NotImplementedError(...)` — **this one is a manual if/elif chain**, not
  introspected, so adding an `RFTrackGenerator` (if RF-Track needs its own
  beam-generator, as opposed to just consuming LAURA/SIMBA's generic
  openPMD beam) means editing this if/elif block by hand.

### A.5 Executables registration

- `simba\Codes\Executables.py` defines the generic `executable` helper class
  (resolves a code's binary path/command per-hostname or per-OS from
  `Executables.yaml`, substituting `$simcodes$`/`$ncpu$`) and the `Executables`
  container class (`__init__`, line 90) that calls one `define_<code>_command()`
  method per code (`define_astra_command` line 177, `define_ASTRAgenerator_command`
  line 157, `define_elegant_command`, `define_csrtrack_command`,
  `define_gpt_command`, `define_opal_command`, `define_genesis_command`) — each
  sets `self.<code> = <code>Executable.executable`. A new code needs an
  equivalent `define_rftrack_command(self, location=None, ncpu=1, scaling=None,
  override_location=None)` method, and a call to it added to
  `Executables.__init__` (Executables.py:122-128) alongside the existing
  `self.define_astra_command()` etc.
- `simba\Framework.py:318-349` (`prepare_executables`) — calls
  `executables.define_astra_command(...)`, `define_elegant_command(...)`, etc.
  in sequence; a new `executables.define_rftrack_command(...)` call needs adding
  here too so `Framework()` construction wires it up by default.
- `simba\Executables.yaml` — per-hostname-key (`nt`, `apclara1`, `apclara2`,
  `apclara3`, `posix`) dict of `<code_key>: [<path>, ...args]`, e.g.
  `nt: {astra: [$simcodes$/ASTRA/astra.exe], ...}`. A new code needs an
  `rftrack:` entry added under each relevant host key.

### A.6 Existing ASTRA-related unit tests as a template

- `simba\unit_tests\test_framework_lattice.py` — small, currently-passing pytest
  file; not ASTRA-specific but is the closest live template for lattice-object
  tests: a `framework_with_elements(tmp_path)` fixture builds a bare
  `sfw.Framework(directory=str(tmp_path))` and injects a hand-built
  `elementObjects` dict (`Quadrupole`, `Marker`/`Element` from
  `laura.models.element`); tests then call plain `Framework` methods
  (`getElement`, `getElementType`, `setElementType`, `set_lattice_prefix`) and
  assert on returned values/`pytest.warns(UserWarning)`. No real code execution
  (no `write()`/`run()`) is exercised in this file.
- `simba\unit_tests\test_track.py` — **entirely commented out** (a dead/legacy
  file), but structurally is the fullest historical template for an end-to-end
  code test: a `test_fodo_elements` fixture builds a hand-written FODO lattice
  dict of `marker`/`quadrupole` elements; `prepare_lattice(...)` builds a real
  `exes.Executables`, a `latticedict` with `code`, `input`, `output`, `charge`,
  `csr` keys, and instantiates `lattice_class(**latattrs)`; then
  `@pytest.mark.parametrize("code,lattice_class", [("elegant", elegantLattice),
  ("astra", astraLattice), ("ocelot", ocelotLattice), ("gpt", gptLattice),
  ("csrtrack", csrtrackLattice), ("cheetah", cheetahLattice)])` drives
  `lattice.preProcess(); lattice.write(); lattice.writeElements(); lattice.run();
  lattice.postProcess()` for each code in turn — this parametrize-across-codes
  pattern is exactly the shape a new `("rftrack", rftrackLattice)` test tuple
  would slot into, once un-commented/rewritten against the current API.

---

## Part B — LAURA's translator/converters and Exporters pattern

### B.1 `laura/translator/converters/*` — the element-level translator layer

Target formats produced: **simulation-code lattice-element representations**
(a string for text-based codes — Elegant, ASTRA, CSRTrack, Genesis, OPAL — or a
native Python object for object-based codes — Ocelot, Cheetah, Xsuite, Wake-T,
GPT-string). This is a **different, lower layer** than `laura/Exporters/*`
(see B.2).

**Contract (`laura\translator\converters\base.py`):**
`BaseElementTranslator(PhysicalBaseElement)` (line 31) is the single
abstract-ish base every element-category translator inherits from. It defines
one method per target code, each with a working default implementation for
`to_elegant`, `to_ocelot`, `to_cheetah`, `to_xsuite`, `to_genesis`, `to_wake_t`,
`to_opal` (these use the generic `full_dump()` + `_convertKeyword_<Code>` +
`elements_<Code>` YAML-table approach, so they work "for free" for any element
that doesn't need special-casing), and three **empty stub methods** meant to be
overridden per element type: `to_astra(self, n=0, **kwargs) -> str` (line 367,
returns `""`), `to_gpt(self, Brho=0.0, ccs="wcs", *args, **kwargs) -> str`
(line 375, returns `""`), `to_csrtrack(self, n=0, **kwargs) -> str` (line 359,
returns `""`). **A new code follows this same stub pattern**: add
`to_rftrack(self, n: int = 0, **kwargs: dict) -> str: return ""` to
`base.py` as the universal fallback.

Also on `base.py`: `_write_ASTRA_dictionary(self, d: dict, n: int|None=1) -> str`
(line 754) — a generic "namelist body" formatter shared by every ASTRA
element-translator override (handles `type: list/array/not_zero` value specs
and 70-column line wrapping). A new code needing a similarly-shaped text
format (e.g. RF-Track's own input syntax) would add an equivalent
`_write_RFTrack_dictionary` helper here, or a per-format helper class in
`codes/rftrack.py` (see below) if RF-Track's format is structured differently
(RF-Track's actual input is a MATLAB/Octave-like scripting API via its Python
bindings, not a namelist file, so this may end up looking more like the
Ocelot/Cheetah/Xsuite object-building pattern than the ASTRA/Elegant
string-building pattern).

**Registration is by LAURA element category, not by target code** — one
Translator subclass per LAURA element *category*, each overriding whichever
`to_<code>()` stubs it needs:
- `laura\translator\converters\magnet.py` — `MagnetTranslator` (generic
  magnets, overrides `to_astra`/`to_csrtrack`/`to_gpt` for quadrupoles),
  `DipoleTranslator` (overrides `to_astra`/`to_csrtrack`/`to_gpt`/`to_opal`),
  `SolenoidTranslator` (`to_astra`/`to_gpt`/`to_opal`), `WigglerTranslator`
  (`to_genesis` only), `NonLinearLensTranslator` (no overrides shown/read past
  its magnetic-element declaration).
- `laura\translator\converters\cavity.py` — `RFCavityTranslator` (overrides
  `to_elegant`, `to_ocelot`, `to_cheetah`, `to_astra` (line 280), `to_xsuite`,
  `to_opal`, `to_gpt`; also owns cavity-specific helpers `get_cells()`,
  `set_wakefield_column_names()`).
- `laura\translator\converters\drift.py` — `DriftTranslator` (overrides only
  `to_elegant`, to choose `csrdrift`/`lscdrift`/`drift` sub-type; relies on the
  base-class stub for `to_astra` — ASTRA drifts are implicit space between
  elements, not written out).
- `laura\translator\converters\aperture.py` — `ApertureTranslator` (overrides
  `to_astra` (line 103) and `to_elegant`; has ASTRA-only helper methods
  `_write_ASTRA_Common`, `_write_ASTRA_Circular`, `_write_ASTRA_Planar`).
- `laura\translator\converters\diagnostic.py` — `DiagnosticTranslator`
  (overrides `to_elegant`, `to_csrtrack`; relies on base stub for `to_astra`
  since ASTRA screens are declared in the `&OUTPUT` header, not per-element —
  see `astra_output.screens` in B.1b).
- `laura\translator\converters\wake.py` — `WakefieldTranslator` (overrides
  `to_astra` (line 15) and `to_gpt` (line 142) — this is instantiated
  on-the-fly by `SectionLatticeTranslator.to_astra()`/`to_gpt()` whenever a
  cavity has a `wakefield_definition`, not dispatched via `translate_elements`).
- `laura\translator\converters\plasma.py` / `laser.py` — `PlasmaTranslator`,
  `LaserTranslator` (both declared, minimal overrides observed).
- `laura\translator\converters\twiss.py` — `TwissMatchTranslator` (referenced
  by `converter.py`'s dispatch table for `TwissMatch` elements).
- `laura\translator\converters\codes\` — a **sub-package of per-target-code
  helper classes**, distinct from the per-element-category files above:
  `astra.py` (namelist header classes: `astra_header` base + `astra_newrun`,
  `astra_output`, `astra_charge`, `astra_errors`, each with `write_ASTRA()`),
  `gpt.py` (`gpt_ccs` coordinate-system class, `gpt_Zminmax`, `gpt_dtmint`),
  plus `bmad.py`, `csrtrack.py`, `elegant.py`, `ocelot.py`, `opal.py`,
  `xsuite.py`. **This is where RF-Track's own "run-level" structures would
  go**: `laura/translator/converters/codes/rftrack.py`.

**Dispatch (`laura\translator\converters\converter.py`):**
`translate_elements(elements, master_lattice=None, directory=".") ->
Dict[str, BaseElementTranslator]` (line 41) is the single dispatch function —
an `isinstance`/`type` if/elif chain (lines 66-96) mapping LAURA model classes
(`Solenoid`, `Dipole` (excluding correctors), `Wiggler`, `NonLinearLens`, plain
`Magnet`, `RFCavity`/`RFDeflectingCavity`, `Drift`, `Diagnostic`/`Marker`/
`Screen`, `Aperture`, `Plasma`, `Laser`, `TwissMatch`) to their Translator
class, falling back to plain `BaseElementTranslator` for anything unmatched.
It then does `translator.model_validate(elem.model_dump(by_alias=False))` to
re-hydrate each LAURA element as its Translator-subclass twin. **This function
does not need to change to add a new target code** — it dispatches by LAURA
element type, not by output format; a new code only adds `to_rftrack()`
methods onto the *existing* Translator classes returned here.

**Answering the "one converter per element category vs. one pluggable
backend" question directly**: it is **one converter per LAURA element
category**, and a new target format is added as **one new method
(`to_rftrack`) sprinkled across the existing per-category files**
(`base.py`, `magnet.py`, `cavity.py`, `aperture.py`, `diagnostic.py`,
`wake.py`, plus a new `codes/rftrack.py` for RF-Track-specific helper/header
classes) — not a single new pluggable class. There is no `Backend`/`Plugin`
abstraction to implement; you extend every relevant existing class.

**Section/Layout/Machine aggregation layer** (calls `translate_elements` then
loops over the results calling each element's `to_<code>()`):
- `laura\translator\converters\section.py` — `SectionLatticeTranslator
  (SectionLattice)` — one **section** (a straight run of elements). Has
  `to_astra()` (line 88), `to_gpt()`, `to_opal()`, `to_elegant()`,
  `to_genesis()`, `to_ocelot()`, `to_cheetah()`, `to_xsuite()`, `to_csrtrack()`,
  `to_wake_t()`. `to_astra()` builds ASTRA's `&APERTURE/&CAVITY/&SOLENOID/
  &QUADRUPOLE/&DIPOLE/&WAKE` header blocks by grouping translated elements by
  `hardware_type`, tracking per-block counters, and concatenating each
  element's `to_astra(n=count)` output; also synthesizes a `WakefieldTranslator`
  on-the-fly for cavities with wakefields.
- `laura\translator\converters\layout.py` — `MachineLayoutTranslator
  (MachineLayout)` — one **lattice/layout** (an ordered set of sections);
  presumably loops `SectionLatticeTranslator` per section (not fully read, but
  used by `model.py` as `MachineLayoutTranslator.from_layout(latt).to_astra()`
  etc.)
- `laura\translator\converters\model.py` — `MachineModelTranslator
  (MachineModel)` — the **whole machine** (multiple layouts). `to_astra()`
  (line 28) returns `Dict[layout_name, MachineLayoutTranslator...to_astra()]`;
  `to_elegant()`/`to_genesis()` build one big string across all
  lattices/sections; `to_ocelot()`/`to_cheetah()`/`to_xsuite()` similarly
  fan out per-layout.

So the translator stack is a strict 4-level recursion:
`MachineModelTranslator.to_<code>()` → `MachineLayoutTranslator.to_<code>()`
→ `SectionLatticeTranslator.to_<code>()` → (per element)
`<CategoryTranslator>.to_<code>()`. **A new code needs a `to_rftrack()` method
added at all 4 levels** (model.py, layout.py, section.py, plus the per-element
category files), following exactly the ASTRA/GPT precedent at each level.

**Conversion-rule YAML files** (`laura\translator\conversion_rules\`), loaded
lazily via `LazyDict` in `laura\translator\converters\__init__.py:78-101`:
- `types\type_conversion_rules.yaml` — `<code>: <LAURA hardware_type>:
  <code's element-type keyword>` (e.g. `elegant: {Dipole: csrcsbend,
  Quadrupole: quad, ...}`); used by codes that have a MAD-style typed element
  syntax (Elegant, Genesis, Opal). ASTRA/Ocelot/Cheetah/Xsuite/GPT don't use
  this file (they use direct dict-building in the translator classes instead).
- `keywords\keyword_conversion_rules_<code>.yaml` — `general: <LAURA field
  name>: <code keyword>` plus optional per-hardware-type override sections
  (e.g. `dipole: isr_enable: isr`). Exists for elegant, genesis, ocelot,
  cheetah, opal, xsuite, wake_t. **ASTRA and GPT do not have one** — their
  keyword mapping is inlined as literal dict keys inside each `to_astra`/
  `_write_ASTRA_*`/`to_gpt` method body (e.g. `"Q_pos"`, `"Q_xoff"` string
  literals in `magnet.py`). RF-Track would follow whichever precedent fits its
  API shape: a YAML table if it has a flat keyword=value config format, or
  inline dict-building (ASTRA-style) if its Python bindings need structured
  objects/method calls instead.
- `elements\elements_<code>.yaml` — `<code element type>: [allowed keyword,
  ...]` used as a filter (`if self._convertKeyword_X(key) in
  elements_X[etype]`) for codes with strict per-element-type keyword lists
  (elegant, genesis, ocelot, opal, cheetah). Not used by ASTRA/GPT/Xsuite/
  Wake-T.
- `codes\` sub-package (`cheetah_conversion.py`, `ocelot_conversion.py`,
  `wake_t_conversion.py`, `xsuite_conversion.py`) — Python dicts mapping LAURA
  `hardware_type` → the actual third-party class object to instantiate (e.g.
  `ocelot.cpbd.elements.Quadrupole`), used only by the object-based codes.
  ASTRA/Elegant/GPT/Genesis/Opal (string-emitting codes) don't need this since
  they don't instantiate foreign objects. **If RF-Track is used via its Python
  API (object-based, like Ocelot/Xsuite) rather than a text input file, it
  would need an equivalent `laura/translator/conversion_rules/codes/
  rftrack_conversion.py`.**

### B.2 `laura/Exporters/*` vs `laura/translator/converters/*`

`laura\Exporters\__init__.py` is confirmed **empty** (1 line/blank) — no
package-level registry or dispatch logic lives there; each Exporter module is
imported directly by its consumer (e.g. `Export_CATAP_YAML.py` imports
`Importers.CATAP_Loader`; `simba\Framework.py:31` imports
`from laura.Exporters.YAML import export_machine, export_elements` directly).

The two layers are **not the same thing and don't overlap in responsibility**:

- **`laura/Exporters/*.py` (CATAP.py, Export_CATAP_YAML.py, YAML.py, SQL.py,
  RDF.py)** operate at the **whole-`MachineModel`** level and serialize LAURA's
  *own* data model to an interoperability/persistence format — YAML files on
  disk (`YAML.py`: `export_as_yaml`, `export_machine`,
  `export_machine_combined_file`, `export_elements`), a SQL database
  (`SQL.py`), an RDF graph (`RDF.py`: `build_rdf_graph(machine, machine_name)`),
  or CATAP control-system YAML (`CATAP.py`: `export_machine(path, machine,
  overwrite=False)` at line 32, iterating `machine.elements.items()` and
  calling `save_CATAP_file` → `element_to_CATAP(elem)` → `elem.to_CATAP()`,
  a method defined on the LAURA element models themselves, not found in
  `translator/converters/` in this search — it's a model-level serialization
  method, separate from the translator stack entirely). These are **round-trippable,
  faithful dumps of the LAURA object graph** — useful for saving/loading
  lattices, feeding EPICS/CATAP control systems, or SPARQL-querying the
  machine — not simulation-code input decks.

- **`laura/translator/converters/*.py`** operate at the **per-element /
  per-section / per-layout** level and produce **lossy, code-specific
  simulation input** (an ASTRA namelist string, an Ocelot object, ...) destined
  to be consumed by a tracking code (SIMBA orchestrates this: e.g.
  `astraLattice.write()` calls `self.section.to_astra()`, a
  `SectionLatticeTranslator` method). These are **one-way** (LAURA model →
  code input); there is no `from_astra()` importer in this layer (ASTRA output
  beam/twiss files are read back by **SIMBA**'s `Modules/Beams/astra.py`
  /`Modules/Twiss/astra.py`, not by LAURA).

Conclusion: **RF-Track needs both**, and they are independent additions:
1. `laura/translator/converters/*` — `to_rftrack()` methods (element/section/
   layout/model level) so **SIMBA** can generate RF-Track's input.
2. Optionally, if RF-Track's own native format should be exportable/importable
   as a standalone LAURA Exporter (round-trip, analogous to CATAP/YAML), a new
   `laura/Exporters/RFTrack.py` with an `export_machine(path, machine,
   overwrite=False)`-shaped function — but this is a separate, optional
   concern from (1), following the CATAP.py precedent, and only needed if you
   want LAURA itself (independent of SIMBA orchestration) to be able to dump a
   `MachineModel` straight to RF-Track's file format.

### B.3 Existing CATAP/YAML export test as a template

`laura\unit_tests\test_exporters_importers.py` — plain **pytest**, no
unittest.TestCase, no custom conftest fixtures used here (fixtures are defined
locally in the file with `@pytest.fixture`, not shared via `conftest.py`).
Structure:
- Module-level fixtures `sample_quad()`, `sample_marker()` build minimal LAURA
  element instances directly (`Quadrupole(name=..., machine_area=...,
  magnetic={...}, physical={...})`).
- `small_machine(sample_quad, sample_marker)` fixture composes a full `LAURA(
  element_list=[...], layout=layouts, section=sections)` object (LAURA's
  top-level class, `from laura import LAURA`) from two elements plus explicit
  `sections`/`layout` dicts.
- Tests are grouped into plain classes (`class TestExportAsYaml:`, `class
  TestExportMachine:`) with one `test_*` method each (not `unittest.TestCase`
  subclasses — just namespacing via a plain class, pytest auto-collects them).
- Assertions are direct dict/attribute checks (`isinstance(result, dict)`,
  `result["name"] == "Q1"`) and filesystem checks using pytest's built-in
  `tmp_path` fixture (`os.path.isfile(filepath)`, `os.walk` counting `.yaml`
  files) — no mocking framework used.
- Round-trip pattern: export via `export_machine(...)`, then re-import via the
  matching `laura.Importers.*` function (e.g. `read_YAML_Element_File`) to
  verify fidelity, for the YAML case; the CATAP-specific tests were not opened
  in this pass but `test_exporters_importers.py`'s docstring covers "YAML and
  ...YAML_Loader" — a new RF-Track export test would follow this exact
  shape: build a small `LAURA(...)` fixture, export via the new
  `translator.converters.*.to_rftrack()` / new Exporter, and assert on the
  returned string/dict/file contents.
- Other exporter-adjacent test files present but not opened: `test_sql_exporter.py`
  (currently modified per `git status`), `test_rdf_sparql.py`,
  `test_yaml_loader_extended.py` — these follow the same pytest-plain-function/
  class-plus-`tmp_path` idiom based on their file naming and co-location.

### B.4 `laura/models/elementList.py` — `MachineModel`

`MachineModel(ModelBase)` at line 962. Key attributes (lines 970-996):
- `layout: str | Dict | None` — layout name(s)/definition.
- `section: str | Dict[str, Dict] | None` — section name(s)/definition.
- `elements: Dict[str, baseElement] = {}` — **every** element in the machine,
  keyed by name (flat, not nested by section).
- `sections: Dict[str, SectionLattice] = {}` — keyed by section name; a
  `SectionLattice` (class at `elementList.py:150`, itself a `BaseLatticeModel`)
  holds an ordered run of elements.
- `lattices: Dict[str, MachineLayout] = {}` — keyed by layout name; a
  `MachineLayout` groups multiple `SectionLattice`s into a full beamline path
  (SIMBA and the translator's `model.py`/`layout.py` iterate `self.lattices`
  then `latt.sections`).
- `master_lattice: str | None` — directory containing the lattice YAML/data
  files (field maps, wakefields) that `field(...)`/`generate_field_file_name`
  resolve paths against.
- Private caches: `_layouts`, `_layout_metadata`, `_section_definitions`,
  `_default_path`.

`translator/converters/section.py`'s `SectionLatticeTranslator` and
`layout.py`'s `MachineLayoutTranslator` and `model.py`'s
`MachineModelTranslator` are `SectionLattice`/`MachineLayout`/`MachineModel`
subclasses respectively (via `.from_section()`/`.from_layout()`/`.from_machine()`
class methods that `model_validate` a copy of the plain model into the
Translator-flavoured subclass) — i.e. the Translator classes at every level
are drop-in "richer" versions of the plain model classes, not wrapper/adapter
objects.

---

## Integration checklist

New files/additions needed to add RF-Track, mirroring ASTRA (SIMBA side) and
CATAP/ASTRA (LAURA side) exactly:

### SIMBA (`c:\Users\jkj62.CLRC\Documents\GitHub\simba`)
- `simba/Codes/RFTrack/RFTrack.py` — new module defining `rftrackLattice
  (frameworkLattice)` (mirrors `simba/Codes/ASTRA/ASTRA.py:68`); implement
  `model_post_init`, `write()`, `preProcess()`, `postProcess()`, `code: str =
  "rftrack"`. Class name **must** be `rftrackLattice` (lowercase `code` +
  `"Lattice"`) for the introspection-based registry to find it.
- `simba/Codes/RFTrack/__init__.py` — empty/package marker, mirrors
  `simba/Codes/ASTRA/__init__.py`.
- `simba/Codes/RFTrack/RFTrackRules.py` (optional) — raw keyword reference
  lists, mirrors `ASTRARules.py`, only if useful for validation/docs.
- `simba/Codes/Generators/rftrack.py` — new `RFTrackGenerator
  (frameworkGenerator)`, mirrors `simba/Codes/Generators/astra.py`, **only
  if** RF-Track needs its own beam-generator step (rather than consuming the
  generic openPMD beam SIMBA already produces).
- `simba/Codes/Generators/rftrack.yaml` — `disallowed:` list, mirrors
  `astra.yaml`.
- `simba/Codes/Generators/aliases.yaml` — add an `rftrack:` block to the
  existing multi-code `aliases:` mapping (not a new file — this file is shared
  across codes).
- `simba/Codes/Generators/__init__.py` — add `from .rftrack import
  RFTrackGenerator`.
- `simba/Modules/Beams/rftrack.py` — beam I/O functions
  (`read_rftrack_beam_file`, `write_rftrack_beam_file`, `interpret_rftrack_data`),
  mirrors `simba/Modules/Beams/astra.py`.
- `simba/Modules/Twiss/rftrack.py` — Twiss I/O (`read_rftrack_twiss_files`,
  `interpret_rftrack_data`), mirrors `simba/Modules/Twiss/astra.py`.
- `simba/Modules/Fields/rftrack.py` — field-map I/O
  (`generate_rftrack_field_data`, `write_rftrack_field_file`,
  `read_rftrack_field_file`), mirrors `simba/Modules/Fields/astra.py`.

**Registration edits (exact file:line):**
- `simba/Framework_lattices.py:1` (append after line 10) — add
  `from .Codes.RFTrack.RFTrack import rftrackLattice  # noqa F401`. This is
  the **only** edit needed for `supported_codes` (Framework.py:159) and
  `read_Lattice` (Framework.py:774) to recognize `code: rftrack`.
- `simba/Codes/Generators/Generators.py:227` — extend the `Literal[...]` on
  `frameworkGenerator.code` to include `"RFTrack", "rftrack"` (only if adding
  a generator).
- `simba/Framework.py:38-43` — add `RFTrackGenerator` to the
  `from .Codes.Generators import (...)` import (only if adding a generator).
- `simba/Framework.py:1426-1434` — add an `elif kwargs["code"].lower() ==
  "rftrack": code = RFTrackGenerator` branch to the manual if/elif chain
  (only if adding a generator; this path is **not** introspected).
- `simba/Codes/Executables.py:122-128` (inside `Executables.__init__`) — add
  `self.rftrack = None` (near line 116-120) and a call to a new
  `self.define_rftrack_command()`; add the method itself following the
  `define_astra_command` template at Executables.py:177-208.
- `simba/Framework.py:318-349` (`prepare_executables`) — add
  `executables.define_rftrack_command(override_location=location, ncpu=ncpu)`
  alongside the existing `define_astra_command(...)` etc. calls.
- `simba/Executables.yaml` — add an `rftrack: [...]` key under each relevant
  host section (`nt:`, `posix:`, `apclara1:`, `apclara2:`, `apclara3:`).
- `simba/unit_tests/test_track.py` — add `("rftrack", rftrackLattice)` to the
  `@pytest.mark.parametrize("code,lattice_class", [...])` lists (once this
  file is revived from its current fully-commented-out state; new tests could
  instead be written fresh following the same fixture/parametrize shape).

### LAURA (`c:\Users\jkj62.CLRC\Documents\GitHub\laura`)
- `laura/translator/converters/base.py` — add
  `to_rftrack(self, n: int = 0, **kwargs: dict) -> str: return ""` stub next
  to `to_astra`/`to_gpt`/`to_csrtrack` (around line 367-381); add any shared
  `_write_RFTrack_*` helper analogous to `_write_ASTRA_dictionary` (line 754)
  if RF-Track's format needs one.
- `laura/translator/converters/magnet.py` — add `to_rftrack()` overrides to
  `MagnetTranslator`, `DipoleTranslator`, `SolenoidTranslator` (mirrors the
  `to_astra`/`_write_ASTRA_quadrupole` etc. pattern at lines 187-338, 553-625,
  990-1057).
- `laura/translator/converters/cavity.py` — add `to_rftrack()` to
  `RFCavityTranslator` (mirrors `to_astra` at line 280-372).
- `laura/translator/converters/aperture.py` — add `to_rftrack()` to
  `ApertureTranslator` (mirrors `to_astra` at line 103-181).
- `laura/translator/converters/diagnostic.py`, `wake.py`, `plasma.py`,
  `laser.py`, `drift.py`, `twiss.py` — add `to_rftrack()` overrides only where
  RF-Track needs element-specific behaviour (many of these currently rely on
  the base-class stub for ASTRA, e.g. `DriftTranslator`/`DiagnosticTranslator`
  — RF-Track may follow the same "no explicit write, implicit in run script"
  pattern for drifts).
- `laura/translator/converters/codes/rftrack.py` — new module for RF-Track
  "run-level" helper classes (mirrors `codes/astra.py`'s `astra_header`/
  `astra_newrun`/`astra_output`/`astra_charge`/`astra_errors`, or
  `codes/gpt.py`'s `gpt_ccs` coordinate-system helper, depending on whether
  RF-Track's Python API is namelist-like or object/coordinate-system-like).
- `laura/translator/converters/section.py` — add `to_rftrack(self, ...) ->
  str | object` to `SectionLatticeTranslator` (mirrors `to_astra()` at line
  88-174 or `to_gpt()` at line 176-278, whichever shape fits RF-Track: a text
  deck built from per-block headers, or an object-per-element API sequence).
- `laura/translator/converters/layout.py` — add `to_rftrack()` to
  `MachineLayoutTranslator` (mirrors whatever pattern `to_astra`/`to_ocelot`
  use there — not fully read in this pass, but referenced via
  `MachineLayoutTranslator.from_layout(latt).to_astra()` in `model.py:31`).
- `laura/translator/converters/model.py` — add `to_rftrack(self) -> Dict[str,
  ...]` to `MachineModelTranslator` (mirrors `to_astra()` at line 28-32).
- `laura/translator/conversion_rules/keywords/keyword_conversion_rules_rftrack.yaml`
  and/or `laura/translator/conversion_rules/elements/elements_rftrack.yaml` —
  **only if** RF-Track ends up using the generic `full_dump()` +
  `_convertKeyword_<Code>` + `elements_<Code>` table-driven approach (like
  Elegant/Genesis/Opal); skip these if RF-Track instead needs bespoke
  dict-building per element (like ASTRA/GPT do, with keys as literals in the
  translator `.py` files).
- `laura/translator/conversion_rules/codes/rftrack_conversion.py` — **only
  if** RF-Track is driven via a Python object API (like Ocelot/Cheetah/Xsuite),
  mapping LAURA `hardware_type` → RF-Track element class, mirrors
  `conversion_rules/codes/ocelot_conversion.py`.
- `laura/Exporters/RFTrack.py` (optional, separate concern from the above) —
  `export_machine(path: str, machine: MachineModel, overwrite: bool = False)
  -> None`, mirrors `laura/Exporters/CATAP.py:32`, only needed if a
  standalone/round-trippable RF-Track file dump (independent of SIMBA-driven
  simulation runs) is wanted.
- `laura/unit_tests/test_rftrack_translator.py` (new) — mirrors the
  fixture/class/`tmp_path` shape of `laura/unit_tests/test_exporters_importers.py`:
  build a small `LAURA(element_list=[...], layout=..., section=...)` fixture,
  call the new `to_rftrack()` chain (or `export_machine` if an Exporter is
  added), assert on the returned string/object/file contents.

No registry file exists on the LAURA side analogous to SIMBA's
`Framework_lattices.py` — LAURA's translator layer has no dynamic
code-discovery mechanism; every target format is wired in by literally adding
a same-named method to each relevant existing class, as enumerated above.
