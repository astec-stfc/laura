"""Track a Bmad lattice natively and through LAURA -> SIMBA, and compare.

This is the end-to-end check that a LAURA import is faithful enough to *track*
with, not merely to read. It runs the same bunch through the same lattice twice:

    native   Tao on the original .bmad lattice
    round    Tao on the lattice LAURA exported from its own imported model

and reports the relative difference in the beam moments at every element the two
have in common. A translator bug that a static element-by-element comparison
misses -- a sign, a missing wake, a phase convention -- shows up here as a
divergence that grows from the element where it was introduced.

Stages
------
Each stage writes its result into ``--workdir`` and can be re-run on its own::

    beam      a Bmad ASCII .beam0 -> openPMD HDF5, in both z conventions
    import    the native lattice -> a pickled LAURA MachineModel
    native    track the original lattice in Tao -> native_result.json
    round     export the LAURA model, track it through SIMBA
    compare   the two result sets, side by side
    all       every stage above, in order

``all`` runs each stage in a **fresh subprocess**. This is not tidiness: Tao
keeps global Fortran state, so two ``Tao`` objects in one interpreter quietly
corrupt each other's lattice.

Run from the repository root::

    python examples/bmad_tracking_comparison.py all \\
        --tao-init $LCLS_LATTICE/bmad/models/cu_hxr/tao.init \\
        --libtao $BMAD_DIST/production/lib/libtao.so \\
        --machine-area CU_HXR --position-mode floor \\
        --start OTR2 --end ENDDMPH_2 \\
        --bmad-beam $LCLS_LATTICE/bmad/beams/OTR2_...beam0 --particles 2000 \\
        --workdir /tmp/cu_hxr_check

and then, for the control that tells you how much of the residual is the
translation itself rather than the wakes::

    python examples/bmad_tracking_comparison.py all --no-wakes ...same...

Reading the output
------------------
Report the **median** as well as the max. One bad element in 1250 is a different
finding from a systematic drift.

The centroids are reported as a fraction of the beam size (marked ``(/sigma_x)``
in the table) rather than of themselves. On a lattice with no deliberate orbit
distortion the centroid is ~1e-8 m -- numerically zero -- so its own relative
difference is noise over noise and reads as ~2, which is not a finding.

Interpret every number against the ``--no-wakes`` control. On LCLS ``cu_hxr``
the wake-free floor is ~1e-3 in the transverse moments, so only ``sigma_z``
-- 1.9e-3 with wakes against a 1.1e-3 floor -- is actually reporting on the
wakes. See ``--wake-samples`` for what that residual is made of.
"""

import argparse
import json
import os
import pickle
import re
import shutil
import subprocess
import sys
import time
import warnings
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

STAGES = ("beam", "import", "native", "round", "compare")

# Quantities compared, as (label, key in Tao's bunch_params, key in SIMBA's
# twiss HDF5, unit, scale). The two codes name the same moment differently,
# which is most of why this table exists.
#
# ``scale`` names another quantity to divide the difference by, instead of the
# value's own magnitude. Only the centroids need it, and they need it badly: on
# a lattice with no deliberate orbit distortion the centroid is ~1e-8 m, which
# is numerically zero, so |a-b|/|a| on it is noise divided by noise and reports
# ~2 -- a number that means nothing and swamps the summary. What actually
# matters is the centroid difference *as a fraction of the beam size*, which is
# what dividing by sigma gives.
FIELDS = (
    ("delta_s", "s_pos", "s", "m", None),
    ("sigma_x", "twiss_sigma_x", "beam_sigma_x", "m", None),
    ("sigma_y", "twiss_sigma_y", "beam_sigma_y", "m", None),
    ("sigma_z", "twiss_sigma_z", "beam_sigma_z", "m", None),
    ("norm_emit_x", "twiss_norm_emit_x", "beam_norm_emit_x", "m.rad", None),
    ("norm_emit_y", "twiss_norm_emit_y", "beam_norm_emit_y", "m.rad", None),
    ("beta_x", "twiss_beta_x", "beam_beta_x", "m", None),
    ("beta_y", "twiss_beta_y", "beam_beta_y", "m", None),
    ("centroid_x", "centroid_vec_1", "beam_x", "m", "sigma_x"),
    ("centroid_y", "centroid_vec_3", "beam_y", "m", "sigma_y"),
    ("p0c", "centroid_p0c", "beam_p0c", "eV/c", None),
    ("n_live", "n_particle_live", "beam_n_particle", "", None),
)


