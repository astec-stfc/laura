"""Multi-component (Taylor) wake tables: kept whole through HDF5 and the ASTRA/Ocelot format."""

import re
import warnings

import numpy as np
import pytest

from laura.models.element import Wakefield
from laura.translator.converters.converter import translate_elements
from laura.translator.utils.fields import FieldMap, WakeComponent
from laura.translator.utils.fields import taylor
from laura.translator.utils.fields.field_parameter import set_field

S = np.linspace(0, 1e-3, 5)


def _components():
    """Every part a table can have: W0 and W1 tables, lumped terms, and an offset-dependent nm."""
    return [
        WakeComponent(nm=0, R=152.0, L=1e-9, Cinv=2e10,
                      W0=np.column_stack([S, 1e12 * np.exp(-S / 1e-4)]),
                      W1=np.column_stack([S[:3], [3e2, 2e2, 1e2]])),
        WakeComponent(nm=13, W1=np.column_stack([S, 1e14 * S])),
        WakeComponent(nm=11, W0=np.column_stack([S[:2], [5e11, 4e11]])),
    ]


def _table_file(path):
    np.savetxt(path, taylor.to_table(_components()))
    return str(path)


def test_the_table_has_ocelots_layout():
    table = taylor.to_table(_components())
    assert table[:4].tolist() == [[3, 0], [5, 3], [152.0, 1e-9], [2e10, 0]]
    assert table[12:15].tolist() == [[0, 5], [0, 0], [0, 13]]
    assert len(table) == 1 + 3 * 3 + (5 + 3) + 5 + 2


def test_a_table_that_disagrees_with_its_headers_is_refused():
    table = taylor.to_table(_components())
    with pytest.raises(ValueError):
        taylor.from_table(table[:-1])
    with pytest.raises(ValueError):
        taylor.from_table(np.vstack([table, [0, 0]]))


@pytest.mark.parametrize("code", ["ocelot", "astra"])
def test_text_round_trip_is_exact(tmp_path, code):
    for sub in ("src", "out"):
        (tmp_path / sub).mkdir()
    wake = FieldMap(_table_file(tmp_path / "src" / "w.dat"), field_type="TaylorWake")
    assert wake.wake_components == _components()
    written = wake.write_field_file(code=code, location=str(tmp_path / "out" / "w"))
    assert written.endswith(f".{code}")
    assert np.array_equal(np.loadtxt(written), taylor.to_table(_components()))


def test_hdf5_round_trip_is_exact(tmp_path):
    (tmp_path / "src").mkdir()
    wake = FieldMap(_table_file(tmp_path / "src" / "w.dat"), field_type="TaylorWake")
    wake.reference_length = 1.0
    again = FieldMap(wake.write_field_file(code="hdf5"))
    assert again.field_type == "TaylorWake"
    assert again.wake_components == _components()
    assert again.reference_length == 1.0


def test_ocelot_reads_what_is_written_as_it_reads_the_source(tmp_path):
    wake3d = pytest.importorskip("ocelot.cpbd.wake3D")
    for sub in ("src", "out"):
        (tmp_path / sub).mkdir()
    source = _table_file(tmp_path / "src" / "w.dat")
    wake = FieldMap(FieldMap(source, field_type="TaylorWake").write_field_file(code="hdf5"))
    written = wake.write_field_file(code="ocelot", location=str(tmp_path / "out" / "w"))
    (t_src, h_src), (t_new, h_new) = (wake3d.WakeTable(f).TH for f in (source, written))
    assert np.array_equal(h_src, h_new)
    for a, b in zip(t_src, t_new):
        for x, y in zip(a, b):
            assert np.array_equal(x, y)


SZ, CHARGE = 1e-4, 250e-12
G = np.linspace(0, 2e-3, 2001)


def _foldable():
    """Every part :func:`taylor.to_3d_wake` keeps, none it drops."""
    c = taylor.speed_of_light
    return [
        WakeComponent(nm=0, Cinv=1e13,
                      W0=np.column_stack([G, 3e14 * np.exp(-np.sqrt(G / 1.7e-3))]),
                      W1=np.column_stack([G, 1e6 * G * np.exp(-G / 2e-4)])),
        WakeComponent(nm=13, R=1e4,
                      W0=np.column_stack([G, 1e17 * np.exp(-G / 1e-4)]),
                      W1=np.column_stack([G, -1e17 * G * np.exp(-G / 1e-3) / (2 * c)])),
        WakeComponent(nm=24, W1=np.column_stack([G, -5e16 * G / (2 * c)])),
    ]


def _ocelot_kicks(path, x=0.0, y=0.0):
    """Ocelot's (Px, Py, Pz) [V] along a 250 pC Gaussian bunch, all at offset (x, y)."""
    from statistics import NormalDist

    wake3d = pytest.importorskip("ocelot.cpbd.wake3D")
    z = SZ * np.array([NormalDist().inv_cdf(p) for p in np.linspace(5e-4, 1 - 5e-4, 40000)])
    n = len(z)
    kicks = wake3d.Wake().add_total_wake(
        np.full(n, x), np.full(n, y), z, np.full(n, CHARGE / n), wake3d.WakeTable(str(path)).TH, 500, 0
    )
    return z, kicks[:3]


