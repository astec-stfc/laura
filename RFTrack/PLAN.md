# RF-Track Integration Plan

Status doc for integrating RF-Track (CERN, A. Latina) as a new tracking code into
LAURA and SIMBA. Read this file first; it links to two research notes with the
detailed evidence behind the decisions below. See `PROGRESS.md` in this same
folder for the live checklist — update that file as work proceeds, this file
only changes when the architecture/approach changes.

Supporting research (already done, read before writing code):
- [`RFTrack_API_notes.md`](RFTrack_API_notes.md) — distilled RF-Track Python API
  (Bunch6d/Bunch6dT, Lattice/Volume, element catalog, field maps, units).
  Source: `RFTrack.md` (the manual, badly mangled by PDF extraction — don't
  read it directly, this distillation already did that work).
- [`Integration_Pattern_notes.md`](Integration_Pattern_notes.md) — exact
  file:line map of how ASTRA is wired into SIMBA/LAURA today, used as the
  template. **Caveat**: it was researched against ASTRA (a subprocess/file-based
  code); §"Architecture decision" below corrects the parts that don't apply to
  RF-Track.

Environment: there are **two** `astec-accelerator-models` environments —
a Windows conda env (`C:\Users\jkj62.CLRC\.conda\envs\astec-accelerator-models\python.exe`,
no RF_Track — everything here uses guarded imports so it stays usable) and a
**WSL** conda env (`/home/jkj62/miniforge3/envs/astec-accelerator-models/bin/python`)
with **RF_Track 2.6.3 genuinely installed** (user installed it directly from
CERN, not PyPI). Use the WSL one for anything that needs the real package.
To invoke it from a Windows Git-Bash shell, prefix with `MSYS_NO_PATHCONV=1`
(otherwise Git Bash mistranslates the WSL path), e.g.:
```
MSYS_NO_PATHCONV=1 wsl -e bash -c "cd /mnt/c/Users/jkj62.CLRC/Documents/GitHub/laura && /home/jkj62/miniforge3/envs/astec-accelerator-models/bin/python -m pytest unit_tests/test_rftrack_translator.py"
```
The WSL env was also missing `easygdf`/`h5py`/`pytest` (pre-existing gaps,
unrelated to RF-Track) — installed via `pip install easygdf h5py pytest` there
to get `laura` importable at all.

**To run anything needing `simba` too**: neither `laura` nor `simba` is
pip-installed in the WSL env — put both on `PYTHONPATH` instead (the heavy
dependency stack — xsuite, ocelot-desy, Wake-T, cheetah-accelerator, PyQt5,
etc. — is already installed there):
```
MSYS_NO_PATHCONV=1 wsl -e bash -c "cd /mnt/c/Users/jkj62.CLRC/Documents/GitHub/simba && PYTHONPATH=/mnt/c/Users/jkj62.CLRC/Documents/GitHub/laura:/mnt/c/Users/jkj62.CLRC/Documents/GitHub/simba /home/jkj62/miniforge3/envs/astec-accelerator-models/bin/python -m pytest unit_tests/test_rftrack.py"
```

---

## Architecture decision: RF-Track follows the Ocelot/Xsuite pattern, not ASTRA

RF-Track ships as a compiled Python extension module (`pip install RF_Track`)
used **in-process**: you build `RF_Track.Lattice()`/`RF_Track.Bunch6d(...)`
Python objects directly and call `.track()` — there is no input-deck file and
no external executable to shell out to. This was confirmed against
`simba/Codes/Ocelot/Ocelot.py` (has `lat_obj`, `pin`, `pout` object attributes,
no `write()`-to-disk-then-subprocess step) and by grepping `Executables.py`/
`Executables.yaml` for "ocelot"/"xsuite" — no matches, confirming in-process
codes never get an executable registration.

Consequences for the plan (diverging from the ASTRA template in
`Integration_Pattern_notes.md` where noted):
- **No `simba/Codes/RFTrack/RFTrackRules.py`** — that mirrored ASTRA's raw
  namelist-keyword reference list, meaningless for an object API.
- **No `simba/Codes/Generators/rftrack.py`/`rftrack.yaml`** — the "Generators"
  layer exists to write a code-specific beam-generator input file (ASTRA's
  `generator` pre-processor); RF-Track takes a `Bunch6d`/`Bunch6dT` object
  directly, built from SIMBA's generic beam, so no separate generator step.
