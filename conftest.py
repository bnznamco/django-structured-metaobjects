from django.core.management import call_command
from django.db import connections
from django.conf import settings
import pytest


@pytest.fixture(scope="session")
def django_db_setup(django_db_blocker):
    from django.conf import settings
    db_name = "test_db.sqlite3"
    settings.DATABASES["default"]["NAME"] = db_name
    with django_db_blocker.unblock():
        call_command("sqlflush",)
        call_command("makemigrations", interactive=False)
        call_command("migrate", interactive=False)
    yield
    for connection in connections.all():
        connection.close()
