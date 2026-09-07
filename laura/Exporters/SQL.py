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
from functools import lru_cache
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Optional

if TYPE_CHECKING:
    from laura.models.elementList import MachineModel

# Path to the generated SQLAlchemy ORM module (never imported at package level so
# sqlalchemy remains an optional dependency).
_ORM_PATH = Path(__file__).parent.parent / "schema" / "generated" / "laura_orm.py"



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


@lru_cache(maxsize=1)
def _valid_hardware_classes() -> frozenset:
    """The ``HardwareClassEnum`` members, read off the generated ORM column.

    Read rather than listed: the hand-kept copy this replaced was four values
    behind the schema, so every Valve and laser element was silently written as
    ``Generic``.
    """
    return frozenset(_load_orm().AcceleratorElement.hardware_class.type.enums)


def _coerce_hardware_class(value: Optional[str]) -> str:
    """Return *value* if it is a valid schema enum member, otherwise ``'Generic'``."""
    if value and str(value) in _valid_hardware_classes():
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


def _float(value: Any) -> Optional[float]:
    """*value* as a float, or ``None`` if it is absent or not a number."""
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _coerce_column(value: Any, column: Any) -> Any:
    """*value* as something the SQLAlchemy *column* will accept, or ``None``.

    Pydantic is looser than the generated DDL in both directions: a slot the
    schema calls a double may hold an int, and an enum-ranged slot may hold a
    string the enum does not list.  A value that cannot be made to fit is
    dropped rather than raised on -- one odd field must not cost the whole
    element.
    """
    if value is None or isinstance(value, (list, tuple, dict, set)):
        return None

    enum_values = getattr(column.type, "enums", None)
    if enum_values is not None:
        return str(value) if str(value) in enum_values else None

    try:
        py = column.type.python_type
    except NotImplementedError:
        return value
    if py is bool:
        return bool(value)
    if py is float:
        return _float(value)
    if py is int:
        try:
            return int(value)
        except (TypeError, ValueError):
            return None
    if py is str:
        return value if isinstance(value, str) else str(value)
    return value if isinstance(value, py) else None


def _slot_value(value: Any, slot: str) -> Any:
    """The field of *value* that LinkML calls *slot*.

    Usually the attribute of the same name, but a Pydantic model may have had to
    rename a field and keep the slot name as its alias: ``ControlsInformation``
    stores ``schema`` as ``schema_`` because ``BaseModel.schema`` is a method,
    and a plain ``getattr`` would return that method rather than the value.
    """
    fields = getattr(type(value), "model_fields", None)
    if fields is not None and slot not in fields:
        for name, info in fields.items():
            if info.alias == slot:
                return getattr(value, name, None)
        return None
    return getattr(value, slot, None)


def _key_slot(mapper: Any) -> Optional[str]:
    """The slot a keyed-inlined map's key belongs in.

    LinkML's ``key: true``, which the ORM no longer records once the primary key
    has had to become a surrogate ``id`` -- a keyed class reachable from more
    than one slot cannot use its key as the primary key.  Every keyed class in
    this schema calls that slot ``name``; the fallback is for one that does not.
    """
    if "name" in mapper.columns:
        return "name"
    return next(
        (c.key for c in mapper.columns if c.key != "id" and not c.foreign_keys),
        None,
    )


def _export_submodel(value: Any, orm_cls: Any) -> Optional[Any]:
    """*value*, a Pydantic sub-model, as an unattached row of *orm_cls*.

    Driven off the mapper rather than written out slot by slot.  There are ~140
    element classes and most retarget ``magnetic`` and ``simulation`` at their
    own table (``Quadrupole.magnetic`` is a ``QuadrupoleMagnet``, not a
    ``MagneticElement``), so the explicit alternative is several hundred cases
    that go stale the moment the schema changes.  Both sides name their fields
    after the same LinkML slots, so matching on name is exact, not a heuristic.

    Nothing here calls ``session.add``: every row it builds is reachable from
    the element through a relationship, and SQLAlchemy's default save-update
    cascade persists it when the element is added.  Adding it as well would make
    ``merge()`` insert the original and its merged copy both.
    """
    if value is None:
        return None

    from sqlalchemy import inspect as sqla_inspect

    mapper = sqla_inspect(orm_cls)
    row = orm_cls(
        **{
            col.key: coerced
            # ``id`` is the surrogate key and every other FK column belongs to a
            # relationship handled below, so neither comes from the sub-model.
            for col in mapper.columns
            if col.key != "id" and not col.foreign_keys
            for coerced in [_coerce_column(_slot_value(value, col.key), col)]
            if coerced is not None
        }
    )
    _attach_related(value, row, mapper)
    return row


