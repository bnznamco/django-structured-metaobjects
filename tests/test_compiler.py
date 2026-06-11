from datetime import date, datetime

import pytest
from pydantic import BaseModel as PydanticBaseModel

from structured_metaobjects.compiler import (
    _cache,
    _field_type,
    _json_schema_extra,
    build_pydantic_model,
    clear_cache,
    get_json_schema,
)
from structured_metaobjects.models import MetaType
from structured_metaobjects.schema_builder import MetaFieldKind, MetaTypeFieldDef


@pytest.mark.django_db
class TestBuildPydanticModel:
    def _make_meta_type(self, name, schema):
        return MetaType.objects.create(name=name, schema=schema)

    def test_build_simple_string_field(self):
        mt = self._make_meta_type("simple", [
            {"name": "title", "kind": "string", "required": True},
        ])
        model_cls = build_pydantic_model(mt)
        assert issubclass(model_cls, PydanticBaseModel)
        instance = model_cls(title="Hello")
        assert instance.title == "Hello"

    def test_build_multiple_field_types(self):
        mt = self._make_meta_type("multi", [
            {"name": "name", "kind": "string", "required": True},
            {"name": "age", "kind": "number", "integer": True},
            {"name": "score", "kind": "number"},
            {"name": "active", "kind": "boolean"},
        ])
        model_cls = build_pydantic_model(mt)
        instance = model_cls(name="Alice", age=30, score=9.5, active=True)
        assert instance.name == "Alice"
        assert instance.age == 30

    def test_build_optional_field_defaults_to_none(self):
        mt = self._make_meta_type("opt", [
            {"name": "bio", "kind": "string", "multiline": True, "required": False},
        ])
        model_cls = build_pydantic_model(mt)
        instance = model_cls()
        assert instance.bio is None

    def test_build_group_field(self):
        mt = self._make_meta_type("grp", [
            {
                "name": "address",
                "kind": "group",
                "children": [
                    {"name": "street", "kind": "string", "required": True},
                    {"name": "city", "kind": "string", "required": True},
                ],
            }
        ])
        model_cls = build_pydantic_model(mt)
        instance = model_cls(address={"street": "123 Main", "city": "NYC"})
        assert instance.address.street == "123 Main"

    def test_build_list_field(self):
        mt = self._make_meta_type("lst", [
            {
                "name": "items",
                "kind": "list",
                "children": [
                    {"name": "label", "kind": "string", "required": True},
                ],
            }
        ])
        model_cls = build_pydantic_model(mt)
        instance = model_cls(items=[{"label": "A"}, {"label": "B"}])
        assert len(instance.items) == 2
        assert instance.items[0].label == "A"

    def test_build_translated_field(self):
        mt = self._make_meta_type("trans", [
            {"name": "title", "kind": "string", "required": True, "translated": True},
        ])
        model_cls = build_pydantic_model(mt)
        instance = model_cls(title={"en": "Hello", "it": "Ciao"})
        assert instance.title["en"] == "Hello"

    def test_build_ref_field(self):
        mt = self._make_meta_type("ref", [
            {"name": "page", "kind": "ref", "target_model": "test_module.Page"},
        ])
        model_cls = build_pydantic_model(mt)
        assert model_cls is not None

    def test_build_queryset_field(self):
        mt = self._make_meta_type("qs", [
            {"name": "pages", "kind": "queryset", "target_model": "test_module.Page"},
        ])
        model_cls = build_pydantic_model(mt)
        assert model_cls is not None

    def test_invalid_ref_target_raises(self):
        mt = self._make_meta_type("badref", [
            {"name": "thing", "kind": "ref", "target_model": "invalid"},
        ])
        with pytest.raises(ValueError, match="target_model"):
            build_pydantic_model(mt)

    def test_build_html_field(self):
        mt = self._make_meta_type("html", [
            {"name": "content", "kind": "html", "required": True},
        ])
        model_cls = build_pydantic_model(mt)
        instance = model_cls(content="<p>Hello</p>")
        assert instance.content == "<p>Hello</p>"

    def test_build_date_field(self):
        mt = self._make_meta_type("date", [
            {"name": "birthday", "kind": "date", "required": True},
        ])
        model_cls = build_pydantic_model(mt)
        instance = model_cls(birthday=date(2000, 1, 15))
        assert instance.birthday == date(2000, 1, 15)

    def test_build_date_field_from_string(self):
        mt = self._make_meta_type("date_str", [
            {"name": "published", "kind": "date", "required": True},
        ])
        model_cls = build_pydantic_model(mt)
        instance = model_cls(published="2023-05-20")
        assert instance.published == date(2023, 5, 20)

    def test_build_datetime_field(self):
        mt = self._make_meta_type("datetime", [
            {"name": "created_at", "kind": "datetime", "required": True},
        ])
        model_cls = build_pydantic_model(mt)
        dt = datetime(2023, 6, 15, 10, 30, 0)
        instance = model_cls(created_at=dt)
        assert instance.created_at == dt

    def test_build_datetime_field_from_string(self):
        mt = self._make_meta_type("datetime_str", [
            {"name": "updated_at", "kind": "datetime", "required": True},
        ])
        model_cls = build_pydantic_model(mt)
        instance = model_cls(updated_at="2023-06-15T10:30:00")
        assert instance.updated_at == datetime(2023, 6, 15, 10, 30, 0)

    def test_build_select_field(self):
        mt = self._make_meta_type("select", [
            {
                "name": "status",
                "kind": "select",
                "required": True,
                "choices": [
                    {"value": "draft", "label": "Draft"},
                    {"value": "published", "label": "Published"},
                ],
            },
        ])
        model_cls = build_pydantic_model(mt)
        instance = model_cls(status="published")
        assert instance.status == "published"

    def test_build_select_field_optional(self):
        mt = self._make_meta_type("select_opt", [
            {
                "name": "category",
                "kind": "select",
                "required": False,
                "choices": [
                    {"value": "news"},
                    {"value": "blog"},
                ],
            },
        ])
        model_cls = build_pydantic_model(mt)
        instance = model_cls()
        assert instance.category is None
        instance2 = model_cls(category="news")
        assert instance2.category == "news"


