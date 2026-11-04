"""SQLAlchemy persistence of MachineModel, round-tripped through SQLite."""
from pathlib import Path

import pytest

pytest.importorskip("sqlalchemy")

from laura import LAURA
from laura.exporters import sql_exporter as sql_mod
from laura.exporters.sql_exporter import export_machine, load_machine_elements, load_machine_sections
from laura.models.element import Marker, Quadrupole, Dipole
from laura.models.element_list import MachineModel

pytestmark = pytest.mark.slow


@pytest.fixture
def small_machine():
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
    m = Marker(name="X1", machine_area="BA1", hardware_class="Marker")
    q = Quadrupole(name="Q2", machine_area="BA1")
    return MachineModel(
        elements={"X1": m, "Q2": q},
        sections={},
        lattices={},
    )


def _export(machine, tmp_path, name="machine.db"):
    db_url = f"sqlite:///{tmp_path / name}"
    return db_url, export_machine(machine, db_url=db_url)


def _empty_machine():
    return MachineModel(elements={}, sections={}, lattices={})


def _single(element):
    return MachineModel(elements={element.name: element}, sections={}, lattices={})


class TestSQLExporterBasic:
    def test_export_returns_integer_id(self, small_machine):
        machine_id = export_machine(small_machine, db_url="sqlite:///:memory:")
        assert isinstance(machine_id, int)
        assert machine_id >= 1

    def test_full_round_trip_elements(self, small_machine, tmp_path):
        db_url, machine_id = _export(small_machine, tmp_path)
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

    def test_full_round_trip_sections(self, small_machine, tmp_path):
        db_url, machine_id = _export(small_machine, tmp_path)
        sections = load_machine_sections(db_url=db_url, machine_id=machine_id)

        assert "S01" in sections
        # The junction table has no position column, so order is not guaranteed.
        assert set(sections["S01"]) == {"M1", "Q1", "D1"}

    def test_multiple_snapshots_share_elements(self, small_machine, tmp_path):
        db_url, id1 = _export(small_machine, tmp_path)
        id2 = export_machine(small_machine, db_url=db_url)
        assert id1 != id2
        rows1 = load_machine_elements(db_url=db_url, machine_id=id1)
        rows2 = load_machine_elements(db_url=db_url, machine_id=id2)
        assert {r["name"] for r in rows1} == {r["name"] for r in rows2}

    @pytest.mark.parametrize(
        "loader, missing",
        [(load_machine_elements, 99), (load_machine_sections, 42)],
        ids=["elements", "sections"],
    )
    def test_load_unknown_id_raises(self, small_machine, tmp_path, loader, missing):
        db_url, _ = _export(small_machine, tmp_path)
        with pytest.raises(KeyError, match=str(missing)):
            loader(db_url=db_url, machine_id=missing)

    def test_bare_machine_no_physical(self, bare_machine, tmp_path):
        db_url, mid = _export(bare_machine, tmp_path)
        rows = load_machine_elements(db_url=db_url, machine_id=mid)

        assert len(rows) == 2
        names = {r["name"] for r in rows}
        assert names == {"X1", "Q2"}

    @pytest.mark.parametrize("bad_class", ["UnknownClass", None], ids=["unknown", "none"])
    def test_invalid_hardware_class_coerced_to_generic(self, tmp_path, bad_class):
        m = Marker(name="ODD", machine_area="X01", hardware_class="Marker")
        # Set after construction to bypass Pydantic enum validation
        object.__setattr__(m, "hardware_class", bad_class)
        db_url, mid = _export(_single(m), tmp_path)
        rows = load_machine_elements(db_url=db_url, machine_id=mid)
        assert rows[0]["hardware_class"] == "Generic"

    def test_empty_machine(self, tmp_path):
        db_url, mid = _export(_empty_machine(), tmp_path)
        assert load_machine_elements(db_url=db_url, machine_id=mid) == []
        assert load_machine_sections(db_url=db_url, machine_id=mid) == {}


class TestSQLInternalHelpers:
    def test_valid_hardware_class_passes_through(self):
        for cls in set(sql_mod._VALID_HARDWARE_CLASSES) | {
            "Magnet", "Diagnostic", "RF", "Marker", "Generic", "Monitor",
            "ACDipole", "Wire", "BeamBeam", "RFMultipole", "Simulation",
        }:
            assert sql_mod._coerce_hardware_class(cls) == cls

    # Enum is case-sensitive; 'magnet' != 'Magnet'
    @pytest.mark.parametrize("cls", ["UnknownWidget", None, "", "magnet"])
    def test_invalid_returns_generic(self, cls):
        assert sql_mod._coerce_hardware_class(cls) == "Generic"

    def test_load_orm_missing_file_raises(self, monkeypatch):
        monkeypatch.setattr(sql_mod, "_ORM_PATH", Path("/nonexistent/path/laura_orm.py"))
        with pytest.raises(FileNotFoundError, match="Generated ORM not found"):
            sql_mod._load_orm()


