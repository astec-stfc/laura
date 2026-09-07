"""Tests for laura.Exporters.SQL — SQLAlchemy persistence of MachineModel.

Phase 4 verification: apply DDL to SQLite, insert a machine model, query it back.
"""
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from laura import LAURA
from laura.models.element import Marker, Quadrupole, Dipole, Solenoid
from laura.models.elementList import MachineModel, SectionLattice

pytestmark = pytest.mark.slow


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def small_machine():
    """Minimal 3-element machine: Marker + Quadrupole + Dipole."""
    m1 = Marker(
        name="M1",
        machine_area="S01",
        hardware_class="Marker",
        physical={"middle": {"x": 0.0, "y": 0.0, "z": 0.0}},
    )
    q1 = Quadrupole(
        name="Q1",
        machine_area="S01",
        magnetic={"length": 0.3, "k1l": -1.0},
        physical={"length": 0.3, "middle": {"x": 0.0, "y": 0.0, "z": 1.0}},
    )
    d1 = Dipole(
        name="D1",
        machine_area="S01",
        magnetic={"length": 0.5, "k0l": 0.1},
        physical={"length": 0.5, "middle": {"x": 0.0, "y": 0.0, "z": 2.0}},
    )
    sections = {"sections": {"S01": ["M1", "Q1", "D1"]}}
    layouts = {"default_layout": "line1", "layouts": {"line1": ["S01"]}}
    return LAURA(
        element_list=[m1, q1, d1],
        layout=layouts,
        section=sections,
    )


@pytest.fixture
def bare_machine():
    """Machine with no physical data (pure AcceleratorElement fields only)."""
    m = Marker(name="X1", machine_area="BA1", hardware_class="Marker")
    q = Quadrupole(name="Q2", machine_area="BA1")
    return MachineModel(
        elements={"X1": m, "Q2": q},
        sections={},
        lattices={},
    )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _import_sql():
    """Import SQL exporter; skip test if sqlalchemy is not installed."""
    pytest.importorskip("sqlalchemy")
    from laura.Exporters.SQL import (
        export_machine,
        load_machine_elements,
        load_machine_sections,
    )
    return export_machine, load_machine_elements, load_machine_sections


