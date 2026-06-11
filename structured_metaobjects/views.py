from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound, ValidationError as DRFValidationError
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from .models import MetaInstance, MetaType
from .serializers import MetaInstanceSerializer, MetaTypeSerializer


class MetaTypeViewSet(viewsets.ModelViewSet):
    queryset = MetaType.objects.all()
    serializer_class = MetaTypeSerializer
    # Meta types define schemas (including refs to any installed model):
    # staff-only by default. Override permission_classes in a subclass to
    # expose them more broadly.
    permission_classes = [IsAdminUser]
    search_fields = ("name",)

    @action(detail=True, methods=["get"], url_path="schema")
    def schema(self, request, pk=None):
        meta_type = self.get_object()
        return Response(meta_type.get_json_schema())


class MetaInstanceViewSet(viewsets.ModelViewSet):
    queryset = MetaInstance.objects.select_related("meta_type")
    serializer_class = MetaInstanceSerializer
    permission_classes = [IsAdminUser]
    search_fields = ()

    @action(detail=False, methods=["get"], url_path="schema")
    def schema(self, request):
        meta_type_id = request.GET.get("meta_type")
        if not meta_type_id:
            raise DRFValidationError({"meta_type": "Query parameter required."})
        try:
            meta_type = MetaType.objects.get(pk=meta_type_id)
        except MetaType.DoesNotExist:
            raise NotFound("MetaType not found")
        return Response(meta_type.get_json_schema())
