"""Round-trip a lattice through every code with both import and export
support, checking how much survives the trip.

LAURA can both import from and export to four of its five supported codes:
ELEGANT, Ocelot, Xsuite, and MAD-X. (Bmad is import-only for now, so excluded.)
This drives a lattice through all four, in a cycle, re-importing each
export before handing it to the next:

    MAD-X (source) -> import -> LAURA
      -> export ELEGANT -> import -> LAURA
      -> export Ocelot   -> import -> LAURA
      -> export Xsuite   -> import -> LAURA
      -> export MAD-X    -> import -> LAURA (final)

then compares the final LAURA model against the original import: element
names, order, lengths, positions, and magnet strengths. Differences are
reported per hop (as warnings raised during that hop's export/import) and
overall (the final-vs-original comparison); not every code's converter
has full element-type coverage, and this script finds the gaps.

Run from the repository root, e.g.::

    python examples/round_trip_example.py --lattice lhc.seq --sequence lhcb1
    python examples/round_trip_example.py --lattice leir.seq --sequence leir

Requires ``cpymad``, the real ``elegant`` executable, ``ocelot-desy``, and ``xtrack``.
"""

from __future__ import annotations

import argparse
import math
import sys
import tempfile
import warnings
from pathlib import Path
from typing import Dict, List, Optional, Tuple

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


class Hop:
    def __init__(self, label: str):
        self.label = label
        self.warnings: List[str] = []
        self.element_count: Optional[int] = None
        self.error: Optional[str] = None


def _run_hop(label: str, fn, *args, **kwargs):
    hop = Hop(label)
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        try:
            result = fn(*args, **kwargs)
        except Exception as exc:  # noqa: BLE001 -- report, don't crash the chain
            hop.error = f"{type(exc).__name__}: {exc}"
            hop.warnings = [str(w.message) for w in caught]
            return None, hop
    hop.warnings = [str(w.message) for w in caught]
    return result, hop


def _single_section(layout):
    """This script assumes one section per layout, matching every real
    lattice checked so far (each MAD-X sequence maps to one LAURA section)."""
    sections = list(layout.sections.values())
    if len(sections) != 1:
        raise ValueError(
            f"Expected exactly one section, found {len(sections)}: "
            f"{list(layout.sections)}. Round-trip a single section at a time."
        )
    return sections[0]


# -- import/export per code -------------------------------------------------


def import_madx(source_file: str, sequence: Optional[str], twiss_file: Optional[str] = None):
    from laura.translator.converters.codes.madx import MadxLatticeImporter

    importer = MadxLatticeImporter(
        source_file=None if twiss_file else source_file,
        twiss_file=twiss_file,
        sequence=sequence,
    )
    return importer.create_layout()


def export_madx(layout, directory: Path) -> Path:
    from laura.translator.converters.layout import MachineLayoutTranslator

    translator = MachineLayoutTranslator.from_layout(layout)
    translator.directory = str(directory)
    texts = translator.to_madx()
    text = next(iter(texts.values()))
    path = directory / "roundtrip.madx"
    path.write_text(text)
    return path


def export_elegant(layout, directory: Path) -> Path:
    from laura.translator.converters.layout import MachineLayoutTranslator

    translator = MachineLayoutTranslator.from_layout(layout)
    translator.directory = str(directory)
    text = translator.to_elegant()
    path = directory / "roundtrip.lte"
    path.write_text(text)
    return path


def import_elegant(path: Path):
    from laura.translator.converters.codes.elegant import ElegantLatticeImporter

    importer = ElegantLatticeImporter(source_file=str(path))
    return importer.create_layout()


def export_ocelot(layout, directory: Path):
    from laura.translator.converters.layout import MachineLayoutTranslator

    translator = MachineLayoutTranslator.from_layout(layout)
    translator.directory = str(directory)
    lattices = translator.to_ocelot(save=False)
    return next(iter(lattices.values()))


def import_ocelot(magnetic_lattice, name: str):
    from laura.translator.converters.codes.ocelot import OcelotLatticeImporter

    importer = OcelotLatticeImporter(magnetic_lattice=magnetic_lattice, name=name)
    return importer.create_layout()


def export_xsuite(layout, directory: Path):
    from laura.translator.converters.layout import MachineLayoutTranslator

    translator = MachineLayoutTranslator.from_layout(layout)
    translator.directory = str(directory)
    lines = translator.to_xsuite(beam_length=1, save=False)
    return next(iter(lines.values()))


def import_xsuite(line, name: str):
    from laura.translator.converters.codes.xsuite import XsuiteLatticeImporter

    importer = XsuiteLatticeImporter(line=line, name=name)
    return importer.create_layout()


# -- comparison ---------------------------------------------------------------


def _elements(layout) -> Dict[str, object]:
    section = _single_section(layout)
    return {
        name: el
        for name, el in section.elements.elements.items()
        if not el.is_subelement()
    }


