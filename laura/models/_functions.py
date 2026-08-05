from pydantic import create_model, BaseModel
from yaml import safe_load


def read_yaml(fname: str) -> BaseModel:
    with open(fname, "r") as f:
        data = safe_load(f)

    # Build fields: field_name: (type, default)
    fields = {key: (type(value), value) for key, value in data.items()}

    # Create and return the dynamic model class
    DynamicModel = create_model(
        "DynamicModel",
        __base__=BaseModel,
        __module__=__name__,
        # model_config=model_config,
        **fields,
    )
    return DynamicModel(**data)
