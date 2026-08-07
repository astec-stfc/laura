from warnings import warn

from ..functions import introspect_model_defaults
from .SDDSFile import SDDSFile
from ...converters import (
    type_conversion_rules_aliases,
    type_conversion_rules_Elegant,
    keyword_conversion_rules_elegant,
    element_keywords,
)
import laura.models.element as LAURA_elements



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
            alias = next(
                (
                    sf
                    for sf, aliases in type_conversion_rules_aliases.items()
                    if elemtype in aliases
                ),
                None,
            )
            if alias:
                sfconvert.update(
                    {k: {"hardware_type": alias, "name": k, "machine_area": "test"}}
                )
            elif elemtype in element_keywords and "drift" not in elemtype:
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
                switch_dict.update(
                    {
                        "watch": "Beam_Position_Monitor",
                        "mark": "Marker",
                        "marker": "Marker",
                    }
                )
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
            if sftype == "Drift":
                sfconvert[k]["hardware_class"] = "Drift"
            try:
                if sftype == "kicker":
                    model_fields = introspect_model_defaults(
                        getattr(LAURA_elements, "Combined_Corrector"),
                        resolve_optional=True,
                    )
                    sfconvert[k]["hardware_type"] = "Combined_Corrector"
                elif "Cavity" not in sftype:
                    classname = (
                        sftype
                        if hasattr(LAURA_elements, sftype)
                        else sftype.capitalize()
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
                warn(f"Elegant type {sftype!r} for {k!r} not recognized; setting as drift.")
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
            for subk in [
                "magnetic",
                "cavity",
                "simulation",
                "diagnostic",
                "physical",
                "aperture",
            ]:
                if subk in model_fields:
                    sfconvert[k].update({subk: {}})
            for i, param in enumerate(v["ElementParameter"]):
                param = param.lower()
                merged = keyword_conversion_rules_elegant["general"]
                if sftype.lower() in keyword_conversion_rules_elegant:
                    merged = (
                        keyword_conversion_rules_elegant[sftype.lower()]
                        | keyword_conversion_rules_elegant["general"]
                    )
                kwele = {y: x for x, y in merged.items()}
                if param == "hgap" and "magnetic" in sfconvert[k]:
                    sfconvert[k]["magnetic"]["gap"] = 2 * v["ParameterValue"][i]
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
                    filenames.setdefault(k, {})[param] = v["ParameterValueString"][i]
                    warn(
                        f"Apparent filename found for element {k}: "
                        f"{param} = {v['ParameterValueString'][i]}; "
                        f"check path, file format and column data"
                    )
        return sfconvert, filenames