- **No `Executables.py`/`Executables.yaml` changes, no `define_rftrack_command`,
  no `prepare_executables` edit** — there is no binary to locate.
- **`laura/translator/converters/*`** — RF-Track needs a
  `laura/translator/conversion_rules/codes/rftrack_conversion.py` mapping
  `hardware_type -> RF_Track element class` (the Ocelot/Xsuite precedent), NOT
  an ASTRA-style namelist-string `to_rftrack()` returning text. Confirm this
  choice by reading `conversion_rules/codes/ocelot_conversion.py` before
  starting Phase 1 (not yet read in this research pass).
- **`simba/Modules/Beams/rftrack.py`, `Twiss/rftrack.py`, `Fields/rftrack.py`
  still needed**, but their job is converting between SIMBA's generic
  `beam`/`twiss`/`field` objects and RF-Track's own `Bunch6d`/`Bunch6dT`/
  `Bunch6d_twiss`/field-map Python objects in-memory — not parsing text files
  off disk (though `Bunch6d.save()`/`.load()`/`save_as_sdds_file()` exist if a
  file round-trip is ever wanted).
- **`simba/Codes/RFTrack/RFTrack.py`** defines `rftrackLattice(frameworkLattice)`
  mirroring `ocelotLattice`'s shape (object attributes `lat_obj: Any = None`
  for the `RF_Track.Lattice`, `pin`/`pout` for beams) rather than
  `astraLattice`'s file-path/subprocess shape. `write()` builds the
  `RF_Track.Lattice` object (via LAURA's `to_rftrack()` conversion chain);
  `run()`/`preProcess()`/`postProcess()` call `.track()` directly in Python.
- Registration is still just **one import line** in
  `simba/Framework_lattices.py` (`from .Codes.RFTrack.RFTrack import
  rftrackLattice  # noqa F401`) — the introspection-based `supported_codes`
  discovery in `Framework.py:159`/`774` is unaffected by any of the above; it
  only cares about the class name ending in `Lattice`.

Everything else in `Integration_Pattern_notes.md` (the 4-level translator
recursion `model.py -> layout.py -> section.py -> per-element category`, the
`BaseElementTranslator` stub-per-code convention, the Exporters-vs-translator
distinction, pyproject.toml per-code optional-dependency pattern) still
applies as documented.

### Further simplification found during implementation

The 4-level recursion still applies structurally, but **`to_rftrack()` only
needed to be implemented once**, in `base.py` — not per element-category file
(`magnet.py`, `cavity.py`, `aperture.py`, ...) as ASTRA/Ocelot/etc. do. This is
because RF-Track's builder functions are dispatched generically by
`hardware_type` string from a single dict
(`rftrack_conversion_rules`), and Python method resolution means the generic
`base.py` implementation still receives the fully-typed subclass instance
(e.g. calling `.to_rftrack()` on a `DipoleTranslator` still gives the builder
function access to `DipoleTranslator`-only computed fields like `e1`/`e2`).
See `laura/translator/converters/base.py`'s `to_rftrack`/`_apply_rftrack_aperture`
and `laura/translator/conversion_rules/codes/rftrack_conversion.py` for the
actual implementation. No edits were needed in `magnet.py`, `cavity.py`,
`aperture.py`, `diagnostic.py`, or `drift.py`.

## Dependency registration

- **LAURA** `pyproject.toml` — follows the existing per-code optional-extra
  pattern (`xsuite`, `ocelot`, `cheetah`, `wake_t`, `bmad` at lines 43-61): add
  ```
  rf_track = [
      "RF-Track>=2.3.0",
  ]
  ```
  and add `"RF-Track>=2.3.0"` to the `conversion` (line 65-71) and `full`
  (line 102-117) bundles. Confirm the actual PyPI package name/version pin
  (manual says `pip install RF_Track`, capitalization/hyphenation on PyPI
  needs double-checking at implementation time).
- **SIMBA** `pyproject.toml` — SIMBA's convention is hard dependencies, not
  optional extras (every other code — `ocelot-desy`, `xsuite`, `cheetah-accelerator`,
  `Wake-T` — is listed directly in `dependencies`, lines 19-48). Add the
  RF-Track package there too, matching that convention, not LAURA's optional-extra one.

## Phased implementation plan

### Phase 0 — Environment prerequisite
- [ ] Confirm the correct PyPI package name/version for RF-Track's Python
  bindings and `pip install` it into `astec-accelerator-models`.
- [ ] Read `laura/translator/conversion_rules/codes/ocelot_conversion.py` and
  `laura/translator/converters/codes/ocelot.py` (if it exists) in full as the
  concrete template for Phase 1 — the research pass identified but did not
  fully read these.
- [ ] Read `simba/Codes/Ocelot/Ocelot.py` in full (only lines 1-120 read so
  far) and `simba/Modules/Beams/ocelot.py`/`Twiss/ocelot.py` as the template
  for Phase 3.

### Phase 1 — LAURA: element -> RF-Track object conversion
Goal: given any LAURA `PhysicalBaseElement`, produce the matching
`RF_Track.<ElementClass>` Python object, and given a `SectionLattice`/
`MachineLayout`/`MachineModel`, produce a fully assembled `RF_Track.Lattice`.

- [ ] `laura/translator/conversion_rules/codes/rftrack_conversion.py` — dict
  mapping LAURA `hardware_type` -> RF-Track element class/constructor, e.g.
  `Drift -> RF_Track.Drift`, `Quadrupole -> RF_Track.Quadrupole`, `Dipole ->
  RF_Track.SBend`/`RBend` (need a rule: SBend if `physical.rotation`/pole
  faces are unset symmetric, RBend otherwise — check LAURA's `Dipole_Magnet`
  model fields against SBend/RBend constructor args in the API notes §4.1),
  `Solenoid -> RF_Track.Solenoid`, `RFCavity -> RF_Track.TW_Structure` /
  `SW_Structure` / `Pillbox_Cavity` (need a rule keyed on `cavity.cavity_type`
  or similar — check `laura/models/RF.py`), `Screen ->
  RF_Track.Screen`, `Beam_Position_Monitor -> RF_Track.Bpm`, `Aperture ->`
  (use `set_aperture()` on the preceding/enclosing element rather than a
  separate RF-Track element — RF-Track has no standalone aperture element,
  aperture is a property of every element).
- [ ] `laura/translator/converters/base.py` — add `to_rftrack(self, **kwargs)`
  stub (mirrors `to_ocelot`/`to_xsuite` shape: returns a constructed RF-Track
  object, not a string) using the conversion-rule dict above for anything not
  needing bespoke handling.
- [ ] `laura/translator/converters/magnet.py`,`cavity.py`,`aperture.py`,
  `diagnostic.py`,`drift.py` — override `to_rftrack()` only where a plain
  dict-driven mapping isn't enough (units conversion is the main risk here:
  LAURA/MAD-X convention vs RF-Track's mm/mrad/MeV-c internal units — see API
  notes §10 gotchas table before writing any of these).