@dataclass
class Layout:
    """Where every stage puts its output.

    The wake-on and wake-free runs get separate names throughout so both can
    live in one workdir -- you need them side by side to read the result, and
    accidentally comparing one against the other is the single easiest way to
    misread this script (it reports a 59 % ``sigma_z`` error on ``cu_hxr`` that
    is pure bookkeeping).
    """

    workdir: Path
    wakes: bool

    @property
    def tag(self) -> str:
        return "" if self.wakes else "_nowake"

    @property
    def model(self) -> Path:
        return self.workdir / f"model{self.tag}.pkl"

    @property
    def native_dir(self) -> Path:
        return self.workdir / f"native{self.tag}"

    @property
    def native_result(self) -> Path:
        return self.workdir / f"native{self.tag}_result.json"

    @property
    def round_dir(self) -> Path:
        return self.workdir / f"round{self.tag}"

    @property
    def comparison(self) -> Path:
        return self.workdir / f"comparison{self.tag}.json"

    @property
    def native_beam(self) -> Path:
        """openPMD beam in the fixed-s convention Bmad reads and writes."""
        return self.workdir / "beam_screen.openpmd.hdf5"

    @property
    def round_beam(self) -> Path:
        """The same bunch in the convention SIMBA's beam objects expect."""
        return self.workdir / "beam_simba.openpmd.hdf5"


def _heading(title: str) -> None:
    print()
    print(title)
    print("-" * len(title))


def design_lattice_file(tao_init: Path) -> Path:
    """The ``.bmad`` lattice a ``tao.init`` points at.

    The native run needs its own ``tao.init`` -- one that saves beams at every
    marker and starts where we want -- so it cannot reuse the model's. Rather
    than make the caller repeat the lattice path, pull it out of theirs.
    ``design_lattice(1)%file`` is normally relative to the init file and may
    carry environment variables (``$LCLS_LATTICE/...``).
    """
    text = tao_init.read_text()
    match = re.search(
        r"^\s*design_lattice\(\d+\)%file\s*=\s*['\"]([^'\"]+)['\"]",
        text,
        re.MULTILINE,
    )
    if match is None:
        raise SystemExit(
            f"no design_lattice(n)%file in {tao_init}; pass --lattice explicitly"
        )
    raw = os.path.expandvars(match.group(1).strip())
    path = Path(raw)
    if not path.is_absolute():
        path = tao_init.parent / path
    if not path.exists():
        raise SystemExit(f"lattice {path} (from {tao_init}) does not exist")
    return path


# -- beam ----------------------------------------------------------------------


