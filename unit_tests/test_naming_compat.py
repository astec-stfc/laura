"""
Backwards-compatibility guards for the PEP 8 naming migration.

Python class names are migrating to CapWords (``Beam_Position_Monitor`` ->
``BeamPositionMonitor``). The ``hardware_type`` values those classes carry are
*not* migrating: they are written into every saved lattice YAML and they key
:data:`ELEMENT_REGISTRY`, so changing them would invalidate existing files and
break consumers reading them.

These tests pin that separation, so a future rename cannot quietly change
on-disk layout or the wire format.

Warnings are FutureWarning rather than DeprecationWarning: Python only displays
a DeprecationWarning raised from ``__main__``, so simba calling a legacy name
from its own library code would have seen nothing.
"""

import pytest

from laura.models.element import ELEMENT_REGISTRY, _identifies_same_type


def _pep8(name: str) -> str:
    """The CapWords form a legacy underscored class name migrates to."""
    return name.replace("_", "")


class TestIdentifiesSameType:
    def test_exact_match(self):
        assert _identifies_same_type("Quadrupole", "Quadrupole")

    def test_underscored_legacy_value_matches_renamed_class(self):
        assert _identifies_same_type("BeamPositionMonitor", "Beam_Position_Monitor")

    def test_still_matches_before_the_rename(self):
        assert _identifies_same_type("Beam_Position_Monitor", "Beam_Position_Monitor")

    def test_genuinely_different_types_do_not_match(self):
        assert not _identifies_same_type("Quadrupole", "Sextupole")
        assert not _identifies_same_type("BeamPositionMonitor", "BeamArrivalMonitor")

    def test_comparison_is_case_sensitive(self):
        # Loosening to case-insensitive would collapse genuinely distinct
        # names; underscores are the only difference the rename introduces.
        assert not _identifies_same_type("beampositionmonitor", "Beam_Position_Monitor")


@pytest.mark.parametrize("hardware_type", sorted(ELEMENT_REGISTRY))
def test_registry_key_is_the_wire_value_not_the_class_name(hardware_type):
    """
    ELEMENT_REGISTRY must stay keyed by ``hardware_type``.

    Saved YAML dispatches through this mapping, so it has to keep resolving the
    legacy value regardless of what the Python class is called.
    """
    cls = ELEMENT_REGISTRY[hardware_type]
    assert cls.model_fields["hardware_type"].default == hardware_type


@pytest.mark.parametrize("hardware_type", sorted(ELEMENT_REGISTRY))
def test_rename_would_not_change_subdirectory(hardware_type):
    """
    ``subdirectory`` branches on class name vs ``hardware_type``. Renaming the
    class must not flip that branch, which would insert an extra path segment
    and move every element's file on disk.
    """
    cls = ELEMENT_REGISTRY[hardware_type]
    assert _identifies_same_type(cls.__name__, hardware_type), (
        f"{cls.__name__} does not currently identify as '{hardware_type}'"
    )
    assert _identifies_same_type(_pep8(cls.__name__), hardware_type), (
        f"renaming {cls.__name__} to {_pep8(cls.__name__)} would change the "
        f"on-disk path for '{hardware_type}'"
    )


def test_underscored_class_names_are_the_expected_set():
    """
    Tracks which classes the rename still has to cover. Shrink this set as
    classes are renamed; it should never grow.
    """
    remaining = {
        cls.__name__ for cls in ELEMENT_REGISTRY.values() if "_" in cls.__name__
    }
    assert remaining == set(), (
        "ELEMENT_REGISTRY still contains underscored class names: " + repr(remaining)
    )


