"""PEP 8 rename guards: class names change, on-disk ``hardware_type`` values don't.

FutureWarning, not DeprecationWarning: the latter is hidden outside ``__main__``.
"""

import pytest

from laura.models.element import ELEMENT_REGISTRY, _identifies_same_type


def _pep8(name: str) -> str:
    return name.replace("_", "")


def _subclasses(cls):
    for sub in cls.__subclasses__():
        yield sub
        yield from _subclasses(sub)


def _import_translators():
    """``__subclasses__()`` only reports imported classes."""
    import importlib

    for mod in ("aperture", "cavity", "diagnostic", "drift", "laser",
                "magnet", "plasma", "twiss", "wake"):
        importlib.import_module(f"laura.translator.converters.{mod}")


class TestIdentifiesSameType:
    @pytest.mark.parametrize(
        "a, b",
        [
            ("Quadrupole", "Quadrupole"),
            ("BeamPositionMonitor", "Beam_Position_Monitor"),
            ("Beam_Position_Monitor", "Beam_Position_Monitor"),
        ],
        ids=["exact", "renamed", "before-rename"],
    )
    def test_match(self, a, b):
        assert _identifies_same_type(a, b)

    # Only underscores may differ; case-insensitive would collapse distinct names.
    @pytest.mark.parametrize(
        "a, b",
        [
            ("Quadrupole", "Sextupole"),
            ("BeamPositionMonitor", "BeamArrivalMonitor"),
            ("beampositionmonitor", "Beam_Position_Monitor"),
        ],
        ids=["different", "different-monitor", "case-sensitive"],
    )
    def test_no_match(self, a, b):
        assert not _identifies_same_type(a, b)


@pytest.mark.parametrize("hardware_type", sorted(ELEMENT_REGISTRY))
def test_registry_key_is_the_wire_value_not_the_class_name(hardware_type):
    """Saved YAML dispatches through ELEMENT_REGISTRY by ``hardware_type``."""
    cls = ELEMENT_REGISTRY[hardware_type]
    assert cls.model_fields["hardware_type"].default == hardware_type


@pytest.mark.parametrize("hardware_type", sorted(ELEMENT_REGISTRY))
def test_rename_would_not_change_subdirectory(hardware_type):
    """Flipping the class-name branch in ``subdirectory`` would move files."""
    cls = ELEMENT_REGISTRY[hardware_type]
    assert _identifies_same_type(cls.__name__, hardware_type), (
        f"{cls.__name__} does not currently identify as '{hardware_type}'"
    )
    assert _identifies_same_type(_pep8(cls.__name__), hardware_type), (
        f"renaming {cls.__name__} to {_pep8(cls.__name__)} would change the "
        f"on-disk path for '{hardware_type}'"
    )


def test_underscored_class_names_are_the_expected_set():
    remaining = {
        cls.__name__ for cls in ELEMENT_REGISTRY.values() if "_" in cls.__name__
    }
    assert remaining == set(), (
        "ELEMENT_REGISTRY still contains underscored class names: " + repr(remaining)
    )


class TestDeprecatedAliases:
    """simba imports laura internals directly, so these aliases are load-bearing."""

    @staticmethod
    def _import_all():
        import importlib

        for mod in (
            "laura.translator.converters.codes.astra",
            "laura.translator.converters.codes.csrtrack",
            "laura.translator.converters.codes.gpt",
            "laura.translator.converters.codes.ocelot",
            "laura.translator.converters.codes.opal",
            "laura.translator.utils.SDDSFile",
            "laura.translator.utils.elegant.sdds_classes_APS",
            "laura.translator.utils.fields",
            "laura.translator.utils.fields.hdf5",
            "laura.translator.utils.fields.sdds",
            "laura.translator.utils.functions",
        ):
            importlib.import_module(mod)

    def test_every_registered_alias_resolves(self):
        import importlib
        from laura._compat import LAURA_RENAMES

        self._import_all()
        assert LAURA_RENAMES, "no modules registered aliases"

        checked = 0
        for module_name, aliases in LAURA_RENAMES.items():
            module = importlib.import_module(module_name)
            for legacy, current in aliases.items():
                with pytest.warns(FutureWarning):
                    obj = getattr(module, legacy)
                assert obj is getattr(module, current), (
                    f"{module_name}.{legacy} does not resolve to {current}"
                )
                checked += 1
        assert checked >= 44, f"expected the full alias surface, checked {checked}"

    def test_unknown_attribute_still_raises(self):
        from laura.translator.converters.codes import astra

        with pytest.raises(AttributeError):
            astra.definitely_not_a_real_name

    def test_simba_facing_field_imports(self):
        import warnings
        from laura.translator.utils import fields

        with warnings.catch_warnings():
            warnings.simplefilter("ignore", FutureWarning)
            assert fields.field is fields.FieldMap
            assert fields.hdf5.read_HDF5_field_file is fields.hdf5.read_hdf5_field_file
            assert fields.sdds.write_SDDS_field_file is fields.sdds.write_sdds_field_file

    def test_renamed_methods_still_reachable(self):
        from laura.translator.converters.codes.astra import AstraHeader

        h = AstraHeader(name="n", type="t", header="&NEWRUN")
        with pytest.warns(FutureWarning):
            assert h.write_ASTRA.__name__ == "write_astra"


