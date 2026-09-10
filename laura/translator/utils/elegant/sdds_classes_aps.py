from warnings import warn

from ..functions import introspect_model_defaults
from .sdds_file import SDDSFile
from ...converters import (
    type_conversion_rules_aliases,
    type_conversion_rules_elegant,
    keyword_conversion_rules_elegant,
    element_keywords,
)
import laura.models.element as laura_elements



class SddsParams:

    def __init__(self, filename: str, page: int = 0):
        self.filename = filename
        self.page = page
        self.elegant_object = None
        self.elegant_data = None
        self.elegant_params = None

    def import_sdds_params_file(self, index=1) -> None:
        self.elegant_object = SDDSFile(index=index)
        self.elegant_object.read_file(self.filename, page=self.page)
        self.elegant_data = self.elegant_object.data

    def join_params(self) -> None:
        if not self.elegant_data:
            self.import_sdds_params_file()
        max_occurrence = {}
        for name, occ in zip(
            self.elegant_data["ElementName"], self.elegant_data["ElementOccurence"]
        ):
            max_occurrence[name] = max(max_occurrence.get(name, 1), occ)

        self.elegant_params = {}
        for i, k in enumerate(self.elegant_data["ElementName"]):
            occurrence = self.elegant_data["ElementOccurence"][i]
            key = f"{k}.{occurrence}" if max_occurrence[k] > 1 else k
            if key not in self.elegant_params:
                self.elegant_params.update(
                    {key: {param: [] for param in list(self.elegant_data.keys())[1:]}}
                )
            for val in list(self.elegant_data.keys())[1:]:
                if self.elegant_data["ElementName"][i] == k:
                    self.elegant_params[key][val].append(self.elegant_data[val][i])

    def create_element_dictionary(self, machine_area: str = "Lattice") -> tuple:
        if not self.elegant_params:
            self.join_params()
        sfconvert = {}
        # disallowed = ["bore", "zwakefile"]
        filenames = {}
        sfconvert = {}
        for k, v in self.elegant_params.items():
            elemtype = v["ElementType"][0].lower()
            alias = (
                "Diagnostic"
                if elemtype == "moni"
                else next(
                    (
                        sf
                        for sf, aliases in type_conversion_rules_aliases.items()
                        if elemtype in aliases
                    ),
                    None,
                )
            )
            if alias:
                sfconvert.update(
                    {k: {"hardware_type": alias, "name": k, "machine_area": machine_area}}
                )
            elif elemtype in element_keywords and "drift" not in elemtype:
                sfconvert.update(
                    {
                        k: {
                            "hardware_type": elemtype,
                            "name": k,
                            "machine_area": machine_area,
                        }
                    }
                )
            elif elemtype in list(type_conversion_rules_elegant.values()):
                switch_dict = {y: x for x, y in type_conversion_rules_elegant.items()}
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
                            "machine_area": machine_area,
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
                            "machine_area": machine_area,
                        }
                    }
                )
            sftype = sfconvert[k]["hardware_type"]
            if sftype == "Drift":
                sfconvert[k]["hardware_class"] = "Drift"
            registry = laura_elements.ELEMENT_REGISTRY
            try:
                if sftype == "kicker":
                    sftype = "Combined_Corrector"
                elif (
                    sftype not in registry
                    and "Cavity" not in sftype
                    and not hasattr(laura_elements, sftype)
                ):
                    sftype = sftype.capitalize()
                model_fields = introspect_model_defaults(
                    registry[sftype]
                    if sftype in registry
                    else getattr(laura_elements, sftype),
                    resolve_optional=True,
                )
                sfconvert[k]["hardware_type"] = sftype
            except AttributeError:
                warn(f"Elegant type {sftype!r} for {k!r} not recognized; setting as drift.")
                sfconvert.update(
                    {
                        k: {
                            "hardware_type": "Drift",
                            "name": k,
                            "hardware_class": "Drift",
                            "machine_area": machine_area,
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
                if param in ("fint1", "fint2") and v["ParameterValue"][i] < 0:
                    continue  # ELEGANT's sentinel for "unset, fall back to FINT"
                merged = keyword_conversion_rules_elegant["general"]
                if sftype.lower() in keyword_conversion_rules_elegant:
                    merged = (
                        keyword_conversion_rules_elegant[sftype.lower()]
                        | keyword_conversion_rules_elegant["general"]
                    )
                kwele = {y: x for x, y in merged.items()}
                kwele["fint"] = "edge_field_integral"
                kwele["fint1"] = "edge_field_integral_entrance"
                kwele["fint2"] = "edge_field_integral_exit"
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
                            if val is not None and not (
                                param in ("n_kicks", "n_slices") and val == 0
                            ):
                                sfconvert[k][subk].update({param: val})
                        elif param in kwele:
                            if kwele[param] in model_fields[subk]:
                                if (
                                    not isinstance(
                                        model_fields[subk][kwele[param]], str
                                    )
                                    or model_fields[subk][kwele[param]]
                                ) and not (
                                    kwele[param] in ("n_kicks", "n_slices")
                                    and val == 0
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


from laura._compat import deprecated_aliases  # noqa: E402

__getattr__ = deprecated_aliases(
    __name__,
    globals(),
    {
        "SDDS_Params": "SddsParams",
    },
)
