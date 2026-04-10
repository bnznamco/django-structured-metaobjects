import pytest
from django.contrib.admin.sites import AdminSite

from structured_metaobjects.admin import MetaInstanceAdmin, MetaTypeAdmin
from structured_metaobjects.models import MetaInstance, MetaType


@pytest.mark.django_db
class TestAdminRegistration:
    def test_meta_type_admin_registered(self):
        site = AdminSite()
        admin = MetaTypeAdmin(MetaType, site)
        assert admin.list_display == ("name",)

    def test_meta_instance_admin_registered(self):
        site = AdminSite()
        admin = MetaInstanceAdmin(MetaInstance, site)
        assert "meta_type" in admin.list_filter

    def test_meta_instance_admin_uses_custom_form(self):
        from structured_metaobjects.forms import MetaInstanceForm

        site = AdminSite()
        admin = MetaInstanceAdmin(MetaInstance, site)
        assert admin.form is MetaInstanceForm
