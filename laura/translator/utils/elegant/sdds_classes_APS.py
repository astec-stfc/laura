import re
from itertools import groupby
import numpy as np
from warnings import warn

try:
    from counter import Counter
except ImportError:
    from ..functions import Counter
from ..functions import chop, introspect_model_defaults
from .SDDSFile import SDDSFile
from ...converters import (
    type_conversion_rules_aliases,
    type_conversion_rules_Elegant,
    keyword_conversion_rules_elegant,
    element_keywords,
)
import laura.models.element as LAURA_elements


class SDDS_Floor:

    duplicates: list = []

    lattice_name: str = None
    """Best-effort lattice/beamline name, parsed from ELEGANT's own
    ``&floor_coordinates`` description string (``"...lattice: Linac.lte"``).
    ``None`` if the description doesn't match that format (e.g. a
    hand-written description, or an ASCII SDDS file without one)."""

    sdds_position_columns = [
        "ElementName",
        "X",
        "Y",
        "Z",
    ]

    sdds_angle_columns = [
        "ElementName",
        "phi",
        "psi",
        "theta",
    ]

    sdds_s_columns = [
        "ElementName",
        "s",
    ]

    def __init__(self, filename: str = None, page: int = 0, prefix: str = "."):
        [
            setattr(self, c, [])
            for c in (self.sdds_position_columns + self.sdds_angle_columns)
        ]
        self.prefix = prefix
        self.counter = Counter()
        if filename is not None:
            self.floor_data = self.import_sdds_floor_file(filename, page)

    def get_duplicate_element_names(self) -> list:
        return [k for k, g in groupby(sorted(self.ElementName)) if len(list(g)) > 1]

    def number_element(self, elem):
        if elem not in self.duplicates:
            return elem
        no = self.counter.counter(elem)
        self.counter.add(elem)
        return elem + self.prefix + str(no)

    def import_sdds_floor_file(self, filename: str, page: int = 0, index=1) -> list:
        elegantObject = SDDSFile(index=index)
        elegantObject.read_file(filename, page=page)
        elegantData = elegantObject.data
        match = re.search(r"lattice:\s*(\S+?)(?:\.lte)?\s*$", elegantObject.description)
        self.lattice_name = match.group(1) if match else None
        has_s = "s" in elegantData
        columns = self.sdds_position_columns + self.sdds_angle_columns
        if has_s:
            columns = columns + ["s"]
        for a in columns:
            if np.array(elegantData[a]).ndim > 1:
                setattr(self, a, elegantData[a][page])
            else:
                setattr(self, a, elegantData[a])
        self.counter = Counter()
        self.duplicates = self.get_duplicate_element_names()
        self.ElementName = [self.number_element(e) for e in self.ElementName]
        # print(self.ElementName)
        # exit()
        rawpositiondata = {
            e: list(map(float, chop([x, y, z], 1e-12)))
            for e, x, y, z in list(
                zip(*[getattr(self, a) for a in self.sdds_position_columns])
            )
        }
        rawangledata = {
            e: list(map(float, chop([phi, psi, theta], 1e-12)))
            for e, phi, psi, theta in list(
                zip(*[getattr(self, a) for a in self.sdds_angle_columns])
            )
        }
        self.data = {
            e: {"end": rawpositiondata[e], "end_rotation": rawangledata[e]}
            for e in self.ElementName
        }
        if has_s:
            rawsdata = dict(zip(self.ElementName, map(float, self.s)))
            for e in self.ElementName:
                self.data[e]["s"] = rawsdata[e]

    def __getitem__(self, key):
        if key in self.data:
            return self.data[key]
        print(f"{key} missing!")


