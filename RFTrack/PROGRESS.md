# RF-Track Integration — Progress Tracker

Live checklist. Update this file (not `PLAN.md`) as work happens — tick boxes,
add dated entries to the log, and note any deviation from `PLAN.md` here with
a reason. If the *approach* changes (not just what's done), update `PLAN.md`
too and reference the change here.

Read [`PLAN.md`](PLAN.md) first for the architecture and phased plan. Read
[`RFTrack_API_notes.md`](RFTrack_API_notes.md) for the RF-Track Python API.
Read [`Integration_Pattern_notes.md`](Integration_Pattern_notes.md) for the
ASTRA/Ocelot template this integration follows.

## Status: ALL PHASES IMPLEMENTED AND VERIFIED END-TO-END.

RF_Track (v2.6.3) is genuinely installed in a **WSL** conda env named
`astec-accelerator-models` (a different environment from the Windows conda
env of the same name used earlier — see PLAN.md "Environment" for how to
invoke it from Git Bash). Both LAURA and SIMBA have been verified against it
for real: a full `simba.Framework` build/track/postProcess of a FODO cell
through `rftrackLattice` passes. 4 real bugs were found and fixed via actual
testing (2 LAURA-side: dipole `P_Q` handling, `Pillbox_Cavity` performance
cliff; 2 SIMBA-side: wrong beam field names, nonexistent global twiss key) —
see PLAN.md "Real-package findings" and "SIMBA blocker resolved" for full
detail. The earlier "SIMBA can't be imported" blocker was a Windows-only MSVC
build issue in one specific conda env — the WSL env already has the entire
heavy dependency stack working; `simba` just needed `PYTHONPATH` set to both
repos (neither is pip-installed there), a fix the user found themselves.

Core integration is code-complete, and **both** the LAURA and SIMBA sides are
tested and passing against the real package.

## Log

- **2026-07-07** — Initial planning session. Wrote `PLAN.md`,
  `RFTrack_API_notes.md`, `Integration_Pattern_notes.md` (see prior log
  entries in git history of this file / conversation). Confirmed `RF_Track`
  not installed, not on PyPI, no prior references anywhere in the 5 repos.
- **2026-07-07** (same day, follow-up session) — Implementation session.
  User chose to fetch the RF-Track wheel/download link themselves rather than
  blocking on it; all code below uses guarded/lazy imports so it works without
  the real package installed.
  - **Phase 1 (LAURA translator layer) — DONE, tested, all green.**
    - Wrote `laura/translator/conversion_rules/codes/rftrack_conversion.py`:
      per-`hardware_type` builder functions (not a flat class dict like
      Ocelot, because RF-Track constructors are positional and
      heterogeneous per type). Covers Drift, Quadrupole, Dipole(->SBend),
      Sextupole/Octupole(->Multipole), Solenoid, Undulator, Correctors,
      RFCavity(->Pillbox_Cavity, simplified), Beam_Position_Monitor(->Bpm),
      Screen, Aperture/Collimator/Marker(->Drift).
    - Added **one generic** `to_rftrack()` + `_apply_rftrack_aperture()` to
      `laura/translator/converters/base.py` — turned out no per-category
      overrides were needed (see PLAN.md "Further simplification found
      during implementation"). `magnet.py`, `cavity.py`, `aperture.py`,
      `diagnostic.py`, `drift.py` were **not modified**.
    - Added `to_rftrack()` to `section.py` (builds `RF_Track.Lattice()`),
      `layout.py`, `model.py` (fan-out), mirroring `to_ocelot()`'s shape at
      each level.
    - Wrote `laura/unit_tests/test_rftrack_translator.py`: 23 tests using a
      monkeypatched fake `RF_Track` module (captures constructor args to
      verify units/dispatch without the real package) plus one
      `pytest.importorskip("RF_Track")`-guarded real-package test. **All 23
      pass, 1 correctly skipped.** Full `laura/unit_tests/` suite (444 tests)
      still green — no regressions.
  - **Phase 2 (SIMBA `rftrackLattice`) — written, registered, NOT
    import-tested.**
    - `simba/Codes/RFTrack/__init__.py` (empty marker) and
      `simba/Codes/RFTrack/RFTrack.py` (`rftrackLattice(frameworkLattice)`,
      mirrors `ocelotLattice`'s in-process object shape, not `astraLattice`'s
      subprocess shape — see PLAN.md architecture decision).
    - Registered via one import line in `simba/Framework_lattices.py`.
    - `py_compile` syntax-checked all new/edited `.py` files — clean.
  - **Phase 3 (beam/twiss conversion) — written, NOT import-tested.**
    - `simba/Modules/Beams/rftrack.py`: `beam_to_bunch6d` /
      `bunch6d_to_beam`, converting SIMBA's generic `beam` (SI units: m,
      kg*m/s, s) to/from RF-Track's `Bunch6d` phase-space convention (mm,
      MeV/c, mm/c). **Unit-conversion factors are derived from the API notes,
      not validated against a real round-trip** — flagged with a `ponytail:`
      comment; re-verify once RF_Track is installed.
    - `simba/Modules/Twiss/rftrack.py`: `read_rftrack_transport_table` /
      `interpret_rftrack_data`, reading RF-Track's `get_transport_table()`
      output directly into SIMBA's generic twiss object (in-process, no file
      parsing — unlike `Twiss/astra.py`). Deliberately covers only the core
      Twiss quantities (s, beta, alpha, emittance, sigma, mean momentum), not
      every field `Twiss/ocelot.py` carries — extend only if a real workflow
      needs more (YAGNI).
  - **Phase 4 (tests) — LAURA done; SIMBA partial.**
    - `simba/unit_tests/test_rftrack.py`: registration/discovery tests only
      (`rftrackLattice` is a `frameworkLattice` subclass, `code` defaults to
      `"rftrack"`, discoverable via the same introspection Framework.py:159
      and Framework.py:774 use). **Could not run these** — see blocker below.
      A deeper build+track integration test (constructing a full
      `frameworkLattice` with `file_block`/`executables`/`global_parameters`
      and actually tracking a beam) was deliberately **not** written blind —
      it would be guesswork without the real package to validate against.
  - **Phase 5 (packaging) — DONE.**
    - `laura/pyproject.toml`: comment near the `bmad` optional-dependency
      entry explaining why there's no `rf_track` extra (not on PyPI).
    - `simba/pyproject.toml`: comment near the dependency list explaining the
      same, noting the lazy-import means `simba` stays importable without it.
