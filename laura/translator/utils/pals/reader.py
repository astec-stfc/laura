"""
Read a PALS (Particle Accelerator Language Standard) document into plain Python.

This module is the *only* place in LAURA that knows ``palsparserpy`` exists.
``palsparserpy`` is a ``ctypes`` wrapper around the C library
built by PALSParserCpp. Expansion runs in a short-lived child process
that writes its result to a temporary file. The child also has
the useful side effect of swallowing the parser's own stdout, which it prints
its problem list to unconditionally.

Neither ``palsparserpy`` nor PALSParserCpp is on PyPI. Both must be cloned and
the C library cmake-built; see :data:`INSTALL_HINT`.
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import warnings
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

import yaml

try:
    _FastLoader = yaml.CSafeLoader
except AttributeError:  # pragma: no cover - PyYAML built without libyaml
    _FastLoader = yaml.SafeLoader

__all__ = [
    "INSTALL_HINT",
    "PalsBranch",
    "PalsDocument",
    "PalsElement",
    "PalsLattice",
    "PalsParserUnavailable",
    "PalsProblem",
    "parse_pals_file",
    "parser_available",
]

INSTALL_HINT = (
    "PALS import needs the `palsparserpy` package and the C library built by "
    "PALSParserCpp, neither of which is on PyPI:\n"
    "    git clone https://github.com/pals-project/PALSParserCpp.git\n"
    "    git clone https://github.com/pals-project/PALSParserPy.git\n"
    "    cd PALSParserCpp && cmake -S . -B build && cmake --build build\n"
    "    pip install -e ../PALSParserPy\n"
    "If PALSParserCpp is not beside the PALSParserPy checkout, point at it with "
    "the PALS_PARSER_CPP_DIR or PALS_PARSER_CPP_LIB environment variable."
)

_WORKER = r"""
import json
import sys

import palsparserpy as pp

source, destination, views = sys.argv[1], sys.argv[2], sys.argv[3].split(",")
lattices = pp.parse_and_expand_pals(source)
payload = {
    "views": {name: str(getattr(lattices, name)) for name in views},
    "problems": [
        {
            "message": problem.message,
            "path": problem.path,
            "severity": problem.severity.name,
            "origin": problem.origin.name,
        }
        for problem in lattices.problems
    ],
    "version": pp.__version__,
}
with open(destination, "w") as handle:
    json.dump(payload, handle)
"""


class PalsParserUnavailable(ImportError):  # noqa: N818
    """Raised when ``palsparserpy`` or its C library cannot be loaded."""


@dataclass(frozen=True)
class PalsProblem:
    """One diagnostic from lattice expansion.

    ``severity`` is ``"ERROR"`` or ``"WARNING"``; ``origin`` is ``"INPUT"``,
    ``"UNSUPPORTED"`` or ``"UNSPECIFIED"``.
    """

    message: str
    path: str = ""
    severity: str = "ERROR"
    origin: str = "INPUT"

    def __str__(self) -> str:
        where = f" at {self.path}" if self.path else ""
        return f"{self.severity}{where}: {self.message}"


@dataclass
class PalsElement:
    """One expanded lattice element."""

    name: str
    kind: str
    parameters: Dict[str, Any] = field(default_factory=dict)

    @property
    def length(self) -> float:
        return float(self.parameters.get("length", 0.0) or 0.0)

    @property
    def s_start(self) -> float:
        """Arc length at the element's *upstream* face.

        PALS ``s_position`` is the entrance, and LAURA's importers use exit for
        ``physical.s``.
        """
        return float(self.parameters.get("s_position", 0.0) or 0.0)

    @property
    def s_end(self) -> float:
        return self.s_start + self.length

    def group(self, name: str) -> Dict[str, Any]:
        """Return parameter group ``name``, or an empty dict if absent."""
        value = self.parameters.get(name)
        return value if isinstance(value, dict) else {}


@dataclass
class PalsBranch:
    """One expanded branch: an ordered element list plus the branch's own keys."""

    name: str
    elements: List[PalsElement] = field(default_factory=list)
    attributes: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PalsLattice:
    """A named PALS ``Lattice`` — one or more branches."""

    name: str
    branches: List[PalsBranch] = field(default_factory=list)


