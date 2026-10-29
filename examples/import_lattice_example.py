"""Import a native lattice into LAURA and check it against the original.

LAURA can read native lattices from five simulation codes. Each importer
follows the same lifecycle::

    create_element_dictionary()        # native lattice -> raw per-element data
    create_laura_element_dictionary()  # raw data -> LAURA Element models
    create_section()                   # -> SectionLattice
    create_layout()                    # -> MachineLayout  (resolves positions)
    export_yaml()                      # -> LAURA YAML

This example drives that lifecycle for a lattice you supply, then compares the
resulting LAURA model back against the native one, element by element:

  * every LAURA element exists in the native lattice, in the same order;
  * lengths agree;
  * arc-length positions agree -- importers record ``s`` at each element's
    *exit* (``s_point="end"``), and ``create_layout()`` normalises that to the
    element *centre* (``s_point="middle"``), so the check is
    ``laura.physical.s + length / 2 == native_s_exit``. This catches elements
    that were reordered, left unresolved, or re-referenced inconsistently;
  * elements imported as a generic ``Magnet`` are counted and the full multipole
    content is carried over. The importer warns for each one;
  * magnet strengths survive the unit conversion. LAURA stores *integrated*
    strengths (``K1L``), where the codes mostly quote strength per metre
    (``K1``), so this recomputes ``K1L = K1 * L`` from the raw native values
    and compares.

Elements the importer deliberately drops (drifts, and MAD-X/Xsuite ``dipedge``
elements folded into their neighbouring bend) are reported separately as
dropped rather than counted as failures.

Run from the repository root::

    python examples/import_lattice_example.py --code madx    --lattice ring.madx
    python examples/import_lattice_example.py --code madx    --lattice twiss.tfs
    python examples/import_lattice_example.py --code elegant --lattice line.lte
    python examples/import_lattice_example.py --code bmad    --lattice lat.bmad
    python examples/import_lattice_example.py --code bmad    --lattice tao.init
    python examples/import_lattice_example.py --code xsuite  --lattice line.json
    python examples/import_lattice_example.py --code ocelot  --lattice lattice.py

Add ``--export <directory>`` to also write the LAURA model out (as
``<directory>/summary.yaml``), and ``--verbose`` to list every element rather
than just the mismatches. The exit status is 0 when everything matches and 1
when it does not.

Each code needs its own optional dependency (``cpymad``, ``pytao``, ``xtrack``,
``ocelot``); install with e.g. ``pip install "laura-accelerator[madx]"``.
"""

from __future__ import annotations

import argparse
import importlib.util
import math
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from laura.translator.utils.functions import number_repeated_names  # noqa: E402

CODES = ("elegant", "bmad", "madx", "ocelot", "xsuite")

EXPECTED_DROPS = {"drift", "dipedge", "marker_end", "_end_point"}


@dataclass
class NativeElement:
    """One element as the *originating code* describes it."""

    name: str
    native_type: str
    length: float
    s_exit: float


@dataclass
class Mismatch:
    name: str
    field: str
    native: object
    laura: object


def _numeric(value) -> Optional[float]:
    """
    Float value, or ``None`` for a deferred symbol/expression.
    """
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


# -- loading -------------------------------------------------------------------


def _resolve_kind(code: str, lattice: Path, kind: str) -> str:
    """Decide which of a code's two input forms ``lattice`` is."""
    if kind != "auto":
        return kind
    suffix = lattice.suffix.lower()
    if code == "elegant":
        return "source" if suffix in {".lte", ".ele"} else "params"
    if code == "madx":
        return "twiss" if suffix in {".tfs", ".twiss"} else "source"
    if code == "bmad":
        return "init" if suffix == ".init" else "source"
    return "source"