@pytest.mark.django_db
class TestCache:
    def test_cache_hit(self):
        mt = MetaType.objects.create(name="cached", schema=[
            {"name": "x", "kind": "string"},
        ])
        clear_cache()
        model1 = build_pydantic_model(mt)
        model2 = build_pydantic_model(mt)
        assert model1 is model2

    def test_clear_cache_by_id(self):
        mt = MetaType.objects.create(name="cc", schema=[
            {"name": "x", "kind": "string"},
        ])
        build_pydantic_model(mt)
        assert any(k[0] == mt.pk for k in _cache)
        clear_cache(mt.pk)
        assert not any(k[0] == mt.pk for k in _cache)

    def test_clear_cache_all(self):
        mt = MetaType.objects.create(name="ca", schema=[
            {"name": "x", "kind": "string"},
        ])
        build_pydantic_model(mt)
        clear_cache()
        assert len(_cache) == 0


class TestFieldType:
    """Unit tests for _field_type helper."""

    def test_string_returns_str(self):
        fdef = MetaTypeFieldDef(name="x", kind=MetaFieldKind.string)
        assert _field_type(fdef, "Test") is str

    def test_html_returns_str(self):
        fdef = MetaTypeFieldDef(name="x", kind=MetaFieldKind.html)
        assert _field_type(fdef, "Test") is str

    def test_number_returns_float(self):
        fdef = MetaTypeFieldDef(name="x", kind=MetaFieldKind.number)
        assert _field_type(fdef, "Test") is float

    def test_number_with_integer_returns_int(self):
        fdef = MetaTypeFieldDef(name="x", kind=MetaFieldKind.number, integer=True)
        assert _field_type(fdef, "Test") is int

    def test_boolean_returns_bool(self):
        fdef = MetaTypeFieldDef(name="x", kind=MetaFieldKind.boolean)
        assert _field_type(fdef, "Test") is bool

    def test_date_returns_date(self):
        fdef = MetaTypeFieldDef(name="x", kind=MetaFieldKind.date)
        assert _field_type(fdef, "Test") is date

    def test_datetime_returns_datetime(self):
        fdef = MetaTypeFieldDef(name="x", kind=MetaFieldKind.datetime)
        assert _field_type(fdef, "Test") is datetime

    def test_select_returns_str(self):
        fdef = MetaTypeFieldDef(
            name="x",
            kind=MetaFieldKind.select,
            choices=[{"value": "a"}, {"value": "b"}],
        )
        assert _field_type(fdef, "Test") is str