def stage_beam(args, layout: Layout) -> None:
    """Convert a Bmad ASCII bunch into the two openPMD files the run needs.

    Bmad phase space at a fixed *s* is ``(x, px/P0, y, py/P0, z, P/P0 - 1)``
    with ``z = -beta*c*(t - t_ref)``, so the conversion back to lab momenta and
    time is exact given the reference momentum.

    The two output files hold the *same bunch* under two conventions, and this
    is a genuine trap rather than a formality:

    * ``screen`` puts every particle at the same ``z`` and carries the
      longitudinal spread in ``t``. That is openPMD's fixed-s convention, and
      what Bmad writes and reads.
    * ``simba`` carries the spread in ``z`` and uses ``t`` only for the
      reference time. A screen-type file loaded into SIMBA arrives with **zero
      bunch length** -- no error, just a wrong answer, and one that looks like a
      translator bug.
    """
    from beamphysics import ParticleGroup
    from scipy.constants import c, e, m_e

    source = Path(args.bmad_beam).expanduser()
    p0c = args.p0c if args.p0c else _reference_momentum(args, layout)
    print(f"reference momentum at {args.start}: {p0c:.6e} eV/c")

    with source.open() as handle:
        for line in handle:
            if line.startswith("BEGIN_BUNCH"):
                break
        species = next(handle).split("!")[0].strip()
        charge = float(next(handle).split("!")[0])
        next(handle)  # mean z, unused: the conversion is relative to t_center
        t_center = float(next(handle).split("!")[0])
        body = [
            row for row in handle if row.strip() and not row.startswith("END_BUNCH")
        ]
    data = np.loadtxt(body)
    print(f"read {data.shape[0]} particles of {species}, charge {charge:.4g} C")

    if args.particles and args.particles < len(data):
        # A fixed seed so the native and round-trip runs get the same bunch;
        # they are separate processes and must not each draw their own.
        chosen = np.sort(
            np.random.default_rng(args.seed).choice(
                len(data), args.particles, replace=False
            )
        )
        data = data[chosen]
        print(f"subsampled to {len(data)} particles (seed {args.seed})")

    x, px_norm, y, py_norm, z_bmad, pz_norm = data[:, :6].T
    weights = data[:, 6]

    momentum = p0c * (1.0 + pz_norm)
    px = px_norm * p0c
    py = py_norm * p0c
    pz = np.sqrt(np.maximum(momentum**2 - px**2 - py**2, 0.0))

    mc2 = m_e * c**2 / e
    gamma = np.sqrt(1.0 + (momentum / mc2) ** 2)
    beta = momentum / (gamma * mc2)
    t = t_center - z_bmad / (beta * c)
    # Renormalise so a subsampled bunch still carries the full original charge.
    weights = np.abs(weights) / np.abs(weights).sum() * charge

    for target, mode in ((layout.native_beam, "screen"), (layout.round_beam, "simba")):
        z_out = -beta * c * (t - t.mean()) if mode == "simba" else np.zeros_like(x)
        group = ParticleGroup(
            data=dict(
                x=x,
                y=y,
                z=z_out,
                px=px,
                py=py,
                pz=pz,
                t=t,
                status=np.ones(len(x), dtype=int),
                weight=weights,
                species=species,
            )
        )
        group.write(str(target))
        print(
            f"  {mode:<7} -> {target.name}  n={len(group)} "
            f"charge={group.charge:.4e} C sigma_z={np.std(z_out):.4e} m "
            f"sigma_t={group.std('t'):.4e} s"
        )


def _reference_momentum(args, layout: Layout) -> float:
    """Ask Tao for ``p0c`` at the start element, so it is never a magic number.

    Getting this wrong does not fail loudly: the bunch simply arrives at a
    slightly different energy on one side than the other, and the comparison
    reports it as a translation error.
    """
    from pytao import Tao

    lattice = args.lattice or design_lattice_file(Path(args.tao_init).expanduser())
    tao = Tao(lattice_file=str(lattice), so_lib=args.libtao, noplot=True)
    return float(tao.lat_list(args.start, "ele.p0c")[0])


# -- import --------------------------------------------------------------------


def stage_import(args, layout: Layout) -> None:
    """Native Bmad lattice -> a LAURA ``MachineModel``, pickled for later stages.

    ``position_mode="floor"`` takes each element's position from Bmad's floor
    coordinates rather than re-deriving it from lengths, which is what keeps a
    3000-element lattice's geometry exact through the round trip.
    """
    from laura.translator.converters.codes.bmad import BmadLatticeImporter

    started = time.time()
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        importer = BmadLatticeImporter(
            tao_init=str(Path(args.tao_init).expanduser()),
            libtao=args.libtao,
            position_mode=args.position_mode,
            machine_area=args.machine_area,
            wake_samples=args.wake_samples,
        )
        model = importer.create_machine_model()
    print(f"imported {len(model.elements)} elements in {time.time() - started:.1f} s")
    print(f"sections: {[name for name in model.sections]}")

    unresolved = sum(1 for entry in caught if "resolve" in str(entry.message))
    if unresolved:
        print(
            f"{unresolved} wake resolution warning(s): the sampling grid is "
            "coarser than the wake structure. Raise --wake-samples."
        )

    carried = _wake_carriers(model)
    if not args.wakes:
        # The control run. Drop the samples rather than re-importing without
        # them, so the two models differ in exactly one thing.
        for element in carried:
            element.simulation.wakefield_definition = None
        print(f"stripped short-range wakes from {len(carried)} element(s)")
    else:
        print(f"elements carrying a short-range wake: {len(carried)}")

    layout.model.parent.mkdir(parents=True, exist_ok=True)
    with layout.model.open("wb") as handle:
        pickle.dump(model, handle)
    print(f"wrote {layout.model}")