class TestDeprecatedAliases:
    """
    Every legacy name must still resolve, and must warn.

    simba (astec-stfc/simba) imports laura internals directly and has not been
    migrated yet, so these aliases are load-bearing, not decorative.
    """

    @staticmethod
    def _import_all():
        """Import the modules that register aliases, so LAURA_RENAMES is full."""
        import importlib

        for mod in (
            "laura.translator.converters.codes.astra",
            "laura.translator.converters.codes.csrtrack",
            "laura.translator.converters.codes.gpt",
            # "laura.translator.converters.codes.ocelot",
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
        import warnings
        from laura._compat import LAURA_RENAMES

        self._import_all()
        assert LAURA_RENAMES, "no modules registered aliases"

        checked = 0
        for module_name, aliases in LAURA_RENAMES.items():
            module = importlib.import_module(module_name)
            for legacy, current in aliases.items():
                with warnings.catch_warnings(record=True) as caught:
                    warnings.simplefilter("always")
                    obj = getattr(module, legacy)
                assert obj is getattr(module, current), (
                    f"{module_name}.{legacy} does not resolve to {current}"
                )
                assert any(
                    issubclass(c.category, FutureWarning) for c in caught
                ), f"{module_name}.{legacy} resolved without a FutureWarning"
                checked += 1
        assert checked >= 44, f"expected the full alias surface, checked {checked}"

    def test_unknown_attribute_still_raises(self):
        from laura.translator.converters.codes import astra

        with pytest.raises(AttributeError):
            astra.definitely_not_a_real_name

    def test_simba_facing_field_imports(self):
        """simba imports laura.translator.utils.fields; pin that surface."""
        import warnings
        from laura.translator.utils import fields

        with warnings.catch_warnings():
            warnings.simplefilter("ignore", FutureWarning)
            assert fields.field is fields.FieldMap
            assert fields.hdf5.read_HDF5_field_file is fields.hdf5.read_hdf5_field_file
            assert fields.sdds.write_SDDS_field_file is fields.sdds.write_sdds_field_file

    def test_renamed_methods_still_reachable(self):
        import warnings
        from laura.translator.converters.codes.astra import AstraHeader

        h = AstraHeader(name="n", type="t", header="&NEWRUN")
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            assert h.write_ASTRA.__name__ == "write_astra"
        assert any(issubclass(c.category, FutureWarning) for c in caught)


class TestConverterAliases:
    """Round 2: laura/translator/converters/ private methods and re-exports."""

    def test_converter_reexports_still_resolve(self):
        import warnings
        from laura.translator import converters

        legacy = {
            "elements_Elegant": "elements_elegant",
            # "elements_Ocelot": "elements_ocelot",
            "type_conversion_rules_Madx": "type_conversion_rules_madx",
            "type_conversion_rules_Names": "type_conversion_rules_names",
        }
        for old, new in legacy.items():
            with warnings.catch_warnings(record=True) as caught:
                warnings.simplefilter("always")
                assert getattr(converters, old) is getattr(converters, new)
            assert any(issubclass(c.category, FutureWarning) for c in caught)

    def test_private_methods_reachable_under_old_names(self):
        import warnings
        from laura.translator.converters.base import BaseElementTranslator

        aliases = BaseElementTranslator._DEPRECATED_METHOD_ALIASES
        assert "_write_ASTRA_dictionary" in aliases
        assert "_convertKeyword_Elegant" in aliases

        # The alias map lives on the shared root, but the methods themselves are
        # spread across subclasses -- `_write_astra` is WakefieldTranslator's,
        # `_write_astra_dipole` is MagnetTranslator's. Resolution happens per
        # instance via getattr(self, current), so the target only has to exist
        # somewhere in the translator hierarchy.
        #
        # __subclasses__() only reports classes that have been imported, so the
        # modules defining them have to be loaded first or this passes vacuously.
        import importlib

        for mod in ("aperture", "cavity", "diagnostic", "drift", "laser",
                    "magnet", "plasma", "twiss", "wake"):
            importlib.import_module(f"laura.translator.converters.{mod}")

        def _subclasses(cls):
            for sub in cls.__subclasses__():
                yield sub
                yield from _subclasses(sub)

        owners = [BaseElementTranslator, *_subclasses(BaseElementTranslator)]
        for legacy, current in aliases.items():
            assert any(current in vars(c) for c in owners), (
                f"{legacy} is aliased to {current}, which no translator defines"
            )

    def test_subclass_overriding_a_legacy_name_is_warned_about(self):
        """
        An alias cannot save a downstream override: laura calls the new name, so
        a subclass still defining the old one is silently skipped. The base class
        warns instead.
        """
        import warnings
        from laura.translator.converters.base import BaseElementTranslator

        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")

            class LegacyOverride(BaseElementTranslator):
                # Deliberately the OLD name -- this is the trap being detected.
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

    def test_notation_arguments_were_not_renamed(self):
        """
        Brho and P_Q are notation *and* public keyword arguments. Renaming them
        would break every `to_rftrack(P_Q=...)` call site.
        """
        import inspect
        from laura.translator.converters.model import MachineModelTranslator

        assert "P_Q" in inspect.signature(MachineModelTranslator.to_rftrack).parameters


class TestLegacyModulePaths:
    """
    Round 4: module and package paths moved to lower_snake_case.

    Served by a meta-path finder rather than shim files, because the old and new
    names differ only in case -- `laura/models/RF.py` and `laura/models/rf.py`
    are the same file on macOS and Windows, so a shim would overwrite what it
    shims. See laura/_legacy.py.
    """

    def test_no_two_source_files_differ_only_by_case(self):
        """
        The property that made shim files impossible. Guards against anyone
        reintroducing a case-only pair, which would be silently broken on a
        case-insensitive filesystem.
        """
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
        # Identity, not just equality: isinstance/issubclass against classes
        # reached through either path must agree.
        assert old_mod is new_mod

    def test_legacy_import_warns(self):
        import importlib
        import sys
        import warnings

        # force a fresh resolution so the finder actually runs
        sys.modules.pop("laura.models.elementList", None)
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            importlib.import_module("laura.models.elementList")
        assert any(issubclass(c.category, FutureWarning) for c in caught), [
            str(c.message) for c in caught
        ]

    def test_importing_laura_alone_warns_about_nothing(self):
        """The finder must be lazy: no legacy path used, no warning."""
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