class TestConverterAliases:
    def test_converter_reexports_still_resolve(self):
        from laura.translator import converters

        legacy = {
            "elements_Elegant": "elements_elegant",
            "elements_Ocelot": "elements_ocelot",
            "type_conversion_rules_Madx": "type_conversion_rules_madx",
            "type_conversion_rules_Names": "type_conversion_rules_names",
        }
        for old, new in legacy.items():
            with pytest.warns(FutureWarning):
                assert getattr(converters, old) is getattr(converters, new)

    def test_private_methods_reachable_under_old_names(self):
        from laura.translator.converters.base import BaseElementTranslator

        aliases = BaseElementTranslator._DEPRECATED_METHOD_ALIASES
        assert "_write_ASTRA_dictionary" in aliases
        assert "_convertKeyword_Elegant" in aliases

        # targets resolve per instance, so any class in the hierarchy may own them
        _import_translators()

        owners = [BaseElementTranslator, *_subclasses(BaseElementTranslator)]
        for legacy, current in aliases.items():
            assert any(current in vars(c) for c in owners), (
                f"{legacy} is aliased to {current}, which no translator defines"
            )

    def test_subclass_overriding_a_legacy_name_is_warned_about(self):
        """laura calls the new name, so an old-name override is silently skipped."""
        import warnings
        from laura.translator.converters.base import BaseElementTranslator

        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")

            class LegacyOverride(BaseElementTranslator):
                def _write_ASTRA_dictionary(self, *args, **kwargs):
                    return "never called"

        messages = [
            str(w.message)
            for w in caught
            if issubclass(w.category, FutureWarning)
        ]
        assert any("_write_ASTRA_dictionary" in m for m in messages), messages

    def test_compliant_subclass_is_not_warned_about(self):
        import warnings
        from laura.translator.converters.base import BaseElementTranslator

        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")

            class ModernOverride(BaseElementTranslator):
                def _write_astra_dictionary(self, *args, **kwargs):
                    return "called fine"

        assert not [
            w for w in caught
            if issubclass(w.category, FutureWarning)
            and "renamed" in str(w.message)
        ]

    def test_namelist_keyword_maps_still_name_real_fields(self):
        """A stale key emits the python name, which ASTRA and OPAL reject."""
        import ast
        import inspect
        import textwrap
        from laura.translator.converters.codes import astra, opal

        def mapped_keys(cls, attr):
            """Read from source: some post-inits need fields a bare instance lacks."""
            src = textwrap.dedent(inspect.getsource(cls.model_post_init))
            return [
                key.value
                for node in ast.walk(ast.parse(src))
                if isinstance(node, ast.Assign) and isinstance(node.value, ast.Dict)
                for target in node.targets
                if isinstance(target, ast.Attribute) and target.attr == attr
                for key in node.value.keys
            ]

        checked = 0
        for base, attr in ((astra.AstraHeader, "astradict"),
                           (opal.OpalHeader, "opaldict")):
            for cls in [base, *_subclasses(base)]:
                if attr not in inspect.getsource(cls.model_post_init):
                    continue
                stale = sorted(set(mapped_keys(cls, attr)) - set(cls.model_fields))
                assert not stale, f"{cls.__name__}.{attr} names missing fields: {stale}"
                checked += 1
        assert checked > 4, f"only {checked} namelist maps found -- did they move?"

    def test_notation_arguments_were_not_renamed(self):
        """Brho and P_Q are public keyword arguments, not just notation."""
        import inspect
        from laura.translator.converters.model import MachineModelTranslator

        assert "P_Q" in inspect.signature(MachineModelTranslator.to_rftrack).parameters


