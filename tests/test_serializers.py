import pytest

from structured_metaobjects.models import MetaInstance, MetaType
from structured_metaobjects.serializers import (
    MetaInstanceSerializer,
    MetaTypeSerializer,
)


@pytest.mark.django_db
class TestMetaTypeSerializer:
    def test_serialize(self):
        mt = MetaType.objects.create(
            name="Ser",
            schema=[{"name": "title", "kind": "string"}],
        )
        data = MetaTypeSerializer(mt).data
        assert data["name"] == "Ser"
        assert isinstance(data["schema"], list)

    def test_deserialize(self):
        payload = {
            "name": "New Type",
            "schema": [{"name": "body", "kind": "string", "multiline": True}],
        }
        s = MetaTypeSerializer(data=payload)
        assert s.is_valid(), s.errors
        mt = s.save()
        assert mt.pk is not None


@pytest.mark.django_db
class TestMetaInstanceSerializer:
    def _make_type(self):
        return MetaType.objects.create(
            name="MI Ser",
            schema=[
                {"name": "title", "kind": "string", "required": True},
            ],
        )

    def test_valid_create(self):
        mt = self._make_type()
        payload = {
            "meta_type": mt.pk,
            "data": {"title": "Hello"},
        }
        s = MetaInstanceSerializer(data=payload)
        assert s.is_valid(), s.errors
        mi = s.save()
        assert mi.data["title"] == "Hello"

    def test_invalid_data_rejected(self):
        mt = self._make_type()
        payload = {
            "meta_type": mt.pk,
            "data": {},
        }
        s = MetaInstanceSerializer(data=payload)
        assert not s.is_valid()
        assert "data" in s.errors

    def test_missing_meta_type_rejected(self):
        payload = {
            "data": {"title": "No type"},
        }
        s = MetaInstanceSerializer(data=payload)
        assert not s.is_valid()

    def test_update_existing(self):
        mt = self._make_type()
        mi = MetaInstance.objects.create(
            meta_type=mt,
            data={"title": "Old"},
        )
        s = MetaInstanceSerializer(mi, data={"data": {"title": "New"}}, partial=True)
        assert s.is_valid(), s.errors
        updated = s.save()
        assert updated.data["title"] == "New"
