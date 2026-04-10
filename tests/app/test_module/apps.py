from django.apps import AppConfig


class TestModuleConfig(AppConfig):
    name = "tests.app.test_module"
    label = "test_module"
    verbose_name = "Test Module"
    default_auto_field = "django.db.models.BigAutoField"
