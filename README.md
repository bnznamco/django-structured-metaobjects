[![Test](https://github.com/bnznamco/django-structured-metaobjects/actions/workflows/ci.yml/badge.svg)](https://github.com/bnznamco/django-structured-metaobjects/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/django-structured-metaobjects.svg)](https://pypi.org/project/django-structured-metaobjects/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

# django-structured-metaobjects

User-defined, typed JSON objects for Django — built on top of
[`django-structured-json-field`](https://github.com/bnznamco/django-structured-field).

Editors define **meta types** in the admin (a list of typed field
definitions). Each `MetaInstance` then picks one of those types and the
admin form / REST API automatically adapts to the schema declared by the
chosen type.

## Features

- Field kinds: `string`, `html`, `number`, `boolean`, `date`, `datetime`,
  `select`, `ref` (single FK), `queryset` (list of FKs), `group` (nested
  object), `list` (repeating group), with optional `translated=True` per-field.
- Runtime Pydantic compiler with per-MetaType caching, invalidated on save.
- Admin form rebuilds the `data` widget for the selected meta type.
- DRF `MetaTypeViewSet` / `MetaInstanceViewSet` with `schema/` action.
- Typed access on `instance.obj.<field>` returning the parsed Pydantic
  model — FK / queryset fields lazily resolve to real Django objects
  with structured-json-field's caching.

## Install

```bash
pip install django-structured-metaobjects
```

Add to `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    # ...
    "structured",
    "structured_metaobjects",
]
```

Wire the REST endpoints into your router:

```python
from rest_framework import routers
from structured_metaobjects.views import MetaTypeViewSet, MetaInstanceViewSet

router = routers.DefaultRouter()
router.register(r"meta-types", MetaTypeViewSet, "meta-types")
router.register(r"meta-instances", MetaInstanceViewSet, "meta-instances")
```

## Field kinds

| kind       | Python type built by the compiler          | Notes                                                        |
|------------|--------------------------------------------|--------------------------------------------------------------|
| `string`   | `str`                                      | Supports `multiline`, `min_length`, `max_length`, `placeholder`. |
| `html`     | `str`                                      | Rich-text. Supports `placeholder`.                           |
| `number`   | `float` / `int`                            | Set `integer=True` for `int`. Supports `minimum`, `maximum`. |
| `boolean`  | `bool`                                     |                                                              |
| `date`     | `datetime.date`                            |                                                              |
| `datetime` | `datetime.datetime`                        |                                                              |
| `select`   | `str`                                      | Requires `choices` (list of `{value, label}`).               |
| `ref`      | `<TargetModel>`                            | Requires `target_model="app.Model"`.                         |
| `queryset` | `List[<TargetModel>]`                      | Requires `target_model="app.Model"`.                         |
| `group`    | nested Pydantic model from `children`      | Requires `children`.                                         |
| `list`     | `List[<group model>]` from `children`      | Requires `children`.                                         |

Setting `translated=True` wraps the field in `Dict[str, T]` so the value
is a per-language map.

## Typed access

```python
instance = MetaInstance.objects.get(pk=1)
obj = instance.obj                # cached Pydantic instance
obj.title                         # typed string
obj.related_page                  # real Django model instance (lazy/cached)
obj.gallery                       # list of real Django model instances
```