- [ ] `laura/translator/converters/section.py` — `to_rftrack()` on
  `SectionLatticeTranslator`: build one `RF_Track.Lattice()`, `.append()` each
  translated element in section order (mirrors `to_ocelot()`'s shape, not
  `to_astra()`'s text-block shape).
- [ ] `laura/translator/converters/layout.py`, `model.py` — `to_rftrack()`
  fan-out across sections/layouts (mirrors `to_ocelot()`/`to_xsuite()`
  patterns at those levels).
- [ ] Units conversion helper(s) — a single well-tested module (candidate:
  `laura/translator/conversion_rules/codes/rftrack_units.py` or inline in
  `rftrack_conversion.py` if small) converting LAURA's stored units (SI: m,
  rad, ...) to RF-Track's (mm, mrad, MeV/c, mm/c for time) and back. Do not
  scatter ad-hoc unit multipliers across every translator file — ponytail:
  one small conversion module beats the same `*1000` sprinkled a dozen places.

### Phase 2 — SIMBA: `rftrackLattice`
- [ ] `simba/Codes/RFTrack/__init__.py` — empty package marker.
- [ ] `simba/Codes/RFTrack/RFTrack.py` — `rftrackLattice(frameworkLattice)`,
  `code: str = "rftrack"`, `lat_obj: Any = None` (the built `RF_Track.Lattice`),
  `pin`/`pout: Any = None` (RF-Track `Bunch6d`/`Bunch6dT` objects). Implement:
  - `model_post_init` — whatever one-time setup ASTRA/Ocelot do (check both
    before deciding); likely just base-class defaults, no namelist headers
    needed here.
  - `write()` — call `self.section.to_rftrack()` (Phase 1's output) to build
    `self.lat_obj`.
  - `preProcess()` — convert SIMBA's generic beam (`self.global_parameters["beam"]`,
    an openPMD/HDF5-backed object) into an `RF_Track.Bunch6d`/`Bunch6dT` via
    `simba/Modules/Beams/rftrack.py` (Phase 3), assign to `self.pin`.
  - `run()`/`postProcess()` — `self.pout = self.lat_obj.track(self.pin)`, then
    convert `self.pout` back to SIMBA's generic beam format and write it out
    (mirrors ASTRA's `astra_to_hdf5` / Ocelot's equivalent).
