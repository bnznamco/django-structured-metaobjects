from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _
from structured.fields import StructuredJSONField

from . import compiler as meta_compiler
from .schema_builder import MetaTypeFieldDef


class MetaType(models.Model):
    """
    A user-defined "type" describing the shape of a ``MetaInstance``.

    The ``schema`` field is a list of ``MetaTypeFieldDef`` rows declared
    by an editor in the admin (string, ref, group, list, ...). When the
    MetaType is saved, the runtime Pydantic compiler cache is invalidated
    so any MetaInstance form/serializer using it picks up the new shape.
    """

    name = models.CharField(max_length=200)
    schema = StructuredJSONField(default=list, schema=MetaTypeFieldDef)
    compiled_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "structured_metaobjects"
        verbose_name = _("meta type")
        verbose_name_plural = _("meta types")
        ordering = ("name",)

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        meta_compiler.clear_cache(self.pk)

    def get_pydantic_model(self):
        return meta_compiler.build_pydantic_model(self)

    def get_json_schema(self) -> dict:
        return meta_compiler.get_json_schema(self)


class MetaInstance(models.Model):
    """
    Concrete entry whose shape is dictated by its referenced ``MetaType``.

    ``data`` is stored as a plain ``JSONField`` because ``StructuredJSONField``
    needs its schema at class load time. We validate ``data`` against the
    runtime Pydantic model built from ``meta_type`` in :meth:`clean` (and
    at the serializer level for the API).
    """

    meta_type = models.ForeignKey(
        MetaType, on_delete=models.PROTECT, related_name="instances"
    )
    data = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "structured_metaobjects"
        verbose_name = _("meta instance")
        verbose_name_plural = _("meta instances")
        ordering = ("-updated_at",)

    def __str__(self) -> str:
        return f"{self.meta_type} #{self.pk}"

    @property
    def obj(self):
        """
        Return ``data`` parsed into the runtime Pydantic model derived from
        ``meta_type``. Field access on the returned object benefits from
        ``django-structured-json-field`` semantics — typed attributes plus
        cached lazy DB lookups for ``ref``/``queryset`` fields — without
        forcing a static schema on the underlying ``JSONField``.

        The parsed object is cached on the instance and invalidated whenever
        the raw ``data`` dict is reassigned.
        """
        if self.meta_type_id is None:
            return None
        cached = getattr(self, "_obj_cache", None)
        if cached is not None and cached[0] is self.data:
            return cached[1]
        model_cls = self.meta_type.get_pydantic_model()
        raw = self.data or {}
        model_cls._cache_engine.build_cache(raw)
        parsed = model_cls.model_validate(raw)
        self._obj_cache = (self.data, parsed)
        return parsed

    def clean(self):
        super().clean()
        if self.meta_type_id is None:
            return
        model_cls = self.meta_type.get_pydantic_model()
        try:
            validated = model_cls.model_validate(self.data or {})
        except Exception as exc:  # pydantic ValidationError
            raise ValidationError({"data": str(exc)})
        self.data = validated.model_dump(mode="json")
