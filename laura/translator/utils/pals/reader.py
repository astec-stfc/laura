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


class PalsParserUnavailable(ImportError):
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
    views: Sequence[str] = ("full_expanded",),
) -> PalsDocument:
    """Expand ``source_file`` and return it as plain dataclasses.

    ``views`` names the trees to bring back. ``full_expanded`` is the one the
    importer reads.
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
    return document


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