- [ ] `simba/Framework_lattices.py` — add
  `from .Codes.RFTrack.RFTrack import rftrackLattice  # noqa F401` (this is
  the entire registration; `supported_codes`/`read_Lattice` need no other edit).

### Phase 3 — SIMBA: beam/twiss/field conversion modules
- [ ] `simba/Modules/Beams/rftrack.py` — functions converting SIMBA's generic
  `beam` object <-> `RF_Track.Bunch6d`/`Bunch6dT` (in-memory object
  conversion, not file parsing — this is the main way this module differs
  from `Beams/astra.py`). Follow whatever signature convention
  `Modules/Beams/ocelot.py` uses (read it first, Phase 0).
- [ ] `simba/Modules/Twiss/rftrack.py` — SIMBA generic `twiss` object <->
  RF-Track `Bunch6d_twiss`/`get_info()` results, plus reading RF-Track's
  transport-table output (`get_transport_table(...)`, API notes §7-8) into
  SIMBA's twiss-array format.
- [ ] `simba/Modules/Fields/rftrack.py` — only needed if SIMBA needs to
  generate/read RF-Track field-map files independent of the object API;
  likely thin or unnecessary since RF-Track field-map objects
  (`RF_FieldMap_1d/2d/3d`, `Static_Magnetic_FieldMap_*`) are constructed
  directly from LAURA's field-map data in Phase 1's conversion step. Decide
  once Phase 1 is underway — don't build this speculatively if Phase 1 turns
  out to cover it (YAGNI).

### Phase 4 — Unit tests
- [ ] LAURA: `laura/unit_tests/test_rftrack_translator.py` — mirrors
  `test_exporters_importers.py`'s shape (small hand-built `LAURA(...)`
  fixture, plain pytest classes, `tmp_path` where needed). Cover: unit
  conversion correctness (this is the highest-risk area — assert exact
  expected mm/mrad/MeV-c values for at least one of each element category),
  one element of each mapped `hardware_type`, and a small multi-element
  section producing a `Lattice` with the right element count/order.