def _load_ocelot_lattice(path: Path, variable: Optional[str]):
    """Load a ``MagneticLattice`` and any initial ``Twiss`` from an Ocelot
    lattice *module*.

    Pass ``--variable`` to name the lattice (or the cell sequence) explicitly;
    otherwise the first ``MagneticLattice`` in the module wins.
    """
    from ocelot import Twiss
    from ocelot.cpbd.magnetic_lattice import MagneticLattice

    spec = importlib.util.spec_from_file_location("laura_ocelot_lattice", path)
    if spec is None or spec.loader is None:
        raise ValueError(f"{path} is not an importable Python module.")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    if variable:
        candidate = getattr(module, variable)
    else:
        candidate = next(
            (
                value
                for value in vars(module).values()
                if isinstance(value, MagneticLattice)
            ),
            None,
        )
        if candidate is None:
            for name in ("cell", "sequence", "lattice"):
                if isinstance(getattr(module, name, None), (list, tuple)):
                    candidate = getattr(module, name)
                    break
        if candidate is None:
            raise ValueError(
                f"No MagneticLattice or cell sequence found in {path}; "
                "name one with --variable."
            )

    twiss = next(
        (value for value in vars(module).values() if isinstance(value, Twiss)), None
    )

    if isinstance(candidate, MagneticLattice):
        return candidate, twiss
    return MagneticLattice(candidate), twiss


def _madx_strengths(data: dict, length: float) -> Dict[str, float]:
    """Integrated strengths MAD-X's raw per-metre values imply."""
    expected = {}
    angle = _numeric(data.get("angle"))
    if angle is not None:
        expected["K0L"] = angle
    for order in (1, 2, 3):
        k = _numeric(data.get(f"k{order}"))
        if k is not None:
            expected[f"K{order}L"] = k * length
    ks = _numeric(data.get("ks"))
    if ks is not None:
        expected["S0L"] = ks * length

    hardware_type = data.get("hardware_type", "")
    if hardware_type == "Combined_Corrector":
        for key, raw in (("hkick", "hkick"), ("vkick", "vkick")):
            value = _numeric(data.get(raw))
            if value is not None:
                expected[key] = value
    elif hardware_type == "Horizontal_Corrector":
        value = _numeric(data.get("kick"))
        if value is not None:
            expected["hkick"] = value
    elif hardware_type == "Vertical_Corrector":
        value = _numeric(data.get("kick"))
        if value is not None:
            expected["vkick"] = value
    return expected


def _elegant_strengths(data: dict, length: float) -> Dict[str, float]:
    """Integrated strengths ELEGANT's raw values imply."""
    expected = {}
    angle = _numeric(data.get("angle"))
    if angle is not None:
        expected["K0L"] = angle
    for order in (1, 2, 3):
        k = _numeric(data.get(f"k{order}"))
        if k is not None:
            expected[f"K{order}L"] = k * length
    return expected


def _bmad_strengths(native_type: str, params: dict, length: float) -> Dict[str, float]:
    """Integrated strengths Tao's raw element parameters imply."""
    from laura.translator.converters.codes import magnetic_orders

    expected = {}
    order = magnetic_orders.get(native_type)
    if order is not None:
        k = _numeric(params.get(f"K{order}"))
        angle = _numeric(params.get("ANGLE"))
        if k is not None:
            expected[f"K{order}L"] = k * length
        elif angle is not None:
            expected["K0L"] = angle
    if native_type == "Solenoid":
        field = _numeric(params.get("BS_FIELD"))
        if field is not None:
            expected["S0L"] = field * length
    return expected


def _xsuite_strengths(native, native_type: str, length: float) -> Dict[str, float]:
    """Integrated strengths an Xtrack element's own attributes imply.

    Xtrack has no single convention, so this follows one rule per family:

    * a thin ``Multipole`` already stores *integrated* ``knl``, so it is used
      as-is with no ``* L``;
    * a thick typed magnet stores strength per metre in ``k1``/``k2``/``k3``,
      on top of any ``knl`` it also carries;
    * a ``Bend`` bends by ``k0`` (or, when that just tracks the reference
      curvature, by ``h``), and LAURA stores the dipole term with the opposite
      sign;
    * a ``Solenoid`` stores ``ks`` per metre.

    Only the normal components are returned, since that is what ``KnL`` reads.
    """
    knl = [float(value) for value in getattr(native, "knl", [])]

    def integrated(order: int) -> float:
        base = knl[order] if order < len(knl) else 0.0
        return base + float(getattr(native, f"k{order}", 0.0) or 0.0) * length

    if native_type == "Multipole":
        return {f"K{order}L": value for order, value in enumerate(knl)}

    if native_type in {"Bend", "RBend"}:
        k0 = getattr(native, "k0", None)
        strength = float(getattr(native, "h", 0.0)) if (
            k0 is None or isinstance(k0, str)
        ) else float(k0)
        return {
            "K0L": -strength * length,
            "K1L": integrated(1),
            "K2L": integrated(2),
        }

    orders = {"Quadrupole": 1, "Sextupole": 2, "Octupole": 3}
    if native_type in orders:
        order = orders[native_type]
        return {f"K{order}L": integrated(order)}

    if native_type in {"Solenoid", "UniformSolenoid"}:
        return {"S0L": float(getattr(native, "ks", 0.0)) * length}

    return {}