class TestLegacyModulePaths:
    """Meta-path finder, not shims: case-only renames collide on macOS/Windows."""

    def test_no_two_source_files_differ_only_by_case(self):
        import collections
        import pathlib

        by_lower = collections.defaultdict(list)
        for p in pathlib.Path("laura").rglob("*.py"):
            if "__pycache__" in p.parts:
                continue
            by_lower[p.as_posix().lower()].append(p.as_posix())
        clashes = {k: v for k, v in by_lower.items() if len(v) > 1}
        assert not clashes, f"case-only filename clashes: {clashes}"

    def test_legacy_table_has_no_self_mapping(self):
        """A self-mapping entry would make the loader import itself forever."""
        from laura._legacy import LEGACY_MODULES

        assert not [k for k, v in LEGACY_MODULES.items() if k == v]

    @pytest.mark.parametrize(
        "legacy,current",
        [
            ("laura.models.RF", "laura.models.rf"),
            ("laura.models.baseModels", "laura.models.base_models"),
            ("laura.models.elementList", "laura.models.element_list"),
            ("laura.Exporters", "laura.exporters"),
            ("laura.Importers", "laura.importers"),
            ("laura.Exporters.YAML", "laura.exporters.yaml_exporter"),
            ("laura.Importers.YAML_Loader", "laura.importers.yaml_loader"),
            ("laura.translator.utils.SDDSFile", "laura.translator.utils.sdds_file"),
        ],
    )
    def test_legacy_path_resolves_to_the_same_module_object(self, legacy, current):
        import importlib
        import warnings

        with warnings.catch_warnings():
            warnings.simplefilter("ignore", FutureWarning)
            old_mod = importlib.import_module(legacy)
            new_mod = importlib.import_module(current)
        # identity, so isinstance agrees through either path
        assert old_mod is new_mod

    def test_legacy_import_warns(self):
        import importlib
        import sys

        sys.modules.pop("laura.models.elementList", None)
        with pytest.warns(FutureWarning):
            importlib.import_module("laura.models.elementList")

    def test_importing_laura_alone_warns_about_nothing(self):
        import subprocess
        import sys

        result = subprocess.run(
            [sys.executable, "-W", "error::FutureWarning", "-c", "import laura"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, result.stderr[-1500:]

    def test_unknown_module_still_raises(self):
        import importlib

        with pytest.raises(ModuleNotFoundError):
            importlib.import_module("laura.models.NotARealModule")


class TestLauraDoesNotUseItsOwnLegacyNames:
    """The aliases are for downstream callers only."""

    def test_no_module_imports_a_legacy_path(self):
        import importlib
        import pkgutil
        import warnings

        import laura

        offenders = []
        for mod in pkgutil.walk_packages(laura.__path__, "laura."):
            with warnings.catch_warnings(record=True) as caught:
                warnings.simplefilter("always", FutureWarning)
                try:
                    importlib.import_module(mod.name)
                except Exception:
                    continue  # optional simulation-code dependency
            offenders += [
                f"{w.filename}:{w.lineno}: {w.message}"
                for w in caught
                if issubclass(w.category, FutureWarning)
            ]
        assert not offenders, "laura imports its own legacy paths:\n" + "\n".join(offenders)

    def test_no_source_file_calls_a_legacy_method(self):
        import pathlib
        import re

        from laura._compat import DeprecatedMethodAliases

        _import_translators()

        legacy = set()
        for cls in [DeprecatedMethodAliases, *_subclasses(DeprecatedMethodAliases)]:
            legacy |= set(vars(cls).get("_DEPRECATED_METHOD_ALIASES", {}))
        assert legacy, "no method aliases registered"

        import laura

        pattern = re.compile(r"self\.(" + "|".join(sorted(map(re.escape, legacy))) + r")\b")
        root = pathlib.Path(laura.__path__[0])
        offenders = []
        for path in sorted(root.rglob("*.py")):
            for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                for match in pattern.finditer(line):
                    offenders.append(f"{path.relative_to(root)}:{i}: self.{match.group(1)}")
        assert not offenders, (
            "laura calls its own renamed methods (these resolve via __getattr__ "
            "only if the alias target exists, and warn every call):\n"
            + "\n".join(offenders)
        )
