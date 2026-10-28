"""Memoised keywords: a type settled at write time still gets its own keywords."""

import pytest

from laura.models.element import Dipole, Drift
from laura.translator.converters import base
from laura.translator.converters.converter import translate_elements

DRIFTS = [(False, False), (False, True), (True, False), (True, True)]


def drift(csr, lsc):
    element = Drift(
        name="D1", hardware_class="Drift", machine_area="A",
        physical={"length": 1.0, "middle": {"x": 0.0, "y": 0.0, "z": 0.5}},
        simulation={"csr_enable": csr, "lsc_enable": lsc},
    )
    return translate_elements([element])["D1"]


def bend(csr):
    element = Dipole(
        name="B1", machine_area="A", physical={"length": 1.3},
        magnetic={"magnetic_length": 1.3, "k0l": 0.11, "k1l": -0.9},
        simulation={"csr_enable": csr},
    )
    return translate_elements([element])["B1"]


def unmemoised(make, code="to_elegant"):
    """What ``make()`` writes with nothing memoised beforehand."""
    saved = {key: dict(memo) for key, memo in base._KEYWORD_MEMO.items()}
    try:
        for memo in base._KEYWORD_MEMO.values():
            memo.clear()
        return getattr(make(), code)()
    finally:
        for key, memo in base._KEYWORD_MEMO.items():
            memo.clear()
            memo.update(saved.get(key, {}))


@pytest.mark.parametrize("csr, lsc", DRIFTS)
def test_each_drift_flavour_writes_its_own_keywords(csr, lsc):
    expected = unmemoised(lambda: drift(csr, lsc))
    for other in DRIFTS:
        drift(*other).to_elegant()
    assert drift(csr, lsc).to_elegant() == expected


@pytest.mark.parametrize("csr", [False, True])
def test_a_bend_writes_its_own_keywords_with_csr_on_or_off(csr):
    expected = unmemoised(lambda: bend(csr))
    bend(not csr).to_elegant()
    assert bend(csr).to_elegant() == expected


def test_the_flavours_really_differ():
    """Guards the tests above."""
    written = {unmemoised(lambda: drift(*flags)).split(",")[0] for flags in DRIFTS}
    assert written == {"D1: drift", "D1: lscdrift", "D1: csrdrift"}


def test_elements_of_a_type_share_one_rules_set():
    """What makes the memo pay: the second element's rules are the first's."""
    assert drift(False, False).conversion_rules["elegant"] is drift(
        True, False
    ).conversion_rules["elegant"]


def test_madx_is_unchanged_by_the_memo():
    expected = unmemoised(lambda: bend(False), "to_madx")
    bend(True).to_madx()
    assert bend(False).to_madx() == expected