def _load_orm_module():
    """The generated ORM, for assertions the public API does not expose."""
    pytest.importorskip("sqlalchemy")
    from laura.Exporters.SQL import _load_orm

    return _load_orm()


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestSQLExporterBasic:
    """Phase 4: DDL creation, insert, and round-trip queries."""

    def test_export_returns_integer_id(self, small_machine):
        export_machine, _, _ = _import_sql()
        machine_id = export_machine(small_machine, db_url="sqlite:///:memory:")
        assert isinstance(machine_id, int)
        assert machine_id >= 1

    def test_load_elements_count(self, small_machine):
        """Export to file DB, load back, confirm element count matches."""
        export_machine, load_machine_elements, _ = _import_sql()
        with tempfile.TemporaryDirectory() as tmpdir:
            db_url = f"sqlite:///{Path(tmpdir) / 'count.db'}"
            mid = export_machine(small_machine, db_url=db_url)
            rows = load_machine_elements(db_url=db_url, machine_id=mid)
        assert len(rows) == 3

    def test_full_round_trip_elements(self, small_machine):
        """Export to SQLite file, load back, verify element metadata."""
        export_machine, load_machine_elements, _ = _import_sql()
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "machine.db"
            db_url = f"sqlite:///{db_path}"
            machine_id = export_machine(small_machine, db_url=db_url)
            rows = load_machine_elements(db_url=db_url, machine_id=machine_id)

        assert len(rows) == 3
        names = {r["name"] for r in rows}
        assert names == {"M1", "Q1", "D1"}

        by_name = {r["name"]: r for r in rows}
        assert by_name["Q1"]["hardware_type"] == "Quadrupole"
        assert by_name["Q1"]["hardware_class"] == "Magnet"
        assert by_name["Q1"]["machine_area"] == "S01"
        assert by_name["D1"]["hardware_type"] == "Dipole"
        assert by_name["M1"]["hardware_type"] == "Marker"

    def test_full_round_trip_sections(self, small_machine):
        """Export to SQLite file, load back, verify section structure."""
        export_machine, _, load_machine_sections = _import_sql()
        with tempfile.TemporaryDirectory() as tmpdir:
            db_url = f"sqlite:///{Path(tmpdir) / 'machine.db'}"
            machine_id = export_machine(small_machine, db_url=db_url)
            sections = load_machine_sections(db_url=db_url, machine_id=machine_id)

        assert "S01" in sections
        # The junction table is a set of foreign keys with no position column,
        # so retrieval order is not guaranteed — compare as a set.
        assert set(sections["S01"]) == {"M1", "Q1", "D1"}

    def test_multiple_snapshots_independent_ids(self, small_machine):
        """Two exports to the same DB produce distinct machine IDs."""
        export_machine, load_machine_elements, _ = _import_sql()
        with tempfile.TemporaryDirectory() as tmpdir:
            db_url = f"sqlite:///{Path(tmpdir) / 'multi.db'}"
            id1 = export_machine(small_machine, db_url=db_url)
            id2 = export_machine(small_machine, db_url=db_url)
        assert id1 != id2

    def test_load_unknown_id_raises(self, small_machine):
        """load_machine_elements raises KeyError for a missing ID."""
        export_machine, load_machine_elements, _ = _import_sql()
        with tempfile.TemporaryDirectory() as tmpdir:
            db_url = f"sqlite:///{Path(tmpdir) / 'test.db'}"
            export_machine(small_machine, db_url=db_url)
            with pytest.raises(KeyError, match="99"):
                load_machine_elements(db_url=db_url, machine_id=99)

    def test_bare_machine_no_physical(self, bare_machine):
        """Elements without physical data export and reload cleanly."""
        export_machine, load_machine_elements, _ = _import_sql()
        with tempfile.TemporaryDirectory() as tmpdir:
            db_url = f"sqlite:///{Path(tmpdir) / 'bare.db'}"
            mid = export_machine(bare_machine, db_url=db_url)
            rows = load_machine_elements(db_url=db_url, machine_id=mid)

        assert len(rows) == 2
        names = {r["name"] for r in rows}
        assert names == {"X1", "Q2"}

    def test_invalid_hardware_class_coerced_to_generic(self):
        """An element with an unrecognised hardware_class is stored as 'Generic'."""
        export_machine, load_machine_elements, _ = _import_sql()
        # Create element via dict to bypass Pydantic enum validation
        m = Marker(name="ODD", machine_area="X01", hardware_class="Marker")
        # Monkey-patch to an invalid class after construction
        object.__setattr__(m, "hardware_class", "UnknownClass")
        machine = MachineModel(elements={"ODD": m}, sections={}, lattices={})
        with tempfile.TemporaryDirectory() as tmpdir:
            db_url = f"sqlite:///{Path(tmpdir) / 'coerce.db'}"
            mid = export_machine(machine, db_url=db_url)
            rows = load_machine_elements(db_url=db_url, machine_id=mid)
        assert rows[0]["hardware_class"] == "Generic"

    def test_empty_machine(self):
        """An empty MachineModel exports without error."""
        export_machine, load_machine_elements, _ = _import_sql()
        machine = MachineModel(elements={}, sections={}, lattices={})
        with tempfile.TemporaryDirectory() as tmpdir:
            db_url = f"sqlite:///{Path(tmpdir) / 'empty.db'}"
            mid = export_machine(machine, db_url=db_url)
            rows = load_machine_elements(db_url=db_url, machine_id=mid)
        assert rows == []


# ---------------------------------------------------------------------------
# Internal helpers — unit tests for _coerce_hardware_class and _load_orm
# ---------------------------------------------------------------------------