class TestJsonSchemaExtra:
    """Unit tests for _json_schema_extra helper."""

    def test_string_multiline_format(self):
        fdef = MetaTypeFieldDef(name="x", kind=MetaFieldKind.string, multiline=True)
        extra = _json_schema_extra(fdef)
        assert extra["format"] == "textarea"

    def test_html_format(self):
        fdef = MetaTypeFieldDef(name="x", kind=MetaFieldKind.html)
        extra = _json_schema_extra(fdef)
        assert extra["format"] == "html"

    def test_select_choices(self):
        fdef = MetaTypeFieldDef(
            name="x",
            kind=MetaFieldKind.select,
            choices=[
                {"value": "draft", "label": "Draft"},
                {"value": "published", "label": "Published"},
            ],
        )
        extra = _json_schema_extra(fdef)
        assert "oneOf" in extra
        assert len(extra["oneOf"]) == 2
        assert extra["oneOf"][0] == {"const": "draft", "title": "Draft"}
        assert extra["oneOf"][1] == {"const": "published", "title": "Published"}

    def test_string_length_constraints(self):
        fdef = MetaTypeFieldDef(
            name="x", kind=MetaFieldKind.string, min_length=5, max_length=100
        )
        extra = _json_schema_extra(fdef)
        assert extra["minLength"] == 5
        assert extra["maxLength"] == 100

    def test_string_placeholder(self):
        fdef = MetaTypeFieldDef(
            name="x", kind=MetaFieldKind.string, placeholder="Enter text"
        )
        extra = _json_schema_extra(fdef)
        assert extra["placeholder"] == "Enter text"

    def test_html_placeholder(self):
        fdef = MetaTypeFieldDef(
            name="x", kind=MetaFieldKind.html, placeholder="Enter HTML"
        )
        extra = _json_schema_extra(fdef)
        assert extra["placeholder"] == "Enter HTML"

    def test_number_constraints(self):
        fdef = MetaTypeFieldDef(
            name="x", kind=MetaFieldKind.number, minimum=0, maximum=100
        )
        extra = _json_schema_extra(fdef)
        assert extra["minimum"] == 0
        assert extra["maximum"] == 100

    def test_no_extra_for_plain_boolean(self):
        fdef = MetaTypeFieldDef(name="x", kind=MetaFieldKind.boolean)
        extra = _json_schema_extra(fdef)
        assert extra == {}

    def test_no_extra_for_plain_date(self):
        fdef = MetaTypeFieldDef(name="x", kind=MetaFieldKind.date)
        extra = _json_schema_extra(fdef)
        assert extra == {}

    def test_no_extra_for_plain_datetime(self):
        fdef = MetaTypeFieldDef(name="x", kind=MetaFieldKind.datetime)
        extra = _json_schema_extra(fdef)
        assert extra == {}


@pytest.mark.django_db
class TestGetJsonSchema:
    def test_returns_dict(self):
        mt = MetaType.objects.create(name="js", schema=[
            {"name": "title", "kind": "string", "required": True},
        ])
        schema = get_json_schema(mt)
        assert isinstance(schema, dict)
        assert "properties" in schema
        assert "title" in schema["properties"]

    def test_schema_includes_date_format(self):
        mt = MetaType.objects.create(name="js_date", schema=[
            {"name": "published", "kind": "date", "required": True},
        ])
        schema = get_json_schema(mt)
        assert "published" in schema["properties"]
        assert schema["properties"]["published"]["type"] == "string"
        assert schema["properties"]["published"]["format"] == "date"

    def test_schema_includes_datetime_format(self):
        mt = MetaType.objects.create(name="js_dt", schema=[
            {"name": "created", "kind": "datetime", "required": True},
        ])
        schema = get_json_schema(mt)
        assert "created" in schema["properties"]
        assert schema["properties"]["created"]["type"] == "string"
        assert schema["properties"]["created"]["format"] == "date-time"

    def test_schema_includes_html_format(self):
        mt = MetaType.objects.create(name="js_html", schema=[
            {"name": "body", "kind": "html", "required": True},
        ])
        schema = get_json_schema(mt)
        assert "body" in schema["properties"]
        assert schema["properties"]["body"].get("format") == "html"

    def test_schema_includes_select_choices(self):
        mt = MetaType.objects.create(name="js_sel", schema=[
            {
                "name": "status",
                "kind": "select",
                "required": True,
                "choices": [
                    {"value": "draft", "label": "Draft"},
                    {"value": "live", "label": "Live"},
                ],
            },
        ])
        schema = get_json_schema(mt)
        assert "status" in schema["properties"]
        prop = schema["properties"]["status"]
        assert "oneOf" in prop
        assert {"const": "draft", "title": "Draft"} in prop["oneOf"]
        assert {"const": "live", "title": "Live"} in prop["oneOf"]

    def test_schema_includes_string_constraints(self):
        mt = MetaType.objects.create(name="js_str", schema=[
            {
                "name": "title",
                "kind": "string",
                "required": True,
                "min_length": 1,
                "max_length": 255,
            },
        ])
        schema = get_json_schema(mt)
        prop = schema["properties"]["title"]
        assert prop.get("minLength") == 1
        assert prop.get("maxLength") == 255

    def test_schema_includes_number_constraints(self):
        mt = MetaType.objects.create(name="js_num", schema=[
            {
                "name": "rating",
                "kind": "number",
                "required": True,
                "minimum": 0,
                "maximum": 5,
            },
        ])
        schema = get_json_schema(mt)
        prop = schema["properties"]["rating"]
        assert prop.get("minimum") == 0
        assert prop.get("maximum") == 5

    def test_schema_nested_group_with_date(self):
        mt = MetaType.objects.create(name="js_ng", schema=[
            {
                "name": "event",
                "kind": "group",
                "children": [
                    {"name": "title", "kind": "string", "required": True},
                    {"name": "start_date", "kind": "date", "required": True},
                    {"name": "start_time", "kind": "datetime"},
                ],
            },
        ])
        schema = get_json_schema(mt)
        assert "event" in schema["properties"]

    def test_schema_list_with_select(self):
        mt = MetaType.objects.create(name="js_ls", schema=[
            {
                "name": "tags",
                "kind": "list",
                "children": [
                    {
                        "name": "category",
                        "kind": "select",
                        "required": True,
                        "choices": [
                            {"value": "tech"},
                            {"value": "news"},
                        ],
                    },
                    {"name": "label", "kind": "string", "required": True},
                ],
            },
        ])
        schema = get_json_schema(mt)
        assert "tags" in schema["properties"]
        # List fields produce an array schema - may be wrapped in anyOf for optional
        tags_prop = schema["properties"]["tags"]
        # Check for anyOf (optional list) or direct items
        if "anyOf" in tags_prop:
            array_branch = next(
                (b for b in tags_prop["anyOf"] if b.get("type") == "array"), None
            )
            assert array_branch is not None
            assert "items" in array_branch
        else:
            assert "items" in tags_prop or "$ref" in tags_prop


