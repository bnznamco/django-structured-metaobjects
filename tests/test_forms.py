import pytest
from structured.widget.fields import StructuredJSONFormField

from structured_metaobjects.forms import MetaInstanceForm
from structured_metaobjects.models import MetaInstance, MetaType


@pytest.mark.django_db
class TestMetaInstanceForm:
    def _make_type(self):
        return MetaType.objects.create(
            name="Form Type",
            schema=[{"name": "title", "kind": "string", "required": True}],
        )

    def test_form_with_existing_instance(self):
        mt = self._make_type()
        mi = MetaInstance.objects.create(
            meta_type=mt,
            data={"title": "Existing"},
        )
        form = MetaInstanceForm(instance=mi)
        assert isinstance(form.fields["data"], StructuredJSONFormField)

    def test_form_without_meta_type_shows_help_text(self):
        form = MetaInstanceForm()
        assert "Select a meta type" in form.fields["data"].help_text

    def test_form_with_initial_meta_type(self):
        mt = self._make_type()
        form = MetaInstanceForm(initial={"meta_type": mt.pk})
        assert isinstance(form.fields["data"], StructuredJSONFormField)