class TestSQLInternalHelpers:
    """Direct unit tests for the private helper functions in SQL.py."""

    def _get_coerce(self):
        pytest.importorskip("sqlalchemy")
        from laura.Exporters.SQL import _coerce_hardware_class
        return _coerce_hardware_class

    def test_valid_hardware_class_passes_through(self):
        coerce = self._get_coerce()
        for cls in ("Magnet", "Diagnostic", "RF", "Marker", "Generic", "Monitor"):
            assert coerce(cls) == cls

    def test_all_schema_enum_members_valid(self):
        coerce = self._get_coerce()
        from laura.Exporters.SQL import _valid_hardware_classes
        for cls in _valid_hardware_classes():
            assert coerce(cls) == cls

    def test_invalid_string_returns_generic(self):
        coerce = self._get_coerce()
        assert coerce("UnknownWidget") == "Generic"

    def test_none_returns_generic(self):
        coerce = self._get_coerce()
        assert coerce(None) == "Generic"

    def test_empty_string_returns_generic(self):
        coerce = self._get_coerce()
        assert coerce("") == "Generic"

    def test_case_sensitive_mismatch_returns_generic(self):
        coerce = self._get_coerce()
        # Enum is case-sensitive; 'magnet' != 'Magnet'
        assert coerce("magnet") == "Generic"

    def test_load_orm_missing_file_raises(self):
        """_load_orm raises FileNotFoundError when the ORM file does not exist."""
        pytest.importorskip("sqlalchemy")
        from laura.Exporters import SQL as sql_mod
        original = sql_mod._ORM_PATH
        try:
            sql_mod._ORM_PATH = Path("/nonexistent/path/laura_orm.py")
            with pytest.raises(FileNotFoundError, match="Generated ORM not found"):
                sql_mod._load_orm()
        finally:
            sql_mod._ORM_PATH = original


# ---------------------------------------------------------------------------
# Edge cases — physical sub-models, optional fields, multi-section machines
# ---------------------------------------------------------------------------

@pytest.fixture
def element_with_datum_and_rotation():
    """Quadrupole with datum and rotation in addition to middle."""
    return Quadrupole(
        name="QR",
        machine_area="S02",
        magnetic={"length": 0.4, "k1l": 0.5},
        physical={
            "length": 0.4,
            "middle": {"x": 0.1, "y": 0.0, "z": 3.0},
            "datum": {"x": 0.0, "y": 0.0, "z": 2.8},
            "rotation": {"phi": 0.0, "psi": 0.0, "theta": 0.01},
        },
    )


@pytest.fixture
def multi_section_machine():
    """Machine with 2 sections and 2 layouts."""
    m1 = Marker(
        name="MS1", machine_area="A01", hardware_class="Marker",
        physical={"middle": {"x": 0, "y": 0, "z": 0}},
    )
    q1 = Quadrupole(
        name="QA", machine_area="A01",
        magnetic={"length": 0.3, "k1l": -1.0},
        physical={"length": 0.3, "middle": {"x": 0, "y": 0, "z": 1.0}},
    )
    m2 = Marker(
        name="MS2", machine_area="B01", hardware_class="Marker",
        physical={"middle": {"x": 0, "y": 0, "z": 5.0}},
    )
    d1 = Dipole(
        name="DB", machine_area="B01",
        magnetic={"length": 0.5, "k0l": 0.05},
        physical={"length": 0.5, "middle": {"x": 0, "y": 0, "z": 6.0}},
    )
    sections = {"sections": {"A01": ["MS1", "QA"], "B01": ["MS2", "DB"]}}
    layouts = {
        "default_layout": "full",
        "layouts": {"full": ["A01", "B01"], "half": ["A01"]},
    }
    return LAURA(element_list=[m1, q1, m2, d1], layout=layouts, section=sections)