def _close(a, b, tol=1e-2):
    return np.max(np.abs(a - b)) < tol * np.max(np.abs(b))


def test_folding_keeps_what_ocelot_does_with_it(tmp_path):
    folded = taylor.from_3d_wake(*_fold(_foldable()))
    np.savetxt(tmp_path / "full.dat", taylor.to_table(_foldable()))
    np.savetxt(tmp_path / "folded.dat", taylor.to_table(folded))
    for offset, axis in (({}, 2), ({"x": 1e-3}, 0), ({"y": 1e-3}, 1)):
        _, full = _ocelot_kicks(tmp_path / "full.dat", **offset)
        _, again = _ocelot_kicks(tmp_path / "folded.dat", **offset)
        assert _close(again[axis], full[axis])


def _fold(components):
    z, w = taylor.to_3d_wake(components)
    return z, w["Wz"], w["Wx"], w["Wy"]


def test_a_3d_wake_gives_ocelot_the_kicks_it_describes(tmp_path):
    """A kick of +q x Wx(s) towards the source's offset, an energy loss of q Wz(s)."""
    for sub in ("src", "out"):
        (tmp_path / sub).mkdir()
    wake = FieldMap()
    for name, value, units in (("z", G, "m"), ("Wz", 3e14 * np.exp(-np.sqrt(G / 1.7e-3)), "V/C"),
                               ("Wx", 1e17 * G * np.exp(-G / 1e-3), "V/C/m"),
                               ("Wy", 5e16 * G, "V/C/m")):
        set_field(wake, name, value, units)
    wake.field_type, wake.read, wake.filename = "3DWake", True, str(tmp_path / "src" / "w.hdf5")
    path = wake.write_field_file("ocelot", location=str(tmp_path / "out" / "w"))

    def expected(name, z):
        """q times the wake convolved with the bunch: the source is u ahead of the witness."""
        density = np.exp(-((z[:, None] - G) ** 2) / (2 * SZ**2)) / (np.sqrt(2 * np.pi) * SZ)
        return CHARGE * np.trapezoid(getattr(wake, name).value.val * density, G, axis=1)

    for offset, axis, name, sign in (({}, 2, "Wz", -1), ({"x": 1e-3}, 0, "Wx", 1e-3),
                                     ({"y": 1e-3}, 1, "Wy", 1e-3)):
        z, kicks = _ocelot_kicks(path, **offset)
        core = np.abs(z) < 2 * SZ
        assert _close(kicks[axis][core], sign * expected(name, z[core]), 2e-2)


def test_dropped_parts_are_the_point_terms_and_the_other_components():
    dropped = taylor.dropped_parts(_components())
    assert len(dropped) == 3
    assert dropped[0].startswith("00: a point wake of -4.44e+10")  # c (R - W1(0))
    assert dropped[1].startswith("00: the inductive term")
    assert dropped[2] == "component 11"
    assert taylor.dropped_parts(_foldable()) == []


@pytest.mark.parametrize("code", ["elegant", "gdf", "bmad"])
def test_other_codes_get_the_longitudinal_and_dipole_parts(tmp_path, code):
    (tmp_path / "src").mkdir()
    wake = FieldMap(_table_file(tmp_path / "src" / "w.dat"), field_type="TaylorWake")
    z, wakes = taylor.to_3d_wake(_components())
    assert np.array_equal(wake.z.value.val, z) and np.array_equal(wake.Wx.value.val, wakes["Wx"])
    with pytest.warns(UserWarning, match="component 11"):
        assert wake.write_field_file(code=code)
    assert wake.field_type == "TaylorWake"


def test_a_wakefield_element_keeps_it_for_astra_and_folds_it_for_elegant(tmp_path):
    (tmp_path / "src").mkdir()
    path = FieldMap(_table_file(tmp_path / "src" / "w.dat"), field_type="TaylorWake").write_field_file(
        code="hdf5")
    element = Wakefield(name="W", machine_area="S", physical={"length": 0.3, "middle": [0, 0, 1.0]},
                        cavity={"n_cells": 3, "cell_length": 0.1},
                        simulation={"wakefield_definition": path})
    run = tmp_path / "run"
    wake = translate_elements([element], directory=str(run))["W"]
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        astra = wake.to_astra()
    assert "Taylor_Method_F" in astra
    name = re.search(r"Wk_filename\(\d+\)\s*=\s*'([^']+)'", astra).group(1)
    assert np.array_equal(np.loadtxt(run / name), taylor.to_table(_components()))
    with pytest.warns(UserWarning, match="component 11"):
        elegant = wake.to_elegant()
    assert "rfcw" in elegant and 'wxcolumn = "Wx"' in elegant and 'wzcolumn = "Wz"' in elegant
