from rest_framework import serializers
from rest_framework.exceptions import ValidationError as DRFValidationError

from .models import MetaInstance, MetaType


class MetaTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = MetaType
        fields = "__all__"


class MetaInstanceSerializer(serializers.ModelSerializer):
    data = serializers.JSONField()

    class Meta:
        model = MetaInstance
        fields = "__all__"

    def _resolve_meta_type(self, attrs):
        meta_type = attrs.get("meta_type")
        if meta_type is None and self.instance is not None:
            meta_type = self.instance.meta_type
        return meta_type

    def validate(self, attrs):
        attrs = super().validate(attrs)
        meta_type = self._resolve_meta_type(attrs)
        if meta_type is None:
            raise DRFValidationError({"meta_type": "This field is required."})
        model_cls = meta_type.get_pydantic_model()
        try:
            validated = model_cls.model_validate(attrs.get("data") or {})
        except Exception as exc:
            raise DRFValidationError({"data": str(exc)})
        attrs["data"] = validated.model_dump(mode="json")
        return attrs
