# Quick Start

## Installation

```bash
pip install django-structured-metaobjects
```

## Configuration

Add to your `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    # ...
    "structured",
    "structured_metaobjects",
]
```

Run migrations:

```bash
python manage.py migrate
```

## Wire REST endpoints

```python
from rest_framework import routers
from structured_metaobjects.views import MetaTypeViewSet, MetaInstanceViewSet

router = routers.DefaultRouter()
router.register(r"meta-types", MetaTypeViewSet, "meta-types")
router.register(r"meta-instances", MetaInstanceViewSet, "meta-instances")
```

## Create a MetaType

In the Django admin (or via the API), create a new **MetaType**:

- **key**: `article`
- **name**: `Article`
- **schema**: define fields like `title` (string, required), `body` (text), `published` (boolean)

## Create a MetaInstance

Create a **MetaInstance** linked to the Article type:

```python
from structured_metaobjects.models import MetaType, MetaInstance

mt = MetaType.objects.get(key="article")
mi = MetaInstance.objects.create(
    meta_type=mt,
    identifier="hello-world",
    data={"title": "Hello World", "body": "Content here", "published": True},
)
```

## Typed access

```python
obj = mi.obj          # cached Pydantic instance
obj.title             # "Hello World"
obj.published         # True
```