def _ocelot_strengths(element, native_type: str, length: float) -> Dict[str, float]:
    """Integrated strengths an Ocelot element's own attributes imply."""
    expected = {}
    if native_type in {"SBend", "RBend", "Bend"}:
        expected["K0L"] = float(getattr(element, "angle", 0.0) or 0.0)
    for order in (1, 2, 3):
        if native_type in {"SBend", "RBend", "Bend", "Quadrupole", "Sextupole", "Octupole"}:
            k = getattr(element, f"k{order}", None)
            if k:
                expected[f"K{order}L"] = float(k) * length
    if native_type == "Hcor":
        expected["hkick"] = float(getattr(element, "angle", 0.0) or 0.0)
    if native_type == "Vcor":
        expected["vkick"] = float(getattr(element, "angle", 0.0) or 0.0)
    return expected


def load(args) -> Tuple[object, List[NativeElement], object, Optional[Dict[str, dict]]]:
    """Build the importer, read the native lattice, and resolve a layout.

    Returns ``(importer, native_elements, layout, expected_strengths)``, where
    ``expected_strengths`` is ``None`` for codes this example does not check.
    Both the native elements and the raw strengths are captured *before*
    ``create_layout()`` runs: the importers convert their raw data in place, so
    a later snapshot would just hand back LAURA's own converted values.
    """
    lattice = Path(args.lattice).expanduser().resolve()
    if not lattice.exists():
        raise FileNotFoundError(lattice)
    kind = _resolve_kind(args.code, lattice, args.kind)

    if args.code == "elegant":
        from laura.translator.converters.codes.elegant import ElegantLatticeImporter

        importer = ElegantLatticeImporter(
            **{f"{'source' if kind == 'source' else 'params'}_file": str(lattice)},
            beamline=args.beamline,
        )
        importer.create_element_dictionary()

        beamlines = list(importer._source_sections) if importer.source_file else [None]

        native, strengths = [], {}
        for beamline in beamlines:
            if beamline is not None:
                importer._select_source_output(beamline)
                importer.create_element_dictionary()
            cumulative = 0.0
            for name, data in importer.elegant_data.items():
                if not data.get("hardware_type"):
                    continue
                length = float(data.get("l", 0.0) or 0.0)
                cumulative += length
                if name in strengths:
                    continue
                native.append(
                    NativeElement(name, str(data["hardware_type"]), length, cumulative)
                )
                strengths[name] = _elegant_strengths(data, length)
        return importer, native, importer.create_layout(), strengths

    if args.code == "madx":
        from laura.translator.converters.codes.madx import MadxLatticeImporter

        importer = MadxLatticeImporter(
            **{f"{'twiss' if kind == 'twiss' else 'source'}_file": str(lattice)},
            sequence=args.sequence,
        )
        madx = None
        if kind == "twiss":
            from laura.translator.utils.madx.TFSFile import TFSFile

            tfs = TFSFile()
            tfs.read_file(str(lattice))
            raw_rows = tfs.rows()
        else:
            madx = importer._load_madx()
            raw_rows = importer._source_rows(madx)
        native = [
            NativeElement(
                str(row["name"]),
                str(row["keyword"]),
                float(row.get("l", 0.0) or 0.0),
                float(row.get("s", 0.0) or 0.0),
            )
            for row in raw_rows
        ]

        importer.create_element_dictionary(madx)
        strengths = {
            name: _madx_strengths(data, float(data.get("l", 0.0) or 0.0))
            for name, data in importer.madx_data.items()
        }
        return importer, native, importer.create_layout(), strengths

    if args.code == "bmad":
        from laura.translator.converters.codes.bmad import BmadLatticeImporter

        importer = BmadLatticeImporter(
            **{"tao_init" if kind == "init" else "lattice_file": str(lattice)},
            libtao=args.libtao,
        )
        universe = args.universe
        if universe not in importer.names_numbered:
            raise KeyError(
                f"Universe {universe} not found; this lattice has "
                f"{sorted(importer.names_numbered)}."
            )
        native, strengths = [], {}
        for branch, names in importer.names_numbered[universe].items():
            for name, native_type, length, s_exit, params in zip(
                names,
                importer.types[universe][branch],
                importer.lengths[universe][branch],
                importer.spos[universe][branch],
                importer.params[universe][branch],
            ):
                native.append(
                    NativeElement(name, native_type, float(length), float(s_exit))
                )
                strengths[name] = _bmad_strengths(native_type, params, float(length))
        return importer, native, importer.create_layout(universe), strengths

    if args.code == "ocelot":
        from laura.translator.converters.codes.ocelot import OcelotLatticeImporter

        magnetic_lattice, twiss = _load_ocelot_lattice(lattice, args.variable)
        importer = OcelotLatticeImporter(
            magnetic_lattice=magnetic_lattice, initial_twiss=twiss, name=lattice.stem
        )
        sequence = list(magnetic_lattice.sequence)
        native, strengths, cumulative = [], {}, 0.0
        if twiss is not None:
            native.append(
                NativeElement(getattr(twiss, "id", "") or "initial_twiss", "Twiss", 0.0, 0.0)
            )
        for element, name in zip(
            sequence, number_repeated_names([element.id for element in sequence])
        ):
            length = float(getattr(element, "l", 0.0) or 0.0)
            cumulative += length
            native_type = type(element).__name__
            native.append(NativeElement(name, native_type, length, cumulative))
            strengths[name] = _ocelot_strengths(element.element, native_type, length)
        return importer, native, importer.create_layout(), strengths

    if args.code == "xsuite":
        from laura.translator.converters.codes.xsuite import XsuiteLatticeImporter

        importer = XsuiteLatticeImporter(
            source_file=str(lattice), name=lattice.stem, line_name=args.line_name
        )
        lines = list(importer._source_lines.values()) or [importer.line]
        native, strengths = [], {}
        for line in lines:
            table = line.get_table()
            for index, name in enumerate(line.element_names):
                element = line.element_dict[name]
                native_type = type(element).__name__
                length = float(getattr(element, "length", 0.0) or 0.0)
                physical_length = length if getattr(element, "isthick", True) else 0.0
                if name in strengths:
                    continue
                native.append(
                    NativeElement(
                        name, native_type, physical_length, float(table.s_end[index])
                    )
                )
                strengths[name] = _xsuite_strengths(element, native_type, length)
        return importer, native, importer.create_layout(), strengths

    raise ValueError(f"Unsupported code {args.code!r}.")