@dataclass
class PalsDocument:
    """Everything LAURA needs from one ``*.pals.yaml`` file."""

    source: Path
    lattices: List[PalsLattice] = field(default_factory=list)
    problems: List[PalsProblem] = field(default_factory=list)
    parser_version: str = ""
    views: Dict[str, Any] = field(default_factory=dict)

    @property
    def errors(self) -> List[PalsProblem]:
        return [p for p in self.problems if p.severity == "ERROR"]

    def branch(self, name: str) -> Optional[PalsBranch]:
        for lattice in self.lattices:
            for branch in lattice.branches:
                if branch.name == name:
                    return branch
        return None


def parser_available() -> bool:
    """Whether ``palsparserpy`` imports *and* finds its C library."""
    try:
        _check_parser()
    except PalsParserUnavailable:
        return False
    return True


def _check_parser() -> None:
    completed = subprocess.run(
        [sys.executable, "-c", "import palsparserpy"],
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        raise PalsParserUnavailable(
            f"{(completed.stderr or '').strip()}\n\n{INSTALL_HINT}".strip()
        )


def parse_pals_file(
    source_file: str | Path,
    views: Sequence[str] = ("full_expanded", "combined"),
) -> PalsDocument:
    """Expand ``source_file`` and return it as plain dataclasses.

    ``views`` names the trees to bring back. ``full_expanded`` is the one the
    importer reads; ``superimpose`` statements, which the parser ignores, are
    applied from ``combined`` by :func:`_superimpose`.
    """
    path = Path(source_file).expanduser().resolve()
    if not path.is_file():
        raise FileNotFoundError(f"No such PALS file: {path}")
    _check_parser()

    with tempfile.TemporaryDirectory() as workdir:
        destination = Path(workdir) / "pals.json"
        completed = subprocess.run(
            [
                sys.executable,
                "-c",
                _WORKER,
                str(path),
                str(destination),
                ",".join(views),
            ],
            capture_output=True,
            text=True,
        )
        if completed.returncode != 0 or not destination.is_file():
            detail = (completed.stderr or completed.stdout or "").strip()
            raise RuntimeError(
                f"palsparserpy failed to expand {path} "
                f"(exit code {completed.returncode}).\n{detail}"
            )
        payload = json.loads(destination.read_text())

    trees = {
        name: yaml.load(text, Loader=_FastLoader) or {}
        for name, text in payload["views"].items()
    }
    document = PalsDocument(
        source=path,
        problems=[PalsProblem(**problem) for problem in payload["problems"]],
        parser_version=payload.get("version", ""),
        views=trees,
    )
    document.lattices = _read_lattices(trees.get("full_expanded", {}))
    if "combined" in trees:
        _superimpose(document, trees["combined"])
    return document


_POINTS = {"ENTRANCE_END": 0.0, "CENTER": 0.5, "EXIT_END": 1.0}
"""Fraction of an item's length at each ``placement`` reference point."""


def _superimpose(document: PalsDocument, combined: Dict[str, Any]) -> None:
    """Insert each ``superimpose``\\ d element into the branches, at its ``s``.

    The element is kept whole and overlaps the line, rather than splitting what it
    lands on. Its body is the facility definition as written (``inherit``
    resolved), plus the ``ReferenceP`` of the line element it starts in. An
    unqualified ``base_item`` matches in every branch; ``line>>name`` only in the
    branch ``line``.
    """
    facility = (combined.get("PALS") or {}).get("facility") or []
    definitions = {
        name: body
        for item in facility
        for name, body in _pairs(item)
        if isinstance(body, dict)
    }
    statements = [
        body for item in facility for key, body in _pairs(item) if key == "superimpose"
    ]
    branches = [b for lattice in document.lattices for b in lattice.branches]
    for statement in statements:
        place = str((statement or {}).get("place", ""))
        placement = (statement or {}).get("placement") or {}
        body = _resolve_inherit(place, definitions)
        to_point = str(placement.get("to_point", "ENTRANCE_END")).upper()
        from_point = str(placement.get("from_point", "EXIT_END")).upper()
        if body is None or body.get("kind") == "BeamLine":
            warnings.warn(f"PALS superimpose of {place!r}: not an element; skipped.")
            continue
        if to_point not in _POINTS or from_point not in _POINTS:
            warnings.warn(
                f"PALS superimpose of {place!r}: placement point {to_point}/"
                f"{from_point} is not supported; skipped."
            )
            continue
        qualifier, _, base = str(placement.get("base_item", "")).rpartition(">>")
        length = float(body.get("length", 0.0) or 0.0)
        placed = 0
        for branch in branches:
            if qualifier and branch.name != qualifier:
                continue
            if base:
                anchors = [
                    e.s_start + _POINTS[from_point] * e.length
                    for e in branch.elements
                    if e.name == base
                ]
            else:  # no base: the beginning of the line
                anchors = [branch.elements[0].s_start] if branch.elements else []
            for anchor in anchors:
                s = anchor + float(placement.get("offset", 0.0) or 0.0)
                s -= _POINTS[to_point] * length
                _insert(branch, place, body, s)
                placed += 1
        if not placed:
            warnings.warn(
                f"PALS superimpose of {place!r}: base item "
                f"{placement.get('base_item')!r} is in no branch; skipped."
            )


def _resolve_inherit(
    name: str, definitions: Dict[str, Any], seen: tuple = ()
) -> Optional[Dict[str, Any]]:
    """The definition of ``name`` with its ``inherit`` chain merged in."""
    body = definitions.get(name)
    if body is None or name in seen:
        return body
    parent = body.get("inherit")
    if parent is None:
        return dict(body)
    # shallow merge, so a child's parameter group replaces the parent's whole
    merged = _resolve_inherit(str(parent), definitions, (*seen, name)) or {}
    merged.update({key: value for key, value in body.items() if key != "inherit"})
    return merged


def _insert(branch: PalsBranch, name: str, body: Dict[str, Any], s: float) -> None:
    """Put ``name`` into ``branch`` after the last element starting at or before
    ``s``, unless the parser already placed it there."""
    if any(e.name == name and abs(e.s_start - s) < 1e-9 for e in branch.elements):
        return
    index = max(
        (i for i, e in enumerate(branch.elements) if e.s_start <= s + 1e-12),
        default=-1,
    )
    parameters = {key: value for key, value in body.items() if key != "kind"}
    parameters["s_position"] = s
    if index >= 0 and branch.elements[index].group("ReferenceP"):
        parameters["ReferenceP"] = dict(branch.elements[index].group("ReferenceP"))
    branch.elements.insert(
        index + 1,
        PalsElement(name=name, kind=str(body.get("kind", "")), parameters=parameters),
    )


def _read_lattices(tree: Dict[str, Any]) -> List[PalsLattice]:
    """Walk ``{lattice: {branches: [{branch: {line: [...]}}]}}`` into dataclasses."""
    lattices: List[PalsLattice] = []
    for lattice_name, lattice_node in (tree or {}).items():
        if not isinstance(lattice_node, dict):
            continue
        lattice = PalsLattice(name=str(lattice_name))
        for branch_item in lattice_node.get("branches") or []:
            for branch_name, branch_node in _pairs(branch_item):
                if not isinstance(branch_node, dict):
                    continue
                branch = PalsBranch(
                    name=str(branch_name),
                    attributes={
                        key: value
                        for key, value in branch_node.items()
                        if key != "line"
                    },
                )
                for line_item in branch_node.get("line") or []:
                    branch.elements.extend(_read_line_item(line_item))
                lattice.branches.append(branch)
        lattices.append(lattice)
    return lattices


def _read_line_item(item: Any) -> List[PalsElement]:
    """Turn one ``line`` entry into elements.

    A fully expanded line is a list of one-key ``{name: {...}}`` maps.
    """
    elements: List[PalsElement] = []
    for name, node in _pairs(item):
        if not isinstance(node, dict):
            continue
        parameters = {key: value for key, value in node.items() if key != "kind"}
        elements.append(
            PalsElement(
                name=str(name),
                kind=str(node.get("kind", "")),
                parameters=parameters,
            )
        )
    return elements


def _pairs(item: Any) -> List[tuple]:
    """Yield ``(key, value)`` for a one-key mapping, nothing for anything else."""
    if isinstance(item, dict):
        return list(item.items())
    return []
