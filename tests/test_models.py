import pytest
from django.core.exceptions import ValidationError
from django.test.utils import override_settings

from structured_metaobjects.compiler import _cache, clear_cache
from structured_metaobjects.models import MetaInstance, MetaType
from tests.app.test_module.models import Page


@pytest.mark.django_db
class TestMetaType:
    def test_create(self):
        mt = MetaType.objects.create(
            name="Article",
            schema=[{"name": "title", "kind": "string", "required": True}],
        )
        assert mt.pk is not None
        assert str(mt) == "Article"

    def test_save_clears_cache(self):
        mt = MetaType.objects.create(
            name="Cache Inv",
            schema=[{"name": "x", "kind": "string"}],
        )
        mt.get_pydantic_model()
        assert any(k[0] == mt.pk for k in _cache)
        mt.name = "Updated"
        mt.save()
        assert not any(k[0] == mt.pk for k in _cache)

    def test_get_pydantic_model(self):
        mt = MetaType.objects.create(
            name="PM",
            schema=[{"name": "body", "kind": "string", "multiline": True}],
        )
        clear_cache()
        model_cls = mt.get_pydantic_model()
        assert hasattr(model_cls, "model_fields")

    def test_get_json_schema(self):
        mt = MetaType.objects.create(
            name="JSON Schema",
            schema=[{"name": "name", "kind": "string", "required": True}],
        )
        schema = mt.get_json_schema()
        assert "properties" in schema


@pytest.mark.django_db
class TestMetaInstance:
    def _make_type(self):
        return MetaType.objects.create(
            name="Inst Type",
            schema=[
                {"name": "title", "kind": "string", "required": True},
                {"name": "count", "kind": "number", "integer": True},
            ],
        )

    def test_create(self):
        mt = self._make_type()
        mi = MetaInstance.objects.create(
            meta_type=mt,
            data={"title": "Hello", "count": 5},
        )
        assert mi.pk is not None

    def test_str(self):
        mt = self._make_type()
        mi = MetaInstance.objects.create(
            meta_type=mt, data={"title": "X"},
        )
        assert str(mi) == f"Inst Type #{mi.pk}"

    def test_obj_property(self):
        mt = self._make_type()
        mi = MetaInstance.objects.create(
            meta_type=mt,
            data={"title": "World", "count": 10},
        )
        obj = mi.obj
        assert obj.title == "World"
        assert obj.count == 10

    def test_obj_caching(self):
        mt = self._make_type()
        mi = MetaInstance.objects.create(
            meta_type=mt,
            data={"title": "Cached"},
        )
        obj1 = mi.obj
        obj2 = mi.obj
        assert obj1 is obj2

    def test_obj_none_without_meta_type(self):
        mi = MetaInstance()
        assert mi.obj is None

    def test_clean_valid_data(self):
        mt = self._make_type()
        mi = MetaInstance(meta_type=mt, data={"title": "Valid"})
        mi.clean()
        assert mi.data["title"] == "Valid"

    def test_clean_invalid_data_raises(self):
        mt = self._make_type()
        mi = MetaInstance(meta_type=mt, data={"title": 123})
        with pytest.raises(ValidationError):
            mi.clean()

    def test_clean_missing_required_raises(self):
        mt = self._make_type()
        mi = MetaInstance(meta_type=mt, data={})
        with pytest.raises(ValidationError):
            mi.clean()

    def test_clean_normalizes_data(self):
        mt = self._make_type()
        mi = MetaInstance(meta_type=mt, data={"title": "Test", "count": "5"})
        mi.clean()
        assert mi.data["count"] == 5


@pytest.mark.django_db
class TestMetaInstanceCacheEngine:
    """Verify that accessing ref/queryset fields on MetaInstance.obj uses
    the structured-field CacheEngine, batch-fetching related objects
    instead of issuing per-field queries."""

    @pytest.fixture()
    def pages(self):
        return [
            Page.objects.create(title="Page A", slug="page-a"),
            Page.objects.create(title="Page B", slug="page-b"),
            Page.objects.create(title="Page C", slug="page-c"),
        ]

    def test_fk_field_single_query(self, django_assert_num_queries, pages):
        mt = MetaType.objects.create(
            name="FK Test",
            schema=[
                {"name": "page", "kind": "ref", "target_model": "test_module.Page"},
            ],
        )
        mi = MetaInstance.objects.create(
            meta_type=mt,
            data={"page": pages[0].pk},
        )
        # Building obj should batch-fetch the FK in a single query
        # (1 query for the cache engine to fetch all referenced Page PKs)
        with django_assert_num_queries(1):
            obj = mi.obj
            assert obj.page.pk == pages[0].pk
            assert obj.page.title == "Page A"

    def test_queryset_field_single_query(self, django_assert_num_queries, pages):
        mt = MetaType.objects.create(
            name="QS Test",
            schema=[
                {"name": "pages", "kind": "queryset", "target_model": "test_module.Page"},
            ],
        )
        pks = [p.pk for p in pages]
        mi = MetaInstance.objects.create(
            meta_type=mt,
            data={"pages": pks},
        )
        # Building obj should batch-fetch all QS PKs in a single query
        with django_assert_num_queries(1):
            obj = mi.obj
            result_pks = [p.pk for p in obj.pages]
            assert set(result_pks) == set(pks)

    def test_mixed_fk_and_qs_fields(self, django_assert_num_queries, pages):
        mt = MetaType.objects.create(
            name="Mixed Test",
            schema=[
                {"name": "main_page", "kind": "ref", "target_model": "test_module.Page"},
                {"name": "related_pages", "kind": "queryset", "target_model": "test_module.Page"},
            ],
        )
        mi = MetaInstance.objects.create(
            meta_type=mt,
            data={
                "main_page": pages[0].pk,
                "related_pages": [p.pk for p in pages[1:]],
            },
        )
        # Both FK and QS point to the same model so the cache engine
        # should resolve everything in a single batched query
        with django_assert_num_queries(1):
            obj = mi.obj
            assert obj.main_page.pk == pages[0].pk
            qs_pks = [p.pk for p in obj.related_pages]
            assert set(qs_pks) == {pages[1].pk, pages[2].pk}

    def test_obj_cache_no_extra_queries(self, django_assert_num_queries, pages):
        mt = MetaType.objects.create(
            name="Cache Hit",
            schema=[
                {"name": "page", "kind": "ref", "target_model": "test_module.Page"},
            ],
        )
        mi = MetaInstance.objects.create(
            meta_type=mt,
            data={"page": pages[0].pk},
        )
        # First access builds the cache
        _ = mi.obj
        # Second access should hit the instance cache — zero queries
        with django_assert_num_queries(0):
            obj = mi.obj
            assert obj.page.pk == pages[0].pk
