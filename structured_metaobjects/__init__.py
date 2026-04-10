from .schema_builder import MetaFieldKind, MetaTypeFieldDef
from .compiler import build_pydantic_model, clear_cache, get_json_schema

__version__ = "1.0.0"

default_app_config = "structured_metaobjects.apps.StructuredMetaobjectsConfig"

__all__ = [
    "MetaFieldKind",
    "MetaTypeFieldDef",
    "build_pydantic_model",
    "clear_cache",
    "get_json_schema",
]