class TestTypedElementRows:
    """The per-type tables, and the geometry that only fits in them."""

    def test_typed_row_carries_geometry(self, small_machine):
        """A Quadrupole lands in the Quadrupole table with its physical sub-model.

        gen-sqla emits concrete inheritance, so the typed row is a second row
        alongside the AcceleratorElement one rather than the same row seen
        through a subclass -- the junctions need the base row, and ``physical``
        is first declared on PhysicalAcceleratorElement, so geometry needs the
        typed one.  Both must be written.
        """
        export_machine, _, _ = _import_sql()
        orm = _load_orm_module()
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker

        with tempfile.TemporaryDirectory() as tmpdir:
            db_url = f"sqlite:///{Path(tmpdir) / 'geom.db'}"
            export_machine(small_machine, db_url=db_url)

            with sessionmaker(bind=create_engine(db_url))() as session:
                assert session.get(orm.AcceleratorElement, "Q1") is not None
                q = session.get(orm.Quadrupole, "Q1")
                assert q.hardware_type == "Quadrupole"
                assert q.physical.length == pytest.approx(0.3)
                assert q.physical.s_point == "middle"
                assert q.physical.middle.z == pytest.approx(1.0)
                # Defaulted by PhysicalElement.model_post_init, not by us.
                assert q.physical.rotation is not None
                assert q.physical.error.position is not None
                assert q.physical.survey.rotation is not None

    def test_re_export_does_not_duplicate_typed_rows(self, small_machine):
        """merge() keyed on the text primary key, so a second export overwrites.

        The sub-models have no natural key -- they are reached only through the
        element -- so nothing stops a second export leaving a full orphaned copy
        of every one of them behind.  What stops it is the composition cascade
        laura/schema/generate_orm.py adds; this is the check that it still does.
        """
        export_machine, _, _ = _import_sql()
        orm = _load_orm_module()
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker

        with tempfile.TemporaryDirectory() as tmpdir:
            db_url = f"sqlite:///{Path(tmpdir) / 'twice.db'}"
            export_machine(small_machine, db_url=db_url)
            export_machine(small_machine, db_url=db_url)

            with sessionmaker(bind=create_engine(db_url))() as session:
                assert session.query(orm.Quadrupole).count() == 1
                assert session.query(orm.AcceleratorElement).count() == 3
                assert session.query(orm.PhysicalElement).count() == 3
                assert session.query(orm.QuadrupoleMagnet).count() == 1


class TestLatticeMetadata:
    """The BaseLatticeModel slots SectionLattice and MachineLayout share."""

    def test_lattice_metadata_round_trips(self, small_machine):
        """section_type, revolution_frequency and functional_definitions persist.

        functional_definitions is the awkward one: it is a keyed class two
        different classes own, so gen-sqla put both owners' foreign keys in the
        primary key and every insert failed on the NULL one.  laura/schema/
        generate_orm.py gives such a table a surrogate id instead; this is the
        check that it still does.
        """
        export_machine, _, _ = _import_sql()
        section = small_machine.sections["S01"]
        section.section_type = "rf"
        section.revolution_frequency = 1.2e6
        section.functional_definitions = {"quad1_k1l": -2, "cav1_phase": 90.5}
        small_machine.lattices["line1"].functional_definitions = {"quad1_k1l": -2}

        orm = _load_orm_module()
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker

        with tempfile.TemporaryDirectory() as tmpdir:
            db_url = f"sqlite:///{Path(tmpdir) / 'meta.db'}"
            export_machine(small_machine, db_url=db_url)

            with sessionmaker(bind=create_engine(db_url))() as session:
                row = session.get(orm.SectionLattice, "S01")
                assert row.section_type == "rf"
                assert row.revolution_frequency == pytest.approx(1.2e6)
                assert {d.name: d.value for d in row.functional_definitions} == {
                    "quad1_k1l": -2.0,
                    "cav1_phase": 90.5,
                }
                layout = session.get(orm.MachineLayout, "line1")
                assert [d.name for d in layout.functional_definitions] == ["quad1_k1l"]