def _attach_related(value: Any, row: Any, mapper: Any) -> None:
    """Fill *row*'s relationships from the matching fields of *value*."""
    for rel in mapper.relationships:
        # Element cross-references, not owned sub-models: they point at rows
        # this function has no way to reach.  export_machine wires them up
        # once every element exists.
        if rel.key in ("upstream", "downstream"):
            continue

        target = rel.mapper.class_
        if not rel.uselist:
            nested = _export_submodel(_slot_value(value, rel.key), target)
            if nested is not None:
                setattr(row, rel.key, nested)
            continue

        # gen-sqla backs a multivalued scalar slot with a junction class and an
        # association proxy over it, so the field to read is the proxy's name.
        field = rel.key[:-4] if rel.key.endswith("_rel") else rel.key
        items = _slot_value(value, field)
        if not items:
            continue
        if rel.key.endswith("_rel"):
            setattr(row, field, [str(item) for item in items])
        elif isinstance(items, dict):
            # A keyed inlined map -- the key is a slot on the target class.
            key_slot = _key_slot(rel.mapper)
            setattr(
                row,
                rel.key,
                [
                    _set_key(_export_submodel(item, target), key_slot, key)
                    for key, item in items.items()
                ],
            )
        else:
            setattr(row, rel.key, [_export_submodel(i, target) for i in items])


def _set_key(row: Optional[Any], key_slot: str, key: Any) -> Optional[Any]:
    """Put a mapping's key back on the row it names, e.g. ControlVariable.name."""
    if row is not None:
        setattr(row, key_slot, str(key))
    return row


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
    from sqlalchemy import inspect as sqla_inspect

    orm = _load_orm()
    _, Session = _make_session_factory(db_url, orm)

    with Session() as session:
        # ── Elements ──────────────────────────────────────────────────────────
        # Use merge() so re-exporting the same machine into the same DB (e.g.
        # multiple snapshot test) does not raise UNIQUE constraint errors on the
        # text primary-key columns.
        elem_rows: Dict[str, Any] = {}
        for name, elem in machine.elements.items():
            common = dict(
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
            # MachineModel_elements and SectionLattice_elements are foreign keys
            # into AcceleratorElement.name, so every element needs a row there
            # whatever its type.
            elem_rows[name] = session.merge(orm.AcceleratorElement(**common))

            # ...and a second row in its own table.  gen-sqla emits *concrete*
            # inheritance -- each per-type table restates the base columns and
            # stands alone, so a Quadrupole row is not also an AcceleratorElement
            # row and cannot go in those junctions.  It is written as well, not
            # instead, because it is the only place geometry fits: ``physical``
            # is first declared on PhysicalAcceleratorElement.
            cls = getattr(orm, elem.linkml_class_name(), None)
            if cls is None or cls is orm.AcceleratorElement:
                continue
            typed = cls(**common)
            # Everything the element composes -- physical, magnetic, electrical,
            # simulation, manufacturer, degauss, controls, reference -- whichever
            # of them this class actually declares.
            _attach_related(elem, typed, sqla_inspect(cls))
            session.merge(typed)

        # ── Element cross-references ──────────────────────────────────────────
        # Deferred to here: an element may name a neighbour declared after it.
        for name, elem in machine.elements.items():
            for slot in ("upstream", "downstream"):
                linked = [
                    elem_rows[str(other)]
                    for other in getattr(elem, slot, None) or []
                    if str(other) in elem_rows
                ]
                if linked:
                    setattr(elem_rows[name], slot, linked)

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
