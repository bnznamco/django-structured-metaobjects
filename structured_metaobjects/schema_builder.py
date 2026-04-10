from enum import Enum
from typing import Annotated, List, Optional

from pydantic import ConfigDict, Field, model_validator
from structured.pydantic.conditionals import When, conditional_schema
from structured.pydantic.models import BaseModel


def _target_model_enum(schema: dict) -> None:
    """
    Inject an enum of all installed Django models into the JSON schema.

    For ``Optional[str]`` Pydantic emits ``anyOf: [{type: string}, {type: null}]``.
    A sibling ``enum`` at that level is ignored by most JSON Schema editors,
    so we place the enum inside the string branch instead.
    """
    from django.apps import apps

    enum = sorted(f"{m._meta.app_label}.{m.__name__}" for m in apps.get_models())
    for branch in schema.get("anyOf", []):
        if branch.get("type") == "string":
            branch["enum"] = enum
            return
    schema["enum"] = enum


class SelectChoice(BaseModel):
    """A single option for a ``select`` field."""
    value: str = Field(min_length=1)
    label: str = ""

    @model_validator(mode="after")
    def _fill_label(self):
        if not self.label:
            self.label = self.value
        return self


class MetaFieldKind(str, Enum):
    string = "string"
    html = "html"
    number = "number"
    boolean = "boolean"
    date = "date"
    datetime = "datetime"
    select = "select"
    ref = "ref"
    queryset = "queryset"
    group = "group"
    list = "list"


class MetaTypeFieldDef(BaseModel):
    """
    Describes a single field declared by an editor on a ``MetaType``.

    The full ``MetaType.schema`` is a list of these (possibly nested via
    ``children``).

    Fields are conditionally shown/required based on ``kind``:

    - ``target_model`` — ``ref``, ``queryset``
    - ``children`` — ``group``, ``list``
    - ``choices`` — ``select``
    - ``multiline``, ``placeholder``, ``min_length``, ``max_length`` — ``string``
    - ``placeholder`` (also) — ``html``
    - ``integer``, ``minimum``, ``maximum`` — ``number``
    """

    # ── common ───────────────────────────────────────────────────────────
    name: str = Field(min_length=1)
    label: str = ""
    kind: MetaFieldKind = MetaFieldKind.string
    required: bool = False
    translated: bool = False

    # ── ref / queryset ───────────────────────────────────────────────────
    target_model: Annotated[
        Optional[str],
        Field(default=None, json_schema_extra=_target_model_enum),
    ] = None

    # ── group / list ─────────────────────────────────────────────────────
    children: List["MetaTypeFieldDef"] = Field(default_factory=list)

    # ── select ───────────────────────────────────────────────────────────
    choices: List[SelectChoice] = Field(default_factory=list)

    # ── string ───────────────────────────────────────────────────────────
    multiline: bool = False
    min_length: Optional[int] = None
    max_length: Optional[int] = None

    # ── string / html ────────────────────────────────────────────────────
    placeholder: str = ""

    # ── number ───────────────────────────────────────────────────────────
    integer: bool = False
    minimum: Optional[float] = None
    maximum: Optional[float] = None

    model_config = ConfigDict(
        json_schema_extra=conditional_schema(
            When(
                "kind",
                in_=["ref", "queryset"],
                controls=["target_model"],
                then={"required": ["target_model"]},
            ),
            When(
                "kind",
                in_=["group", "list"],
                controls=["children"],
                then={"required": ["children"]},
            ),
            When(
                "kind",
                in_=["select"],
                controls=["choices"],
                then={"required": ["choices"]},
            ),
            When(
                "kind",
                in_=["string"],
                controls=["multiline", "min_length", "max_length"],
            ),
            When(
                "kind",
                in_=["string", "html"],
                controls=["placeholder"],
            ),
            When(
                "kind",
                in_=["number"],
                controls=["integer", "minimum", "maximum"],
            ),
        )
    )

    @model_validator(mode="after")
    def _validate_fields(self):
        if not self.label:
            self.label = self.name.replace("_", " ").replace("-", " ").title()
        return self

    @model_validator(mode="after")
    def _validate_kind_dependencies(self):
        if self.kind in (MetaFieldKind.ref, MetaFieldKind.queryset):
            if not self.target_model:
                raise ValueError(
                    f"target_model is required when kind is '{self.kind.value}'"
                )
        if self.kind in (MetaFieldKind.group, MetaFieldKind.list):
            if not self.children:
                raise ValueError(
                    f"children is required when kind is '{self.kind.value}'"
                )
        if self.kind == MetaFieldKind.select:
            if not self.choices:
                raise ValueError(
                    "choices is required when kind is 'select'"
                )
        return self


MetaTypeFieldDef.model_rebuild()