def resolved_elements(layout) -> Dict[str, object]:
    """Every non-subelement in the layout, keyed by name.

    Subelements (a BPM embedded in a magnet, the H/V halves of a kicker) are
    created *by* the importer and have no native counterpart, so they are
    excluded from the comparison.
    """
    elements: Dict[str, object] = {}
    for section in layout.sections.values():
        for name, element in section.elements.elements.items():
            if element.is_subelement():
                continue
            elements.setdefault(name, element)
    return elements


# -- comparison ----------------------------------------------------------------


def _laura_strength(element, key: str) -> Optional[float]:
    """Read back the LAURA value a native strength should have become."""
    magnetic = getattr(element, "magnetic", None)
    if magnetic is None:
        return None
    try:
        if key.startswith("K") and key.endswith("L"):
            return _numeric(magnetic.KnL(int(key[1:-1])))
        if key == "S0L":
            return _numeric(magnetic.ks)
        if key == "hkick":
            return _numeric(getattr(magnetic, "horizontal_kick", None))
        if key == "vkick":
            return _numeric(getattr(magnetic, "vertical_kick", None))
    except (AttributeError, KeyError, IndexError, TypeError, ValueError):
        return None
    return None


def compare(
    native: List[NativeElement],
    elements: Dict[str, object],
    tolerance: float,
    strengths: Optional[Dict[str, dict]] = None,
):
    """Check the LAURA elements against their native originals."""
    native_by_name = {row.name: row for row in native}

    mismatches: List[Mismatch] = []
    strength_mismatches: List[Mismatch] = []
    strength_checks = 0
    generic: List[str] = []
    unexpected: List[str] = []
    matched: List[str] = []

    def close(left: float, right: float) -> bool:
        return math.isclose(left, right, rel_tol=1e-9, abs_tol=tolerance)

    for name, element in elements.items():
        row = native_by_name.get(name)
        if row is None:
            unexpected.append(name)
            continue
        if element.hardware_type == "Generic":
            generic.append(name)

        length = float(element.physical.length or 0.0)
        if not close(length, row.length):
            mismatches.append(Mismatch(name, "length", row.length, length))

        s_exit = float(element.physical.s or 0.0) + length / 2.0
        if not close(s_exit, row.s_exit):
            mismatches.append(Mismatch(name, "s (exit)", row.s_exit, s_exit))

        for key, expected in (strengths or {}).get(name, {}).items():
            actual = _laura_strength(element, key)
            if actual is None:
                continue
            strength_checks += 1
            if not close(actual, expected):
                strength_mismatches.append(Mismatch(name, key, expected, actual))

        matched.append(name)

    dropped = [row for row in native if row.name not in elements]
    expected_drops = [
        row for row in dropped if row.native_type.lower() in EXPECTED_DROPS
    ]
    unexpected_drops = [row for row in dropped if row not in expected_drops]

    native_order = [row.name for row in native if row.name in elements]
    laura_order = [name for name in elements if name in native_by_name]
    order_ok = native_order == laura_order

    return {
        "matched": matched,
        "mismatches": mismatches,
        "strength_mismatches": strength_mismatches,
        "strength_checks": strength_checks,
        "strengths_supported": strengths is not None,
        "generic": generic,
        "unexpected": unexpected,
        "expected_drops": expected_drops,
        "unexpected_drops": unexpected_drops,
        "order_ok": order_ok,
    }