@pytest.mark.django_db
class TestConstraintEnforcement:
    """Declared constraints must be enforced server-side, not only
    advertised in the JSON schema (regression for UI-only constraints)."""

    def _model(self, **fdef):
        mt = MetaType.objects.create(name="Constr", schema=[{"name": "f", **fdef}])
        return mt.get_pydantic_model()

    def test_select_choices_enforced(self):
        model = self._model(
            kind="select",
            choices=[{"value": "red"}, {"value": "blue", "label": "Blue"}],
        )
        assert model.model_validate({"f": "red"}).f == "red"
        with pytest.raises(Exception):
            model.model_validate({"f": "PURPLE"})

    def test_string_length_enforced(self):
        model = self._model(kind="string", min_length=3, max_length=5)
        assert model.model_validate({"f": "abcd"}).f == "abcd"
        with pytest.raises(Exception):
            model.model_validate({"f": "ab"})
        with pytest.raises(Exception):
            model.model_validate({"f": "abcdef"})

    def test_number_bounds_enforced(self):
        model = self._model(kind="number", minimum=0, maximum=10)
        assert model.model_validate({"f": 5}).f == 5
        with pytest.raises(Exception):
            model.model_validate({"f": -1})
        with pytest.raises(Exception):
            model.model_validate({"f": 999})

    def test_integer_bounds_enforced(self):
        model = self._model(kind="number", integer=True, minimum=1, maximum=3)
        assert model.model_validate({"f": 2}).f == 2
        with pytest.raises(Exception):
            model.model_validate({"f": 4})

    def test_translated_constraints_apply_per_value(self):
        model = self._model(kind="string", translated=True, max_length=3)
        ok = model.model_validate({"f": {"en": "abc", "it": "ab"}})
        assert ok.f["en"] == "abc"
        with pytest.raises(Exception):
            model.model_validate({"f": {"en": "too-long"}})

    def test_schema_output_unchanged(self):
        """Constraints still appear in the JSON schema for the widget,
        including the oneOf choice titles."""
        mt = MetaType.objects.create(
            name="SchemaOut",
            schema=[
                {
                    "name": "color",
                    "kind": "select",
                    "required": True,
                    "choices": [{"value": "red", "label": "Red"}],
                },
                {"name": "title", "kind": "string", "min_length": 2, "max_length": 8, "required": True},
            ],
        )
        schema = mt.get_json_schema()
        color = schema["properties"]["color"]
        assert {"const": "red", "title": "Red"} in color["oneOf"]
        title = schema["properties"]["title"]
        assert title["minLength"] == 2
        assert title["maxLength"] == 8