def compare_layouts(original, final, tolerance: float = 1e-6) -> dict:
    orig = _elements(original)
    fin = _elements(final)

    missing = [name for name in orig if name not in fin]
    extra = [name for name in fin if name not in orig]

    def close(a: float, b: float) -> bool:
        return math.isclose(a, b, rel_tol=1e-6, abs_tol=tolerance)

    mismatches = []
    for name, orig_el in orig.items():
        fin_el = fin.get(name)
        if fin_el is None:
            continue
        if orig_el.hardware_type != fin_el.hardware_type:
            mismatches.append(
                (name, "hardware_type", orig_el.hardware_type, fin_el.hardware_type)
            )
            continue
        ol, fl = orig_el.physical.length or 0.0, fin_el.physical.length or 0.0
        if not close(ol, fl):
            mismatches.append((name, "length", ol, fl))
        os_, fs = orig_el.physical.s or 0.0, fin_el.physical.s or 0.0
        if not close(os_, fs):
            mismatches.append((name, "s", os_, fs))
        orig_mag = getattr(orig_el, "magnetic", None)
        fin_mag = getattr(fin_el, "magnetic", None)
        if orig_mag is not None and fin_mag is not None:
            orders = getattr(getattr(orig_mag, "multipoles", None), "model_fields", {})
            for order_name in orders:
                if not order_name.startswith("K") or not order_name.endswith("L"):
                    continue
                n = int(order_name[1:-1])
                try:
                    ok = orig_mag.KnL(n)
                    fk = fin_mag.KnL(n)
                except Exception:
                    continue
                if isinstance(ok, str) or isinstance(fk, str):
                    continue
                if not close(float(ok or 0.0), float(fk or 0.0)):
                    mismatches.append((name, order_name, ok, fk))
            for field in ("horizontal_kick", "vertical_kick"):
                ov = getattr(orig_mag, field, None)
                fv = getattr(fin_mag, field, None)
                if ov is None and fv is None:
                    continue
                if isinstance(ov, str) or isinstance(fv, str):
                    continue
                if not close(float(ov or 0.0), float(fv or 0.0)):
                    mismatches.append((name, field, ov, fv))
            # Solenoid field.
            of, ff = getattr(orig_mag, "fields", None), getattr(fin_mag, "fields", None)
            if of is not None and ff is not None:
                os0, fs0 = getattr(of, "S0L", None), getattr(ff, "S0L", None)
                if os0 is not None and fs0 is not None and not (
                    isinstance(os0, str) or isinstance(fs0, str)
                ):
                    if not close(float(os0 or 0.0), float(fs0 or 0.0)):
                        mismatches.append((name, "S0L", os0, fs0))

        orig_cav, fin_cav = getattr(orig_el, "cavity", None), getattr(fin_el, "cavity", None)
        if orig_cav is not None and fin_cav is not None:
            for field in ("frequency", "phase"):
                ov, fv = getattr(orig_cav, field, None), getattr(fin_cav, field, None)
                if ov is None and fv is None:
                    continue
                if isinstance(ov, str) or isinstance(fv, str):
                    continue
                if not close(float(ov or 0.0), float(fv or 0.0)):
                    mismatches.append((name, f"cavity.{field}", ov, fv))
        orig_sim, fin_sim = getattr(orig_el, "simulation", None), getattr(fin_el, "simulation", None)
        if orig_sim is not None and fin_sim is not None:
            ov = getattr(orig_sim, "field_amplitude", None)
            fv = getattr(fin_sim, "field_amplitude", None)
            if ov is not None and fv is not None and not (
                isinstance(ov, str) or isinstance(fv, str)
            ):
                if not close(float(ov or 0.0), float(fv or 0.0)):
                    mismatches.append((name, "field_amplitude", ov, fv))

        orig_ap, fin_ap = getattr(orig_el, "aperture", None), getattr(fin_el, "aperture", None)
        if orig_ap is not None and fin_ap is not None:
            for field in ("horizontal_size", "vertical_size"):
                ov, fv = getattr(orig_ap, field, None), getattr(fin_ap, field, None)
                if ov is None and fv is None:
                    continue
                if isinstance(ov, str) or isinstance(fv, str):
                    continue
                if not close(float(ov or 0.0), float(fv or 0.0)):
                    mismatches.append((name, f"aperture.{field}", ov, fv))

    order_orig = [n for n in orig if n in fin]
    order_fin = [n for n in fin if n in orig]

    orig_length = max((e.physical.s or 0.0) for e in orig.values()) if orig else 0.0
    fin_length = max((e.physical.s or 0.0) for e in fin.values()) if fin else 0.0

    return {
        "orig_count": len(orig),
        "fin_count": len(fin),
        "missing": missing,
        "extra": extra,
        "mismatches": mismatches,
        "order_preserved": order_orig == order_fin,
        "orig_length": orig_length,
        "fin_length": fin_length,
        "length_matches": close(orig_length, fin_length),
    }


