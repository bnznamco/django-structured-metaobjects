import django.db.models.deletion
import structured.fields
from django.db import migrations, models

import structured_metaobjects.schema_builder


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="MetaType",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=200)),
                (
                    "schema",
                    structured.fields.StructuredJSONField(
                        default=list,
                        schema=structured_metaobjects.schema_builder.MetaTypeFieldDef,
                    ),
                ),
                ("compiled_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "meta type",
                "verbose_name_plural": "meta types",
                "ordering": ("name",),
            },
        ),
        migrations.CreateModel(
            name="MetaInstance",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("data", models.JSONField(blank=True, default=dict)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "meta_type",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="instances",
                        to="structured_metaobjects.metatype",
                    ),
                ),
            ],
            options={
                "verbose_name": "meta instance",
                "verbose_name_plural": "meta instances",
                "ordering": ("-updated_at",),
            },
        ),
    ]
