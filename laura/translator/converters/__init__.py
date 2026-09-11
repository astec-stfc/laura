import os
import yaml

try:
    _FastLoader = yaml.CSafeLoader
except AttributeError:
    _FastLoader = yaml.SafeLoader


class LazyDict(dict):
    """A dictionary that loads its content from a loader function on the first access."""

    def __init__(self, loader):
        self._loader = loader
        self._loaded = False

    def _ensure_loaded(self):
        if not self._loaded:
            data = self._loader()
            if data:
                self.update(data)
            self._loaded = True

    def __getitem__(self, key):
        self._ensure_loaded()
        return super().__getitem__(key)

    def __setitem__(self, key, value):
        self._ensure_loaded()
        super().__setitem__(key, value)

    def __contains__(self, key):
        self._ensure_loaded()
        return super().__contains__(key)

    def __len__(self):
        self._ensure_loaded()
        return super().__len__()

    def __iter__(self):
        self._ensure_loaded()
        return super().__iter__()

    def items(self):
        self._ensure_loaded()
        return super().items()

    def values(self):
        self._ensure_loaded()
        return super().values()

    def keys(self):
        self._ensure_loaded()
        return super().keys()

    def get(self, key, default=None):
        self._ensure_loaded()
        return super().get(key, default)

    def __or__(self, other):
        self._ensure_loaded()
        if isinstance(other, LazyDict):
            other._ensure_loaded()
        return super().__or__(other)

    def __ror__(self, other):
        self._ensure_loaded()
        return super().__ror__(other)

    def __repr__(self):
        if not self._loaded:
            return f"LazyDict(loaded=False, loader={self._loader})"
        return super().__repr__()


def _load_yaml_file(filename):
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
    with open(path, "r") as f:
        return yaml.load(f, Loader=_FastLoader)


type_conversion_rules = LazyDict(
    lambda: _load_yaml_file("../conversion_rules/types/type_conversion_rules.yaml")
)
type_conversion_rules_elegant = LazyDict(lambda: type_conversion_rules["elegant"])
type_conversion_rules_genesis = LazyDict(lambda: type_conversion_rules["genesis"])
type_conversion_rules_opal = LazyDict(lambda: type_conversion_rules["opal"])
type_conversion_rules_madx = LazyDict(lambda: type_conversion_rules["madx"])
type_conversion_rules_names = LazyDict(lambda: type_conversion_rules["name"])
type_conversion_rules_aliases = LazyDict(
    lambda: type_conversion_rules["aliases"]["elegant"]
)

keyword_conversion_rules_elegant = LazyDict(
    lambda: _load_yaml_file(
        "../conversion_rules/keywords/keyword_conversion_rules_elegant.yaml"
    )
)
elements_elegant = LazyDict(
    lambda: _load_yaml_file("../conversion_rules/elements/elements_elegant.yaml")
)

keyword_conversion_rules_ocelot = LazyDict(
    lambda: _load_yaml_file(
        "../conversion_rules/keywords/keyword_conversion_rules_ocelot.yaml"
    )
)
elements_ocelot = LazyDict(
    lambda: _load_yaml_file("../conversion_rules/elements/elements_ocelot.yaml")
)

keyword_conversion_rules_cheetah = LazyDict(
    lambda: _load_yaml_file(
        "../conversion_rules/keywords/keyword_conversion_rules_cheetah.yaml"
    )
)
elements_cheetah = LazyDict(
    lambda: _load_yaml_file("../conversion_rules/elements/elements_cheetah.yaml")
)

elements_opal = LazyDict(
    lambda: _load_yaml_file("../conversion_rules/elements/elements_opal.yaml")
)
keyword_conversion_rules_opal = LazyDict(
    lambda: _load_yaml_file(
        "../conversion_rules/keywords/keyword_conversion_rules_opal.yaml"
    )
)

keyword_conversion_rules_xsuite = LazyDict(
    lambda: _load_yaml_file(
        "../conversion_rules/keywords/keyword_conversion_rules_Xsuite.yaml"
    )
)
keyword_conversion_rules_wake_t = LazyDict(
    lambda: _load_yaml_file(
        "../conversion_rules/keywords/keyword_conversion_rules_wake_t.yaml"
    )
)
keyword_conversion_rules_genesis = LazyDict(
    lambda: _load_yaml_file(
        "../conversion_rules/keywords/keyword_conversion_rules_genesis.yaml"
    )
)
elements_genesis = LazyDict(
    lambda: _load_yaml_file("../conversion_rules/elements/elements_genesis.yaml")
)
element_keywords = LazyDict(
    lambda: _load_yaml_file("../conversion_rules/elements/element_keywords.yaml")
)

keyword_conversion_rules_madx = LazyDict(
    lambda: _load_yaml_file(
        "../conversion_rules/keywords/keyword_conversion_rules_madx.yaml"
    )
)
elements_madx = LazyDict(
    lambda: _load_yaml_file("../conversion_rules/elements/elements_madx.yaml")
)

# ---------------------------------------------------------------------------
# Backwards compatibility: names renamed for PEP 8. Served lazily with a
# DeprecationWarning so downstream consumers (astec-stfc/simba) keep working.
# ---------------------------------------------------------------------------
from laura._compat import deprecated_aliases  # noqa: E402

__getattr__ = deprecated_aliases(
    __name__,
    globals(),
    {
        "elements_Cheetah": "elements_cheetah",
        "elements_Elegant": "elements_elegant",
        "elements_Genesis": "elements_genesis",
        "elements_Madx": "elements_madx",
        "elements_Ocelot": "elements_ocelot",
        "elements_Opal": "elements_opal",
        "type_conversion_rules_Elegant": "type_conversion_rules_elegant",
        "type_conversion_rules_Genesis": "type_conversion_rules_genesis",
        "type_conversion_rules_Madx": "type_conversion_rules_madx",
        "type_conversion_rules_Names": "type_conversion_rules_names",
        "type_conversion_rules_Opal": "type_conversion_rules_opal",
    },
)