# -- reporting -----------------------------------------------------------------


def _heading(title: str) -> None:
    print()
    print("=" * 74)
    print(f"  {title}")
    print("=" * 74)


def report(
    code: str,
    lattice: Path,
    native: List[NativeElement],
    elements: Dict[str, object],
    result: dict,
    verbose: bool,
    sections: int = 1,
) -> bool:
    _heading(f"{code} lattice: {lattice.name}")

    longest = max((row.s_exit for row in native), default=0.0)
    label = "longest section" if sections > 1 else "lattice length"
    print(f"  native elements      : {len(native)}")
    print(f"  LAURA elements       : {len(elements)}")
    print(f"  sections             : {sections}")
    print(f"  native {label:<14}: {longest:.6f} m")

    if verbose:
        print()
        print(f"  {'element':<28}{'type':<22}{'length [m]':>12}{'s exit [m]':>14}")
        print(f"  {'-' * 74}")
        for row in native:
            element = elements.get(row.name)
            laura_type = element.hardware_type if element else "(dropped)"
            print(
                f"  {row.name:<28}{laura_type:<22}"
                f"{row.length:>12.6f}{row.s_exit:>14.6f}"
            )

    print()
    checks = [
        ("element order preserved", result["order_ok"], ""),
        (
            "lengths and s-positions match",
            not result["mismatches"],
            f"{len(result['mismatches'])} mismatch(es)",
        ),
        (
            "no unexpected LAURA elements",
            not result["unexpected"],
            f"{len(result['unexpected'])} extra",
        ),
        (
            "no unexplained dropped elements",
            not result["unexpected_drops"],
            f"{len(result['unexpected_drops'])} dropped",
        ),
    ]
    if result["strengths_supported"]:
        checks.append(
            (
                f"magnet strengths converted ({result['strength_checks']} checked)",
                not result["strength_mismatches"],
                f"{len(result['strength_mismatches'])} mismatch(es)",
            )
        )
    for label, passed, detail in checks:
        status = "PASS" if passed else "FAIL"
        suffix = f"  ({detail})" if detail and not passed else ""
        print(f"  [{status}] {label}{suffix}")
    if not result["strengths_supported"]:
        print(f"  [SKIP] magnet strengths not checked for {code}")
    if result["generic"]:
        print(f"  [NOTE] {len(result['generic'])} element(s) imported as generic Magnet")

    if result["strength_mismatches"]:
        print()
        print("  strength mismatches (LAURA stores integrated strengths, Kn * L):")
        for item in result["strength_mismatches"][:20]:
            print(
                f"    {item.name:<28}{item.field:<12}"
                f"expected={item.native!r:<20}laura={item.laura!r}"
            )
        if len(result["strength_mismatches"]) > 20:
            print(f"    ... and {len(result['strength_mismatches']) - 20} more")

    if result["mismatches"]:
        print()
        print("  mismatches:")
        for item in result["mismatches"][:20]:
            print(
                f"    {item.name:<28}{item.field:<12}"
                f"native={item.native!r:<20}laura={item.laura!r}"
            )
        if len(result["mismatches"]) > 20:
            print(f"    ... and {len(result['mismatches']) - 20} more")

    if result["generic"]:
        print()
        print("  imported as generic Magnet (order undetermined or above K3L):")
        print(f"    {', '.join(result['generic'][:15])}")

    if result["unexpected"]:
        print()
        print("  in LAURA but not in the native lattice:")
        print(f"    {', '.join(result['unexpected'][:15])}")

    if result["unexpected_drops"]:
        print()
        print("  dropped by the importer (not a drift or folded edge):")
        for row in result["unexpected_drops"][:15]:
            print(f"    {row.name:<28}{row.native_type}")
        if len(result["unexpected_drops"]) > 15:
            print(f"    ... and {len(result['unexpected_drops']) - 15} more")

    if result["expected_drops"]:
        print()
        print(
            f"  {len(result['expected_drops'])} drift/edge element(s) dropped "
            "as expected"
        )

    passed = all(check[1] for check in checks)
    print()
    print(f"  RESULT: {'lattice matches the original' if passed else 'differences found'}")
    return passed


