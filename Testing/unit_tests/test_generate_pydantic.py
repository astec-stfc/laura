"""Check that LinkML slot descriptions survive as attribute docstrings."""

from laura.schema.generate_pydantic import _add_attribute_docstrings

SAMPLE = '''\
class _PositionBase(ConfiguredBaseModel):
    """
    Cartesian position.
    """
    x: float = Field(default=0, description="""Horizontal component [m].""", json_schema_extra = { "linkml_meta": {'domain_of': ['Position'],
         'unit': {'ucum_code': 'm'}} })
    y: float = Field(default=0, json_schema_extra = { "linkml_meta": {} })
'''


def test_attribute_docstrings():
    out = _add_attribute_docstrings(SAMPLE)
    lines = out.split("\n")
    # Docstring lands immediately after the multi-line Field(...) statement
    assert lines[lines.index("         'unit': {'ucum_code': 'm'}} })") + 1] == (
        '    """Horizontal component [m]."""'
    )
    # Fields without a description gain nothing
    assert out.count('"""') == SAMPLE.count('"""') + 2
    compile(out, "<test>", "exec")


if __name__ == "__main__":
    test_attribute_docstrings()
    print("ok")