def _wake_carriers(model) -> List[object]:
    return [
        element
        for element in model.elements.values()
        if getattr(getattr(element, "simulation", None), "wakefield_definition", None)
        is not None
    ]


# -- native --------------------------------------------------------------------


NATIVE_INIT = """&tao_start
  n_universes = 1
/

&tao_design_lattice
  design_lattice(1)%file = '{lattice}'
/

&tao_params
  global%track_type = 'single'
  global%plot_on = F
  bmad_com%radiation_damping_on = F
  bmad_com%radiation_fluctuations_on = F
{wake_flags}/

&tao_beam_init
  ix_universe = 1
  beam_saved_at = "MARKER::*, MONITOR::*"
  track_start = '{start}'
  beam_init%position_file = '{beam}'
/
"""


def stage_native(args, layout: Layout) -> None:
    """Track the original lattice in Tao and record the moments by name.

    Radiation is switched off on both sides. Leaving fluctuations on (the
    ``cu_hxr`` model's own default) makes every re-run differ from the last,
    which buries a translation error of this size in noise.
    """
    from pytao import Tao

    lattice = args.lattice or design_lattice_file(Path(args.tao_init).expanduser())
    flags = (
        "" if args.wakes else "  bmad_com%sr_wakes_on = F\n  bmad_com%lr_wakes_on = F\n"
    )
    layout.native_dir.mkdir(parents=True, exist_ok=True)
    init = layout.native_dir / "tao.init"
    init.write_text(
        NATIVE_INIT.format(
            lattice=lattice,
            wake_flags=flags,
            start=args.start,
            beam=layout.native_beam.resolve(),
        )
    )
    print(f"wrote {init} (wakes {'on' if args.wakes else 'off'})")

    # Tao resolves the init file relative to the working directory, and writes
    # its .digested cache beside the lattice keyed by *filename* -- so a
    # wake-on and a wake-free run of the same lattice must not share a
    # directory, or the second silently reads the first's cache.
    previous = Path.cwd()
    try:
        os.chdir(layout.native_dir)
        started = time.time()
        tao = Tao(init_file="tao.init", so_lib=args.libtao, noplot=True)
        print(f"loaded lattice in {time.time() - started:.1f} s")
        started = time.time()
        tao.cmd("set global track_type = beam")
        print(f"tracked in {time.time() - started:.1f} s")

        names = tao.lat_list("*", "ele.name", flags="-array_out -no_slaves")
        positions = tao.lat_list("*", "ele.s", flags="-no_slaves")
    finally:
        os.chdir(previous)

    records = []
    for name, s_exit in zip(names, positions):
        try:
            params = tao.bunch_params(name)
        except Exception:  # noqa: BLE001, S112 -- absence is the signal, not an error
            # No beam saved here. Only markers and monitors carry one.
            continue
        if not params or params.get("n_particle_live", 0) == 0:
            continue
        # bunch_params already has an "s" key, so build the record first and
        # assign the extras after: dict(params, s=...) raises.
        record = {
            key: (float(value) if isinstance(value, (int, float, bool)) else value)
            for key, value in params.items()
        }
        record["name"] = name
        record["s_pos"] = float(s_exit)
        records.append(record)

    layout.native_result.write_text(json.dumps(records))
    print(f"saved {len(records)} bunches -> {layout.native_result}")


# -- round trip ----------------------------------------------------------------