# -- reporting -----------------------------------------------------------------


def _report_hop(hop: Hop, before: Optional[int], after: Optional[int]) -> bool:
    ok = hop.error is None
    status = "OK" if ok else "FAIL"
    print(f"\n[{status}] {hop.label}")
    if before is not None:
        print(f"    elements before: {before}" + (f"  after: {after}" if after is not None else ""))
    if hop.error:
        print(f"    ERROR: {hop.error}")
    if hop.warnings:
        from collections import Counter

        counted = Counter(hop.warnings)
        print(f"    {len(hop.warnings)} warning(s):")
        for msg, count in counted.most_common(10):
            prefix = f"  ({count}x)" if count > 1 else ""
            print(f"      {msg[:160]}{prefix}")
        if len(counted) > 10:
            print(f"      ... and {len(counted) - 10} more distinct warnings")
    return ok


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--lattice", required=True, help="MAD-X source file to start from")
    parser.add_argument("--sequence", help="MAD-X sequence to import")
    parser.add_argument("--twiss", help="Use a MAD-X TWISS TFS file instead of source")
    parser.add_argument("--keep", action="store_true", help="Keep the temp directory")
    args = parser.parse_args(argv)

    tmpdir = Path(tempfile.mkdtemp(prefix="laura-roundtrip-"))
    print(f"Working directory: {tmpdir}")

    layout, hop = _run_hop(
        "import MAD-X (original)",
        import_madx,
        args.lattice,
        args.sequence,
        args.twiss,
    )
    n0 = len(_elements(layout)) if layout else None
    if not _report_hop(hop, None, n0) or layout is None:
        return 1
    original = layout
    section_name = _single_section(original).name
    n_before = n0
    # ELEGANT
    path, hop = _run_hop("export ELEGANT", export_elegant, layout, tmpdir)
    if not _report_hop(hop, n_before, None) or path is None:
        return 1
    layout, hop = _run_hop("import ELEGANT", import_elegant, path)
    n_after = len(_elements(layout)) if layout else None
    if not _report_hop(hop, n_before, n_after) or layout is None:
        return 1
    n_before = n_after

    # Ocelot
    maglat, hop = _run_hop("export Ocelot", export_ocelot, layout, tmpdir)
    if not _report_hop(hop, n_before, None) or maglat is None:
        return 1
    layout, hop = _run_hop("import Ocelot", import_ocelot, maglat, section_name)
    n_after = len(_elements(layout)) if layout else None
    if not _report_hop(hop, n_before, n_after) or layout is None:
        return 1
    n_before = n_after

    # Xsuite
    line, hop = _run_hop("export Xsuite", export_xsuite, layout, tmpdir)
    if not _report_hop(hop, n_before, None) or line is None:
        return 1
    layout, hop = _run_hop("import Xsuite", import_xsuite, line, section_name)
    n_after = len(_elements(layout)) if layout else None
    if not _report_hop(hop, n_before, n_after) or layout is None:
        return 1
    n_before = n_after

    # MAD-X
    path, hop = _run_hop("export MAD-X", export_madx, layout, tmpdir)
    if not _report_hop(hop, n_before, None) or path is None:
        return 1
    layout, hop = _run_hop(
        "import MAD-X (final)", import_madx, str(path), None, None
    )
    n_after = len(_elements(layout)) if layout else None
    if not _report_hop(hop, n_before, n_after) or layout is None:
        return 1

    final = layout

    print("\n" + "=" * 74)
    print("  FINAL COMPARISON: original MAD-X import vs. after full round trip")
    print("=" * 74)
    result = compare_layouts(original, final)
    print(f"  original elements: {result['orig_count']}")
    print(f"  final elements   : {result['fin_count']}")
    print(f"  order preserved  : {result['order_preserved']}")
    length_status = "MATCH" if result["length_matches"] else "MISMATCH"
    print(
        f"  section length   : orig={result['orig_length']:.6f} m  "
        f"final={result['fin_length']:.6f} m  [{length_status}]"
    )
    print(f"  missing (dropped somewhere in the chain): {len(result['missing'])}")
    if result["missing"]:
        print(f"    {result['missing'][:15]}")
    print(f"  extra (appeared from nowhere): {len(result['extra'])}")
    if result["extra"]:
        print(f"    {result['extra'][:15]}")
    print(f"  field mismatches: {len(result['mismatches'])}")
    for name, field, o, f in result["mismatches"][:30]:
        print(f"    {name:<28}{field:<12}orig={o!r:<20}final={f!r}")
    if len(result["mismatches"]) > 30:
        print(f"    ... and {len(result['mismatches']) - 30} more")

    if not args.keep:
        import shutil

        shutil.rmtree(tmpdir, ignore_errors=True)

    return 0


if __name__ == "__main__":
    sys.exit(main())
