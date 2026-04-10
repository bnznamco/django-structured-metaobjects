from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from tests.app.test_module.views import PageViewSet

router = DefaultRouter()
router.register(r'pages', PageViewSet)

urlpatterns = [
    path("", include("structured.urls")),
    path('admin/', admin.site.urls),
    path('api/', include('structured_metaobjects.urls')),
    path('api/', include(router.urls)),
]