def stage_round(args, layout: Layout) -> None:
    """Export the LAURA model and track it through SIMBA.

    Three things here are load-bearing and none are obvious:

    * ``Framework.loadSettings`` builds its own ``LAURA`` from the settings.
      Do **not** pass ``machine=model`` -- ``Framework.machine`` wants a
      ``LAURA``, not a ``MachineModel``.
    * ``preProcess()`` *resets* ``csr_enable``, ``lsc_enable`` and
      ``space_charge_n_bin``. Set them after it, or the written lattice carries
      ``bmad_com[csr_and_space_charge_on] = T`` however many times you set them
      before, and you are no longer comparing like with like.
    * SIMBA tracks ``BEGINNING`` to ``END``, so a lattice containing an element
      literally *named* ``END`` -- ``cu_hxr`` has one -- fails with
      ``MULTIPLE TRACK_END ELEMENTS FOUND``. Name the real last element as
      ``--end`` instead.
    """
    import simba.Framework as fw

    from laura.Exporters.YAML import export_machine

    with layout.model.open("rb") as handle:
        model = pickle.load(handle)
    key = args.name or next(iter(model.sections))
    exported = layout.round_dir / "lattice"
    layout.round_dir.mkdir(parents=True, exist_ok=True)

    started = time.time()
    export_machine(path=str(exported), machine=model, overwrite=True)
    print(f"export_machine {time.time() - started:.1f} s -> {exported}")

    settings = fw.FrameworkSettings()
    settings.files = {
        key: {
            "code": "bmad",
            "charge": {"space_charge_mode": "False"},
            "input": {},
            "output": {"start_element": args.start, "end_element": args.end},
        }
    }
    settings.layout = model.layout
    settings.section = {
        "sections": {name: section.names for name, section in model.sections.items()}
    }
    settings.element_list = str(exported)

    framework = fw.Framework(
        directory=str(layout.round_dir), clean=False, verbose=False
    )
    framework.loadSettings(settings=settings)
    lattice = framework[key]
    lattice.libtao = args.libtao

    # SIMBA reads the input bunch from <workdir>/<start element>.openpmd.hdf5.
    shutil.copy(layout.round_beam, layout.round_dir / f"{args.start}.openpmd.hdf5")

    lattice.preProcess()
    lattice.space_charge_n_bin = None
    lattice.section.csr_enable = False
    lattice.section.lsc_enable = False
    lattice.write()
    written = Path(lattice.lattice_file)
    wakes = len(re.findall(r"sr_wake\s*=", written.read_text()))
    print(f"wrote {written.name}: {wakes} element(s) with sr_wake")
    if args.wakes and not wakes:
        print(
            "  no wakes in the export. Comparing this against a wake-carrying "
            "native run reports a large sigma_z error that is not a bug."
        )

    started = time.time()
    lattice.run()
    print(f"run {time.time() - started:.1f} s")
    started = time.time()
    lattice.postProcess()
    print(f"postProcess {time.time() - started:.1f} s")


# -- compare -------------------------------------------------------------------


