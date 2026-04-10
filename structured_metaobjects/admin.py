from django.contrib import admin

from .forms import MetaInstanceForm
from .models import MetaInstance, MetaType


@admin.register(MetaType)
class MetaTypeAdmin(admin.ModelAdmin):
    list_display = ("name",)


@admin.register(MetaInstance)
class MetaInstanceAdmin(admin.ModelAdmin):
    form = MetaInstanceForm
    list_display = ("__str__", "meta_type", "updated_at")
    list_filter = ("meta_type",)
    search_fields = ()

    class Media:
        js = ("structured_metaobjects/admin/meta_instance.js",)
