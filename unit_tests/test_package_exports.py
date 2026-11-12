import importlib

import pytest

import laura.models
import laura.models.element as element

PACKAGES = ["laura.translator", "laura.models", "laura.importers", "laura.exporters"]


@pytest.mark.parametrize("package", PACKAGES)
def test_every_export_resolves(package):
    module = importlib.import_module(package)
    for name in module.__all__:
        assert getattr(module, name) is not None, f"{package}.{name}"
        assert name in dir(module)


def test_every_element_class_is_exposed():
    for cls in element.ELEMENT_REGISTRY.values():
        assert getattr(laura.models, cls.__name__) is cls


def test_models_does_not_leak_element_imports():
    with pytest.raises(AttributeError):
        laura.models.CascadingAccessMixin  # imported into element, not defined there


def test_sql_export_machine_is_renamed():
    from laura.exporters import export_machine, export_machine_sql
    from laura.exporters import sql_exporter, yaml_exporter

    assert export_machine is yaml_exporter.export_machine
    assert export_machine_sql is sql_exporter.export_machine
