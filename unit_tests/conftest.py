import pytest

from laura.models.base_models import set_functional_definitions, set_resolve_functional


@pytest.fixture(autouse=True)
def _reset_functionals():
    """Functional definitions and the resolve flag are module globals; start and end every test clean."""
    set_functional_definitions({}, merge=False)
    set_resolve_functional(False)
    yield
    set_functional_definitions({}, merge=False)
    set_resolve_functional(False)
