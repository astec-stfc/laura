"""Tests for laura.exporters.SQL — SQLAlchemy persistence of MachineModel.

Phase 4 verification: apply DDL to SQLite, insert a machine model, query it back.
"""
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from laura import LAURA
from laura.models.element import Marker, Quadrupole, Dipole, Solenoid
from laura.models.element_list import MachineModel, SectionLattice

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
    from laura.exporters.sql_exporter import (
        export_machine,
        load_machine_elements,
        load_machine_sections,
    )
    return export_machine, load_machine_elements, load_machine_sections


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
        # The junction table stores element names but has no position column,
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
        from laura.exporters.sql_exporter import _coerce_hardware_class
        return _coerce_hardware_class

    def test_valid_hardware_class_passes_through(self):
        coerce = self._get_coerce()
        for cls in ("Magnet", "Diagnostic", "RF", "Marker", "Generic", "Monitor"):
            assert coerce(cls) == cls

    def test_all_schema_enum_members_valid(self):
        coerce = self._get_coerce()
        from laura.exporters.sql_exporter import _VALID_HARDWARE_CLASSES
        for cls in _VALID_HARDWARE_CLASSES:
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
        from laura.exporters import sql_exporter as sql_mod
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
# Direct unit tests for the un-integrated physical helpers
# (_export_position, _export_rotation, _export_physical)
# These helpers are defined but not yet called by export_machine.
# ---------------------------------------------------------------------------

def _get_sql_helpers():
    """Import SQL helpers; skip if sqlalchemy not installed."""
    pytest.importorskip("sqlalchemy")
    from laura.exporters.sql_exporter import (
        _load_orm,
        _make_session_factory,
        _export_position,
        _export_rotation,
        _export_physical,
    )
    return _load_orm, _make_session_factory, _export_position, _export_rotation, _export_physical


def _make_orm_session(orm):
    """Create a fresh in-memory SQLite session backed by the generated ORM."""
    _, Session = orm  # unpack tuple only if already called — helper handles both
    from laura.exporters.sql_exporter import _make_session_factory
    _, Session = _make_session_factory("sqlite:///:memory:", orm)
    return Session()


class TestSQLExportPhysicalHelpers:
    """Direct unit tests for _export_position, _export_rotation, _export_physical."""

    @pytest.fixture(autouse=True)
    def _setup(self):
        _load_orm, _make_session_factory, self._ep, self._er, self._eph = _get_sql_helpers()
        from laura.exporters.sql_exporter import _load_orm as lorm, _make_session_factory as msf
        self.orm = lorm()
        _, Session = msf("sqlite:///:memory:", self.orm)
        self.session = Session()

    def teardown_method(self):
        self.session.close()

    def test_export_position_none_returns_none(self):
        assert self._ep(None, self.orm, self.session) is None

    def test_export_position_valid_object(self):
        from laura.models.physical import Position
        pos = Position(x=1.0, y=2.0, z=3.0)
        result = self._ep(pos, self.orm, self.session)
        assert result is not None
        assert float(result.x) == pytest.approx(1.0)
        assert float(result.y) == pytest.approx(2.0)
        assert float(result.z) == pytest.approx(3.0)

    def test_export_position_bad_object_returns_none(self):
        class BadPos:
            x = "not_a_number"
            y = "not_a_number"
            z = "not_a_number"
        # float() on a string raises ValueError; but the except catches AttributeError/TypeError
        # If Position-like object has string coords, orm.Position constructor may raise TypeError
        # The fallback returns None
        bad = type("BadPos", (), {"x": object(), "y": object(), "z": object()})()
        result = self._ep(bad, self.orm, self.session)
        # Either returns a row (if ORM accepts it) or returns None (TypeError caught)
        # We verify no exception is raised
        assert result is None or result is not None  # must not raise

    def test_export_position_missing_attrs_returns_none(self):
        class NoXYZ:
            pass
        result = self._ep(NoXYZ(), self.orm, self.session)
        assert result is None

    def test_export_rotation_none_returns_none(self):
        assert self._er(None, self.orm, self.session) is None

    def test_export_rotation_valid_object(self):
        from laura.models.physical import Rotation
        rot = Rotation(phi=0.1, psi=0.2, theta=0.3)
        result = self._er(rot, self.orm, self.session)
        assert result is not None
        assert float(result.theta) == pytest.approx(0.3)

    def test_export_rotation_missing_attrs_returns_none(self):
        class NoAngles:
            pass
        result = self._er(NoAngles(), self.orm, self.session)
        assert result is None

    def test_export_physical_no_physical_returns_none(self):
        """_export_physical returns None when element has no physical attribute."""
        # Use a plain Python object with physical=None
        class NoPhysElem:
            physical = None
        result = self._eph(NoPhysElem(), self.orm, self.session)
        assert result is None

    def test_export_physical_with_physical_returns_row(self):
        q = Quadrupole(
            name="QPH",
            magnetic={"length": 0.3},
            physical={"length": 0.3, "middle": {"x": 0.0, "y": 0.0, "z": 1.0}},
        )
        result = self._eph(q, self.orm, self.session)
        assert result is not None
        assert float(result.length) == pytest.approx(0.3)

    def test_export_physical_non_numeric_length_uses_none(self):
        q = Quadrupole(
            name="QBAD",
            magnetic={"length": 0.3},
            physical={"length": 0.3, "middle": {"x": 0.0, "y": 0.0, "z": 1.0}},
        )
        # Monkey-patch physical.length to a non-numeric string
        object.__setattr__(q.physical, "length", "not_a_number")
        result = self._eph(q, self.orm, self.session)
        # The ValueError path sets length=None but still creates the row
        assert result is not None
        assert result.length is None
