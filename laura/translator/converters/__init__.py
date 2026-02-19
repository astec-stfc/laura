import os
import yaml

try:
    _FastLoader = yaml.CSafeLoader
except AttributeError:
    _FastLoader = yaml.SafeLoader

with open(
    os.path.dirname(os.path.abspath(__file__))
    + "/../conversion_rules/types/type_conversion_rules.yaml",
    "r",
) as infile:
    type_conversion_rules = yaml.load(infile, Loader=_FastLoader)
    type_conversion_rules_Elegant = type_conversion_rules["elegant"]
    type_conversion_rules_Genesis = type_conversion_rules["genesis"]
    type_conversion_rules_Opal = type_conversion_rules["opal"]
    type_conversion_rules_Names = type_conversion_rules["name"]
    type_conversion_rules_aliases = type_conversion_rules["aliases"]["elegant"]

with open(
    os.path.dirname(os.path.abspath(__file__))
    + "/../conversion_rules/keywords/keyword_conversion_rules_elegant.yaml",
    "r",
) as infile:
    keyword_conversion_rules_elegant = yaml.load(infile, Loader=_FastLoader)

with open(
    os.path.dirname(os.path.abspath(__file__))
    + "/../conversion_rules/elements/elements_elegant.yaml",
    "r",
) as infile:
    elements_Elegant = yaml.load(infile, Loader=_FastLoader)

with open(
    os.path.dirname(os.path.abspath(__file__))
    + "/../conversion_rules/keywords/keyword_conversion_rules_ocelot.yaml",
    "r",
) as infile:
    keyword_conversion_rules_ocelot = yaml.load(infile, Loader=_FastLoader)

with open(
    os.path.dirname(os.path.abspath(__file__))
    + "/../conversion_rules/elements/elements_ocelot.yaml",
    "r",
) as infile:
    elements_Ocelot = yaml.load(infile, Loader=_FastLoader)

with open(
    os.path.dirname(os.path.abspath(__file__))
    + "/../conversion_rules/keywords/keyword_conversion_rules_cheetah.yaml",
    "r",
) as infile:
    keyword_conversion_rules_cheetah = yaml.load(infile, Loader=_FastLoader)

with open(
    os.path.dirname(os.path.abspath(__file__))
    + "/../conversion_rules/elements/elements_cheetah.yaml",
    "r",
) as infile:
    elements_Cheetah = yaml.load(infile, Loader=_FastLoader)

with open(
    os.path.dirname(os.path.abspath(__file__))
    + "/../conversion_rules/elements/elements_opal.yaml",
    "r",
) as infile:
    elements_Opal = yaml.load(infile, Loader=_FastLoader)

with open(
    os.path.dirname(os.path.abspath(__file__))
    + "/../conversion_rules/keywords/keyword_conversion_rules_opal.yaml",
    "r",
) as infile:
    keyword_conversion_rules_opal = yaml.load(infile, Loader=_FastLoader)

with open(
    os.path.dirname(os.path.abspath(__file__))
    + "/../conversion_rules/keywords/keyword_conversion_rules_Xsuite.yaml",
    "r",
) as infile:
    keyword_conversion_rules_xsuite = yaml.load(infile, Loader=_FastLoader)

with open(
    os.path.dirname(os.path.abspath(__file__))
    + "/../conversion_rules/keywords/keyword_conversion_rules_wake_t.yaml",
    "r",
) as infile:
    keyword_conversion_rules_wake_t = yaml.load(infile, Loader=_FastLoader)

with open(
    os.path.dirname(os.path.abspath(__file__))
    + "/../conversion_rules/keywords/keyword_conversion_rules_genesis.yaml",
    "r",
) as infile:
    keyword_conversion_rules_genesis = yaml.load(infile, Loader=_FastLoader)

with open(
    os.path.dirname(os.path.abspath(__file__))
    + "/../conversion_rules/elements/elements_genesis.yaml",
    "r",
) as infile:
    elements_Genesis = yaml.load(infile, Loader=_FastLoader)

with open(
    os.path.dirname(os.path.abspath(__file__))
    + "/../conversion_rules/elements/element_keywords.yaml",
    "r",
) as infile:
    element_keywords = yaml.load(infile, Loader=_FastLoader)
