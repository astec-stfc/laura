"""
laura/Exporters/SQL.py — SQLAlchemy-based persistence for a LAURA MachineModel.

Uses the generated ORM from ``laura/schema/generated/laura_orm.py`` which is produced by
``gen-sqla`` from the LinkML schema.  Any SQLAlchemy-supported database is accepted via a
standard database URL.

Requires the ``sql`` optional dependency group::

    pip install "laura-accelerator[sql]"

Public API::

    from laura.Exporters.SQL import export_machine, load_machine_elements

    # Persist to SQLite file
    machine_id = export_machine(machine, db_url="sqlite:///machine.db")

    # Query elements back
    rows = load_machine_elements(db_url="sqlite:///machine.db", machine_id=machine_id)
    # [{'name': 'Q1', 'hardware_type': 'Quadrupole', 'hardware_class': 'Magnet',
    #   'machine_area': 'S01'}, ...]

    # Query sections back
    sections = load_machine_sections(db_url="sqlite:///machine.db", machine_id=machine_id)
    # {'SEC1': ['M1', 'Q1', ...], ...}
"""
from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Optional

if TYPE_CHECKING:
    from laura.models.elementList import MachineModel

# Path to the generated SQLAlchemy ORM module (never imported at package level so
# sqlalchemy remains an optional dependency).
_ORM_PATH = Path(__file__).parent.parent / "schema" / "generated" / "laura_orm.py"

