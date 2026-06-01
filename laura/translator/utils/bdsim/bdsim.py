def aperture_params(dic: dict | None):
    conv = {}
    if dic is None:
        return conv
    if len(list(dic.keys())) == 0:
        return conv
    if "type" in dic:
        conv.update({"apertureType": dic["type"]})
    if "size" in dic:
        if isinstance(dic["size"], list) and len(dic["size"]) == 2:
            conv.update({"aper1": (dic["size"][0], "m")})
            conv.update({"aper2": (dic["size"][1], "m")})
        elif isinstance(dic["size"], (int, float)):
            conv.update({"aper1": (dic["size"], "m")})
    if "material" in dic:
        conv.update({"beampipeMaterial": dic["material"]})
    return conv