def stage_compare(args, layout: Layout) -> bool:
    """Match the two runs by element *name* and report the moment differences.

    Not by index and not by ``s``: SIMBA's ``s`` is offset by the floor ``z``
    of the start element, and coincident-s clusters pair different elements
    against each other. Names are the only stable key.
    """
    import h5py

    with layout.native_result.open() as handle:
        native = {record["name"]: record for record in json.load(handle)}

    key = args.name or _section_key(layout)
    twiss = layout.round_dir / f"{key}_twiss.bmad.hdf5"
    with h5py.File(twiss, "r") as handle:
        rounded = {
            name: (
                value.asstr()[:]
                if h5py.check_string_dtype(value.dtype)
                else np.array(value)
            )
            for name, value in handle.items()
        }

    names = list(rounded["element_name"])
    print(f"native records: {len(native)}   round-trip records: {len(names)}")

    s_native = native[args.start]["s_pos"]
    s_round = float(rounded["s"][0])

    rows = []
    for index, name in enumerate(names):
        record = native.get(name)
        if record is None or rounded["beam_n_particle"][index] <= 0:
            continue
        row = {"name": name}
        for label, native_key, round_key, _, _ in FIELDS:
            left, right = float(record[native_key]), float(rounded[round_key][index])
            if label == "delta_s":
                left, right = left - s_native, right - s_round
            row[label] = (left, right)
        rows.append(row)

    print(f"common elements with a live bunch on both sides: {len(rows)}")
    if not rows:
        print("no overlap -- check --start/--end and that both runs saved beams")
        return False

    native_side = {
        label: np.array([row[label][0] for row in rows]) for label, *_ in FIELDS
    }
    round_side = {
        label: np.array([row[label][1] for row in rows]) for label, *_ in FIELDS
    }

    _heading(f"{'wake-on' if layout.wakes else 'wake-free'} comparison")
    print(
        f"{'quantity':<14} {'max |rel|':>12} {'median |rel|':>13} "
        f"{'worst element':>22} {'native':>14} {'round trip':>14}"
    )
    print("-" * 94)
    worst = 0.0
    for label, _, _, _, against in FIELDS:
        left, right = native_side[label], round_side[label]
        relative = _relative(left, right, native_side.get(against))
        peak = int(np.argmax(relative))
        median = float(np.median(relative))
        worst = max(worst, median)
        marker = f"  (/{against})" if against else ""
        print(
            f"{label:<14} {relative.max():>12.3e} {median:>13.3e} "
            f"{rows[peak]['name']:>22} {left[peak]:>14.6g} {right[peak]:>14.6g}"
            f"{marker}"
        )

    last = len(rows) - 1
    _heading(f"final element compared: {rows[last]['name']}")
    for label, _, _, unit, against in FIELDS:
        left, right = native_side[label], round_side[label]
        relative = _relative(left, right, native_side.get(against))[last]
        print(
            f"  {label:<14} native={left[last]:>15.8g}  round={right[last]:>15.8g}  "
            f"rel={relative:.3e}  {unit}"
        )

    layout.comparison.write_text(json.dumps(rows))
    print(f"\nwrote {layout.comparison}")
    if worst > args.tolerance:
        print(
            f"worst median {worst:.3e} exceeds --tolerance {args.tolerance:.3e}. "
            "Compare against a --no-wakes run before calling it a bug: the "
            "translation itself has a floor."
        )
    return worst <= args.tolerance


def _relative(left: np.ndarray, right: np.ndarray, against=None) -> np.ndarray:
    """Difference between the two runs, divided by something meaningful.

    Normally that is the value's own magnitude. When ``against`` is given it is
    another quantity's native value -- the beam size, for a centroid -- which is
    the only way to get a number out of a quantity that is legitimately zero.
    Elements where the denominator is itself zero contribute 0 rather than a
    NaN: there is no difference to report there.
    """
    scale = (
        np.abs(against)
        if against is not None
        else np.maximum(np.abs(left), np.abs(right))
    )
    relative = np.zeros_like(left, dtype=float)
    usable = scale > 0
    relative[usable] = np.abs(left[usable] - right[usable]) / scale[usable]
    return relative


def _section_key(layout: Layout) -> str:
    with layout.model.open("rb") as handle:
        return next(iter(pickle.load(handle).sections))


# -- driver --------------------------------------------------------------------


def run_all(args, layout: Layout) -> int:
    """Run every stage, each in its own interpreter.

    Tao holds global Fortran state, so the native and round-trip runs cannot
    share a process: the second lattice loaded into one interpreter is not the
    lattice you think it is.
    """
    for stage in STAGES:
        if stage == "beam" and not args.bmad_beam:
            print(f"skipping 'beam' (no --bmad-beam); using {layout.native_beam.name}")
            continue
        _heading(f"stage: {stage}")
        command = [sys.executable, str(Path(__file__).resolve()), stage]
        command += _forwarded(args)
        result = subprocess.run(command, check=False)
        if result.returncode != 0:
            print(f"stage '{stage}' failed with exit code {result.returncode}")
            return result.returncode
    return 0


