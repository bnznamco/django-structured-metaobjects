# Field Kinds

Each field in a MetaType schema is described by a `MetaTypeFieldDef` with a `kind` property. The compiler maps each kind to a Python type at runtime.

## Primitive Kinds

| Kind       | Python Type         | Notes                                                         |
|------------|---------------------|---------------------------------------------------------------|
| `string`   | `str`               | Supports `multiline`, `min_length`, `max_length`, `placeholder`. |
| `html`     | `str`               | Rich-text. Emits `format: html` in JSON Schema. Supports `placeholder`. |
| `number`   | `float` / `int`     | Set `integer: true` for `int`. Supports `minimum`, `maximum`. |
| `boolean`  | `bool`              |                                                               |
| `date`     | `datetime.date`     |                                                               |
| `datetime` | `datetime.datetime` |                                                               |

### Kind-specific options

**`string`**
- `multiline` (bool) — emits `format: textarea` in JSON Schema.
- `min_length` / `max_length` (int) — enforced as `minLength` / `maxLength` constraints.
- `placeholder` (str) — forwarded to the JSON Schema editor widget.

**`html`**
- `placeholder` (str) — forwarded to the JSON Schema editor widget.

**`number`**
- `integer` (bool) — compiles to `int` instead of `float`.
- `minimum` / `maximum` (float) — enforced as JSON Schema numeric constraints.

## Select Kind

| Kind     | Python Type | Notes                                        |
|----------|-------------|----------------------------------------------|
| `select` | `str`       | Requires `choices` (list of `{value, label}`). |

Define the available options via the `choices` field, which is a list of `SelectChoice` objects:

```json
{
  "name": "status",
  "kind": "select",
  "choices": [
    {"value": "draft", "label": "Draft"},
    {"value": "published", "label": "Published"}
  ]
}
```

The compiler emits a `oneOf` constraint in the JSON Schema so editors only allow valid values.

## Relationship Kinds

| Kind       | Python Type           | Notes                                     |
|------------|-----------------------|-------------------------------------------|
| `ref`      | `<TargetModel>`       | Requires `target_model="app.Model"`       |
| `queryset` | `List[<TargetModel>]` | Requires `target_model="app.Model"`       |

These resolve to real Django model instances via `django-structured-json-field`'s lazy caching.

## Composite Kinds

| Kind    | Python Type                     | Notes                        |
|---------|---------------------------------|------------------------------|
| `group` | Nested Pydantic model           | Requires `children`          |
| `list`  | `List[<nested Pydantic model>]` | Requires `children`          |

`children` is a list of `MetaTypeFieldDef` objects and can be nested arbitrarily deep.

## Translated Fields

Setting `translated: true` on any field wraps its type in `Dict[str, T]`, turning the value into a per-language map:

```python
{"name": "title", "kind": "string", "translated": true}
# Compiled type: Dict[str, str]
# Example value: {"en": "Hello", "it": "Ciao"}
```

## Conditional Schema

The `MetaTypeFieldDef` schema enforces kind-dependent fields both in the admin editor and at validation time:

| Condition               | Required / shown fields              |
|-------------------------|--------------------------------------|
| `kind` is `ref` or `queryset`  | `target_model` (required)    |
| `kind` is `group` or `list`    | `children` (required)        |
| `kind` is `select`             | `choices` (required)         |
| `kind` is `string`             | `multiline`, `min_length`, `max_length` shown |
| `kind` is `string` or `html`   | `placeholder` shown          |
| `kind` is `number`             | `integer`, `minimum`, `maximum` shown |

These conditionals are enforced in the admin JSON editor via `django-structured-json-field`'s `When` / `conditional_schema` utilities.
