"""Dependency-free checks for the common lattice-importer contract."""

import ast
from pathlib import Path


CODE_DIR = Path(__file__).parents[1] / "laura" / "translator" / "converters" / "codes"
IMPORTERS = {
    "bmad.py": "BmadLatticeImporter",
    "elegant.py": "ElegantLatticeImporter",
    "madx.py": "MadxLatticeImporter",
    "ocelot.py": "OcelotLatticeImporter",
    "xsuite.py": "XsuiteLatticeImporter",
}
REQUIRED_METHODS = {
    "create_element_dictionary",
    "create_laura_element_dictionary",
    "create_section",
    "create_layout",
    "export_yaml",
}


def _class(filename, classname):
    tree = ast.parse((CODE_DIR / filename).read_text())
    return next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == classname)


def _methods(importer):
    """``{name: FunctionDef}`` for *importer*, including a ``LatticeImporter`` base."""
    bodies = [importer.body]
    if any(getattr(base, "id", None) == "LatticeImporter" for base in importer.bases):
        bodies.insert(0, _class("importer.py", "LatticeImporter").body)
    return {
        node.name: node
        for body in bodies
        for node in body
        if isinstance(node, ast.FunctionDef)
    }


def test_importers_share_the_same_lifecycle():
    for filename, classname in IMPORTERS.items():
        methods = _methods(_class(filename, classname))
        assert REQUIRED_METHODS <= set(methods)
        assert ast.unparse(methods["create_layout"].returns) == "MachineLayout"


def test_ocelot_type_collisions_have_explicit_generic_winners():
    tree = ast.parse((CODE_DIR / "ocelot.py").read_text())
    switch_node = next(
        node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "_switch_dict"
    )
    namespace = {"Dict": dict}
    exec(compile(ast.Module([switch_node], []), "ocelot.py", "exec"), namespace)
    marker = type("Marker", (), {})
    switch = namespace["_switch_dict"]({"Screen": marker, "Marker": marker})
    assert switch["marker"] == "Marker"


if __name__ == "__main__":
    test_importers_share_the_same_lifecycle()
    test_ocelot_type_collisions_have_explicit_generic_winners()
