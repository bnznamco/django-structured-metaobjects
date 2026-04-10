from django.urls import include, path
from rest_framework import routers

from .views import MetaInstanceViewSet, MetaTypeViewSet

router = routers.DefaultRouter()
router.register(r"meta-types", MetaTypeViewSet, "meta-types")
router.register(r"meta-instances", MetaInstanceViewSet, "meta-instances")

urlpatterns = [
    path("", include(router.urls)),
]