- [ ] SIMBA: extend `simba/unit_tests/test_track.py`'s parametrize list with
  `("rftrack", rftrackLattice)` if/when that file is revived, or add a new
  `simba/unit_tests/test_rftrack.py` following `test_framework_lattice.py`'s
  fixture shape otherwise. Cover: a small FODO-style lattice (mirrors the
  manual's own FODO example in `RFTrack_API_notes.md` §11) built via SIMBA,
  tracked through `rftrackLattice`, and Twiss/phase-space results sanity
  checked (e.g. beta functions periodic/positive, transmission == 1 for a
  loss-free lattice).
- [ ] Both test suites must be skippable/xfail gracefully if `RF_Track` isn't
  installed in the environment running CI (check how `ocelot`/`xsuite`
  optional imports are guarded elsewhere, e.g. `pytest.importorskip` or a
  `try/except ImportError` module guard) — mirror that pattern exactly,
  don't invent a new one.

### Phase 5 — Docs & packaging (do last, low effort)
- [ ] `laura/pyproject.toml`, `simba/pyproject.toml` — dependency entries per
  the "Dependency registration" section above.
- [ ] `docs/source` in both repos — add RF-Track to whatever
  supported-codes list/table already documents ASTRA/Elegant/GPT/etc., if one
  exists (check before writing new docs prose — ponytail: don't add a new
  docs page if a table just needs one more row).

---

## Open questions — resolution status

1. **SBend vs RBend mapping for LAURA `Dipole`** — RESOLVED: `SBend`. LAURA's
   `Dipole_Magnet`/`DipoleTranslator` already stores explicit `e1`/`e2`
   entrance/exit edge angles per element (`magnet.py`'s `DipoleTranslator.e1`/
   `.e2` computed fields), which map directly onto `SBend(L, P_Q, angle, E1, E2)`
   with no rectangular-geometry re-derivation needed. Implemented in
   `rftrack_conversion.build_sbend`.
2. **RFCavity mapping** — RESOLVED (pragmatically, flagged for later
   improvement): a single-Fourier-coefficient `Pillbox_Cavity` approximating
   the cavity as a uniform on-axis field (`rftrack_conversion.build_pillbox_cavity`,
   marked with a `ponytail:` comment). This is a genuine physics
   simplification, not full TW/SW fidelity — upgrade once LAURA stores
   per-cell field-map Fourier coefficients for a cavity. `RFDeflectingCavity`
   is deliberately left unmapped (falls back to a warned Drift) rather than
   silently using the wrong (longitudinal, not transverse) kick physics.
3. **Does RF-Track need its own Generator step at all?** RESOLVED: no. SIMBA's
   generic beam, converted in `rftrackLattice.preProcess()` via
   `Modules/Beams/rftrack.py`, is sufficient. No `Codes/Generators/rftrack.py`
   was created.
4. **Confirm exact PyPI package name** — RESOLVED: there isn't one. RF-Track is
   not on PyPI under any spelling checked (`RF_Track`, `RF-Track`, `rf-track`,
   `rf_track`, `RFTrack`, `rftrack`) — confirmed pip's index works correctly
   against real packages (tested with `numpy`), so this is a real absence, not
   a network issue. It must be downloaded from CERN's RF-Track page directly.
   pyproject.toml in both repos documents this with a comment instead of a
   (currently unusable) dependency/extras entry.

## Real-package findings (verified against RF_Track 2.6.3 in WSL)

The user installed the real RF-Track package in a **WSL** conda env (see
"Environment" above) after the first implementation pass. Re-testing against
it surfaced two real bugs/gotchas that the manual doesn't warn about — fixed
in code, documented here so nobody re-discovers them the hard way:

1. **`SBend`'s `P_Q` is not deferrable like `Quadrupole`/`Multipole`'s is.**
   The manual documents a `P_Q=NaN` convention for `Quadrupole`/`Multipole`
   ("defer gradient calc to `autophase()`") but says nothing either way about
   `SBend`. Empirically: passing `NaN` for `SBend`'s `P_Q` **silently produces
   zero transmission** (the whole bunch lost) — not a crash, not a warning,
   just a lattice that loses every particle. Worse, the *value* of `P_Q`
   materially changes the bend trajectory (tested 4 values: `mean_x` came out
   -54220, 250, 1.35e16, -250 — not just sign/magnitude noise), so it cannot
   be a dummy placeholder either. **Fix**: `to_rftrack()` now threads an
   explicit `P_Q` parameter through all 4 translator levels (element -> section
   -> layout -> model), exactly mirroring how `to_gpt(Brho=...)` already
   threads the equivalent rigidity value through this same codebase. If no
   `P_Q` is supplied, `build_sbend` warns loudly and substitutes `1.0` (avoids
   the catastrophic zero-transmission case, but the bend will still be
   physically wrong — the warning says so). `simba/Codes/RFTrack/RFTrack.py`'s
   `write()` now computes a real `P_Q` from the beam via the new
   `Modules/Beams/rftrack.get_P_Q()` helper. Regression tests for both the
   fake-module and real-package cases are in `test_rftrack_translator.py`
   (`TestElementToRFTrack`/`TestRealRFTrack`, dipole-related tests).
2. **`Pillbox_Cavity` construction time explodes with cell count.** Tested
   `n_cells` from 1 to 30 with the same single Fourier coefficient: fine up to
   ~25 cells, ~10s+ at 28, and the original attempt at a realistic 30-cell
   S-band value got the whole process OOM-killed. `Pillbox_Cavity` is a
   few-cell standing-wave element, not meant for many-cell travelling-wave
   linac sections. **Fix**: `build_pillbox_cavity` now always collapses to
   `n_cells=1` (whole cavity as one effective cell) regardless of the LAURA
   element's real `cavity.n_cells`/`cell_length` — deliberately, not as an
   oversight — which keeps it fast and sidesteps the cliff entirely, at the
   cost of even coarser physics fidelity than before (already a known
   simplification, see open question 2 above).

Every other builder (`Drift`, `Quadrupole`, `Solenoid`, `Undulator`,
`Corrector`, `Multipole`/Sextupole/Octupole, `Bpm`, `Screen`, aperture-as-Drift)
was exercised individually against the real package with realistic parameter
values and worked without incident on the first try.

## SIMBA blocker resolved — two more real bugs found and fixed

The Windows `pip install -e simba` build failure (MSVC/`xdeps`) was a
red herring specific to that one Windows conda env: the **WSL**
`astec-accelerator-models` env already has the entire heavy dependency stack
built and working (xsuite, xdeps, ocelot-desy, Wake-T, cheetah-accelerator,
PyQt5, etc. — confirmed via `pip list`). `simba` imports and runs fine there
once both `laura` and `simba` are on `PYTHONPATH` (neither is pip-installed
there; the user's own tip: `PYTHONPATH=/mnt/c/.../laura:/mnt/c/.../simba`).
No environment fix was needed — just the right `PYTHONPATH`.

With `simba` actually running, a real end-to-end `simba.Framework` FODO
build/track/postProcess (a real `frameworkGenerator`-produced beam, not a
mock) surfaced two more real bugs in the SIMBA-side code, both fixed:

1. **`bunch6d_to_beam` tried to set `cpx`/`cpy`/`cpz` on SIMBA's generic
   beam — those are read-only computed properties** (`cpx = px / q_over_c`,
   see `Modules/Beams/Particles/__init__.py:532`). The real settable SI
   momentum fields are `px`/`py`/`pz`, exactly matching how
   `Modules/Beams/ocelot.py`'s own `particle_array_to_beam` sets them. Fixed
   in `Modules/Beams/rftrack.py`.
2. **`postProcess` referenced a `global_parameters["twiss"]` key that does
   not exist anywhere in the codebase** — invented without checking (no other
   code's `postProcess` populates a global twiss object at all; ASTRA/Ocelot
   only *save twiss data to a file* in `postProcess`, and reading it back into
   a `simba.Modules.Twiss.twiss()` instance — note: **not** the same class as
   `beam.twiss`, which is a different, unrelated `Particles.twiss.twiss` — is
   a separate, opt-in step a user/notebook does afterward, e.g.
   `simba.Modules.Twiss.twiss().read_astra_twiss_files(...)`). Fixed by: (a)
   `rftrackLattice.postProcess()` now just stores the raw transport table on
   `self.tws` (mirrors `ocelotLattice.tws`, no auto-conversion), and (b) wired
   `"rftrack": rftrack.read_rftrack_transport_table` into
   `Modules/Twiss/__init__.py`'s `codes` dict (both the module-level and
   instance-level copies) plus a `read_rftrack_transport_table` wrapper
   method on the `twiss` class, so the same opt-in call other codes support
   now works for RF-Track too: `simba.Modules.Twiss.twiss().read_rftrack_transport_table(lat_obj, name)`.

Both fixes are covered by `simba/unit_tests/test_rftrack.py::TestRealRFTrack::test_full_fodo_build_track_postprocess`
(a genuine `simba.Framework` build+track+postProcess, not mocked) — passing.

## Implementation status (see PROGRESS.md for the live checklist)

**All phases are now implemented and verified against the real RF_Track
package end-to-end**, on both the LAURA side (29 tests) and the SIMBA side (6
tests, including a full `simba.Framework` FODO build/track/postProcess).
Total of 4 real bugs found and fixed this session via actual testing (2
LAURA-side: `SBend` `P_Q`, `Pillbox_Cavity` cell count; 2 SIMBA-side:
`cpx`/`px` field name, nonexistent `global_parameters["twiss"]`) — none of
which would have been caught by code review alone. Remaining open items are
in PROGRESS.md's checklist (mainly: `Modules/Fields/rftrack.py` not started,
per the YAGNI note; the two known cavity-physics simplifications; and the two
pre-existing, unrelated `simba` test failures noted there).