# Valid hardware_class values from the schema enum.
_VALID_HARDWARE_CLASSES = {
    "Magnet", "Diagnostic", "RF", "Vacuum", "Laser", "Plasma",
    "Feedback", "Marker", "Aperture", "Stage", "Lighting", "Shutter",
    "Wakefield", "TwissMatch", "Drift", "Generic", "Monitor",
}


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _load_orm() -> Any:
    """Load the generated ORM module from its file path.

    The ORM lives in the ``generated/`` directory and is not a proper package
    module, so we load it via ``importlib.util`` to avoid adding it to
    ``sys.modules`` under a misleading name.
    """
    if not _ORM_PATH.exists():
        raise FileNotFoundError(
            f"Generated ORM not found at {_ORM_PATH}. "
            "Run laura/schema/generate.ps1 (or generate.sh) to regenerate it."
        )
    spec = importlib.util.spec_from_file_location("_laura_orm_module", _ORM_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _make_session_factory(db_url: str, orm: Any):
    """Create all tables and return a ``(engine, Session)`` pair.

    Pool strategy:

    * **In-memory SQLite** (``sqlite:///:memory:``) — ``StaticPool`` shares a
      single connection so ``create_all`` and every subsequent session see the
      same in-memory database.
    * **File-based SQLite** — ``NullPool`` closes file handles immediately after
      each session exits, allowing temporary directories to be cleaned up on
      Windows without a ``PermissionError``.
    * **All other databases** — default SQLAlchemy pool.
    """
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    kwargs: Dict[str, Any] = {}
    if "/:memory:" in db_url:
        from sqlalchemy.pool import StaticPool
        kwargs["poolclass"] = StaticPool
        kwargs["connect_args"] = {"check_same_thread": False}
    elif db_url.startswith("sqlite"):
        from sqlalchemy.pool import NullPool
        kwargs["poolclass"] = NullPool

    engine = create_engine(db_url, **kwargs)
    orm.Base.metadata.create_all(engine)
    return engine, sessionmaker(bind=engine)


def _coerce_hardware_class(value: Optional[str]) -> str:
    """Return *value* if it is a valid schema enum member, otherwise ``'Generic'``."""
    if value and str(value) in _VALID_HARDWARE_CLASSES:
        return str(value)
    return "Generic"


def _functional_definition_rows(lattice: Any, orm: Any) -> List[Any]:
    """Rows for a lattice's resolved ``functional_definitions`` mapping.

    BaseLatticeModel.model_post_init has already turned a YAML path into the
    mapping it names, so this only ever sees ``{name: number}``.
    """
    return [
        orm.FunctionalDefinition(name=str(name), value=float(value))
        for name, value in (
            getattr(lattice, "functional_definitions", None) or {}
        ).items()
    ]


def _export_position(pos, orm, session) -> Optional[Any]:
    """Persist a Position sub-model and return the ORM row, or ``None``."""
    if pos is None:
        return None
    try:
        row = orm.Position(x=float(pos.x), y=float(pos.y), z=float(pos.z))
    except (AttributeError, TypeError):
        return None
    session.add(row)
    return row


def _export_rotation(rot, orm, session) -> Optional[Any]:
    """Persist a Rotation sub-model and return the ORM row, or ``None``."""
    if rot is None:
        return None
    try:
        row = orm.Rotation(
            phi=float(rot.phi), psi=float(rot.psi), theta=float(rot.theta)
        )
    except (AttributeError, TypeError):
        return None
    session.add(row)
    return row


def _export_physical(elem: Any, orm: Any, session: Any) -> Optional[Any]:
    """Persist the ``physical`` sub-model of *elem* if present.

    Returns the ``PhysicalElement`` ORM row, or ``None`` if the element has no
    physical placement data.
    """
    phys = getattr(elem, "physical", None)
    if phys is None:
        return None

    length = getattr(phys, "length", None)
    try:
        length = float(length) if length is not None else None
    except (TypeError, ValueError):
        length = None

    phys_row = orm.PhysicalElement(
        length=length,
        middle=_export_position(getattr(phys, "middle", None), orm, session),
        datum=_export_position(getattr(phys, "datum", None), orm, session),
        rotation=_export_rotation(getattr(phys, "rotation", None), orm, session),
    )
    session.add(phys_row)
    return phys_row


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def export_machine(
    machine: "MachineModel",
    db_url: str = "sqlite:///:memory:",
) -> int:
    """Persist *machine* to the database at *db_url*.

    Creates the schema automatically (``CREATE TABLE IF NOT EXISTS``).
    Multiple snapshots of the same machine can be stored; each gets a unique
    integer ID.

    Parameters
    ----------
    machine:
        A :class:`~laura.models.elementList.MachineModel` instance.
    db_url:
        SQLAlchemy database URL, e.g. ``"sqlite:///machine.db"`` or
        ``"postgresql://user:pass@host/db"``.

    Returns
    -------
    int
        The auto-generated ``MachineModel.id`` that identifies this snapshot.
    """
    orm = _load_orm()
    _, Session = _make_session_factory(db_url, orm)

    with Session() as session:
        # ── Elements ──────────────────────────────────────────────────────────
        # Use merge() so re-exporting the same machine into the same DB (e.g.
        # multiple snapshot test) does not raise UNIQUE constraint errors on the
        # text primary-key columns.
        elem_rows: Dict[str, Any] = {}
        for name, elem in machine.elements.items():
            row = orm.AcceleratorElement(
                name=name,
                hardware_type=getattr(elem, "hardware_type", None),
                hardware_class=_coerce_hardware_class(
                    getattr(elem, "hardware_class", None)
                ),
                hardware_model=getattr(elem, "hardware_model", None),
                machine_area=getattr(elem, "machine_area", None),
                virtual_name=getattr(elem, "virtual_name", None),
                subelement=(
                    str(elem.subelement)
                    if getattr(elem, "subelement", None) is not None
                    else None
                ),
            )
            merged = session.merge(row)
            elem_rows[name] = merged

        # ── Sections ──────────────────────────────────────────────────────────
        # Use get-or-create: if the SectionLattice already exists (re-export to
        # same DB), reuse the existing row to avoid FK cascade conflicts when
        # merge() tries to reconcile SectionLattice_elements child rows.
        section_rows: Dict[str, Any] = {}
        for sec_name, section in machine.sections.items():
            master = getattr(section, "master_lattice", None) or getattr(
                machine, "master_lattice", None
            )
            existing = session.get(orm.SectionLattice, sec_name)
            if existing is None:
                sec_row = orm.SectionLattice(
                    name=sec_name,
                    master_lattice=master,
                    section_type=getattr(section, "section_type", None),
                    revolution_frequency=getattr(
                        section, "revolution_frequency", None
                    ),
                )
                sec_row.functional_definitions = _functional_definition_rows(
                    section, orm
                )
                sec_row.elements = [
                    elem_rows[n]
                    for n in getattr(section, "order", [])
                    if n in elem_rows
                ]
                session.add(sec_row)
                section_rows[sec_name] = sec_row
            else:
                existing.master_lattice = master
                section_rows[sec_name] = existing

        # ── Layouts ───────────────────────────────────────────────────────────
        # Same get-or-create pattern for MachineLayout / MachineLayout_sections.
        layout_rows: Dict[str, Any] = {}
        for layout_name, layout in machine.lattices.items():
            master = getattr(layout, "master_lattice", None) or getattr(
                machine, "master_lattice", None
            )
            existing_layout = session.get(orm.MachineLayout, layout_name)
            if existing_layout is None:
                layout_row = orm.MachineLayout(
                    name=layout_name,
                    master_lattice=master,
                    layout_type=getattr(layout, "layout_type", None),
                    revolution_frequency=getattr(
                        layout, "revolution_frequency", None
                    ),
                )
                layout_row.functional_definitions = _functional_definition_rows(
                    layout, orm
                )
                layout_row.sections = [
                    section_rows[n] for n in layout.sections if n in section_rows
                ]
                session.add(layout_row)
                layout_rows[layout_name] = layout_row
            else:
                existing_layout.master_lattice = master
                layout_rows[layout_name] = existing_layout

        # ── MachineModel container ────────────────────────────────────────────
        mm_row = orm.MachineModel()
        mm_row.elements = list(elem_rows.values())
        mm_row.sections = list(section_rows.values())
        mm_row.layouts = list(layout_rows.values())
        session.add(mm_row)

        session.commit()
        session.refresh(mm_row)
        return mm_row.id


def load_machine_elements(
    db_url: str = "sqlite:///:memory:",
    machine_id: int = 1,
) -> List[Dict[str, Optional[str]]]:
    """Load element metadata for a machine snapshot from the database.

    Parameters
    ----------
    db_url:
        SQLAlchemy database URL.
    machine_id:
        The ID returned by :func:`export_machine`.

    Returns
    -------
    list of dict
        One entry per element with keys ``name``, ``hardware_type``,
        ``hardware_class``, ``hardware_model``, ``machine_area``.

    Raises
    ------
    KeyError
        If no ``MachineModel`` with the given *machine_id* exists.
    """
    orm = _load_orm()
    _, Session = _make_session_factory(db_url, orm)

    with Session() as session:
        mm = session.get(orm.MachineModel, machine_id)
        if mm is None:
            raise KeyError(f"No MachineModel with id={machine_id}")
        return [
            {
                "name": elem.name,
                "hardware_type": elem.hardware_type,
                "hardware_class": (
                    str(elem.hardware_class) if elem.hardware_class else None
                ),
                "hardware_model": elem.hardware_model,
                "machine_area": elem.machine_area,
            }
            for elem in mm.elements
        ]


def load_machine_sections(
    db_url: str = "sqlite:///:memory:",
    machine_id: int = 1,
) -> Dict[str, List[str]]:
    """Load section → element-name mapping for a machine snapshot.

    Parameters
    ----------
    db_url:
        SQLAlchemy database URL.
    machine_id:
        The ID returned by :func:`export_machine`.

    Returns
    -------
    dict
        ``{section_name: [element_name, ...]}``.  The join table is a set, so
        the beamline order is not preserved; sort on the elements' geometry if
        you need it.

    Raises
    ------
    KeyError
        If no ``MachineModel`` with the given *machine_id* exists.
    """
    orm = _load_orm()
    _, Session = _make_session_factory(db_url, orm)

    with Session() as session:
        mm = session.get(orm.MachineModel, machine_id)
        if mm is None:
            raise KeyError(f"No MachineModel with id={machine_id}")
        # sec.elements holds AcceleratorElement rows now, not name strings.
        return {sec.name: [e.name for e in sec.elements] for sec in mm.sections}