class SDDS_Params:

    def __init__(self, filename: str, page: int = 0):
        self.filename = filename
        self.page = page
        self.elegantObject = None
        self.elegantData = None
        self.elegantParams = None

    def import_sdds_params_file(self, index=1) -> None:
        self.elegantObject = SDDSFile(index=index)
        self.elegantObject.read_file(self.filename, page=self.page)
        self.elegantData = self.elegantObject.data

    def join_params(self) -> None:
        if not self.elegantData:
            self.import_sdds_params_file()
        max_occurrence = {}
        for name, occ in zip(
            self.elegantData["ElementName"], self.elegantData["ElementOccurence"]
        ):
            max_occurrence[name] = max(max_occurrence.get(name, 1), occ)

        self.elegantParams = {}
        for i, k in enumerate(self.elegantData["ElementName"]):
            occurrence = self.elegantData["ElementOccurence"][i]
            key = f"{k}.{occurrence}" if max_occurrence[k] > 1 else k
            if key not in self.elegantParams:
                self.elegantParams.update(
                    {key: {param: [] for param in list(self.elegantData.keys())[1:]}}
                )
            for val in list(self.elegantData.keys())[1:]:
                if self.elegantData["ElementName"][i] == k:
                    self.elegantParams[key][val].append(self.elegantData[val][i])

    def create_element_dictionary(self) -> tuple:
        if not self.elegantParams:
            self.join_params()
        sfconvert = {}
        # disallowed = ["bore", "zwakefile"]
        filenames = {}
        sfconvert = {}
        for k, v in self.elegantParams.items():
            elemtype = v["ElementType"][0].lower()
            if elemtype in element_keywords and "drift" not in elemtype:
                sfconvert.update(
                    {
                        k: {
                            "hardware_type": elemtype,
                            "name": k,
                            "machine_area": "test",
                        }
                    }
                )
            elif elemtype in list(type_conversion_rules_Elegant.values()):
                switch_dict = {y: x for x, y in type_conversion_rules_Elegant.items()}
                sfconvert.update(
                    {
                        k: {
                            "hardware_type": switch_dict[elemtype],
                            "name": k,
                            "machine_area": "test",
                        }
                    }
                )
            else:
                found = False
                for sf, aliases in type_conversion_rules_aliases.items():
                    if elemtype in aliases:
                        sfconvert.update(
                            {
                                k: {
                                    "hardware_type": sf,
                                    "name": k,
                                    "machine_area": "test",
                                }
                            }
                        )
                        found = True
                if not found:
                    warn(
                        f"Could not parse ELEGANT element type {elemtype} for {k}; setting as drift."
                    )
                    sfconvert.update(
                        {
                            k: {
                                "hardware_type": "Drift",
                                "name": k,
                                "hardware_class": "Drift",
                                "machine_area": "test",
                            }
                        }
                    )
            sftype = sfconvert[k]["hardware_type"]
            try:
                if sftype == "kicker":
                    model_fields = introspect_model_defaults(
                        getattr(LAURA_elements, "Combined_Corrector"),
                        resolve_optional=True,
                    )
                    sfconvert[k]["hardware_type"] = "Combined_Corrector"
                elif "Cavity" not in sftype:
                    classname = (
                        sftype if hasattr(LAURA_elements, sftype) else sftype.capitalize()
                    )
                    model_fields = introspect_model_defaults(
                        getattr(LAURA_elements, classname),
                        resolve_optional=True,
                    )
                    sfconvert[k]["hardware_type"] = classname
                else:
                    model_fields = introspect_model_defaults(
                        getattr(LAURA_elements, sftype),
                        resolve_optional=True,
                    )
            except AttributeError:
                print(f"type {sftype} not recognized")
                sfconvert.update(
                    {
                        k: {
                            "hardware_type": "Drift",
                            "name": k,
                            "hardware_class": "Drift",
                            "machine_area": "test",
                        }
                    }
                )
                continue
            for subk in ["magnetic", "cavity", "simulation", "diagnostic", "physical", "aperture"]:
                if subk in model_fields:
                    sfconvert[k].update({subk: {}})
            if sfconvert[k]["hardware_type"] == "Drift":
                continue
            for i, param in enumerate(v["ElementParameter"]):
                param = param.lower()
                merged = keyword_conversion_rules_elegant["general"]
                if sftype.lower() in keyword_conversion_rules_elegant:
                    merged = (
                        keyword_conversion_rules_elegant[sftype.lower()]
                        | keyword_conversion_rules_elegant["general"]
                    )
                kwele = {y: x for x, y in merged.items()}
                for subk in model_fields:
                    val = (
                        v["ParameterValueString"][i]
                        if len(v["ParameterValueString"][i]) > 0
                        else v["ParameterValue"][i]
                    )
                    if isinstance(model_fields[subk], dict):
                        if param in ["k1", "k2", "k3", "angle", "l"]:
                            sfconvert[k].update({param: v["ParameterValue"][i]})
                        if param in model_fields[subk]:
                            if val:
                                sfconvert[k][subk].update({param: val})
                        elif param in kwele:
                            if kwele[param] in model_fields[subk]:
                                if (
                                    not isinstance(
                                        model_fields[subk][kwele[param]], str
                                    )
                                    or model_fields[subk][kwele[param]]
                                ):
                                    sfconvert[k][subk].update({kwele[param]: val})
                if "file" in param and v["ParameterValueString"][i]:
                    filenames.update({k: {param: v["ParameterValueString"][i]}})
                    warn(
                        f"Apparent filename found for element {k}: "
                        f"{param} = {v['ParameterValueString'][i]}; "
                        f"check path, file format and column data"
                    )
        return sfconvert, filenames