class TestSQLExporterEdgeCases:
    """Test edge cases and less-common code paths in the SQL exporter."""

    def test_load_sections_unknown_id_raises(self, small_machine):
        """load_machine_sections also raises KeyError for a missing machine ID."""
        export_machine, _, load_machine_sections = _import_sql()
        with tempfile.TemporaryDirectory() as tmpdir:
            db_url = f"sqlite:///{Path(tmpdir) / 'sec.db'}"
            export_machine(small_machine, db_url=db_url)
            with pytest.raises(KeyError, match="42"):
                load_machine_sections(db_url=db_url, machine_id=42)

    def test_load_sections_empty_machine(self):
        """Empty machine has no sections; load_machine_sections returns {}."""
        export_machine, _, load_machine_sections = _import_sql()
        machine = MachineModel(elements={}, sections={}, lattices={})
        with tempfile.TemporaryDirectory() as tmpdir:
            db_url = f"sqlite:///{Path(tmpdir) / 'empty_sec.db'}"
            mid = export_machine(machine, db_url=db_url)
            sections = load_machine_sections(db_url=db_url, machine_id=mid)
        assert sections == {}

    def test_element_with_datum_and_rotation(self, element_with_datum_and_rotation):
        """Elements whose physical sub-model has datum and rotation export cleanly."""
        export_machine, load_machine_elements, _ = _import_sql()
        machine = MachineModel(
            elements={"QR": element_with_datum_and_rotation},
            sections={},
            lattices={},
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            db_url = f"sqlite:///{Path(tmpdir) / 'rot.db'}"
            mid = export_machine(machine, db_url=db_url)
            rows = load_machine_elements(db_url=db_url, machine_id=mid)
        assert len(rows) == 1
        assert rows[0]["name"] == "QR"

    def test_multi_section_multi_layout_machine(self, multi_section_machine):
        """Machines with 2 sections and 2 layouts store and reload correctly."""
        export_machine, load_machine_elements, load_machine_sections = _import_sql()
        with tempfile.TemporaryDirectory() as tmpdir:
            db_url = f"sqlite:///{Path(tmpdir) / 'multi.db'}"
            mid = export_machine(multi_section_machine, db_url=db_url)
            rows = load_machine_elements(db_url=db_url, machine_id=mid)
            sections = load_machine_sections(db_url=db_url, machine_id=mid)

        assert len(rows) == 4
        element_names = {r["name"] for r in rows}
        assert element_names == {"MS1", "QA", "MS2", "DB"}

        assert set(sections.keys()) == {"A01", "B01"}
        assert set(sections["A01"]) == {"MS1", "QA"}
        assert set(sections["B01"]) == {"MS2", "DB"}

    def test_element_with_none_hardware_class_stored_as_generic(self):
        """Elements where hardware_class is None are stored as 'Generic'."""
        export_machine, load_machine_elements, _ = _import_sql()
        m = Marker(name="NHC", machine_area="X01", hardware_class="Marker")
        object.__setattr__(m, "hardware_class", None)
        machine = MachineModel(elements={"NHC": m}, sections={}, lattices={})
        with tempfile.TemporaryDirectory() as tmpdir:
            db_url = f"sqlite:///{Path(tmpdir) / 'nhc.db'}"
            mid = export_machine(machine, db_url=db_url)
            rows = load_machine_elements(db_url=db_url, machine_id=mid)
        assert rows[0]["hardware_class"] == "Generic"

    def test_element_optional_fields_stored(self):
        """hardware_model and machine_area are stored and retrieved."""
        export_machine, load_machine_elements, _ = _import_sql()
        q = Quadrupole(
            name="QM",
            machine_area="SEC99",
            hardware_model="LINAC_QUAD_V2",
            magnetic={"length": 0.3},
        )
        machine = MachineModel(elements={"QM": q}, sections={}, lattices={})
        with tempfile.TemporaryDirectory() as tmpdir:
            db_url = f"sqlite:///{Path(tmpdir) / 'fields.db'}"
            mid = export_machine(machine, db_url=db_url)
            rows = load_machine_elements(db_url=db_url, machine_id=mid)
        row = rows[0]
        assert row["hardware_model"] == "LINAC_QUAD_V2"
        assert row["machine_area"] == "SEC99"

    def test_second_snapshot_references_same_elements(self, small_machine):
        """Elements are shared across snapshots; both snapshots' element sets are equal."""
        export_machine, load_machine_elements, _ = _import_sql()
        with tempfile.TemporaryDirectory() as tmpdir:
            db_url = f"sqlite:///{Path(tmpdir) / 'shared.db'}"
            id1 = export_machine(small_machine, db_url=db_url)
            id2 = export_machine(small_machine, db_url=db_url)
            rows1 = load_machine_elements(db_url=db_url, machine_id=id1)
            rows2 = load_machine_elements(db_url=db_url, machine_id=id2)
        assert {r["name"] for r in rows1} == {r["name"] for r in rows2}

    def test_in_memory_export_returns_correct_id_sequence(self):
        """Back-to-back in-memory exports yield IDs 1, 2, …"""
        export_machine, _, _ = _import_sql()
        machine = MachineModel(elements={}, sections={}, lattices={})
        id1 = export_machine(machine, db_url="sqlite:///:memory:")
        id2 = export_machine(machine, db_url="sqlite:///:memory:")
        # Each call creates its own in-memory DB, so both start at 1
        assert id1 == 1
        assert id2 == 1

    def test_machine_area_none_stored_as_none(self):
        """Elements with no machine_area store None and retrieve None."""
        export_machine, load_machine_elements, _ = _import_sql()
        q = Quadrupole(name="QN", magnetic={"length": 0.2})
        machine = MachineModel(elements={"QN": q}, sections={}, lattices={})
        with tempfile.TemporaryDirectory() as tmpdir:
            db_url = f"sqlite:///{Path(tmpdir) / 'none_area.db'}"
            mid = export_machine(machine, db_url=db_url)
            rows = load_machine_elements(db_url=db_url, machine_id=mid)
        assert rows[0]["machine_area"] is None


# ---------------------------------------------------------------------------
# The mapper-driven sub-model exporter
# ---------------------------------------------------------------------------

def _get_export_submodel():
    """Import _export_submodel; skip if sqlalchemy not installed."""
    pytest.importorskip("sqlalchemy")
    from laura.Exporters.SQL import _export_submodel

    return _export_submodel


class TestExportSubmodel:
    """Direct unit tests for the generic sub-model exporter.

    One function replaced the per-class helpers this file used to test, because
    ~140 element classes each retarget ``magnetic``/``simulation`` at their own
    table and writing that out by hand is several hundred cases that go stale.
    """

    @pytest.fixture(autouse=True)
    def _setup(self):
        # No session: it builds unattached rows and lets the save-update cascade
        # persist them via the element that owns them.
        self._export = _get_export_submodel()
        self.orm = _load_orm_module()

    def test_none_returns_none(self):
        assert self._export(None, self.orm.Position) is None

    def test_scalars_are_copied_by_slot_name(self):
        from laura.models.physical import Position

        row = self._export(Position(x=1.0, y=2.0, z=3.0), self.orm.Position)
        assert (row.x, row.y, row.z) == pytest.approx((1.0, 2.0, 3.0))

    def test_absent_fields_are_left_unset(self):
        """A source object with none of the slots still yields an empty row."""

        row = self._export(type("NoXYZ", (), {})(), self.orm.Position)
        assert row is not None
        assert row.x is None

    def test_unusable_value_is_dropped_not_raised(self):
        """One odd field must not cost the whole element."""
        bad = type("BadPos", (), {"x": object(), "y": "nope", "z": 3})()
        row = self._export(bad, self.orm.Position)
        assert row.x is None
        assert row.y is None
        assert row.z == pytest.approx(3.0)

    def test_nested_submodels_recurse(self):
        q = Quadrupole(
            name="QPH",
            magnetic={"length": 0.3},
            physical={"length": 0.3, "middle": {"x": 0.0, "y": 0.0, "z": 1.0}},
        )
        row = self._export(q.physical, self.orm.PhysicalElement)
        assert row.length == pytest.approx(0.3)
        assert row.middle.z == pytest.approx(1.0)

    def test_out_of_range_enum_value_is_dropped(self):
        """gen-sqla emits real Enum columns, which raise on an unlisted value."""
        q = Quadrupole(name="QBAD", magnetic={"length": 0.3})
        object.__setattr__(q.magnetic, "plane", "Diagonal")
        object.__setattr__(q.magnetic, "length", "not_a_number")
        row = self._export(q.magnetic, self.orm.QuadrupoleMagnet)
        assert row.plane is None
        assert row.length is None

    def test_keyed_map_puts_the_key_back_on_the_row(self):
        """ControlsInformation.variables is a name -> ControlVariable mapping."""
        q = Quadrupole(
            name="QCTL",
            magnetic={"length": 0.3},
            controls={
                "variables": {
                    "SETI": {"identifier": "Q:SETI", "protocol": "EPICS"},
                }
            },
        )
        row = self._export(q.controls, self.orm.ControlsInformation)
        assert [(v.name, v.identifier) for v in row.variables] == [
            ("SETI", "Q:SETI")
        ]


class TestSubmodelsReachTheDatabase:
    """End-to-end: the composed sub-models, not just identity and geometry."""

    def test_magnetic_and_controls_are_written(self, small_machine):
        export_machine, _, _ = _import_sql()
        orm = _load_orm_module()
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker

        small_machine.elements["Q1"].controls = {
            "variables": {"SETI": {"identifier": "S01-Q1:SETI", "protocol": "EPICS"}}
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            db_url = f"sqlite:///{Path(tmpdir) / 'sub.db'}"
            export_machine(small_machine, db_url=db_url)

            with sessionmaker(bind=create_engine(db_url))() as session:
                q = session.get(orm.Quadrupole, "Q1")
                # Quadrupole.magnetic targets QuadrupoleMagnet, not the base
                # MagneticElement -- the reason this is mapper-driven.
                assert type(q.magnetic).__name__ == "QuadrupoleMagnet"
                assert q.magnetic.length == pytest.approx(0.3)
                assert [v.identifier for v in q.controls.variables] == [
                    "S01-Q1:SETI"
                ]

    def test_upstream_and_downstream_are_linked(self):
        """Written in a second pass: an element may name one declared later."""
        export_machine, _, _ = _import_sql()
        orm = _load_orm_module()
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker

        machine = LAURA(
            element_list=[
                Quadrupole(name="QA", machine_area="S01", downstream=["QB"]),
                Quadrupole(name="QB", machine_area="S01", upstream=["QA"]),
            ],
            layout={"default_layout": "l", "layouts": {"l": ["S01"]}},
            section={"sections": {"S01": ["QA", "QB"]}},
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            db_url = f"sqlite:///{Path(tmpdir) / 'links.db'}"
            export_machine(machine, db_url=db_url)

            with sessionmaker(bind=create_engine(db_url))() as session:
                qa = session.get(orm.AcceleratorElement, "QA")
                qb = session.get(orm.AcceleratorElement, "QB")
                assert [e.name for e in qa.downstream] == ["QB"]
                assert [e.name for e in qb.upstream] == ["QA"]

    def test_per_type_controls_row_is_written(self):
        """A Screen's controls go in ScreenControlsInformation, with its extras.

        The per-type controls classes mirror the per-type ``magnetic`` ones, so
        this is the same claim as ``QuadrupoleMagnet`` above -- but they were
        added later and the ``slot_usage`` that ranges them is easy to lose in a
        schema edit.
        """
        from laura.models.element import Screen

        export_machine, _, _ = _import_sql()
        orm = _load_orm_module()
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker

        machine = LAURA(
            element_list=[
                Screen(
                    name="SCR",
                    machine_area="S01",
                    controls={
                        "variables": {},
                        "movement_type": "VMOTOR",
                        "schema": "screen.yaml",
                    },
                )
            ],
            layout={"default_layout": "l", "layouts": {"l": ["S01"]}},
            section={"sections": {"S01": ["SCR"]}},
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            db_url = f"sqlite:///{Path(tmpdir) / 'screen.db'}"
            export_machine(machine, db_url=db_url)

            with sessionmaker(bind=create_engine(db_url))() as session:
                controls = session.get(orm.Screen, "SCR").controls
                assert type(controls).__name__ == "ScreenControlsInformation"
                assert controls.movement_type == "VMOTOR"
                # Read through the ``schema_`` field alias, not getattr.
                assert controls.schema == "screen.yaml"