def _forwarded(args) -> List[str]:
    """Rebuild the command line for a child stage."""
    out: List[str] = []
    for flag, value in (
        ("--tao-init", args.tao_init),
        ("--lattice", args.lattice),
        ("--libtao", args.libtao),
        ("--machine-area", args.machine_area),
        ("--position-mode", args.position_mode),
        ("--start", args.start),
        ("--end", args.end),
        ("--name", args.name),
        ("--bmad-beam", args.bmad_beam),
        ("--workdir", args.workdir),
    ):
        if value:
            out += [flag, str(value)]
    out += ["--wake-samples", str(args.wake_samples)]
    out += ["--tolerance", str(args.tolerance)]
    out += ["--seed", str(args.seed)]
    if args.particles:
        out += ["--particles", str(args.particles)]
    if args.p0c:
        out += ["--p0c", str(args.p0c)]
    if not args.wakes:
        out += ["--no-wakes"]
    return out


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__.splitlines()[0],
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("stage", choices=STAGES + ("all",), help="which stage to run")
    parser.add_argument(
        "--tao-init", required=True, help="tao.init of the native Bmad model"
    )
    parser.add_argument(
        "--lattice",
        help="native .bmad lattice (default: read design_lattice from --tao-init)",
    )
    parser.add_argument("--libtao", help="path to libtao.so")
    parser.add_argument("--machine-area", help="machine area name for the import")
    parser.add_argument(
        "--position-mode",
        default="floor",
        choices=("floor", "s"),
        help="how the importer places elements (default: floor)",
    )
    parser.add_argument(
        "--start", required=True, help="element the comparison starts from"
    )
    parser.add_argument(
        "--end",
        required=True,
        help="last element to track. Never 'END' -- see the 'round' stage",
    )
    parser.add_argument(
        "--name", help="SIMBA lattice key (default: the model's sole section)"
    )
    parser.add_argument("--bmad-beam", help="Bmad ASCII .beam0 to start from")
    parser.add_argument(
        "--particles", type=int, help="subsample the input bunch to this many"
    )
    parser.add_argument(
        "--p0c", type=float, help="reference momentum [eV/c] (default: ask Tao)"
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=20260902,
        help="subsampling seed (default: 20260902)",
    )
    parser.add_argument(
        "--wake-samples",
        type=int,
        default=0,
        help=(
            "points per sampled short-range wake (default: the importer's own). "
            "Raising it buys sigma_z and nothing else, and costs memory in the "
            "tracking process: on cu_hxr's 465 wake carriers, 8001 peaks at "
            "6.9 GB and 16001 does not fit in 14 GB"
        ),
    )
    parser.add_argument(
        "--no-wakes",
        dest="wakes",
        action="store_false",
        help=(
            "switch short-range wakes off on both sides. This is the control "
            "that separates the translation's own error floor from the wakes'"
        ),
    )
    parser.add_argument(
        "--tolerance",
        type=float,
        default=2e-2,
        help=(
            "largest median relative difference to exit 0 on (default: 2e-2). "
            "Calibrated on cu_hxr, whose worst quantity is beta_y at 1.4e-2 "
            "with wakes and 1.1e-2 without: high enough that a known-good round "
            "trip passes, low enough to catch what this script exists to find, "
            "which is order-of-magnitude breakage rather than a drift in the "
            "third digit"
        ),
    )
    parser.add_argument(
        "--workdir", default="bmad_comparison", help="directory for all outputs"
    )
    args = parser.parse_args(argv)

    if not args.wake_samples:
        from laura.translator.utils.bmad import BMAD_SR_WAKE_SAMPLES

        args.wake_samples = BMAD_SR_WAKE_SAMPLES
    args.libtao = args.libtao or os.environ.get("LAURA_LIBTAO")

    workdir = Path(args.workdir).expanduser().resolve()
    workdir.mkdir(parents=True, exist_ok=True)
    layout = Layout(workdir=workdir, wakes=args.wakes)

    if args.stage == "all":
        return run_all(args, layout)
    if args.stage == "beam":
        if not args.bmad_beam:
            raise SystemExit("--bmad-beam is required for the 'beam' stage")
        stage_beam(args, layout)
    elif args.stage == "import":
        stage_import(args, layout)
    elif args.stage == "native":
        stage_native(args, layout)
    elif args.stage == "round":
        stage_round(args, layout)
    elif args.stage == "compare":
        return 0 if stage_compare(args, layout) else 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
