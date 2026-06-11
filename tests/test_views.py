import pytest
from rest_framework.test import APIClient

from structured_metaobjects.models import MetaInstance, MetaType


@pytest.fixture
def api_client(django_user_model):
    """Staff-authenticated client — the API is IsAdminUser by default."""
    user = django_user_model.objects.create_user(
        username="staff", password="pw", is_staff=True
    )
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.fixture
def anon_client():
    return APIClient()


@pytest.mark.django_db
class TestApiPermissions:
    def test_anonymous_rejected(self, anon_client):
        mt = MetaType.objects.create(name="P", schema=[])
        assert anon_client.get("/api/meta-types/").status_code in (401, 403)
        assert anon_client.get(f"/api/meta-types/{mt.pk}/schema/").status_code in (401, 403)
        assert anon_client.get("/api/meta-instances/").status_code in (401, 403)
        resp = anon_client.post(
            "/api/meta-types/", {"name": "X", "schema": []}, format="json"
        )
        assert resp.status_code in (401, 403)

    def test_non_staff_rejected(self, django_user_model):
        user = django_user_model.objects.create_user(username="plain", password="pw")
        client = APIClient()
        client.force_authenticate(user=user)
        assert client.get("/api/meta-types/").status_code == 403


@pytest.mark.django_db
class TestMetaTypeViewSet:
    def _url(self, pk=None):
        if pk:
            return f"/api/meta-types/{pk}/"
        return "/api/meta-types/"

    def test_list(self, api_client):
        MetaType.objects.create(name="V1", schema=[])
        resp = api_client.get(self._url())
        assert resp.status_code == 200
        assert len(resp.data) >= 1

    def test_create(self, api_client):
        resp = api_client.post(
            self._url(),
            {"name": "V2", "schema": [{"name": "x", "kind": "string"}]},
            format="json",
        )
        assert resp.status_code == 201
        assert resp.data["name"] == "V2"

    def test_retrieve(self, api_client):
        mt = MetaType.objects.create(name="V3", schema=[])
        resp = api_client.get(self._url(mt.pk))
        assert resp.status_code == 200
        assert resp.data["name"] == "V3"

    def test_update(self, api_client):
        mt = MetaType.objects.create(name="V4", schema=[])
        resp = api_client.patch(
            self._url(mt.pk),
            {"name": "V4 Updated"},
            format="json",
        )
        assert resp.status_code == 200
        assert resp.data["name"] == "V4 Updated"

    def test_delete(self, api_client):
        mt = MetaType.objects.create(name="V5", schema=[])
        resp = api_client.delete(self._url(mt.pk))
        assert resp.status_code == 204

    def test_schema_action(self, api_client):
        mt = MetaType.objects.create(
            name="V6",
            schema=[{"name": "title", "kind": "string", "required": True}],
        )
        resp = api_client.get(f"/api/meta-types/{mt.pk}/schema/")
        assert resp.status_code == 200
        assert "properties" in resp.data


@pytest.mark.django_db
class TestMetaInstanceViewSet:
    def _url(self, pk=None):
        if pk:
            return f"/api/meta-instances/{pk}/"
        return "/api/meta-instances/"

    def _make_type(self):
        return MetaType.objects.create(
            name="VI",
            schema=[{"name": "title", "kind": "string", "required": True}],
        )

    def test_list(self, api_client):
        mt = self._make_type()
        MetaInstance.objects.create(meta_type=mt, data={"title": "A"})
        resp = api_client.get(self._url())
        assert resp.status_code == 200

    def test_create(self, api_client):
        mt = self._make_type()
        resp = api_client.post(
            self._url(),
            {"meta_type": mt.pk, "data": {"title": "New"}},
            format="json",
        )
        assert resp.status_code == 201

    def test_create_invalid_data(self, api_client):
        mt = self._make_type()
        resp = api_client.post(
            self._url(),
            {"meta_type": mt.pk, "data": {}},
            format="json",
        )
        assert resp.status_code == 400

    def test_retrieve(self, api_client):
        mt = self._make_type()
        mi = MetaInstance.objects.create(meta_type=mt, data={"title": "R"})
        resp = api_client.get(self._url(mi.pk))
        assert resp.status_code == 200

    def test_schema_action(self, api_client):
        mt = self._make_type()
        resp = api_client.get(f"/api/meta-instances/schema/?meta_type={mt.pk}")
        assert resp.status_code == 200
        assert "properties" in resp.data

    def test_schema_action_missing_param(self, api_client):
        resp = api_client.get("/api/meta-instances/schema/")
        assert resp.status_code == 400

    def test_schema_action_not_found(self, api_client):
        resp = api_client.get("/api/meta-instances/schema/?meta_type=99999")
        assert resp.status_code == 404