@pytest.fixture
def element_with_datum_and_rotation():
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
    def test_element_with_datum_and_rotation(self, element_with_datum_and_rotation, tmp_path):
        db_url, mid = _export(_single(element_with_datum_and_rotation), tmp_path)
        rows = load_machine_elements(db_url=db_url, machine_id=mid)
        assert len(rows) == 1
        assert rows[0]["name"] == "QR"

    def test_multi_section_multi_layout_machine(self, multi_section_machine, tmp_path):
        db_url, mid = _export(multi_section_machine, tmp_path)
        rows = load_machine_elements(db_url=db_url, machine_id=mid)
        sections = load_machine_sections(db_url=db_url, machine_id=mid)

        assert len(rows) == 4
        element_names = {r["name"] for r in rows}
        assert element_names == {"MS1", "QA", "MS2", "DB"}

        assert set(sections.keys()) == {"A01", "B01"}
        assert set(sections["A01"]) == {"MS1", "QA"}
        assert set(sections["B01"]) == {"MS2", "DB"}

    def test_element_optional_fields_stored(self, tmp_path):
        q = Quadrupole(
            name="QM",
            machine_area="SEC99",
            hardware_model="LINAC_QUAD_V2",
            magnetic={"length": 0.3},
        )
        db_url, mid = _export(_single(q), tmp_path)
        row = load_machine_elements(db_url=db_url, machine_id=mid)[0]
        assert row["hardware_model"] == "LINAC_QUAD_V2"
        assert row["machine_area"] == "SEC99"

    def test_in_memory_export_returns_correct_id_sequence(self):
        id1 = export_machine(_empty_machine(), db_url="sqlite:///:memory:")
        id2 = export_machine(_empty_machine(), db_url="sqlite:///:memory:")
        # Each call creates its own in-memory DB, so both start at 1
        assert id1 == 1
        assert id2 == 1

    def test_machine_area_none_stored_as_none(self, tmp_path):
        db_url, mid = _export(_single(Quadrupole(name="QN", magnetic={"length": 0.2})), tmp_path)
        rows = load_machine_elements(db_url=db_url, machine_id=mid)
        assert rows[0]["machine_area"] is None


class TestSQLExportPhysicalHelpers:
    """These helpers are not yet called by export_machine."""

    @pytest.fixture(autouse=True)
    def _setup(self):
        self._ep, self._er, self._eph = sql_mod._export_position, sql_mod._export_rotation, sql_mod._export_physical
        self.orm = sql_mod._load_orm()
        _, Session = sql_mod._make_session_factory("sqlite:///:memory:", self.orm)
        self.session = Session()
        yield
        self.session.close()

    @pytest.mark.parametrize("which", ["_ep", "_er"])
    def test_export_none_returns_none(self, which):
        assert getattr(self, which)(None, self.orm, self.session) is None

    @pytest.mark.parametrize("which", ["_ep", "_er"])
    def test_export_missing_attrs_returns_none(self, which):
        class NoAttrs:
            pass
        assert getattr(self, which)(NoAttrs(), self.orm, self.session) is None

    def test_export_position_valid_object(self):
        from laura.models.physical import Position
        pos = Position(x=1.0, y=2.0, z=3.0)
        result = self._ep(pos, self.orm, self.session)
        assert result is not None
        assert float(result.x) == pytest.approx(1.0)
        assert float(result.y) == pytest.approx(2.0)
        assert float(result.z) == pytest.approx(3.0)

    def test_export_position_bad_object_does_not_raise(self):
        # Returning None or a row are both fine; it just must not raise.
        bad = type("BadPos", (), {"x": object(), "y": object(), "z": object()})()
        self._ep(bad, self.orm, self.session)

    def test_export_rotation_valid_object(self):
        from laura.models.physical import Rotation
        rot = Rotation(phi=0.1, psi=0.2, theta=0.3)
        result = self._er(rot, self.orm, self.session)
        assert result is not None
        assert float(result.theta) == pytest.approx(0.3)

    def test_export_physical_no_physical_returns_none(self):
        class NoPhysElem:
            physical = None
        result = self._eph(NoPhysElem(), self.orm, self.session)
        assert result is None

    def test_export_physical_length(self):
        q = Quadrupole(
            name="QPH",
            magnetic={"length": 0.3},
            physical={"length": 0.3, "middle": {"x": 0.0, "y": 0.0, "z": 1.0}},
        )
        result = self._eph(q, self.orm, self.session)
        assert result is not None
        assert float(result.length) == pytest.approx(0.3)

        object.__setattr__(q.physical, "length", "not_a_number")
        result = self._eph(q, self.orm, self.session)
        assert result is not None
        assert result.length is None
