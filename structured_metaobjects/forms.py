from django import forms
from structured.widget.fields import StructuredJSONFormField

from .models import MetaInstance, MetaType


class MetaInstanceForm(forms.ModelForm):
    """
    Rebuild the ``data`` form field as a ``StructuredJSONFormField`` whose
    schema is the runtime Pydantic model compiled from the chosen
    ``MetaType``. The selected meta type is taken from the bound instance
    or — when adding — from ``initial`` / submitted data.
    """

    class Meta:
        model = MetaInstance
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        meta_type = None
        if self.instance and self.instance.pk:
            meta_type = self.instance.meta_type
        else:
            initial_mt = self.initial.get("meta_type") or self.data.get("meta_type")
            if initial_mt:
                meta_type = MetaType.objects.filter(pk=initial_mt).first()
        if meta_type is not None:
            schema_cls = meta_type.get_pydantic_model()
            self.fields["data"] = StructuredJSONFormField(
                schema=schema_cls, required=False
            )
        else:
            self.fields["data"].help_text = (
                "Select a meta type and save to start editing the data."
            )