# -- entry point ---------------------------------------------------------------


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__.splitlines()[0],
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--code", required=True, choices=CODES, help="source code")
    parser.add_argument("--lattice", required=True, help="native lattice file")
    parser.add_argument(
        "--kind",
        default="auto",
        choices=("auto", "source", "params", "twiss", "init"),
        help=(
            "which input form the file is: a native source lattice, an ELEGANT "
            "SDDS parameters file, a MAD-X TFS twiss table, or a Bmad tao.init "
            "(default: infer from the file extension)"
        ),
    )
    parser.add_argument("--sequence", help="MAD-X sequence to import")
    parser.add_argument("--beamline", help="ELEGANT beamline to import")
    parser.add_argument("--line-name", help="Xsuite line to import")
    parser.add_argument("--variable", help="Ocelot lattice/cell variable name")
    parser.add_argument("--libtao", help="path to libtao.so (Bmad)")
    parser.add_argument(
        "--universe", type=int, default=1, help="Tao universe to import (Bmad)"
    )
    parser.add_argument(
        "--tolerance",
        type=float,
        default=1e-6,
        help="absolute tolerance on lengths and positions [m] (default: 1e-6)",
    )
    parser.add_argument(
        "--export",
        metavar="DIRECTORY",
        help="also export the LAURA model as <DIRECTORY>/summary.yaml",
    )
    parser.add_argument(
        "--verbose", action="store_true", help="list every element, not just problems"
    )
    args = parser.parse_args(argv)

    importer, native, layout, strengths = load(args)
    elements = resolved_elements(layout)
    result = compare(native, elements, args.tolerance, strengths)
    passed = report(
        args.code,
        Path(args.lattice),
        native,
        elements,
        result,
        args.verbose,
        sections=len(layout.sections),
    )

    if args.export:
        importer.export_yaml(args.export, layout, position_mode="s")
        print(f"  exported to {Path(args.export) / 'summary.yaml'}")

    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