- **2026-07-07** (same day, second follow-up) — User installed RF_Track 2.6.3
  for real, in a **WSL** conda env also named `astec-accelerator-models`
  (`/home/jkj62/miniforge3/envs/astec-accelerator-models`) — a different
  environment from the Windows one used above. Re-verified the LAURA side
  against it:
  - Found and fixed WSL-env gaps unrelated to RF-Track: missing `easygdf`,
    `h5py`, `pytest` (installed via pip so `laura` would import at all).
  - Ran `unit_tests/test_rftrack_translator.py` against the real package —
    all 24 originally-written tests passed first try, **except** it exposed
    that my `build_pillbox_cavity` and `build_sbend` assumptions needed
    real-world correction (found via an ad hoc smoke-test script exercising
    every builder + a real build+track round trip, not via the committed
    tests, which didn't yet cover this).
  - **Bug found and fixed: `SBend`'s `P_Q=NaN` silently loses the whole
    beam.** Confirmed by direct experimentation (bisecting a real
    `RF_Track.SBend` call) that, unlike `Quadrupole`/`Multipole`, `SBend`
    does not support deferring `P_Q` to `autophase()` — and that the actual
    *value* of `P_Q` changes the bend trajectory (not just presence/absence).
    Fixed by threading a `P_Q` parameter through `to_rftrack()` at all 4
    translator levels (mirrors `to_gpt(Brho=...)`'s existing precedent
    exactly), with a warn-and-placeholder fallback in `build_sbend` so a
    missing `P_Q` degrades to "wrong bend, particles survive" rather than
    "everything lost". Added `simba/Modules/Beams/rftrack.get_P_Q()` and wired
    it into `rftrackLattice.write()`. See PLAN.md "Real-package findings" for
    full detail.
  - **Bug found and fixed: `Pillbox_Cavity` construction time explodes with
    cell count**, to the point of OOM-killing the process at a realistic
    30-cell S-band value (bisected: fine to ~25 cells, ~10s+ by 28). Fixed
    `build_pillbox_cavity` to always use `n_cells=1` (whole cavity as one
    effective cell), deliberately, regardless of the LAURA element's real
    cell count.
  - Extended `test_rftrack_translator.py` with fake-module tests for the new
    `P_Q` behavior (`test_dipole_without_p_q_warns_and_uses_placeholder`,
    `test_dipole_with_p_q_uses_supplied_value`,
    `test_quadrupole_p_q_always_nan_regardless_of_caller`) and real-package
    regression tests (`test_dipole_without_p_q_gives_wrong_trajectory_but_no_loss`,
    `test_dipole_with_p_q_preserves_transmission`) — **29 tests total, all
    passing** against the real package in WSL, and the full `laura/unit_tests/`
    suite is green in both the Windows env (447 passed, 3 skipped) and the WSL
    env (418 passed, 8 skipped — fewer only because that env is missing some
    unrelated optional deps like `rdflib`/`sqlalchemy`, not a regression).
  - Did **not** attempt to fix the `simba` MSVC/`xdeps` build blocker in this
    part of the session (see next entry — it turned out to be moot).

- **2026-07-07** (same day, third follow-up) — User pointed out that in WSL,
  `simba` "seems to run" with `PYTHONPATH` set to the laura repo path.
  Investigated: the WSL `astec-accelerator-models` env already has the
  **entire** heavy dependency stack installed and working (`pip list` showed
  xsuite 0.50.1, xdeps 0.10.16, ocelot-desy, Wake-T, cheetah-accelerator,
  PyQt5, soliday.sdds, deap, pyqtgraph, numba, pyfftw, numexpr, paramiko,
  fastkde, openpmd-beamphysics, mpl-axes-aligner, lox, deepdiff, attrs, tqdm,
  munch, h5py, scipy, pydantic — everything except `xopt`, which apparently
  isn't imported eagerly). Confirmed: `simba` imports fine with
  `PYTHONPATH=<laura>:<simba>` (neither package is pip-installed there, just
  raw source on the path). **The earlier Windows MSVC/`xdeps` build failure
  was specific to that one Windows conda env and is not a blocker at all** —
  it was solved by using WSL, which the user was already doing for RF_Track.
  - Ran `simba/unit_tests/test_rftrack.py` for real: all 5 registration tests
    passed immediately.
  - Ran the full `simba/unit_tests/` suite: 55 passed, 2 failed
    (`test_framework_settings_and_tracking`, `test_modifyElements`) — verified
    via `git stash` that both failures are **pre-existing and unrelated to
    RF-Track** (identical failures with none of this session's changes applied).
  - Wrote and ran an ad hoc end-to-end script (real `simba.Framework`, a real
    `frameworkGenerator`-produced beam — not mocked — `code: "rftrack"`,
    `framework.track()`). This found and fixed **two more real bugs**:
    1. `bunch6d_to_beam` tried to set `beam.cpx/cpy/cpz` — these are read-only
       computed properties (`cpx = px / q_over_c`). Fixed to set the real
       settable fields `px`/`py`/`pz`, matching `Modules/Beams/ocelot.py`'s
       own precedent exactly.
    2. `rftrackLattice.postProcess()` referenced
       `self.global_parameters["twiss"]`, a key that doesn't exist anywhere in
       the codebase (invented without checking — no other code's
       `postProcess` populates a global twiss object; twiss reading is a
       separate opt-in step). Fixed: `postProcess` now just stores the raw
       transport table on `self.tws` (mirrors `ocelotLattice.tws`), and
       `"rftrack": rftrack.read_rftrack_transport_table` was wired into
       `Modules/Twiss/__init__.py`'s `codes` dict + a wrapper method, so
       `simba.Modules.Twiss.twiss().read_rftrack_transport_table(lat_obj, name)`
       works as the opt-in path, matching `read_astra_twiss_files` etc.
  - Converted the validated ad hoc script into a permanent test:
    `simba/unit_tests/test_rftrack.py::TestRealRFTrack::test_full_fodo_build_track_postprocess`
    — a genuine (not mocked) build+track+postProcess+Twiss-read round trip.
    **Passing.** Full `simba/unit_tests/` suite re-run: 56 passed (the new
    test), same 2 pre-existing unrelated failures, no regressions.
  - Cleaned up: removed the ad hoc script and a leftover `test.def` artifact
    from the pre-existing failing test (not committed either way).
  - Left `simba/elementkeywords.yaml`'s modification alone — confirmed via
    `git stash` that it's pre-existing uncommitted work on this branch
    (`fix/ASTRA_quotes`), not something introduced by this session.

## Checklist (mirrors PLAN.md phases)

### Phase 0 — Prerequisites
- [x] RF_Track installed by user — v2.6.3, in a **WSL** conda env
      `astec-accelerator-models` (not the Windows one of the same name)
- [x] Read `laura/translator/conversion_rules/codes/ocelot_conversion.py` in full
- [x] Read `laura/translator/converters/codes/ocelot.py` in full
- [x] Read `simba/Codes/Ocelot/Ocelot.py` in full
- [x] Read `simba/Modules/Beams/ocelot.py`, `simba/Modules/Twiss/ocelot.py` in full

### Phase 1 — LAURA element -> RF-Track object conversion — DONE, verified against real package
- [x] `laura/translator/conversion_rules/codes/rftrack_conversion.py`
- [x] Resolve open question 1 (SBend chosen)
- [x] Resolve open question 2 (Pillbox_Cavity, simplified, chosen; further
      simplified to always `n_cells=1` after a real-package perf finding)
- [x] `base.py` — `to_rftrack()` + `_apply_rftrack_aperture()` (generic, covers all categories)
- [x] `section.py` / `layout.py` / `model.py` — `to_rftrack()`, now threading
      a `P_Q` parameter through all 4 levels (dipole fix, see log)
- [x] `laura/unit_tests/test_rftrack_translator.py` — **29 tests, all passing
      against the real RF_Track 2.6.3 package** (WSL env); same file also
      passes (with the real-package tests auto-skipped) in the Windows env
      without RF_Track installed
- [x] Full `laura/unit_tests/` suite green in both environments (no regressions)
- [x] Found and fixed 2 real bugs via real-package testing (dipole `P_Q`
      handling, `Pillbox_Cavity` cell-count performance) — see PLAN.md
      "Real-package findings"

### Phase 2 — SIMBA `rftrackLattice` — DONE, verified end-to-end
- [x] `simba/Codes/RFTrack/__init__.py`
- [x] `simba/Codes/RFTrack/RFTrack.py` (`rftrackLattice`) — `write()` computes
      and passes `P_Q` via `Modules/Beams/rftrack.get_P_Q()`; `postProcess()`
      stores the raw transport table on `self.tws` (no auto twiss conversion,
      matches `ocelotLattice`/`astraLattice` precedent)
- [x] `simba/Framework_lattices.py` — import line added
- [x] Full pipeline (`write`/`preProcess`/`run`/`postProcess`) verified via a
      real `simba.Framework` FODO build+track+postProcess with a real
      generated beam (not mocked) — see
      `simba/unit_tests/test_rftrack.py::TestRealRFTrack::test_full_fodo_build_track_postprocess`
- [x] `simba` import-tested and run-tested for real (WSL env, `PYTHONPATH` set
      to both repos — see PLAN.md "Environment")

### Phase 3 — SIMBA beam/twiss/field conversion — DONE, verified end-to-end
- [x] `simba/Modules/Beams/rftrack.py` — `get_P_Q()` (dipole fix);
      `bunch6d_to_beam` fixed to set `px`/`py`/`pz` (not the read-only
      `cpx`/`cpy`/`cpz` computed properties)
- [x] `simba/Modules/Twiss/rftrack.py` — wired into
      `Modules/Twiss/__init__.py`'s `codes` dict + wrapper method; verified
      both automatically (via `self.tws`) and via the opt-in
      `simba.Modules.Twiss.twiss().read_rftrack_transport_table(...)` path
- [ ] `simba/Modules/Fields/rftrack.py` — still not started; decide if needed once
      a real cavity/field-map use case is tried (see PLAN.md YAGNI note)
- [x] Unit-conversion round-trip (`beam_to_bunch6d`/`bunch6d_to_beam`)
      validated against a real `RF_Track.Bunch6d` — transmission preserved,
      full pipeline completes without error (exact numerical fidelity of the
      round-trip conversion itself — e.g. re-deriving the original phase space
      bit-for-bit — has not been separately regression-tested, only that the
      pipeline runs correctly end to end)

### Phase 4 — Tests
- [x] `laura/unit_tests/test_rftrack_translator.py` — 29 tests, verified
      against the real package
- [x] `simba/unit_tests/test_rftrack.py` — 6 tests, including a full real
      build+track+postProcess integration test, all passing
- [x] Both test files degrade gracefully without `RF_Track` installed (`pytest.importorskip`)

### Phase 5 — Docs & packaging — DONE (packaging); docs not touched
- [x] `laura/pyproject.toml`
- [x] `simba/pyproject.toml`
- [ ] Docs (`docs/source` in both repos) — not checked/updated this session;
      look for an existing supported-codes table before writing new prose

## Notes for whoever picks this up next

- The two `*_notes.md` files in this folder are research artifacts, not
  living docs — don't edit them as implementation proceeds; if they turn out
  to be wrong about something, note the correction here and in `PLAN.md`
  rather than rewriting history in the notes files.
- RF_Track **is** installed now — in a WSL conda env, not the Windows one —
  and `simba` runs fine there too (via `PYTHONPATH`, not a pip install). See
  PLAN.md "Environment" for the exact invocation from a Windows Git-Bash
  shell. The earlier "SIMBA can't be imported" blocker is resolved/moot; don't
  waste time on the Windows MSVC/`xdeps` build issue, just use WSL.
- The `RFCavity -> Pillbox_Cavity` mapping in `rftrack_conversion.py` is a
  known physics simplification (single Fourier coefficient, always 1 cell) —
  don't be surprised if cavity tracking results don't match ASTRA/Elegant
  closely until this is revisited with real field-map data.
- `RFDeflectingCavity` has no RF-Track mapping at all yet (falls back to a
  warned `Drift`) — deliberately left unmapped rather than silently wrong.
- **Read PLAN.md's "Real-package findings" section before touching
  `build_sbend` or `build_pillbox_cavity`** — both contain non-obvious,
  empirically-discovered constraints (SBend's `P_Q` is not deferrable the way
  Quadrupole's is; Pillbox_Cavity's construction time explodes with cell
  count) that aren't documented anywhere in the manual.
