import pytest
from structured_metaobjects.schema_builder import MetaFieldKind, MetaTypeFieldDef


class TestMetaFieldKind:
    def test_all_kinds_present(self):
        expected = {
            "string", "html", "number", "boolean",
            "date", "datetime", "select", "ref", "queryset", "group", "list",
        }
        assert {k.value for k in MetaFieldKind} == expected

    def test_kind_is_str_enum(self):
        assert isinstance(MetaFieldKind.string, str)
        assert MetaFieldKind.string == "string"


class TestMetaTypeFieldDef:
    def test_minimal_field(self):
        fd = MetaTypeFieldDef(name="title")
        assert fd.name == "title"
        assert fd.kind == MetaFieldKind.string
        assert fd.required is False
        assert fd.translated is False
        assert fd.target_model is None
        assert fd.children == []

    def test_ref_field(self):
        fd = MetaTypeFieldDef(
            name="page",
            kind=MetaFieldKind.ref,
            target_model="test_module.Page",
        )
        assert fd.kind == MetaFieldKind.ref
        assert fd.target_model == "test_module.Page"

    def test_group_with_children(self):
        child = MetaTypeFieldDef(name="street", kind=MetaFieldKind.string)
        fd = MetaTypeFieldDef(
            name="address",
            kind=MetaFieldKind.group,
            children=[child],
        )
        assert len(fd.children) == 1
        assert fd.children[0].name == "street"

    def test_json_schema_has_conditional_logic(self):
        schema = MetaTypeFieldDef.model_json_schema()
        assert "if" in schema or "allOf" in schema or "$defs" in schema

    def test_round_trip_dict(self):
        data = {
            "name": "bio",
            "label": "Biography",
            "kind": "string",
            "multiline": True,
            "required": True,
            "translated": True,
        }
        fd = MetaTypeFieldDef.model_validate(data)
        dumped = fd.model_dump(mode="json")
        assert dumped["name"] == "bio"
        assert dumped["kind"] == "string"
        assert dumped["translated"] is True

    def test_recursive_children(self):
        data = {
            "name": "section",
            "kind": "group",
            "children": [
                {
                    "name": "subsection",
                    "kind": "group",
                    "children": [
                        {"name": "title", "kind": "string"},
                    ],
                }
            ],
        }
        fd = MetaTypeFieldDef.model_validate(data)
        assert fd.children[0].children[0].name == "title"
